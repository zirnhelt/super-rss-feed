#!/usr/bin/env python3
"""Claude Code hooks for super-rss-feed. Stdlib only; any Python 3.

    guard.py spend   PreToolUse(Bash): ask before a command that spends on a paid
                     API or rewrites committed state.
    guard.py merge   PreToolUse(mcp__github__merge_pull_request): deny until every
                     check on the PR's head has finished green. Eight PRs here were
                     merged before their checks finished (2026-09-23 to 10-18).
    guard.py stop    Stop: once per stop, run config validation + pytest when code
                     changed, and point out committed state the session rewrote.

Each reads the hook's JSON on stdin. A guard that can't decide (no network, no
interpreter) never blocks silently: it asks, or says why it skipped.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Optional

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])

# Scripts that call a paid API (Anthropic, Cohere, Brave, Kagi) or rewrite the
# caches, configs and logs CI commits. A --dry-run flag only lowers the stakes
# where the script honours it without spending.
PAID_SCRIPTS: dict[str, str] = {
    "super_rss_curator_json.py": "Haiku + Cohere scoring, Brave/Kagi fallbacks, rewrites every root cache",
    "feed_discovery.py": "23 Brave queries on the cap shared with the podcast, plus Haiku",
    "calibration_agent.py": "a Claude call; writes config/ unless CALIBRATION_DRY_RUN is true",
    "feedback_trainer.py": "a Claude call; rewrites config/feedback_examples.txt",
    "feedback_archive.py": "a Haiku distil call; moves feedback/ files",
    "standing_preferences.py": "a Haiku call; writes the proposal ledger",
    "generate_weekly_report.py": "a Haiku narrative call; rewrites weekly-state-article.json (read by the podcast)",
    "score_scrub_report.py": "a Claude call",
    "review_filter_priority.py": "Cohere calls",
    "integrate_discoveries.py": "rewrites feeds.opml",
}
DRY_RUN_SAFE = {"integrate_discoveries.py", "feedback_archive.py"}

# tests.yml's job. Its absence is the signal: a bot-opened PR's run has zero jobs
# and creates no check run, so "every check is green" passes vacuously.
REQUIRED_CHECKS = {"pytest"}

# Committed state a session should not rewrite unless the task is about it.
STATE_PATTERNS = [
    r"^[a-z_]+_cache\.json$", r"^feeds\.opml$", r"^curated-feeds\.opml$",
    r"^[A-Z_]+_LOG\.md$", r"^FEED_ERRORS\.md$", r"^weekly-state-article\.json$",
    r"^article_review_audit_summary\.json$", r"^feed_discovery_report\.json$",
    r"^discovery_actions\.json$", r"^feedback/", r"^calibration_memory/", r"^reports/",
]
CODE_PATTERNS = [r"\.py$", r"^config/", r"^tests/", r"^requirements"]


def _read_input() -> dict:
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return {}


def _decide(decision: str, reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": decision,
        "permissionDecisionReason": reason,
    }}))
    sys.exit(0)


# ── spend ────────────────────────────────────────────────────────────────────

def spend(data: dict) -> None:
    command = (data.get("tool_input") or {}).get("command", "")
    for script, cost in PAID_SCRIPTS.items():
        # `python [-flags] [path/]script.py`: running it, not reading or testing it.
        if not re.search(r"python[0-9.]*\s+(-[A-Za-z]+\s+)*(\S+/)?" + re.escape(script) + r"\b", command):
            continue
        if script in DRY_RUN_SAFE and "--dry-run" in command:
            continue
        search = "" if "USE_SEARCH_APIS=false" in command else \
            " Prefix USE_SEARCH_APIS=false to keep Brave/Kagi off."
        _decide("ask", f"{script} spends or writes committed state: {cost}.{search} "
                       "Run it only if the task needs a live run; revert the caches after.")


# ── merge ────────────────────────────────────────────────────────────────────

def _github(path: str) -> dict:
    ctx = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE")
                                     or os.environ.get("REQUESTS_CA_BUNDLE") or None)
    req = urllib.request.Request(f"https://api.github.com{path}",
                                 headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
        return json.load(resp)


def merge(data: dict) -> None:
    args = data.get("tool_input") or {}
    owner, repo, number = args.get("owner"), args.get("repo"), args.get("pullNumber")
    if not (owner and repo and number):
        return
    try:
        pr = _github(f"/repos/{owner}/{repo}/pulls/{int(number)}")
        sha = args.get("expectedHeadSha") or pr["head"]["sha"]
        runs = _github(f"/repos/{owner}/{repo}/commits/{sha}/check-runs?per_page=100")["check_runs"]
    except Exception as exc:  # network, rate limit, private repo
        _decide("ask", f"Could not read the checks for #{number} ({exc}); confirm they are green first.")
    if pr.get("draft"):
        _decide("deny", f"#{number} is a draft; drafts wait on the human's decision.")
    missing = REQUIRED_CHECKS - {r["name"] for r in runs}
    if missing:
        _decide("deny", f"#{number} has no {', '.join(sorted(missing))} check on {sha[:8]}: CI never ran "
                        "on this head. A bot-opened PR triggers no workflows (its run shows zero jobs); "
                        "push a commit to the branch so tests.yml runs.")
    pending = [r["name"] for r in runs if r["status"] != "completed"]
    red = [r["name"] for r in runs if r["status"] == "completed"
           and r["conclusion"] not in ("success", "skipped", "neutral")]
    if pending:
        _decide("deny", f"#{number}: checks still running on {sha[:8]}: {', '.join(pending)}. "
                        "Wait for them; merging now is how 8 PRs here beat CI.")
    if red:
        _decide("deny", f"#{number}: checks not green on {sha[:8]}: {', '.join(red)}.")


# ── stop ─────────────────────────────────────────────────────────────────────

def _changed_files() -> list[str]:
    out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                         cwd=ROOT, capture_output=True, text=True).stdout
    return [line[3:].split(" -> ")[-1].strip('"') for line in out.splitlines() if line[3:]]


def _python() -> Optional[str]:
    for candidate in (ROOT / "venv" / "bin" / "python", Path("/usr/bin/python3.11")):
        if candidate.exists():
            return str(candidate)
    return None


def stop(data: dict) -> None:
    if data.get("stop_hook_active"):
        return  # one reminder per stop, never a loop
    changed = _changed_files()
    problems: list[str] = []

    state = [f for f in changed if any(re.search(p, f) for p in STATE_PATTERNS)]
    if state:
        problems.append("Committed state changed: " + ", ".join(state[:12])
                        + (" …" if len(state) > 12 else "")
                        + ". If the task didn't ask for it (a local pipeline run, a test that "
                          "wrote to the repo), restore with `git checkout -- <file>`.")

    code = [f for f in changed if any(re.search(p, f) for p in CODE_PATTERNS)]
    python = _python()
    if code and python:
        diff = subprocess.run(["git", "diff", "HEAD"], cwd=ROOT, capture_output=True).stdout
        for f in code:
            path = ROOT / f
            if path.is_file():
                diff += f.encode() + path.read_bytes()
        stamp = ROOT / "venv" / ".last-green"
        digest = hashlib.sha256(diff).hexdigest()
        if not (stamp.exists() and stamp.read_text() == digest):
            env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "USE_SEARCH_APIS": "false"}
            for key in ("ANTHROPIC_API_KEY", "COHERE_API_KEY", "BRAVE_API_KEY", "KAGI_API_KEY"):
                env.pop(key, None)
            result = subprocess.run(
                f"{python} config_loader.py >/dev/null && {python} -m pytest tests/ -q -x -p no:cacheprovider",
                shell=True, cwd=ROOT, capture_output=True, text=True, env=env, timeout=300)
            if result.returncode != 0:
                tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-15:])
                problems.append(f"Code changed and the checks are red:\n{tail}")
            elif stamp.parent.is_dir():
                stamp.write_text(digest)
    elif code:
        problems.append("Code changed but no Python 3.11 was found to run the tests "
                        "(the default 3.13 can't import feedparser 6.0.10).")

    if problems:
        print("\n\n".join(problems), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    payload = _read_input()
    {"spend": spend, "merge": merge, "stop": stop}.get(mode, lambda _d: None)(payload)
