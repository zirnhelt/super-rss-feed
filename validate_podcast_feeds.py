#!/usr/bin/env python3
"""
Post-deploy quality report for the podcast feed JSON files.

Reports on each feed-podcast-{day}.json. **Findings never fail the process** —
this runs in its own workflow job after the deploy and its job is to be read,
not to gate. A non-zero exit from this script means the script itself broke;
a starved or off-charter feed is a row in the report.

That split is deliberate. The old arrangement ran inside the build job under
`continue-on-error: true` and re-raised the outcome after the deploy, so its
only possible effect was turning a run red — and from 2026-08-30 it did that on
every single run, always on the same two feeds. A check that is permanently red
is not an alarm, it is a reason to stop reading the alarms, and it hid the
build job's real signals (the curator, and the gh-pages byte-match verifier)
behind noise.

Checks (per feed):
  - At least 8 articles with summary length >= 100 chars
  - At least 5 articles with ai_score > 0
  - At least 3 articles with _keyword_matches > 0
  - Top-10 mean _theme_score_raw at or above the theme's own floor

Also checks episode sizes *across* themes. A charter whose scoring_prompt drifts
off-scale starves its own feed while the others stay healthy — that regression
ran undetected for 16 consecutive runs (see CALIBRATION_LOG.md, 2026-07-26)
because per-feed checks alone can't see the imbalance.
"""

import json
import os
import sys
from pathlib import Path

DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

THRESHOLDS = {
    'min_with_summary': 8,
    'summary_min_len': 100,
    'min_with_ai_score': 5,
    'min_with_keyword_matches': 3,
}

# Absolute floor on the charter's own output, which percentile normalization
# cannot reach. Selection ranks articles *within* a theme
# (`normalize_theme_scores()`), so the top of a collapsed distribution is
# promoted to `_theme_score` 90-100 regardless of how poorly it actually fits:
# on 2026-08-30 the Thursday episode carried a Windows 11 performance-boost
# article at percentile 90 whose raw charter score was 16. `_theme_score_raw`
# is the un-rescaled 0-100 charter judgement, so a theme whose best candidates
# sit near the bottom of its own ladder is airing filler.
#
# **The floor is per theme, because the scale is.** Each day's `scoring_prompt`
# is independently worded and the seven cover subjects of very different
# breadth, so their raw output is not on one ladder. Measured top-10 means over
# the eight runs published 2026-08-30..09-01 are rank-stable and an order of
# magnitude apart at the ends:
#
#   sunday 74.4-85.2   saturday 62.1-70.3   friday 60.5-69.2   monday 36.1-43.1
#   thursday 26.4-35.7  tuesday 15.5-22.0   wednesday 9.8-18.1
#
# A single global floor (this was `MIN_TOP_RAW_MEAN = 25`) drawn across that
# separates broad themes from narrow ones, not healthy ones from broken ones.
# It cut between Thursday and Tuesday and so failed Tuesday and Wednesday on
# every run from the day it was added, while a genuine 50% collapse in Sunday
# would have sailed through at 40.
#
# **That reading of the low end was wrong, and the numbers above are a record of
# a bug rather than of theme breadth.** The note here used to conclude that
# Wednesday's 'Repair Culture & Practical Tech' was "honestly reporting weak
# fit" against a general corpus. It was not: `score_all_themes_at_ingest` rated
# each article against all 7 charters in one Haiku response, and a model asked
# for 7 numbers at once apportions one general-interest magnitude instead of
# applying each charter. On the 2026-09-01 cache, Science was the best-fit theme
# for 82.4% of 2,004 articles and Working Lands, Repair Culture, Arts and
# Indigenous Lands were best-fit for *none*; Repair Culture's maximum over 2,121
# articles was 35, on a charter whose own anchors put a teardown at 98 and a
# Raspberry Pi weather-station build at 68. Hackaday was supplying ~44 hands-on
# hardware articles a week the whole time — "Reviving an SD Card With Shorted
# Capacitors" scored 11. The rank order these floors were fitted to is that
# fixed per-theme prior, not a property of the subjects.
#
# `rescore_underserved_themes()` now re-asks the question one charter at a time
# for the affected days. **So tuesday and wednesday's floors below are stale by
# construction** — they describe the collapsed scorer. They are left as-is
# rather than guessed upward: they still catch a true collapse, and raising
# them on prediction would trade a floor fitted to real numbers for one fitted
# to hope. Refit all seven off a measured month *after* the rescore has been
# running, using the per-theme values this report prints on every run.
#
# **These floors are provisional and instrumented for refit.** They are 0.6x
# each theme's observed minimum over eight runs — a ~40% drop below the bottom
# of a four-day band — which is a collapse, not a slow week. Four days is a
# thin sample and the whole corpus drifts down together as the pool ages
# (Sunday fell 85.2 -> 77.4 over three days), so the report prints every
# theme's measured value on every run, pass or fail. Refit these off a measured
# month of those numbers rather than off appetite.
RAW_FIT_FLOORS = {
    'monday': 22,
    'tuesday': 9,
    'wednesday': 6,
    'thursday': 16,
    'friday': 36,
    'saturday': 37,
    'sunday': 45,
}

TOP_RAW_SAMPLE = 10

# A feed holding less than this share of the healthiest feed's size is starved
# relative to its peers, even if it clears the absolute per-feed floors.
# Compared against the max rather than the median deliberately: the 2026-07-26
# regression starved four of seven themes at once, which drags the median down
# with it and hides the very failure this check exists to catch.
#
# Item counts, unlike raw charter scores, *are* on one ladder across themes —
# every feed is drawn from the same pool against the same budget — so this one
# stays a single global constant.
STARVATION_RATIO = 0.25


def _summary_len(item: dict) -> int:
    """Length of an item's summary, falling back to its rendered content."""
    s = item.get('summary', '') or item.get('content_html', '') or ''
    return len(s.strip())


def validate_feed(path: Path, day: str) -> tuple[list[str], dict]:
    """Return (findings, metrics) for one feed.

    `findings` is empty when the feed is healthy. `metrics` is reported whether
    or not anything was found — the numbers are what make the floors refittable.
    """
    # Shaped up front so every return path — including the unreadable and
    # empty ones — carries the same keys for the report table to render.
    metrics = {
        'readable': False,
        'items': 0,
        'with_summary': 0,
        'with_ai_score': 0,
        'with_keyword_matches': 0,
        'top_raw_mean': None,
        'raw_floor': RAW_FIT_FLOORS.get(day),
    }

    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        return [f"Cannot read feed: {e}"], metrics

    metrics['readable'] = True
    items = data.get('items', [])
    if not items:
        return ['Feed has no items'], metrics

    findings = []

    with_summary = sum(1 for it in items if _summary_len(it) >= THRESHOLDS['summary_min_len'])
    with_ai_score = sum(1 for it in items if (it.get('ai_score') or 0) > 0)
    # _keyword_matches: explicit 0 is fine; missing is also treated as 0 here
    with_kw = sum(1 for it in items if (it.get('_keyword_matches') or 0) > 0)

    metrics.update({
        'items': len(items),
        'with_summary': with_summary,
        'with_ai_score': with_ai_score,
        'with_keyword_matches': with_kw,
    })

    if with_summary < THRESHOLDS['min_with_summary']:
        findings.append(
            f"summary ≥ {THRESHOLDS['summary_min_len']} chars: "
            f"{with_summary}/{len(items)} (need {THRESHOLDS['min_with_summary']})"
        )

    if with_ai_score < THRESHOLDS['min_with_ai_score']:
        findings.append(
            f"ai_score > 0: {with_ai_score}/{len(items)} (need {THRESHOLDS['min_with_ai_score']})"
        )

    if with_kw < THRESHOLDS['min_with_keyword_matches']:
        findings.append(
            f"_keyword_matches > 0: {with_kw}/{len(items)} "
            f"(need {THRESHOLDS['min_with_keyword_matches']})"
        )

    # Raw charter fit, against this theme's own floor. Skipped when no item
    # carries the field, so a feed built before the field existed reports its
    # other checks instead of failing here.
    raw_scores = [it['_theme_score_raw'] for it in items
                  if isinstance(it.get('_theme_score_raw'), (int, float))]
    floor = RAW_FIT_FLOORS.get(day)
    if raw_scores:
        top = sorted(raw_scores, reverse=True)[:TOP_RAW_SAMPLE]
        top_mean = sum(top) / len(top)
        metrics['top_raw_mean'] = top_mean
        if floor is not None and top_mean < floor:
            findings.append(
                f"raw theme fit: top-{len(top)} mean _theme_score_raw "
                f"{top_mean:.1f}, below this theme's floor of {floor} — the "
                f"charter is scoring its own best candidates far under its "
                f"normal range, so percentile normalization is masking an "
                f"off-scale scoring_prompt or an empty corpus for this theme"
            )

    return findings, metrics


def check_theme_balance(sizes: dict[str, int]) -> list[str]:
    """Return findings for feeds starved relative to their peers.

    Percentile-normalized theme selection should keep episode sizes broadly
    comparable. A single feed collapsing while the rest stay healthy is the
    signature of a scoring_prompt that has drifted off-scale.
    """
    if len(sizes) < 3:
        return []

    healthiest = max(sizes.values())
    if healthiest <= 0:
        return []

    floor = healthiest * STARVATION_RATIO
    return [
        f"{day}: {n} articles vs {healthiest} for the healthiest theme "
        f"(< {STARVATION_RATIO:.0%}) — check scoring_prompt for scale drift"
        for day, n in sorted(sizes.items())
        if n < floor
    ]


def write_summary(rows: list[tuple[str, dict, list[str]]], balance: list[str]) -> None:
    """Append the report table to $GITHUB_STEP_SUMMARY, if the runner set one.

    The table is the point of this script now that nothing gates on it: the
    per-theme raw-fit numbers are what RAW_FIT_FLOORS gets refitted against,
    and they are only useful if they are recorded on a passing run too.
    """
    dest = os.environ.get('GITHUB_STEP_SUMMARY')
    if not dest:
        return

    lines = [
        '## Podcast feed quality',
        '',
        '| Feed | Items | Summaries | ai_score | Keywords | Top-10 raw fit | Floor |',
        '|---|---:|---:|---:|---:|---:|---:|',
    ]
    for day, m, findings in rows:
        mark = '' if not findings else ' ⚠️'
        if not m['readable']:
            lines.append(f'| {day}{mark} | unreadable | — | — | — | — | — |')
            continue
        raw = f"{m['top_raw_mean']:.1f}" if m['top_raw_mean'] is not None else '—'
        lines.append(
            f"| {day}{mark} | {m['items']} | {m['with_summary']} | "
            f"{m['with_ai_score']} | {m['with_keyword_matches']} | "
            f"{raw} | {m['raw_floor'] if m['raw_floor'] is not None else '—'} |"
        )

    flagged = [(day, f) for day, _, fs in rows for f in fs]
    if flagged or balance:
        lines += ['', '### Findings', '']
        lines += [f'- **{day}** — {f}' for day, f in flagged]
        lines += [f'- **theme balance** — {f}' for f in balance]
    else:
        lines += ['', 'All podcast feeds passed.']

    try:
        with open(dest, 'a', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
    except OSError as e:
        print(f'::warning::could not write job summary: {e}')


def main() -> None:
    rows: list[tuple[str, dict, list[str]]] = []
    sizes: dict[str, int] = {}

    for day in DAYS:
        path = Path(f'feed-podcast-{day}.json')
        if not path.exists():
            print(f'⏭️  {path.name}: not found, skipping')
            continue

        findings, metrics = validate_feed(path, day)
        if metrics['items']:
            sizes[day] = metrics['items']
        rows.append((day, metrics, findings))

        raw = metrics['top_raw_mean']
        raw_note = (
            f" | top-{TOP_RAW_SAMPLE} raw fit {raw:.1f} (floor {metrics['raw_floor']})"
            if raw is not None else ''
        )
        mark = '⚠️ ' if findings else '✅'
        print(f'{mark} {path.name}: {metrics["items"]} items{raw_note}')
        for msg in findings:
            print(f'   • {msg}')

    balance = check_theme_balance(sizes)
    if balance:
        print('\n⚠️  Theme balance: feeds starved relative to their peers')
        for msg in balance:
            print(f'   • {msg}')

    write_summary(rows, balance)

    if not rows:
        # Not a pass. `build`'s gh-pages verifier is what fails on a bad
        # deploy; saying "all feeds passed" when none were read would be a lie
        # that reads exactly like a healthy run.
        print('\n::warning::No podcast feeds were found to report on.')
        sys.exit(0)

    flagged = sorted({day for day, _, fs in rows if fs})
    if flagged or balance:
        # A GitHub annotation, not a failure: this runs after the deploy and
        # the feeds are already published. Recalibrating a charter is a human's
        # weekly job, not something to re-run the pipeline over.
        print(f'\n::warning::Podcast feed quality findings: '
              f'{", ".join(flagged) or "theme balance"} — see the job summary.')
    else:
        print('\n✅ All podcast feeds passed quality validation.')

    # Always 0. A non-zero exit from here means this script crashed.
    sys.exit(0)


if __name__ == '__main__':
    main()
