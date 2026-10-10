"""Editorial-exempt sources skip story-overlap dedup; URL dedup still applies.

The Cariboo Signals episode review is templated ("Episode Review — Cariboo
Signals, September 29, 2026"), so each day's title had the same term set as
the last one and the cross-run check suppressed every review after the first.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import super_rss_curator_json as m

REVIEWS = 'Cariboo Signals Reviews'


def _article(title: str, source: str, link: str) -> m.Article:
    return m.Article({'title': title, 'link': link}, source, 'https://example.com')


def _review(day: int) -> m.Article:
    return _article(
        f'Episode Review — Cariboo Signals, September {day}, 2026', REVIEWS,
        f'https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-09-{day}.html')


def test_reviews_source_is_exempt() -> None:
    assert REVIEWS in m.EDITORIAL_EXEMPT_SOURCES
    assert m._story_dedup_exempt(REVIEWS)
    assert not m._story_dedup_exempt('Williams Lake Tribune')


def test_cross_run_does_not_suppress_next_review() -> None:
    stored = [_review(26).title_terms]
    assert not m._is_cross_run_story_dupe(_review(29), stored)


def test_cross_run_still_suppresses_ordinary_sources() -> None:
    a = _article('Williams Lake council approves new water treatment plant', 'Tribune', 'https://a.example/1')
    b = _article('Council approves Williams Lake water treatment plant', 'Observer', 'https://b.example/2')
    assert m._is_cross_run_story_dupe(b, [a.title_terms])


def test_in_run_keeps_every_review_but_not_url_repeats() -> None:
    kept = m.deduplicate_articles([_review(28), _review(29), _review(29)])
    assert [a.link for a in kept] == [_review(28).link, _review(29).link]


def test_review_does_not_knock_out_a_news_story() -> None:
    news = _article('Episode review of Cariboo Signals podcast, September 2026', 'Tribune', 'https://a.example/3')
    kept = m.deduplicate_articles([_review(29), news])
    assert {a.source for a in kept} == {REVIEWS, 'Tribune'}


def test_aggregator_entries_are_attributed_to_their_origin_site() -> None:
    """Kagi Small Web is a listing: the byline is the linked site, not Kagi."""
    listed = _article('A post', 'Kagi Small Web', 'https://www.blog.example/posts/1')
    assert listed.source == 'blog.example'
    assert listed.source_url == 'https://www.blog.example'
    # The prescore gate and per-source cap stay keyed on the feed title.
    assert listed.listing_source == 'Kagi Small Web'
    direct = _article('A post', 'Vox', 'https://www.vox.com/a')
    assert direct.source == 'Vox'


# --- Same-morning refresh ----------------------------------------------------
# The review publishes at ~10:05 UTC, six hours after the nightly run, so it used
# to reach feed-local a day late. refresh_editorial_feeds() splices it in once it
# is live, with no API call and no category decision of its own.

REVIEW_FEED_URL = 'https://zirnhelt.github.io/curated-podcast-generator/episode-reviews.xml'
OPML = f'''<?xml version="1.0"?><opml version="1.0"><body>
<outline type="rss" title="{REVIEWS}" xmlUrl="{REVIEW_FEED_URL}" htmlUrl="https://zirnhelt.github.io/curated-podcast-generator" />
<outline type="rss" title="Williams Lake Tribune" xmlUrl="https://wltribune.example/feed" htmlUrl="https://wltribune.example" />
</body></opml>'''


def _review_url(day: int) -> str:
    return f'https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-{day:02d}.html'


def _rss(*days: int) -> bytes:
    from datetime import datetime, timedelta, timezone
    from email.utils import format_datetime
    now = datetime.now(timezone.utc)
    items = ''.join(
        f'<item><title>Episode Review — Cariboo Signals, October {d}, 2026</title>'
        f'<link>{_review_url(d)}</link><pubDate>{format_datetime(now - timedelta(hours=i))}</pubDate>'
        f'<description>&lt;p&gt;What the pipeline did.&lt;/p&gt;</description></item>'
        for i, d in enumerate(days))
    return f'<?xml version="1.0"?><rss version="2.0"><channel><title>Reviews</title>{items}</channel></rss>'.encode()


def _item(url: str, source: str, title: str, hours_ago: int = 20) -> dict:
    from datetime import datetime, timedelta, timezone
    return {'id': url, 'url': url, 'title': f'[{source}] {title}', 'content_html': '<p>Body.</p>',
            'date_published': (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).isoformat(),
            'authors': [{'name': source, 'url': 'https://example.com'}]}


def _setup(tmp_path, monkeypatch, feeds: dict, body: bytes) -> list:
    import json

    class _Resp:
        content = body

        def raise_for_status(self) -> None:
            pass

    asked = []
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'feeds.opml').write_text(OPML, encoding='utf-8')
    for cat, items in feeds.items():
        (tmp_path / f'feed-{cat}.json').write_text(json.dumps({'items': items}), encoding='utf-8')
    monkeypatch.setattr(m.requests, 'get', lambda url, **kw: asked.append(url) or _Resp())
    return asked


def test_refresh_splices_a_new_review_into_the_feed_that_carries_reviews(tmp_path, monkeypatch) -> None:
    import json
    local = [_item(_review_url(9), REVIEWS, 'Episode Review — Cariboo Signals, October 9, 2026', 24),
             _item('https://wltribune.example/a', 'Williams Lake Tribune', 'Council meets', 20)]
    asked = _setup(tmp_path, monkeypatch, {'local': local, 'news': [_item('https://n.example/1', 'CBC', 'News')]},
                   _rss(10, 9))

    written = m.refresh_editorial_feeds(output_dir='output')

    assert asked == [REVIEW_FEED_URL]                     # only the editorial source is fetched
    assert sorted(written) == ['output/feed-local.json', 'output/feed-local.xml']
    items = json.loads((tmp_path / 'output/feed-local.json').read_text())['items']
    assert [i['id'] for i in items] == [_review_url(10), 'https://wltribune.example/a', _review_url(9)]
    assert items[0]['title'] == f'[{REVIEWS}] Episode Review — Cariboo Signals, October 10, 2026'
    assert not (tmp_path / 'output/feed-news.json').exists()


def test_refresh_is_a_no_op_once_the_review_is_in(tmp_path, monkeypatch) -> None:
    local = [_item(_review_url(10), REVIEWS, 'Episode Review — Cariboo Signals, October 10, 2026', 1)]
    _setup(tmp_path, monkeypatch, {'local': local}, _rss(10))
    assert m.refresh_editorial_feeds(output_dir='output') == []


def test_refresh_never_places_a_source_the_nightly_has_not(tmp_path, monkeypatch) -> None:
    """No feed carries reviews yet: the category is the nightly's call, not this pass's."""
    _setup(tmp_path, monkeypatch, {'local': [_item('https://wltribune.example/a', 'Williams Lake Tribune', 'x')]},
           _rss(10))
    assert m.refresh_editorial_feeds(output_dir='output') == []
