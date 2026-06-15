#!/usr/bin/env python3
"""
score_scrub_report.py — On-demand scoring and scrubbing review of current feeds.

Reads existing feed-*.json files, computes quality metrics, runs a Claude Haiku
content scrub on borderline articles, and writes a formatted markdown report.

Usage:
    python score_scrub_report.py [--no-scrub] [--output PATH] [--json-summary PATH]

Options:
    --no-scrub          Skip the Claude API scrub pass (stat analysis only)
    --output PATH       Write report to PATH (default: FEED_REVIEW_YYYY-MM-DD.md)
    --json-summary PATH Write a compact JSON summary to PATH (for the weekly report)
"""

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import anthropic

# ── Configuration ────────────────────────────────────────────────────────────

FEED_GLOB = "feed-*.json"
PODCAST_PREFIX = "feed-podcast-"
SCORE_FIELD = "_score"
LOCAL_FIELD = "_local"
LOW_SCORE_FLAG = 30       # flag articles at or below this score
SCRUB_SCORE_MAX = 40      # only send borderline articles to the scrub pass
SCRUB_SCORE_MIN = 15
SCRUB_BATCH_MAX = 60      # cap API call size
STALE_HOURS = 48          # articles older than this are "stale"
SOURCE_DOMINANCE_PCT = 40      # flag if one source > this % of a feed
SOURCE_DOMINANCE_MIN_ITEMS = 8 # only check dominance on feeds with this many articles

SCRUB_SYSTEM = (
    "You are a strict content quality reviewer for a personal RSS feed curator. "
    "The curator is interested in: AI/ML tech, climate/energy, homelab/self-hosting, "
    "science, sci-fi/fantasy, local BC community news, and general quality journalism. "
    "It has already filtered out obvious junk; you are the last line of defence."
)

SCRUB_USER_TMPL = """Review the following borderline-scored articles (score 15–40) from a personal RSS curator.
Flag any that are clearly unwanted in a quality curated feed:
- Sports scores, game recaps, trades, drafts
- Celebrity gossip, red carpet, tabloid
- Deal alerts, promo codes, shopping listicles
- Advice columns (Dear Abby, Ask Amy, Miss Manners)
- Duplicate breaking news with no added analysis
- Pure clickbait headlines with zero information value

Do NOT flag articles just because they are low interest — only flag clearly problematic content.
Local BC/Cariboo community news should almost never be flagged.

Articles:
{items}

Respond with a JSON array only (no prose):
[{{"item_num": N, "title": "...", "issue": "sports|celebrity|deals|advice|duplicate|clickbait", "recommendation": "remove|keep"}}]
If nothing is problematic return [].
"""


# ── Feed loading ─────────────────────────────────────────────────────────────

def load_feeds(root: Path) -> dict[str, dict]:
    feeds = {}
    for path in sorted(root.glob(FEED_GLOB)):
        if path.name.startswith(PODCAST_PREFIX):
            continue
        with path.open() as fh:
            feeds[path.name] = json.load(fh)
    return feeds


# ── Per-feed analysis ─────────────────────────────────────────────────────────

def parse_age_hours(date_str: str, now: datetime) -> float | None:
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return (now - dt).total_seconds() / 3600
    except Exception:
        return None


def analyse_feed(feed_name: str, feed_data: dict, now: datetime) -> dict:
    items = feed_data.get("items", [])

    scores = [item[SCORE_FIELD] for item in items if SCORE_FIELD in item]
    sources = [
        (item.get("authors") or [{}])[0].get("name", "Unknown")
        for item in items
    ]
    ages = [h for item in items if (h := parse_age_hours(item.get("date_published"), now)) is not None]

    low_score = [item for item in items if item.get(SCORE_FIELD, 100) <= LOW_SCORE_FLAG]
    scrub_candidates = [
        item for item in items
        if SCRUB_SCORE_MIN <= item.get(SCORE_FIELD, 100) <= SCRUB_SCORE_MAX
    ]

    source_counts = Counter(sources)
    top_source, top_count = source_counts.most_common(1)[0] if source_counts else ("—", 0)

    return {
        "title": feed_data.get("title", feed_name),
        "count": len(items),
        "scored_count": len(scores),
        "avg_score": sum(scores) / len(scores) if scores else 0.0,
        "min_score": min(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "score_buckets": _bucket_scores(scores),
        "source_counts": source_counts,
        "top_source": top_source,
        "top_source_count": top_count,
        "top_source_pct": (top_count / len(items) * 100) if items else 0,
        "low_score_items": low_score,
        "scrub_candidates": scrub_candidates,
        "avg_age_hours": sum(ages) / len(ages) if ages else 0.0,
        "stale_count": sum(1 for h in ages if h > STALE_HOURS),
        "local_count": sum(1 for item in items if item.get(LOCAL_FIELD, False)),
        "local_override_zero": sum(
            1 for item in items
            if item.get(LOCAL_FIELD, False) and item.get(SCORE_FIELD, -1) == 0
        ),
    }


def _bucket_scores(scores: list[int]) -> dict[str, int]:
    labels = ["0–9", "10–19", "20–29", "30–39", "40–49",
              "50–59", "60–69", "70–79", "80–89", "90–100"]
    buckets = {lbl: 0 for lbl in labels}
    for s in scores:
        idx = min(s // 10, 9)
        buckets[labels[idx]] += 1
    return buckets


# ── Claude scrub pass ─────────────────────────────────────────────────────────

def run_scrub_pass(
    analyses: dict[str, dict], client: anthropic.Anthropic
) -> list[dict]:
    candidates: list[dict] = []
    for feed_name, analysis in analyses.items():
        for item in analysis["scrub_candidates"]:
            candidates.append({
                "feed": feed_name,
                "feed_title": analysis["title"],
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "score": item.get(SCORE_FIELD, 0),
                "local": item.get(LOCAL_FIELD, False),
            })

    if not candidates:
        return []

    candidates = candidates[:SCRUB_BATCH_MAX]

    lines = []
    for i, c in enumerate(candidates, 1):
        local_tag = " [LOCAL]" if c["local"] else ""
        lines.append(f"{i}. [{c['feed_title']}{local_tag}] (score {c['score']}) {c['title']}")

    prompt = SCRUB_USER_TMPL.format(items="\n".join(lines))

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        system=SCRUB_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start < 0 or end <= start:
        return []

    try:
        flagged = json.loads(raw[start:end])
    except json.JSONDecodeError:
        return []

    for flag in flagged:
        idx = flag.get("item_num", 1) - 1
        if 0 <= idx < len(candidates):
            flag.update({
                "feed": candidates[idx]["feed"],
                "feed_title": candidates[idx]["feed_title"],
                "url": candidates[idx]["url"],
                "score": candidates[idx]["score"],
            })
    return flagged


# ── Report generation ─────────────────────────────────────────────────────────

def _histogram(buckets: dict[str, int]) -> str:
    if not buckets:
        return "  (no data)"
    max_val = max(buckets.values()) or 1
    rows = []
    for label, count in buckets.items():
        bar = "█" * int(count / max_val * 20)
        rows.append(f"  {label:7s} │ {bar:<20s} {count:>3d}")
    return "\n".join(rows)


def _score_band_emoji(avg: float) -> str:
    if avg >= 70:
        return "🟢"
    if avg >= 45:
        return "🟡"
    return "🔴"


def generate_report(
    analyses: dict[str, dict],
    flagged: list[dict],
    scrub_ran: bool,
    now: datetime,
) -> str:
    ts = now.strftime("%Y-%m-%d %H:%M UTC")
    total_articles = sum(a["count"] for a in analyses.values())
    total_stale = sum(a["stale_count"] for a in analyses.values())

    sections: list[str] = []

    # ── Header ──
    sections.append(f"# Feed Scoring & Scrubbing Report\n\n_Generated: {ts}_\n")

    # ── Executive summary ──
    sections.append("## Executive Summary\n")
    sections.append(
        f"| Metric | Value |\n|--------|-------|\n"
        f"| Feeds reviewed | {len(analyses)} |\n"
        f"| Total articles | {total_articles} |\n"
        f"| Stale articles (>{STALE_HOURS}h) | {total_stale} |\n"
        f"| Scrub pass | {'✅ ran' if scrub_ran else '⏭ skipped (--no-scrub)'} |\n"
        f"| Flagged for removal | {sum(1 for f in flagged if f.get('recommendation') == 'remove')} |\n"
    )

    # ── Feed summary table ──
    sections.append("\n## Feed Summary\n")
    header = "| Feed | Articles | Avg Score | Score Range | Stale | Top Source |"
    sep    = "|------|----------|-----------|-------------|-------|------------|"
    rows   = [header, sep]
    for feed_name, a in analyses.items():
        band = _score_band_emoji(a["avg_score"])
        top = f"{a['top_source']} ({a['top_source_count']})"
        rows.append(
            f"| {a['title']} | {a['count']} "
            f"| {band} {a['avg_score']:.1f} "
            f"| {a['min_score']}–{a['max_score']} "
            f"| {a['stale_count']} "
            f"| {top} |"
        )
    sections.append("\n".join(rows))

    # ── Per-feed detail ──
    sections.append("\n---\n\n## Per-Feed Detail\n")
    for feed_name, a in analyses.items():
        band = _score_band_emoji(a["avg_score"])
        sections.append(f"### {band} {a['title']}\n")

        meta = [
            f"- **Articles**: {a['count']} ({a['scored_count']} scored)",
            f"- **Score**: avg {a['avg_score']:.1f} | min {a['min_score']} | max {a['max_score']}",
            f"- **Stale** (>{STALE_HOURS}h): {a['stale_count']}",
            f"- **Avg age**: {a['avg_age_hours']:.1f}h",
        ]
        if a["local_count"]:
            note = f" ({a['local_override_zero']} with score=0 via local override)" if a["local_override_zero"] else ""
            meta.append(f"- **Local-flagged**: {a['local_count']}{note}")
        sections.append("\n".join(meta))

        # Score histogram
        sections.append("\n**Score distribution:**\n```")
        sections.append(_histogram(a["score_buckets"]))
        sections.append("```")

        # Source breakdown (top 8)
        if a["source_counts"]:
            sections.append("\n**Sources (top 8):**\n")
            rows2 = ["| Source | Count | % of feed |", "|--------|-------|-----------|"]
            for src, cnt in a["source_counts"].most_common(8):
                pct = cnt / a["count"] * 100 if a["count"] else 0
                check_dom = a["count"] >= SOURCE_DOMINANCE_MIN_ITEMS
                dom = " ⚠️" if (check_dom and pct > SOURCE_DOMINANCE_PCT) else ""
                rows2.append(f"| {src} | {cnt} | {pct:.0f}%{dom} |")
            sections.append("\n".join(rows2))

        # Low-score articles
        if a["low_score_items"]:
            sections.append(f"\n**Low-score articles (≤{LOW_SCORE_FLAG}):**\n")
            for item in a["low_score_items"][:15]:
                score = item.get(SCORE_FIELD, "?")
                title = item.get("title", "Untitled")
                url = item.get("url", "")
                sections.append(f"- `[{score:>3}]` {title}  \n  <{url}>")

        sections.append("")

    # ── Scrub pass findings ──
    sections.append("---\n\n## Scrub Pass Findings\n")

    if not scrub_ran:
        sections.append("_Scrub pass skipped. Re-run without `--no-scrub` to enable._\n")
    elif not flagged:
        sections.append(
            "✅ **Nothing flagged.** All borderline articles reviewed by Claude Haiku — "
            "no sports, celebrity, deal, or advice-column content detected.\n"
        )
    else:
        to_remove = [f for f in flagged if f.get("recommendation") == "remove"]
        to_keep   = [f for f in flagged if f.get("recommendation") != "remove"]

        if to_remove:
            sections.append(f"### 🗑️ Recommended for Removal ({len(to_remove)})\n")
            for item in to_remove:
                sections.append(
                    f"- **[{item.get('feed_title', item.get('feed'))}]** "
                    f"`score {item.get('score', '?')}` — {item.get('title', '')}  \n"
                    f"  Issue: `{item.get('issue', 'unknown')}`  \n"
                    f"  <{item.get('url', '')}>"
                )
            sections.append("")

        if to_keep:
            sections.append(f"### ⚠️ Borderline but Acceptable ({len(to_keep)})\n")
            for item in to_keep:
                sections.append(
                    f"- **[{item.get('feed_title', item.get('feed'))}]** "
                    f"`score {item.get('score', '?')}` — {item.get('title', '')}  \n"
                    f"  Note: `{item.get('issue', 'ok')}`"
                )
            sections.append("")

    # ── Recommendations ──
    sections.append("---\n\n## Recommendations\n")

    recs: list[str] = []

    for feed_name, a in analyses.items():
        label = a["title"]

        if a["avg_score"] < 35 and a["count"] > 5:
            recs.append(
                f"⚠️ **{label}** has a low average score ({a['avg_score']:.1f}) — "
                "consider tightening category rules or raising `min_claude_score` in `config/limits.json`."
            )

        if a["stale_count"] > 5:
            recs.append(
                f"🕐 **{label}** has {a['stale_count']} articles older than {STALE_HOURS}h — "
                "verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently."
            )

        if a["top_source_pct"] > SOURCE_DOMINANCE_PCT and a["count"] >= SOURCE_DOMINANCE_MIN_ITEMS:
            recs.append(
                f"📊 **{label}** is dominated by **{a['top_source']}** "
                f"({a['top_source_count']} articles, {a['top_source_pct']:.0f}%) — "
                "consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`."
            )

    to_remove = [f for f in flagged if f.get("recommendation") == "remove"]
    if to_remove:
        issues = Counter(f.get("issue", "unknown") for f in to_remove)
        issue_list = ", ".join(f"`{k}` ×{v}" for k, v in issues.most_common())
        recs.append(
            f"🗑️ {len(to_remove)} article(s) should be removed ({issue_list}) — "
            "add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence."
        )

    if not recs:
        recs.append("✅ Feeds look healthy. No actionable issues detected.")

    for rec in recs:
        sections.append(f"- {rec}")

    sections.append(
        f"\n---\n\n_Report generated by `score_scrub_report.py` · "
        f"{len(analyses)} feeds · {total_articles} articles · {ts}_\n"
    )

    return "\n".join(sections)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--no-scrub", action="store_true", help="Skip the Claude API scrub pass")
    parser.add_argument("--output", metavar="PATH", help="Output file path")
    parser.add_argument("--json-summary", metavar="PATH", help="Write a compact JSON summary to PATH")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    root = Path(__file__).parent

    # Default output path
    output_path = Path(args.output) if args.output else root / f"FEED_REVIEW_{now.strftime('%Y-%m-%d')}.md"

    print("Loading feeds…")
    feeds = load_feeds(root)
    if not feeds:
        print("ERROR: No feed-*.json files found. Run from the project root.", file=sys.stderr)
        sys.exit(1)
    print(f"  Found {len(feeds)} feed files.")

    print("Analysing…")
    analyses: dict[str, dict] = {}
    for feed_name, feed_data in feeds.items():
        analyses[feed_name] = analyse_feed(feed_name, feed_data, now)
        a = analyses[feed_name]
        cands = len(a["scrub_candidates"])
        print(f"  {a['title']:30s}  {a['count']:3d} articles  avg score {a['avg_score']:5.1f}  scrub candidates {cands}")

    # Claude scrub pass
    flagged: list[dict] = []
    scrub_ran = False

    if not args.no_scrub:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("WARNING: ANTHROPIC_API_KEY not set — skipping scrub pass.")
        else:
            total_candidates = sum(len(a["scrub_candidates"]) for a in analyses.values())
            print(f"Running Claude Haiku scrub pass on {min(total_candidates, SCRUB_BATCH_MAX)} borderline articles…")
            client = anthropic.Anthropic(api_key=api_key)
            try:
                flagged = run_scrub_pass(analyses, client)
                scrub_ran = True
                to_remove = sum(1 for f in flagged if f.get("recommendation") == "remove")
                print(f"  Flagged {len(flagged)} articles ({to_remove} recommended for removal).")
            except Exception as exc:
                print(f"WARNING: Scrub pass failed — {exc}")
    else:
        print("Skipping scrub pass (--no-scrub).")

    print("Generating report…")
    report = generate_report(analyses, flagged, scrub_ran, now)
    output_path.write_text(report, encoding="utf-8")
    print(f"Report written to {output_path}")

    if args.json_summary:
        to_remove = sum(1 for f in flagged if f.get("recommendation") == "remove")
        summary = {
            "generated": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_articles": sum(a["count"] for a in analyses.values()),
            "scrub_ran": scrub_ran,
            "flagged_count": len(flagged),
            "flagged_remove_count": to_remove,
            "feeds": {
                name: {
                    "title": a["title"],
                    "count": a["count"],
                    "avg_score": round(a["avg_score"], 1),
                    "low_score_count": len(a["low_score_items"]),
                    "stale_count": a["stale_count"],
                    "top_source": a["top_source"],
                    "top_source_pct": round(a["top_source_pct"], 1),
                }
                for name, a in analyses.items()
            },
        }
        Path(args.json_summary).write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"JSON summary written to {args.json_summary}")


if __name__ == "__main__":
    main()
