#!/usr/bin/env python3
"""Weekly feedback trainer — reads user article ratings and updates config/feedback_examples.txt.

Reads all feedback/YYYY-MM-DD.json files committed by the review.html UI, analyzes
patterns in Exemplar/Good/Interesting/Bad ratings, calls Claude to synthesize actionable
interest-profile signals, and writes the result to config/feedback_examples.txt. The main
curator injects this file into the Claude scoring prompt so future runs reflect explicit
user preferences. Exemplars (rating='exemplar') are user-submitted articles from anywhere
on the web — added via the "Add a Great Example" form in review.html — and are treated as
the strongest available signal.

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

from fetch_images import fetch_page_title

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


def backfill_exemplar_titles(lookback_days: int = LOOKBACK_DAYS) -> int:
    """Scrape titles for exemplars submitted without one. Returns count backfilled."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    backfilled = 0

    if not FEEDBACK_DIR.exists():
        return backfilled

    for f in sorted(FEEDBACK_DIR.glob('????-??-??.json')):
        try:
            date = datetime.fromisoformat(f.stem).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if date < cutoff:
            continue
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
        except Exception:
            continue

        dirty = False
        for r in data.get('ratings', []):
            if r.get('rating') == 'exemplar' and not r.get('title'):
                title = fetch_page_title(r['url'])
                if title:
                    r['title'] = title
                    dirty = True
                    backfilled += 1

        if dirty and not DRY_RUN:
            f.write_text(json.dumps(data, indent=2), encoding='utf-8')

    return backfilled


def aggregate_stats(ratings: list) -> dict:
    """Compute aggregates from raw ratings list."""
    exemplars   = [r for r in ratings if r.get('rating') == 'exemplar']
    good        = [r for r in ratings if r.get('rating') == 'good']
    interesting = [r for r in ratings if r.get('rating') == 'interesting']
    bad         = [r for r in ratings if r.get('rating') == 'bad']
    reassigned  = [r for r in good if r.get('approved_days') or r.get('better_theme')]

    recategorized = [
        r for r in ratings
        if r.get('original_category') and r.get('category')
        and r['original_category'] != r['category']
    ]

    source_good: dict = defaultdict(int)
    source_bad: dict  = defaultdict(int)
    cat_good: dict    = defaultdict(int)
    cat_bad: dict     = defaultdict(int)
    day_from_to: dict = defaultdict(lambda: defaultdict(int))
    category_from_to: dict = defaultdict(lambda: defaultdict(int))

    for r in good:
        source_good[r.get('source', '?')] += 1
        cat_good[r.get('category', '?')] += 1
    for r in bad:
        source_bad[r.get('source', '?')] += 1
        cat_bad[r.get('category', '?')] += 1
    for r in reassigned:
        from_day = r.get('today', '?')
        to_days  = r.get('approved_days') or ([r['better_theme']] if r.get('better_theme') else [])
        for to_day in to_days:
            day_from_to[from_day][to_day] += 1
    for r in recategorized:
        category_from_to[r['original_category']][r['category']] += 1

    return {
        'exemplars': exemplars,
        'good': good,
        'interesting': interesting,
        'bad': bad,
        'reassigned': reassigned,
        'recategorized': recategorized,
        'source_good': dict(source_good),
        'source_bad': dict(source_bad),
        'cat_good': dict(cat_good),
        'cat_bad': dict(cat_bad),
        'day_from_to': {k: dict(v) for k, v in day_from_to.items()},
        'category_from_to': {k: dict(v) for k, v in category_from_to.items()},
    }


def build_claude_prompt(stats: dict) -> str:
    exemplars   = stats.get('exemplars', [])
    good        = stats['good']
    interesting = stats['interesting']
    bad         = stats['bad']

    def fmt(r: dict) -> str:
        line = (
            f"- [{r.get('category','?')}] {r.get('title','?')} ({r.get('source','?')}) "
            f"[score {r.get('score',0)}, Q{r.get('quality',0)} R{r.get('relevance',0)}]"
        )
        return line + (f" — note: {r['note']}" if r.get('note') else '')

    def fmt_exemplar(r: dict) -> str:
        label = r.get('title') or r.get('source') or r.get('url', '?')
        line = f"- [{r.get('category','?')}] {label} ({r.get('source','?')})"
        return line + (f" — why: {r['note']}" if r.get('note') else '')

    exemplar_lines     = '\n'.join(fmt_exemplar(r) for r in exemplars[:20])
    good_lines         = '\n'.join(fmt(r) for r in good[:40])
    interesting_lines  = '\n'.join(fmt(r) for r in interesting[:30])
    bad_lines          = '\n'.join(fmt(r) for r in bad[:40])

    reassign_lines = ''
    if stats['reassigned']:
        reassign_lines = '\nDAY REASSIGNMENTS (articles tagged to specific podcast days):\n'
        for r in stats['reassigned'][:20]:
            to_days = r.get('approved_days') or ([r['better_theme']] if r.get('better_theme') else ['?'])
            reassign_lines += f"- '{r.get('title','?')}' from {r.get('today','?')} → {', '.join(to_days)}\n"

    recat_lines = ''
    if stats['recategorized']:
        recat_lines = '\nCATEGORY RETAGS (user corrected the curator\'s category assignment):\n'
        for r in stats['recategorized'][:20]:
            recat_lines += f"- '{r.get('title','?')}' from {r['original_category']} → {r['category']}\n"

    return f"""A user has been rating RSS news articles for their personal feed and podcast.
Analyze the patterns and write concise, actionable bullet points for the curator's scoring prompt.

USER-CURATED EXEMPLARS (manually flagged by the user, from anywhere on the web, as ideal examples of
their interests — this is the strongest signal available, stronger than the passive ratings below):
{exemplar_lines or '(none yet)'}

GOOD FIT articles (user liked these and tagged them to podcast days):
{good_lines or '(none yet)'}

INTERESTING articles (user finds these relevant but not podcast-quality — boost these topics in relevance scoring):
{interesting_lines or '(none yet)'}

BAD FIT articles (user explicitly disliked these):
{bad_lines or '(none yet)'}
{reassign_lines}{recat_lines}
Task: Write 6-12 bullet points that a news-scoring AI should use to calibrate RELEVANCE scores.
Focus on:
(a) Topic and framing signals from the exemplars first, then Good/Interesting vs Bad articles
(b) Topics in exemplars or Interesting articles that may be under-represented in the main feed
(c) Source or content-type patterns worth noting
(d) Any day-reassignment patterns (articles consistently moved to specific podcast days)
(e) Any category-retag patterns (articles consistently miscategorized by the curator)

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
    exemplar_count    = len(stats.get('exemplars', []))
    good_count        = len(stats['good'])
    interesting_count = len(stats.get('interesting', []))
    bad_count         = len(stats['bad'])
    reassign_count    = len(stats['reassigned'])
    recat_count       = len(stats.get('recategorized', []))

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

    category_retag_lines = ''
    if stats.get('category_from_to'):
        category_retag_lines = '\n**Category retag summary:**\n'
        for from_cat, to_cats in stats['category_from_to'].items():
            for to_cat, count in sorted(to_cats.items(), key=lambda x: x[1], reverse=True):
                category_retag_lines += f'- {from_cat} → {to_cat}: {count} articles\n'

    status = '(DRY RUN — no changes written)' if dry_run else '✅ config/feedback_examples.txt updated'

    return f"""## Feedback Training Run — {now}

**Files processed:** {', '.join(files) if files else 'none'}
**Ratings:** {exemplar_count} Exemplars, {good_count} Good, {interesting_count} Interesting, {bad_count} Bad, {reassign_count} reassigned to day(s), {recat_count} recategorized
**Status:** {status}

**Top liked sources:** {', '.join(f'{s} ({n})' for s, n in top_good_sources) or 'n/a'}
**Top disliked sources:** {', '.join(f'{s} ({n})' for s, n in top_bad_sources) or 'n/a'}
**Categories liked:** {', '.join(f'{c} ({n})' for c, n in top_good_cats) or 'n/a'}
**Categories disliked:** {', '.join(f'{c} ({n})' for c, n in top_bad_cats) or 'n/a'}
{day_reassign_lines}{category_retag_lines}
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
    backfilled = backfill_exemplar_titles(LOOKBACK_DAYS)
    if backfilled:
        print(f'   🔎 Backfilled {backfilled} exemplar title(s) from source pages')
    files, ratings = load_feedback(LOOKBACK_DAYS)
    qualifying = [f for f in files]

    if len(qualifying) < MIN_FILES:
        print(f'ℹ️  Insufficient feedback ({len(qualifying)} qualifying files, need {MIN_FILES}). Skipping.')
        sys.exit(0)

    exemplar_count = len([r for r in ratings if r.get('rating') == 'exemplar'])
    good_count     = len([r for r in ratings if r.get('rating') == 'good'])
    bad_count      = len([r for r in ratings if r.get('rating') == 'bad'])
    print(f'   {len(qualifying)} files, {exemplar_count} Exemplars / {good_count} Good / {bad_count} Bad ratings')

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
