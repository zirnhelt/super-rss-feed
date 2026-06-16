#!/usr/bin/env python3
"""Weekly feedback trainer — reads user article ratings and updates config/feedback_examples.txt.

Reads all feedback/YYYY-MM-DD.json files committed by the review.html UI, analyzes
patterns in Good vs Bad ratings, calls Claude to synthesize actionable interest-profile
signals, and writes the result to config/feedback_examples.txt. The main curator injects
this file into the Claude scoring prompt so future runs reflect explicit user preferences.

Also analyzes day-reassignment patterns (articles tagged for a different podcast day)
and appends recommendations to FEEDBACK_TRAINING_LOG.md.

Run weekly via weekly-maintenance.yml. Requires ANTHROPIC_API_KEY.
Exits 0 with a note when insufficient feedback exists (< 3 files with >= 5 ratings each).
"""
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("❌ anthropic package not installed")
    sys.exit(1)

FEEDBACK_DIR     = Path('feedback')
EXAMPLES_FILE    = Path('config/feedback_examples.txt')
LOG_FILE         = Path('FEEDBACK_TRAINING_LOG.md')
LOOKBACK_DAYS    = 30
MIN_FILES        = 3
MIN_RATINGS_PER  = 5
DRY_RUN          = os.getenv('FEEDBACK_DRY_RUN', 'false').lower() == 'true'


def load_feedback(lookback_days: int = LOOKBACK_DAYS):
    """Load all feedback JSON files within the lookback window."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    files = []
    ratings = []

    if not FEEDBACK_DIR.exists():
        return files, ratings

    for f in sorted(FEEDBACK_DIR.glob('????-??-??.json')):
        try:
            date = datetime.fromisoformat(f.stem)
            date = date.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if date < cutoff:
            continue
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"⚠️  Skipping {f}: {e}")
            continue
        file_ratings = data.get('ratings', [])
        if len(file_ratings) >= MIN_RATINGS_PER:
            files.append(f.name)
        ratings.extend(file_ratings)

    return files, ratings


def aggregate_stats(ratings: list) -> dict:
    """Compute aggregates from raw ratings list."""
    good = [r for r in ratings if r.get('rating') == 'good']
    bad  = [r for r in ratings if r.get('rating') == 'bad']
    reassigned = [r for r in good if r.get('better_theme')]

    source_good: dict = defaultdict(int)
    source_bad: dict  = defaultdict(int)
    cat_good: dict    = defaultdict(int)
    cat_bad: dict     = defaultdict(int)
    day_from_to: dict = defaultdict(lambda: defaultdict(int))

    for r in good:
        source_good[r.get('source', '?')] += 1
        cat_good[r.get('category', '?')] += 1
    for r in bad:
        source_bad[r.get('source', '?')] += 1
        cat_bad[r.get('category', '?')] += 1
    for r in reassigned:
        from_day = r.get('today', '?')
        to_day   = r.get('better_theme', '?')
        day_from_to[from_day][to_day] += 1

    return {
        'good': good,
        'bad': bad,
        'reassigned': reassigned,
        'source_good': dict(source_good),
        'source_bad': dict(source_bad),
        'cat_good': dict(cat_good),
        'cat_bad': dict(cat_bad),
        'day_from_to': {k: dict(v) for k, v in day_from_to.items()},
    }


def build_claude_prompt(stats: dict) -> str:
    good = stats['good']
    bad  = stats['bad']

    good_lines = '\n'.join(
        f"- [{r.get('category','?')}] {r.get('title','?')} ({r.get('source','?')}) "
        f"[score {r.get('score',0)}, Q{r.get('quality',0)} R{r.get('relevance',0)}]"
        + (f" — note: {r['note']}" if r.get('note') else '')
        for r in good[:40]
    )
    bad_lines = '\n'.join(
        f"- [{r.get('category','?')}] {r.get('title','?')} ({r.get('source','?')}) "
        f"[score {r.get('score',0)}, Q{r.get('quality',0)} R{r.get('relevance',0)}]"
        + (f" — note: {r['note']}" if r.get('note') else '')
        for r in bad[:40]
    )

    reassign_lines = ''
    if stats['reassigned']:
        reassign_lines = '\nDAY REASSIGNMENTS (articles rated Good but moved to a different podcast day):\n'
        reassign_lines += '\n'.join(
            f"- '{r.get('title','?')}' moved from {r.get('today','?')} → {r.get('better_theme','?')}"
            for r in stats['reassigned'][:20]
        )

    return f"""A user has been rating RSS news articles as Good Fit or Bad Fit for their personal feed.
Analyze the patterns and write concise, actionable bullet points for the curator's scoring prompt.

GOOD FIT articles (user explicitly liked these):
{good_lines or '(none yet)'}

BAD FIT articles (user explicitly disliked these):
{bad_lines or '(none yet)'}
{reassign_lines}

Task: Write 6-12 bullet points that a news-scoring AI should use to calibrate RELEVANCE scores.
Focus on:
(a) Topic and framing signals that appear in liked articles but not disliked ones
(b) Topic and framing signals that appear in disliked articles (to down-weight)
(c) Source or content-type patterns worth noting
(d) Any day-reassignment patterns (e.g. articles consistently moved from one day to another)

Format as plain bullet points (- ...). Be specific and actionable. Do not repeat the raw article list.
Keep the total under 400 words."""


def synthesize_with_claude(prompt: str, api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model='claude-haiku-4-5',
        max_tokens=600,
        messages=[{'role': 'user', 'content': prompt}],
    )
    return response.content[0].text.strip()


def build_log_entry(files: list, stats: dict, synthesis: str, dry_run: bool) -> str:
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    good_count = len(stats['good'])
    bad_count  = len(stats['bad'])
    reassign_count = len(stats['reassigned'])

    top_good_sources = sorted(stats['source_good'].items(), key=lambda x: x[1], reverse=True)[:5]
    top_bad_sources  = sorted(stats['source_bad'].items(),  key=lambda x: x[1], reverse=True)[:5]
    top_good_cats    = sorted(stats['cat_good'].items(),    key=lambda x: x[1], reverse=True)
    top_bad_cats     = sorted(stats['cat_bad'].items(),     key=lambda x: x[1], reverse=True)

    day_reassign_lines = ''
    if stats['day_from_to']:
        day_reassign_lines = '\n**Day reassignment summary:**\n'
        for from_day, to_days in stats['day_from_to'].items():
            for to_day, count in sorted(to_days.items(), key=lambda x: x[1], reverse=True):
                day_reassign_lines += f'- {from_day} → {to_day}: {count} articles\n'

    status = '(DRY RUN — no changes written)' if dry_run else '✅ config/feedback_examples.txt updated'

    return f"""## Feedback Training Run — {now}

**Files processed:** {', '.join(files) if files else 'none'}
**Ratings:** {good_count} Good, {bad_count} Bad, {reassign_count} reassigned to different day
**Status:** {status}

**Top liked sources:** {', '.join(f'{s} ({n})' for s, n in top_good_sources) or 'n/a'}
**Top disliked sources:** {', '.join(f'{s} ({n})' for s, n in top_bad_sources) or 'n/a'}
**Categories liked:** {', '.join(f'{c} ({n})' for c, n in top_good_cats) or 'n/a'}
**Categories disliked:** {', '.join(f'{c} ({n})' for c, n in top_bad_cats) or 'n/a'}
{day_reassign_lines}
**Synthesized signals (written to feedback_examples.txt):**

{synthesis}

---
"""


def append_log(entry: str):
    existing = ''
    if LOG_FILE.exists():
        existing = LOG_FILE.read_text(encoding='utf-8')
    LOG_FILE.write_text(entry + existing, encoding='utf-8')


def main():
    api_key = os.getenv('ANTHROPIC_API_KEY', '')
    if not api_key:
        print('❌ ANTHROPIC_API_KEY not set')
        sys.exit(1)

    print('📊 Feedback Trainer — loading ratings...')
    files, ratings = load_feedback(LOOKBACK_DAYS)
    qualifying = [f for f in files]

    if len(qualifying) < MIN_FILES:
        print(f'ℹ️  Insufficient feedback ({len(qualifying)} qualifying files, need {MIN_FILES}). Skipping.')
        sys.exit(0)

    good_count = len([r for r in ratings if r.get('rating') == 'good'])
    bad_count  = len([r for r in ratings if r.get('rating') == 'bad'])
    print(f'   {len(qualifying)} files, {good_count} Good / {bad_count} Bad ratings')

    stats  = aggregate_stats(ratings)
    prompt = build_claude_prompt(stats)

    print('🤖 Synthesizing feedback signals with Claude...')
    synthesis = synthesize_with_claude(prompt, api_key)
    print(f'   Got {len(synthesis.split())} words of signals')

    log_entry = build_log_entry(qualifying, stats, synthesis, DRY_RUN)

    if DRY_RUN:
        print('🔍 DRY RUN — would write to config/feedback_examples.txt:')
        print(synthesis)
    else:
        EXAMPLES_FILE.parent.mkdir(exist_ok=True)
        EXAMPLES_FILE.write_text(synthesis, encoding='utf-8')
        print(f'✅ Written to {EXAMPLES_FILE}')

    append_log(log_entry)
    print(f'📝 Appended to {LOG_FILE}')
    print('✅ Feedback training complete')


if __name__ == '__main__':
    main()
