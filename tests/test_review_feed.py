"""The review feed's strata partition the pool, its stats read the ledger locally, and
a batch is offered once."""
import json
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import super_rss_curator_json as m


def _n(category: str, score: int, **kw) -> types.SimpleNamespace:
    return types.SimpleNamespace(category=category, score=score, source=kw.pop('source', 's'),
                                 world_lane=kw.pop('world_lane', False), **kw)


def test_near_misses_rank_by_distance_to_their_own_categorys_line():
    shipped = [_n('news', 70), _n('news', 60), _n('scifi', 30),
               _n('news', 10, world_lane=True)]          # the lane does not set the line
    cut = [_n('news', 40), _n('scifi', 28), _n('news', 58)]

    order = [(a.category, a.score) for a in m.review_near_misses(cut, shipped)]

    # news line 60, scifi line 30: gaps -2, -2, -20 (stable sort keeps input order on a tie)
    assert order == [('scifi', 28), ('news', 58), ('news', 40)]


def test_a_category_that_shipped_nothing_measures_from_its_floor(monkeypatch):
    monkeypatch.setattr(m, 'min_score_for_category', lambda cat: 50)
    order = [a.score for a in m.review_near_misses([_n('design', 20), _n('design', 45)], [])]
    assert order == [45, 20]


def test_the_batch_is_twelve_and_every_stratum_is_one_the_audit_counts():
    import article_review_audit
    assert sum(m.REVIEW_QUOTAS.values()) == m.REVIEW_CURATED_TARGET
    assert m.REVIEW_CURATED_TARGET + m.REVIEW_UNFILTERED_CAP == 12
    assert set(m.REVIEW_QUOTAS) <= set(article_review_audit.SHIPPED_STRATA)


def test_stats_merge_frequent_notes_with_defaults(tmp_path, monkeypatch):
    fb = tmp_path / 'feedback'
    fb.mkdir()
    rows = [
        {'url': 'u1', 'rating': 'bad', 'note': 'us politics', 'selection_bucket': 'unfiltered'},
        {'url': 'u2', 'rating': 'bad', 'note': 'US politics.', 'selection_bucket': 'mid'},
        {'url': 'u3', 'rating': 'bad', 'note': 'one-off', 'selection_bucket': 'mid'},
        {'url': 'u4', 'rating': 'good', 'selection_bucket': 'mid'},
    ]
    (fb / '2026-09-23.json').write_text(json.dumps({'ratings': rows}))
    (fb / '2026-09-24.json').write_text(json.dumps({'ratings': rows[3:]}))
    (fb / 'feedback_rollup.json').write_text(json.dumps({'totals': {'good': 10}}))
    monkeypatch.chdir(tmp_path)

    stats = m.review_history_stats('2026-09-24')

    bad = stats['reasons']['bad']
    assert bad[0] == 'US politics'  # the default's casing wins
    assert 'One-off' not in bad
    assert sum(r.lower() == 'us politics' for r in bad) == 1
    assert stats['reasons']['good'] == m.REVIEW_REASON_DEFAULTS['good']
    assert set(stats['reasons']) == {'good', 'interesting', 'bad', 'podcast_only'}
    assert stats['streak'] == 2
    assert stats['all_time']['good'] == 12
    assert stats['by_bucket']['mid'] == {'n': 4, 'positive_pct': 50}


def test_tapped_reasons_count_separately(tmp_path, monkeypatch):
    fb = tmp_path / 'feedback'
    fb.mkdir()
    rows = [
        {'url': 'u1', 'rating': 'interesting', 'note': 'Beaver dams; Surprising'},
        {'url': 'u2', 'rating': 'interesting', 'note': 'beaver dams'},
        {'url': 'u3', 'rating': 'bad', 'note': 'Beaver dams'},
    ]
    (fb / '2026-09-24.json').write_text(json.dumps({'ratings': rows}))
    monkeypatch.chdir(tmp_path)

    reasons = m.review_history_stats('2026-09-24')['reasons']

    assert reasons['interesting'][0] == 'Beaver dams'
    assert 'Beaver dams' not in reasons['bad']  # counted per rating, n=1 there


def test_podcast_only_counts_in_a_bucket_but_not_as_feed_positive(tmp_path, monkeypatch):
    fb = tmp_path / 'feedback'
    fb.mkdir()
    rows = [{'url': 'u1', 'rating': 'podcast_only', 'selection_bucket': 'mid'},
            {'url': 'u2', 'rating': 'good', 'selection_bucket': 'mid'}]
    (fb / '2026-09-30.json').write_text(json.dumps({'ratings': rows}))
    monkeypatch.chdir(tmp_path)

    stats = m.review_history_stats('2026-09-30')

    assert stats['by_bucket']['mid'] == {'n': 2, 'positive_pct': 50}
    assert stats['recent']['podcast_only'] == 1


# ── A batch is offered once ────────────────────────────────────────────────────

def _feed(batch, urls, offered=None, legacy=False):
    feed = {'items': [{'url': u} for u in urls], '_offered': offered or {}}
    if legacy:
        feed['_generated_at'] = f'{batch}T04:10:41+00:00'
    else:
        feed['_batch'] = batch
    return feed


def test_yesterdays_batch_is_not_offered_again():
    ledger = m.review_offered_ledger(_feed('2026-09-28', ['a', 'b']), '2026-09-29', 3)
    assert ledger == {'a': '2026-09-28', 'b': '2026-09-28'}


def test_a_missed_day_is_dropped_not_carried():
    # Day 1 never opened; day 2 still excludes it, and day 3 excludes both.
    day2 = m.review_offered_ledger(_feed('2026-09-27', ['missed']), '2026-09-28', 3)
    day3 = m.review_offered_ledger(_feed('2026-09-28', ['seen'], offered=day2), '2026-09-29', 3)
    assert day3 == {'missed': '2026-09-27', 'seen': '2026-09-28'}


def test_a_same_day_rerun_keeps_its_own_batch_eligible():
    previous = _feed('2026-09-29', ['mine'], offered={'older': '2026-09-28'})
    assert m.review_offered_ledger(previous, '2026-09-29', 3) == {'older': '2026-09-28'}


def test_the_ledger_only_spans_the_lookback():
    previous = _feed('2026-09-28', ['recent'], offered={'stale': '2026-09-20'})
    assert m.review_offered_ledger(previous, '2026-09-29', 3) == {'recent': '2026-09-28'}


def test_a_feed_from_before_the_ledger_still_counts():
    previous = _feed('2026-09-28', ['a'], legacy=True)
    assert m.review_offered_ledger(previous, '2026-09-29', 3) == {'a': '2026-09-28'}


def test_no_previous_feed_excludes_nothing():
    assert m.review_offered_ledger(None, '2026-09-29', 3) == {}
    assert m.review_offered_ledger({'items': 'garbage'}, '2026-09-29', 3) == {}


def _c(category: str, score: int) -> types.SimpleNamespace:
    return types.SimpleNamespace(category=category, score=score)


def test_categories_rotate_within_a_stratum_and_the_lead_is_kept():
    pool = [_c('news', 90), _c('news', 88), _c('news', 85), _c('scifi', 70),
            _c('news', 60), _c('homestead', 55), _c('scifi', 50)]

    rotated = m.rotate_review_categories(pool)

    assert [(a.category, a.score) for a in rotated] == [
        ('news', 90), ('scifi', 70), ('homestead', 55),
        ('news', 88), ('scifi', 50),
        ('news', 85), ('news', 60)]


def test_rotation_keeps_every_article_and_defaults_a_missing_category_to_news():
    pool = [_c(None, 40), _c('news', 39), _c('design', 38)]
    rotated = m.rotate_review_categories(pool)
    assert sorted(a.score for a in rotated) == [38, 39, 40]
    assert [a.score for a in rotated] == [40, 38, 39]
    assert m.rotate_review_categories([]) == []


def test_the_wildcard_is_its_own_stratum_and_never_also_in_feed(monkeypatch):
    """docs/MANIFESTO.md: the wildcard ships at the bottom of a category, so in_feed
    (top of the feed) would almost never sample it. A partition keeps the weights valid."""
    monkeypatch.setattr(m, 'min_score_for_category', lambda cat: 50)
    top = _n('news', 90, url_hash='a')
    wild = _n('science', 20, url_hash='w', wildcard=True)
    cut = _n('news', 48, url_hash='c')

    pools = m.review_pools([top, wild, cut], shipped=[top, wild])

    assert pools['wildcard'] == [wild]
    assert pools['in_feed'] == [top]
    assert pools['near_miss'] == [cut]
    assert list(m.REVIEW_QUOTAS)[0] == 'wildcard', 'taken first, before a shared source blocks it'
