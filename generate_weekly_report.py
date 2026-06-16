#!/usr/bin/env python3
"""Generate a weekly "State of the Feed" article and inject it into feed-news.json.

Runs every Sunday at 13:15 UTC (after discover-feeds @ 10:00 UTC and
generate-feed @ 12:30 UTC have both completed).

Outputs:
  output/feed-news.json              — feed-news with the new article prepended
  output/weekly-report-YYYY-Www.html — standalone HTML permalink
  weekly-report-YYYY-Www.html        — committed to main so generate-feed persists it
  weekly-state-article.json          — committed to main for reference
"""

import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

import anthropic
import requests

BASE_URL = "https://zirnhelt.github.io/super-rss-feed"
GITHUB_REPO_URL = "https://github.com/zirnhelt/super-rss-feed"
FEED_NEWS_URL = f"{BASE_URL}/feed-news.json"
OUTPUT_DIR = Path("output")
CATEGORY_ORDER = ["local", "ai-tech", "climate", "homelab", "wellness", "science", "scifi", "news"]


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
            r"(local|ai-tech|climate|homelab|wellness|news|science|scifi):(\d+)\(", day_text
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
        candidates = data.get("candidates") or data.get("feeds") or []
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
# Quality review summaries (score_scrub_report.py / corpus_alignment_report.py)
# ---------------------------------------------------------------------------

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

def generate_narrative(
    client: anthropic.Anthropic,
    week_label: str,
    stats: dict,
    new_feeds: list,
    errors: list,
    discovery: list,
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
        f"New feeds added: {new_feeds_text}\n"
        f"Feed health: {error_text}\n"
        f"Feed discovery: {discovery_text}\n\n"
        f"Report the data plainly, as a technical summary."
    )

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


# ---------------------------------------------------------------------------
# HTML builders
# ---------------------------------------------------------------------------

def build_content_html(
    narrative: str,
    stats: dict,
    new_feeds: list,
    errors: list,
    discovery: list,
    calibration_changes: list,
    quality_review: dict,
    actions: list,
) -> str:
    parts = [f"<p>{p.strip()}</p>" for p in narrative.split("\n\n") if p.strip()]
    html = "\n".join(parts)

    if new_feeds:
        html += "\n<h3>New Feeds This Week</h3>\n<ul>\n"
        for feed in new_feeds:
            html += f"  <li>{feed['title']}</li>\n"
        html += "</ul>"

    cat_totals = stats.get("cat_totals", {})
    if cat_totals:
        html += "\n<h3>Weekly Article Distribution</h3>\n"
        html += "<table><thead><tr><th>Category</th><th>Articles</th></tr></thead><tbody>\n"
        for cat in CATEGORY_ORDER:
            count = cat_totals.get(cat, 0)
            if count:
                html += f"<tr><td>{cat}</td><td>{count}</td></tr>\n"
        html += "</tbody></table>"

    if errors:
        html += "\n<h3>Feed Issues</h3>\n<ul>\n"
        for err in errors[:5]:
            html += f"  <li><strong>{err['feed']}</strong>: {err['error']}</li>\n"
        html += "</ul>"

    if discovery:
        html += "\n<h3>Discovery Highlights</h3>\n<ul>\n"
        for d in discovery:
            html += f"  <li>{d['title']} (score: {d['score']})</li>\n"
        html += "</ul>"

    html += build_quality_review_html(quality_review)
    html += build_calibration_html(calibration_changes)
    html += build_actions_html(actions)

    return html


def build_quality_review_html(quality_review: dict) -> str:
    scrub = quality_review.get("scrub")
    alignment = quality_review.get("alignment")
    if not scrub and not alignment:
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
                f"<tr><td>{feed['title']}</td><td>{feed['count']}</td>"
                f"<td>{feed['avg_score']}</td><td>{feed['stale_count']}</td>"
                f"<td>{feed['top_source']} ({feed['top_source_pct']}%)</td></tr>\n"
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
            report_url = f"{GITHUB_REPO_URL}/blob/main/CORPUS_ALIGNMENT_REPORT_{report_date}.md"
            html += f' <a href="{report_url}">Full report</a>.'
        html += "</p>\n"
        if alignment.get("content_type_breakdown"):
            ct_text = ", ".join(
                f"{ct}: {n}"
                for ct, n in sorted(alignment["content_type_breakdown"].items(), key=lambda x: -x[1])
            )
            html += f"<p>Content type breakdown: {ct_text}.</p>\n"

    return html


def build_calibration_html(calibration_changes: list) -> str:
    html = "\n<h3>Calibration</h3>\n"
    if not calibration_changes:
        return html + "<p>No config changes applied this run.</p>\n"

    html += "<table><thead><tr><th>Knob</th><th>Old</th><th>New</th><th>Rationale</th></tr></thead><tbody>\n"
    for c in calibration_changes:
        html += (
            f"<tr><td>{c.get('knob', '?')}</td><td>{c.get('old_value')}</td>"
            f"<td>{c.get('new_value')}</td><td>{c.get('rationale', '')}</td></tr>\n"
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
                f'<a href="{GITHUB_REPO_URL}/commit/{a["commit"]}"><code>{a["commit"]}</code></a>'
                f' (<code>git revert {a["commit"]}</code> to undo)'
            )
        else:
            commit_cell = "—"
        html += (
            f"<tr><td>{a['component']}</td><td>{a['action']}</td><td>{commit_cell}</td></tr>\n"
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
    body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; color: #222; }}
    h1 {{ border-bottom: 2px solid #333; padding-bottom: 0.5rem; font-size: 1.6rem; }}
    h3 {{ margin-top: 1.5rem; font-size: 1.1rem; color: #444; }}
    table {{ border-collapse: collapse; width: 100%; margin: 0.5rem 0; }}
    th, td {{ border: 1px solid #ddd; padding: 0.4rem 0.8rem; text-align: left; }}
    th {{ background: #f5f5f5; }}
    .meta {{ color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }}
    a {{ color: #0066cc; }}
    ul {{ padding-left: 1.4rem; }}
    li {{ margin: 0.25rem 0; }}
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
        print("❌ ANTHROPIC_API_KEY not set")
        sys.exit(1)

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

    print("  → Reading calibration_memory/change_history.json...")
    today = now.strftime("%Y-%m-%d")
    calibration_changes = get_calibration_changes(today)
    print(f"     {len(calibration_changes)} config change(s) applied today")

    print("  → Reading quality review summaries...")
    quality_review = get_quality_review()
    print(f"     scrub={'scrub' in quality_review}, alignment={'alignment' in quality_review}")

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
    if calibration_changes:
        commit = git_commit_for(["config/limits.json", "config/podcast_schedule.json"])
        for c in calibration_changes:
            actions.append({
                "component": "Calibration",
                "action": f"{c.get('knob', '?')}: {c.get('old_value')} → {c.get('new_value')}",
                "commit": commit,
            })
    print(f"     {len(actions)} action(s) this week")

    print("  → Generating narrative with Claude Haiku...")
    client = anthropic.Anthropic(api_key=api_key)
    narrative = generate_narrative(client, week_label, stats, new_feeds, errors, discovery)

    content_html = build_content_html(
        narrative, stats, new_feeds, errors, discovery,
        calibration_changes, quality_review, actions,
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
    }

    # Persist article to repo root (committed to main; referenced by generate-feed deploys)
    Path("weekly-state-article.json").write_text(
        json.dumps(article, indent=2, ensure_ascii=False), "utf-8"
    )

    # HTML permalink — written to both root (for generate-feed.yml to copy) and output/
    html_page = build_html_page(title, content_html, week_label, pub_date_human)
    html_filename = f"{article_slug}.html"
    Path(html_filename).write_text(html_page, "utf-8")

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
    feed_news["items"] = [article] + items

    feed_news_out = OUTPUT_DIR / "feed-news.json"
    feed_news_out.write_text(json.dumps(feed_news, indent=2, ensure_ascii=False), "utf-8")
    html_out = OUTPUT_DIR / html_filename
    html_out.write_text(html_page, "utf-8")

    print(f"  ✓ output/feed-news.json ({len(feed_news['items'])} items)")
    print(f"  ✓ output/{html_filename}")
    print(f"  ✓ {html_filename} (repo root)")
    print(f"  ✓ weekly-state-article.json (repo root)")
    print(f"\n✅ Weekly report complete → {article_url}")


if __name__ == "__main__":
    main()
