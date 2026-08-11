#!/usr/bin/env python3
"""
Pre-deploy quality validation for podcast feed JSON files.

Checks each feed-podcast-{day}.json against minimum quality thresholds.
Exits with code 1 if any assertion fails so the CI step appears as a
failure in the GitHub Actions UI (the step is configured continue-on-error
so the deploy still proceeds, but the failure is visible).

Thresholds (per feed):
  - At least 8 articles with summary length >= 100 chars
  - At least 5 articles with ai_score > 0
  - At least 3 articles with _keyword_matches > 0

Also checks episode sizes *across* themes. A charter whose scoring_prompt drifts
off-scale starves its own feed while the others stay healthy — that regression
ran undetected for 16 consecutive runs (see CALIBRATION_LOG.md, 2026-07-26)
because per-feed checks alone can't see the imbalance.
"""

import json
import sys
from pathlib import Path

DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

THRESHOLDS = {
    'min_with_summary': 8,
    'summary_min_len': 100,
    'min_with_ai_score': 5,
    'min_with_keyword_matches': 3,
}

# A feed holding less than this share of the healthiest feed's size is starved
# relative to its peers, even if it clears the absolute per-feed floors.
# Compared against the max rather than the median deliberately: the 2026-07-26
# regression starved four of seven themes at once, which drags the median down
# with it and hides the very failure this check exists to catch.
STARVATION_RATIO = 0.25


def validate_feed(path: Path) -> list[str]:
    """Return a list of failure messages for the feed, empty if it passes."""
    failures = []

    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return [f"Cannot read feed: {e}"]

    items = data.get('items', [])
    if not items:
        return ['Feed has no items']

    # summary: prefer the dedicated 'summary' field, fall back to content_html
    def _summary_len(item):
        s = item.get('summary', '') or item.get('content_html', '') or ''
        return len(s.strip())

    with_summary = sum(1 for it in items if _summary_len(it) >= THRESHOLDS['summary_min_len'])
    with_ai_score = sum(1 for it in items if (it.get('ai_score') or 0) > 0)
    # _keyword_matches: explicit 0 is fine; missing is also treated as 0 here
    with_kw = sum(1 for it in items if (it.get('_keyword_matches') or 0) > 0)

    if with_summary < THRESHOLDS['min_with_summary']:
        failures.append(
            f"summary ≥ {THRESHOLDS['summary_min_len']} chars: "
            f"{with_summary}/{len(items)} (need {THRESHOLDS['min_with_summary']})"
        )

    if with_ai_score < THRESHOLDS['min_with_ai_score']:
        failures.append(
            f"ai_score > 0: {with_ai_score}/{len(items)} (need {THRESHOLDS['min_with_ai_score']})"
        )

    if with_kw < THRESHOLDS['min_with_keyword_matches']:
        failures.append(
            f"_keyword_matches > 0: {with_kw}/{len(items)} "
            f"(need {THRESHOLDS['min_with_keyword_matches']})"
        )

    return failures


def check_theme_balance(sizes: dict[str, int]) -> list[str]:
    """Return failures for feeds starved relative to their peers.

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


def main():
    any_failed = False
    sizes: dict[str, int] = {}

    for day in DAYS:
        path = Path(f'feed-podcast-{day}.json')
        if not path.exists():
            print(f'⏭️  {path.name}: not found, skipping')
            continue

        try:
            with open(path, encoding='utf-8') as f:
                sizes[day] = len(json.load(f).get('items', []))
        except (OSError, json.JSONDecodeError):
            pass  # validate_feed reports the read failure below

        failures = validate_feed(path)
        if failures:
            any_failed = True
            print(f'❌ {path.name}: FAILED quality checks')
            for msg in failures:
                print(f'   • {msg}')
        else:
            print(f'✅ {path.name}: OK')

    balance_failures = check_theme_balance(sizes)
    if balance_failures:
        any_failed = True
        print('\n❌ Theme balance: feeds starved relative to their peers')
        for msg in balance_failures:
            print(f'   • {msg}')

    if any_failed:
        print('\n⚠️  One or more podcast feeds failed quality validation.')
        print('   Upstream scoring/summary extraction needs investigation.')
        sys.exit(1)
    else:
        print('\n✅ All podcast feeds passed quality validation.')


if __name__ == '__main__':
    main()
