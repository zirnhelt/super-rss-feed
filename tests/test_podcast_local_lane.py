"""Every daily podcast feed carries fresh Cariboo stories the show has not aired.

On 2026-10-28 the Wednesday (tech) feed's only local stories were five that had
already aired that week, so the episode opened with no local news while
feed-local held eight fresh Cariboo stories the theme-fit floor had dropped.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import super_rss_curator_json as m

SIGNALS = ['williams lake', 'quesnel', 'cariboo']


def _art(link: str, title: str, source: str = 'Williams Lake Tribune', hours_ago: int = 1,
         local: int = 100, q_gate: int = 60) -> SimpleNamespace:
    return SimpleNamespace(
        link=link, title=title, description='', source=source, local=local, q_gate=q_gate,
        pub_date=datetime.now(timezone.utc) - timedelta(hours=hours_ago),
    )


def test_aired_on_any_day_is_skipped():
    fresh = _art('https://x/fresh', 'Williams Lake council says farewell')
    aired = _art('https://x/aired', 'Rogers outage cut Quesnel off', source='My Cariboo Now')
    shown = {'https://x/aired:::thursday': {'day': 'thursday', 'shown_at': 'x'}}
    assert m.select_local_lane([fresh, aired], set(), shown, 4, SIGNALS) == [fresh]


def test_unanchored_selected_stale_and_syndicated_are_skipped():
    taken = _art('https://x/taken', 'Quesnel poppy campaign kicks off')
    kamloops = _art('https://x/kam', 'Kamloops council budget', source='CFJC Today Kamloops',
                   local=40)
    stale = _art('https://x/old', 'Williams Lake rodeo grounds', hours_ago=100)
    # Anchored only by the outlet's name: provincial syndication, local score 0.
    syndicated = _art('https://x/ferry', 'BC Ferries CEO replaced', local=0)
    lane = m.select_local_lane([taken, kamloops, stale, syndicated], {'https://x/taken'},
                               {}, 4, SIGNALS)
    assert lane == []


def test_ranked_by_gate_score_capped_per_outlet_and_in_total():
    weather = _art('https://x/snow', 'Snow to fall in the Cariboo', q_gate=30, hours_ago=0)
    council = _art('https://x/council', 'Williams Lake councillors give farewells', q_gate=60)
    mock = _art('https://x/mock', 'Williams Lake mock election', q_gate=75)
    mural = _art('https://x/mural', 'Williams Lake mural completed', q_gate=78)
    clinton = _art('https://x/clinton', 'Clinton wildfire recovery in the Cariboo',
                   source='100 Mile Free Press', q_gate=65)
    lane = m.select_local_lane([weather, council, mock, mural, clinton], set(), {}, 3, SIGNALS)
    assert [a.link for a in lane] == ['https://x/mural', 'https://x/mock', 'https://x/clinton']


def test_lane_is_wired_into_the_feed_and_not_calibrated():
    src = Path(m.__file__).read_text()
    assert 'local_lane_candidates' in src and 'select_local_lane(' in src
    bounds = json.loads((Path(m.__file__).parent / 'config' / 'calibration_bounds.json').read_text())
    assert 'podcast.local_lane_slots' in bounds['forbidden']
    assert 'podcast.schedule.*.local_lane_week' in bounds['forbidden']


# The local day's lane. On 2026-11-14 the Saturday feed carried 18 local stories the
# weekday episodes had already aired and 3 fresh ones; the show's Cariboo Local
# Affairs roundup aired no local story.

def test_the_week_lane_reaches_back_the_whole_week():
    old = _art('https://x/babyfest', 'Baby Fest in Williams Lake', hours_ago=120)
    older = _art('https://x/rodeo', 'Williams Lake rodeo grounds', hours_ago=200)
    assert m.select_local_lane([old, older], set(), {}, 4, SIGNALS) == []
    assert m.select_local_lane([old, older], set(), {}, 4, SIGNALS, week=True) == [old]


def test_the_week_lane_keeps_a_story_shown_on_another_day_behind_the_unshown():
    shown_story = _art('https://x/unbc', 'UNBC plan for Quesnel', source='My Cariboo Now', q_gate=80)
    unshown = _art('https://x/fog', 'Fog advisory for the Cariboo', q_gate=30)
    shown = {'https://x/unbc:::tuesday': {'day': 'tuesday', 'shown_at': 'x'}}
    lane = m.select_local_lane([shown_story, unshown], set(), shown, 4, SIGNALS, week=True)
    assert lane == [unshown, shown_story]


def test_the_week_lane_fills_from_bc_only_after_the_cariboo():
    storm = _art('https://x/storm', 'Second major storm hits the Sea to Sky',
                 source='Pique Newsmagazine', local=35, q_gate=90)
    council = _art('https://x/council', 'Quesnel council sets its budget', q_gate=20)
    ferry = _art('https://x/ferry', 'BC Ferries CEO replaced', source='Pique Newsmagazine', local=0)
    assert m.select_local_lane([storm, council, ferry], set(), {}, 4, SIGNALS) == [council]
    assert m.select_local_lane([storm, council, ferry], set(), {}, 4, SIGNALS,
                               week=True) == [council, storm]
    assert m.select_local_lane([storm, council], set(), {}, 1, SIGNALS, week=True) == [council]


def test_the_week_lane_takes_more_from_each_outlet():
    stories = [_art(f'https://x/{i}', f'Williams Lake story {i}', q_gate=60 - i) for i in range(6)]
    assert len(m.select_local_lane(stories, set(), {}, 10, SIGNALS)) == m.LOCAL_LANE_PER_SOURCE
    assert len(m.select_local_lane(stories, set(), {}, 10, SIGNALS,
                                   week=True)) == m.LOCAL_LANE_WEEK_PER_SOURCE


def test_saturday_is_the_week_lane_day():
    schedule = m.load_podcast_schedule()['schedule']
    assert [day for day, cfg in schedule.items() if cfg.get('local_lane_week')] == ['saturday']
    assert schedule['saturday']['local_lane_slots'] == 10
    src = Path(m.__file__).read_text()
    assert 'cap_podcast_outlets(items_with_score, lane_week)' in src


def _item(title: str, outlet: str, local: int) -> dict:
    return {'title': title, 'authors': [{'name': outlet}], '_local': local}


def test_the_outlet_cap_spares_local_stories_on_the_local_day_only():
    """2026-11-14: the cap cut 23 local stories from the Saturday feed, 15 never aired."""
    tribune = [(90 - i, _item(f'Williams Lake story {i}', 'Williams Lake Tribune', 100))
               for i in range(6)]
    syndicated = [(50 - i, _item(f'Penticton story {i}', 'Williams Lake Tribune', 0))
                  for i in range(5)]
    kept, dropped = m.cap_podcast_outlets(tribune + syndicated)
    assert len(kept) == m.PODCAST_OUTLET_CAP and dropped == 8
    kept, dropped = m.cap_podcast_outlets(tribune + syndicated, local_day=True)
    assert [item['title'] for _, item in kept][:6] == [f'Williams Lake story {i}' for i in range(6)]
    # The paper's provincial syndication is still capped.
    assert len(kept) == 6 + m.PODCAST_OUTLET_CAP and dropped == 2
