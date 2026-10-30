"""A feed the probe can read and the nightly cannot is broken, not recovered.

Hacker News failed every nightly from 2026-10-01 (http_419, 29 runs in a row)
while `--heal` logged it "✓ Recovered on its own" four Saturdays running: its
one probe, sent at 13:23 UTC, was answered every time. These tests pin the
override (`HEAL_PROBE_OVERRIDE_DAYS`) and the recheck rules that keep it from
flip-flopping: a nightly-blocked retirement waits out a cool-off instead of
trusting the probe, and a hand retirement is never undone.
"""
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import integrate_discoveries as heal  # noqa: E402

FEED_URL = 'https://example.com/rss'


class _FakeCache:
    def resolved_url(self, url):
        return None


def _tree(**attrs) -> ET.ElementTree:
    root = ET.Element('opml')
    body = ET.SubElement(root, 'body')
    outline = ET.SubElement(body, 'outline', {
        'type': 'rss', 'title': 'Example', 'text': 'Example', 'xmlUrl': FEED_URL, **attrs,
    })
    assert outline is not None
    return ET.ElementTree(root)


def _outline(tree: ET.ElementTree) -> ET.Element:
    return next(o for o in tree.iter('outline') if o.get('xmlUrl') == FEED_URL)


@pytest.fixture
def network(monkeypatch):
    """Stub every network touch; `probe` and `discovered` are set per test."""
    state = {'probe': True, 'discovered': None, 'span_days': 0.0}
    monkeypatch.setattr(heal, '_load_recovery_helpers',
                        lambda: (lambda feed: state['discovered'], None, None, None))
    monkeypatch.setattr(heal, '_probe_feed', lambda url, helpers: 'browser' if state['probe'] else None)
    monkeypatch.setattr(heal, 'network_is_sane', lambda *a: True)
    monkeypatch.setattr(heal, '_google_news_substitute', lambda url, helpers: None)
    monkeypatch.setattr(heal, 'collect_failure_evidence', lambda tree, cache: {
        FEED_URL: {'url': FEED_URL, 'title': 'Example', 'kind': 'http_419',
                   'failures': 29, 'span_days': state['span_days'],
                   'sources': ['feed_http_cache.json']},
    })
    return state


def _heal(tree):
    return heal.heal_feeds(tree, _FakeCache(), min_failures=3, min_days=2,
                           max_feeds=25, allow_substitutes=True, dry_run=False)


def _stamp(days_ago: float) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime('%Y-%m-%d')


def test_short_streak_that_answers_the_probe_is_recovered(network):
    network['span_days'] = 5
    tree = _tree()
    actions = _heal(tree)
    assert [a['action'] for a in actions] == ['recovered']
    assert _outline(tree).get('type') == 'rss'


def test_long_streak_that_answers_the_probe_is_retired_as_nightly_blocked(network):
    network['span_days'] = 28
    tree = _tree()
    actions = _heal(tree)
    assert [a['action'] for a in actions] == ['retired']
    outline = _outline(tree)
    assert outline.get('type') == heal.RETIRED_TYPE
    assert outline.get('nightlyBlocked') == '1'


def test_nightly_block_is_never_relocated_to_the_same_blocked_feed(network):
    network['span_days'] = 28
    network['discovered'] = 'https://example.com/feed/'
    tree = _tree()
    actions = _heal(tree)
    assert [a['action'] for a in actions] == ['retired']
    assert _outline(tree).get('xmlUrl') == FEED_URL


def test_restored_feed_is_judged_only_on_nights_since_restore(network):
    network['span_days'] = 60  # cache streak predates the retirement
    tree = _tree(restoredAt=_stamp(3))
    actions = _heal(tree)
    assert [a['action'] for a in actions] == ['recovered']


def test_recheck_keeps_nightly_blocked_feed_retired_during_cooloff(network):
    tree = _tree(type=heal.RETIRED_TYPE, nightlyBlocked='1', retiredAt=_stamp(7))
    assert heal.recheck_retired(tree, max_feeds=25, dry_run=False) == []
    assert _outline(tree).get('type') == heal.RETIRED_TYPE


def test_recheck_restores_nightly_blocked_feed_after_cooloff(network):
    network['probe'] = False  # the probe is not what restores it
    tree = _tree(type=heal.RETIRED_TYPE, nightlyBlocked='1',
                 retiredAt=_stamp(heal.HEAL_NIGHTLY_BLOCK_COOLOFF_DAYS + 1))
    actions = heal.recheck_retired(tree, max_feeds=25, dry_run=False)
    assert [a['action'] for a in actions] == ['restored']
    outline = _outline(tree)
    assert outline.get('type') == 'rss'
    assert outline.get('nightlyBlocked') is None


def test_recheck_never_restores_a_hand_retirement(network):
    tree = _tree(type=heal.RETIRED_TYPE, retiredBy='hand', retiredAt=_stamp(400))
    assert heal.recheck_retired(tree, max_feeds=25, dry_run=False) == []
    assert _outline(tree).get('type') == heal.RETIRED_TYPE
