#!/usr/bin/env python3
"""Offline audit: user review ratings vs. pipeline scoring, filtering, and theme routing.

Joins the `feedback/YYYY-MM-DD.json` ratings captured by `review.html` against
the scores the pipeline itself assigned (each rating record snapshots the
article's composite/quality/relevance, content_type, all 7 theme scores, and
the day it aired), plus run telemetry from `calibration_stats_cache.json`,
the long-run volume trend in `FEED_LOG.md`, and the committed
`CORPUS_ALIGNMENT_REPORT_*.md` filler series.

Answers: how well did scoring/prioritization match the user's verdicts per
category and per daily theme bucket, how much fluff got through, and is the
feed actually running lighter? Since 2026-10 also what one week cannot show:
findings that repeat week after week, how well each paid score predicts the
ratings against what its stage costs, and whether calibration changes landed.
Each run's headline numbers go into `reports/weekly_metrics.jsonl`.

Entirely offline — stdlib only, no API calls. Follows the same dual-output
convention as `corpus_alignment_report.py`:

    python article_review_audit.py [--output PATH] [--json-summary PATH] [--metrics-history PATH]

Defaults: `ARTICLE_REVIEW_AUDIT_<YYYY-MM-DD>.md` and (when requested)
`article_review_audit_summary.json`, which `calibration_agent.py` and
`generate_weekly_report.py` consume.
"""

import argparse
import bisect
import glob
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import config_loader
from cache import atomic_write_text

BASE_DIR = Path(__file__).parent
FEEDBACK_DIR = BASE_DIR / 'feedback'
FEED_LOG_FILE = BASE_DIR / 'FEED_LOG.md'
CALIBRATION_STATS_FILE = BASE_DIR / 'calibration_stats_cache.json'
CALIBRATION_LOG_FILE = BASE_DIR / 'CALIBRATION_LOG.md'
THEME_HOLDOVER_FILE = BASE_DIR / 'theme_holdover_cache.json'
METRICS_HISTORY_FILE = BASE_DIR / 'reports' / 'weekly_metrics.jsonl'
CHANGE_HISTORY_FILE = BASE_DIR / 'calibration_memory' / 'change_history.json'
POOL_CACHE_FILE = BASE_DIR / 'podcast_articles_cache.json'
CLAUDE_MD_FILE = BASE_DIR / 'CLAUDE.md'

WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
SCORE_BANDS = [(80, 100), (60, 79), (40, 59), (20, 39), (0, 19)]
SWEEP_THRESHOLDS = [13, 15, 20, 25, 30, 35, 40, 45, 50, 60]
MIN_SOURCE_RATINGS = 5
# A source becomes a block candidate only at this many ratings with zero positives
# of any kind (docs/decisions/scoring.md, gotcha 17).
SOURCE_BLOCK_MIN_RATINGS = 8

# review.html asks two questions — in my feed? on which podcast days? — and stores the
# answer as one verdict:
#
#                   podcast day(s)   no day
#   in my feed      good             interesting
#   not in my feed  podcast_only     bad
#
# Feed-quality metrics count good+interesting (POSITIVE). Day-fit metrics count the
# verdicts that carry approved days (DAY_FIT). 'podcast_only' is neither a feed
# positive nor a dislike, so it never counts toward blocking a source.
POSITIVE = ('good', 'interesting', 'exemplar')
DAY_FIT = ('good', 'podcast_only')
VERDICTS = ('good', 'interesting', 'podcast_only', 'bad', 'skip')
RATED = ('good', 'interesting', 'podcast_only', 'bad')  # every verdict but skip


def _positive(counts: Counter) -> int:
    return sum(counts[v] for v in POSITIVE)


def _pct(part: int, whole: int) -> Optional[float]:
    return round(100 * part / whole, 1) if whole else None


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_ratings(feedback_dir: Path = FEEDBACK_DIR) -> List[Dict]:
    """All ratings, live and archived, deduplicated by URL (latest wins).

    Live files cover the retention window; older ratings live in the gzipped shards
    written by feedback_archive.py, so the audit keeps its full horizon even after the
    raw `feedback/YYYY-MM-DD.json` files have been compressed away.
    """
    by_url: Dict[str, Dict] = {}

    def absorb(ratings: List[Dict]) -> None:
        for rating in ratings:
            url = rating.get('url')
            if not url or rating.get('rating') not in VERDICTS:
                continue
            prev = by_url.get(url)
            if prev is None or (rating.get('rated_at') or '') >= (prev.get('rated_at') or ''):
                by_url[url] = rating

    try:
        from feedback_archive import read_archived_ratings
        absorb(read_archived_ratings(feedback_dir / 'archive'))
    except Exception as e:
        print(f'⚠️ Could not read archived feedback shards: {e}')

    for path in sorted(glob.glob(str(feedback_dir / '????-??-??.json'))):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue
        absorb(data.get('ratings', []))

    return sorted(by_url.values(), key=lambda r: r.get('rated_at') or '')


def load_calibration_runs() -> List[Dict]:
    try:
        with open(CALIBRATION_STATS_FILE, 'r', encoding='utf-8') as f:
            records = json.load(f)
        return records if isinstance(records, list) else []
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Section 1 — scoring precision vs. verdicts
# ---------------------------------------------------------------------------

def _is_blocked(source: str, blocked: List[str]) -> bool:
    """The curator's own rule: a blocked entry anywhere in the lowercased source name."""
    source_lower = (source or '').lower()
    return any(entry in source_lower for entry in blocked)


def rating_distribution(ratings: List[Dict], blocked: Optional[List[str]] = None) -> Dict[str, Any]:
    if blocked is None:
        try:
            blocked = [b.lower() for b in config_loader.get_blocked_sources()]
        except Exception:
            blocked = []
    counts = Counter(r['rating'] for r in ratings)
    total = len(ratings)
    by_category: Dict[str, Counter] = defaultdict(Counter)
    by_source: Dict[str, Counter] = defaultdict(Counter)
    for r in ratings:
        by_category[r.get('category') or 'unknown'][r['rating']] += 1
        by_source[r.get('source') or 'unknown'][r['rating']] += 1

    def _cell(c: Counter) -> Dict[str, Any]:
        n = sum(c.values())
        return {'n': n, 'good': c['good'], 'interesting': c['interesting'], 'bad': c['bad'],
                'podcast_only': c['podcast_only'], 'positive': _positive(c),
                'good_pct': _pct(c['good'], n) or 0.0, 'bad_pct': _pct(c['bad'], n) or 0.0,
                'positive_pct': _pct(_positive(c), n) or 0.0}

    categories = {
        cat: _cell(c)
        for cat, c in sorted(by_category.items(), key=lambda kv: -sum(kv[1].values()))
    }
    sources = {
        src: _cell(c)
        for src, c in by_source.items() if sum(c.values()) >= MIN_SOURCE_RATINGS
    }
    for src, cell in sources.items():
        # A blocked source leaves the podcast pool too, so show-only material protects it.
        cell['block_candidate'] = (cell['n'] >= SOURCE_BLOCK_MIN_RATINGS
                                   and cell['positive'] == 0 and cell['podcast_only'] == 0)
        cell['blocked'] = _is_blocked(src, blocked)
    # Ranked on positives, not good alone: a source with only 'interesting' ratings
    # is wanted material, and a good-only ranking made it look like a free cut.
    best_sources = sorted(sources.items(), key=lambda kv: (-kv[1]['positive_pct'], -kv[1]['n']))[:10]
    # Blocked sources keep their old ratings forever. Rolling Stone, The New Yorker
    # and Cottage Life were blocked on 2026-09-24 and still headed this list in the
    # next two audits, and the calibration notes kept recommending those blocks.
    worst_sources = sorted(((s, c) for s, c in sources.items() if not c['blocked']),
                           key=lambda kv: (kv[1]['positive_pct'], -kv[1]['n']))[:10]

    return {
        'total': total,
        'counts': dict(counts),
        'bad_pct': round(100 * counts['bad'] / total, 1) if total else 0.0,
        'good_pct': round(100 * counts['good'] / total, 1) if total else 0.0,
        'positive_pct': _pct(_positive(counts), total) or 0.0,
        'by_category': categories,
        'best_sources': dict(best_sources),
        'worst_sources': dict(worst_sources),
    }


SHIPPED_STRATA = ('high', 'mid', 'promising', 'border', 'low', 'floor_fill')


def stratified_estimate(ratings: List[Dict]) -> Dict[str, Any]:
    """Reweight the quota sample back to the population it was drawn from.

    The review feed is a stratified sample with fixed quotas — a handful from each
    score band (and the high-relevance 'promising' slice
    carved out of the sub-50 bands) plus a few scrub rejects — so the raw good-rate across all
    ratings describes that quota design, not the feed. Rates *within* a stratum are
    unbiased; the overall number is only meaningful once each rating is weighted by
    how many articles it stands for.

    It also matters which side of the pipeline a rating is on. A 'bad' verdict on a
    scrub reject is the pipeline working; a 'bad' verdict on something that shipped
    is the pipeline failing. Summing them, as the old headline did, reported 67.5%
    bad on a corpus where two thirds of the bad verdicts were correct rejections.
    """
    per_stratum: Dict[str, Dict[str, Any]] = {}
    for r in ratings:
        b = r.get('selection_bucket') or 'unknown'
        cell = per_stratum.setdefault(
            b, {'n': 0, 'good': 0, 'interesting': 0, 'podcast_only': 0, 'bad': 0,
                'weight_sum': 0.0, 'weighted': 0})
        cell['n'] += 1
        if r['rating'] in ('good', 'interesting', 'podcast_only', 'bad'):
            cell[r['rating']] += 1
        w = r.get('stratum_weight')
        if isinstance(w, (int, float)) and w > 0:
            cell['weight_sum'] += w
            cell['weighted'] += 1
    for cell in per_stratum.values():
        n = cell['n']
        cell['good_pct'] = round(100 * cell['good'] / n, 1) if n else 0.0
        cell['positive_pct'] = round(100 * (cell['good'] + cell['interesting']) / n, 1) if n else 0.0

    # Weighted estimate over what actually shipped. Only rows carrying a recorded
    # weight can contribute; `coverage` says how much of the corpus that is, so a
    # thin estimate reads as thin rather than as fact.
    num = den = 0.0
    weighted_rows = 0
    for r in ratings:
        if (r.get('selection_bucket') or '') not in SHIPPED_STRATA:
            continue
        w = r.get('stratum_weight')
        if not isinstance(w, (int, float)) or w <= 0:
            continue
        weighted_rows += 1
        den += w
        if r['rating'] in POSITIVE:
            num += w
    shipped_rows = sum(1 for r in ratings if (r.get('selection_bucket') or '') in SHIPPED_STRATA)

    # Shipped vs correctly-rejected split of the bad verdicts.
    bad_shipped = sum(1 for r in ratings
                      if r['rating'] == 'bad' and (r.get('selection_bucket') or '') in SHIPPED_STRATA)
    bad_rejected = sum(1 for r in ratings
                       if r['rating'] == 'bad' and r.get('selection_bucket') == 'unfiltered')
    rejects = [r for r in ratings if r.get('selection_bucket') == 'unfiltered']
    false_neg = sum(1 for r in rejects if r['rating'] in POSITIVE)

    return {
        'per_stratum': per_stratum,
        'weighted_positive_pct': round(100 * num / den, 1) if den else None,
        'weight_coverage_pct': round(100 * weighted_rows / shipped_rows, 1) if shipped_rows else 0.0,
        'weighted_rows': weighted_rows,
        'shipped_rows': shipped_rows,
        'bad_shipped': bad_shipped,
        'bad_correctly_rejected': bad_rejected,
        'rejects_n': len(rejects),
        'reject_false_negative_pct': round(100 * false_neg / len(rejects), 1) if rejects else 0.0,
    }


def score_stats_by_rating(ratings: List[Dict]) -> Dict[str, Dict[str, float]]:
    stats: Dict[str, Dict[str, float]] = {}
    for verdict in ('good', 'interesting', 'podcast_only', 'bad'):
        rows = [r for r in ratings if r['rating'] == verdict and isinstance(r.get('score'), (int, float))]
        if not rows:
            continue
        stats[verdict] = {
            'n': len(rows),
            'mean_score': round(statistics.mean(r['score'] for r in rows), 1),
            'median_score': round(statistics.median(r['score'] for r in rows), 1),
            'mean_quality': round(statistics.mean(r.get('quality') or 0 for r in rows), 1),
            'mean_relevance': round(statistics.mean(r.get('relevance') or 0 for r in rows), 1),
        }
    return stats


def band_precision(ratings: List[Dict]) -> List[Dict[str, Any]]:
    bands = []
    for lo, hi in SCORE_BANDS:
        rows = [r for r in ratings if isinstance(r.get('score'), (int, float)) and lo <= r['score'] <= hi]
        counts = Counter(r['rating'] for r in rows)
        n = len(rows)
        bands.append({
            'band': f'{lo}-{hi}',
            'n': n,
            'good': counts['good'],
            'interesting': counts['interesting'],
            'bad': counts['bad'],
            'good_pct': _pct(counts['good'], n),
            'positive_pct': _pct(_positive(counts), n),
            'bad_pct': _pct(counts['bad'], n),
        })
    return bands


def threshold_sweep(ratings: List[Dict]) -> List[Dict[str, Any]]:
    """For each candidate min-score floor: how much bad is cut vs. wanted articles lost.

    'interesting' articles carry low relevance scores, so a floor raise costs them
    first; `positive_lost_pct` is the number to weigh against `bad_cut_pct`.
    """
    scored = [r for r in ratings if isinstance(r.get('score'), (int, float))]
    totals = Counter(r['rating'] for r in scored)
    sweep = []
    for t in SWEEP_THRESHOLDS:
        below = Counter(r['rating'] for r in scored if r['score'] < t)
        sweep.append({
            'threshold': t,
            'bad_cut': below['bad'],
            'bad_cut_pct': _pct(below['bad'], totals['bad']) or 0.0,
            'good_lost': below['good'],
            'good_lost_pct': _pct(below['good'], totals['good']) or 0.0,
            'interesting_lost': below['interesting'],
            'interesting_lost_pct': _pct(below['interesting'], totals['interesting']) or 0.0,
            'positive_lost': _positive(below),
            'positive_lost_pct': _pct(_positive(below), _positive(totals)) or 0.0,
        })
    return sweep


def content_type_by_rating(ratings: List[Dict]) -> Dict[str, Dict[str, int]]:
    table: Dict[str, Counter] = defaultdict(Counter)
    for r in ratings:
        table[str(r.get('content_type') or 'unlabeled')][r['rating']] += 1
    return {ct: dict(c) for ct, c in sorted(table.items(), key=lambda kv: -sum(kv[1].values()))}


def bucket_by_rating(ratings: List[Dict]) -> Dict[str, Dict[str, int]]:
    table: Dict[str, Counter] = defaultdict(Counter)
    for r in ratings:
        table[str(r.get('selection_bucket') or 'unknown')][r['rating']] += 1
    return {b: dict(c) for b, c in table.items()}


# ---------------------------------------------------------------------------
# Section 3 — theme-bucket routing accuracy
# ---------------------------------------------------------------------------

def theme_routing_audit(ratings: List[Dict]) -> Dict[str, Any]:
    with_day = [r for r in ratings if r.get('today') in WEEKDAYS]
    corrections = [
        r for r in with_day
        if r.get('better_theme') in WEEKDAYS and r['better_theme'] != r['today']
    ]

    confusion: Dict[str, Dict[str, int]] = {d: defaultdict(int) for d in WEEKDAYS}
    for r in corrections:
        confusion[r['today']][r['better_theme']] += 1

    # Approved-day reassignments (day-fit articles routed to extra/other days)
    reassigned_via_days = [
        r for r in with_day
        if r['rating'] in DAY_FIT and r.get('approved_days')
        and any(d != r['today'] for d in r['approved_days'] if d in WEEKDAYS)
    ]

    # Root-cause split: did the pipeline's own theme scores already prefer the
    # user's corrected day? If yes, selection ignored its own signal (routing);
    # if no, the theme scorer itself missed (scoring).
    # How many of these corrections are about an article podcast selection actually
    # routed? `today` is the weekday the rating was made, not a routing decision, and
    # almost every rated article comes from a *category* feed. So a correction where
    # the theme scorer already preferred your day is not evidence of a routing bug —
    # the router never saw the article. Counting it as one sends people looking for a
    # defect in generate_podcast_feed() that is not there.
    podcast_routed = sum(
        1 for r in corrections if str(r.get('category') or '').startswith('podcast-'))

    routing_bugs = scoring_misses = unsplittable = 0
    for r in corrections:
        ts = r.get('theme_scores') or {}
        today_score, better_score = ts.get(r['today']), ts.get(r['better_theme'])
        if not isinstance(today_score, (int, float)) or not isinstance(better_score, (int, float)):
            unsplittable += 1
        elif better_score > today_score:
            routing_bugs += 1
        else:
            scoring_misses += 1

    per_day: Dict[str, Dict[str, Any]] = {}
    for day in WEEKDAYS:
        rows = [r for r in with_day if r['today'] == day]
        if not rows:
            continue
        counts = Counter(r['rating'] for r in rows)
        labels = Counter(r.get('today_label') for r in rows if r.get('today_label'))
        n = len(rows)
        # good_pct is day fit (good + podcast_only, the verdicts that carry days);
        # positive_pct is feed fit (good + interesting).
        per_day[day] = {
            'label': labels.most_common(1)[0][0] if labels else '',
            'n': n,
            'good': counts['good'],
            'interesting': counts['interesting'],
            'podcast_only': counts['podcast_only'],
            'bad': counts['bad'],
            'good_pct': round(100 * sum(counts[v] for v in DAY_FIT) / n, 1),
            'positive_pct': round(100 * _positive(counts) / n, 1),
            'corrected_away': sum(1 for r in corrections if r['today'] == day),
        }

    n_day = len(with_day)
    return {
        'rated_with_day': n_day,
        'corrections': len(corrections),
        'correction_pct': round(100 * len(corrections) / n_day, 1) if n_day else 0.0,
        'reassigned_via_approved_days': len(reassigned_via_days),
        'confusion': {d: dict(t) for d, t in confusion.items() if t},
        'podcast_routed': podcast_routed,
        'root_cause': {
            'routing_bug': routing_bugs,
            'theme_scoring_miss': scoring_misses,
            'missing_scores': unsplittable,
        },
        'per_day': per_day,
    }


# ---------------------------------------------------------------------------
# Section 3b — category retag accuracy
# ---------------------------------------------------------------------------

def category_retag_audit(ratings: List[Dict]) -> Dict[str, Any]:
    with_category = [r for r in ratings if r.get('original_category')]
    corrections = [
        r for r in with_category
        if r.get('category') and r['category'] != r['original_category']
    ]

    confusion: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in corrections:
        confusion[r['original_category']][r['category']] += 1

    n = len(with_category)
    return {
        'rated_with_category': n,
        'corrections': len(corrections),
        'correction_pct': round(100 * len(corrections) / n, 1) if n else 0.0,
        'confusion': {k: dict(v) for k, v in confusion.items()},
    }


# ---------------------------------------------------------------------------
# Section 4 — volume trend
# ---------------------------------------------------------------------------

def parse_feed_log(path: Path = FEED_LOG_FILE) -> List[Dict[str, Any]]:
    """Per-ISO-week averages of fetched/quality per run, oldest first."""
    try:
        text = path.read_text(encoding='utf-8')
    except Exception:
        return []

    daily: List[Tuple[str, int, float, float]] = []  # (date, runs, avg_fetched, avg_quality)

    for m in re.finditer(
        r'^## Week of (\d{4}-\d{2}-\d{2})[^\n]*\n- (\d+) runs · avg fetched (\d+) · avg quality (\d+)',
        text, re.MULTILINE,
    ):
        daily.append((m.group(1), int(m.group(2)), float(m.group(3)), float(m.group(4))))

    for m in re.finditer(r'^## (\d{4}-\d{2}-\d{2}) \((.*?)\)\n(.*?)(?=^## |\Z)', text, re.MULTILINE | re.DOTALL):
        date, body = m.group(1), m.group(3)
        runs = re.findall(
            r'Fetched \*\*(\d+)\*\* → dedup \*\*\d+\*\* → new \*\*\d+\*\* → quality \*\*(\d+)\*\*', body)
        if runs:
            fetched = [int(a) for a, _ in runs]
            quality = [int(b) for _, b in runs]
            daily.append((date, len(runs),
                          sum(fetched) / len(fetched), sum(quality) / len(quality)))

    weeks: Dict[str, Dict[str, float]] = defaultdict(lambda: {'runs': 0, 'fetched': 0.0, 'quality': 0.0})
    for date_str, runs, fetched, quality in daily:
        try:
            iso = datetime.strptime(date_str, '%Y-%m-%d').isocalendar()
        except ValueError:
            continue
        key = f'{iso.year}-W{iso.week:02d}'
        w = weeks[key]
        w['runs'] += runs
        w['fetched'] += fetched * runs
        w['quality'] += quality * runs

    trend = []
    for key in sorted(weeks):
        w = weeks[key]
        if w['runs']:
            trend.append({
                'week': key,
                'runs': int(w['runs']),
                'avg_fetched': round(w['fetched'] / w['runs']),
                'avg_quality': round(w['quality'] / w['runs']),
            })
    return trend


def current_funnel(runs: List[Dict]) -> Dict[str, Any]:
    if not runs:
        return {}
    funnel = []
    scrub_removed = 0
    quality_dropped = 0
    for r in runs:
        ingest = r.get('ingest', {})
        qg = r.get('quality_gate', {})
        passed = sum(qg.get('passed_by_category', {}).values())
        dropped = sum(qg.get('dropped_below_floor_by_category', {}).values())
        scrub = r.get('scrub', {})
        removed = (sum(scrub.get('cohere_removed_by_category', {}).values())
                   + sum(scrub.get('haiku_removed_by_category', {}).values()))
        scrub_removed += removed
        quality_dropped += dropped
        funnel.append({
            'run_id': r.get('run_id'),
            'fetched': ingest.get('fetched'),
            'new': ingest.get('new'),
            'quality_passed': passed,
            'quality_dropped': dropped,
            'scrub_removed': removed,
        })
    return {
        'runs': funnel,
        'first': runs[0].get('timestamp'),
        'last': runs[-1].get('timestamp'),
        'total_scrub_removed': scrub_removed,
        'total_quality_dropped': quality_dropped,
    }


def feed_item_counts() -> Dict[str, int]:
    counts = {}
    for path in sorted(BASE_DIR.glob('feed-*.json')):
        if path.name.startswith('feed-podcast-'):
            continue
        try:
            with open(path, 'r', encoding='utf-8') as f:
                counts[path.stem.replace('feed-', '')] = len(json.load(f).get('items', []))
        except Exception:
            continue
    return counts


# ---------------------------------------------------------------------------
# Section 2b — filler trend from committed alignment reports
# ---------------------------------------------------------------------------

def filler_trend() -> List[Dict[str, Any]]:
    trend = []
    for path in sorted((BASE_DIR / 'reports').glob('CORPUS_ALIGNMENT_REPORT_*.md')):
        m_date = re.search(r'(\d{4}-\d{2}-\d{2})', path.name)
        try:
            text = path.read_text(encoding='utf-8')
        except Exception:
            continue
        m_total = re.search(r'Articles analysed \| (\d+)', text)
        m_filler = re.search(r'\| Filler [^|]*\| (\d+) \((\d+)%', text)
        if m_date and m_total and m_filler:
            trend.append({
                'date': m_date.group(1),
                'analysed': int(m_total.group(1)),
                'filler': int(m_filler.group(1)),
                'filler_pct': int(m_filler.group(2)),
            })
    return trend


# ---------------------------------------------------------------------------
# Section 5 — process health
# ---------------------------------------------------------------------------

def process_health(runs: List[Dict]) -> Dict[str, Any]:
    calibration_entries = failed_entries = 0
    try:
        log_text = CALIBRATION_LOG_FILE.read_text(encoding='utf-8')
        calibration_entries = len(re.findall(r'^## \d{4}-\d{2}-\d{2}', log_text, re.MULTILINE))
        failed_entries = log_text.count('No changes:')
    except Exception:
        pass
    return {
        'calibration_log_entries': calibration_entries,
        'calibration_no_change_entries': failed_entries,
        'calibration_stats_runs': len(runs),
        'calibration_stats_range': (
            f"{runs[0].get('timestamp', '?')[:10]} → {runs[-1].get('timestamp', '?')[:10]}"
            if runs else 'no data'),
        'theme_holdover_cache_present': THEME_HOLDOVER_FILE.exists(),
    }


# ---------------------------------------------------------------------------
# Reader model — the order review.html shows the daily batch in
# ---------------------------------------------------------------------------

# A per-field log-odds table, each value shrunk toward the base rate, summed. Fitted on a
# time split (train before 2026-09-15, test the 11 review days after) it ranks each
# day's batch at AUC 0.81 against 0.75 for the old stratum-then-score order, and puts
# 72% positives in the top ten against 63%. A logistic fit on the same fields scored no
# better. Source carries most of it: dropping it costs 0.05 AUC, any other field < 0.02.
READER_MODEL_FIELDS = ('selection_bucket', 'source', 'original_category', 'content_type',
                       'relevance_band')
READER_MODEL_PRIOR = 4.0      # pseudo-ratings pulling each value toward the base rate
READER_MODEL_MIN_SOURCE = 3   # ratings a source needs before it gets its own term


def _reader_value(row: Dict, field: str) -> Any:
    if field == 'relevance_band':
        relevance = row.get('relevance')
        return int(relevance) // 20 if isinstance(relevance, (int, float)) else None
    if field == 'original_category':
        return row.get('original_category') or row.get('category')
    return row.get(field)


def fit_reader_model(ratings: List[Dict]) -> Optional[Callable[[Dict], float]]:
    """P(the reader wants this) for a rating-shaped dict; None without both outcomes.

    "Wants" is any verdict but 'bad': in the feed, on the show, or both. Only the order
    uses this — the review sample itself stays stratified.
    """
    rows = [r for r in ratings if r.get('rating') in ('good', 'interesting', 'podcast_only', 'bad')]
    wanted = sum(1 for r in rows if r['rating'] != 'bad')
    if not wanted or wanted == len(rows):
        return None
    base = wanted / len(rows)
    base_logit = math.log(base / (1 - base))

    tables: Dict[str, Dict[Any, float]] = {}
    for field in READER_MODEL_FIELDS:
        counts: Dict[Any, List[int]] = defaultdict(lambda: [0, 0])  # value -> [bad, wanted]
        for r in rows:
            counts[_reader_value(r, field)][r['rating'] != 'bad'] += 1
        min_n = READER_MODEL_MIN_SOURCE if field == 'source' else 1
        tables[field] = {
            value: math.log((w + READER_MODEL_PRIOR * base)
                            / (b + READER_MODEL_PRIOR * (1 - base))) - base_logit
            for value, (b, w) in counts.items() if b + w >= min_n
        }

    def predict(row: Dict) -> float:
        z = base_logit + sum(table.get(_reader_value(row, field), 0.0)
                             for field, table in tables.items())
        return 1 / (1 + math.exp(-z))

    return predict


# ---------------------------------------------------------------------------
# Section 6 — what one week's snapshot cannot see
# ---------------------------------------------------------------------------

TREND_WINDOW_DAYS = 28          # a rate needs more than one week of ratings to read
COVERAGE_MIN_RATINGS = 20       # under this in TREND_WINDOW_DAYS a category is unmeasured
VERDICT_WINDOW_DAYS = 14
VERDICT_MIN_RATINGS = 50        # a verdict unused across this many ratings is a dead channel
GATE_MISS_FLAG_PCT = 10.0       # wanted share of rated rejects that makes the gate a finding
GATE_MISS_MIN_REJECTS = 20
GATE_MISS_MIN_WANTED = 3        # wanted rejects a source needs before it is named
PLACE_MIN_RATINGS = 5
PLACE_APPETITE_MARGIN = 15.0    # points above the corpus wanted rate
PLACE_STARVED_POOL_PCT = 1.0    # share of the podcast pool mentioning the place
SCORECARD_TEST_WEEKS = 4
AUC_MIN_CLASS = 10
REPEAT_ESCALATE_WEEKS = 3
BEFORE_AFTER_DAYS = 14
PRICE_TABLE_MAX_AGE_DAYS = 30
TREND_REPORT_WEEKS = 12

# The scores a rating snapshots, and the pipeline stage that pays for each
# (`api_usage` stage names). 'quality' is q_gate outside the news head.
SCORECARD_SIGNALS = (
    ('score', 'final score', 'gate + deep_score'),
    ('quality', 'quality (Q)', 'deep_score; q_gate elsewhere'),
    ('relevance', 'relevance (R)', 'deep_score'),
    ('local', 'local (L)', 'deep_score'),
    ('theme_today', "theme fit for that day's theme", 'theme_ingest / theme / theme_batch'),
    ('reader_model', 'reader model', 'free: your earlier ratings'),
)


def _rated_on(rating: Dict) -> Optional[date]:
    try:
        return date.fromisoformat(str(rating.get('rated_at') or '')[:10])
    except ValueError:
        return None


def _rated_between(ratings: List[Dict], start: date, end: date) -> List[Dict]:
    """Verdicts (no skips) rated on days start <= day < end."""
    return [r for r in ratings
            if r['rating'] in RATED and (day := _rated_on(r)) is not None and start <= day < end]


def _rated_within(ratings: List[Dict], today: date, days: int) -> List[Dict]:
    """Verdicts rated in the `days` days ending with `today`."""
    return _rated_between(ratings, today - timedelta(days=days - 1), today + timedelta(days=1))


def _shown_category(rating: Dict) -> str:
    """The category the pipeline showed, before any retag."""
    return rating.get('original_category') or rating.get('category') or 'unknown'


def _text(item: Dict) -> str:
    return f"{item.get('title') or ''} {item.get('description') or ''}".lower()


def _wanted_pct(rows: List[Dict]) -> Optional[float]:
    return _pct(sum(1 for r in rows if r['rating'] != 'bad'), len(rows))


def _load_json(path: Path, default: Any) -> Any:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def auc(pairs: List[Tuple[Any, bool]]) -> Optional[float]:
    """P(a wanted article outscores an unwanted one), ties counted half; None when thin.

    0.5 is a coin flip. It ignores the score's scale, so a 0-100 score, a percentile
    and a probability are graded alike.
    """
    scored = [(s, wanted) for s, wanted in pairs if isinstance(s, (int, float))]
    wanted_scores = [s for s, wanted in scored if wanted]
    unwanted = sorted(s for s, wanted in scored if not wanted)
    if len(wanted_scores) < AUC_MIN_CLASS or len(unwanted) < AUC_MIN_CLASS:
        return None
    wins = 0.0
    for s in wanted_scores:
        below = bisect.bisect_left(unwanted, s)
        wins += below + 0.5 * (bisect.bisect_right(unwanted, s) - below)
    return round(wins / (len(wanted_scores) * len(unwanted)), 3)


def signal_scorecard(ratings: List[Dict], today: date) -> Dict[str, Any]:
    """How well each score separates what you wanted from what you didn't, out of time.

    Graded on the last SCORECARD_TEST_WEEKS weeks of ratings. The reader model is refit
    for each week on the ratings made before it, so it is never graded on a rating it
    saw; the paid scores are graded on the same rows. Theme fit is graded on day fit
    (good / podcast_only), every other signal on wanted (any verdict but bad).
    """
    rows: List[Dict] = []
    predictions: List[float] = []
    for weeks_back in range(SCORECARD_TEST_WEEKS, 0, -1):
        start = today - timedelta(days=7 * weeks_back - 1)
        test = _rated_between(ratings, start, start + timedelta(days=7))
        model = fit_reader_model([r for r in ratings
                                  if (day := _rated_on(r)) is not None and day < start])
        if test and model is not None:
            rows += test
            predictions += [model(r) for r in test]

    def value(row: Dict, prediction: float, key: str) -> Any:
        if key == 'reader_model':
            return prediction
        if key == 'theme_today':
            return (row.get('theme_scores') or {}).get(row.get('today'))
        return row.get(key)

    def wanted(row: Dict, key: str) -> bool:
        return row['rating'] in DAY_FIT if key == 'theme_today' else row['rating'] != 'bad'

    signals = {}
    for key, name, stage in SCORECARD_SIGNALS:
        graded = [(value(r, p, key), wanted(r, key), _shown_category(r) == 'news')
                  for r, p in zip(rows, predictions)]
        signals[key] = {
            'name': name, 'stage': stage,
            'auc': auc([(v, w) for v, w, _ in graded]),
            'auc_news': auc([(v, w) for v, w, news in graded if news]),
        }
    return {
        'weeks': SCORECARD_TEST_WEEKS,
        'n': len(rows),
        'n_news': sum(1 for r in rows if _shown_category(r) == 'news'),
        'signals': signals,
    }


def stage_costs(runs: List[Dict], today: date, days: int = 7) -> Dict[str, Any]:
    """Claude spend by pipeline stage over the last `days` days of nightly runs."""
    by_stage: Dict[str, Dict[str, Any]] = defaultdict(lambda: {'calls': 0, 'est_cost_usd': 0.0})
    in_window = with_stages = 0
    total = 0.0
    for run in runs:
        try:
            day = date.fromisoformat(str(run.get('timestamp') or '')[:10])
        except ValueError:
            continue
        if day <= today - timedelta(days=days) or day > today:
            continue
        in_window += 1
        usage = run.get('api_usage') or {}
        total += usage.get('est_cost_usd') or 0.0
        stages = usage.get('claude_by_stage') or {}
        with_stages += bool(stages)
        for stage, cell in stages.items():
            by_stage[stage]['calls'] += cell.get('calls', 0)
            by_stage[stage]['est_cost_usd'] += cell.get('est_cost_usd', 0.0)
    return {
        'days': days,
        'runs': in_window,
        'runs_with_stages': with_stages,
        'est_cost_usd': round(total, 4),
        'by_stage': {stage: {'calls': c['calls'], 'est_cost_usd': round(c['est_cost_usd'], 4)}
                     for stage, c in sorted(by_stage.items(), key=lambda kv: -kv[1]['est_cost_usd'])},
    }


def place_supply(ratings: List[Dict], pool: List[Dict],
                 places: Optional[List[str]] = None) -> Dict[str, Any]:
    """Each local place: how often you want it (appetite) against how often the pool has it.

    Places are `filters.json` → `local_signals`, the pipeline's own definition of local.
    Supply is the share of the 7-day podcast pool mentioning the place.
    """
    if places is None:
        try:
            places = config_loader.load_filters_config().get('local_signals') or []
        except Exception:
            places = []
    rated = [r for r in ratings if r['rating'] in RATED]
    baseline = _wanted_pct(rated)
    rows = []
    for place in places:
        needle = place.lower()
        mentions = [r for r in rated if needle in _text(r)]
        in_pool = sum(1 for item in pool if needle in _text(item))
        rows.append({
            'place': place,
            'rated': len(mentions),
            'wanted_pct': _wanted_pct(mentions),
            'in_pool': in_pool,
            'pool_pct': _pct(in_pool, len(pool)),
        })
    return {'baseline_wanted_pct': baseline, 'pool_size': len(pool), 'places': rows}


_KNOB_LOADERS = {
    'config/limits.json': config_loader.load_limits_config,
    'config/podcast_schedule.json': config_loader.load_podcast_schedule_config,
    'config/scoring_modifiers.json': config_loader.load_scoring_modifiers,
    'config/source_preferences.json': config_loader.load_source_preferences,
    'config/feed_slots.json': config_loader.load_feed_slots_config,
}


def _config_value(spec: Dict) -> Tuple[bool, Any]:
    """(found, value) of a calibration knob in the config on disk now."""
    loader = _KNOB_LOADERS.get(spec.get('file', ''))
    if loader is None:
        return False, None
    node: Any = loader()
    for key in spec.get('path') or []:
        if not isinstance(node, dict) or key not in node:
            return False, None
        node = node[key]
    return True, node


def calibration_followthrough(ratings: List[Dict]) -> List[Dict[str, Any]]:
    """Every applied calibration change: is it in config now, and what moved around it?

    A change logged as applied is not proof it landed: 2026-09-13 and 09-20 both
    "raised" source_preferences.kagi_search_result_limit 10 → 12 because the workflow
    committed only two config files. Only the latest change per knob can be checked
    against config. Before/after is the reweighted wanted rate of the shipped feed
    over BEFORE_AFTER_DAYS either side: a correlation, not an effect size.
    """
    changes = [c for c in _load_json(CHANGE_HISTORY_FILE, {}).get('changes', [])
               if isinstance(c, dict) and not c.get('dry_run') and c.get('knob')]
    try:
        knobs = config_loader.load_calibration_bounds().get('knobs', {})
    except Exception:
        knobs = {}
    latest = {c['knob']: i for i, c in enumerate(changes)}
    rows = []
    for i, change in enumerate(changes):
        status, current = '', None
        if latest[change['knob']] == i and change['knob'] in knobs:
            found, current = _config_value(knobs[change['knob']])
            if not found:
                status = 'not found'
            elif current == change.get('new_value'):
                status = 'in config'
            elif current == change.get('old_value'):
                status = 'not in config'
            else:
                status = 'changed since'
        row = {'run_date': change.get('run_date'), 'knob': change['knob'],
               'old_value': change.get('old_value'), 'new_value': change.get('new_value'),
               'status': status, 'current': current}
        try:
            day = date.fromisoformat(str(change.get('run_date')))
        except ValueError:
            rows.append(row)
            continue
        span = timedelta(days=BEFORE_AFTER_DAYS)
        before = stratified_estimate(_rated_between(ratings, day - span, day))
        after = stratified_estimate(_rated_between(ratings, day, day + span))
        row.update({'before_pct': before['weighted_positive_pct'], 'before_n': before['weighted_rows'],
                    'after_pct': after['weighted_positive_pct'], 'after_n': after['weighted_rows']})
        rows.append(row)
    return rows


def price_table_age(today: date) -> Optional[int]:
    """Days since CLAUDE.md's Anthropic price table was last checked; None if unreadable."""
    try:
        m = re.search(r'Anthropic prices\*\*.*?checked (\d{4}-\d{2}-\d{2})',
                      CLAUDE_MD_FILE.read_text(encoding='utf-8'))
        return (today - date.fromisoformat(m.group(1))).days if m else None
    except (OSError, ValueError):
        return None


def blind_spots(ratings: List[Dict], runs: List[Dict], today: date,
                distribution: Dict[str, Any], places: Dict[str, Any],
                followthrough: List[Dict[str, Any]],
                history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Findings no single week's numbers raise: each with how many weekly audits in a row
    have reported it. At REPEAT_ESCALATE_WEEKS it has been seen and not acted on."""
    findings: List[Dict[str, Any]] = []

    def add(finding_id: str, title: str, detail: str) -> None:
        findings.append({'id': finding_id, 'title': title, 'detail': detail})

    recent = _rated_within(ratings, today, TREND_WINDOW_DAYS)

    # Review effort follows the score-band quotas, not the categories, so a small
    # category can go a season without enough ratings to say anything about it.
    try:
        categories = config_loader.get_all_categories()
    except Exception:
        categories = []
    shown = Counter(_shown_category(r) for r in recent)
    thin = [f'{c} ({shown.get(c, 0)})' for c in categories if shown.get(c, 0) < COVERAGE_MIN_RATINGS]
    if thin:
        add('unmeasured-categories', f'{len(thin)} categories are unmeasured',
            f'Under {COVERAGE_MIN_RATINGS} ratings in {TREND_WINDOW_DAYS} days: {", ".join(thin)}. '
            f'Their rates are noise, not "fine"; news took {_pct(shown.get("news", 0), len(recent))}% '
            'of the ratings.')

    # The gate is interest-blind by design and runs before the interest ranking, so
    # what it throws away never reaches news_interests.txt; the rated rejects are the
    # only window onto it.
    rejects = [r for r in recent if r.get('selection_bucket') == 'unfiltered']
    wanted_rejects = [r for r in rejects if r['rating'] != 'bad']
    miss_pct = _pct(len(wanted_rejects), len(rejects))
    if len(rejects) >= GATE_MISS_MIN_REJECTS and (miss_pct or 0) >= GATE_MISS_FLAG_PCT:
        by_source = Counter(r.get('source') for r in ratings
                            if r.get('selection_bucket') == 'unfiltered' and r['rating'] in RATED
                            and r['rating'] != 'bad')
        named = [f'{s} ({n})' for s, n in by_source.most_common() if n >= GATE_MISS_MIN_WANTED][:6]
        add('gate-misses', f'The gate threw away {miss_pct}% of the rejects you wanted',
            f'{len(wanted_rejects)} of {len(rejects)} rated rejects in {TREND_WINDOW_DAYS} days. '
            + (f'Most often, all time: {", ".join(named)}.' if named else ''))

    last = _rated_within(ratings, today, VERDICT_WINDOW_DAYS)
    if len(last) >= VERDICT_MIN_RATINGS:
        used = Counter(r['rating'] for r in last)
        for verdict in RATED:
            if not used[verdict]:
                add(f'unused-verdict:{verdict}', f'Nobody has used "{verdict}"',
                    f'0 of {len(last)} ratings in {VERDICT_WINDOW_DAYS} days. If it is never the '
                    'answer, every metric that counts it is reading one channel.')

    # The standing guard for a starved theme (docs/decisions/podcast-pool.md).
    window_runs = [run for run in runs
                   if (run.get('theme_argmax') or {}).get('wins')
                   and str(run.get('timestamp') or '')[:10] > (today - timedelta(days=7)).isoformat()]
    if window_runs:
        try:
            schedule = config_loader.load_podcast_schedule_config()
        except Exception:
            schedule = {}
        rescored = set((schedule.get('targeted_rescore') or {}).get('days') or [])
        latest = window_runs[-1]['theme_argmax']
        top_day, top_wins = max(latest['wins'].items(), key=lambda kv: kv[1])
        top_pct = _pct(top_wins, sum(latest['wins'].values()))
        for day in WEEKDAYS:
            if any(run['theme_argmax']['wins'].get(day, 0) for run in window_runs):
                continue
            label = ((schedule.get('schedule') or {}).get(day) or {}).get('label', '')
            add(f'starved-theme:{day}', f'{day.title()} ({label}) never wins the pool',
                f'0 argmax wins in all {len(window_runs)} runs this week; {top_day} won {top_pct}% '
                f'of the latest. {"In" if day in rescored else "Not in"} targeted_rescore.days. '
                'Check scoring before sourcing: more feeds cannot fix a theme nothing can win.')

    baseline = places.get('baseline_wanted_pct') or 0.0
    starved = [p for p in places.get('places', [])
               if p['rated'] >= PLACE_MIN_RATINGS
               and (p['wanted_pct'] or 0) >= baseline + PLACE_APPETITE_MARGIN
               and p['pool_pct'] is not None and p['pool_pct'] < PLACE_STARVED_POOL_PCT]
    if starved:
        add('starved-places', 'Places you want that the pool barely carries',
            ', '.join(f"{p['place']}: {p['wanted_pct']}% wanted, {p['in_pool']} in the pool "
                      f"({p['pool_pct']}%)" for p in starved)
            + f'. Baseline {baseline}% wanted.')
    unrated = [p['place'] for p in places.get('places', []) if p['rated'] < PLACE_MIN_RATINGS]
    if unrated:
        add('unmeasured-places', 'Local places with almost no ratings',
            f'Under {PLACE_MIN_RATINGS} ratings ever: {", ".join(unrated)}.')

    candidates = [s for s, c in distribution.get('worst_sources', {}).items() if c.get('block_candidate')]
    if candidates:
        add('unblocked-candidates', 'Block candidates still unblocked',
            f'{", ".join(candidates)}: n ≥ {SOURCE_BLOCK_MIN_RATINGS} with nothing wanted. '
            'Block them in filters.json or rate why not.')

    for row in followthrough:
        if row['status'] == 'not in config':
            add(f'not-landed:{row["knob"]}', f'Calibration change never landed: {row["knob"]}',
                f'Logged {row["run_date"]} as {row["old_value"]} → {row["new_value"]}; '
                f'config still says {row["current"]}.')

    age = price_table_age(today)
    if age is not None and age > PRICE_TABLE_MAX_AGE_DAYS:
        add('stale-prices', 'The Anthropic price table is stale',
            f'CLAUDE.md prices were checked {age} days ago. Refresh them before a cost decision.')

    for finding in findings:
        finding['weeks'] = 1 + _consecutive_weeks(finding['id'], history, today)
        finding['escalate'] = finding['weeks'] >= REPEAT_ESCALATE_WEEKS
    return sorted(findings, key=lambda f: -f['weeks'])


def _consecutive_weeks(finding_id: str, history: List[Dict[str, Any]], today: date) -> int:
    """Earlier weekly audits in a row, newest first, that reported `finding_id`."""
    this_week = _iso_week(today)
    count = 0
    for record in reversed(history):
        if record.get('week') == this_week:
            continue
        if finding_id not in (record.get('findings') or []):
            break
        count += 1
    return count


def _iso_week(day: date) -> str:
    iso = day.isocalendar()
    return f'{iso.year}-W{iso.week:02d}'


def week_record(ratings: List[Dict], today: date) -> Dict[str, Any]:
    """The rating-derived metrics for the week ending `today`, rebuildable from the archive.

    Counts cover the 7 days; rates cover TREND_WINDOW_DAYS, because a week of ratings is
    too few to read a rate from.
    """
    last7 = _rated_within(ratings, today, 7)
    last28 = _rated_within(ratings, today, TREND_WINDOW_DAYS)
    verdicts = Counter(r['rating'] for r in last7)
    strat = stratified_estimate(last28)
    shown = Counter(_shown_category(r) for r in last28)
    return {
        'week': _iso_week(today),
        'through': today.isoformat(),
        'rated': len(last7),
        'verdicts': {v: verdicts[v] for v in RATED},
        'notes': sum(1 for r in last7 if r.get('note')),
        'shipped_wanted_pct_28d': strat['weighted_positive_pct'],
        'gate_miss_pct_28d': _pct(sum(1 for r in last28 if r.get('selection_bucket') == 'unfiltered'
                                      and r['rating'] != 'bad'),
                                  sum(1 for r in last28 if r.get('selection_bucket') == 'unfiltered')),
        'news_share_pct_28d': _pct(shown.get('news', 0), len(last28)),
        'rated_by_category_28d': dict(shown.most_common()),
    }


def read_metrics_history(path: Path = METRICS_HISTORY_FILE) -> List[Dict[str, Any]]:
    records = []
    try:
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.strip():
                records.append(json.loads(line))
    except (OSError, ValueError):
        return []
    return records


def merge_metrics_history(history: List[Dict[str, Any]], record: Dict[str, Any],
                          ratings: List[Dict]) -> List[Dict[str, Any]]:
    """`history` with `record` replacing its week, oldest first.

    An empty history is rebuilt from the ratings archive first, one record per week
    back to the first rating, marked `backfilled`: those have the rating-derived half
    only, since costs, scores and findings were never recorded for them.
    """
    records = list(history)
    if not records:
        days = [d for r in ratings if (d := _rated_on(r)) is not None]
        through = date.fromisoformat(record['through'])
        weeks_back = 1
        while days and through - timedelta(days=7 * weeks_back) >= min(days):
            past = week_record(ratings, through - timedelta(days=7 * weeks_back))
            past['backfilled'] = True
            records.append(past)
            weeks_back += 1
    by_week = {r['week']: r for r in records}
    by_week[record['week']] = record
    return [by_week[w] for w in sorted(by_week)]


def write_metrics_history(records: List[Dict[str, Any]], path: Path = METRICS_HISTORY_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(str(path), ''.join(
        json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n' for r in records))


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def _md_table(headers: List[str], rows: List[List[Any]]) -> str:
    out = ['| ' + ' | '.join(headers) + ' |',
           '|' + '|'.join(['---'] * len(headers)) + '|']
    out += ['| ' + ' | '.join('' if v is None else str(v) for v in row) + ' |' for row in rows]
    return '\n'.join(out)


def build_report(audit: Dict[str, Any]) -> str:
    dist = audit['distribution']
    strat = audit['stratified']
    routing = audit['theme_routing']
    category_retag = audit['category_retag']
    window = audit['window']
    lines = [
        '# Article Review Audit',
        '',
        f"_Generated: {audit['generated_at']} — ratings window {window['first']} → {window['last']}_",
        '',
        '## Executive Summary',
        '',
        _md_table(['Metric', 'Value'], [
            ['Articles rated (unique URLs)', dist['total']],
            ['Rated **bad** — reached you (pipeline failed)', strat['bad_shipped']],
            ['Rated **bad** — correctly rejected (pipeline worked)', strat['bad_correctly_rejected']],
            ['Rated **good**', f"{dist['counts'].get('good', 0)} ({dist['good_pct']}%)"],
            ['Rated **interesting** (wanted, no specific day)', dist['counts'].get('interesting', 0)],
            ['Rated **podcast only** (for the show, not your feed)', dist['counts'].get('podcast_only', 0)],
            ['Rated good or interesting (raw, quota-biased)', f"{dist['positive_pct']}%"],
            ['Reweighted good-or-interesting rate of the **shipped** feed',
             (f"{strat['weighted_positive_pct']}% "
              f"(from {strat['weight_coverage_pct']}% of shipped ratings)")
             if strat['weighted_positive_pct'] is not None
             else 'not yet estimable — no sampling weights recorded'],
            ['Scrub false-negative rate (wanted articles thrown away)',
             f"{strat['reject_false_negative_pct']}% of {strat['rejects_n']} rejects"],
            ['Theme-day corrections (`better_theme`)', f"{routing['corrections']} ({routing['correction_pct']}% of day-routed ratings)"],
            ['…where the theme scorer already preferred your day', routing['root_cause']['routing_bug']],
            ['…where the theme scorer disagreed with you', routing['root_cause']['theme_scoring_miss']],
            ['…of those, actually routed by podcast selection', routing['podcast_routed']],
            ['Category retags', f"{category_retag['corrections']} ({category_retag['correction_pct']}% of categorized ratings)"],
        ]),
        '',
        '## Needs Attention',
        '',
        '_Checks one week of numbers cannot make on its own. **Weeks** counts the weekly audits in a '
        f'row that reported it; at {REPEAT_ESCALATE_WEEKS}+ it has been seen and not acted on._',
        '',
        (_md_table(['Finding', 'Detail', 'Weeks'],
                   [[('⚠️ ' if f['escalate'] else '') + f['title'], f['detail'], f['weeks']]
                    for f in audit['blind_spots']])
         if audit['blind_spots'] else '_Nothing flagged._'),
        '',
        '### Sampling strata',
        '',
        'The review feed is a **quota** sample: a fixed handful from each score band '
        'plus up to 10 scrub rejects. Rates within a stratum are unbiased; the '
        'corpus-wide rate is not, because half the ratings come from the reject pile. '
        'Reweight before comparing anything across strata.',
        '',
        _md_table(
            ['Stratum', 'n', 'good', 'interesting', 'podcast only', 'bad', '% good', '% good+int'],
            [[b, c['n'], c['good'], c['interesting'], c['podcast_only'], c['bad'],
              c['good_pct'], c['positive_pct']]
             for b, c in sorted(strat['per_stratum'].items(), key=lambda kv: -kv[1]['n'])]),
        '',
        '## 1. Scoring Precision vs. Your Verdicts',
        '',
        '### Pipeline score by verdict',
        '',
        _md_table(
            ['Verdict', 'n', 'Mean score', 'Median', 'Mean quality (Q)', 'Mean relevance (R)'],
            [[v, s['n'], s['mean_score'], s['median_score'], s['mean_quality'], s['mean_relevance']]
             for v, s in audit['score_by_rating'].items()]),
        '',
        '### Precision by score band',
        '',
        _md_table(
            ['Score band', 'n', 'good', 'interesting', 'bad', '% good', '% good+int', '% bad'],
            [[b['band'], b['n'], b['good'], b['interesting'], b['bad'],
              b['good_pct'], b['positive_pct'], b['bad_pct']]
             for b in audit['band_precision']]),
        '',
        '### Threshold sweep — what a higher quality floor would have done',
        '',
        f"Current `min_claude_score` floor: **{audit['current_min_score']}** "
        "(manually lowered 20 → 13 on 2026-06-24).",
        '',
        '`interesting` articles score low on relevance, so a higher floor costs them first. '
        'Weigh **% of bad cut** against **% of good+int lost**.',
        '',
        _md_table(
            ['Floor', 'Bad cut', '% of bad', 'Good lost', '% of good',
             'Interesting lost', '% of int', '% of good+int'],
            [[s['threshold'], s['bad_cut'], s['bad_cut_pct'], s['good_lost'], s['good_lost_pct'],
              s['interesting_lost'], s['interesting_lost_pct'], s['positive_lost_pct']]
             for s in audit['threshold_sweep']]),
        '',
        '### By category',
        '',
        _md_table(
            ['Category', 'n', 'good', 'interesting', 'bad', '% good+int', '% bad'],
            [[cat, c['n'], c['good'], c['interesting'], c['bad'], c['positive_pct'], c['bad_pct']]
             for cat, c in dist['by_category'].items()]),
        '',
        '### Sources (≥ 5 ratings)',
        '',
        '**Highest good+interesting rate**',
        '',
        _md_table(['Source', 'n', 'good', 'interesting', 'bad', '% good+int'],
                  [[s, c['n'], c['good'], c['interesting'], c['bad'], c['positive_pct']]
                   for s, c in dist['best_sources'].items()]),
        '',
        f'**Lowest good+interesting rate** — block candidate only at n ≥ {SOURCE_BLOCK_MIN_RATINGS} '
        'with zero positives of any kind',
        '',
        _md_table(['Source', 'n', 'good', 'interesting', 'bad', '% good+int', 'Block candidate'],
                  [[s, c['n'], c['good'], c['interesting'], c['bad'], c['positive_pct'],
                    'yes' if c['block_candidate'] else '']
                   for s, c in dist['worst_sources'].items()]),
        '',
        '## 2. Fluff Quantification',
        '',
        '### Verdicts by content type',
        '',
        _md_table(
            ['Content type', 'good', 'interesting', 'bad'],
            [[ct, c.get('good', 0), c.get('interesting', 0), c.get('bad', 0)]
             for ct, c in audit['content_type_by_rating'].items()]),
        '',
        '### Verdicts by selection bucket',
        '',
        _md_table(
            ['Bucket', 'good', 'interesting', 'bad'],
            [[b, c.get('good', 0), c.get('interesting', 0), c.get('bad', 0)]
             for b, c in audit['bucket_by_rating'].items()]),
        '',
        '### Filler trend (from corpus alignment reports)',
        '',
        _md_table(
            ['Report date', 'Articles analysed', 'Filler', 'Filler %'],
            [[t['date'], t['analysed'], t['filler'], t['filler_pct']]
             for t in audit['filler_trend']]) if audit['filler_trend'] else '_No committed alignment reports found._',
        '',
        '## 3. Theme-Bucket Routing Accuracy',
        '',
        f"Of **{routing['rated_with_day']}** ratings tied to an aired day, you corrected the day on "
        f"**{routing['corrections']}** ({routing['correction_pct']}%). "
        f"Additionally {routing['reassigned_via_approved_days']} articles were approved for other days.",
        '',
        '### Per theme day',
        '',
        '`% day fit` counts good + podcast only (the verdicts that name days). '
        '`% good+int` is feed fit: wanted in your feed, any day or none.',
        '',
        _md_table(
            ['Day', 'Theme', 'n', 'good', 'interesting', 'podcast only', 'bad',
             '% day fit', '% good+int', 'Corrected away'],
            [[d, p['label'], p['n'], p['good'], p['interesting'], p.get('podcast_only', 0), p['bad'],
              p['good_pct'], p['positive_pct'], p['corrected_away']]
             for d, p in routing['per_day'].items()]),
        '',
        '### Day → day correction matrix (shown → should-have-been)',
        '',
        _md_table(
            ['Shown \\ Better'] + WEEKDAYS,
            [[shown] + [routing['confusion'].get(shown, {}).get(target, '') for target in WEEKDAYS]
             for shown in WEEKDAYS if routing['confusion'].get(shown)]),
        '',
        '### Root cause of corrections',
        '',
        _md_table(['Cause', 'Count'], [
            ['Selection ignored its own theme scores (routing bug)', routing['root_cause']['routing_bug']],
            ['Theme scorer disagreed with you (scoring miss)', routing['root_cause']['theme_scoring_miss']],
            ['Theme scores missing on the rating', routing['root_cause']['missing_scores']],
        ]),
        '',
        '## 3b. Category Retag Accuracy',
        '',
        (f"Of **{category_retag['rated_with_category']}** ratings carrying a confirmed/retagged category, you retagged "
         f"**{category_retag['corrections']}** ({category_retag['correction_pct']}%) to a different category."
         if category_retag['rated_with_category'] else
         '_No ratings with a confirmed/retagged category yet (requires the category-retag UI in review.html)._'),
        '',
        '### Category → category correction matrix (shown → corrected)',
        '',
        (_md_table(
            ['Shown', 'Corrected to', 'Count'],
            [[shown, target, count]
             for shown, targets in category_retag['confusion'].items()
             for target, count in sorted(targets.items(), key=lambda kv: -kv[1])])
         if category_retag['confusion'] else '_No category retags recorded._'),
        '',
        '## 4. Volume Trend — Is the Feed Lighter?',
        '',
        '_Average per-run articles fetched and passing the quality gate, by ISO week '
        '(from FEED_LOG.md). The quality floor was manually dropped 20 → 13 in week 2026-W26._',
        '',
        _md_table(
            ['Week', 'Runs', 'Avg fetched/run', 'Avg quality/run'],
            [[w['week'], w['runs'], w['avg_fetched'], w['avg_quality']] for w in audit['volume_trend']]),
        '',
        '### Current funnel (calibration stats window)',
        '',
        (_md_table(
            ['Run', 'Fetched', 'New', 'Quality passed', 'Dropped below floor', 'Scrub removed'],
            [[f['run_id'], f['fetched'], f['new'], f['quality_passed'], f['quality_dropped'], f['scrub_removed']]
             for f in audit['funnel'].get('runs', [])])
         if audit['funnel'] else '_No calibration stats available._'),
        '',
        '### Current category feed sizes',
        '',
        _md_table(['Feed', 'Items'], sorted(audit['feed_counts'].items(), key=lambda kv: -kv[1])),
        '',
        '## 5. Process Health',
        '',
        _md_table(['Check', 'State'], [
            ['Calibration log entries / "No changes" entries',
             f"{audit['process_health']['calibration_log_entries']} / "
             f"{audit['process_health']['calibration_no_change_entries']}"],
            ['Calibration stats runs available', audit['process_health']['calibration_stats_runs']],
            ['Calibration stats range', audit['process_health']['calibration_stats_range']],
            ['theme_holdover_cache.json present', audit['process_health']['theme_holdover_cache_present']],
        ]),
        '',
        '**Context:** `calibration_stats_cache.json` was first committed on 2026-07-07, so every weekly '
        'calibration run before that found no stats and skipped — the log\'s repeated "Claude call or '
        'response parsing failed" lines were misleading boilerplate, not API failures. The agent\'s '
        'Claude path has effectively never run.',
        '',
    ]
    lines += _trend_lines(audit) + _scorecard_lines(audit) + _followthrough_lines(audit)
    return '\n'.join(lines) + '\n'


def _trend_lines(audit: Dict[str, Any]) -> List[str]:
    trend = audit['trend'][-TREND_REPORT_WEEKS:]
    return [
        '## 6. Week over Week',
        '',
        f'_Counts are the 7 days to each date; rates cover {TREND_WINDOW_DAYS} days. Weeks marked * '
        'were rebuilt from the ratings archive and carry no cost or scorecard data._',
        '',
        _md_table(
            ['Week', 'Through', 'Rated', 'good', 'interesting', 'podcast only', 'bad', 'Notes',
             'Shipped wanted % (reweighted)', 'Gate miss %', 'News share of ratings %'],
            [[w['week'] + ('*' if w.get('backfilled') else ''), w['through'], w['rated'],
              w['verdicts'].get('good', 0), w['verdicts'].get('interesting', 0),
              w['verdicts'].get('podcast_only', 0), w['verdicts'].get('bad', 0), w['notes'],
              w['shipped_wanted_pct_28d'], w['gate_miss_pct_28d'], w['news_share_pct_28d']]
             for w in trend]),
        '',
    ]


def _scorecard_lines(audit: Dict[str, Any]) -> List[str]:
    card = audit['scorecard']
    costs = audit['stage_costs']
    places = audit['places']
    lines = [
        '## 7. What Each Score Buys',
        '',
        f"Graded on the last {card['weeks']} weeks of ratings ({card['n']} rated, {card['n_news']} news). "
        'AUC is the chance a wanted article outscores an unwanted one: 0.5 is a coin flip. The reader '
        'model is refit each week on earlier ratings only; it uses the relevance band, so it is not '
        'wholly free of the paid pass.',
        '',
        _md_table(['Signal', 'Paid by', 'AUC', 'AUC, news only'],
                  [[c['name'], c['stage'], c['auc'] if c['auc'] is not None else 'too few',
                    c['auc_news'] if c['auc_news'] is not None else 'too few']
                   for c in card['signals'].values()]),
        '',
        f"### Claude cost by stage (last {costs['days']} days)",
        '',
    ]
    if costs['by_stage']:
        lines += [
            f"{costs['runs_with_stages']} of {costs['runs']} runs recorded stages; all vendors "
            f"together est. ${costs['est_cost_usd']:.4f}.",
            '',
            _md_table(['Stage', 'Calls', 'Est. cost'],
                      [[stage, c['calls'], f"${c['est_cost_usd']:.4f}"]
                       for stage, c in costs['by_stage'].items()]),
        ]
    else:
        lines.append(f"_No run in the window recorded stages yet ({costs['runs']} runs, "
                     f"est. ${costs['est_cost_usd']:.4f} all vendors)._")
    lines += [
        '',
        '### Local places: appetite vs. supply',
        '',
        f"Wanted % among rated articles mentioning the place (baseline {places['baseline_wanted_pct']}%), "
        f"against its share of the {places['pool_size']}-article podcast pool.",
        '',
        _md_table(['Place', 'Rated', 'Wanted %', 'In pool', 'Pool %'],
                  [[p['place'], p['rated'], p['wanted_pct'], p['in_pool'], p['pool_pct']]
                   for p in places['places']]),
        '',
    ]
    return lines


def _rate_cell(pct: Optional[float], n: Optional[int]) -> str:
    return f'{pct}% ({n})' if pct is not None else '—'


def _followthrough_lines(audit: Dict[str, Any]) -> List[str]:
    rows = audit['followthrough']
    return [
        '## 8. Did Calibration Changes Land?',
        '',
        f'_Status is checked for the latest change to each knob. Before/after is the reweighted wanted '
        f'rate of the shipped feed over {BEFORE_AFTER_DAYS} days either side (weighted ratings in '
        'brackets): everything else changed too, so read it as a correlation._',
        '',
        (_md_table(['Date', 'Knob', 'Change', 'In config now?', 'Before', 'After'],
                   [[r['run_date'], r['knob'], f"{r['old_value']} → {r['new_value']}",
                     (f"{r['status']} ({r['current']})" if r['status'] == 'changed since'
                      else r['status'] or 'superseded'),
                     _rate_cell(r.get('before_pct'), r.get('before_n')),
                     _rate_cell(r.get('after_pct'), r.get('after_n'))]
                    for r in rows])
         if rows else '_No applied calibration changes on record._'),
        '',
    ]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_current_min_score() -> Optional[int]:
    try:
        with open(BASE_DIR / 'config' / 'limits.json', 'r', encoding='utf-8') as f:
            return json.load(f).get('min_claude_score')
    except Exception:
        return None


def run_audit(today: Optional[date] = None,
              history_path: Path = METRICS_HISTORY_FILE) -> Dict[str, Any]:
    today = today or datetime.now(timezone.utc).date()
    ratings = load_ratings()
    runs = load_calibration_runs()
    dates = [r.get('rated_at', '')[:10] for r in ratings if r.get('rated_at')]
    distribution = rating_distribution(ratings)
    pool = _load_json(POOL_CACHE_FILE, [])
    places = place_supply(ratings, pool if isinstance(pool, list) else [])
    followthrough = calibration_followthrough(ratings)
    history = read_metrics_history(history_path)
    findings = blind_spots(ratings, runs, today, distribution, places, followthrough, history)
    scorecard = signal_scorecard(ratings, today)
    costs = stage_costs(runs, today)
    latest_wins = next((run['theme_argmax']['wins'] for run in reversed(runs)
                        if (run.get('theme_argmax') or {}).get('wins')), {})
    record = {
        **week_record(ratings, today),
        'scorecard': {k: c['auc'] for k, c in scorecard['signals'].items()},
        'est_cost_usd_7d': costs['est_cost_usd'],
        'claude_by_stage_7d': costs['by_stage'],
        'theme_wins': latest_wins,
        'findings': [f['id'] for f in findings],
    }
    return {
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'window': {'first': min(dates) if dates else '?', 'last': max(dates) if dates else '?'},
        'distribution': distribution,
        'score_by_rating': score_stats_by_rating(ratings),
        'band_precision': band_precision(ratings),
        'threshold_sweep': threshold_sweep(ratings),
        'current_min_score': load_current_min_score(),
        'content_type_by_rating': content_type_by_rating(ratings),
        'bucket_by_rating': bucket_by_rating(ratings),
        'stratified': stratified_estimate(ratings),
        'filler_trend': filler_trend(),
        'theme_routing': theme_routing_audit(ratings),
        'category_retag': category_retag_audit(ratings),
        'volume_trend': parse_feed_log(),
        'funnel': current_funnel(runs),
        'feed_counts': feed_item_counts(),
        'process_health': process_health(runs),
        'blind_spots': findings,
        'scorecard': scorecard,
        'stage_costs': costs,
        'places': places,
        'followthrough': followthrough,
        'trend': merge_metrics_history(history, record, ratings),
    }


def build_summary(audit: Dict[str, Any]) -> Dict[str, Any]:
    """Compact machine summary for calibration_agent.py / generate_weekly_report.py."""
    dist = audit['distribution']
    routing = audit['theme_routing']
    return {
        'generated_at': audit['generated_at'],
        'window': audit['window'],
        'total_rated': dist['total'],
        'counts': dist['counts'],
        'bad_pct': dist['bad_pct'],
        'good_pct': dist['good_pct'],
        'positive_pct': dist['positive_pct'],
        'score_by_rating': audit['score_by_rating'],
        'band_precision': audit['band_precision'],
        'threshold_sweep': audit['threshold_sweep'],
        'current_min_score': audit['current_min_score'],
        'by_category': dist['by_category'],
        'stratified': audit['stratified'],
        'worst_sources': dist['worst_sources'],
        'content_type_by_rating': audit['content_type_by_rating'],
        'theme_routing': {
            'rated_with_day': routing['rated_with_day'],
            'corrections': routing['corrections'],
            'correction_pct': routing['correction_pct'],
            'root_cause': routing['root_cause'],
            'per_day': routing['per_day'],
            'confusion': routing['confusion'],
        },
        'category_retag': audit['category_retag'],
        'volume_trend_recent': audit['volume_trend'][-8:],
        'process_health': audit['process_health'],
        'blind_spots': audit['blind_spots'],
        'scorecard': audit['scorecard'],
        'stage_costs': audit['stage_costs'],
        'places': audit['places'],
        'calibration_followthrough': audit['followthrough'],
        'trend_recent': audit['trend'][-8:],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Audit user review ratings vs. pipeline behaviour (offline).')
    default_output = f"reports/ARTICLE_REVIEW_AUDIT_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.md"
    parser.add_argument('--output', default=default_output, help='Markdown report path')
    parser.add_argument('--json-summary', default=None, help='Optional compact JSON summary path')
    parser.add_argument('--metrics-history', default=None,
                        help='Write this week into the JSONL metrics history at PATH '
                             '(reports/weekly_metrics.jsonl in CI); read-only without it')
    args = parser.parse_args()

    history_path = Path(args.metrics_history) if args.metrics_history else METRICS_HISTORY_FILE
    audit = run_audit(history_path=history_path)
    if not audit['distribution']['total']:
        print('⚠️ No feedback ratings found — nothing to audit.')
        return

    report = build_report(audit)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(args.output, report)
    print(f"✅ Audit report written to {args.output} "
          f"({audit['distribution']['total']} ratings, "
          f"{audit['theme_routing']['corrections']} theme corrections, "
          f"{audit['category_retag']['corrections']} category retags)")

    if args.json_summary:
        atomic_write_text(args.json_summary, json.dumps(build_summary(audit), indent=2, ensure_ascii=False) + '\n')
        print(f"✅ JSON summary written to {args.json_summary}")

    if args.metrics_history:
        write_metrics_history(audit['trend'], history_path)
        print(f"✅ Metrics history: {len(audit['trend'])} week(s) in {history_path}")
    flagged = [f for f in audit['blind_spots'] if f['escalate']]
    print(f"🔎 {len(audit['blind_spots'])} finding(s), {len(flagged)} repeated "
          f"{REPEAT_ESCALATE_WEEKS}+ weeks")


if __name__ == '__main__':
    main()
