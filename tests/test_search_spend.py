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
