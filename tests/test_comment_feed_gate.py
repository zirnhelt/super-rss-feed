"""Comment feeds must be rejected at discovery, not at the OPML gate.

The predicate has always been right and has always run too late. Three weeks
running (W36-W38 2026) `feed_discovery_report.json` recommended feeds like
"Comments for Homesteading Family" (70.1) and "Comments for Investing in
regenerative agriculture" (87.5). None reached `feeds.opml` — the gate in
`add_feeds_to_opml` held — but each one was fetched, Haiku-scored and written
into the report, where the weekly report read it back as a source that
"warrants evaluation for inclusion".

They score high for a structural reason no threshold can fix: a comment entry
is titled "Comment on <Article Title> by <Name>", so the scorer is rating the
host blog's headlines. The score is true about the blog and meaningless about
the feed.
"""
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from integrate_discoveries import is_comment_feed


def _candidate(url, title):
    c = types.SimpleNamespace()
    c.url = url
    c.title = title
    return c


class TestUrlMarkers:
    def test_wordpress_site_comment_feed(self):
        assert is_comment_feed('https://homesteadingfamily.com/comments/feed/', '')

    def test_query_string_form(self):
        assert is_comment_feed('https://example.com/?feed=comments-rss2', '')
        assert is_comment_feed('https://example.com/?feed=comments-atom', '')

    def test_blogger_comment_feed(self):
        """Kagi Small Web supplies blogspot feeds; Blogger's comment feed lives
        at /feeds/comments/default, which carries no 'comments/feed' marker."""
        assert is_comment_feed('http://astroblogger.blogspot.com/feeds/comments/default', '')


class TestTitleFallback:
    def test_feed_self_title(self):
        assert is_comment_feed('https://mariaadey.com/comments/feed/',
                               'Comments for The Road Goes Ever On')

    def test_per_post_comment_feed_has_no_url_marker(self):
        """WordPress serves a post's comment feed at <post-slug>/feed/ — the
        URL is indistinguishable from a site feed, so the title is the only
        tell."""
        assert is_comment_feed('https://homesteadingfamily.com/preservation-101-root-cellaring/feed/',
                               'Comments on: Preservation 101: Root Cellaring')


class TestArticleFeedsPass:
    def test_parent_feed_of_a_rejected_comment_feed(self):
        """The W37 run added mariaadey.com/feed/ while its comment feed was
        being recommended separately. Rejecting one must never cost the other."""
        assert not is_comment_feed('https://mariaadey.com/feed/', 'The Road Goes Ever On')

    def test_ordinary_feeds(self):
        assert not is_comment_feed('https://blog.cloudflare.com/rss/', 'The Cloudflare Blog')
        assert not is_comment_feed('https://hikebiketravel.com/feed/', 'Hike Bike Travel')

    def test_a_blog_about_commenting_is_not_a_comment_feed(self):
        """Substring matching on the word alone would cut these; the markers are
        path-anchored and the title check is an exact WordPress template prefix."""
        assert not is_comment_feed('https://example.com/feed/', 'Commentary on BC forestry')
        assert not is_comment_feed('https://commentarymagazine.com/feed/', 'Commentary Magazine')
        assert not is_comment_feed('https://example.com/feed/', 'Comments on Canadian forestry policy')


class TestDiscoveryChokePoint:
    def test_candidates_are_dropped_before_scoring(self):
        import feed_discovery
        candidates = [
            _candidate('https://homesteadingfamily.com/comments/feed/',
                       'Comments for Homesteading Family'),
            _candidate('https://hikebiketravel.com/feed/', 'Hike Bike Travel'),
        ]
        kept = [c for c in candidates
                if not feed_discovery.is_comment_feed(c.url, c.title)]
        assert [c.title for c in kept] == ['Hike Bike Travel']
