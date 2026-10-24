"""Kagi News's community feed lists as a free discovery candidate source.

Kite needs 25+ feeds per category, so its lists are broad: only hosts not
already in feeds.opml become candidates, and the source rides the same
per-run cap and keyword prefilter as Kagi Small Web.
"""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config_loader
import feed_discovery as fd

KITE_FEEDS = {
    'Canada': {'feeds': [
        'https://www.castanet.net/rss/topheadlines.xml',
        'https://www.cbc.ca/webfeed/rss/rss-canada-britishcolumbia',  # known host
        'https://news.google.com/rss/topics/CAAq?hl=en-CA',
        'https://rsshub.app/some/route',
        'https://www.castanet.net/rss/topheadlines.xml',  # listed twice
        'https://www.bnn.ca/rss',
    ]},
    'Smart Home': {'feeds': ['https://digiblur.com/feed/', 'not-a-url']},
    'Pizza': {'feeds': ['https://pizza.example/feed']},  # not a category we map
}


def _discovery() -> fd.FeedDiscovery:
    discovery = fd.FeedDiscovery.__new__(fd.FeedDiscovery)
    discovery.existing_feeds = {'https://www.cbc.ca/cmlink/rss-canada'}
    return discovery


def _reply(payload):
    response = mock.Mock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


def test_only_new_hosts_from_mapped_categories_become_interleaved_candidates() -> None:
    with mock.patch.object(fd.requests, 'get', return_value=_reply(KITE_FEEDS)):
        candidates = _discovery()._fetch_kite_candidates()
    assert [(c.url, c.category, c.source) for c in candidates] == [
        ('https://www.castanet.net/rss/topheadlines.xml', 'news', fd.KITE_FEEDS_SOURCE),
        ('https://digiblur.com/feed/', 'homelab', fd.KITE_FEEDS_SOURCE),
        ('https://www.bnn.ca/rss', 'news', fd.KITE_FEEDS_SOURCE),
    ]
    assert candidates[0].title == 'castanet.net'


def test_a_fetch_failure_yields_no_candidates() -> None:
    with mock.patch.object(fd.requests, 'get', side_effect=fd.requests.ConnectionError('down')):
        assert _discovery()._fetch_kite_candidates() == []


def test_the_source_is_gated_like_kagi_small_web() -> None:
    gate = config_loader.load_source_preferences()['discovery_prescore_filter']
    assert fd.KITE_FEEDS_SOURCE in gate['sources']
