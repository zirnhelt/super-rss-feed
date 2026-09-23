# Role and Style
You are an expert software engineer and product manager. Your persona is direct, technical, and efficient. 

- **Communication:** No fluff. No apologies. No "I can certainly help with that." Get straight to the technical solution.
- **Code Style:** Prioritize clean, readable, modular Python code. Adhere to PEP 8 standards. Focus on maintainability and robustness.
- **Problem Solving:** Always explain the "why" behind significant architectural decisions briefly before writing code.
- **Context:** Remember that this is a personal project intended for local automation and curation. Keep dependencies minimal.

# Project Constraints
- Prioritize Python best practices for automation scripts.
- Use clear, descriptive variable and function names.
- Always include type hints.
- When generating scripts, ensure they are idempotent where possible.
- If an existing function or class can be refactored to be cleaner, do so. Do not create new files if the existing structure can handle the logic.

# Workflow
1. Analyze the request.
2. If the request is unclear, ask for clarification immediately.
3. Propose the technical solution (short).
4. Implement the solution.
5. Provide a summary of changes, specifically highlighting any new dependencies or breaking changes.

PR descriptions auto-populate from `.github/pull_request_template.md`. For local commits, `git config commit.template .gitmessage` loads a matching commit-message template.

This file holds the **standing rules**. The incidents and reasoning behind them live in
[`docs/decisions/`](docs/decisions/), linked from each section. Read the linked file before
changing the code it describes. When you add a rule, keep it here as one or two lines and
put the story in the decision file.

# Project Context

## What This Is

**Super RSS Feed Curator** — an AI-powered RSS aggregator that pulls from ~150 feeds, deduplicates, scores, and publishes 11 categorized JSON feeds plus 7 themed daily podcast feeds via GitHub Pages. Runs nightly on GitHub Actions. The audience is a single user in Williams Lake, BC (Cariboo region); the podcast feeds are read by the sibling repo `curated-podcast-generator`, whose show is public.

Live site: `https://zirnhelt.github.io/super-rss-feed/`
Repo: `github.com/zirnhelt/super-rss-feed`

## Terminology

### "ponytail"
When the user says "ponytail", they are referring to the concept described at:
https://abhishek-shankar.com/posts/best-agent-upgrade-wasnt-a-mode

Ponytail is a portable AI agent skill distribution pattern. The core idea: define agent skills/behaviors once in reusable skill files (a `skills/` directory), then deploy them via lightweight platform-specific adapters across multiple AI coding environments (Claude Code, Codex, GitHub Copilot, Cursor, Windsurf, etc.). A single source of truth for agent behavior, no duplication across platforms.

Reference implementation: https://github.com/DietrichGebert/ponytail

## API Cost Management

Keep API costs as low as possible at all times. This is a hard constraint.

- **Prefer small models** (e.g. `claude-haiku-4-5-20251001`) for simple tasks like classification, extraction, summarization, and short-form generation. Only use larger models when the task genuinely requires it.
- **Use prompt caching** wherever possible. Structure prompts so that long, stable context (system prompts, documents, tool definitions) comes first and can be cached.
- **Minimize tokens**: write concise system prompts, strip unnecessary whitespace, avoid redundant instructions.
- **Batch requests** rather than issuing one call per item when the API supports it.
- **Short-circuit early**: if a cheap check (keyword filter, regex, small model) can rule out most cases, do it before calling a larger/more expensive model.
- **Never call the API speculatively** or "just in case" — every call must serve a clear purpose.
- **Brave Search is shared with the podcast.** One Search key serves both repos, and its monthly cap is also the podcast's research budget. Read Brave's per-key usage export before trusting any estimate; `api_usage` prices Brave at $0.005 a call.
- When in doubt, ask: "Can I do this with fewer tokens or a cheaper model?"

---

# Codebase Structure

## Active Source Files

| File | Purpose |
|------|---------|
| `super_rss_curator_json.py` | **Main pipeline** — the only curator script that runs. Fetch → filter → dedup → score → categorize → merge → output. |
| `config_loader.py` | Loads and validates all `config/` files. Use its functions rather than opening JSON directly. `python config_loader.py` validates and exits non-zero on errors. |
| `cache.py` | `Cache` (TTL JSON dict) and `FeedHTTPCache` (ETag/Last-Modified/skip_until per feed URL). |
| `api_usage.py` | Thread-safe tracker for Claude token counts + Cohere/Brave/Kagi call counts + cost estimate. |
| `cohere_integration.py` | Cohere Rerank + Embed. Auto-activates when `COHERE_API_KEY` is set; every public function is a no-op when disabled. |
| `fetch_images.py` | Open Graph images (favicon fallback); also harvests `apple.news` IDs from the same page fetch. |
| `calibration_agent.py` | Weekly. Reads `calibration_stats_cache.json` and proposes bounded adjustments to the whitelisted config knobs. Uses `claude-sonnet-4-5`. |
| `feedback_trainer.py` | Weekly. Reads `feedback/` ratings (30 days raw + the rollup) and updates `config/feedback_examples.txt`. |
| `feedback_archive.py` | Weekly. Distils old ratings into `feedback/feedback_rollup.json`, compresses raw files to `feedback/archive/`, maintains `feedback/reviewed_urls.json`. Idempotent; `--dry-run`, `--no-distil`. |
| `standing_preferences.py` | Weekly. Turns notes on "bad" ratings into proposed lines for `config/standing_preferences.txt` and opens a PR (one Haiku call, only when there are new notes). Merge adopts, close declines for good (`feedback/standing_proposals.json`). |
| `feed_discovery.py` | Weekly feed discovery — searches Brave/Kagi, scores candidates, writes `feed_discovery_report.json`. |
| `integrate_discoveries.py` | Reconciles `feeds.opml` with reality: `--auto-add-threshold` adds discovery candidates; `--heal` is the feed health agent. Writes `FEED_HEALTH_LOG.md`. |
| `corpus_alignment_report.py` | Weekly audit of upstream interest scores against per-theme fit. Writes `reports/CORPUS_ALIGNMENT_REPORT_<date>.md`. |
| `article_review_audit.py` | Weekly, stdlib-only. Joins ratings against pipeline scores. Writes `reports/ARTICLE_REVIEW_AUDIT_<date>.md` + `article_review_audit_summary.json` (read by calibration and the weekly report). |
| `score_scrub_report.py` | Spot-checks live feeds. Writes `reports/FEED_REVIEW_<date>.md`. |
| `generate_weekly_report.py` | Produces `reports/weekly-report-YYYY-WNN.html` (deployed to gh-pages at the root). |
| `log_feed_results.py` | Parses curator stdout into `FEED_LOG.md` (newest first; older days compressed to weekly summaries). |
| `validate_podcast_feeds.py` | Quality **report** on the 7 podcast feeds, in its own job after the deploy. Never exits non-zero on a finding. |
| `tools/review_filter_priority.py` | Cohere-powered review of filter/priority logic; writes `tools/filter_priority_review.md`. |

Dated reports live in `reports/`; the root holds code, config, caches and running logs.

## Configuration (`config/`)

All config is loaded via `config_loader.py`. Never open config files directly in application code.

| File | Purpose |
|------|---------|
| `system.json` | Cache paths and TTLs, base URLs, `lookback_hours` (48), and the `kagi_news` / `topic_queries` on-off switches. |
| `limits.json` | Feed sizes, retention, per-source caps, thresholds, dedup parameters, batch sizes. **Tunable by calibration agent.** |
| `filters.json` | `blocked_sources`, `blocked_keywords`, `blocked_keywords_unless_local`, `local_signals`, `blocked_title_patterns`, `blocked_url_path_patterns`. |
| `standing_preferences.txt` | **The reader's** reject rules, one per line, placed in the quality gate's subject list (same call, no extra cost). Edited by hand or by merging a weekly proposal PR. The pipeline owns the built-in subjects in `GATE_REJECT_RUBRIC`; the reader owns this file. |
| `categories.json` | Category definitions: name, emoji, description. |
| `category_rules.json` | Per-category include/exclude keyword rules. |
| `news_interests.txt` | The personal interest profile, used by the **news head only** (relevance dimension + Cohere interest ranking). The most impactful news-feed tuning lever. |
| `quality_charter.txt` | Interest-independent newsworthiness rubric: the quality gate (`q_gate`) and background for theme prompts. Never mention personal interests here. |
| `feeds.json` | Output feed metadata (JSON Feed 1.1); `"rss": true` adds an RSS 2.0 mirror. |
| `source_preferences.json` | Source type map (`print`/`broadcast`), per-type score adjustments, `max_per_source` caps. |
| `feed_slots.json` | Per-category `min_slots` (filled regardless of floor) and `max_slots`. |
| `podcast_schedule.json` | The 7 themed podcast feeds: charters, `min_score`, `holdover_threshold`, `rescore_sources`, `targeted_rescore`, `excluded_content`. **Tunable by calibration agent.** |
| `calibration_bounds.json` | Whitelist of auto-tunable knobs and their bounds; `forbidden` lists what the agent may never touch. |
| `scoring_weights.json` | Composite weights, **fitted against ratings** — see Scoring below. |
| `scoring_modifiers.json` | `local_keyword_bonus`, `wire_quality_penalty`, `source_type_quality_adjustments`. |
| `topic_queries.json` | Brave/Kagi topic queries (switched off by `system.json` since 2026-09-23). |
| `feedback_examples.txt` | Generated by `feedback_trainer.py`; injected into the scoring prompt. |

## Feedback History (`feedback/`)

Ratings from `review.html` land in `feedback/YYYY-MM-DD.json`. `feedback_archive.py` keeps the directory bounded in three layers — **always distil before deleting**:

| Layer | File | Lifetime |
|-------|------|----------|
| Raw | `feedback/YYYY-MM-DD.json` | `limits.feedback_retention_days` (90) |
| Distilled | `feedback/feedback_rollup.json` | permanent — statistics plus a ~300-word prose `lessons` block (one Haiku call per archived batch) |
| Cold | `feedback/archive/YYYY-MM.jsonl.gz` | permanent, lossless |

`feedback/reviewed_urls.json` answers "already reviewed?" for the curator; `load_reviewed_urls()` unions it with live files. `article_review_audit.py` reads live and archived shards; `feedback_trainer.py` reads 30 days raw plus the rollup.

**`review.html` never holds a credential.** It asks for a fine-grained token (super-rss-feed only, Contents read/write) in a password field when saving, filled from a password manager, and keeps it only while open — never in browser storage. A token was baked into this public page from 2026-06-17 until it was revoked on 2026-09-23.

## Output Feeds

11 category feeds (`feed-local.json`, `feed-ai-tech.json`, `feed-climate.json`, `feed-homelab.json`, `feed-wellness.json`, `feed-news.json`, `feed-science.json`, `feed-scifi.json`, `feed-homestead.json`, `feed-design.json`, `feed-outdoors.json`) and 7 podcast feeds (`feed-podcast-{monday..sunday}.json`), all JSON Feed 1.1.

**RSS 2.0 mirrors:** a feed with `"rss": true` in `config/feeds.json` (currently `local`) also gets `feed-<category>.xml`, rendered by `generate_rss_feed()` from the finished JSON Feed dict so the two can't drift, capped at `RSS_MAX_ITEMS` (100). `<guid>` is `id` (always the publisher URL).

**The podcast feeds are a contract.** `curated-podcast-generator` reads the keys in `PODCAST_FEED_CONTRACT` and defaults any that are missing, so renaming or dropping one changes the show without an error. `tests/test_podcast_feed_contract.py` pins the list against `generate_podcast_feed()`; the podcast keeps a matching list and degrades its run on a breach. Change both lists together.

## Runtime Cache Files (root, committed by CI, mirrored to gh-pages)

| File | Purpose | TTL |
|------|---------|-----|
| `scored_articles_cache.json` | Scores by URL hash; avoids re-scoring. | 48 h |
| `shown_articles_cache.json` | Articles already surfaced. | 14 days |
| `shown_terms_cache.json` | Term sets for cross-run story dedup. | 14 days |
| `wlt_cache.json` | Williams Lake Tribune scrape. | 48 h |
| `podcast_articles_cache.json` | Rolling pool for podcast theme scoring. | 7 days |
| `theme_scores_cache.json` | Per-article, per-theme fit. Version key `THEME_SCORE_CACHE_VERSION`. | 7 days |
| `podcast_shown_cache.json` | URLs used per day's episode. | 7 days |
| `image_cache.json` | Open Graph image URLs. | — |
| `feed_http_cache.json` | Conditional-GET state, failure counts/kind, `resolved_url`. **Must be persisted** or the backoff and paid-fallback cutoff never fire. | — |
| `calibration_stats_cache.json` | Per-run stats for the calibration agent. | 14 days |
| `theme_holdover_cache.json` | Cross-week bank of future-theme articles. | 28 days |
| `apple_news_cache.json` | Harvested `apple.news` IDs. | articles 14 days |

`calibration_memory/` holds the calibration agent's `recurring_issues.json`, `change_history.json` and `notes.md`.

---

# CI/CD Workflows — see [docs/decisions/scheduling-and-ci.md](docs/decisions/scheduling-and-ci.md)

## `generate-feed.yml` — nightly pipeline

- The 04:00 UTC run and its 07:00 UTC backup arrive as `workflow_dispatch` from a **Cloudflare Worker** in the sibling repo (`curated-podcast-generator/cloudflare/scheduler/`) with a `run_slot` input. The podcast reads the pool at 08:05 UTC.
- **One GitHub cron remains, `0 10 * * *`**, as the backstop for the Worker being down. Don't remove it; don't add the ladder ticks back.
- **Gate on `inputs.run_slot`, never `github.event.schedule`.** A source channel switched off by a missed gate reads exactly like a quiet week — the `USE_SEARCH_APIS` bug.
- Steps: download feeds and caches from gh-pages → bootstrap thin feeds → run the curator → log to `FEED_LOG.md` → copy `review.html` unchanged → commit caches → deploy `output/` and verify the gh-pages tip byte-matches.
- **`validate` is a separate job that never fails.** A permanently red check buries the signals that matter. Keep it out of `build`.
- Secrets: `ANTHROPIC_API_KEY` (required); `COHERE_API_KEY`, `BRAVE_API_KEY`, `KAGI_API_KEY` (optional).

## `weekly-maintenance.yml` — Sunday 13:00 UTC

Eight jobs in order, each skippable by `workflow_dispatch` input: **discovery** (auto-merged PR at threshold 65) → **feed-health** (`--heal`; after discovery because both rewrite `feeds.opml`) → **calibration** (commits all of `config/`) → **feedback-training** (archive, then train) → **standing-preferences** (a proposal PR, never auto-merged; skipped while one is open) → **quality-review** (the three reports into `reports/`) → **filter-review** → **report** (weekly HTML to gh-pages).

`git_push_retry.sh` auto-resolves rebase conflicts only in generated files (`GENERATED_PATTERNS`, which includes `reports/*`); a conflict in anything hand-editable fails the step.

## Other workflows

- `tests.yml` — config validation + pytest on changes to code, config, tests or requirements.
- `deploy-static.yml` — copies `review.html` to gh-pages on push.
- `cleanup-branches.yml` — stale branch cleanup.

---

# Key Conventions

## Pipeline Architecture (`super_rss_curator_json.py`)

1. **Fetch** — `feedparser`, last 48 h, conditional GET via `FeedHTTPCache`. Free recovery before paid: 403 → feed-reader UA retry; 404/410 → `_discover_feed_url()` (cached as `resolved_url`). Then Brave → Kagi → Google News RSS. ≥3 consecutive failures skip Brave/Kagi; unrecoverable failures back off 6 h / 24 h / 72 h.
2. **WLT scrape** — BeautifulSoup scrapes Williams Lake Tribune directly.
3. **Topic news** — Brave News + Kagi from `topic_queries.json`, only when `USE_SEARCH_APIS=true` **and** `system.json` → `topic_queries.enabled`. **Off since 2026-09-23 as a two-week trial; review 2026-10-07** (~47 Brave calls a night for 1 of 467 category items). The run log prints `Topic queries: disabled`.
4. **Filter** — `filters.json`: blocked sources, keywords (`blocked_keywords_unless_local` allows a local override), title patterns, URL path patterns, and bare homepages.
5. **Prescore gate** — high-volume aggregators must match a `PRESCORE_KEYWORDS` term before paid scoring.
6. **Deduplicate** — URL hash → fuzzy title → term-set containment (source priority local > print > broadcast), plus Cohere similarity when enabled.
7. **Cross-run dedup** against `shown_terms_cache`.
8. **Score (gated)** — the only scoring mode:
   a. **Quality gate** (`score_quality_gate()`): one Haiku pass returns `q_gate` (0-100, against `quality_charter.txt`) **and** a `gate_reject` verdict against `GATE_REJECT_RUBRIC`, both cached. Local articles bypass the score but not the rejection. API failure fails open.
   b. **News head**: gate survivors are ordered by Cohere Rerank against `news_interests.txt` (ordering only), then the display-bound slice gets full Q/R/L Haiku scoring with `feedback_examples.txt`; the rest keep `q_gate`.
9. **Local priority** — `local_signals` matches get score ≥ 80 and the `local` feed.
10. **Source preferences** — per-type adjustments.
11. **Scrub** — `scrub_feed_with_haiku()` applies step 8a's verdicts. **It makes no API call**; name and `(kept, scrub_stats)` contract kept for the calibration agent.
12. **Slot allocation** — `apply_feed_slot_allocation()`, ranked (see Scoring).
13. **Images** — up to 50 articles.
14. **Categorize** — keyword rules + Claude category assignment.
15. **Podcast cache** — entry gated by `q_gate >= quality_gate.podcast_floor` (or `local >= 25`); theme scores computed once at ingest against the charters + quality charter (never the interest profile); `targeted_rescore` days get a single-charter second pass.
16. **Podcast feeds** — all 7 regenerated every run from the pool (pure cache reads for the other 6 days).
17. **Diversify** — per-source caps.
18. **Merge & output** — JSON Feed files + `curated-feeds.opml`.

## Conventions

- **URLs:** everything passes through `canonicalize_url()` before hashing.
- **Caches:** `Cache('file.json', ttl_hours=48)` → `load()` returns `{}` on missing/corrupt; `save(data)`. `FeedHTTPCache`: `load()` once at startup, `save()` once at shutdown.
- **API usage:** after every Claude call, `api_usage.record_claude_usage(response.usage)` (`batch=True` for batch results); `api_usage.record_call('cohere' | 'brave' | 'kagi')` for the others; print `api_usage.format_summary()` at the end.
- **Cohere:** check `cohere_integration.is_enabled()`; public functions return falsy when disabled, so always fall back.

## Safety rules for the automated agents

- **Feed health agent** (`--heal`) — see [docs/decisions/sources.md](docs/decisions/sources.md). Evidence makes a candidate; a **fresh live probe** decides. Nothing is deleted: retirement flips `type="retired"` and `recheck_retired()` restores. If none of 3 healthy control feeds answers, the fault is local and the pass changes nothing. `--heal-max-feeds` caps the blast radius. A Google News stand-in needs an article from the last 30 days.
- **Calibration agent** — only whitelisted knobs in `calibration_bounds.json`, clamped to bounds and `global_caps`, with a flip-flop guard. **The workflow commits all of `config/`.** Changes go to `CALIBRATION_LOG.md` and `calibration_memory/change_history.json`. A fresh `article_review_audit_summary.json` is treated as ground truth. Skip reasons are logged verbatim.

## Scoring — see [docs/decisions/scoring.md](docs/decisions/scoring.md)

- **Feed selection is ranked, not floored.** Pass 1 fills `min_slots` regardless of the floor; pass 2 fills to `max_slots` above it. The floor bounds quality, not volume.
- **The weights are fitted against ratings, and two fitted values were deliberately overridden:** `w_local` stays at 0.20 (an editorial commitment, and zeroing it disables the local bonus), and `w_quality` stays at 0.15–0.20 (a range-restriction artifact). Weights stay **out** of `calibration_bounds.json`.
- **The deep-scoring queue is split**, not sorted by `q_gate`: `NEWS_INTEREST_RESERVE_SHARE` (0.4) goes to interest rank, held at every prefix length (`_interleave_reserved`).
- **The review corpus is a quota sample.** Rates within a stratum are unbiased; the corpus-wide rate is not. Never quote the headline good-rate as feed quality; use `stratified_estimate()`.
- **Source verdicts count `interesting` as positive.** Block a source only at n ≥ 8 with zero positives of any kind.

## The podcast pool — see [docs/decisions/podcast-pool.md](docs/decisions/podcast-pool.md)

- **Holdover never fills the pool:** `FRESH_POOL_SHARE` (0.5) reserves half of `POOL_CAP` for the current week; the bank is trimmed worst-first. `PODCAST_POOL_DEBUG=1` traces pool composition.
- **The pool cap is theme-aware:** `THEME_RESERVE_SHARE` (0.4) of direct-qualify slots go to candidates at or above p80 of the day's theme.
- **`_theme_score` is a percentile and cannot show charter collapse**; read `_theme_score_raw`. `RAW_FIT_FLOORS` are per weekday; refit all seven off a measured month.
- **A theme is only meaningful if something can win it.** Joint 7-theme scoring collapses narrow themes; `targeted_rescore` re-asks one charter at a time, and its `rescore_sources` list is the load-bearing half. The standing guard is `run_stats['theme_argmax']`. **Sourcing cannot fix a starved theme — check the argmax before touching `feeds.opml`.**
- **`podcast_content_exclusion()`** drops op-eds and crime incidents from the podcast pool only (`podcast_schedule.json` → `excluded_content`). The crime classifier is fitted: category-gated, title-anchored, ambiguous terms need justice context. **Widen the exemption list, never the rule; refit against the live pool, never against appetite.** Applied at one choke point after the pools merge.

## Sources — see [docs/decisions/sources.md](docs/decisions/sources.md)

- **Feed item `url` is not identity.** Code reading a written feed back must use `item_source_link(item)`, never `item['url']`.
- **Apple News IDs are discovered, never constructed.** `resolve_apple_news_url()` tiers article ID > channel ID > publisher URL.
- **A rediscovered feed URL lives in `feed_http_cache.json`** until the weekly heal writes it into `feeds.opml`.
- **Comment feeds are not article feeds.** `integrate_discoveries.is_comment_feed()` is the single predicate, applied at the top of `evaluate_candidates()` and in `_probe_page_for_feeds()`. Never add one by hand.

## Known Gotchas

1. **WLT cache corruption** — `wlt_cache.json` entries can degrade to bare strings. Always guard with `isinstance(v, dict)` before accessing fields.
2. **Cache merge conflicts** — Actions commits caches to `main`; local `git pull` can conflict. Keep the remote version.
3. **Feed HTTP blocking** — some sites reject the default User-Agent. Both `fetch_images.py` and feed fetching send custom UA headers.
4. **`shown_articles_cache` bloat** — cleanup runs in `load_shown_cache()` past ~300K.
5. **`THEME_SCORE_CACHE_VERSION`** — bump it whenever the theme score formula changes.
6. **Bootstrap** — `python super_rss_curator_json.py --bootstrap-feeds` refills thin feeds from the podcast cache; CI runs it when any feed has < 20 items.

---

# Local Development

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY='...'
export COHERE_API_KEY='...'   # optional
export BRAVE_API_KEY='...'    # optional

# Validate config (exits non-zero on errors)
python config_loader.py

# Tests
pip install pytest && python -m pytest tests/ -q

# Full run
python super_rss_curator_json.py feeds.opml

# Recover thin feeds
python super_rss_curator_json.py --bootstrap-feeds
```

**Dependencies** (`requirements.txt`): `feedparser`, `anthropic`, `requests`, `beautifulsoup4`, `cohere`, `tzdata`

# Decision records

| File | Covers |
|------|--------|
| [scheduling-and-ci.md](docs/decisions/scheduling-and-ci.md) | The nightly workflow: the Worker ladder, the backstop cron, `USE_SEARCH_APIS`, the `validate` job |
| [scoring.md](docs/decisions/scoring.md) | Ranked slot fill, fitted weights, the deep-scoring reserve, the review corpus, source verdicts |
| [podcast-pool.md](docs/decisions/podcast-pool.md) | Holdover, the theme reserve, raw theme scores, targeted rescore, content exclusion |
| [sources.md](docs/decisions/sources.md) | The feed health agent, rediscovered URLs, comment feeds, item identity, Apple News |
