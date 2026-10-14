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

import pytest

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


class TestCrimeRefit20261013:
    """Two Quesnel stories the reader rated bad that aired in September. Against
    the 4,706 unique live pool and bank items the five added keywords add one hit,
    the RCMP story below, and no false positives."""

    def test_faces_multiple_charges(self):
        a = _article('Man faces multiple charges after allegedly ramming police cars in Quesnel',
                     'RCMP say the suspect was arrested.', category='local')
        assert m.podcast_content_exclusion(a) == 'crime_incident'

    def test_loaded_firearms_and_drugs(self):
        a = _article('RCMP recover loaded firearms and drugs in separate Quesnel incidents',
                     'Quesnel RCMP seized the items.', category='local')
        assert m.podcast_content_exclusion(a) == 'crime_incident'

    def test_the_firearms_phrases_still_need_justice_context(self):
        """'faces/facing/multiple charges' carry their own context ('charges' is a
        justice-context term, as with the existing 'charges laid'). The two firearms
        phrases do not: loaded firearms in a hunting-safety story are not a blotter item."""
        a = _article('Hunting course warns about loaded firearms in trucks',
                     'A safety course for new hunters in the Cariboo.', category='local')
        assert m.podcast_content_exclusion(a) is None
        b = _article('Hunting course warns about loaded firearms in trucks',
                     'RCMP will attend the safety course.', category='local')
        assert m.podcast_content_exclusion(b) == 'crime_incident'


class TestCrimeRefitReview20261013:
    """Shapes the corpus scan missed. Each cut a story the show wants."""

    def test_a_candidate_who_faces_charges_is_an_election_story(self):
        a = _article('Williams Lake mayoral candidate faces multiple charges',
                     'The candidate says the charges will not affect the campaign. RCMP confirmed them.',
                     category='local')
        assert m.podcast_content_exclusion(a) is None

    def test_a_regulatory_prosecution_is_working_lands_material(self):
        a = _article('Company faces multiple charges under the Fisheries Act',
                     'Crown counsel laid the charges after a spill on a Cariboo river.',
                     category='news')
        assert m.podcast_content_exclusion(a) is None

    def test_a_search_and_rescue_story_is_emergency_operations(self):
        a = _article('Multiple SAR teams locate missing person east of Quesnel',
                     'Quesnel Search and Rescue and RCMP found the hiker overnight.',
                     category='local')
        assert m.podcast_content_exclusion(a) is None

    def test_an_ordinary_blotter_item_is_still_cut(self):
        a = _article('Man faces multiple charges after allegedly ramming police cars in Quesnel',
                     'RCMP say the suspect was arrested.', category='local')
        assert m.podcast_content_exclusion(a) == 'crime_incident'


class TestGateRejectReachesTheShow:
    """2026-10-12: a Mother Jones piece the gate had rejected was a deep-dive source,
    the day after Mother Jones was blocked. The pool is captured before the scrub, and
    nothing in the pool step read gate_reject."""

    def test_a_reject_is_dropped_with_its_own_reason(self):
        a = _article('Stop the Steal Never Stopped', category='news', source='Mother Jones')
        a.gate_reject = True
        assert m.podcast_content_exclusion(a) == 'gate_reject'

    def test_no_verdict_and_a_pass_are_kept(self):
        """None is "the gate never ruled" (an API failure, or an entry cached before
        the verdict was stored). Fail open, as the gate does."""
        a = _article('Cariboo Regional District approves new library hours', category='local')
        assert m.podcast_content_exclusion(a) is None
        a.gate_reject = None
        assert m.podcast_content_exclusion(a) is None
        a.gate_reject = False
        assert m.podcast_content_exclusion(a) is None

    def test_a_reject_is_reported_ahead_of_other_reasons(self):
        a = _article('DOERKSON: Natural resource sector crumbling', category='local',
                     content_type='opinion')
        a.gate_reject = True
        assert m.podcast_content_exclusion(a) == 'gate_reject'

    def test_the_config_switch_turns_it_off(self, monkeypatch):
        monkeypatch.setattr(m, 'PODCAST_EXCLUDED_CONTENT',
                            {**m.PODCAST_EXCLUDED_CONTENT, 'gate_reject': False})
        a = _article('Cariboo Regional District approves new library hours', category='local')
        a.gate_reject = True
        assert m.podcast_content_exclusion(a) is None

    def test_enabled_false_turns_the_gate_rule_off_with_the_rest(self, monkeypatch):
        """The config comment says so; the bank and the review page's pool label used to
        keep acting on the verdict while the choke point had stopped."""
        monkeypatch.setitem(m.PODCAST_EXCLUDED_CONTENT, 'enabled', False)
        assert m._gate_reject_honoured() is False
        assert m.podcast_content_exclusion(_article('Story', category='news')) is None
        rejected = types.SimpleNamespace(link='https://x.test/r', gate_reject=True)
        assert m._in_show_pool(rejected, {'https://x.test/r'}) is True

    def test_a_reject_is_not_in_the_shows_pool_but_is_in_the_cache(self):
        rejected = types.SimpleNamespace(link='https://x.test/r', gate_reject=True)
        kept = types.SimpleNamespace(link='https://x.test/k', gate_reject=None)
        links = {'https://x.test/r', 'https://x.test/k'}
        assert m._in_show_pool(rejected, links) is False
        assert m._in_show_pool(kept, links) is True
        assert m._in_show_pool(kept, set()) is False

    def test_the_shipped_config_has_it_on(self):
        assert m.PODCAST_EXCLUDED_CONTENT.get('gate_reject') is True

    def test_cached_articles_read_the_verdict_back(self):
        """generate_podcast_feed() builds its articles from cache entries through an
        inner CachedArticle; a missing assignment there silently turns the rule off."""
        import ast
        tree = ast.parse(Path(m.__file__).read_text(encoding='utf-8'))
        func = next(n for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == 'generate_podcast_feed')
        cls = next(n for n in ast.walk(func)
                   if isinstance(n, ast.ClassDef) and n.name == 'CachedArticle')
        assigned = {t.attr: n.value for n in ast.walk(cls) if isinstance(n, ast.Assign)
                    for t in n.targets if isinstance(t, ast.Attribute)}
        assert {'gate_reject', 'content_type'} <= set(assigned)
        # Read from the entry, not set to a constant: `self.gate_reject = None` would
        # turn the rule off while still assigning the attribute.
        for field in ('gate_reject', 'content_type'):
            assert ast.unparse(assigned[field]) == f"data.get('{field}')", field


def _pool_article(link, gate_reject=None, source='Example', title='A story'):
    from datetime import datetime, timezone
    return types.SimpleNamespace(
        link=link, title=title, description='d', summary='s', excerpt='e',
        pub_date=datetime.now(timezone.utc), source=source, source_url='https://example.test',
        score=50, quality=50, relevance=50, local=0, q_gate=50, content_type='news',
        category='news', image=None, gate_reject=gate_reject)


class TestThePoolCarriesTheVerdict:
    @pytest.fixture(autouse=True)
    def _tmp_caches(self, tmp_path, monkeypatch):
        # The live caches are committed production data: never write them from a test.
        monkeypatch.setattr(m, 'PODCAST_CACHE_FILE', str(tmp_path / 'pool.json'))
        monkeypatch.setattr(m, 'THEME_HOLDOVER_FILE', str(tmp_path / 'bank.json'))

    def test_a_new_entry_stores_the_verdict(self):
        m.save_podcast_cache([_pool_article('https://x.test/a', gate_reject=True),
                              _pool_article('https://x.test/b', gate_reject=False),
                              _pool_article('https://x.test/c', gate_reject=None)],
                             main_feed_quality=False)
        by_link = {e['link']: e for e in m.load_podcast_cache()}
        assert by_link['https://x.test/a']['gate_reject'] is True
        assert by_link['https://x.test/b']['gate_reject'] is False
        assert by_link['https://x.test/c']['gate_reject'] is None

    def test_a_rejudged_article_updates_its_verdict(self):
        m.save_podcast_cache([_pool_article('https://x.test/a', gate_reject=True)], False)
        m.save_podcast_cache([_pool_article('https://x.test/a', gate_reject=False)], False)
        assert m.load_podcast_cache()[0]['gate_reject'] is False

    def test_a_missing_verdict_never_erases_one(self):
        m.save_podcast_cache([_pool_article('https://x.test/a', gate_reject=True)], False)
        m.save_podcast_cache([_pool_article('https://x.test/a', gate_reject=None)], True)
        assert m.load_podcast_cache()[0]['gate_reject'] is True

    def _bank(self, monkeypatch, items):
        url_days = {f"{i['link']}:::monday": 99 for i in items}
        saved = {}
        monkeypatch.setattr(m, 'load_theme_score_cache', lambda: {})
        monkeypatch.setattr(m, 'normalize_theme_scores', lambda *a, **k: url_days)
        monkeypatch.setattr(m, 'load_theme_holdover_cache', lambda: {})
        monkeypatch.setattr(m, 'save_theme_holdover_cache', lambda h: saved.update(h))
        m.bank_articles_for_all_themes(
            items, {'schedule': {'monday': {'label': 'Arts', 'holdover_threshold': 10}},
                    'holdover_threshold': 30})
        return saved.get('monday', [])

    def test_the_bank_carries_content_type_and_the_verdict(self, monkeypatch):
        """None of the bank's 19,250 entries carried content_type, so a banked op-ed
        passed the opinion filter."""
        base = dict(title='t', description='d', pub_date='2026-10-12T00:00:00+00:00',
                    source='Example', source_url='u', score=50, category='news')
        banked = self._bank(monkeypatch, [
            dict(base, link='https://x.test/op', content_type='opinion', gate_reject=False)])
        assert banked[0]['content_type'] == 'opinion'
        assert banked[0]['gate_reject'] is False

    def test_a_gate_reject_is_not_banked(self, monkeypatch):
        base = dict(title='t', description='d', pub_date='2026-10-12T00:00:00+00:00',
                    source='Example', source_url='u', score=50, category='news')
        banked = self._bank(monkeypatch, [
            dict(base, link='https://x.test/no', gate_reject=True),
            dict(base, link='https://x.test/yes', gate_reject=None)])
        assert [b['link'] for b in banked] == ['https://x.test/yes']

    def _bank_into(self, monkeypatch, existing, items, honour=True):
        url_days = {f"{i['link']}:::monday": 99 for i in items}
        bank = {'monday': existing}
        saved = []
        monkeypatch.setattr(m, 'load_theme_score_cache', lambda: {})
        monkeypatch.setattr(m, 'normalize_theme_scores', lambda *a, **k: url_days)
        monkeypatch.setattr(m, 'load_theme_holdover_cache', lambda: bank)
        monkeypatch.setattr(m, 'save_theme_holdover_cache', lambda h: saved.append(True))
        monkeypatch.setattr(m, '_gate_reject_honoured', lambda: honour)
        m.bank_articles_for_all_themes(
            items, {'schedule': {'monday': {'label': 'Arts', 'holdover_threshold': 10}},
                    'holdover_threshold': 30})
        return bank['monday'], bool(saved)

    _BASE = dict(title='t', description='d', pub_date='2026-10-12T00:00:00+00:00',
                 source='Example', source_url='u', score=50, category='news')

    def test_a_banked_copy_takes_the_pools_latest_ruling(self, monkeypatch):
        """Banked with no verdict (or False), rejected later: the copy must follow, or the
        story comes back out of the bank when its pool entry ages out."""
        for stored in (None, False):
            existing = [dict(self._BASE, link='https://x.test/a', gate_reject=stored)]
            rows, saved = self._bank_into(monkeypatch, existing, [
                dict(self._BASE, link='https://x.test/a', gate_reject=True)])
            assert [r['link'] for r in rows] == ['https://x.test/a']
            assert rows[0]['gate_reject'] is True
            assert saved is True
            assert m.podcast_content_exclusion(types.SimpleNamespace(
                source='S', title='t', description='d', category='news',
                content_type=None, gate_reject=rows[0]['gate_reject'])) == 'gate_reject'

    def test_a_pass_clears_a_stale_reject_and_a_missing_ruling_erases_nothing(self, monkeypatch):
        existing = [dict(self._BASE, link='https://x.test/a', gate_reject=True)]
        rows, _ = self._bank_into(monkeypatch, existing, [
            dict(self._BASE, link='https://x.test/a', gate_reject=None)])
        assert rows[0]['gate_reject'] is True
        rows, _ = self._bank_into(monkeypatch, existing, [
            dict(self._BASE, link='https://x.test/a', gate_reject=False)])
        assert rows[0]['gate_reject'] is False

    def test_a_banked_copy_without_content_type_takes_the_pools(self, monkeypatch):
        existing = [dict(self._BASE, link='https://x.test/a')]
        rows, saved = self._bank_into(monkeypatch, existing, [
            dict(self._BASE, link='https://x.test/a', content_type='opinion')])
        assert rows[0]['content_type'] == 'opinion'
        assert saved is True

    def test_nothing_is_saved_when_nothing_changed(self, monkeypatch):
        existing = [dict(self._BASE, link='https://x.test/a', gate_reject=False, content_type='news')]
        _, saved = self._bank_into(monkeypatch, existing, [
            dict(self._BASE, link='https://x.test/a', gate_reject=False, content_type='news')])
        assert saved is False

    def test_a_reject_is_banked_when_the_verdict_is_switched_off(self, monkeypatch):
        rows, _ = self._bank_into(monkeypatch, [], [
            dict(self._BASE, link='https://x.test/no', gate_reject=True)], honour=False)
        assert [r['link'] for r in rows] == ['https://x.test/no']

    def test_the_per_theme_bank_writer_carries_the_same_fields(self, monkeypatch):
        from datetime import datetime, timezone
        bank = {}
        monkeypatch.setattr(m, 'load_theme_holdover_cache', lambda: bank)
        monkeypatch.setattr(m, 'save_theme_holdover_cache', lambda h: None)
        article = types.SimpleNamespace(
            link='https://x.test/h', title='t', description='d', pub_date=datetime.now(timezone.utc),
            source='S', source_url='u', score=50, category='news',
            content_type='opinion', gate_reject=False)
        m.update_theme_holdover('monday', 'Arts', [(article, 80)], 10)
        row = bank['monday'][0]
        assert row['content_type'] == 'opinion'
        assert row['gate_reject'] is False


class TestGateRejectLog:
    @pytest.fixture(autouse=True)
    def _fresh(self, monkeypatch):
        monkeypatch.setattr(m, '_GATE_REJECT_LOGGED', set())
        monkeypatch.setattr(m, '_GATE_REJECT_CAPPED', False)
        monkeypatch.setattr(m, 'GATE_REJECT_LOG_CAP', 3)

    @staticmethod
    def _a(i):
        return types.SimpleNamespace(link=f'https://x.test/{i}', source='S', title=f'Story {i}')

    def test_each_title_is_listed_once(self, capsys):
        for _ in range(3):
            m._log_gate_reject(self._a(1))
        assert capsys.readouterr().out.count('Story 1') == 1

    def test_the_cap_is_announced_once_not_silent(self, capsys):
        for i in range(8):
            m._log_gate_reject(self._a(i))
        out = capsys.readouterr().out
        assert out.count('gate_reject: [S]') == 3
        assert out.count('counted, not listed') == 1
        assert 'Story 3' not in out


class TestBlockedSourcesLeaveReusedArticles:
    """`blocked_sources` was only checked at fetch, so Mother Jones stayed in the pool,
    the holdover bank and the retained feed items for a week after the block."""

    def test_predicate_is_substring_and_case_insensitive(self):
        assert m.is_blocked_source('Mother Jones')
        assert m.is_blocked_source('motherjones.com')
        assert not m.is_blocked_source('Williams Lake Tribune')
        assert not m.is_blocked_source(None)

    def test_hn_no_longer_blocks_technica_or_technology_feeds(self):
        for source in ('Ars Technica Technology Lab', 'GN CleanTechnica',
                       'MIT Technology Review', 'MIT News STS'):
            assert not m.is_blocked_source(source), source
        assert m.is_blocked_source('Hacker News')

    def test_pool_refuses_blocked_and_show_excluded_sources(self):
        assert m._pool_source_excluded('Mother Jones')
        assert not m._pool_source_excluded('The Tyee')

    def test_pool_loader_evicts_a_blocked_source(self, tmp_path, monkeypatch):
        import json
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        rows = [{'link': 'https://motherjones.com/a', 'source': 'Mother Jones', 'pub_date': now},
                {'link': 'https://thetyee.ca/b', 'source': 'The Tyee', 'pub_date': now}]
        (tmp_path / 'podcast_articles_cache.json').write_text(json.dumps(rows))
        monkeypatch.chdir(tmp_path)
        assert [r['source'] for r in m.load_podcast_cache()] == ['The Tyee']

    def test_holdover_loader_evicts_a_blocked_source(self, tmp_path, monkeypatch):
        import json
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        bank = {'monday': [{'source': 'Mother Jones', 'banked_at': now},
                           {'source': 'The Tyee', 'banked_at': now}]}
        (tmp_path / 'theme_holdover_cache.json').write_text(json.dumps(bank))
        monkeypatch.chdir(tmp_path)
        assert [a['source'] for a in m.load_theme_holdover_cache()['monday']] == ['The Tyee']


class TestLocalNeedsACaribooAnchor:
    """The deep-score prompt filed "BC Interior" community news under local, so a Canal
    Flats mayoral profile shipped in feed-local. `local` is the Cariboo feed."""

    @staticmethod
    def _local(title, source, local_score=45, description=''):
        a = _article(title, description=description, category='local', source=source)
        a.quality, a.relevance, a.local = 40, 55, local_score
        a.score = 50
        return a

    def _adjusted(self, article):
        return m.apply_dimension_adjustments([article])[0].category

    def test_out_of_region_story_is_refiled_as_news(self):
        article = self._local('Canal Flats mayoral candidate prioritizes infrastructure',
                              'My East Kootenay Now')
        assert self._adjusted(article) == 'news'

    def test_high_local_score_keeps_local(self):
        assert self._adjusted(self._local('Council votes on arena', 'Tribune Wire', 85)) == 'local'

    def test_scraped_cariboo_paper_keeps_local(self):
        assert self._adjusted(self._local('MP endorses candidate', 'Williams Lake Tribune', 20)) == 'local'

    def test_place_in_description_or_source_keeps_local(self):
        assert self._adjusted(self._local('Fire hall opens', 'Example',
                                          description='HORSEFLY — the new hall')) == 'local'
        assert self._adjusted(self._local('Weekly roundup', 'My Cariboo Now')) == 'local'

    def test_non_local_category_is_untouched(self):
        article = self._local('Canal Flats mayoral candidate', 'My East Kootenay Now')
        article.category = 'news'
        assert self._adjusted(article) == 'news'



class TestCivicRacesOutsideTheCariboo:
    """A standing-preference line for this was tried on 2026-10-12 and rejected Cariboo
    "Meet the Candidates" profiles two nights running. The model cannot hold a place
    rule reliably; a keyword with a local override can."""

    @staticmethod
    def _filtered(title, source, summary='A profile.'):
        entry = {'title': title, 'link': 'https://example.com/2026/10/13/a-story/',
                 'summary': summary, 'description': summary}
        return m.Article(entry, source, 'https://example.com').should_filter()

    def test_out_of_region_races_are_filtered(self):
        for title, source in [
                ('Canal Flats mayoral candidate Mark Doherty prioritizes infrastructure',
                 'My East Kootenay Now'),
                ('Sparwood mayoral candidate Hadden Kelloway promises to reconnect community',
                 'My East Kootenay Now'),
                ('Winnipeg mayoral candidates using AI in campaign', 'Global News')]:
            assert self._filtered(title, source), title

    def test_cariboo_profiles_survive_by_place_in_text(self):
        assert not self._filtered(
            'Meet the Candidates: Mike Cave seeks council seat for City of Quesnel', 'Example')

    def test_cariboo_profiles_survive_by_outlet_name(self):
        assert not self._filtered(
            'MEET THE CANDIDATE: City council candidate Sheila Boehm', 'Williams Lake Tribune')
        assert not self._filtered('Councillor candidate Joe Smith on housing', 'My Cariboo Now')

    def test_province_wide_election_coverage_is_untouched(self):
        for title in ('B.C. Conservatives drop Victoria-Beacon Hill candidate over racist posts',
                      'B.C. election: Eby vows to fast-track int’l medical grads',
                      'Dene Nation establishes water council as leaders warn of tailings risk'):
            assert not self._filtered(title, 'The Tyee'), title
