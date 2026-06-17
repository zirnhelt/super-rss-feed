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
    "You are a senior Python code reviewer specializing in data pipeline correctness. "
    "Review only what is shown — do not invent assumptions about missing code."
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

Do not suggest rewrites. Do not review feed fetching, deduplication, or output stages.
Do not review prompt text sent to Claude — only the Python logic around it.

Group output as: Filter Logic / Scoring & Priority / Edge Cases.
Flag the top 2–3 most impactful findings at the top.
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
        if output == "return":
            response = client.chat(model=model, messages=messages)
            return response.message.content[0].text

        # Stream and print as chunks arrive
        collected: list[str] = []
        for event in client.chat_stream(model=model, messages=messages):
            if event.type == "content-delta":
                chunk = event.delta.message.content.text
                print(chunk, end="", flush=True)
                collected.append(chunk)
        print()  # final newline
        return None

    except Exception as e:
        err_str = str(e).lower()
        if "not found" in err_str or "404" in err_str:
            print(
                f"\nModel '{model}' was not found. "
                "Check https://docs.cohere.com/docs/models for the correct identifier."
            )
        raise


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    review_filter_priority()


if __name__ == "__main__":
    main()
