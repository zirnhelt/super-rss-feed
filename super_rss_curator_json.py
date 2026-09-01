#!/usr/bin/env python3
"""
Super RSS Feed Curator - JSON Feed Edition
Aggregates feeds, deduplicates, scores with Claude, generates categorized JSON feeds
"""

import os
import sys
import json
import hashlib
import re
import concurrent.futures
from html import escape as html_escape
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from zoneinfo import ZoneInfo
from collections import defaultdict, Counter
from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote, urljoin
import anthropic
from fetch_images import batch_fetch_images
import cohere_integration
import api_usage
import config_loader
from cache import Cache, FeedHTTPCache

# Configuration paths (kept for direct file access e.g. scoring_mode.json)
CONFIG_DIR = Path(__file__).parent / 'config'

CATEGORIES = config_loader.load_categories_config()
CATEGORY_RULES = config_loader.load_category_rules_config()
FILTERS = config_loader.load_filters_config()
LIMITS = config_loader.load_limits_config()
SYSTEM = config_loader.load_system_config()
FEEDS_CONFIG = config_loader.load_feeds_config()
SOURCE_PREFS = config_loader.load_source_preferences()
SUBSCRIBER_ACCESS = SOURCE_PREFS.get('subscriber_access', {}).get('sources', {})
APPLE_NEWS_CHANNELS = SOURCE_PREFS.get('apple_news_channels', {}).get('sources', {})
APPLE_NEWS_PRIMARY_CHANNEL_LINK = SOURCE_PREFS.get('apple_news_channels', {}).get(
    'use_as_primary_link', False
)
# Sources exempt from the two subjective content gates — filter_by_content_type()
# and scrub_feed_with_haiku(). Those gates triage 1200 articles nobody chose, by
# judging whether a headline is newsworthy consumer content. A feed added to
# feeds.opml deliberately has already answered that question, and a machine-written
# operational report is a category error for the rubric: the Cariboo Signals episode
# review scored 'analysis'/84 one day and 'fluff'/56 the next, and was dropped on the
# second. Exempt sources still pass through scoring, dedup, the quality floor and
# slot allocation like anything else.
EDITORIAL_EXEMPT_SOURCES = frozenset(SOURCE_PREFS.get('editorial_exempt_sources', []))
# Sources that must never enter the podcast pool. A source reporting *on* the
# podcast would otherwise be routed into an episode, and the show would discuss
# its own review of itself. Enforced in save_podcast_cache() and both cache
# loaders rather than at one call site: the pool has two writers (the candidate
# branch and the post-categorisation save of every published article), and only
# the loaders can evict entries an earlier build already banked.
try:
    PODCAST_EXCLUDED_SOURCES = frozenset(
        config_loader.load_podcast_schedule_config().get('excluded_sources', []))
except Exception:
    PODCAST_EXCLUDED_SOURCES = frozenset()
SCORING_WEIGHTS = config_loader.load_scoring_weights() or {
    'general': {'w_quality': 0.25, 'w_relevance': 0.55, 'w_local': 0.20},
    'podcast': {'w_quality': 0.25, 'w_relevance': 0.0, 'w_local': 0.10, 'w_theme': 0.65}
}
SCORING_MODIFIERS = config_loader.load_scoring_modifiers() or {
    'local_keyword_bonus': 25,
    'wire_quality_penalty': -10,
    'source_type_quality_adjustments': {}
}
FEED_SLOTS = config_loader.load_feed_slots_config()

# ════════════════════════════════════════════════════════════════════════════════
# Hybrid Scoring Configuration
# ════════════════════════════════════════════════════════════════════════════════

def load_scoring_mode_config() -> Dict:
    """Load hybrid scoring configuration."""
    path = CONFIG_DIR / "scoring_mode.json"
    
    defaults = {
        "mode": "cohere-only",
        "cohere_rerank_all": True,
        "claude_depth_threshold": 0.70,
        "claude_top_percent": 0.30,
    }
    
    if path.exists():
        try:
            config = json.load(open(path))
            result = {**defaults, **config}
            print(f"  📋 Loaded scoring mode: {result['mode']}")
            return result
        except Exception as e:
            print(f"  ⚠️ Failed to load scoring config: {e}, using defaults")
            return defaults
    
    return defaults

# ════════════════════════════════════════════════════════════════════════════════

def _build_prescore_keywords() -> frozenset:
    """Union of all category include-keywords plus local signals.

    Reused as a free relevance gate for high-volume aggregator sources
    (e.g. Kagi Small Web) so off-topic articles never reach paid scoring.
    """
    keywords = set()
    for rules in CATEGORY_RULES.values():
        for kw in rules.get('include', []):
            keywords.add(kw.lower())
    for signal in FILTERS.get('local_signals', []):
        keywords.add(signal.lower())
    return frozenset(keywords)

PRESCORE_KEYWORDS = _build_prescore_keywords()

def _build_all_podcast_keywords(schedule_config: Dict) -> frozenset:
    """Collect all keyword strings across all podcast themes (lowercased)."""
    keywords = set()
    for cfg in schedule_config.get('schedule', {}).values():
        for kw in cfg.get('keywords', []):
            keywords.add(kw.lower())
    return frozenset(keywords)

def _article_matches_podcast_keywords(article: 'Article', keywords: frozenset) -> bool:
    text = f"{article.title} {article.description or ''}".lower()
    return any(kw in text for kw in keywords)

def _podcast_quality(article) -> Optional[int]:
    """Best interest-independent quality signal for podcast gating.

    Prefers the absolute quality gate score, then the Claude quality dimension.
    Returns None when neither exists (legacy cache entries, Cohere-only
    articles) so callers can decide their own fallback — never silently
    substitute the interest composite here.
    """
    q = getattr(article, 'q_gate', None)
    if q is not None:
        return int(q)
    q = getattr(article, 'quality', 0)
    if q and q > 0 and not getattr(article, 'cohere_scored', False):
        return int(q)
    return None

def _build_us_policy_keywords() -> frozenset:
    """US-federal policy/program/agency signal terms (lowercased)."""
    return frozenset(s.lower() for s in FILTERS.get('us_policy_signals', []))

US_POLICY_KEYWORDS = _build_us_policy_keywords()

def _build_canadian_context_keywords() -> frozenset:
    """Terms signalling a Canadian angle; reuses local place-names."""
    kws = {s.lower() for s in FILTERS.get('canadian_context_signals', [])}
    kws |= {s.lower() for s in FILTERS.get('local_signals', [])}
    return frozenset(kws)

CANADIAN_CONTEXT_KEYWORDS = _build_canadian_context_keywords()

def us_policy_scope(title: str, description: str) -> Optional[str]:
    """Classify jurisdiction for US-policy stories.

    Deterministic keyword match — no API cost. Returns None for stories that
    aren't about US policy/programs, 'cross-border-impact' when a US-policy
    story also carries a Canadian angle (direct/inspirational relevance), and
    'out-of-jurisdiction' for pure US-jurisdiction stories.
    """
    text = f"{title} {description or ''}".lower()
    if not any(kw in text for kw in US_POLICY_KEYWORDS):
        return None
    if any(kw in text for kw in CANADIAN_CONTEXT_KEYWORDS):
        return 'cross-border-impact'
    return 'out-of-jurisdiction'

# Shared guidance appended to every theme-scoring system prompt so US-federal
# policy stories are judged on their Cariboo/BC relevance and impact rather than
# penalized for jurisdiction — the podcast host contextualizes that separately.
US_POLICY_SCORING_GUIDANCE = (
    "\n\nJURISDICTION NOTE: US federal policy/program stories are IN SCOPE. Score them on their "
    "relevance and impact to the Cariboo/BC audience (trade effects, precedent, or inspiration) — "
    "do NOT penalize a story merely for being US-jurisdiction. The host contextualizes jurisdiction "
    "separately on-air."
)

def min_score_for_category(category: str) -> int:
    """Per-category quality floor, falling back to the global min_claude_score."""
    return LIMITS.get('min_score_by_category', {}).get(category or 'news', LIMITS['min_claude_score'])

_brave_call_count = 0
_brave_quota_exceeded = False

# Cache files
SCORED_CACHE_FILE = SYSTEM['cache_files']['scored_articles']
WLT_CACHE_FILE = SYSTEM['cache_files']['wlt']
SHOWN_CACHE_FILE = SYSTEM['cache_files']['shown_articles']
EXTRACT_CACHE_FILE = SYSTEM['cache_files']['extract_cache']
PODCAST_CACHE_FILE = 'podcast_articles_cache.json'  # Weekly cache for podcast feeds
PODCAST_SHOWN_FILE = 'podcast_shown_cache.json'      # Tracks URLs used in each day's podcast episode
PODCAST_SHOWN_TTL_DAYS = 7                           # Exclude articles shown in the last 7 days
THEME_SCORE_CACHE_FILE = 'theme_scores_cache.json'  # Cache for per-article theme scores
THEME_SCORE_CACHE_TTL_DAYS = 7
THEME_SCORE_CACHE_VERSION = 'v5'  # v5: weekday theme charters recalibrated; selection now percentile-normalized
PENDING_THEME_BATCH_FILE = 'pending_theme_batch.json'  # Tracks in-flight async theme batch
SHOWN_TERMS_CACHE_FILE = 'shown_terms_cache.json'   # Term sets for cross-run story dedup
THEME_HOLDOVER_FILE = 'theme_holdover_cache.json'   # Cross-week pool of theme-relevant articles
THEME_HOLDOVER_TTL_DAYS = 28                         # 4 weeks — covers monthly themed episode cycles
# Upper bound on each day's *available* (non-USED) holdover bank. Banking is
# unconditional and percentile-based, so it admits far more per run than one
# episode can drain; left unbounded the bank grew ~70-100 entries/day/theme and
# eventually consumed the whole candidate pool. See save_theme_holdover_cache().
THEME_HOLDOVER_MAX_AVAILABLE_PER_DAY = 400
CALIBRATION_STATS_CACHE_FILE = 'calibration_stats_cache.json'  # Rolling per-run audit stats
CALIBRATION_STATS_TTL_DAYS = 14                      # Window consumed by the weekly calibration agent
FEED_HTTP_CACHE_FILE = 'feed_http_cache.json'        # Per-feed ETag/Last-Modified/skip_until state
APPLE_NEWS_CACHE_FILE = 'apple_news_cache.json'      # Harvested apple.news article + channel IDs
APPLE_NEWS_ARTICLE_TTL_DAYS = 14                     # Matches the longest category-feed retention

# URLs
WLT_BASE_URL = SYSTEM['urls']['wlt_base']
WLT_NEWS_URL = SYSTEM['urls']['wlt_news']

# Cache instances (simple dict caches with TTL)
_scored_cache = Cache(SCORED_CACHE_FILE, ttl_hours=SYSTEM['cache_expiry']['scored_hours'])
_extract_cache = Cache(EXTRACT_CACHE_FILE, ttl_hours=SYSTEM['cache_expiry']['scored_hours'])
_wlt_cache = Cache(WLT_CACHE_FILE, ttl_hours=SYSTEM['cache_expiry']['scored_hours'])
_shown_cache = Cache(SHOWN_CACHE_FILE, ttl_hours=SYSTEM['cache_expiry']['shown_days'] * 24)
_shown_terms_cache = Cache(SHOWN_TERMS_CACHE_FILE, ttl_hours=SYSTEM['cache_expiry']['shown_days'] * 24, ts_field='ts')
_feed_http_cache = FeedHTTPCache(FEED_HTTP_CACHE_FILE)
# Harvested apple.news IDs. Read deep in the item-building call tree (like
# SUBSCRIBER_ACCESS), so it is module-level rather than threaded through four
# feed generators. Populated by load_apple_news_cache() in main()/bootstrap.
_apple_news_cache: Dict = {'articles': {}, 'channels': {}}

# ---------------------------------------------------------------------------
# URL canonicalization
# ---------------------------------------------------------------------------
_TRACKING_PARAMS = frozenset({
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    'utm_id', 'utm_reader', 'utm_name', 'utm_place',
    'traffic_source', 'traffic_type',
    'ref', 'referrer', 'ref_src', 'ref_url',
    'fbclid', 'gclid', 'msclkid', 'twclid',
    'mc_cid', 'mc_eid',
    '_ga', '_gl',
    'source', 'via',
})

def canonicalize_url(url: str) -> str:
    """Strip known tracking parameters from a URL before hashing.

    Two URLs that differ only in UTM tags or similar tracking parameters
    should be treated as the same article.
    """
    try:
        parsed = urlparse(url)
        if not parsed.query:
            return url
        params = parse_qs(parsed.query, keep_blank_values=True)
        clean = {k: v for k, v in params.items() if k.lower() not in _TRACKING_PARAMS}
        return urlunparse(parsed._replace(query=urlencode(clean, doseq=True)))
    except Exception:
        return url


_AGGREGATOR_DOMAINS = frozenset({'news.google.com'})

def _is_aggregator_url(url: str) -> bool:
    """Return True if the URL routes through a search-engine aggregator.

    Google News RSS entries use opaque encoded proxy URLs
    (news.google.com/rss/articles/CBMi…) rather than the publisher's
    canonical link, which makes cross-episode deduplication unreliable.
    """
    try:
        return urlparse(url).netloc in _AGGREGATOR_DOMAINS
    except Exception:
        return False


def _load_topic_queries() -> list:
    """Load topic search queries from config/topic_queries.json."""
    try:
        with open(CONFIG_DIR / 'topic_queries.json') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def fetch_topic_news(cutoff_date: datetime) -> List['Article']:
    """Fetch recent articles for all configured topic queries.

    Primary: Brave News API (/v1/news) — news-specific endpoint with freshness
    filtering. Falls back to Kagi Search API per query when Brave returns no
    results or errors. Returns empty list if neither key is set.
    """
    if os.environ.get('USE_SEARCH_APIS', 'true').lower() != 'true':
        return []

    queries = _load_topic_queries()
    if not queries:
        return []

    brave_key = os.environ.get('BRAVE_API_KEY', '')
    kagi_key = os.environ.get('KAGI_API_KEY', '')

    if not brave_key and not kagi_key:
        return []

    now = datetime.now(timezone.utc)
    freshness_range = f"{cutoff_date.strftime('%Y-%m-%d')}to{now.strftime('%Y-%m-%d')}"

    class _SyntheticEntry:
        def get(self, key, default=''):
            return default

    def _make_article(url: str, title: str, snippet: str, pub_str: str, label: str):
        parsed_url = urlparse(url)
        if not (parsed_url.scheme and parsed_url.netloc):
            return None
        source_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        domain = parsed_url.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        article = Article(_SyntheticEntry(), domain, source_url, feed_url='')
        article.title = title.strip()
        if not article.title:
            return None
        article.link = url
        article.url_hash = hashlib.md5(canonicalize_url(url).encode()).hexdigest()
        article.description = '' if _is_tagline_boilerplate(snippet) else snippet
        article.summary = _clean_text(article.description, max_chars=300)
        article.excerpt = _clean_text(article.description, max_chars=600)
        if pub_str:
            try:
                article.pub_date = datetime.fromisoformat(pub_str.replace('Z', '+00:00'))
            except Exception:
                article.pub_date = now
        else:
            article.pub_date = now
        if article.pub_date < cutoff_date:
            return None
        return article

    def _fetch_brave(query_config: dict) -> List['Article']:
        global _brave_quota_exceeded
        if _brave_quota_exceeded:
            return []
        label = query_config.get('label', 'Brave News')
        query = query_config.get('query', '')
        if not query:
            return []
        try:
            api_usage.record_call('brave')
            resp = requests.get(
                'https://api.search.brave.com/res/v1/news/search',
                headers={'X-Subscription-Token': brave_key, 'Accept': 'application/json'},
                params={'q': query, 'count': 20, 'freshness': freshness_range},
                timeout=15,
            )
            resp.raise_for_status()
            if not resp.text.strip():
                return []
            results = []
            for r in resp.json().get('results') or []:
                article = _make_article(
                    url=r.get('url', ''),
                    title=r.get('title', ''),
                    snippet=r.get('description', '') or '',
                    pub_str=r.get('page_fetched', ''),
                    label=label,
                )
                if article:
                    results.append(article)
            return results
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else '?'
            if status == 402:
                _brave_quota_exceeded = True
                print(f"  ✗ {label} (Brave): HTTP 402 — quota exceeded, disabling Brave for this run")
            else:
                print(f"  ✗ {label} (Brave): HTTP {status}")
        except ValueError as e:
            print(f"  ✗ {label} (Brave): invalid JSON response - {e}")
        except Exception as e:
            print(f"  ✗ {label} (Brave): {e}")
        return []

    def _fetch_kagi(query_config: dict) -> List['Article']:
        label = query_config.get('label', 'Kagi Search')
        query = query_config.get('query', '')
        if not query:
            return []
        try:
            api_usage.record_call('kagi')
            default_limit = SOURCE_PREFS.get('kagi_search_result_limit', 10)
            limit = query_config.get('max_results', default_limit)
            resp = requests.post(
                'https://kagi.com/api/v1/search',
                headers={'Authorization': f'Bearer {kagi_key}'},
                json={'query': query, 'limit': limit},
                timeout=15,
            )
            resp.raise_for_status()
            results = []
            for r in (resp.json().get('data') or {}).get('search') or []:
                if not isinstance(r, dict):
                    continue
                article = _make_article(
                    url=r.get('url', ''),
                    title=r.get('title', ''),
                    snippet=r.get('snippet', '') or '',
                    pub_str=r.get('published', ''),
                    label=label,
                )
                if article:
                    results.append(article)
            return results
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else '?'
            body = e.response.text.strip()[:1000] if e.response is not None else ''
            print(f"  ✗ {label} (Kagi): HTTP {status} - {body}")
        except Exception as e:
            print(f"  ✗ {label} (Kagi): {e}")
        return []

    def _fetch_one(query_config: dict) -> List['Article']:
        label = query_config.get('label', '')
        brave_results = _fetch_brave(query_config) if brave_key else []
        if brave_results:
            print(f"  ✓ {label}: {len(brave_results)} articles (Brave)")
            return brave_results

        # Fall back to Kagi only when Brave returned nothing (empty or failed).
        kagi_results = _fetch_kagi(query_config) if kagi_key else []
        if kagi_results:
            print(f"  ✓ {label}: {len(kagi_results)} articles (Kagi)")
            return kagi_results
        return []

    all_articles: List['Article'] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for batch in pool.map(_fetch_one, queries):
            all_articles.extend(batch)

    print(f"  🔍 Topic queries: {len(all_articles)} articles from {len(queries)} "
          f"queries (Brave={'on' if brave_key else 'off'}, Kagi={'on' if kagi_key else 'off'})")
    _enrich_thin_local_articles(all_articles)
    return all_articles


def fetch_kite_news(cutoff_date: datetime) -> List['Article']:
    """Fetch broad, pre-clustered headlines from Kagi's Kite News API.

    Unlike the curated OPML feeds and topic queries (all individually chosen
    for personal relevance), this pulls Kite's own category batches — each
    story is already a multi-source cluster, giving a general "front page"
    survey independent of the personal interest profile. Keyless per the
    published spec, but sends KAGI_API_KEY when set in case it raises
    anonymous rate limits. Fails open: any error just yields no articles.
    """
    news_cfg = SYSTEM.get('kagi_news', {})
    if not news_cfg.get('enabled', False):
        return []

    base_url = news_cfg.get('base_url', 'https://kite.kagi.com')
    wanted_categories = {c.lower() for c in news_cfg.get('categories', [])}
    max_per_category = news_cfg.get('max_stories_per_category', 8)

    kagi_key = os.environ.get('KAGI_API_KEY', '')
    headers = {'Authorization': f'Bearer {kagi_key}'} if kagi_key else {}

    def _make_kite_article(story: dict) -> Optional['Article']:
        primary = (story.get('articles') or [{}])[0]
        url = primary.get('link', '')
        parsed_url = urlparse(url)
        if not (parsed_url.scheme and parsed_url.netloc):
            return None
        domain = parsed_url.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        source_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        class _SyntheticEntry:
            def get(self, key, default=''):
                return default

        article = Article(_SyntheticEntry(), domain, source_url, feed_url='')
        article.title = (story.get('title') or '').strip()
        if not article.title:
            return None
        article.link = url
        article.url_hash = hashlib.md5(canonicalize_url(url).encode()).hexdigest()
        description = story.get('short_summary', '') or ''
        article.description = description
        article.summary = _clean_text(description, max_chars=300)
        article.excerpt = _clean_text(description, max_chars=600)
        image = (story.get('primary_image') or {}).get('url')
        if image:
            article.image = image

        pub_str = primary.get('date', '')
        try:
            article.pub_date = (datetime.fromisoformat(pub_str.replace('Z', '+00:00'))
                                 if pub_str else datetime.now(timezone.utc))
        except Exception:
            article.pub_date = datetime.now(timezone.utc)
        if article.pub_date < cutoff_date:
            return None
        return article

    try:
        api_usage.record_call('kite')
        resp = requests.get(f"{base_url}/api/batches/latest/categories",
                             headers=headers, params={'lang': 'en'}, timeout=15)
        resp.raise_for_status()
        categories = resp.json().get('categories') or []
    except Exception as e:
        print(f"  ✗ Kite News categories: {e}")
        return []

    matched = [c for c in categories
               if c.get('categoryId', '').lower() in wanted_categories
               or c.get('categoryName', '').lower() in wanted_categories]

    all_articles: List['Article'] = []
    for cat in matched:
        category_id = cat.get('id', '')
        label = cat.get('categoryName', category_id)
        if not category_id:
            continue
        try:
            api_usage.record_call('kite')
            resp = requests.get(
                f"{base_url}/api/batches/latest/categories/{category_id}/stories",
                headers=headers,
                params={'limit': max_per_category, 'lang': 'en'},
                timeout=15,
            )
            resp.raise_for_status()
            stories = resp.json().get('stories') or []
            count = 0
            for story in stories:
                article = _make_kite_article(story)
                if article:
                    all_articles.append(article)
                    count += 1
            print(f"  ✓ Kite News/{label}: {count} stories")
        except Exception as e:
            print(f"  ✗ Kite News/{label}: {e}")

    print(f"  📰 Kite News: {len(all_articles)} broad headlines from {len(matched)} categories")
    return all_articles


# ---------------------------------------------------------------------------
# Term-set utilities for story-level deduplication
# ---------------------------------------------------------------------------
_STOPWORDS = frozenset({
    # Articles / conjunctions / prepositions
    'a', 'an', 'the', 'and', 'or', 'but', 'nor', 'so', 'yet',
    'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from',
    'up', 'about', 'into', 'through', 'during', 'before', 'after',
    'above', 'below', 'between', 'out', 'off', 'over', 'under',
    'again', 'further', 'then', 'once', 'per',
    # Verbs / auxiliaries
    'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall',
    'get', 'gets', 'got', 'make', 'made', 'says', 'said',
    # Pronouns / determiners
    'it', 'its', 'this', 'that', 'these', 'those',
    'i', 'you', 'he', 'she', 'we', 'they', 'them', 'their', 'our', 'your',
    'what', 'which', 'who', 'whom', 'whose',
    'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
    'some', 'such', 'no', 'not', 'only', 'own', 'same', 'than',
    'too', 'very', 'just', 'as', 'if', 'can',
    # Common news-headline filler (too generic to identify a story)
    'new', 'now', 'how', 'why', 'when', 'where', 'here', 'there',
    'latest', 'update', 'report', 'reports', 'week', 'day', 'year', 'month',
    'vs', 'via', 'amid', 'amid', 'inside', 'following',
})

def _term_set(text: str) -> frozenset:
    """Return the set of meaningful words from a headline."""
    words = re.findall(r'[a-z0-9]+', text.lower())
    return frozenset(w for w in words if len(w) > 2 and w not in _STOPWORDS)


def _story_overlap(a: frozenset, b: frozenset) -> float:
    """Containment similarity: |A∩B| / min(|A|,|B|).

    Returns a value in [0, 1].  Unlike Jaccard this is invariant to one
    set being a subset of the other, which handles cases where one
    headline is a sub-phrase of another.
    """
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def _clean_text(html_or_text: str, max_chars: int = 0) -> str:
    """Strip HTML tags and normalize whitespace. Truncate at a word boundary if max_chars > 0."""
    if not html_or_text:
        return ''
    text = BeautifulSoup(html_or_text, 'html.parser').get_text(' ', strip=True)
    text = ' '.join(text.split())
    if max_chars and len(text) > max_chars:
        truncated = text[:max_chars]
        # Break at the last space so we don't cut mid-word
        space_idx = truncated.rfind(' ')
        text = truncated[:space_idx] if space_idx > 0 else truncated
    return text


def _boilerplate_key(html_or_text: str) -> str:
    """Reduce text to a markup/whitespace/punctuation-insensitive key.

    Used to detect boilerplate descriptions: feeds that repeat their channel
    tagline as every item's <description> often vary only in markup (e.g.
    <strong> wrappers) or spacing, which defeats exact string comparison.
    """
    return re.sub(r'[^a-z0-9]+', '', _clean_text(html_or_text).lower())


def _find_boilerplate_keys(descriptions: List[str], channel_key: str = '',
                           min_repeats: int = 3) -> set:
    """Return keys of descriptions that are channel boilerplate, not article text.

    A description is boilerplate if it matches the channel-level description or
    appears verbatim on min_repeats+ items — real article summaries are unique.
    """
    counts = Counter(_boilerplate_key(d) for d in descriptions)
    return {
        key for key, count in counts.items()
        if key and (key == channel_key or count >= min_repeats)
    }


# The "Now" network of Cariboo/Kootenay local news sites (My Cariboo Now, My East
# Kootenay Now, etc.) republishes this site-wide tagline as every article's RSS/meta
# description. Their feeds also reliably 403 on direct fetch (see FEED_ERRORS.md), so
# these articles always come in through the Brave/Kagi/Google News search fallbacks,
# which have no parsed channel description and often only 1-2 items per run — too few
# to trip _find_boilerplate_keys's count/channel heuristic. Match the tagline directly
# so it's stripped regardless of fetch path or batch size.
_TAGLINE_BOILERPLATE_RE = re.compile(
    r'stay connected with .{0,60}now\b.{0,20}delivering local news', re.IGNORECASE
)


def _is_tagline_boilerplate(text: str) -> bool:
    """True if text is the 'Stay connected with My Cariboo Now...' site tagline."""
    return bool(text) and bool(_TAGLINE_BOILERPLATE_RE.search(text))


def _strip_markdown_links(text: str) -> str:
    """Convert markdown link syntax to plain text: [text](url) → text, ![alt](url) → alt.

    Kagi Extract returns markdown; without this the link syntax appears literally
    in content_html because feed readers treat the field as HTML, not markdown.
    Safe to apply to HTML content — the pattern doesn't appear in normal HTML.
    """
    if not text:
        return text
    text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', text)  # images first
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)   # then links
    return text


# Local BC news domains whose RSS descriptions are often empty/stub due to paywalls.
# When an article from one of these domains has a very short description (<100 chars),
# the feed will attempt a lightweight body fetch to capture text before the paywall closes.
_LOCAL_BC_DOMAINS = frozenset({
    'wltribune.com', 'quesnelobserver.com', '100milefreepress.net',
    'mycariboonow.com', 'myeastkootenaynow.com', 'cfjctoday.com',
    'bclocalnews.com',
})


class Article:
    """Represents a single article"""
    def __init__(self, entry, source_title: str, source_url: str, feed_url: str = ''):
        is_google_news = 'news.google.com' in feed_url

        # Clean title - remove source suffix if present
        raw_title = entry.get('title', '').strip()
        # Remove " - SourceName" pattern common in Google News
        extracted_outlet = None
        if is_google_news and ' - ' in raw_title:
            parts = raw_title.rsplit(' - ', 1)
            # Only remove if the suffix looks like a source name (not too long)
            if len(parts) == 2 and len(parts[1]) < 50:
                self.title = parts[0].strip()
                extracted_outlet = parts[1].strip()
            else:
                self.title = raw_title
        else:
            self.title = raw_title
        self.link = entry.get('link', '').strip()
        self.description = entry.get('description', '') or entry.get('summary', '')
        if _is_tagline_boilerplate(self.description):
            self.description = ''
        self.pub_date = self._parse_date(entry)
        # For Google News feeds, use the outlet name embedded in the title suffix
        # (e.g. "TechCrunch") rather than the generic feed title ("GN AI ML Infrastructure")
        self.source = extracted_outlet if (is_google_news and extracted_outlet) else source_title
        self.source_url = source_url
        self.feed_url = feed_url
        self.score = 0
        self.quality = 0       # Q: journalistic depth, sourcing, originality (0-100)
        self.relevance = 0     # R: match to interest profile (0-100)
        self.local = 0         # L: Cariboo/BC/rural specificity (0-100)
        self.content_type = None  # analysis|breaking|opinion|feature|recap|fluff|sponsored|wire
        self.cohere_scored = False  # True when scored via Cohere (Q/R/L are synthesized, not real)
        self.gate_scored = False   # True when only the quality gate scored this article (score == q_gate)
        self.q_gate: Optional[int] = None  # Absolute newsworthiness score, interest-independent (0-100)
        self.category = None
        self.image = self._extract_image(entry)

        self.url_hash = hashlib.md5(canonicalize_url(self.link).encode()).hexdigest()
        self.title_normalized = self.title.lower().strip()
        self.title_terms = _term_set(self.title_normalized)
        self.story_group: Optional[str] = None  # Claude-assigned event label for dedup

        # Plain-text extracts used by the downstream podcast generator as verified
        # source material.  Derived from description at construction time; may be
        # updated later via _fetch_article_excerpt when the description is too short.
        self.summary = _clean_text(self.description, max_chars=300)
        self.excerpt = _clean_text(self.description, max_chars=600)
    
    def _parse_date(self, entry) -> datetime:
        """Parse publication date from entry"""
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
        return datetime.now(timezone.utc)

    def _extract_image(self, entry) -> str:
        """Extract image URL from feed entry metadata"""
        # media:thumbnail (common in Media RSS)
        thumbs = getattr(entry, 'media_thumbnail', None)
        if thumbs and isinstance(thumbs, list) and thumbs[0].get('url'):
            return thumbs[0]['url']

        # media:content with medium="image"
        media = getattr(entry, 'media_content', None)
        if media and isinstance(media, list):
            for m in media:
                if m.get('medium') == 'image' and m.get('url'):
                    return m['url']
                if m.get('type', '').startswith('image/') and m.get('url'):
                    return m['url']

        # RSS enclosures with image type
        enclosures = getattr(entry, 'enclosures', None)
        if enclosures and isinstance(enclosures, list):
            for enc in enclosures:
                if enc.get('type', '').startswith('image/'):
                    return enc.get('href') or enc.get('url', '')

        return None

    def should_filter(self) -> bool:
        """Check if article should be filtered out"""
        text = f"{self.title} {self.description}".lower()

        source_lower = self.source.lower()
        if any(blocked in source_lower for blocked in FILTERS['blocked_sources']):
            return True

        # blocked_keywords always applies — sports leagues, sports terms, advice columns,
        # and stock jargon are universally unwanted regardless of local signals.
        if any(keyword in text for keyword in FILTERS['blocked_keywords']):
            return True

        # Title-pattern blocklist: first-person anecdote listicles ("I ditched...",
        # "My home server...") plus deal/shopping-listicle commerce titles ("43% off",
        # "15 best ice cream makers..."). Patterns match anywhere in the title.
        title_lower = self.title.lower()
        if any(re.search(pattern, title_lower) for pattern in FILTERS.get('blocked_title_patterns', [])):
            return True

        # Arts/entertainment keywords are skipped when article mentions local places
        # (e.g. an arena hosts a concert, or a local tournament isn't sports).
        is_local = any(signal in text for signal in FILTERS.get('local_signals', []))
        nonlocal_keywords = FILTERS.get('blocked_keywords_unless_local', [])
        if nonlocal_keywords and not is_local:
            if any(keyword in text for keyword in nonlocal_keywords):
                return True

        return False


def load_apple_news_cache() -> Dict:
    """Load harvested apple.news IDs, pruning stale article entries.

    Channel IDs are never pruned — a publication's channel does not change, and
    it is the tier that gives near-total coverage once learned.
    """
    empty = {'articles': {}, 'channels': {}}
    if not os.path.exists(APPLE_NEWS_CACHE_FILE):
        return empty

    try:
        with open(APPLE_NEWS_CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        if not isinstance(cache, dict):
            return empty
    except Exception:
        return empty

    cutoff = datetime.now(timezone.utc).timestamp() - (APPLE_NEWS_ARTICLE_TTL_DAYS * 86400)
    articles = {
        url: entry for url, entry in (cache.get('articles') or {}).items()
        if isinstance(entry, dict) and entry.get('ts', 0) > cutoff
    }
    channels = {
        source: entry for source, entry in (cache.get('channels') or {}).items()
        if isinstance(entry, dict) and entry.get('id')
    }
    return {'articles': articles, 'channels': channels}


def save_apple_news_cache(cache: Dict) -> None:
    """Persist harvested apple.news IDs."""
    try:
        with open(APPLE_NEWS_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Failed to save Apple News cache: {e}")


def resolve_apple_news_url(article: 'Article', apple_news_cache: Dict) -> Tuple[Optional[str], str]:
    """Best available `https://apple.news/…` link for a subscriber-access article.

    Returns ``(url, tier)`` where tier is ``'article'``, ``'channel'`` or
    ``''``. Most precise first:

    1. the article's own harvested `A…` ID — lands on the article itself;
    2. the publication's `T…` channel ID — lands on the channel, where a
       <48 h-old article is normally near the top;
    3. nothing, and the caller keeps the publisher URL.

    Tier 2 falls back to the hand-maintained `apple_news_channels` map in
    `config/source_preferences.json` for publications whose pages never expose a
    channel link. Both tiers yield an https universal link, so Apple devices
    hand off into the News app and everything else redirects to Apple's web
    fallback — which is the whole reason the `applenews://` scheme was dropped.
    """
    entry = (apple_news_cache.get('articles') or {}).get(article.link)
    if entry and entry.get('id'):
        return f"https://apple.news/{entry['id']}", 'article'

    channel = (apple_news_cache.get('channels') or {}).get(article.source)
    channel_id = channel.get('id') if channel else APPLE_NEWS_CHANNELS.get(article.source)
    if channel_id:
        return f"https://apple.news/{channel_id}", 'channel'

    return None, ''


def apply_subscriber_links(item: Dict, article: 'Article', subscriber_label: str) -> None:
    """Tag a subscriber-access item and route it into Apple News when possible.

    For an `Apple News` label with a resolvable link, `url` becomes the
    apple.news link and the publisher URL moves to `external_url`. `id` stays
    the publisher URL — it is the identity key behind cross-run dedup, the
    shown/scored caches and the feedback ledger — so every read-back of a
    written feed must go through `item_source_link()`.

    Only an *article*-tier link is promoted to `url` by default: it is strictly
    better than the publisher URL everywhere, opening the article in News on
    Apple devices and redirecting elsewhere. A *channel*-tier link is not — in a
    desktop browser it lands on the publication's channel rather than the piece
    you clicked — so it stays a secondary `_apple_news_url` badge unless
    `apple_news_channels.use_as_primary_link` is set. Turn that on if you read
    the feed almost entirely from Apple devices.

    With nothing resolvable, `url` stays the publisher URL. The reader always
    gets a link that works; the Apple News tiers only ever upgrade it.
    """
    item['_subscriber_access'] = subscriber_label
    if not subscriber_label.startswith('Apple News'):
        return

    apple_url, tier = resolve_apple_news_url(article, _apple_news_cache)
    if not apple_url:
        return

    item['_apple_news_url'] = apple_url
    if tier == 'article' or APPLE_NEWS_PRIMARY_CHANNEL_LINK:
        item['external_url'] = item['url']
        item['url'] = apple_url


def item_source_link(item: Dict) -> str:
    """Return the publisher URL for a feed item written by this pipeline.

    ``url`` is the link the reader follows and is not guaranteed to be the
    publisher URL; whenever it is not, ``external_url`` holds the publisher URL.
    Every read-back that treats a URL as article identity — retention dedup,
    bootstrap dedup, reporting — must go through here instead of touching
    ``url`` directly, or those articles fail to match themselves across runs
    and accumulate a duplicate every night.

    Feeds already deployed to gh-pages still carry ``applenews://`` in ``url``
    from the reverted deep-link experiment, so this is also the migration path:
    retained items are rebuilt from the value returned here.
    """
    return item.get('external_url') or item.get('url', '')


def load_podcast_cache():
    """Load weekly podcast articles cache (7 days retention)"""
    if not os.path.exists(PODCAST_CACHE_FILE):
        return []

    try:
        with open(PODCAST_CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        # Keep articles from last 7 days
        cache_expiry = timedelta(days=7)
        cutoff = datetime.now(timezone.utc) - cache_expiry

        valid_articles = []
        for item in cache_data:
            pub_date = datetime.fromisoformat(item['pub_date'])
            if (pub_date > cutoff
                    and not _is_aggregator_url(item.get('link', ''))
                    and item.get('source') not in PODCAST_EXCLUDED_SOURCES):
                valid_articles.append(item)

        if len(valid_articles) != len(cache_data):
            print(f"🧹 Cleaned podcast cache: {len(cache_data)} → {len(valid_articles)} articles")

        # Strip boilerplate descriptions that entered the cache before fetch-time
        # detection (or via fallback ingest paths that bypass it): a description
        # shared verbatim by 3+ cached articles is channel boilerplate, not
        # article content.
        boilerplate_keys = _find_boilerplate_keys(
            [item.get('description', '') for item in valid_articles]
        )
        if boilerplate_keys:
            scrubbed = 0
            for item in valid_articles:
                if _boilerplate_key(item.get('description', '')) in boilerplate_keys:
                    item['description'] = ''
                    item['summary'] = ''
                    item['excerpt'] = ''
                    scrubbed += 1
            if scrubbed:
                print(f"🧹 Stripped boilerplate descriptions from {scrubbed} cached podcast articles")

        return valid_articles

    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        print(f"⚠️ Error loading podcast cache: {e}")
        return []


def save_podcast_cache(articles, main_feed_quality: bool = True):
    """Save articles to weekly podcast cache.

    Args:
        articles: List of Article objects to cache.
        main_feed_quality: True if articles passed all main-feed filters (safe for
            bootstrap). False for podcast-only candidates captured before haiku scrub
            or quality floor. Existing False entries are upgraded to True when the
            same article later passes main-feed quality.
    """
    try:
        existing = load_podcast_cache()

        # Index by link for O(1) lookup and in-place upgrade
        existing_by_link: Dict[str, Dict] = {item['link']: item for item in existing}

        for article in articles:
            if _is_aggregator_url(article.link):
                continue
            if article.source in PODCAST_EXCLUDED_SOURCES:
                continue
            if article.link not in existing_by_link:
                entry = {
                    'link': article.link,
                    'title': article.title,
                    'description': article.description,
                    'summary': getattr(article, 'summary', ''),
                    'excerpt': getattr(article, 'excerpt', ''),
                    'pub_date': article.pub_date.isoformat(),
                    'source': article.source,
                    'source_url': article.source_url,
                    'score': article.score,
                    'composite': article.score,
                    'quality': getattr(article, 'quality', 0),
                    'relevance': getattr(article, 'relevance', 0),
                    'local': getattr(article, 'local', 0),
                    'q_gate': getattr(article, 'q_gate', None),
                    'content_type': getattr(article, 'content_type', None),
                    'category': article.category,
                    'image': getattr(article, 'image', None),
                    'main_feed_quality': main_feed_quality,
                }
                existing.append(entry)
                existing_by_link[article.link] = entry
            else:
                entry = existing_by_link[article.link]
                if main_feed_quality and not entry.get('main_feed_quality', False):
                    entry['main_feed_quality'] = True
                if article.category and not entry.get('category'):
                    entry['category'] = article.category

        existing.sort(key=lambda x: x['pub_date'], reverse=True)

        with open(PODCAST_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

        label = 'main-feed' if main_feed_quality else 'podcast-candidate'
        print(f"💾 Podcast cache updated: {len(existing)} articles ({label}, 7-day window)")

    except Exception as e:
        print(f"⚠️ Failed to save podcast cache: {e}")


def load_theme_holdover_cache() -> Dict:
    """Load cross-week theme holdover cache (28-day retention).

    Format: {day_name: [{article_data..., "theme_score": int, "banked_at": ISO}]}
    Articles here bypassed the base-score filter because they scored well on the
    day's theme; they stay available for up to 4 weekly episodes.
    """
    if not os.path.exists(THEME_HOLDOVER_FILE):
        return {}
    try:
        with open(THEME_HOLDOVER_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        cutoff = datetime.now(timezone.utc) - timedelta(days=THEME_HOLDOVER_TTL_DAYS)
        pruned = {}
        for day, articles in data.items():
            valid = [a for a in articles
                     if datetime.fromisoformat(a['banked_at']) > cutoff
                     and a.get('source') not in PODCAST_EXCLUDED_SOURCES]
            if valid:
                pruned[day] = valid
        return pruned
    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        print(f"⚠️ Error loading theme holdover cache: {e}")
        return {}


def save_theme_holdover_cache(holdover: Dict):
    """Persist the cross-week holdover bank, bounding each day's available pool.

    ``bank_articles_for_all_themes`` admits every article above a *percentile*
    threshold (e.g. 12 == "top 88% of this theme's candidates"), on every run,
    for every day — far more than a single episode's ~100 selections can drain.
    Unbounded, each day's available bank grew monotonically until it exceeded the
    candidate-pool cap in ``generate_podcast_feed``, at which point no fresh
    article could enter the pool at all and the feed regenerated from week-old
    material only.

    Keeping the best-fitting ``THEME_HOLDOVER_MAX_AVAILABLE_PER_DAY`` entries
    preserves the bank's purpose (a deep reserve for thin themes) without letting
    it become the pool. USED entries are retained — they suppress re-banking and
    re-airing — and age out on the normal 28-day TTL.
    """
    bounded: Dict = {}
    for day, articles in holdover.items():
        used = [a for a in articles if a.get('status') == 'USED']
        available = [a for a in articles if a.get('status') != 'USED']
        if len(available) > THEME_HOLDOVER_MAX_AVAILABLE_PER_DAY:
            available.sort(
                key=lambda a: (a.get('theme_score') or 0, a.get('banked_at') or ''),
                reverse=True,
            )
            available = available[:THEME_HOLDOVER_MAX_AVAILABLE_PER_DAY]
        bounded[day] = used + available
    try:
        with open(THEME_HOLDOVER_FILE, 'w', encoding='utf-8') as f:
            json.dump(bounded, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Failed to save theme holdover cache: {e}")


def update_theme_holdover(theme_name: str, theme_label: str,
                          scored_articles: List[tuple], threshold: int) -> int:
    """Bank articles scoring >= threshold on a theme for future episodes.

    Args:
        theme_name: Day key e.g. 'tuesday'
        theme_label: Human label e.g. 'Working Lands & Industry'
        scored_articles: List of (article, theme_score) from score_articles_for_theme
        threshold: Minimum theme score to bank an article

    Returns:
        Number of articles newly banked.
    """
    holdover = load_theme_holdover_cache()
    existing_urls = {a['link'] for a in holdover.get(theme_name, [])}
    now_iso = datetime.now(timezone.utc).isoformat()
    banked = 0
    for article, theme_score in scored_articles:
        if theme_score >= threshold and article.link not in existing_urls:
            holdover.setdefault(theme_name, []).append({
                'link': article.link,
                'title': article.title,
                'description': article.description,
                'summary': getattr(article, 'summary', ''),
                'excerpt': getattr(article, 'excerpt', ''),
                'pub_date': article.pub_date.isoformat(),
                'source': article.source,
                'source_url': article.source_url,
                'score': article.score,
                'quality': getattr(article, 'quality', 0),
                'local': getattr(article, 'local', 0),
                'q_gate': getattr(article, 'q_gate', None),
                'category': article.category,
                'image': getattr(article, 'image', None),
                'theme_score': theme_score,
                'banked_at': now_iso,
            })
            existing_urls.add(article.link)
            banked += 1
    if banked:
        save_theme_holdover_cache(holdover)
        print(f"  📦 Banked {banked} articles for future {theme_label} episodes")
    return banked


def load_podcast_shown_cache() -> Dict:
    """Load cache tracking which article URLs have appeared in recent podcast episodes.

    Format: {"{url}:::{day}": {"day": "monday", "shown_at": "<ISO8601>"}}
    The compound key allows the same article to appear in multiple themed episodes
    (once per theme) within the 7-day TTL window, enabling cross-theme reuse.

    Migrates legacy entries keyed by plain URL on first load.
    Entries older than PODCAST_SHOWN_TTL_DAYS are discarded.
    """
    if not os.path.exists(PODCAST_SHOWN_FILE):
        return {}
    try:
        with open(PODCAST_SHOWN_FILE, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        cutoff = datetime.now(timezone.utc) - timedelta(days=PODCAST_SHOWN_TTL_DAYS)
        migrated: Dict = {}
        for key, entry in raw.items():
            # Migrate legacy plain-URL keys to compound "{url}:::{day}" format
            if ':::' not in key:
                day = entry.get('day', 'unknown')
                new_key = f"{key}:::{day}"
            else:
                new_key = key
            if datetime.fromisoformat(entry['shown_at']) > cutoff:
                migrated[new_key] = entry
        if len(migrated) != len(raw):
            print(f"🧹 Podcast shown cache: {len(raw)} → {len(migrated)} entries (cleaned/migrated)")
        return migrated
    except Exception:
        return {}


def save_podcast_shown_cache(cache: Dict):
    """Persist the podcast shown cache to disk."""
    try:
        with open(PODCAST_SHOWN_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Failed to save podcast shown cache: {e}")


def load_theme_score_cache() -> Dict:
    """Load cached per-article theme scores.

    Returns an empty dict when the cache file is missing, unreadable, or was
    written by an older scoring formula (identified by __version__ mismatch).
    This forces a clean re-score with the current normalization logic.
    """
    if not os.path.exists(THEME_SCORE_CACHE_FILE):
        return {}
    try:
        with open(THEME_SCORE_CACHE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data.get('__version__') != THEME_SCORE_CACHE_VERSION:
            print(f"  ♻️  Theme score cache version mismatch — clearing for re-score")
            return {}
        return {k: v for k, v in data.items() if k != '__version__'}
    except Exception:
        return {}


def save_theme_score_cache(cache: Dict):
    """Persist theme score cache, pruning entries older than TTL."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=THEME_SCORE_CACHE_TTL_DAYS)).isoformat()
    pruned = {k: v for k, v in cache.items()
              if isinstance(v, dict) and v.get('cached_at', '') >= cutoff}
    pruned['__version__'] = THEME_SCORE_CACHE_VERSION
    try:
        with open(THEME_SCORE_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(pruned, f)
    except Exception as e:
        print(f"⚠️ Failed to save theme score cache: {e}")


def percentile_ranks(scores: List[int]) -> List[int]:
    """Convert raw scores to 0-100 percentile ranks, preserving order.

    Ties share the lower rank, so a large block of identical scores (common at
    the bottom of a narrow theme) does not fan out into spurious separation.
    A single value, or an all-identical set, maps to 50.
    """
    total = len(scores)
    if total == 0:
        return []
    if total == 1:
        return [50]

    rank_of_score: Dict[int, int] = {}
    for idx, raw in enumerate(sorted(scores)):
        if raw not in rank_of_score:
            rank_of_score[raw] = idx

    return [max(0, min(100, round(rank_of_score[s] / (total - 1) * 100))) for s in scores]


def normalize_theme_scores(theme_cache: Dict, schedule: Dict,
                           pool_links: Optional[Set[str]] = None) -> Dict[str, int]:
    """Map raw theme scores to within-theme percentile ranks (0-100).

    Raw scores are not comparable across themes: each theme's charter judges a
    different slice of the corpus, so a narrow theme (Working Lands) sits at a
    mean of ~3 while a broad one (Science) sits near ~49 on the *same* pool.
    Any absolute threshold shared across themes — the theme-fit floor,
    ``holdover_threshold``, ``theme_routing_min_score`` — is therefore wrong by
    construction, and ``argmax`` over raw scores tracks charter generosity
    rather than fit.

    Ranking within each theme removes the scale entirely. This mirrors the news
    head, where Cohere Rerank orders candidates and never becomes a pass/fail
    score; absolute "is this worth airing" stays with ``q_gate``.

    Args:
        theme_cache: ``{f"{url}:::{label}": {"score": int, ...}}``
        schedule: The ``schedule`` block of ``podcast_schedule.json``.
        pool_links: Restrict ranking to these URLs. Percentiles are relative to
            the ranked set, so passing the live podcast pool keeps stale cache
            entries from skewing the distribution. ``None`` ranks everything.

    Returns:
        ``{f"{url}:::{day}": percentile}`` keyed by *day name* (not label), so
        callers can look up by the same day key the schedule uses. Ties share
        the lower rank, and a theme whose scores are all identical maps to 50.
    """
    normalized: Dict[str, int] = {}

    for day, cfg in schedule.items():
        suffix = f":::{cfg['label']}"
        scored: List[Tuple[str, int]] = []
        for key, entry in theme_cache.items():
            if not key.endswith(suffix) or not isinstance(entry, dict):
                continue
            url = key[:-len(suffix)]
            if pool_links is not None and url not in pool_links:
                continue
            scored.append((url, entry.get('score', 0)))

        if not scored:
            continue

        for (url, _), pct in zip(scored, percentile_ranks([s for _, s in scored])):
            normalized[f"{url}:::{day}"] = pct

    return normalized


def load_calibration_stats_cache() -> List[Dict]:
    """Load the rolling-window run-stats log consumed by the weekly calibration agent."""
    if not os.path.exists(CALIBRATION_STATS_CACHE_FILE):
        return []
    try:
        with open(CALIBRATION_STATS_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_calibration_stats_cache(records: List[Dict]):
    try:
        with open(CALIBRATION_STATS_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Failed to save calibration stats cache: {e}")


def record_run_stats(run_stats: Dict):
    """Append this run's summary stats to the rolling calibration stats cache,
    pruning entries older than CALIBRATION_STATS_TTL_DAYS.

    The cache holds aggregate counts/histograms only (no article text or URLs)
    so the weekly calibration agent can review selection/filtering trends
    without re-reading article content.
    """
    records = load_calibration_stats_cache()
    records.append(run_stats)
    cutoff = datetime.now(timezone.utc) - timedelta(days=CALIBRATION_STATS_TTL_DAYS)
    pruned = []
    for r in records:
        try:
            if datetime.fromisoformat(r['timestamp']) > cutoff:
                pruned.append(r)
        except (KeyError, ValueError):
            continue
    save_calibration_stats_cache(pruned)
    print(f"📊 Calibration stats recorded ({len(pruned)} runs in {CALIBRATION_STATS_TTL_DAYS}-day window)")


def _score_histogram(articles: List[Article]) -> Dict[str, Dict[str, int]]:
    """Bucket article scores (0-100) into 20-point ranges per category."""
    buckets = ["0-19", "20-39", "40-59", "60-79", "80-100"]

    def _bucket(score: int) -> str:
        score = max(0, min(100, score))
        idx = min(score // 20, 4)
        return buckets[idx]

    histogram: Dict[str, Dict[str, int]] = defaultdict(lambda: {b: 0 for b in buckets})
    for a in articles:
        histogram[a.category or 'news'][_bucket(a.score)] += 1
    return {cat: counts for cat, counts in histogram.items()}


def _dimensional_histograms(articles: List[Article]) -> Dict[str, Dict[str, Dict[str, int]]]:
    """Bucket Q/R/L dimension scores into 20-point ranges per category."""
    buckets = ["0-19", "20-39", "40-59", "60-79", "80-100"]
    dims = ('quality', 'relevance', 'local')
    result: Dict[str, Dict[str, Dict[str, int]]] = {
        dim: defaultdict(lambda: {b: 0 for b in buckets}) for dim in dims
    }
    for a in articles:
        cat = a.category or 'news'
        for dim in dims:
            val = getattr(a, dim, None)
            if val is None:
                continue
            val = max(0, min(100, int(val)))
            bucket = buckets[min(val // 20, 4)]
            result[dim][cat][bucket] += 1
    return {dim: {cat: dict(h) for cat, h in hists.items()} for dim, hists in result.items()}


def _content_type_breakdown(articles: List[Article]) -> Dict[str, Dict[str, int]]:
    """Count articles by content_type per category."""
    result: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for a in articles:
        ct = getattr(a, 'content_type', None) or 'unknown'
        result[a.category or 'news'][ct] += 1
    return {cat: dict(cts) for cat, cts in result.items()}


def load_pending_theme_batch() -> Optional[Dict]:
    if not os.path.exists(PENDING_THEME_BATCH_FILE):
        return None
    try:
        with open(PENDING_THEME_BATCH_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return None


def save_pending_theme_batch(data: Dict):
    try:
        with open(PENDING_THEME_BATCH_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        print(f"⚠️ Failed to save pending theme batch metadata: {e}")


def clear_pending_theme_batch():
    try:
        if os.path.exists(PENDING_THEME_BATCH_FILE):
            os.remove(PENDING_THEME_BATCH_FILE)
    except Exception:
        pass


def process_pending_theme_batch(api_key: str):
    """Check if a previously submitted theme batch has completed and cache its results."""
    pending = load_pending_theme_batch()
    if not pending:
        return

    batch_id = pending['batch_id']
    print(f"🔄 Checking pending theme batch {batch_id}...")

    client = anthropic.Anthropic(api_key=api_key)
    try:
        batch_job = client.messages.batches.retrieve(batch_id)
    except Exception as e:
        print(f"  ⚠️ Failed to retrieve batch: {e}")
        return

    if batch_job.processing_status != "ended":
        print(f"  ⏳ Batch still processing ({batch_job.processing_status}), will retry next run")
        return

    print(f"  ✅ Batch complete, writing theme scores to cache...")

    theme_cache = load_theme_score_cache()
    now_iso = datetime.now(timezone.utc).isoformat()

    article_batches = {b['custom_id']: b['articles'] for b in pending['article_batches']}
    schedule_labels = pending['schedule_labels']

    results_processed = 0
    for result in client.messages.batches.results(batch_id):
        custom_id = result.custom_id
        batch_articles = article_batches.get(custom_id, [])

        if result.result.type != "succeeded":
            for art in batch_articles:
                for label in schedule_labels.values():
                    key = f"{art['link']}:::{label}"
                    if key not in theme_cache:
                        theme_cache[key] = {'score': 50, 'cached_at': now_iso}
            continue

        api_usage.record_claude_usage(result.result.message.usage, batch=True)
        response_text = result.result.message.content[0].text.strip()
        if response_text.startswith('```'):
            lines = response_text.splitlines()
            inner = lines[1:]
            if inner and inner[-1].strip() == '```':
                inner = inner[:-1]
            response_text = '\n'.join(inner).strip()
        _start, _end = response_text.find('['), response_text.rfind(']') + 1
        if _start != -1 and _end > _start:
            response_text = response_text[_start:_end]

        try:
            scores = json.loads(response_text)
            scored_in_batch = set()
            for score_data in scores:
                idx = score_data.get('article', 0) - 1
                if 0 <= idx < len(batch_articles):
                    art = batch_articles[idx]
                    scored_in_batch.add(idx)
                    for day, label in schedule_labels.items():
                        theme_score = int(score_data.get(day, 50))
                        theme_cache[f"{art['link']}:::{label}"] = {
                            'score': theme_score,
                            'cached_at': now_iso
                        }
            for idx, art in enumerate(batch_articles):
                if idx not in scored_in_batch:
                    for label in schedule_labels.values():
                        key = f"{art['link']}:::{label}"
                        if key not in theme_cache:
                            theme_cache[key] = {'score': 50, 'cached_at': now_iso}
            results_processed += len(batch_articles)
        except (json.JSONDecodeError, Exception) as e:
            print(f"  ⚠️ Error parsing results for {custom_id}: {e}")

    save_theme_score_cache(theme_cache)
    clear_pending_theme_batch()
    print(f"  📊 Cached theme scores for {results_processed} articles from completed batch")


def parse_opml(opml_path: str) -> List[Dict[str, str]]:
    """Extract RSS feed URLs from OPML file"""
    import xml.etree.ElementTree as ET
    
    feeds = []
    tree = ET.parse(opml_path)
    root = tree.getroot()
    
    for outline in root.findall(".//outline[@type='rss']"):
        feed_url = outline.get('xmlUrl')
        feed_title = outline.get('title') or outline.get('text')
        html_url = outline.get('htmlUrl', '')
        
        if feed_url:
            feeds.append({
                'url': feed_url,
                'title': feed_title,
                'html_url': html_url
            })
    
    print(f"📚 Found {len(feeds)} feeds in OPML")
    return feeds




def _fetch_article_excerpt(url: str, max_chars: int = 600) -> str:
    """Fetch an article page and return a plain-text excerpt of the body.

    Used as a fallback when the RSS description is missing or too short — most
    commonly for local BC news sources that omit descriptions from their feeds.
    Returns '' on any failure so callers can treat it as optional.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,*/*',
        }
        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Try common article-body selectors in order of specificity
        for sel in ('article', 'div.article-body', 'div.entry-content',
                    'div.post-content', 'div.story-content', 'main'):
            elem = soup.select_one(sel)
            if not elem:
                continue
            for noise in elem.find_all(['nav', 'script', 'style', 'figure',
                                        'aside', 'footer', 'form']):
                noise.decompose()
            text = ' '.join(elem.get_text(' ', strip=True).split())
            if len(text) >= 80:
                return _clean_text(text, max_chars=max_chars)

        # Fallback: meta description / og:description
        for attr, key in (({'name': 'description'}, 'content'),
                          ({'property': 'og:description'}, 'content')):
            meta = soup.find('meta', attrs=attr)
            if meta and meta.get(key, ''):
                text = meta[key].strip()
                if len(text) >= 80:
                    return _clean_text(text, max_chars=max_chars)

        return ''
    except Exception:
        return ''


def _enrich_thin_local_articles(articles: List['Article']) -> int:
    """Fetch a body excerpt for thin/empty descriptions from known local BC domains.

    Recovers real article text once a boilerplate tagline has been stripped to ''
    (see _is_tagline_boilerplate), and covers feed/search results that never had a
    usable description to begin with. Used by every fetch path — direct RSS and the
    Brave/Kagi/Google News fallbacks — so local articles get consistent treatment
    regardless of which path sourced them.
    """
    fetched = 0
    for article in articles:
        if (len(article.summary) < 100
                and any(d in article.link for d in _LOCAL_BC_DOMAINS)):
            body = _fetch_article_excerpt(article.link, max_chars=600)
            if body and not _is_tagline_boilerplate(body):
                article.description = body
                article.summary = _clean_text(body, max_chars=300)
                article.excerpt = _clean_text(body, max_chars=600)
                fetched += 1
    return fetched


def _kagi_enrich_articles(
    articles: List['Article'],
    kagi_key: str,
    max_calls: int = 40,
    prescore_keywords: frozenset | None = None,
) -> None:
    """Enrich thin-description articles using Kagi's Extract API before Claude scoring.

    Calls POST https://kagi.com/api/v1/extract with {"pages": [{"url": <url>}]} for:
    - All articles from _LOCAL_BC_DOMAINS (often paywalled, descriptions unreliable)
    - Articles whose description is < 150 chars AND whose title matches at least one
      prescore_keyword (skips off-topic thin stubs that would fail scoring anyway)

    Results are cached 48 h by url_hash so repeated runs don't re-fetch.
    Updates article.description / .summary / .excerpt in-place.
    """
    cache = _extract_cache.load()
    candidates = []
    skipped_gate = 0
    for a in articles:
        if a.url_hash in cache:
            continue
        is_local = any(d in a.link for d in _LOCAL_BC_DOMAINS)
        is_thin = len(a.description.strip()) < 150
        if is_local:
            candidates.append(a)
        elif is_thin:
            if prescore_keywords is None or any(kw in a.title.lower() for kw in prescore_keywords):
                candidates.append(a)
            else:
                skipped_gate += 1
    if skipped_gate:
        print(f"  🔎 Kagi gate: skipped {skipped_gate} thin articles (title mismatch)")
    if not candidates:
        return

    to_fetch = candidates[:max_calls]
    enriched = 0
    error_statuses: dict = {}
    error_bodies: dict = {}
    now_ts = datetime.now(timezone.utc).timestamp()

    for article in to_fetch:
        try:
            api_usage.record_call('kagi')
            resp = requests.post(
                'https://kagi.com/api/v1/extract',
                headers={'Authorization': f'Bearer {kagi_key}', 'Content-Type': 'application/json'},
                json={'pages': [{'url': article.link}]},
                timeout=12,
            )
            resp.raise_for_status()
            data = resp.json().get('data') or []
            page = data[0] if data else {}
            text = (page.get('markdown') or '').strip()
            if len(text) >= 80:
                text = _strip_markdown_links(text)
                article.description = _clean_text(text, max_chars=600)
                article.summary = _clean_text(text, max_chars=300)
                article.excerpt = _clean_text(text, max_chars=600)
                cache[article.url_hash] = {'text': article.description, 'timestamp': now_ts}
                enriched += 1
            else:
                cache[article.url_hash] = {'text': '', 'timestamp': now_ts}
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else '?'
            error_statuses[status] = error_statuses.get(status, 0) + 1
            if status not in error_bodies and e.response is not None:
                error_bodies[status] = e.response.text.strip()[:1000]
        except Exception:
            pass

    _extract_cache.save(cache)
    if enriched:
        print(f"  🔍 Kagi Summarizer: enriched {enriched}/{len(to_fetch)} thin articles")
    if error_statuses:
        summary = ', '.join(f"HTTP {status} x{count}" for status, count in error_statuses.items())
        print(f"  ✗ Kagi Summarizer: {summary}")
        for status, body in error_bodies.items():
            print(f"     HTTP {status} body: {body}")


def _try_wlt_selector(soup, container_sel, link_sel, title_sel, desc_sel, img_sel, cache):
    """Attempt to extract articles using a specific set of CSS selectors.

    Returns a list of article dicts and the updated cache, or an empty list if
    no containers matched.
    """
    containers = soup.select(container_sel)
    if not containers:
        return []

    articles = []
    for article_div in containers[:10]:
        try:
            link_elem = article_div.select_one(link_sel) if link_sel else article_div.find('a')
            if not link_elem:
                continue

            href = link_elem.get('href', '').strip()
            if not href:
                continue
            # Build absolute URL
            if href.startswith('http'):
                full_url = href
            else:
                full_url = f"{WLT_BASE_URL}{href}"

            # Skip non-wltribune links (ads, external)
            if 'wltribune.com' not in full_url:
                continue

            url_hash = hashlib.md5(full_url.encode()).hexdigest()
            if url_hash in cache:
                articles.append(cache[url_hash])
                continue

            title_elem = article_div.select_one(title_sel) if title_sel else None
            title = title_elem.get_text(strip=True) if title_elem else link_elem.get_text(strip=True)

            desc_elem = article_div.select_one(desc_sel) if desc_sel else None
            description = desc_elem.get_text(strip=True) if desc_elem else ''

            img_elem = article_div.select_one(img_sel) if img_sel else None
            image_url = None
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src', '')
                if image_url and image_url.startswith('/'):
                    image_url = f"{WLT_BASE_URL}{image_url}"

            if title and full_url:
                # WLT listing pages often have stub descriptions.  Fetch the
                # article body so the podcast generator has real source text.
                if len(description) < 100:
                    body = _fetch_article_excerpt(full_url, max_chars=600)
                    if body:
                        description = body

                article_data = {
                    'title': title,
                    'link': full_url,
                    'description': description,
                    'summary': _clean_text(description, max_chars=300),
                    'excerpt': _clean_text(description, max_chars=600),
                    'image': image_url,
                    'timestamp': datetime.now(timezone.utc).timestamp()
                }
                articles.append(article_data)
                cache[url_hash] = article_data

        except Exception as e:
            print(f"  ⚠️ Error parsing WLT article: {e}")
            continue

    return articles


def scrape_wlt_news() -> List[Dict]:
    """Scrape Williams Lake Tribune news page.

    Tries multiple CSS selector patterns in order so the scraper degrades
    gracefully when the site layout changes.  When all patterns fail it logs
    a snippet of visible text to aid debugging.
    """
    cache = _wlt_cache.load()

    # Ordered list of (container, link, title, desc, img) selector tuples.
    # Add new patterns at the top when the site redesigns; keep old ones as
    # fallbacks so a partial match still surfaces articles.
    SELECTOR_PATTERNS = [
        # Black Press Media 2024+ pattern
        ('div.article-card', 'a.article-card__link', 'h3.article-card__headline',
         'div.article-card__details', 'img.article-card__image'),
        # Black Press Media alternate card style
        ('div.article-card--horizontal', 'a', 'h3', 'p.article-card__description', 'img'),
        # Generic article list items (many BP sites)
        ('li.article-list__item', 'a', 'h3', 'p', 'img'),
        # Story/post grid
        ('div.story', 'a.story__link', 'h2.story__headline', 'p.story__excerpt', 'img'),
        # WordPress-style post entries
        ('article', 'a[rel="bookmark"]', 'h2.entry-title', 'div.entry-summary', 'img'),
        # Very generic fallback: any <article> tag with a headline link
        ('article', 'a', 'h2', 'p', 'img'),
    ]

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-CA,en;q=0.9',
        }

        response = requests.get(WLT_NEWS_URL, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []

        for container_sel, link_sel, title_sel, desc_sel, img_sel in SELECTOR_PATTERNS:
            articles = _try_wlt_selector(soup, container_sel, link_sel, title_sel, desc_sel, img_sel, cache)
            if articles:
                print(f"📰 Williams Lake Tribune: {len(articles)} articles (selector: {container_sel!r})")
                break

        if not articles:
            # Log a snippet of the page to aid selector debugging
            body_text = ' '.join(soup.get_text(' ', strip=True).split())[:300]
            print(f"⚠️ Williams Lake Tribune: 0 articles scraped — all selector patterns failed")
            print(f"   Page text preview: {body_text!r}")

        _wlt_cache.save(cache)
        return articles

    except Exception as e:
        print(f"⚠️ Failed to scrape Williams Lake Tribune: {e}")
        return []


class _AttrDict:
    """Minimal dict-like entry object that supports both .get() and attribute access.

    Used to construct Article objects from non-feedparser sources (e.g. Brave Search).
    Attribute access returns None for missing keys so Article's hasattr() guards work.
    """
    def __init__(self, data: dict):
        object.__setattr__(self, '_data', data)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __getattr__(self, name):
        return self._data.get(name)


# The browser identity we lead with. Most feeds are served by CDNs that
# reject the python-requests default outright.
_BROWSER_UA = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
)

# ...and the identity we fall back to on a 403. WAFs that block a browser UA
# coming from a datacenter IP (Cloudflare bot-fight, Wordfence) routinely
# allowlist self-identifying feed readers, because publishers want to be
# syndicated even when they don't want to be scraped. Declaring what we
# actually are is both more honest and, empirically, more likely to be let
# through — and it costs nothing, unlike the search-API fallbacks below.
_FEED_READER_UA = (
    'SuperRSSCurator/1.0 (+https://zirnhelt.github.io/super-rss-feed/) '
    'RSS/Atom feed reader'
)

_FEED_ACCEPT = 'application/rss+xml, application/atom+xml, application/xml, text/xml, */*'

# Conventional feed locations, probed only when a feed 404s and the site
# advertises no <link rel="alternate">. Ordered by how common they are.
_COMMON_FEED_PATHS = (
    '/feed/', '/rss/', '/rss.xml', '/feed.xml', '/atom.xml', '/index.xml',
    '/blog/feed/', '/news/feed/', '/feeds/posts/default',
)

# Cap on HTTP requests spent looking for one moved feed, so rediscovery stays
# cheap and polite even when every guess misses.
_MAX_DISCOVERY_PROBES = 6


def _fetch_via_brave_fallback(feed: Dict, cutoff_date: datetime) -> List[Article]:
    """Query Brave Search for recent articles from a domain that blocked direct RSS access.

    Used when the RSS feed returns 403. Returns Article objects populated with
    title, url, and description from Brave's index. BRAVE_API_KEY must be set.
    """
    if os.environ.get('USE_SEARCH_APIS', 'true').lower() != 'true':
        return []

    brave_key = os.environ.get('BRAVE_API_KEY', '')
    if not brave_key:
        return []

    domain = urlparse(feed.get('url', '')).netloc.replace('www.', '')
    if not domain:
        return []

    params = {'q': f'site:{domain}', 'count': 10, 'freshness': 'pw'}
    headers = {'X-Subscription-Token': brave_key, 'Accept': 'application/json'}

    global _brave_call_count, _brave_quota_exceeded
    if _brave_quota_exceeded:
        return []
    _brave_call_count += 1
    api_usage.record_call('brave')
    try:
        resp = requests.get(
            'https://api.search.brave.com/res/v1/web/search',
            headers=headers, params=params, timeout=15
        )
        resp.raise_for_status()
        results = resp.json().get('web', {}).get('results', [])
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 402:
            _brave_quota_exceeded = True
            print(f"    ⚠️  Brave fallback failed for {domain}: 402 — quota exceeded, disabling Brave for this run")
        else:
            print(f"    ⚠️  Brave fallback failed for {domain}: {e}")
        return []
    except Exception as e:
        print(f"    ⚠️  Brave fallback failed for {domain}: {e}")
        return []

    articles = []
    for r in results:
        pub_date = None
        pub_str = r.get('published_time') or ''
        if pub_str:
            try:
                pub_date = datetime.fromisoformat(pub_str.replace('Z', '+00:00'))
            except Exception:
                pass
        if pub_date and pub_date < cutoff_date:
            continue

        desc = (r.get('description') or '')[:500]
        entry = _AttrDict({
            'title': r.get('title', '').strip(),
            'link': r.get('url', ''),
            'description': desc,
            'summary': desc,
            'published': pub_str,
            'published_parsed': None,
            'updated_parsed': None,
            'media_thumbnail': [],
            'media_content': [],
            'enclosures': [],
            'tags': [],
        })

        if not entry.get('title') or not entry.get('link'):
            continue

        try:
            article = Article(entry, feed['title'], feed.get('html_url', ''), feed['url'])
            if pub_date:
                article.pub_date = pub_date
            articles.append(article)
        except Exception:
            continue

    # Search snippets for local BC domains are often the site-wide tagline (already
    # stripped in Article.__init__) rather than real article text — recover it now.
    _enrich_thin_local_articles(articles)
    return articles


def _fetch_via_kagi_fallback(feed: Dict, cutoff_date: datetime) -> List[Article]:
    """Query Kagi Search for recent articles from a domain that blocked direct RSS access.

    Secondary fallback used after Brave returns 0 results. Uses site:domain query.
    KAGI_API_KEY must be set.
    """
    if os.environ.get('USE_SEARCH_APIS', 'true').lower() != 'true':
        return []

    kagi_key = os.environ.get('KAGI_API_KEY', '')
    if not kagi_key:
        return []

    domain = urlparse(feed.get('url', '')).netloc.replace('www.', '')
    if not domain:
        return []

    api_usage.record_call('kagi')
    try:
        resp = requests.post(
            'https://kagi.com/api/v1/search',
            headers={'Authorization': f'Bearer {kagi_key}'},
            json={'query': f'site:{domain}', 'limit': 10},
            timeout=15,
        )
        resp.raise_for_status()
        results = (resp.json().get('data') or {}).get('search') or []
    except Exception as e:
        print(f"    ⚠️  Kagi fallback failed for {domain}: {e}")
        return []

    articles = []
    for r in results:
        pub_date = None
        pub_str = r.get('published') or ''
        if pub_str:
            try:
                pub_date = datetime.fromisoformat(pub_str.replace('Z', '+00:00'))
            except Exception:
                pass
        if pub_date and pub_date < cutoff_date:
            continue

        desc = (r.get('snippet') or '')[:500]
        entry = _AttrDict({
            'title': (r.get('title') or '').strip(),
            'link': r.get('url', ''),
            'description': desc,
            'summary': desc,
            'published': pub_str,
            'published_parsed': None,
            'updated_parsed': None,
            'media_thumbnail': [],
            'media_content': [],
            'enclosures': [],
            'tags': [],
        })

        if not entry.get('title') or not entry.get('link'):
            continue

        try:
            article = Article(entry, feed['title'], feed.get('html_url', ''), feed['url'])
            if pub_date:
                article.pub_date = pub_date
            articles.append(article)
        except Exception:
            continue

    # Search snippets for local BC domains are often the site-wide tagline (already
    # stripped in Article.__init__) rather than real article text — recover it now.
    _enrich_thin_local_articles(articles)
    return articles


def _fetch_via_google_news_fallback(feed: Dict, cutoff_date: datetime) -> List[Article]:
    """Fetch recent articles for a blocked domain via Google News RSS search.

    Keyless last resort after Brave/Kagi, so it also covers manual runs where
    USE_SEARCH_APIS is off. Links are opaque news.google.com proxy URLs, which
    downstream stages already exclude from podcast pools and cross-run
    retention — the articles still reach the category feeds.
    """
    domain = urlparse(feed.get('url', '')).netloc.replace('www.', '')
    if not domain:
        return []

    lookback_days = max(1, (datetime.now(timezone.utc) - cutoff_date).days + 1)
    query = quote(f'site:{domain} when:{lookback_days}d')
    gn_url = f'https://news.google.com/rss/search?q={query}&hl=en-CA&gl=CA&ceid=CA:en'

    headers = {'User-Agent': _BROWSER_UA, 'Accept': _FEED_ACCEPT}
    try:
        response = requests.get(gn_url, headers=headers, timeout=10)
        response.raise_for_status()
        parsed = feedparser.parse(response.content)
    except Exception as e:
        print(f"    ⚠️  Google News fallback failed for {domain}: {e}")
        return []

    articles = []
    for entry in parsed.entries[:10]:
        try:
            article = Article(entry, feed['title'], feed.get('html_url', ''), gn_url)
        except Exception:
            continue
        if article.pub_date < cutoff_date:
            continue
        if article.should_filter():
            continue
        articles.append(article)

    _enrich_thin_local_articles(articles)
    return articles


def _looks_like_feed(content: bytes) -> bool:
    """True only if the bytes parse as a feed that actually carries entries.

    Guards against soft 404s: many CMSs answer an unknown /feed path with a
    200 HTML error page, which feedparser will happily parse into an empty
    feed. Requiring entries means we can never adopt one as a replacement.
    """
    try:
        parsed = feedparser.parse(content)
    except Exception:
        return False
    return bool(parsed.entries) and bool(parsed.get('version'))


def _fetch_url_bytes(url: str, user_agent: str = _BROWSER_UA) -> Optional[bytes]:
    """GET a URL, returning its body or None on any failure. Never raises."""
    try:
        response = requests.get(
            url,
            headers={'User-Agent': user_agent, 'Accept': _FEED_ACCEPT},
            timeout=10,
        )
        response.raise_for_status()
        return response.content
    except Exception:
        return None


def _autodiscovery_links(page_url: str) -> List[str]:
    """Read a page's <link rel="alternate"> feed advertisements."""
    html = _fetch_url_bytes(page_url)
    if not html:
        return []
    try:
        soup = BeautifulSoup(html, 'html.parser')
    except Exception:
        return []

    links = []
    for tag in soup.find_all('link', rel=lambda v: v and 'alternate' in v):
        mime = (tag.get('type') or '').lower()
        href = tag.get('href')
        if href and ('rss' in mime or 'atom' in mime):
            links.append(urljoin(page_url, href))
    return links


def _discover_feed_url(feed: Dict) -> Optional[str]:
    """Find where a 404ing feed moved to, without spending an API call.

    A 404 means the feed URL is stale, not that the outlet is gone — the usual
    cause is a CMS migration that moved /feed to somewhere else on the same
    site. Search-API fallbacks paper over that at a per-run cost and return
    thin search-index summaries instead of real feed entries; rediscovery
    fixes the cause once, for free, and restores full-fidelity articles.
    """
    old_url = feed.get('url', '')
    parsed = urlparse(old_url)
    if not parsed.netloc:
        return None
    origin = f'{parsed.scheme}://{parsed.netloc}'

    candidates: List[str] = []
    for page in dict.fromkeys(p for p in (feed.get('html_url'), origin) if p):
        candidates.extend(_autodiscovery_links(page))
    candidates.extend(urljoin(origin, path) for path in _COMMON_FEED_PATHS)

    seen = {old_url}
    probes = 0
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if probes >= _MAX_DISCOVERY_PROBES:
            break
        probes += 1
        content = _fetch_url_bytes(candidate)
        if content and _looks_like_feed(content):
            return candidate
    return None


def _articles_from_feed_bytes(
    content: bytes, feed: Dict, cutoff_date: datetime, source_url: str
) -> List[Article]:
    """Turn a fetched feed body into filtered, enriched Article objects."""
    parsed = feedparser.parse(content)

    # Some feeds (e.g. My Cariboo Now) repeat the channel-level description
    # as every item's <description> — sometimes with extra markup like
    # <strong> wrappers — producing identical boilerplate "summaries" that
    # hide the real article content and game keyword-based scoring. Detect
    # and strip that case so the article is treated as having no description
    # (the body-excerpt fetch below then recovers real article text).
    channel_key = _boilerplate_key(
        parsed.feed.get('description', '') or parsed.feed.get('subtitle', '')
    )
    boilerplate_keys = _find_boilerplate_keys(
        [e.get('description', '') or e.get('summary', '') for e in parsed.entries],
        channel_key,
    )

    articles = []
    stripped_boilerplate = 0
    for entry in parsed.entries:
        article = Article(entry, feed['title'], feed['html_url'], source_url)

        if boilerplate_keys and _boilerplate_key(article.description) in boilerplate_keys:
            article.description = ''
            article.summary = ''
            article.excerpt = ''
            stripped_boilerplate += 1

        if article.pub_date < cutoff_date:
            continue

        if article.should_filter():
            continue

        articles.append(article)

    # For known local BC sources with a stub (or just-stripped) description,
    # attempt a body fetch while the article is still within the paywall-free window.
    fetched_excerpts = _enrich_thin_local_articles(articles)

    if articles:
        extra = f", {fetched_excerpts} body excerpts fetched" if fetched_excerpts else ""
        if stripped_boilerplate:
            extra += f", {stripped_boilerplate} boilerplate descriptions stripped"
        print(f"  ✓ {feed['title']}: {len(articles)} articles{extra}")

    return articles


def fetch_feed_articles(feed: Dict, cutoff_date: datetime) -> List[Article]:
    """Fetch and parse articles from a feed.

    Failures escalate through free recovery before paid recovery: a 403 gets
    one retry under a feed-reader identity, a 404 gets free rediscovery of the
    feed's new URL, and only then do the search-API fallbacks run — and those
    are cut off entirely for feeds that have been failing for several runs
    (see FeedHTTPCache.should_skip_paid_fallback), so a permanently dead
    source stops competing for Brave/Kagi quota with recoverable ones.
    """
    # Cache state is always keyed on the OPML URL — that is the feed's stable
    # identity — while the request may go to a rediscovered URL.
    cache_key = feed['url']
    request_url = _feed_http_cache.resolved_url(cache_key) or cache_key

    try:
        if _feed_http_cache.should_skip(cache_key):
            # Two very different reasons to skip. A healthy feed inside its
            # Cache-Control window simply isn't due yet — leave it alone. A
            # feed serving out its failure backoff, though, is producing
            # nothing at all, so still give it the keyless Google News
            # fallback: the backoff exists to stop wasting direct fetches and
            # paid search on a dead source, not to drop its coverage.
            if _feed_http_cache.failure_count(cache_key):
                fallback = _fetch_via_google_news_fallback(feed, cutoff_date)
                if fallback:
                    print(f"  ↩ {feed['title']}: in backoff, Google News fallback → {len(fallback)} articles")
                    return fallback
                print(f"  ⏭ {feed['title']}: skipped (backing off after repeated failures)")
            else:
                print(f"  ⏭ {feed['title']}: skipped (Cache-Control/Retry-After not yet expired)")
            return []

        headers = {'User-Agent': _BROWSER_UA, 'Accept': _FEED_ACCEPT}
        headers.update(_feed_http_cache.request_headers(cache_key))

        response = requests.get(request_url, headers=headers, timeout=10)

        if response.status_code == 304:
            print(f"  ✓ {feed['title']}: 304 Not Modified (no new articles)")
            _feed_http_cache.record_success(cache_key)
            return []

        if response.status_code in (429, 503):
            retry_after = response.headers.get('Retry-After', '3600')
            _feed_http_cache.set_retry_after(cache_key, retry_after)
            response.raise_for_status()

        response.raise_for_status()
        _feed_http_cache.update_from_response(cache_key, response)
        _feed_http_cache.record_success(cache_key)

        return _articles_from_feed_bytes(response.content, feed, cutoff_date, request_url)

    except Exception as e:
        status = (
            e.response.status_code
            if isinstance(e, requests.exceptions.HTTPError) and e.response is not None
            else None
        )
        is_timeout = isinstance(e, (requests.exceptions.ReadTimeout, requests.exceptions.Timeout))
        # ConnectionError covers DNS failures (NameResolutionError) and refused/reset
        # connections — the direct fetch can never work, but the outlet may still be
        # searchable (e.g. a CDN/DNS hiccup, or content mirrored elsewhere).
        is_connection_error = isinstance(e, requests.exceptions.ConnectionError)
        is_dns_failure = is_connection_error and 'NameResolution' in str(e)

        # A rediscovered URL that has itself started failing is stale — forget
        # it so the next run rediscovers from the OPML URL rather than
        # compounding one bad guess into a permanent one.
        if request_url != cache_key:
            _feed_http_cache.clear_resolved_url(cache_key)

        # --- Free recovery, tried before anything that costs money ---------

        # 403: bot-blocked. Retry once as a self-identified feed reader.
        if status == 403:
            content = _fetch_url_bytes(request_url, user_agent=_FEED_READER_UA)
            if content and _looks_like_feed(content):
                print(f"  ↩ {feed['title']}: 403 as browser, allowed as feed reader")
                _feed_http_cache.record_success(cache_key)
                return _articles_from_feed_bytes(content, feed, cutoff_date, request_url)

        # 404/410: the feed moved. Find its new home instead of buying summaries.
        if status in (404, 410):
            discovered = _discover_feed_url(feed)
            if discovered:
                content = _fetch_url_bytes(discovered)
                if content and _looks_like_feed(content):
                    _feed_http_cache.set_resolved_url(cache_key, discovered)
                    _feed_http_cache.record_success(cache_key)
                    print(f"  ↩ {feed['title']}: feed moved → {discovered} (update feeds.opml)")
                    return _articles_from_feed_bytes(content, feed, cutoff_date, discovered)

        # --- Paid recovery, rationed by failure history --------------------

        failures = _feed_http_cache.record_failure(
            cache_key,
            'dns' if is_dns_failure else ('http_%s' % status if status else 'network'),
        )

        # 403: bot-blocked (common from Actions runner IPs). 404: feed URL moved.
        # 421 Misdirected Request: persistent CDN/TLS misconfig (e.g. IndigiNews).
        # 500: origin server error on the feed route specifically — the outlet
        # itself is usually still up and searchable even when its feed 500s.
        # (503 is deliberately excluded: it already gets a Retry-After skip_until
        # circuit breaker above, so hitting the paid API fallback for it too would
        # just burn quota on a source we're already backing off from.)
        should_try_fallback = status in (403, 404, 421, 500) or is_timeout or is_connection_error

        # A feed that has failed this many runs in a row is not having a bad
        # day. Brave is already hitting its 402 quota ceiling mid-run, so every
        # call spent re-confirming a dead source is one denied to a live one.
        skip_paid = _feed_http_cache.should_skip_paid_fallback(cache_key)
        if should_try_fallback and skip_paid:
            print(f"  ⚠ {feed['title']}: {failures} consecutive failures — free fallback only")

        if should_try_fallback and not skip_paid and os.environ.get('BRAVE_API_KEY'):
            fallback = _fetch_via_brave_fallback(feed, cutoff_date)
            if fallback:
                print(f"  ↩ {feed['title']}: Brave fallback → {len(fallback)} articles")
                return fallback
            print(f"  ⚠ {feed['title']}: Brave fallback returned 0 articles")

        if should_try_fallback and not skip_paid and os.environ.get('KAGI_API_KEY'):
            fallback = _fetch_via_kagi_fallback(feed, cutoff_date)
            if fallback:
                print(f"  ↩ {feed['title']}: Kagi fallback → {len(fallback)} articles")
                return fallback

        if should_try_fallback:
            fallback = _fetch_via_google_news_fallback(feed, cutoff_date)
            if fallback:
                print(f"  ↩ {feed['title']}: Google News fallback → {len(fallback)} articles")
                return fallback

        # Nothing worked. A dead domain or a feed that no longer exists cannot
        # fix itself, so stop polling it every run — the ladder still retries
        # periodically in case the outlet comes back.
        if is_dns_failure or status in (404, 410):
            backoff = _feed_http_cache.set_failure_backoff(cache_key)
            if backoff:
                print(f"  ⏸ {feed['title']}: backing off {backoff // 3600}h ({failures} consecutive failures)")

        print(f"  ✗ {feed['title']}: {e}")
        return []



# Dedup rank per source type. Lower = wins ties. Every type declared in
# config/source_preferences.json must appear here, otherwise it silently lands
# in the unclassified bucket and can outrank types it should lose to.
_SOURCE_TYPE_DEDUP_RANK = {
    'preferred_local': 1,
    'print': 3,
    'maker_gadget': 4,       # specialty gadget/repair outlets: below newspapers
    'broadcast': 6,
    'personal_listicle': 7,  # thin first-person listicles: never the best version
}
_UNCLASSIFIED_DEDUP_RANK = 5

# Subscriber tier, used only to break ties between sources of equal type rank.
# Lower = wins. Paid subscriptions beat free Apple News channels, which beat
# sources we have no access to at all.
_SUBSCRIBER_DEDUP_RANK = {
    'Williams Lake Tribune': 0,
    'New York Times': 1,
    'Apple News+': 2,
    'Apple News': 3,
}
_UNRANKED_SUBSCRIBER_RANK = 4   # subscribed, but the label is not listed above
_NO_SUBSCRIBER_RANK = 9         # no paywall-free access


def _subscriber_priority(article: Article) -> int:
    """Return the subscriber tiebreak rank for an article's source."""
    label = SUBSCRIBER_ACCESS.get(article.source)
    if not label:
        return _NO_SUBSCRIBER_RANK
    if label in _SUBSCRIBER_DEDUP_RANK:
        return _SUBSCRIBER_DEDUP_RANK[label]
    if label.startswith('Apple News'):
        return _SUBSCRIBER_DEDUP_RANK['Apple News']
    return _UNRANKED_SUBSCRIBER_RANK


def _source_priority(article: Article) -> Tuple[int, int]:
    """Return sort key for dedup ordering. Lower = processed first = wins ties.

    The first element is the source-type rank; the second breaks ties between
    equally ranked sources in favour of outlets we can actually read (direct
    subscription > Apple News+ > free Apple News channel > no access).
    """
    source_map = SOURCE_PREFS.get('source_map', {})
    source_type = source_map.get(article.source)
    sub_rank = _subscriber_priority(article)
    # WLT scraper articles are pre-scored at local_priority_score before dedup runs.
    # RSS feeds for the same paper (e.g. www.wltribune.com/feed/) share the same
    # source name and therefore the same preferred_local type, so without this
    # check the RSS version (fetched first) would win and the richer scraper
    # version would be silently dropped as a duplicate.
    if source_type == 'preferred_local' and article.score == LIMITS.get('local_priority_score', 100):
        return (0, sub_rank)
    # Subscribed / preferred local paper via RSS
    if source_type == 'preferred_local':
        return (1, sub_rank)
    # Other explicitly local-priority articles, whatever their source type
    if article.category == 'local' or article.score == LIMITS.get('local_priority_score', 100):
        return (2, sub_rank)
    return (_SOURCE_TYPE_DEDUP_RANK.get(source_type, _UNCLASSIFIED_DEDUP_RANK), sub_rank)


def _fuzz_ratio(a: str, b: str) -> int:
    return int(SequenceMatcher(None, a, b).ratio() * 100)


def _token_sort_ratio(a: str, b: str) -> int:
    return _fuzz_ratio(' '.join(sorted(a.split())), ' '.join(sorted(b.split())))


def deduplicate_articles(articles: List[Article]) -> List[Article]:
    """Remove duplicate articles based on URL and title similarity.

    Uses three complementary signals, checked in order:
      1. Exact URL hash match (canonical URL, tracking params stripped).
      2. Fuzzy string similarity on the full title (_fuzz_ratio /
         token_sort_ratio > 78%).  Catches wire-service reprints with
         near-identical wording.
      3. Term-set containment similarity ≥ 45% with at least 3 shared
         significant words.  Catches same-story coverage across outlets
         that write completely different headlines (e.g. five tech blogs
         all covering the same product launch with unique titles).

    Sorts by source preference first so that local / print sources win
    when two outlets cover the same story, with subscriber access breaking
    ties between sources of equal rank.
    """
    # Preferred sources get processed first so they survive dedup
    sorted_articles = sorted(articles, key=_source_priority)

    seen_urls = set()
    seen_entries = []   # list of (title_normalized, title_terms, Article)
    unique = []

    for article in sorted_articles:
        if article.url_hash in seen_urls:
            continue

        is_duplicate = False
        swap_idx = None

        for idx, (seen_title, seen_terms, seen_article) in enumerate(seen_entries):
            # Signal 1 & 2: fuzzy string similarity on full title
            string_sim = max(
                _fuzz_ratio(article.title_normalized, seen_title),
                _token_sort_ratio(article.title_normalized, seen_title),
            )
            # Signal 3: term-set containment (handles completely different headlines)
            overlap = (
                _story_overlap(article.title_terms, seen_terms)
                if len(article.title_terms) >= 3 and len(seen_terms) >= 3
                else 0.0
            )
            shared_terms = len(article.title_terms & seen_terms) if seen_terms else 0

            is_story_match = (
                string_sim > LIMITS.get('dedup_fuzzy_threshold', 78)
                or (overlap >= LIMITS.get('dedup_overlap_high', 0.55) and shared_terms >= LIMITS.get('dedup_min_terms_high', 2))
                or (overlap >= LIMITS.get('dedup_overlap_low', 0.40) and shared_terms >= LIMITS.get('dedup_min_terms_low', 3))
            )

            if is_story_match:
                # Keep the higher-priority source; swap if current article wins.
                if _source_priority(article) < _source_priority(seen_article):
                    swap_idx = idx
                else:
                    is_duplicate = True
                break

        if swap_idx is not None:
            # Replace the weaker duplicate in-place
            replaced = seen_entries[swap_idx][2]
            unique.remove(replaced)
            seen_entries.pop(swap_idx)
            # Fall through to add the current article below

        if not is_duplicate:
            seen_urls.add(article.url_hash)
            seen_entries.append((article.title_normalized, article.title_terms, article))
            unique.append(article)

    print(f"🔄 Deduplication: {len(articles)} → {len(unique)} articles")
    return unique


def dedup_across_categories(categorized: dict) -> dict:
    """Drop news articles that are covered by a more specific category.

    After categorization, the same story can appear in both 'news' (via a
    Google News proxy URL or generic outlet) and a specific category (via the
    original source).  Specific categories always win: any news article whose
    title is a story-match for an article in ai-tech, climate, homelab, etc.
    is silently dropped from news.
    """
    overlap_thresh = LIMITS.get('cross_category_overlap_threshold', 0.45)
    min_terms = LIMITS.get('cross_category_min_terms', 2)
    fuzzy_thresh = LIMITS.get('dedup_fuzzy_threshold', 78)

    specific_cats = [c for c in CATEGORIES if c not in ('news', 'local')]
    specific_articles = [a for cat in specific_cats for a in categorized.get(cat, [])]

    if not specific_articles:
        return categorized

    filtered_news = []
    dropped = 0
    for news_art in categorized.get('news', []):
        dominated = False
        for spec_art in specific_articles:
            sim = max(
                _fuzz_ratio(news_art.title_normalized, spec_art.title_normalized),
                _token_sort_ratio(news_art.title_normalized, spec_art.title_normalized),
            )
            ov = (
                _story_overlap(news_art.title_terms, spec_art.title_terms)
                if len(news_art.title_terms) >= min_terms and len(spec_art.title_terms) >= min_terms
                else 0.0
            )
            shared = len(news_art.title_terms & spec_art.title_terms)
            if sim > fuzzy_thresh or (ov >= overlap_thresh and shared >= min_terms):
                dominated = True
                break
        if dominated:
            dropped += 1
        else:
            filtered_news.append(news_art)

    if dropped:
        print(f"🔀 Cross-category dedup: removed {dropped} news articles covered by specific categories")
    categorized['news'] = filtered_news
    return categorized


# Content type preference order for dedup: original > aggregated > summary
_CONTENT_TYPE_RANK = {
    'analysis': 6, 'feature': 5, 'opinion': 4, 'breaking': 3, 'wire': 2, 'recap': 1
}


def _dedup_story_key(article: Article) -> Tuple[int, float, int]:
    """Sort key for story-group dedup (max wins): content_type, Q score, access."""
    ct = getattr(article, 'content_type', None) or ''
    q = getattr(article, 'quality', 0) or getattr(article, 'score', 0)
    # Negated so that a lower (better) subscriber rank sorts higher under max().
    return (_CONTENT_TYPE_RANK.get(ct, 0), q, -_subscriber_priority(article))


def dedup_by_story_group(articles: List[Article]) -> List[Article]:
    """Collapse articles that Claude labelled with the same story_group.

    Within a story group, prefer original reporting over wire reprints using
    content_type hierarchy (analysis > feature > opinion > breaking > wire > recap).
    Tiebreak within same type by quality score, then by subscriber access so a
    readable version wins over one behind a paywall.
    """
    groups: dict = defaultdict(list)
    ungrouped = []
    for a in articles:
        sg = getattr(a, 'story_group', None)
        if sg:
            groups[sg.lower().strip()].append(a)
        else:
            ungrouped.append(a)

    result = ungrouped[:]
    collapsed = 0
    for group_articles in groups.values():
        best = max(group_articles, key=_dedup_story_key)
        result.append(best)
        collapsed += len(group_articles) - 1

    if collapsed:
        print(f"📰 Story-group dedup: collapsed {collapsed} duplicate event articles")
    return result


def dedup_by_term_cluster(
    articles: List[Article],
    overlap_threshold: float,
    max_per_cluster: int,
) -> List[Article]:
    """Greedy term-cluster dedup: cap articles that share high term overlap.

    Catches breaking-news floods where many sources cover the same event with
    different enough headlines to survive fuzzy dedup and story_group collapse
    (e.g. inconsistent Claude labeling or null story_group).

    Sorted by score descending. Each candidate is skipped if it matches
    >= max_per_cluster already-selected articles at >= overlap_threshold
    containment similarity.
    """
    sorted_arts = sorted(articles, key=lambda a: a.score, reverse=True)
    selected: List[Article] = []
    dropped = 0

    for candidate in sorted_arts:
        if not candidate.title_terms or len(candidate.title_terms) < 3:
            selected.append(candidate)
            continue
        cluster_matches = sum(
            1 for s in selected
            if s.title_terms
            and _story_overlap(candidate.title_terms, s.title_terms) >= overlap_threshold
        )
        if cluster_matches >= max_per_cluster:
            dropped += 1
        else:
            selected.append(candidate)

    if dropped:
        print(f"🗞️  Term-cluster dedup: dropped {dropped} near-duplicate event articles")
    return selected


def categorize_article(title: str, description: str) -> Optional[str]:
    """Determine article category using keyword rules"""
    text = f"{title} {description}".lower()
    
    for category, rules in CATEGORY_RULES.items():
        if category not in CATEGORIES:
            continue
        
        include_keywords = [kw.lower() for kw in rules.get('include', [])]
        exclude_keywords = [kw.lower() for kw in rules.get('exclude', [])]

        has_include = any(keyword in text for keyword in include_keywords)
        has_exclude = any(keyword in text for keyword in exclude_keywords)
        
        if has_include and not has_exclude:
            return category
    
    return None


def semantic_dedup_articles(articles: List[Article]) -> List[Article]:
    """Passthrough — embedding-based dedup removed.

    URL-hash + fuzzy-title + term-set dedup already handles near-duplicates.
    The 0.92 cosine threshold caught almost nothing on the already-reduced
    candidate set and cost ~6 Cohere Embed calls per run.
    """
    return articles


def score_articles_with_cohere(articles: List[Article]) -> List[Article]:
    """Score and categorize articles using Cohere Rerank + embedding story clustering.

    Drop-in replacement for score_articles_with_claude() when COHERE_API_KEY is set.
    Uses the same scored_articles_cache so switching back to Claude on subsequent
    runs is safe (cache entries include score, category, and a null story_group).
    """
    if not articles:
        return []

    cache = _scored_cache.load()

    try:
        interests = config_loader.load_news_interests().strip()
    except Exception:
        interests = "Technology, science, climate, local news"

    scored_articles: List[Article] = []
    uncached: List[Article] = []

    for article in articles:
        if article.url_hash in cache:
            entry = cache[article.url_hash]
            # Extract score: entry['score'] is a tuple (int, str), get first element
            score_tuple = entry['score']
            score_val = score_tuple[0] if isinstance(score_tuple, tuple) else score_tuple
            article.score = int(score_val) if score_val else 0
            article.category = entry['category']
            # Synthesize Q/R/L from composite score — Cohere has no dimensional breakdown.
            # Using score as a proxy keeps calibration histograms populated without
            # changing apply_dimension_adjustments behaviour (cohere_scored=True bypasses
            # the composite recompute there).
            article.quality = int(score_val) if score_val else 0
            article.relevance = int(score_val) if score_val else 0
            article.local = entry.get('local', 0)
            article.content_type = entry.get('content_type')
            article.story_group = entry.get('story_group')
            article.cohere_scored = True
            scored_articles.append(article)
        else:
            uncached.append(article)

    if uncached:
        print(f"\n🔮 Scoring {len(uncached)} new articles with Cohere Rerank...")
        print(f"   (using cache for {len(scored_articles)} articles)")

        rerank_scores = cohere_integration.score_with_rerank(uncached, interests)
        timestamp = datetime.now(timezone.utc).timestamp()

        for article in uncached:
            score, _ = rerank_scores.get(article.url_hash, (50, ''))
            article.score = score
            article.quality = score   # synthesized: Q/R set to composite as best proxy
            article.relevance = score
            article.local = 0
            article.cohere_scored = True
            article.category = categorize_article(article.title, article.description) or 'news'
            cache[article.url_hash] = {
                'score': article.score,
                'quality': article.quality,
                'relevance': article.relevance,
                'local': article.local,
                'category': article.category,
                'story_group': None,
                'timestamp': timestamp,
            }
            scored_articles.append(article)

    _scored_cache.save(cache)

    # Assign story groups only for newly-scored articles. Cached articles restore
    # their story_group from the cache entry above (story_group: None means no
    # cluster was found last time, which is fine). Embedding only the uncached
    # subset avoids re-embedding the full ~500-article set every run.
    if uncached:
        print(f"   🔗 Clustering story groups for {len(uncached)} new articles...")
        embeddings = cohere_integration.embed_articles(uncached)
        cohere_integration.cluster_story_groups(uncached, embeddings)
        # Persist the newly-assigned story_group labels back to the cache.
        updated_cache = _scored_cache.load()
        for article in uncached:
            if article.url_hash in updated_cache and article.story_group:
                updated_cache[article.url_hash]['story_group'] = article.story_group
        _scored_cache.save(updated_cache)

    return scored_articles


# ════════════════════════════════════════════════════════════════════════════════
# Hybrid Scoring: Cohere + Claude
# ════════════════════════════════════════════════════════════════════════════════

def score_articles_with_claude(articles: List[Article], api_key: str) -> List[Article]:
    """
    Score articles using configured mode: pure Cohere, hybrid, or pure Claude.
    
    Dispatches to the appropriate scoring strategy based on config.
    """
    config = load_scoring_mode_config()
    mode = config.get("mode", "cohere-only")
    
    if mode == "cohere-only":
        # Pure Cohere path (existing behavior)
        if cohere_integration.is_enabled():
            return score_articles_with_cohere(articles)
        else:
            # Fallback if no Cohere API key
            return score_articles_with_claude_pure(articles, api_key)
    
    elif mode == "gated":
        # Absolute quality gate + interest-ranked deep scoring
        return score_articles_gated(articles, api_key, config)

    elif mode == "hybrid":
        # Hybrid Cohere + Claude (legacy rank-percentile eligibility; kept for rollback)
        return score_articles_hybrid(articles, api_key, config)

    elif mode == "claude-only":
        # Pure Claude (fallback for testing)
        return score_articles_with_claude_pure(articles, api_key)
    
    else:
        print(f"  ⚠️ Unknown scoring mode: {mode}, using cohere-only")
        if cohere_integration.is_enabled():
            return score_articles_with_cohere(articles)
        return score_articles_with_claude_pure(articles, api_key)


def score_quality_gate(articles: List[Article], api_key: str) -> None:
    """Assign an absolute, interest-independent newsworthiness score (article.q_gate).

    This is the shared eligibility signal for both the news head and the podcast
    pool: unlike the Cohere percentile scores it does not depend on how the rest
    of the batch looks, and unlike the interest composite it does not depend on
    the personal interest profile. Local articles bypass the gate entirely
    (q_gate stays None) — local priority rules own their eligibility.

    Fail-open: on API failure articles keep q_gate=None and downstream gates
    treat missing values as passing, so an outage degrades to the legacy
    behavior instead of emptying every feed.
    """
    if not articles or not api_key:
        return

    gate_cfg = LIMITS.get('quality_gate', {})
    batch_size = int(gate_cfg.get('batch_size', 30))
    charter = config_loader.load_quality_charter().strip()
    cache = _scored_cache.load()
    local_signals = [s.lower() for s in FILTERS.get('local_signals', [])]

    to_score: List[Article] = []
    cached_hits = 0
    bypassed = 0
    for article in articles:
        entry = cache.get(article.url_hash)
        if isinstance(entry, dict) and entry.get('q_gate') is not None:
            article.q_gate = int(entry['q_gate'])
            cached_hits += 1
            continue
        title_l = article.title.lower()
        if article.category == 'local' or any(s in title_l for s in local_signals):
            bypassed += 1
            continue
        to_score.append(article)

    print(f"\n🚪 Quality gate: {len(to_score)} to score "
          f"({cached_hits} cached, {bypassed} local bypass)")
    if not to_score:
        return

    client = anthropic.Anthropic(api_key=api_key)
    system_blocks = [{
        "type": "text",
        "text": charter,
        "cache_control": {"type": "ephemeral", "ttl": "1h"}
    }]

    timestamp = datetime.now(timezone.utc).timestamp()
    scored = 0
    for i in range(0, len(to_score), batch_size):
        batch = to_score[i:i + batch_size]
        articles_text = "\n\n".join(
            f"Article {j+1}:\nTitle: {a.title}\nSource: {a.source}\n"
            f"Description: {(a.description or '')[:200]}"
            for j, a in enumerate(batch)
        )
        prompt = (
            "Score each article's absolute newsworthiness/quality per the charter (0-100). "
            "Respond with ONLY a JSON array, no other text:\n"
            '[{"a": 1, "q": 55}, {"a": 2, "q": 12}]\n\n'
            f"Articles:\n{articles_text}"
        )
        try:
            response = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=700,
                system=system_blocks,
                messages=[{"role": "user", "content": prompt}]
            )
            api_usage.record_claude_usage(response.usage)
            response_text = response.content[0].text.strip()
            _start, _end = response_text.find('['), response_text.rfind(']') + 1
            if _start != -1 and _end > _start:
                response_text = response_text[_start:_end]
            for item in json.loads(response_text):
                idx = int(item['a']) - 1
                if 0 <= idx < len(batch):
                    article = batch[idx]
                    article.q_gate = min(100, max(0, int(item['q'])))
                    entry = cache.get(article.url_hash)
                    if not isinstance(entry, dict):
                        entry = {}
                        cache[article.url_hash] = entry
                    entry['q_gate'] = article.q_gate
                    entry.setdefault('timestamp', timestamp)
                    scored += 1
        except Exception as e:
            print(f"  ⚠️ Quality gate batch failed (fail-open): {e}")

    _scored_cache.save(cache)
    if scored:
        gated_scores = sorted(a.q_gate for a in to_score if a.q_gate is not None)
        _n = len(gated_scores)
        print(f"   Gate scored {scored} articles: "
              f"p25={gated_scores[_n // 4]} p50={gated_scores[_n // 2]} p75={gated_scores[3 * _n // 4]}")


def score_articles_gated(articles: List[Article], api_key: str, config: Dict) -> List[Article]:
    """Gated scoring: absolute quality gate → interest ranking → targeted deep scoring.

    Replaces the hybrid mode's rank-percentile eligibility (bottom 70% of every
    batch hard-capped below the quality floor regardless of content) with an
    absolute gate, then spends Claude Q/R/L scoring only on the display-bound
    slice chosen by interest rank. Articles that fail the gate keep q_gate as
    their score — low enough to miss news floors, but visible to the podcast
    pool, which applies its own (lower) quality floor.
    """
    if not articles:
        return []

    gate_cfg = LIMITS.get('quality_gate', {})
    gate_floor = gate_cfg.get('gate_floor', 25)

    print(f"\n🔀 Gated scoring: {len(articles)} articles (gate_floor={gate_floor})")
    score_quality_gate(articles, api_key)

    survivors: List[Article] = []
    failures: List[Article] = []
    for a in articles:
        q = a.q_gate
        if q is None or q >= gate_floor or a.category == 'local':
            survivors.append(a)
        else:
            failures.append(a)

    for a in failures:
        a.score = int(a.q_gate or 0)
        a.gate_scored = True

    # Resolve each survivor's provisional category once, up front, so both the
    # ordering pass below and the slice-cap pass can share it.
    provisional_cat = {
        a.url_hash: (a.category or categorize_article(a.title, a.description) or 'news')
        for a in survivors
    }

    # Interest ranking orders survivors for deep scoring; it never gates. `news`
    # is a broad, non-personalized survey category, so its deep-scoring priority
    # is q_gate (interest-independent newsworthiness) instead — otherwise the
    # limited deep-scoring budget for `news` would keep going to whichever
    # articles happen to match personal interests rather than the biggest
    # stories. Every other category keeps interest-rank ordering.
    if cohere_integration.is_enabled():
        order = cohere_integration.rank_with_rerank(
            survivors, config_loader.load_news_interests())
        rank_of = {h: i for i, h in enumerate(order)} if order else {}
    else:
        rank_of = {}

    news_survivors = [a for a in survivors if provisional_cat[a.url_hash] == 'news']
    other_survivors = [a for a in survivors if provisional_cat[a.url_hash] != 'news']
    news_survivors.sort(key=lambda a: a.q_gate or 0, reverse=True)
    if rank_of:
        other_survivors.sort(key=lambda a: rank_of.get(a.url_hash, len(other_survivors)))
    else:
        other_survivors.sort(key=lambda a: a.q_gate or 0, reverse=True)
    survivors = other_survivors + news_survivors

    # Display-bound slice: per provisional category, up to 2x the category's
    # max feed slots get full Q/R/L dimensional scoring. Everything else keeps
    # its absolute gate score.
    default_cfg = FEED_SLOTS.get('default', {'min_slots': 1, 'max_slots': 5})
    deep: List[Article] = []
    slice_counts: Dict[str, int] = defaultdict(int)
    for a in survivors:
        cat = provisional_cat[a.url_hash]
        cap = 2 * FEED_SLOTS.get(cat, default_cfg).get('max_slots', default_cfg.get('max_slots', 5))
        if slice_counts[cat] < cap:
            deep.append(a)
            slice_counts[cat] += 1

    print(f"  🎯 Deep scoring {len(deep)}/{len(survivors)} gate survivors "
          f"({len(failures)} below gate floor)")
    if deep:
        try:
            score_articles_with_claude_pure(deep, api_key)
        except Exception as e:
            print(f"  ⚠️ Deep scoring failed, keeping gate scores: {e}")

    # A failed deep-scoring batch leaves synthetic 50/50 dims — prefer the
    # real absolute gate score over that placeholder.
    for a in deep:
        if getattr(a, 'score_fallback', False) and a.q_gate is not None:
            a.quality = 0
            a.relevance = 0

    # Anything without real dimensions carries its absolute gate score.
    for a in survivors:
        if a.quality <= 0 and a.relevance <= 0:
            a.score = int(a.q_gate if a.q_gate is not None else a.score or 0)
            a.gate_scored = True

    # Keyword-only category fallback for articles Claude never saw (no API cost).
    for a in articles:
        if not a.category:
            a.category = categorize_article(a.title, a.description) or 'news'

    print(f"  ✅ Gated scoring complete")
    return articles


def score_articles_hybrid(articles: List[Article], api_key: str, config: Dict) -> List[Article]:
    """
    Hybrid scoring: Cohere reranks all articles (fast filter), Claude scores top N.
    
    Flow:
    1. Cohere rerank all articles (cheap, gives relevance ranking)
    2. Take top 30% by Cohere score
    3. Claude dimensional scoring on top articles
    4. Rest get Cohere score as final score
    """
    if not articles:
        return []
    
    print(f"\n🔀 Hybrid scoring: {len(articles)} articles")
    
    # Step 1: Get Cohere rankings for ALL articles
    print(f"  1️⃣ Cohere rerank (all {len(articles)} articles)...")
    cohere_scores = _cohere_prescore(articles)
    
    # Attach Cohere scores to articles
    for article in articles:
        cohere_result = cohere_scores.get(article.url_hash, 0)
        # Extract score: cohere_result is either int or tuple (int, str)
        if isinstance(cohere_result, tuple):
            cohere_score = cohere_result[0]
        else:
            cohere_score = cohere_result
        # Enforce int type
        score_int = int(cohere_score) if cohere_score else 0
        article.score = score_int
        article.cohere_scored = True
        article._cohere_prescore = score_int
    
    # Step 2: Identify top X% by Cohere score for Claude review
    top_percent = config.get("claude_top_percent", 0.30)
    
    # Sort by Cohere score, take top N
    sorted_by_cohere = sorted(articles, key=lambda a: getattr(a, "score", 0), reverse=True)
    num_for_claude = max(1, int(len(sorted_by_cohere) * top_percent))
    claude_candidates = sorted_by_cohere[:num_for_claude]
    
    print(f"  2️⃣ Claude dimensions (top {num_for_claude}/{len(articles)} articles)...")
    
    # Step 3: Claude scores only the top candidates (dimensional: Quality/Relevance/Local)
    if api_key:
        try:
            claude_scored = score_articles_with_claude_pure(claude_candidates, api_key)
            
            # Update articles in the main list with Claude scores
            # Create a map from url_hash to scored article
            claude_scored_map = {a.url_hash: a for a in claude_scored}
            
            for article in articles:
                if article.url_hash in claude_scored_map:
                    scored = claude_scored_map[article.url_hash]
                    # Copy Claude's dimensional scores — enforce int type
                    article.score = int(scored.score) if scored.score else 50
                    article.quality = scored.quality
                    article.relevance = scored.relevance
                    article.local = scored.local
                    article.content_type = scored.content_type
                    article.category = scored.category
                    article.story_group = scored.story_group
                    article.cohere_scored = False  # Mark as Claude-scored
        except Exception as e:
            print(f"  ⚠️ Claude scoring failed: {e}, keeping Cohere scores")
    else:
        print("  ⚠️ No Claude API key, keeping Cohere scores for top articles")
    
    # Step 4: Ensure all articles have a score (fallback to Cohere)
    for article in articles:
        # Check if score is missing, zero, or a tuple (shouldn't happen but safeguard)
        try:
            score_val = article.score if hasattr(article, "score") else None
            if score_val is None or score_val == 0 or isinstance(score_val, tuple):
                # Get Cohere score and extract from tuple if needed
                cohere_result = cohere_scores.get(article.url_hash, 0)
                if isinstance(cohere_result, tuple):
                    article.score = int(cohere_result[0]) if cohere_result[0] else 0
                else:
                    article.score = int(cohere_result) if cohere_result else 0
                article.cohere_scored = True
        except Exception:
            # If anything goes wrong, use Cohere score
            cohere_result = cohere_scores.get(article.url_hash, 0)
            if isinstance(cohere_result, tuple):
                article.score = int(cohere_result[0]) if cohere_result[0] else 0
            else:
                article.score = int(cohere_result) if cohere_result else 0
            article.cohere_scored = True

    # Articles that didn't go through Claude never get a category there;
    # use the same keyword-only fallback as the cohere-only path (no API cost).
    for article in articles:
        if not article.category:
            article.category = categorize_article(article.title, article.description) or 'news'

    print(f"  ✅ Hybrid complete")
    
    return articles


def _cohere_prescore(articles: List[Article]) -> Dict[str, int]:
    """
    Use Cohere Rerank to score all articles, return scores by url_hash.
    
    Returns: {url_hash: score_0_to_100, ...}
    """
    try:
        interests = config_loader.load_news_interests().strip()
    except Exception:
        interests = "Technology, science, climate, local news"

    # Call existing Cohere integration
    return cohere_integration.score_with_rerank(articles, interests)


# ════════════════════════════════════════════════════════════════════════════════

def score_articles_with_claude_pure(articles: List[Article], api_key: str) -> List[Article]:
    """Pure Claude scoring with dimensional analysis (Quality/Relevance/Local).
    
    This is the original dimensional scoring logic, now used as the deep-scoring
    step for top articles in hybrid mode.
    """
    if not articles:
        return []

    cache = _scored_cache.load()

    # The relevance dimension is defined by the personal news interest profile;
    # quality and local have their own interest-independent rubrics below.
    try:
        interests = config_loader.load_news_interests().strip()
    except Exception:
        print("⚠️ news interest profile not found, using basic scoring")
        interests = "Technology, science, climate, local news"

    client = anthropic.Anthropic(api_key=api_key)

    # Load user feedback examples when available (written weekly by feedback_trainer.py).
    feedback_section = ''
    feedback_examples_file = CONFIG_DIR / 'feedback_examples.txt'
    if feedback_examples_file.exists():
        try:
            feedback_text = feedback_examples_file.read_text(encoding='utf-8').strip()
            if feedback_text:
                feedback_section = (
                    f"\n\n--- USER FEEDBACK SIGNAL (recent explicit ratings) ---\n"
                    f"The user has reviewed articles and given explicit Good/Bad ratings. "
                    f"Use these signals to calibrate your relevance scores:\n{feedback_text}"
                )
        except Exception:
            pass

    # Build the cached system prompt once — includes the large interests text and
    # full category guide so they are only billed on cache miss, not on every batch.
    #
    # The category guide (with include/exclude signals from CATEGORY_RULES) replaces
    # the bare category-keys list. It adds ~570 tokens of genuinely useful context
    # AND pushes the prefix past the 4096-token minimum required for Haiku 4.5
    # prompt caching — without it, cache_control is silently ignored.
    category_lines = []
    for key, cat_data in CATEGORIES.items():
        rules = CATEGORY_RULES.get(key, {})
        desc = rules.get('description', cat_data.get('description', ''))
        line = f"  {key}: {desc}"
        includes = rules.get('include', [])
        excludes = rules.get('exclude', [])
        if includes:
            line += f"\n    Signals that suggest this category: {', '.join(includes)}"
        if excludes:
            line += f"\n    Do NOT use this category for: {', '.join(excludes)}"
        if cat_data.get('always_priority'):
            line += "\n    Note: Local content always scores 80+ regardless of topic."
        category_lines.append(line)
    category_guide = '\n'.join(category_lines)

    cached_system_prompt = (
        f"You are a news curator. Respond only with valid JSON arrays.\n\n"
        f"Rate each article on THREE dimensions (0-100 each):\n"
        f"- quality: Journalistic depth, sourcing, original reporting. High (70+): investigation, expert sourcing, original data. Low (0-30): wire reprint, press release, pure hype, advice column.\n"
        f"- relevance: Match to these interest priorities:\n{interests}\n"
        f"- local: Cariboo/BC Interior specificity. 80-100: Williams Lake/Cariboo focus. 40-79: BC regional. 0-39: no local angle.\n\n"
        f"Also assign content_type (pick one):\n"
        f"- analysis: Substantive explanation, deep dive, investigation\n"
        f"- breaking: Immediate event coverage, developing story\n"
        f"- opinion: Op-ed, commentary, editorial\n"
        f"- feature: Long-form profile, narrative journalism\n"
        f"- recap: Game/event summary, roundup, 'what happened' piece\n"
        f"- fluff: Celebrity gossip, tabloid, advice column, deals/promotions, pure sports score coverage, 'AI is transforming X' hype with no substance\n"
        f"- sponsored: Press release, sponsored content, promotional\n"
        f"- wire: Wire-service reprint (AP, Reuters, CP) with no local addition\n\n"
        f"CATEGORY DEFINITIONS AND ASSIGNMENT RULES:\n"
        f"Assign each article to exactly ONE category using the descriptions, signals, and exclusions below:\n\n"
        f"{category_guide}\n\n"
        f"CATEGORY PRIORITY (when an article qualifies for multiple categories, use this order):\n"
        f"1. local     — ANY Williams Lake, Cariboo, Quesnel, CRD, or BC Interior community content\n"
        f"2. homelab   — self-hosting, 3D printing, home automation, home servers, woodworking and shop craft, hands-on home repair\n"
        f"3. homestead — small/hobby farming, market gardens, small livestock, food preservation, woodlots, rural self-sufficiency (NOT commodity agriculture, NOT homelab electronics)\n"
        f"4. climate   — renewable energy, EVs, climate science, carbon, wildfire ecology\n"
        f"5. wellness  — personal health, nutrition, mental health, fitness, medicine, healthy aging, dementia, eldercare, caregiving\n"
        f"6. science   — peer-reviewed research, discoveries, academic findings\n"
        f"7. scifi     — science fiction, speculative fiction, worldbuilding\n"
        f"8. design    — architecture, building science, mass timber, small dwellings, heritage reuse, period-home restoration, placemaking, industrial design (NOT software/system architecture, NOT housing markets)\n"
        f"9. outdoors  — hiking, backcountry, camping, paddling, cycling, fishing and hunting, park and trip reporting (NOT wildfire emergencies or conservation policy — those are climate/local — and NOT racing or gear roundups)\n"
        f"10. ai-tech  — AI/ML systems, platform engineering, infrastructure\n"
        f"11. news     — default catch-all for anything not clearly matching 1–10\n\n"
        f"Also provide a 'story_group': a 3-5 word label for the SPECIFIC event or product covered "
        f"(e.g. 'Apple AirTag 2 launch', 'Williams Lake council vote', 'OpenAI GPT-5 release'). "
        f"Use null for standalone analysis, opinion, or evergreen pieces with no discrete news event. "
        f"Articles covering the SAME event MUST use IDENTICAL story_group strings."
        f"{feedback_section}"
    )

    scored_articles = []
    uncached = []

    for article in articles:
        if article.url_hash in cache:
            entry = cache[article.url_hash]
            if 'quality' in entry:
                # New dimensional format
                article.quality = entry['quality']
                article.relevance = entry['relevance']
                article.local = entry.get('local', 0)
                article.content_type = entry.get('content_type')
                # Extract score: could be tuple (int, str), get first element
                score_tuple = entry['score']
                score_val = score_tuple[0] if isinstance(score_tuple, tuple) else score_tuple
                article.score = int(score_val) if score_val else 0
                article.category = entry['category']
                article.story_group = entry.get('story_group')
                if entry.get('q_gate') is not None:
                    article.q_gate = int(entry['q_gate'])
                scored_articles.append(article)
            else:
                # Old single-score format — force re-score to get dimensions
                uncached.append(article)
        else:
            uncached.append(article)

    if uncached:
        print(f"\n🤖 Scoring {len(uncached)} new articles with Claude...")
        print(f"   (using cache for {len(scored_articles)} articles)")

        batch_size = LIMITS.get('claude_scoring_batch_size', 15)
        for i in range(0, len(uncached), batch_size):
            batch = uncached[i:i + batch_size]

            articles_text = "\n\n".join([
                f"Article {j+1}:\nTitle: {article.title}\nSource: {article.source}\nDescription: {article.description[:300]}"
                for j, article in enumerate(batch)
            ])

            prompt = f"""Rate each article on quality, relevance, and local dimensions; assign content_type, category, and story_group.

Respond with ONLY a JSON array (no other text):
[
  {{"article": 1, "quality": 72, "relevance": 85, "local": 40, "content_type": "analysis", "category": "ai-tech", "story_group": "Apple AirTag 2 launch"}},
  {{"article": 2, "quality": 45, "relevance": 30, "local": 0, "content_type": "wire", "category": "news", "story_group": null}}
]

Articles to evaluate:
{articles_text}"""

            try:
                response = client.messages.create(
                    model="claude-haiku-4-5",
                    max_tokens=1500,
                    system=[
                        {
                            "type": "text",
                            "text": cached_system_prompt,
                            "cache_control": {"type": "ephemeral", "ttl": "1h"}
                        }
                    ],
                    messages=[{"role": "user", "content": prompt}]
                )

                api_usage.record_claude_usage(response.usage)

                # Log cache token usage to verify prompt caching is working
                usage = response.usage
                cache_write = getattr(usage, 'cache_creation_input_tokens', 0) or 0
                cache_read = getattr(usage, 'cache_read_input_tokens', 0) or 0
                if cache_write or cache_read:
                    print(f"   💾 Cache: {cache_write} written, {cache_read} read, {usage.input_tokens} uncached")

                response_text = response.content[0].text.strip()
                # Strip markdown code fences if model wraps the JSON
                if response_text.startswith('```'):
                    lines = response_text.splitlines()
                    inner = lines[1:]
                    if inner and inner[-1].strip() == '```':
                        inner = inner[:-1]
                    response_text = '\n'.join(inner).strip()
                # Extract just the JSON array to ignore any trailing text
                _start, _end = response_text.find('['), response_text.rfind(']') + 1
                if _start != -1 and _end > _start:
                    response_text = response_text[_start:_end]

                scores = json.loads(response_text)

                timestamp = datetime.now(timezone.utc).timestamp()
                _gen_weights = SCORING_WEIGHTS.get('general', {})
                _w_q = _gen_weights.get('w_quality', 0.25)
                _w_r = _gen_weights.get('w_relevance', 0.55)
                _w_l = _gen_weights.get('w_local', 0.20)

                for score_data in scores:
                    idx = score_data['article'] - 1
                    if 0 <= idx < len(batch):
                        article = batch[idx]
                        article.quality = int(score_data.get('quality', 50))
                        article.relevance = int(score_data.get('relevance', 50))
                        article.local = int(score_data.get('local', 0))
                        article.content_type = score_data.get('content_type') or None
                        article.category = score_data.get('category', 'news')
                        if article.category not in CATEGORIES:
                            article.category = categorize_article(article.title, article.description) or 'news'
                        article.story_group = score_data.get('story_group') or None
                        # Composite score from dimensional weights
                        article.score = min(100, max(0, round(
                            _w_q * article.quality + _w_r * article.relevance + _w_l * article.local
                        )))

                        cache[article.url_hash] = {
                            'score': article.score,
                            'quality': article.quality,
                            'relevance': article.relevance,
                            'local': article.local,
                            'content_type': article.content_type,
                            'category': article.category,
                            'story_group': article.story_group,
                            'q_gate': getattr(article, 'q_gate', None),
                            'timestamp': timestamp
                        }

                        scored_articles.append(article)
                
            except json.JSONDecodeError as e:
                print(f"  ⚠️ JSON parsing error: {e}")
                print(f"     Response was: {response_text[:300]!r}")
                for article in batch:
                    article.quality = 50
                    article.relevance = 50
                    article.local = 0
                    article.score = 50
                    article.score_fallback = True  # synthetic neutral dims, not a real judgement
                    article.category = categorize_article(article.title, article.description) or 'news'
                    scored_articles.append(article)

            except Exception as e:
                print(f"  ⚠️ API error: {e}")
                for article in batch:
                    article.quality = 50
                    article.relevance = 50
                    article.local = 0
                    article.score = 50
                    article.score_fallback = True  # synthetic neutral dims, not a real judgement
                    article.category = categorize_article(article.title, article.description) or 'news'
                    scored_articles.append(article)
    
    _scored_cache.save(cache)
    return scored_articles


def scrub_feed_with_haiku(articles: List[Article], api_key: str) -> Tuple[List[Article], Dict]:
    """Final headline-only pass with Haiku to catch unwanted subjects that slipped through keyword filters.

    Returns (kept_articles, scrub_stats) where scrub_stats has
    'cohere_removed_by_category' and 'haiku_removed_by_category' dicts,
    used for the calibration agent's audit data.
    """
    if not articles:
        return [], {'cohere_removed_by_category': {}, 'haiku_removed_by_category': {}}

    local_signals = [s.lower() for s in FILTERS.get('local_signals', [])]

    # Editorial-exempt sources skip both passes below (see EDITORIAL_EXEMPT_SOURCES).
    exempt: List[Article] = []
    if EDITORIAL_EXEMPT_SOURCES:
        reviewable: List[Article] = []
        for article in articles:
            (exempt if article.source in EDITORIAL_EXEMPT_SOURCES
             else reviewable).append(article)
        if exempt:
            articles = reviewable
            print(f"🛡️  Scrub exempt: {len(exempt)} article(s) from "
                  f"{sorted({a.source for a in exempt})}")

    # Cohere pre-filter: auto-remove high-confidence junk before calling Claude.
    # Very conservative threshold avoids false positives.
    # Local articles are never auto-removed regardless of score.
    auto_removed_count = 0
    cohere_removed_by_category: Dict[str, int] = defaultdict(int)
    if cohere_integration.is_enabled():
        try:
            interests_text = config_loader.load_news_interests().strip()
        except Exception:
            interests_text = ''

        # Reuse scored_articles_cache (keyed by url_hash, same TTL as scoring)
        # so an article that keeps reappearing across runs without being
        # "shown" doesn't get re-sent to Cohere Rerank every time.
        scored_cache = _scored_cache.load()
        interest_scores: Dict[str, float] = {}
        uncached: List[Article] = []
        for article in articles:
            entry = scored_cache.get(article.url_hash)
            if entry and 'scrub_interest_score' in entry:
                interest_scores[article.url_hash] = entry['scrub_interest_score']
            else:
                uncached.append(article)

        if uncached:
            new_scores = cohere_integration.score_scrub_interest(uncached, interests_text)
            if new_scores:
                for article in uncached:
                    score = new_scores.get(article.url_hash)
                    if score is None:
                        continue
                    interest_scores[article.url_hash] = score
                    scored_cache.setdefault(article.url_hash, {})['scrub_interest_score'] = score
                _scored_cache.save(scored_cache)

        articles, auto_removed = cohere_integration.apply_scrub_threshold(
            articles, interest_scores, local_signals=local_signals,
            threshold=LIMITS.get('cohere_prefilter_threshold', 2.5)
        )
        auto_removed_count = len(auto_removed)
        for a in auto_removed:
            cohere_removed_by_category[a.category or 'news'] += 1

    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = (
        "You are a strict content filter reviewing article headlines.\n\n"
        "Each headline is prefixed with its category and relevance score, e.g. [ai-tech, score=22].\n\n"
        "Remove articles whose PRIMARY subject is one of:\n"
        "- Sports: game scores/recaps, drafts, trades, player stats, sports leagues "
        "(NFL, NBA, NHL, MLB, CFL, MLS, UFC, MMA, FIFA, PGA, NASCAR, Premier League, "
        "Champions League, World Cup, Olympics, Super Bowl), sports tournaments, "
        "championships, playoff coverage, athlete profiles focused on sport performance\n"
        "- Celebrity gossip: tabloid content, paparazzi, red carpet, award show results, "
        "celebrity relationships/feuds\n"
        "- Deals/promotions: promo codes, coupons, flash sales, best deals roundups, "
        "discount codes\n"
        "- Advice columns: Dear Abby, Ask Amy, Miss Manners, relationship/dating advice\n"
        "- Fluffy AI/tech (ONLY for ai-tech or homelab category articles): "
        "pure funding/valuation announcements ('raises $X million', 'valued at $Y billion', "
        "'goes public'), product launch press releases with no hands-on content, "
        "AI benchmark releases with no practical application ('scores X on Y benchmark'), "
        "conference keynote summaries that are pure announcement without substance, "
        "'X is transforming Y' hype takes without specific findings or implementation detail. "
        "Be more lenient for higher-scored articles (score >= 40) — only remove clear fluff.\n\n"
        "KEEP articles that use sports/entertainment as context for a deeper story "
        "(e.g. technology in sports, economics of a league, health research on athletes).\n"
        "KEEP local community news that is NOT primarily about sport (local politics, "
        "infrastructure, business, community events).\n"
        "REMOVE local articles whose primary subject is a sports game, score, result, "
        "draft, trade, player stat, or team recap — the [LOCAL] tag does not exempt "
        "sports coverage.\n"
        "KEEP ai-tech articles with hands-on content, research findings, or practical guides.\n\n"
        "Respond ONLY with valid JSON: {\"remove\": [list of article numbers to remove]}\n"
        "If nothing should be removed respond with: {\"remove\": []}"
    )

    kept: List[Article] = []
    total_removed = auto_removed_count
    haiku_removed_by_category: Dict[str, int] = defaultdict(int)

    batch_size = LIMITS.get('haiku_scrub_batch_size', 40)
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]

        # Build numbered headline list with category+score hint so Haiku can apply
        # category-aware filtering (e.g. stricter on low-scoring ai-tech articles).
        lines = []
        for j, article in enumerate(batch):
            title_lower = article.title.lower()
            is_local = any(sig in title_lower for sig in local_signals)
            cat_tag = f"{article.category or 'news'}, score={article.score}"
            if is_local:
                prefix = f"{j+1}. [LOCAL] [{cat_tag}] "
            else:
                prefix = f"{j+1}. [{cat_tag}] "
            lines.append(f"{prefix}{article.title}")
        headlines_text = "\n".join(lines)

        prompt = f"Review these headlines and identify any whose primary subject is unwanted:\n\n{headlines_text}"

        try:
            response = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=300,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            api_usage.record_claude_usage(response.usage)

            raw = response.content[0].text.strip()
            # Strip markdown fences if present
            if raw.startswith("```"):
                lines_r = raw.splitlines()
                inner = lines_r[1:]
                if inner and inner[-1].strip() == "```":
                    inner = inner[:-1]
                raw = "\n".join(inner).strip()

            # Use raw_decode so trailing text after the JSON object doesn't
            # cause "Extra data" errors (model sometimes appends a note).
            start = raw.find('{')
            if start == -1:
                raise ValueError("No JSON object in response")
            result, _ = json.JSONDecoder().raw_decode(raw, start)
            remove_nums = set(result.get("remove", []))

            for j, article in enumerate(batch):
                if (j + 1) in remove_nums:
                    print(f"  ✂️  Scrubbed: {article.title[:90]}")
                    total_removed += 1
                    haiku_removed_by_category[article.category or 'news'] += 1
                else:
                    kept.append(article)

        except Exception as e:
            print(f"  ⚠️ Scrub batch {i // batch_size + 1} failed ({e}), keeping all")
            kept.extend(batch)

    kept.extend(exempt)

    if total_removed:
        print(f"✂️  Final scrub removed {total_removed} article(s) from {len(articles)} quality articles")
    else:
        print(f"✂️  Final scrub: feed is clean ({len(articles)} articles passed)")

    scrub_stats = {
        'cohere_removed_by_category': dict(cohere_removed_by_category),
        'haiku_removed_by_category': dict(haiku_removed_by_category),
    }
    return kept, scrub_stats



def apply_prescore_filter(articles: List[Article]) -> List[Article]:
    """Cheap keyword + per-source cap gate for high-volume aggregator sources
    before they reach Claude/Cohere scoring.

    Configured via source_preferences.json: prescore_keyword_filter.sources
    lists source names subject to the gate. Articles from those sources are
    dropped unless they contain at least one CATEGORY_RULES interest keyword,
    and survivors are capped at max_candidates_per_source (most keyword hits
    win ties).
    """
    config = SOURCE_PREFS.get('prescore_keyword_filter', {})
    gated_sources = set(config.get('sources', []))
    if not gated_sources:
        return articles

    max_candidates = config.get('max_candidates_per_source', 15)

    local_signals_lower = [s.lower() for s in FILTERS.get('local_signals', [])]

    kept = []
    candidates_by_source = defaultdict(list)
    dropped = 0
    for article in articles:
        if article.source not in gated_sources:
            kept.append(article)
            continue
        text = f"{article.title} {article.description}".lower()
        is_local = any(sig in text for sig in local_signals_lower)
        hits = sum(1 for kw in PRESCORE_KEYWORDS if kw in text)
        # Local articles pass through even with zero keyword hits — the pipeline's
        # local-preservation rules must have a chance to run. Non-local zero-hit
        # articles are dropped as off-topic for this feed's interests.
        if hits == 0 and not is_local:
            dropped += 1
            continue
        article._prescore_hits = hits
        article._prescore_is_local = is_local
        candidates_by_source[article.source].append(article)

    for source, candidates in candidates_by_source.items():
        # Sort local articles first, then by keyword-hit density, so local content
        # is never bumped off the per-source cap by higher-hit non-local articles.
        candidates.sort(key=lambda a: (a._prescore_is_local, a._prescore_hits), reverse=True)
        kept.extend(candidates[:max_candidates])
        dropped += max(0, len(candidates) - max_candidates)

    if dropped:
        print(f"🔎 Prescore keyword filter ({', '.join(sorted(gated_sources))}): dropped {dropped} articles")

    return kept




def apply_feed_slot_allocation(articles: List[Article]) -> List[Article]:
    """Phase 8: Category slot allocation — guarantee min_slots per category,
    cap at max_slots, fill greedily by composite score.

    Uses config/feed_slots.json. Falls back to 'default' slot config for
    categories not explicitly listed. Runs after quality filtering and floor
    rescue so it has the full available pool to draw from.
    """
    if not FEED_SLOTS:
        return articles

    default_cfg = FEED_SLOTS.get('default', {'min_slots': 1, 'max_slots': 5})

    # Group by category, best composite score first within each group
    by_cat: Dict[str, List[Article]] = defaultdict(list)
    for a in sorted(articles, key=lambda x: x.score, reverse=True):
        by_cat[a.category or 'news'].append(a)

    result: List[Article] = []
    cat_counts: Dict[str, int] = defaultdict(int)

    # Pass 1: guarantee min_slots for every category that has articles
    for cat, arts in by_cat.items():
        cfg = FEED_SLOTS.get(cat, default_cfg)
        min_s = cfg.get('min_slots', default_cfg.get('min_slots', 1))
        for a in arts[:min_s]:
            result.append(a)
            cat_counts[cat] += 1

    included_ids = {id(a) for a in result}

    # Pass 2: fill remaining capacity greedily by composite score up to max_slots
    remaining = [a for a in sorted(articles, key=lambda x: x.score, reverse=True)
                 if id(a) not in included_ids]
    for a in remaining:
        cat = a.category or 'news'
        cfg = FEED_SLOTS.get(cat, default_cfg)
        max_s = cfg.get('max_slots', default_cfg.get('max_slots', 5))
        if cat_counts[cat] < max_s:
            result.append(a)
            cat_counts[cat] += 1

    slot_summary = ', '.join(f"{cat}:{n}" for cat, n in sorted(cat_counts.items()))
    print(f"📊 Feed slot allocation: {len(articles)} → {len(result)} articles [{slot_summary}]")
    return result


def compute_composite_score(article: 'Article', weights: dict = None) -> int:
    """Compute composite score from Q, R, L dimensions using configured weights."""
    if weights is None:
        weights = SCORING_WEIGHTS.get(article.category, SCORING_WEIGHTS.get('general', {}))
    w_q = weights.get('w_quality', 0.25)
    w_r = weights.get('w_relevance', 0.55)
    w_l = weights.get('w_local', 0.20)
    return min(100, max(0, round(w_q * article.quality + w_r * article.relevance + w_l * article.local)))


def apply_dimension_adjustments(articles: List[Article]) -> List[Article]:
    """Apply dimension-level score adjustments and recompute composite scores.

    Replaces enforce_local_priority (L += local_keyword_bonus) and
    apply_source_preferences (Q += source quality adjustment).
    Articles lacking dimensional scores (quality=relevance=0) fall back to
    direct composite adjustment for backward-compatibility with the Cohere path.
    """
    local_signals = [s.lower() for s in FILTERS.get('local_signals', [])]
    local_bonus = SCORING_MODIFIERS.get('local_keyword_bonus', 25)
    wire_penalty = SCORING_MODIFIERS.get('wire_quality_penalty', -10)
    q_adjustments = SCORING_MODIFIERS.get('source_type_quality_adjustments', {})
    local_thin_day_floor = LIMITS.get('local_thin_day_score_floor', 80)

    source_map = SOURCE_PREFS.get('source_map', {})

    local_boosted = 0
    source_adjusted = 0

    for article in articles:
        # Cohere articles carry synthesized Q/R values (quality=relevance=score) so the
        # calibration histograms stay populated, but the composite must not be recomputed
        # from those synthetic values — keep the Cohere percentile score as-is.
        has_dimensions = (article.quality > 0 or article.relevance > 0) and not getattr(article, 'cohere_scored', False)

        # Local keyword signals → L dimension boost + category override
        title_text = article.title.lower()
        if any(signal in title_text for signal in local_signals):
            if has_dimensions:
                article.local = min(100, article.local + local_bonus)
            else:
                # Thin-day fallback: floor local content so it isn't suppressed
                # when Cohere gives it a low raw percentile score.
                article.score = max(article.score, local_thin_day_floor)
            article.category = 'local'
            local_boosted += 1

        # Source type → Q dimension (or fallback composite adjustment)
        source_type = source_map.get(article.source)
        if source_type:
            adjustment = q_adjustments.get(source_type, 0)
            if adjustment != 0:
                if has_dimensions:
                    article.quality = max(0, min(100, article.quality + adjustment))
                else:
                    article.score = max(0, min(100, article.score + adjustment))
                source_adjusted += 1

        # Wire content type → Q penalty (applied after source adjustment intentionally:
        # wire content from a preferred outlet is still less valuable than original
        # reporting from that same outlet, so the penalty should dominate the boost).
        if has_dimensions and article.content_type == 'wire':
            article.quality = max(0, min(100, article.quality + wire_penalty))

        # Recompute composite only when dimensional scores are present
        if has_dimensions:
            article.score = compute_composite_score(article)

    if local_boosted:
        print(f"📍 Local dimension boost: {local_boosted} article(s) received L += {local_bonus}")
    if source_adjusted:
        print(f"📰 Source Q adjustments applied to {source_adjusted} article(s)")
    return articles


def filter_by_content_type(articles: List[Article]) -> Tuple[List[Article], Dict]:
    """Phase 3: Absolute content type filter — score-independent.

    - fluff, sponsored: always drop (except high-scoring AI/tech fluff — Haiku scrub
      handles those with score-aware leniency; dropping them here would override that)
    - recap: drop unless article.local >= 50 (local recaps may have community value)
    - wire: kept but flagged; dedup already prefers original reporting over wire
    - None/unknown: pass through (e.g. Cohere-scored articles)
    - EDITORIAL_EXEMPT_SOURCES: pass through regardless of type
    """
    ALWAYS_DROP = {'fluff', 'sponsored'}
    # AI/tech articles above this threshold have already been reviewed leniently by
    # scrub_feed_with_haiku (score >= 40 triggers "only remove clear fluff"). Dropping
    # them here unconditionally would contradict that leniency, so let them pass.
    ai_tech_fluff_threshold = LIMITS.get('ai_tech_fluff_score_threshold', 40)
    AI_TECH_CATEGORIES = {'ai-tech', 'homelab'}
    kept = []
    removed: Dict[str, int] = defaultdict(int)

    exempted = 0
    for article in articles:
        ct = article.content_type
        if not ct:
            kept.append(article)
            continue
        if article.source in EDITORIAL_EXEMPT_SOURCES:
            kept.append(article)
            exempted += 1
            continue
        if ct in ALWAYS_DROP:
            if (ct == 'fluff'
                    and article.category in AI_TECH_CATEGORIES
                    and article.score >= ai_tech_fluff_threshold):
                kept.append(article)
            else:
                removed[ct] += 1
            continue
        if ct == 'recap' and article.local < 50 and article.category != 'local':
            removed['recap_nonlocal'] += 1
            continue
        kept.append(article)

    if exempted:
        print(f"🛡️  Content type exempt: {exempted} article(s) from editorial-exempt sources")
    total = sum(removed.values())
    if total:
        breakdown = ', '.join(f"{v} {k}" for k, v in removed.items())
        print(f"🚫 Content type filter: removed {total} articles ({breakdown})")
    return kept, {'content_type_removed': dict(removed)}


def apply_diversity_limits(articles: List[Article], category: str) -> List[Article]:
    """Limit articles per source to ensure diversity, respecting source type preferences"""
    if category == 'local':
        default_max = LIMITS['max_per_local']
    else:
        default_max = LIMITS['max_per_source']

    source_map = SOURCE_PREFS.get('source_map', {})
    source_types = SOURCE_PREFS.get('source_types', {})

    source_counts = defaultdict(int)
    diverse_articles = []

    sorted_articles = sorted(articles, key=lambda a: a.score, reverse=True)

    for article in sorted_articles:
        # Determine per-source limit: use source type override if available
        source_type = source_map.get(article.source)
        if source_type and source_type in source_types:
            max_for_source = source_types[source_type].get('max_per_source', default_max)
        else:
            max_for_source = default_max

        if source_counts[article.source] < max_for_source:
            diverse_articles.append(article)
            source_counts[article.source] += 1

    print(f"📊 Diversity filter ({category}): {len(articles)} → {len(diverse_articles)} articles")
    return diverse_articles


_CT_EMOJI = {
    "analysis":  "🔍",
    "breaking":  "🚨",
    "opinion":   "💬",
    "feature":   "📖",
    "recap":     "📋",
    "fluff":     "🍭",
    "sponsored": "💰",
    "wire":      "📡",
}

_DAY_ABBREV = {
    "monday": "Mon", "tuesday": "Tue", "wednesday": "Wed",
    "thursday": "Thu", "friday": "Fri", "saturday": "Sat", "sunday": "Sun",
}

_DAY_EMOJI = {
    "monday":    "🎨",  # Arts & Culture
    "tuesday":   "🌾",  # Working Lands
    "wednesday": "🔧",  # Repair & Tech
    "thursday":  "🪶",  # Indigenous Lands
    "friday":    "🌲",  # Wild Spaces
    "saturday":  "🏔️",  # Cariboo Local
    "sunday":    "🔭",  # Science & Wonder
}

_BADGE_STYLE = (
    "margin:0 0 0.75em;padding:5px 10px;background:#f0f4f8;"
    "border-left:3px solid #7b9fc4;border-radius:3px;"
    "font-size:0.82em;color:#444;line-height:1.8;"
)

_REVIEW_URL = "https://zirnhelt.github.io/super-rss-feed/review.html"


def _make_score_badge(
    score: int,
    quality: int,
    relevance: int,
    local_score: int,
    content_type: Optional[str],
    tags: List[str],
    *,
    composite_score: Optional[int] = None,
    theme_score: Optional[int] = None,
    kw_matches: Optional[int] = None,
    is_bonus: bool = False,
    podcast_days: Optional[List[str]] = None,
    article_url: str = "",
) -> str:
    """Return a minimal day-routing badge for display in RSS readers like Inoreader."""
    if not podcast_days:
        return ""
    emojis = " ".join(_DAY_EMOJI.get(d, "📅") for d in podcast_days)
    fix_href = f"{_REVIEW_URL}?url={quote(article_url, safe='')}" if article_url else _REVIEW_URL
    fix_link = f'<a href="{fix_href}" style="color:#7b9fc4;text-decoration:none;">✏️</a>'
    return f'<p style="{_BADGE_STYLE}">{emojis} {fix_link}</p>\n'


# RSS 2.0 mirror ---------------------------------------------------------
# Readers that speak JSON Feed (NetNewsWire, Reeder, Feedbin, Miniflux) get the
# .json file; everything else gets a .xml mirror of it. Which categories get a
# mirror is driven by `"rss": true` in config/feeds.json.

# A reader only needs a recent window, and content_html carries an image and a
# badge per item, so the mirror is capped well below `max_feed_size`. The JSON
# feed remains the full retention archive.
RSS_MAX_ITEMS = 100

# Characters outside these ranges are illegal in XML 1.0. Escaping does not
# rescue them — a single one makes the whole feed unparseable for every
# reader — so they are dropped.
_XML_ILLEGAL = re.compile(
    r'[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]'
)


def _xml_text(value: str) -> str:
    """Escape a string for use as XML character data."""
    return html_escape(_XML_ILLEGAL.sub('', value or ''), quote=True)


def _rfc822(iso_timestamp: str) -> str:
    """Convert an ISO-8601 timestamp to the RFC 822 form RSS 2.0 requires."""
    dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return format_datetime(dt)


def generate_rss_feed(feed: Dict, output_path: str) -> None:
    """Render an RSS 2.0 file from an already-built JSON Feed dict.

    The mirror is a projection of the JSON feed rather than a second pass over
    the articles, so the two cannot drift. Mapping decisions worth knowing:

    * ``<link>`` is the item's ``url`` — the link the reader should follow,
      which is not always the publisher URL (see ``apply_subscriber_links``).
    * ``<guid isPermaLink="false">`` is the item's ``id``, which is always the
      publisher URL and is the identity key everywhere else in the pipeline.
      Keeping it here means a reader's read/unread state survives an Apple News
      link upgrade instead of resurfacing the article as new.
    * ``<description>`` carries the same ``content_html`` as the JSON feed —
      image and day-routing badge included — escaped rather than wrapped in
      CDATA, which would break on a ``]]>`` inside scraped article text.
    * ``<dc:creator>`` holds the source name; RSS's own ``<author>`` is
      specified as an email address and readers render a bare name there badly.
    """
    self_url = f"{FEEDS_CONFIG['base_url']}/{os.path.basename(output_path)}"

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:media="http://search.yahoo.com/mrss/">',
        '<channel>',
        f"<title>{_xml_text(feed['title'])}</title>",
        f"<link>{_xml_text(feed['home_page_url'])}</link>",
        f'<atom:link href="{_xml_text(self_url)}" rel="self" '
        'type="application/rss+xml" />',
        f"<description>{_xml_text(feed['description'])}</description>",
        f"<language>{_xml_text(feed.get('language', 'en'))}</language>",
        f'<lastBuildDate>{format_datetime(datetime.now(timezone.utc))}</lastBuildDate>',
        '<generator>Super RSS Feed Curator</generator>',
    ]

    if feed.get('icon'):
        lines += [
            '<image>',
            f"<url>{_xml_text(feed['icon'])}</url>",
            f"<title>{_xml_text(feed['title'])}</title>",
            f"<link>{_xml_text(feed['home_page_url'])}</link>",
            '</image>',
        ]

    for item in feed['items'][:RSS_MAX_ITEMS]:
        lines.append('<item>')
        lines.append(f"<title>{_xml_text(item['title'])}</title>")
        lines.append(f"<link>{_xml_text(item['url'])}</link>")
        lines.append(
            f'<guid isPermaLink="false">{_xml_text(item["id"])}</guid>'
        )
        lines.append(f"<pubDate>{_rfc822(item['date_published'])}</pubDate>")

        authors = item.get('authors') or []
        if authors and authors[0].get('name'):
            lines.append(f"<dc:creator>{_xml_text(authors[0]['name'])}</dc:creator>")

        for tag in item.get('tags', []):
            lines.append(f"<category>{_xml_text(tag)}</category>")

        if item.get('image'):
            lines.append(
                f'<media:content url="{_xml_text(item["image"])}" medium="image" />'
            )

        lines.append(
            f"<description>{_xml_text(item.get('content_html', ''))}</description>"
        )
        lines.append('</item>')

    lines += ['</channel>', '</rss>', '']

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    item_count = min(len(feed['items']), RSS_MAX_ITEMS)
    print(f"✅ Generated RSS mirror: {output_path} ({item_count} articles)")


def generate_json_feed(articles: List[Article], category: str, output_path: str):
    """Generate JSON Feed format output"""
    cat_config = CATEGORIES[category]
    feed_config = FEEDS_CONFIG['feeds'][category]
    podcast_shown_cache = load_podcast_shown_cache()

    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": f"{cat_config['emoji']} {feed_config['title']}",
        "home_page_url": FEEDS_CONFIG['base_url'],
        "feed_url": f"{FEEDS_CONFIG['base_url']}/feed-{category}.json",
        "description": feed_config['description'],
        "icon": f"{FEEDS_CONFIG['base_url']}/favicon.ico",
        "authors": [{"name": FEEDS_CONFIG['author']}],
        "language": "en",
        "items": []
    }

    for article in articles[:LIMITS['max_feed_size']]:
        clean_desc = _strip_markdown_links(article.description or "")
        has_source_in_title = (article.title.startswith(f"[{article.source}]")
                               or article.source in article.title)

        # Collect tags and podcast appearances first (needed for badge)
        item_tags: List[str] = []
        if category == 'local':
            item_tags.append("local-priority")

        subscriber_label = SUBSCRIBER_ACCESS.get(article.source)
        if subscriber_label:
            item_tags.append("subscriber-access")

        _us_scope = us_policy_scope(article.title, article.description or "")
        if _us_scope:
            item_tags.append("us-policy")

        podcast_days = sorted({
            entry['day']
            for key, entry in podcast_shown_cache.items()
            if key.startswith(f"{article.link}:::")
        }, key=lambda d: list(_DAY_ABBREV.keys()).index(d) if d in _DAY_ABBREV else 99)

        badge = _make_score_badge(
            score=article.score,
            quality=article.quality,
            relevance=article.relevance,
            local_score=article.local,
            content_type=article.content_type,
            tags=item_tags,
            podcast_days=podcast_days or None,
            article_url=article.link,
        )

        # image → badge → description
        content_html = badge + clean_desc
        if hasattr(article, 'image') and article.image:
            img_html = f'<img src="{html_escape(article.image)}" style="width:100%;max-height:300px;object-fit:cover;" />\n'
            content_html = img_html + content_html

        item = {
            "id": article.link,
            "url": article.link,
            "title": article.title if has_source_in_title else f"[{article.source}] {article.title}",
            "content_html": content_html,
            "date_published": article.pub_date.isoformat(),
            "authors": [{"name": article.source, "url": article.source_url}]
        }

        if hasattr(article, 'image') and article.image:
            item["image"] = article.image

        item["_score"] = article.score
        item["_quality"] = article.quality
        item["_relevance"] = article.relevance
        item["_local_score"] = article.local
        if article.content_type:
            item["_content_type"] = article.content_type

        if category == 'local':
            item["_local"] = True

        if _us_scope:
            item["_us_policy"] = True
            item["_us_policy_scope"] = _us_scope

        if item_tags:
            item["tags"] = item_tags

        if subscriber_label:
            item["title"] = f"🔓 {item['title']}"
            apply_subscriber_links(item, article, subscriber_label)

        feed["items"].append(item)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(feed, f, indent=2, ensure_ascii=False)

    print(f"✅ Generated {category} feed: {len(feed['items'])} articles")

    if feed_config.get('rss'):
        generate_rss_feed(feed, f"{os.path.splitext(output_path)[0]}.xml")


def load_podcast_schedule():
    """Load podcast schedule configuration"""
    try:
        return config_loader.load_podcast_schedule_config()
    except SystemExit:
        print("⚠️ podcast_schedule.json not found, skipping podcast feed")
        return None


def _keyword_match_count(text: str, keywords: List[str]) -> int:
    """Count how many keywords appear in the text (case-insensitive)."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw.lower() in text_lower)


def _net_keyword_match_count(text: str, keywords: List[str], anti_keywords: List[str]) -> int:
    """Keyword hits minus anti-keyword hits, floored at 0.

    Lets a theme day's keyword set be penalized by terms that belong to a
    neighboring theme's keyword set, so articles dominated by that
    neighboring theme's topic don't get bucketed here as strong matches.
    """
    hits = _keyword_match_count(text, keywords)
    if not anti_keywords:
        return hits
    anti_hits = _keyword_match_count(text, anti_keywords)
    return max(0, hits - anti_hits)


def score_articles_for_theme(articles: List[Article], theme_prompt: str, theme_label: str, api_key: str) -> List[tuple]:
    """Score articles for thematic fit using Claude.

    Results are cached by (article URL, theme label) for THEME_SCORE_CACHE_TTL_DAYS days
    so repeated runs do not re-score the same articles.

    Returns list of tuples: (article, theme_score)
    where theme_score is 0-100 indicating fit to the daily theme.
    """
    if not articles:
        return []

    # Load cache and separate already-scored articles from those that need scoring
    theme_cache = load_theme_score_cache()
    now_iso = datetime.now(timezone.utc).isoformat()

    scored_results = []
    uncached = []
    for article in articles:
        cache_key = f"{article.link}:::{theme_label}"
        if cache_key in theme_cache:
            scored_results.append((article, theme_cache[cache_key]['score']))
        else:
            uncached.append(article)

    cache_hits = len(articles) - len(uncached)
    if cache_hits:
        print(f"🎯 Theme scoring [{theme_label}]: {cache_hits} cached, {len(uncached)} need scoring")
    else:
        print(f"🎯 Scoring {len(uncached)} articles for theme: {theme_label}")

    if not uncached:
        return scored_results

    # Cohere Rerank branch — uses the theme's scoring_prompt as the relevance query
    if cohere_integration.is_enabled():
        theme_results = cohere_integration.score_themes_with_rerank(
            uncached,
            {theme_label: {'label': theme_label, 'scoring_prompt': theme_prompt}},
        )
        for article in uncached:
            ts = theme_results.get(article.link, {}).get(theme_label, 50)
            scored_results.append((article, ts))
            cache_key = f"{article.link}:::{theme_label}"
            theme_cache[cache_key] = {'score': ts, 'cached_at': now_iso}
        save_theme_score_cache(theme_cache)
        return scored_results

    client = anthropic.Anthropic(api_key=api_key)

    # Theme fit must be judged by the theme's own editorial charter, NOT the
    # personal interest profile — embedding scoring_interests.txt here skewed
    # every theme score toward the news feed's interests. The quality charter
    # provides interest-independent background on what good journalism looks
    # like; the category guide supplies the content taxonomy. (This fallback
    # path's system prompt sits below Haiku's 4096-token caching minimum, but
    # it only runs for articles missed by ingest-time batch scoring.)
    quality_charter = config_loader.load_quality_charter().strip()

    category_lines = []
    for key, cat_data in CATEGORIES.items():
        rules = CATEGORY_RULES.get(key, {})
        desc = rules.get('description', cat_data.get('description', ''))
        line = f"  {key}: {desc}"
        includes = rules.get('include', [])
        excludes = rules.get('exclude', [])
        if includes:
            line += f"\n    Signals: {', '.join(includes)}"
        if excludes:
            line += f"\n    Exclude: {', '.join(excludes)}"
        category_lines.append(line)
    category_guide = '\n'.join(category_lines)

    cached_theme_system = (
        f"You are evaluating news articles for thematic relevance. Respond only with valid JSON arrays.\n\n"
        f"BACKGROUND — quality charter (what good journalism looks like, independent of topic):\n{quality_charter}\n\n"
        f"CONTENT TAXONOMY (for reference):\n{category_guide}\n\n"
        f"{theme_prompt}"
        f"{US_POLICY_SCORING_GUIDANCE}"
    )

    batch_size = 30

    for i in range(0, len(uncached), batch_size):
        batch = uncached[i:i + batch_size]
        batch_start_count = len(scored_results)

        try:
            articles_text = "\n\n".join([
                f"Article {j+1}:\nTitle: {article.title}\nSource: {article.source}\nDescription: {(article.description or '')[:300]}"
                for j, article in enumerate(batch)
            ])

            prompt = f"""Rate each article 0-100 for theme fit.

Respond with ONLY a JSON array (no other text):
[
  {{"article": 1, "theme_score": 85}},
  {{"article": 2, "theme_score": 45}}
]

Articles to evaluate:
{articles_text}"""

            response = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=750,
                system=[
                    {
                        "type": "text",
                        "text": cached_theme_system,
                        "cache_control": {"type": "ephemeral", "ttl": "1h"}
                    }
                ],
                messages=[{"role": "user", "content": prompt}]
            )
            api_usage.record_claude_usage(response.usage)

            response_text = response.content[0].text.strip()
            # Strip markdown code fences if model wraps the JSON
            if response_text.startswith('```'):
                lines = response_text.splitlines()
                inner = lines[1:]
                if inner and inner[-1].strip() == '```':
                    inner = inner[:-1]
                response_text = '\n'.join(inner).strip()
            # Extract just the JSON array to ignore any trailing text
            _start, _end = response_text.find('['), response_text.rfind(']') + 1
            if _start != -1 and _end > _start:
                response_text = response_text[_start:_end]
            scores = json.loads(response_text)

            for score_data in scores:
                idx = score_data['article'] - 1
                if 0 <= idx < len(batch):
                    article = batch[idx]
                    theme_score = score_data.get('theme_score', 0)
                    scored_results.append((article, theme_score))
                    cache_key = f"{article.link}:::{theme_label}"
                    theme_cache[cache_key] = {'score': theme_score, 'cached_at': now_iso}

        except json.JSONDecodeError as e:
            print(f"  ⚠️ JSON parsing error: {e}")
            for article in batch:
                scored_results.append((article, 50))

        except Exception as e:
            print(f"  ⚠️ API error: {e}")
            for article in batch:
                scored_results.append((article, 50))

        # Fallback: if Claude returned a valid but empty/incomplete response,
        # ensure every article in the batch gets a score so none are silently dropped
        scored_in_batch = {a.link for a, _ in scored_results[batch_start_count:]}
        for article in batch:
            if article.link not in scored_in_batch:
                scored_results.append((article, 50))

    save_theme_score_cache(theme_cache)
    return scored_results


def score_all_themes_at_ingest(articles: List[Article], schedule_config: Dict, api_key: str):
    """Score new articles against all podcast themes in one pass at ingest time.

    Called once per run after quality articles are saved to the podcast cache.
    Each article is scored for all 7 themes in a single Claude call per batch,
    with results written to the shared theme score cache.  Daily podcast feed
    generation then becomes a pure cache read with zero API calls.

    Uses prompt caching on the combined multi-theme system message (Option D).
    """
    if not articles or not schedule_config or not schedule_config.get('enabled', False):
        return

    schedule = schedule_config.get('schedule', {})
    if not schedule:
        return

    theme_cache = load_theme_score_cache()
    now_iso = datetime.now(timezone.utc).isoformat()

    # Collect articles that are missing a score for at least one theme
    uncached = []
    for article in articles:
        if any(f"{article.link}:::{cfg['label']}" not in theme_cache for cfg in schedule.values()):
            uncached.append(article)

    if not uncached:
        print(f"🎯 Ingest theme scoring: all {len(articles)} articles already cached for all themes")
        return

    print(f"🎯 Ingest theme scoring: {len(uncached)} articles × {len(schedule)} themes...")

    # Cohere Rerank branch — one synchronous Rerank call per theme (fast, no batch job needed)
    if cohere_integration.is_enabled():
        theme_scores = cohere_integration.score_themes_with_rerank(uncached, schedule)
        for article in uncached:
            link_scores = theme_scores.get(article.link, {})
            for cfg in schedule.values():
                label = cfg['label']
                score = link_scores.get(label, 50)
                theme_cache[f"{article.link}:::{label}"] = {'score': score, 'cached_at': now_iso}
        save_theme_score_cache(theme_cache)
        print(f"   ✅ Cohere theme scoring complete ({len(uncached)} articles × {len(schedule)} themes cached)")
        return

    client = anthropic.Anthropic(api_key=api_key)

    # Theme fit is judged by each theme's editorial charter alone — the personal
    # interest profile must NOT appear here (it skewed every theme score toward
    # the news feed's interests). The quality charter replaces it as background:
    # interest-independent, and together with the 7 theme prompts (~3.7k tokens)
    # it keeps the combined system prompt past Haiku's 4096-token cache minimum.
    quality_charter = config_loader.load_quality_charter().strip()

    theme_descriptions = "\n\n".join(
        f"Theme key \"{day}\" — {cfg['label']}:\n{cfg.get('scoring_prompt', '')}"
        for day, cfg in schedule.items()
    )
    day_keys = list(schedule.keys())
    combined_system = (
        f"You are evaluating news articles for thematic relevance across multiple themes. "
        f"Respond only with valid JSON arrays.\n\n"
        f"BACKGROUND — quality charter (what good journalism looks like, independent of topic):\n{quality_charter}\n\n"
        f"Score each article 0-100 for each of the following themes:\n\n"
        f"{theme_descriptions}"
        f"{US_POLICY_SCORING_GUIDANCE}"
    )

    day_schema = ", ".join(f'"{d}": 0' for d in day_keys)
    batch_size = 30

    batch_requests = []
    article_batches_meta = []

    for i in range(0, len(uncached), batch_size):
        batch = uncached[i:i + batch_size]
        articles_text = "\n\n".join(
            f"Article {j+1}:\nTitle: {a.title}\nSource: {a.source}\nDescription: {(a.description or '')[:300]}"
            for j, a in enumerate(batch)
        )
        prompt = f"""Rate each article 0-100 for every theme key listed in the system prompt.

Respond with ONLY a JSON array (no other text):
[
  {{"article": 1, {day_schema}}},
  {{"article": 2, {day_schema}}}
]

Articles to evaluate:
{articles_text}"""
        custom_id = f"themes_{i // batch_size}"
        batch_requests.append({
            "custom_id": custom_id,
            "params": {
                "model": "claude-haiku-4-5",
                "max_tokens": 2500,
                "system": [{"type": "text", "text": combined_system,
                            "cache_control": {"type": "ephemeral", "ttl": "1h"}}],
                "messages": [{"role": "user", "content": prompt}]
            }
        })
        article_batches_meta.append({
            "custom_id": custom_id,
            "articles": [{"link": a.link, "title": a.title} for a in batch]
        })

    try:
        batch_job = client.messages.batches.create(requests=batch_requests)
        save_pending_theme_batch({
            "batch_id": batch_job.id,
            "submitted_at": now_iso,
            "article_batches": article_batches_meta,
            "day_keys": day_keys,
            "schedule_labels": {day: cfg['label'] for day, cfg in schedule.items()}
        })
        print(f"   📤 Submitted async batch {batch_job.id} — results will be cached next run"
              f" ({len(uncached)} articles × {len(schedule)} themes)")
    except Exception as e:
        print(f"  ⚠️ Batch submission failed, falling back to synchronous scoring: {e}")
        for i in range(0, len(uncached), batch_size):
            batch = uncached[i:i + batch_size]
            articles_text = "\n\n".join(
                f"Article {j+1}:\nTitle: {a.title}\nSource: {a.source}\nDescription: {(a.description or '')[:300]}"
                for j, a in enumerate(batch)
            )
            prompt = f"""Rate each article 0-100 for every theme key listed in the system prompt.

Respond with ONLY a JSON array (no other text):
[
  {{"article": 1, {day_schema}}},
  {{"article": 2, {day_schema}}}
]

Articles to evaluate:
{articles_text}"""
            try:
                response = client.messages.create(
                    model="claude-haiku-4-5",
                    max_tokens=2500,
                    system=[{"type": "text", "text": combined_system,
                             "cache_control": {"type": "ephemeral", "ttl": "1h"}}],
                    messages=[{"role": "user", "content": prompt}]
                )
                api_usage.record_claude_usage(response.usage)
                response_text = response.content[0].text.strip()
                if response_text.startswith('```'):
                    lines = response_text.splitlines()
                    inner = lines[1:]
                    if inner and inner[-1].strip() == '```':
                        inner = inner[:-1]
                    response_text = '\n'.join(inner).strip()
                _start, _end = response_text.find('['), response_text.rfind(']') + 1
                if _start != -1 and _end > _start:
                    response_text = response_text[_start:_end]
                scores = json.loads(response_text)
                scored_in_batch = set()
                for score_data in scores:
                    idx = score_data.get('article', 0) - 1
                    if 0 <= idx < len(batch):
                        article = batch[idx]
                        scored_in_batch.add(idx)
                        for day, cfg in schedule.items():
                            label = cfg['label']
                            theme_score = int(score_data.get(day, 50))
                            theme_cache[f"{article.link}:::{label}"] = {
                                'score': theme_score,
                                'cached_at': now_iso
                            }
                for idx, article in enumerate(batch):
                    if idx not in scored_in_batch:
                        for cfg in schedule.values():
                            key = f"{article.link}:::{cfg['label']}"
                            if key not in theme_cache:
                                theme_cache[key] = {'score': 50, 'cached_at': now_iso}
            except (json.JSONDecodeError, Exception) as sync_err:
                print(f"  ⚠️ Sync fallback error (batch {i//batch_size + 1}): {sync_err}")
                for article in batch:
                    for cfg in schedule.values():
                        key = f"{article.link}:::{cfg['label']}"
                        if key not in theme_cache:
                            theme_cache[key] = {'score': 50, 'cached_at': now_iso}
        save_theme_score_cache(theme_cache)
        print(f"   ✅ Sync fallback complete ({len(uncached)} articles × {len(schedule)} themes cached)")


def route_articles_to_best_themes(
    cached_articles: List[Dict],
    schedule_config: Dict,
    today_name: str,
) -> Dict:
    """Proactively bank articles that score significantly better on a future day's theme.

    For each article in the podcast cache that has a complete set of cached
    theme scores (all 7 days), compare today's score against every other day.
    When another day's score beats today's by at least ``theme_routing_gap``
    points AND meets ``theme_routing_min_score``, the article is banked into
    that day's holdover cache so it surfaces at the right time.

    Articles are NOT excluded from today's feed — cross-theme reuse is
    intentional. An article that fits both today and a future day will appear
    in both episodes, with the second appearance carrying ``_cross_theme``
    metadata identifying the prior episode.

    Articles missing a cached score for any theme are left for normal
    today-centric processing — routing only acts on complete data.

    Comparisons run on percentile-normalized scores (see
    ``normalize_theme_scores``). On raw scores this function was structurally
    one-way: the narrow weekday charters top out below ``theme_routing_min_score``,
    so no article could ever be routed *to* them.
    """
    schedule = schedule_config.get('schedule', {})
    routing_gap = schedule_config.get('theme_routing_gap', 20)
    routing_min_score = schedule_config.get('theme_routing_min_score', 55)
    holdover_threshold = schedule_config.get('holdover_threshold', 30)

    if not schedule or today_name not in schedule:
        return {'routed_by_target_day': {}, 'routed_count': 0}

    theme_cache = load_theme_score_cache()
    pool_links = {item['link'] for item in cached_articles}
    normalized = normalize_theme_scores(theme_cache, schedule, pool_links)
    to_bank: Dict[str, list] = defaultdict(list)  # {day_name: [(item_dict, score)]}

    for item in cached_articles:
        url = item['link']
        all_scores: Dict[str, int] = {}
        complete = True
        for day, cfg in schedule.items():
            pct = normalized.get(f"{url}:::{day}")
            if pct is None:
                complete = False
                break
            all_scores[day] = pct

        if not complete:
            continue

        today_score = all_scores[today_name]
        best_day = max(all_scores, key=lambda d: all_scores[d])
        best_score = all_scores[best_day]

        if (best_day != today_name
                and best_score - today_score >= routing_gap
                and best_score >= routing_min_score):
            to_bank[best_day].append((item, best_score))

    if to_bank:
        now_iso = datetime.now(timezone.utc).isoformat()
        holdover = load_theme_holdover_cache()
        total_banked = 0
        for day_name, day_articles in to_bank.items():
            existing_urls = {a['link'] for a in holdover.get(day_name, [])}
            for item, theme_score in day_articles:
                url = item['link']
                if url not in existing_urls and theme_score >= holdover_threshold:
                    holdover.setdefault(day_name, []).append({
                        'link': url,
                        'title': item['title'],
                        'description': item['description'],
                        'summary': item.get('summary', ''),
                        'excerpt': item.get('excerpt', ''),
                        'pub_date': item['pub_date'],
                        'source': item['source'],
                        'source_url': item['source_url'],
                        'score': item['score'],
                        'quality': item.get('quality', 0),
                        'local': item.get('local', 0),
                        'q_gate': item.get('q_gate'),
                        'category': item['category'],
                        'image': item.get('image'),
                        'theme_score': theme_score,
                        'banked_at': now_iso,
                    })
                    existing_urls.add(url)
                    total_banked += 1
        if total_banked:
            save_theme_holdover_cache(holdover)

        day_summary = ', '.join(
            f"{d} ({schedule[d]['label']}): {len(arts)}"
            for d, arts in sorted(to_bank.items())
        )
        total_candidates = sum(len(arts) for arts in to_bank.values())
        print(
            f"  🗓️  Theme routing: {total_candidates} articles banked for better-fit days"
            f" (gap ≥ {routing_gap}pts, min {routing_min_score}) → {day_summary}"
        )
        if total_banked:
            print(f"  📦 Pre-banked {total_banked} articles into upcoming day holdovers")

    # Articles are no longer excluded from today's feed — cross-theme reuse is
    # intentional: the same article can appear in multiple themed episodes,
    # with _cross_theme metadata on the second appearance. Return routing
    # stats for the calibration agent's audit data.
    return {
        'routed_by_target_day': {d: len(arts) for d, arts in to_bank.items()},
        'routed_count': sum(len(arts) for arts in to_bank.values()),
    }


def bank_articles_for_all_themes(
    cached_articles: List[Dict],
    schedule_config: Dict,
) -> Dict[str, int]:
    """Bank qualifying articles into the holdover cache for every themed day.

    Called on every run so that by the time a day's podcast generates, its
    holdover pool holds up to a week's worth of pre-scored candidates.
    Articles already present in the holdover (regardless of status) are skipped
    to avoid overwriting USED/SKIPPED annotations set after generation.

    ``holdover_threshold`` is applied to the percentile-normalized score, so it
    means "top (100 - threshold)% of this theme's candidates" rather than a raw
    cutoff that only the broad charters could ever clear.
    """
    theme_cache = load_theme_score_cache()
    schedule = schedule_config.get('schedule', {})
    global_threshold = schedule_config.get('holdover_threshold', 30)
    holdover = load_theme_holdover_cache()
    pool_links = {item['link'] for item in cached_articles}
    normalized = normalize_theme_scores(theme_cache, schedule, pool_links)
    now_iso = datetime.now(timezone.utc).isoformat()
    newly_banked: Dict[str, int] = defaultdict(int)

    for item in cached_articles:
        url = item['link']
        for day, cfg in schedule.items():
            threshold = cfg.get('holdover_threshold', global_threshold)
            pct = normalized.get(f"{url}:::{day}")
            if pct is None or pct < threshold:
                continue
            existing_urls = {a['link'] for a in holdover.get(day, [])}
            if url in existing_urls:
                continue
            holdover.setdefault(day, []).append({
                'link': url,
                'title': item['title'],
                'description': item['description'],
                'summary': item.get('summary', ''),
                'excerpt': item.get('excerpt', ''),
                'pub_date': item['pub_date'],
                'source': item['source'],
                'source_url': item['source_url'],
                'score': item['score'],
                'quality': item.get('quality', 0),
                'local': item.get('local', 0),
                'q_gate': item.get('q_gate'),
                'category': item['category'],
                'image': item.get('image'),
                'theme_score': pct,
                # Raw charter output kept alongside the percentile so scale
                # drift stays auditable after normalization hides it.
                'theme_score_raw': (theme_cache.get(f"{url}:::{cfg['label']}") or {}).get('score'),
                'banked_at': now_iso,
            })
            newly_banked[day] += 1

    if any(newly_banked.values()):
        save_theme_holdover_cache(holdover)

    total = sum(newly_banked.values())
    if total:
        summary = ', '.join(
            f"{d}: +{n}" for d, n in sorted(newly_banked.items()) if n
        )
        print(f"  📦 Banked {total} articles across all themes ({summary})")
    return dict(newly_banked)


def generate_podcast_feed(theme_name: str, cached_articles: List[Dict], podcast_shown_cache: Dict,
                          reserved_urls: set = None) -> Tuple[set, Optional[Dict]]:
    """Generate a themed podcast feed from weekly cached articles.

    Args:
        theme_name: Day name (e.g., 'monday', 'tuesday')
        cached_articles: List of article dicts from the weekly cache
        podcast_shown_cache: Dict of {"{url}:::{day}": entry} tracking which articles
            have appeared in each day's recent episodes. An article is excluded from
            today's feed only if it was already shown in THIS theme's episode — the
            same article can appear in multiple themed episodes (cross-theme reuse).

    Returns:
        Set of article URLs that were included in the generated feed, so the
        caller can update the shown cache.

    Each theme has associated categories and a custom scoring prompt.
    Articles from the weekly cache are evaluated by Claude for thematic fit,
    then the top articles are selected. Articles from outside the theme categories
    can still appear as bonus picks if they score high enough.
    """
    schedule_config = load_podcast_schedule()
    if not schedule_config or not schedule_config.get('enabled', False):
        return set(), None

    schedule = schedule_config['schedule']

    if theme_name not in schedule:
        print(f"⚠️ No podcast schedule entry for {theme_name}")
        return set(), None

    today = schedule[theme_name]
    theme_categories = today['categories']
    theme_label = today['label']
    theme_description = today.get('theme_description', today.get('description', ''))
    theme_scoring_prompt = today.get('scoring_prompt', '')
    theme_keywords = [kw.lower() for kw in today.get('keywords', [])]
    theme_anti_keywords = [kw.lower() for kw in today.get('anti_keywords', [])]
    max_articles = schedule_config.get('max_articles', 10)
    min_score = today.get('min_score', schedule_config.get('min_score', 25))
    include_bonus = schedule_config.get('include_top_from_other', 0)
    bonus_min_score = schedule_config.get('other_min_score', 70)
    holdover_threshold = today.get('holdover_threshold', schedule_config.get('holdover_threshold', 30))

    # Get API key for theme scoring
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("⚠️ No API key available for theme scoring")
        return set(), None

    # Convert cached article dicts to Article objects
    # Create a simple Article-like class for cached articles
    class CachedArticle:
        def __init__(self, data):
            self.title = data['title']
            self.link = data['link']
            self.description = data['description']
            self.summary = data.get('summary', '') or _clean_text(data['description'], max_chars=300)
            self.excerpt = data.get('excerpt', '') or _clean_text(data['description'], max_chars=600)
            self.pub_date = datetime.fromisoformat(data['pub_date'])
            self.source = data['source']
            self.source_url = data['source_url']
            self.score = data['score']
            # Absent dimensions stay 0 — the podcast composite renormalizes
            # weights over missing dims instead of substituting the interest
            # composite (the old default made Q/R silently equal `score`).
            self.quality = data.get('quality', 0)
            self.relevance = data.get('relevance', 0)
            self.local = data.get('local', 0)
            self.q_gate = data.get('q_gate')
            self.content_type = data.get('content_type')
            self.category = data['category']
            self.image = data.get('image')

    all_cached = [CachedArticle(item) for item in cached_articles]
    all_cached_urls = {a.link for a in all_cached}

    # Stage-by-stage pool composition tracing (PODCAST_POOL_DEBUG=1). "fresh" is
    # anything in the current 7-day weekly cache; "hold" is a cross-week holdover
    # carry-in. A feed whose final selection is 100% hold is a stale feed.
    _pool_debug = os.getenv('PODCAST_POOL_DEBUG') == '1'

    def _dbg(stage: str, items: List) -> None:
        if not _pool_debug:
            return
        links = [getattr(x, 'link', None) if not isinstance(x, tuple) else getattr(x[0], 'link', None)
                 for x in items]
        fresh = sum(1 for l in links if l in all_cached_urls)
        print(f"  🔬 [{theme_name}] {stage:<28} total={len(links):4d} fresh={fresh:4d} hold={len(links) - fresh:4d}")

    # Load cross-week holdover: articles that scored well on this theme in previous
    # runs and were banked for future episodes (28-day retention).
    holdover_cache = load_theme_holdover_cache()
    holdover_raw = holdover_cache.get(theme_name, [])

    def _holdover_eligible(item: Dict) -> bool:
        return (
            item.get('status') != 'USED'  # exclude articles already used in this theme's episode
            and f"{item['link']}:::{theme_name}" not in podcast_shown_cache
            and not _is_aggregator_url(item['link'])
            and item['link'] not in all_cached_urls  # already in 7-day pool
            # Quality floor on the interest-independent signal (q_gate/quality);
            # legacy entries without dims fall back to the stored composite.
            and (item.get('q_gate') or item.get('quality') or item.get('score', 0)) >= LIMITS['min_claude_score']
        )

    holdover_pool = []
    for item in holdover_raw:
        if not _holdover_eligible(item):
            continue
        carried = CachedArticle(item)
        # Percentile recorded when the article was banked. Carried through so the
        # bank can be ranked — and trimmed worst-first — when it has to make room
        # for current-week candidates at the pool cap below.
        carried.banked_theme_score = item.get('theme_score') or 0
        carried.banked_at = item.get('banked_at') or ''
        holdover_pool.append(carried)
    if holdover_pool:
        print(f"  📦 +{len(holdover_pool)} holdover articles from previous weeks")
    _dbg('holdover_pool', holdover_pool)
    _dbg('weekly_cache', all_cached)

    # The theme scoring prompt is the real semantic filter, so score ALL
    # quality-eligible articles — not just those in the day's primary categories.
    # theme_set marks which categories are "primary" for _is_bonus labelling only.
    theme_set = set(theme_categories)
    theme_pool = list(all_cached)

    # Filter by minimum quality: the per-day min_score is a floor on the
    # interest-independent quality signal (q_gate/quality dimension), NOT the
    # personal-interest composite — theme fit is judged by the theme prompt,
    # quality by the gate. Local articles pass on local strength; legacy
    # entries without dims fall back to the stored composite.
    def _pool_quality_ok(a) -> bool:
        if getattr(a, 'local', 0) >= 25:
            return True
        q = _podcast_quality(a)
        return (q if q is not None else a.score) >= min_score

    theme_pool = [a for a in theme_pool if _pool_quality_ok(a)]
    _dbg('after quality filter', theme_pool)

    # Track articles that qualify for this day's pool on upstream quality score
    # alone (not via rescue/holdover), so a theme-fit floor can be applied to
    # them after theme scoring below.
    direct_qualify_links = {a.link for a in theme_pool}

    # Percentile-normalized theme scores: raw charter output is not comparable
    # across themes, so every threshold below reads "top N% of this theme's
    # candidates" instead of an absolute cutoff only broad charters can clear.
    # Ranked over the 7-day pool so stale cache entries don't skew the spread.
    theme_score_cache = load_theme_score_cache()
    theme_pct = normalize_theme_scores(
        theme_score_cache, schedule, {a.link for a in all_cached}
    )

    def _theme_pct(link: str, default: int = 0) -> int:
        return theme_pct.get(f"{link}:::{theme_name}", default)

    # Rescue: include articles below the base threshold when they already rank
    # in this theme's top tier.  These proved their thematic fit even though
    # their general quality score is low (e.g. niche local sources).
    rescued = [
        a for a in all_cached
        if not _pool_quality_ok(a)
        and not _is_aggregator_url(a.link)
        and f"{a.link}:::{theme_name}" not in podcast_shown_cache
        and _theme_pct(a.link) >= holdover_threshold
    ]
    if rescued:
        print(f"  🌾 +{len(rescued)} theme-relevant articles rescued (base score < {min_score})")
        theme_pool.extend(rescued)
    _dbg('after rescue', theme_pool)

    # Merge holdover articles into the pool (already theme-qualified and quality-filtered above)
    theme_pool.extend(holdover_pool)
    _dbg('after holdover merge', theme_pool)

    # Exclude articles already used in a recent podcast episode.
    # Exception: allow articles shown *earlier today* for *today's theme* back into
    # the pool so the second daily run can do an additive refresh rather than
    # picking from the depleted remainder and overwriting the morning's better feed.
    before_shown_filter = len(theme_pool)
    _today_date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')

    def _available_for_today(link: str) -> bool:
        # An article is available unless it was already shown in THIS theme's episode.
        # The compound key allows the same article to appear in multiple themed episodes.
        entry = podcast_shown_cache.get(f"{link}:::{theme_name}")
        if entry is None:
            return True
        # Allow it back in if shown earlier today for this same theme (additive refresh)
        return entry.get('shown_at', '').startswith(_today_date_str)

    theme_pool = [a for a in theme_pool if _available_for_today(a.link)]
    shown_excluded = before_shown_filter - len(theme_pool)
    if shown_excluded:
        print(f"  🔄 Excluded {shown_excluded} articles already shown in recent podcast episodes")
    _dbg('after shown filter', theme_pool)

    # Exclude articles whose link goes through a search-engine aggregator
    # (e.g. Google News encoded proxy URLs). These opaque URLs defeat
    # cross-episode deduplication since the same story can have different
    # encoded links on different runs.
    before_agg = len(theme_pool)
    theme_pool = [a for a in theme_pool if not _is_aggregator_url(a.link)]
    agg_excluded = before_agg - len(theme_pool)
    if agg_excluded:
        print(f"  🚫 Excluded {agg_excluded} aggregator-URL articles (e.g. Google News)")
    _dbg('after aggregator filter', theme_pool)

    # Articles banked for other days via theme routing are NOT excluded here.
    # Cross-theme reuse is intentional — the same article may appear in multiple
    # themed episodes with _cross_theme metadata on the second appearance.

    # Cap the pool: keep only the top direct-qualify candidates, ranked by theme
    # fit for a reserved share of the slots and by quality score for the rest
    # (see the two-list fill below). Rescued/holdover articles are exempt from
    # the *quality* sort — they already proved thematic fit via a cached theme
    # score, so sorting by upstream quality score would systematically cut them
    # (that's exactly why they needed rescuing). Scoring them costs nothing
    # extra since their theme score is already cached.
    #
    # They are NOT, however, exempt from the cap itself. The bank grows every run
    # and the exemption used to be unbounded, so once it passed POOL_CAP the
    # direct-qualify allowance `room` fell to zero and no current-week article
    # could enter the pool at all — the episode regenerated purely from holdover
    # and its newest item sat a full week behind the run date. FRESH_POOL_SHARE
    # reserves a floor for current-week candidates; the reserve shrinks to what
    # is actually available, so a genuinely thin week still fills from the bank.
    POOL_CAP = 300
    FRESH_POOL_SHARE = 0.5
    # Share of the direct-qualify allowance held for the strongest theme fits,
    # and the percentile an article must reach to compete for one of those slots.
    THEME_RESERVE_SHARE = 0.4
    THEME_RESERVE_MIN_PCT = 80
    if len(theme_pool) > POOL_CAP:
        rescued_links = {a.link for a in rescued}
        holdover_links = {a.link for a in holdover_pool} - rescued_links
        # Rescued articles are current-week too, so they count toward the fresh
        # side and are never trimmed; only the cross-week bank gives up slots.
        rescued_in_pool = [a for a in theme_pool if a.link in rescued_links]
        from_bank = [a for a in theme_pool if a.link in holdover_links]
        cappable = [a for a in theme_pool
                    if a.link not in rescued_links and a.link not in holdover_links]

        fresh_reserve = min(len(cappable), int(POOL_CAP * FRESH_POOL_SHARE))
        bank_room = max(0, POOL_CAP - len(rescued_in_pool) - fresh_reserve)
        if len(from_bank) > bank_room:
            from_bank.sort(
                key=lambda a: (getattr(a, 'banked_theme_score', 0),
                               getattr(a, 'banked_at', '')),
                reverse=True,
            )
            print(f"  ✂️ Holdover bank trimmed {len(from_bank)} → {bank_room} "
                  f"to reserve {fresh_reserve} pool slots for current-week articles")
            from_bank = from_bank[:bank_room]
        protected = rescued_in_pool + from_bank
        room = max(0, POOL_CAP - len(protected))

        # Fill the direct-qualify allowance from two ranked lists, not one.
        # Ranking solely by a.score is theme-blind by construction — it is the
        # general-interest composite — so on a day whose subject matter sits
        # outside the corpus's high-scoring mainstream, the most on-theme
        # articles are cut here, before theme scoring ever sees them. On
        # 2026-08-30 the Thursday episode was built entirely from articles whose
        # raw charter scores were 10-20, while eight APTN First Nations stories
        # sitting at the 97th-99th theme percentile were dropped for scoring
        # 47-57 upstream against a cutoff of 67. Percentile normalization then
        # rescaled the survivors to look like a 90-100 fit, hiding the failure.
        #
        # Articles with no cached theme score default to percentile 0, so they
        # never take a reserve slot; they compete on quality exactly as before.
        theme_reserve = max(0, int(room * THEME_RESERVE_SHARE))
        on_theme = [a for a in cappable if _theme_pct(a.link) >= THEME_RESERVE_MIN_PCT]
        on_theme.sort(key=lambda a: (_theme_pct(a.link), a.score), reverse=True)
        reserved = on_theme[:theme_reserve]
        reserved_links = {a.link for a in reserved}

        by_quality = [a for a in cappable if a.link not in reserved_links]
        by_quality.sort(key=lambda a: a.score, reverse=True)

        theme_pool = protected + reserved + by_quality[:max(0, room - len(reserved))]
        print(f"  📊 Pool capped at top {room} direct-qualify articles "
              f"({len(reserved)} held for theme fit ≥ p{THEME_RESERVE_MIN_PCT}, "
              f"rest by quality score; +{len(protected)} rescued/holdover exempted)")
    _dbg('after POOL_CAP', theme_pool)

    # Score articles for thematic fit using Claude
    theme_scored = score_articles_for_theme(theme_pool, theme_scoring_prompt, theme_label, api_key)

    # Fallback: if scoring returned nothing despite having a pool, use quality scores directly
    if not theme_scored and theme_pool:
        print(f"  ⚠️ Theme scoring returned empty for {theme_label}, falling back to quality scores")
        theme_scored = [(article, article.score) for article in theme_pool]

    # Re-rank within the candidate set actually being selected from. This covers
    # holdover articles carried in from earlier weeks, which are absent from the
    # pool-wide ranking above. Raw scores are kept for stats and audit only.
    theme_raw = {a.link: ts for a, ts in theme_scored}
    theme_scored = [
        (article, pct)
        for (article, _), pct in zip(
            theme_scored, percentile_ranks([ts for _, ts in theme_scored])
        )
    ]
    _dbg('after theme scoring', theme_scored)
    if _pool_debug:
        _top = sorted(theme_scored, key=lambda x: x[1], reverse=True)[:max_articles * 3]
        _tf = sum(1 for a, _ in _top if a.link in all_cached_urls)
        print(f"  🔬 [{theme_name}] top-{len(_top)} by theme pct        "
              f"fresh={_tf:4d} hold={len(_top) - _tf:4d}")

    # Theme-fit floor for the direct-qualify path: articles that only entered the
    # pool via the upstream quality score (not rescue/holdover) must also rank
    # above the holdover_threshold percentile — unless they have a keyword hit —
    # so generic high-upstream-score content (e.g. local civic news boosted by
    # the Williams Lake bonus) doesn't crowd out genuinely on-theme picks on
    # its best-scoring but still-weak day.
    filtered_theme_scored = []
    floor_dropped = 0
    for article, theme_score in theme_scored:
        if article.link in direct_qualify_links and theme_score < holdover_threshold:
            kw_text = f"{article.title} {article.description or ''}".lower()
            if _net_keyword_match_count(kw_text, theme_keywords, theme_anti_keywords) == 0:
                floor_dropped += 1
                continue
        filtered_theme_scored.append((article, theme_score))
    if filtered_theme_scored:
        if floor_dropped:
            print(f"  🧹 Dropped {floor_dropped} direct-qualify articles below theme-fit floor "
                  f"({holdover_threshold}) with no keyword match")
        theme_scored = filtered_theme_scored
    elif floor_dropped:
        print(f"  ⚠️ Theme-fit floor would drop all {floor_dropped} candidates for {theme_label}; keeping unfiltered pool")
    _dbg('after theme-fit floor', theme_scored)

    # Keyword boost applies to T (theme dimension) before composite computation.
    # Rural context is no longer a hardcoded penalty — incorporate guidance into
    # the theme's scoring_prompt instead (configurable per day).
    kw_boost_val = schedule_config.get('keyword_boost', 10)
    kw_boost_cap = schedule_config.get('keyword_boost_cap', 5)
    bonus_thematic_boost = schedule_config.get('bonus_thematic_boost', 5)
    bonus_max_per_category = schedule_config.get('bonus_max_per_category', 3)

    _pod_weights = SCORING_WEIGHTS.get('podcast', {})
    _pod_w_q = _pod_weights.get('w_quality', 0.25)
    _pod_w_r = _pod_weights.get('w_relevance', 0.0)
    _pod_w_l = _pod_weights.get('w_local', 0.10)
    _pod_w_t = _pod_weights.get('w_theme', 0.65)

    def _podcast_composite(article, t_adjusted: float) -> int:
        # Use only dimensions that actually exist and renormalize weights over
        # the missing ones. The old `or score` fallback silently substituted
        # the personal-interest composite for Q and R on every Cohere-only,
        # cached, and holdover article — 30%+ of the podcast composite.
        parts = [(_pod_w_t, t_adjusted), (_pod_w_l, getattr(article, 'local', 0))]
        q = _podcast_quality(article)
        if q is not None:
            parts.append((_pod_w_q, q))
        r = getattr(article, 'relevance', 0)
        if _pod_w_r > 0 and r > 0 and not getattr(article, 'cohere_scored', False):
            parts.append((_pod_w_r, r))
        total_w = sum(w for w, _ in parts)
        raw = (sum(w * v for w, v in parts) / total_w) if total_w > 0 else t_adjusted
        return min(100, max(0, round(raw)))

    # Build scored pool: (article, composite_podcast, T_adjusted, T_raw, kw_hits)
    # Signals for deprioritizing legislative procedural milestone items without analysis
    _LEG_MILESTONES = ('second reading', 'third reading', 'first reading', 'royal assent', 'passes committee', 'committee stage')
    _ANALYSIS_SIGNALS = ('analysis', 'breakdown', 'what it means', 'what this means', 'would allow', 'would require', 'impact of', 'what the bill', 'what it does', 'proposes to')
    scored_pool = []
    for article, theme_score in theme_scored:
        kw_text = f"{article.title} {article.description or ''} {getattr(article, 'summary', '') or ''} {getattr(article, 'excerpt', '') or ''}".lower()
        raw_kw_hits = _net_keyword_match_count(kw_text, theme_keywords, theme_anti_keywords)
        kw_hits = min(raw_kw_hits, kw_boost_cap)
        t_adjusted = min(100, theme_score + kw_hits * kw_boost_val) if kw_boost_val > 0 else theme_score
        composite = _podcast_composite(article, t_adjusted)

        # Thin body: articles with < 280 chars of content across all text fields get
        # a composite penalty so they rank below articles with real reporting depth.
        _body_len = max(
            len((article.description or '').strip()),
            len((getattr(article, 'summary', '') or '').strip()),
            len((getattr(article, 'excerpt', '') or '').strip()),
        )
        if _body_len < 280:
            composite = max(0, composite - 15)

        # Legislation-only penalty: pure procedural milestone (passed X reading) with no
        # substantive analysis of what the bill actually does scores lower.
        _leg_text = f"{article.title} {article.description or ''}".lower()
        if (any(m in _leg_text for m in _LEG_MILESTONES)
                and not any(s in _leg_text for s in _ANALYSIS_SIGNALS)):
            composite = max(0, composite - 20)

        scored_pool.append((article, composite, t_adjusted, theme_score, raw_kw_hits))

    # Bank top-ranked articles for future episodes (percentile, same basis as
    # the threshold that will admit them back).
    banked_count = update_theme_holdover(theme_name, theme_label,
                          [(a, ts) for a, _, _, ts, _ in scored_pool],
                          holdover_threshold)

    if theme_keywords:
        # Split into theme-matched (>=1 keyword hit) and bonus candidates.
        # Bonus candidates from the day's primary categories get a small adjacency lift.
        kw_match = [t for t in scored_pool if t[4] > 0]
        non_match = [t for t in scored_pool if t[4] == 0]

        if bonus_thematic_boost:
            non_match = [
                (a, min(100, comp + bonus_thematic_boost) if a.category in theme_set else comp,
                 t_adj, ts, kh)
                for a, comp, t_adj, ts, kh in non_match
            ]

        kw_match.sort(key=lambda x: x[1], reverse=True)
        non_match.sort(key=lambda x: x[1], reverse=True)
        _dbg('kw_match candidates', kw_match)
        _dbg('non_match candidates', non_match)

        # Fill keyword-matched first, then bonus candidates capped per category.
        selected = list(kw_match[:max_articles])
        remaining = max_articles - len(selected)
        # Target ≥70% on-theme: when there are enough keyword-matched articles,
        # cap off-theme filler to 30% so the feed stays thematically coherent.
        if len(selected) >= int(max_articles * 0.70):
            remaining = min(remaining, max(2, int(max_articles * 0.30)))
        if remaining > 0 and non_match:
            category_counts = defaultdict(int)
            leftover = []
            added = 0
            for entry in non_match:
                article = entry[0]
                if added >= remaining or category_counts[article.category] >= bonus_max_per_category:
                    leftover.append(entry)
                    continue
                selected.append(entry)
                category_counts[article.category] += 1
                added += 1
            if remaining - added > 0:
                selected.extend(leftover[:remaining - added])

        selected.sort(key=lambda x: x[1], reverse=True)
        # theme_articles: (article, composite_podcast, T_raw)
        theme_articles = [(a, comp, ts) for a, comp, _, ts, _ in selected]
    else:
        scored_pool.sort(key=lambda x: x[1], reverse=True)
        theme_articles = [(a, comp, ts) for a, comp, _, ts, _ in scored_pool[:max_articles]]
    _dbg('SELECTED (theme_articles)', theme_articles)

    # Optionally include top articles from other categories as bonus picks
    # with theme-aware scoring for diversity
    bonus_entries = []
    if include_bonus > 0:
        # Collect all non-theme articles that meet minimum score
        other = []
        for article in all_cached:
            if article.category not in theme_set and article.score >= bonus_min_score \
                    and not _is_aggregator_url(article.link):
                other.append((article, article.category))

        theme_urls = {a.link for a, _, _ in theme_articles}
        other_filtered = [
            (a, c) for a, c in other
            if a.link not in theme_urls and f"{a.link}:::{theme_name}" not in podcast_shown_cache
        ]

        if other_filtered:
            # Score bonus articles for thematic fit
            other_articles = [a for a, _ in other_filtered]
            other_scored = score_articles_for_theme(other_articles, theme_scoring_prompt, theme_label, api_key)

            # Build scored list with category info
            scored_other = []
            cat_lookup = {a.link: c for a, c in other_filtered}
            for article, theme_score in other_scored:
                cat = cat_lookup.get(article.link, 'news')
                scored_other.append((article, theme_score, cat))

            # Sort by theme score descending
            scored_other.sort(key=lambda x: x[1], reverse=True)

            # Apply category diversity: cap each category in bonus set to prevent dominance
            max_per_category = schedule_config.get('bonus_max_per_category', 2)
            category_counts = defaultdict(int)

            for article, theme_score, cat in scored_other:
                # Check category cap
                if category_counts[cat] >= max_per_category:
                    continue

                bonus_composite = _podcast_composite(article, theme_score)
                bonus_entries.append((article, bonus_composite, theme_score))
                category_counts[cat] += 1

                if len(bonus_entries) >= include_bonus:
                    break

    all_entries = theme_articles + bonus_entries
    _dbg('FINAL (incl. bonus)', all_entries)

    if not all_entries:
        print(f"🎙️ Podcast feed ({theme_label}): no articles met criteria")
        return set(), None

    # Local BC sources that should never be marked _is_bonus on the Saturday feed
    LOCAL_BC_SOURCES = {
        "Williams Lake Tribune", "Quesnel Cariboo Observer", "100 Mile Free Press",
        "My Cariboo Now", "My East Kootenay Now", "CFJC Today Kamloops", "CBC Kamloops",
    }

    # Build the JSON Feed with podcast-specific metadata
    feed_config = FEEDS_CONFIG['feeds'].get('podcast', {})
    feed_filename = f"feed-podcast-{theme_name}.json"

    # Compute bonus_count for metadata using keyword-based logic
    def _is_bonus_article(article: object) -> bool:
        text = f"{article.title} {article.description or ''} {getattr(article, 'summary', '') or ''} {getattr(article, 'excerpt', '') or ''}".lower()
        kw_hits = _net_keyword_match_count(text, theme_keywords, theme_anti_keywords)
        if kw_hits > 0:
            return False
        # Local BC sources are never bonus on Saturday regardless of keyword score
        if theme_name == "saturday" and article.source in LOCAL_BC_SOURCES:
            return False
        return True

    bonus_count = sum(1 for a, _, _ in all_entries if _is_bonus_article(a))
    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": f"🎙️ {theme_label}",
        "home_page_url": FEEDS_CONFIG['base_url'],
        "feed_url": f"{FEEDS_CONFIG['base_url']}/{feed_filename}",
        "description": f"{theme_description} - {feed_config.get('description', 'Themed podcast feed from weekly articles')}",
        "icon": f"{FEEDS_CONFIG['base_url']}/favicon.ico",
        "authors": [{"name": FEEDS_CONFIG['author']}],
        "language": "en",
        "_podcast": {
            "theme": theme_label,
            "theme_description": theme_description,
            "theme_categories": theme_categories,
            "theme_scoring_prompt": theme_scoring_prompt,
            "day": theme_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "article_count": len(all_entries),
            "bonus_count": bonus_count,
            "scoring_method": "claude_theme_evaluation_weekly_cache"
        },
        "items": []
    }

    items_with_score = []
    for article, composite_podcast, theme_score in all_entries:
        text = f"{article.title} {article.description or ''} {getattr(article, 'summary', '') or ''} {getattr(article, 'excerpt', '') or ''}".lower()
        kw_matches = _net_keyword_match_count(text, theme_keywords, theme_anti_keywords)
        is_bonus = _is_bonus_article(article)
        clean_desc = _strip_markdown_links(article.description or "")
        has_source_in_title = (article.title.startswith(f"[{article.source}]")
                               or article.source in article.title)
        _item_body_len = max(
            len((article.description or '').strip()),
            len((getattr(article, 'summary', '') or '').strip()),
            len((getattr(article, 'excerpt', '') or '').strip()),
        )

        # Collect tags first (needed for badge)
        pod_tags: List[str] = []
        subscriber_label = SUBSCRIBER_ACCESS.get(article.source)
        if subscriber_label:
            pod_tags.append("subscriber-access")

        _us_scope = us_policy_scope(article.title, article.description or "")
        if _us_scope:
            pod_tags.append("us-policy")

        badge = _make_score_badge(
            score=article.score,
            quality=getattr(article, 'quality', article.score),
            relevance=getattr(article, 'relevance', article.score),
            local_score=getattr(article, 'local', 0),
            content_type=getattr(article, 'content_type', None),
            tags=pod_tags,
            composite_score=composite_podcast,
            theme_score=theme_score,
            kw_matches=kw_matches,
            is_bonus=is_bonus,
            podcast_days=[theme_name],
            article_url=article.link,
        )

        # image → badge → description
        content_html = badge + clean_desc
        if hasattr(article, 'image') and article.image:
            img_html = f'<img src="{html_escape(article.image)}" style="width:100%;max-height:300px;object-fit:cover;" />\n'
            content_html = img_html + content_html

        item = {
            "id": article.link,
            "url": article.link,
            "title": article.title if has_source_in_title else f"[{article.source}] {article.title}",
            "content_html": content_html,
            "summary": getattr(article, 'summary', '') or _clean_text(article.description, max_chars=300),
            "_excerpt": getattr(article, 'excerpt', '') or _clean_text(article.description, max_chars=600),
            "date_published": article.pub_date.isoformat(),
            "authors": [{"name": article.source, "url": article.source_url}],
            "ai_score": article.score,
            "_quality": getattr(article, 'quality', article.score),
            "_relevance": getattr(article, 'relevance', article.score),
            "_local": getattr(article, 'local', 0),
            "_theme_score": theme_score,
            # Charter's own 0-100 output, kept alongside the percentile because
            # normalization rescales the top of a collapsed distribution to
            # 90-100 and so cannot show scale drift. validate_podcast_feeds.py
            # reports on this field against a per-theme floor (the scales are
            # not comparable across themes — see its RAW_FIT_FLOORS).
            "_theme_score_raw": theme_raw.get(article.link),
            "_composite_podcast": composite_podcast,
            "_keyword_matches": kw_matches,
            "_category": article.category,
            "_source_category": article.category,
            "_is_bonus": is_bonus,
            **({"_thin_body": True} if _item_body_len < 280 else {}),
        }

        if hasattr(article, 'image') and article.image:
            item["image"] = article.image

        if _us_scope:
            item["_us_policy"] = True
            item["_us_policy_scope"] = _us_scope

        if pod_tags:
            item["tags"] = pod_tags

        if subscriber_label:
            apply_subscriber_links(item, article, subscriber_label)

        # Mark articles that previously appeared in a different theme's episode
        prior_appearances = [
            v for k, v in podcast_shown_cache.items()
            if k.startswith(f"{article.link}:::") and v.get('day') != theme_name
        ]
        if prior_appearances:
            prior = max(prior_appearances, key=lambda x: x['shown_at'])
            prior_day = prior.get('day', '')
            prior_label = schedule.get(prior_day, {}).get('label', prior_day)
            item['_cross_theme'] = {
                'day': prior_day,
                'label': prior_label,
                'shown_at': prior['shown_at']
            }
        items_with_score.append((composite_podcast, item))

    items_with_score.sort(key=lambda x: x[0], reverse=True)

    # Per-source cap: avoid 4+ articles from the same outlet in a single podcast episode.
    _pod_source_counts: Dict[str, int] = defaultdict(int)
    _pod_source_cap = 3
    _items_capped = []
    _items_dropped_source = 0
    for _score, _item in items_with_score:
        _src = (_item.get('authors') or [{}])[0].get('name', '')
        if _pod_source_counts[_src] < _pod_source_cap:
            _items_capped.append((_score, _item))
            _pod_source_counts[_src] += 1
        else:
            _items_dropped_source += 1
    if _items_dropped_source:
        print(f"  ✂️ Source cap ({_pod_source_cap}/outlet): dropped {_items_dropped_source} excess articles")
    items_with_score = _items_capped

    feed["items"] = [item for _, item in items_with_score]

    with open(feed_filename, 'w', encoding='utf-8') as f:
        json.dump(feed, f, indent=2, ensure_ascii=False)

    avg_theme_score = sum(ts for _, _, ts in theme_articles) / len(theme_articles) if theme_articles else 0
    avg_final_score = sum(cp for _, cp, _ in all_entries) / len(all_entries) if all_entries else 0
    # Raw charter mean over the selected set. Percentiles are uniform by
    # construction, so only this can reveal a charter drifting off-scale.
    selected_raw = [theme_raw[a.link] for a, _, _ in theme_articles if a.link in theme_raw]
    avg_theme_raw = sum(selected_raw) / len(selected_raw) if selected_raw else 0
    cross_cat = bonus_count
    print(f"🎙️ Podcast feed {theme_name} ({theme_label}): {len(all_entries)} articles (avg theme score: {avg_theme_score:.1f}, {cross_cat} cross-category)")

    feed_stats = {
        'article_count': len(all_entries),
        'bonus_count': bonus_count,
        'mean_final_score': round(avg_final_score, 1),
        'mean_theme_score': round(avg_theme_score, 1),
        'mean_theme_score_raw': round(avg_theme_raw, 1),
        'relative_scaled': True,
        'banked_count': banked_count,
    }
    return {a.link for a, _, _ in all_entries}, feed_stats


def generate_opml():
    """Generate OPML file with all category feeds and podcast feeds"""
    import xml.etree.ElementTree as ET

    opml = ET.Element('opml', version='1.0')
    head = ET.SubElement(opml, 'head')
    ET.SubElement(head, 'title').text = "Erich's Curated Feeds"
    ET.SubElement(head, 'dateCreated').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')

    body = ET.SubElement(opml, 'body')

    # Add category feeds
    category_folder = ET.SubElement(body, 'outline', {
        'text': 'Category Feeds',
        'title': 'Category Feeds'
    })

    for cat_key, cat_config in CATEGORIES.items():
        feed_title = f"{cat_config['emoji']} {cat_config['name']}"
        # Every outline is declared type="rss", so point at the real RSS mirror
        # wherever one exists — a reader that only speaks XML cannot do
        # anything with the JSON URL it would otherwise be handed.
        ext = 'xml' if FEEDS_CONFIG['feeds'].get(cat_key, {}).get('rss') else 'json'
        feed_url = f"{FEEDS_CONFIG['base_url']}/feed-{cat_key}.{ext}"

        ET.SubElement(category_folder, 'outline', {
            'type': 'rss',
            'text': feed_title,
            'title': feed_title,
            'xmlUrl': feed_url,
            'htmlUrl': FEEDS_CONFIG['base_url']
        })

    # Add podcast feeds
    schedule_config = load_podcast_schedule()
    if schedule_config and schedule_config.get('enabled', False):
        podcast_folder = ET.SubElement(body, 'outline', {
            'text': '🎙️ Themed Podcast Feeds',
            'title': '🎙️ Themed Podcast Feeds'
        })

        for day_name, day_config in schedule_config['schedule'].items():
            feed_title = f"🎙️ {day_config['label']}"
            feed_url = f"{FEEDS_CONFIG['base_url']}/feed-podcast-{day_name}.json"

            ET.SubElement(podcast_folder, 'outline', {
                'type': 'rss',
                'text': feed_title,
                'title': feed_title,
                'xmlUrl': feed_url,
                'htmlUrl': FEEDS_CONFIG['base_url']
            })

    tree = ET.ElementTree(opml)
    ET.indent(tree)  # the file is downloaded and read by hand; keep it legible
    tree.write('curated-feeds.opml', encoding='utf-8', xml_declaration=True)
    print("✅ Generated OPML file: curated-feeds.opml")


def main():
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    run_timestamp = datetime.now(timezone.utc).isoformat()
    run_stats: Dict = {
        'run_id': run_timestamp,
        'timestamp': run_timestamp,
        'slot': 'morning' if datetime.now(timezone.utc).hour < 12 else 'evening',
    }

    opml_path = sys.argv[1] if len(sys.argv) > 1 else 'feeds.opml'
    feeds = parse_opml(opml_path)

    lookback_hours = SYSTEM['lookback_hours']
    cutoff_date = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    print(f"\n📥 Fetching articles from last {lookback_hours} hours...")

    global _apple_news_cache
    _apple_news_cache = load_apple_news_cache()

    _feed_http_cache.load()
    # Feeds relocated or retired by the weekly health agent leave their old
    # OPML URL behind as a dead cache key. Drop those before the fetch loop so
    # the file tracks the live feed list rather than every URL ever polled.
    pruned = _feed_http_cache.prune_to(f['url'] for f in feeds)
    if pruned:
        print(f"  🧹 Pruned {pruned} HTTP cache entries for feeds no longer in the OPML")

    all_articles = []
    for feed in feeds:
        articles = fetch_feed_articles(feed, cutoff_date)
        all_articles.extend(articles)
    _feed_http_cache.save()

    all_articles = apply_prescore_filter(all_articles)

    wlt_articles = scrape_wlt_news()
    for wlt_entry in wlt_articles:
        class WLTEntry:
            def get(self, key, default=''):
                return wlt_entry.get(key, default)
        
        article = Article(WLTEntry(), 'Williams Lake Tribune', WLT_BASE_URL)
        article.title = wlt_entry['title']
        article.link = wlt_entry['link']
        article.description = wlt_entry['description']
        article.summary = wlt_entry.get('summary', '') or _clean_text(wlt_entry['description'], max_chars=300)
        article.excerpt = wlt_entry.get('excerpt', '') or _clean_text(wlt_entry['description'], max_chars=600)
        article.image = wlt_entry.get('image')
        article.score = LIMITS['local_priority_score']
        article.category = 'local'
        all_articles.append(article)

    topic_articles = fetch_topic_news(cutoff_date)
    all_articles.extend(topic_articles)

    kite_articles = fetch_kite_news(cutoff_date)
    all_articles.extend(kite_articles)

    print(f"\n📈 Total fetched: {len(all_articles)} articles")
    
    unique_articles = deduplicate_articles(all_articles)
    unique_articles = semantic_dedup_articles(unique_articles)

    shown_cache = _shown_cache.load()
    shown_terms_cache = _shown_terms_cache.load()

    # Build a list of term-sets for all recently-shown articles so we can
    # detect the same story arriving from a new source / URL on a later run.
    stored_term_sets = [
        frozenset(v['terms'])
        for v in shown_terms_cache.values()
        if v.get('terms')
    ]

    new_articles = []
    story_dupes = 0
    for a in unique_articles:
        if a.url_hash in shown_cache:
            continue
        # Cross-run story dedup: skip if ≥3 significant terms overlap with a
        # recently-shown article at ≥50% containment similarity.
        #
        # Both sides must carry ≥3 terms and share ≥3 of them, matching the
        # guards deduplicate_articles() already applies in-run. Containment is
        # |A∩B| / min(|A|,|B|), so without a shared-term floor a two-term stored
        # headline suppresses anything sharing a single common word: {'eggzellant',
        # 'review'} scores 0.50 against any headline containing "review".
        if (a.title_terms
                and len(a.title_terms) >= 3
                and any(
                    len(stored) >= 3
                    and len(a.title_terms & stored) >= 3
                    and _story_overlap(a.title_terms, stored) >= 0.50
                    for stored in stored_term_sets
                )):
            story_dupes += 1
            continue
        new_articles.append(a)

    print(
        f"🆕 New articles (not previously shown): {len(unique_articles)} → {len(new_articles)}"
        + (f"  ({story_dupes} cross-run story dupes suppressed)" if story_dupes else "")
    )

    run_stats['ingest'] = {
        'fetched': len(all_articles),
        'deduped': len(unique_articles),
        'new': len(new_articles),
        'cross_run_story_dupes': story_dupes,
    }

    if kagi_key := os.environ.get('KAGI_API_KEY', ''):
        _kagi_enrich_articles(new_articles, kagi_key, max_calls=10, prescore_keywords=PRESCORE_KEYWORDS)

    scored_articles = score_articles_with_claude(new_articles, api_key)

    # Phase 4: Dimension adjustments (L += local_bonus, Q += source_adjustment)
    # Replaces enforce_local_priority + apply_source_preferences.
    scored_articles = apply_dimension_adjustments(scored_articles)

    # Podcast candidate branch: capture theme-relevant articles BEFORE destructive
    # main-feed filters (haiku scrub, content-type filter, quality floor).
    # Articles killed by those filters may still score 90+ on a podcast theme —
    # e.g. a CBC recap of wildfire news, or a niche local story below the quality floor.
    # The rescue mechanism in generate_podcast_feed() will pull them in if they earn
    # a strong theme score here.
    schedule_config = load_podcast_schedule()
    podcast_candidates: List[Article] = []
    if schedule_config and schedule_config.get('enabled', False):
        _pod_keywords = _build_all_podcast_keywords(schedule_config)
        _pod_floor = LIMITS.get('quality_gate', {}).get('podcast_floor', 20)
        _pod_min = LIMITS.get('podcast_candidate_min_score', 5)
        def _pool_eligible(a: Article) -> bool:
            # Excluded sources are rejected by save_podcast_cache() too; skipping
            # them here as well avoids paying for their theme scores at ingest.
            if a.source in PODCAST_EXCLUDED_SOURCES:
                return False
            if getattr(a, 'content_type', None) == 'sponsored' or _is_aggregator_url(a.link):
                return False
            if getattr(a, 'local', 0) >= 25:
                return True
            q = _podcast_quality(a)
            if q is not None:
                # Absolute quality floor — no interest score, no keyword gate.
                # Theme fit is judged downstream by the theme scoring prompt;
                # keywords only boost T at generation time.
                return q >= _pod_floor
            # Legacy fallback (no gate ran, e.g. hybrid rollback mode): old
            # interest-composite + keyword gate.
            return a.score >= _pod_min and _article_matches_podcast_keywords(a, _pod_keywords)

        podcast_candidates = [a for a in scored_articles if _pool_eligible(a)]

        # Without the keyword gate the pool can balloon on heavy news days, and
        # every new pool entry costs 7 theme scores at ingest. Cap per-run
        # intake to the highest-quality candidates to bound API cost.
        _pod_cap = LIMITS.get('podcast_candidate_max_per_run', 250)
        if len(podcast_candidates) > _pod_cap:
            podcast_candidates.sort(
                key=lambda a: (_podcast_quality(a) or 0, getattr(a, 'local', 0)),
                reverse=True)
            podcast_candidates = podcast_candidates[:_pod_cap]

        print(f"🎙️  Podcast candidate branch: {len(podcast_candidates)} articles "
              f"(from {len(scored_articles)} scored, quality floor {_pod_floor}, "
              f"before scrub/quality-floor)")
        save_podcast_cache(podcast_candidates, main_feed_quality=False)

    if scored_articles:
        _scores = sorted(a.score for a in scored_articles)
        _n = len(_scores)
        _floor = LIMITS['min_claude_score']
        _scrub_floor = LIMITS.get('haiku_scrub_floor', 15)
        _above_floor = sum(1 for s in _scores if s >= _floor)
        _above_scrub = sum(1 for s in _scores if s >= _scrub_floor)
        print(
            f"📊 Score dist: n={_n}  "
            f"p25={_scores[_n // 4]}  p50={_scores[_n // 2]}  p75={_scores[3 * _n // 4]}  "
            f"above_scrub_floor(>={_scrub_floor})={_above_scrub}  "
            f"above_quality_floor(>={_floor})={_above_floor}"
        )

    _dim_hists = _dimensional_histograms(scored_articles)
    # q_gate distribution (global, not per-category — the gate runs before
    # categorization) so the calibration agent can tune gate_floor/podcast_floor.
    _qg_buckets = ["0-19", "20-39", "40-59", "60-79", "80-100"]
    _qg_hist = {b: 0 for b in _qg_buckets}
    _qg_values = [a.q_gate for a in scored_articles if getattr(a, 'q_gate', None) is not None]
    for _qg in _qg_values:
        _qg_hist[_qg_buckets[min(max(0, min(100, _qg)) // 20, 4)]] += 1
    run_stats['scoring'] = {
        'scored_count': len(scored_articles),
        'score_histogram_by_category': _score_histogram(scored_articles),
        'quality_histogram_by_category': _dim_hists['quality'],
        'relevance_histogram_by_category': _dim_hists['relevance'],
        'local_histogram_by_category': _dim_hists['local'],
        'q_gate_histogram': _qg_hist,
        'q_gate_scored_count': len(_qg_values),
        'content_type_breakdown_by_category': _content_type_breakdown(scored_articles),
    }

    # Phase 3: Hard content type filter — absolute, score-independent.
    # Drops fluff, sponsored, and non-local recaps regardless of composite score.
    scored_articles, content_type_stats = filter_by_content_type(scored_articles)
    run_stats['content_type_filter'] = content_type_stats

    # Haiku scrub: semantic safety net for subjects that slip past content_type filter
    # (e.g. sports articles classified as 'breaking'). Runs on articles above a low floor.
    # Articles below SCRUB_FLOOR are preserved for category floor rescue only.
    SCRUB_FLOOR = LIMITS.get('haiku_scrub_floor', 15)
    scrub_candidates = [a for a in scored_articles if a.score >= SCRUB_FLOOR]
    scrub_below = [a for a in scored_articles if a.score < SCRUB_FLOOR]
    print(f"\n✂️  Running headline scrub with Haiku ({len(scrub_candidates)} articles, {len(scrub_below)} below floor skipped)...")
    scrubbed, scrub_stats = scrub_feed_with_haiku(scrub_candidates, api_key)
    run_stats['scrub'] = scrub_stats
    _scrubbed_hashes = {a.url_hash for a in scrubbed}
    haiku_rejected = [a for a in scrub_candidates if a.url_hash not in _scrubbed_hashes]

    # Quality filter now works on pre-scrubbed candidates
    quality_articles = [a for a in scrubbed if a.score >= min_score_for_category(a.category)]
    print(f"⭐ Quality filter (composite >= {LIMITS['min_claude_score']}, "
          f"per-category overrides {LIMITS.get('min_score_by_category', {})}): "
          f"{len(scrubbed)} → {len(quality_articles)} articles")

    # Per-category floor: rescue the top-N articles for categories under their minimum quota.
    # Draws from the scrubbed pool (clean) plus below-floor articles so niche categories
    # aren't starved when all their content scored below SCRUB_FLOOR.
    min_per_cat = LIMITS.get('min_per_category', {})
    if min_per_cat:
        quality_urls = {a.url_hash for a in quality_articles}
        subthreshold = [a for a in scrubbed if a.url_hash not in quality_urls] + scrub_below
        quality_by_cat: Dict[str, int] = defaultdict(int)
        for a in quality_articles:
            quality_by_cat[a.category or 'news'] += 1
        by_cat: Dict[str, List[Article]] = defaultdict(list)
        for a in subthreshold:
            by_cat[a.category or 'news'].append(a)
        rescued: List[Article] = []
        for cat, floor in min_per_cat.items():
            need = floor - quality_by_cat.get(cat, 0)
            if need > 0:
                top = sorted(by_cat.get(cat, []), key=lambda a: a.score, reverse=True)
                rescued.extend(top[:need])
        if rescued:
            print(f"🌱 Category floors rescued {len(rescued)} additional articles")
            quality_articles.extend(rescued)

    # Phase 8: Category slot allocation — enforce min/max per category using feed_slots.json.
    # Runs after floor rescue so the full available pool is visible. When FEED_SLOTS is empty
    # (config missing), this is a no-op and the existing min_per_category/max_new_per_category
    # limits.json knobs remain in effect.
    quality_articles = apply_feed_slot_allocation(quality_articles)

    scrubbed_by_cat: Dict[str, int] = defaultdict(int)
    for a in scrubbed:
        scrubbed_by_cat[a.category or 'news'] += 1
    passed_by_cat: Dict[str, int] = defaultdict(int)
    for a in quality_articles:
        passed_by_cat[a.category or 'news'] += 1
    run_stats['quality_gate'] = {
        'passed_count': len(quality_articles),
        'passed_by_category': dict(passed_by_cat),
        'dropped_below_floor_by_category': {
            cat: max(0, scrubbed_by_cat.get(cat, 0) - passed_by_cat.get(cat, 0))
            for cat in scrubbed_by_cat
        },
    }

    # Fetch images for quality articles only (after filtering). The same page
    # fetch harvests any apple.news IDs the publisher exposes — no extra request.
    print(f"🖼️  Fetching images for quality articles...")
    _apple_before = len(_apple_news_cache.get('channels', {}))
    quality_articles = batch_fetch_images(
        quality_articles, max_fetch=50, apple_news_cache=_apple_news_cache
    )
    images_found = sum(1 for a in quality_articles if hasattr(a, 'image') and a.image)
    print(f"   Found images for {images_found}/{len(quality_articles)} articles")

    _apple_channels = _apple_news_cache.get('channels', {})
    print(
        f"📰 Apple News: {len(_apple_news_cache.get('articles', {}))} article links cached, "
        f"{len(_apple_channels)} channels known "
        f"(+{len(_apple_channels) - _apple_before} new)"
    )
    save_apple_news_cache(_apple_news_cache)
    
    categorized = defaultdict(list)
    for article in quality_articles:
        category = article.category or 'news'
        categorized[category].append(article)
    
    print(f"\n📂 Categorization results:")
    for cat_key in CATEGORIES.keys():
        count = len(categorized[cat_key])
        print(f"  {cat_key}: {count} articles")

    categorized = dedup_across_categories(categorized)

    # Save quality articles to weekly podcast cache
    save_podcast_cache(quality_articles)

    # Score all themes at ingest using the broader podcast candidate pool (not just
    # quality_articles) so articles captured before the scrub/quality-floor also get
    # theme scores. The rescue mechanism in generate_podcast_feed() then picks them up.
    process_pending_theme_batch(api_key)
    score_all_themes_at_ingest(podcast_candidates or quality_articles, schedule_config, api_key)

    # Snapshot per-theme score distributions for the calibration agent. This reflects
    # the full cumulative cache (not just this run's deltas), which is what matters
    # for detecting theme-score collapse over time.
    if schedule_config and schedule_config.get('enabled', False):
        theme_score_snapshot = load_theme_score_cache()
        buckets = ["0-19", "20-39", "40-59", "60-79", "80-100"]
        theme_scoring_stats: Dict[str, Dict] = {}
        for day, cfg in schedule_config.get('schedule', {}).items():
            label = cfg['label']
            suffix = f":::{label}"
            scores = [v['score'] for k, v in theme_score_snapshot.items() if k.endswith(suffix)]
            if not scores:
                continue
            hist = {b: 0 for b in buckets}
            for s in scores:
                idx = min(max(0, min(100, s)) // 20, 4)
                hist[buckets[idx]] += 1
            theme_scoring_stats[day] = {
                'scored': len(scores),
                'histogram': hist,
                'mean': round(sum(scores) / len(scores), 1),
                'max': max(scores),
            }
        run_stats['theme_scoring'] = theme_scoring_stats

    # Load weekly cache for podcast feed generation
    podcast_cache = load_podcast_cache()

    # Generate ALL 7 themed podcast feeds from the accumulated weekly staging pool.
    # Ingest-time scoring (score_all_themes_at_ingest) already rates every cached
    # article against every theme, so regenerating a non-today feed is a pure
    # cache read with no extra Claude calls. Refreshing daily (instead of only on
    # each theme's calendar day) means a single failed/skipped run no longer
    # leaves a feed stale for up to a week.
    print(f"\n🎙️ Generating all themed podcast feeds from {len(podcast_cache)} cached articles...")
    if schedule_config and schedule_config.get('enabled', False):
        today_name = datetime.now(ZoneInfo('America/Vancouver')).strftime('%A').lower()
        podcast_shown_cache = load_podcast_shown_cache()
        # Bank qualifying articles into every day's holdover staging pool.
        banking_stats = bank_articles_for_all_themes(podcast_cache, schedule_config)
        run_stats['theme_routing'] = {
            'routed_by_target_day': banking_stats,
            'routed_count': sum(banking_stats.values()),
        }
        day_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        podcast_feed_stats: Dict[str, Dict] = {}
        now_iso = datetime.now(timezone.utc).isoformat()
        today_date_str = now_iso[:10]
        for day in day_order:
            if day not in schedule_config['schedule']:
                continue
            label = schedule_config['schedule'][day]['label']
            selected_urls, feed_stats = generate_podcast_feed(
                day, podcast_cache, podcast_shown_cache
            )
            if feed_stats:
                podcast_feed_stats[day] = feed_stats

            # Mark this day's holdover entries as USED or SKIPPED for auditing.
            if selected_urls is not None:
                _hov = load_theme_holdover_cache()
                day_staged = _hov.get(day, [])
                used_count = skipped_count = 0
                for article in day_staged:
                    if article['link'] in selected_urls:
                        article['status'] = 'USED'
                        used_count += 1
                    elif article.get('status') != 'USED':
                        article['status'] = 'SKIPPED'
                        skipped_count += 1
                if day_staged:
                    _hov[day] = day_staged
                    save_theme_holdover_cache(_hov)
                    print(f"  ♻️  [{label}] Holdover status: {used_count} USED, {skipped_count} SKIPPED")

            if selected_urls:
                newly_marked = 0
                compound_key = lambda u: f"{u}:::{day}"
                for url in selected_urls:
                    existing = podcast_shown_cache.get(compound_key(url), {})
                    # Don't overwrite a same-day entry so the original shown_at is preserved
                    if not existing.get('shown_at', '').startswith(today_date_str):
                        podcast_shown_cache[compound_key(url)] = {'day': day, 'shown_at': now_iso}
                        newly_marked += 1
                print(f"  📌 [{label}] Marked {newly_marked} new articles as shown ({len(selected_urls) - newly_marked} already in episode)")

        save_podcast_shown_cache(podcast_shown_cache)
        run_stats['podcast_feeds'] = podcast_feed_stats

        holdover_cache_snapshot = load_theme_holdover_cache()
        run_stats['holdover'] = {
            'bank_size_by_day_eod': {
                day: len(arts) for day, arts in holdover_cache_snapshot.items()
            },
            'banked_today': sum(s.get('banked_count', 0) for s in podcast_feed_stats.values()),
        }

        print(f"\n📅 Podcast day buckets:")
        for day in day_order:
            if day not in schedule_config['schedule']:
                continue
            label = schedule_config['schedule'][day]['label']
            count = podcast_feed_stats.get(day, {}).get('article_count', 0)
            marker = ' [TODAY]' if day == today_name else ''
            print(f"  {day} ({label}): {count} articles{marker}")

    # Generate daily review feed for user training feedback
    generate_review_feed(quality_articles, scrubbed, schedule_config, haiku_rejected)

    # Load existing feeds to preserve old articles
    retention_days = LIMITS['feed_retention_days']
    retention_cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)

    final_feed_sizes: Dict[str, int] = {}

    for cat_key in CATEGORIES.keys():
        feed_file = f"feed-{cat_key}.json"
        existing_articles = []
        
        if os.path.exists(feed_file):
            try:
                with open(feed_file, 'r') as f:
                    existing_feed = json.load(f)
                    for item in existing_feed.get('items', []):
                        pub_date = datetime.fromisoformat(item['date_published'].replace('Z', '+00:00'))
                        if pub_date > retention_cutoff:
                            existing_articles.append(item)
            except Exception as e:
                print(f"⚠️ Error loading existing {cat_key} feed: {e}")
        
        new_items = categorized[cat_key]
        diverse_new = apply_diversity_limits(new_items, cat_key)
        diverse_new = dedup_by_story_group(diverse_new)
        diverse_new = dedup_by_term_cluster(
            diverse_new,
            overlap_threshold=LIMITS.get('story_cluster_overlap_threshold', 0.60),
            max_per_cluster=LIMITS.get('max_per_story_cluster', 2),
        )

        cat_cap = LIMITS.get('max_new_per_category', {}).get(cat_key)
        if cat_cap and len(diverse_new) > cat_cap:
            print(f"🔢 Category cap ({cat_key}): {len(diverse_new)} → {cat_cap} articles")
            diverse_new = diverse_new[:cat_cap]

        # Filter retained articles: drop any whose URL or story terms overlap with a new article.
        # Prevents the same story from accumulating across runs within the 7-day window.
        merge_overlap = LIMITS.get('feed_merge_overlap_threshold', 0.50)
        merge_min_terms = LIMITS.get('feed_merge_min_terms', 2)
        new_urls = {a.link for a in diverse_new}
        new_term_sets = [(a.title_terms) for a in diverse_new]

        def _retained_is_fresh(item: dict) -> bool:
            item_url = item_source_link(item)
            if item_url in new_urls:
                return False
            if '/weekly-report-' in item_url:
                # Weekly "State of the Feed" meta-article. Its title is short and
                # generic ("State of the Feed — Week of <Month> <year>"), so the
                # containment-similarity check below false-positives against any
                # ordinary headline sharing two of those terms (e.g. a month/year
                # date). It isn't a news story that can duplicate one, so it's
                # exempt from story-overlap dedup entirely.
                return True
            _raw_title = re.sub(r'^(?:🔓\s*)+', '', item.get('title', ''))
            r_terms = _term_set(re.sub(r'^\[.*?\]\s*', '', _raw_title).lower())
            if len(r_terms) < merge_min_terms:
                return True
            for nt in new_term_sets:
                if len(nt) >= merge_min_terms:
                    ov = _story_overlap(r_terms, nt)
                    if ov >= merge_overlap and len(r_terms & nt) >= merge_min_terms:
                        return False
            return True

        fresh_existing = [item for item in existing_articles if _retained_is_fresh(item)]
        if len(fresh_existing) < len(existing_articles):
            print(f"🗂️  Feed merge dedup ({cat_key}): {len(existing_articles)} → {len(fresh_existing)} retained articles")

        all_items = diverse_new + [
            type('Article', (), {
                'link': item_source_link(item),
                'title': re.sub(r'^(?:🔓\s*)+', '', item['title']),
                'description': item['content_html'],
                'pub_date': datetime.fromisoformat(item['date_published'].replace('Z', '+00:00')),
                'source': item['authors'][0]['name'],
                'source_url': item['authors'][0]['url'],
                'score': item.get('_score', 0),
                'quality': item.get('_quality', 0),
                'relevance': item.get('_relevance', 0),
                'local': item.get('_local_score', 0),
                'content_type': item.get('_content_type'),
                'image': item.get('image')
            })() for item in fresh_existing
        ]
        
        all_items.sort(key=lambda a: a.pub_date, reverse=True)
        all_items = all_items[:LIMITS['max_feed_size']]

        final_feed_sizes[cat_key] = len(all_items)

        generate_json_feed(all_items, cat_key, feed_file)

    run_stats['final_feeds'] = final_feed_sizes

    now_ts = datetime.now(timezone.utc).timestamp()
    for article in quality_articles:
        shown_cache[article.url_hash] = now_ts
        shown_terms_cache[article.url_hash] = {
            'ts': now_ts,
            'terms': list(article.title_terms),
        }
    _shown_cache.save(shown_cache)
    _shown_terms_cache.save(shown_terms_cache)
    
    generate_opml()
    
    print("\n📊 Final stats:")
    print(f"  Total sources: {len(feeds)}")
    print(f"  Articles fetched: {len(all_articles)}")
    print(f"  After dedup: {len(unique_articles)}")
    print(f"  New articles: {len(new_articles)}")
    print(f"  After scoring: {len(quality_articles)}")
    print(f"  Brave API calls: {_brave_call_count}")

    api_summary = api_usage.format_summary()
    if api_summary:
        print(api_summary)

    run_stats['api_usage'] = api_usage.get_summary_dict()
    record_run_stats(run_stats)

    print("\n✅ Feed generation complete!")


def load_reviewed_urls() -> set:
    """Every URL the user has already rated, so review feeds never re-surface one.

    Reads `feedback/reviewed_urls.json` — the compact ledger maintained by
    feedback_archive.py — and unions in any live `feedback/YYYY-MM-DD.json` files, which
    covers ratings submitted since the last archiver run. Falls back cleanly to the live
    files alone when the ledger does not exist yet.
    """
    reviewed_urls: set = set()
    feedback_dir = Path('feedback')

    ledger_file = feedback_dir / 'reviewed_urls.json'
    try:
        ledger = json.loads(ledger_file.read_text(encoding='utf-8'))
        reviewed_urls.update(ledger.get('urls', {}).keys())
    except Exception:
        pass

    if feedback_dir.exists():
        for f in feedback_dir.glob('????-??-??.json'):
            try:
                with open(f, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                for r in data.get('ratings', []):
                    if r.get('url'):
                        reviewed_urls.add(r['url'])
            except Exception:
                pass

    return reviewed_urls


def generate_review_feed(quality_articles: List[Article], scrubbed: List[Article],
                         schedule_config: Optional[Dict],
                         haiku_rejected: Optional[List[Article]] = None):
    """Select 20 articles for daily training feedback and write feed-review.json."""
    # Load already-reviewed URLs so we don't surface the same article twice.
    reviewed_urls = load_reviewed_urls()

    today_name = datetime.now(ZoneInfo('America/Vancouver')).strftime('%A').lower()
    today_label = ''
    day_labels: Dict[str, str] = {}
    if schedule_config and schedule_config.get('enabled'):
        for day, cfg in schedule_config.get('schedule', {}).items():
            day_labels[day] = cfg.get('label', day.capitalize())
        today_label = day_labels.get(today_name, '')

    theme_cache = load_theme_score_cache()

    # Surface the same percentile-normalized scores the pipeline selects on, so
    # the day picker in review.html — and the routing_bug/scoring_miss split
    # article_review_audit.py derives from these ratings — reflect what actually
    # drove routing rather than the incomparable raw charter output.
    theme_pct = normalize_theme_scores(
        theme_cache,
        (schedule_config or {}).get('schedule', {}),
        {a['link'] for a in load_podcast_cache()},
    )

    def theme_scores(article: Article) -> Dict[str, int]:
        return {day: theme_pct.get(f"{article.link}:::{day}", 0) for day in day_labels}

    def theme_scores_raw(article: Article) -> Dict[str, int]:
        out: Dict[str, int] = {}
        for day, label in day_labels.items():
            entry = theme_cache.get(f"{article.link}:::{label}", {})
            out[day] = entry.get('score', 0) if isinstance(entry, dict) else 0
        return out

    # Merge pools: scrubbed is the superset (quality + below-floor).
    # quality_articles may have been enlarged by floor rescue so union both.
    all_by_hash: Dict[str, Article] = {a.url_hash: a for a in scrubbed}
    for a in quality_articles:
        all_by_hash[a.url_hash] = a
    candidates = [a for a in all_by_hash.values() if a.link not in reviewed_urls]

    high   = sorted([a for a in candidates if a.score >= 80],  key=lambda a: a.score, reverse=True)
    mid    = sorted([a for a in candidates if 50 <= a.score < 80], key=lambda a: a.score, reverse=True)
    border = sorted([a for a in candidates if 30 <= a.score < 50], key=lambda a: a.score, reverse=True)
    low    = sorted([a for a in candidates if 20 <= a.score < 30], key=lambda a: a.score, reverse=True)

    selected: List[Article] = []
    seen_hashes: set = set()
    seen_sources: set = set()

    def pick(pool: List[Article], n: int):
        for a in pool:
            if len([x for x in selected if x in pool]) >= n:
                break
            if a.url_hash in seen_hashes or a.source in seen_sources:
                continue
            selected.append(a)
            seen_hashes.add(a.url_hash)
            seen_sources.add(a.source)

    for pool, quota in [(high, 5), (mid, 8), (border, 5), (low, 2)]:
        taken = 0
        for a in pool:
            if taken >= quota:
                break
            if a.url_hash in seen_hashes or a.source in seen_sources:
                continue
            selected.append(a)
            seen_hashes.add(a.url_hash)
            seen_sources.add(a.source)
            taken += 1

    # Fill any shortfall from the mid-range pool
    if len(selected) < 20:
        for a in mid:
            if len(selected) >= 20:
                break
            if a.url_hash not in seen_hashes and a.source not in seen_sources:
                selected.append(a)
                seen_hashes.add(a.url_hash)
                seen_sources.add(a.source)

    # Unfiltered slot: up to 10 haiku-rejected articles so over-filtering patterns
    # are visible in the review cycle.
    unfiltered_set: set = set()
    if haiku_rejected:
        for a in haiku_rejected:
            if len(unfiltered_set) >= 10:
                break
            if a.link in reviewed_urls or a.url_hash in seen_hashes or a.source in seen_sources:
                continue
            selected.append(a)
            seen_hashes.add(a.url_hash)
            seen_sources.add(a.source)
            unfiltered_set.add(a.url_hash)

    # Tag each with its selection bucket
    high_set   = {a.url_hash for a in high[:5]}
    mid_set    = {a.url_hash for a in mid[:8]}
    border_set = {a.url_hash for a in border[:5]}
    low_set    = {a.url_hash for a in low[:2]}

    def bucket_label(a: Article) -> str:
        if a.url_hash in unfiltered_set: return 'unfiltered'
        if a.url_hash in high_set:   return 'high'
        if a.url_hash in mid_set:    return 'mid'
        if a.url_hash in border_set: return 'border'
        if a.url_hash in low_set:    return 'low'
        return 'mid'

    now_iso = datetime.now(timezone.utc).isoformat()
    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": "📋 Daily Review — Article Training Feedback",
        "home_page_url": FEEDS_CONFIG['base_url'],
        "feed_url": f"{FEEDS_CONFIG['base_url']}/feed-review.json",
        "description": "20 articles for daily training feedback",
        "authors": [{"name": FEEDS_CONFIG['author']}],
        "language": "en",
        "_generated_at": now_iso,
        "_today": today_name,
        "_today_label": today_label,
        "_categories": {
            slug: {"name": cfg["name"], "emoji": cfg.get("emoji", "")}
            for slug, cfg in CATEGORIES.items()
        },
        "items": [],
    }

    for article in selected:
        item = {
            "id": article.link,
            "url": article.link,
            "title": article.title,
            "content_html": _strip_markdown_links(article.description or ""),
            "date_published": article.pub_date.isoformat(),
            "authors": [{"name": article.source, "url": article.source_url}],
            "_score": article.score,
            "_quality": article.quality,
            "_relevance": article.relevance,
            "_local_score": article.local,
            "_category": article.category or 'news',
            "_content_type": article.content_type,
            "_selection_bucket": bucket_label(article),
            "_theme_scores": theme_scores(article),
            "_theme_scores_raw": theme_scores_raw(article),
            "_today": today_name,
            "_today_label": today_label,
        }
        if getattr(article, 'image', None):
            item['image'] = article.image

        # review.html keys every rating on `url` and the feedback ledger has to
        # stay joinable with pipeline links, so `url` is always the publisher URL
        # here. Apple News rides along as a separate badge instead of a swap.
        subscriber_label = SUBSCRIBER_ACCESS.get(article.source)
        if subscriber_label:
            item['_subscriber_access'] = subscriber_label
            if subscriber_label.startswith('Apple News'):
                apple_url, _tier = resolve_apple_news_url(article, _apple_news_cache)
                if apple_url:
                    item['_apple_news_url'] = apple_url

        feed['items'].append(item)

    with open('feed-review.json', 'w', encoding='utf-8') as fh:
        json.dump(feed, fh, indent=2, ensure_ascii=False)

    unfiltered_count = len(unfiltered_set)
    print(f"📋 Review feed: {len(feed['items'])} articles "
          f"(20 curated + {unfiltered_count} unfiltered, "
          f"{len(reviewed_urls)} already-reviewed excluded)")


def bootstrap_feeds_from_podcast_cache(api_key: str = ''):
    """Repopulate empty feed JSON files from the podcast articles cache.

    Reads podcast_articles_cache.json (7-day retention) and re-scores every
    article through the live scoring pipeline (Cohere if enabled, Claude otherwise)
    so backlog articles get scores consistent with what new articles receive.
    Writes qualifying articles directly into the feed-*.json files, bypassing the
    shown-cache filter.  Intended as a one-time recovery after the Cohere scoring
    bug drained the feeds.  Run before the normal curator so the retention mechanism
    can merge these articles with new ones on the next scheduled CI run.
    """
    if not os.path.exists(PODCAST_CACHE_FILE):
        print("❌ podcast_articles_cache.json not found")
        return

    # Read-only here: bootstrap does no page fetching, so it can resolve against
    # links a previous run harvested but cannot learn new ones.
    global _apple_news_cache
    _apple_news_cache = load_apple_news_cache()

    try:
        with open(PODCAST_CACHE_FILE, 'r', encoding='utf-8') as f:
            cached = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load podcast cache: {e}")
        return

    retention_cutoff = datetime.now(timezone.utc) - timedelta(days=LIMITS['feed_retention_days'])

    # Build Article objects from podcast cache entries so we can pass them through
    # the scoring pipeline rather than using their stored (Claude-era) scores.
    articles: List[Article] = []
    skipped = 0
    for item in cached:
        link = item.get('link', '')
        if not link:
            skipped += 1
            continue
        # Skip podcast-only candidates — bootstrap should only repopulate feeds with
        # articles that passed the full main-feed quality pipeline. Old cache entries
        # without the flag default to True for backward compatibility.
        if not item.get('main_feed_quality', True):
            skipped += 1
            continue
        try:
            pub_date = datetime.fromisoformat(item['pub_date'])
        except Exception:
            skipped += 1
            continue
        if pub_date <= retention_cutoff:
            skipped += 1
            continue
        entry = _AttrDict({
            'title': item.get('title', ''),
            'link': link,
            'description': item.get('description', '') or item.get('summary', ''),
            'summary': item.get('summary', ''),
            'published_parsed': None,
            'updated_parsed': None,
            'media_thumbnail': [],
            'media_content': [],
            'enclosures': [],
        })
        try:
            article = Article(entry, item.get('source', ''), item.get('source_url', ''))
            article.pub_date = pub_date
            if item.get('image'):
                article.image = item['image']
            # Preserve original category as a hint; scoring may override it
            article.category = item.get('category') or 'news'
            article.score = item.get('score', 0)
            articles.append(article)
        except Exception:
            skipped += 1

    print(f"📦 Bootstrap: {len(cached)} cached → {len(articles)} within retention ({skipped} skipped)")

    # Score through the live pipeline so backlog articles get the same treatment
    # as new articles.  Check the scored_articles_cache first so articles already
    # scored with valid Q/R/L dimensional entries are not re-scored unnecessarily.
    # Only articles missing from the cache, or present in the old single-score
    # format (no 'quality' key), are sent to the scoring API.
    if cohere_integration.is_enabled():
        try:
            interests = config_loader.load_news_interests().strip()
        except Exception:
            interests = 'Technology, science, climate, local news'

        scored_cache = _scored_cache.load()
        already_cached: List[Article] = []
        uncached_bootstrap: List[Article] = []
        for article in articles:
            entry = scored_cache.get(article.url_hash)
            if entry and 'quality' in entry:
                article.score = entry['score']
                article.quality = entry['quality']
                article.relevance = entry['relevance']
                article.local = entry.get('local', 0)
                article.category = entry.get('category', article.category) or 'news'
                already_cached.append(article)
            else:
                uncached_bootstrap.append(article)

        print(f"🔮 Bootstrap Cohere scoring: {len(already_cached)} cached, "
              f"{len(uncached_bootstrap)} need scoring...")

        if uncached_bootstrap:
            rerank_scores = cohere_integration.score_with_rerank(uncached_bootstrap, interests)
            if not rerank_scores:
                print("⚠️  Cohere returned no scores — keeping stored podcast-cache scores")
            else:
                timestamp = datetime.now(timezone.utc).timestamp()
                for article in uncached_bootstrap:
                    # Fall back to the stored podcast-cache score so a Cohere API hiccup
                    # does not zero out every article and produce an empty bootstrap.
                    score, _ = rerank_scores.get(article.url_hash, (article.score, ''))
                    article.score = score
                    article.quality = score
                    article.relevance = score
                    article.local = 0
                    # Re-derive category from keywords so it matches the regular pipeline
                    article.category = (categorize_article(article.title, article.description)
                                         or article.category or 'news')
                    scored_cache[article.url_hash] = {
                        'score': score,
                        'quality': score,
                        'relevance': score,
                        'local': 0,
                        'category': article.category,
                        'story_group': None,
                        'timestamp': timestamp,
                    }
                _scored_cache.save(scored_cache)
                print(f"   ✅ Scored and cached {len(uncached_bootstrap)} new articles")

        articles = already_cached + uncached_bootstrap

    elif api_key:
        # Claude fallback — uses the scored_articles_cache so already-cached articles
        # are free; only articles not yet in cache will be billed.
        print(f"🤖 Scoring bootstrap articles through Claude...")
        articles = score_articles_with_claude(articles, api_key)
    else:
        print("⚠️  No scoring API available — using stored podcast-cache scores")

    articles = apply_dimension_adjustments(articles)

    quality_articles = [a for a in articles if a.score >= min_score_for_category(a.category)]
    print(f"⭐ Quality filter (score >= {LIMITS['min_claude_score']}, "
          f"per-category overrides {LIMITS.get('min_score_by_category', {})}): "
          f"{len(articles)} → {len(quality_articles)} articles")

    # Group by category
    categorized: Dict[str, List[Article]] = defaultdict(list)
    for article in quality_articles:
        cat = article.category or 'news'
        if cat not in CATEGORIES:
            cat = 'news'
        categorized[cat].append(article)

    print(f"\n📂 Bootstrap categorization:")
    for cat_key in CATEGORIES.keys():
        print(f"  {cat_key}: {len(categorized[cat_key])} articles")

    total_written = 0
    for cat_key in CATEGORIES.keys():
        items: List[Article] = sorted(categorized.get(cat_key, []),
                                      key=lambda a: a.score, reverse=True)

        # Load any existing feed to avoid duplicates
        feed_file = f"feed-{cat_key}.json"
        existing_urls: set = set()
        existing_items: list = []
        if os.path.exists(feed_file):
            try:
                with open(feed_file, 'r', encoding='utf-8') as f:
                    existing_feed = json.load(f)
                for ei in existing_feed.get('items', []):
                    try:
                        pub_date = datetime.fromisoformat(ei['date_published'].replace('Z', '+00:00'))
                    except Exception:
                        continue
                    if pub_date > retention_cutoff:
                        existing_urls.add(item_source_link(ei))
                        existing_items.append(ei)
            except Exception:
                pass

        cat_config = CATEGORIES[cat_key]
        feed_config = FEEDS_CONFIG['feeds'][cat_key]
        feed = {
            "version": "https://jsonfeed.org/version/1.1",
            "title": f"{cat_config['emoji']} {feed_config['title']}",
            "home_page_url": FEEDS_CONFIG['base_url'],
            "feed_url": f"{FEEDS_CONFIG['base_url']}/feed-{cat_key}.json",
            "description": feed_config['description'],
            "icon": f"{FEEDS_CONFIG['base_url']}/favicon.ico",
            "authors": [{"name": FEEDS_CONFIG['author']}],
            "language": "en",
            "items": list(existing_items),
        }

        added = 0
        for article in items:
            if not article.link or article.link in existing_urls:
                continue
            feed_item = {
                "id": article.link,
                "url": article.link,
                "title": (article.title if article.title.startswith(f"[{article.source}]")
                          else f"[{article.source}] {article.title}"),
                "content_html": article.description,
                "date_published": article.pub_date.isoformat(),
                "authors": [{"name": article.source, "url": article.source_url}],
                "_score": article.score,
            }
            if getattr(article, 'image', None):
                feed_item['image'] = article.image
                feed_item['content_html'] = (
                    f'<img src="{html_escape(article.image)}" style="width:100%;max-height:300px;object-fit:cover;" />\n'
                    + (article.description or '')
                )
            if cat_key == 'local':
                feed_item['_local'] = True
                feed_item['tags'] = ['local-priority']

            subscriber_label = SUBSCRIBER_ACCESS.get(article.source)
            if subscriber_label:
                feed_item['title'] = f"🔓 {feed_item['title']}"
                feed_item.setdefault('tags', []).append('subscriber-access')
                apply_subscriber_links(feed_item, article, subscriber_label)

            feed['items'].append(feed_item)
            existing_urls.add(article.link)
            added += 1

        feed['items'].sort(key=lambda x: x.get('date_published', ''), reverse=True)
        feed['items'] = feed['items'][:LIMITS['max_feed_size']]

        with open(feed_file, 'w', encoding='utf-8') as f:
            json.dump(feed, f, indent=2, ensure_ascii=False)

        # Keep the RSS mirror in step, so a standalone bootstrap run does not
        # leave subscribers on a stale .xml.
        if feed_config.get('rss'):
            generate_rss_feed(feed, f"{os.path.splitext(feed_file)[0]}.xml")

        if added:
            print(f"  ✅ {cat_key}: wrote {added} bootstrap articles ({len(feed['items'])} total)")
            total_written += added
        else:
            print(f"  — {cat_key}: no new bootstrap articles (feed already has {len(existing_items)})")

    print(f"\n🎉 Bootstrap complete: {total_written} articles written across {len(CATEGORIES)} feeds")


if __name__ == '__main__':
    if '--bootstrap-feeds' in sys.argv:
        bootstrap_feeds_from_podcast_cache(api_key=os.getenv('ANTHROPIC_API_KEY', ''))
    else:
        main()
