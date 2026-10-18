"""refresh_hot_feeds(): between nightlies, splice clear winners into the hot categories.

The nightly fetched at 04:00 UTC (9 PM Pacific), so the 2026-10-17 municipal
election results, out by 9 PM, waited a day; it now starts at 06:00 UTC. The
refresh judges only the delta since the nightly, with the quality gate alone, and
commits nothing: the next nightly supersedes whatever it placed.
"""
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import super_rss_curator_json as m

OPML = '''<?xml version="1.0"?><opml version="1.0"><body>
<outline type="rss" title="CBC Top" xmlUrl="https://cbc.example/rss" htmlUrl="https://cbc.example" />
</body></opml>'''

# title → (q_gate, gate_reject, gate_world); a title missing here is a gate outage.
VERDICTS = {
    'Williams Lake elects new mayor': (None, False, False),
    'Parliament passes housing bill': (72, False, False),
    'Earthquake strikes Japan coast': (40, False, True),
    'Local bakery opens second shop': (30, False, False),
    'Canucks win season opener': (70, True, False),
    'Ottawa announces budget date': (80, False, False),
}


def _rss(*titles: str) -> bytes:
    now = datetime.now(timezone.utc)
    items = ''.join(
        f'<item><title>{t}</title><link>https://cbc.example/{i}</link>'
        f'<pubDate>{format_datetime(now - timedelta(minutes=30 + i))}</pubDate>'
        f'<description>Story {i}.</description></item>'
        for i, t in enumerate(titles))
    return f'<?xml version="1.0"?><rss version="2.0"><channel><title>CBC</title>{items}</channel></rss>'.encode()


def _item(url: str, title: str, source: str = 'Tribune', hot: bool = False) -> dict:
    item = {'id': url, 'url': url, 'title': f'[{source}] {title}', 'content_html': '<p>Body.</p>',
            'date_published': (datetime.now(timezone.utc) - timedelta(hours=20)).isoformat(),
            'authors': [{'name': source, 'url': 'https://example.com'}]}
    if hot:
        item['_hot_refresh'] = True
    return item


def _fake_gate(articles, api_key) -> None:
    for a in articles:
        if a.title in VERDICTS:
            a.q_gate, a.gate_reject, a.gate_world = VERDICTS[a.title]


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('ANTHROPIC_API_KEY', 'test')
    monkeypatch.setitem(m.SYSTEM, 'hot_refresh', {
        'enabled': True, 'categories': ['local', 'news'], 'lookback_hours': 6,
        'min_score': 65, 'max_new_per_run': {'local': 5, 'news': 3}})
    monkeypatch.setattr(m, 'scrape_local_news', lambda: [])
    monkeypatch.setattr(m, 'batch_fetch_images', lambda arts, **kw: arts)
    monkeypatch.setattr(m, 'score_quality_gate', _fake_gate)
    monkeypatch.setattr(m, 'categorize_article', lambda title, desc: None)
    (tmp_path / 'feeds.opml').write_text(OPML, encoding='utf-8')
    for cat, items in {'local': [_item('https://t.example/1', 'Council meets')],
                       'news': [_item('https://n.example/1', 'Old news', 'CBC')]}.items():
        (tmp_path / f'feed-{cat}.json').write_text(json.dumps({'items': items}), encoding='utf-8')

    def serve(*titles: str) -> list:
        asked = []

        class _Resp:
            content = _rss(*titles)

            def raise_for_status(self) -> None:
                pass

        monkeypatch.setattr(m.requests, 'get', lambda url, **kw: asked.append(url) or _Resp())
        return asked
    return tmp_path, serve


def _ids(tmp_path, cat: str) -> list:
    return [i['id'] for i in json.loads((tmp_path / f'output/feed-{cat}.json').read_text())['items']]


def test_admits_local_world_and_top_band_news_only(env) -> None:
    tmp_path, serve = env
    serve(*VERDICTS)  # the six titles, at https://cbc.example/0..5

    written = m.refresh_hot_feeds(output_dir='output')

    assert sorted(written) == ['output/feed-local.json', 'output/feed-local.xml', 'output/feed-news.json']
    assert _ids(tmp_path, 'local')[:1] == ['https://cbc.example/0']           # Cariboo anchor
    news = _ids(tmp_path, 'news')
    assert news[:3] == ['https://cbc.example/1', 'https://cbc.example/2', 'https://cbc.example/5']
    assert 'https://cbc.example/3' not in news                                # below the bar
    assert 'https://cbc.example/4' not in news                                # gate reject
    items = json.loads((tmp_path / 'output/feed-news.json').read_text())['items']
    assert [i.get('_hot_refresh', False) for i in items] == [True, True, True, False]


def test_what_the_nightly_judged_or_placed_is_left_alone(env) -> None:
    tmp_path, serve = env
    serve('Parliament passes housing bill', 'Ottawa announces budget date')
    seen = m.Article({'title': 'x', 'link': 'https://cbc.example/0'}, 'CBC Top', '')
    (tmp_path / 'scored_articles_cache.json').write_text(
        json.dumps({seen.url_hash: {'q_gate': 72, 'timestamp': time.time()}}), encoding='utf-8')
    feed = json.loads((tmp_path / 'feed-news.json').read_text())
    feed['items'].append(_item('https://n.example/2', 'Ottawa announces budget date for spring', 'Globe'))
    (tmp_path / 'feed-news.json').write_text(json.dumps(feed), encoding='utf-8')

    assert m.refresh_hot_feeds(output_dir='output') == []


def test_gate_outage_holds_everything_for_the_nightly(env, monkeypatch) -> None:
    _, serve = env
    serve('Parliament passes housing bill')
    monkeypatch.setattr(m, 'score_quality_gate', lambda arts, key: None)
    assert m.refresh_hot_feeds(output_dir='output') == []


def test_disabled_fetches_nothing(env, monkeypatch) -> None:
    _, serve = env
    asked = serve('Parliament passes housing bill')
    monkeypatch.setitem(m.SYSTEM['hot_refresh'], 'enabled', False)
    assert m.refresh_hot_feeds(output_dir='output') == []
    assert asked == []


def test_cap_per_run(env, monkeypatch) -> None:
    tmp_path, serve = env
    serve('Parliament passes housing bill', 'Earthquake strikes Japan coast', 'Ottawa announces budget date')
    monkeypatch.setitem(m.SYSTEM['hot_refresh'], 'max_new_per_run', {'news': 1})
    m.refresh_hot_feeds(output_dir='output')
    assert _ids(tmp_path, 'news') == ['https://cbc.example/2', 'https://n.example/1']  # highest score wins


# --- The nightly supersedes a hot-refresh copy ---------------------------------

def test_hot_mark_survives_a_refresh_rewrite_but_not_a_nightly() -> None:
    hot = _item('https://cbc.example/1', 'Parliament passes housing bill', 'CBC', hot=True)
    assert m._article_from_feed_item(hot, keep_hot_mark=True).hot_refresh is True
    assert m._article_from_feed_item(hot).hot_refresh is False


def test_nightly_drops_a_hot_copy_it_filed_elsewhere() -> None:
    """Retained hot items are checked against every category's new articles, not just their own."""
    hot = _item('https://cbc.example/0', 'Williams Lake elects new mayor', 'CBC', hot=True)
    tonight = m.Article({'title': 'Williams Lake elects new mayor in tight race',
                         'link': 'https://wltribune.example/mayor'}, 'Williams Lake Tribune', '')
    assert m._retained_is_fresh(hot, set(), [])                            # nothing new in its own feed
    assert not m._retained_is_fresh(hot, {tonight.link}, [tonight.title_terms])
    assert not m._retained_is_fresh(hot, {'https://cbc.example/0'}, [])
