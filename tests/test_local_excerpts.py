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
