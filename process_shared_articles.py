#!/usr/bin/env python3
"""Weekly shared-article processor — turns articles found elsewhere into training
signal and source-discovery candidates.

Reads shared_articles/YYYY-MM-DD.json files committed by share.html, fetches
each new URL, and scores it against config/scoring_interests.txt using the
same Claude path feed_discovery.py uses for candidate feeds. For each shared
article:
  - writes a 'good'-rated entry into feedback/YYYY-MM-DD.json, in the exact
    schema feedback_trainer.py already consumes — no changes needed there,
    it folds these into next week's synthesis automatically.
  - if the article's domain isn't already an RSS source, probes for a feed
    (feed_discovery._probe_page_for_feeds) and, if one validates and scores
    well, adds it to feeds.opml (>= AUTO_ADD_THRESHOLD) or
    shared_source_candidates.json for human review (>= RECOMMEND_THRESHOLD).

Run weekly via weekly-maintenance.yml, before feedback-training. Requires
ANTHROPIC_API_KEY. Idempotent: processed URLs are tracked in
shared_articles_cache.json so re-running is a no-op.
"""
import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

import feedparser
import requests
from bs4 import BeautifulSoup

import config_loader
import feed_discovery
import integrate_discoveries
from cache import Cache

SHARED_DIR          = Path('shared_articles')
FEEDBACK_DIR         = Path('feedback')
LOG_FILE             = Path('SHARED_ARTICLES_LOG.md')
CANDIDATES_FILE      = Path('shared_source_candidates.json')
CACHE_FILE           = 'shared_articles_cache.json'
OPML_PATH            = 'feeds.opml'
LOOKBACK_DAYS        = 30
AUTO_ADD_THRESHOLD   = 65  # matches the weekly discovery job's auto-add bar
RECOMMEND_THRESHOLD  = feed_discovery.MIN_FEED_SCORE  # 60
DRY_RUN              = os.getenv('SHARED_ARTICLES_DRY_RUN', 'false').lower() == 'true'
USER_AGENT           = 'Mozilla/5.0 (compatible; SharedArticleProcessor/1.0)'


def load_shares(lookback_days: int = LOOKBACK_DAYS) -> list:
    """Load all shared-article entries within the lookback window, tagged with their source date."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    shares = []
    if not SHARED_DIR.exists():
        return shares
    for f in sorted(SHARED_DIR.glob('????-??-??.json')):
        try:
            date = datetime.fromisoformat(f.stem).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if date < cutoff:
            continue
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"⚠️  Skipping {f}: {e}")
            continue
        for share in data.get('shares', []):
            if share.get('url'):
                share['_date'] = f.stem
                shares.append(share)
    return shares


def fetch_article(url: str) -> dict:
    """Fetch title/description for a shared URL. Returns {} on failure."""
    try:
        resp = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        title = None
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            title = og_title['content'].strip()
        elif soup.title and soup.title.string:
            title = soup.title.string.strip()

        description = ''
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            description = og_desc['content'].strip()

        return {'title': title or url, 'description': description}
    except Exception as e:
        print(f"  ⚠️ Could not fetch {url}: {e}")
        return {}


def guess_category(title: str, description: str) -> str:
    """Best-effort category guess via config/category_rules.json keyword overlap."""
    text = f"{title} {description}".lower()
    rules = config_loader.load_category_rules_config()
    best_category, best_hits = 'shared', 0
    for category, rule in rules.items():
        hits = sum(1 for kw in rule.get('include', []) if kw.lower() in text)
        if hits > best_hits:
            best_category, best_hits = category, hits
    return best_category


def score_article(title: str, description: str, interests_text: str) -> float:
    """Score a single shared article via the same Claude path feed_discovery.py uses for candidates."""
    article = feed_discovery.SimpleArticle({'title': title, 'description': description}, title, '')
    scored = feed_discovery.score_articles_with_claude([article], os.environ['ANTHROPIC_API_KEY'], interests_text)
    return scored[0].score if scored else 0.0


def domain_already_covered(url: str, existing_feeds: set) -> bool:
    """True if the shared article's domain already matches an OPML feed's netloc."""
    netloc = urlparse(url).netloc.lower().removeprefix('www.')
    for feed_url in existing_feeds:
        feed_netloc = urlparse(feed_url).netloc.lower().removeprefix('www.')
        if feed_netloc and feed_netloc == netloc:
            return True
    return False


def find_new_source_candidate(url: str, existing_feeds: set, interests_text: str, category: str) -> dict:
    """Probe a shared article's page for an RSS feed and score it. Returns a candidate dict or None."""
    for feed_url in feed_discovery._probe_page_for_feeds(url):
        norm = feed_url.strip().lower()
        if norm in existing_feeds or not feed_discovery._validate_feed_url(feed_url):
            continue
        parsed = feedparser.parse(feed_url)
        title = parsed.feed.get('title', '') or urlparse(feed_url).netloc
        sample = [
            feed_discovery.SimpleArticle(entry, title, url)
            for entry in parsed.entries[:feed_discovery.MAX_ARTICLES_PER_FEED]
        ]
        if not sample:
            continue
        scored = feed_discovery.score_articles_with_claude(sample, os.environ['ANTHROPIC_API_KEY'], interests_text)
        return {
            'title': title,
            'url': feed_url,
            'html_url': url,
            'category': category,
            'average_score': sum(a.score for a in scored) / len(scored),
            'sample_articles': len(scored),
        }
    return None


def append_feedback_entry(date_key: str, entry: dict):
    """Merge a shared-article 'good' rating into feedback/<date_key>.json by URL.

    Same shape and merge-by-url semantics review.html already writes, so
    feedback_trainer.py picks it up next run with no changes.
    """
    FEEDBACK_DIR.mkdir(exist_ok=True)
    path = FEEDBACK_DIR / f"{date_key}.json"
    data = {'date': date_key, 'ratings': []}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            pass
    ratings_by_url = {r.get('url'): r for r in data.get('ratings', [])}
    ratings_by_url[entry['url']] = entry
    data['ratings'] = list(ratings_by_url.values())
    data['submitted_at'] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def write_candidates_file(candidates: list):
    """Merge newly-recommended (sub-auto-add) source candidates into shared_source_candidates.json."""
    existing = []
    if CANDIDATES_FILE.exists():
        try:
            existing = json.loads(CANDIDATES_FILE.read_text(encoding='utf-8'))
        except Exception:
            existing = []
    by_url = {c['url']: c for c in existing}
    for c in candidates:
        by_url[c['url']] = c
    CANDIDATES_FILE.write_text(json.dumps(list(by_url.values()), indent=2), encoding='utf-8')


def add_sources_to_opml(opml_tree: ET.ElementTree, candidates: list):
    integrate_discoveries.add_feeds_to_opml(opml_tree, candidates, category_name='Discovered Feeds')
    head = opml_tree.getroot().find('head')
    if head is not None:
        date_modified = head.find('dateModified')
        if date_modified is None:
            date_modified = ET.SubElement(head, 'dateModified')
        date_modified.text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
    opml_tree.write(OPML_PATH, encoding='utf-8', xml_declaration=True)


def build_log_entry(shares: list, feedback_written: int, sources_added: list, sources_recommended: list, errors: list, dry_run: bool) -> str:
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    status = '(DRY RUN — no changes written)' if dry_run else '✅ feedback entries + feeds.opml updated'

    added_lines = ''.join(f"- {c['title']} ({c['average_score']:.1f}) — {c['url']}\n" for c in sources_added)
    recommended_lines = ''.join(f"- {c['title']} ({c['average_score']:.1f}) — {c['url']}\n" for c in sources_recommended)

    return f"""## Shared Article Run — {now}

**Shared articles processed:** {len(shares)} ({feedback_written} scored, {len(errors)} fetch failures)
**Status:** {status}

**New sources auto-added (score >= {AUTO_ADD_THRESHOLD}):**
{added_lines or 'none'}
**New sources recommended for review (score >= {RECOMMEND_THRESHOLD}):**
{recommended_lines or 'none'}
---
"""


def append_log(entry: str):
    existing = LOG_FILE.read_text(encoding='utf-8') if LOG_FILE.exists() else ''
    LOG_FILE.write_text(entry + existing, encoding='utf-8')


def main():
    api_key = os.getenv('ANTHROPIC_API_KEY', '')
    if not api_key:
        print('❌ ANTHROPIC_API_KEY not set')
        sys.exit(1)

    print('📨 Shared Article Processor — loading shares...')
    shares = load_shares(LOOKBACK_DAYS)
    if not shares:
        print('ℹ️  No shared articles found. Skipping.')
        sys.exit(0)

    cache = Cache(CACHE_FILE)
    processed = cache.load()
    new_shares = [s for s in shares if s['url'] not in processed]

    if not new_shares:
        print(f'ℹ️  All {len(shares)} shared articles already processed. Skipping.')
        sys.exit(0)

    print(f'   {len(new_shares)} new of {len(shares)} total shared articles')

    interests_text = config_loader.load_scoring_interests()
    opml_tree = integrate_discoveries.load_opml(OPML_PATH)
    existing_feeds = integrate_discoveries.get_existing_feeds(opml_tree)

    feedback_written = 0
    sources_added = []
    sources_recommended = []
    errors = []

    for share in new_shares:
        url = share['url']
        print(f'  → {url}')
        meta = fetch_article(url)
        if not meta:
            errors.append(url)
            processed[url] = datetime.now(timezone.utc).timestamp()
            continue

        title = meta['title']
        description = meta['description']
        category = guess_category(title, description)
        score = score_article(title, description, interests_text)

        entry = {
            'url': url,
            'title': title,
            'source': urlparse(url).netloc,
            'category': category,
            'score': round(score),
            'quality': 0,
            'relevance': round(score),
            'local': 0,
            'description': description[:300],
            'rating': 'good',
            'approved_days': [],
            'better_theme': None,
            'note': share.get('note'),
            'rated_at': datetime.now(timezone.utc).isoformat(),
        }
        if not DRY_RUN:
            append_feedback_entry(share['_date'], entry)
        feedback_written += 1

        if not domain_already_covered(url, existing_feeds):
            candidate = find_new_source_candidate(url, existing_feeds, interests_text, category)
            if candidate and candidate['average_score'] >= AUTO_ADD_THRESHOLD:
                sources_added.append(candidate)
                existing_feeds.add(candidate['url'].strip().lower())
            elif candidate and candidate['average_score'] >= RECOMMEND_THRESHOLD:
                sources_recommended.append(candidate)

        processed[url] = datetime.now(timezone.utc).timestamp()

    if not DRY_RUN:
        if sources_added:
            add_sources_to_opml(opml_tree, sources_added)
        if sources_recommended:
            write_candidates_file(sources_recommended)
        cache.save(processed)

    log_entry = build_log_entry(new_shares, feedback_written, sources_added, sources_recommended, errors, DRY_RUN)
    if DRY_RUN:
        print(log_entry)
    else:
        append_log(log_entry)
        print(f'📝 Appended to {LOG_FILE}')

    print(f'✅ Shared article processing complete — {feedback_written} feedback entries, '
          f'{len(sources_added)} sources added, {len(sources_recommended)} recommended')


if __name__ == '__main__':
    main()
