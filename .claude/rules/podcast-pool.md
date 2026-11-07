---
paths:
  - "super_rss_curator_json.py"
  - "validate_podcast_feeds.py"
  - "config/podcast_schedule.json"
  - "tests/test_podcast_*.py"
  - "tests/test_theme_*.py"
---

# The podcast pool — see [docs/decisions/podcast-pool.md](../../docs/decisions/podcast-pool.md)

**The podcast feeds are a contract.** `curated-podcast-generator` reads the keys in `PODCAST_FEED_CONTRACT` and defaults any that are missing, so renaming or dropping one changes the show without an error. `tests/test_podcast_feed_contract.py` pins the list against `generate_podcast_feed()`; the podcast keeps a matching list and degrades its run on a breach. Change both lists together.

**Before fixing a pool symptom, check for a fix in flight.** The podcast's daily roadmap fixer opens `claude/roadmap-*` PRs here when the root cause is upstream, and other sessions push `claude/*` branches. List open PRs and branches on both repos first.

- **Holdover never fills the pool:** `FRESH_POOL_SHARE` (0.5) reserves half of `POOL_CAP` for the current week; the bank is trimmed worst-first. `PODCAST_POOL_DEBUG=1` traces pool composition.
- **The pool cap is theme-aware:** `THEME_RESERVE_SHARE` (0.4) of direct-qualify slots go to candidates at or above p80 of the day's theme.
- **`_theme_score` is a percentile and cannot show charter collapse**; read `_theme_score_raw`. `RAW_FIT_FLOORS` are per weekday; refit all seven off a measured month.
- **A theme is only meaningful if something can win it.** Joint 7-theme scoring collapses narrow themes; `targeted_rescore` re-asks one charter at a time, and its `rescore_sources` list is the load-bearing half. The standing guard is `run_stats['theme_argmax']`. **Sourcing cannot fix a starved theme — check the argmax before touching `feeds.opml`.**
- **Theme keywords match whole words** (`_keyword_pattern`: plural allowed, a trailing `*` for word endings). A keyword is a phrase, never a bare word with a common second sense (`park` matched "amusement park"); measure a new one against the live pool first.
- **Every daily feed carries a local lane** (`select_local_lane`, `local_lane_slots`): fresh Cariboo-anchored stories no recent episode aired, on top of the theme selection and exempt from the theme-fit floor. The show leads with local news every day. Keep it out of calibration.
- **Only the episode's own feed counts as shown** (`episode_day`, the run's UTC weekday). Marking all seven feeds burned each day's best articles in feeds nobody aired.
- **A single-charter rescore is stamped with its charter's fingerprint** (`charter_fingerprint`), so editing a `scoring_prompt` re-asks that day's confirmed scores once; never stamp `rescored: True`.
- **High theme scores are confirmed against the charter** (`confirm_theme_contenders`, `targeted_rescore.contender_band`): Rerank never reads a charter's exclusions, and a false high is the score that airs.
- **`podcast_content_exclusion()`** drops op-eds and crime incidents from the podcast pool only (`podcast_schedule.json` → `excluded_content`). The crime classifier is fitted: category-gated, title-anchored, ambiguous terms need justice context. **Widen the exemption list, never the rule; refit against the live pool, never against appetite.** Applied at one choke point after the pools merge.
- **The pool honours the gate's reject verdict** (`gate_reject`, which holds `_show_verdict()`: the `x` flag or a `[show]` standing-preference match. Rejects are not theme-scored at ingest (`_pool_eligible`). The verdict is stored with each pool and bank entry and refreshed on banked rows from the pool, dropped at that same choke point; `enabled: false` turns it off with the other exclusions; a blocked source is evicted from both caches by `_pool_source_excluded()`). The verdict is a snapshot: a new standing-preference line reaches cached entries only as they are judged again. Review ratings are training data and never a runtime input to the pool.
