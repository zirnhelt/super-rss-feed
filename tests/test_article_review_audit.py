"""The audit counts 'interesting' as wanted everywhere except day fit."""
import itertools
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import article_review_audit as audit

_ids = itertools.count()


def _r(rating: str, score: Optional[int] = None, source: str = 'S',
       category: str = 'news', today: Optional[str] = None) -> Dict:
    return {'url': f'u{next(_ids)}', 'rating': rating, 'score': score,
            'source': source, 'category': category, 'today': today}


def test_band_precision_reports_interesting_as_positive():
    ratings: List[Dict] = [_r('good', 45), _r('interesting', 45), _r('bad', 45), _r('bad', 45)]
    band = next(b for b in audit.band_precision(ratings) if b['band'] == '40-59')
    assert band['good_pct'] == 25.0
    assert band['interesting'] == 1
    assert band['positive_pct'] == 50.0


def test_threshold_sweep_counts_interesting_lost():
    ratings = [_r('good', 50), _r('interesting', 22), _r('interesting', 50), _r('bad', 10)]
    row = next(s for s in audit.threshold_sweep(ratings) if s['threshold'] == 25)
    assert row['good_lost'] == 0
    assert row['interesting_lost'] == 1
    assert row['interesting_lost_pct'] == 50.0
    assert row['positive_lost_pct'] == round(100 / 3, 1)
    assert row['bad_cut_pct'] == 100.0


def test_source_with_only_interesting_is_not_a_block_candidate():
    ratings = ([_r('bad', source='Edge') for _ in range(8)] + [_r('interesting', source='Edge')]
               + [_r('bad', source='RS') for _ in range(8)])
    dist = audit.rating_distribution(ratings)
    assert dist['worst_sources']['RS']['block_candidate'] is True
    assert dist['worst_sources']['Edge']['block_candidate'] is False
    assert list(dist['worst_sources'])[0] == 'RS'


def test_block_candidate_needs_eight_ratings():
    ratings = [_r('bad', source='Thin') for _ in range(7)]
    assert audit.rating_distribution(ratings)['worst_sources']['Thin']['block_candidate'] is False


def test_per_day_good_pct_is_day_fit_and_positive_pct_adds_interesting():
    ratings = [_r('good', today='monday'), _r('interesting', today='monday'),
               _r('bad', today='monday'), _r('bad', today='monday')]
    day = audit.theme_routing_audit(ratings)['per_day']['monday']
    assert day['good_pct'] == 25.0
    assert day['positive_pct'] == 50.0


# ── podcast_only: wanted on the show, not in the feed ──────────────────────────

def test_podcast_only_is_day_fit_but_not_feed_fit():
    ratings = [_r('podcast_only', today='saturday'), _r('interesting', today='saturday'),
               _r('bad', today='saturday'), _r('bad', today='saturday')]
    day = audit.theme_routing_audit(ratings)['per_day']['saturday']
    assert day['good_pct'] == 25.0        # day fit: good + podcast_only
    assert day['positive_pct'] == 25.0    # feed fit: good + interesting
    assert day['podcast_only'] == 1


def test_show_only_material_protects_a_source_from_blocking():
    # Blocking a source drops it from the podcast pool as well as the feed.
    ratings = [_r('bad', source='Tribune') for _ in range(8)] + [_r('podcast_only', source='Tribune')]
    cell = audit.rating_distribution(ratings)['worst_sources']['Tribune']
    assert cell['positive'] == 0
    assert cell['block_candidate'] is False


def test_podcast_only_is_loaded_and_counts_against_the_feed_rate(tmp_path):
    import json
    (tmp_path / '2026-09-30.json').write_text(json.dumps({'ratings': [
        {'url': 'a', 'rating': 'podcast_only', 'score': 45},
        {'url': 'b', 'rating': 'good', 'score': 45},
    ]}))
    ratings = audit.load_ratings(tmp_path)
    assert {r['rating'] for r in ratings} == {'podcast_only', 'good'}
    band = next(b for b in audit.band_precision(ratings) if b['band'] == '40-59')
    assert band['positive_pct'] == 50.0


# ── The reader model orders the review batch ──────────────────────────────────

def _row(rating: str, source: str, bucket: str = 'mid') -> Dict:
    return {'rating': rating, 'source': source, 'selection_bucket': bucket,
            'original_category': 'news', 'content_type': None, 'relevance': 40}


def test_reader_model_ranks_a_liked_source_above_a_disliked_one():
    history = ([_row('good', 'Liked') for _ in range(6)] + [_row('bad', 'Liked')]
               + [_row('bad', 'Disliked') for _ in range(6)] + [_row('interesting', 'Disliked')])
    predict = audit.fit_reader_model(history)
    liked, disliked, unseen = (predict(_row('bad', s)) for s in ('Liked', 'Disliked', 'New'))
    assert liked > unseen > disliked
    assert 0 < disliked < liked < 1


def test_reader_model_counts_podcast_only_as_wanted_and_ignores_skip():
    history = ([_row('podcast_only', 'Show') for _ in range(5)]
               + [_row('bad', 'Other') for _ in range(5)] + [_row('skip', 'Other') for _ in range(20)])
    predict = audit.fit_reader_model(history)
    assert predict(_row('bad', 'Show')) > 0.5 > predict(_row('bad', 'Other'))


def test_reader_model_needs_both_outcomes():
    assert audit.fit_reader_model([_row('good', 'A'), _row('interesting', 'B')]) is None
    assert audit.fit_reader_model([]) is None


# ── What one week cannot show (2026-10): repeats, scorecard, follow-through ───

from datetime import date, timedelta  # noqa: E402

TODAY = date(2026, 10, 10)


def _on(rating: str, days_ago: int, **fields) -> Dict:
    row = {'url': f'u{next(_ids)}', 'rating': rating,
           'rated_at': f'{(TODAY - timedelta(days=days_ago)).isoformat()}T12:00:00Z'}
    row.update(fields)
    return row


def test_auc_is_a_coin_flip_at_half_and_none_when_thin():
    assert audit.auc([(s, True) for s in range(50, 60)] + [(s, False) for s in range(10)]) == 1.0
    assert audit.auc([(5, True)] * 10 + [(5, False)] * 10) == 0.5
    assert audit.auc([(9, True)] * 3 + [(1, False)] * 30) is None
    assert audit.auc([(None, True)] * 20 + [(1, False)] * 20) is None


def test_blocked_sources_leave_the_worst_list():
    # Rolling Stone headed this list for two audits after it was blocked.
    ratings = [_r('bad', source='Rolling Stone') for _ in range(9)] + [_r('bad', source='Other') for _ in range(9)]
    worst = audit.rating_distribution(ratings, blocked=['rolling stone'])['worst_sources']
    assert list(worst) == ['Other'] and worst['Other']['blocked'] is False


def test_scorecard_grades_the_reader_model_out_of_time():
    # Before the test weeks the reader liked A; inside them, only B. A model that had
    # seen the test weeks would rank B first; one fitted on the past ranks A first.
    past = ([_on('good', 60, source='A', selection_bucket='mid') for _ in range(20)]
            + [_on('bad', 60, source='B', selection_bucket='mid') for _ in range(20)])
    test = ([_on('bad', d, source='A', selection_bucket='mid', score=80) for d in range(1, 21)]
            + [_on('good', d, source='B', selection_bucket='mid', score=20) for d in range(1, 21)])
    card = audit.signal_scorecard(past + test, TODAY)
    assert card['n'] == 40
    assert card['signals']['reader_model']['auc'] < 0.5
    assert card['signals']['score']['auc'] == 0.0


def test_stage_costs_sum_the_week_and_skip_older_runs():
    def run(day: date, gate: float) -> Dict:
        return {'timestamp': f'{day.isoformat()}T04:00:00+00:00',
                'api_usage': {'est_cost_usd': gate + 0.1,
                              'claude_by_stage': {'gate': {'calls': 2, 'est_cost_usd': gate}}}}
    costs = audit.stage_costs([run(TODAY - timedelta(days=9), 5.0), run(TODAY, 0.2),
                               run(TODAY - timedelta(days=1), 0.3)], TODAY)
    assert costs['runs'] == 2 and costs['runs_with_stages'] == 2
    assert costs['by_stage']['gate'] == {'calls': 4, 'est_cost_usd': 0.5}
    assert costs['est_cost_usd'] == 0.7


def _spots(ratings=(), runs=(), distribution=None, places=None, followthrough=(),
           history=()) -> Dict[str, Dict]:
    found = audit.blind_spots(list(ratings), list(runs), TODAY, distribution or {},
                              places or {'places': []}, list(followthrough), list(history))
    return {f['id']: f for f in found}


def test_unused_verdict_and_unmeasured_category(monkeypatch):
    monkeypatch.setattr(audit.config_loader, 'get_all_categories', lambda: ['news', 'scifi'])
    monkeypatch.setattr(audit, 'price_table_age', lambda today: 0)
    ratings = ([_on('bad', 2, original_category='news') for _ in range(40)]
               + [_on('good', 2, original_category='news') for _ in range(20)]
               + [_on('interesting', 3, original_category='scifi')])
    found = _spots(ratings)
    assert 'unused-verdict:podcast_only' in found
    assert 'unused-verdict:bad' not in found
    assert 'scifi (1)' in found['unmeasured-categories']['detail']
    assert 'news (' not in found['unmeasured-categories']['detail']


def test_a_theme_that_never_wins_is_flagged_once_it_never_wins(monkeypatch):
    monkeypatch.setattr(audit, 'price_table_age', lambda today: 0)
    monkeypatch.setattr(audit.config_loader, 'get_all_categories', lambda: [])
    monkeypatch.setattr(audit.config_loader, 'load_podcast_schedule_config', lambda: {
        'targeted_rescore': {'days': ['tuesday']},
        'schedule': {'thursday': {'label': 'Indigenous Lands & Innovation'}}})

    def run(days_ago: int, thursday: int) -> Dict:
        wins = {d: 10 for d in audit.WEEKDAYS}
        wins['thursday'] = thursday
        return {'timestamp': f'{(TODAY - timedelta(days=days_ago)).isoformat()}T04:00',
                'theme_argmax': {'wins': wins}}
    found = _spots(runs=[run(2, 0), run(1, 0)])
    assert 'Not in targeted_rescore.days' in found['starved-theme:thursday']['detail']
    assert 'starved-theme:thursday' not in _spots(runs=[run(2, 0), run(1, 1)])


def test_findings_count_the_weeks_they_have_repeated(monkeypatch):
    monkeypatch.setattr(audit, 'price_table_age', lambda today: 0)
    monkeypatch.setattr(audit.config_loader, 'get_all_categories', lambda: [])
    distribution = {'worst_sources': {'Mother Jones': {'block_candidate': True}}}
    history = [{'week': '2026-W39', 'findings': ['unblocked-candidates']},
               {'week': '2026-W40', 'findings': ['unblocked-candidates']},
               {'week': '2026-W41', 'findings': []}]  # this week's own earlier run
    found = _spots(distribution=distribution, history=history)['unblocked-candidates']
    assert found['weeks'] == 3 and found['escalate'] is True
    gap = [{'week': '2026-W39', 'findings': ['unblocked-candidates']}, {'week': '2026-W40', 'findings': []}]
    assert _spots(distribution=distribution, history=gap)['unblocked-candidates']['weeks'] == 1


def test_starved_place_needs_appetite_ratings_and_thin_supply(monkeypatch):
    monkeypatch.setattr(audit, 'price_table_age', lambda today: 0)
    monkeypatch.setattr(audit.config_loader, 'get_all_categories', lambda: [])
    ratings = ([_on('good', 5, title='Quesnel council') for _ in range(6)]
               + [_on('bad', 5, title='Elsewhere') for _ in range(30)]
               + [_on('good', 5, title='Horsefly salmon')])
    pool = [{'title': 'Quesnel bridge'}] + [{'title': 'other'}] * 199
    places = audit.place_supply(ratings, pool, ['quesnel', 'horsefly'])
    assert places['places'][0] == {'place': 'quesnel', 'rated': 6, 'wanted_pct': 100.0,
                                   'in_pool': 1, 'pool_pct': 0.5}
    found = _spots(places=places)
    assert 'quesnel' in found['starved-places']['detail']
    assert found['unmeasured-places']['detail'].endswith('horsefly.')


def test_followthrough_checks_the_latest_change_against_config(tmp_path, monkeypatch):
    import json
    history = tmp_path / 'change_history.json'
    history.write_text(json.dumps({'changes': [
        {'run_date': '2026-09-13', 'knob': 'source_preferences.kagi', 'old_value': 10, 'new_value': 12},
        {'run_date': '2026-09-20', 'knob': 'source_preferences.kagi', 'old_value': 10, 'new_value': 12},
        {'run_date': '2026-09-06', 'knob': 'limits.floor', 'old_value': 23, 'new_value': 25},
        {'run_date': '2026-09-06', 'knob': 'feed_slots.news', 'old_value': 25, 'new_value': 22},
        {'run_date': '2026-09-27', 'knob': 'limits.dry', 'old_value': 1, 'new_value': 2, 'dry_run': True},
    ]}))
    monkeypatch.setattr(audit, 'CHANGE_HISTORY_FILE', history)
    monkeypatch.setattr(audit.config_loader, 'load_calibration_bounds', lambda: {'knobs': {
        'source_preferences.kagi': {'file': 'config/source_preferences.json', 'path': ['kagi']},
        'limits.floor': {'file': 'config/limits.json', 'path': ['floor']},
        'feed_slots.news': {'file': 'config/feed_slots.json', 'path': ['news', 'max_slots']}}})
    monkeypatch.setitem(audit._KNOB_LOADERS, 'config/source_preferences.json', lambda: {'kagi': 10})
    monkeypatch.setitem(audit._KNOB_LOADERS, 'config/limits.json', lambda: {'floor': 25})
    monkeypatch.setitem(audit._KNOB_LOADERS, 'config/feed_slots.json', lambda: {'news': {'max_slots': 10}})
    rows = audit.calibration_followthrough([])
    assert [r['status'] for r in rows] == ['', 'not in config', 'in config', 'changed since']
    assert rows[3]['current'] == 10
    assert 'not-landed:source_preferences.kagi' in _spots(followthrough=rows)


def test_metrics_history_backfills_once_and_replaces_its_own_week():
    ratings = [_on('good', d) for d in (1, 8, 15, 22)]
    record = {**audit.week_record(ratings, TODAY), 'findings': ['x']}
    first = audit.merge_metrics_history([], record, ratings)
    assert [r['week'] for r in first] == ['2026-W38', '2026-W39', '2026-W40', '2026-W41']
    assert all(r.get('backfilled') for r in first[:-1]) and first[-1]['findings'] == ['x']
    again = audit.merge_metrics_history(first, {**record, 'findings': ['y']}, ratings)
    assert len(again) == 4 and again[-1]['findings'] == ['y']


def test_metrics_history_round_trips(tmp_path):
    path = tmp_path / 'reports' / 'weekly_metrics.jsonl'
    audit.write_metrics_history([{'week': '2026-W40', 'rated': 3}], path)
    assert audit.read_metrics_history(path) == [{'week': '2026-W40', 'rated': 3}]
    assert audit.read_metrics_history(tmp_path / 'missing.jsonl') == []


def test_price_table_age_reads_claude_md(tmp_path, monkeypatch):
    md = tmp_path / 'CLAUDE.md'
    md.write_text('**Anthropic prices** (USD per million tokens, checked 2026-09-01; refresh)')
    monkeypatch.setattr(audit, 'CLAUDE_MD_FILE', md)
    assert audit.price_table_age(TODAY) == 39
    monkeypatch.setattr(audit, 'CLAUDE_MD_FILE', tmp_path / 'missing.md')
    assert audit.price_table_age(TODAY) is None
