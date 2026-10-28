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
