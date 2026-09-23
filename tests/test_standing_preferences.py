"""Standing preferences: the reader's reject rules, and the weekly proposer that
turns rating notes into them. No API calls here — the model's one job is phrasing,
and everything it claims is re-checked locally."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config_loader
import standing_preferences as sp
import super_rss_curator_json as m


def test_standing_lines_sit_in_the_gate_subject_list():
    rubric = m.build_gate_reject_rubric(["Horoscopes: astrology columns. KEEP astronomy."])
    listed = rubric.index("- Horoscopes: astrology columns. KEEP astronomy.")
    assert rubric.index("UNWANTED SUBJECTS") < listed < rubric.index("Apply the fluff rule")


def test_the_live_file_loads_and_skips_comments():
    lines = config_loader.load_standing_preferences()
    assert lines, "config/standing_preferences.txt is empty or missing"
    assert not any(line.startswith("#") for line in lines)
    assert any(line.startswith("US domestic politics") for line in lines)
    assert all(f"- {line}" in m.GATE_REJECT_RUBRIC for line in lines)


def _write_ratings(folder, day, entries):
    (folder / f"{day}.json").write_text(json.dumps(entries), encoding="utf-8")


def test_only_notes_on_bad_ratings_in_the_window_count(tmp_path, monkeypatch):
    monkeypatch.setattr(sp, "FEEDBACK_DIR", tmp_path)
    _write_ratings(tmp_path, "2026-09-20", [
        {"rating": "bad", "note": "Horoscope", "title": "Your stars this week", "source": "X", "category": "news"},
        {"rating": "good", "note": "More like this", "title": "A", "source": "Y", "category": "news"},
        {"rating": "bad", "note": "", "title": "B", "source": "Z", "category": "news"},
    ])
    _write_ratings(tmp_path, "2026-07-01", [
        {"rating": "bad", "note": "Too old", "title": "C", "source": "Z", "category": "news"},
    ])
    notes = sp.load_bad_notes(datetime(2026, 9, 23, tzinfo=timezone.utc))
    assert [n["note"] for n in notes] == ["Horoscope"]


def test_proposals_need_support_and_novelty():
    standing = ["US domestic politics: partisan politics. KEEP direct Canadian effects."]
    declined = ["Horoscopes: astrology columns."]
    proposals = [
        {"rule": "Horoscopes: astrology columns", "supporting_notes": 4},     # declined before
        {"rule": "US domestic politics: partisan politics.", "supporting_notes": 5},  # already standing
        {"rule": "Lottery results: draw numbers.", "supporting_notes": 1},   # one note is not a pattern
        {"rule": "Outlet homepages: a site's front page.", "supporting_notes": 2,
         "examples": ["Macleans.ca", "The Walrus"]},
    ]
    kept = sp.select_proposals(proposals, standing, declined)
    assert [k["rule"] for k in kept] == ["Outlet homepages: a site's front page."]


def test_proposals_are_capped():
    proposals = [{"rule": f"Subject {i}: something distinct number {i * 1000}.", "supporting_notes": 3}
                 for i in range(6)]
    assert len(sp.select_proposals(proposals, [], [])) <= sp.MAX_PROPOSALS


def test_unparseable_reply_proposes_nothing():
    assert sp.parse_proposals("Sorry, I can't help with that.") == []
    assert sp.parse_proposals('{"rules": [{"rule": "A: b."}]}') == [{"rule": "A: b."}]


def test_unchanged_notes_make_no_api_call(tmp_path, monkeypatch):
    monkeypatch.setattr(sp, "FEEDBACK_DIR", tmp_path)
    monkeypatch.setattr(sp, "LEDGER_FILE", tmp_path / "standing_proposals.json")
    _write_ratings(tmp_path, datetime.now(timezone.utc).date().isoformat(), [
        {"rating": "bad", "note": "Horoscope", "title": "Stars", "source": "X", "category": "news"},
        {"rating": "bad", "note": "Horoscope", "title": "More stars", "source": "X", "category": "news"},
    ])
    notes = sp.load_bad_notes(datetime.now(timezone.utc))
    (tmp_path / "standing_proposals.json").write_text(
        json.dumps({"last_fingerprint": sp.notes_fingerprint(notes), "proposed": []}))

    def _no_call(prompt):
        raise AssertionError("called the API with no new notes")
    monkeypatch.setattr(sp, "call_haiku", _no_call)
    monkeypatch.setattr(sys, "argv", ["standing_preferences.py"])
    assert sp.main() == 0
