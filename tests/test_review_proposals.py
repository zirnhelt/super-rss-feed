"""review.html's Proposals tab: the podcast's roadmap fixer writes proposals/queue.json each
morning, and the producer's approve / decline / comment calls go to proposals/decisions.json,
which the fixer acts on at its next run. The queue is written by a model and the decisions
direct merges, closes and deletes, so the page must escape everything it shows and must never
lose or overwrite a saved call."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "review.html").read_text(encoding="utf-8")


def _between(start: str, end: str) -> str:
    i = PAGE.index(start)
    return PAGE[i:PAGE.index(end, i)]


def test_the_tab_is_wired_like_the_others() -> None:
    assert 'id="tab-proposals" data-tab="proposals" aria-controls="panel-proposals"' in PAGE
    assert "const TABS = ['articles', 'episode', 'exemplar', 'proposals'];" in PAGE
    # Static markup outside the article grid: an empty or failed batch cannot hide it.
    panel = PAGE.index('id="panel-proposals"')
    assert panel < PAGE.index('id="article-grid"') and panel < PAGE.index('id="loading-msg"')
    boot = _between("window.addEventListener('DOMContentLoaded'", "function populateExemplarCategories")
    assert boot.index("loadProposals();") < boot.index("init();")


def test_reading_the_queue_needs_no_token() -> None:
    """The repo is public: the tab shows the queue before the token field is filled."""
    read = _between("async function fetchRepoJson", "function runLabel")
    assert "readToken()" not in read and "Authorization" not in read
    assert "await githubFetch(" in read and "cache: 'no-store'" in read


def test_every_github_call_on_the_save_path_can_time_out() -> None:
    save = _between("async function saveDecisions", "async function submitDecisions")
    assert "await fetch(" not in save
    assert save.count("await githubFetch(") == 2
    assert "cache: 'no-store'" in save   # a cached read hands back a stale sha


def test_a_saved_call_is_never_lost_or_overwritten() -> None:
    save = _between("async function saveDecisions", "async function submitDecisions")
    # An unreadable file is refused, never replaced with this save's rows alone.
    assert "the decisions file could not be read, so it was not overwritten" in save
    assert "decisions: [...kept, ...entries]" in save
    # Another save between the read and the write is retried, not clobbered.
    assert "put.status === 409 || put.status === 422" in save
    assert "[skip ci]" in save
    assert "const PROPOSALS_DECISIONS  = 'proposals/decisions.json';" in PAGE


def test_the_latest_row_holds_the_whole_answer() -> None:
    """A comment alone carries the pending call with it, so the fixer reads one row per item."""
    rows = _between("function decisionEntries", "// Appends `entries`")
    assert "const verdict = pick.verdict !== undefined ? pick.verdict : before;" in rows
    assert "if (!comment && verdict === before) continue;" in rows
    for field in ("id: item.id", "kind: item.kind", "title: item.title", "verdict", "decided_at: now"):
        assert field in rows, field


def test_the_queue_is_cleaned_before_it_is_shown() -> None:
    clean = _between("function cleanProposal", "function cleanDone")
    assert "if (!id || !title || !Object.hasOwn(PROPOSAL_KINDS, raw.kind)) return null;" in clean
    assert "url: httpsUrl(raw.url)" in clean
    assert "filter(l => l && httpsUrl(l.url))" in clean
    assert "function httpsUrl(value) { return typeof value === 'string' && /^https:\\/\\//i.test(value) ? value : ''; }" in PAGE


def test_nothing_from_the_queue_reaches_the_page_unescaped() -> None:
    card = _between("function proposalCard", "function renderProposals")
    for shown in ("escHtml(item.title)", "escHtml(item.detail)", "escHtml(item.fix)",
                  "escHtml(item.response)", "escHtml(item.acted.outcome)", "escAttr(safeHref(item.url))",
                  "escAttr(safeHref(l.url))", "escHtml(l.label)", "escHtml(text)", "escHtml(said || 'no call')",
                  "escHtml(comment)"):
        assert shown in card, shown
    # Every interpolated item field is either only tested for truth, or (since) a tag's text,
    # which goes through escHtml(text) with the rest of the tags.
    for field in re.findall(r"\$\{item\.(\w+)", card):
        assert field in ("detail", "fix", "response", "url", "since"), field
    assert "item.since ? ['', `since ${item.since}`] : null" in card
    done = _between("function renderProposals", "// Updates the card in place")
    assert "escHtml(d.title)" in done and "escHtml(d.outcome)" in done and "escAttr(safeHref(d.url))" in done


def test_each_kind_says_what_approve_and_decline_do() -> None:
    kinds = _between("const PROPOSAL_KINDS = {", "};")
    assert "proposal: { tag: '💡 Proposal',     yes: '✅ Build it',           no: '🚫 Drop it' }" in kinds
    assert "pr:       { tag: '🔀 Pull request', yes: '✅ Merge',              no: '🚫 Close' }" in kinds
    assert "branch:   { tag: '🌿 Branch',       yes: '✅ Open a PR & merge', no: '🚫 Delete' }" in kinds


def test_a_session_cannot_write_the_producers_calls() -> None:
    settings = json.loads((ROOT / ".claude/settings.json").read_text())
    deny = settings["permissions"]["deny"]
    assert "Edit(proposals/decisions.json)" in deny and "Write(proposals/decisions.json)" in deny


def test_the_committed_queue_has_the_shape_the_page_reads() -> None:
    queue = json.loads((ROOT / "proposals/queue.json").read_text(encoding="utf-8"))
    assert isinstance(queue["items"], list) and isinstance(queue.get("done", []), list)
    ids = [item["id"] for item in queue["items"]]
    assert len(ids) == len(set(ids))
    for item in queue["items"]:
        assert item["kind"] in ("proposal", "pr", "branch") and item["title"].strip(), item
        for link in [item.get("url")] + [l["url"] for l in item.get("links", [])]:
            assert link is None or link.startswith("https://"), link


def test_a_saved_call_looks_saved_and_save_waits_for_a_change() -> None:
    """2026-11-23: with every call already saved, Save answered 'Pick a call', and a saved call
    drew the same solid green as one tapped and not yet saved."""
    assert "episode-opt[data-saved][aria-pressed=true]" in PAGE
    card = _between("function proposalCard", "function renderProposals")
    assert card.count("callSaved(item.id, verdict)") == 2
    click = _between("function onProposalClick", "function onProposalInput")
    assert "callSaved(" in click and "updateProposalSave()" in click
    save = _between("function updateProposalSave", "async function fetchRepoJson")
    assert "!decisionEntries().length" in save and "proposalSaving" in save
    submit = _between("async function submitDecisions", "// User-submitted exemplar")
    assert "Nothing new to save: every call is already saved." in submit
    assert "Pick a call or write a comment first." in submit
    assert "saveBtn" not in submit
