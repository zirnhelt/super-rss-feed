#!/usr/bin/env python3
"""
Super RSS Feed Curator with Category Feeds
- Loads existing feed and merges with new articles (no article loss between runs)
- Ages out articles older than FEED_RETENTION_DAYS
- Uses shown_cache to prevent re-scoring and re-adding aged-out articles
- Outputs JSON Feed format with prominent source attribution and image support
- Williams Lake Tribune gets priority treatment with direct scraping
- Generates separate category feeds: local, ai-tech, climate, homelab, science, scifi, news
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
MAX_FEED_SIZE = 500         # Total items in feed (cap to prevent bloat)
FEED_RETENTION_DAYS = 3     # Keep articles in feed for 3 days
MAX_PER_SOURCE = 8          # Default limit per source
MAX_PER_LOCAL = 15          # Higher limit for local content
LOOKBACK_HOURS = 48         # How far back to fetch articles
MIN_CLAUDE_SCORE = 20       # Minimum relevance score (0-100)
LOCAL_PRIORITY_SCORE = 100  # Maximum score for local articles

# Caching configuration
SCORED_CACHE_FILE = 'scored_articles_cache.json'
WLT_CACHE_FILE = 'wlt_cache.json'
SHOWN_CACHE_FILE = 'shown_articles_cache.json'  # Track articles already shown
CACHE_EXPIRY_HOURS = 48      # Don't re-score articles for 6 hours
SHOWN_CACHE_DAYS = 14       # Remember shown articles for 14 days

# Williams Lake Tribune settings
WLT_BASE_URL = "https://wltribune.com"
WLT_NEWS_URL = f"{WLT_BASE_URL}/news/"

# Filters
BLOCKED_SOURCES = [
    # News aggregators and low-quality sources  
    "fox news", "foxnews",
    "metafilter", "metafilter.com",
    "hacker news", "news.ycombinator.com", "hn",
    "reddit", "reddit.com",
    "digg", "digg.com", 
    "slashdot", "slashdot.org",
    "alltop", "allsides",
    "stumbleupon", "delicious",
    "newsvine", "mixx",
    # Social media aggregators
    "buzzfeed", "upworthy", "viral viral",
    "clickhole", "bored panda"
]
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
            self.image_url = self._extract_image(entry)
        else:
            self.title = title.strip()
            self.link = link.strip()
            self.description = description.strip()
            self.pub_date = pub_date or datetime.now(timezone.utc)
            self.image_url = None
        
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
                    return enc.href
        
        # Check media content (Media RSS)
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if media.get('type', '').startswith('image/'):
                    return media.get('url')
        
        # Parse description for <img> tags as fallback
        if self.description:
            img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', self.description)
            if img_match:
                return img_match.group(1)
        
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


def categorize_article(article: Article) -> str:
    """Categorize article based on title, description, and source"""
    text = f"{article.title} {article.description} {article.source}".lower()
    
    # Local content always goes to local feed
    if article.is_local:
        return "local"
    
    # Keywords for each category (order matters - first match wins)
    # Note: Mesh networking merged into homelab per user's Google Takeout analysis
    categories = {
        "ai-tech": [
            "ai", "machine learning", "ml", "artificial intelligence", "mlops",
            "platform engineering", "telemetry", "observability", "data pipeline",
            "llm", "neural", "deep learning", "transformer", "gpu computing",
            "anthropic", "openai", "claude", "chatgpt"
        ],
        "climate": [
            "climate", "solar", "battery", "batteries", "ev ", "electric vehicle", 
            "renewable", "carbon", "sustainability", "green energy", "wind power", 
            "emissions", "clean energy", "carbon capture", "geothermal"
        ],
        "homelab": [
            "homelab", "self-host", "home automation", "homekit", "homebridge",
            "3d print", "bambu", "smart home", "home assistant", "home network",
            "unifi", "omada", "philips hue", "ikea smart",
            # Mesh networking merged here (0.3% clicks vs 10.8% smart home)
            "meshtastic", "lora", "lorawan", "mesh network", "radio mesh"
        ],
        "science": [
            "research", "study finds", "scientists", "discovery", "academic",
            "peer review", "journal", "systems thinking", "complex system",
            "emergence", "network effect", "interdepend"
        ],
        "scifi": [
            "sci-fi", "science fiction", "fantasy", "worldbuilding", "novel",
            "author", "book review", "sanderson", "rothfuss", "leckie",
            "tchaikovsky", "murderbot"
        ]
    }
    
    # Check each category
    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category
    
    # Default to general news
    return "news"


def load_existing_feed(feed_path: str) -> List[Article]:
    """Load articles from previous feed generation"""
    try:
        with open(feed_path, 'r') as f:
            feed_data = json.load(f)
        
        articles = []
        for item in feed_data.get('items', []):
            # Reconstruct Article objects from previous feed
            article = Article(
                title=item['_source']['original_title'],
                link=item['url'],
                description=item['summary'],
                pub_date=datetime.fromisoformat(item['date_published']),
                source_title=item['_source']['source_name'],
                source_url=item['_source']['source_url'],
                is_local=item['_source'].get('is_local', False)
            )
            article.score = item['_source']['ai_score']
            article.image_url = item.get('image')
            articles.append(article)
        
        print(f"📚 Loaded {len(articles)} articles from previous feed")
        return articles
    except FileNotFoundError:
        print("📚 No previous feed found, starting fresh")
        return []
    except Exception as e:
        print(f"⚠️ Error loading previous feed: {e}")
        return []


def merge_and_age_articles(existing: List[Article], new: List[Article], 
                           retention_days: int = 3) -> List[Article]:
    """Merge new articles with existing, remove old ones, dedupe by URL"""
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
    
    # Keep existing articles that aren't too old
    retained = [a for a in existing if a.pub_date > cutoff_date]
    aged_out = len(existing) - len(retained)
    if aged_out > 0:
        print(f"📅 Aged out {aged_out} articles (> {retention_days} days old)")
    
    # Combine with new articles
    combined = retained + new
    
    # Dedupe by URL (existing articles take precedence to preserve state)
    seen_urls = set()
    deduped = []
    
    for article in combined:
        if article.url_hash not in seen_urls:
            seen_urls.add(article.url_hash)
            deduped.append(article)
    
    removed_dupes = len(combined) - len(deduped)
    if removed_dupes > 0:
        print(f"🔄 Removed {removed_dupes} duplicate articles during merge")
    
    return deduped


def load_wlt_cache() -> Dict[str, bool]:
    """Load Williams Lake Tribune URL cache to avoid re-scraping"""
    try:
        if os.path.exists(WLT_CACHE_FILE):
            with open(WLT_CACHE_FILE, 'r') as f:
                cache = json.load(f)
                print(f"📖 Loaded WLT cache with {len(cache)} URLs")
                return cache
    except Exception as e:
        print(f"⚠️ WLT cache load error: {e}")
    
    return {}


def save_wlt_cache(cache: Dict[str, bool]):
    """Save Williams Lake Tribune URL cache"""
    try:
        with open(WLT_CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"⚠️ WLT cache save error: {e}")


def scrape_williams_lake_tribune() -> List[Article]:
    """Scrape fresh Williams Lake Tribune articles with caching"""
    print("📰 Scraping Williams Lake Tribune...")
    
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
        cache_cleaned = {url: True for url in cache.keys() 
                        if any(f'/{year}/' in url for year in ['2026'])}  # Keep 2026 articles
        
        # Save updated cache
        save_wlt_cache(cache_cleaned)
        
        print(f"  📰 Williams Lake Tribune: {new_articles} new articles")
        if len(articles) != new_articles:
            print(f"  📖 Cache: {len(articles) - new_articles} previously seen")
    
    except Exception as e:
        print(f"  ✗ Williams Lake Tribune scraping error: {e}")
    
    return articles


def load_scored_cache() -> Dict[str, Dict]:
    """Load cached article scores to avoid re-scoring"""
    try:
        if os.path.exists(SCORED_CACHE_FILE):
            with open(SCORED_CACHE_FILE, 'r') as f:
                cache = json.load(f)
                print(f"📖 Loaded {len(cache)} articles from scoring cache")
                return cache
    except Exception as e:
        print(f"⚠️ Scoring cache load error: {e}")
    
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
            print(f"💾 Saved scoring cache with {len(cleaned_cache)} articles (removed {removed} old entries)")
    except Exception as e:
        print(f"⚠️ Scoring cache save error: {e}")


def is_cache_entry_valid(cache_entry: Dict) -> bool:
    """Check if cached score is still valid (within CACHE_EXPIRY_HOURS)"""
    try:
        scored_at = datetime.fromisoformat(cache_entry['scored_at'])
        cutoff = datetime.now(timezone.utc) - timedelta(hours=CACHE_EXPIRY_HOURS)
        return scored_at > cutoff
    except:
        return False


def load_shown_cache() -> set:
    """Load cache of previously shown article hashes"""
    try:
        with open(SHOWN_CACHE_FILE, 'r') as f:
            data = json.load(f)
            # Clean expired entries on load
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=SHOWN_CACHE_DAYS)
            valid_hashes = {
                url_hash for url_hash, timestamp in data.items()
                if datetime.fromisoformat(timestamp) > cutoff_time
            }
            print(f"📖 Loaded {len(valid_hashes)} previously shown articles ({len(data) - len(valid_hashes)} expired)")
            return valid_hashes
    except FileNotFoundError:
        print("📖 No shown articles cache found, starting fresh")
        return set()
    except Exception as e:
        print(f"⚠️ Shown cache load error: {e}")
        return set()


def save_shown_cache(shown_hashes: set):
    """Save cache of shown article hashes with timestamps"""
    try:
        # Load existing data first
        existing_data = {}
        try:
            with open(SHOWN_CACHE_FILE, 'r') as f:
                existing_data = json.load(f)
        except:
            pass
        
        # Add new hashes with current timestamp
        current_time = datetime.now(timezone.utc).isoformat()
        for url_hash in shown_hashes:
            existing_data[url_hash] = current_time
        
        # Clean expired entries
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=SHOWN_CACHE_DAYS)
        cleaned_data = {
            url_hash: timestamp for url_hash, timestamp in existing_data.items()
            if datetime.fromisoformat(timestamp) > cutoff_time
        }
        
        with open(SHOWN_CACHE_FILE, 'w') as f:
            json.dump(cleaned_data, f, indent=2)
        
        removed = len(existing_data) - len(cleaned_data)
        print(f"💾 Saved shown articles cache with {len(cleaned_data)} articles" + 
              (f" (removed {removed} expired)" if removed > 0 else ""))
    except Exception as e:
        print(f"⚠️ Shown cache save error: {e}")


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
        # Set user agent to avoid blocking by tech sites
        feedparser.USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        headers = {
            "User-Agent": feedparser.USER_AGENT,
            "Accept": "application/rss+xml, application/xml, text/xml"
        }
        parsed = feedparser.parse(feed["url"], request_headers=headers)
        
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
PRIMARY INTERESTS (High Relevance - Score 70-100):
- AI/ML infrastructure and telemetry: MLOps, observability, production AI systems, platform engineering, data pipelines
- Climate tech and renewable energy: Solar, batteries, EVs, carbon capture, clean energy technologies
- Smart home and home automation: HomeKit, HomeBridge, Omada networking, home network infrastructure
- 3D printing: Bambu Lab ecosystem, PLA materials, printer mechanics, slicing software
- Williams Lake and Cariboo local news: Community events, regional development, local politics, Indigenous issues

SECONDARY INTERESTS (Medium Relevance - Score 40-69):
- Systems thinking and complex systems: Network effects, feedback loops, emergence, interdependencies, resilience
- Meshtastic and LoRa mesh networking: Off-grid communication, mesh protocols, rural connectivity
- Homelab and self-hosting: Infrastructure, privacy-focused tech, home servers, automation
- Sustainable agriculture and food systems: Regenerative farming, permaculture, local food webs, organic practices
- Rural connectivity and infrastructure: Broadband access, remote work technology, small-town digital infrastructure
- Community resilience: Local economies, disaster preparedness, social infrastructure, mutual aid
- Sci-fi worldbuilding: Hard science fiction, speculative fiction, world-building systems, narrative construction

CONTEXTUAL INTERESTS (Score Based on Quality - 20-60):
- Cariboo region culture and development: BC rural issues, small-town planning, regional history
- Food preservation and traditional skills: When tied to systems thinking or sustainability
- Off-grid and homestead technology: Solar systems, water management, DIY infrastructure
- Deep technical how-tos: Hands-on guides, configuration walkthroughs, troubleshooting
- Scientific research and discoveries: Breakthrough studies, novel findings with systems implications

SCORING NOTES:
- Local Williams Lake/Cariboo content should score 80+ regardless of topic
- Content bridging multiple interests (e.g. "solar homestead automation") scores higher
- Prefer deep analysis over breaking news
- Prioritize systems-level thinking over isolated facts
- Technical depth and hands-on utility boost scores

AVOID (Score 0-20):
- Celebrity news, gossip, advice columns
- Sports coverage (unless technology/systems angle)
- Surface-level product reviews without technical depth
- Clickbait and engagement farming
- Pure lifestyle content without systems thinking
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
                print(f"  ⚠️ Scoring error: {e}")
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


def generate_json_feed(articles: List[Article], output_path: str, feed_title: str = "Curated Feed"):
    """Generate JSON Feed file with prominent source attribution and image support"""
    
    feed_data = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": feed_title,
        "home_page_url": "https://github.com/zirnhelt/super-rss-feed",
        "feed_url": f"https://zirnhelt.github.io/super-rss-feed/{output_path}",
        "description": f"AI-curated {feed_title.lower()} articles",
        "authors": [{"name": "Erich's AI Curator"}],
        "items": []
    }
    
    for article in articles:
        # Create prominent source-first title with local indicator
        local_prefix = "📍 " if article.is_local else ""
        item_title = f"{local_prefix}[{article.source}] {article.title}"
        
        # Rich metadata for better reader display
        item = {
            "id": article.link,
            "url": article.link,
            "title": item_title,
            "content_html": f"<p>{article.description}</p>",
            "summary": article.description,
            "date_published": article.pub_date.isoformat(),
            "authors": [{"name": article.source}],
            "tags": [article.source.lower().replace(" ", "_")],
            "_source": {
                "original_title": article.title,
                "source_name": article.source,
                "source_url": article.source_url,
                "ai_score": article.score,
                "relevance": "local" if article.is_local else ("high" if article.score >= 70 else "medium"),
                "is_local": article.is_local
            }
        }
        
        # Add image if available
        if article.image_url:
            item["image"] = article.image_url
        
        # Add external URL reference
        if article.source_url:
            item["external_url"] = article.source_url
            
        feed_data["items"].append(item)
    
    # Write JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(feed_data, f, indent=2, ensure_ascii=False)
    
    # Count articles with images for stats
    articles_with_images = sum(1 for a in articles if a.image_url)
    
    print(f"  ✅ {output_path} ({len(articles)} articles, {articles_with_images} with images)")


def main():
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    # Load shown cache (prevents re-adding aged-out articles and re-scoring existing ones)
    shown_cache = load_shown_cache()
    
    # Parse OPML (excludes Williams Lake Tribune RSS to avoid duplicates)
    opml_path = sys.argv[1] if len(sys.argv) > 1 else 'feeds.opml'
    feeds = parse_opml(opml_path)
    
    # Scrape Williams Lake Tribune directly for priority local news
    local_articles = scrape_williams_lake_tribune()
    
    # Fetch RSS feed articles
    cutoff_date = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    print(f"\n📥 Fetching articles from last {LOOKBACK_HOURS} hours...")
    
    rss_articles = []
    for feed in feeds:
        articles = fetch_feed_articles(feed, cutoff_date)
        rss_articles.extend(articles)
    
    # Combine local and RSS articles
    all_new_articles = local_articles + rss_articles
    print(f"\n📈 Total NEW articles fetched: {len(all_new_articles)}")
    
    # Filter against shown cache (removes already-in-feed AND aged-out-but-seen)
    truly_new = [a for a in all_new_articles if a.url_hash not in shown_cache]
    print(f"🆕 Truly new articles (not in cache): {len(truly_new)}")
    
    # Deduplicate truly new articles
    unique_new = deduplicate_articles(truly_new)
    
    # Score only NEW articles with Claude (using smart caching)
    scored_new = score_articles_with_claude(unique_new, api_key)
    
    # Filter NEW articles by minimum score (but always keep local articles)
    quality_new = [a for a in scored_new if a.score >= MIN_CLAUDE_SCORE or a.is_local]
    non_local_filtered = len([a for a in scored_new if not a.is_local and a.score < MIN_CLAUDE_SCORE])
    if non_local_filtered > 0:
        print(f"⭐ Quality filter (score >= {MIN_CLAUDE_SCORE}): {len(scored_new)} → {len(quality_new)} articles ({non_local_filtered} filtered)")
    
    # CATEGORIZE all quality new articles
    print("\n📂 Categorizing new articles...")
    categorized_new = defaultdict(list)
    for article in quality_new:
        category = categorize_article(article)
        categorized_new[category].append(article)
    
    for category in sorted(categorized_new.keys()):
        print(f"  {category}: {len(categorized_new[category])} new articles")
    
    # For each category: load existing feed, merge, age, apply diversity, generate
    all_categories = ['local', 'ai-tech', 'climate', 'homelab', 'science', 'scifi', 'news']
    
    print("\n📦 Processing category feeds...")
    category_stats = {}
    
    for category in all_categories:
        category_output = f"feed-{category}.json"
        category_title_map = {
            'local': 'Williams Lake Local',
            'ai-tech': 'AI/ML & Tech',
            'climate': 'Climate & Energy',
            'homelab': 'Homelab & DIY',
            'science': 'Science',
            'scifi': 'Sci-Fi & Culture',
            'news': 'General News'
        }
        feed_title = category_title_map.get(category, category.title())
        
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
        
        # Generate category feed
        generate_json_feed(final_cat, category_output, feed_title)
        
        # Collect stats
        category_stats[category] = {
            'total': len(final_cat),
            'local': sum(1 for a in final_cat if a.is_local)
        }
    
    # Update shown cache with ALL new articles
    new_shown_hashes = {a.url_hash for a in quality_new}
    shown_cache.update(new_shown_hashes)
    save_shown_cache(shown_cache)
    
    # Final stats
    total_articles = sum(stats['total'] for stats in category_stats.values())
    print("\n📊 Final stats:")
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
