#!/usr/bin/env python3
"""Generate a weekly "State of the Feed" article and inject it into feed-news.json.

Runs as the last job of weekly-maintenance.yml, Saturdays, after every agent
that can change the pipeline has run.

Outputs:
  output/feed-news.json              — feed-news with the new article prepended
  output/weekly-report-YYYY-Www.html — standalone HTML permalink
  reports/weekly-report-YYYY-Www.html — committed to main so generate-feed persists it
  weekly-state-article.json          — committed to main; its `_changes` feed the
                                       podcast's Sunday Meta Moment
"""

import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import defaultdict
from html import escape
from datetime import datetime, timezone, timedelta
from pathlib import Path

import anthropic
import requests

import api_usage
from api_usage import FLAT_COST_PER_CALL
from cache import atomic_write_json, atomic_write_text
from sanitize import plain_text, sanitize_feed

BASE_URL = "https://zirnhelt.github.io/super-rss-feed"
GITHUB_REPO_URL = "https://github.com/zirnhelt/super-rss-feed"
FEED_NEWS_URL = f"{BASE_URL}/feed-news.json"
OUTPUT_DIR = Path("output")
CATEGORY_ORDER = ["local", "ai-tech", "climate", "homelab", "homestead", "wellness", "science", "scifi", "design", "outdoors", "news"]


# ---------------------------------------------------------------------------
# New feed detection via git diff
# ---------------------------------------------------------------------------

def _opml_urls(text: str) -> dict:
    """Parse OPML text → {xmlUrl: title}."""
    try:
        root = ET.fromstring(text)
        return {
            o.get("xmlUrl"): (o.get("title") or o.get("text") or o.get("xmlUrl", ""))
            for o in root.iter("outline")
            if o.get("xmlUrl")
        }
    except ET.ParseError:
        return {}


def get_new_feeds_this_week() -> list:
    """Return feeds added to feeds.opml in the past 7 days."""
    try:
        # Find the most recent commit to feeds.opml that is older than 7 days
        old_hash = subprocess.run(
            ["git", "log", "--before=7 days ago", "--format=%H", "-1", "--", "feeds.opml"],
            capture_output=True, text=True, check=False,
        ).stdout.strip()

        if not old_hash:
            # Repo is <7 days old; compare against the very first commit touching feeds.opml
            all_hashes = subprocess.run(
                ["git", "log", "--format=%H", "--", "feeds.opml"],
                capture_output=True, text=True, check=False,
            ).stdout.strip().split("\n")
            all_hashes = [h for h in all_hashes if h]
            old_hash = all_hashes[-1] if len(all_hashes) > 1 else None

        if not old_hash:
            return []

        old_text = subprocess.run(
            ["git", "show", f"{old_hash}:feeds.opml"],
            capture_output=True, text=True, check=False,
        ).stdout
        curr_text = Path("feeds.opml").read_text("utf-8")

        old_urls = _opml_urls(old_text)
        curr_urls = _opml_urls(curr_text)
        new_url_set = set(curr_urls) - set(old_urls)

        feeds = []
        if new_url_set:
            root = ET.fromstring(curr_text)
            for o in root.iter("outline"):
                url = o.get("xmlUrl")
                if url in new_url_set:
                    feeds.append({
                        "title": o.get("title") or o.get("text") or url,
                        "url": url,
                    })
        return feeds

    except Exception as exc:
        print(f"  ⚠️  Could not detect new feeds: {exc}")
        return []


# ---------------------------------------------------------------------------
# Parse FEED_LOG.md for the past 7 days
# ---------------------------------------------------------------------------

def get_weekly_stats() -> dict:
    log_path = Path("FEED_LOG.md")
    if not log_path.exists():
        return {}

    content = log_path.read_text("utf-8")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

    total_runs = 0
    total_fetched = 0
    total_quality = 0
    cat_totals: dict = defaultdict(int)

    for m_day in re.finditer(
        r"^## (\d{4}-\d{2}-\d{2}[^\n]*)\n(.*?)(?=^## |\Z)",
        content, re.MULTILINE | re.DOTALL,
    ):
        date_key = re.match(r"\d{4}-\d{2}-\d{2}", m_day.group(1))
        if not date_key or date_key.group() < cutoff:
            continue

        day_text = m_day.group(2)
        total_runs += len(re.findall(r"^####", day_text, re.MULTILINE))

        for hm in re.finditer(r"Fetched \*\*(\d+)\*\*", day_text):
            total_fetched += int(hm.group(1))
        for qm in re.finditer(r"quality \*\*(\d+)\*\*", day_text):
            total_quality += int(qm.group(1))
        for cm in re.finditer(
            r"(local|ai-tech|climate|homelab|homestead|wellness|news|science|scifi|design|outdoors):(\d+)\(", day_text
        ):
            cat_totals[cm.group(1)] += int(cm.group(2))

    return {
        "total_runs": total_runs,
        "total_fetched": total_fetched,
        "avg_fetched": round(total_fetched / total_runs) if total_runs else 0,
        "total_quality": total_quality,
        "avg_quality": round(total_quality / total_runs) if total_runs else 0,
        "cat_totals": dict(cat_totals),
        "failed_feeds": get_failed_feeds(cutoff),
    }


def get_failed_feeds(cutoff: str) -> list:
    """Distinct feed names that failed in FEED_ERRORS.md since cutoff (YYYY-MM-DD)."""
    log_path = Path("FEED_ERRORS.md")
    if not log_path.exists():
        return []

    content = log_path.read_text("utf-8")
    failed_feeds: list = []

    for m_day in re.finditer(
        r"^## (\d{4}-\d{2}-\d{2}[^\n]*)\n(.*?)(?=^## |\Z)",
        content, re.MULTILINE | re.DOTALL,
    ):
        date_key = re.match(r"\d{4}-\d{2}-\d{2}", m_day.group(1))
        if not date_key or date_key.group() < cutoff:
            continue

        for fm in re.finditer(r"⚠️ \*\*(.+?)\*\* failed", m_day.group(2)):
            name = fm.group(1)
            if name not in failed_feeds:
                failed_feeds.append(name)

    return failed_feeds


# ---------------------------------------------------------------------------
# Parse TODO.md for current errors
# ---------------------------------------------------------------------------

def get_current_errors() -> list:
    todo_path = Path("TODO.md")
    if not todo_path.exists():
        return []

    content = todo_path.read_text("utf-8")
    start, end = "<!-- AUTO:START -->", "<!-- AUTO:END -->"
    if start not in content or end not in content:
        return []

    auto_section = content[content.index(start):content.index(end)]
    errors = []
    seen = set()
    for m in re.finditer(
        r"\|\s*\d{4}-\d{2}-\d{2}\s*\|[^|]*\|\s*(?:⚠️|❌)\s*\*?\*?([^|*]+?)\*?\*?\s*(?:failed)?\s*\|\s*`?([^|`\n]+?)`?\s*\|",
        auto_section,
    ):
        feed = m.group(1).strip()
        if feed and feed not in seen:
            seen.add(feed)
            errors.append({"feed": feed, "error": m.group(2).strip()[:80]})
    return errors


# ---------------------------------------------------------------------------
# Parse feed_discovery_report.json
# ---------------------------------------------------------------------------

def get_discovery_highlights() -> list:
    report_path = Path("feed_discovery_report.json")
    if not report_path.exists():
        return []
    try:
        data = json.loads(report_path.read_text("utf-8"))
        candidates = (
            data.get("summary", {}).get("top_recommendations")
            or data.get("candidates")
            or data.get("feeds")
            or []
        )
        scored = [c for c in candidates if c.get("score") or c.get("total_score")]
        scored.sort(key=lambda x: x.get("score", x.get("total_score", 0)), reverse=True)
        return [
            {
                "title": c.get("title") or c.get("name") or "Unknown",
                "score": c.get("score") or c.get("total_score") or 0,
            }
            for c in scored[:3]
        ]
    except Exception as exc:
        print(f"  ⚠️  Could not read discovery report: {exc}")
        return []


# ---------------------------------------------------------------------------
# Discovery actions (feeds auto-added this run)
# ---------------------------------------------------------------------------

def get_discovery_actions() -> list:
    path = Path("discovery_actions.json")
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text("utf-8"))
    except Exception as exc:
        print(f"  ⚠️  Could not read discovery_actions.json: {exc}")
        return []


# ---------------------------------------------------------------------------
# Feed health actions (feeds repaired, retired, or restored this run)
# ---------------------------------------------------------------------------

def get_feed_health_actions() -> list:
    """Health fixes the weekly heal pass applied to feeds.opml.

    'recovered' entries are dropped: a feed that started working again on its
    own is a non-event for a table whose purpose is "what changed, and how do
    I undo it". They stay in FEED_HEALTH_LOG.md for anyone tracing a feed.
    """
    path = Path("feed_health_actions.json")
    if not path.exists():
        return []
    try:
        actions = json.loads(path.read_text("utf-8"))
    except Exception as exc:
        print(f"  ⚠️  Could not read feed_health_actions.json: {exc}")
        return []
    return [a for a in actions if a.get("action") != "recovered"]


# ---------------------------------------------------------------------------
# Calibration changes from calibration_memory/change_history.json
# ---------------------------------------------------------------------------

def get_calibration_changes(today: str) -> list:
    path = Path("calibration_memory/change_history.json")
    if not path.exists():
        return []
    try:
        history = json.loads(path.read_text("utf-8"))
        return [
            c for c in history.get("changes", [])
            if c.get("run_date") == today and not c.get("dry_run")
        ]
    except Exception as exc:
        print(f"  ⚠️  Could not read change_history.json: {exc}")
        return []


# ---------------------------------------------------------------------------
# What changed this week, for the podcast's Sunday Meta Moment
# ---------------------------------------------------------------------------

# 'recovered' never gets here: get_feed_health_actions drops it.
_HEAL_VERBS = {
    "relocated": "Repaired the feed address of the source",
    "substituted": "Replaced an unreachable feed with a Google News search for the source",
    "retired": "Retired the source",
    "restored": "Restored the retired source",
}
CHANGE_LINE_MAX = 160


def get_week_changes(discovery_actions: list, health_actions: list,
                     calibration_changes: list) -> list[str]:
    """The week's applied changes as one-line subjects, built without a model.

    curated-podcast-generator reads these from `weekly-state-article.json` →
    `_changes`, and the Sunday Meta Moment may cite them, so they are the
    agents' own records, never the narrative (a model's reading of them).
    Source titles are chosen by the feeds' publishers and end up in a prompt,
    so every line is stripped to plain text and capped.
    """
    lines = [f"Added a new source: {feed.get('title', '?')} ({feed.get('category', 'general')})"
             for feed in discovery_actions]
    lines += [f"{_HEAL_VERBS.get(fix.get('action'), str(fix.get('action', '?')).title())} "
              f"{fix.get('title', '?')}" for fix in health_actions]
    lines += [f"Tuned {c.get('knob', '?')} from {c.get('old_value')} to {c.get('new_value')}"
              for c in calibration_changes]
    return [" ".join(plain_text(line).split())[:CHANGE_LINE_MAX] for line in lines]


ACTION_TEXT_MAX = 400


def get_week_actions(feedback_audit: dict) -> list[dict]:
    """The audit's open findings as owned actions, in the audit's order (fixer first).

    Written to `weekly-state-article.json` → `_actions`, which the podcast side's
    daily roadmap fixer reads as candidates: an `owner: "fixer"` row is a defect to
    root-cause, an `owner: "reader"` row waits on the reader and is never built for.
    Details name feed sources, and the rows end up in a prompt, so every string is
    stripped to plain text and capped, like `_changes`.
    """
    def clean(value: object) -> str:
        return " ".join(plain_text(str(value or "")).split())[:ACTION_TEXT_MAX]

    actions = []
    for f in feedback_audit.get("blind_spots") or []:
        if not f.get("action"):
            continue
        row = {
            "id": clean(f.get("id")),
            "title": clean(f.get("title")),
            "owner": "fixer" if f.get("owner") == "fixer" else "reader",
            "weeks_open": int(f.get("weeks") or 1),
            "evidence": clean(f.get("detail")),
            "action": clean(f.get("action")),
            "done_when": clean(f.get("done_when")),
            "movement": clean(f.get("movement") or "unmeasured"),
        }
        if "metric_then" in f:
            row["metric_then"], row["metric_now"] = f["metric_then"], f.get("metric_now")
        actions.append(row)
    return actions


def build_verdict_html(feedback_audit: dict) -> str:
    """The article's lead: one conclusion, then who does what next and how to tell it worked."""
    verdict = feedback_audit.get("verdict") or {}
    actions = get_week_actions(feedback_audit)
    if not verdict and not actions:
        return ""
    state = str(verdict.get("state") or "unmeasured")
    label = state + (", cycling" if verdict.get("cycling") else "")
    html = f"<h3>Verdict: {_esc(label)}</h3>\n<p>{_esc(verdict.get('headline', ''))}</p>\n"
    for owner, heading in (("fixer", "Fix next (a session can do these)"),
                           ("reader", "Yours to decide or rate")):
        rows = [a for a in actions if a["owner"] == owner]
        if not rows:
            continue
        html += f"<h4>{heading}</h4>\n<ol>\n"
        for a in rows:
            moved = (f", {a['metric_then']} → {a['metric_now']}, {a['movement']}"
                     if "metric_then" in a else "")
            html += (f"  <li><strong>{_esc(a['title'])}</strong> "
                     f"({_esc(a['weeks_open'])} week(s) open{_esc(moved)}). "
                     f"{_esc(a['action'])} <em>Done when: {_esc(a['done_when'])}.</em></li>\n")
        html += "</ol>\n"
    if not actions:
        html += "<p>Nothing open. No follow-up needed.</p>\n"
    return html


# ---------------------------------------------------------------------------
# API cost summary from FEED_LOG.md
# ---------------------------------------------------------------------------

def get_api_cost_summary() -> dict:
    """Parse FEED_LOG.md for the past 7 days and aggregate API call counts and costs."""
    log_path = Path("FEED_LOG.md")
    if not log_path.exists():
        return {}

    content = log_path.read_text("utf-8")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

    vendor_totals: dict = defaultdict(int)
    total_tokens = 0
    total_cost = 0.0
    run_costs: list = []

    for m_day in re.finditer(
        r"^## (\d{4}-\d{2}-\d{2}[^\n]*)\n(.*?)(?=^## |\Z)",
        content, re.MULTILINE | re.DOTALL,
    ):
        date_key = re.match(r"\d{4}-\d{2}-\d{2}", m_day.group(1))
        if not date_key or date_key.group() < cutoff:
            continue

        day_text = m_day.group(2)
        for m in re.finditer(
            r"API calls:\s*([\w:,\s]+?)\s*·\s*([\d,]+)\s*Claude tokens\s*·\s*est\. cost \$([\d.]+)",
            day_text,
        ):
            for vm in re.finditer(r"(\w+):(\d+)", m.group(1)):
                vendor_totals[vm.group(1).lower()] += int(vm.group(2))
            total_tokens += int(m.group(2).replace(",", ""))
            cost = float(m.group(3))
            total_cost += cost
            run_costs.append(cost)

    if not run_costs:
        return {}

    return {
        "vendor_totals": dict(vendor_totals),
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 4),
        "avg_cost_per_run": round(total_cost / len(run_costs), 4),
        "run_count": len(run_costs),
    }


# ---------------------------------------------------------------------------
# Quality review summaries (score_scrub_report.py / corpus_alignment_report.py)
# ---------------------------------------------------------------------------

def get_noise_signal_benchmark() -> list:
    """Load week-over-week noise-to-signal benchmark history from calibration_memory/benchmarks.json."""
    path = Path("calibration_memory/benchmarks.json")
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text("utf-8"))
        weeks = data.get("weeks", [])
        return sorted(weeks, key=lambda w: w.get("week_date", ""))[-8:]
    except Exception as exc:
        print(f"  ⚠️  Could not read benchmarks.json: {exc}")
        return []


def get_quality_review() -> dict:
    review = {}
    scrub_path = Path("score_scrub_summary.json")
    if scrub_path.exists():
        try:
            review["scrub"] = json.loads(scrub_path.read_text("utf-8"))
        except Exception as exc:
            print(f"  ⚠️  Could not read score_scrub_summary.json: {exc}")

    alignment_path = Path("corpus_alignment_summary.json")
    if alignment_path.exists():
        try:
            review["alignment"] = json.loads(alignment_path.read_text("utf-8"))
        except Exception as exc:
            print(f"  ⚠️  Could not read corpus_alignment_summary.json: {exc}")

    audit_path = Path("article_review_audit_summary.json")
    if audit_path.exists():
        try:
            review["feedback_audit"] = json.loads(audit_path.read_text("utf-8"))
        except Exception as exc:
            print(f"  ⚠️  Could not read article_review_audit_summary.json: {exc}")

    return review


# ---------------------------------------------------------------------------
# Git commit lookup (for the Actions Taken / rollback table)
# ---------------------------------------------------------------------------

def git_commit_for(paths: list) -> str | None:
    """Return the short SHA of the most recent commit touching any of `paths`."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--"] + paths,
        capture_output=True, text=True, check=False,
    )
    sha = result.stdout.strip()
    return sha[:7] if sha else None


# ---------------------------------------------------------------------------
# Claude Haiku narrative
# ---------------------------------------------------------------------------

def _fallback_narrative(
    week_label: str,
    stats: dict,
    new_feeds: list,
    errors: list,
    discovery: list,
    nts_benchmarks: list,
) -> str:
    """Deterministic stand-in for the Haiku narrative.

    Every other section of this report is aggregated from local files with no
    API call, so a failed narrative must not cost the whole report — which is
    exactly what happened on 2026-08-23, when an Anthropic billing error took
    down the Weekly Report job and week W34 was never published. Same facts,
    same shape, no tokens.
    """
    cat_totals = stats.get("cat_totals", {})
    ranked = sorted(
        ((c, n) for c, n in cat_totals.items() if n > 0),
        key=lambda kv: kv[1], reverse=True,
    )
    volume = (
        "; ".join(f"{cat} {count}" for cat, count in ranked[:5])
        if ranked else "no category data"
    )

    para1 = (
        f"{week_label}: {stats.get('total_runs', 0)} aggregation run(s), averaging "
        f"{stats.get('avg_fetched', 0)} articles fetched and "
        f"{stats.get('avg_quality', 0)} quality articles delivered per run. "
        f"Leading categories by volume: {volume}."
    )
    if nts_benchmarks:
        latest = nts_benchmarks[-1]
        para1 += (
            f" Pipeline efficiency held at a mean noise-to-signal ratio of "
            f"{latest.get('mean', '?')} (range {latest.get('min', '?')}"
            f"–{latest.get('max', '?')}) over "
            f"{latest.get('run_count', '?')} run(s)."
        )

    if new_feeds:
        para2 = (f"{len(new_feeds)} new feed(s) were added: "
                 + ", ".join(f["title"] for f in new_feeds[:8]) + ".")
    else:
        para2 = "No new feeds were added this week."
    if errors:
        para2 += (f" {len(errors)} feed(s) reported delivery errors: "
                  + ", ".join(e["feed"] for e in errors[:5]) + ".")
    else:
        para2 += " No feed delivery errors were recorded."
    if discovery:
        para2 += (" Top discovery candidates: "
                  + ", ".join(f"{d['title']} ({d['score']})" for d in discovery[:3]) + ".")

    para3 = (
        "This week's narrative was generated without the summarisation model — "
        "the Claude call was unavailable, so the figures above are reported "
        "directly. Every other section of this report is unaffected."
    )
    return f"{para1}\n\n{para2}\n\n{para3}"


def generate_narrative(
    client: anthropic.Anthropic | None,
    week_label: str,
    stats: dict,
    new_feeds: list,
    errors: list,
    discovery: list,
    nts_benchmarks: list,
) -> str:
    cat_summary = ", ".join(
        f"{cat}: {count} articles"
        for cat in CATEGORY_ORDER
        for count in [stats.get("cat_totals", {}).get(cat, 0)]
        if count > 0
    ) or "no category data"

    new_feeds_text = (
        ", ".join(f["title"] for f in new_feeds) if new_feeds else "no new feeds added"
    )
    error_text = (
        f"{len(errors)} feed(s) with errors: {', '.join(e['feed'] for e in errors[:5])}"
        if errors
        else "no feed errors"
    )
    discovery_parts = ["{} (score: {})".format(d["title"], d["score"]) for d in discovery]
    discovery_text = (
        "Top discovery candidates: " + ", ".join(discovery_parts)
        if discovery
        else "no discovery report available"
    )

    if nts_benchmarks:
        latest = nts_benchmarks[-1]
        nts_text = (
            f"mean {latest.get('mean', '?')} "
            f"(range {latest.get('min', '?')}–{latest.get('max', '?')}) "
            f"over {latest.get('run_count', '?')} runs"
        )
    else:
        nts_text = "no benchmark data available yet"

    prompt = (
        f"Write a brief 2–3 paragraph 'State of the Feed' weekly summary for a personal "
        f"AI-curated RSS aggregator. Be factual and concise. No conversational filler, "
        f"greetings, sign-offs, or editorial opinions. "
        f"No markdown headers or lists — flowing paragraphs only.\n\n"
        f"Week: {week_label}\n"
        f"Runs this week: {stats.get('total_runs', 0)} "
        f"(avg {stats.get('avg_fetched', 0)} articles fetched, "
        f"avg {stats.get('avg_quality', 0)} quality articles per run)\n"
        f"Category breakdown: {cat_summary}\n"
        f"Scoring model: dimensional Q/R/L composite (quality/relevance/local, weights 0.25/0.55/0.20)\n"
        f"Pipeline efficiency (noise-to-signal ratio, articles fetched per 1 delivered): {nts_text}\n"
        f"New feeds added: {new_feeds_text}\n"
        f"Feed health: {error_text}\n"
        f"Feed discovery: {discovery_text}\n\n"
        f"Report the data plainly, as a technical summary. "
        f"Mention pipeline efficiency if the noise-to-signal ratio is notably high or low."
    )

    if client is None:
        print("     ⚠️  No Anthropic client — using stats-only narrative")
        return _fallback_narrative(
            week_label, stats, new_feeds, errors, discovery, nts_benchmarks
        )

    # One paragraph of prose sits on top of a report that is otherwise pure
    # local-file aggregation. Retry once for a transient failure, then degrade
    # rather than lose the report, the permalink and the feed item with it.
    last_exc: Exception | None = None
    for attempt in range(2):
        try:
            response = client.messages.create(
                model=api_usage.HAIKU_MODEL,
                extra_body=api_usage.HAIKU_EXTRA_BODY,
                max_tokens=700,
                messages=[{"role": "user", "content": prompt}],
            )
            api_usage.record_claude_usage(response.usage)
            text = api_usage.response_text(response).strip()
            if not text:
                raise ValueError('empty response')
            return text
        except Exception as exc:
            last_exc = exc
            if attempt == 0:
                print(f"     ⚠️  Narrative call failed ({exc}); retrying once")

    print(f"     ⚠️  Narrative unavailable ({last_exc}) — using stats-only narrative")
    return _fallback_narrative(
        week_label, stats, new_feeds, errors, discovery, nts_benchmarks
    )


# ---------------------------------------------------------------------------
# HTML builders
# ---------------------------------------------------------------------------

def _esc(value: object) -> str:
    """Escape a value for the report's HTML.

    The report is published on the same origin as review.html. Feed titles and error
    text come from arbitrary third-party feeds found by search, and the narrative and
    rationale come from a model that read them, so none of it is markup we wrote.
    """
    return escape(str(value), quote=True)

def build_noise_signal_html(nts_benchmarks: list) -> str:
    if not nts_benchmarks:
        return ""
    html = "\n<h3>Pipeline Efficiency: Noise-to-Signal Ratio</h3>\n"
    html += "<p>Noise-to-signal = (articles fetched &minus; articles in final feeds) &divide; final total. Lower is more efficient.</p>\n"
    html += "<table><thead><tr><th>Week</th><th>Mean N:S</th><th>Min</th><th>Max</th><th>Runs</th></tr></thead><tbody>\n"
    for w in nts_benchmarks:
        html += (
            f"<tr><td>{_esc(w.get('week_date', '?'))}</td>"
            f"<td>{_esc(w.get('mean', '?'))}</td>"
            f"<td>{_esc(w.get('min', '?'))}</td>"
            f"<td>{_esc(w.get('max', '?'))}</td>"
            f"<td>{_esc(w.get('run_count', '?'))}</td></tr>\n"
        )
    html += "</tbody></table>"
    return html


# ---------------------------------------------------------------------------
# Charts (inline SVG, standalone page only)
#
# sanitize_feed strips <svg>, so these never go into the feed copy of the report;
# the tables further down are the table view for every chart here. No dependencies.
# Colours are CSS variables (--s1.. , --ink..) that build_html_page defines for
# light and dark; categorical slots are the validated order blue, aqua, violet, orange.
# ---------------------------------------------------------------------------

METRICS_PATH = Path("reports/weekly_metrics.jsonl")
VERDICT_SERIES = [
    ("good", "Good", "var(--s1)"),
    ("interesting", "Interesting", "var(--s2)"),
    ("podcast_only", "Podcast only", "var(--s3)"),
    ("bad", "Bad", "var(--s4)"),
]
CHART_W = 480


def get_metrics_trend(limit: int = 8) -> list:
    """The last `limit` weekly rows of reports/weekly_metrics.jsonl (one per week)."""
    if not METRICS_PATH.exists():
        return []
    rows = []
    for line in METRICS_PATH.read_text("utf-8").splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and row.get("week"):
            rows.append(row)
    return sorted(rows, key=lambda r: str(r["week"]))[-limit:]


def _num(value: object) -> float | None:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _bar_path(x: float, y: float, w: float, h: float, r: float = 4) -> str:
    """A bar anchored square on its baseline with a rounded data end (right side)."""
    w = max(w, 1.0)
    r = min(r, w, h / 2)
    return (f"M{x:.1f},{y:.1f}h{w - r:.1f}a{r:.1f},{r:.1f} 0 0 1 {r:.1f},{r:.1f}"
            f"v{h - 2 * r:.1f}a{r:.1f},{r:.1f} 0 0 1 -{r:.1f},{r:.1f}h-{w - r:.1f}z")


def _figure(title: str, caption: str, svg: str, legend: list | None = None) -> str:
    key = ""
    if legend:
        key = '<div class="legend">' + "".join(
            f'<span><i style="background:{color}"></i>{_esc(name)}</span>' for name, color in legend
        ) + "</div>"
    return (f'<figure class="chart"><figcaption><strong>{_esc(title)}</strong>'
            f'<span>{_esc(caption)}</span></figcaption>{key}{svg}</figure>\n')


def _svg(height: float, label: str, body: str) -> str:
    return (f'<svg viewBox="0 0 {CHART_W} {height:.0f}" role="img" aria-label="{_esc(label)}" '
            f'preserveAspectRatio="xMidYMid meet">{body}</svg>')


def hbar_chart_svg(rows: list, label: str, fmt: str = "{:,.0f}") -> str:
    """Ranked horizontal bars, one hue, value at the bar end. rows = [(name, value)]."""
    rows = [(n, v) for n, v in rows if v is not None]
    if not rows:
        return ""
    row_h, left, right = 30, 110, 56
    top_value = max(v for _, v in rows) or 1
    plot_w = CHART_W - left - right
    parts = []
    for i, (name, value) in enumerate(rows):
        y = 4 + i * row_h
        width = plot_w * value / top_value
        text = fmt.format(value)
        parts.append(
            f'<g><title>{_esc(name)}: {_esc(text)}</title>'
            f'<text x="{left - 10}" y="{y + 15}" class="t2" text-anchor="end">{_esc(name)}</text>'
            f'<path d="{_bar_path(left, y + 2, width, 18)}" fill="var(--s1)"/>'
            f'<text x="{left + width + 8:.1f}" y="{y + 15}" class="t1">{_esc(text)}</text></g>'
        )
    parts.append(f'<line x1="{left}" y1="2" x2="{left}" y2="{4 + len(rows) * row_h - 4}" class="axis"/>')
    return _svg(len(rows) * row_h + 8, label, "".join(parts))


def stacked_hbar_svg(rows: list, series: list, label: str) -> str:
    """100% stacked horizontal bars. rows = [(name, n, {key: count})]; shares labelled in-segment."""
    rows = [r for r in rows if r[1]]
    if not rows:
        return ""
    row_h, left, right = 36, 72, 52
    plot_w = CHART_W - left - right
    parts = []
    for i, (name, total, counts) in enumerate(rows):
        y = 4 + i * row_h
        parts.append(f'<text x="{left - 10}" y="{y + 20}" class="t2" text-anchor="end">{_esc(name)}</text>')
        x = float(left)
        for key, series_name, color in series:
            share = 100.0 * (counts.get(key) or 0) / total
            seg_w = plot_w * share / 100
            if seg_w <= 0:
                continue
            parts.append(
                f'<g><title>{_esc(name)} · {_esc(series_name)}: {counts.get(key, 0)} of {total} ({share:.0f}%)</title>'
                f'<rect x="{x:.1f}" y="{y + 3}" width="{max(seg_w - 2, 1):.1f}" height="24" fill="{color}"/>'
                + (f'<text x="{x + (seg_w - 2) / 2:.1f}" y="{y + 20}" class="on-fill" text-anchor="middle">{share:.0f}%</text>'
                   if seg_w > 30 else "")
                + "</g>"
            )
            x += seg_w
        parts.append(f'<text x="{CHART_W - right + 8}" y="{y + 20}" class="t3">n={total:,}</text>')
    return _svg(len(rows) * row_h + 8, label, "".join(parts))


def stacked_columns_svg(weeks: list, series: list, label: str) -> str:
    """100% stacked columns per week. weeks = [(label, {key: count})]; good sits on the baseline."""
    weeks = [(w, c) for w, c in weeks if sum((c.get(k) or 0) for k, _, _ in series)]
    if not weeks:
        return ""
    height, top, bottom, left, right = 250, 12, 28, 40, 12
    plot_h = height - top - bottom
    slot = (CHART_W - left - right) / len(weeks)
    col_w = min(slot * 0.7, 52)
    parts = []
    for pct in (0, 25, 50, 75, 100):
        y = top + plot_h * (1 - pct / 100)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{CHART_W - right}" y2="{y:.1f}" class="{"axis" if pct == 0 else "grid"}"/>'
                     f'<text x="{left - 6}" y="{y + 4:.1f}" class="t3" text-anchor="end">{pct}%</text>')
    for i, (week, counts) in enumerate(weeks):
        total = sum((counts.get(k) or 0) for k, _, _ in series)
        x = left + i * slot + (slot - col_w) / 2
        y = top + plot_h
        for key, name, color in series:
            n = counts.get(key) or 0
            h = plot_h * n / total
            if h <= 0:
                continue
            parts.append(
                f'<g><title>{_esc(week)} · {_esc(name)}: {n} of {total} ({100 * n / total:.0f}%)</title>'
                f'<rect x="{x:.1f}" y="{y - h + 1:.1f}" width="{col_w:.1f}" height="{max(h - 2, 1):.1f}" fill="{color}"/>'
                + (f'<text x="{x + col_w / 2:.1f}" y="{y - h / 2 + 4:.1f}" class="on-fill" text-anchor="middle">{100 * n / total:.0f}</text>'
                   if h > 17 else "") + "</g>"
            )
            y -= h
        parts.append(f'<text x="{x + col_w / 2:.1f}" y="{height - 8}" class="t3" text-anchor="middle">{_esc(week)}</text>')
    return _svg(height, label, "".join(parts))


def line_chart_svg(points: list, label: str, fmt: str = "{:.2f}", band: list | None = None) -> str:
    """One line over weeks, optional min–max band, last point labelled. points = [(x_label, value)]."""
    points = [(x, _num(v)) for x, v in points]
    if sum(v is not None for _, v in points) < 2:
        return ""
    height, top, bottom, left, right = 220, 14, 28, 46, 52
    plot_w, plot_h = CHART_W - left - right, height - top - bottom
    highs = [_num(b[1]) for b in (band or []) if b and _num(b[1]) is not None]
    top_value = max([v for _, v in points if v is not None] + highs) * 1.1 or 1
    step = plot_w / max(len(points) - 1, 1)

    def px(i: int) -> float:
        return left + i * step

    def py(v: float) -> float:
        return top + plot_h * (1 - v / top_value)

    parts = []
    for frac in (0, 0.5, 1):
        v = top_value / 1.1 * frac
        y = py(v)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{CHART_W - right}" y2="{y:.1f}" class="{"axis" if frac == 0 else "grid"}"/>'
                     f'<text x="{left - 6}" y="{y + 4:.1f}" class="t3" text-anchor="end">{_esc(fmt.format(v))}</text>')
    if band:
        pairs = [(i, _num(b[0]), _num(b[1])) for i, b in enumerate(band) if b and _num(b[0]) is not None and _num(b[1]) is not None]
        if len(pairs) > 1:
            upper = " ".join(f"{px(i):.1f},{py(hi):.1f}" for i, _, hi in pairs)
            lower = " ".join(f"{px(i):.1f},{py(lo):.1f}" for i, lo, _ in reversed(pairs))
            parts.append(f'<polygon points="{upper} {lower}" fill="var(--s1)" opacity="0.16"/>')
    coords = [(i, v) for i, (_, v) in enumerate(points) if v is not None]
    parts.append('<polyline fill="none" stroke="var(--s1)" stroke-width="2" stroke-linejoin="round" points="'
                 + " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in coords) + '"/>')
    for i, v in coords:
        parts.append(f'<g><title>{_esc(points[i][0])}: {_esc(fmt.format(v))}</title>'
                     f'<circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="4" fill="var(--s1)" stroke="var(--surface)" stroke-width="2"/></g>')
        parts.append(f'<text x="{px(i):.1f}" y="{height - 8}" class="t3" text-anchor="middle">{_esc(points[i][0])}</text>')
    last_i, last_v = coords[-1]
    parts.append(f'<text x="{px(last_i) + 10:.1f}" y="{py(last_v) + 4:.1f}" class="t1">{_esc(fmt.format(last_v))}</text>')
    return _svg(height, label, "".join(parts))


def auc_dot_svg(signals: list, label: str) -> str:
    """Dot plot of AUC per signal against the 0.5 coin-flip line. signals = [(name, auc, auc_news)]."""
    signals = [s for s in signals if _num(s[1]) is not None or _num(s[2]) is not None]
    if not signals:
        return ""
    row_h, left, right = 34, 200, 16
    lo, hi = 0.4, 0.8
    plot_w = CHART_W - left - right

    def px(v: float) -> float:
        return left + plot_w * (min(max(v, lo), hi) - lo) / (hi - lo)

    height = len(signals) * row_h + 30
    parts = []
    for v in (0.4, 0.5, 0.6, 0.7, 0.8):
        parts.append(f'<line x1="{px(v):.1f}" y1="4" x2="{px(v):.1f}" y2="{height - 26}" class="{"ref" if v == 0.5 else "grid"}"/>'
                     f'<text x="{px(v):.1f}" y="{height - 8}" class="t3" text-anchor="middle">{v:.1f}</text>')
    parts.append(f'<text x="{px(0.5) - 4:.1f}" y="14" class="t3" text-anchor="end">coin flip</text>')
    for i, (name, auc, auc_news) in enumerate(signals):
        y = 22 + i * row_h
        parts.append(f'<text x="{left - 10}" y="{y + 4}" class="t2" text-anchor="end">{_esc(name)}</text>')
        a, n = _num(auc), _num(auc_news)
        if a is not None and n is not None:
            parts.append(f'<line x1="{px(a):.1f}" y1="{y}" x2="{px(n):.1f}" y2="{y}" class="grid" stroke-width="3"/>')
        for value, color, kind in ((a, "var(--s1)", "all ratings"), (n, "var(--s4)", "news only")):
            if value is not None:
                parts.append(f'<g><title>{_esc(name)} · {kind}: AUC {value:.3f}</title>'
                             f'<circle cx="{px(value):.1f}" cy="{y}" r="6" fill="{color}" stroke="var(--surface)" stroke-width="2"/></g>')
    return _svg(height, label, "".join(parts))


def build_charts_html(
    stats: dict,
    nts_benchmarks: list,
    api_cost: dict,
    quality_review: dict,
    trend: list,
) -> str:
    """The report's at-a-glance charts; each reads data the tables below already show."""
    audit = quality_review.get("feedback_audit") or {}
    figures = []

    cat_totals = stats.get("cat_totals") or {}
    rows = sorted(((c, cat_totals.get(c, 0)) for c in CATEGORY_ORDER if cat_totals.get(c)), key=lambda r: -r[1])
    svg = hbar_chart_svg(rows, "Articles per category this week, largest first")
    if svg:
        figures.append(_figure("Where the articles went",
                               f"Articles per category over {stats.get('total_runs', 0)} nightly runs", svg))

    weeks = [(str(r["week"]).split("-")[-1], r.get("verdicts") or {}) for r in trend]
    svg = stacked_columns_svg(weeks, VERDICT_SERIES, "Share of each week's ratings by verdict")
    if svg:
        figures.append(_figure("What you thought, week by week",
                               "Share of rated articles by verdict. The review batch is a quota sample, so read the trend, not the level.",
                               svg, [(n, c) for _, n, c in VERDICT_SERIES]))

    # Band rows carry good / interesting / bad; what is left of n is podcast_only.
    band_rows = []
    for b in audit.get("band_precision") or []:
        n = b.get("n") or 0
        counts = {k: b.get(k) or 0 for k in ("good", "interesting", "bad")}
        counts["podcast_only"] = max(n - sum(counts.values()), 0)
        band_rows.append((str(b.get("band")), n, counts))
    svg = stacked_hbar_svg(band_rows, VERDICT_SERIES, "Verdict share by pipeline score band")
    if svg:
        figures.append(_figure("Do higher scores earn better ratings?",
                               "Verdicts by score band. The good + interesting share should climb with the score.",
                               svg, [(n, c) for _, n, c in VERDICT_SERIES]))

    signals = ((audit.get("scorecard") or {}).get("signals") or {}).values()
    svg = auc_dot_svg([(s.get("name", "?"), s.get("auc"), s.get("auc_news")) for s in signals],
                      "AUC per scoring signal against the 0.5 coin-flip line")
    if svg:
        figures.append(_figure("What each score buys",
                               "AUC: 0.5 is a coin flip, 1.0 is perfect. Further right is better.",
                               svg, [("All ratings", "var(--s1)"), ("News only", "var(--s4)")]))

    svg = line_chart_svg([(str(r["week"]).split("-")[-1], r.get("est_cost_usd_7d")) for r in trend],
                         "Estimated Claude cost per week in US dollars", fmt="${:.2f}")
    if svg:
        figures.append(_figure("Weekly Claude cost", "Estimated spend over the trailing 7 days, in USD", svg))

    stages = ((audit.get("stage_costs") or {}).get("by_stage") or {})
    svg = hbar_chart_svg(
        sorted(((s, _num(c.get("est_cost_usd")) or 0.0) for s, c in stages.items()), key=lambda r: -r[1]),
        "Estimated Claude cost by pipeline stage, last 7 days", fmt="${:.2f}")
    if svg:
        figures.append(_figure("Cost by stage", "Last 7 days, estimated", svg))

    svg = line_chart_svg(
        [(str(w.get("week_date", "?"))[5:], w.get("mean")) for w in nts_benchmarks],
        "Mean noise-to-signal ratio per week with min–max range",
        band=[(w.get("min"), w.get("max")) for w in nts_benchmarks])
    if svg:
        figures.append(_figure("Noise-to-signal",
                               "Weekly mean with the min–max band across runs; lower is more efficient", svg))

    if not figures:
        return ""
    return ('\n<h3>At a glance</h3>\n<div class="charts">\n' + "".join(figures)
            + '</div>\n<p class="meta">Every chart has its table below.</p>\n')


def build_content_html(
    narrative: str,
    stats: dict,
    new_feeds: list,
    errors: list,
    discovery: list,
    calibration_changes: list,
    quality_review: dict,
    actions: list,
    nts_benchmarks: list,
    api_cost: dict,
    charts_html: str = "",
) -> str:
    parts = [f"<p>{_esc(p.strip())}</p>" for p in narrative.split("\n\n") if p.strip()]
    # The conclusion leads; the narrative and tables below are its evidence.
    html = build_verdict_html(quality_review.get("feedback_audit") or {}) + "\n".join(parts) + charts_html

    if new_feeds:
        html += "\n<h3>New Feeds This Week</h3>\n<ul>\n"
        for feed in new_feeds:
            html += f"  <li>{_esc(feed['title'])}</li>\n"
        html += "</ul>"

    cat_totals = stats.get("cat_totals", {})
    if cat_totals:
        html += "\n<h3>Weekly Article Distribution</h3>\n"
        html += "<table><thead><tr><th>Category</th><th>Articles</th></tr></thead><tbody>\n"
        for cat in CATEGORY_ORDER:
            count = cat_totals.get(cat, 0)
            if count:
                html += f"<tr><td>{_esc(cat)}</td><td>{_esc(count)}</td></tr>\n"
        html += "</tbody></table>"

    if errors:
        html += "\n<h3>Feed Issues</h3>\n<ul>\n"
        for err in errors[:5]:
            html += f"  <li><strong>{_esc(err['feed'])}</strong>: {_esc(err['error'])}</li>\n"
        html += "</ul>"

    if discovery:
        html += "\n<h3>Discovery Highlights</h3>\n<ul>\n"
        for d in discovery:
            html += f"  <li>{_esc(d['title'])} (score: {_esc(d['score'])})</li>\n"
        html += "</ul>"

    html += build_noise_signal_html(nts_benchmarks)
    html += build_quality_review_html(quality_review)
    html += build_api_cost_html(api_cost)
    html += build_calibration_html(calibration_changes)
    html += build_actions_html(actions)

    return html


def build_quality_review_html(quality_review: dict) -> str:
    scrub = quality_review.get("scrub")
    alignment = quality_review.get("alignment")
    feedback_audit = quality_review.get("feedback_audit")
    if not scrub and not alignment and not feedback_audit:
        return ""

    html = "\n<h3>Quality Review</h3>\n"

    if scrub:
        flagged = scrub.get("flagged_count", 0)
        to_remove = scrub.get("flagged_remove_count", 0)
        html += (
            f"<p>{scrub.get('total_articles', 0)} articles across "
            f"{len(scrub.get('feeds', {}))} feeds. "
        )
        if scrub.get("scrub_ran"):
            html += f"Scrub pass flagged {flagged} article(s), {to_remove} recommended for removal.</p>\n"
        else:
            html += "Scrub pass not run (stats only).</p>\n"

        html += "<table><thead><tr><th>Feed</th><th>Articles</th><th>Avg composite</th><th>Stale</th><th>Top source</th></tr></thead><tbody>\n"
        for feed in scrub.get("feeds", {}).values():
            html += (
                f"<tr><td>{_esc(feed['title'])}</td><td>{_esc(feed['count'])}</td>"
                f"<td>{_esc(feed['avg_score'])}</td><td>{_esc(feed['stale_count'])}</td>"
                f"<td>{_esc(feed['top_source'])} ({_esc(feed['top_source_pct'])}%)</td></tr>\n"
            )
        html += "</tbody></table>"

    if alignment:
        html += (
            f"<p>Corpus alignment: {alignment.get('total_articles', 0)} articles analysed — "
            f"{alignment.get('total_direct', 0)} direct-qualify, "
            f"{alignment.get('total_rescue', 0)} rescue-dependent, "
            f"{alignment.get('total_stranded', 0)} stranded, "
            f"{alignment.get('total_filler', 0)} filler "
            f"({alignment.get('total_filler_pct', 0)}%)."
        )
        report_date = str(alignment.get("generated", "")).split(" ")[0]
        if re.match(r"^\d{4}-\d{2}-\d{2}$", report_date):
            report_url = f"{GITHUB_REPO_URL}/blob/main/reports/CORPUS_ALIGNMENT_REPORT_{report_date}.md"
            html += f' <a href="{report_url}">Full report</a>.'
        html += "</p>\n"
        if alignment.get("content_type_breakdown"):
            ct_text = ", ".join(
                f"{ct}: {n}"
                for ct, n in sorted(alignment["content_type_breakdown"].items(), key=lambda x: -x[1])
            )
            html += f"<p>Content type breakdown: {_esc(ct_text)}.</p>\n"

    if feedback_audit:
        counts = feedback_audit.get("counts", {})
        routing = feedback_audit.get("theme_routing", {})
        window = feedback_audit.get("window", {})
        weighted = (feedback_audit.get("stratified") or {}).get("weighted_positive_pct")
        html += "\n<h3>User Feedback Audit</h3>\n"
        html += (
            f"<p>{feedback_audit.get('total_rated', 0)} articles rated "
            f"({_esc(window.get('first', '?'))} → {_esc(window.get('last', '?'))}): "
            f"{counts.get('good', 0)} good, {counts.get('interesting', 0)} interesting, "
            f"{counts.get('podcast_only', 0)} podcast only, {counts.get('bad', 0)} bad. "
        )
        # The raw rates describe the review quota, not the feed; only the
        # reweighted shipped-feed rate is a quality figure.
        if weighted is not None:
            html += f"Shipped feed, reweighted: {_esc(weighted)}% good or interesting. "
        html += (
            f"Theme-day corrections: {routing.get('corrections', 0)} of "
            f"{routing.get('rated_with_day', 0)} ({routing.get('correction_pct', 0)}%)."
        )
        report_date = str(feedback_audit.get("generated_at", "")).split(" ")[0]
        if re.match(r"^\d{4}-\d{2}-\d{2}$", report_date):
            report_url = f"{GITHUB_REPO_URL}/blob/main/reports/ARTICLE_REVIEW_AUDIT_{report_date}.md"
            html += f' <a href="{report_url}">Full audit</a>.'
        html += "</p>\n"
        html += build_audit_findings_html(feedback_audit)
        bands = feedback_audit.get("band_precision") or []
        if bands:
            html += (
                "<table><thead><tr><th>Score band</th><th>Rated</th><th>% good</th>"
                "<th>% good+interesting</th><th>% bad</th></tr></thead><tbody>\n"
            )
            for band in bands:
                html += (
                    f"<tr><td>{_esc(band.get('band'))}</td><td>{_esc(band.get('n'))}</td>"
                    f"<td>{_esc(band.get('good_pct'))}</td><td>{_esc(band.get('positive_pct', ''))}</td>"
                    f"<td>{_esc(band.get('bad_pct'))}</td></tr>\n"
                )
            html += "</tbody></table>"

    return html


def build_audit_findings_html(feedback_audit: dict) -> str:
    """The audit's multi-week findings and what each paid score buys, from its summary."""
    html = ""
    findings = feedback_audit.get("blind_spots") or []
    if findings:
        html += "<h4>Needs attention</h4>\n<ul>\n"
        for f in findings:
            weeks = f.get("weeks", 1)
            repeat = f" <strong>({_esc(weeks)} weeks running)</strong>" if f.get("escalate") else ""
            html += f"  <li><strong>{_esc(f.get('title'))}</strong>{repeat}: {_esc(f.get('detail'))}</li>\n"
        html += "</ul>\n"

    closed = feedback_audit.get("closed_findings") or []
    if closed:
        html += "<h4>Closed this week</h4>\n<ul>\n"
        for c in closed:
            changes = "; ".join(c.get("calibration_changes") or []) or "no calibration change logged"
            html += (f"  <li><strong>{_esc(c.get('title'))}</strong>: open {_esc(c.get('weeks'))} "
                     f"week(s) from {_esc(c.get('opened'))}; {_esc(changes)}</li>\n")
        html += "</ul>\n"

    card = feedback_audit.get("scorecard") or {}
    signals = card.get("signals") or {}
    if signals:
        def cell(value) -> str:
            return _esc(value) if value is not None else "too few"
        html += (
            f"<h4>What each score buys</h4>\n<p>Last {_esc(card.get('weeks'))} weeks, "
            f"{_esc(card.get('n'))} ratings. AUC: 0.5 is a coin flip, 1.0 perfect.</p>\n"
            "<table><thead><tr><th>Signal</th><th>Paid by</th><th>AUC</th><th>AUC, news</th>"
            "</tr></thead><tbody>\n"
        )
        for sig in signals.values():
            html += (f"<tr><td>{_esc(sig.get('name'))}</td><td>{_esc(sig.get('stage'))}</td>"
                     f"<td>{cell(sig.get('auc'))}</td><td>{cell(sig.get('auc_news'))}</td></tr>\n")
        html += "</tbody></table>"

    stages = (feedback_audit.get("stage_costs") or {}).get("by_stage") or {}
    if stages:
        html += ("\n<h4>Claude cost by stage (7 days)</h4>\n<table><thead><tr><th>Stage</th>"
                 "<th>Calls</th><th>Est. cost</th></tr></thead><tbody>\n")
        for stage, c in stages.items():
            html += (f"<tr><td>{_esc(stage)}</td><td>{_esc(c.get('calls'))}</td>"
                     f"<td>${float(c.get('est_cost_usd') or 0):.4f}</td></tr>\n")
        html += "</tbody></table>"
    return html


def build_calibration_html(calibration_changes: list) -> str:
    html = "\n<h3>Calibration</h3>\n"
    if not calibration_changes:
        return html + "<p>No config changes applied this run.</p>\n"

    html += "<table><thead><tr><th>Knob</th><th>Old</th><th>New</th><th>Rationale</th></tr></thead><tbody>\n"
    for c in calibration_changes:
        html += (
            f"<tr><td>{_esc(c.get('knob', '?'))}</td><td>{_esc(c.get('old_value'))}</td>"
            f"<td>{_esc(c.get('new_value'))}</td><td>{_esc(c.get('rationale', ''))}</td></tr>\n"
        )
    html += "</tbody></table>"
    return html


def build_api_cost_html(api_cost: dict) -> str:
    if not api_cost:
        return ""

    VENDOR_ORDER = ["claude", "cohere", "brave", "kagi"]

    vendor_totals = api_cost.get("vendor_totals", {})
    run_count = api_cost.get("run_count", 1)
    # The per-call rates are api_usage's, the ones the run estimates were made with.
    # A copy here said Brave was free for weeks after api_usage started pricing it.
    flat_cost = sum(n * FLAT_COST_PER_CALL.get(v, 0.0) for v, n in vendor_totals.items() if v != "claude")

    html = "\n<h3>API Cost Review</h3>\n"
    html += (
        f"<p>{run_count} run(s) this week &middot; "
        f"total est. cost <strong>${api_cost['total_cost']:.4f}</strong> &middot; "
        f"avg <strong>${api_cost['avg_cost_per_run']:.4f}</strong>/run &middot; "
        f"{api_cost['total_tokens']:,} Claude tokens</p>\n"
    )

    html += "<table><thead><tr><th>Vendor</th><th>Calls (week)</th><th>Avg/run</th><th>Rate</th><th>Est. weekly cost</th></tr></thead><tbody>\n"
    ordered = [v for v in VENDOR_ORDER if v in vendor_totals]
    ordered += [v for v in sorted(vendor_totals) if v not in VENDOR_ORDER]
    for vendor in ordered:
        calls = vendor_totals[vendor]
        avg = round(calls / run_count, 1)
        if vendor == "claude":
            rate_str = "token-based"
            cost_str = f"${max(api_cost['total_cost'] - flat_cost, 0.0):.4f}"
        else:
            rate = FLAT_COST_PER_CALL.get(vendor, 0.0)
            rate_str = f"${rate:.4f}/call" if rate else "free"
            cost_str = f"${calls * rate:.4f}" if rate else "$0"
        html += (
            f"<tr><td>{_esc(vendor.title())}</td><td>{calls:,}</td>"
            f"<td>{avg}</td><td>{rate_str}</td><td>{cost_str}</td></tr>\n"
        )
    html += "</tbody></table>"
    return html


def build_actions_html(actions: list) -> str:
    html = "\n<h3>Actions Taken This Week</h3>\n"
    if not actions:
        return html + "<p>No config or feed-list changes this week.</p>\n"

    html += (
        "<table><thead><tr><th>Component</th><th>Action</th><th>Commit</th></tr></thead><tbody>\n"
    )
    for a in actions:
        if a.get("commit"):
            commit_cell = (
                f'<a href="{GITHUB_REPO_URL}/commit/{_esc(a["commit"])}"><code>{_esc(a["commit"])}</code></a>'
                f' (<code>git revert {_esc(a["commit"])}</code> to undo)'
            )
        else:
            commit_cell = "—"
        html += (
            f"<tr><td>{_esc(a['component'])}</td><td>{_esc(a['action'])}</td><td>{commit_cell}</td></tr>\n"
        )
    html += "</tbody></table>"
    return html


def build_html_page(title: str, content_html: str, week_label: str, pub_date: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #fcfcfb; --ink: #0b0b0b; --ink2: #52514e; --ink3: #898781; --link: #0066cc;
      --line: #e1e0d9; --axis: #c3c2b7; --th: #f3f2ef; --surface: #fcfcfb;
      --s1: #2a78d6; --s2: #1baf7a; --s3: #6250d6; --s4: #eb6834;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #1a1a19; --ink: #f0efec; --ink2: #c3c2b7; --ink3: #898781; --link: #6da7ec;
        --line: #2c2c2a; --axis: #383835; --th: #232321; --surface: #1a1a19;
        --s1: #3987e5; --s2: #199e70; --s3: #9085e9; --s4: #d95926;
      }}
    }}
    body {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; color: var(--ink); background: var(--bg); }}
    h1 {{ border-bottom: 2px solid var(--ink); padding-bottom: 0.5rem; font-size: 1.6rem; }}
    h3 {{ margin-top: 1.5rem; font-size: 1.1rem; color: var(--ink2); }}
    table {{ border-collapse: collapse; width: 100%; margin: 0.5rem 0; }}
    th, td {{ border: 1px solid var(--line); padding: 0.4rem 0.8rem; text-align: left; }}
    th {{ background: var(--th); }}
    .meta {{ color: var(--ink2); font-size: 0.9rem; margin-bottom: 1.5rem; }}
    a {{ color: var(--link); }}
    ul {{ padding-left: 1.4rem; }}
    li {{ margin: 0.25rem 0; }}
    .charts {{ display: grid; gap: 1rem; grid-template-columns: 1fr; }}
    .chart {{ margin: 0; padding: 0.9rem 1rem 0.6rem; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; }}
    .chart figcaption {{ display: flex; flex-direction: column; margin-bottom: 0.4rem; line-height: 1.35; }}
    .chart figcaption span {{ color: var(--ink2); font-size: 0.85rem; }}
    .chart svg {{ width: 100%; max-width: 560px; height: auto; display: block; margin: 0 auto; }}
    .legend {{ display: flex; flex-wrap: wrap; gap: 0.3rem 1rem; font-size: 0.8rem; color: var(--ink2); margin-bottom: 0.3rem; }}
    .legend i {{ display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 0.35rem; }}
    svg text {{ font-family: inherit; font-size: 13px; fill: var(--ink2); }}
    svg .t1 {{ fill: var(--ink); font-weight: 600; }}
    svg .t3 {{ fill: var(--ink3); font-size: 12px; }}
    svg .on-fill {{ fill: #fff; font-size: 12px; font-weight: 600; }}
    svg .grid {{ stroke: var(--line); stroke-width: 1; }}
    svg .axis {{ stroke: var(--axis); stroke-width: 1; }}
    svg .ref {{ stroke: var(--ink3); stroke-width: 1; stroke-dasharray: 4 3; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <p class="meta">Published {pub_date} &middot; <a href="{BASE_URL}">Back to feed</a></p>
  {content_html}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY not set — report will use a stats-only narrative")

    now = datetime.now(timezone.utc)
    iso_year, iso_week, _ = now.isocalendar()

    # Week date range label (Mon–Sun)
    week_start = now - timedelta(days=now.weekday())
    week_end = week_start + timedelta(days=6)
    week_label = f"Week of {week_start.strftime('%B %-d')}–{week_end.strftime('%-d, %Y')}"

    article_slug = f"weekly-report-{iso_year}-W{iso_week:02d}"
    article_url = f"{BASE_URL}/{article_slug}.html"
    pub_date_iso = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    pub_date_human = now.strftime("%B %-d, %Y")
    title = f"State of the Feed — {week_label}"

    print(f"📊 Generating: {title}")

    print("  → Detecting new feeds...")
    new_feeds = get_new_feeds_this_week()
    print(f"     {len(new_feeds)} new feed(s): {[f['title'] for f in new_feeds]}")

    print("  → Aggregating weekly stats from FEED_LOG.md...")
    stats = get_weekly_stats()
    print(f"     {stats.get('total_runs', 0)} runs, avg quality {stats.get('avg_quality', 0)}")

    print("  → Reading feed errors from TODO.md...")
    errors = get_current_errors()
    print(f"     {len(errors)} error(s)")

    print("  → Reading feed_discovery_report.json...")
    discovery = get_discovery_highlights()
    print(f"     {len(discovery)} discovery candidate(s)")

    print("  → Reading discovery_actions.json...")
    discovery_actions = get_discovery_actions()
    print(f"     {len(discovery_actions)} feed(s) auto-added")

    print("  → Reading feed_health_actions.json...")
    health_actions = get_feed_health_actions()
    print(f"     {len(health_actions)} feed health fix(es)")

    print("  → Reading calibration_memory/change_history.json...")
    today = now.strftime("%Y-%m-%d")
    calibration_changes = get_calibration_changes(today)
    print(f"     {len(calibration_changes)} config change(s) applied today")

    print("  → Reading calibration_memory/benchmarks.json...")
    nts_benchmarks = get_noise_signal_benchmark()
    print(f"     {len(nts_benchmarks)} week(s) of noise-to-signal benchmark data")

    print("  → Reading quality review summaries...")
    quality_review = get_quality_review()
    print(f"     scrub={'scrub' in quality_review}, alignment={'alignment' in quality_review}")

    print("  → Aggregating API cost data from FEED_LOG.md...")
    api_cost = get_api_cost_summary()
    if api_cost:
        print(f"     {api_cost['run_count']} run(s), total est. cost ${api_cost['total_cost']:.4f}")

    print("  → Building actions taken / rollback table...")
    actions = []
    if discovery_actions:
        commit = git_commit_for(["feeds.opml"])
        for feed in discovery_actions:
            actions.append({
                "component": "Discovery",
                "action": f"Added feed “{feed['title']}” ({feed.get('category', '—')}, score {feed.get('score', 0)})",
                "commit": commit,
            })
    if health_actions:
        commit = git_commit_for(["feeds.opml", "FEED_HEALTH_LOG.md"])
        for fix in health_actions:
            target = f" → {fix['new_url']}" if fix.get("new_url") else ""
            actions.append({
                "component": "Feed health",
                "action": (f"{fix.get('action', '?').title()} “{fix.get('title', '?')}”"
                           f"{target} ({fix.get('reason', '')}; {fix.get('evidence', '')})"),
                "commit": commit,
            })
    if calibration_changes:
        commit = git_commit_for([
            "config/limits.json", "config/podcast_schedule.json",
            "config/source_preferences.json", "config/feed_slots.json",
        ])
        for c in calibration_changes:
            actions.append({
                "component": "Calibration",
                "action": f"{c.get('knob', '?')}: {c.get('old_value')} → {c.get('new_value')}",
                "commit": commit,
            })
    print(f"     {len(actions)} action(s) this week")

    print("  → Generating narrative with Claude Haiku...")
    client = anthropic.Anthropic(api_key=api_key) if api_key else None
    narrative = generate_narrative(client, week_label, stats, new_feeds, errors, discovery, nts_benchmarks)

    content_html = build_content_html(
        narrative, stats, new_feeds, errors, discovery,
        calibration_changes, quality_review, actions,
        nts_benchmarks, api_cost,
    )
    # The permalink page also gets the SVG charts; the feed copy can't carry them.
    page_content_html = build_content_html(
        narrative, stats, new_feeds, errors, discovery,
        calibration_changes, quality_review, actions,
        nts_benchmarks, api_cost,
        charts_html=build_charts_html(stats, nts_benchmarks, api_cost, quality_review, get_metrics_trend()),
    )

    # JSON Feed article item
    article = {
        "id": article_url,
        "url": article_url,
        "title": title,
        "content_html": content_html,
        "date_published": pub_date_iso,
        "authors": [{"name": "AI Feed Curator", "url": BASE_URL}],
        "_score": 99,
        "_changes": get_week_changes(discovery_actions, health_actions, calibration_changes),
        "_verdict": (quality_review.get("feedback_audit") or {}).get("verdict") or {},
        "_actions": get_week_actions(quality_review.get("feedback_audit") or {}),
    }
    print(f"     {len(article['_changes'])} change line(s) for the podcast's Meta Moment")
    print(f"     {len(article['_actions'])} open action(s) for the roadmap fixer; "
          f"verdict: {article['_verdict'].get('state', 'none')}")

    # Persist article to repo root (committed to main; referenced by generate-feed deploys)
    atomic_write_json("weekly-state-article.json", article, indent=2, ensure_ascii=False)

    # HTML permalink — written to both reports/ (for generate-feed.yml to copy) and output/
    html_page = build_html_page(title, page_content_html, week_label, pub_date_human)
    html_filename = f"{article_slug}.html"
    Path("reports").mkdir(exist_ok=True)
    atomic_write_text(str(Path("reports") / html_filename), html_page)

    # Fetch current feed-news.json from GitHub Pages and prepend the article
    OUTPUT_DIR.mkdir(exist_ok=True)

    try:
        resp = requests.get(FEED_NEWS_URL, timeout=30)
        resp.raise_for_status()
        feed_news = resp.json()
        print(f"  ✓ Downloaded feed-news.json ({len(feed_news.get('items', []))} existing items)")
    except Exception as exc:
        print(f"  ⚠️  Could not fetch feed-news.json ({exc}), creating fresh wrapper")
        feed_news = {
            "version": "https://jsonfeed.org/version/1.1",
            "title": "News",
            "home_page_url": BASE_URL,
            "feed_url": f"{BASE_URL}/feed-news.json",
            "description": "AI-curated news articles",
            "author": {"name": "Erich's AI Curator"},
            "items": [],
        }

    # Remove any existing weekly report for this ISO week (idempotent re-runs)
    items = [
        i for i in feed_news.get("items", [])
        if not i.get("id", "").endswith(f"weekly-report-{iso_year}-W{iso_week:02d}.html")
    ]
    # `_changes` is for the podcast, which reads the committed file, not feed readers.
    feed_news["items"] = [{k: v for k, v in article.items()
                           if k not in ("_changes", "_verdict", "_actions")}] + items

    feed_news_out = OUTPUT_DIR / "feed-news.json"
    # The downloaded items are third-party content like any other feed's.
    sanitize_feed(feed_news, "feed-news.json")
    atomic_write_json(feed_news_out, feed_news, indent=2, ensure_ascii=False)
    html_out = OUTPUT_DIR / html_filename
    atomic_write_text(str(html_out), html_page)

    print(f"  ✓ output/feed-news.json ({len(feed_news['items'])} items)")
    print(f"  ✓ output/{html_filename}")
    print(f"  ✓ reports/{html_filename}")
    print(f"  ✓ weekly-state-article.json (repo root)")
    print(f"\n✅ Weekly report complete → {article_url}")


if __name__ == "__main__":
    main()
