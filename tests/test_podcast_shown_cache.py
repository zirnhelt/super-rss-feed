"""Only a mark stamped on its own day's weekday survives a load of the shown cache.

Before 2026-10-24 every nightly marked all seven podcast feeds as shown, so each
day's best articles were locked out of its own episode for the cache's 7-day TTL.
Those leftover marks kept the Thursday feed led by articles the charter had just
scored 4-14, while twelve confirmed Indigenous-governance stories waited out
marks from earlier in the week.
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import super_rss_curator_json as m


def _stamp(days_ago: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()


def test_a_mark_from_another_days_run_is_dropped(monkeypatch, tmp_path):
    path = tmp_path / 'shown.json'
    monkeypatch.setattr(m, 'PODCAST_SHOWN_FILE', str(path))
    aired = _stamp(1)
    aired_day = datetime.fromisoformat(aired).strftime('%A').lower()
    other_day = 'monday' if aired_day != 'monday' else 'tuesday'
    path.write_text(json.dumps({
        f'https://example.com/aired:::{aired_day}': {'day': aired_day, 'shown_at': aired},
        f'https://example.com/burned:::{other_day}': {'day': other_day, 'shown_at': aired},
        f'https://example.com/old:::{aired_day}': {'day': aired_day, 'shown_at': _stamp(15)},
    }))

    assert list(m.load_podcast_shown_cache()) == [f'https://example.com/aired:::{aired_day}']
