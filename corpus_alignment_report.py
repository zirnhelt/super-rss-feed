#!/usr/bin/env python3
"""
corpus_alignment_report.py — Corpus-wide scoring/theme alignment audit.

Joins podcast_articles_cache.json (the rolling weekly candidate pool, each
article carrying its upstream "interest" score from scoring_interests.txt)
against theme_scores_cache.json (per-article, per-theme fit scores for each
of the 7 daily podcast themes) to check whether the upstream score is a good
proxy for thematic fit — i.e. whether it's correctly gating which articles
become eligible for each day's themed bucket.

Two failure modes this surfaces:
  - FILLER: upstream score clears a day's quality gate, but the article
    doesn't fit ANY theme well. These pad "direct qualify" candidacy
    without being a strong match for the bucket they end up in.
  - STRANDED / RESCUE-DEPENDENT: the article fits some theme well (theme
    score >= that day's holdover_threshold) but its upstream score is too
    low to be considered for that day at all (rescue-dependent) or even to
    enter the pool (stranded, upstream < per-category min_score_by_category
    floor, falling back to min_claude_score).

Usage:
    python corpus_alignment_report.py [--output PATH] [--json-summary PATH]
"""

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

PODCAST_CACHE_FILE = "podcast_articles_cache.json"
THEME_SCORE_CACHE_FILE = "theme_scores_cache.json"
SCHEDULE_FILE = "config/podcast_schedule.json"
LIMITS_FILE = "config/limits.json"

FILLER_THEME_CEILING = 30   # best theme fit below this counts as "no real fit"
FILLER_UPSTREAM_FLOOR = 50  # upstream score at/above this is treated as "passes a gate"
TOP_N_EXAMPLES = 12


def load_json(path: Path) -> dict | list:
    with path.open() as f:
        return json.load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", metavar="PATH", help="Output file path")
    parser.add_argument("--json-summary", metavar="PATH", help="Write a compact JSON summary to PATH")
    args = parser.parse_args()

    root = Path(__file__).parent
    now = datetime.now(timezone.utc)
    output_path = Path(args.output) if args.output else root / f"CORPUS_ALIGNMENT_REPORT_{now.strftime('%Y-%m-%d')}.md"

    pod_path = root / PODCAST_CACHE_FILE
    tsc_path = root / THEME_SCORE_CACHE_FILE
    sched_path = root / SCHEDULE_FILE
    limits_path = root / LIMITS_FILE

    for p in (pod_path, tsc_path, sched_path, limits_path):
        if not p.exists():
            print(f"ERROR: required file not found: {p}", file=sys.stderr)
            sys.exit(1)

    print("Loading corpus...")
    podcast_cache = load_json(pod_path)
    theme_cache = load_json(tsc_path)
    schedule_cfg = load_json(sched_path)
    limits = load_json(limits_path)

    ct_breakdown = Counter(a.get('content_type', 'unknown') for a in podcast_cache)

    schedule = schedule_cfg["schedule"]
    global_holdover = schedule_cfg.get("holdover_threshold", 30)
    min_claude_score = limits.get("min_claude_score", 20)
    _score_by_cat = limits.get("min_score_by_category", {})

    def _min_score_for_cat(cat: str) -> int:
        return _score_by_cat.get(cat or "news", min_claude_score)

    day_label = {d: cfg["label"] for d, cfg in schedule.items()}
    day_min = {d: cfg.get("min_score", schedule_cfg.get("min_score", 25)) for d, cfg in schedule.items()}
    day_hold = {d: cfg.get("holdover_threshold", global_holdover) for d, cfg in schedule.items()}

    print(f"  {len(podcast_cache)} articles in podcast_articles_cache.json")
    print(f"  {len(theme_cache)} theme-score entries across {len(schedule)} themes")

    # ── Per-article analysis ────────────────────────────────────────────────
    cat_upstream: dict[str, list[int]] = defaultdict(list)
    cat_besttheme: dict[str, list[int]] = defaultdict(list)
    cat_status: dict[str, Counter] = defaultdict(Counter)
    missing_theme_data = 0

    direct_examples: list[tuple] = []
    rescue_examples: list[tuple] = []
    stranded_examples: list[tuple] = []
    filler_examples: list[tuple] = []

    day_pool_qualifies = {d: 0 for d in schedule}       # theme_score[d] >= day_min[d]
    day_direct = {d: 0 for d in schedule}               # qualifies AND upstream >= day_min[d]
    day_rescue = {d: 0 for d in schedule}               # qualifies via holdover, upstream < day_min[d]
    day_unreachable = {d: 0 for d in schedule}          # qualifies on theme but upstream < min_claude_score
    day_theme_scores: dict[str, list[int]] = {d: [] for d in schedule}  # raw theme-fit scores, whole corpus

    for article in podcast_cache:
        link = article["link"]
        cat = article.get("category", "unknown")
        upstream = article.get("composite", article.get("score", 0))
        title = article.get("title", "")

        theme_scores: dict[str, int] = {}
        for day, label in day_label.items():
            entry = theme_cache.get(f"{link}:::{label}")
            if entry is None:
                continue
            theme_scores[day] = entry["score"]

        if len(theme_scores) < len(schedule):
            missing_theme_data += 1
            continue

        best_day = max(theme_scores, key=lambda d: theme_scores[d])
        best_score = theme_scores[best_day]

        cat_upstream[cat].append(upstream)
        cat_besttheme[cat].append(best_score)

        # Per-day candidacy accounting
        cat_floor = _min_score_for_cat(cat)
        for day in schedule:
            ts = theme_scores[day]
            day_theme_scores[day].append(ts)
            if ts >= day_hold[day]:
                if upstream >= day_min[day]:
                    day_direct[day] += 1
                elif upstream >= cat_floor:
                    day_rescue[day] += 1
                else:
                    day_unreachable[day] += 1
                if ts >= day_min[day]:
                    day_pool_qualifies[day] += 1

        # Overall classification using the article's single best-fitting theme
        if best_score >= day_hold[best_day]:
            if upstream >= day_min[best_day]:
                cat_status[cat]["direct"] += 1
                direct_examples.append((upstream, best_score, cat, title, best_day))
            elif upstream >= cat_floor:
                cat_status[cat]["rescue"] += 1
                rescue_examples.append((best_score, upstream, cat, title, best_day))
            else:
                cat_status[cat]["stranded"] += 1
                stranded_examples.append((best_score, upstream, cat, title, best_day))
        else:
            cat_status[cat]["no_fit"] += 1

        if upstream >= FILLER_UPSTREAM_FLOOR and max(theme_scores.values()) < FILLER_THEME_CEILING:
            cat_status[cat]["filler"] += 1
            filler_examples.append((upstream, max(theme_scores.values()), cat, title))

    # ── Report generation ───────────────────────────────────────────────────
    ts_str = now.strftime("%Y-%m-%d %H:%M UTC")
    total = sum(len(v) for v in cat_upstream.values())

    sections: list[str] = []
    sections.append(f"# Cache Corpus Alignment Report\n\n_Generated: {ts_str}_\n")

    sections.append("## Executive Summary\n")
    total_filler = sum(c["filler"] for c in cat_status.values())
    total_rescue = sum(c["rescue"] for c in cat_status.values())
    total_stranded = sum(c["stranded"] for c in cat_status.values())
    total_direct = sum(c["direct"] for c in cat_status.values())
    sections.append(
        "| Metric | Value |\n|--------|-------|\n"
        f"| Articles analysed | {total} |\n"
        f"| Articles missing theme-score data (skipped) | {missing_theme_data} |\n"
        f"| Direct-qualify (upstream score gates them in for their best theme) | {total_direct} |\n"
        f"| Rescue-dependent (good theme fit, upstream below day minimum) | {total_rescue} |\n"
        f"| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | {total_stranded} |\n"
        f"| Filler (upstream ≥ {FILLER_UPSTREAM_FLOOR} but best theme fit < {FILLER_THEME_CEILING} for ALL 7 themes) | {total_filler} ({(total_filler/total*100 if total else 0):.0f}% of corpus) |\n"
    )

    sections.append(
        "\n**Interpretation:** *Filler* articles clear a quality bar on upstream "
        "interest score alone and so are eligible to be picked for whichever day's "
        "bucket they happen to score (marginally) highest on — even though that "
        "score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* "
        "articles are the mirror problem: content that fits a theme well but is "
        "filtered out (or only conditionally rescued) because the upstream score "
        "underrates it.\n"
    )

    if ct_breakdown:
        ct_rows = "".join(
            f"| {ct} | {count} |\n"
            for ct, count in sorted(ct_breakdown.items(), key=lambda x: -x[1])
        )
        sections.append(
            "\n**Content type breakdown** (fluff/sponsored are hard-dropped before articles "
            "enter this cache; their absence here is expected):\n\n"
            f"| Content type | Count |\n|-------------|-------|\n{ct_rows}"
        )

    # ── Per-category alignment table ──
    sections.append("\n## Per-Category: Upstream Score vs. Best Theme Fit\n")
    sections.append(
        "| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |\n"
        "|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|"
    )
    for cat in sorted(cat_upstream, key=lambda c: -len(cat_upstream[c])):
        u = statistics.mean(cat_upstream[cat])
        t = statistics.mean(cat_besttheme[cat])
        n = len(cat_upstream[cat])
        st = cat_status[cat]
        sections.append(
            f"| {cat} | {n} | {u:.1f} | {t:.1f} | {t - u:+.1f} "
            f"| {st['direct']} | {st['rescue']} | {st['stranded']} | {st['filler']} |"
        )
    sections.append(
        "\nA large negative Δ means the upstream interest score runs well ahead of "
        "how well that category's articles actually fit any of the 7 themes — a "
        "signal that the upstream score for that category may be inflated relative "
        "to its real bucket value (e.g. via the local-priority override, or a "
        "permissive `news` baseline).\n"
    )

    # ── Theme coverage table ──
    sections.append("\n## Theme Coverage Across the Corpus\n")
    sections.append(
        "Distribution of each theme's fit score across **all** "
        f"{total} corpus articles (not just that day's primary categories — "
        "theme scoring is run against the whole pool):\n"
    )
    sections.append(
        "| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |\n"
        "|-----|-------|---------|---------|------------|-------------|"
    )
    NEAR_ZERO_AVG = 2.0
    near_zero_days = []
    for day, cfg in schedule.items():
        scores = day_theme_scores[day]
        avg = statistics.mean(scores) if scores else 0.0
        mx = max(scores) if scores else 0
        n_hold = sum(1 for s in scores if s >= day_hold[day])
        n_min = sum(1 for s in scores if s >= day_min[day])
        flag = " ⚠️" if avg < NEAR_ZERO_AVG else ""
        sections.append(
            f"| {day.title()} | {cfg['label']} | {avg:.1f}{flag} | {mx} | {n_hold} | {n_min} |"
        )
        if avg < NEAR_ZERO_AVG:
            near_zero_days.append((day, cfg["label"], avg, mx))

    if near_zero_days:
        names = ", ".join(f"**{lbl}** (avg {avg:.1f}, max {mx})" for _, lbl, avg, mx in near_zero_days)
        sections.append(
            f"\n⚠️ **{len(near_zero_days)} of {len(schedule)} themes have near-zero fit "
            f"across the entire corpus**: {names}. This isn't a scoring-threshold problem — "
            "essentially nothing in the 7-day candidate pool is even rated as *somewhat* "
            "relevant to these themes. Either (a) the upstream interest score is filtering "
            "out this content before it ever reaches the podcast cache (so theme-scoring "
            "never sees genuinely relevant articles), (b) the feeds themselves aren't "
            "surfacing this content, or (c) these theme-scoring prompts are miscalibrated "
            "relative to the rest. Worth spot-checking a few raw feed articles for these "
            "topics against their theme score directly.\n"
        )

    # ── Per-day candidacy table ──
    sections.append("\n## Per-Theme-Day Candidacy\n")
    sections.append(
        "For each day's theme, counts of corpus articles whose **theme-fit score** "
        f"clears that day's `holdover_threshold`, broken down by how the upstream "
        "score would treat them.\n"
    )
    sections.append(
        "| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |\n"
        "|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|"
    )
    for day, cfg in schedule.items():
        sections.append(
            f"| {day.title()} | {cfg['label']} | {day_min[day]} | {day_hold[day]} "
            f"| {day_pool_qualifies[day]} | {day_direct[day]} | {day_rescue[day]} | {day_unreachable[day]} |"
        )
    sections.append(
        "\n'Unreachable' articles fit a theme well but score below `min_claude_score` "
        "overall, so the rescue mechanism in `route_articles_to_best_themes` / "
        "`generate_podcast_feed` never sees them — they're filtered out before "
        "theme routing runs at all.\n"
    )

    # ── Examples ──
    def _fmt_examples(rows: list[tuple], cols: list[str]) -> list[str]:
        out = [f"| {' | '.join(cols)} |", f"|{'|'.join(['---'] * len(cols))}|"]
        for row in rows[:TOP_N_EXAMPLES]:
            out.append("| " + " | ".join(str(v) for v in row) + " |")
        return out

    sections.append("\n---\n\n## Filler Examples (clears upstream gate, fits no theme)\n")
    sections.append(
        f"Top {TOP_N_EXAMPLES} by upstream score — these are the articles most likely "
        "to be picked for a bucket on the strength of upstream score alone, despite "
        f"scoring below {FILLER_THEME_CEILING} on every one of the 7 daily themes:\n"
    )
    sections.extend(_fmt_examples(
        sorted(filler_examples, reverse=True),
        ["Upstream", "Best theme fit", "Category", "Title"],
    ))

    sections.append("\n## Rescue-Dependent Examples (good fit, conditional inclusion)\n")
    sections.append(
        f"Top {TOP_N_EXAMPLES} by theme-fit score — these only make it into a bucket "
        "via the holdover-rescue path, not because the upstream score recognised "
        "their relevance:\n"
    )
    sections.extend(_fmt_examples(
        sorted(rescue_examples, reverse=True),
        ["Best theme fit", "Upstream", "Category", "Title", "Best-fit day"],
    ))

    if stranded_examples:
        sections.append("\n## Stranded Examples (good fit, never bankable)\n")
        sections.append(
            "Articles scoring ≥ a day's holdover threshold on theme fit, but below "
            "their category's quality floor (`min_score_by_category`, falling back to "
            f"`min_claude_score`={min_claude_score}) upstream — these are filtered out "
            "before theme routing ever considers them:\n"
        )
        sections.extend(_fmt_examples(
            sorted(stranded_examples, reverse=True),
            ["Best theme fit", "Upstream", "Category", "Title", "Best-fit day"],
        ))

    # ── Recommendations ──
    sections.append("\n---\n\n## Recommendations\n")
    recs: list[str] = []

    if near_zero_days:
        day_list = ", ".join(f"{d.title()} ({lbl})" for d, lbl, _, _ in near_zero_days)
        recs.append(
            f"🚨 {day_list} have essentially no viable candidates in the current "
            "corpus. Pull a handful of raw feed articles you'd *expect* to score well "
            "for these themes and run them through `score_articles_for_theme` directly — "
            "if they score near 0 there too, the theme prompts in "
            "`config/podcast_schedule.json` need recalibration; if they score normally, "
            "the upstream interest score (or feed sourcing) is the bottleneck keeping "
            "this content out of `podcast_articles_cache.json` in the first place."
        )

    news_filler = cat_status.get("news", Counter())["filler"]
    news_n = len(cat_upstream.get("news", []))
    if news_n and news_filler / news_n > 0.2:
        recs.append(
            f"📊 **news** is {news_n}/{total} ({news_n/total*100:.0f}%) of the corpus, and "
            f"{news_filler} of those ({news_filler/news_n*100:.0f}%) clear the upstream gate "
            f"while fitting no theme above {FILLER_THEME_CEILING}. Consider adding a "
            "theme-fit floor to `route_articles_to_best_themes`/`generate_podcast_feed`'s "
            "'direct qualify' path (not just upstream score) so generic news doesn't "
            "crowd out better-fitting candidates on its best-scoring (but still weak) day."
        )

    local = cat_status.get("local", Counter())
    local_n = len(cat_upstream.get("local", []))
    if local_n and local["filler"] / local_n > 0.3:
        recs.append(
            f"📍 **local** articles average {statistics.mean(cat_upstream['local']):.1f} upstream "
            f"(boosted by `local_keyword_bonus` in `scoring_modifiers.json`, +25 to the L dimension) but "
            f"only {statistics.mean(cat_besttheme['local']):.1f} best-theme-fit — "
            f"{local['filler']}/{local_n} are filler. Local civic/crime/awards items pass the "
            "quality bar on the geographic bonus alone but don't map to any of the 7 themes; "
            "Saturday's 'Cariboo Local Affairs' (min_score 25) is the only day designed to "
            "absorb these — verify the bonus isn't pushing them into other days' buckets instead."
        )

    if total_stranded:
        recs.append(
            f"🌾 {total_stranded} article(s) fit a theme well but score below their "
            "per-category quality floor (`min_score_by_category` in `config/limits.json`, "
            f"falling back to `min_claude_score`={min_claude_score}) and are stranded — "
            "see the Stranded Examples table. Consider lowering or adding a floor for "
            "those categories so they survive into the podcast pool."
        )

    for day, cfg in schedule.items():
        qualifies = day_pool_qualifies[day]
        direct = day_direct[day]
        if qualifies and direct / qualifies < 0.5:
            recs.append(
                f"🗓️ **{cfg['label']}** ({day.title()}): only {direct}/{qualifies} "
                "theme-qualified articles clear the upstream gate directly — most rely on "
                "rescue. Consider lowering `min_score` for this day in "
                "`config/podcast_schedule.json` or raising the upstream scores for the "
                f"categories that feed it ({', '.join(cfg['categories'])})."
            )

    if not recs:
        recs.append("✅ Upstream scores and theme fit look reasonably aligned.")

    for rec in recs:
        sections.append(f"- {rec}")

    sections.append(
        f"\n---\n\n_Report generated by `corpus_alignment_report.py` · "
        f"{total} articles analysed · {ts_str}_\n"
    )

    output_path.write_text("\n".join(sections), encoding="utf-8")
    print(f"Report written to {output_path}")

    if args.json_summary:
        summary = {
            "generated": ts_str,
            "total_articles": total,
            "missing_theme_data": missing_theme_data,
            "total_direct": total_direct,
            "total_rescue": total_rescue,
            "total_stranded": total_stranded,
            "total_filler": total_filler,
            "total_filler_pct": round(total_filler / total * 100, 1) if total else 0,
            "content_type_breakdown": dict(ct_breakdown),
        }
        Path(args.json_summary).write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"JSON summary written to {args.json_summary}")


if __name__ == "__main__":
    main()
