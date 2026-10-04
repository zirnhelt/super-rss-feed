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
