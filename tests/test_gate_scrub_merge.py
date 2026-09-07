"""The quality gate now returns the topical reject verdict alongside the score.

These cover the merge itself: one call producing both answers, the local-bypass
rule that must survive it, and the fail-open behavior the old separate scrub had.
"""
import json
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import super_rss_curator_json as m


class _FakeResponse:
    def __init__(self, text):
        self.content = [types.SimpleNamespace(text=text)]
        self.usage = types.SimpleNamespace(
            input_tokens=10, output_tokens=10,
            cache_creation_input_tokens=0, cache_read_input_tokens=0)


class _FakeClient:
    """Records the requests made so the tests can assert on call count."""
    def __init__(self, payloads):
        self._payloads = list(payloads)
        self.calls = []
        self.messages = types.SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return _FakeResponse(self._payloads.pop(0))


def _article(title, source='Example', category=None, description=''):
    a = m.Article.__new__(m.Article)
    a.title = title
    a.description = description
    a.source = source
    a.category = category
    a.link = f'https://example.com/{abs(hash(title))}'
    a.url_hash = f'h{abs(hash(title))}'
    a.score = 0
    a.quality = 0
    a.relevance = 0
    a.local = 0
    a.q_gate = None
    a.gate_reject = None
    a.gate_scored = False
    return a


def _install(monkeypatch, tmp_path, payloads):
    """Point the score cache at a tmp file and hand the gate a fake client."""
    monkeypatch.setattr(m, '_scored_cache', m.Cache(str(tmp_path / 'scored.json'), ttl_hours=48))
    client = _FakeClient(payloads)
    monkeypatch.setattr(m.anthropic, 'Anthropic', lambda **kw: client)
    return client


def test_gate_returns_score_and_verdict_in_one_call(monkeypatch, tmp_path):
    arts = [_article('A real story about forestry policy'),
            _article('Canucks lose 4-2 in overtime thriller')]
    client = _install(monkeypatch, tmp_path,
                      ['[{"a":1,"q":62,"x":0},{"a":2,"q":18,"x":1}]'])

    m.score_quality_gate(arts, 'test-key')

    assert len(client.calls) == 1, 'the merge exists to make exactly one call'
    assert arts[0].q_gate == 62 and arts[0].gate_reject is False
    assert arts[1].q_gate == 18 and arts[1].gate_reject is True


def test_local_articles_bypass_the_score_but_not_the_verdict(monkeypatch, tmp_path):
    """'local' never exempted sports coverage and the merge must not smuggle that in."""
    art = _article('Williams Lake Stampeders win the junior final', category='local')
    _install(monkeypatch, tmp_path, ['[{"a":1,"q":40,"x":1}]'])

    m.score_quality_gate([art], 'test-key')

    assert art.q_gate is None, 'local priority rules own local eligibility'
    assert art.gate_reject is True


def test_api_failure_fails_open(monkeypatch, tmp_path):
    art = _article('Something that never got judged')
    monkeypatch.setattr(m, '_scored_cache', m.Cache(str(tmp_path / 'scored.json'), ttl_hours=48))

    class _Boom:
        def __init__(self):
            self.messages = types.SimpleNamespace(
                create=lambda **kw: (_ for _ in ()).throw(RuntimeError('down')))
    monkeypatch.setattr(m.anthropic, 'Anthropic', lambda **kw: _Boom())

    m.score_quality_gate([art], 'test-key')

    assert art.q_gate is None and art.gate_reject is None


def test_verdict_is_cached_and_not_re_asked(monkeypatch, tmp_path):
    art = _article('A story worth caching')
    client = _install(monkeypatch, tmp_path, ['[{"a":1,"q":55,"x":0}]'])
    m.score_quality_gate([art], 'test-key')
    assert len(client.calls) == 1

    again = _article('A story worth caching')
    again.url_hash = art.url_hash
    m.score_quality_gate([again], 'test-key')
    assert len(client.calls) == 1, 'a cached verdict must not cost a second call'
    assert again.q_gate == 55 and again.gate_reject is False


def test_scrub_partitions_on_the_gate_verdict_without_calling_claude(monkeypatch):
    keep, drop = _article('Keeper'), _article('Dropper')
    keep.gate_reject = False
    drop.gate_reject = True
    monkeypatch.setattr(m.cohere_integration, 'is_enabled', lambda: False)

    def _explode(**kw):
        raise AssertionError('the scrub must not make an API call any more')
    monkeypatch.setattr(m.anthropic, 'Anthropic', _explode)

    kept, stats = m.scrub_feed_with_haiku([keep, drop], 'test-key')

    assert [a.title for a in kept] == ['Keeper']
    assert sum(stats['haiku_removed_by_category'].values()) == 1


def test_unjudged_articles_are_kept(monkeypatch):
    """A pre-merge cache entry carries q_gate but no verdict; it must not be dropped."""
    a = _article('Judged by nothing')
    assert a.gate_reject is None
    monkeypatch.setattr(m.cohere_integration, 'is_enabled', lambda: False)

    kept, stats = m.scrub_feed_with_haiku([a], 'test-key')

    assert kept == [a]
    assert stats['unjudged'] == 1


def test_gated_scoring_composes_with_the_scrub_and_the_allocator(monkeypatch, tmp_path):
    """End-to-end over the three stages this change touched: one gate call
    produces both answers, the scrub partitions on them, the allocator selects."""
    arts = [_article(f'Serious story number {i}') for i in range(4)]
    arts.append(_article('Oilers trade deadline roundup'))

    verdicts = [{"a": i + 1, "q": 70 - i * 5, "x": 0} for i in range(4)]
    verdicts.append({"a": 5, "q": 30, "x": 1})
    client = _install(monkeypatch, tmp_path, [json.dumps(verdicts)])
    monkeypatch.setattr(m.cohere_integration, 'is_enabled', lambda: False)
    # keep the run local: no deep-scoring call
    monkeypatch.setattr(m, 'score_articles_with_claude_pure', lambda deep, key: deep)
    monkeypatch.setattr(m, 'FEED_SLOTS', {'news': {'min_slots': 2, 'max_slots': 3},
                                          'default': {'min_slots': 1, 'max_slots': 5}})
    monkeypatch.setattr(m, 'LIMITS', dict(m.LIMITS, quality_gate={'gate_floor': 25, 'batch_size': 30},
                                          min_claude_score=25, min_score_by_category={'news': 20}))

    m.score_articles_gated(arts, 'test-key', {})
    assert len(client.calls) == 1, 'the gate is the only call in this path'

    kept, stats = m.scrub_feed_with_haiku(arts, 'test-key')
    assert 'Oilers trade deadline roundup' not in [a.title for a in kept]

    for a in kept:
        a.category = 'news'
    selected = m.apply_feed_slot_allocation(kept)
    assert len(selected) == 3, 'max_slots caps the category'
    assert selected[0].score >= selected[-1].score, 'filled best-first'
