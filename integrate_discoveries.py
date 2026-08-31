#!/usr/bin/env python3
"""Reconcile feeds.opml with what the week actually learned about the feeds.

Two modes, both driven from the weekly maintenance workflow:

  --auto-add-threshold N   add high-scoring feed_discovery.py candidates
  --heal                   repair feeds that have been failing, by evidence

Healing exists because the daily pipeline can route *around* a broken feed
(rediscovery, feed-reader retry, search fallbacks) but can never repair the
OPML, which is the only durable record of what we subscribe to. Left alone,
every broken feed becomes a line in a weekly report that a human has to act
on, and until they do, the pipeline pays the recovery cost again every run.
The healer closes that loop: it re-verifies each failing feed against the
live network and writes the answer back into the OPML.

Every mutation is reversible and visible in the OPML diff — feeds are
retired by flipping type="rss" to type="retired" (which parse_opml stops
selecting) rather than deleted, and relocations record where they came from.

Usage: python integrate_discoveries.py [--auto-add-threshold 80] [--heal]
"""
import json
import os
import re
import sys
import argparse
from typing import List, Dict, Optional
from urllib.parse import urlparse, quote_plus
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

def load_discovery_report() -> Dict:
    """Load the latest discovery report"""
    try:
        with open('feed_discovery_report.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No discovery report found. Run feed_discovery.py first.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading discovery report: {e}")
        sys.exit(1)

def load_opml(path: str = 'feeds.opml') -> ET.ElementTree:
    """Load existing OPML file"""
    try:
        return ET.parse(path)
    except Exception as e:
        print(f"❌ Error loading OPML file: {e}")
        sys.exit(1)

def get_existing_feeds(tree: ET.ElementTree) -> set:
    """Get set of feed URLs already present in the OPML, retired ones included.

    Retirement is a decision, not an absence: a feed the health agent retired
    last week is still "known", and discovery must not re-add it as though it
    were a fresh find. Matching on xmlUrl rather than type keeps that decision
    sticky until a human (or a successful recheck) reverses it.
    """
    existing = set()
    for outline in tree.iter('outline'):
        url = outline.get('xmlUrl')
        if url:
            existing.add(url.strip())
    return existing

# WordPress publishes a parallel comment feed next to every content feed
# (/comments/feed/, ?feed=comments-rss2). Discovery scores them like any other
# feed because they look identical structurally, but they carry reader comments
# rather than articles — no headline, no body, nothing scoreable — and they are
# disproportionately WAF-blocked, so each one also costs a failed fetch and a
# search-API fallback on every run. Reject them at the gate.
_COMMENT_FEED_MARKERS = (
    '/comments/feed',
    '/comment-feed',
    'feed=comments-rss2',
    'feed=comments-atom',
)


def is_comment_feed(url: str, title: str = '') -> bool:
    """True if a discovered feed carries reader comments rather than articles."""
    lowered = (url or '').lower()
    if any(marker in lowered for marker in _COMMENT_FEED_MARKERS):
        return True
    return (title or '').strip().lower().startswith('comments for ')


# ---------------------------------------------------------------------------
# Feed health self-healing
#
# The daily pipeline already recovers from a broken feed at runtime — it
# retries a 403 as a feed reader, rediscovers a moved feed, and falls back to
# search. What it cannot do is write the answer down: feeds.opml is
# user-curated, and rewriting it mid-run would fight integrate_discoveries.py
# and destroy hand-made edits. So every broken feed stays broken in the OPML,
# and the pipeline re-pays the recovery cost on every run until a human edits
# the file.
#
# This is the weekly pass that edits the file. It is deliberately structured
# as *evidence → live verification → bounded mutation*: the evidence only
# decides which feeds are worth probing, the live probe decides what is
# actually true right now, and nothing is deleted. A feed is retired by
# flipping type="rss" to type="retired", which parse_opml() stops selecting;
# reversing it is a one-word edit, and the recheck pass below reverses it
# automatically once the source comes back.
# ---------------------------------------------------------------------------

RETIRED_TYPE = 'retired'

# A feed must have failed this many times, across at least this many days,
# before it is a candidate. Both floors matter: the count alone would condemn
# a feed for one bad afternoon of retries, and the span alone would condemn
# one that failed twice a week apart.
HEAL_MIN_FAILURES = 3
HEAL_MIN_FAILURE_DAYS = 2.0

# Ceiling on feeds probed in one pass, so a week where everything breaks at
# once (a runner network fault, say) cannot turn into hundreds of requests
# and a mass retirement.
HEAL_MAX_FEEDS = 25

# A Google News site-search feed is the documented replacement for an outlet
# behind a hostile WAF (FEEDS_MAINTENANCE.md §1). It is only accepted if it
# carries a genuinely recent article: for a dead outlet the search index still
# answers, with years-old results, and adopting that would quietly resurrect a
# source that has stopped publishing.
GOOGLE_NEWS_SEARCH = 'https://news.google.com/rss/search?q=site:{domain}&hl=en&gl=CA&ceid=CA:en'
GOOGLE_NEWS_MAX_AGE_DAYS = 30

HEALTH_LOG_FILE = 'FEED_HEALTH_LOG.md'


def _classify_error(error_text: str) -> str:
    """Map a logged fetch error to the same failure kinds the cache records."""
    text = error_text or ''
    if 'NameResol' in text or 'Name or service not known' in text:
        return 'dns'
    m = re.search(r'\b(\d{3}) (?:Client|Server) Error', text)
    if m:
        return f'http_{m.group(1)}'
    if 'timed out' in text or 'Timeout' in text:
        return 'timeout'
    return 'network'


def _outlines_by_title(tree: ET.ElementTree) -> Dict[str, list]:
    """Index live (type="rss") outlines by the title parse_opml() would use."""
    index: Dict[str, list] = {}
    for outline in tree.iter('outline'):
        if outline.get('type') != 'rss' or not outline.get('xmlUrl'):
            continue
        title = outline.get('title') or outline.get('text') or ''
        index.setdefault(title, []).append(outline)
    return index


def collect_failure_evidence(tree: ET.ElementTree, http_cache) -> Dict[str, Dict]:
    """Gather what the week says about each failing feed, keyed by OPML URL.

    Two independent sources, deliberately. feed_http_cache.json is precise
    (exact consecutive-failure counts, the streak's start, the failure kind)
    but it is runtime state that a lost or reset cache takes with it.
    FEED_ERRORS.md is coarser — one line per failure per run — but it is
    committed history. Either alone can qualify a feed; together they mean a
    wiped cache does not amnesty a feed that has been dead for a week.
    """
    evidence: Dict[str, Dict] = {}

    def record(url: str, title: str, kind: str, failures: int, span_days: float, source: str):
        entry = evidence.setdefault(url, {
            'url': url, 'title': title, 'kind': kind,
            'failures': 0, 'span_days': 0.0, 'sources': [],
        })
        entry['failures'] = max(entry['failures'], failures)
        entry['span_days'] = max(entry['span_days'], span_days)
        if kind and kind != 'network':
            entry['kind'] = kind
        if source not in entry['sources']:
            entry['sources'].append(source)

    live_outlines = [
        o for o in tree.iter('outline')
        if o.get('type') == 'rss' and o.get('xmlUrl')
    ]

    # Source 1 — runtime failure memory.
    for outline in live_outlines:
        url = outline.get('xmlUrl').strip()
        state = http_cache.entry(url)
        if state.get('failures'):
            record(
                url,
                outline.get('title') or outline.get('text') or url,
                state.get('failure_kind', 'network'),
                state['failures'],
                http_cache.failure_age_days(url),
                'feed_http_cache.json',
            )

    # Source 2 — the committed error log, matched back by feed title.
    by_title = _outlines_by_title(tree)
    seen_days: Dict[str, set] = {}
    kinds: Dict[str, str] = {}
    for date, _slot, issues in _recent_logged_errors():
        for failure in issues.get('failed_feeds', []):
            for outline in by_title.get(failure['feed'], []):
                url = outline.get('xmlUrl').strip()
                seen_days.setdefault(url, set()).add(date)
                kinds[url] = _classify_error(failure['error'])

    by_url = {o.get('xmlUrl').strip(): o for o in live_outlines}
    for url, days in seen_days.items():
        outline = by_url.get(url)
        if outline is None:
            continue
        record(
            url,
            outline.get('title') or outline.get('text') or url,
            kinds.get(url, 'network'),
            len(days),
            _date_span_days(days),
            'FEED_ERRORS.md',
        )

    return evidence


def _date_span_days(days: set) -> float:
    """Days between the first and last failure date in a set of YYYY-MM-DD strings."""
    try:
        parsed = sorted(datetime.strptime(d, '%Y-%m-%d') for d in days)
    except ValueError:
        return 0.0
    return (parsed[-1] - parsed[0]).days


def _recent_logged_errors() -> list:
    """Failures from the last 7 days of FEED_ERRORS.md, or [] if unreadable.

    Delegates to log_feed_results, which owns that file's format — parsing it
    a second time here would leave two regexes to keep in sync.
    """
    try:
        from log_feed_results import extract_recent_errors
        return extract_recent_errors()
    except Exception as exc:
        print(f"   ⚠️  Could not read FEED_ERRORS.md: {exc}")
        return []


def _load_recovery_helpers():
    """Import the curator's fetch/verify helpers, or None if unavailable.

    The healer's whole safety argument is that it verifies against the live
    network before it edits anything, and it must verify exactly the way the
    pipeline fetches — same user agents, same "is this really a feed with
    entries" test. Importing beats reimplementing: a divergence here would
    retire feeds the pipeline can read perfectly well. Imported lazily so the
    discovery path still runs where the curator's dependencies are absent.
    """
    try:
        from super_rss_curator_json import (
            _discover_feed_url, _fetch_url_bytes, _looks_like_feed, _FEED_READER_UA,
        )
        return _discover_feed_url, _fetch_url_bytes, _looks_like_feed, _FEED_READER_UA
    except Exception as exc:
        print(f"❌ Cannot load feed verification helpers: {exc}")
        return None


def _probe_feed(url: str, helpers) -> Optional[str]:
    """Return the user agent that got a real feed out of this URL, or None.

    Mirrors the pipeline's own escalation: browser identity first, then the
    self-identified feed reader that WAFs tend to allowlist.
    """
    _discover, fetch_bytes, looks_like_feed, feed_reader_ua = helpers
    content = fetch_bytes(url)
    if content and looks_like_feed(content):
        return 'browser'
    content = fetch_bytes(url, user_agent=feed_reader_ua)
    if content and looks_like_feed(content):
        return 'feed-reader'
    return None


def _feed_is_current(content: bytes, max_age_days: int) -> bool:
    """True if a parsed feed carries at least one entry newer than max_age_days."""
    try:
        import feedparser
        from calendar import timegm
        import time as _time
        parsed = feedparser.parse(content)
    except Exception:
        return False

    cutoff = _time.time() - max_age_days * 86400
    for entry in parsed.entries:
        stamp = entry.get('published_parsed') or entry.get('updated_parsed')
        if stamp and timegm(stamp) >= cutoff:
            return True
    return False


def _google_news_substitute(url: str, helpers) -> Optional[str]:
    """A Google News site-search feed for this outlet, if it is still publishing."""
    _discover, fetch_bytes, looks_like_feed, _ua = helpers
    domain = urlparse(url).netloc.replace('www.', '')
    # A Google News feed that stops working cannot be rescued by another
    # Google News feed — site:news.google.com is not a search for anything.
    if not domain or domain.endswith('news.google.com'):
        return None

    candidate = GOOGLE_NEWS_SEARCH.format(domain=quote_plus(domain))
    content = fetch_bytes(candidate)
    if not (content and looks_like_feed(content)):
        return None
    if not _feed_is_current(content, GOOGLE_NEWS_MAX_AGE_DAYS):
        return None
    return candidate


def _parent_map(tree: ET.ElementTree) -> Dict:
    """child -> parent, since ElementTree elements do not know their parent."""
    return {child: parent for parent in tree.iter() for child in parent}


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%d')


def retire_outline(outline: ET.Element, reason: str) -> None:
    """Take a feed out of rotation without losing it.

    type="retired" is invisible to parse_opml()'s type='rss' selector, so the
    curator stops fetching it, while the URL, title and the reason it was
    retired all stay in the file for a human — or the recheck pass — to undo.
    """
    outline.set('type', RETIRED_TYPE)
    outline.set('retiredReason', reason)
    outline.set('retiredAt', _stamp())


def restore_outline(outline: ET.Element) -> None:
    """Put a retired feed back into rotation after it started working again."""
    outline.set('type', 'rss')
    for attr in ('retiredReason', 'retiredAt'):
        outline.attrib.pop(attr, None)
    outline.set('restoredAt', _stamp())


def relocate_outline(outline: ET.Element, new_url: str) -> None:
    """Point a feed at the URL it actually lives at now."""
    outline.set('relocatedFrom', outline.get('xmlUrl', ''))
    outline.set('relocatedAt', _stamp())
    outline.set('xmlUrl', new_url)


def _insert_substitute(tree: ET.ElementTree, outline: ET.Element, gn_url: str, title: str) -> bool:
    """Add a Google News stand-in immediately after the outlet it replaces.

    Returns False if the outline has no parent to insert beside, so the caller
    can leave the original in rotation rather than retiring it with nothing
    put in its place.
    """
    parent = _parent_map(tree).get(outline)
    if parent is None:
        return False
    parent.insert(list(parent).index(outline) + 1, ET.Element('outline', {
        'type': 'rss',
        'text': f'GN {title}',
        'title': f'GN {title}',
        'xmlUrl': gn_url,
        'htmlUrl': 'https://news.google.com',
        'substituteFor': outline.get('xmlUrl', ''),
    }))
    return True


# How many known-good feeds to probe before trusting a run's verdicts.
NETWORK_SANITY_PROBES = 3


def network_is_sane(tree: ET.ElementTree, evidence: Dict[str, Dict], helpers) -> bool:
    """True if feeds that are *not* under suspicion still fetch.

    Every verdict here is inferred from a failed request, which makes the
    healer only as trustworthy as the runner's own network. A DNS outage or a
    blocked egress proxy makes healthy feeds and dead ones indistinguishable,
    and the honest reading of that evidence — "every outlet died this week" —
    would retire a large slice of the OPML in one pass. So probe a few feeds
    with no failure history first: if none of them answers either, the fault
    is on this side of the connection and nothing that follows is evidence.
    """
    controls = [
        o.get('xmlUrl').strip()
        for o in tree.iter('outline')
        if o.get('type') == 'rss' and o.get('xmlUrl')
        and o.get('xmlUrl').strip() not in evidence
    ]
    if not controls:
        return True   # nothing to compare against; the floors are the only guard

    for url in controls[:NETWORK_SANITY_PROBES]:
        if _probe_feed(url, helpers):
            return True

    print(f"\n🛑 None of {min(len(controls), NETWORK_SANITY_PROBES)} known-good feeds "
          f"is reachable — treating this as a network fault here, not {len(evidence)} "
          f"dead outlets. No changes made.")
    return False


def heal_feeds(tree: ET.ElementTree, http_cache, *, min_failures: int, min_days: float,
               max_feeds: int, allow_substitutes: bool, dry_run: bool) -> List[Dict]:
    """Re-verify every feed the week says is broken, and write the answer back."""
    helpers = _load_recovery_helpers()
    if helpers is None:
        return []

    discover_feed_url = helpers[0]
    evidence = collect_failure_evidence(tree, http_cache)

    candidates = [
        e for e in evidence.values()
        if e['failures'] >= min_failures and e['span_days'] >= min_days
    ]
    # Worst first, so a max_feeds cutoff spends the budget on the feeds that
    # have been broken longest rather than whichever the OPML lists first.
    candidates.sort(key=lambda e: (-e['failures'], -e['span_days']))

    skipped = max(0, len(candidates) - max_feeds)
    candidates = candidates[:max_feeds]

    print(f"\n🩺 HEAL MODE — {len(evidence)} feed(s) with failures, "
          f"{len(candidates)} past the {min_failures}-failure/{min_days:g}-day floor")
    if skipped:
        print(f"   ⚠️  {skipped} more deferred to next week by the {max_feeds}-feed cap")

    if candidates and not network_is_sane(tree, evidence, helpers):
        return []

    by_url = {
        o.get('xmlUrl', '').strip(): o
        for o in tree.iter('outline')
        if o.get('type') == 'rss' and o.get('xmlUrl')
    }

    actions: List[Dict] = []
    for item in candidates:
        outline = by_url.get(item['url'])
        if outline is None:
            continue

        title = item['title']
        why = (f"{item['failures']} failures over {item['span_days']:.0f}d "
               f"({item['kind']}, via {'+'.join(item['sources'])})")

        def log(action: str, detail: str, new_url: str = '') -> None:
            actions.append({
                'action': action, 'title': title, 'url': item['url'],
                'new_url': new_url, 'reason': detail, 'evidence': why,
            })

        # A comment feed is broken by nature, not by circumstance — no probe
        # will make it carry articles. Retire without spending a request.
        if is_comment_feed(item['url'], title):
            print(f"   🗑  {title}: comment feed — retiring")
            if not dry_run:
                retire_outline(outline, 'comment feed — carries reader comments, not articles')
            log('retired', 'comment feed')
            continue

        # 1. Is it actually still broken? Evidence is up to a week old, and a
        #    transient outage that has since cleared must not cost a feed.
        if _probe_feed(item['url'], helpers):
            print(f"   ✓ {title}: recovered on its own — leaving alone")
            log('recovered', 'fetches normally again')
            continue

        # 2. Did it move? The cache may already know where; otherwise look.
        resolved = http_cache.resolved_url(item['url'])
        if resolved and _probe_feed(resolved, helpers):
            print(f"   ↩ {title}: relocated → {resolved}")
            if not dry_run:
                relocate_outline(outline, resolved)
            log('relocated', 'rediscovered URL confirmed live', resolved)
            continue

        discovered = discover_feed_url({
            'url': item['url'],
            'title': title,
            'html_url': outline.get('htmlUrl', ''),
        })
        if discovered:
            print(f"   ↩ {title}: relocated → {discovered}")
            if not dry_run:
                relocate_outline(outline, discovered)
            log('relocated', 'feed rediscovered on the outlet site', discovered)
            continue

        # 3. Unreachable but still publishing? That is a WAF, not a closure —
        #    read it through Google News instead of losing the outlet.
        if allow_substitutes:
            gn_url = _google_news_substitute(item['url'], helpers)
            if gn_url and (dry_run or _insert_substitute(tree, outline, gn_url, title)):
                print(f"   🔁 {title}: unreachable but still publishing — Google News stand-in")
                if not dry_run:
                    retire_outline(outline, 'unreachable — replaced by a Google News search feed')
                log('substituted', 'outlet unreachable but still publishing', gn_url)
                continue

        # 4. Nothing answers. Retire it rather than pay for it every run.
        print(f"   🗑  {title}: unrecoverable — retiring")
        if not dry_run:
            retire_outline(outline, f"unrecoverable after {item['failures']} failures ({item['kind']})")
        log('retired', f"unrecoverable ({item['kind']})")

    return actions


def recheck_retired(tree: ET.ElementTree, *, max_feeds: int, dry_run: bool) -> List[Dict]:
    """Put retired feeds back if they started working again.

    Retirement has to be reversible in practice, not just in principle. A WAF
    rule is relaxed, a CMS migration finishes, an outlet renews its domain —
    without this pass, all of those stay retired until someone notices, which
    makes the healer a ratchet that only ever shrinks the feed list.
    """
    retired = [
        o for o in tree.iter('outline')
        if o.get('type') == RETIRED_TYPE and o.get('xmlUrl')
    ]
    if not retired:
        return []

    helpers = _load_recovery_helpers()
    if helpers is None:
        return []

    # No sanity guard here, deliberately: this pass can only ever restore a
    # feed, so the worst a network fault can do is restore nothing.
    print(f"\n🔎 Rechecking {min(len(retired), max_feeds)} of {len(retired)} retired feed(s)")

    parents = _parent_map(tree)
    actions: List[Dict] = []
    for outline in retired[:max_feeds]:
        url = outline.get('xmlUrl').strip()
        title = outline.get('title') or outline.get('text') or url
        if is_comment_feed(url, title):
            continue
        if not _probe_feed(url, helpers):
            continue

        print(f"   ✅ {title}: working again — restoring")
        if not dry_run:
            restore_outline(outline)
            # Its Google News stand-in, if one was added, is now redundant —
            # leaving both would double every article this outlet publishes.
            for sibling in list(tree.iter('outline')):
                if sibling.get('substituteFor') == url:
                    parent = parents.get(sibling)
                    if parent is not None:
                        parent.remove(sibling)
        actions.append({
            'action': 'restored', 'title': title, 'url': url,
            'new_url': '', 'reason': 'retired source is reachable again',
            'evidence': f"retired {outline.get('retiredAt', 'unknown')}",
        })

    return actions


_HEAL_LABELS = {
    'relocated': '↩ Relocated',
    'retired': '🗑 Retired',
    'substituted': '🔁 Substituted',
    'restored': '✅ Restored',
    'recovered': '✓ Recovered on its own',
}


def write_health_actions_file(path: str, actions: List[Dict]) -> None:
    """Structured record of this pass, for the weekly report's actions table.

    Always written, empty list included, so the report can tell "healed
    nothing" apart from "never ran".
    """
    with open(path, 'w') as f:
        json.dump(actions, f, indent=2)
        f.write('\n')
    print(f"📝 Health actions written to {path}")


def append_health_log(actions: List[Dict], dry_run: bool, path: str = HEALTH_LOG_FILE) -> None:
    """Append one dated section per pass, mirroring CALIBRATION_LOG.md."""
    header = (
        '# Feed Health Log\n\n'
        '_Appended by `integrate_discoveries.py --heal` during weekly maintenance._\n'
        '_Every entry was verified against the live network before it was applied._\n'
    )
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(header)

    lines = [f"\n\n## {_stamp()}{' (dry run)' if dry_run else ''}\n"]
    if not actions:
        lines.append('\nNo feed met the failure floor — nothing to heal.\n')
    else:
        lines.append('\n| Action | Feed | Detail | Evidence |\n')
        lines.append('|---|---|---|---|\n')
        for a in actions:
            label = _HEAL_LABELS.get(a['action'], a['action'])
            detail = f"{a['reason']} → `{a['new_url']}`" if a['new_url'] else a['reason']
            lines.append(f"| {label} | {a['title']} | {detail} | {a['evidence']} |\n")

    with open(path, 'a') as f:
        f.writelines(lines)
    print(f"📝 Health log appended to {path}")


def run_heal(args) -> int:
    """Entry point for --heal. Returns the number of OPML mutations applied."""
    from cache import FeedHTTPCache

    tree = load_opml(args.opml_path)

    if not os.path.exists(args.http_cache_path):
        print(f"ℹ️  No {args.http_cache_path} yet — healing from FEED_ERRORS.md alone")
    http_cache = FeedHTTPCache(args.http_cache_path)
    http_cache.load()

    actions = heal_feeds(
        tree, http_cache,
        min_failures=args.heal_min_failures,
        min_days=args.heal_min_days,
        max_feeds=args.heal_max_feeds,
        allow_substitutes=not args.no_substitutes,
        dry_run=args.dry_run,
    )
    actions += recheck_retired(tree, max_feeds=args.heal_max_feeds, dry_run=args.dry_run)

    applied = [a for a in actions if a['action'] != 'recovered']
    if applied and not args.dry_run:
        head = tree.getroot().find('head')
        if head is not None:
            date_modified = head.find('dateModified')
            if date_modified is None:
                date_modified = ET.SubElement(head, 'dateModified')
            date_modified.text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
        tree.write(args.opml_path, encoding='utf-8', xml_declaration=True)
        print(f"\n✅ Applied {len(applied)} feed health fix(es) to {args.opml_path}")
    elif applied:
        print(f"\n🔍 DRY RUN — {len(applied)} fix(es) would have been applied")
    else:
        print("\n✅ Nothing to heal")

    append_health_log(actions, args.dry_run)
    if args.heal_actions_file:
        write_health_actions_file(args.heal_actions_file, actions)

    return len(applied)


def add_feeds_to_opml(tree: ET.ElementTree, feeds_to_add: List[Dict], category_name: str = "Discovered Feeds") -> int:
    """Add new feeds to OPML under a category"""
    if not feeds_to_add:
        return 0
    
    root = tree.getroot()
    body = root.find('body')
    if body is None:
        body = ET.SubElement(root, 'body')
    
    # Find or create category folder
    category_folder = None
    for outline in body.findall('outline'):
        if outline.get('text') == category_name:
            category_folder = outline
            break
    
    if category_folder is None:
        category_folder = ET.SubElement(body, 'outline', 
                                      text=category_name, 
                                      title=category_name)
    
    # Add feeds to category
    added_count = 0
    for feed in feeds_to_add:
        if is_comment_feed(feed['url'], feed.get('title', '')):
            print(f"   ✗ Skipping comment feed: {feed.get('title') or feed['url']}")
            continue
        # Create feed entry
        ET.SubElement(category_folder, 'outline',
                     type='rss',
                     text=feed['title'],
                     title=feed['title'],
                     xmlUrl=feed['url'],
                     htmlUrl=feed.get('html_url', ''))
        added_count += 1
    
    return added_count

def interactive_selection(report: Dict) -> List[Dict]:
    """Interactively select feeds to add"""
    selected_feeds = []
    
    print("\n🔍 INTERACTIVE FEED SELECTION")
    print("=" * 50)
    
    # Go through each category
    for category, data in report['categories'].items():
        if not data['feeds']:
            continue
            
        print(f"\n📂 {category.upper()} ({data['count']} feeds)")
        print("-" * 30)
        
        for i, feed in enumerate(data['feeds']):
            print(f"\n{i+1}. {feed['title']}")
            print(f"   Score: {feed['average_score']} | Articles: {feed['sample_articles']}")
            print(f"   URL: {feed['url']}")
            print(f"   Reason: {feed['reason']}")
            
            while True:
                choice = input("   Add this feed? (y/n/s=skip category): ").strip().lower()
                if choice in ['y', 'yes']:
                    selected_feeds.append(feed)
                    print("   ✅ Added to selection")
                    break
                elif choice in ['n', 'no']:
                    print("   ❌ Skipped")
                    break
                elif choice in ['s', 'skip']:
                    print(f"   ⏭️  Skipping rest of {category} category")
                    return selected_feeds
                else:
                    print("   Please enter 'y' for yes, 'n' for no, or 's' to skip category")
    
    return selected_feeds

def write_actions_file(path: str, feeds_added: List[Dict]):
    """Write a small structured JSON list of feeds added this run.

    Consumed by the weekly report's "Actions Taken" / rollback section.
    Always written (empty list if nothing was added) so the report can
    distinguish "ran, nothing to add" from "didn't run".
    """
    actions = [
        {
            "title": feed["title"],
            "url": feed["url"],
            "category": feed.get("category", "—"),
            "score": feed.get("average_score", 0),
        }
        for feed in feeds_added
    ]
    with open(path, 'w') as f:
        json.dump(actions, f, indent=2)
        f.write('\n')
    print(f"📝 Actions file written to {path}")


def write_summary_file(path: str, feeds_added: List[Dict], threshold: float, report: Dict):
    """Write a markdown summary of an auto-add run, e.g. for a notification PR body.

    Always writes a summary — including a "nothing qualified" note — so the
    notification reflects what actually happened on weeks with no additions.
    """
    lines = []
    if feeds_added:
        lines.append(f"## 🔍 Weekly Feed Discovery — {len(feeds_added)} feed(s) auto-added\n")
        lines.append(f"These scored {threshold:.0f}+ and were added to `feeds.opml` automatically:\n")
        lines.append("| Feed | Category | Score | URL |")
        lines.append("|---|---|---|---|")
        for feed in feeds_added:
            lines.append(f"| {feed['title']} | {feed.get('category', '—')} | {feed['average_score']:.1f} | {feed['url']} |")
        lines.append("")
        lines.append("These start contributing articles on the next curation run — prune any that don't fit by editing `feeds.opml`.")
    else:
        lines.append("## 🔍 Weekly Feed Discovery — no feeds auto-added this week\n")
        lines.append(f"No candidates scored {threshold:.0f}+ this run, so `feeds.opml` is unchanged.")
        min_score = report.get('min_score_threshold')
        if min_score is not None:
            lines.append(f"See `feed_discovery_report.json` for candidates that cleared the {min_score:.0f}-point recommendation bar but not the auto-add threshold.")
    lines.append("")
    lines.append("_`discovery_cache.json` and `feed_discovery_report.json` were refreshed with this run's evaluations._")

    with open(path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"📝 Summary written to {path}")


def main():
    parser = argparse.ArgumentParser(description='Integrate discovered feeds into OPML')
    parser.add_argument('--auto-add-threshold', type=float, default=None,
                       help='Automatically add feeds above this score threshold')
    parser.add_argument('--opml-path', default='feeds.opml',
                       help='Path to OPML file (default: feeds.opml)')
    parser.add_argument('--category-name', default='Discovered Feeds',
                       help='Category name for new feeds (default: Discovered Feeds)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be added without making changes')
    parser.add_argument('--summary-file', default=None,
                       help='Write a markdown summary of auto-add results to this path '
                            '(used as the body for the automated notification PR)')
    parser.add_argument('--actions-file', default=None,
                       help='Write a JSON list of feeds added this run to this path '
                            '(used by the weekly report\'s actions/rollback section)')

    heal = parser.add_argument_group('feed health (--heal)')
    heal.add_argument('--heal', action='store_true',
                      help='Repair feeds that have been failing: relocate, substitute, '
                           'retire, or restore them after verifying against the live network')
    heal.add_argument('--http-cache-path', default='feed_http_cache.json',
                      help='Per-feed runtime failure state (default: feed_http_cache.json)')
    heal.add_argument('--heal-min-failures', type=int, default=HEAL_MIN_FAILURES,
                      help=f'Failures before a feed is a candidate (default: {HEAL_MIN_FAILURES})')
    heal.add_argument('--heal-min-days', type=float, default=HEAL_MIN_FAILURE_DAYS,
                      help=f'Days the failures must span (default: {HEAL_MIN_FAILURE_DAYS:g})')
    heal.add_argument('--heal-max-feeds', type=int, default=HEAL_MAX_FEEDS,
                      help=f'Cap on feeds probed per pass (default: {HEAL_MAX_FEEDS})')
    heal.add_argument('--no-substitutes', action='store_true',
                      help='Retire unreachable outlets outright instead of replacing '
                           'them with a Google News search feed')
    heal.add_argument('--heal-actions-file', default=None,
                      help='Write a JSON list of health fixes applied to this path '
                           '(used by the weekly report\'s actions/rollback section)')

    args = parser.parse_args()

    # Healing is independent of discovery: it reads runtime failure state and
    # the error log, not feed_discovery_report.json, and must still run on a
    # week when discovery found nothing or failed outright.
    if args.heal:
        run_heal(args)
        return

    # Load discovery report
    report = load_discovery_report()
    
    # Load existing OPML
    opml_tree = load_opml(args.opml_path)
    existing_feeds = get_existing_feeds(opml_tree)
    
    print(f"📚 Loaded {len(existing_feeds)} existing feeds from {args.opml_path}")
    print(f"🎯 Discovery report has {report['recommended_feeds']} recommendations")
    
    # Collect feeds to add
    feeds_to_add = []
    
    if args.auto_add_threshold:
        # Automatic mode
        print(f"\n🤖 AUTO-ADD MODE (threshold: {args.auto_add_threshold})")
        for category, data in report['categories'].items():
            for feed in data['feeds']:
                if (feed['average_score'] >= args.auto_add_threshold and
                    feed['url'] not in existing_feeds):
                    feed['category'] = category
                    feeds_to_add.append(feed)
                    print(f"  ✅ Auto-selected: {feed['title']} (score: {feed['average_score']})")
    else:
        # Interactive mode
        if report['recommended_feeds'] == 0:
            print("❌ No feeds recommended (all below threshold)")
            return
        
        # Filter out feeds already in OPML
        for category, data in report['categories'].items():
            data['feeds'] = [f for f in data['feeds'] if f['url'] not in existing_feeds]
        
        feeds_to_add = interactive_selection(report)
    
    if not feeds_to_add:
        print("\n❌ No feeds selected for addition")
        if args.summary_file and args.auto_add_threshold:
            write_summary_file(args.summary_file, [], args.auto_add_threshold, report)
        if args.actions_file:
            write_actions_file(args.actions_file, [])
        return

    print(f"\n📝 Selected {len(feeds_to_add)} feeds to add:")
    for feed in feeds_to_add:
        print(f"  • {feed['title']} (score: {feed['average_score']})")

    if args.dry_run:
        print("\n🔍 DRY RUN - No changes made")
        if args.actions_file:
            write_actions_file(args.actions_file, [])
        return
    
    # Add feeds to OPML
    added_count = add_feeds_to_opml(opml_tree, feeds_to_add, args.category_name)
    
    # Update OPML metadata
    head = opml_tree.getroot().find('head')
    if head is not None:
        date_modified = head.find('dateModified')
        if date_modified is None:
            date_modified = ET.SubElement(head, 'dateModified')
        date_modified.text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    # Save updated OPML
    opml_tree.write(args.opml_path, encoding='utf-8', xml_declaration=True)
    
    print(f"\n✅ Successfully added {added_count} feeds to {args.opml_path}")
    print(f"📂 Added under category: '{args.category_name}'")

    if args.summary_file and args.auto_add_threshold:
        write_summary_file(args.summary_file, feeds_to_add, args.auto_add_threshold, report)
    else:
        print(f"\n🚀 Next steps:")
        print(f"1. Review the new feeds in your OPML")
        print(f"2. Run your main curation script to test")
        print(f"3. Adjust categories or remove feeds as needed")

    if args.actions_file:
        write_actions_file(args.actions_file, feeds_to_add)

if __name__ == "__main__":
    main()
