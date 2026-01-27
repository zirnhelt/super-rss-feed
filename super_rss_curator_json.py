#!/usr/bin/env python3
"""
Super RSS Curator with Caching, JSON Feed Output and Categorization
Now with smart caching to reduce API costs by 60-90%
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import List, Dict, Optional
import json
import hashlib
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import feedparser
import anthropic
import requests
from bs4 import BeautifulSoup

# Import configuration loader
from config_loader import (
    load_categories_config,
    load_feeds_config, 
    load_filters_config,
    load_limits_config,
    load_system_config
)

# Load all configuration
CATEGORIES = load_categories_config()
FEEDS_CONFIG = load_feeds_config()
FILTERS = load_filters_config()
LIMITS = load_limits_config()
SYSTEM = load_system_config()


def load_scored_cache():
    """Load cached article scores"""
    cache_file = SYSTEM['cache_files']['scored_articles']
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_scored_cache(cache):
    """Save article scores to cache"""
    cache_file = SYSTEM['cache_files']['scored_articles']
    with open(cache_file, 'w') as f:
        json.dump(cache, f, indent=2)


def is_cache_valid(timestamp, expiry_hours):
    """Check if cached score is still valid"""
    cache_age = datetime.now(timezone.utc).timestamp() - timestamp
    return cache_age < (expiry_hours * 3600)


class Article:
    """Represents a single article"""
    def __init__(self, entry, source_title: str, source_url: str):
        self.title = entry.get('title', '').strip()
        self.link = entry.get('link', '').strip()
        self.description = entry.get('description', '') or entry.get('summary', '')
        self.pub_date = self._parse_date(entry)
        self.source = source_title
        self.source_url = source_url
        self.score = 0
        self.category = None
        self.image_url = None
        
        # Generate hash for deduplication
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


def scrape_williams_lake_tribune():
    """Scrape Williams Lake Tribune since they don't have RSS"""
    print("📰 Scraping Williams Lake Tribune...")
    articles = []
    
    cache_file = SYSTEM['cache_files']['wlt']
    
    # Try to load from cache first
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
                # Check if cache is less than 1 hour old
                cache_time = datetime.fromisoformat(cached['timestamp'])
                if datetime.now(timezone.utc) - cache_time < timedelta(hours=1):
                    print(f"  ✓ Using cached WLT data ({len(cached['articles'])} articles)")
                    return [Article(a, "Williams Lake Tribune", SYSTEM['urls']['wlt_base']) 
                            for a in cached['articles']]
        except:
            pass
    
    # Scrape fresh data
    try:
        response = requests.get(SYSTEM['urls']['wlt_news'], timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        article_entries = []
        for article in soup.find_all('article', class_='post'):
            title_elem = article.find('h2', class_='entry-title')
            if not title_elem:
                continue
            
            link = title_elem.find('a')
            if not link:
                continue
            
            title = title_elem.get_text().strip()
            url = link.get('href', '')
            
            # Get excerpt
            excerpt_elem = article.find('div', class_='entry-content')
            description = excerpt_elem.get_text().strip() if excerpt_elem else ""
            
            # Get date
            date_elem = article.find('time', class_='entry-date')
            date_str = date_elem.get('datetime', '') if date_elem else ''
            
            entry_dict = {
                'title': title,
                'link': url,
                'description': description
            }
            
            if date_str:
                try:
                    pub_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    entry_dict['published_parsed'] = pub_date.timetuple()
                except:
                    pass
            
            article_entries.append(entry_dict)
            
            # Create Article object for deduplication
            article_obj = Article(entry_dict, "Williams Lake Tribune", SYSTEM['urls']['wlt_base'])
            articles.append(article_obj)
        
        # Save to cache
        cache_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'articles': article_entries
        }
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        print(f"  ✓ Scraped {len(articles)} articles from Williams Lake Tribune")
        
    except Exception as e:
        print(f"  ✗ Error scraping WLT: {e}")
    
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


def deduplicate_articles(articles: List[Article]) -> List[Article]:
    """Remove duplicate articles using URL and fuzzy title matching"""
    from fuzzywuzzy import fuzz
    
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
    
    # Load cache
    cache = load_scored_cache()
    expiry_hours = SYSTEM['cache_expiry']['scored_hours']
    
    # Separate cached vs new articles
    articles_to_score = []
    cached_articles = []
    
    for article in articles:
        cache_key = article.url_hash
        
        if cache_key in cache and is_cache_valid(cache[cache_key]['timestamp'], expiry_hours):
            article.score = cache[cache_key]['score']
            article.category = cache[cache_key].get('category')
            cached_articles.append(article)
        else:
            articles_to_score.append(article)
    
    print(f"\n📊 Scoring status:")
    print(f"  - Using cached: {len(cached_articles)} articles")
    print(f"  - Need scoring: {len(articles_to_score)} articles")
    
    if not articles_to_score:
        return cached_articles
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Load interests from config
    with open('config/scoring_interests.txt', 'r') as f:
        interests = f.read()
    
    print(f"🤖 Scoring {len(articles_to_score)} new articles with Claude...")
    
    # Batch articles for efficiency (10 at a time)
    batch_size = 10
    scored_new = []
    
    for i in range(0, len(articles_to_score), batch_size):
        batch = articles_to_score[i:i+batch_size]
        
        # Prepare batch for Claude
        article_list = "\n\n".join([
            f"Article {idx}:\nTitle: {a.title}\nSource: {a.source}\nDescription: {a.description[:300]}..."
            for idx, a in enumerate(batch)
        ])
        
        prompt = f"""Score these articles for relevance to my interests. Return ONLY a JSON array with scores and categories.

MY INTERESTS:
{interests}

ARTICLES:
{article_list}

Return format (VALID JSON ONLY):
[
  {{"score": 85, "category": "ai-tech"}},
  {{"score": 42, "category": "news"}},
  ...
]

Categories: local, ai-tech, climate, homelab, science, scifi, news"""
        
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                system=[
                    {
                        "type": "text",
                        "text": "You are an article scoring system. Return only valid JSON.",
                        "cache_control": {"type": "ephemeral"}
                    }
                ],
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": interests,
                            "cache_control": {"type": "ephemeral"}
                        },
                        {
                            "type": "text",
                            "text": f"Score these articles:\n\n{article_list}"
                        }
                    ]
                }]
            )
            
            # Parse JSON response
            response_text = response.content[0].text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            scores_data = json.loads(response_text)
            
            for article, score_data in zip(batch, scores_data):
                article.score = score_data['score']
                article.category = score_data.get('category', 'news')
                scored_new.append(article)
                
                # Update cache
                cache[article.url_hash] = {
                    'title': article.title,
                    'score': article.score,
                    'category': article.category,
                    'timestamp': datetime.now(timezone.utc).timestamp()
                }
        
        except Exception as e:
            print(f"  ⚠ Scoring error: {e}")
            # Assign default scores on error
            for article in batch:
                article.score = 50
                article.category = 'news'
                scored_new.append(article)
                
                cache[article.url_hash] = {
                    'title': article.title,
                    'score': 50,
                    'category': 'news',
                    'timestamp': datetime.now(timezone.utc).timestamp()
                }
    
    # Save updated cache
    save_scored_cache(cache)
    
    return cached_articles + scored_new


def scrape_article_image(url: str) -> Optional[str]:
    """Attempt to scrape article image from page"""
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try Open Graph image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
        
        # Try Twitter card image
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']
        
        # Try first large image in article
        article_elem = soup.find('article') or soup.find('div', class_='article')
        if article_elem:
            img = article_elem.find('img')
            if img and img.get('src'):
                img_src = img['src']
                # Make absolute URL if needed
                if img_src.startswith('//'):
                    img_src = 'https:' + img_src
                elif img_src.startswith('/'):
                    parsed = urlparse(url)
                    img_src = f"{parsed.scheme}://{parsed.netloc}{img_src}"
                return img_src
    except:
        pass
    
    return None


def load_shown_articles_cache():
    """Load cache of previously shown articles"""
    cache_file = SYSTEM['cache_files']['shown_articles']
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_shown_articles_cache(cache):
    """Save cache of shown articles"""
    cache_file = SYSTEM['cache_files']['shown_articles']
    # Keep only last 14 days
    cutoff = (datetime.now(timezone.utc) - timedelta(days=SYSTEM['cache_expiry']['shown_days'])).timestamp()
    cleaned = {k: v for k, v in cache.items() if float(v) > cutoff}
    
    with open(cache_file, 'w') as f:
        json.dump(cleaned, f, indent=2)


def filter_shown_articles(articles: List[Article]) -> List[Article]:
    """Remove articles that were shown in recent feeds"""
    shown_cache = load_shown_articles_cache()
    
    new_articles = []
    for article in articles:
        if article.url_hash not in shown_cache:
            new_articles.append(article)
            shown_cache[article.url_hash] = datetime.now(timezone.utc).timestamp()
    
    save_shown_articles_cache(shown_cache)
    
    if len(new_articles) < len(articles):
        print(f"🔄 Filtered {len(articles) - len(new_articles)} previously shown articles")
    
    return new_articles


def apply_diversity_limits(articles: List[Article], category: str) -> List[Article]:
    """Limit articles per source to ensure diversity"""
    source_counts = defaultdict(int)
    diverse_articles = []
    
    # Sort by score first
    sorted_articles = sorted(articles, key=lambda a: a.score, reverse=True)
    
    # Determine max per source based on category
    if category == 'local':
        max_per_source = LIMITS['max_per_local']
    else:
        max_per_source = LIMITS['max_per_source']
    
    for article in sorted_articles:
        if source_counts[article.source] < max_per_source:
            diverse_articles.append(article)
            source_counts[article.source] += 1
    
    return diverse_articles


def generate_json_feed(articles: List[Article], category: str, output_path: str):
    """Generate JSON Feed format output"""
    
    cat_config = CATEGORIES[category]
    feed_config = FEEDS_CONFIG['feeds'][category]
    
    feed = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": f"{cat_config['emoji']} {cat_config['name']}",
        "home_page_url": FEEDS_CONFIG['base_url'],
        "feed_url": f"{FEEDS_CONFIG['base_url']}/{output_path}",
        "description": feed_config['description'],
        "authors": [{"name": FEEDS_CONFIG['author']}],
        "language": "en-US",
        "items": []
    }
    
    for article in articles:
        item = {
            "id": article.link,
            "url": article.link,
            "title": article.title,
            "content_html": article.description,
            "date_published": article.pub_date.isoformat(),
            "authors": [{"name": article.source}],
            "_score": article.score
        }
        
        if article.image_url:
            item["image"] = article.image_url
        
        feed["items"].append(item)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(feed, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated {output_path} ({len(articles)} articles)")


def generate_opml_file(output_path: str):
    """Generate OPML file with all category feeds"""
    opml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<opml version="1.0">',
        '<head>',
        '<title>Erich\'s Curated Feeds</title>',
        f'<dateCreated>{datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")}</dateCreated>',
        '</head>',
        '<body>'
    ]
    
    for cat_key, cat_config in CATEGORIES.items():
        feed_url = f"{FEEDS_CONFIG['base_url']}/feed-{cat_key}.json"
        opml_lines.append(
            f'    <outline type="rss" text="{cat_config["emoji"]} {cat_config["name"]}" '
            f'title="{cat_config["emoji"]} {cat_config["name"]}" '
            f'xmlUrl="{feed_url}" htmlUrl="{FEEDS_CONFIG["base_url"]}" />'
        )
    
    opml_lines.extend(['</body>', '</opml>'])
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(opml_lines))
    
    print(f"✅ Generated {output_path}")


def main():
    """Main curation workflow"""
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    # Parse OPML
    opml_path = sys.argv[1] if len(sys.argv) > 1 else 'feeds.opml'
    feeds = parse_opml(opml_path)
    
    # Fetch articles
    cutoff_date = datetime.now(timezone.utc) - timedelta(hours=SYSTEM['lookback_hours'])
    print(f"\n📥 Fetching articles from last {SYSTEM['lookback_hours']} hours...")
    
    all_articles = []
    
    # Scrape Williams Lake Tribune first
    wlt_articles = scrape_williams_lake_tribune()
    all_articles.extend(wlt_articles)
    
    # Fetch from RSS feeds
    for feed in feeds:
        articles = fetch_feed_articles(feed, cutoff_date)
        all_articles.extend(articles)
    
    print(f"\n📈 Total fetched: {len(all_articles)} articles")
    
    # Deduplicate
    unique_articles = deduplicate_articles(all_articles)
    
    # Filter previously shown
    new_articles = filter_shown_articles(unique_articles)
    
    # Score with Claude (with caching!)
    scored_articles = score_articles_with_claude(new_articles, api_key)
    
    # Categorize articles
    categorized = defaultdict(list)
    for article in scored_articles:
        # Local articles always priority
        if article.source == "Williams Lake Tribune":
            article.category = 'local'
            article.score = LIMITS['local_priority_score']
        
        if article.category:
            categorized[article.category].append(article)
    
    # Generate feeds for each category
    print(f"\n📝 Generating category feeds...")
    
    for category, articles in categorized.items():
        if not articles:
            continue
        
        # Filter by minimum score (except local)
        if category != 'local':
            articles = [a for a in articles if a.score >= LIMITS['min_claude_score']]
        
        # Apply diversity limits
        diverse = apply_diversity_limits(articles, category)
        
        # Limit feed size
        limited = diverse[:LIMITS['max_feed_size']]
        
        # Scrape images for high-scoring articles
        for article in limited[:10]:  # Top 10 only
            if article.score >= 70 and not article.image_url:
                article.image_url = scrape_article_image(article.link)
        
        # Generate JSON feed
        output_file = f"feed-{category}.json"
        generate_json_feed(limited, category, output_file)
    
    # Generate OPML
    generate_opml_file('curated-feeds.opml')
    
    # Stats
    print("\n📊 Final stats:")
    for category, articles in categorized.items():
        print(f"  {CATEGORIES[category]['emoji']} {category}: {len(articles)} articles")


if __name__ == '__main__':
    main()
