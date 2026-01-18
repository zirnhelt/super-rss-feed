#!/usr/bin/env python3
"""
Super RSS Feed Curator (Cached JSON Feed Edition)
Aggregates feeds from OPML, deduplicates, scores with Claude, outputs JSON Feed format
Includes smart caching to avoid re-scoring the same articles multiple times per day
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
import hashlib
import json

import feedparser
from fuzzywuzzy import fuzz
import anthropic

# Configuration
MAX_ARTICLES_OUTPUT = 250
MAX_PER_SOURCE = 5  # Default limit per source
LOOKBACK_HOURS = 48  # How far back to fetch articles
MIN_CLAUDE_SCORE = 30  # Minimum relevance score (0-100)

# Caching configuration
SCORED_CACHE_FILE = 'scored_articles_cache.json'
CACHE_EXPIRY_HOURS = 6  # Don't re-score articles for 6 hours

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
    def __init__(self, entry, source_title: str, source_url: str):
        self.title = entry.get('title', '').strip()
        self.link = entry.get('link', '').strip()
        self.description = entry.get('description', '') or entry.get('summary', '')
        self.pub_date = self._parse_date(entry)
        self.source = source_title
        self.source_url = source_url
        self.score = 0
        
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
        """Check if article should be filtered out"""
        text = f"{self.title} {self.description}".lower()
        
        # Check blocked sources
        source_lower = self.source.lower()
        if any(blocked in source_lower for blocked in BLOCKED_SOURCES):
            return True
        
        # Check blocked keywords
        if any(keyword in text for keyword in BLOCKED_KEYWORDS):
            return True
        
        return False


def load_scored_cache() -> Dict[str, Dict]:
    """Load previously scored articles from cache"""
    try:
        with open(SCORED_CACHE_FILE, 'r') as f:
            cache = json.load(f)
            print(f"📁 Loaded {len(cache)} articles from cache")
            return cache
    except FileNotFoundError:
        print("📁 No cache file found, starting fresh")
        return {}
    except Exception as e:
        print(f"⚠ Cache load error: {e}, starting fresh")
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
        print(f"💾 Saved cache with {len(cleaned_cache)} articles" + 
              (f" (removed {removed} old entries)" if removed > 0 else ""))
    except Exception as e:
        print(f"⚠ Cache save error: {e}")


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
    """Score articles using Claude API with smart caching"""
    
    # Load cache
    cache = load_scored_cache()
    
    # Separate cached vs new articles
    cached_articles = []
    new_articles = []
    cache_hits = 0
    
    for article in articles:
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
    
    # Return all articles (cached + newly scored)
    all_articles = cached_articles + new_articles
    return all_articles


def apply_diversity_limits(articles: List[Article], max_per_source: int) -> List[Article]:
    """Limit articles per source to ensure diversity"""
    source_counts = defaultdict(int)
    diverse_articles = []
    
    # Sort by score first
    sorted_articles = sorted(articles, key=lambda a: a.score, reverse=True)
    
    for article in sorted_articles:
        if source_counts[article.source] < max_per_source:
            diverse_articles.append(article)
            source_counts[article.source] += 1
    
    print(f"📊 Diversity filter: {len(articles)} → {len(diverse_articles)} articles")
    return diverse_articles


def generate_json_feed(articles: List[Article], output_path: str):
    """Generate JSON Feed file with prominent source attribution"""
    
    feed_data = {
        "version": "https://jsonfeed.org/version/1.1",
        "title": "Curated Feed",  # Shorter, less prominent title
        "home_page_url": "https://github.com/zirnhelt/super-rss-feed",
        "feed_url": f"https://zirnhelt.github.io/super-rss-feed/{output_path}",
        "description": "AI-curated articles from trusted sources",
        "authors": [{"name": "Erich's AI Curator"}],
        "items": []
    }
    
    for article in articles[:MAX_ARTICLES_OUTPUT]:
        # Create prominent source-first title
        item_title = f"[{article.source}] {article.title}"
        
        # Rich metadata for better reader display
        item = {
            "id": article.link,
            "url": article.link,
            "title": item_title,  # Source-prominent title
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
                "relevance": "high" if article.score >= 70 else "medium"
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
    
    # Fetch articles
    cutoff_date = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    print(f"\n🔥 Fetching articles from last {LOOKBACK_HOURS} hours...")
    
    all_articles = []
    for feed in feeds:
        articles = fetch_feed_articles(feed, cutoff_date)
        all_articles.extend(articles)
    
    print(f"\n📈 Total fetched: {len(all_articles)} articles")
    
    # Deduplicate
    unique_articles = deduplicate_articles(all_articles)
    
    # Score with Claude (using cache)
    scored_articles = score_articles_with_claude(unique_articles, api_key)
    
    # Filter by minimum score
    quality_articles = [a for a in scored_articles if a.score >= MIN_CLAUDE_SCORE]
    print(f"⭐ Quality filter (score >= {MIN_CLAUDE_SCORE}): {len(scored_articles)} → {len(quality_articles)} articles")
    
    # Apply diversity limits
    diverse_articles = apply_diversity_limits(quality_articles, MAX_PER_SOURCE)
    
    # Generate JSON feed
    output_path = 'super-feed.json'
    generate_json_feed(diverse_articles, output_path)
    
    # Stats
    print("\n📊 Final stats:")
    print(f"  Total sources: {len(feeds)}")
    print(f"  Articles fetched: {len(all_articles)}")
    print(f"  After dedup: {len(unique_articles)}")
    print(f"  After scoring: {len(quality_articles)}")
    print(f"  Final output: {min(len(diverse_articles), MAX_ARTICLES_OUTPUT)}")


if __name__ == '__main__':
    main()
