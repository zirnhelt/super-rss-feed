"""Two subjects the podcast does not do: an op-ed and a crime incident.

Every case below is a real headline from the 1,545-article pool cached on
2026-09-18. The first version of this filter cut 20 articles from that pool and
11 of them were wrong — a gaming monitor "for shooters", a Windows driver
deprecation "on trial", a Lone Butte woman's success in competitive shooting.
The three narrowing rules (category gate, title anchor, justice context) each
exist to remove one of those, so each is pinned here by the headline that
motivated it.

The filter is podcast-only on purpose: the general category feeds still carry
the local RCMP story, because "is this worth reading?" and "is this twenty-two
minutes of two hosts talking?" are different questions.
"""
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import super_rss_curator_json as m


def _article(title, description='', category='local', source='Example',
             content_type=None):
    a = types.SimpleNamespace()
    a.title = title
    a.description = description
    a.category = category
    a.source = source
    a.content_type = content_type
    return a


class TestCrimeIncidents:
    """Headlines the show should not be opening a segment with."""

    def test_stabbing_incident(self):
        assert m._is_general_crime_story(
            'Quesnel RCMP respond to stabbing incident', '', 'local')

    def test_homicide_investigation(self):
        assert m._is_general_crime_story(
            'Major Crime Unit investigating homicide after Fort St. James man dead',
            '', 'local')

    def test_manslaughter_plea(self):
        assert m._is_general_crime_story(
            "All 3 youth pleaded guilty to manslaughter in death of Penticton's "
            "Taig Savage", '', 'news')

    def test_drug_bust_trial(self):
        assert m._is_general_crime_story(
            'Accused in drug bust in Williams Lake to go to trial early next year',
            '', 'local')

    def test_assault_with_justice_context(self):
        """'assault' is ambiguous; 'RCMP investigating' is what settles it."""
        assert m._is_general_crime_story(
            'Prince George RCMP investigating axe assault; security guard injured',
            '', 'local')


class TestCrimeFalsePositives:
    """Each of these was cut by the first version of the filter."""

    def test_sport_shooting_is_not_a_shooting(self):
        assert not m._is_general_crime_story(
            'Lone Butte woman sees success in competitive shooting',
            'She placed second at the provincial championships.', 'local')

    def test_a_gaming_monitor_for_shooters(self):
        """The category gate: a crime word in an ai-tech story describes the
        technology's subject, not the story's."""
        assert not m._is_general_crime_story(
            'Sony Inzone M10S II is one of the best monitors for a shooter',
            '', 'ai-tech')

    def test_windows_drivers_on_trial(self):
        assert not m._is_general_crime_story(
            'Microsoft is putting your Windows drivers on trial this October',
            '', 'ai-tech')

    def test_ai_hallucinated_witnesses_in_a_murder_case(self):
        """An AI-in-the-courts story is exactly the show's beat."""
        assert not m._is_general_crime_story(
            'Lawyer fined $5K over AI-hallucinated witnesses in a murder case',
            '', 'ai-tech')

    def test_a_body_only_mention_is_not_the_subject(self):
        """The title anchor: CPJ and Amnesty pieces cite arrests in their body."""
        assert not m._is_general_crime_story(
            'Egypt must account for Sudanese journalist Ataf Mohamed Mokhtar',
            'He was arrested in Cairo and remains in custody.', 'news')

    def test_wildlife_act_sentencing_is_an_outdoors_story(self):
        assert not m._is_general_crime_story(
            'Two hunters sentenced for Wildlife Act violations near Quesnel',
            '', 'local')

    def test_ransomware_is_not_a_police_blotter_item(self):
        assert not m._is_general_crime_story(
            'Hospital network charged premium after ransomware attack',
            'The RCMP cybercrime unit is investigating.', 'news')

    def test_mmiwg_coverage_is_never_cut(self):
        """Indigenous Lands material whose subject is the system, not the incident."""
        assert not m._is_general_crime_story(
            'Families mark Red Dress Day for missing and murdered women',
            'RCMP data shows unsolved cases across the north.', 'local')

    def test_a_policing_budget_debate_is_civic_affairs(self):
        assert not m._is_general_crime_story(
            'Williams Lake city council debates RCMP detachment funding',
            'The policing budget rises 4 per cent.', 'local')

    def test_surveillance_tech_is_not_a_crime_story(self):
        assert not m._is_general_crime_story(
            'Trump backs Flock license plate cameras, but 47% of US public '
            'oppose them as 3 people are arrested', '', 'news')


class TestRefit20260923:
    """Two Quesnel court stories led the 2026-09-22 Working Lands roundup.

    Sentencing and jail phrasing were only ambiguous terms needing a justice word,
    and the Local Journalism Initiative byline matched the `journalism` exemption.
    Refit against 1,515 cached articles: 4 new catches, 0 false positives.
    """

    def test_sentencing_story_whose_only_justice_words_are_jail(self):
        assert m._is_general_crime_story(
            'Man sentenced in connection with serious incident outside a temporary '
            'shelter in Quesnel',
            'pleaded guilty to a charge of assault with a weapon ... and was sentenced '
            'to 88 days in jail and 18 months probation.', 'local')

    def test_jail_story_with_an_lji_byline(self):
        assert m._is_general_crime_story(
            "Quesnel man whose life 'was off the rails' spending another 88 days in jail",
            'By Bob Mackin, Local Journalism Initiative. Quesnel court room.', 'local')

    def test_guilty_plea(self):
        assert m._is_general_crime_story(
            'Maduro ally Alex Saab pleads guilty to money laundering, fraud', '', 'news')

    def test_press_freedom_reporting_is_still_exempt(self):
        assert not m._is_general_crime_story(
            'Journalist jailed for reporting on protests, press freedom groups say',
            '', 'news')

    def test_court_alone_is_context_not_an_incident(self):
        assert not m._is_general_crime_story(
            'City approves new pickleball court at Boitanio Park', '', 'local')


class TestFeedFilters:
    """Free checks in Article.should_filter, ahead of the paid gate. Every rule
    below drops only items the reader had already rated bad (1,659 ratings);
    the two positively rated homepages were votes for an outlet, not articles."""

    def _filtered(self, title, link):
        a = m.Article.__new__(m.Article)
        a.title, a.description, a.source, a.link = title, '', 'Example', link
        return a.should_filter()

    def test_homepage_is_not_an_article(self):
        assert self._filtered('Macleans.ca - Canada’s magazine', 'https://macleans.ca/')

    def test_wordpress_query_post_is_kept(self):
        assert not self._filtered('Community garden opens', 'https://example.com/?p=1234')

    def test_sports_section_url(self):
        assert self._filtered(
            'Kodiaks drop season opener to Raiders',
            'https://www.mycariboonow.com/315117/news/sports/kodiaks-drop-season-opener')

    def test_review_and_guide_title_shapes(self):
        assert self._filtered('Sennheiser Momentum 5 Wireless Headphones Review (2026)',
                              'https://www.wired.com/review/sennheiser-momentum-5/')
        assert self._filtered('Best Android Charger: Wireless, Portable, Cable (2026)',
                              'https://www.wired.com/story/best-android-charger/')
        assert self._filtered('Save $200 on This Lenovo Chromebook Plus',
                              'https://www.cnet.com/deals/lenovo-chromebook-plus-deal/')
        assert self._filtered('The 10 most rewarding day trips from Budapest',
                              'https://qz.com/most-rewarding-day-trips-budapest')

    def test_ordinary_article_passes(self):
        assert not self._filtered('Red Rock inspection station rebuild begins',
                                  'https://www.mycariboonow.com/316385/news/transport/red-rock')


class TestExclusionReasons:
    def test_opinion_is_excluded_by_content_type(self):
        a = _article('DOERKSON: Natural resource sector crumbling under NDP',
                     category='local', source='Williams Lake Tribune',
                     content_type='opinion')
        assert m.podcast_content_exclusion(a) == 'content_type:opinion'

    def test_the_trade_press_carve_out_survives(self):
        """news_interests.txt calls a Western Producer column on equipment
        subscriptions working-lands journalism, not a hot take. The exemption
        list is the seam between that judgment and 'the show avoids op-eds'."""
        a = _article('Subscription services have become a reality of modern ag',
                     category='homestead', source='Western Producer',
                     content_type='opinion')
        assert m.podcast_content_exclusion(a) is None

    def test_analysis_is_not_opinion(self):
        a = _article('What the softwood duty ruling changes for BC mills',
                     category='news', content_type='analysis')
        assert m.podcast_content_exclusion(a) is None

    def test_crime_reason_is_named_not_just_flagged(self):
        """A filter that removes articles silently is indistinguishable from a
        thin news day — the run has to be able to report what it cut."""
        a = _article('Quesnel RCMP respond to stabbing incident', category='local')
        assert m.podcast_content_exclusion(a) == 'crime_incident'

    def test_an_ordinary_story_passes(self):
        a = _article('Cariboo Regional District approves new library hours',
                     category='local', content_type='breaking')
        assert m.podcast_content_exclusion(a) is None


class TestWordBoundaries:
    def test_substrings_never_match(self):
        """The sibling repo filed a Highway 1 story under astrophysics because
        'star' is inside 'starting'. Same discipline here."""
        assert m._crime_hit_count('charleston chowder', ['charge']) == 0
        assert m._crime_hit_count('he was charged', ['charged']) == 1
