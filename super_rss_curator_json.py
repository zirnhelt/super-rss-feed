#!/usr/bin/env python3
"""
Super RSS Feed Curator with Category-Based Feeds
- Categorizes articles into 8 topic-based feeds
- Generates individual JSON feeds per category
- Auto-generates OPML subscription file
- Uses Claude API with prompt caching for cost efficiency
"""
import os
import sys
import re
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import List, Dict, Optional, Set
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
MAX_PER_CATEGORY = 50  # Max articles per category feed
MAX_PER_SOURCE = 8  # Default limit per source
MAX_PER_LOCAL = 15  # Higher limit for local content
LOOKBACK_HOURS = 48  # How far back to fetch articles
MIN_CLAUDE_SCORE = 30  # Minimum relevance score (0-100)
LOCAL_PRIORITY_SCORE = 100  # Maximum score for local articles

# Caching configuration
SCORED_CACHE_FILE = 'scored_articles_cache.json'
WLT_CACHE_FILE = 'wlt_cache.json'
CACHE_EXPIRY_HOURS = 24  # Don't re-score articles for 24 hours

# Williams Lake Tribune settings
WLT_BASE_URL = "https://wltribune.com"
WLT_NEWS_URL = f"{WLT_BASE_URL}/news/"

# Category definitions
CATEGORIES = {
    'local': {
        'name': 'Williams Lake Local',
        'emoji': '📍',
        'description': 'Local news from Williams Lake and surrounding Cariboo region',
        'filename': 'feed-local.json'
    },
    'ai_tech': {
        'name': 'AI/ML & Tech Infrastructure',
        'emoji': '🤖',
        'description': 'AI, machine learning, infrastructure, and telemetry',
        'filename': 'feed-ai-tech.json'
    },
    'climate': {
        'name': 'Climate & Sustainability',
        'emoji': '🌍',
        'description': 'Climate technology, sustainability, and environmental news',
        'filename': 'feed-climate.json'
    },
    'homelab': {
        'name': 'Homelab & Self-Hosting',
        'emoji': '🏠',
        'description': 'Homelab tech, self-hosting, and home automation',
        'filename': 'feed-homelab.json'
    },
    'mesh': {
        'name': 'Mesh Networks & Hardware',
        'emoji': '📡',
        'description': 'Meshtastic, mesh networking, and hardware projects',
        'filename': 'feed-mesh.json'
    },
    'science': {
        'name': 'Science & Systems Thinking',
        'emoji': '🔬',
        'description': 'Systems thinking, complexity, and scientific discoveries',
        'filename': 'feed-science.json'
    },
    'scifi': {
        'name': 'Sci-fi & Worldbuilding',
        'emoji': '📚',
        'description': 'Science fiction, fantasy, and worldbuilding',
        'filename': 'feed-scifi.json'
    },
    'news': {
        'name': 'Canadian and Global News',
        'emoji': '🌐',
        'description': 'Canadian and international news coverage',
        'filename': 'feed-news.json'
    }
}

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
    """Represents a single article with category tags"""
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
        self.categories: Set[str] = {'local'} if is_local else set()
        
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
                if enc.get('type', '').startswith('image/'):
                    return enc.get('href') or enc.get('url')
        
        # Check media:content
        if hasattr(entry, 'media_content') and entry.media_content:
            for media in entry.media_content:
                if media.get('medium') == 'image' or media.get('type', '').startswith('image/'):
                    return media.get('url')
        
        # Check media:thumbnail
        if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
            return entry.media_thumbnail[0].get('url')
        
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
        with open(WLT_CACHE_FILE, 'r') as f:
            cache = json.load(f)
            print(f"📖 Loaded WLT cache with {len(cache)} URLs")
            return cache
    except FileNotFoundError:
        print("📖 No WLT cache found, starting fresh")
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
    print("📍 Scraping Williams Lake Tribune...")
    
    cache = load_wlt_cache()
    articles = []
    new_urls = []
    
    # Sports keywords for filtering even local content
    sports_keywords = ["hockey", "basketball", "soccer", "football", "baseball", 
                      "tournament", "championship", "sports", "athletics",
                      "game", "season", "playoff", "league"]
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(WLT_NEWS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        article_links = soup.find_all('a', href=True)
        
        for link in article_links:
            href = link.get('href', '')
            
            if not href or href.startswith('#') or 'javascript:' in href:
                continue
                
            if href.startswith('/'):
                full_url = urljoin(WLT_BASE_URL, href)
            elif href.startswith('http'):
                full_url = href
            else:
                continue
            
            if 'wltribune.com' not in full_url or '/2026/' not in full_url:
                continue
                
            if full_url in cache:
                continue
            
            title = link.get_text().strip()
            if not title or len(title) < 10:
                continue
                
            # Check if title contains sports keywords (even for local content)
            title_lower = title.lower()
            if any(keyword in title_lower for keyword in sports_keywords):
                continue  # Skip sports articles even from WLT
                
            article = Article(
                title=title,
                link=full_url,
                description=f"Local news from Williams Lake Tribune",
                pub_date=datetime.now(timezone.utc),
                source_title="Williams Lake Tribune",
                source_url=WLT_BASE_URL,
                is_local=True
            )
            
            articles.append(article)
            new_urls.append(full_url)
            cache[full_url] = True
            
            if len(articles) >= 20:
                break
        
        if new_urls:
            save_wlt_cache(cache)
            
        print(f"  📰 Williams Lake Tribune: {len(articles)} new articles")
    
    except Exception as e:
        print(f"  ✗ Williams Lake Tribune scraping error: {e}")
    
    return articles


def load_scored_cache() -> Dict[str, Dict]:
    """Load cache of previously scored articles"""
    try:
        with open(SCORED_CACHE_FILE, 'r') as f:
            cache = json.load(f)
            print(f"📖 Loaded {len(cache)} articles from scoring cache")
            return cache
    except FileNotFoundError:
        print("📖 No scoring cache found, starting fresh")
        return {}
    except Exception as e:
        print(f"⚠ Scoring cache load error: {e}")
        return {}


def save_scored_cache(cache: Dict[str, Dict]):
    """Save cache of scored articles, removing old entries"""
    try:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=12)
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
            
            if article.pub_date < cutoff_date:
                continue
            
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
        if article.url_hash in seen_urls:
            continue
        
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


def score_and_categorize_articles(articles: List[Article], api_key: str) -> List[Article]:
    """Score articles and assign categories using Claude API with prompt caching"""
    
    # Separate local articles (already categorized) from others
    local_articles = [a for a in articles if a.is_local]
    non_local_articles = [a for a in articles if not a.is_local]
    
    if local_articles:
        print(f"📍 Local articles: {len(local_articles)} (auto-scored and categorized)")
    
    if not non_local_articles:
        print("🔍 Only local articles found, skipping Claude scoring")
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
            # Use cached score and categories
            article.score = cache_entry['score']
            article.categories = set(cache_entry.get('categories', []))
            cached_articles.append(article)
            cache_hits += 1
        else:
            new_articles.append(article)
    
    print(f"💡 Cache: {cache_hits} hits, {len(new_articles)} new articles to score")
    
    # Only score new articles if there are any
    if new_articles:
        client = anthropic.Anthropic(api_key=api_key)
        
        # System prompt with cache control (cached across all API calls!)
        # NOTE: Must be >1024 tokens to trigger caching
        system_prompt = [{
            "type": "text",
            "text": """You are an expert article scorer and categorizer for an RSS feed curation system. Your task is to evaluate articles based on specific interests and assign both relevance scores and category tags.

SCORING CRITERIA (0-100 scale):

Primary Interests (HIGH scores 70-100):
- AI/ML Infrastructure & Telemetry: Focus on production systems, observability, MLOps, platform engineering, and data pipelines. Value architecture discussions over product announcements.
- Systems Thinking & Complex Systems: Articles exploring feedback loops, emergence, network effects, interdependencies, and holistic approaches to understanding systems.
- Climate Tech & Sustainability: Clean energy technologies, carbon capture, sustainable materials, climate adaptation strategies, and environmental policy with technical depth.
- Homelab & Self-Hosting: Home automation, self-hosted services, privacy-focused alternatives, HomeLab infrastructure, local-first software, and DIY tech projects.
- Meshtastic & Mesh Networking: LoRa mesh networks, decentralized communication, radio technology, network resilience, and community mesh infrastructure.
- 3D Printing (Bambu Lab focus): Technical discussions of 3D printing technology, materials science, printer mechanics, slicing software, and practical applications.
- Sci-Fi Worldbuilding: Hard science fiction, speculative fiction with deep worldbuilding, magic systems, fictional technologies, and narrative construction.
- Canadian Content & Local News: Stories from Williams Lake, Quesnel, Cariboo region, British Columbia, and broader Canadian news with regional relevance.

Secondary Interests (MEDIUM scores 40-69):
- General technology news with technical depth
- Scientific research papers and discoveries
- Policy discussions with technical implications
- Engineering deep-dives in any field
- Open source software development
- Privacy and digital rights
- Remote work and distributed teams

Low Interest (scores 10-39):
- Surface-level tech product reviews
- Celebrity news and entertainment
- Sports coverage (unless locally relevant)
- Lifestyle and personal advice
- Political news without policy substance
- Marketing and promotional content

SCORING GUIDELINES:
- 90-100: Exceptional match to core interests with technical depth
- 70-89: Strong match to core interests or very good technical content
- 50-69: Moderate relevance or good content in secondary interests
- 30-49: Tangential relevance or surface-level coverage of topics
- 10-29: Minimal relevance but not filtered out
- 0-9: Should have been filtered (but score honestly)

CATEGORY ASSIGNMENTS:

ai_tech: 
- AI/ML systems, infrastructure, telemetry
- Tech platforms, APIs, developer tools
- Data engineering, MLOps, observability
- Software architecture and systems design

climate: 
- Climate technology and clean energy
- Sustainability practices and materials
- Environmental policy and regulations
- Carbon capture, renewable energy, EVs
- Climate adaptation and resilience

homelab: 
- Home automation (HomeKit, HomeBridge, etc.)
- Self-hosted services and applications
- Privacy tools and local-first software
- DIY electronics and maker projects
- Network equipment and configuration

mesh: 
- Meshtastic and LoRa networks
- Mesh networking protocols
- Decentralized communication
- Radio technology and amateur radio
- Network resilience and redundancy

science: 
- Systems thinking and complexity science
- Scientific research and discoveries
- Academic papers and studies
- Network science and graph theory
- Interdisciplinary research

scifi: 
- Science fiction and speculative fiction
- Fantasy with rich worldbuilding
- Magic systems and fictional technologies
- Narrative construction and storytelling
- Book reviews and author discussions

news: 
- Canadian news (national and regional)
- Williams Lake and Cariboo local news
- Global current events
- Political developments
- General interest journalism

CATEGORY ASSIGNMENT RULES:
- Assign 1-3 categories per article (most articles have 1-2)
- Primary category should match the article's main focus
- Add secondary categories if substantial overlap exists
- Technical depth may warrant multiple categories (e.g., climate + ai_tech for AI in climate modeling)
- Local news always gets 'news' category
- Don't force categories if article is genuinely single-topic

OUTPUT FORMAT:
Return ONLY valid JSON array (no markdown, no code blocks, no backticks, no explanatory text):
[{"score": 85, "categories": ["ai_tech", "science"]}, {"score": 42, "categories": ["news"]}, ...]

Each object must have:
- "score": integer 0-100
- "categories": array of 1-3 category strings from the allowed list

EXAMPLES:
Article: "New Observability Platform Traces ML Model Performance in Production"
Response: {"score": 88, "categories": ["ai_tech"]}

Article: "Williams Lake Fire Department Responds to Wildfire Near City Limits"
Response: {"score": 95, "categories": ["news"]}

Article: "Mesh Networks Provide Communications During Hurricane Aftermath"
Response: {"score": 92, "categories": ["mesh", "news"]}

Article: "Celebrity Chef Opens New Restaurant in Vancouver"
Response: {"score": 15, "categories": ["news"]}

Remember: Be consistent, honest in scoring, and focus on technical depth and substantive content over hype and promotion.""",
            "cache_control": {"type": "ephemeral"}
        }]
        
        print(f"🤖 Scoring and categorizing {len(new_articles)} articles with Claude (prompt caching enabled)...")
        
        # Batch articles for efficiency (10 at a time)
        batch_size = 10
        
        for i in range(0, len(new_articles), batch_size):
            batch = new_articles[i:i+batch_size]
            
            # Prepare batch for Claude
            article_list = "\n\n".join([
                f"Article {idx}:\nTitle: {a.title}\nSource: {a.source}\nDescription: {a.description[:200]}..."
                for idx, a in enumerate(batch)
            ])
            
            try:
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    system=system_prompt,
                    messages=[{
                        "role": "user",
                        "content": f"Score and categorize these articles:\n\n{article_list}"
                    }]
                )
                
                result_text = response.content[0].text.strip()
                
                # Parse JSON response
                results = json.loads(result_text)
                
                # Apply scores and categories
                current_time = datetime.now(timezone.utc).isoformat()
                for article, result in zip(batch, results):
                    article.score = result.get('score', 50)
                    article.categories = set(result.get('categories', ['news']))
                    
                    # Update cache
                    cache[article.url_hash] = {
                        'score': article.score,
                        'categories': list(article.categories),
                        'title': article.title,
                        'source': article.source,
                        'scored_at': current_time
                    }
            
            except Exception as e:
                print(f"  ⚠ Scoring error: {e}")
                # Assign default scores on error
                for article in batch:
                    article.score = 50
                    article.categories = {'news'}
    
    # Save updated cache
    if new_articles:
        save_scored_cache(cache)
    
    # Return all articles (local + cached + newly scored)
    all_articles = local_articles + cached_articles + new_articles
    return all_articles


def apply_diversity_limits(articles: List[Article], max_per_source: int) -> List[Article]:
    """Limit articles per source to ensure diversity"""
    source_counts = defaultdict(int)
    diverse_articles = []
    
    # Sort by score first
    sorted_articles = sorted(articles, key=lambda a: a.score, reverse=True)
    
    for article in sorted_articles:
        limit = MAX_PER_LOCAL if article.is_local else max_per_source
        
        if source_counts[article.source] < limit:
            diverse_articles.append(article)
            source_counts[article.source] += 1
    
    print(f"📊 Diversity filter: {len(articles)} → {len(diverse_articles)} articles")
    return diverse_articles


def generate_category_feeds(articles: List[Article], base_url: str):
    """Generate individual JSON feeds per category"""
    
    # Organize articles by category
    category_articles = defaultdict(list)
    for article in articles:
        for category in article.categories:
            if category in CATEGORIES:
                category_articles[category].append(article)
    
    print(f"\n📂 Generating category feeds...")
    
    # Generate feed for each category
    for cat_key, cat_info in CATEGORIES.items():
        cat_articles = category_articles.get(cat_key, [])
        
        if not cat_articles:
            print(f"  ⚠ {cat_info['emoji']} {cat_info['name']}: 0 articles (skipping)")
            continue
        
        # Sort by score and limit
        cat_articles.sort(key=lambda a: a.score, reverse=True)
        cat_articles = cat_articles[:MAX_PER_CATEGORY]
        
        feed_data = {
            "version": "https://jsonfeed.org/version/1.1",
            "title": f"{cat_info['emoji']} {cat_info['name']}",
            "home_page_url": "https://github.com/zirnhelt/super-rss-feed",
            "feed_url": f"{base_url}/{cat_info['filename']}",
            "description": cat_info['description'],
            "authors": [{"name": "Erich's AI Curator"}],
            "items": []
        }
        
        for article in cat_articles:
            local_prefix = "📍 " if article.is_local else ""
            item_title = f"{local_prefix}[{article.source}] {article.title}"
            
            item = {
                "id": article.link,
                "url": article.link,
                "title": item_title,
                "content_html": f"<p>{article.description}</p>",
                "summary": article.description,
                "date_published": article.pub_date.isoformat(),
                "authors": [{"name": article.source}],
                "tags": [article.source.lower().replace(" ", "_")] + list(article.categories),
                "_source": {
                    "original_title": article.title,
                    "source_name": article.source,
                    "source_url": article.source_url,
                    "ai_score": article.score,
                    "categories": list(article.categories),
                    "is_local": article.is_local
                }
            }
            
            if article.source_url:
                item["external_url"] = article.source_url
            
            if article.image_url:
                item["image"] = article.image_url
                
            feed_data["items"].append(item)
        
        # Write JSON file
        with open(cat_info['filename'], 'w', encoding='utf-8') as f:
            json.dump(feed_data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ {cat_info['emoji']} {cat_info['name']}: {len(cat_articles)} articles → {cat_info['filename']}")


def generate_opml(base_url: str):
    """Generate OPML subscription file for all category feeds"""
    
    opml = ET.Element('opml', version="1.0")
    head = ET.SubElement(opml, 'head')
    ET.SubElement(head, 'title').text = "Erich's Curated Feeds"
    ET.SubElement(head, 'dateCreated').text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    body = ET.SubElement(opml, 'body')
     
    # Add category feeds
    for cat_key, cat_info in CATEGORIES.items():
        ET.SubElement(body, 'outline',
                      type="rss",
                      text=f"{cat_info['emoji']} {cat_info['name']}",
                      title=f"{cat_info['emoji']} {cat_info['name']}",
                      xmlUrl=f"{base_url}/{cat_info['filename']}",
                      htmlUrl="https://github.com/zirnhelt/super-rss-feed")
    
    # Write OPML file
    tree = ET.ElementTree(opml)
    ET.indent(tree, space="  ")
    tree.write('curated-feeds.opml', encoding='utf-8', xml_declaration=True)
    
    print(f"\n📋 OPML subscription file → curated-feeds.opml")
    print(f"   Import this into Inoreader to subscribe to all feeds at once!")


def main():
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    # Parse OPML
    opml_path = sys.argv[1] if len(sys.argv) > 1 else 'feeds.opml'
    feeds = parse_opml(opml_path)
    
    # Step 1: Scrape Williams Lake Tribune
    local_articles = scrape_williams_lake_tribune()
    
    # Step 2: Fetch articles from OPML feeds
    cutoff_date = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    print(f"\n🔥 Fetching articles from last {LOOKBACK_HOURS} hours...")
    
    rss_articles = []
    for feed in feeds:
        if 'wltribune' in feed['url'].lower():
            print(f"  ⭐ {feed['title']}: Skipped (using direct scraper)")
            continue
            
        articles = fetch_feed_articles(feed, cutoff_date)
        rss_articles.extend(articles)
    
    # Combine and process
    all_articles = local_articles + rss_articles
    print(f"\n📈 Total fetched: {len(all_articles)} articles ({len(local_articles)} local + {len(rss_articles)} RSS)")
    
    # Deduplicate
    unique_articles = deduplicate_articles(all_articles)
    
    # Score and categorize with Claude
    scored_articles = score_and_categorize_articles(unique_articles, api_key)
    
    # Filter by minimum score (but always include local)
    quality_articles = [a for a in scored_articles if a.score >= MIN_CLAUDE_SCORE or a.is_local]
    print(f"⭐ Quality filter (score >= {MIN_CLAUDE_SCORE}): {len(scored_articles)} → {len(quality_articles)} articles")
    
    # Apply diversity limits
    diverse_articles = apply_diversity_limits(quality_articles, MAX_PER_SOURCE)
    
    # Generate category feeds
    base_url = "https://zirnhelt.github.io/super-rss-feed"
    generate_category_feeds(diverse_articles, base_url)
    
    # Generate OPML subscription file
    generate_opml(base_url)
    
    # Stats
    print("\n📊 Final stats:")
    print(f"  Total sources: {len(feeds) + 1}")
    print(f"  Articles fetched: {len(all_articles)}")
    print(f"  After dedup: {len(unique_articles)}")
    print(f"  After scoring: {len(quality_articles)}")
    print(f"  After diversity: {len(diverse_articles)}")
    
    # Category breakdown
    print("\n📂 Articles by category:")
    category_counts = defaultdict(int)
    for article in diverse_articles:
        for cat in article.categories:
            if cat in CATEGORIES:
                category_counts[cat] += 1
    
    for cat_key in CATEGORIES.keys():
        count = category_counts.get(cat_key, 0)
        emoji = CATEGORIES[cat_key]['emoji']
        name = CATEGORIES[cat_key]['name']
        print(f"  {emoji} {name}: {count} articles")


if __name__ == '__main__':
    main()
