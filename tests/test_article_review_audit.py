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
