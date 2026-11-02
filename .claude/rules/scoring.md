---
paths:
  - "super_rss_curator_json.py"
  - "article_review_audit.py"
  - "calibration_agent.py"
  - "feedback_trainer.py"
  - "feedback_archive.py"
  - "standing_preferences.py"
  - "generate_weekly_report.py"
  - "review.html"
  - "webapp/**"
  - "config/scoring_*.json"
  - "config/limits.json"
  - "config/feed_slots.json"
  - "config/calibration_bounds.json"
  - "config/news_interests.txt"
  - "config/quality_charter.txt"
  - "config/standing_preferences.txt"
  - "tests/test_slot_allocation.py"
  - "tests/test_article_review_audit.py"
  - "tests/test_review_*.py"
  - "tests/test_episode_verdict.py"
---

# Scoring, ratings and calibration — see [docs/decisions/scoring.md](../../docs/decisions/scoring.md)

Read the podcast repo's [`docs/MANIFESTO.md`](https://github.com/zirnhelt/curated-podcast-generator/blob/main/docs/MANIFESTO.md) before changing scoring, the gate, or what a feed admits.

## Scoring

- **Feed selection is ranked, not floored.** Pass 1 fills `min_slots` regardless of the floor; pass 2 fills to `max_slots` above it. The floor bounds quality, not volume.
- **News has a world lane.** `world_slots` (4) go to gate-flagged major world events ranked by `q_gate`, on top of `max_slots`. The ratings starved world news once; keep the lane out of `calibration_bounds.json` knobs.
- **The weights are fitted against ratings, and two fitted values were deliberately overridden:** `w_local` stays at 0.20 (an editorial commitment, and zeroing it disables the local bonus), and `w_quality` stays at 0.15–0.20 (a range-restriction artifact). Weights stay **out** of `calibration_bounds.json`.
- **One wildcard a day rides on top of the slots** (pass 3): the best `q_gate` (≥ `WILDCARD_MIN_Q_GATE`) the interest profile missed. Not a rescue for a thin category.
- **The deep-scoring queue is split**, not sorted by `q_gate`: `NEWS_INTEREST_RESERVE_SHARE` (0.4) goes to interest rank, held at every prefix length (`_interleave_reserved`).
- **The review corpus is a quota sample.** Rates within a stratum are unbiased; the corpus-wide rate is not. Never quote the headline good-rate as feed quality; use `stratified_estimate()`. Categories rotate within each stratum (`rotate_review_categories()`) so small categories get rated.
- **The audit reads across weeks.** Its **Needs Attention** findings carry how many weekly audits in a row reported them (from `reports/weekly_metrics.jsonl`); at 3 they escalate. Before paying for a stage, or for a test of an alternative, read **What each score buys**: its out-of-time AUC beside its cost by stage.
- **The weekly review stays bounded.** Corpus tables read a rolling 90 days; trend tables show 8 weeks then one row a quarter (`weekly_metrics.jsonl` keeps every week); dated `.md` reports are pruned at 13 weeks, never the weekly HTML (gh-pages deploys it with `keep_files: false`). `CALIBRATION_LOG.md` keeps 8 weeks in full, `notes.md` its last 6 entries plus Haiku-folded standing lessons. A finding that stops firing goes to **Closed Findings**.
- **A verdict is feed × podcast:** `good` (both), `interesting` (feed only), `podcast_only` (show only), `bad` (neither). Feed, band, sweep and source metrics count good+interesting; day fit (`theme_routing.per_day.good_pct`) counts good+podcast_only. Block a source only at n ≥ 8 with zero positives of any kind, `podcast_only` included.
- `standing_preferences.txt` is **the reader's**: reject rules placed in the gate's subject list (same call, no extra cost), edited by hand or by merging a weekly proposal PR. The pipeline owns `GATE_REJECT_RUBRIC`. A place rule goes in code or config, never here (see the sources rule).

## Feedback History (`feedback/`)

Ratings from `review.html` land in `feedback/YYYY-MM-DD.json`. They are the reader's data: never edit them by hand. `feedback_archive.py` keeps the directory bounded in three layers — **always distil before deleting**:

| Layer | File | Lifetime |
|-------|------|----------|
| Raw | `feedback/YYYY-MM-DD.json` | `limits.feedback_retention_days` (90) |
| Distilled | `feedback/feedback_rollup.json` | permanent — statistics plus a ~300-word prose `lessons` block (one Haiku call per archived batch) |
| Cold | `feedback/archive/YYYY-MM.jsonl.gz` | permanent, lossless |

`feedback/reviewed_urls.json` answers "already reviewed?" for the curator; `load_reviewed_urls()` unions it with live files. `article_review_audit.py` reads live and archived shards; `feedback_trainer.py` reads 30 days raw plus the rollup.

**The review batch is 12, spent at the margin:** 1 `wildcard` (its own stratum so the audit can judge the slot), 7 `near_miss` (lost a slot by the fewest points in their category, `review_near_misses()`), 2 `in_feed` (top-of-feed canary; never drop it) and 2 `unfiltered` (highest-scoring gate rejects). `review_pools()` keeps them a partition. The episode card saves `episode_segments` and `episode_note` beside the verdict; the podcast's weekly script review reads them.

**A review batch is offered once.** `review_offered_ledger()` keeps an earlier batch's articles out of the next (the ledger rides in `feed-review.json` as `_offered`), so a missed day is dropped, not queued; `review.html` keys drafts and its saved flag on `_batch`, never the calendar date. The batch is sorted by `fit_reader_model()`; that changes the order only, never the stratified sample.

**Episode verdicts** (`rating: 'episode'`, answer in `episode_verdict`, no `url`) share these files. They are not article ratings: anything that counts rows by `rating` must skip them (`review_history_stats`, the trainer's file minimum do); the page merges them by date.

**`review.html` never holds a credential.** It asks for a fine-grained token (super-rss-feed only, Contents read/write) in a password field when saving, filled from a password manager, and keeps it only while open — never in browser storage. A token was baked into this public page from 2026-06-17 until it was revoked on 2026-09-23; it is still in gh-pages history.

## Calibration agent

Only whitelisted knobs in `calibration_bounds.json`, clamped to bounds and `global_caps`, with a flip-flop guard. **The workflow commits all of `config/`** (after `config_loader.py` + pytest pass in the job). Changes go to `CALIBRATION_LOG.md` and `calibration_memory/change_history.json`. A fresh `article_review_audit_summary.json` is treated as ground truth. Skip reasons are logged verbatim.
