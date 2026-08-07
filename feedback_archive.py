#!/usr/bin/env python3
"""Weekly feedback archiver — distills old ratings into durable aggregates, then compresses them.

The `feedback/` directory grows without bound (~15 ratings/day, ~12 KB/day) and every
consumer treats it differently: `feedback_trainer.py` only looks back 30 days,
`article_review_audit.py` reads everything, and `super_rss_curator_json.py` re-parses the
whole directory on *every* run just to rebuild a set of already-reviewed URLs. This script
gives the history a bounded, three-layer shape:

  1. `feedback/YYYY-MM-DD.json`      — raw ratings, kept for `feedback_retention_days`.
  2. `feedback/feedback_rollup.json` — permanent distilled aggregates (verdict counts by
                                       source/category, score-band vs verdict histograms,
                                       day-reassignment and category-retag matrices, and
                                       score sums for deriving means). Never expires.
  3. `feedback/archive/YYYY-MM.jsonl.gz` — lossless gzipped JSONL of the raw files, one
                                       original file object per line. Read by the weekly
                                       audit; never read on the hot path.

It also maintains `feedback/reviewed_urls.json`, a compact append-only ledger of rated URLs
so the curator can answer "have I shown this before?" without touching the raw history.

Distillation happens *before* deletion: a file is only removed once its ratings have been
folded into the rollup and written to an archive shard. Idempotent — the rollup records
which filenames it has already absorbed, so re-running is a no-op.

The rollup carries two layers. Statistical aggregates are stdlib and free, but they only
capture what is already a categorical field — source, category, day routing, score bands —
and are blind to *topic and framing*, which lives in the article title. So when a batch is
actually archived, one Haiku call consolidates the batch's titles into a durable prose
`lessons` block. That fires only when files cross the retention boundary (roughly monthly,
never weekly) and costs ~$0.013 a batch. It degrades to statistics-only without an API key
or on any API error — archival never depends on it.

Run weekly via weekly-maintenance.yml.
"""
import argparse
import gzip
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config_loader import load_limits_config

FEEDBACK_DIR = Path('feedback')
ARCHIVE_DIR = FEEDBACK_DIR / 'archive'
ROLLUP_FILE = FEEDBACK_DIR / 'feedback_rollup.json'
LEDGER_FILE = FEEDBACK_DIR / 'reviewed_urls.json'
LOG_FILE = Path('FEEDBACK_TRAINING_LOG.md')

ROLLUP_VERSION = 1
LEDGER_VERSION = 1

DEFAULT_RETENTION_DAYS = 90
DEFAULT_LEDGER_DAYS = 180

DISTIL_MODEL = 'claude-haiku-4-5'
DISTIL_MAX_TOKENS = 600
DISTIL_MAX_TITLES = 600  # hard ceiling on batch size so one call can never blow up

# Mirrors article_review_audit.SCORE_BANDS so rolled-up histograms stay comparable
# with the ones the audit computes from live files.
SCORE_BANDS: List[Tuple[int, int]] = [(80, 100), (60, 79), (40, 59), (20, 39), (0, 19)]
VERDICTS = ('exemplar', 'good', 'interesting', 'bad', 'skip')


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def _read_json(path: Path) -> Optional[Any]:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def empty_rollup() -> Dict[str, Any]:
    return {
        'version': ROLLUP_VERSION,
        'updated_at': None,
        'archived_files': [],
        'first_rated_at': None,
        'last_rated_at': None,
        'total_ratings': 0,
        'totals': {},
        'by_source': {},
        'by_category': {},
        'score_bands': {},
        'day_reassignments': {},
        'category_retags': {},
        'score_sums': {},
        'lessons': '',
        'lessons_updated_at': None,
        'lessons_batches': 0,
    }


def load_rollup() -> Dict[str, Any]:
    """Load the durable rollup, resetting it if the schema version moved."""
    data = _read_json(ROLLUP_FILE)
    if not isinstance(data, dict) or data.get('version') != ROLLUP_VERSION:
        return empty_rollup()
    base = empty_rollup()
    base.update(data)
    return base


def load_ledger() -> Dict[str, str]:
    """Load the reviewed-URL ledger as {url: rated_at}."""
    data = _read_json(LEDGER_FILE)
    if not isinstance(data, dict) or data.get('version') != LEDGER_VERSION:
        return {}
    urls = data.get('urls')
    return urls if isinstance(urls, dict) else {}


def save_ledger(urls: Dict[str, str]) -> None:
    LEDGER_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        'version': LEDGER_VERSION,
        'updated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'count': len(urls),
        'urls': dict(sorted(urls.items())),
    }
    LEDGER_FILE.write_text(json.dumps(payload, separators=(',', ':')), encoding='utf-8')


def save_rollup(rollup: Dict[str, Any]) -> None:
    ROLLUP_FILE.parent.mkdir(parents=True, exist_ok=True)
    rollup['updated_at'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    ROLLUP_FILE.write_text(json.dumps(rollup, indent=2, sort_keys=True), encoding='utf-8')


# ---------------------------------------------------------------------------
# Distillation
# ---------------------------------------------------------------------------

def score_band(score: Any) -> Optional[str]:
    if not isinstance(score, (int, float)):
        return None
    for low, high in SCORE_BANDS:
        if low <= score <= high:
            return f'{low}-{high}'
    return None


def _bump(container: Dict[str, Dict[str, int]], key: str, verdict: str) -> None:
    container.setdefault(key, {})
    container[key][verdict] = container[key].get(verdict, 0) + 1


def fold_into_rollup(rollup: Dict[str, Any], ratings: List[Dict]) -> int:
    """Fold one file's ratings into the durable aggregates. Returns ratings absorbed."""
    absorbed = 0
    for r in ratings:
        verdict = r.get('rating')
        if verdict not in VERDICTS:
            continue
        absorbed += 1

        rollup['totals'][verdict] = rollup['totals'].get(verdict, 0) + 1
        _bump(rollup['by_source'], r.get('source') or 'unknown', verdict)
        _bump(rollup['by_category'], r.get('category') or 'unknown', verdict)

        band = score_band(r.get('score'))
        if band:
            _bump(rollup['score_bands'], band, verdict)

        # Running sums let the trainer and audit derive means without the raw rows.
        sums = rollup['score_sums'].setdefault(
            verdict, {'n': 0, 'score': 0.0, 'quality': 0.0, 'relevance': 0.0, 'local': 0.0})
        sums['n'] += 1
        for dim in ('score', 'quality', 'relevance', 'local'):
            value = r.get(dim)
            if isinstance(value, (int, float)):
                sums[dim] += value

        # Routing corrections are the most actionable long-horizon signal, so they
        # survive archival as explicit from → to matrices.
        to_days = r.get('approved_days') or ([r['better_theme']] if r.get('better_theme') else [])
        if to_days:
            from_day = r.get('today') or 'unknown'
            bucket = rollup['day_reassignments'].setdefault(from_day, {})
            for to_day in to_days:
                bucket[to_day] = bucket.get(to_day, 0) + 1

        original, current = r.get('original_category'), r.get('category')
        if original and current and original != current:
            bucket = rollup['category_retags'].setdefault(original, {})
            bucket[current] = bucket.get(current, 0) + 1

        rated_at = r.get('rated_at')
        if rated_at:
            if not rollup['first_rated_at'] or rated_at < rollup['first_rated_at']:
                rollup['first_rated_at'] = rated_at
            if not rollup['last_rated_at'] or rated_at > rollup['last_rated_at']:
                rollup['last_rated_at'] = rated_at

    rollup['total_ratings'] += absorbed
    return absorbed


# ---------------------------------------------------------------------------
# Prose distillation — the layer counters cannot reach
# ---------------------------------------------------------------------------

def title_lines(ratings: List[Dict]) -> List[str]:
    """Compact `[verdict][category] title (source)` lines for the distillation prompt."""
    lines = []
    for r in ratings:
        verdict = r.get('rating')
        if verdict not in VERDICTS:
            continue
        title = (r.get('title') or '').strip()
        if not title:
            continue
        line = f"[{verdict}][{r.get('category') or '?'}] {title} ({r.get('source') or '?'})"
        note = r.get('note')
        if note:
            line += f" — note: {note}"
        lines.append(line)
    return lines


def build_distil_prompt(lines: List[str], previous: str) -> str:
    prior = previous.strip() or '(none yet — this is the first archived batch)'
    return f"""You maintain a durable, consolidated set of scoring lessons for a personal RSS curator.
The raw ratings behind these lessons are being archived, so this text is the only form in
which their topical signal survives.

EXISTING LESSONS (carry forward what still holds; revise what this batch contradicts):
{prior}

NEWLY ARCHIVED RATINGS (verdicts the user gave; 'bad' means they disliked it):
{chr(10).join(lines)}

Task: rewrite the lessons as a single consolidated list of 8-12 bullet points capturing
TOPIC AND FRAMING patterns — what subject matter, angle, and article type the user accepts
or rejects. Skip source-level and category-level statistics; those are tracked separately.
Merge rather than append: this replaces the existing lessons entirely and must not grow
over time. Plain bullets (- ...), under 300 words total."""


def distil_lessons(rollup: Dict[str, Any], ratings: List[Dict], api_key: str) -> bool:
    """Consolidate a batch's topical signal into rollup['lessons']. Returns True on success.

    Never raises: any failure leaves the previous lessons intact so an API outage can
    never cost us the archival run.
    """
    lines = title_lines(ratings)
    if not lines:
        return False
    if len(lines) > DISTIL_MAX_TITLES:
        lines = lines[-DISTIL_MAX_TITLES:]

    try:
        import anthropic
    except ImportError:
        print('⚠️  anthropic package unavailable — keeping statistics-only rollup')
        return False

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=DISTIL_MODEL,
            max_tokens=DISTIL_MAX_TOKENS,
            messages=[{'role': 'user',
                       'content': build_distil_prompt(lines, rollup.get('lessons', ''))}],
        )
        text = response.content[0].text.strip()
    except Exception as e:
        print(f'⚠️  Lesson distillation failed ({e}) — keeping previous lessons')
        return False

    if not text:
        return False

    try:
        import api_usage
        api_usage.record_claude_usage(response.usage)
    except Exception:
        pass

    rollup['lessons'] = text
    rollup['lessons_updated_at'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    rollup['lessons_batches'] = rollup.get('lessons_batches', 0) + 1
    return True


def rollup_summary(rollup: Optional[Dict[str, Any]] = None, top_n: int = 8) -> str:
    """Render the rollup as compact prompt-ready text. Empty string when there is none."""
    if rollup is None:
        rollup = load_rollup()
    if not rollup.get('total_ratings'):
        return ''

    totals = rollup.get('totals', {})
    lines = [
        f"Archived history: {rollup['total_ratings']} ratings "
        f"({(rollup.get('first_rated_at') or '?')[:10]} → {(rollup.get('last_rated_at') or '?')[:10]})",
        'Verdict totals: ' + ', '.join(f'{k} {v}' for k, v in sorted(totals.items())),
    ]

    # Topic/framing lessons lead: they are the part the statistics below cannot express.
    if rollup.get('lessons'):
        lines.append('Durable topic/framing lessons from archived ratings:\n'
                     + rollup['lessons'])

    def _ranked(container: Dict[str, Dict[str, int]], verdict: str, min_n: int) -> List[str]:
        rows = []
        for key, counts in container.items():
            n = sum(counts.values())
            if n >= min_n:
                rows.append((key, counts.get(verdict, 0) / n, n))
        rows.sort(key=lambda x: (-x[1], -x[2]))
        return [f'{k} ({pct:.0%} of {n})' for k, pct, n in rows[:top_n] if pct > 0]

    liked = _ranked(rollup.get('by_source', {}), 'good', 5)
    disliked = _ranked(rollup.get('by_source', {}), 'bad', 5)
    if liked:
        lines.append('Historically liked sources: ' + ', '.join(liked))
    if disliked:
        lines.append('Historically disliked sources: ' + ', '.join(disliked))

    weak_cats = _ranked(rollup.get('by_category', {}), 'bad', 5)
    if weak_cats:
        lines.append('Historically weak categories: ' + ', '.join(weak_cats))

    day_lines = [
        f'{frm} → {to} ({n})'
        for frm, tos in rollup.get('day_reassignments', {}).items()
        for to, n in sorted(tos.items(), key=lambda x: -x[1]) if n >= 2
    ]
    if day_lines:
        lines.append('Recurring day reassignments: ' + ', '.join(day_lines[:top_n]))

    retag_lines = [
        f'{frm} → {to} ({n})'
        for frm, tos in rollup.get('category_retags', {}).items()
        for to, n in sorted(tos.items(), key=lambda x: -x[1]) if n >= 2
    ]
    if retag_lines:
        lines.append('Recurring category retags: ' + ', '.join(retag_lines[:top_n]))

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Archival
# ---------------------------------------------------------------------------

def live_files() -> List[Path]:
    if not FEEDBACK_DIR.exists():
        return []
    return sorted(FEEDBACK_DIR.glob('????-??-??.json'))


def file_date(path: Path) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(path.stem).replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def append_shard(month: str, payload: Dict[str, Any]) -> Path:
    """Append one original file object as a line to that month's gzipped JSONL shard."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    shard = ARCHIVE_DIR / f'{month}.jsonl.gz'
    with gzip.open(shard, 'at', encoding='utf-8') as fh:
        fh.write(json.dumps(payload, separators=(',', ':')) + '\n')
    return shard


def read_archived_ratings(archive_dir: Path = ARCHIVE_DIR) -> List[Dict]:
    """All ratings from every archive shard. Used by the weekly offline audit."""
    ratings: List[Dict] = []
    if not archive_dir.exists():
        return ratings
    for shard in sorted(archive_dir.glob('*.jsonl.gz')):
        try:
            with gzip.open(shard, 'rt', encoding='utf-8') as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    ratings.extend(entry.get('ratings', []))
        except Exception as e:
            print(f'⚠️  Skipping unreadable shard {shard.name}: {e}')
    return ratings


def prune_ledger(urls: Dict[str, str], ledger_days: int) -> int:
    """Drop ledger entries older than the horizon. Returns the number removed.

    Safe because the curator only ever scores articles from the last `lookback_hours`
    (48h), and the longest pool an article can linger in is the 28-day theme holdover.
    A 180-day default leaves a wide margin while keeping the ledger bounded.
    """
    if ledger_days <= 0:
        return 0
    cutoff = (datetime.now(timezone.utc) - timedelta(days=ledger_days)).isoformat()
    stale = [u for u, ts in urls.items() if ts and ts < cutoff]
    for u in stale:
        del urls[u]
    return len(stale)


def archive(retention_days: int, ledger_days: int, dry_run: bool,
            distil: bool = True, api_key: str = '') -> Dict[str, Any]:
    """Distil → archive → prune. Returns a summary dict."""
    rollup = load_rollup()
    already = set(rollup.get('archived_files', []))
    ledger = load_ledger()

    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    files = live_files()

    archived: List[str] = []
    batch_ratings: List[Dict] = []
    absorbed_total = 0
    new_urls = 0
    bytes_freed = 0

    for path in files:
        data = _read_json(path)
        if not isinstance(data, dict):
            print(f'⚠️  Skipping unreadable {path.name}')
            continue
        ratings = data.get('ratings') or []

        # Every rated URL enters the ledger, whether or not the file is old enough
        # to archive — this is what lets the curator stop walking the directory.
        for r in ratings:
            url = r.get('url')
            if not url:
                continue
            rated_at = r.get('rated_at') or data.get('submitted_at') or ''
            if url not in ledger:
                new_urls += 1
            if rated_at >= ledger.get(url, ''):
                ledger[url] = rated_at

        date = file_date(path)
        if date is None or date >= cutoff:
            continue
        if path.name in already:
            # Rollup already absorbed it on a previous run but the file survived
            # (interrupted run); remove it without double-counting the aggregates.
            print(f'   {path.name} already in rollup — removing stale copy')
            if not dry_run:
                bytes_freed += path.stat().st_size
                path.unlink()
            archived.append(path.name)
            continue

        absorbed = fold_into_rollup(rollup, ratings)
        absorbed_total += absorbed
        archived.append(path.name)
        batch_ratings.extend(ratings)
        rollup.setdefault('archived_files', []).append(path.name)

        if not dry_run:
            append_shard(path.stem[:7], data)
            bytes_freed += path.stat().st_size
            path.unlink()

    pruned = prune_ledger(ledger, ledger_days)

    # One Haiku call per batch, only when something actually crossed the boundary.
    # Statistics are already safely folded in by this point, so a failure here costs
    # nothing but the prose layer.
    distilled = False
    if batch_ratings and distil and not dry_run:
        if api_key:
            print(f'   🤖 Distilling topic/framing lessons from {len(batch_ratings)} archived ratings...')
            distilled = distil_lessons(rollup, batch_ratings, api_key)
        else:
            print('   ⚠️  No ANTHROPIC_API_KEY — statistics-only rollup (topic signal not distilled)')

    if not dry_run:
        rollup['archived_files'] = sorted(set(rollup.get('archived_files', [])))
        save_rollup(rollup)
        save_ledger(ledger)

    return {
        'archived_files': archived,
        'ratings_absorbed': absorbed_total,
        'ledger_size': len(ledger),
        'ledger_new': new_urls,
        'ledger_pruned': pruned,
        'bytes_freed': bytes_freed,
        'remaining_files': len(live_files()),
        'rollup_total': rollup.get('total_ratings', 0),
        'distilled': distilled,
        'lessons_words': len((rollup.get('lessons') or '').split()),
    }


def build_log_entry(result: Dict[str, Any], retention_days: int, dry_run: bool) -> str:
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    status = '(DRY RUN — no changes written)' if dry_run else '✅ archived'
    files = result['archived_files']
    span = f'{files[0]} … {files[-1]}' if len(files) > 1 else (files[0] if files else 'none')
    if result.get('distilled'):
        lessons = f"✅ consolidated to {result['lessons_words']} words"
    elif files:
        lessons = '⚠️ not run — statistics only'
    else:
        lessons = 'n/a (no batch archived)'
    return f"""## Feedback Archive Run — {now}

**Status:** {status}
**Retention:** {retention_days} days
**Files archived:** {len(files)} ({span})
**Ratings folded into rollup:** {result['ratings_absorbed']} (rollup now holds {result['rollup_total']})
**Topic/framing lessons:** {lessons}
**Raw bytes freed:** {result['bytes_freed'] / 1024:.1f} KB
**Live files remaining:** {result['remaining_files']}
**URL ledger:** {result['ledger_size']} URLs (+{result['ledger_new']} new, −{result['ledger_pruned']} pruned)

---
"""


def append_log(entry: str) -> None:
    existing = LOG_FILE.read_text(encoding='utf-8') if LOG_FILE.exists() else ''
    LOG_FILE.write_text(entry + existing, encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true',
                        help='Report what would be archived without writing anything.')
    parser.add_argument('--retention-days', type=int, default=None,
                        help='Override limits.feedback_retention_days.')
    parser.add_argument('--ledger-days', type=int, default=None,
                        help='Override limits.feedback_url_ledger_days (0 disables pruning).')
    parser.add_argument('--no-distil', action='store_true',
                        help='Skip the Haiku lesson-distillation call; statistics only.')
    args = parser.parse_args()

    try:
        limits = load_limits_config()
    except Exception as e:
        print(f'⚠️  Could not load limits.json ({e}); using defaults')
        limits = {}

    retention_days = args.retention_days if args.retention_days is not None else \
        int(limits.get('feedback_retention_days', DEFAULT_RETENTION_DAYS))
    ledger_days = args.ledger_days if args.ledger_days is not None else \
        int(limits.get('feedback_url_ledger_days', DEFAULT_LEDGER_DAYS))

    print(f'🗄️  Feedback Archiver — retention {retention_days}d, ledger horizon {ledger_days}d')
    if not FEEDBACK_DIR.exists():
        print('ℹ️  No feedback/ directory — nothing to do.')
        return

    result = archive(retention_days, ledger_days, args.dry_run,
                     distil=not args.no_distil, api_key=os.getenv('ANTHROPIC_API_KEY', ''))

    if result['archived_files']:
        print(f"   Archived {len(result['archived_files'])} files, "
              f"distilled {result['ratings_absorbed']} ratings, "
              f"freed {result['bytes_freed'] / 1024:.1f} KB")
        if result['distilled']:
            print(f"   Lessons consolidated to {result['lessons_words']} words")
    else:
        print(f'   No files older than {retention_days} days — nothing to archive.')
    print(f"   URL ledger: {result['ledger_size']} URLs "
          f"(+{result['ledger_new']} new, −{result['ledger_pruned']} pruned)")
    print(f"   Live files remaining: {result['remaining_files']}")

    if not args.dry_run and (result['archived_files'] or result['ledger_new']):
        append_log(build_log_entry(result, retention_days, args.dry_run))
        print(f'📝 Appended to {LOG_FILE}')

    print('✅ Feedback archival complete')


if __name__ == '__main__':
    main()
