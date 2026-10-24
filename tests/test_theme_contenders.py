"""A day's highest unconfirmed theme scores are re-judged against its charter.

With Cohere on, pool theme scores are Rerank similarity to the first 400
characters of a charter, which never reach its exclusions. On 2026-10-23 a B.C.
election poll scored 56 for Wild Spaces and led the Friday feed. Targeted rescore
only lifted low scores, so a false high was never asked again.
"""
import json
import re
import sys
import types
from pathlib import Path

import anthropic
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import super_rss_curator_json as m

LABEL = 'Wild Spaces & Outdoor Life'
SCHEDULE = {'targeted_rescore': {'enabled': True, 'days': ['friday'], 'contender_band': 2}}


def _article(slug: str) -> types.SimpleNamespace:
    return types.SimpleNamespace(link=f'https://example.com/{slug}', title=slug, source='Example',
                                 description='')


def _isolate(monkeypatch, tmp_path, handler):
    monkeypatch.setattr(m, 'THEME_SCORE_CACHE_FILE', str(tmp_path / 'themes.json'))
    monkeypatch.setattr(m.cohere_integration, 'is_enabled', lambda: False)
    real = anthropic.Anthropic
    monkeypatch.setattr(m.anthropic, 'Anthropic', lambda api_key: real(
        api_key=api_key, max_retries=0, http_client=httpx.Client(transport=httpx.MockTransport(handler))))


def _charter(scores_by_title: dict, sent: list):
    """A mock Messages endpoint that scores each article in the prompt by title."""
    def handler(request):
        body = json.loads(request.content)
        titles = re.findall(r'Title: (\S+)', body['messages'][0]['content'])
        sent.extend(titles)
        reply = [{'article': i + 1, 'theme_score': scores_by_title[t]} for i, t in enumerate(titles)]
        return httpx.Response(200, json={
            'id': 'msg_1', 'type': 'message', 'role': 'assistant', 'model': 'claude-haiku-5-5',
            'content': [{'type': 'text', 'text': json.dumps(reply)}],
            'stop_reason': 'end_turn', 'stop_sequence': None,
            'usage': {'input_tokens': 10, 'output_tokens': 10},
        })
    return handler


def test_the_band_is_rejudged_and_stamped(monkeypatch, tmp_path):
    sent = []
    _isolate(monkeypatch, tmp_path, _charter({'poll': 4, 'burn': 81}, sent))
    poll, burn, quiet = _article('poll'), _article('burn'), _article('quiet')
    scored = [(quiet, 12), (poll, 56), (burn, 48)]

    out, confirmed = m.confirm_theme_contenders(scored, 'friday', 'charter', LABEL, 'key', SCHEDULE)

    assert sorted(sent) == ['burn', 'poll']
    assert confirmed == 2
    assert [(a.title, s) for a, s in out] == [('quiet', 12), ('poll', 4), ('burn', 81)]
    cache = m.load_theme_score_cache()
    assert cache[f'{poll.link}:::{LABEL}']['rescored'] is True


def test_a_confirmed_score_is_not_paid_for_twice(monkeypatch, tmp_path):
    sent = []
    _isolate(monkeypatch, tmp_path, _charter({'burn': 81, 'quiet': 9}, sent))
    poll, burn, quiet = _article('poll'), _article('burn'), _article('quiet')
    m.save_theme_score_cache({f'{poll.link}:::{LABEL}': {'score': 4, 'rescored': True}})

    m.confirm_theme_contenders([(poll, 4), (burn, 48), (quiet, 12)],
                               'friday', 'charter', LABEL, 'key', SCHEDULE)

    assert sorted(sent) == ['burn', 'quiet']


def test_a_failed_call_keeps_the_old_scores(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path, lambda request: httpx.Response(
        401, json={'type': 'error', 'error': {'type': 'authentication_error', 'message': 'no'}}))
    scored = [(_article('poll'), 56), (_article('burn'), 48)]

    out, confirmed = m.confirm_theme_contenders(scored, 'friday', 'charter', LABEL, 'key', SCHEDULE)

    assert confirmed == 0
    assert [s for _, s in out] == [56, 48]
    assert not any(v.get('rescored') for v in m.load_theme_score_cache().values())


def test_off_when_the_day_is_not_listed(monkeypatch, tmp_path):
    sent = []
    _isolate(monkeypatch, tmp_path, _charter({}, sent))
    scored = [(_article('poll'), 56)]

    out, confirmed = m.confirm_theme_contenders(scored, 'monday', 'charter', LABEL, 'key', SCHEDULE)

    assert (out, confirmed, sent) == (scored, 0, [])
