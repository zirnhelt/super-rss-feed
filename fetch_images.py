#!/usr/bin/env python3
"""
Image fetching module with OpenGraph scraping and fallbacks
"""

import json
import hashlib
import re
import requests
from typing import Dict, Optional, Tuple
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from pathlib import Path

CONFIG_DIR = Path(__file__).parent / 'config'
CACHE_FILE = Path(__file__).parent / 'image_cache.json'
CACHE_EXPIRY_DAYS = 30

# Apple News share links: `A…` is an article, `T…` is a publication's channel.
# IDs are opaque base64url and cannot be derived from a publisher URL, so the
# only way to get one is to find it in the wild.
APPLE_NEWS_LINK_RE = re.compile(r'apple\.news/([AT][A-Za-z0-9_-]{8,})')


def extract_apple_news_ids(html: str) -> Tuple[Optional[str], Optional[str]]:
    """Pull the (article_id, channel_id) pair out of a publisher's page HTML.

    Publishers that distribute through Apple News usually emit their own
    `apple.news/A…` share link and a `apple.news/T…` "follow our channel" link.

    An ID is only accepted when the page carries exactly one distinct candidate
    of that kind. Pages with several — a related-articles rail, a syndication
    block — are ambiguous, and guessing wrong sends the reader to a different
    article than the headline promised.
    """
    articles, channels = set(), set()
    for token in APPLE_NEWS_LINK_RE.findall(html or ''):
        (articles if token.startswith('A') else channels).add(token)

    return (
        articles.pop() if len(articles) == 1 else None,
        channels.pop() if len(channels) == 1 else None,
    )

def load_image_cache():
    """Load image URL cache"""
    if not CACHE_FILE.exists():
        return {}
    
    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        
        # Clean expired entries
        cutoff = datetime.now(timezone.utc).timestamp() - (CACHE_EXPIRY_DAYS * 24 * 3600)
        valid_cache = {k: v for k, v in cache.items() if v.get('timestamp', 0) > cutoff}
        
        if len(valid_cache) != len(cache):
            print(f"🧹 Cleaned image cache: {len(cache)} → {len(valid_cache)} entries")
            save_image_cache(valid_cache)
        
        return valid_cache
    except:
        return {}


def save_image_cache(cache):
    """Save image URL cache"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save image cache: {e}")


def fetch_page_metadata(url, timeout=3) -> Dict:
    """Scrape one article page for everything the pipeline wants from its HTML.

    Returns ``{'image', 'apple_article', 'apple_channel'}``, any of which may be
    None. The Apple News IDs ride along on the request the image scrape was
    already making, so harvesting them costs no extra fetch.
    """
    result = {'image': None, 'apple_article': None, 'apple_channel': None}
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; RSS Reader/1.0)',
            'Accept': 'text/html,application/xhtml+xml'
        }

        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()

        result['apple_article'], result['apple_channel'] = extract_apple_news_ids(response.text)

        soup = BeautifulSoup(response.text, 'html.parser')

        # Try various OpenGraph image tags
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            result['image'] = og_image['content']
            return result

        # Try Twitter card image
        twitter_image = soup.find('meta', {'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            result['image'] = twitter_image['content']
            return result

        # Try standard meta image
        meta_image = soup.find('meta', {'name': 'image'})
        if meta_image and meta_image.get('content'):
            result['image'] = meta_image['content']

        return result

    except Exception as e:
        return result


def fetch_page_title(url, timeout=3):
    """Fetch og:title or <title> from a page"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; RSS Reader/1.0)',
            'Accept': 'text/html,application/xhtml+xml'
        }

        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()

        if soup.title and soup.title.string:
            return soup.title.string.strip()

        return None

    except Exception:
        return None


def get_source_logo(source_url):
    """Get favicon/logo for a source domain"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(source_url)
        domain = parsed.netloc or parsed.path
        
        # Try Google's favicon service (reliable fallback)
        return f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
    except:
        return None


def get_article_image(article_url, source_url, cache=None):
    """
    Get image for article - tries OpenGraph, falls back to source logo

    Returns: (image_url, cache_updated, apple_ids) where apple_ids is
    ``{'article', 'channel'}`` harvested from the same page fetch, both None on
    a cache hit (no fetch happened) or when the page carries no Apple News link.
    """
    if cache is None:
        cache = load_image_cache()

    no_apple = {'article': None, 'channel': None}

    # Check cache first
    url_hash = hashlib.md5(article_url.encode()).hexdigest()
    if url_hash in cache:
        return cache[url_hash].get('image_url'), False, no_apple

    # Try OpenGraph scraping
    meta = fetch_page_metadata(article_url)
    og_image = meta['image']
    apple_ids = {'article': meta['apple_article'], 'channel': meta['apple_channel']}

    if og_image:
        # Cache successful OpenGraph fetch
        cache[url_hash] = {
            'image_url': og_image,
            'source': 'opengraph',
            'timestamp': datetime.now(timezone.utc).timestamp()
        }
        return og_image, True, apple_ids

    # Fall back to source logo
    logo = get_source_logo(source_url)
    if logo:
        cache[url_hash] = {
            'image_url': logo,
            'source': 'favicon',
            'timestamp': datetime.now(timezone.utc).timestamp()
        }
        return logo, True, apple_ids

    # No image found
    cache[url_hash] = {
        'image_url': None,
        'source': 'none',
        'timestamp': datetime.now(timezone.utc).timestamp()
    }
    return None, True, apple_ids


def record_apple_news_ids(apple_news_cache: Dict, article, apple_ids: Dict) -> None:
    """Fold one page's Apple News sightings into the persistent cache.

    Keys mirror what the curator resolves against later: articles by publisher
    URL (``article.link``, the same value `item_source_link()` returns for a
    written item), channels by source name.
    """
    now = datetime.now(timezone.utc).timestamp()

    if apple_ids.get('article'):
        apple_news_cache.setdefault('articles', {})[article.link] = {
            'id': apple_ids['article'], 'ts': now,
        }

    # First sighting wins: a publication's channel ID never changes, and not
    # re-writing it keeps the cache stable across runs.
    if apple_ids.get('channel'):
        channels = apple_news_cache.setdefault('channels', {})
        if article.source not in channels:
            channels[article.source] = {'id': apple_ids['channel'], 'ts': now}


def batch_fetch_images(articles, max_fetch=20, apple_news_cache=None):
    """
    Fetch images for a batch of articles
    Only fetches OpenGraph for first max_fetch articles to avoid slowdown

    When ``apple_news_cache`` is supplied it is filled in place with any Apple
    News IDs found on the pages this pass already fetches — article IDs keyed by
    publisher URL, channel IDs keyed by source name. Channel IDs are the durable
    half: one sighting covers every future article from that publication.
    """
    cache = load_image_cache()
    cache_updated = False
    images_fetched = 0

    for i, article in enumerate(articles):
        # Check if article already has an image
        if hasattr(article, 'image') and article.image:
            continue

        # For first max_fetch articles, try OpenGraph
        # For rest, just use favicon fallback
        if images_fetched < max_fetch:
            image_url, updated, apple_ids = get_article_image(
                article.link, article.source_url, cache
            )
            if updated:
                cache_updated = True
            if image_url:
                article.image = image_url
                images_fetched += 1
            if apple_news_cache is not None:
                record_apple_news_ids(apple_news_cache, article, apple_ids)
        else:
            # Just use favicon for remaining articles
            logo = get_source_logo(article.source_url)
            article.image = logo if logo else None
        
        # Final safety net - ensure every article has an image
        if not hasattr(article, 'image') or not article.image:
            logo = get_source_logo(article.source_url)
            article.image = logo if logo else None
    
    if cache_updated:
        save_image_cache(cache)
    
    return articles


if __name__ == '__main__':
    # Test the image fetcher
    print("Testing image fetching...")
    
    test_url = "https://arstechnica.com/ai/2025/01/openai-offers-free-chatgpt-pro-to-federal-workers/"
    test_source = "https://arstechnica.com"
    
    image_url, _, apple_ids = get_article_image(test_url, test_source)
    print(f"Image URL: {image_url}")
    print(f"Apple News IDs: {apple_ids}")
