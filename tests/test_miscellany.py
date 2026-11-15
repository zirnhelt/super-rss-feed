"""Niche interests ship in a Miscellany feed instead of taking regular slots.

To 2026-11-13 the reader rated Dezeen 6 bad / 5 interesting ("Niche but fun",
then "No local hook" three days running), Architizer 2 bad ("Too niche") and the
PyTorch and Dark Reading posts "Too niche". Their outlets are typed `niche`: not
demoted, but routed to their own small feed, and tagged for the podcast's weekly
niche closer.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

import super_rss_curator_json as m

NICHE = ('Dezeen', 'Architizer', 'PyTorch', 'darkreading.com', 'Pitchfork', 'Stereogum')


def _a(source, category, score=50, q_gate=50):
    return SimpleNamespace(source=source, category=category, score=score, q_gate=q_gate,
                           title=f'{source} story {score}')


def test_the_niche_outlets_are_typed_niche_and_not_demoted():
    prefs = m.SOURCE_PREFS
    assert all(prefs['source_map'][s] == 'niche' for s in NICHE)
    assert prefs['source_types']['niche']['score_adjustment'] == 0
    assert prefs['source_map']['ArchDaily'] == 'project_showcase', 'unchanged'


def test_a_niche_outlet_ships_in_miscellany_whatever_its_category():
    assert m.reader_category(_a('Dezeen', 'design')) == 'miscellany'
    assert m.reader_category(_a('PyTorch', 'ai-tech')) == 'miscellany'
    assert m.reader_category(_a('Dezeen', 'news')) == 'miscellany'
    assert m.reader_category(_a('Dezeen', 'local')) == 'local', 'a local story stays local'
    assert m.reader_category(_a('Hackaday', 'homelab')) == 'homelab'
    assert m.reader_category(_a('Hackaday', None)) == 'news'


def test_miscellany_has_its_own_small_allocation(monkeypatch):
    monkeypatch.setattr(m, 'FEED_SLOTS', {'design': {'min_slots': 1, 'max_slots': 2},
                                          'miscellany': {'min_slots': 1, 'max_slots': 3},
                                          'default': {'min_slots': 1, 'max_slots': 5}})
    monkeypatch.setattr(m, 'LIMITS', dict(m.LIMITS, min_claude_score=25,
                                          min_score_by_category={'design': 12}))
    monkeypatch.setattr(m, 'WILDCARD_MIN_Q_GATE', 101)
    dezeen = [_a('Dezeen', 'design', s) for s in (90, 80, 70, 60)]
    design = [_a('Small Dwellings', 'design', s) for s in (40, 30)]
    out = m.apply_feed_slot_allocation(dezeen + design)
    assert sorted(a.score for a in out if a.source == 'Dezeen') == [70, 80, 90]
    assert sorted(a.score for a in out if a.source != 'Dezeen') == [30, 40], \
        'Dezeen no longer takes the Design slots'


def test_the_category_guide_never_offers_miscellany_to_the_model():
    src = Path(m.__file__).read_text()
    assert src.count("if cat_data.get('source_routed'):") == 2
    assert m.CATEGORIES['miscellany'].get('source_routed') is True
    assert 'miscellany' not in m.CATEGORY_RULES, 'no keyword may file a story there'


def test_the_feed_is_declared_and_slotted():
    assert 'miscellany' in m.FEEDS_CONFIG['feeds']
    assert m.FEED_SLOTS['miscellany']['max_slots'] == 3


def test_podcast_items_carry_the_niche_tag():
    assert '_niche' in m.PODCAST_FEED_CONTRACT['items']
    tree = ast.parse(Path(m.__file__).read_text())
    writer = next(n for n in tree.body
                  if isinstance(n, ast.FunctionDef) and n.name == 'generate_podcast_feed')
    assert 'is_niche_source(article.source)' in ast.unparse(writer)


def test_the_nightly_keeps_the_feed_but_never_bootstraps_it():
    """At 1-3 items a night the feed stays under the bootstrap check's 20 for a week,
    and --bootstrap-feeds re-scores the pool: it spends."""
    wf = (Path(m.__file__).parent / '.github' / 'workflows' / 'generate-feed.yml').read_text()
    loops = [line for line in wf.splitlines() if line.strip().startswith('for feed in local ')]
    assert len(loops) == 2
    download, bootstrap = loops
    assert 'miscellany' in download and 'miscellany' not in bootstrap
