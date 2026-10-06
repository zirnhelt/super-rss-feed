"""The weekly report must not publish third-party text as markup.

`weekly-report-*.html` is served from the same origin as review.html
(zirnhelt.github.io). Its feed titles, feed-error messages and discovery
candidates come from arbitrary feeds found by search, and its narrative and
calibration rationale come from a model that read them. Until 2026-09-23 all
of it was interpolated raw, so a feed titled `<script>…</script>` would have
run on that origin.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generate_weekly_report import build_content_html

HOSTILE = '<script>alert(1)</script>'


def _render(**overrides):
    args = dict(
        narrative=f'Quiet week. {HOSTILE}',
        stats={'cat_totals': {'news': 3}},
        new_feeds=[{'title': HOSTILE}],
        errors=[{'feed': HOSTILE, 'error': f'404 for {HOSTILE}'}],
        discovery=[{'title': HOSTILE, 'score': 70}],
        calibration_changes=[{'knob': 'limits.x', 'old_value': 1, 'new_value': 2, 'rationale': HOSTILE}],
        quality_review={'scrub': {'total_articles': 1, 'feeds': {'news': {
            'title': HOSTILE, 'count': 1, 'avg_score': 50, 'stale_count': 0,
            'top_source': HOSTILE, 'top_source_pct': 100}}}},
        actions=[{'component': 'feeds.opml', 'action': f'Added feed “{HOSTILE}”', 'commit': 'abc1234'}],
        nts_benchmarks=[],
        api_cost={},
    )
    args.update(overrides)
    return build_content_html(**args)


def test_no_third_party_text_survives_as_markup():
    html = _render()
    assert '<script>' not in html
    assert '&lt;script&gt;' in html


def test_report_structure_is_still_markup():
    html = _render()
    assert '<ul>' in html and '<table>' in html
    assert '<a href="https://github.com/' in html


def test_plain_text_is_unchanged():
    html = _render(narrative='Feeds held steady.', new_feeds=[{'title': 'Williams Lake Tribune'}])
    assert '<p>Feeds held steady.</p>' in html
    assert '<li>Williams Lake Tribune</li>' in html


# The `_changes` lines go to the podcast, which hands them to a Meta Moment
# prompt as citable facts, so they are plain text and bounded like any other
# publisher-chosen string.
from generate_weekly_report import CHANGE_LINE_MAX, get_week_changes


def test_week_changes_are_plain_bounded_lines():
    lines = get_week_changes(
        discovery_actions=[{'title': f'One Earth {HOSTILE}', 'category': 'climate', 'score': 79.1}],
        health_actions=[{'action': 'retired', 'title': 'X' * 400},
                         {'action': 'substituted', 'title': 'CleanTechnica'}],
        calibration_changes=[{'knob': 'feed_slots.max_slots.news', 'old_value': 25, 'new_value': 22}],
    )
    assert lines[0] == 'Added a new source: One Earth (climate)'
    assert lines[1].startswith('Retired the source XXX') and len(lines[1]) == CHANGE_LINE_MAX
    assert lines[2].endswith('Google News search for the source CleanTechnica')
    assert lines[3] == 'Tuned feed_slots.max_slots.news from 25 to 22'
    assert all('\n' not in line and '<' not in line for line in lines)


def test_quiet_week_has_no_changes():
    assert get_week_changes([], [], []) == []
