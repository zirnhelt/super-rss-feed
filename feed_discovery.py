#!/usr/bin/env python3
"""
Feed Discovery System for Super RSS Curator
- Fetches curated OPML files from GitHub sources
- Scores candidate feeds using existing Claude logic
- Outputs recommendations for new feeds to add
- Caches results monthly to minimize API costs
"""
import os
import sys
import json
import requests
from datetime import datetime, timezone
from typing import List, Dict, Set, Tuple
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import feedparser
import anthropic
from dataclasses import dataclass

# Import from existing curator (assumes it's in same directory)
sys.path.append('.')
from super_rss_curator_json import Article, score_articles_with_claude

# Configuration
DISCOVERY_CACHE_FILE = 'discovery_cache.json'
DISCOVERY_OUTPUT_FILE = 'feed_discovery_report.json'
MAX_ARTICLES_PER_FEED = 3  # Sample articles for scoring
MIN_FEED_SCORE = 60  # Minimum average score to recommend
CACHE_EXPIRY_DAYS = 30  # Re-evaluate feeds monthly

# Curated OPML sources
DISCOVERY_SOURCES = [
    {
        'name': 'AI/ML Feeds',
        'url': 'https://raw.githubusercontent.com/vishalshar/awesome_ML_AI_RSS_feed/master/rssowl.opml',
        'category': 'ai_ml'
    },
    {
        'name': 'Tech & Startups',
        'url': 'https://raw.githubusercontent.com/tuan3w/awesome-tech-rss/main/feeds.opml',
        'category': 'tech'
    },
    {
        'name': 'RSS Renaissance AI',
        'url': 'https://raw.githubusercontent.com/RSS-Renaissance/awesome-AI-feeds/master/feedlist.opml',
        'category': 'ai_ml'
    },
    {
        'name': 'Plenary Awesome Feeds',
        'url': 'https://raw.githubusercontent.com/plenaryapp/awesome-rss-feeds/master/recommended_feeds.opml',
        'category': 'general'
    }
]

@dataclass
class FeedCandidate:
    """Represents a potential feed to evaluate"""
    title: str
    url: str
    html_url: str
    source: str
    category: str
    sample_articles: List[Article] = None
    average_score: float = 0.0
    article_count: int = 0
    error: str = None

class FeedDiscovery:
    def __init__(self, api_key: str, existing_opml_path: str = 'feeds.opml'):
        self.api_key = api_key
        self.existing_opml_path = existing_opml_path
        self.existing_feeds = self._load_existing_feeds()
        self.cache = self._load_cache()
        
    def _load_existing_feeds(self) -> Set[str]:
        """Load existing feed URLs from current OPML"""
        existing = set()
        try:
            tree = ET.parse(self.existing_opml_path)
            for outline in tree.findall(".//outline[@type='rss']"):
                url = outline.get('xmlUrl')
                if url:
                    existing.add(url.strip().lower())
        except Exception as e:
            print(f"⚠️  Warning: Could not load existing OPML: {e}")
        
        print(f"📚 Loaded {len(existing)} existing feeds")
        return existing
    
    def _load_cache(self) -> Dict:
        """Load discovery cache"""
        try:
            with open(DISCOVERY_CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_cache(self):
        """Save discovery cache"""
        with open(DISCOVERY_CACHE_FILE, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def _fetch_opml_sources(self) -> List[FeedCandidate]:
        """Fetch and parse OPML files from discovery sources"""
        candidates = []
        
        for source in DISCOVERY_SOURCES:
            print(f"\n🌐 Fetching {source['name']}...")
            try:
                response = requests.get(source['url'], timeout=30)
                response.raise_for_status()
                
                # Parse OPML
                root = ET.fromstring(response.content)
                feed_count = 0
                
                for outline in root.findall(".//outline[@type='rss']"):
                    feed_url = outline.get('xmlUrl')
                    if not feed_url:
                        continue
                    
                    # Skip if already exists
                    if feed_url.strip().lower() in self.existing_feeds:
                        continue
                    
                    candidate = FeedCandidate(
                        title=outline.get('title') or outline.get('text') or 'Unknown',
                        url=feed_url.strip(),
                        html_url=outline.get('htmlUrl', ''),
                        source=source['name'],
                        category=source['category']
                    )
                    candidates.append(candidate)
                    feed_count += 1
                
                print(f"  ✅ Found {feed_count} new candidates")
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
        
        print(f"\n🎯 Total candidates: {len(candidates)}")
        return candidates
    
    def _sample_feed_articles(self, candidate: FeedCandidate) -> List[Article]:
        """Sample recent articles from a feed candidate"""
        try:
            parsed = feedparser.parse(candidate.url)
            articles = []
            
            # Convert to Article objects (limit to MAX_ARTICLES_PER_FEED)
            for entry in parsed.entries[:MAX_ARTICLES_PER_FEED]:
                article = Article(entry, candidate.title, candidate.html_url)
                
                # Skip very old articles (older than 30 days)
                if (datetime.now(timezone.utc) - article.pub_date).days > 30:
                    continue
                
                articles.append(article)
            
            return articles
            
        except Exception as e:
            candidate.error = str(e)
            return []
    
    def _is_feed_cached(self, feed_url: str) -> bool:
        """Check if feed evaluation is cached and still valid"""
        cache_entry = self.cache.get(feed_url)
        if not cache_entry:
            return False
        
        # Check cache expiry
        cached_date = datetime.fromisoformat(cache_entry['evaluated_at'])
        days_old = (datetime.now(timezone.utc) - cached_date).days
        
        return days_old < CACHE_EXPIRY_DAYS
    
    def evaluate_candidates(self, candidates: List[FeedCandidate]) -> List[FeedCandidate]:
        """Evaluate feed candidates using Claude scoring"""
        
        # Separate cached vs new candidates
        cached_candidates = []
        new_candidates = []
        
        for candidate in candidates:
            if self._is_feed_cached(candidate.url):
                # Load from cache
                cache_entry = self.cache[candidate.url]
                candidate.average_score = cache_entry['average_score']
                candidate.article_count = cache_entry['article_count']
                candidate.error = cache_entry.get('error')
                cached_candidates.append(candidate)
            else:
                new_candidates.append(candidate)
        
        print(f"💡 Cache: {len(cached_candidates)} cached, {len(new_candidates)} new to evaluate")
        
        if not new_candidates:
            return cached_candidates
        
        print(f"\n🤖 Evaluating {len(new_candidates)} new feed candidates...")
        
        # Sample articles from each candidate
        for i, candidate in enumerate(new_candidates):
            print(f"  📝 Sampling {candidate.title} ({i+1}/{len(new_candidates)})")
            candidate.sample_articles = self._sample_feed_articles(candidate)
            candidate.article_count = len(candidate.sample_articles)
            
            if candidate.sample_articles:
                # Score articles using existing Claude logic
                try:
                    scored_articles = score_articles_with_claude(candidate.sample_articles, self.api_key)
                    scores = [a.score for a in scored_articles]
                    candidate.average_score = sum(scores) / len(scores) if scores else 0
                except Exception as e:
                    candidate.error = f"Scoring error: {str(e)}"
                    candidate.average_score = 0
            else:
                candidate.average_score = 0
                if not candidate.error:
                    candidate.error = "No recent articles found"
            
            # Cache the result
            self.cache[candidate.url] = {
                'average_score': candidate.average_score,
                'article_count': candidate.article_count,
                'error': candidate.error,
                'evaluated_at': datetime.now(timezone.utc).isoformat()
            }
        
        # Save cache after evaluation
        self._save_cache()
        
        return cached_candidates + new_candidates
    
    def generate_recommendations(self, evaluated_candidates: List[FeedCandidate]) -> Dict:
        """Generate feed recommendations report"""
        
        # Filter and sort recommendations
        good_candidates = [
            c for c in evaluated_candidates 
            if c.average_score >= MIN_FEED_SCORE and not c.error
        ]
        good_candidates.sort(key=lambda x: x.average_score, reverse=True)
        
        # Group by category for better organization
        by_category = {}
        for candidate in good_candidates:
            if candidate.category not in by_category:
                by_category[candidate.category] = []
            by_category[candidate.category].append(candidate)
        
        # Generate report
        report = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'total_candidates_evaluated': len(evaluated_candidates),
            'recommended_feeds': len(good_candidates),
            'min_score_threshold': MIN_FEED_SCORE,
            'categories': {}
        }
        
        # Add recommendations by category
        for category, candidates in by_category.items():
            report['categories'][category] = {
                'count': len(candidates),
                'feeds': []
            }
            
            for candidate in candidates:
                feed_info = {
                    'title': candidate.title,
                    'url': candidate.url,
                    'html_url': candidate.html_url,
                    'source': candidate.source,
                    'average_score': round(candidate.average_score, 1),
                    'sample_articles': candidate.article_count,
                    'reason': self._get_recommendation_reason(candidate.average_score)
                }
                report['categories'][category]['feeds'].append(feed_info)
        
        # Add summary stats
        report['summary'] = {
            'by_category': {cat: len(feeds['feeds']) for cat, feeds in report['categories'].items()},
            'top_recommendations': [
                {
                    'title': c.title,
                    'category': c.category,
                    'score': round(c.average_score, 1),
                    'url': c.url
                }
                for c in good_candidates[:10]  # Top 10
            ]
        }
        
        return report
    
    def _get_recommendation_reason(self, score: float) -> str:
        """Get human-readable reason for recommendation"""
        if score >= 85:
            return "Excellent match for your interests"
        elif score >= 75:
            return "Strong alignment with your interests"
        elif score >= MIN_FEED_SCORE:
            return "Good potential addition"
        else:
            return "Below threshold"
    
    def save_report(self, report: Dict):
        """Save discovery report to file"""
        with open(DISCOVERY_OUTPUT_FILE, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Report saved to {DISCOVERY_OUTPUT_FILE}")
    
    def print_summary(self, report: Dict):
        """Print a summary of recommendations"""
        print(f"\n🎯 FEED DISCOVERY SUMMARY")
        print(f"=" * 50)
        print(f"Total candidates evaluated: {report['total_candidates_evaluated']}")
        print(f"Recommended feeds: {report['recommended_feeds']}")
        print(f"Score threshold: {report['min_score_threshold']}")
        
        if report['recommended_feeds'] > 0:
            print(f"\n📈 TOP RECOMMENDATIONS:")
            for feed in report['summary']['top_recommendations'][:5]:
                print(f"  • {feed['title']} ({feed['category']}) - Score: {feed['score']}")
                print(f"    {feed['url']}")
        
        print(f"\n📂 BY CATEGORY:")
        for category, count in report['summary']['by_category'].items():
            print(f"  • {category}: {count} feeds")

def main():
    # Check for API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    
    # Initialize discovery system
    discovery = FeedDiscovery(api_key)
    
    print("🔍 FEED DISCOVERY SYSTEM")
    print("=" * 50)
    
    # Fetch candidates from OPML sources
    candidates = discovery._fetch_opml_sources()
    
    if not candidates:
        print("❌ No new feed candidates found")
        sys.exit(1)
    
    # Evaluate candidates
    evaluated = discovery.evaluate_candidates(candidates)
    
    # Generate recommendations
    report = discovery.generate_recommendations(evaluated)
    
    # Save and display results
    discovery.save_report(report)
    discovery.print_summary(report)
    
    print(f"\n✅ Discovery complete! Check {DISCOVERY_OUTPUT_FILE} for full details.")

if __name__ == "__main__":
    main()
