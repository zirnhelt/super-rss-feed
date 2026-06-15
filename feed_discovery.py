#!/usr/bin/env python3
"""
Feed Discovery System for Super RSS Curator
- Fetches curated OPML files from GitHub sources
- Scores candidate feeds using existing Claude logic
- Outputs recommendations for new feeds to add
"""
import os
import sys
import json
import socket
import requests
from datetime import datetime, timezone
from collections import defaultdict
from typing import List, Dict, Set, Tuple
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
import feedparser
import anthropic
from dataclasses import dataclass
from bs4 import BeautifulSoup
import config_loader
import cohere_integration


def _build_prescore_keywords() -> frozenset:
    """Union of all category include-keywords plus local signals.

    Used as a free relevance gate for candidate feeds from high-volume
    discovery sources (e.g. Kagi Small Web) so off-topic feeds never
    reach paid Claude/Cohere scoring.
    """
    keywords = set()
    for rules in config_loader.load_category_rules_config().values():
        for kw in rules.get('include', []):
            keywords.add(kw.lower())
    for signal in config_loader.load_filters_config().get('local_signals', []):
        keywords.add(signal.lower())
    return frozenset(keywords)

PRESCORE_KEYWORDS = _build_prescore_keywords()

# Brave Search discovery
# Topics are weighted toward the podcast's themed daily buckets that the weekly
# reviews keep flagging as thin (config/podcast_schedule.json: Indigenous Lands &
# Innovation, Working Lands & Industry, Arts/Culture, Wild Spaces, Science & Wonder)
# plus categories (wellness) that have no dedicated discovery query yet.
BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"
BRAVE_SEARCH_TOPICS = [
    ("meshtastic lora mesh networking blog rss feed", "homelab"),
    ("williams lake cariboo BC community news rss", "local"),
    ("homelab self-hosting proxmox blog rss feed", "homelab"),
    ("solarpunk climate fiction worldbuilding blog rss feed", "scifi"),
    ("sustainable agriculture regenerative ranching rss feed", "climate"),
    ("3d printing bambu lab maker repair blog rss feed", "homelab"),
    ("off-grid solar homestead rural technology blog rss", "climate"),
    ("canadian rural broadband community technology rss feed", "local"),
    # Thursday: Indigenous Lands & Innovation
    ("Tsilhqotin Secwepemc Dakelh Indigenous land stewardship language technology rss feed", "local"),
    # Tuesday: Working Lands & Industry
    ("Cariboo forestry ranching mining agtech resource economy blog rss feed", "climate"),
    # Monday: Arts, Culture & Digital Storytelling
    ("rural arts community media digital storytelling Canada blog rss feed", "local"),
    # Friday: Wild Spaces & Outdoor Life
    ("BC wildfire backcountry conservation Chilcotin wilderness blog rss feed", "climate"),
    # Sunday: Science, Wonder & the Natural World
    ("ecology natural science wonder discovery Cariboo BC interior blog rss feed", "science"),
    # Health & Wellness category has no dedicated query yet
    ("evidence-based health wellness nutrition longevity research blog rss feed", "wellness"),
]
FEED_PROBE_PATHS = ["/feed", "/rss", "/atom.xml", "/feed.xml", "/index.xml", "/rss.xml"]

# feedparser.parse() has no timeout of its own and falls back to whatever
# socket default is in effect. Without this, a handful of slow/dead feeds
# among hundreds of candidates (e.g. a 1000-candidate catch-up run) can each
# hang for minutes, pushing the whole job past the 6-hour GitHub Actions
# limit and getting it cancelled with nothing saved.
FEED_FETCH_TIMEOUT_SECS = 15
socket.setdefaulttimeout(FEED_FETCH_TIMEOUT_SECS)

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
    },
    {
        'name': 'Kagi Small Web',
        'url': 'https://kagi.com/smallweb/opml',
        'category': 'general'
    }
]

def _brave_search(query: str, api_key: str, count: int = 10) -> List[str]:
    """Search Brave for page URLs matching query. Returns [] on error."""
    headers = {'X-Subscription-Token': api_key, 'Accept': 'application/json'}
    params = {'q': query, 'count': count}
    try:
        resp = requests.get(BRAVE_API_URL, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return [r['url'] for r in data.get('web', {}).get('results', [])]
    except Exception as e:
        print(f"  ⚠️ Brave search error for '{query}': {e}")
        return []


def _probe_page_for_feeds(page_url: str) -> List[str]:
    """Discover RSS/Atom feed URLs from an HTML page's <link> tags and common path probes."""
    feeds = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; FeedDiscovery/1.0)'}
        resp = requests.get(page_url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        for link in soup.find_all('link', attrs={'rel': 'alternate'}):
            link_type = link.get('type', '')
            if 'rss' in link_type or 'atom' in link_type:
                href = link.get('href', '')
                if href:
                    feeds.append(urljoin(page_url, href))
    except Exception:
        pass

    if not feeds:
        parsed = urlparse(page_url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        for path in FEED_PROBE_PATHS:
            try:
                r = requests.head(base + path, timeout=5, allow_redirects=True)
                if r.status_code == 200:
                    feeds.append(base + path)
                    break
            except Exception:
                continue

    return list(dict.fromkeys(feeds))


def _validate_feed_url(url: str) -> bool:
    """Return True if feedparser can parse the URL and finds at least one entry."""
    try:
        parsed = feedparser.parse(url)
        return not parsed.bozo and len(parsed.entries) > 0
    except Exception:
        return False


class SimpleArticle:
    """Simple article representation for feed discovery"""
    def __init__(self, entry, source_title: str, source_url: str):
        self.title = entry.get('title', '').strip()
        self.link = entry.get('link', '')
        self.description = entry.get('description', '') or entry.get('summary', '')
        self.source = source_title
        self.source_url = source_url
        self.score = 0
        
        # Parse publication date
        try:
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                from datetime import datetime, timezone
                self.pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            else:
                self.pub_date = datetime.now(timezone.utc)
        except:
            self.pub_date = datetime.now(timezone.utc)

_FALLBACK_INTEREST_QUERY = (
    "AI technology rural community applications, climate tech renewable energy, "
    "Williams Lake Cariboo local news, homelab self-hosting, smart home automation, "
    "3D printing Bambu Lab, health wellness science research, systems thinking, "
    "Meshtastic mesh networking, sustainable agriculture, sci-fi worldbuilding, "
    "Canadian content local news"
)


def score_articles_with_claude(articles: List[SimpleArticle], api_key: str, interests_text: str = '') -> List[SimpleArticle]:
    """Score articles for feed discovery using Cohere Rerank (when available) or Claude.

    `interests_text` is the live podcast scoring profile (config/scoring_interests.txt).
    Deriving the query from it — the same source the main curator tunes every week —
    means discovery scoring evolves automatically alongside the podcast's interests
    instead of drifting from a separately-maintained copy.
    """
    if not articles:
        return articles

    interest_query = cohere_integration.build_interest_query(interests_text) if interests_text else _FALLBACK_INTEREST_QUERY

    cohere_api_key = os.environ.get('COHERE_API_KEY')
    if cohere_api_key:
        try:
            import cohere
            co = cohere.ClientV2(api_key=cohere_api_key)
            documents = [f"{a.title}. {(a.description or '')[:200]}" for a in articles]
            result = co.rerank(
                model="rerank-english-v3.0",
                query=interest_query,
                documents=documents,
                top_n=len(documents),
            )
            for item in result.results:
                articles[item.index].score = int(item.relevance_score * 100)
            print(f"  🔮 Scored {len(articles)} discovery articles with Cohere Rerank")
            return articles
        except Exception as e:
            print(f"  ⚠️ Cohere Rerank error in discovery, falling back to Claude: {e}")

    client = anthropic.Anthropic(api_key=api_key)

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

My interests: {interest_query}

Articles to score:
{article_list}

Return ONLY a comma-separated list of scores (one per article), like: 85,42,91,15,73,...
No explanations, just the numbers."""

        try:
            response = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse scores
            scores_text = response.content[0].text.strip()
            scores = [float(s.strip()) for s in scores_text.split(',')]

            # Assign scores to articles
            for j, article in enumerate(batch):
                if j < len(scores):
                    article.score = scores[j]
                scored_articles.append(article)

        except Exception as e:
            print(f"  ❌ Error scoring batch {i//batch_size + 1}: {str(e)}")
            # Add articles with 0 score if API fails
            for article in batch:
                article.score = 0
                scored_articles.append(article)

    return scored_articles

@dataclass
class FeedCandidate:
    """Represents a potential feed to evaluate"""
    title: str
    url: str
    html_url: str
    source: str
    category: str
    sample_articles: List[SimpleArticle] = None
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
    
    def _sample_feed_articles(self, candidate: FeedCandidate) -> List[SimpleArticle]:
        """Sample recent articles from a feed candidate"""
        try:
            parsed = feedparser.parse(candidate.url)
            articles = []
            
            # Convert to SimpleArticle objects (limit to MAX_ARTICLES_PER_FEED)
            for entry in parsed.entries[:MAX_ARTICLES_PER_FEED]:
                article = SimpleArticle(entry, candidate.title, candidate.html_url)
                
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
    
    def _fetch_brave_candidates(self) -> List['FeedCandidate']:
        """Search Brave for RSS feeds on niche interest topics not covered by OPML sources."""
        brave_key = os.environ.get('BRAVE_API_KEY')
        if not brave_key:
            return []

        print(f"\n🦁 Running Brave Search discovery ({len(BRAVE_SEARCH_TOPICS)} queries)...")
        candidates = []
        seen_feed_urls: Set[str] = set()

        for topic_query, category in BRAVE_SEARCH_TOPICS:
            page_urls = _brave_search(topic_query, brave_key)
            for page_url in page_urls:
                feed_urls = _probe_page_for_feeds(page_url)
                for feed_url in feed_urls:
                    norm = feed_url.strip().lower()
                    if norm in self.existing_feeds or norm in seen_feed_urls:
                        continue
                    if not _validate_feed_url(feed_url):
                        continue
                    seen_feed_urls.add(norm)
                    parsed = feedparser.parse(feed_url)
                    title = parsed.feed.get('title', '') or urlparse(feed_url).netloc
                    candidates.append(FeedCandidate(
                        title=title,
                        url=feed_url,
                        html_url=page_url,
                        source='brave_search',
                        category=category,
                    ))

        print(f"  🦁 Found {len(candidates)} new Brave-discovered feed candidates")
        return candidates

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

        # High-volume discovery sources (e.g. Kagi Small Web) can dump hundreds of
        # uncached candidates into a single run. Cap how many get evaluated this
        # run; the rest stay uncached and get picked up on later runs, trickling
        # the full source through over several weeks instead of one expensive run.
        discovery_filter = config_loader.load_source_preferences().get('discovery_prescore_filter', {})
        gated_sources = set(discovery_filter.get('sources', []))
        max_per_run = discovery_filter.get('max_new_candidates_per_run')
        # Allow ad-hoc catch-up runs (via workflow_dispatch) to process a larger
        # batch than the steady-state weekly default, without editing the config.
        override = os.environ.get('DISCOVERY_MAX_NEW_CANDIDATES_PER_RUN')
        if override:
            max_per_run = int(override)
        if gated_sources and max_per_run is not None:
            kept_new = []
            deferred = 0
            seen_from_gated: Dict[str, int] = defaultdict(int)
            for candidate in new_candidates:
                if candidate.source in gated_sources:
                    if seen_from_gated[candidate.source] >= max_per_run:
                        deferred += 1
                        continue
                    seen_from_gated[candidate.source] += 1
                kept_new.append(candidate)
            if deferred:
                print(f"  ⏳ Deferring {deferred} candidates from {', '.join(sorted(gated_sources))} to later runs (cap {max_per_run}/run)")
            new_candidates = kept_new

        if not new_candidates:
            return cached_candidates

        print(f"\n🤖 Evaluating {len(new_candidates)} new feed candidates...")

        # Load the live podcast scoring profile once. Reusing config/scoring_interests.txt
        # — instead of a separately-maintained interest list — is what lets discovery
        # absorb the podcast's evolving interests/categories without manual syncing.
        try:
            interests_text = config_loader.load_scoring_interests().strip()
        except Exception:
            interests_text = ''

        # Sample articles from each candidate
        for i, candidate in enumerate(new_candidates):
            print(f"  📝 Sampling {candidate.title} ({i+1}/{len(new_candidates)})")
            candidate.sample_articles = self._sample_feed_articles(candidate)
            candidate.article_count = len(candidate.sample_articles)

            # Free pre-filter for gated discovery sources: skip Claude/Cohere
            # entirely if none of the sampled articles hit a CATEGORY_RULES
            # interest keyword.
            if candidate.sample_articles and candidate.source in gated_sources:
                text = " ".join(
                    f"{a.title} {a.description}" for a in candidate.sample_articles
                ).lower()
                if not any(kw in text for kw in PRESCORE_KEYWORDS):
                    candidate.average_score = 0
                    candidate.error = "No keyword match (prescore filter)"
                    self.cache[candidate.url] = {
                        'average_score': candidate.average_score,
                        'article_count': candidate.article_count,
                        'error': candidate.error,
                        'evaluated_at': datetime.now(timezone.utc).isoformat()
                    }
                    continue

            if candidate.sample_articles:
                # Score articles using existing Claude/Cohere logic
                try:
                    scored_articles = score_articles_with_claude(candidate.sample_articles, self.api_key, interests_text)
                    scores = [a.score for a in scored_articles]
                    candidate.average_score = sum(scores) / len(scores) if scores else 0
                except Exception as e:
                    candidate.error = f"Scoring error: {str(e)}"
                    candidate.average_score = 0

                # Apply Cohere embed affinity bonus (max +20 pts) when available
                try:
                    if cohere_integration.is_enabled() and interests_text:
                        texts = [f"{a.title}. {(a.description or '')[:200]}" for a in candidate.sample_articles]
                        affinity = cohere_integration.score_feed_against_interests(texts, interests_text)
                        bonus = round(affinity * 20, 1)
                        if bonus > 0:
                            candidate.average_score = min(100, candidate.average_score + bonus)
                            print(f"    🔮 Affinity bonus +{bonus:.0f}pts → score {candidate.average_score:.1f}")
                except Exception:
                    pass
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

            # Periodically flush so a large run that gets cancelled partway
            # (e.g. hitting the job time limit) doesn't lose all its progress.
            if (i + 1) % 25 == 0:
                self._save_cache()

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
    
    # Fetch candidates from OPML sources and Brave Search
    opml_candidates = discovery._fetch_opml_sources()
    brave_candidates = discovery._fetch_brave_candidates()
    candidates = opml_candidates + brave_candidates

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
