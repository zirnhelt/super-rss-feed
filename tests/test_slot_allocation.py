"""Slot allocation is the selector now — the floor bounds quality, not volume."""
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import super_rss_curator_json as m


def _a(cat, score):
    o = types.SimpleNamespace()
    o.category = cat
    o.score = score
    return o


def test_min_slots_are_filled_even_below_the_floor(monkeypatch):
    """A thin day in a niche category still ships its best available articles —
    this is what the old min_per_category rescue did."""
    monkeypatch.setattr(m, 'FEED_SLOTS', {'science': {'min_slots': 3, 'max_slots': 8},
                                          'default': {'min_slots': 1, 'max_slots': 5}})
    monkeypatch.setattr(m, 'LIMITS', dict(m.LIMITS, min_claude_score=25,
                                          min_score_by_category={'science': 40}))
    arts = [_a('science', s) for s in (12, 9, 5, 3)]

    out = m.apply_feed_slot_allocation(arts)

    assert len(out) == 3, 'min_slots must be honoured regardless of the floor'
    assert [x.score for x in out] == [12, 9, 5], 'and filled best-first'


def test_floor_applies_past_the_guaranteed_minimum(monkeypatch):
    monkeypatch.setattr(m, 'FEED_SLOTS', {'news': {'min_slots': 2, 'max_slots': 25},
                                          'default': {'min_slots': 1, 'max_slots': 5}})
    monkeypatch.setattr(m, 'LIMITS', dict(m.LIMITS, min_claude_score=25,
                                          min_score_by_category={'news': 20}))
    arts = [_a('news', s) for s in (80, 60, 19, 18, 5)]

    out = m.apply_feed_slot_allocation(arts)

    assert sorted(x.score for x in out) == [60, 80], \
        'past min_slots only floor-clearing articles are eligible'


def test_max_slots_still_caps_a_heavy_category(monkeypatch):
    monkeypatch.setattr(m, 'FEED_SLOTS', {'news': {'min_slots': 2, 'max_slots': 4},
                                          'default': {'min_slots': 1, 'max_slots': 5}})
    monkeypatch.setattr(m, 'LIMITS', dict(m.LIMITS, min_claude_score=10,
                                          min_score_by_category={}))
    out = m.apply_feed_slot_allocation([_a('news', s) for s in range(90, 60, -1)])

    assert len(out) == 4
    assert [x.score for x in out] == [90, 89, 88, 87]


def test_feed_size_is_stable_across_a_good_and_a_bad_day(monkeypatch):
    """The point of the change: volume stops tracking where the day's scores landed."""
    slots = {'news': {'min_slots': 2, 'max_slots': 10},
             'default': {'min_slots': 1, 'max_slots': 5}}
    monkeypatch.setattr(m, 'FEED_SLOTS', slots)
    monkeypatch.setattr(m, 'LIMITS', dict(m.LIMITS, min_claude_score=25,
                                          min_score_by_category={'news': 20}))
    good_day = m.apply_feed_slot_allocation([_a('news', s) for s in range(70, 40, -1)])
    lean_day = m.apply_feed_slot_allocation([_a('news', s) for s in range(30, 18, -1)])

    assert len(good_day) == 10
    assert len(lean_day) == 10, 'a lean day fills its slots instead of collapsing'


def test_empty_slot_config_is_a_passthrough(monkeypatch):
    monkeypatch.setattr(m, 'FEED_SLOTS', {})
    arts = [_a('news', 50)]
    assert m.apply_feed_slot_allocation(arts) == arts


def _w(cat, score, q_gate, world=True):
    o = _a(cat, score)
    o.q_gate = q_gate
    o.gate_world = world
    return o


def _world_config(monkeypatch, world_slots=2, max_slots=3):
    monkeypatch.setattr(m, 'FEED_SLOTS', {
        'news': {'min_slots': 1, 'max_slots': max_slots, 'world_slots': world_slots},
        'default': {'min_slots': 1, 'max_slots': 5}})
    monkeypatch.setattr(m, 'LIMITS', dict(m.LIMITS, min_claude_score=25,
                                          min_score_by_category={'news': 20},
                                          quality_gate={'gate_floor': 25}))


def test_world_lane_ships_on_top_of_max_slots(monkeypatch):
    """A war's turning point scores 8-30 on the personal composite; the lane
    must not make it compete with the day's best interest matches for a slot."""
    _world_config(monkeypatch)
    personal = [_a('news', s) for s in (90, 80, 70, 60)]
    world = [_w('news', 15, 70), _w('news', 23, 65)]

    out = m.apply_feed_slot_allocation(personal + world)

    assert len(out) == 5, 'max_slots (3) for the composite, plus 2 world slots'
    assert all(a in out for a in world)
    assert [a.score for a in out if not getattr(a, 'world_lane', False)] == [90, 80, 70]


def test_world_lane_ranks_by_q_gate_not_composite(monkeypatch):
    _world_config(monkeypatch, world_slots=1)
    thin_but_big = _w('news', 12, 72)
    well_liked = _w('news', 60, 40)

    out = m.apply_feed_slot_allocation([well_liked, thin_but_big])

    assert thin_but_big.world_lane is True
    assert not getattr(well_liked, 'world_lane', False), \
        'the runner-up competes for an ordinary slot on its composite instead'
    assert well_liked in out


def test_world_lane_needs_the_flag_and_the_gate_floor(monkeypatch):
    _world_config(monkeypatch, world_slots=3, max_slots=0)
    unflagged = _w('news', 50, 80, world=False)
    below_gate = _w('news', 50, 20)
    unjudged = _w('news', 50, 80, world=None)
    flagged = _w('news', 50, 30)

    out = m.apply_feed_slot_allocation([unflagged, below_gate, unjudged, flagged])

    assert [a for a in out if getattr(a, 'world_lane', False)] == [flagged]


def test_world_lane_is_per_category(monkeypatch):
    """Only a category that configures world_slots reserves them."""
    _world_config(monkeypatch)
    climate_summit = _w('climate', 15, 75)

    m.apply_feed_slot_allocation([climate_summit])

    assert not getattr(climate_summit, 'world_lane', False)
