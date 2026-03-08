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
SHOWN_TERMS_CACHE_FILE = 'shown_terms_cache.json'   # Term sets for cross-run story dedup

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
    # Subscribed / preferred local paper always wins dedup
    if source_type == 'preferred_local':
        return 0
    # Other explicitly local-priority articles
    if article.category == 'local' or article.score == LIMITS.get('local_priority_score', 100):
        return 1
    if source_type == 'print':
        return 2
    if source_type == 'broadcast':
        return 4
    return 3  # unclassified sources


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
                string_sim > 78
                or (overlap >= 0.40 and shared_terms >= 3)
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
    # category list so they are only billed on cache miss, not on every batch.
    categories_json = json.dumps(list(CATEGORIES.keys()))
    cached_system_prompt = (
        f"You are a news curator. Respond only with valid JSON arrays.\n\n"
        f"Rate articles 0-100 for personal relevance and quality based on these interest priorities:\n{interests}\n\n"
        f"Also assign each article to ONE of these categories: {categories_json}"
    )

    scored_articles = []
    uncached = []

    for article in articles:
        if article.url_hash in cache:
            article.score = cache[article.url_hash]['score']
            article.category = cache[article.url_hash]['category']
            scored_articles.append(article)
        else:
            uncached.append(article)

    if uncached:
        print(f"\n🤖 Scoring {len(uncached)} new articles with Claude...")
        print(f"   (using cache for {len(scored_articles)} articles)")

        batch_size = 10
        for i in range(0, len(uncached), batch_size):
            batch = uncached[i:i + batch_size]

            articles_text = "\n\n".join([
                f"Article {j+1}:\nTitle: {article.title}\nSource: {article.source}\nDescription: {article.description[:300]}"
                for j, article in enumerate(batch)
            ])

            prompt = f"""Rate each article from 0-100 and assign a category from: {categories_json}

Respond with ONLY a JSON array (no other text):
[
  {{"article": 1, "score": 75, "category": "ai-tech"}},
  {{"article": 2, "score": 45, "category": "news"}}
]

Articles to evaluate:
{articles_text}"""

            try:
                response = client.messages.create(
                    model="claude-haiku-4-5",
                    max_tokens=500,
                    system=[
                        {
                            "type": "text",
                            "text": cached_system_prompt,
                            "cache_control": {"type": "ephemeral"}
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

                        cache[article.url_hash] = {
                            'score': article.score,
                            'category': article.category,
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
        text = f"{article.title} {article.description}".lower()
        if any(signal in text for signal in local_signals):
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
            item["content_html"] = f'<img src="{article.image}" style="width:100%;max-height:300px;object-fit:cover;" />\n' + (article.description or "")
        
        if category == 'local':
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

    # The theme prompt is the same for all batches in this call, so put it in
    # the cached system message to avoid paying for it on every batch.
    cached_theme_system = (
        f"You are evaluating news articles for thematic relevance. Respond only with valid JSON arrays.\n\n"
        f"{theme_prompt}"
    )

    batch_size = 10

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
                max_tokens=500,
                system=[
                    {
                        "type": "text",
                        "text": cached_theme_system,
                        "cache_control": {"type": "ephemeral"}
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

    client = anthropic.Anthropic(api_key=api_key)

    # Build one combined system prompt covering all themes, then cache it so
    # subsequent batches in the same run pay only the (cheaper) cache-read rate.
    theme_descriptions = "\n\n".join(
        f"Theme key \"{day}\" — {cfg['label']}:\n{cfg.get('scoring_prompt', '')}"
        for day, cfg in schedule.items()
    )
    day_keys = list(schedule.keys())
    combined_system = (
        f"You are evaluating news articles for thematic relevance across multiple themes. "
        f"Respond only with valid JSON arrays.\n\n"
        f"Score each article 0-100 for each of the following themes:\n\n"
        f"{theme_descriptions}"
    )

    day_schema = ", ".join(f'"{d}": 0' for d in day_keys)

    batch_size = 10
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
                max_tokens=800,
                system=[
                    {
                        "type": "text",
                        "text": combined_system,
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text.strip()
            if response_text.startswith('```'):
                lines = response_text.splitlines()
                inner = lines[1:]
                if inner and inner[-1].strip() == '```':
                    inner = inner[:-1]
                response_text = '\n'.join(inner).strip()

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

            # Fallback score for any articles Claude omitted from the response
            for idx, article in enumerate(batch):
                if idx not in scored_in_batch:
                    for cfg in schedule.values():
                        key = f"{article.link}:::{cfg['label']}"
                        if key not in theme_cache:
                            theme_cache[key] = {'score': 50, 'cached_at': now_iso}

        except (json.JSONDecodeError, Exception) as e:
            print(f"  ⚠️ Ingest theme scoring error (batch {i//batch_size + 1}): {e}")
            for article in batch:
                for cfg in schedule.values():
                    key = f"{article.link}:::{cfg['label']}"
                    if key not in theme_cache:
                        theme_cache[key] = {'score': 50, 'cached_at': now_iso}

    save_theme_score_cache(theme_cache)
    print(f"   ✅ Ingest theme scoring complete ({len(uncached)} articles × {len(schedule)} themes cached)")


def generate_podcast_feed(theme_name: str, cached_articles: List[Dict], podcast_shown_cache: Dict) -> set:
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
    theme_description = today.get('description', '')
    theme_scoring_prompt = today.get('scoring_prompt', '')
    max_articles = schedule_config.get('max_articles', 10)
    min_score = schedule_config.get('min_score', 25)
    include_bonus = schedule_config.get('include_top_from_other', 0)
    bonus_min_score = schedule_config.get('other_min_score', 70)

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

    # The theme scoring prompt is the real semantic filter, so score ALL
    # quality-eligible articles — not just those in the day's primary categories.
    # theme_set marks which categories are "primary" for _is_bonus labelling only.
    theme_set = set(theme_categories)
    theme_pool = list(all_cached)

    # Filter by minimum quality score
    theme_pool = [a for a in theme_pool if a.score >= min_score]

    # Exclude articles already used in a recent podcast episode
    before_shown_filter = len(theme_pool)
    theme_pool = [a for a in theme_pool if a.link not in podcast_shown_cache]
    shown_excluded = before_shown_filter - len(theme_pool)
    if shown_excluded:
        print(f"  🔄 Excluded {shown_excluded} articles already shown in recent podcast episodes")

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

    # Build the JSON Feed with podcast-specific metadata
    feed_config = FEEDS_CONFIG['feeds'].get('podcast', {})
    # Mark articles whose category is outside the day's primary category list as bonus
    bonus_urls = {a.link for a, _, _ in all_entries if a.category not in theme_set}
    feed_filename = f"feed-podcast-{theme_name}.json"
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
            "bonus_count": len(bonus_urls),
            "scoring_method": "claude_theme_evaluation_weekly_cache"
        },
        "items": []
    }

    for article, final_score, theme_score in all_entries:
        is_bonus = article.link in bonus_urls
        item = {
            "id": article.link,
            "url": article.link,
            "title": article.title if article.title.startswith(f"[{article.source}]") else f"[{article.source}] {article.title}",
            "content_html": article.description,
            "date_published": article.pub_date.isoformat(),
            "authors": [{"name": article.source, "url": article.source_url}],
            "_quality_score": article.score,
            "_theme_score": theme_score,
            "_final_score": final_score,
            "_category": article.category,
            "_source_category": article.category,
            "_is_bonus": is_bonus
        }
        if hasattr(article, 'image') and article.image:
            item["image"] = article.image
            item["content_html"] = f'<img src="{article.image}" style="width:100%;max-height:300px;object-fit:cover;" />\n' + (article.description or "")
        feed["items"].append(item)

    with open(feed_filename, 'w', encoding='utf-8') as f:
        json.dump(feed, f, indent=2, ensure_ascii=False)

    avg_theme_score = sum(ts for _, _, ts in theme_articles) / len(theme_articles) if theme_articles else 0
    cross_cat = len(bonus_urls)
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

    # Save quality articles to weekly podcast cache
    save_podcast_cache(quality_articles)

    # Score new articles for all themes at ingest time so daily podcast generation
    # is a pure cache read with zero additional API calls (Options B + D).
    schedule_config = load_podcast_schedule()
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
            selected_urls = generate_podcast_feed(today_name, podcast_cache, podcast_shown_cache)
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

        cat_cap = LIMITS.get('max_new_per_category', {}).get(cat_key)
        if cat_cap and len(diverse_new) > cat_cap:
            print(f"🔢 Category cap ({cat_key}): {len(diverse_new)} → {cat_cap} articles")
            diverse_new = diverse_new[:cat_cap]
        
        all_items = diverse_new + [
            type('Article', (), {
                'link': item['url'],
                'title': item['title'],
                'description': item['content_html'],
                'pub_date': datetime.fromisoformat(item['date_published'].replace('Z', '+00:00')),
                'source': item['authors'][0]['name'],
                'source_url': item['authors'][0]['url'],
                'score': 0,
                'image': item.get('image')
            })() for item in existing_articles
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
