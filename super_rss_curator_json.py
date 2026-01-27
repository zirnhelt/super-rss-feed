#!/usr/bin/env python3
"""
Super RSS Feed Curator with Category Feeds (Config-driven version)
- All configuration loaded from config/ directory
- Loads existing feed and merges with new articles
- Ages out articles older than FEED_RETENTION_DAYS
- Uses shown_cache to prevent re-scoring and re-adding aged-out articles
- Outputs JSON Feed format with prominent source attribution and image support
- Williams Lake Tribune gets priority treatment with direct scraping
- Generates separate category feeds
- Uses Claude for both scoring AND categorization in one API call
"""
import os
import sys
import re
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import List, Dict, Optional
import hashlib
import json
from urllib.parse import urljoin, urlparse

import feedparser
from fuzzywuzzy import fuzz
import anthropic
import requests
from bs4 import BeautifulSoup

from config_loader import *

# Load configuration from config/ directory
CONFIG = get_all_config()

# Extract commonly used config values
SYSTEM = CONFIG['system']
LIMITS = CONFIG['limits']
FILTERS = CONFIG['filters']
CATEGORIES = CONFIG['categories']
FEEDS = CONFIG['feeds']
SCORING_INTERESTS = CONFIG['scoring_interests']

# Configuration from config files
MAX_FEED_SIZE = LIMITS['max_feed_size']
FEED_RETENTION_DAYS = LIMITS['feed_retention_days']
MAX_PER_SOURCE = LIMITS['max_per_source']
MAX_PER_LOCAL = LIMITS['max_per_local']
MIN_CLAUDE_SCORE = LIMITS['min_claude_score']
LOCAL_PRIORITY_SCORE = LIMITS['local_priority_score']

# Cache configuration
SCORED_CACHE_FILE = SYSTEM['cache_files']['scored_articles']
WLT_CACHE_FILE = SYSTEM['cache_files']['wlt']
SHOWN_CACHE_FILE = SYSTEM['cache_files']['shown_articles']
CACHE_EXPIRY_HOURS = SYSTEM['cache_expiry']['scored_hours']
SHOWN_CACHE_DAYS = SYSTEM['cache_expiry']['shown_days']

# URLs
WLT_BASE_URL = SYSTEM['urls']['wlt_base']
WLT_NEWS_URL = SYSTEM['urls']['wlt_news']

# System settings
LOOKBACK_HOURS = SYSTEM['lookback_hours']

class Article:
    """Represents a single RSS article with metadata"""
    def __init__(self, entry, source_title: str, source_url: str):
        self.title = entry.get('title', '').strip()
        self.link = entry.get('link', '').strip()
        self.description = entry.get('description', '') or entry.get('summary', '')
        self.pub_date = self._parse_date(entry)
        self.source = source_title
        self.source_url = source_url
        self.score = 0
        self.category = "news"  # Default category
        
        # Generate unique identifiers for deduplication
        self.url_hash = hashlib.md5(self.link.encode()).hexdigest()
        self.title_normalized = self.title.lower().strip()
        
        # Check if this is local content
        self.is_local = self._is_local_content()
        
        # Set priority scoring for local content
        if self.is_local:
            self.score = LOCAL_PRIORITY_SCORE
            self.category = "local"
    
    def _parse_date(self, entry) -> datetime:
        """Parse publication date from entry"""
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            return datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
        return datetime.now(timezone.utc)
    
    def _is_local_content(self) -> bool:
        """Check if article is from Williams Lake Tribune or local sources"""
        local_indicators = [
            'williams lake', 'wltribune', 'tribune',
            'cariboo', 'quesnel', '100 mile house',
            'fraser valley', 'bc interior'
        ]
        
        text_to_check = f"{self.source} {self.title} {self.link}".lower()
        return any(indicator in text_to_check for indicator in local_indicators)
    
    def should_filter(self) -> bool:
        """Check if article should be filtered out based on configured filters"""
        text = f"{self.title} {self.description}".lower()
        
        # Check blocked sources
        source_lower = self.source.lower()
        if any(blocked in source_lower for blocked in FILTERS['blocked_sources']):
            return True
        
        # Check blocked keywords
        if any(keyword in text for keyword in FILTERS['blocked_keywords']):
            return True
        
        return False

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

def fetch_feed_articles(feed: Dict[str, str], cutoff_date: datetime) -> List[Article]:
    """Fetch recent articles from a single feed with proper browser headers"""
    articles = []
    
    try:
        # Full browser headers to avoid blocking
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        response = requests.get(feed['url'], headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        # Parse the response content with feedparser
        parsed = feedparser.parse(response.content)
        
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
    
    except requests.exceptions.Timeout:
        print(f"  ⚠️ {feed['title']}: Connection timeout (15s)")
    except requests.exceptions.ConnectionError:
        print(f"  ⚠️ {feed['title']}: Connection failed")
    except requests.exceptions.HTTPError as e:
        print(f"  ⚠️ {feed['title']}: HTTP {e.response.status_code}")
    except Exception as e:
        print(f"  ✗ {feed['title']}: {str(e)}")
    
    return articles

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

def scrape_williams_lake_tribune() -> List[Article]:
    """Scrape Williams Lake Tribune directly for comprehensive local coverage"""
    articles = []
    
    try:
        print("🏔️ Scraping Williams Lake Tribune directly...")
        
        # Load cached articles to avoid re-processing
        cache = load_wlt_cache()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(WLT_NEWS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find article links (adjust selector based on site structure)
        article_links = soup.find_all('a', href=True)
        
        cutoff_date = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
        new_articles = 0
        
        for link in article_links:
            href = link.get('href', '')
            if not href.startswith('/') or 'news' not in href:
                continue
            
            full_url = urljoin(WLT_BASE_URL, href)
            
            # Skip if already processed recently
            if full_url in cache and cache[full_url].get('scraped_at'):
                scraped_at = datetime.fromisoformat(cache[full_url]['scraped_at'])
                if scraped_at > cutoff_date:
                    continue
            
            # Create article object
            title = link.get_text(strip=True)
            if len(title) < 10:  # Skip short/invalid titles
                continue
            
            # Create a mock entry for Article constructor
            mock_entry = {
                'title': title,
                'link': full_url,
                'description': '',
                'published_parsed': None
            }
            
            article = Article(mock_entry, "Williams Lake Tribune", WLT_BASE_URL)
            article.is_local = True
            article.score = LOCAL_PRIORITY_SCORE
            article.category = "local"
            
            articles.append(article)
            new_articles += 1
            
            # Update cache
            cache[full_url] = {
                'title': title,
                'scraped_at': datetime.now(timezone.utc).isoformat()
            }
        
        # Save updated cache
        save_wlt_cache(cache)
        
        print(f"  ✓ Williams Lake Tribune: {new_articles} new articles")
        
    except Exception as e:
        print(f"  ✗ Williams Lake Tribune scraping error: {e}")
    
    return articles

def load_scored_cache() -> Dict[str, Dict]:
    """Load cached article scores to avoid re-scoring"""
    try:
        if os.path.exists(SCORED_CACHE_FILE):
            with open(SCORED_CACHE_FILE, 'r') as f:
                cache = json.load(f)
                
                # Clean expired entries
                cutoff = datetime.now(timezone.utc) - timedelta(hours=CACHE_EXPIRY_HOURS)
                cleaned_cache = {}
                
                for key, entry in cache.items():
                    try:
                        scored_at = datetime.fromisoformat(entry['scored_at'])
                        if scored_at > cutoff:
                            cleaned_cache[key] = entry
                    except:
                        continue
                
                if len(cleaned_cache) != len(cache):
                    save_scored_cache(cleaned_cache)
                
                return cleaned_cache
    except Exception as e:
        print(f"⚠️ Scoring cache load error: {e}")
    
    return {}

def save_scored_cache(cache: Dict[str, Dict]):
    """Save article scores cache"""
    try:
        # Clean old entries (older than 12 hours) to keep cache manageable
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat()
        cleaned_cache = {}
        
        for key, entry in cache.items():
            if entry.get('scored_at', '') > cutoff:
                cleaned_cache[key] = entry
        
        with open(SCORED_CACHE_FILE, 'w') as f:
            json.dump(cleaned_cache, f, indent=2)
            
    except Exception as e:
        print(f"⚠️ Cache save error: {e}")

def load_wlt_cache() -> Dict[str, Dict]:
    """Load Williams Lake Tribune scraping cache"""
    try:
        if os.path.exists(WLT_CACHE_FILE):
            with open(WLT_CACHE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️ WLT cache load error: {e}")
    return {}

def save_wlt_cache(cache: Dict[str, Dict]):
    """Save Williams Lake Tribune scraping cache"""
    try:
        with open(WLT_CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"⚠️ WLT cache save error: {e}")

def load_shown_cache() -> set:
    """Load cache of articles that have been shown in feeds"""
    try:
        if os.path.exists(SHOWN_CACHE_FILE):
            with open(SHOWN_CACHE_FILE, 'r') as f:
                data = json.load(f)
                
                # Clean old entries
                cutoff = datetime.now(timezone.utc) - timedelta(days=SHOWN_CACHE_DAYS)
                cutoff_str = cutoff.isoformat()
                
                cleaned = {url_hash: shown_at for url_hash, shown_at in data.items() 
                          if shown_at > cutoff_str}
                
                if len(cleaned) != len(data):
                    save_shown_cache(cleaned)
                
                return set(cleaned.keys())
    except Exception as e:
        print(f"⚠️ Shown cache load error: {e}")
    
    return set()

def save_shown_cache(cache):
    """Save cache of shown articles"""
    try:
        if isinstance(cache, set):
            # Convert set to dict with timestamps
            cache_dict = {url_hash: datetime.now(timezone.utc).isoformat() 
                         for url_hash in cache}
        else:
            cache_dict = cache
            
        with open(SHOWN_CACHE_FILE, 'w') as f:
            json.dump(cache_dict, f, indent=2)
    except Exception as e:
        print(f"⚠️ Shown cache save error: {e}")

def is_cache_entry_valid(cache_entry: Dict) -> bool:
    """Check if cached score is still valid (within CACHE_EXPIRY_HOURS)"""
    try:
        scored_at = datetime.fromisoformat(cache_entry['scored_at'])
        cutoff = datetime.now(timezone.utc) - timedelta(hours=CACHE_EXPIRY_HOURS)
        return scored_at > cutoff
    except:
        return False

def deduplicate_articles(articles: List[Article], shown_cache: set) -> List[Article]:
    """Remove duplicate articles using URL and fuzzy title matching, plus shown cache"""
    seen_urls = set()
    seen_titles = []
    unique = []
    
    for article in articles:
        # Skip if already shown recently
        if article.url_hash in shown_cache:
            continue
            
        # Exact URL match
        if article.url_hash in seen_urls:
            continue
        
        # Fuzzy title match (75% similarity threshold for better precision)
        is_duplicate = False
        for seen_title in seen_titles:
            if fuzz.ratio(article.title_normalized, seen_title) > 75:
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
    """Score and categorize articles using Claude API with smart caching"""
    # Load existing cache
    cache = load_scored_cache()
    
    # Separate cached and new articles
    cached_articles = []
    new_articles = []
    
    for article in articles:
        # Skip scoring for local articles - they get maximum priority
        if article.is_local:
            article.category = "local"
            cached_articles.append(article)
            continue
            
        cache_entry = cache.get(article.url_hash)
        if cache_entry and is_cache_entry_valid(cache_entry):
            # Use cached score and category
            article.score = cache_entry['score']
            article.category = cache_entry.get('category', 'news')  # Fallback for old cache entries
            cached_articles.append(article)
        else:
            new_articles.append(article)
    
    if cached_articles and new_articles:
        print(f"💡 Cache: {len(cached_articles)} hits, {len(new_articles)} new articles to score")
    elif cached_articles:
        print(f"💡 Cache: All {len(cached_articles)} articles found in cache")
    else:
        print(f"🤖 Scoring {len(new_articles)} articles with Claude...")
    
    # Score and categorize new articles if any
    if new_articles:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Use scoring interests from config
        interests = SCORING_INTERESTS
        
        # Build category descriptions for Claude
        category_descriptions = []
        for cat_key, cat_data in CATEGORIES.items():
            category_descriptions.append(f"- {cat_key}: {cat_data['description']}")
        
        categories_text = "\n".join(category_descriptions)
        
        # Batch articles for efficiency (6 at a time for more complex prompt)
        batch_size = 6
        
        for i in range(0, len(new_articles), batch_size):
            batch = new_articles[i:i+batch_size]
            
            # Prepare batch for Claude
            article_list = "\n\n".join([
                f"Article {idx}:\nTitle: {a.title}\nSource: {a.source}\nDescription: {a.description[:200]}..."
                for idx, a in enumerate(batch)
            ])
            
            prompt = f"""Score and categorize these articles for relevance to my interests.

MY INTERESTS:
{interests}

AVAILABLE CATEGORIES:
{categories_text}

ARTICLES TO EVALUATE:
{article_list}

Return ONLY comma-separated pairs of score,category (one per article), like:
85,ai-tech
42,news
91,homelab
15,news
73,climate

Rules:
- Score 0-100 based on relevance to my interests
- Williams Lake/Cariboo content should be "local" and score 80+
- Use category key names (ai-tech, homelab, climate, science, scifi, local, news)
- Default to "news" for general content that doesn't fit other categories"""
            
            try:
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=300,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                scores_text = response.content[0].text.strip()
                
                # Parse score,category pairs
                pairs = []
                lines = scores_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if ',' in line:
                        try:
                            parts = line.split(',', 1)
                            score = int(parts[0].strip())
                            category = parts[1].strip()
                            
                            # Validate category exists
                            if category not in CATEGORIES:
                                print(f"  ⚠️ Invalid category '{category}', defaulting to 'news'")
                                category = 'news'
                            
                            pairs.append((score, category))
                        except ValueError:
                            print(f"  ⚠️ Invalid format: {line}, defaulting to (50, 'news')")
                            pairs.append((50, 'news'))
                
                # Ensure we have enough pairs for the batch
                while len(pairs) < len(batch):
                    pairs.append((50, 'news'))
                
                # Apply scores and categories, update cache
                for article, (score, category) in zip(batch, pairs):
                    article.score = score
                    article.category = category
                    cache[article.url_hash] = {
                        'score': score,
                        'category': category,
                        'title': article.title,
                        'source': article.source,
                        'scored_at': datetime.now(timezone.utc).isoformat()
                    }
                
                print(f"  ✅ Processed batch {i//batch_size + 1}: {len(pairs)} articles scored and categorized")
                
            except Exception as e:
                print(f"  ⚠️ Scoring error: {e}")
                # Assign default scores and categories on error
                for article in batch:
                    article.score = 50
                    article.category = 'news'
                    cache[article.url_hash] = {
                        'score': 50,
                        'category': 'news',
                        'title': article.title,
                        'source': article.source,
                        'scored_at': datetime.now(timezone.utc).isoformat()
                    }
    
    # Save updated cache
    if new_articles:
        save_scored_cache(cache)
    
    # Combine all articles
    all_scored = cached_articles + new_articles
    return all_scored

def apply_diversity_limits(articles: List[Article], max_per_source: int = None) -> List[Article]:
    """Limit articles per source to ensure diversity, with higher limits for local content"""
    if max_per_source is None:
        max_per_source = MAX_PER_SOURCE
        
    source_counts = defaultdict(int)
    diverse_articles = []
    
    # Sort by score first (highest scores get priority)
    sorted_articles = sorted(articles, key=lambda a: a.score, reverse=True)
    
    for article in sorted_articles:
        # Local sources get higher limits
        limit = MAX_PER_LOCAL if article.is_local else max_per_source
        
        if source_counts[article.source] < limit:
            diverse_articles.append(article)
            source_counts[article.source] += 1
    
    print(f"📊 Diversity filter: {len(articles)} → {len(diverse_articles)} articles")
    return diverse_articles

def load_existing_feed(filename: str) -> List[Article]:
    """Load existing articles from JSON feed file"""
    if not os.path.exists(filename):
        return []
    
    try:
        with open(filename, 'r') as f:
            feed_data = json.load(f)
        
        articles = []
        for item in feed_data.get('items', []):
            # Create Article object from JSON data
            mock_entry = {
                'title': item.get('title', ''),
                'link': item.get('url', ''),
                'description': item.get('summary', ''),
                'published_parsed': None
            }
            
            article = Article(mock_entry, 
                           item.get('authors', [{}])[0].get('name', 'Unknown'),
                           item.get('url', ''))
            
            # Restore metadata
            article.score = item.get('_score', 0)
            if item.get('date_published'):
                article.pub_date = datetime.fromisoformat(item['date_published'].replace('Z', '+00:00'))
            
            articles.append(article)
        
        return articles
        
    except Exception as e:
        print(f"  ⚠️ Error loading {filename}: {e}")
        return []

def merge_and_age_articles(existing: List[Article], new: List[Article], retention_days: int) -> List[Article]:
    """Merge existing and new articles, removing old ones"""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
    
    # Filter existing articles by age
    fresh_existing = [a for a in existing if a.pub_date > cutoff_date]
    
    # Create lookup for deduplication
    existing_urls = {a.url_hash for a in fresh_existing}
    
    # Add new articles that aren't duplicates
    unique_new = [a for a in new if a.url_hash not in existing_urls]
    
    merged = fresh_existing + unique_new
    
    if len(existing) != len(fresh_existing):
        aged_count = len(existing) - len(fresh_existing)
        print(f"  🗓️ Aged out {aged_count} old articles")
    
    return merged

def generate_json_feed(articles: List[Article], feed_config: Dict, category_key: str) -> Dict:
    """Generate JSON Feed format output"""
    feed_info = FEEDS['feeds'].get(category_key, {
        'title': f"Category: {category_key}",
        'description': f"Articles in {category_key} category"
    })
    
    base_url = FEEDS['base_url']
    
    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": feed_info['title'],
        "home_page_url": base_url,
        "feed_url": f"{base_url}/feed-{category_key}.json",
        "description": feed_info['description'],
        "author": {"name": FEEDS['author']},
        "items": []
    }
    
    for article in articles[:MAX_FEED_SIZE]:
        # Determine content type and format description
        content_html = f"<p>{article.description}</p>" if article.description else ""
        
        # Add source attribution
        source_attribution = f"<p><small><strong>Source:</strong> {article.source}"
        if article.source_url:
            source_attribution += f" | <a href='{article.source_url}'>Visit {article.source}</a>"
        source_attribution += f" | <strong>AI Score:</strong> {article.score}</small></p>"
        
        content_html += source_attribution
        
        item = {
            "id": article.url_hash,
            "url": article.link,
            "title": article.title,
            "content_html": content_html,
            "summary": article.description[:200] + "..." if len(article.description) > 200 else article.description,
            "date_published": article.pub_date.isoformat(),
            "authors": [{"name": article.source}],
            "_score": article.score,  # Custom field for debugging
            "_local": article.is_local  # Custom field for local content identification
        }
        
        feed["items"].append(item)
    
    return feed

def save_json_feed(feed_data: Dict, filename: str):
    """Save JSON feed to file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(feed_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"  ❌ Error saving {filename}: {e}")

def generate_master_opml(categories: Dict) -> str:
    """Generate OPML file for all category feeds"""
    base_url = FEEDS['base_url']
    
    opml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<opml version="1.0">',
        '<head>',
        '<title>Erich\'s Curated Feeds</title>',
        f'<dateCreated>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")}</dateCreated>',
        '</head>',
        '<body>'
    ]
    
    for category_key, category_data in categories.items():
        emoji = category_data.get('emoji', '📰')
        name = category_data.get('name', category_key.title())
        
        opml_lines.append(f'    <outline type="rss" text="{emoji} {name}" title="{emoji} {name}" xmlUrl="{base_url}/feed-{category_key}.json" htmlUrl="{base_url}" />')
    
    opml_lines.extend(['</body>', '</opml>'])
    
    return '\n'.join(opml_lines)

def main():
    """Main RSS curation workflow with category-specific feeds"""
    print("🎯 Starting Super RSS Feed generation...")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    # Parse OPML
    opml_path = sys.argv[1] if len(sys.argv) > 1 else 'feeds.opml'
    if not os.path.exists(opml_path):
        print(f"❌ Error: OPML file '{opml_path}' not found")
        sys.exit(1)
    
    feeds = parse_opml(opml_path)
    
    # Load caches
    shown_cache = load_shown_cache()
    
    print(f"💾 Loaded shown articles cache: {len(shown_cache)} entries")
    
    # Fetch articles from all feeds
    cutoff_date = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    print(f"\n📥 Fetching articles from last {LOOKBACK_HOURS} hours...")
    
    all_new_articles = []
    
    # Fetch from OPML feeds
    for feed in feeds:
        articles = fetch_feed_articles(feed, cutoff_date)
        all_new_articles.extend(articles)
    
    # Add Williams Lake Tribune articles
    wlt_articles = scrape_williams_lake_tribune()
    all_new_articles.extend(wlt_articles)
    
    print(f"\n📈 Total fetched: {len(all_new_articles)} articles")
    
    # Deduplicate against shown cache and internal duplicates
    unique_new = deduplicate_articles(all_new_articles, shown_cache)
    
    # Score and categorize new articles with Claude
    scored_new = score_articles_with_claude(unique_new, api_key)
    
    # Filter by minimum score (but keep all local articles regardless of score)
    quality_new = [a for a in scored_new if a.score >= MIN_CLAUDE_SCORE or a.is_local]
    non_local_filtered = len([a for a in scored_new if not a.is_local and a.score < MIN_CLAUDE_SCORE])
    
    if non_local_filtered > 0:
        print(f"⭐ Quality filter (score >= {MIN_CLAUDE_SCORE}): {len(scored_new)} → {len(quality_new)} articles ({non_local_filtered} filtered)")
    
    # CATEGORIZE all quality new articles (now done by Claude in scoring function)
    print("\n📂 Categorizing new articles...")
    categorized_new = defaultdict(list)
    for article in quality_new:
        category = article.category  # Already set by Claude
        categorized_new[category].append(article)
    
    for category in sorted(categorized_new.keys()):
        print(f"  {category}: {len(categorized_new[category])} new articles")
    
    # For each category: load existing feed, merge, age, apply diversity, generate
    all_categories = CATEGORIES.keys()
    
    print("\n📦 Processing category feeds...")
    category_stats = {}
    
    for category in all_categories:
        category_output = f"feed-{category}.json"
        feed_title = CATEGORIES[category]['name']
        
        # Load existing feed for this category
        existing_cat = load_existing_feed(category_output)
        
        # Add existing to shown cache
        for article in existing_cat:
            shown_cache.add(article.url_hash)
        
        # Get new articles for this category
        new_cat = categorized_new.get(category, [])
        
        # Merge and age
        merged_cat = merge_and_age_articles(existing_cat, new_cat, FEED_RETENTION_DAYS)
        
        # Apply diversity limits
        diverse_cat = apply_diversity_limits(merged_cat, MAX_PER_SOURCE)
        
        # Limit total feed size and sort by score
        final_cat = sorted(diverse_cat, key=lambda a: a.score, reverse=True)[:MAX_FEED_SIZE]
        
        # Generate and save JSON feed
        feed_data = generate_json_feed(final_cat, FEEDS, category)
        save_json_feed(feed_data, category_output)
        
        # Track stats
        local_count = len([a for a in final_cat if a.is_local])
        category_stats[category] = {
            'total': len(final_cat),
            'new': len(new_cat),
            'local': local_count
        }
        
        print(f"  ✅ {category}: {len(final_cat)} articles ({len(new_cat)} new)")
        
        # Add final articles to shown cache
        for article in final_cat:
            shown_cache.add(article.url_hash)
    
    # Save updated shown cache
    save_shown_cache(shown_cache)
    
    # Generate master OPML
    opml_content = generate_master_opml(CATEGORIES)
    with open('curated-feeds.opml', 'w') as f:
        f.write(opml_content)
    
    # Final statistics
    total_articles = sum(stats['total'] for stats in category_stats.values())
    total_new = sum(stats['new'] for stats in category_stats.values())
    
    print(f"\n📊 Generation complete!")
    print(f"  New articles fetched: {len(all_new_articles)}")
    print(f"  New articles scored: {len(quality_new)}")
    print(f"  Total articles across all feeds: {total_articles}")
    
    print(f"\n📂 Category breakdown:")
    for category in all_categories:
        stats = category_stats[category]
        local_suffix = f" ({stats['local']} local)" if stats['local'] > 0 else ""
        print(f"  {category}: {stats['total']} articles{local_suffix}")

if __name__ == '__main__':
    main()
