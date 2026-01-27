#!/usr/bin/env python3
"""
Super RSS Curator with JSON Feed Output and Categorization
Fixes: timestamp preservation, improved sports filtering, better Claude categorization
"""

import os
import sys
import json
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import List, Dict, Optional
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import anthropic

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

class Article:
    """Represents a single article with metadata"""
    
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
        """Parse publication date from entry, preserving original timestamp"""
        # Try multiple date fields in order of preference
        date_fields = ['published_parsed', 'updated_parsed']
        
        for field in date_fields:
            if hasattr(entry, field) and getattr(entry, field):
                parsed_time = getattr(entry, field)
                if parsed_time:
                    try:
                        return datetime(*parsed_time[:6], tzinfo=timezone.utc)
                    except (ValueError, TypeError):
                        continue
        
        # Try string parsing as fallback
        date_strings = [entry.get('published'), entry.get('updated')]
        for date_str in date_strings:
            if date_str:
                try:
                    # Parse common RSS date formats
                    from email.utils import parsedate_to_datetime
                    return parsedate_to_datetime(date_str)
                except (ValueError, TypeError):
                    continue
        
        # Fallback to current time if no date found
        return datetime.now(timezone.utc)
    
    def should_filter(self) -> bool:
        """Enhanced filtering with better sports detection"""
        text = f"{self.title} {self.description}".lower()
        source_lower = self.source.lower()
        
        # Check blocked sources
        if any(blocked in source_lower for blocked in FILTERS['blocked_sources']):
            return True
        
        # Enhanced sports filtering - look for multiple sports indicators
        sports_indicators = [
            'hockey', 'basketball', 'football', 'soccer', 'baseball',
            'tournament', 'playoff', 'championship', 'final score',
            'overtime', 'goal scorer', 'assist', 'penalty', 'game recap',
            'blazers', 'canucks', 'lions', 'whitecaps', 'junior hockey',
            'whl', 'nhl', 'nba', 'nfl', 'mlb', 'arena', 'stadium'
        ]
        
        sports_count = sum(1 for indicator in sports_indicators if indicator in text)
        
        # If multiple sports indicators or clear sports context, filter it
        if sports_count >= 2 or any(clear_sport in text for clear_sport in ['final score', 'game recap', 'overtime']):
            return True
        
        # General keyword filtering
        if any(keyword in text for keyword in FILTERS['blocked_keywords']):
            return True
        
        return False
    
    def to_json_item(self) -> Dict:
        """Convert to JSON Feed item format with preserved timestamp"""
        return {
            "id": self.url_hash,
            "url": self.link,
            "title": self.title,
            "content_html": self.description,
            "summary": self.description[:200] + "..." if len(self.description) > 200 else self.description,
            "date_published": self.pub_date.isoformat(),  # Preserve original timestamp
            "authors": [{"name": self.source, "url": self.source_url}],
            "_ai_score": self.score,
            "_category": self.category,
            "_image": self.image_url
        }


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


def fetch_wlt_articles(base_url: str, cutoff_date: datetime) -> List[Article]:
    """Fetch articles from Williams Lake Tribune scraper"""
    print(f"  🏔️  Fetching Williams Lake Tribune articles...")
    
    # Load existing cache
    cache = load_cache(SYSTEM['cache_files']['wlt'])
    cached_articles = []
    
    try:
        response = requests.get(f"{base_url}/news/", timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('article', class_='post')
        
        if not articles:
            print(f"    ⚠️  No articles found with expected structure")
            return cached_articles
        
        for article_elem in articles:
            try:
                title_elem = article_elem.find('h2') or article_elem.find('h3')
                link_elem = title_elem.find('a') if title_elem else None
                
                if not link_elem:
                    continue
                
                title = link_elem.get_text(strip=True)
                relative_url = link_elem.get('href', '')
                
                if relative_url.startswith('/'):
                    full_url = base_url + relative_url
                else:
                    full_url = relative_url
                
                # Create mock entry for Article class
                mock_entry = {
                    'title': title,
                    'link': full_url,
                    'description': f'Local news from Williams Lake Tribune: {title}',
                    'published_parsed': None  # Will use current time
                }
                
                article = Article(mock_entry, "Williams Lake Tribune", base_url)
                
                # Skip if too old (though for WLT we're more permissive)
                if article.pub_date < cutoff_date - timedelta(hours=24):
                    continue
                
                cached_articles.append(article)
                
                # Cache this article
                cache[article.url_hash] = {
                    'title': article.title,
                    'url': article.link,
                    'timestamp': article.pub_date.timestamp(),
                    'score': LIMITS['local_priority_score']  # Always high priority
                }
                
            except Exception as e:
                print(f"      ⚠️  Error parsing article: {e}")
                continue
        
        # Save updated cache
        save_cache(SYSTEM['cache_files']['wlt'], cache)
        
        print(f"    ✅ Williams Lake Tribune: {len(cached_articles)} articles")
        
    except Exception as e:
        print(f"    ❌ Williams Lake Tribune error: {e}")
    
    return cached_articles


def fetch_feed_articles(feed: Dict[str, str], cutoff_date: datetime) -> List[Article]:
    """Fetch recent articles from a single RSS feed"""
    articles = []
    
    try:
        # Handle special case for Williams Lake Tribune
        if 'wltribune.com' in feed.get('html_url', ''):
            return fetch_wlt_articles(SYSTEM['urls']['wlt_base'], cutoff_date)
        
        parsed = feedparser.parse(feed['url'])
        
        if not parsed.entries:
            print(f"    ⚠️  No entries found in feed")
            return articles
        
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
    
    print(f"🔄 Deduplication: {len(articles)} → {len(unique)} articles")
    return unique


def load_cache(cache_file: str) -> Dict:
    """Load cache from JSON file"""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return {}


def save_cache(cache_file: str, cache_data: Dict):
    """Save cache to JSON file"""
    try:
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        print(f"⚠️  Cache save error: {e}")


def score_and_categorize_articles_with_claude(articles: List[Article], api_key: str) -> List[Article]:
    """Score and categorize articles using Claude API with caching"""
    client = anthropic.Anthropic(api_key=api_key)
    
    # Load scoring cache
    cache = load_cache(SYSTEM['cache_files']['scored_articles'])
    cache_expiry = datetime.now().timestamp() - (SYSTEM['cache_expiry']['scored_hours'] * 3600)
    
    # Separate cached and new articles
    cached_articles = []
    new_articles = []
    
    for article in articles:
        cache_key = f"{article.url_hash}_{article.title_normalized[:50]}"
        
        if (cache_key in cache and 
            cache[cache_key].get('timestamp', 0) > cache_expiry and
            cache[cache_key].get('score') is not None and
            cache[cache_key].get('category') is not None):
            
            article.score = cache[cache_key]['score']
            article.category = cache[cache_key]['category']
            cached_articles.append(article)
        else:
            new_articles.append(article)
    
    print(f"🤖 Processing: {len(cached_articles)} cached, {len(new_articles)} new articles")
    
    if not new_articles:
        return articles
    
    # Load interests from config file
    with open('config/scoring_interests.txt', 'r') as f:
        interests = f.read()
    
    # Batch articles for efficiency (6 at a time for better context)
    batch_size = 6
    
    for i in range(0, len(new_articles), batch_size):
        batch = new_articles[i:i+batch_size]
        
        # Prepare batch for Claude with enhanced context
        article_list = "\n\n".join([
            f"Article {idx}:\nTitle: {a.title}\nSource: {a.source}\nDescription: {a.description[:300]}..."
            for idx, a in enumerate(batch)
        ])
        
        prompt = f"""Analyze these articles and provide both SCORES (0-100) and CATEGORIES.

My interests and scoring guidance:
{interests}

Available categories:
- local: Williams Lake, Cariboo, Quesnel regional news and events
- ai-tech: AI/ML, software development, tech platforms, infrastructure
- climate: Climate tech, renewable energy, sustainability, environmental
- homelab: 3D printing, home automation, self-hosting, DIY tech
- science: Research, studies, scientific discoveries, data analysis
- scifi: Science fiction, fantasy, books, worldbuilding, culture
- news: General news, politics, business, current events

Articles to analyze:
{article_list}

Instructions:
- Williams Lake/Cariboo content should score 80+ and be categorized as 'local'
- AI articles need clear AI/ML focus, not just mentioning AI in passing
- Be precise with categories - don't put general news in specialized categories
- Score based on depth and relevance to my interests
- Technical content and systems thinking boost scores

Return ONLY two lines:
SCORES: 85,42,91,15,73,60
CATEGORIES: local,news,ai-tech,climate,science,homelab

No other text or explanations."""
        
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            lines = response_text.split('\n')
            
            scores_line = None
            categories_line = None
            
            for line in lines:
                if line.startswith('SCORES:'):
                    scores_line = line.replace('SCORES:', '').strip()
                elif line.startswith('CATEGORIES:'):
                    categories_line = line.replace('CATEGORIES:', '').strip()
            
            if scores_line and categories_line:
                scores = [int(s.strip()) for s in scores_line.split(',')]
                categories = [c.strip() for c in categories_line.split(',')]
                
                # Update articles and cache
                for article, score, category in zip(batch, scores, categories):
                    article.score = score
                    article.category = category
                    cache_key = f"{article.url_hash}_{article.title_normalized[:50]}"
                    cache[cache_key] = {
                        'title': article.title,
                        'score': score,
                        'category': category,
                        'timestamp': datetime.now().timestamp()
                    }
            else:
                # Fallback if parsing fails
                for article in batch:
                    article.score = 50
                    article.category = 'news'
        
        except Exception as e:
            print(f"  ⚠️ Processing error: {e}")
            # Assign default values on error
            for article in batch:
                article.score = 50
                article.category = 'news'
    
    # Save updated cache
    save_cache(SYSTEM['cache_files']['scored_articles'], cache)
    
    return articles


def apply_diversity_limits(articles: List[Article]) -> List[Article]:
    """Apply per-source limits with special handling for local content"""
    source_counts = defaultdict(int)
    diverse_articles = []
    
    # Sort by score first
    sorted_articles = sorted(articles, key=lambda a: a.score, reverse=True)
    
    for article in sorted_articles:
        # Determine limit based on category
        if article.category == 'local':
            max_per_source = LIMITS['max_per_local']
        else:
            max_per_source = LIMITS['max_per_source']
        
        if source_counts[article.source] < max_per_source:
            diverse_articles.append(article)
            source_counts[article.source] += 1
    
    print(f"📊 Diversity filter: {len(articles)} → {len(diverse_articles)} articles")
    return diverse_articles


def categorize_articles(articles: List[Article]) -> Dict[str, List[Article]]:
    """Group articles by category"""
    categorized = defaultdict(list)
    
    for article in articles:
        # Ensure category is valid
        if article.category not in CATEGORIES:
            article.category = 'news'
        
        categorized[article.category].append(article)
    
    # Print category summary
    print("\n📑 Category distribution:")
    for category, article_list in categorized.items():
        config = CATEGORIES[category]
        print(f"  {config['emoji']} {config['name']}: {len(article_list)} articles")
    
    return categorized


def generate_json_feeds(categorized_articles: Dict[str, List[Article]]):
    """Generate JSON Feed files for each category with preserved timestamps"""
    print("\n📄 Generating JSON feeds...")
    
    for category, articles in categorized_articles.items():
        if not articles:
            continue
        
        category_config = CATEGORIES[category]
        feed_config = FEEDS_CONFIG['feeds'][category]
        
        # Sort articles by score, then by publication date (newest first)
        sorted_articles = sorted(
            articles,
            key=lambda a: (a.score, a.pub_date.timestamp()),
            reverse=True
        )
        
        # Limit feed size
        limited_articles = sorted_articles[:LIMITS['max_feed_size']]
        
        # Generate JSON Feed
        json_feed = {
            "version": "https://jsonfeed.org/version/1.1",
            "title": f"{category_config['emoji']} {category_config['name']}",
            "description": feed_config['description'],
            "home_page_url": FEEDS_CONFIG['base_url'],
            "feed_url": f"{FEEDS_CONFIG['base_url']}/feed-{category}.json",
            "author": {
                "name": FEEDS_CONFIG['author']
            },
            "items": [article.to_json_item() for article in limited_articles]
        }
        
        # Save to file
        output_file = f"feed-{category}.json"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_feed, f, indent=2, ensure_ascii=False)
            
            print(f"  ✅ {output_file}: {len(limited_articles)} articles")
            
        except Exception as e:
            print(f"  ❌ Error saving {output_file}: {e}")


def generate_opml_feed():
    """Generate OPML file for the curated feeds"""
    print("\n📋 Generating OPML feed...")
    
    opml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<opml version="1.0">',
        '<head>',
        f'<title>Erich\'s Curated Feeds</title>',
        f'<dateCreated>{datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")}</dateCreated>',
        '</head>',
        '<body>'
    ]
    
    # Add feeds in priority order
    priority_order = ['local', 'homelab', 'climate', 'science', 'ai-tech', 'scifi', 'news']
    
    for category in priority_order:
        if category in CATEGORIES:
            config = CATEGORIES[category]
            opml_lines.append(
                f'    <outline type="rss" text="{config["emoji"]} {config["name"]}" '
                f'title="{config["emoji"]} {config["name"]}" '
                f'xmlUrl="{FEEDS_CONFIG["base_url"]}/feed-{category}.json" '
                f'htmlUrl="{FEEDS_CONFIG["base_url"]}" />'
            )
    
    opml_lines.extend([
        '</body>',
        '</opml>'
    ])
    
    with open('curated-feeds.opml', 'w', encoding='utf-8') as f:
        f.write('\n'.join(opml_lines))
    
    print("✅ Generated curated-feeds.opml")


def clean_old_feeds():
    """Remove articles older than retention period from feeds"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=LIMITS['feed_retention_days'])
    cutoff_timestamp = cutoff.timestamp()
    
    print(f"🧹 Cleaning articles older than {LIMITS['feed_retention_days']} days...")
    
    for category in CATEGORIES.keys():
        feed_file = f"feed-{category}.json"
        if os.path.exists(feed_file):
            try:
                with open(feed_file, 'r') as f:
                    feed_data = json.load(f)
                
                original_count = len(feed_data.get('items', []))
                
                # Filter out old articles
                fresh_items = []
                for item in feed_data.get('items', []):
                    try:
                        item_date = datetime.fromisoformat(item['date_published'].replace('Z', '+00:00'))
                        if item_date.timestamp() > cutoff_timestamp:
                            fresh_items.append(item)
                    except (ValueError, KeyError):
                        # Keep items with unparseable dates
                        fresh_items.append(item)
                
                feed_data['items'] = fresh_items
                
                with open(feed_file, 'w', encoding='utf-8') as f:
                    json.dump(feed_data, f, indent=2, ensure_ascii=False)
                
                if original_count != len(fresh_items):
                    print(f"  🗑️  {category}: {original_count} → {len(fresh_items)} articles")
                
            except Exception as e:
                print(f"  ⚠️  Error cleaning {feed_file}: {e}")


def main():
    """Main workflow"""
    print("🎯 Super RSS Feed Curator with JSON Output")
    print("=" * 60)
    
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
    for feed in feeds:
        articles = fetch_feed_articles(feed, cutoff_date)
        all_articles.extend(articles)
    
    print(f"\n📈 Total fetched: {len(all_articles)} articles")
    
    # Deduplicate
    unique_articles = deduplicate_articles(all_articles)
    
    # Score and categorize with Claude
    processed_articles = score_and_categorize_articles_with_claude(unique_articles, api_key)
    
    # Filter by minimum score
    quality_articles = [a for a in processed_articles if a.score >= LIMITS['min_claude_score']]
    print(f"⭐ Quality filter (score >= {LIMITS['min_claude_score']}): {len(processed_articles)} → {len(quality_articles)} articles")
    
    # Apply diversity limits
    diverse_articles = apply_diversity_limits(quality_articles)
    
    # Categorize articles
    categorized_articles = categorize_articles(diverse_articles)
    
    # Clean old feeds
    clean_old_feeds()
    
    # Generate JSON feeds
    generate_json_feeds(categorized_articles)
    
    # Generate OPML
    generate_opml_feed()
    
    # Final stats
    print(f"\n📊 Final stats:")
    print(f"  Total sources: {len(feeds)}")
    print(f"  Articles fetched: {len(all_articles)}")
    print(f"  After dedup: {len(unique_articles)}")
    print(f"  After scoring: {len(quality_articles)}")
    print(f"  Final output: {len(diverse_articles)}")
    print(f"  Categories: {len(categorized_articles)}")
    
    print("\n✅ RSS feed generation complete!")


if __name__ == '__main__':
    main()