#!/usr/bin/env python3
"""
tools/review_filter_priority.py — Code review of filter and scoring logic via Cohere.

Extracts the filter/priority pipeline functions from super_rss_curator_json.py
and submits them to north-mini-code-1-0 for a focused review.

Usage:
    python tools/review_filter_priority.py
    COHERE_API_KEY=... python tools/review_filter_priority.py
"""

import os
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────────────────────

CURATOR_FILENAME = "super_rss_curator_json.py"

# (label, start_line, end_line) — 1-indexed, inclusive
SECTIONS = [
    ("Article.should_filter() — Filter: keyword/source/title-pattern blocking", 520, 545),
    ("scrub_feed_with_haiku() — Filter: semantic scrub pass", 2208, 2339),
    ("apply_prescore_filter() — Filter: aggregator source gating", 2343, 2383),
    ("compute_composite_score() — Score: Q/R/L composite formula", 2435, 2442),
    ("apply_dimension_adjustments() — Score: L bonus, Q adjustments, wire penalty", 2445, 2502),
    ("filter_by_content_type() — Filter: hard drops (fluff/sponsored/recap)", 2505, 2534),
    ("score_articles_with_claude() — Score: main dimensional scoring", 1970, 2205),
    ("_podcast_composite() — Score: podcast formula (adds T/theme dimension)", 3386, 3392),
]

SYSTEM_PROMPT = (
    "You are a senior Python engineer doing a blocking code review. "
    "You are direct and do not hedge. When you find a problem, you state what it is and "
    "where it is without softening language. For every BLOCKING finding you must include "
    "the corrected code — either as a diff or a rewritten snippet — so it can be applied "
    "immediately without further discussion. Do not say 'consider' or 'you might want to'. "
    "Say what is wrong and what the fix is. Review only what is shown — do not invent "
    "assumptions about missing code."
)

REVIEW_PROMPT = """\
Review the filter and priority scoring logic in this RSS curation pipeline code.

Focus only on:
- Filters that can contradict each other across stages
- Score floors or overrides that a later penalty can erode
- Drop decisions made before all adjustments have run
- Whether quality and relevance are separable or collapsed into one value
- Whether the final sort formula matches the configured weights
- Hardcoded constants that belong in config
- Thin-day behaviour: does the pipeline auto-inflate low-scoring items?
- What wins when a local source also matches a high-volume prescore gate?

For each finding state: what the problem is, where it lives (function name or
approximate line), whether it is a conflict / hardcode / sequencing issue / missing
config surface, and severity: blocking / latent / cosmetic.

Do not review feed fetching, deduplication, or output stages.
Do not review prompt text sent to Claude — only the Python logic around it.

Group output as: Filter Logic / Scoring & Priority / Edge Cases.
List ALL findings — do not truncate or summarise.
For each BLOCKING finding, include the corrected code diff or full rewrite inline
so it can be applied immediately.
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_lines(filepath: Path, start: int, end: int) -> str:
    """Return lines [start, end] (1-indexed, inclusive) from filepath."""
    lines = filepath.read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[max(0, start - 1) : end])


def build_code_payload(curator_path: Path) -> str:
    """Assemble annotated code blocks for all SECTIONS."""
    parts = []
    for label, start, end in SECTIONS:
        code = extract_lines(curator_path, start, end)
        if code.strip():
            parts.append(
                f"### {label} (lines {start}–{end})\n\n```python\n{code}\n```"
            )
    if not parts:
        raise ValueError(
            f"No code extracted from {curator_path}. "
            "Expected filter/scoring functions to be present."
        )
    return "\n\n---\n\n".join(parts)


# ── Public API ────────────────────────────────────────────────────────────────

def review_filter_priority(
    model: str = "north-mini-code-1-0",
    cohere_api_key: str | None = None,
    output: str = "print",
) -> str | None:
    """Submit filter/priority logic to Cohere for a focused code review.

    Args:
        model: Cohere model identifier.
        cohere_api_key: API key; falls back to COHERE_API_KEY env var.
        output: "print" streams findings to stdout and returns None;
                "return" returns the full response as a string.
    """
    api_key = cohere_api_key or os.environ.get("COHERE_API_KEY")
    if not api_key:
        raise ValueError(
            "COHERE_API_KEY is not set. "
            "Export it or pass cohere_api_key= explicitly."
        )

    curator_path = Path(__file__).parent.parent / CURATOR_FILENAME
    if not curator_path.exists():
        raise FileNotFoundError(
            f"Curator file not found at expected path: {curator_path}"
        )

    total_lines = sum(end - start + 1 for _, start, end in SECTIONS)
    print(f"Extracting {len(SECTIONS)} sections (~{total_lines} lines) from {curator_path.name}...")
    code_payload = build_code_payload(curator_path)

    import cohere  # lazy — same pattern as cohere_integration.py

    client = cohere.ClientV2(api_key=api_key)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"{REVIEW_PROMPT}\n\n---\n\n{code_payload}"},
    ]

    print(f"Submitting to {model}...\n")

    try:
        response = client.chat(model=model, messages=messages)
        findings = next(
            item.text for item in response.message.content
            if hasattr(item, "text") and item.text
        )
    except Exception as e:
        err_str = str(e).lower()
        if "not found" in err_str or "404" in err_str:
            print(
                f"\nModel '{model}' was not found. "
                "Check https://docs.cohere.com/docs/models for the correct identifier."
            )
        raise

    _write_markdown(findings, model)

    if output == "print":
        print(findings)
        return None
    return findings


def _write_markdown(findings: str, model: str) -> None:
    """Write findings to tools/filter_priority_review.md next to this script."""
    import datetime
    date = datetime.date.today().isoformat()
    md = (
        f"# Filter & Priority Logic Review\n\n"
        f"**Date:** {date}  \n"
        f"**Model:** {model}  \n\n"
        f"---\n\n"
        f"{findings}\n"
    )
    out_path = Path(__file__).parent / "filter_priority_review.md"
    out_path.write_text(md, encoding="utf-8")
    print(f"\nFindings written to {out_path.relative_to(Path(__file__).parent.parent)}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    import re

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-on-blocking",
        action="store_true",
        help="Exit with code 1 if any BLOCKING findings are detected in the output.",
    )
    parser.add_argument(
        "--model",
        default="north-mini-code-1-0",
        help="Cohere model identifier (default: %(default)s).",
    )
    args = parser.parse_args()

    review_filter_priority(model=args.model)

    if args.fail_on_blocking:
        out_path = Path(__file__).parent / "filter_priority_review.md"
        text = out_path.read_text(encoding="utf-8")
        blocking_matches = re.findall(r"\bblocking\b", text, flags=re.IGNORECASE)
        count = len(blocking_matches)
        if count:
            print(f"\n{count} blocking finding(s) detected — fix before merging")
            raise SystemExit(1)


if __name__ == "__main__":
    main()
