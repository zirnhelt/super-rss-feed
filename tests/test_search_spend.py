"""Search spend must be visible and switchable.

The feed's Brave Search key is shared with the podcast. On 2026-09-23 the 45 topic
queries were ~47 Brave calls a night for 1 of 467 category-feed items, and the cost
tracker priced every one of those calls at $0.
"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import api_usage
import log_feed_results
import super_rss_curator_json as m


def test_disabled_topic_queries_make_no_request(monkeypatch, capsys):
    monkeypatch.setitem(m.SYSTEM, 'topic_queries', {'enabled': False})
    monkeypatch.setenv('BRAVE_API_KEY', 'test-key')

    def _no_request(*a, **k):
        raise AssertionError('topic query sent while disabled')
    monkeypatch.setattr(m.requests, 'get', _no_request)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
    assert m.fetch_topic_news(cutoff) == []
    assert 'Topic queries: disabled' in capsys.readouterr().out


def test_feed_log_says_disabled_rather_than_nothing():
    metrics = log_feed_results.parse_output(
        '  🔍 Topic queries: disabled (config/system.json topic_queries.enabled)\n')
    section = log_feed_results.format_run_section('manual', metrics)
    assert 'Topic queries: **disabled**' in section


def test_brave_calls_are_priced():
    assert api_usage.FLAT_COST_PER_CALL['brave'] > 0


def test_cache_writes_are_priced_at_the_one_hour_rate():
    """Every cache_control in the curator sets ttl=1h, which bills 2x input."""
    from types import SimpleNamespace
    api_usage.reset()
    api_usage.record_claude_usage(SimpleNamespace(
        input_tokens=0, output_tokens=0,
        cache_creation_input_tokens=1_000_000, cache_read_input_tokens=0))
    assert abs(api_usage.estimate_cost() - 2.00) < 1e-9
    api_usage.reset()


def test_calibration_call_disables_thinking(monkeypatch):
    """Sonnet 5 thinks when `thinking` is omitted, and the pinned SDK has no
    `thinking` kwarg, so it must reach the wire through extra_body."""
    import json

    import anthropic
    import httpx

    import calibration_agent

    sent = {}

    def handler(request: httpx.Request) -> httpx.Response:
        sent.update(json.loads(request.content))
        return httpx.Response(200, json={
            "id": "msg_1", "type": "message", "role": "assistant",
            "model": sent["model"], "stop_reason": "end_turn", "stop_sequence": None,
            "content": [{"type": "text", "text": '{"changes": []}'}],
            "usage": {"input_tokens": 10, "output_tokens": 5},
        })

    real_client = anthropic.Anthropic
    monkeypatch.setattr(calibration_agent.anthropic, "Anthropic", lambda api_key: real_client(
        api_key=api_key, http_client=httpx.Client(transport=httpx.MockTransport(handler))))

    result, error = calibration_agent.call_claude_with_memory("system", "user", "test-key")

    assert error is None and result == {"changes": []}
    assert sent["model"] == "claude-sonnet-5"
    assert sent["thinking"] == {"type": "disabled"}


def test_claude_cost_is_kept_by_stage_with_the_batch_discount():
    # The weekly audit sets each stage's cost beside how well its scores predict ratings.
    from types import SimpleNamespace
    api_usage.reset()
    api_usage.record_claude_usage(SimpleNamespace(input_tokens=1_000_000, output_tokens=0), stage='gate')
    api_usage.record_claude_usage(SimpleNamespace(input_tokens=1_000_000, output_tokens=0),
                                  batch=True, stage='theme_batch')
    api_usage.record_claude_usage(SimpleNamespace(input_tokens=0, output_tokens=0))
    by_stage = api_usage.get_summary_dict()['claude_by_stage']
    assert by_stage == {'gate': {'calls': 1, 'est_cost_usd': 1.0},
                        'other': {'calls': 1, 'est_cost_usd': 0.0},
                        'theme_batch': {'calls': 1, 'est_cost_usd': 0.5}}
    api_usage.reset()
    assert api_usage.get_summary_dict()['claude_by_stage'] == {}
