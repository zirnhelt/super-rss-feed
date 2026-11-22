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


def test_cost_table_prices_every_vendor_from_api_usage():
    # Brave read "free" here for weeks after api_usage priced it at $0.005 a call.
    from generate_weekly_report import build_api_cost_html
    html = build_api_cost_html({'vendor_totals': {'claude': 10, 'brave': 100, 'kagi': 4},
                                'run_count': 2, 'total_cost': 1.53, 'avg_cost_per_run': 0.765,
                                'total_tokens': 1000})
    assert 'free' not in html
    assert '$0.5000' in html          # brave: 100 x $0.005
    assert '$1.0000' in html          # claude: total less the flat-priced vendors


def test_audit_findings_are_escaped():
    from generate_weekly_report import build_audit_findings_html
    html = build_audit_findings_html({
        'blind_spots': [{'title': HOSTILE, 'detail': f'source {HOSTILE}', 'weeks': 3, 'escalate': True}],
        'scorecard': {'weeks': 4, 'n': 10, 'signals': {'score': {'name': HOSTILE, 'stage': 'gate',
                                                                 'auc': 0.7, 'auc_news': None}}},
        'stage_costs': {'by_stage': {'gate': {'calls': 3, 'est_cost_usd': 0.25}}},
    })
    assert '<script>' not in html and '3 weeks running' in html and 'too few' in html


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


# `_actions` is read by the podcast side's roadmap fixer: owned, bounded, plain.
def test_week_actions_are_owned_plain_and_lead_the_article():
    from generate_weekly_report import ACTION_TEXT_MAX, build_verdict_html, get_week_actions
    audit = {
        'verdict': {'state': 'worse', 'cycling': True, 'headline': f'Down. {HOSTILE}'},
        'blind_spots': [
            {'id': 'gate-misses', 'title': HOSTILE, 'detail': 'x' * 900, 'weeks': 6,
             'owner': 'fixer', 'action': 'Fix the gate.', 'done_when': 'under 10%',
             'movement': 'worse', 'metric_then': 11.8, 'metric_now': 32.7},
            {'id': 'headline-misses', 'title': 'Missed headlines', 'detail': 'd', 'weeks': 1,
             'owner': 'someone-else', 'action': 'Decide.', 'done_when': 'under 50%'},
            {'id': 'old-summary-row', 'title': 'No playbook fields', 'detail': 'd', 'weeks': 2},
        ],
    }
    actions = get_week_actions(audit)
    assert [a['id'] for a in actions] == ['gate-misses', 'headline-misses']
    assert actions[0]['owner'] == 'fixer' and actions[1]['owner'] == 'reader'
    assert all('<' not in v and len(v) <= ACTION_TEXT_MAX
               for a in actions for v in a.values() if isinstance(v, str))
    html = build_verdict_html(audit)
    assert html.startswith('<h3>Verdict: worse, cycling</h3>')
    assert '<script>' not in html and '11.8 → 32.7, worse' in html
    assert 'Done when: under 10%.' in html
    assert build_verdict_html({}) == ''


def test_charts_escape_and_degrade():
    """Charts are inline SVG on the permalink page: hostile labels stay inert, empty data draws nothing."""
    from generate_weekly_report import build_charts_html, build_content_html

    empty = build_charts_html({}, [], {}, {}, [])
    assert set(empty) == {'glance', 'pipeline', 'quality', 'cost', 'discovery'}
    assert not any(empty.values())

    audit = {
        'band_precision': [{'band': HOSTILE, 'n': 10, 'good': 5, 'interesting': 2, 'bad': 2}],
        'scorecard': {'signals': {'x': {'name': HOSTILE, 'auc': 0.7, 'auc_news': None}}},
        'stage_costs': {'by_stage': {HOSTILE: {'est_cost_usd': 0.5}}},
        'by_category': {HOSTILE: {'n': 4, 'good': 2, 'bad': 2}},
        'theme_routing': {'per_day': {'monday': {'label': HOSTILE, 'n': 4, 'good': 2, 'bad': 2}}},
        'headline_coverage': {'headlines': 5, 'missed': 4, 'miss_pct': 80, 'by_outcome': {HOSTILE: 4, 'published': 1}},
        'threshold_sweep': [{'threshold': 20, 'bad_cut_pct': 10, 'positive_lost_pct': 1},
                            {'threshold': 25, 'bad_cut_pct': 20, 'positive_lost_pct': 3}],
        'current_min_score': 25,
        'places': {'baseline_wanted_pct': 40, 'places': [{'place': HOSTILE, 'rated': 30, 'wanted_pct': 70}]},
        'volume_trend_recent': [{'week': '2026-W46', 'avg_fetched': 10, 'avg_quality': 5},
                                {'week': '2026-W47', 'avg_fetched': 12, 'avg_quality': 6}],
    }
    quality_review = {
        'feedback_audit': audit,
        'scrub': {'feeds': {'a': {'title': HOSTILE, 'count': 3, 'avg_score': 50, 'stale_count': 0,
                                  'top_source': 'x', 'top_source_pct': 20}}},
        'alignment': {'total_direct': 3, 'total_rescue': 1},
    }
    charts = build_charts_html(
        {'cat_totals': {'news': 3}, 'total_runs': 1},
        [{'week_date': '2026-11-07', 'mean': 2.0, 'min': 1.0, 'max': 3.0},
         {'week_date': HOSTILE, 'mean': 2.5, 'min': 1.5, 'max': 3.5}],
        {'vendor_totals': {'claude': 3, 'brave': 2}, 'total_cost': 1.0, 'run_count': 1},
        quality_review,
        [{'week': '2026-W46', 'verdicts': {'good': 1, 'bad': 2}, 'est_cost_usd_7d': 1.0},
         {'week': '2026-W47', 'verdicts': {'good': 2, 'bad': 1}, 'est_cost_usd_7d': 1.5}],
        [(HOSTILE, 80.0), ('Other', 70.0)],
    )
    counts = {k: v.count('<figure') for k, v in charts.items()}
    assert counts == {'glance': 4, 'pipeline': 3, 'quality': 7, 'cost': 3, 'discovery': 1}
    page = build_content_html(
        'Quiet.', {'cat_totals': {'news': 3}}, [], [], [{'title': 'x', 'score': 1}], [],
        quality_review, [], [], {'vendor_totals': {'claude': 3}, 'total_cost': 1.0,
                                 'avg_cost_per_run': 1.0, 'total_tokens': 1, 'run_count': 1},
        charts=charts,
    )
    assert page.count('<figure') == 18
    assert HOSTILE not in page
