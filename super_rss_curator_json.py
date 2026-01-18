#!/usr/bin/env python3
"""
Super RSS Feed Curator with Williams Lake Tribune Priority Integration
- Aggregates feeds from OPML with smart caching
- Scrapes Williams Lake Tribune directly for priority local news
- Local news gets maximum priority and 📍 tags
- Outputs JSON Feed format with prominent source attribution
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
        else:
            self.title = title.strip()
            self.link = link.strip()
            self.description = description.strip()
            self.pub_date = pub_date or datetime.now(timezone.utc)
        
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
        with open(WLT_CACHE_FILE, 'r') as f:
            cache = json.load(f)
            print(f"📁 Loaded WLT cache with {len(cache)} URLs")
            return cache
    except FileNotFoundError:
        print("📁 No WLT cache found, starting fresh")
        return {}
    except Exception as e:
        print(f"⚠ WLT cache load error: {e}")
        return {}


def save_wlt_cache(cache: Dict[str, bool]):
    """Save Williams Lake Tribune URL cache"""
    try:
        with open(WLT_CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
        print(f"💾 Saved WLT cache with {len(cache)} URLs")
    except Exception as e:
        print(f"⚠ WLT cache save error: {e}")


def scrape_williams_lake_tribune() -> List[Article]:
    """Scrape Williams Lake Tribune directly for priority local news"""
    print("🏔️ Scraping Williams Lake Tribune...")
    
    # Load cache
    url_cache = load_wlt_cache()
    articles = []
    new_urls = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(WLT_NEWS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for article links (adjust selectors based on site structure)
        article_links = soup.find_all('a', href=True)
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
        
        for link in article_links:
            href = link.get('href', '')
            
            # Skip non-article URLs
            if not href or href.startswith('#') or 'javascript:' in href:
                continue
                
            # Convert relative URLs to absolute
            if href.startswith('/'):
                full_url = urljoin(WLT_BASE_URL, href)
            elif href.startswith('http'):
                full_url = href
            else:
                continue
            
            # Only include wltribune.com articles from 2026
            if 'wltribune.com' not in full_url or '/2026/' not in full_url:
                continue
                
            # Skip if we've seen this URL before
            if full_url in url_cache:
                continue
            
            # Extract title from link text or try to scrape article
            title = link.get_text().strip()
            if not title or len(title) < 10:  # Skip short/empty titles
                continue
                
            # Create article with maximum priority
            article = Article(
                title=title,
                link=full_url,
                description=f"Local news from Williams Lake Tribune",
                pub_date=datetime.now(timezone.utc),  # Use current time for fresh articles
                source_title="Williams Lake Tribune",
                source_url=WLT_BASE_URL,
                is_local=True
            )
            
            articles.append(article)
            new_urls.append(full_url)
            
            # Add to cache
            url_cache[full_url] = True
            
            # Limit scraping to avoid overload
            if len(articles) >= 20:
                break
        
        # Save updated cache
        if new_urls:
            save_wlt_cache(url_cache)
            
        print(f"  📰 Williams Lake Tribune: {len(articles)} new articles")
        
    except Exception as e:
        print(f"  ❌ Williams Lake Tribune scraping error: {e}")
    
    return articles


def load_scored_cache() -> Dict[str, Dict]:
    """Load previously scored articles from cache"""
    try:
        with open(SCORED_CACHE_FILE, 'r') as f:
            cache = json.load(f)
            print(f"📁 Loaded {len(cache)} articles from scoring cache")
            return cache
    except FileNotFoundError:
        print("📁 No scoring cache found, starting fresh")
        return {}
    except Exception as e:
        print(f"⚠ Scoring cache load error: {e}, starting fresh")
        return {}


def save_scored_cache(cache: Dict[str, Dict]):
    """Save scored articles to cache"""
    try:
        # Clean old entries while saving
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=CACHE_EXPIRY_HOURS * 2)
        cleaned_cache = {
            url_hash: data for url_hash, data in cache.items()
            if datetime.fromisoformat(data['scored_at']) > cutoff_time
        }
        
        with open(SCORED_CACHE_FILE, 'w') as f:
            json.dump(cleaned_cache, f, indent=2)
        
        removed = len(cache) - len(cleaned_cache)
        print(f"💾 Saved scoring cache with {len(cleaned_cache)} articles" + 
              (f" (removed {removed} old entries)" if removed > 0 else ""))
    except Exception as e:
        print(f"⚠ Scoring cache save error: {e}")


def is_cache_entry_valid(cache_entry: Dict) -> bool:
    """Check if cached score is still valid (not expired)"""
    try:
        scored_time = datetime.fromisoformat(cache_entry['scored_at'])
        expiry_time = scored_time + timedelta(hours=CACHE_EXPIRY_HOURS)
        return datetime.now(timezone.utc) < expiry_time
    except:
        return False


def parse_opml(opml_path: str) -> List[Dict[str, str]]:
    """Extract RSS feed URLs from OPML file"""
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
            print(f"  ✓ {feed['title']}: {len(articles)} articles")
    
    except Exception as e:
        print(f"  ✗ {feed['title']}: {str(e)}")
    
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
    """Score articles using Claude API with smart caching (skip local articles)"""
    
    # Separate local articles (already have max score) from others
    local_articles = [a for a in articles if a.is_local]
    non_local_articles = [a for a in articles if not a.is_local]
    
    if local_articles:
        print(f"🏔️ Local articles: {len(local_articles)} (auto-scored at {LOCAL_PRIORITY_SCORE})")
    
    if not non_local_articles:
        print("📍 Only local articles found, skipping Claude scoring")
        return articles
    
    # Load cache
    cache = load_scored_cache()
    
    # Separate cached vs new articles
    cached_articles = []
    new_articles = []
    cache_hits = 0
    
    for article in non_local_articles:
        cache_entry = cache.get(article.url_hash)
        if cache_entry and is_cache_entry_valid(cache_entry):
            # Use cached score
            article.score = cache_entry['score']
            cached_articles.append(article)
            cache_hits += 1
        else:
            # Need to score this one
            new_articles.append(article)
    
    print(f"💡 Cache: {cache_hits} hits, {len(new_articles)} new articles to score")
    
    # Only score new articles if there are any
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
        
        print(f"🤖 Scoring {len(new_articles)} new articles with Claude...")
        
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
                current_time = datetime.now(timezone.utc).isoformat()
                for article, score in zip(batch, scores):
                    article.score = score
                    # Update cache
                    cache[article.url_hash] = {
                        'score': score,
                        'title': article.title,
                        'source': article.source,
                        'scored_at': current_time
                    }
            
            except Exception as e:
                print(f"  ⚠ Scoring error: {e}")
                # Assign default scores on error
                for article in batch:
                    article.score = 50
    
    # Save updated cache
    if new_articles:
        save_scored_cache(cache)
    
    # Return all articles (local + cached + newly scored)
    all_articles = local_articles + cached_articles + new_articles
    return all_articles


def apply_diversity_limits(articles: List[Article], max_per_source: int) -> List[Article]:
    """Limit articles per source to ensure diversity (higher limit for local)"""
    source_counts = defaultdict(int)
    diverse_articles = []
    
    # Sort by score first (local articles will be at top with score 100)
    sorted_articles = sorted(articles, key=lambda a: a.score, reverse=True)
    
    for article in sorted_articles:
        # Use higher limit for local content
        limit = MAX_PER_LOCAL if article.is_local else max_per_source
        
        if source_counts[article.source] < limit:
            diverse_articles.append(article)
            source_counts[article.source] += 1
    
    print(f"📊 Diversity filter: {len(articles)} → {len(diverse_articles)} articles")
    return diverse_articles


def generate_json_feed(articles: List[Article], output_path: str):
    """Generate JSON Feed file with prominent source attribution and local priority"""
    
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
        
        # Add external URL reference (some readers show this prominently)
        if article.source_url:
            item["external_url"] = article.source_url
            
        feed_data["items"].append(item)
    
    # Write JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(feed_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated JSON Feed: {output_path} ({len(articles[:MAX_ARTICLES_OUTPUT])} articles)")


def main():
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("⌛ Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    # Parse OPML
    opml_path = sys.argv[1] if len(sys.argv) > 1 else 'feeds.opml'
    feeds = parse_opml(opml_path)
    
    # Step 1: Scrape Williams Lake Tribune for priority local news
    local_articles = scrape_williams_lake_tribune()
    
    # Step 2: Fetch articles from OPML feeds
    cutoff_date = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    print(f"\n🔥 Fetching articles from last {LOOKBACK_HOURS} hours...")
    
    rss_articles = []
    for feed in feeds:
        # Skip Williams Lake Tribune RSS if we're scraping it directly
        if 'wltribune' in feed['url'].lower():
            print(f"  ⏭️ {feed['title']}: Skipped (using direct scraper)")
            continue
            
        articles = fetch_feed_articles(feed, cutoff_date)
        rss_articles.extend(articles)
    
    # Combine local and RSS articles
    all_articles = local_articles + rss_articles
    print(f"\n📈 Total fetched: {len(all_articles)} articles ({len(local_articles)} local + {len(rss_articles)} RSS)")
    
    # Deduplicate
    unique_articles = deduplicate_articles(all_articles)
    
    # Score with Claude (local articles already have max scores)
    scored_articles = score_articles_with_claude(unique_articles, api_key)
    
    # Filter by minimum score (but always include local)
    quality_articles = [a for a in scored_articles if a.score >= MIN_CLAUDE_SCORE or a.is_local]
    print(f"⭐ Quality filter (score >= {MIN_CLAUDE_SCORE}): {len(scored_articles)} → {len(quality_articles)} articles")
    
    # Apply diversity limits
    diverse_articles = apply_diversity_limits(quality_articles, MAX_PER_SOURCE)
    
    # Generate JSON feed
    output_path = 'super-feed.json'
    generate_json_feed(diverse_articles, output_path)
    
    # Stats
    local_count = sum(1 for a in diverse_articles if a.is_local)
    print("\n📊 Final stats:")
    print(f"  Total sources: {len(feeds) + 1}")  # +1 for WLT scraper
    print(f"  Articles fetched: {len(all_articles)}")
    print(f"  After dedup: {len(unique_articles)}")
    print(f"  After scoring: {len(quality_articles)}")
    print(f"  Final output: {min(len(diverse_articles), MAX_ARTICLES_OUTPUT)} ({local_count} local)")


if __name__ == '__main__':
    main()
