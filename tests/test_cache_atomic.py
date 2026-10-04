"""Cache and state files are replaced whole or not at all, and a corrupt one never stops a run.

CI commits these files after every run, so a write cut short used to commit a
truncated file that the loaders read back as empty: the history was gone and
nothing failed.
"""
import json
import os
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import cache
from cache import Cache, FeedHTTPCache, atomic_write_json, atomic_write_text


def _leftovers(directory: Path) -> list:
    return [p.name for p in directory.iterdir() if p.name.endswith('.tmp')]


# --- Loading what is already on disk -----------------------------------------

@pytest.mark.parametrize('content', [
    b'{"a": {"timestamp": 1',   # truncated mid-write
    b'',                        # zero-length
    b'\xff\xfe\x00garbage',     # not UTF-8
    b'[1, 2, 3]',               # valid JSON, wrong shape
    b'null',
])
def test_a_corrupt_cache_loads_empty_instead_of_raising(tmp_path, content, capsys):
    path = tmp_path / 'c.json'
    path.write_bytes(content)
    assert Cache(str(path), ttl_hours=48).load() == {}
    assert Cache(str(path)).load() == {}
    http = FeedHTTPCache(str(path))
    http.load()
    assert http.entry('https://feed.test') == {}
    assert 'starting empty' in capsys.readouterr().out


def test_a_missing_cache_is_empty_and_silent(tmp_path, capsys):
    assert Cache(str(tmp_path / 'nope.json'), ttl_hours=1).load() == {}
    assert capsys.readouterr().out == ''


def test_degraded_entries_expire_instead_of_crashing_the_ttl_filter(tmp_path):
    """Known gotcha: wlt_cache.json entries have degraded to bare strings before."""
    now = time.time()
    path = tmp_path / 'c.json'
    path.write_text(json.dumps({
        'fresh': {'timestamp': now},
        'stale': {'timestamp': now - 10 * 86400},
        'bare_string': 'https://wltribune.com/x',
        'string_stamp': {'timestamp': '2026-10-01'},
        'bool_stamp': {'timestamp': True},
        'null': None,
        'float_value': now,
    }))
    assert set(Cache(str(path), ttl_hours=48).load()) == {'fresh', 'float_value'}


def test_feed_http_cache_drops_non_dict_entries(tmp_path):
    path = tmp_path / 'h.json'
    path.write_text(json.dumps({
        'https://ok.test/feed': {'skip_until': time.time() + 3600},
        'https://bad.test/feed': 'junk',
    }))
    http = FeedHTTPCache(str(path))
    http.load()
    assert http.should_skip('https://ok.test/feed')
    assert not http.should_skip('https://bad.test/feed')


# --- Writing ------------------------------------------------------------------

def test_round_trip_keeps_unicode_and_leaves_no_temp_file(tmp_path):
    path = tmp_path / 's.json'
    atomic_write_json(str(path), {'title': 'Xatśūll — café'}, indent=2, ensure_ascii=False)
    assert json.loads(path.read_text(encoding='utf-8')) == {'title': 'Xatśūll — café'}
    assert _leftovers(tmp_path) == []


def test_a_value_that_cannot_serialize_never_touches_the_file(tmp_path):
    path = tmp_path / 's.json'
    path.write_text('{"keep": 1}')
    with pytest.raises(TypeError):
        atomic_write_json(str(path), {'bad': object()})
    assert json.loads(path.read_text()) == {'keep': 1}
    assert _leftovers(tmp_path) == []


@pytest.mark.parametrize('stage', ['fsync', 'replace'])
def test_a_write_that_dies_midway_keeps_the_old_file(tmp_path, monkeypatch, stage):
    path = tmp_path / 's.json'
    path.write_text('{"keep": 1}')

    def boom(*args, **kwargs):
        raise OSError(28, 'No space left on device')
    monkeypatch.setattr(cache.os, stage, boom)

    with pytest.raises(OSError):
        atomic_write_text(str(path), '{"new": 2}')
    assert json.loads(path.read_text()) == {'keep': 1}
    assert _leftovers(tmp_path) == []


def test_cache_save_failure_is_reported_and_the_previous_copy_survives(tmp_path, monkeypatch, capsys):
    path = tmp_path / 'c.json'
    path.write_text(json.dumps({'k': {'timestamp': time.time()}}))
    monkeypatch.setattr(cache.os, 'replace', lambda *a: (_ for _ in ()).throw(OSError('disk full')))

    Cache(str(path)).save({'other': {'timestamp': 1}})  # must not raise into the pipeline
    assert 'previous copy kept' in capsys.readouterr().out
    assert set(json.loads(path.read_text())) == {'k'}


def test_existing_file_mode_is_kept(tmp_path):
    path = tmp_path / 's.json'
    path.write_text('{}')
    os.chmod(path, 0o664)
    atomic_write_json(str(path), {'a': 1})
    assert (path.stat().st_mode & 0o777) == 0o664


def test_feed_http_cache_round_trips_through_an_atomic_save(tmp_path):
    path = tmp_path / 'h.json'
    http = FeedHTTPCache(str(path))
    http.load()
    http.record_failure('https://feed.test/rss', 'dns')
    http.save()
    again = FeedHTTPCache(str(path))
    again.load()
    assert again.failure_count('https://feed.test/rss') == 1


def test_opml_write_is_atomic_and_byte_identical(tmp_path):
    import integrate_discoveries
    tree = ET.ElementTree(ET.fromstring(
        '<opml version="2.0"><head><title>t</title></head>'
        '<body><outline text="Café" xmlUrl="https://a.test/feed?x=1&amp;y=2"/></body></opml>'))
    expected = tmp_path / 'expected.opml'
    tree.write(str(expected), encoding='utf-8', xml_declaration=True)
    actual = tmp_path / 'feeds.opml'
    integrate_discoveries.write_opml(tree, str(actual))
    assert actual.read_bytes() == expected.read_bytes()
    assert _leftovers(tmp_path) == []


# --- Accumulating markdown logs ----------------------------------------------
# These grow by append and are committed by CI. An append cut short commits a
# torn file; a truncating rewrite cut short commits the history as empty. Each
# writer now builds the whole file and swaps it in.

def _log_writers(tmp_path, monkeypatch):
    import calibration_agent
    import feedback_archive
    import feedback_trainer
    import integrate_discoveries
    import log_feed_results
    import standing_preferences

    def calibration(path):
        monkeypatch.setattr(calibration_agent, 'CALIBRATION_LOG_FILE', path)
        calibration_agent.write_changelog(None, [], [], [], {}, True, reason='no_stats')

    def calibration_notes(path):
        monkeypatch.setattr(calibration_agent, 'NOTES_FILE', path)
        monkeypatch.setattr(calibration_agent, 'CALIBRATION_LOG_FILE', tmp_path / 'cal.md')
        monkeypatch.setattr(calibration_agent, 'MEMORY_DIR', tmp_path)
        for name in ('BENCHMARKS_FILE', 'CHANGE_HISTORY_FILE', 'RECURRING_ISSUES_FILE'):
            monkeypatch.setattr(calibration_agent, name, tmp_path / f'{name}.json')
        calibration_agent.write_changelog({'analysis': 'NEW'}, [], [], [], {}, True)

    def trainer(path):
        monkeypatch.setattr(feedback_trainer, 'LOG_FILE', path)
        feedback_trainer.append_log('NEW\n')

    def archive(path):
        monkeypatch.setattr(feedback_archive, 'LOG_FILE', path)
        feedback_archive.append_log('NEW\n')

    def health(path):
        integrate_discoveries.append_health_log([], False, str(path))

    def todo(path):
        monkeypatch.setattr(log_feed_results, 'TODO_FILE', path)
        log_feed_results.update_todo([], [])

    def preferences(path):
        monkeypatch.setattr(standing_preferences, 'PREFERENCES_FILE', path)
        monkeypatch.setattr(standing_preferences, 'PR_BODY_FILE', tmp_path / 'body.md')
        standing_preferences.write_proposals(
            [{'rule': 'NEW', 'supporting_notes': 2, 'examples': ['x']}], '2026-10-04', 2)

    return {'calibration': calibration, 'calibration_notes': calibration_notes,
            'trainer': trainer, 'archive': archive, 'health': health,
            'todo': todo, 'preferences': preferences}


@pytest.mark.parametrize('writer', ['calibration', 'calibration_notes', 'trainer', 'archive',
                                    'health', 'todo', 'preferences'])
def test_a_log_write_that_dies_keeps_the_history(tmp_path, monkeypatch, writer):
    path = tmp_path / 'LOG.md'
    history = '# Log\n\n## 2026-01-01\nOLD HISTORY\n'
    path.write_text(history)
    run = _log_writers(tmp_path, monkeypatch)[writer]

    real_replace = os.replace

    def replace(src, dst):
        if Path(dst) == path:
            raise OSError(28, 'No space left on device')
        real_replace(src, dst)

    with monkeypatch.context() as m:
        m.setattr(cache.os, 'replace', replace)
        with pytest.raises(OSError):
            run(path)
    assert path.read_text() == history
    assert _leftovers(tmp_path) == []

    run(path)
    assert 'OLD HISTORY' in path.read_text()
    assert path.read_text() != history


def test_feed_log_rewrite_is_atomic(tmp_path, monkeypatch):
    import log_feed_results
    from datetime import datetime, timezone
    path = tmp_path / 'FEED_LOG.md'
    path.write_text(log_feed_results.LOG_HEADER)
    monkeypatch.setattr(cache.os, 'replace', lambda *a: (_ for _ in ()).throw(OSError(28, 'disk full')))
    with pytest.raises(OSError):
        log_feed_results.update_log_file(path, log_feed_results.LOG_HEADER, '### run\nNEW\n', 'manual',
                                         datetime.now(timezone.utc), log_feed_results.compress_to_week)
    assert path.read_text() == log_feed_results.LOG_HEADER
