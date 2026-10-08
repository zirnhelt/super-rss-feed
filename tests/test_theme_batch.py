"""The ingest theme batch is submitted, polled and read back through the real SDK.

anthropic==0.40.0 has Message Batches only under `client.beta`. The pipeline
called `client.messages.batches`, which does not exist in that version, so every
submission fell through to synchronous scoring at full price and no batch was
ever polled. These drive the real client against a mock transport, so a call
to a missing attribute fails here rather than silently in the nightly run.
"""
import json
import sys
import types
from pathlib import Path

import anthropic
import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import super_rss_curator_json as m

SCHEDULE = {
    'enabled': True,
    'schedule': {
        'monday': {'label': 'Arts', 'scoring_prompt': 'Arts and culture.'},
        'tuesday': {'label': 'Working Lands', 'scoring_prompt': 'Farming and forestry.'},
    },
}

_BATCH = {
    'id': 'msgbatch_1', 'type': 'message_batch', 'created_at': '2026-10-08T00:00:00Z',
    'expires_at': '2026-10-09T00:00:00Z', 'ended_at': None, 'cancel_initiated_at': None,
    'archived_at': None, 'results_url': None,
    'request_counts': {'processing': 1, 'succeeded': 0, 'errored': 0,
                       'canceled': 0, 'expired': 0},
}


def _client(handler):
    real = anthropic.Anthropic
    return lambda api_key: real(api_key=api_key,
                                http_client=httpx.Client(transport=httpx.MockTransport(handler)))


def _isolate(monkeypatch, tmp_path):
    monkeypatch.setattr(m, 'PENDING_THEME_BATCH_FILE', str(tmp_path / 'pending.json'))
    monkeypatch.setattr(m, 'THEME_SCORE_CACHE_FILE', str(tmp_path / 'themes.json'))
    monkeypatch.setattr(m.cohere_integration, 'is_enabled', lambda: False)


def test_ingest_submits_one_batch_with_thinking_off(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    sent = []

    def handler(request):
        sent.append((request.method, request.url.path, json.loads(request.content)))
        return httpx.Response(200, json={**_BATCH, 'processing_status': 'in_progress'})

    monkeypatch.setattr(m.anthropic, 'Anthropic', _client(handler))
    articles = [types.SimpleNamespace(link='https://example.com/a', title='A barn raising',
                                      source='Example', description='')]

    m.score_all_themes_at_ingest(articles, SCHEDULE, 'test-key')

    assert [(meth, path) for meth, path, _ in sent] == [('POST', '/v1/messages/batches')]
    params = sent[0][2]['requests'][0]['params']
    assert params['model'] == 'claude-haiku-5-5'
    assert params['thinking'] == {'type': 'disabled'}
    pending = json.loads((tmp_path / 'pending.json').read_text())
    assert pending['batch_id'] == 'msgbatch_1'
    assert pending['article_batches'][0]['articles'][0]['link'] == 'https://example.com/a'


def test_a_finished_batch_is_read_back_into_the_theme_cache(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    m.save_pending_theme_batch({
        'batch_id': 'msgbatch_1',
        'article_batches': [{'custom_id': 'themes_0',
                             'articles': [{'link': 'https://example.com/a', 'title': 'A'}]}],
        'day_keys': ['monday', 'tuesday'],
        'schedule_labels': {'monday': 'Arts', 'tuesday': 'Working Lands'},
    })
    result_line = {
        'custom_id': 'themes_0',
        'result': {'type': 'succeeded', 'message': {
            'id': 'msg_1', 'type': 'message', 'role': 'assistant', 'model': 'claude-haiku-5-5',
            'content': [{'type': 'text', 'text': '[{"article": 1, "monday": 12, "tuesday": 81}]'}],
            'stop_reason': 'end_turn', 'stop_sequence': None,
            'usage': {'input_tokens': 10, 'output_tokens': 10}}},
    }

    def handler(request):
        if request.url.path.endswith('/results'):
            return httpx.Response(200, text=json.dumps(result_line) + '\n',
                                  headers={'content-type': 'application/binary'})
        return httpx.Response(200, json={
            **_BATCH, 'processing_status': 'ended', 'ended_at': '2026-10-08T01:00:00Z',
            'results_url': 'https://api.anthropic.com/v1/messages/batches/msgbatch_1/results'})

    monkeypatch.setattr(m.anthropic, 'Anthropic', _client(handler))

    m.process_pending_theme_batch('test-key')

    cache = m.load_theme_score_cache()
    assert cache['https://example.com/a:::Arts']['score'] == 12
    assert cache['https://example.com/a:::Working Lands']['score'] == 81
    assert m.load_pending_theme_batch() is None
