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
feed actually running lighter?

Entirely offline — stdlib only, no API calls. Follows the same dual-output
convention as `corpus_alignment_report.py`:

    python article_review_audit.py [--output PATH] [--json-summary PATH]

Defaults: `ARTICLE_REVIEW_AUDIT_<YYYY-MM-DD>.md` and (when requested)
`article_review_audit_summary.json`, which `calibration_agent.py` and
`generate_weekly_report.py` consume.
"""

import argparse
import glob
import json
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).parent
FEEDBACK_DIR = BASE_DIR / 'feedback'
FEED_LOG_FILE = BASE_DIR / 'FEED_LOG.md'
CALIBRATION_STATS_FILE = BASE_DIR / 'calibration_stats_cache.json'
CALIBRATION_LOG_FILE = BASE_DIR / 'CALIBRATION_LOG.md'
THEME_HOLDOVER_FILE = BASE_DIR / 'theme_holdover_cache.json'

WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
SCORE_BANDS = [(80, 100), (60, 79), (40, 59), (20, 39), (0, 19)]
SWEEP_THRESHOLDS = [13, 15, 20, 25, 30, 35, 40, 45, 50, 60]
MIN_SOURCE_RATINGS = 5


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_ratings(feedback_dir: Path = FEEDBACK_DIR) -> List[Dict]:
    """All ratings across feedback files, deduplicated by URL (latest wins)."""
    by_url: Dict[str, Dict] = {}
    for path in sorted(glob.glob(str(feedback_dir / '????-??-??.json'))):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue
        for rating in data.get('ratings', []):
            url = rating.get('url')
            if not url or rating.get('rating') not in ('good', 'interesting', 'bad', 'skip'):
                continue
            prev = by_url.get(url)
            if prev is None or (rating.get('rated_at') or '') >= (prev.get('rated_at') or ''):
                by_url[url] = rating
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

def rating_distribution(ratings: List[Dict]) -> Dict[str, Any]:
    counts = Counter(r['rating'] for r in ratings)
    total = len(ratings)
    by_category: Dict[str, Counter] = defaultdict(Counter)
    by_source: Dict[str, Counter] = defaultdict(Counter)
    for r in ratings:
        by_category[r.get('category') or 'unknown'][r['rating']] += 1
        by_source[r.get('source') or 'unknown'][r['rating']] += 1

    def _rate(c: Counter, key: str) -> float:
        n = sum(c.values())
        return round(100 * c[key] / n, 1) if n else 0.0

    categories = {
        cat: {'n': sum(c.values()), 'good': c['good'], 'interesting': c['interesting'],
              'bad': c['bad'], 'bad_pct': _rate(c, 'bad'), 'good_pct': _rate(c, 'good')}
        for cat, c in sorted(by_category.items(), key=lambda kv: -sum(kv[1].values()))
    }
    sources = {
        src: {'n': sum(c.values()), 'good': c['good'], 'bad': c['bad'],
              'good_pct': _rate(c, 'good'), 'bad_pct': _rate(c, 'bad')}
        for src, c in by_source.items() if sum(c.values()) >= MIN_SOURCE_RATINGS
    }
    best_sources = sorted(sources.items(), key=lambda kv: (-kv[1]['good_pct'], -kv[1]['n']))[:10]
    worst_sources = sorted(sources.items(), key=lambda kv: (-kv[1]['bad_pct'], -kv[1]['n']))[:10]

    return {
        'total': total,
        'counts': dict(counts),
        'bad_pct': round(100 * counts['bad'] / total, 1) if total else 0.0,
        'good_pct': round(100 * counts['good'] / total, 1) if total else 0.0,
        'by_category': categories,
        'best_sources': dict(best_sources),
        'worst_sources': dict(worst_sources),
    }


def score_stats_by_rating(ratings: List[Dict]) -> Dict[str, Dict[str, float]]:
    stats: Dict[str, Dict[str, float]] = {}
    for verdict in ('good', 'interesting', 'bad'):
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
            'bad': counts['bad'],
            'good_pct': round(100 * counts['good'] / n, 1) if n else None,
            'bad_pct': round(100 * counts['bad'] / n, 1) if n else None,
        })
    return bands


def threshold_sweep(ratings: List[Dict]) -> List[Dict[str, Any]]:
    """For each candidate min-score floor: how much bad is cut vs. good lost."""
    scored = [r for r in ratings if isinstance(r.get('score'), (int, float))]
    total_bad = sum(1 for r in scored if r['rating'] == 'bad')
    total_good = sum(1 for r in scored if r['rating'] == 'good')
    sweep = []
    for t in SWEEP_THRESHOLDS:
        cut_bad = sum(1 for r in scored if r['rating'] == 'bad' and r['score'] < t)
        lost_good = sum(1 for r in scored if r['rating'] == 'good' and r['score'] < t)
        sweep.append({
            'threshold': t,
            'bad_cut': cut_bad,
            'bad_cut_pct': round(100 * cut_bad / total_bad, 1) if total_bad else 0.0,
            'good_lost': lost_good,
            'good_lost_pct': round(100 * lost_good / total_good, 1) if total_good else 0.0,
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

    # Approved-day reassignments (good articles routed to extra/other days)
    reassigned_via_days = [
        r for r in with_day
        if r['rating'] == 'good' and r.get('approved_days')
        and any(d != r['today'] for d in r['approved_days'] if d in WEEKDAYS)
    ]

    # Root-cause split: did the pipeline's own theme scores already prefer the
    # user's corrected day? If yes, selection ignored its own signal (routing);
    # if no, the theme scorer itself missed (scoring).
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
        per_day[day] = {
            'label': labels.most_common(1)[0][0] if labels else '',
            'n': n,
            'good': counts['good'],
            'bad': counts['bad'],
            'good_pct': round(100 * counts['good'] / n, 1),
            'corrected_away': sum(1 for r in corrections if r['today'] == day),
        }

    n_day = len(with_day)
    return {
        'rated_with_day': n_day,
        'corrections': len(corrections),
        'correction_pct': round(100 * len(corrections) / n_day, 1) if n_day else 0.0,
        'reassigned_via_approved_days': len(reassigned_via_days),
        'confusion': {d: dict(t) for d, t in confusion.items() if t},
        'root_cause': {
            'routing_bug': routing_bugs,
            'theme_scoring_miss': scoring_misses,
            'missing_scores': unsplittable,
        },
        'per_day': per_day,
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
    for path in sorted(BASE_DIR.glob('CORPUS_ALIGNMENT_REPORT_*.md')):
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
# Report rendering
# ---------------------------------------------------------------------------

def _md_table(headers: List[str], rows: List[List[Any]]) -> str:
    out = ['| ' + ' | '.join(headers) + ' |',
           '|' + '|'.join(['---'] * len(headers)) + '|']
    out += ['| ' + ' | '.join('' if v is None else str(v) for v in row) + ' |' for row in rows]
    return '\n'.join(out)


def build_report(audit: Dict[str, Any]) -> str:
    dist = audit['distribution']
    routing = audit['theme_routing']
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
            ['Rated **bad** (fluff/noise that reached you)', f"{dist['counts'].get('bad', 0)} ({dist['bad_pct']}%)"],
            ['Rated **good**', f"{dist['counts'].get('good', 0)} ({dist['good_pct']}%)"],
            ['Rated **interesting**', dist['counts'].get('interesting', 0)],
            ['Theme-day corrections (`better_theme`)', f"{routing['corrections']} ({routing['correction_pct']}% of day-routed ratings)"],
            ['…caused by selection ignoring its own theme scores', routing['root_cause']['routing_bug']],
            ['…caused by the theme scorer itself missing', routing['root_cause']['theme_scoring_miss']],
        ]),
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
            ['Score band', 'n', 'good', 'bad', '% good', '% bad'],
            [[b['band'], b['n'], b['good'], b['bad'], b['good_pct'], b['bad_pct']]
             for b in audit['band_precision']]),
        '',
        '### Threshold sweep — what a higher quality floor would have done',
        '',
        f"Current `min_claude_score` floor: **{audit['current_min_score']}** "
        "(manually lowered 20 → 13 on 2026-06-24).",
        '',
        _md_table(
            ['Floor', 'Bad cut', '% of bad', 'Good lost', '% of good'],
            [[s['threshold'], s['bad_cut'], s['bad_cut_pct'], s['good_lost'], s['good_lost_pct']]
             for s in audit['threshold_sweep']]),
        '',
        '### By category',
        '',
        _md_table(
            ['Category', 'n', 'good', 'interesting', 'bad', '% bad'],
            [[cat, c['n'], c['good'], c['interesting'], c['bad'], c['bad_pct']]
             for cat, c in dist['by_category'].items()]),
        '',
        '### Sources (≥ 5 ratings)',
        '',
        '**Highest good-rate**',
        '',
        _md_table(['Source', 'n', 'good', 'bad', '% good'],
                  [[s, c['n'], c['good'], c['bad'], c['good_pct']]
                   for s, c in dist['best_sources'].items()]),
        '',
        '**Highest bad-rate**',
        '',
        _md_table(['Source', 'n', 'good', 'bad', '% bad'],
                  [[s, c['n'], c['good'], c['bad'], c['bad_pct']]
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
        f"Additionally {routing['reassigned_via_approved_days']} good articles were approved for other days.",
        '',
        '### Per theme day',
        '',
        _md_table(
            ['Day', 'Theme', 'n', 'good', 'bad', '% good', 'Corrected away'],
            [[d, p['label'], p['n'], p['good'], p['bad'], p['good_pct'], p['corrected_away']]
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
    return '\n'.join(lines) + '\n'


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def load_current_min_score() -> Optional[int]:
    try:
        with open(BASE_DIR / 'config' / 'limits.json', 'r', encoding='utf-8') as f:
            return json.load(f).get('min_claude_score')
    except Exception:
        return None


def run_audit() -> Dict[str, Any]:
    ratings = load_ratings()
    runs = load_calibration_runs()
    dates = [r.get('rated_at', '')[:10] for r in ratings if r.get('rated_at')]
    return {
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'window': {'first': min(dates) if dates else '?', 'last': max(dates) if dates else '?'},
        'distribution': rating_distribution(ratings),
        'score_by_rating': score_stats_by_rating(ratings),
        'band_precision': band_precision(ratings),
        'threshold_sweep': threshold_sweep(ratings),
        'current_min_score': load_current_min_score(),
        'content_type_by_rating': content_type_by_rating(ratings),
        'bucket_by_rating': bucket_by_rating(ratings),
        'filler_trend': filler_trend(),
        'theme_routing': theme_routing_audit(ratings),
        'volume_trend': parse_feed_log(),
        'funnel': current_funnel(runs),
        'feed_counts': feed_item_counts(),
        'process_health': process_health(runs),
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
        'score_by_rating': audit['score_by_rating'],
        'band_precision': audit['band_precision'],
        'threshold_sweep': audit['threshold_sweep'],
        'current_min_score': audit['current_min_score'],
        'by_category': dist['by_category'],
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
        'volume_trend_recent': audit['volume_trend'][-8:],
        'process_health': audit['process_health'],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Audit user review ratings vs. pipeline behaviour (offline).')
    default_output = f"ARTICLE_REVIEW_AUDIT_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.md"
    parser.add_argument('--output', default=default_output, help='Markdown report path')
    parser.add_argument('--json-summary', default=None, help='Optional compact JSON summary path')
    args = parser.parse_args()

    audit = run_audit()
    if not audit['distribution']['total']:
        print('⚠️ No feedback ratings found — nothing to audit.')
        return

    report = build_report(audit)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ Audit report written to {args.output} "
          f"({audit['distribution']['total']} ratings, "
          f"{audit['theme_routing']['corrections']} theme corrections)")

    if args.json_summary:
        with open(args.json_summary, 'w', encoding='utf-8') as f:
            json.dump(build_summary(audit), f, indent=2, ensure_ascii=False)
            f.write('\n')
        print(f"✅ JSON summary written to {args.json_summary}")


if __name__ == '__main__':
    main()
