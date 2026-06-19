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
from zoneinfo import ZoneInfo
from collections import defaultdict
from typing import List, Dict, Optional, Tuple
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
import anthropic
from fetch_images import batch_fetch_images
import cohere_integration
import api_usage
import config_loader
from cache import Cache

# Configuration paths (kept for direct file access e.g. scoring_interests.txt)
CONFIG_DIR = Path(__file__).parent / 'config'

CATEGORIES = config_loader.load_categories_config()
CATEGORY_RULES = config_loader.load_category_rules_config()
FILTERS = config_loader.load_filters_config()
LIMITS = config_loader.load_limits_config()
SYSTEM = config_loader.load_system_config()
FEEDS_CONFIG = config_loader.load_feeds_config()
SOURCE_PREFS = config_loader.load_source_preferences()
SUBSCRIBER_ACCESS = SOURCE_PREFS.get('subscriber_access', {}).get('sources', {})
SCORING_WEIGHTS = config_loader.load_scoring_weights() or {
    'general': {'w_quality': 0.25, 'w_relevance': 0.55, 'w_local': 0.20},
    'podcast': {'w_quality': 0.10, 'w_relevance': 0.20, 'w_local': 0.10, 'w_theme': 0.60}
}
SCORING_MODIFIERS = config_loader.load_scoring_modifiers() or {
    'local_keyword_bonus': 25,
    'wire_quality_penalty': -10,
    'source_type_quality_adjustments': {}
}
FEED_SLOTS = config_loader.load_feed_slots_config()

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
THEME_SCORE_CACHE_VERSION = 'v2'  # Bump to invalidate caches from old raw-score formula
PENDING_THEME_BATCH_FILE = 'pending_theme_batch.json'  # Tracks in-flight async theme batch
SHOWN_TERMS_CACHE_FILE = 'shown_terms_cache.json'   # Term sets for cross-run story dedup
THEME_HOLDOVER_FILE = 'theme_holdover_cache.json'   # Cross-week pool of theme-relevant articles
THEME_HOLDOVER_TTL_DAYS = 28                         # 4 weeks — covers monthly themed episode cycles
CALIBRATION_STATS_CACHE_FILE = 'calibration_stats_cache.json'  # Rolling per-run audit stats
CALIBRATION_STATS_TTL_DAYS = 14                      # Window consumed by the weekly calibration agent

# URLs
WLT_BASE_URL = SYSTEM['urls']['wlt_base']
WLT_NEWS_URL = SYSTEM['urls']['wlt_news']

# Cache instances (simple dict caches with TTL)
_scored_cache = Cache(SCORED_CACHE_FILE, ttl_hours=SYSTEM['cache_expiry']['scored_hours'])
_extract_cache = Cache(EXTRACT_CACHE_FILE, ttl_hours=SYSTEM['cache_expiry']['scored_hours'])
_wlt_cache = Cache(WLT_CACHE_FILE, ttl_hours=SYSTEM['cache_expiry']['scored_hours'])
_shown_cache = Cache(SHOWN_CACHE_FILE, ttl_hours=SYSTEM['cache_expiry']['shown_days'] * 24)
_shown_terms_cache = Cache(SHOWN_TERMS_CACHE_FILE, ttl_hours=SYSTEM['cache_expiry']['shown_days'] * 24, ts_field='ts')

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
        article.description = snippet
        article.summary = _clean_text(snippet, max_chars=300)
        article.excerpt = _clean_text(snippet, max_chars=600)
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

        # First-person anecdote listicles ("I ditched...", "My home server...") are
        # low-depth regardless of outlet - one regex replaces the old per-phrase
        # "I ___" blocklist entries.
        title_lower = self.title.lower()
        if any(re.match(pattern, title_lower) for pattern in FILTERS.get('blocked_title_patterns', [])):
            return True

        # Arts/entertainment keywords are skipped when article mentions local places
        # (e.g. an arena hosts a concert, or a local tournament isn't sports).
        is_local = any(signal in text for signal in FILTERS.get('local_signals', []))
        nonlocal_keywords = FILTERS.get('blocked_keywords_unless_local', [])
        if nonlocal_keywords and not is_local:
            if any(keyword in text for keyword in nonlocal_keywords):
                return True

        return False


APPLE_NEWS_TITLE_SUFFIX_RE = re.compile(r'\s*[\|–—-]\s*[^|–—-]{1,50}$')


def build_apple_news_search_url(title: str) -> str:
    """Build an applenews://search URL from a cleaned article title."""
    clean_title = APPLE_NEWS_TITLE_SUFFIX_RE.sub('', title).strip() or title
    return f"applenews://search?term={quote(clean_title)}"




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
            if pub_date > cutoff and not _is_aggregator_url(item.get('link', '')):
                valid_articles.append(item)

        if len(valid_articles) != len(cache_data):
            print(f"🧹 Cleaned podcast cache: {len(cache_data)} → {len(valid_articles)} articles")

        return valid_articles

    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        print(f"⚠️ Error loading podcast cache: {e}")
        return []


def save_podcast_cache(articles):
    """Save articles to weekly podcast cache

    Args:
        articles: List of Article objects to cache
    """
    try:
        # Load existing cache
        existing = load_podcast_cache()

        # Build set of existing URLs to avoid duplicates
        existing_urls = {item['link'] for item in existing}

        # Add new articles
        for article in articles:
            if article.link not in existing_urls and not _is_aggregator_url(article.link):
                existing.append({
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
                    'content_type': getattr(article, 'content_type', None),
                    'category': article.category,
                    'image': getattr(article, 'image', None)
                })

        # Sort by pub_date descending
        existing.sort(key=lambda x: x['pub_date'], reverse=True)

        # Save back to file
        with open(PODCAST_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

        print(f"💾 Podcast cache updated: {len(existing)} articles (7-day window)")

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
            valid = [a for a in articles if datetime.fromisoformat(a['banked_at']) > cutoff]
            if valid:
                pruned[day] = valid
        return pruned
    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        print(f"⚠️ Error loading theme holdover cache: {e}")
        return {}


def save_theme_holdover_cache(holdover: Dict):
    try:
        with open(THEME_HOLDOVER_FILE, 'w', encoding='utf-8') as f:
            json.dump(holdover, f, indent=2, ensure_ascii=False)
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

    return articles


def fetch_feed_articles(feed: Dict, cutoff_date: datetime) -> List[Article]:
    """Fetch and parse articles from a feed"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*'
        }
        
        response = requests.get(feed['url'], headers=headers, timeout=10)
        response.raise_for_status()
        
        parsed = feedparser.parse(response.content)

        # Some feeds (e.g. My Cariboo Now) repeat the channel-level description
        # verbatim as every item's <description>, producing identical boilerplate
        # "summaries" that game keyword-based scoring. Detect and strip that case
        # so the article is treated as having no description.
        feed_description = _clean_text(
            parsed.feed.get('description', '') or parsed.feed.get('subtitle', '')
        )

        articles = []
        fetched_excerpts = 0
        for entry in parsed.entries:
            article = Article(entry, feed['title'], feed['html_url'], feed['url'])

            if feed_description and _clean_text(article.description) == feed_description:
                article.description = ''
                article.summary = ''
                article.excerpt = ''

            if article.pub_date < cutoff_date:
                continue

            if article.should_filter():
                continue

            # For known local BC sources with a stub description, attempt a body
            # fetch while the article is still within the paywall-free window.
            if (len(article.summary) < 100
                    and any(d in article.link for d in _LOCAL_BC_DOMAINS)):
                body = _fetch_article_excerpt(article.link, max_chars=600)
                if body:
                    article.description = body
                    article.summary = _clean_text(body, max_chars=300)
                    article.excerpt = _clean_text(body, max_chars=600)
                    fetched_excerpts += 1

            articles.append(article)

        if articles:
            extra = f", {fetched_excerpts} body excerpts fetched" if fetched_excerpts else ""
            print(f"  ✓ {feed['title']}: {len(articles)} articles{extra}")

        return articles
        
    except Exception as e:
        is_403 = (
            isinstance(e, requests.exceptions.HTTPError)
            and e.response is not None
            and e.response.status_code == 403
        )
        is_404 = (
            isinstance(e, requests.exceptions.HTTPError)
            and e.response is not None
            and e.response.status_code == 404
        )
        is_timeout = isinstance(e, (requests.exceptions.ReadTimeout, requests.exceptions.Timeout))
        should_try_fallback = is_403 or is_404 or is_timeout

        if should_try_fallback and os.environ.get('BRAVE_API_KEY'):
            fallback = _fetch_via_brave_fallback(feed, cutoff_date)
            if fallback:
                print(f"  ↩ {feed['title']}: Brave fallback → {len(fallback)} articles")
                return fallback
            print(f"  ⚠ {feed['title']}: Brave fallback returned 0 articles")

        if should_try_fallback and os.environ.get('KAGI_API_KEY'):
            fallback = _fetch_via_kagi_fallback(feed, cutoff_date)
            if fallback:
                print(f"  ↩ {feed['title']}: Kagi fallback → {len(fallback)} articles")
                return fallback

        print(f"  ✗ {feed['title']}: {e}")
        return []


def _source_priority(article: Article) -> int:
    """Return sort key for dedup ordering. Lower = processed first = wins ties."""
    source_map = SOURCE_PREFS.get('source_map', {})
    source_type = source_map.get(article.source)
    # WLT scraper articles are pre-scored at local_priority_score before dedup runs.
    # RSS feeds for the same paper (e.g. www.wltribune.com/feed/) share the same
    # source name and therefore the same preferred_local type, so without this
    # check the RSS version (fetched first) would win and the richer scraper
    # version would be silently dropped as a duplicate.
    if source_type == 'preferred_local' and article.score == LIMITS.get('local_priority_score', 100):
        return 0
    # Subscribed / preferred local paper via RSS
    if source_type == 'preferred_local':
        return 1
    # Other explicitly local-priority articles
    if article.category == 'local' or article.score == LIMITS.get('local_priority_score', 100):
        return 2
    if source_type == 'print':
        return 3
    if source_type == 'broadcast':
        return 5
    return 4  # unclassified sources


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
    when two outlets cover the same story.
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


def _dedup_story_key(article) -> tuple:
    """Sort key for story-group dedup: prefer by content_type hierarchy, then Q score."""
    ct = getattr(article, 'content_type', None) or ''
    q = getattr(article, 'quality', 0) or getattr(article, 'score', 0)
    return (_CONTENT_TYPE_RANK.get(ct, 0), q)


def dedup_by_story_group(articles: List[Article]) -> List[Article]:
    """Collapse articles that Claude labelled with the same story_group.

    Within a story group, prefer original reporting over wire reprints using
    content_type hierarchy (analysis > feature > opinion > breaking > wire > recap).
    Tiebreak within same type by quality score.
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
    """Extra dedup pass using Cohere embeddings. No-op when Cohere is disabled.

    Runs after the URL-hash / fuzzy / term-set pass so it only sees the already-
    reduced candidate set (~200-400 articles), keeping embedding costs minimal.
    Articles with cosine similarity >= 0.92 are considered the same story; the
    first (highest-priority) article wins, matching the existing dedup behaviour.
    """
    if not cohere_integration.is_enabled():
        return articles

    embeddings = cohere_integration.embed_articles(articles)
    if not embeddings:
        return articles

    THRESHOLD = 0.92
    unique: List[Article] = []
    seen: List[List[float]] = []

    for article in articles:
        emb = embeddings.get(article.url_hash)
        if emb is None:
            unique.append(article)
            continue
        is_dup = any(cohere_integration.cosine_sim(emb, s) >= THRESHOLD for s in seen)
        if not is_dup:
            unique.append(article)
            seen.append(emb)

    dropped = len(articles) - len(unique)
    if dropped:
        print(f"🔄 Semantic dedup: removed {dropped} additional near-duplicate articles")
    return unique


def score_articles_with_cohere(articles: List[Article]) -> List[Article]:
    """Score and categorize articles using Cohere Rerank + embedding story clustering.

    Drop-in replacement for score_articles_with_claude() when COHERE_API_KEY is set.
    Uses the same scored_articles_cache so switching back to Claude on subsequent
    runs is safe (cache entries include score, category, and a null story_group).
    """
    if not articles:
        return []

    cache = _scored_cache.load()

    interests_file = CONFIG_DIR / 'scoring_interests.txt'
    try:
        with open(interests_file, 'r') as f:
            interests = f.read().strip()
    except FileNotFoundError:
        interests = "Technology, science, climate, local news"

    scored_articles: List[Article] = []
    uncached: List[Article] = []

    for article in articles:
        if article.url_hash in cache:
            entry = cache[article.url_hash]
            article.score = entry['score']
            article.category = entry['category']
            # Synthesize Q/R/L from composite score — Cohere has no dimensional breakdown.
            # Using score as a proxy keeps calibration histograms populated without
            # changing apply_dimension_adjustments behaviour (cohere_scored=True bypasses
            # the composite recompute there).
            article.quality = entry.get('quality', entry['score'])
            article.relevance = entry.get('relevance', entry['score'])
            article.local = entry.get('local', 0)
            article.content_type = entry.get('content_type')
            article.cohere_scored = True
            # story_group is intentionally not restored — clustering is run-scoped
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

    # Assign story groups for all articles in this run via embedding clusters.
    # This replaces Claude's story_group string assignment; downstream
    # dedup_by_story_group() is unchanged and works the same way.
    print(f"   🔗 Clustering story groups for {len(scored_articles)} articles...")
    embeddings = cohere_integration.embed_articles(scored_articles)
    cohere_integration.cluster_story_groups(scored_articles, embeddings)

    return scored_articles


def score_articles_with_claude(articles: List[Article], api_key: str) -> List[Article]:
    """Score and categorize articles using Claude API with prompt caching"""
    if cohere_integration.is_enabled():
        return score_articles_with_cohere(articles)

    if not articles:
        return []

    cache = _scored_cache.load()

    # Load scoring interests
    interests_file = CONFIG_DIR / 'scoring_interests.txt'
    try:
        with open(interests_file, 'r') as f:
            interests = f.read().strip()
    except FileNotFoundError:
        print("⚠️ scoring_interests.txt not found, using basic scoring")
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
        f"1. local    — ANY Williams Lake, Cariboo, Quesnel, CRD, or BC Interior community content\n"
        f"2. homelab  — self-hosting, 3D printing, home automation, home servers\n"
        f"3. climate  — renewable energy, EVs, climate science, carbon, wildfire ecology\n"
        f"4. wellness — personal health, nutrition, mental health, fitness, medicine\n"
        f"5. science  — peer-reviewed research, discoveries, academic findings\n"
        f"6. scifi    — science fiction, speculative fiction, worldbuilding\n"
        f"7. ai-tech  — AI/ML systems, platform engineering, infrastructure\n"
        f"8. news     — default catch-all for anything not clearly matching 1–7\n\n"
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
                article.score = entry['score']
                article.category = entry['category']
                article.story_group = entry.get('story_group')
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
                    article.category = categorize_article(article.title, article.description) or 'news'
                    scored_articles.append(article)

            except Exception as e:
                print(f"  ⚠️ API error: {e}")
                for article in batch:
                    article.quality = 50
                    article.relevance = 50
                    article.local = 0
                    article.score = 50
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

    # Cohere pre-filter: auto-remove high-confidence junk before calling Claude.
    # Very conservative threshold avoids false positives.
    # Local articles are never auto-removed regardless of score.
    auto_removed_count = 0
    cohere_removed_by_category: Dict[str, int] = defaultdict(int)
    if cohere_integration.is_enabled():
        try:
            interests_text = (CONFIG_DIR / 'scoring_interests.txt').read_text().strip()
        except Exception:
            interests_text = ''
        articles, auto_removed = cohere_integration.prefilter_scrub_articles(
            articles, interests_text, local_signals=local_signals,
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
        weights = SCORING_WEIGHTS.get('general', {})
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
    """
    ALWAYS_DROP = {'fluff', 'sponsored'}
    # AI/tech articles above this threshold have already been reviewed leniently by
    # scrub_feed_with_haiku (score >= 40 triggers "only remove clear fluff"). Dropping
    # them here unconditionally would contradict that leniency, so let them pass.
    ai_tech_fluff_threshold = LIMITS.get('ai_tech_fluff_score_threshold', 40)
    AI_TECH_CATEGORIES = {'ai-tech', 'homelab'}
    kept = []
    removed: Dict[str, int] = defaultdict(int)

    for article in articles:
        ct = article.content_type
        if not ct:
            kept.append(article)
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


def generate_json_feed(articles: List[Article], category: str, output_path: str):
    """Generate JSON Feed format output"""
    cat_config = CATEGORIES[category]
    feed_config = FEEDS_CONFIG['feeds'][category]
    
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
        item = {
            "id": article.link,
            "url": article.link,
            "title": article.title if has_source_in_title else f"[{article.source}] {article.title}",
            "content_html": clean_desc,
            "date_published": article.pub_date.isoformat(),
            "authors": [{"name": article.source, "url": article.source_url}]
        }

        if hasattr(article, 'image') and article.image:
            item["image"] = article.image
            item["content_html"] = f'<img src="{html_escape(article.image)}" style="width:100%;max-height:300px;object-fit:cover;" />\n' + clean_desc

        item["_score"] = article.score
        item["_quality"] = article.quality
        item["_relevance"] = article.relevance
        item["_local_score"] = article.local
        if article.content_type:
            item["_content_type"] = article.content_type

        if category == 'local':
            item["_local"] = True
            item["tags"] = ["local-priority"]

        subscriber_label = SUBSCRIBER_ACCESS.get(article.source)
        if subscriber_label:
            item["title"] = f"🔓 {item['title']}"
            item.setdefault("tags", []).append("subscriber-access")
            item["_subscriber_access"] = subscriber_label
            if subscriber_label == "Apple News+":
                _clean = re.sub(r'^\[.*?\]\s*', '', article.title)
                item["_apple_news_url"] = build_apple_news_search_url(_clean or article.title)

        feed["items"].append(item)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(feed, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated {category} feed: {len(feed['items'])} articles")


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

    # Load curator interests and build category guide to prepend as background context.
    # The bare theme prompt alone is ~300-500 tokens — well below the 4096-token minimum
    # required for Haiku 4.5 prompt caching, so cache_control silently does nothing without
    # this extra context. The interests + category guide together add ~4200 tokens, ensuring
    # every theme (including the shortest) clears the threshold. The category guide is also
    # genuinely useful: knowing the content taxonomy (e.g. homelab vs ai-tech) helps Claude
    # correctly score how well an article fits a given theme.
    interests_file = CONFIG_DIR / 'scoring_interests.txt'
    try:
        with open(interests_file, 'r') as f:
            interests = f.read().strip()
    except FileNotFoundError:
        interests = "Technology, science, climate, local news"

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
        f"BACKGROUND — curator interest profile (for context when judging relevance):\n{interests}\n\n"
        f"CONTENT TAXONOMY (for reference):\n{category_guide}\n\n"
        f"{theme_prompt}"
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

    # Load curator interests to prepend as background context.
    # The 7 theme descriptions alone are ~2000 tokens — below the 4096-token minimum
    # for Haiku 4.5 caching. Adding the interests file (~2100 tokens) pushes the
    # combined system prompt well past the threshold.
    interests_file = CONFIG_DIR / 'scoring_interests.txt'
    try:
        with open(interests_file, 'r') as f:
            interests = f.read().strip()
    except FileNotFoundError:
        interests = "Technology, science, climate, local news"

    theme_descriptions = "\n\n".join(
        f"Theme key \"{day}\" — {cfg['label']}:\n{cfg.get('scoring_prompt', '')}"
        for day, cfg in schedule.items()
    )
    day_keys = list(schedule.keys())
    combined_system = (
        f"You are evaluating news articles for thematic relevance across multiple themes. "
        f"Respond only with valid JSON arrays.\n\n"
        f"BACKGROUND — curator interest profile (for context when judging relevance):\n{interests}\n\n"
        f"Score each article 0-100 for each of the following themes:\n\n"
        f"{theme_descriptions}"
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
    """
    schedule = schedule_config.get('schedule', {})
    routing_gap = schedule_config.get('theme_routing_gap', 20)
    routing_min_score = schedule_config.get('theme_routing_min_score', 55)
    holdover_threshold = schedule_config.get('holdover_threshold', 30)

    if not schedule or today_name not in schedule:
        return {'routed_by_target_day': {}, 'routed_count': 0}

    theme_cache = load_theme_score_cache()
    to_bank: Dict[str, list] = defaultdict(list)  # {day_name: [(item_dict, score)]}

    for item in cached_articles:
        url = item['link']
        all_scores: Dict[str, int] = {}
        complete = True
        for day, cfg in schedule.items():
            entry = theme_cache.get(f"{url}:::{cfg['label']}")
            if entry is None:
                complete = False
                break
            all_scores[day] = entry['score']

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
    """
    theme_cache = load_theme_score_cache()
    schedule = schedule_config.get('schedule', {})
    global_threshold = schedule_config.get('holdover_threshold', 30)
    holdover = load_theme_holdover_cache()
    now_iso = datetime.now(timezone.utc).isoformat()
    newly_banked: Dict[str, int] = defaultdict(int)

    for item in cached_articles:
        url = item['link']
        for day, cfg in schedule.items():
            threshold = cfg.get('holdover_threshold', global_threshold)
            label = cfg['label']
            entry = theme_cache.get(f"{url}:::{label}")
            if entry is None or entry['score'] < threshold:
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
                'category': item['category'],
                'image': item.get('image'),
                'theme_score': entry['score'],
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
            self.quality = data.get('quality', data['score'])
            self.relevance = data.get('relevance', data['score'])
            self.local = data.get('local', 0)
            self.content_type = data.get('content_type')
            self.category = data['category']
            self.image = data.get('image')

    all_cached = [CachedArticle(item) for item in cached_articles]
    all_cached_urls = {a.link for a in all_cached}

    # Load cross-week holdover: articles that scored well on this theme in previous
    # runs and were banked for future episodes (28-day retention).
    holdover_cache = load_theme_holdover_cache()
    holdover_raw = holdover_cache.get(theme_name, [])
    holdover_pool = [
        CachedArticle(item) for item in holdover_raw
        if item.get('status') != 'USED'  # exclude articles already used in this theme's episode
        and f"{item['link']}:::{theme_name}" not in podcast_shown_cache
        and not _is_aggregator_url(item['link'])
        and item['link'] not in all_cached_urls  # already in 7-day pool
        and item.get('score', 0) >= LIMITS['min_claude_score']  # enforce current quality floor
    ]
    if holdover_pool:
        print(f"  📦 +{len(holdover_pool)} holdover articles from previous weeks")

    # The theme scoring prompt is the real semantic filter, so score ALL
    # quality-eligible articles — not just those in the day's primary categories.
    # theme_set marks which categories are "primary" for _is_bonus labelling only.
    theme_set = set(theme_categories)
    theme_pool = list(all_cached)

    # Filter by minimum quality score
    theme_pool = [a for a in theme_pool if a.score >= min_score]

    # Track articles that qualify for this day's pool on upstream quality score
    # alone (not via rescue/holdover), so a theme-fit floor can be applied to
    # them after theme scoring below.
    direct_qualify_links = {a.link for a in theme_pool}

    # Rescue: include articles below the base threshold when they already have a
    # cached theme score >= holdover_threshold.  These proved their thematic fit
    # even though their general quality score is low (e.g. niche local sources).
    theme_score_cache = load_theme_score_cache()
    rescued = [
        a for a in all_cached
        if a.score < min_score
        and not _is_aggregator_url(a.link)
        and f"{a.link}:::{theme_name}" not in podcast_shown_cache
        and theme_score_cache.get(f"{a.link}:::{theme_label}", {}).get('score', 0) >= holdover_threshold
    ]
    if rescued:
        print(f"  🌾 +{len(rescued)} theme-relevant articles rescued (base score < {min_score})")
        theme_pool.extend(rescued)

    # Merge holdover articles into the pool (already theme-qualified and quality-filtered above)
    theme_pool.extend(holdover_pool)

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

    # Exclude articles whose link goes through a search-engine aggregator
    # (e.g. Google News encoded proxy URLs). These opaque URLs defeat
    # cross-episode deduplication since the same story can have different
    # encoded links on different runs.
    before_agg = len(theme_pool)
    theme_pool = [a for a in theme_pool if not _is_aggregator_url(a.link)]
    agg_excluded = before_agg - len(theme_pool)
    if agg_excluded:
        print(f"  🚫 Excluded {agg_excluded} aggregator-URL articles (e.g. Google News)")

    # Articles banked for other days via theme routing are NOT excluded here.
    # Cross-theme reuse is intentional — the same article may appear in multiple
    # themed episodes with _cross_theme metadata on the second appearance.

    # Cap the pool: sort by quality score and keep only the top candidates.
    # Articles with lower quality scores are unlikely to beat well-scored candidates
    # for theme fit, so scoring them wastes API calls.
    POOL_CAP = 300
    if len(theme_pool) > POOL_CAP:
        theme_pool.sort(key=lambda a: a.score, reverse=True)
        theme_pool = theme_pool[:POOL_CAP]
        print(f"  📊 Pool capped at top {POOL_CAP} articles by quality score")

    # Score articles for thematic fit using Claude
    theme_scored = score_articles_for_theme(theme_pool, theme_scoring_prompt, theme_label, api_key)

    # Fallback: if scoring returned nothing despite having a pool, use quality scores directly
    if not theme_scored and theme_pool:
        print(f"  ⚠️ Theme scoring returned empty for {theme_label}, falling back to quality scores")
        theme_scored = [(article, article.score) for article in theme_pool]

    # Theme-fit floor for the direct-qualify path: articles that only entered the
    # pool via the upstream quality score (not rescue/holdover) must also clear
    # the holdover_threshold theme-fit bar — unless they have a keyword hit —
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

    # Keyword boost applies to T (theme dimension) before composite computation.
    # Rural context is no longer a hardcoded penalty — incorporate guidance into
    # the theme's scoring_prompt instead (configurable per day).
    kw_boost_val = schedule_config.get('keyword_boost', 10)
    kw_boost_cap = schedule_config.get('keyword_boost_cap', 5)
    bonus_thematic_boost = schedule_config.get('bonus_thematic_boost', 5)
    bonus_max_per_category = schedule_config.get('bonus_max_per_category', 3)

    _pod_weights = SCORING_WEIGHTS.get('podcast', {})
    _pod_w_q = _pod_weights.get('w_quality', 0.10)
    _pod_w_r = _pod_weights.get('w_relevance', 0.20)
    _pod_w_l = _pod_weights.get('w_local', 0.10)
    _pod_w_t = _pod_weights.get('w_theme', 0.60)

    def _podcast_composite(article, t_adjusted: float) -> int:
        q = getattr(article, 'quality', 0) or getattr(article, 'score', 0)
        r = getattr(article, 'relevance', 0) or getattr(article, 'score', 0)
        l_ = getattr(article, 'local', 0)
        return min(100, max(0, round(
            _pod_w_q * q + _pod_w_r * r + _pod_w_l * l_ + _pod_w_t * t_adjusted
        )))

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

    # Bank articles with strong raw theme scores for future episodes.
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
        item = {
            "id": article.link,
            "url": article.link,
            "title": article.title if has_source_in_title else f"[{article.source}] {article.title}",
            "content_html": clean_desc,
            "summary": getattr(article, 'summary', '') or _clean_text(article.description, max_chars=300),
            "_excerpt": getattr(article, 'excerpt', '') or _clean_text(article.description, max_chars=600),
            "date_published": article.pub_date.isoformat(),
            "authors": [{"name": article.source, "url": article.source_url}],
            "ai_score": article.score,
            "_quality": getattr(article, 'quality', article.score),
            "_relevance": getattr(article, 'relevance', article.score),
            "_local": getattr(article, 'local', 0),
            "_theme_score": theme_score,
            "_composite_podcast": composite_podcast,
            "_keyword_matches": kw_matches,
            "_category": article.category,
            "_source_category": article.category,
            "_is_bonus": is_bonus,
            **({"_thin_body": True} if _item_body_len < 280 else {}),
        }

        subscriber_label = SUBSCRIBER_ACCESS.get(article.source)
        if subscriber_label:
            item.setdefault("tags", []).append("subscriber-access")
            item["_subscriber_access"] = subscriber_label
            if subscriber_label == "Apple News+":
                _clean = re.sub(r'^\[.*?\]\s*', '', article.title)
                item["_apple_news_url"] = build_apple_news_search_url(_clean or article.title)

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
        if hasattr(article, 'image') and article.image:
            item["image"] = article.image
            item["content_html"] = f'<img src="{html_escape(article.image)}" style="width:100%;max-height:300px;object-fit:cover;" />\n' + clean_desc
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
    cross_cat = bonus_count
    print(f"🎙️ Podcast feed {theme_name} ({theme_label}): {len(all_entries)} articles (avg theme score: {avg_theme_score:.1f}, {cross_cat} cross-category)")

    feed_stats = {
        'article_count': len(all_entries),
        'bonus_count': bonus_count,
        'mean_final_score': round(avg_final_score, 1),
        'mean_theme_score': round(avg_theme_score, 1),
        'relative_scaled': False,
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
        feed_url = f"{FEEDS_CONFIG['base_url']}/feed-{cat_key}.json"

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
    
    all_articles = []
    for feed in feeds:
        articles = fetch_feed_articles(feed, cutoff_date)
        all_articles.extend(articles)

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
        if (a.title_terms
                and len(a.title_terms) >= 3
                and any(
                    _story_overlap(a.title_terms, stored) >= 0.50
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
        _kagi_enrich_articles(new_articles, kagi_key, prescore_keywords=PRESCORE_KEYWORDS)

    scored_articles = score_articles_with_claude(new_articles, api_key)

    # Phase 4: Dimension adjustments (L += local_bonus, Q += source_adjustment)
    # Replaces enforce_local_priority + apply_source_preferences.
    scored_articles = apply_dimension_adjustments(scored_articles)

    _dim_hists = _dimensional_histograms(scored_articles)
    run_stats['scoring'] = {
        'scored_count': len(scored_articles),
        'score_histogram_by_category': _score_histogram(scored_articles),
        'quality_histogram_by_category': _dim_hists['quality'],
        'relevance_histogram_by_category': _dim_hists['relevance'],
        'local_histogram_by_category': _dim_hists['local'],
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

    # Fetch images for quality articles only (after filtering)
    print(f"🖼️  Fetching images for quality articles...")
    quality_articles = batch_fetch_images(quality_articles, max_fetch=50)
    images_found = sum(1 for a in quality_articles if hasattr(a, 'image') and a.image)
    print(f"   Found images for {images_found}/{len(quality_articles)} articles")
    
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

    # Score new articles for all themes at ingest time so daily podcast generation
    # is a pure cache read with zero additional API calls (Options B + D).
    # First, flush any completed async batch from the previous run into the cache.
    schedule_config = load_podcast_schedule()
    process_pending_theme_batch(api_key)
    score_all_themes_at_ingest(quality_articles, schedule_config, api_key)

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

    # Generate today's themed podcast feed from the accumulated weekly staging pool.
    # Each daily run banks qualifying articles into the holdover cache for all 7 themes;
    # by the actual day, the holdover holds up to a week of pre-qualified candidates.
    # After generation, holdover entries are marked USED (appeared) or SKIPPED (passed over).
    print(f"\n🎙️ Generating today's podcast feed from {len(podcast_cache)} cached articles...")
    if schedule_config and schedule_config.get('enabled', False):
        today_name = datetime.now(ZoneInfo('America/Vancouver')).strftime('%A').lower()
        if today_name in schedule_config['schedule']:
            podcast_shown_cache = load_podcast_shown_cache()
            # Bank qualifying articles into every day's holdover staging pool.
            banking_stats = bank_articles_for_all_themes(podcast_cache, schedule_config)
            run_stats['theme_routing'] = {
                'routed_by_target_day': banking_stats,
                'routed_count': sum(banking_stats.values()),
            }
            selected_urls, feed_stats = generate_podcast_feed(
                today_name, podcast_cache, podcast_shown_cache
            )
            if feed_stats:
                run_stats['podcast_feeds'] = {today_name: feed_stats}
            # Mark today's holdover entries as USED or SKIPPED for auditing.
            if selected_urls is not None:
                _hov = load_theme_holdover_cache()
                today_staged = _hov.get(today_name, [])
                used_count = skipped_count = 0
                for article in today_staged:
                    if article['link'] in selected_urls:
                        article['status'] = 'USED'
                        used_count += 1
                    elif article.get('status') != 'USED':
                        article['status'] = 'SKIPPED'
                        skipped_count += 1
                if today_staged:
                    _hov[today_name] = today_staged
                    save_theme_holdover_cache(_hov)
                    print(f"  ♻️  Holdover status: {used_count} USED, {skipped_count} SKIPPED")
            holdover_cache_snapshot = load_theme_holdover_cache()
            run_stats['holdover'] = {
                'bank_size_by_day_eod': {
                    day: len(arts) for day, arts in holdover_cache_snapshot.items()
                },
                'banked_today': feed_stats.get('banked_count', 0) if feed_stats else 0,
            }
            if selected_urls:
                now_iso = datetime.now(timezone.utc).isoformat()
                today_date_str = now_iso[:10]
                newly_marked = 0
                compound_key = lambda u: f"{u}:::{today_name}"
                for url in selected_urls:
                    existing = podcast_shown_cache.get(compound_key(url), {})
                    # Don't overwrite a same-day entry so the original shown_at is preserved
                    if not existing.get('shown_at', '').startswith(today_date_str):
                        podcast_shown_cache[compound_key(url)] = {'day': today_name, 'shown_at': now_iso}
                        newly_marked += 1
                save_podcast_shown_cache(podcast_shown_cache)
                print(f"  📌 Marked {newly_marked} new articles as shown ({len(selected_urls) - newly_marked} already in today's episode)")
            print(f"\n📅 Podcast day buckets:")
            day_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day in day_order:
                if day not in schedule_config['schedule']:
                    continue
                label = schedule_config['schedule'][day]['label']
                if day == today_name:
                    count = feed_stats['article_count'] if feed_stats else 0
                    print(f"  {day} ({label}): {count} articles [TODAY]")
                else:
                    staged = len(holdover_cache_snapshot.get(day, []))
                    print(f"  {day} ({label}): {staged} staged")
        else:
            print(f"⚠️ No podcast schedule for today ({today_name})")

    # Generate daily review feed for user training feedback
    generate_review_feed(quality_articles, scrubbed, schedule_config)

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
            if item['url'] in new_urls:
                return False
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
                'link': item['url'],
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


def generate_review_feed(quality_articles: List[Article], scrubbed: List[Article],
                         schedule_config: Optional[Dict]):
    """Select 20 articles for daily training feedback and write feed-review.json."""
    # Load already-reviewed URLs so we don't surface the same article twice.
    reviewed_urls: set = set()
    feedback_dir = Path('feedback')
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

    today_name = datetime.now(ZoneInfo('America/Vancouver')).strftime('%A').lower()
    today_label = ''
    day_labels: Dict[str, str] = {}
    if schedule_config and schedule_config.get('enabled'):
        for day, cfg in schedule_config.get('schedule', {}).items():
            day_labels[day] = cfg.get('label', day.capitalize())
        today_label = day_labels.get(today_name, '')

    theme_cache = load_theme_score_cache()

    def theme_scores(article: Article) -> Dict[str, int]:
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

    # Tag each with its selection bucket
    high_set   = {a.url_hash for a in high[:5]}
    mid_set    = {a.url_hash for a in mid[:8]}
    border_set = {a.url_hash for a in border[:5]}
    low_set    = {a.url_hash for a in low[:2]}

    def bucket_label(a: Article) -> str:
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
        "description": f"20 articles for daily training feedback. Today: {today_label}",
        "authors": [{"name": FEEDS_CONFIG['author']}],
        "language": "en",
        "_generated_at": now_iso,
        "_today": today_name,
        "_today_label": today_label,
        "items": [],
    }

    for article in selected[:20]:
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
            "_today": today_name,
            "_today_label": today_label,
        }
        if getattr(article, 'image', None):
            item['image'] = article.image
        feed['items'].append(item)

    with open('feed-review.json', 'w', encoding='utf-8') as fh:
        json.dump(feed, fh, indent=2, ensure_ascii=False)

    print(f"📋 Review feed: {len(feed['items'])}/20 articles "
          f"({len(reviewed_urls)} already-reviewed excluded)")


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
        interests_file = CONFIG_DIR / 'scoring_interests.txt'
        try:
            interests = interests_file.read_text().strip()
        except FileNotFoundError:
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
                        existing_urls.add(ei['url'])
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
            feed['items'].append(feed_item)
            existing_urls.add(article.link)
            added += 1

        feed['items'].sort(key=lambda x: x.get('date_published', ''), reverse=True)
        feed['items'] = feed['items'][:LIMITS['max_feed_size']]

        with open(feed_file, 'w', encoding='utf-8') as f:
            json.dump(feed, f, indent=2, ensure_ascii=False)

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
