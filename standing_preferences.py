#!/usr/bin/env python3
"""Propose standing reader preferences from rating notes (weekly).

A note on a rating ("US politics", "Product review", "No article") is the reader
saying, in their own words, what they do not want. Until 2026-09-23 those notes
reached the pipeline only as few-shot examples for the small slice of articles
that get full scoring, so the same complaint came back for months.

This closes the loop. Each week it reads the notes left on "bad" ratings over the
last NOTE_WINDOW_DAYS. When there is new signal, it asks Haiku once to phrase any
subject that at least MIN_SUPPORTING_NOTES notes share, and that neither the gate's
rubric nor config/standing_preferences.txt covers yet, as a rubric line. The lines
are appended to config/standing_preferences.txt and the workflow opens a pull
request:

- merging it adopts them, because the gate reads that file every run;
- closing it declines them. Every proposal is recorded in
  feedback/standing_proposals.json, which the workflow commits to main, and is
  never proposed again.

Short-circuits before any API call when there are too few notes, or when the
notes are exactly the ones the last run already saw.

Usage:
    python standing_preferences.py              # propose and write
    python standing_preferences.py --dry-run    # print the proposals, write nothing
"""

import argparse
import difflib
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).parent
FEEDBACK_DIR = BASE_DIR / "feedback"
PREFERENCES_FILE = BASE_DIR / "config" / "standing_preferences.txt"
LEDGER_FILE = FEEDBACK_DIR / "standing_proposals.json"
PR_BODY_FILE = BASE_DIR / "standing_preferences_pr.md"

MODEL = "claude-haiku-4-5"
NOTE_WINDOW_DAYS = 30
MIN_SUPPORTING_NOTES = 2
MAX_PROPOSALS = 3
# Two phrasings this close are the same rule; re-proposing either is noise.
DUPLICATE_RATIO = 0.75
SUBJECT_RATIO = 0.85


def load_bad_notes(now: datetime, days: int = NOTE_WINDOW_DAYS) -> List[Dict[str, str]]:
    """Notes left on 'bad' ratings within the window, oldest first."""
    cutoff = (now - timedelta(days=days)).date().isoformat()
    notes = []
    for path in sorted(FEEDBACK_DIR.glob("20??-??-??.json")):
        if path.stem < cutoff:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        entries = data if isinstance(data, list) else data.get("ratings") or data.get("entries") or []
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("rating") != "bad":
                continue
            note = (entry.get("note") or "").strip()
            if note:
                notes.append({
                    "note": note,
                    "title": (entry.get("title") or "").strip()[:120],
                    "source": (entry.get("source") or "").strip(),
                    "category": (entry.get("category") or "").strip(),
                })
    return notes


def notes_fingerprint(notes: List[Dict[str, str]]) -> str:
    raw = "\n".join(f"{n['note']}|{n['title']}" for n in notes)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def load_ledger() -> Dict:
    try:
        return json.loads(LEDGER_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"last_fingerprint": None, "proposed": []}


def _subject(rule: str) -> str:
    """The part before the first colon: rules are written "<Subject>: <scope>."."""
    return rule.split(":", 1)[0].strip().lower()


def is_duplicate(rule: str, existing: List[str]) -> bool:
    """Same subject, or near-identical wording. A shorter restatement of a standing
    rule scores low on whole-string similarity, so the subject is compared on its own."""
    key, subject = rule.lower(), _subject(rule)
    return any(difflib.SequenceMatcher(None, subject, _subject(other)).ratio() >= SUBJECT_RATIO
               or difflib.SequenceMatcher(None, key, other.lower()).ratio() >= DUPLICATE_RATIO
               for other in existing)


def build_prompt(notes: List[Dict[str, str]], rubric: str, declined: List[str]) -> str:
    note_lines = "\n".join(
        f'- "{n["note"]}" on: {n["title"]} ({n["source"]}, {n["category"]})' for n in notes)
    declined_block = "\n".join(f"- {r}" for r in declined) or "(none)"
    return f"""The reader rated these articles "bad" and left a note saying why:

{note_lines}

The reject rubric already applied every night (built-in subjects plus the reader's standing preferences):
<rubric>
{rubric.strip()}
</rubric>

Rules already proposed to the reader and declined or pending — never propose these again:
{declined_block}

Propose at most {MAX_PROPOSALS} NEW standing rules for the reject list. Each must be:
- supported by at least {MIN_SUPPORTING_NOTES} of the notes above that share one subject;
- about a subject the rubric does not already cover;
- written like the rubric's lines: "<Subject>: <what it covers>. KEEP <the exception>."

A note that describes a one-off mistake (a mis-tagged article, a single bad source) is not a
standing rule. An empty list is a good answer when nothing new recurs.

Reply with JSON only:
{{"rules": [{{"rule": "...", "supporting_notes": <int>, "examples": ["<title>", "<title>"]}}]}}"""


def parse_proposals(text: str) -> List[Dict]:
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        return []
    try:
        rules = json.loads(match.group(0)).get("rules", [])
    except ValueError:
        return []
    return [r for r in rules if isinstance(r, dict) and isinstance(r.get("rule"), str)]


def select_proposals(proposals: List[Dict], standing: List[str], declined: List[str]) -> List[Dict]:
    """The model's claims are checked here, not trusted: support count, novelty, cap."""
    kept: List[Dict] = []
    for p in proposals:
        rule = " ".join(p["rule"].split())
        try:
            support = int(p.get("supporting_notes") or 0)
        except (TypeError, ValueError):
            support = 0
        if support < MIN_SUPPORTING_NOTES:
            continue
        if is_duplicate(rule, standing + declined + [k["rule"] for k in kept]):
            continue
        kept.append({"rule": rule, "supporting_notes": support,
                     "examples": [str(e)[:120] for e in (p.get("examples") or [])][:3]})
    return kept[:MAX_PROPOSALS]


def call_haiku(prompt: str) -> Optional[str]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY not set — skipping")
        return None
    import anthropic
    import api_usage
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=MODEL,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    api_usage.record_claude_usage(response.usage)
    print(api_usage.format_summary())
    return response.content[0].text


def write_proposals(proposals: List[Dict], today: str, note_count: int) -> None:
    lines = [f"\n# Proposed {today} from {note_count} rating notes — merge to adopt, close to decline."]
    lines += [p["rule"] for p in proposals]
    with PREFERENCES_FILE.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    body = [f"Proposed from the notes on your \"bad\" ratings over the last {NOTE_WINDOW_DAYS} days.",
            "",
            "**Merge** to adopt: the quality gate applies these from the next run.",
            "**Close** to decline: they will not be proposed again.",
            "You can also edit the wording in this PR before merging.",
            ""]
    for p in proposals:
        body.append(f"- **{p['rule']}**")
        body.append(f"  - supported by {p['supporting_notes']} notes, e.g. "
                    + "; ".join(f"_{e}_" for e in p["examples"]))
    PR_BODY_FILE.write_text("\n".join(body) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    notes = load_bad_notes(now)
    print(f"Standing preferences: {len(notes)} notes on bad ratings in the last {NOTE_WINDOW_DAYS} days")
    if len(notes) < MIN_SUPPORTING_NOTES:
        print("Too few notes to support a rule — nothing to propose")
        return 0

    ledger = load_ledger()
    fingerprint = notes_fingerprint(notes)
    if fingerprint == ledger.get("last_fingerprint"):
        print("No new notes since the last run — nothing to propose")
        return 0

    import config_loader
    from super_rss_curator_json import build_gate_reject_rubric
    standing = config_loader.load_standing_preferences()
    declined = [p["rule"] for p in ledger.get("proposed", [])]
    text = call_haiku(build_prompt(notes, build_gate_reject_rubric(standing), declined))
    if text is None:
        return 0
    proposals = select_proposals(parse_proposals(text), standing, declined)

    print(f"Proposals: {len(proposals)}")
    for p in proposals:
        print(f"  - {p['rule']} ({p['supporting_notes']} notes)")
    if args.dry_run:
        return 0

    today = now.date().isoformat()
    ledger["last_fingerprint"] = fingerprint
    ledger.setdefault("proposed", []).extend({"rule": p["rule"], "date": today} for p in proposals)
    LEDGER_FILE.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if proposals:
        write_proposals(proposals, today, len(notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
