#!/usr/bin/env python3
"""
Super RSS Feed Curator
Aggregates feeds from OPML, deduplicates, scores with Claude, applies diversity filters
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
import hashlib

import feedparser
from feedgen.feed import FeedGenerator
from fuzzywuzzy import fuzz
import anthropic

# Configuration
MAX_ARTICLES_OUTPUT = 250
MAX_PER_SOURCE = 5  # Default limit per source
LOOKBACK_HOURS = 48  # How far back to fetch articles
MIN_CLAUDE_SCORE = 30  # Minimum relevance score (0-100)

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
        if any(blocked in source_lower for blocked in BLOCKED_SOURCES):
            return True
        
        # Check blocked keywords
        if any(keyword in text for keyword in BLOCKED_KEYWORDS):
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
    """Score articles using Claude API"""
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
    
    print(f"🤖 Scoring {len(articles)} articles with Claude...")
    
    # Batch articles for efficiency (10 at a time)
    batch_size = 10
    scored_articles = []
    
    for i in range(0, len(articles), batch_size):
        batch = articles[i:i+batch_size]
        
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
            
            for article, score in zip(batch, scores):
                article.score = score
                scored_articles.append(article)
        
        except Exception as e:
            print(f"  ⚠ Scoring error: {e}")
            # Assign default scores on error
            for article in batch:
                article.score = 50
                scored_articles.append(article)
    
    return scored_articles


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


def generate_rss_feed(articles: List[Article], output_path: str):
    """Generate RSS XML file"""
    fg = FeedGenerator()
    fg.title("Erich's Curated Super Feed")
    fg.link(href="https://github.com/your-username/super-rss-feed", rel="alternate")
    fg.description("AI-curated RSS aggregator from 50+ sources")
    fg.language("en")
    fg.lastBuildDate(datetime.now(timezone.utc))
    
    for article in articles[:MAX_ARTICLES_OUTPUT]:
        fe = fg.add_entry()
        fe.title(article.title)
        fe.link(href=article.link)
        fe.description(f"{article.description}<br><br><em>Source: {article.source} | Score: {article.score}</em>")
        fe.published(article.pub_date)
        fe.author(name=article.source)
    
    fg.rss_file(output_path)
    print(f"✅ Generated RSS feed: {output_path} ({len(articles[:MAX_ARTICLES_OUTPUT])} articles)")


def main():
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    # Parse OPML
    opml_path = sys.argv[1] if len(sys.argv) > 1 else 'feeds.opml'
    feeds = parse_opml(opml_path)
    
    # Fetch articles
    cutoff_date = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    print(f"\n📥 Fetching articles from last {LOOKBACK_HOURS} hours...")
    
    all_articles = []
    for feed in feeds:
        articles = fetch_feed_articles(feed, cutoff_date)
        all_articles.extend(articles)
    
    print(f"\n📈 Total fetched: {len(all_articles)} articles")
    
    # Deduplicate
    unique_articles = deduplicate_articles(all_articles)
    
    # Score with Claude
    scored_articles = score_articles_with_claude(unique_articles, api_key)
    
    # Filter by minimum score
    quality_articles = [a for a in scored_articles if a.score >= MIN_CLAUDE_SCORE]
    print(f"⭐ Quality filter (score >= {MIN_CLAUDE_SCORE}): {len(scored_articles)} → {len(quality_articles)} articles")
    
    # Apply diversity limits
    diverse_articles = apply_diversity_limits(quality_articles, MAX_PER_SOURCE)
    
    # Generate RSS feed
    output_path = 'super-feed.xml'
    generate_rss_feed(diverse_articles, output_path)
    
    # Stats
    print("\n📊 Final stats:")
    print(f"  Total sources: {len(feeds)}")
    print(f"  Articles fetched: {len(all_articles)}")
    print(f"  After dedup: {len(unique_articles)}")
    print(f"  After scoring: {len(quality_articles)}")
    print(f"  Final output: {min(len(diverse_articles), MAX_ARTICLES_OUTPUT)}")


if __name__ == '__main__':
    main()
