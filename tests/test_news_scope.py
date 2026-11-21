"""World news back in the reader's feed (2026-11-07).

Standing preferences get a scope: a `[show]` line keeps its subject off the podcast
and out of every feed but news. The Kagi News clusters no feed carried are counted
(run_stats.kite_coverage, read by the weekly audit) and the widely covered news ones
are listed in one digest item on top of the news feed.
"""
import json
import sys
import types
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import article_review_audit as audit
import config_loader
import super_rss_curator_json as m
from tests.test_gate_scrub_merge import _article, _install


# --- the scope tag -----------------------------------------------------------

def test_scope_tag_splits_the_file_and_is_stripped(tmp_path, monkeypatch):
    (tmp_path / 'standing_preferences.txt').write_text(
        '# comment\nHoroscopes: astrology. KEEP astronomy.\n'
        '[show] Warfare: wars anywhere.\n[SHOW]  US elections: races.\n', encoding='utf-8')
    monkeypatch.setattr(config_loader, 'CONFIG_DIR', tmp_path)
    assert config_loader.load_standing_preferences('everywhere') == ['Horoscopes: astrology. KEEP astronomy.']
    assert config_loader.load_standing_preferences('show') == ['Warfare: wars anywhere.', 'US elections: races.']
    assert len(config_loader.load_standing_preferences()) == 3


def test_show_lines_get_their_own_section_and_flag():
    rubric = m.build_gate_reject_rubric(['Horoscopes: astrology.'], ['Warfare: wars anywhere.'])
    show_at = rubric.index('--- SHOW-ONLY SUBJECTS ---')
    assert rubric.index('- Horoscopes: astrology.') < rubric.index('Apply the fluff rule') < show_at
    assert rubric.index('- Warfare: wars anywhere.') > show_at
    assert 'never sets "x" by itself' in rubric


def test_live_show_lines_sit_in_the_show_section_only():
    show = config_loader.load_standing_preferences('show')
    assert any(line.startswith('Warfare and military technology') for line in show)
    section = m.GATE_REJECT_RUBRIC[m.GATE_REJECT_RUBRIC.index('--- SHOW-ONLY SUBJECTS ---'):]
    head = m.GATE_REJECT_RUBRIC[:m.GATE_REJECT_RUBRIC.index('--- SHOW-ONLY SUBJECTS ---')]
    for line in show:
        assert f'- {line}' in section and f'- {line}' not in head
    assert '[show]' not in m.GATE_REJECT_RUBRIC


def test_gate_reads_and_caches_the_show_flag(monkeypatch, tmp_path):
    arts = [_article('Strike hits port as war widens'), _article('Forestry policy story')]
    client = _install(monkeypatch, tmp_path,
                      ['[{"a":1,"q":60,"x":0,"s":1,"w":1},{"a":2,"q":55,"x":0,"s":0,"w":0}]'])
    m.score_quality_gate(arts, 'test-key')
    assert '"s"' in client.calls[0]['messages'][0]['content']
    assert arts[0].gate_show_reject is True and arts[0].gate_reject is False
    assert arts[1].gate_show_reject is False

    again = _article('Strike hits port as war widens')
    m.score_quality_gate([again], 'test-key')
    assert len(client.calls) == 1 and again.gate_show_reject is True


# --- where the show flag bites --------------------------------------------------

def _judged(category, x=False, s=False):
    return types.SimpleNamespace(category=category, gate_reject=x, gate_show_reject=s)


def test_show_flag_drops_from_every_feed_but_news():
    assert not m._feed_rejects(_judged('news', s=True))
    assert m._feed_rejects(_judged('ai-tech', s=True))
    assert m._feed_rejects(_judged('news', x=True))
    assert not m._feed_rejects(_judged('news'))
    assert not m._feed_rejects(types.SimpleNamespace(category='news', gate_reject=None))


def test_the_show_never_gets_a_show_only_story():
    assert m._show_verdict(_judged('news', s=True)) is True
    assert m._show_verdict(_judged('news')) is False
    assert m._show_verdict(types.SimpleNamespace(gate_reject=None, gate_show_reject=True)) is None


def test_scrub_keeps_show_only_news_and_drops_it_elsewhere():
    news = _article('Ceasefire signed', category='news')
    tech = _article('Drone maker raises funds', category='ai-tech')
    for a in (news, tech):
        a.gate_reject, a.gate_show_reject, a.score = False, True, 50
    kept, stats = m.scrub_feed_with_haiku([news, tech], 'k')
    assert kept == [news]
    assert stats['show_only_kept'] == 1


def test_pool_rows_store_the_show_verdict(monkeypatch, tmp_path):
    path = tmp_path / 'pool.json'
    path.write_text('[]', encoding='utf-8')
    monkeypatch.setattr(m, 'PODCAST_CACHE_FILE', str(path))
    a = _article('Ceasefire signed', category='news')
    a.link = 'https://example.org/ceasefire'
    a.pub_date = datetime.now(timezone.utc)
    a.source_url = 'https://example.org'
    a.gate_reject, a.gate_show_reject = False, True
    m.save_podcast_cache([a])
    (row,) = json.loads(path.read_text())
    assert row['gate_reject'] is True, 'a [show] match must not reach the episode'


# --- Kagi News coverage and the digest ---------------------------------------------

def _kite(title, sources, label='World', feed='news', **verdict):
    a = _article(title, source='apnews.com', category=feed,
                 description=f'{title}. A summary sentence about it.')
    a.kite_sources, a.kite_label, a.kite_feed = sources, label, feed
    a.gate_reject = verdict.get('x', False)
    a.gate_show_reject = verdict.get('s', False)
    a.title_terms = m._term_set(title.lower())
    return a


def _published(title, link='https://outlet.example/x'):
    return types.SimpleNamespace(title=f'[Outlet] {title}', link=link)


def test_coverage_names_each_cluster_for_the_stage_that_dropped_it():
    shipped = _kite('Paraguay impeaches president over bank collapse', 80)
    by_outlet = _kite('Canada loses jobs as provincial rates diverge', 17, 'Canada')
    seen = _kite('Pope Leo arrives in Uruguay', 39)
    junk = _kite('Russell Brand faces new allegations', 21, x=True)
    war = _kite('Trump confirms limited Iran strike', 42, s=True, feed='ai-tech')
    cut = _kite('Stephen Miller named chief of staff', 64, 'USA')
    lost = _kite('Bomb threats spread across Europe', 72, 'Europe')
    kites = [shipped, by_outlet, seen, junk, war, cut, lost]
    published = [_published(shipped.title, shipped.link),
                 _published('Canada loses 4,700 jobs as provincial jobless rates diverge')]
    unique = {k.url_hash for k in kites if k is not lost}
    new = unique - {seen.url_hash}
    outcomes = dict((k.title, o) for k, o in m.kite_coverage(kites, published, unique, new))
    assert outcomes == {shipped.title: 'published', by_outlet.title: 'published',
                        seen.title: 'already_shown', junk.title: 'gate_reject',
                        war.title: 'show_only', cut.title: 'ranked_out', lost.title: 'dedup'}

    stats = m.kite_coverage_stats(list(zip(kites, outcomes.values())), 2)
    assert stats['headlines'] == 7 and stats['headline_missed'] == 4
    assert 'Stephen' not in json.dumps(stats), 'run_stats holds counts only'


def test_digest_lists_widely_covered_news_misses_best_first():
    cut = _kite('Stephen Miller named chief of staff', 64, 'USA')
    small = _kite('Toronto van attacker drops appeal', 3, 'Canada')
    tiny = _kite('Lotto Max jackpot split', 2, 'Canada')
    junk = _kite('Russell Brand faces new allegations', 21, x=True)
    tech = _kite('A cloud outage', 30, 'Technology', feed='ai-tech')
    shown = _kite('Paraguay impeaches president', 80)
    outcomes = [(small, 'ranked_out'), (cut, 'show_only'), (tiny, 'ranked_out'),
                (junk, 'gate_reject'), (tech, 'ranked_out'), (shown, 'published')]
    now = datetime(2026, 11, 7, 6, 0, tzinfo=timezone.utc)
    item = m.build_kite_digest(outcomes, now=now)
    html = item['content_html']
    assert item['id'] == 'https://news.kagi.com/#digest-2026-11-07'
    assert item['_stories'] == 2 and '2 stories' in item['title']
    assert html.index('Stephen Miller') < html.index('Toronto van')
    for absent in ('Lotto', 'Russell Brand', 'cloud outage', 'Paraguay'):
        assert absent not in html
    assert '64 outlets · USA' in html and 'Kagi News' in html
    assert item['url'].endswith('/' + m.DIGEST_PAGE), 'a tap opens the page of links, not Kagi'


def test_digest_page_lists_every_story_with_its_link(tmp_path):
    item = _digest_item()
    page = tmp_path / m.DIGEST_PAGE
    assert m.write_digest_page(item, str(page)) is True
    html = page.read_text(encoding='utf-8')
    assert 'Stephen Miller named chief of staff</a>' in html and '<a href="http' in html
    assert item['title'].split(',')[0] in html
    assert m.write_digest_page(None, str(tmp_path / 'none.html')) is False
    assert not (tmp_path / 'none.html').exists()


def test_digest_off_or_empty_is_none(monkeypatch):
    assert m.build_kite_digest([]) is None
    monkeypatch.setitem(m.SYSTEM, 'kagi_news', {'digest': {'enabled': False}})
    assert m.build_kite_digest([(_kite('Big story', 50), 'ranked_out')]) is None


def _digest_item():
    return m.build_kite_digest([(_kite('Stephen Miller named chief of staff', 64, 'USA'), 'ranked_out')],
                               now=datetime.now(timezone.utc))


def test_digest_is_written_verbatim_on_top_and_survives_a_splice(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    digest = _digest_item()
    story = {'id': 'https://cbc.example/1', 'url': 'https://cbc.example/1', 'title': '[CBC] Story',
             'content_html': '<p>Body.</p>',
             'date_published': (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
             'authors': [{'name': 'CBC', 'url': 'https://cbc.example'}]}
    m._write_spliced_feed('news', [digest, story], [], str(tmp_path))
    items = json.loads((tmp_path / 'feed-news.json').read_text())['items']
    assert items[0]['id'] == digest['id'] and items[0]['title'] == digest['title']
    assert items[0]['_digest'] is True and 'Score' not in items[0]['content_html']
    assert m._is_digest_item(items[0]) and not m._is_digest_item(items[1])


# --- the weekly audit ----------------------------------------------------------------

def test_audit_reads_the_week_of_headline_coverage():
    today = date(2026, 11, 8)
    runs = [{'timestamp': '2026-11-06T06:00:00+00:00',
             'kite_coverage': {'headline_by_outcome': {'published': 4, 'ranked_out': 10, 'show_only': 2}}},
            {'timestamp': '2026-11-07T06:00:00+00:00',
             'kite_coverage': {'headline_by_outcome': {'published': 2, 'already_shown': 2, 'gate_reject': 4}}},
            {'timestamp': '2026-10-20T06:00:00+00:00',
             'kite_coverage': {'headline_by_outcome': {'ranked_out': 99}}},
            {'timestamp': '2026-11-07T07:00:00+00:00'}]
    heads = audit.headline_coverage(runs, today)
    assert heads == {'runs': 2, 'headlines': 24, 'missed': 16, 'miss_pct': audit._pct(16, 24),
                     'by_outcome': {'published': 6, 'ranked_out': 10, 'show_only': 2,
                                    'already_shown': 2, 'gate_reject': 4}}
    findings = audit.blind_spots([], runs, today, {}, {}, [], [])
    assert any(f['id'] == 'headline-misses' for f in findings)
    assert any('Headline coverage' in line for line in audit._headline_lines(heads))


def test_digest_lists_one_telling_of_each_event():
    a = _kite('Trump appoints Stephen Miller chief of staff', 64, 'World')
    b = _kite("Miller's promotion puts immigration enforcement at center of fight", 40, 'USA')
    c = _kite('France prepares 70,000 officers for protests', 59, 'Europe')
    shared = frozenset(f'https://o{i}.example/miller' for i in range(10))
    a.kite_links = shared | {'https://a.example/1'}
    b.kite_links = shared | {'https://b.example/1'}
    c.kite_links = frozenset({'https://o1.example/france', 'https://o2.example/france'})
    item = m.build_kite_digest([(a, 'ranked_out'), (b, 'ranked_out'), (c, 'ranked_out')])
    assert item['_stories'] == 2 and 'center of fight' not in item['content_html']


def test_gate_rejects_are_not_pool_candidates_worth_theme_scoring():
    """The pool eligibility test reads _show_verdict: either flag keeps it out."""
    src = Path(m.__file__).read_text(encoding='utf-8')
    body = src[src.index('def _pool_eligible'):src.index('podcast_candidates = [a for a in scored_articles')]
    assert '_show_verdict(a)' in body


def test_fetch_keeps_one_cluster_per_event():
    shared = frozenset(f'https://o{i}.example/x' for i in range(8))
    world = _kite('Trump appoints Stephen Miller chief of staff', 49, 'World')
    usa = _kite("Miller's promotion puts immigration enforcement at center of fight", 62, 'USA')
    other = _kite('France prepares 70,000 officers for protests', 59, 'Europe')
    world.kite_links, usa.kite_links = shared, shared | {'https://u.example/1'}
    other.kite_links = frozenset({'https://f.example/1'})
    assert m._collapse_kite_events([world, usa, other]) == [usa, other]


# --- digest clicks (cloudflare/clicks in the podcast repo, approved 2026-11-20) ----------

CLICKS_BASE = 'https://cariboo-signals-clicks.example.workers.dev'


def _clicks_on(monkeypatch, key='test-key-0123456789abcdef0123456789'):
    monkeypatch.setitem(m.SYSTEM, 'clicks', {'base_url': CLICKS_BASE + '/'})
    monkeypatch.setenv('CLICKS_KEY', key)


def test_click_signature_matches_the_worker():
    # Computed by the Worker's own sign() (cloudflare/clicks/src/index.ts). A change on
    # either side makes every digest link a 400, so both must move together.
    assert m._click_signature('test-key-0123456789abcdef0123456789', 'https://www.cbc.ca/news/a?b=1&c=2',
                              'Canada | British Columbia', '2026-11-20') == 'ee046b42a6069e52601a1d9c110b2bfe'


def test_digest_links_go_through_the_click_worker_only_when_configured(tmp_path, monkeypatch):
    from urllib.parse import parse_qs, urlparse
    story = _kite('Stephen Miller named chief of staff', 64, 'USA')
    now = datetime(2026, 11, 20, 8, 0, tzinfo=timezone.utc)
    plain = m.build_kite_digest([(story, 'ranked_out')], now=now)
    assert f'href="{story.link}"' in plain['content_html'], 'no Worker configured: the story itself'

    monkeypatch.setitem(m.SYSTEM, 'clicks', {'base_url': CLICKS_BASE})
    monkeypatch.delenv('CLICKS_KEY', raising=False)
    assert f'href="{story.link}"' in m.build_kite_digest([(story, 'ranked_out')], now=now)['content_html'], \
        'a URL without the key stays plain: an unsigned link would be a 400'

    _clicks_on(monkeypatch)
    item = m.build_kite_digest([(story, 'ranked_out')], now=now)
    href = item['content_html'].split('<li>', 1)[1].split('href="', 1)[1].split('"')[0].replace('&amp;', '&')
    assert href.startswith(CLICKS_BASE + '/go?')
    q = {k: v[0] for k, v in parse_qs(urlparse(href).query).items()}
    assert (q['u'], q['c'], q['d']) == (story.link, 'USA', '2026-11-20')
    assert q['s'] == m._click_signature('test-key-0123456789abcdef0123456789', story.link, 'USA', '2026-11-20')
    assert item['_listed'] == [('USA', 'example.com')]

    page = tmp_path / m.DIGEST_PAGE
    m.write_digest_page({k: v for k, v in item.items() if k != '_listed'}, str(page))
    assert CLICKS_BASE + '/go?u=' in page.read_text(encoding='utf-8'), 'the page keeps the Worker link'


def test_click_key_ignores_whitespace_pasted_with_it(monkeypatch):
    # The deploy strips whitespace before giving the key to the Worker; so must the nightly.
    _clicks_on(monkeypatch, key='test-key-0123456789abcdef0123456789\r\n')
    assert m._clicks_config() == (CLICKS_BASE, 'test-key-0123456789abcdef0123456789')


def test_digest_href_falls_back_to_the_story_when_the_worker_would_refuse_it():
    key, day = 'k' * 32, '2026-11-20'
    assert m._digest_href('http://insecure.example/a', 'World', day, CLICKS_BASE, key) == 'http://insecure.example/a'
    long_url = 'https://example.com/' + 'a' * m.CLICKS_MAX_URL_CHARS
    assert m._digest_href(long_url, 'World', day, CLICKS_BASE, key) == long_url
    href = m._digest_href('https://example.com/x', 'C' * 120, day, CLICKS_BASE, key)
    assert 'c=' + 'C' * m.CLICKS_MAX_CATEGORY_CHARS + '&' in href, 'signed as the Worker trims it'


def test_coverage_stats_count_what_the_digest_listed():
    story = _kite('Stephen Miller named chief of staff', 64, 'USA')
    stats = m.kite_coverage_stats([(story, 'ranked_out')], 1,
                                  [('USA', 'apnews.com'), ('World', 'apnews.com')])
    assert stats['digest_by_label'] == {'USA': 1, 'World': 1}
    assert stats['digest_by_host'] == {'apnews.com': 2}
    assert m.kite_coverage_stats([], 0)['digest_by_label'] == {}


class _Reply:
    def __init__(self, body, status=200):
        self.body, self.status_code = body, status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f'HTTP {self.status_code}')

    def json(self):
        return self.body


def _click(at, url='https://www.cbc.ca/a', c='World', d='2026-11-19'):
    return {'at': at, 'u': url, 'c': c, 'd': d}


def test_fetch_digest_clicks_saves_new_clicks_by_month_from_the_last_one_saved(tmp_path, monkeypatch):
    _clicks_on(monkeypatch)
    clicks_dir = tmp_path / 'clicks'
    clicks_dir.mkdir()
    (clicks_dir / '2026-10.json').write_text(json.dumps(
        [{'at': '2026-10-31T23:00:00.000Z', 'url': 'https://x.example/old', 'category': 'USA',
          'digest_date': '2026-10-31'}]))
    calls = []
    pages = [{'clicks': [_click('2026-10-31T23:00:00.000Z'), _click('2026-10-31T23:30:00.000Z')], 'more': True},
             {'clicks': [_click('2026-11-19T09:00:00.000Z', c='Canada')], 'more': False}]

    def fake_get(url, params=None, headers=None, timeout=None):
        calls.append((url, dict(params or {}), headers))
        return _Reply(pages[len(calls) - 1])

    monkeypatch.setattr(m.requests, 'get', fake_get)
    assert m.fetch_digest_clicks(str(clicks_dir)) == 2, 'the click already saved is not new'
    assert calls[0][0] == CLICKS_BASE + '/clicks'
    assert calls[0][1] == {'since': '2026-10-31T23:00:00.000Z'}
    assert calls[1][1] == {'since': '2026-10-31T23:30:00.000Z'}, 'the next page starts after the last row'
    assert calls[0][2] == {'Authorization': 'Bearer test-key-0123456789abcdef0123456789'}
    october = json.loads((clicks_dir / '2026-10.json').read_text())
    november = json.loads((clicks_dir / '2026-11.json').read_text())
    assert [r['at'] for r in october] == ['2026-10-31T23:00:00.000Z', '2026-10-31T23:30:00.000Z']
    assert november == [{'at': '2026-11-19T09:00:00.000Z', 'url': 'https://www.cbc.ca/a',
                         'category': 'Canada', 'digest_date': '2026-11-19'}]


def test_fetch_digest_clicks_never_fails_the_run_and_is_off_unconfigured(tmp_path, monkeypatch):
    clicks_dir = tmp_path / 'clicks'

    def boom(*a, **k):
        raise AssertionError('no call without a Worker')

    monkeypatch.setattr(m.requests, 'get', boom)
    monkeypatch.delenv('CLICKS_KEY', raising=False)
    assert m.fetch_digest_clicks(str(clicks_dir)) == 0
    _clicks_on(monkeypatch)
    monkeypatch.setattr(m.requests, 'get', lambda *a, **k: _Reply({}, status=401))
    assert m.fetch_digest_clicks(str(clicks_dir)) == 0
    assert not clicks_dir.exists(), 'a failed read writes nothing'


def test_click_files_are_not_ratings(tmp_path):
    (tmp_path / 'clicks').mkdir()
    (tmp_path / 'clicks' / '2026-11.json').write_text(json.dumps([{'at': '2026-11-19T09:00:00Z'}]))
    assert audit.load_ratings(tmp_path) == []


def test_audit_reports_digest_click_through_by_category_and_outlet(tmp_path):
    today = date(2026, 11, 22)
    runs = [{'timestamp': '2026-11-19T08:10:00', 'kite_coverage': {
                'digest_by_label': {'World': 3, 'Canada': 2}, 'digest_by_host': {'cbc.ca': 2, 'apnews.com': 3}}},
            {'timestamp': '2026-11-01T08:10:00', 'kite_coverage': {'digest_by_label': {'World': 9}}}]
    (tmp_path / '2026-11.json').write_text(json.dumps([
        {'at': '2026-11-19T09:00:00Z', 'url': 'https://www.cbc.ca/a', 'category': 'Canada', 'digest_date': '2026-11-19'},
        {'at': '2026-11-19T09:05:00Z', 'url': 'https://www.cbc.ca/a', 'category': 'Canada', 'digest_date': '2026-11-19'},
        {'at': '2026-11-02T09:00:00Z', 'url': 'https://old.example/b', 'category': 'World', 'digest_date': '2026-11-02'},
    ]))
    clicks = audit.digest_clicks(runs, audit.load_digest_clicks(tmp_path), today)
    assert (clicks['listed'], clicks['opened']) == (5, 1), 'last 7 days only; a story opened twice counts once'
    assert clicks['by_category'][0] == {'name': 'Canada', 'listed': 2, 'opened': 1, 'pct': 50.0}
    assert clicks['by_host'][0]['name'] == 'cbc.ca'
    report = '\n'.join(audit._digest_click_lines(clicks))
    assert 'You opened 1 of the 5 stories' in report and '| cbc.ca | 2 | 1 |' in report
    assert audit._digest_click_lines(audit.digest_clicks(runs, [], today)) == [], \
        'no clicks recorded is not a finding'
