"""The calibration log and notes stay bounded: old entries fold, nothing is lost silently."""
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import calibration_agent as agent  # noqa: E402

NOW = datetime(2026, 10, 18, tzinfo=timezone.utc)

LOG = """# Calibration Log

Header text.

## 2026-06-14 (dry run)

No changes: Claude call or response parsing failed. See logs for details.


## 2026-07-12

Audit window: 7 runs (a to b).


**Analysis**

Long analysis.

**Changes applied**

- `limits.min_claude_score`: 13 → 16 — rationale one
- `limits.haiku_scrub_floor`: 10 → 13 — rationale two

## 2026-07-26 (manual — rearchitecture)

Pipeline rearchitected. More detail.

Second paragraph.

## 2026-08-02

Audit window: 7 runs.


**Analysis**

Text.


No changes applied this run.


**Human recommendations**

- one
- two

## 2026-10-10

Audit window: 14 runs.

Recent entry kept in full.
"""


def test_old_log_entries_cut_to_one_line_and_recent_kept():
    out = agent.compact_calibration_log(LOG, NOW)
    assert out.startswith('# Calibration Log\n\nHeader text.\n\n' + agent.EARLIER_RUNS_HEADER)
    assert ('- **2026-06-14** (dry run) — No changes: Claude call or response parsing failed. '
            'See logs for details.') in out
    assert ('- **2026-07-12** — applied `limits.min_claude_score`: 13 → 16; '
            '`limits.haiku_scrub_floor`: 10 → 13') in out
    assert '- **2026-07-26** (manual — rearchitecture) — Pipeline rearchitected. More detail.' in out
    assert '- **2026-08-02** — no changes, 2 human recommendations' in out
    assert 'Long analysis' not in out
    assert '## 2026-10-10\n\nAudit window: 14 runs.\n\nRecent entry kept in full.\n' in out


def test_log_compaction_is_idempotent_and_merges_later_folds():
    once = agent.compact_calibration_log(LOG, NOW)
    assert agent.compact_calibration_log(once, NOW) == once
    later = agent.compact_calibration_log(once, datetime(2026, 12, 31, tzinfo=timezone.utc))
    assert later.count(agent.EARLIER_RUNS_HEADER) == 1
    assert '- **2026-10-10** — no changes' in later
    lines = [line for line in later.splitlines() if line.startswith('- **')]
    assert [line[4:14] for line in lines] == sorted(line[4:14] for line in lines)


NOTES = """# Calibration Agent Notes

Preamble.

---
""" + ''.join(f"\n## 2026-0{m}-01\n\nEntry {m}.\n" for m in range(1, 10))


def _fake_client(text, calls, stop_reason='end_turn'):
    def create(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(content=[SimpleNamespace(type='text', text=text)],
                               stop_reason=stop_reason,
                               usage=SimpleNamespace(input_tokens=10, output_tokens=5))
    return lambda api_key: SimpleNamespace(messages=SimpleNamespace(create=create))


def _setup(tmp_path, monkeypatch, text, stop_reason='end_turn'):
    notes = tmp_path / 'notes.md'
    notes.write_text(NOTES)
    calls = []
    monkeypatch.setattr(agent, 'NOTES_FILE', notes)
    monkeypatch.setattr(agent.anthropic, 'Anthropic', _fake_client(text, calls, stop_reason))
    monkeypatch.setattr(agent.config_loader, 'get_blocked_sources', lambda: ['rolling stone'])
    return notes, calls


def test_notes_fold_old_entries_into_lessons_and_keep_the_last_six(tmp_path, monkeypatch):
    notes, calls = _setup(tmp_path, monkeypatch, '- lesson one\n- lesson two')
    assert agent.compact_notes('key')
    out = notes.read_text()
    assert out.startswith('# Calibration Agent Notes\n\nPreamble.\n\n---\n\n' + agent.LESSONS_HEADER)
    assert 'through 2026-03-01' in out and '- lesson one' in out
    assert [m for m in range(1, 10) if f'## 2026-0{m}-01' in out] == [4, 5, 6, 7, 8, 9]
    prompt = calls[0]['messages'][0]['content']
    assert 'Entry 1.' in prompt and 'Entry 4.' not in prompt and 'rolling stone' in prompt
    assert calls[0]['extra_body'] == agent.api_usage.HAIKU_EXTRA_BODY

    assert not agent.compact_notes('key')  # nothing left to fold: no second call
    assert len(calls) == 1


def test_notes_refold_carries_the_existing_lessons(tmp_path, monkeypatch):
    notes, calls = _setup(tmp_path, monkeypatch, '- lesson one')
    agent.compact_notes('key')
    notes.write_text(notes.read_text() + '\n## 2026-10-01\n\nEntry 10.\n')
    assert agent.compact_notes('key')
    prompt = calls[1]['messages'][0]['content']
    assert '- lesson one' in prompt and 'Folded from' not in prompt and 'Entry 4.' in prompt
    assert notes.read_text().count(agent.LESSONS_HEADER) == 1


def test_notes_untouched_when_the_call_fails_or_truncates(tmp_path, monkeypatch):
    notes, _ = _setup(tmp_path, monkeypatch, '- partial', stop_reason='max_tokens')
    assert not agent.compact_notes('key')
    assert notes.read_text() == NOTES

    def boom(api_key):
        raise RuntimeError('down')
    monkeypatch.setattr(agent.anthropic, 'Anthropic', boom)
    assert not agent.compact_notes('key')
    assert notes.read_text() == NOTES
