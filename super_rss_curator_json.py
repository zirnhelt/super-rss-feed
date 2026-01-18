#!/usr/bin/env python3
"""
Super RSS Feed Curator with Williams Lake Tribune Priority Integration + Enhanced Images
- Aggregates feeds from OPML with smart caching
- Scrapes Williams Lake Tribune directly for priority local news
- Local news gets maximum priority and 📍 tags
- Outputs JSON Feed format with prominent source attribution
- Includes enhanced image support with conditional scraping for high-scoring articles
"""
import os
import sys
import re
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
import hashlib
import json
from urllib.parse import urljoin, urlparse

import feedparser
from fuzzywuzzy import fuzz
import anthropic
import requests
from bs4 import BeautifulSoup

# Configuration
MAX_ARTICLES_OUTPUT = 250
MAX_PER_SOURCE = 5  # Default limit per source
MAX_PER_LOCAL = 15  # Higher limit for local content
LOOKBACK_HOURS = 48  # How far back to fetch articles
MIN_CLAUDE_SCORE = 30  # Minimum relevance score (0-100)
LOCAL_PRIORITY_SCORE = 100  # Maximum score for local articles

# Image scraping configuration
ENABLE_IMAGE_SCRAPING = True
MIN_SCORE_FOR_SCRAPING = 60  # Only scrape images for articles with score >= 60
MAX_SCRAPE_REQUESTS = 20  # Limit HTTP requests to avoid rate limiting

# Caching configuration
SCORED_CACHE_FILE = 'scored_articles_cache.json'
WLT_CACHE_FILE = 'wlt_cache.json'
CACHE_EXPIRY_HOURS = 6  # Don't re-score articles for 6 hours

# Williams Lake Tribune settings
WLT_BASE_URL = "https://wltribune.com"
WLT_NEWS_URL = f"{WLT_BASE_URL}/news/"

# Filters
BLOCKED_SOURCES = ["fox news", "foxnews"]
BLOCKED_KEYWORDS = [
    # Sports
    "nfl", "nba", "mlb", "nhl", "premier league", "champions league",
    "world cup", "olympics", "super bowl", "playoff", "touchdown",
    "hockey", "football", "soccer", "basketball", "baseball",
    "tournament", "championship", "sports", "athletics",
    "rec centre", "recreation centre", "arena",
    # Advice columns
    "dear abby", "ask amy", "miss manners", "advice column",
    "relationship advice", "dating advice"
]


class Article:
    """Represents a single article"""
    def __init__(self, entry=None, source_title: str = "", source_url: str = "", 
                 title: str = "", link: str = "", description: str = "", 
                 pub_date: datetime = None, is_local: bool = False):
        
        # Handle both RSS entries and manual creation
        if entry:
            self.title = entry.get('title', '').strip()
            self.link = entry.get('link', '').strip()
            self.description = entry.get('description', '') or entry.get('summary', '')
            self.pub_date = self._parse_date(entry)
            self.image_url = self._extract_image(entry)  # Extract image from RSS entry
            self.needs_image_scraping = not bool(self.image_url)
        else:
            self.title = title.strip()
            self.link = link.strip()
            self.description = description.strip()
            self.pub_date = pub_date or datetime.now(timezone.utc)
            self.image_url = None  # Manual articles (WLT scraping) don't have images yet
            self.needs_image_scraping = True
        
        self.source = source_title
        self.source_url = source_url
        self.score = LOCAL_PRIORITY_SCORE if is_local else 0
        self.is_local = is_local
        
        # Generate hash for deduplication and caching
        self.url_hash = hashlib.md5(self.link.encode()).hexdigest()
        self.title_normalized = self.title.lower().strip()
    
    def _parse_date(self, entry) -> datetime:
        """Parse publication date from entry"""
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
        return datetime.now(timezone.utc)
    
    def _extract_image(self, entry) -> Optional[str]:
        """Extract image URL from RSS feed entry"""
        # Check enclosures first (most common)
        if hasattr(entry, 'enclosures') and entry.enclosures:
            for enc in entry.enclosures:
                if hasattr(enc, 'type') and enc.type and enc.type.startswith('image/'):
                    # Basic filter for tiny images (likely tracking pixels)
                    url = enc.href
                    if not self._is_tiny_image(url):
                        return url
        
        # Check media content (Media RSS)
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if media.get('type', '').startswith('image/'):
                    url = media.get('url')
                    if url and not self._is_tiny_image(url):
                        return url
        
        # Parse description for <img> tags as fallback
        if self.description:
            soup = BeautifulSoup(self.description, 'html.parser')
            for img in soup.find_all('img', src=True):
                url = img['src']
                if not self._is_tiny_image(url):
                    return url
        
        return None
    
    def _is_tiny_image(self, url: str) -> bool:
        """Filter out likely tracking pixels and tiny images"""
        tiny_patterns = [
            'pixel', '1x1', 'tracker', 'analytics', 'doubleclick',
            'facebook.com/tr', 'google-analytics', 'googletagmanager'
        ]
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in tiny_patterns)
    
    def _scrape_article_image(self) -> Optional[str]:
        """Scrape article page for Open Graph/Twitter Card images"""
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; RSS-Curator/1.0)"}
            response = requests.get(self.link, headers=headers, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Open Graph image (best option)
            og_image = soup.find("meta", property="og:image")
            if og_image and og_image.get("content"):
                url = og_image["content"]
                if not self._is_tiny_image(url):
                    return url
            
            # Twitter Card image (fallback)
            twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
            if twitter_image and twitter_image.get("content"):
                url = twitter_image["content"]
                if not self._is_tiny_image(url):
                    return url
                
            return None
        except Exception:
            # Fail silently - image scraping is optional
            return None
    
    def should_filter(self) -> bool:
        """Check if article should be filtered out (never filter local content)"""
        if self.is_local:
            return False
            
        text = f"{self.title} {self.description}".lower()
        
        # Check blocked sources
        source_lower = self.source.lower()
        if any(blocked in source_lower for blocked in BLOCKED_SOURCES):
            return True
        
        # Check blocked keywords
        if any(keyword in text for keyword in BLOCKED_KEYWORDS):
            return True
        
        return False


def load_wlt_cache() -> Dict[str, bool]:
    """Load Williams Lake Tribune URL cache to avoid re-scraping"""
    try:
        if os.path.exists(WLT_CACHE_FILE):
            with open(WLT_CACHE_FILE, 'r') as f:
                cache = json.load(f)
                print(f"📁 Loaded WLT cache with {len(cache)} URLs")
                return cache
    except Exception as e:
        print(f"⚠ WLT cache load error: {e}")
    
    return {}


def save_wlt_cache(cache: Dict[str, bool]):
    """Save Williams Lake Tribune URL cache"""
    try:
        with open(WLT_CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"⚠ WLT cache save error: {e}")


def scrape_williams_lake_tribune() -> List[Article]:
    """Scrape fresh Williams Lake Tribune articles with caching"""
    print("🔍️ Scraping Williams Lake Tribune...")
    
    # Load existing cache
    cache = load_wlt_cache()
    articles = []
    
    try:
        # Fetch the news page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(WLT_NEWS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all article links (adjust selectors as needed for their site structure)
        # Look for article links - these are educated guesses for common patterns
        article_links = set()
        
        # Method 1: Look for links containing 2026 (current year articles)
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Skip if not an article URL or if it's 2025 or older
            if '/2026/' in href and ('/news/' in href or '/local/' in href):
                full_url = urljoin(WLT_BASE_URL, href)
                article_links.add(full_url)
        
        # Method 2: Look in common news sections
        news_sections = soup.find_all(['article', 'div'], class_=re.compile(r'(news|article|post)', re.I))
        for section in news_sections:
            for link in section.find_all('a', href=True):
                href = link['href']
                if '/2026/' in href:
                    full_url = urljoin(WLT_BASE_URL, href)
                    article_links.add(full_url)
        
        print(f"  📄 Found {len(article_links)} potential article URLs")
        
        # Filter out cached URLs and process new ones
        new_articles = 0
        for url in article_links:
            if url not in cache:
                # For now, create basic article entries
                # In future, could scrape individual article pages for better metadata
                title = f"Williams Lake Tribune Article"  # Default title
                description = "Local news from Williams Lake Tribune"
                
                # Try to extract a better title from the URL path
                path_parts = urlparse(url).path.split('/')
                if len(path_parts) > 1:
                    # Use the last part of path as title hint, clean it up
                    url_title = path_parts[-1].replace('-', ' ').replace('_', ' ').title()
                    if len(url_title) > 10:  # If we got a reasonable title
                        title = url_title
                
                article = Article(
                    source_title="Williams Lake Tribune",
                    source_url=WLT_BASE_URL,
                    title=title,
                    link=url,
                    description=description,
                    is_local=True
                )
                
                articles.append(article)
                cache[url] = True
                new_articles += 1
        
        # Clean old cache entries (older than 7 days)
        cutoff = (datetime.now() - timedelta(days=7)).timestamp()
        cache_cleaned = {url: True for url in cache.keys() 
                        if any(f'/{year}/' in url for year in ['2026'])}  # Keep 2026 articles
        
        # Save updated cache
        save_wlt_cache(cache_cleaned)
        
        print(f"  📰 Williams Lake Tribune: {new_articles} new articles")
        if len(articles) != new_articles:
            print(f"  📁 Cache: {len(articles) - new_articles} previously seen")
    
    except Exception as e:
        print(f"  ❌ Williams Lake Tribune scraping error: {e}")
    
    return articles


def load_scored_cache() -> Dict[str, Dict]:
    """Load cached article scores to avoid re-scoring"""
    try:
        if os.path.exists(SCORED_CACHE_FILE):
            with open(SCORED_CACHE_FILE, 'r') as f:
                cache = json.load(f)
                print(f"📁 Loaded {len(cache)} articles from cache")
                return cache
    except Exception as e:
        print(f"⚠ Cache load error: {e}")
    
    return {}


def save_scored_cache(cache: Dict[str, Dict]):
    """Save article scores cache"""
    try:
        # Clean old entries (older than 12 hours) to keep cache manageable
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat()
        cleaned_cache = {}
        
        for url_hash, entry in cache.items():
            if entry.get('scored_at', '2020-01-01') > cutoff:
                cleaned_cache[url_hash] = entry
        
        with open(SCORED_CACHE_FILE, 'w') as f:
            json.dump(cleaned_cache, f, indent=2)
            
        removed = len(cache) - len(cleaned_cache)
        if removed > 0:
            print(f"💾 Saved cache with {len(cleaned_cache)} articles (removed {removed} old entries)")
    except Exception as e:
        print(f"⚠ Cache save error: {e}")


def is_cache_entry_valid(cache_entry: Dict) -> bool:
    """Check if cached score is still valid (within CACHE_EXPIRY_HOURS)"""
    try:
        scored_at = datetime.fromisoformat(cache_entry['scored_at'])
        cutoff = datetime.now(timezone.utc) - timedelta(hours=CACHE_EXPIRY_HOURS)
        return scored_at > cutoff
    except:
        return False


def parse_opml(opml_path: str) -> List[Dict[str, str]]:
    """Extract RSS feed URLs from OPML file, excluding Williams Lake Tribune"""
    feeds = []
    tree = ET.parse(opml_path)
    root = tree.getroot()
    
    for outline in root.findall(".//outline[@type='rss']"):
        feed_url = outline.get('xmlUrl')
        feed_title = outline.get('title') or outline.get('text')
        html_url = outline.get('htmlUrl', '')
        
        # Skip Williams Lake Tribune RSS feed to avoid duplicates with scraped content
        if feed_title and "williams lake" in feed_title.lower():
            continue
        
        if feed_url:
            feeds.append({
                'url': feed_url,
                'title': feed_title,
                'html_url': html_url
            })
    
    print(f"📚 Found {len(feeds)} feeds in OPML")
    return feeds


def fetch_feed_articles(feed: Dict[str, str], cutoff_date: datetime) -> List[Article]:
    """Fetch recent articles from a single feed"""
    articles = []
    
    try:
        parsed = feedparser.parse(feed['url'])
        
        for entry in parsed.entries:
            article = Article(entry, feed['title'], feed['html_url'])
            
            # Skip old articles
            if article.pub_date < cutoff_date:
                continue
            
            # Skip filtered content
            if article.should_filter():
                continue
            
            articles.append(article)
        
        if articles:
            print(f"  ✅ {feed['title']}: {len(articles)} articles")
    
    except Exception as e:
        print(f"  ❌ {feed['title']}: {str(e)}")
    
    return articles


def deduplicate_articles(articles: List[Article]) -> List[Article]:
    """Remove duplicate articles using URL and fuzzy title matching"""
    seen_urls = set()
    seen_titles = []
    unique = []
    
    for article in articles:
        # Exact URL match
        if article.url_hash in seen_urls:
            continue
        
        # Fuzzy title match (85% similarity threshold)
        is_duplicate = False
        for seen_title in seen_titles:
            if fuzz.ratio(article.title_normalized, seen_title) > 85:
                is_duplicate = True
                break
        
        if is_duplicate:
            continue
        
        seen_urls.add(article.url_hash)
        seen_titles.append(article.title_normalized)
        unique.append(article)
    
    print(f"🔍 Deduplication: {len(articles)} → {len(unique)} articles")
    return unique


def score_articles_with_claude(articles: List[Article], api_key: str) -> List[Article]:
    """Score articles using Claude API with smart caching"""
    # Load existing cache
    cache = load_scored_cache()
    
    # Separate cached and new articles
    cached_articles = []
    new_articles = []
    
    for article in articles:
        # Skip scoring for local articles - they get maximum priority
        if article.is_local:
            cached_articles.append(article)
            continue
            
        cache_entry = cache.get(article.url_hash)
        if cache_entry and is_cache_entry_valid(cache_entry):
            # Use cached score
            article.score = cache_entry['score']
            cached_articles.append(article)
        else:
            new_articles.append(article)
    
    if cached_articles and new_articles:
        print(f"💡 Cache: {len(cached_articles)} hits, {len(new_articles)} new articles to score")
    elif cached_articles:
        print(f"💡 Cache: All {len(cached_articles)} articles found in cache")
    else:
        print(f"🤖 Scoring {len(new_articles)} articles with Claude...")
    
    # Score new articles if any
    if new_articles:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Your interests for scoring
        interests = """
        - AI/ML infrastructure and telemetry
        - Systems thinking and complex systems
        - Climate tech and sustainability
        - Homelab/self-hosting technology
        - Meshtastic and mesh networking
        - 3D printing (Bambu Lab)
        - Sci-fi worldbuilding
        - Deep technical content over news
        - Canadian content and local news (Williams Lake, Quesnel)
        """
        
        # Batch articles for efficiency (10 at a time)
        batch_size = 10
        
        for i in range(0, len(new_articles), batch_size):
            batch = new_articles[i:i+batch_size]
            
            # Prepare batch for Claude
            article_list = "\n\n".join([
                f"Article {idx}:\nTitle: {a.title}\nSource: {a.source}\nDescription: {a.description[:200]}..."
                for idx, a in enumerate(batch)
            ])
            
            prompt = f"""Score these articles for relevance to my interests on a scale of 0-100.

My interests:
{interests}

Articles to score:
{article_list}

Return ONLY a comma-separated list of scores (one per article), like: 85,42,91,15,73,...
No explanations, just the numbers."""
            
            try:
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=200,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                scores_text = response.content[0].text.strip()
                scores = [int(s.strip()) for s in scores_text.split(',')]
                
                # Apply scores and update cache
                for article, score in zip(batch, scores):
                    article.score = score
                    cache[article.url_hash] = {
                        'score': score,
                        'title': article.title,
                        'scored_at': datetime.now(timezone.utc).isoformat()
                    }
            
            except Exception as e:
                print(f"  ⚠ Scoring error: {e}")
                # Assign default scores on error
                for article in batch:
                    article.score = 50
                    cache[article.url_hash] = {
                        'score': 50,
                        'title': article.title,
                        'scored_at': datetime.now(timezone.utc).isoformat()
                    }
    
    # Save updated cache
    if new_articles:
        save_scored_cache(cache)
    
    # Combine all articles
    all_scored = cached_articles + new_articles
    return all_scored


def enhance_missing_images(articles: List[Article]) -> List[Article]:
    """Conditionally scrape images for high-scoring articles that lack them"""
    if not ENABLE_IMAGE_SCRAPING:
        print("🖼️ Image scraping disabled")
        return articles
    
    # Filter candidates: needs image scraping AND score >= threshold AND not local
    candidates = [
        a for a in articles 
        if (a.needs_image_scraping and 
            a.score >= MIN_SCORE_FOR_SCRAPING and 
            not a.is_local)
    ]
    
    if not candidates:
        print("🖼️ No articles need image enhancement")
        return articles
    
    # Sort by score (highest first) and limit requests
    candidates.sort(key=lambda a: a.score, reverse=True)
    to_scrape = candidates[:MAX_SCRAPE_REQUESTS]
    
    print(f"🖼️ Enhancing images for {len(to_scrape)} high-scoring articles...")
    
    enhanced_count = 0
    for article in to_scrape:
        scraped_image = article._scrape_article_image()
        if scraped_image:
            article.image_url = scraped_image
            article.needs_image_scraping = False
            enhanced_count += 1
            print(f"  ✅ {article.source}: Found image")
    
    print(f"🖼️ Enhanced {enhanced_count}/{len(to_scrape)} articles with images")
    return articles


def apply_diversity_limits(articles: List[Article], max_per_source: int) -> List[Article]:
    """Limit articles per source to ensure diversity, with higher limits for local content"""
    source_counts = defaultdict(int)
    diverse_articles = []
    
    # Sort by local priority first, then by score
    sorted_articles = sorted(articles, key=lambda a: (not a.is_local, -a.score))
    
    for article in sorted_articles:
        # Use higher limit for local content
        limit = MAX_PER_LOCAL if article.is_local else max_per_source
        
        if source_counts[article.source] < limit:
            diverse_articles.append(article)
            source_counts[article.source] += 1
    
    print(f"📊 Diversity filter: {len(articles)} → {len(diverse_articles)} articles")
    return diverse_articles


def generate_json_feed(articles: List[Article], output_path: str):
    """Generate JSON Feed file with prominent source attribution and image support"""
    
    feed_data = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": "Curated Feed",  # Shorter, less prominent title
        "home_page_url": "https://github.com/zirnhelt/super-rss-feed",
        "feed_url": f"https://zirnhelt.github.io/super-rss-feed/{output_path}",
        "description": "AI-curated articles with priority local news from Williams Lake",
        "authors": [{"name": "Erich's AI Curator"}],
        "items": []
    }
    
    for article in articles[:MAX_ARTICLES_OUTPUT]:
        # Create prominent source-first title with local indicator
        local_prefix = "📍 " if article.is_local else ""
        item_title = f"{local_prefix}[{article.source}] {article.title}"
        
        # Rich metadata for better reader display
        item = {
            "id": article.link,
            "url": article.link,
            "title": item_title,  # Source-prominent title with local indicator
            "content_html": f"<p>{article.description}</p>",
            "summary": article.description,
            "date_published": article.pub_date.isoformat(),
            "authors": [{"name": article.source}],
            "tags": [article.source.lower().replace(" ", "_")],
            "_source": {  # Custom metadata for your use
                "original_title": article.title,
                "source_name": article.source,
                "source_url": article.source_url,
                "ai_score": article.score,
                "relevance": "local" if article.is_local else ("high" if article.score >= 70 else "medium"),
                "is_local": article.is_local
            }
        }
        
        # Add image if available (JSON Feed 1.1 supports image field)
        if article.image_url:
            item["image"] = article.image_url
        
        # Add external URL reference (some readers show this prominently)
        if article.source_url:
            item["external_url"] = article.source_url
            
        feed_data["items"].append(item)
    
    # Write JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(feed_data, f, indent=2, ensure_ascii=False)
    
    # Enhanced statistics with image coverage
    articles_with_images = sum(1 for a in articles[:MAX_ARTICLES_OUTPUT] if a.image_url)
    image_percentage = (articles_with_images / len(articles[:MAX_ARTICLES_OUTPUT])) * 100 if articles else 0
    
    print(f"✅ Generated JSON Feed: {output_path} ({len(articles[:MAX_ARTICLES_OUTPUT])} articles)")
    print(f"🖼️ Images: {articles_with_images}/{len(articles[:MAX_ARTICLES_OUTPUT])} ({image_percentage:.1f}%)")


def main():
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    # Parse OPML (excludes Williams Lake Tribune RSS to avoid duplicates)
    opml_path = sys.argv[1] if len(sys.argv) > 1 else 'feeds.opml'
    feeds = parse_opml(opml_path)
    
    # Scrape Williams Lake Tribune directly for priority local news
    local_articles = scrape_williams_lake_tribune()
    
    # Fetch RSS feed articles
    cutoff_date = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    print(f"\n🔥 Fetching articles from last {LOOKBACK_HOURS} hours...")
    
    rss_articles = []
    for feed in feeds:
        articles = fetch_feed_articles(feed, cutoff_date)
        rss_articles.extend(articles)
    
    # Combine local and RSS articles
    all_articles = local_articles + rss_articles
    print(f"\n📈 Total fetched: {len(all_articles)} articles ({len(local_articles)} local + {len(rss_articles)} RSS)")
    
    # Deduplicate
    unique_articles = deduplicate_articles(all_articles)
    
    # Score with Claude (using smart caching)
    scored_articles = score_articles_with_claude(unique_articles, api_key)
    
    # Enhance missing images for high-scoring articles
    enhanced_articles = enhance_missing_images(scored_articles)
    
    # Filter by minimum score (but always keep local articles)
    quality_articles = [a for a in enhanced_articles if a.score >= MIN_CLAUDE_SCORE or a.is_local]
    non_local_filtered = len([a for a in enhanced_articles if not a.is_local and a.score < MIN_CLAUDE_SCORE])
    if non_local_filtered > 0:
        print(f"⭐ Quality filter (score >= {MIN_CLAUDE_SCORE}): {len(enhanced_articles)} → {len(quality_articles)} articles ({non_local_filtered} filtered)")
    
    # Apply diversity limits
    diverse_articles = apply_diversity_limits(quality_articles, MAX_PER_SOURCE)
    
    # Generate JSON feed
    output_path = 'super-feed.json'
    generate_json_feed(diverse_articles, output_path)
    
    # Stats
    print("\n📊 Final stats:")
    print(f"  Total sources: {len(feeds) + 1}")  # +1 for Williams Lake Tribune
    print(f"  Articles fetched: {len(all_articles)}")
    print(f"  After dedup: {len(unique_articles)}")
    print(f"  After scoring: {len(quality_articles)}")
    print(f"  Final output: {min(len(diverse_articles), MAX_ARTICLES_OUTPUT)}")
    
    # Local content stats
    local_count = sum(1 for a in diverse_articles[:MAX_ARTICLES_OUTPUT] if a.is_local)
    print(f"  📍 Local articles: {local_count}")


if __name__ == '__main__':
    main()
