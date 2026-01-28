#!/usr/bin/env python3
"""
Image fetching module with OpenGraph scraping and fallbacks
"""

import json
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from pathlib import Path

CONFIG_DIR = Path(__file__).parent / 'config'
CACHE_FILE = Path(__file__).parent / 'image_cache.json'
CACHE_EXPIRY_DAYS = 30

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


def fetch_opengraph_image(url, timeout=3):
    """Fetch OpenGraph image from article URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; RSS Reader/1.0)',
            'Accept': 'text/html,application/xhtml+xml'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try various OpenGraph image tags
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
        
        # Try Twitter card image
        twitter_image = soup.find('meta', {'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']
        
        # Try standard meta image
        meta_image = soup.find('meta', {'name': 'image'})
        if meta_image and meta_image.get('content'):
            return meta_image['content']
        
        return None
        
    except Exception as e:
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
    
    Returns: (image_url, cache_updated)
    """
    if cache is None:
        cache = load_image_cache()
    
    # Check cache first
    url_hash = hashlib.md5(article_url.encode()).hexdigest()
    if url_hash in cache:
        return cache[url_hash].get('image_url'), False
    
    # Try OpenGraph scraping
    og_image = fetch_opengraph_image(article_url)
    
    if og_image:
        # Cache successful OpenGraph fetch
        cache[url_hash] = {
            'image_url': og_image,
            'source': 'opengraph',
            'timestamp': datetime.now(timezone.utc).timestamp()
        }
        return og_image, True
    
    # Fall back to source logo
    logo = get_source_logo(source_url)
    if logo:
        cache[url_hash] = {
            'image_url': logo,
            'source': 'favicon',
            'timestamp': datetime.now(timezone.utc).timestamp()
        }
        return logo, True
    
    # No image found
    cache[url_hash] = {
        'image_url': None,
        'source': 'none',
        'timestamp': datetime.now(timezone.utc).timestamp()
    }
    return None, True


def batch_fetch_images(articles, max_fetch=20):
    """
    Fetch images for a batch of articles
    Only fetches OpenGraph for first max_fetch articles to avoid slowdown
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
            image_url, updated = get_article_image(article.link, article.source_url, cache)
            if updated:
                cache_updated = True
            if image_url:
                article.image = image_url
                images_fetched += 1
        else:
            # Just use favicon for remaining articles
            logo = get_source_logo(article.source_url)
            if logo:
                article.image = logo
    
    if cache_updated:
        save_image_cache(cache)
    
    return articles


if __name__ == '__main__':
    # Test the image fetcher
    print("Testing image fetching...")
    
    test_url = "https://arstechnica.com/ai/2025/01/openai-offers-free-chatgpt-pro-to-federal-workers/"
    test_source = "https://arstechnica.com"
    
    image_url, _ = get_article_image(test_url, test_source)
    print(f"Image URL: {image_url}")
