"""Local article text is the story, not the site's chrome.

Kagi Extract returns a whole Black Press page as markdown: logo images and the
nav menu come first, so the WLT summaries read "Site Logo Site Logo - News -
Regional News - ..." and replaced the scraper's real dek. Listing cards also
put a "1 MIN READ" badge where the dek goes.
"""
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import super_rss_curator_json as m

BLACK_PRESS_PAGE = """\
![Site Logo](https://wltribune.com/logo.svg)
![Site Logo](https://wltribune.com/logo-dark.svg)

- [News](https://wltribune.com/news)
- [Regional News](https://wltribune.com/news/regional-news)
  - [Election](https://wltribune.com/election)
- [Wildfires](https://wltribune.com/wildfires)

# Multiple SAR teams locate missing person after overnight search east of Quesnel

1 MIN READ

The rescue took place on Sunday, Oct. 4 and it involved Prince George, \
[Central Cariboo](https://example.com/ccsar) and Quesnel SARs.

Searchers worked through the night in steep terrain before the person was found \
cold but uninjured early Monday morning.

- [Submit Letter to the Editor](https://wltribune.com/letters)
- [Public Notices](https://wltribune.com/notices)
"""


def test_markdown_body_drops_chrome() -> None:
    text = m._markdown_body_text(BLACK_PRESS_PAGE)
    assert text.startswith('The rescue took place on Sunday, Oct. 4')
    assert 'Central Cariboo and Quesnel SARs.' in text
    assert 'cold but uninjured' in text
    for chrome in ('Site Logo', 'Regional News', 'MIN READ', 'Public Notices', '](', '#'):
        assert chrome not in text


def test_markdown_body_of_nav_only_page_is_empty() -> None:
    nav = '\n'.join(f'- [Section {i}](https://example.com/{i})' for i in range(40))
    assert m._markdown_body_text(nav) == ''
    assert m._markdown_body_text('') == ''


def _wlt_article(description: str) -> m.Article:
    article = m.Article({'title': 'Multiple SAR teams locate missing person',
                         'link': 'https://wltribune.com/2026/10/07/sar/',
                         'description': description},
                        'Williams Lake Tribune', 'https://wltribune.com')
    article.summary = m._clean_text(description, max_chars=300)
    article.excerpt = m._clean_text(description, max_chars=600)
    return article


def _run_enrich(article: m.Article, markdown: str) -> None:
    response = mock.Mock()
    response.json.return_value = {'data': [{'markdown': markdown}]}
    with mock.patch.object(m.requests, 'post', return_value=response), \
            mock.patch.object(m._extract_cache, 'load', return_value={}), \
            mock.patch.object(m._extract_cache, 'save'):
        m._kagi_enrich_articles([article], 'key')


def test_kagi_enrich_uses_story_text() -> None:
    article = _wlt_article('')
    _run_enrich(article, BLACK_PRESS_PAGE)
    assert article.summary.startswith('The rescue took place')
    assert 'Site Logo' not in article.excerpt


def test_kagi_enrich_keeps_dek_when_page_is_chrome() -> None:
    dek = ('The rescue took place on Sunday, Oct. 4 and it involved Prince George, '
           'Central Cariboo and Quesnel SARs')
    article = _wlt_article(dek)
    nav = '\n'.join(f'- [Section {i}](https://example.com/{i})' for i in range(40))
    _run_enrich(article, nav)
    assert article.summary == dek


def test_read_time_badge_is_not_a_description() -> None:
    for badge in ('1 MIN READ', '4 min read', '2 minutes read'):
        assert m._READ_TIME_RE.match(badge)
    assert not m._READ_TIME_RE.match('Read 1 min about the election')


def _card(href: str, title: str) -> str:
    return (f'<div class="article-card"><a class="article-card__link" href="{href}">'
            f'<h3 class="article-card__headline">{title}</h3></a>'
            f'<div class="article-card__details">{"A Williams Lake story. " * 10}</div></div>')


def test_every_configured_paper_is_scraped_under_its_own_name(tmp_path, monkeypatch):
    pages = {
        'https://wltribune.com/': _card('/2026/10/10/council/', 'Council meets'),
        'https://quesnelobserver.com/': (_card('https://quesnelobserver.com/2026/10/10/bridge/', 'Bridge reopens')
                                         + _card('https://ads.example/x', 'Sponsored')),
        'https://100milefreepress.net/': _card('https://www.100milefreepress.net/2026/10/10/fair/', 'Job fair'),
    }

    def fake_get(url, **kwargs):
        resp = mock.Mock(text=pages[url])
        resp.raise_for_status = mock.Mock()
        return resp

    monkeypatch.setattr(m, 'LOCAL_SCRAPES', m.SYSTEM['local_scrapes'])
    monkeypatch.setattr(m, '_wlt_cache', m.Cache(str(tmp_path / 'wlt_cache.json'), ttl_hours=48))
    monkeypatch.setattr(m.requests, 'get', fake_get)

    scraped = {a['link']: a['source'] for a in m.scrape_local_news()}

    assert scraped == {
        'https://wltribune.com/2026/10/10/council/': 'Williams Lake Tribune',
        'https://quesnelobserver.com/2026/10/10/bridge/': 'Quesnel Cariboo Observer',
        'https://www.100milefreepress.net/2026/10/10/fair/': '100 Mile Free Press',
    }


def test_one_paper_down_does_not_stop_the_others(tmp_path, monkeypatch):
    def fake_get(url, **kwargs):
        if 'quesnel' in url:
            raise m.requests.exceptions.ConnectionError('down')
        resp = mock.Mock(text=_card('/2026/10/10/a/', 'Story'))
        resp.raise_for_status = mock.Mock()
        return resp

    monkeypatch.setattr(m, 'LOCAL_SCRAPES', m.SYSTEM['local_scrapes'])
    monkeypatch.setattr(m, '_wlt_cache', m.Cache(str(tmp_path / 'wlt_cache.json'), ttl_hours=48))
    monkeypatch.setattr(m.requests, 'get', fake_get)

    assert {a['source'] for a in m.scrape_local_news()} == {'Williams Lake Tribune', '100 Mile Free Press'}


_NOW = m.datetime(2026, 10, 13, 4, 3, tzinfo=m.timezone.utc)


def _scraped(source: str, host: str, path: str, title: str, description: str = '') -> dict:
    return {'source': source, 'link': f'https://{host}{path}', 'title': title, 'description': description}


def test_network_card_on_two_homepages_is_dropped() -> None:
    goat = '/2026/10/12/cliffhanger-b-c-firefighters-offer-helping-hoof-to-stranded-goat/'
    cards = [
        _scraped('Quesnel Cariboo Observer', 'quesnelobserver.com', goat, 'Cliffhanger: B.C. firefighters offer helping hoof'),
        _scraped('100 Mile Free Press', '100milefreepress.net', goat, 'Cliffhanger: B.C. firefighters offer helping hoof'),
        _scraped('100 Mile Free Press', '100milefreepress.net', '/2026/10/10/curling/',
                 '100 Mile House Curling Club grows'),
    ]
    assert [c['title'] for c in m._drop_network_cards(cards, now=_NOW)] == ['100 Mile House Curling Club grows']


def test_shared_card_that_names_a_cariboo_place_is_kept() -> None:
    path = '/2026/10/12/free-transit-on-election-day/'
    cards = [
        _scraped('Williams Lake Tribune', 'wltribune.com', path, 'Free transit on election day',
                 'Residents in Quesnel and Williams Lake ride free'),
        _scraped('Quesnel Cariboo Observer', 'quesnelobserver.com', path, 'Free transit on election day',
                 'Residents in Quesnel and Williams Lake ride free'),
    ]
    assert len(m._drop_network_cards(cards, now=_NOW)) == 2


def test_stale_card_on_one_homepage_is_dropped_unless_local() -> None:
    cards = [
        _scraped('Williams Lake Tribune', 'wltribune.com', '/2026/09/17/boaters-rescue-bear-cub/',
                 'Boaters rescue bear cub from middle of Okanagan Lake'),
        _scraped('Williams Lake Tribune', 'wltribune.com', '/2026/09/17/horsefly-river-salmon/',
                 'Horsefly River salmon count'),
        _scraped('Williams Lake Tribune', 'wltribune.com', '/2026/10/12/mp-endorses-candidate/',
                 'MP Todd Doherty endorses Lorne Doerkson for Premier'),
    ]
    kept = [c['title'] for c in m._drop_network_cards(cards, now=_NOW)]
    assert kept == ['Horsefly River salmon count', 'MP Todd Doherty endorses Lorne Doerkson for Premier']


STORY = ('The rescue took place on Sunday, Oct. 4 and it involved Prince George, '
         'Central Cariboo and Quesnel SARs. ') * 30


def _extract(articles, data, cache=None):
    """Run the enrichment against one canned Extract reply; return (post mock, saved cache)."""
    response = mock.Mock()
    response.json.return_value = {'data': data}
    cache = {} if cache is None else cache
    with mock.patch.object(m.requests, 'post', return_value=response) as post, \
            mock.patch.object(m._extract_cache, 'load', return_value=cache), \
            mock.patch.object(m._extract_cache, 'save') as save:
        m._kagi_enrich_articles(articles, 'key')
    return post, (save.call_args[0][0] if save.called else None)


def _thin(n: int, scheme: str = 'https') -> m.Article:
    return m.Article({'title': f'Story {n}', 'link': f'{scheme}://wltribune.com/{n}/',
                      'description': ''}, 'Williams Lake Tribune', 'https://wltribune.com')


def test_extract_batches_pages_and_matches_by_url() -> None:
    articles = [_thin(1), _thin(2), _thin(3, scheme='http')]
    data = [{'url': 'https://wltribune.com/3/', 'markdown': STORY},
            {'url': 'https://wltribune.com/1/', 'error': 'No data returned from crawlers!'},
            {'url': 'https://wltribune.com/2/', 'markdown': STORY}]
    post, saved = _extract(articles, data)
    assert post.call_count == 1
    sent = [p['url'] for p in post.call_args.kwargs['json']['pages']]
    assert sent == ['https://wltribune.com/1/', 'https://wltribune.com/2/', 'https://wltribune.com/3/']
    assert articles[0].excerpt == ''
    assert articles[1].excerpt.startswith('The rescue') and articles[2].excerpt.startswith('The rescue')
    # The podcast reads `_excerpt` as its body: keep the long text, not 600 chars.
    assert len(articles[1].excerpt) > 600 and len(articles[1].description) <= 600
    # A per-page error is retried next run, not cached as empty.
    assert articles[0].url_hash not in saved and articles[1].url_hash in saved


def test_local_article_with_a_description_is_not_sent() -> None:
    article = _wlt_article('A real dek from the scraper. ' * 10)
    post, _ = _extract([article], [])
    post.assert_not_called()


def test_cached_extract_is_reapplied_without_a_call() -> None:
    article = _thin(1)
    post, _ = _extract([article], [], cache={article.url_hash: {'text': STORY, 'timestamp': 9e9}})
    post.assert_not_called()
    assert article.summary.startswith('The rescue')
