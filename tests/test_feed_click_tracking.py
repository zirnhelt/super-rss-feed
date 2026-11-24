"""Click tracking on feed articles: phase 1 of a click training signal (2026-11-24).

The listed feeds (system.json -> clicks.feeds) route each item's `url` through the digest-click
Worker; an exposure ledger remembers what was offered, and the nightly joins each click back to
the article's features. Nothing here changes a score: clicks stay evidence, never ratings.
"""
import inspect
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import article_review_audit as audit
import super_rss_curator_json as m
from tests.test_sanitize import _article

BASE = 'https://cariboo-signals-clicks.example.workers.dev'
KEY = 'test-key-0123456789abcdef0123456789'
TODAY = datetime.now(timezone.utc).date().isoformat()


def _on(monkeypatch, feeds=('news', 'local')):
    monkeypatch.setitem(m.SYSTEM, 'clicks', {'base_url': BASE, 'feeds': list(feeds)})
    monkeypatch.setenv('CLICKS_KEY', KEY)


def _written(tmp_path, name='feed-news.json'):
    return json.loads((tmp_path / name).read_text(encoding='utf-8'))['items']


def _query(href):
    return {k: v[0] for k, v in parse_qs(urlparse(href).query).items()}


def test_listed_feeds_route_item_links_through_the_worker(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _on(monkeypatch)
    m.generate_json_feed([_article('https://news.test/a')], 'news', 'feed-news.json')
    item, = _written(tmp_path)
    assert item['url'].startswith(BASE + '/go?')
    q = _query(item['url'])
    assert (q['u'], q['c'], q['d']) == ('https://news.test/a', 'feed:news', TODAY)
    assert q['s'] == m._click_signature(KEY, 'https://news.test/a', 'feed:news', TODAY)
    assert item['id'] == 'https://news.test/a', 'identity stays the publisher URL'
    assert item['external_url'] == 'https://news.test/a'
    assert m.item_source_link(item) == 'https://news.test/a'


def test_the_rss_mirror_carries_the_tracked_link_and_the_publisher_guid(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _on(monkeypatch)
    m.generate_json_feed([_article('https://news.test/a')], 'local', 'feed-local.json')
    rss = (tmp_path / 'feed-local.xml').read_text(encoding='utf-8')
    assert BASE + '/go?' in rss
    assert '>https://news.test/a</guid>' in rss


def test_unlisted_feeds_and_an_unconfigured_worker_stay_plain(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _on(monkeypatch, feeds=('news',))
    m.generate_json_feed([_article('https://news.test/a')], 'science', 'feed-science.json')
    item, = _written(tmp_path, 'feed-science.json')
    assert item['url'] == 'https://news.test/a' and 'external_url' not in item

    monkeypatch.delenv('CLICKS_KEY')
    m.generate_json_feed([_article('https://news.test/a')], 'news', 'feed-news.json')
    assert _written(tmp_path)[0]['url'] == 'https://news.test/a', 'no key: an unsigned link would be a 400'

    monkeypatch.setitem(m.SYSTEM, 'clicks', {'base_url': BASE})
    monkeypatch.setenv('CLICKS_KEY', KEY)
    m.generate_json_feed([_article('https://news.test/a')], 'news', 'feed-news.json')
    assert _written(tmp_path)[0]['url'] == 'https://news.test/a', 'no feeds listed: off'


def test_an_apple_news_link_is_wrapped_and_keeps_the_publisher_url():
    item = {'url': 'https://apple.news/Axyz', 'external_url': 'https://pub.test/a'}
    target = m.apply_click_tracking(item, 'news', '2026-11-24', BASE, KEY)
    assert target == 'https://apple.news/Axyz', 'the Worker forwards to what the reader would have opened'
    assert item['external_url'] == 'https://pub.test/a'
    assert _query(item['url'])['u'] == 'https://apple.news/Axyz'


def test_a_link_the_worker_would_refuse_is_left_alone():
    insecure = {'url': 'http://insecure.test/a'}
    assert m.apply_click_tracking(insecure, 'news', '2026-11-24', BASE, KEY) is None
    assert insecure == {'url': 'http://insecure.test/a'}
    too_long = {'url': 'https://pub.test/' + 'a' * m.CLICKS_MAX_URL_CHARS}
    assert m.apply_click_tracking(too_long, 'news', '2026-11-24', BASE, KEY) is None
    assert 'external_url' not in too_long


def test_a_retained_item_is_rewrapped_from_the_publisher_url_never_stacked(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _on(monkeypatch)
    m.generate_json_feed([_article('https://news.test/a')], 'news', 'feed-news.json')
    for _ in range(3):
        item, = _written(tmp_path)
        retained = m._article_from_feed_item(item)
        assert retained.link == 'https://news.test/a'
        m.generate_json_feed([retained], 'news', 'feed-news.json')
    item, = _written(tmp_path)
    assert _query(item['url'])['u'] == 'https://news.test/a'
    assert item['external_url'] == 'https://news.test/a'


def test_the_digest_item_and_the_podcast_feeds_are_never_wrapped(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _on(monkeypatch)
    digest = {'id': m.DIGEST_ID_PREFIX + '2026-11-24', 'url': f'{m.FEEDS_CONFIG["base_url"]}/{m.DIGEST_PAGE}',
              'title': 'Also in the news', 'content_html': '<p>x</p>', 'date_published': '2026-11-24T08:00:00+00:00',
              'authors': [{'name': 'Kagi News', 'url': 'https://kite.kagi.com'}]}
    m.generate_json_feed([_article('https://news.test/a')], 'news', 'feed-news.json', passthrough_items=[digest])
    first = _written(tmp_path)[0]
    assert first['url'] == digest['url'] and 'external_url' not in first
    # The show reads these links and defaults what it cannot match: no wrapper may reach them.
    assert 'apply_click_tracking' not in inspect.getsource(m.generate_podcast_feed)


def test_exposure_is_recorded_per_article_with_its_features(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _on(monkeypatch)
    exposure = {}
    arts = [_article('https://news.test/a', content_type='analysis', relevance=71),
            _article('https://news.test/b?utm_source=x')]
    m.generate_json_feed(arts, 'news', 'feed-news.json', exposure=exposure)
    entry = exposure[m.canonicalize_url('https://news.test/a')]
    assert entry == {'link': 'https://news.test/a', 'source': 'Test Outlet', 'feed': 'news',
                     'content_type': 'analysis', 'relevance_band': 3,
                     'first': TODAY, 'last': TODAY, 'days': 1, 'best_pos': 0}
    assert exposure[m.canonicalize_url('https://news.test/b?utm_source=x')]['best_pos'] == 1
    assert len(exposure) == 2


def test_nothing_is_recorded_without_a_ledger_or_for_unlisted_feeds(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _on(monkeypatch, feeds=('news',))
    exposure = {}
    m.generate_json_feed([_article('https://news.test/a')], 'science', 'feed-science.json', exposure=exposure)
    assert exposure == {}
    m.generate_json_feed([_article('https://news.test/a')], 'news', 'feed-news.json')  # the refresh paths


def _item(url='https://news.test/a', rel=55):
    return {'url': url, 'authors': [{'name': 'Outlet'}], '_relevance': rel}


def test_a_day_counts_once_and_the_best_position_wins():
    exposure = {}
    for day, pos in (('2026-11-20', 7), ('2026-11-20', 3), ('2026-11-21', 9), ('2026-11-22', 5)):
        m.record_click_exposure(exposure, 'https://news.test/a', _item(), 'news', pos, day)
    entry, = exposure.values()
    assert (entry['first'], entry['last'], entry['days'], entry['best_pos']) == ('2026-11-20', '2026-11-22', 3, 3)


def test_a_missing_relevance_leaves_the_band_empty():
    exposure = {}
    item = _item()
    del item['_relevance']
    m.record_click_exposure(exposure, 'https://news.test/a', item, 'news', 0, '2026-11-20')
    assert next(iter(exposure.values()))['relevance_band'] is None


def test_the_ledger_round_trips_and_drops_what_has_left_the_feeds(tmp_path):
    path = str(tmp_path / 'clicks' / 'exposure.json')
    assert m.load_click_exposure(path) == {}, 'absent'
    exposure = {}
    m.record_click_exposure(exposure, 'https://news.test/old', _item(), 'news', 0, '2026-10-01')
    m.record_click_exposure(exposure, 'https://news.test/new', _item(), 'news', 0, '2026-11-23')
    assert m.save_click_exposure(exposure, '2026-11-24', path) == 1
    assert list(m.load_click_exposure(path)) == [m.canonicalize_url('https://news.test/new')]
    Path(path).write_text('{truncated', encoding='utf-8')
    assert m.load_click_exposure(path) == {}, 'a corrupt ledger loads as empty, like every cache'
    Path(path).write_text('[1, 2]', encoding='utf-8')
    assert m.load_click_exposure(path) == {}


class _Reply:
    def __init__(self, body):
        self.body, self.status_code = body, 200

    def raise_for_status(self):
        pass

    def json(self):
        return self.body


def test_fetched_feed_clicks_carry_the_article_they_opened(tmp_path, monkeypatch):
    _on(monkeypatch)
    exposure = {}
    m.record_click_exposure(exposure, 'https://news.test/a', _item(rel=71), 'news', 2, '2026-11-23')
    clicks = [
        {'at': '2026-11-24T09:00:00.000Z', 'u': 'https://news.test/a', 'c': 'feed:news', 'd': '2026-11-23'},
        {'at': '2026-11-24T09:01:00.000Z', 'u': 'https://news.test/gone', 'c': 'feed:news', 'd': '2026-11-23'},
        {'at': '2026-11-24T09:02:00.000Z', 'u': 'https://news.test/a', 'c': 'World', 'd': '2026-11-23'},
    ]
    monkeypatch.setattr(m.requests, 'get', lambda *a, **k: _Reply({'clicks': clicks, 'more': False}))
    assert m.fetch_digest_clicks(str(tmp_path), exposure=exposure) == 3
    rows = json.loads((tmp_path / '2026-11.json').read_text())
    by_url_cat = {(r['url'], r['category']): r for r in rows}
    joined = by_url_cat[('https://news.test/a', 'feed:news')]['article']
    assert (joined['source'], joined['relevance_band'], joined['best_pos']) == ('Outlet', 3, 2)
    assert 'article' not in by_url_cat[('https://news.test/gone', 'feed:news')], 'aged out: kept, unjoined'
    assert 'article' not in by_url_cat[('https://news.test/a', 'World')], 'a digest click is not a feed click'


def test_the_ledger_is_read_from_the_clicks_directory_when_none_is_passed(tmp_path, monkeypatch):
    _on(monkeypatch)
    exposure = {}
    m.record_click_exposure(exposure, 'https://news.test/a', _item(), 'news', 0, '2026-11-23')
    m.save_click_exposure(exposure, '2026-11-24', str(tmp_path / 'exposure.json'))
    click = {'at': '2026-11-24T09:00:00.000Z', 'u': 'https://news.test/a', 'c': 'feed:news', 'd': '2026-11-23'}
    monkeypatch.setattr(m.requests, 'get', lambda *a, **k: _Reply({'clicks': [click], 'more': False}))
    assert m.fetch_digest_clicks(str(tmp_path)) == 1
    assert json.loads((tmp_path / '2026-11.json').read_text())[0]['article']['source'] == 'Outlet'


def test_the_ledger_file_is_not_mistaken_for_a_month_of_clicks_or_for_ratings(tmp_path):
    (tmp_path / 'clicks').mkdir()
    (tmp_path / 'clicks' / 'exposure.json').write_text('{}')
    assert audit.load_digest_clicks(tmp_path / 'clicks') == []
    assert audit.load_ratings(tmp_path) == []


def test_feed_clicks_stay_out_of_the_digest_click_through():
    assert audit.FEED_CLICK_PREFIX == m.CLICK_FEED_PREFIX
    runs = [{'timestamp': '2026-11-23T08:10:00', 'kite_coverage': {
        'digest_by_label': {'World': 2}, 'digest_by_host': {'cbc.ca': 2}}}]
    feed_only = [{'at': '2026-11-23T09:00:00Z', 'url': 'https://www.cbc.ca/a', 'category': 'feed:news',
                  'digest_date': '2026-11-23'}]
    today = datetime(2026, 11, 24).date()
    assert audit.digest_clicks(runs, feed_only, today)['recorded'] is False
    mixed = feed_only + [{'at': '2026-11-23T09:05:00Z', 'url': 'https://www.cbc.ca/b', 'category': 'World',
                          'digest_date': '2026-11-23'}]
    got = audit.digest_clicks(runs, mixed, today)
    assert got['opened'] == 1 and [r['name'] for r in got['by_category'] if r['opened']] == ['World']
