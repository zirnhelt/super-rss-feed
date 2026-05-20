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
from html import escape as html_escape
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import List, Dict, Optional
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import anthropic
from fetch_images import batch_fetch_images

# Configuration paths
CONFIG_DIR = Path(__file__).parent / 'config'

def load_json_config(filename):
    """Load JSON configuration file"""
    try:
        with open(CONFIG_DIR / filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file not found: {filename}")
        sys.exit(1)

def load_categories():
    """Load category definitions"""
    return load_json_config('categories.json')

def load_category_rules():
    """Load category rules with include/exclude lists"""
    try:
        with open(CONFIG_DIR / 'category_rules.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ category_rules.json not found, using basic categorization")
        return {}

def load_filters():
    """Load filtering rules"""
    return load_json_config('filters.json')

def load_limits():
    """Load limit configurations"""
    return load_json_config('limits.json')

def load_system_config():
    """Load system settings"""
    return load_json_config('system.json')

def load_feeds_config():
    """Load feed metadata configuration"""
    return load_json_config('feeds.json')

# Load all configurations
CATEGORIES = load_categories()
CATEGORY_RULES = load_category_rules()
FILTERS = load_filters()
LIMITS = load_limits()
SYSTEM = load_system_config()
FEEDS_CONFIG = load_feeds_config()

def load_source_preferences():
    """Load source type preferences"""
    return load_json_config('source_preferences.json')

SOURCE_PREFS = load_source_preferences()

# Cache files
SCORED_CACHE_FILE = SYSTEM['cache_files']['scored_articles']
WLT_CACHE_FILE = SYSTEM['cache_files']['wlt']
SHOWN_CACHE_FILE = SYSTEM['cache_files']['shown_articles']
PODCAST_CACHE_FILE = 'podcast_articles_cache.json'  # Weekly cache for podcast feeds
PODCAST_SHOWN_FILE = 'podcast_shown_cache.json'      # Tracks URLs used in each day's podcast episode
PODCAST_SHOWN_TTL_DAYS = 7                           # Exclude articles shown in the last 7 days
THEME_SCORE_CACHE_FILE = 'theme_scores_cache.json'  # Cache for per-article theme scores
THEME_SCORE_CACHE_TTL_DAYS = 7
PENDING_THEME_BATCH_FILE = 'pending_theme_batch.json'  # Tracks in-flight async theme batch
SHOWN_TERMS_CACHE_FILE = 'shown_terms_cache.json'   # Term sets for cross-run story dedup
THEME_HOLDOVER_FILE = 'theme_holdover_cache.json'   # Cross-week pool of theme-relevant articles
THEME_HOLDOVER_TTL_DAYS = 28                         # 4 weeks — covers monthly themed episode cycles

# URLs
WLT_BASE_URL = SYSTEM['urls']['wlt_base']
WLT_NEWS_URL = SYSTEM['urls']['wlt_news']

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


class Article:
    """Represents a single article"""
    def __init__(self, entry, source_title: str, source_url: str, feed_url: str = ''):
        is_google_news = 'news.google.com' in feed_url

        # Clean title - remove source suffix if present
        raw_title = entry.get('title', '').strip()
        # Remove " - SourceName" pattern common in Google News
        extracted_outlet = None
        if ' - ' in raw_title:
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
        self.category = None
        self.image = self._extract_image(entry)

        self.url_hash = hashlib.md5(canonicalize_url(self.link).encode()).hexdigest()
        self.title_normalized = self.title.lower().strip()
        self.title_terms = _term_set(self.title_normalized)
        self.story_group: Optional[str] = None  # Claude-assigned event label for dedup
    
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

        if any(keyword in text for keyword in FILTERS['blocked_keywords']):
            return True

        # Arts/entertainment keywords are skipped when article mentions local places
        nonlocal_keywords = FILTERS.get('blocked_keywords_unless_local', [])
        if nonlocal_keywords:
            is_local = any(signal in text for signal in FILTERS.get('local_signals', []))
            if not is_local and any(keyword in text for keyword in nonlocal_keywords):
                return True

        return False


def load_scored_cache():
    """Load scored articles cache"""
    if not os.path.exists(SCORED_CACHE_FILE):
        return {}
    
    try:
        with open(SCORED_CACHE_FILE, 'r') as f:
            cache = json.load(f)
        
        cache_expiry = timedelta(hours=SYSTEM['cache_expiry']['scored_hours'])
        cutoff = datetime.now(timezone.utc).timestamp() - cache_expiry.total_seconds()
        
        valid_cache = {k: v for k, v in cache.items() if v.get('timestamp', 0) > cutoff}
        
        if len(valid_cache) != len(cache):
            print(f"🧹 Cleaned scored cache: {len(cache)} → {len(valid_cache)} entries")
        
        return valid_cache
        
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_scored_cache(cache):
    """Save scored articles cache"""
    try:
        with open(SCORED_CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save scored cache: {e}")


def load_shown_cache():
    """Load shown articles cache"""
    if not os.path.exists(SHOWN_CACHE_FILE):
        return {}
    
    try:
        with open(SHOWN_CACHE_FILE, 'r') as f:
            cache = json.load(f)
        
        cache_expiry = timedelta(days=SYSTEM['cache_expiry']['shown_days'])
        cutoff = datetime.now(timezone.utc).timestamp() - cache_expiry.total_seconds()
        
        valid_urls = {url: timestamp for url, timestamp in cache.items() if timestamp > cutoff}
        
        return valid_urls
        
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_shown_cache(shown_urls):
    """Save shown articles cache"""
    try:
        cache = shown_urls
        with open(SHOWN_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save shown cache: {e}")


def load_shown_terms_cache() -> dict:
    """Load per-article term sets used for cross-run story deduplication.

    Format: {url_hash: {"ts": float, "terms": [str, ...]}}
    Entries older than the shown-cache window are dropped on load.
    """
    try:
        with open(SHOWN_TERMS_CACHE_FILE) as f:
            raw = json.load(f)
        cutoff = (datetime.now(timezone.utc)
                  - timedelta(days=SYSTEM['cache_expiry']['shown_days'])).timestamp()
        return {k: v for k, v in raw.items()
                if isinstance(v, dict) and v.get('ts', 0) > cutoff}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_shown_terms_cache(cache: dict):
    """Persist the shown-terms cache."""
    try:
        with open(SHOWN_TERMS_CACHE_FILE, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"⚠️ Failed to save shown terms cache: {e}")


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
            if pub_date > cutoff:
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
            if article.link not in existing_urls:
                existing.append({
                    'link': article.link,
                    'title': article.title,
                    'description': article.description,
                    'pub_date': article.pub_date.isoformat(),
                    'source': article.source,
                    'source_url': article.source_url,
                    'score': article.score,
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
                          scored_articles: List[tuple], threshold: int):
    """Bank articles scoring >= threshold on a theme for future episodes.

    Args:
        theme_name: Day key e.g. 'tuesday'
        theme_label: Human label e.g. 'Working Lands & Industry'
        scored_articles: List of (article, theme_score) from score_articles_for_theme
        threshold: Minimum theme score to bank an article
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


def load_podcast_shown_cache() -> Dict:
    """Load cache tracking which article URLs have appeared in recent podcast episodes.

    Format: {url: {"day": "monday", "shown_at": "<ISO8601>"}}
    Entries older than PODCAST_SHOWN_TTL_DAYS are discarded so articles can
    reappear after a full 7-day rotation.
    """
    if not os.path.exists(PODCAST_SHOWN_FILE):
        return {}
    try:
        with open(PODCAST_SHOWN_FILE, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        cutoff = datetime.now(timezone.utc) - timedelta(days=PODCAST_SHOWN_TTL_DAYS)
        valid = {
            url: entry for url, entry in raw.items()
            if datetime.fromisoformat(entry['shown_at']) > cutoff
        }
        if len(valid) != len(raw):
            print(f"🧹 Cleaned podcast shown cache: {len(raw)} → {len(valid)} entries")
        return valid
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
    """Load cached per-article theme scores."""
    if not os.path.exists(THEME_SCORE_CACHE_FILE):
        return {}
    try:
        with open(THEME_SCORE_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_theme_score_cache(cache: Dict):
    """Persist theme score cache, pruning entries older than TTL."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=THEME_SCORE_CACHE_TTL_DAYS)).isoformat()
    pruned = {k: v for k, v in cache.items() if v.get('cached_at', '') >= cutoff}
    try:
        with open(THEME_SCORE_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(pruned, f)
    except Exception as e:
        print(f"⚠️ Failed to save theme score cache: {e}")


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


def load_wlt_cache():
    """Load WLT scraping cache"""
    if not os.path.exists(WLT_CACHE_FILE):
        return {}
    
    try:
        with open(WLT_CACHE_FILE, 'r') as f:
            cache = json.load(f)
        
        cache_expiry = timedelta(hours=SYSTEM['cache_expiry']['scored_hours'])
        cutoff = datetime.now(timezone.utc).timestamp() - cache_expiry.total_seconds()
        
        # Defensive: ensure all cache values are dicts
        valid_cache = {}
        for url_hash, entry in cache.items():
            if isinstance(entry, dict) and entry.get('timestamp', 0) > cutoff:
                valid_cache[url_hash] = entry
        
        if len(valid_cache) != len(cache):
            print(f"🧹 Cleaned WLT cache: {len(cache)} → {len(valid_cache)} entries")
        
        return valid_cache
        
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_wlt_cache(cache):
    """Save WLT scraping cache"""
    try:
        with open(WLT_CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save WLT cache: {e}")


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
                article_data = {
                    'title': title,
                    'link': full_url,
                    'description': description,
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
    cache = load_wlt_cache()

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

        save_wlt_cache(cache)
        return articles

    except Exception as e:
        print(f"⚠️ Failed to scrape Williams Lake Tribune: {e}")
        return []


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
        
        articles = []
        for entry in parsed.entries:
            article = Article(entry, feed['title'], feed['html_url'], feed['url'])
            
            if article.pub_date < cutoff_date:
                continue
            
            if article.should_filter():
                continue
            
            articles.append(article)
        
        if articles:
            print(f"  ✓ {feed['title']}: {len(articles)} articles")
        
        return articles
        
    except Exception as e:
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


def deduplicate_articles(articles: List[Article]) -> List[Article]:
    """Remove duplicate articles based on URL and title similarity.

    Uses three complementary signals, checked in order:
      1. Exact URL hash match (canonical URL, tracking params stripped).
      2. Fuzzy string similarity on the full title (fuzz.ratio /
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
                fuzz.ratio(article.title_normalized, seen_title),
                fuzz.token_sort_ratio(article.title_normalized, seen_title),
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
                fuzz.ratio(news_art.title_normalized, spec_art.title_normalized),
                fuzz.token_sort_ratio(news_art.title_normalized, spec_art.title_normalized),
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


def dedup_by_story_group(articles: List[Article]) -> List[Article]:
    """Collapse articles that Claude labelled with the same story_group.

    Within a single category's article list, when multiple pieces cover the
    same discrete news event (identical story_group string), only the
    highest-scored article is kept.  Articles with no story_group (null) are
    left untouched.
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
        best = max(group_articles, key=lambda x: x.score)
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


def score_articles_with_claude(articles: List[Article], api_key: str) -> List[Article]:
    """Score and categorize articles using Claude API with prompt caching"""
    if not articles:
        return []

    cache = load_scored_cache()

    # Load scoring interests
    interests_file = CONFIG_DIR / 'scoring_interests.txt'
    try:
        with open(interests_file, 'r') as f:
            interests = f.read().strip()
    except FileNotFoundError:
        print("⚠️ scoring_interests.txt not found, using basic scoring")
        interests = "Technology, science, climate, local news"

    client = anthropic.Anthropic(api_key=api_key)

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
        f"Rate articles 0-100 for personal relevance and quality based on these interest priorities:\n{interests}\n\n"
        f"CATEGORY DEFINITIONS AND ASSIGNMENT RULES:\n"
        f"Assign each article to exactly ONE category using the descriptions, signals, and exclusions below:\n\n"
        f"{category_guide}\n\n"
        f"Also provide a 'story_group': a 3-5 word label for the SPECIFIC event or product covered "
        f"(e.g. 'Apple AirTag 2 launch', 'Williams Lake council vote', 'OpenAI GPT-5 release'). "
        f"Use null for standalone analysis, opinion, or evergreen pieces with no discrete news event. "
        f"Articles covering the SAME event MUST use IDENTICAL story_group strings."
    )

    scored_articles = []
    uncached = []

    for article in articles:
        if article.url_hash in cache:
            article.score = cache[article.url_hash]['score']
            article.category = cache[article.url_hash]['category']
            article.story_group = cache[article.url_hash].get('story_group')
            scored_articles.append(article)
        else:
            uncached.append(article)

    if uncached:
        print(f"\n🤖 Scoring {len(uncached)} new articles with Claude...")
        print(f"   (using cache for {len(scored_articles)} articles)")

        batch_size = 15
        for i in range(0, len(uncached), batch_size):
            batch = uncached[i:i + batch_size]

            articles_text = "\n\n".join([
                f"Article {j+1}:\nTitle: {article.title}\nSource: {article.source}\nDescription: {article.description[:300]}"
                for j, article in enumerate(batch)
            ])

            prompt = f"""Rate each article from 0-100, assign a category (see system prompt for definitions), and provide a story_group.

Respond with ONLY a JSON array (no other text):
[
  {{"article": 1, "score": 75, "category": "ai-tech", "story_group": "Apple AirTag 2 launch"}},
  {{"article": 2, "score": 45, "category": "news", "story_group": null}}
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

                for score_data in scores:
                    idx = score_data['article'] - 1
                    if 0 <= idx < len(batch):
                        article = batch[idx]
                        article.score = score_data['score']
                        article.category = score_data.get('category', 'news')
                        if article.category not in CATEGORIES:
                            article.category = categorize_article(article.title, article.description) or 'news'
                        article.story_group = score_data.get('story_group') or None

                        cache[article.url_hash] = {
                            'score': article.score,
                            'category': article.category,
                            'story_group': article.story_group,
                            'timestamp': timestamp
                        }

                        scored_articles.append(article)
                
            except json.JSONDecodeError as e:
                print(f"  ⚠️ JSON parsing error: {e}")
                print(f"     Response was: {response_text[:300]!r}")
                for article in batch:
                    article.score = 50
                    article.category = categorize_article(article.title, article.description) or 'news'
                    scored_articles.append(article)

            except Exception as e:
                print(f"  ⚠️ API error: {e}")
                for article in batch:
                    article.score = 50
                    article.category = categorize_article(article.title, article.description) or 'news'
                    scored_articles.append(article)
    
    save_scored_cache(cache)
    return scored_articles


def scrub_feed_with_haiku(articles: List[Article], api_key: str) -> List[Article]:
    """Final headline-only pass with Haiku to catch unwanted subjects that slipped through keyword filters."""
    if not articles:
        return []

    local_signals = [s.lower() for s in FILTERS.get('local_signals', [])]

    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = (
        "You are a strict content filter reviewing article headlines.\n\n"
        "Remove articles whose PRIMARY subject is one of:\n"
        "- Sports: game scores/recaps, drafts, trades, player stats, sports leagues "
        "(NFL, NBA, NHL, MLB, CFL, MLS, UFC, MMA, FIFA, PGA, NASCAR, Premier League, "
        "Champions League, World Cup, Olympics, Super Bowl), sports tournaments, "
        "championships, playoff coverage, athlete profiles focused on sport performance\n"
        "- Celebrity gossip: tabloid content, paparazzi, red carpet, award show results, "
        "celebrity relationships/feuds\n"
        "- Deals/promotions: promo codes, coupons, flash sales, best deals roundups, "
        "discount codes\n"
        "- Advice columns: Dear Abby, Ask Amy, Miss Manners, relationship/dating advice\n\n"
        "KEEP articles that use sports/entertainment as context for a deeper story "
        "(e.g. technology in sports, economics of a league, health research on athletes).\n"
        "KEEP all local community news even if sports-related.\n\n"
        "Respond ONLY with valid JSON: {\"remove\": [list of article numbers to remove]}\n"
        "If nothing should be removed respond with: {\"remove\": []}"
    )

    kept: List[Article] = []
    total_removed = 0

    batch_size = 40
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i + batch_size]

        # Build numbered headline list; flag local articles so Haiku respects the keep rule
        lines = []
        for j, article in enumerate(batch):
            title_lower = article.title.lower()
            is_local = any(sig in title_lower for sig in local_signals)
            prefix = f"{j+1}. [LOCAL] " if is_local else f"{j+1}. "
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

            raw = response.content[0].text.strip()
            # Strip markdown fences if present
            if raw.startswith("```"):
                lines_r = raw.splitlines()
                inner = lines_r[1:]
                if inner and inner[-1].strip() == "```":
                    inner = inner[:-1]
                raw = "\n".join(inner).strip()

            result = json.loads(raw)
            remove_nums = set(result.get("remove", []))

            for j, article in enumerate(batch):
                if (j + 1) in remove_nums:
                    print(f"  ✂️  Scrubbed: {article.title[:90]}")
                    total_removed += 1
                else:
                    kept.append(article)

        except Exception as e:
            print(f"  ⚠️ Scrub batch {i // batch_size + 1} failed ({e}), keeping all")
            kept.extend(batch)

    if total_removed:
        print(f"✂️  Final scrub removed {total_removed} article(s) from {len(articles)} quality articles")
    else:
        print(f"✂️  Final scrub: feed is clean ({len(articles)} articles passed)")

    return kept


def enforce_local_priority(articles: List[Article]) -> List[Article]:
    """Enforce 80+ score and 'local' category for any article containing Cariboo/local signals.

    Claude reliably applies the local priority rule for most articles, but occasionally
    scores on topic relevance alone and misses the geographic locality signal. This
    post-scoring pass guarantees the intent of the scoring_interests.txt rule:
    'Local Williams Lake/Cariboo content should score 80+ regardless of topic'.
    """
    local_signals = [s.lower() for s in FILTERS.get('local_signals', [])]
    if not local_signals:
        return articles

    enforced = 0
    for article in articles:
        # Check title only — description can contain "Williams Lake" as a dateline or
        # source byline on syndicated Tribune articles, which would falsely promote
        # national/sports wire content to local priority.
        title_text = article.title.lower()
        if any(signal in title_text for signal in local_signals):
            if article.score < 80:
                article.score = 80
                enforced += 1
            # Always correct the category so local articles reach the local feed
            article.category = 'local'

    if enforced:
        print(f"📍 Local priority enforced: boosted {enforced} article(s) to score 80+")
    return articles


def apply_source_preferences(articles: List[Article]) -> List[Article]:
    """Apply score adjustments based on source type preferences (print vs broadcast)"""
    source_map = SOURCE_PREFS.get('source_map', {})
    source_types = SOURCE_PREFS.get('source_types', {})
    adjusted_count = 0

    for article in articles:
        source_type = source_map.get(article.source)
        if source_type and source_type in source_types:
            adjustment = source_types[source_type].get('score_adjustment', 0)
            if adjustment != 0:
                article.score = max(0, min(100, article.score + adjustment))
                adjusted_count += 1

    if adjusted_count:
        print(f"📰 Source preferences: adjusted scores for {adjusted_count} articles")
    return articles


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
        item = {
            "id": article.link,
            "url": article.link,
            "title": article.title if article.title.startswith(f"[{article.source}]") else f"[{article.source}] {article.title}",
            "content_html": article.description,
            "date_published": article.pub_date.isoformat(),
            "authors": [{"name": article.source, "url": article.source_url}]
        }
        
        if hasattr(article, 'image') and article.image:
            item["image"] = article.image
            item["content_html"] = f'<img src="{html_escape(article.image)}" style="width:100%;max-height:300px;object-fit:cover;" />\n' + (article.description or "")

        item["_score"] = article.score

        if category == 'local':
            item["_local"] = True
            item["tags"] = ["local-priority"]

        feed["items"].append(item)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(feed, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated {category} feed: {len(feed['items'])} articles")


def load_podcast_schedule():
    """Load podcast schedule configuration"""
    try:
        return load_json_config('podcast_schedule.json')
    except SystemExit:
        print("⚠️ podcast_schedule.json not found, skipping podcast feed")
        return None


def _keyword_match_count(text: str, keywords: List[str]) -> int:
    """Count how many keywords appear in the text (case-insensitive)."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw.lower() in text_lower)


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

    print(f"🎯 Ingest theme scoring: {len(uncached)} articles × {len(schedule)} themes (async batch)...")

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
) -> set:
    """Reserve articles that clearly belong to a different day's theme.

    For each article in the podcast cache that has a complete set of cached
    theme scores (all 7 days), compare today's score against every other day.
    When another day's score beats today's by at least ``theme_routing_gap``
    points AND meets ``theme_routing_min_score``, the article is:

      1. Proactively banked into that day's holdover cache so it surfaces on
         the right episode even if today's feed would have consumed it first.
      2. Added to the returned reserved set so ``generate_podcast_feed`` skips
         it today.

    Articles missing a cached score for any theme are left for normal
    today-centric processing — routing only acts on complete data.
    """
    schedule = schedule_config.get('schedule', {})
    routing_gap = schedule_config.get('theme_routing_gap', 20)
    routing_min_score = schedule_config.get('theme_routing_min_score', 55)
    holdover_threshold = schedule_config.get('holdover_threshold', 30)

    if not schedule or today_name not in schedule:
        return set()

    theme_cache = load_theme_score_cache()
    reserved_urls = set()
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
            reserved_urls.add(url)
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
        print(
            f"  🗓️  Theme routing: deferred {len(reserved_urls)} articles to better-fit days"
            f" (gap ≥ {routing_gap}pts, min {routing_min_score}) → {day_summary}"
        )
        if total_banked:
            print(f"  📦 Pre-banked {total_banked} articles into upcoming day holdovers")

    return reserved_urls


def generate_podcast_feed(theme_name: str, cached_articles: List[Dict], podcast_shown_cache: Dict,
                          reserved_urls: set = None) -> set:
    """Generate a themed podcast feed from weekly cached articles.

    Args:
        theme_name: Day name (e.g., 'monday', 'tuesday')
        cached_articles: List of article dicts from the weekly cache
        podcast_shown_cache: Dict of {url: entry} for articles already used in
            recent podcast episodes.  Articles in this set are excluded so each
            day's episode surfaces fresh content.

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
        return set()

    schedule = schedule_config['schedule']

    if theme_name not in schedule:
        print(f"⚠️ No podcast schedule entry for {theme_name}")
        return set()

    today = schedule[theme_name]
    theme_categories = today['categories']
    theme_label = today['label']
    theme_description = today.get('theme_description', today.get('description', ''))
    theme_scoring_prompt = today.get('scoring_prompt', '')
    theme_keywords = [kw.lower() for kw in today.get('keywords', [])]
    max_articles = schedule_config.get('max_articles', 10)
    min_score = schedule_config.get('min_score', 25)
    include_bonus = schedule_config.get('include_top_from_other', 0)
    bonus_min_score = schedule_config.get('other_min_score', 70)
    holdover_threshold = schedule_config.get('holdover_threshold', 30)

    # Get API key for theme scoring
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("⚠️ No API key available for theme scoring")
        return set()

    # Rural/local context signals — ai-tech articles without these get penalized
    # in the podcast to keep the feed locally grounded
    rural_context_signals = [
        "rural", "community", "small town", "local", "municipal", "civic",
        "off-grid", "remote", "broadband", "connectivity", "digital equity",
        "precision agriculture", "farm", "forestry", "ranch", "mining",
        "wildfire", "emergency", "telehealth", "education", "indigenous",
        "first nation", "co-op", "cooperative", "volunteer", "non-profit",
        "williams lake", "cariboo", "quesnel", "100 mile house",
        "horsefly", "lac la hache", "chilcotin", "bella coola",
        "resource", "homestead", "self-hosted", "mesh network", "meshtastic",
        "lora", "solar", "off grid", "preparedness", "resilience",
    ]
    ai_tech_penalty = schedule_config.get('ai_tech_no_context_penalty', 30)

    # Convert cached article dicts to Article objects
    # Create a simple Article-like class for cached articles
    class CachedArticle:
        def __init__(self, data):
            self.title = data['title']
            self.link = data['link']
            self.description = data['description']
            self.pub_date = datetime.fromisoformat(data['pub_date'])
            self.source = data['source']
            self.source_url = data['source_url']
            self.score = data['score']
            self.category = data['category']
            self.image = data.get('image')

    all_cached = [CachedArticle(item) for item in cached_articles]
    all_cached_urls = {a.link for a in all_cached}

    # Load cross-week holdover: articles that scored well on this theme in previous
    # runs and were banked for future episodes (28-day retention, bypasses base filter).
    holdover_cache = load_theme_holdover_cache()
    holdover_raw = holdover_cache.get(theme_name, [])
    holdover_pool = [
        CachedArticle(item) for item in holdover_raw
        if item['link'] not in podcast_shown_cache
        and not _is_aggregator_url(item['link'])
        and item['link'] not in all_cached_urls  # already in 7-day pool
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

    # Rescue: include articles below the base threshold when they already have a
    # cached theme score >= holdover_threshold.  These proved their thematic fit
    # even though their general quality score is low (e.g. niche local sources).
    theme_score_cache = load_theme_score_cache()
    rescued = [
        a for a in all_cached
        if a.score < min_score
        and not _is_aggregator_url(a.link)
        and a.link not in podcast_shown_cache
        and theme_score_cache.get(f"{a.link}:::{theme_label}", {}).get('score', 0) >= holdover_threshold
    ]
    if rescued:
        print(f"  🌾 +{len(rescued)} theme-relevant articles rescued (base score < {min_score})")
        theme_pool.extend(rescued)

    # Merge holdover articles into the pool (already theme-qualified, skip base filter)
    theme_pool.extend(holdover_pool)

    # Exclude articles already used in a recent podcast episode
    before_shown_filter = len(theme_pool)
    theme_pool = [a for a in theme_pool if a.link not in podcast_shown_cache]
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

    # Exclude articles proactively routed to a better-fit day; holdover pool
    # articles bypass this filter since they were explicitly banked for today.
    holdover_links = {a.link for a in holdover_pool}
    if reserved_urls:
        before_reserved = len(theme_pool)
        theme_pool = [
            a for a in theme_pool
            if a.link not in reserved_urls or a.link in holdover_links
        ]
        deferred = before_reserved - len(theme_pool)
        if deferred:
            print(f"  🗓️  Deferred {deferred} articles to their better-fit day's episode")

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

    # Bank articles with strong theme scores for future episodes of this day's theme.
    # This builds the cross-week holdover pool so good content accumulates over time.
    update_theme_holdover(theme_name, theme_label, theme_scored, holdover_threshold)

    # Apply rural-context penalty: ai-tech articles without local/rural signals are demoted
    ai_tech_penalty = schedule_config.get('ai_tech_no_context_penalty', 30)
    scored_pool = []
    for article, theme_score in theme_scored:
        text = f"{article.title} {article.description}"
        final_score = theme_score

        # Penalize ai-tech articles that lack rural/local context
        if article.category == 'ai-tech':
            has_rural_context = _keyword_match_count(text, rural_context_signals) > 0
            if not has_rural_context:
                final_score = max(0, final_score - ai_tech_penalty)

        scored_pool.append((article, final_score, theme_score))

    # Relative scoring: if even the best article in the pool scores below the
    # absolute threshold, scale all scores so the top scorer reaches min_score.
    # This ensures theme-relevant articles always outrank zero-relevance filler
    # on thin news days rather than losing to tiebreaker (base score).
    best_final = max((fs for _, fs, _ in scored_pool), default=0)
    if 0 < best_final < min_score:
        scale = min_score / best_final
        print(f"  📈 Relative scoring: pool max was {best_final}, scaled ×{scale:.1f}")
        scored_pool = [
            (a, min(100, round(fs * scale)), min(100, round(ts * scale)))
            for a, fs, ts in scored_pool
        ]

    # Sort by final score descending
    scored_pool.sort(key=lambda x: x[1], reverse=True)
    theme_articles = [(a, fs, ts) for a, fs, ts in scored_pool[:max_articles]]

    # Optionally include top articles from other categories as bonus picks
    # with theme-aware scoring for diversity
    bonus_entries = []
    if include_bonus > 0:
        # Collect all non-theme articles that meet minimum score
        other = []
        for article in all_cached:
            if article.category not in theme_set and article.score >= bonus_min_score:
                other.append((article, article.category))

        theme_urls = {a.link for a, _, _ in theme_articles}
        other_filtered = [
            (a, c) for a, c in other
            if a.link not in theme_urls and a.link not in podcast_shown_cache
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

                bonus_entries.append((article, theme_score, theme_score))
                category_counts[cat] += 1

                if len(bonus_entries) >= include_bonus:
                    break

    all_entries = theme_articles + bonus_entries

    if not all_entries:
        print(f"🎙️ Podcast feed ({theme_label}): no articles met criteria")
        return set()

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
        text = f"{article.title} {article.description or ''}".lower()
        kw_hits = _keyword_match_count(text, theme_keywords)
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
    for article, final_score, theme_score in all_entries:
        text = f"{article.title} {article.description or ''}".lower()
        kw_matches = _keyword_match_count(text, theme_keywords)
        boosted_score = min(100, kw_matches * 20 + article.score * 0.3)
        is_bonus = _is_bonus_article(article)
        item = {
            "id": article.link,
            "url": article.link,
            "title": article.title if article.title.startswith(f"[{article.source}]") else f"[{article.source}] {article.title}",
            "content_html": article.description,
            "date_published": article.pub_date.isoformat(),
            "authors": [{"name": article.source, "url": article.source_url}],
            "ai_score": article.score,
            "_quality_score": article.score,
            "_theme_score": theme_score,
            "_final_score": final_score,
            "_keyword_matches": kw_matches,
            "_boosted_score": int(boosted_score),
            "_category": article.category,
            "_source_category": article.category,
            "_is_bonus": is_bonus
        }
        if hasattr(article, 'image') and article.image:
            item["image"] = article.image
            item["content_html"] = f'<img src="{html_escape(article.image)}" style="width:100%;max-height:300px;object-fit:cover;" />\n' + (article.description or "")
        items_with_score.append((int(boosted_score), item))

    items_with_score.sort(key=lambda x: x[0], reverse=True)
    feed["items"] = [item for _, item in items_with_score]

    with open(feed_filename, 'w', encoding='utf-8') as f:
        json.dump(feed, f, indent=2, ensure_ascii=False)

    avg_theme_score = sum(ts for _, _, ts in theme_articles) / len(theme_articles) if theme_articles else 0
    cross_cat = bonus_count
    print(f"🎙️ Podcast feed {theme_name} ({theme_label}): {len(all_entries)} articles (avg theme score: {avg_theme_score:.1f}, {cross_cat} cross-category)")

    return {a.link for a, _, _ in all_entries}


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
    
    opml_path = sys.argv[1] if len(sys.argv) > 1 else 'feeds.opml'
    feeds = parse_opml(opml_path)
    
    lookback_hours = SYSTEM['lookback_hours']
    cutoff_date = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    print(f"\n📥 Fetching articles from last {lookback_hours} hours...")
    
    all_articles = []
    for feed in feeds:
        articles = fetch_feed_articles(feed, cutoff_date)
        all_articles.extend(articles)
    
    wlt_articles = scrape_wlt_news()
    for wlt_entry in wlt_articles:
        class WLTEntry:
            def get(self, key, default=''):
                return wlt_entry.get(key, default)
        
        article = Article(WLTEntry(), 'Williams Lake Tribune', WLT_BASE_URL)
        article.title = wlt_entry['title']
        article.link = wlt_entry['link']
        article.description = wlt_entry['description']
        article.image = wlt_entry.get('image')
        article.score = LIMITS['local_priority_score']
        article.category = 'local'
        all_articles.append(article)
    
    print(f"\n📈 Total fetched: {len(all_articles)} articles")
    
    unique_articles = deduplicate_articles(all_articles)
    
    shown_cache = load_shown_cache()
    shown_terms_cache = load_shown_terms_cache()

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
    
    scored_articles = score_articles_with_claude(new_articles, api_key)

    scored_articles = enforce_local_priority(scored_articles)

    scored_articles = apply_source_preferences(scored_articles)

    quality_articles = [a for a in scored_articles if a.score >= LIMITS['min_claude_score']]
    print(f"⭐ Quality filter (score >= {LIMITS['min_claude_score']}): {len(scored_articles)} → {len(quality_articles)} articles")

    print(f"\n✂️  Running final headline scrub with Haiku ({len(quality_articles)} articles)...")
    quality_articles = scrub_feed_with_haiku(quality_articles, api_key)

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

    # Load weekly cache for podcast feed generation
    podcast_cache = load_podcast_cache()

    # Generate only today's themed podcast feed from weekly cache.
    # Regenerating all 7 feeds on every run causes identical feeds across days
    # because the article pool and cached theme scores don't change between runs.
    # Instead, each day's episode is generated once (on that day) from a pool
    # that excludes articles already shown in the past 7 days of podcast episodes.
    print(f"\n🎙️ Generating today's podcast feed from {len(podcast_cache)} cached articles...")
    if schedule_config and schedule_config.get('enabled', False):
        today_name = datetime.now(timezone.utc).strftime('%A').lower()
        if today_name in schedule_config['schedule']:
            podcast_shown_cache = load_podcast_shown_cache()
            # Before generating today's feed, reserve articles that score
            # significantly higher on an upcoming day's theme so they aren't
            # consumed here and then excluded from the day they truly belong to.
            reserved_for_other_days = route_articles_to_best_themes(
                podcast_cache, schedule_config, today_name
            )
            selected_urls = generate_podcast_feed(
                today_name, podcast_cache, podcast_shown_cache, reserved_for_other_days
            )
            if selected_urls:
                now_iso = datetime.now(timezone.utc).isoformat()
                for url in selected_urls:
                    podcast_shown_cache[url] = {'day': today_name, 'shown_at': now_iso}
                save_podcast_shown_cache(podcast_shown_cache)
                print(f"  📌 Marked {len(selected_urls)} articles as shown for future episode exclusion")
        else:
            print(f"⚠️ No podcast schedule for today ({today_name})")

    # Load existing feeds to preserve old articles
    retention_days = LIMITS['feed_retention_days']
    retention_cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    
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
            r_terms = _term_set(re.sub(r'^\[.*?\]\s*', '', item.get('title', '')).lower())
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
                'title': item['title'],
                'description': item['content_html'],
                'pub_date': datetime.fromisoformat(item['date_published'].replace('Z', '+00:00')),
                'source': item['authors'][0]['name'],
                'source_url': item['authors'][0]['url'],
                'score': item.get('_score', 0),
                'image': item.get('image')
            })() for item in fresh_existing
        ]
        
        all_items.sort(key=lambda a: a.pub_date, reverse=True)
        all_items = all_items[:LIMITS['max_feed_size']]
        
        generate_json_feed(all_items, cat_key, feed_file)
    
    now_ts = datetime.now(timezone.utc).timestamp()
    for article in quality_articles:
        shown_cache[article.url_hash] = now_ts
        shown_terms_cache[article.url_hash] = {
            'ts': now_ts,
            'terms': list(article.title_terms),
        }
    save_shown_cache(shown_cache)
    save_shown_terms_cache(shown_terms_cache)
    
    generate_opml()
    
    print("\n📊 Final stats:")
    print(f"  Total sources: {len(feeds)}")
    print(f"  Articles fetched: {len(all_articles)}")
    print(f"  After dedup: {len(unique_articles)}")
    print(f"  New articles: {len(new_articles)}")
    print(f"  After scoring: {len(quality_articles)}")
    
    print("\n✅ Feed generation complete!")


if __name__ == '__main__':
    main()
