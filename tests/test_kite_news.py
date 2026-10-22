"""Kagi News (Kite) clusters enter as the finished version of their story.

A Kite story is already merged across outlets and summarised. Before this the
pipeline built it from an empty entry, so its title terms were empty and same-
story dedup never saw it; it linked `articles[0]`, which is regularly a foreign-
language page on a neighbouring story; and its summary carried raw "[domain#1]"
markers into the feeds.
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import super_rss_curator_json as m

CUTOFF = datetime.now(timezone.utc) - timedelta(hours=48)
RECENT = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat().replace('+00:00', 'Z')

STORY = {
    'title': 'Uganda targets 10,000 tractors in five-year mechanization push',
    'short_summary': (
        'Uganda plans to deploy 10,000 tractors over five years, Agriculture Minister '
        'Frank Tumwebaze told Parliament [agrifocusafrica.com#1]. Kubota is extending '
        'an orchard autonomy pilot [agdaily.com#1][northernag.net#1].'
    ),
    'talking_points': ['Existing capacity: 1,080 tractors since 2018 [agrifocusafrica.com#1].'],
    'unique_domains': 14,
    'articles': [
        {'link': 'https://agricolae.eu/macchine-agricole/', 'domain': 'agricolae.eu', 'date': RECENT},
        {'link': 'https://news.google.com/rss/articles/CBMi', 'domain': 'agrifocusafrica.com',
         'date': RECENT},
        {'link': 'https://agrifocusafrica.com/uganda-tractors/', 'domain': 'agrifocusafrica.com',
         'date': RECENT},
        {'link': 'https://www.agdaily.com/kubota/', 'domain': 'agdaily.com', 'date': RECENT},
    ],
}


def _kite(story: dict = STORY, category=None) -> 'm.Article':
    article = m._make_kite_article(story, category, CUTOFF)
    assert article is not None
    return article


def test_links_the_first_cited_outlet_not_articles_zero() -> None:
    article = _kite()
    assert article.link == 'https://agrifocusafrica.com/uganda-tractors/'
    assert article.source == 'agrifocusafrica.com'


def test_citations_are_stripped_from_the_feed_text_and_kept_in_the_body() -> None:
    article = _kite()
    assert '[' not in article.description and '#1' not in article.description
    assert '(agdaily.com, northernag.net)' in article.excerpt
    assert 'Existing capacity' in article.excerpt  # talking points ride in the body


def test_title_terms_are_built_so_dedup_can_see_the_story() -> None:
    assert len(_kite().title_terms) >= 3


def test_carries_cluster_size_and_provisional_category() -> None:
    article = _kite(category='news')
    assert article.kite_sources == 14
    assert article.category == 'news'


def test_stale_cluster_is_dropped() -> None:
    old = dict(STORY, articles=[dict(a, date='2020-01-01T00:00:00Z') for a in STORY['articles']])
    assert m._make_kite_article(old, None, CUTOFF) is None


def test_kite_cluster_beats_a_single_outlet_and_loses_to_local() -> None:
    kite = _kite()
    single = m.Article(m._AttrDict({'title': 'Some outlet', 'link': 'https://ex.com/a'}),
                       'Unlisted Outlet', 'https://ex.com')
    local = m.Article(m._AttrDict({'title': 'Local', 'link': 'https://ex.com/b'}),
                      'Unlisted Outlet', 'https://ex.com')
    local.category = 'local'
    assert m._source_priority(kite) < m._source_priority(single)
    assert m._source_priority(local) < m._source_priority(kite)


def test_kite_cluster_wins_same_story_dedup() -> None:
    kite = _kite()
    reprint = m.Article(
        m._AttrDict({'title': 'Uganda targets 10,000 tractors in five-year mechanization push',
                     'link': 'https://ex.com/uganda'}),
        'Unlisted Outlet', 'https://ex.com')
    kept = m.deduplicate_articles([reprint, kite])
    assert kept == [kite]


def test_podcast_feed_contract_carries_kite_sources() -> None:
    assert '_kite_sources' in m.PODCAST_FEED_CONTRACT['items']
