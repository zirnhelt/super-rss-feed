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
import anthropic

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

# Cache files
SCORED_CACHE_FILE = SYSTEM['cache_files']['scored_articles']
WLT_CACHE_FILE = SYSTEM['cache_files']['wlt']
SHOWN_CACHE_FILE = SYSTEM['cache_files']['shown_articles']

# URLs
WLT_BASE_URL = SYSTEM['urls']['wlt_base']
WLT_NEWS_URL = SYSTEM['urls']['wlt_news']

class Article:
    """Represents a single article"""
    def __init__(self, entry, source_title: str, source_url: str, feed_url: str = ''):
        self.title = entry.get('title', '').strip()
        self.link = entry.get('link', '').strip()
        self.description = entry.get('description', '') or entry.get('summary', '')
        self.pub_date = self._parse_date(entry)
        self.source = source_title
        self.source_url = source_url
        self.feed_url = feed_url
        self.score = 0
        self.category = None
        
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
        """Check if article should be filtered out"""
        text = f"{self.title} {self.description}".lower()
        
        source_lower = self.source.lower()
        if any(blocked in source_lower for blocked in FILTERS['blocked_sources']):
            return True
        
        if any(keyword in text for keyword in FILTERS['blocked_keywords']):
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
        return set()
    
    try:
        with open(SHOWN_CACHE_FILE, 'r') as f:
            cache = json.load(f)
        
        cache_expiry = timedelta(days=SYSTEM['cache_expiry']['shown_days'])
        cutoff = datetime.now(timezone.utc).timestamp() - cache_expiry.total_seconds()
        
        valid_urls = {url for url, timestamp in cache.items() if timestamp > cutoff}
        
        return valid_urls
        
    except (json.JSONDecodeError, FileNotFoundError):
        return set()


def save_shown_cache(shown_urls):
    """Save shown articles cache"""
    try:
        cache = {url: datetime.now(timezone.utc).timestamp() for url in shown_urls}
        with open(SHOWN_CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save shown cache: {e}")


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
        
        return {k: v for k, v in cache.items() if v.get('timestamp', 0) > cutoff}
        
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_wlt_cache(cache):
    """Save WLT scraping cache"""
    try:
        with open(WLT_CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save WLT cache: {e}")


def scrape_wlt_news():
    """Scrape Williams Lake Tribune news page"""
    print(f"📰 Scraping Williams Lake Tribune from {WLT_NEWS_URL}")
    
    cache = load_wlt_cache()
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; RSS Reader/1.0)'}
        response = requests.get(WLT_NEWS_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        
        for article_div in soup.find_all('div', class_='story-block'):
            try:
                title_elem = article_div.find('h3')
                if not title_elem or not title_elem.find('a'):
                    continue
                
                link_elem = title_elem.find('a')
                title = link_elem.get_text(strip=True)
                relative_url = link_elem.get('href', '')
                
                if not relative_url.startswith('http'):
                    url = f"{WLT_BASE_URL}{relative_url}"
                else:
                    url = relative_url
                
                url_hash = hashlib.md5(url.encode()).hexdigest()
                if url_hash in cache:
                    continue
                
                img_elem = article_div.find('img')
                image_url = None
                if img_elem and img_elem.get('src'):
                    img_src = img_elem['src']
                    if img_src.startswith('http'):
                        image_url = img_src
                    elif img_src.startswith('/'):
                        image_url = f"{WLT_BASE_URL}{img_src}"
                
                summary_elem = article_div.find('p')
                summary = summary_elem.get_text(strip=True) if summary_elem else ''
                
                cache[url_hash] = {
                    'title': title,
                    'url': url,
                    'summary': summary,
                    'image': image_url,
                    'timestamp': datetime.now(timezone.utc).timestamp()
                }
                
                articles.append({
                    'title': title,
                    'link': url,
                    'description': summary,
                    'image': image_url
                })
                
            except Exception as e:
                print(f"  ⚠️ Error parsing article: {e}")
                continue
        
        save_wlt_cache(cache)
        print(f"  ✅ Scraped {len(articles)} new WLT articles")
        return articles
        
    except Exception as e:
        print(f"  ❌ WLT scraping failed: {e}")
        return []


def fetch_feed_articles(feed: Dict[str, str], cutoff_date: datetime) -> List[Article]:
    """Fetch recent articles from a single feed"""
    articles = []
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; RSS Reader/1.0)'}
        parsed = feedparser.parse(feed['url'], request_headers=headers)
        
        for entry in parsed.entries:
            article = Article(entry, feed['title'], feed['html_url'], feed['url'])
            
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
    """Score articles with Claude API using interests and category rules"""
    if not articles:
        return []
    
    print(f"🤖 Scoring {len(articles)} articles with Claude...")
    
    # Load interests
    try:
        with open(CONFIG_DIR / 'scoring_interests.txt', 'r') as f:
            interests = f.read()
    except FileNotFoundError:
        print("❌ scoring_interests.txt not found")
        return articles
    
    # Build category guidance from rules
    category_guidance = "\n\nCATEGORY RULES (be strict with these):\n"
    for cat_key, rules in CATEGORY_RULES.items():
        category_guidance += f"\n{cat_key.upper()}:\n"
        category_guidance += f"  Description: {rules.get('description', '')}\n"
        if rules.get('include'):
            category_guidance += f"  MUST include: {', '.join(rules['include'])}\n"
        if rules.get('exclude'):
            category_guidance += f"  MUST exclude: {', '.join(rules['exclude'])}\n"
        if rules.get('is_default'):
            category_guidance += f"  This is the DEFAULT for everything else\n"
    
    category_guidance += """
IMPORTANT CATEGORIZATION RULES:
- Product reviews, consumer tips, phone accessories → "news"
- App recommendations, digital lifestyle → "news"  
- If unclear or doesn't fit well → "news"
- Be strict: only use specialized categories for clear matches
- "homelab" is for self-hosted infrastructure, NOT consumer gadgets
- "scifi" is ONLY for fiction/books, NOT tech lifestyle
"""
    
    # Load cache
    cache = load_scored_cache()
    client = anthropic.Anthropic(api_key=api_key)
    batch_size = 10
    scored_articles = []
    
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i+batch_size]
        
        # Check cache first
        uncached = []
        for article in batch:
            cache_key = f"{article.title}|{article.source}"
            if cache_key in cache:
                article.score = cache[cache_key]['score']
                article.category = cache[cache_key].get('category')
                scored_articles.append(article)
            else:
                uncached.append(article)
        
        if not uncached:
            continue
        
        article_list = "\n\n".join([
            f"Article {idx}:\nTitle: {a.title}\nSource: {a.source}\nDescription: {a.description[:200]}..."
            for idx, a in enumerate(uncached)
        ])
        
        prompt = f"""Score and categorize these articles based on the interests and category rules.

INTERESTS:
{interests}
{category_guidance}

Return JSON array with score (0-100) and category for each article:
[
  {{"score": 85, "category": "ai-tech"}},
  {{"score": 42, "category": "news"}},
  ...
]
Categories: local, ai-tech, climate, homelab, science, scifi, news

ARTICLES TO SCORE:
{article_list}"""
        
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                system=[
                    {
                        "type": "text",
                        "text": "You are an article scoring system. Return only valid JSON array. Be strict with categorization - when in doubt, use 'news'.",
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": interests + category_guidance,
                            "cache_control": {"type": "ephemeral"}
                        },
                        {
                            "type": "text",
                            "text": f"Score these articles:\n\n{article_list}"
                        }
                    ]
                }]
            )
            
            response_text = response.content[0].text.strip()
            
            if response_text.startswith('```'):
                response_text = '\n'.join(response_text.split('\n')[1:-1])
            
            scores_data = json.loads(response_text)
            
            for idx, article in enumerate(uncached):
                if idx < len(scores_data):
                    score_data = scores_data[idx]
                    article.score = score_data.get('score', 0)
                    article.category = score_data.get('category', 'news')
                    
                    cache_key = f"{article.title}|{article.source}"
                    cache[cache_key] = {
                        'score': article.score,
                        'category': article.category,
                        'timestamp': datetime.now(timezone.utc).timestamp()
                    }
                else:
                    article.score = 0
                    article.category = 'news'
                
                scored_articles.append(article)
            
        except Exception as e:
            print(f"  ⚠️ Batch scoring error: {e}")
            for article in uncached:
                article.score = 50
                article.category = 'news'
                scored_articles.append(article)
    
    save_scored_cache(cache)
    return scored_articles


def apply_diversity_limits(articles: List[Article], category: str) -> List[Article]:
    """Limit articles per source to ensure diversity"""
    if category == 'local':
        max_per_source = LIMITS['max_per_local']
    else:
        max_per_source = LIMITS['max_per_source']
    
    source_counts = defaultdict(int)
    diverse_articles = []
    
    sorted_articles = sorted(articles, key=lambda a: a.score, reverse=True)
    
    for article in sorted_articles:
        if source_counts[article.source] < max_per_source:
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
            "title": article.title,
            "content_html": article.description,
            "date_published": article.pub_date.isoformat(),
            "authors": [{"name": article.source, "url": article.source_url}]
        }
        
        if hasattr(article, 'image') and article.image:
            item["image"] = article.image
        
        if category == 'local':
            item["tags"] = ["local-priority"]
        
        feed["items"].append(item)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(feed, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated {category} feed: {len(feed['items'])} articles")


def generate_opml():
    """Generate OPML file with all category feeds"""
    import xml.etree.ElementTree as ET
    
    opml = ET.Element('opml', version='1.0')
    head = ET.SubElement(opml, 'head')
    ET.SubElement(head, 'title').text = "Erich's Curated Feeds"
    ET.SubElement(head, 'dateCreated').text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    body = ET.SubElement(opml, 'body')
    
    for cat_key, cat_config in CATEGORIES.items():
        feed_title = f"{cat_config['emoji']} {cat_config['name']}"
        feed_url = f"{FEEDS_CONFIG['base_url']}/feed-{cat_key}.json"
        
        ET.SubElement(body, 'outline', {
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
    new_articles = [a for a in unique_articles if a.url_hash not in shown_cache]
    print(f"🆕 New articles (not previously shown): {len(unique_articles)} → {len(new_articles)}")
    
    scored_articles = score_articles_with_claude(new_articles, api_key)
    
    quality_articles = [a for a in scored_articles if a.score >= LIMITS['min_claude_score']]
    print(f"⭐ Quality filter (score >= {LIMITS['min_claude_score']}): {len(scored_articles)} → {len(quality_articles)} articles")
    
    categorized = defaultdict(list)
    for article in quality_articles:
        category = article.category or 'news'
        categorized[category].append(article)
    
    print(f"\n📂 Categorization results:")
    for cat_key in CATEGORIES.keys():
        count = len(categorized[cat_key])
        print(f"  {cat_key}: {count} articles")
    
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
    
    new_shown = set(a.url_hash for a in quality_articles)
    shown_cache.update(new_shown)
    save_shown_cache(shown_cache)
    
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
