# Super RSS Feed Curator

An AI-powered RSS aggregator: ~150 feeds plus Kagi News clusters → fetch, filter, dedup, score, categorize → 11 category JSON feeds plus 7 themed daily podcast feeds on GitHub Pages, nightly on GitHub Actions. The audience is one reader in Williams Lake, BC (Cariboo); the podcast feeds are read by the sibling repo `curated-podcast-generator`, whose show is public. Live site `https://zirnhelt.github.io/super-rss-feed/`.

The values behind both curators are in the podcast repo's [`docs/MANIFESTO.md`](https://github.com/zirnhelt/curated-podcast-generator/blob/main/docs/MANIFESTO.md): read it before changing scoring, the gate, or what a feed admits.

**Style:** direct and technical, no fluff. Clean PEP 8 Python with type hints and descriptive names; minimal dependencies; idempotent scripts. Explain the "why" of an architectural decision briefly before the code. Refactor an existing function rather than adding a file. End with a summary that names new dependencies, breaking changes and cost impact. Ask when a request is unclear.

**Detail lives in `.claude/rules/`** (loaded when you touch the files they cover) and the incidents behind each rule in [`docs/decisions/`](docs/decisions/). Read the linked decision file before changing the code it describes. A new rule goes in the matching rule file as a line or two; its story goes in the decision file.

PR descriptions auto-populate from `.github/pull_request_template.md`; `git config commit.template .gitmessage` loads the matching commit template.

## NEVER

- Run a paid or state-writing script to "try" a change (table below). Stub the API in a test instead. The `spend` hook asks first; say why the task needs a live run.
- Merge a PR before its `pytest` check has finished green on the current head. The `merge` hook denies it. Eight PRs here merged before CI finished; bot-opened PRs have no check at all.
- Commit regenerated caches, logs, `reports/` or `feedback/` from a session unless the task is about them. The Stop hook points them out; restore with `git checkout -- <file>`.
- Edit `feedback/*.json` (the reader's ratings; denied in settings) or `config/standing_preferences.txt` (the reader's rules; asks first).
- Rename or drop a key in `PODCAST_FEED_CONTRACT`, the `generate-feed.yml` / `refresh-editorial.yml` file names, the `run_slot` input, or `_changes` / `date_published` in `weekly-state-article.json` without the matching change in `curated-podcast-generator` (see Cross-repo contracts).
- Remove the `0 10 * * *` backstop cron, gate on `github.event.schedule`, or add a `paths:` filter to `tests.yml`'s `pull_request` trigger (see the CI rule).
- Put scoring weights, the world lane or the podcast local lane into `calibration_bounds.json`; zero `w_local`.
- Skip, disable or loosen a test to get green.

## Running and testing

Cloud sessions: the SessionStart hook builds `venv/` (Python 3.11, from `requirements-lock.txt`, plus pytest) and puts it on `PATH`. **Use 3.11**: the container's default 3.13 can't import the pinned `feedparser` 6.0.10 (it needs `cgi`), and CI runs 3.11. The hook also exports `USE_SEARCH_APIS=false`; the code defaults it to `true`.

```bash
python config_loader.py          # validate config/ (exits non-zero on errors)
python -m pytest tests/ -q       # ~450 tests, ~3 s, no API keys needed
```

Locally: `python3.11 -m venv venv && venv/bin/pip install -r requirements-lock.txt pytest`.

**What each entry point costs.** Everything below spends money or rewrites committed state, so none of it is a test:

| Command | Spends | Writes |
|---|---|---|
| `super_rss_curator_json.py feeds.opml` | Haiku, Cohere; Brave/Kagi when `USE_SEARCH_APIS` isn't `false` | Every root cache, `output/` |
| `super_rss_curator_json.py --bootstrap-feeds` | Re-scores the pool (Haiku/Cohere) | Feed files |
| `--refresh-hot` / `--refresh-editorial` | Gate only / nothing | Feed files |
| `feed_discovery.py` | 23 Brave queries + Haiku | Discovery report and cache |
| `integrate_discoveries.py --heal` / `--auto-add-threshold` | — | `feeds.opml` (`--dry-run` doesn't) |
| `calibration_agent.py` | A Claude call | `config/` only if `CALIBRATION_DRY_RUN=false` (default `true`); always its logs |
| `feedback_archive.py` | Haiku distil (`--no-distil` skips) | `feedback/` (`--dry-run` doesn't) |
| `feedback_trainer.py`, `standing_preferences.py`, `generate_weekly_report.py`, `score_scrub_report.py` | A Claude call each | Config, ledger, `weekly-state-article.json`, reports |
| `tools/review_filter_priority.py` | Cohere | Its review file |

## API cost management

Keep API costs as low as possible at all times. This is a hard constraint.

- **Prefer small models** (`api_usage.HAIKU_MODEL`, Haiku 5.5) for classification, extraction, summarization and short-form generation; a larger model only when the task needs it.
- **Use prompt caching**: long, stable context (system prompts, documents, tool definitions) first.
- **Minimize tokens**: concise prompts, no redundant instructions. **Batch** where the API supports it.
- **Short-circuit early**: a keyword filter, regex or small model before a larger one.
- **Never call the API speculatively.** Ask: "Can I do this with fewer tokens or a cheaper model?"
- **Brave Search is shared with the podcast.** One Search key serves both repos, and its monthly cap is also the podcast's research budget. Read Brave's per-key usage export before trusting any estimate; `api_usage` prices Brave at $0.005 a call. The curator stops at `system.json` → `brave.max_calls_per_run` (25; late-October nights used 0-3), and every Brave call in this repo is counted in `api_usage`.

**Anthropic prices** (USD per million tokens, first-party API, checked 2026-10-08; refresh from the pricing page before any cost decision):

| Model | Input | Output | Cache read |
|-------|-------|--------|------------|
| Haiku 5.5 (prompt ≤ 100K tokens) | $0.10 | $0.50 | $0.01 |
| Haiku 5.5 (prompt > 100K) | $0.50 | $2.50 | $0.05 |
| Haiku 4.5 | $1 | $5 | $0.10 |
| Sonnet 5 / 5.5 | $2 | $10 | $0.20 |
| Sonnet 4.5 | $3 | $15 | $0.30 |
| Opus 5.5 | $4 | $20 | $0.20 |
| Opus 5 | $5 | $25 | $0.50 |

Cache writes are 1.25x input (5-minute TTL) or 2x (1-hour TTL). The Batch API halves every line, cache included. A cancelled batch still bills the requests that finished before the cancel. Baseline for September 2026 was $31.21 billed (list price, no discounts) across both keys: `cariboosignals` $21.0 (Sonnet 5 script and polish about 3/4 of it), `superfeed` $10.2 (Haiku scoring $9.2).

## Codebase

| File | Purpose |
|------|---------|
| `super_rss_curator_json.py` | **Main pipeline**, ~8k lines (~95k tokens: read it by function, never whole). Fetch → filter → dedup → score → categorize → merge → output. See the pipeline rule. |
| `config_loader.py` | Loads and validates `config/`. Use its functions, never open config JSON directly. |
| `cache.py` | `Cache` (TTL JSON dict), `FeedHTTPCache`, `atomic_write_json` / `atomic_write_text`. |
| `sanitize.py` | Makes third-party content inert: `safe_url`, `plain_text`, `sanitize_html`, `sanitize_feed`; `is_public_http_url` and `get_public` for the pipeline's own fetches. |
| `api_usage.py` | Thread-safe tracker: Claude tokens by stage, Cohere/Brave/Kagi calls, cost estimate. |
| `cohere_integration.py` | Rerank + Embed; active when `COHERE_API_KEY` is set, every public function a no-op otherwise. |
| `fetch_images.py` | Open Graph images (favicon fallback); harvests `apple.news` IDs from the same fetch. |
| `calibration_agent.py` | Weekly. Bounded adjustments to whitelisted config knobs (Haiku 5.5, thinking off, effort `high`). |
| `feedback_trainer.py` / `feedback_archive.py` | Weekly. Ratings → `config/feedback_examples.txt`; distil, compress and ledger old ratings (`--dry-run`, `--no-distil`). |
| `standing_preferences.py` | Weekly. Notes on "bad" ratings → a proposal PR for `config/standing_preferences.txt`. Merge adopts, close declines (`feedback/standing_proposals.json`). |
| `feed_discovery.py` / `integrate_discoveries.py` | Weekly. Find and score candidate feeds; reconcile `feeds.opml` (`--auto-add-threshold`, `--heal`), writing `FEED_HEALTH_LOG.md`. |
| `article_review_audit.py` | Weekly, stdlib-only. Ratings vs pipeline scores → `reports/ARTICLE_REVIEW_AUDIT_<date>.md`, `article_review_audit_summary.json`, `reports/weekly_metrics.jsonl`. Holds `fit_reader_model()` (nightly review-batch order). Reads this file's price-table date. |
| `corpus_alignment_report.py`, `score_scrub_report.py`, `generate_weekly_report.py` | Weekly reports into `reports/`; the last also writes `weekly-state-article.json`. |
| `log_feed_results.py` | Curator stdout → `FEED_LOG.md` (newest first; older days folded weekly). |
| `validate_podcast_feeds.py` | Quality **report** on the podcast feeds, its own job after deploy; never exits non-zero. |
| `tools/review_filter_priority.py` | Cohere review of filter/priority logic → `tools/filter_priority_review.md`. |

**Config (`config/`)**, all via `config_loader.py`: `system.json` (cache paths/TTLs, URLs, `local_scrapes`, `lookback_hours`, `brave`, `hot_refresh`, `kagi_news` (incl. `digest`), `standing_preferences` (feeds that ignore `[show]` lines), `topic_queries`), `limits.json` and `podcast_schedule.json` (**tunable by calibration**), `filters.json`, `standing_preferences.txt` (the reader's; a `[show]` line keeps its subject off the podcast only), `categories.json`, `category_rules.json`, `news_interests.txt` (news head only; the biggest news-tuning lever), `quality_charter.txt` (interest-independent; never mention personal interests), `feeds.json` (`"rss": true` adds an RSS mirror), `source_preferences.json`, `feed_slots.json`, `calibration_bounds.json` (whitelist + `forbidden`), `scoring_weights.json` (fitted against ratings), `scoring_modifiers.json`, `topic_queries.json`, `feedback_examples.txt` (generated).

Dated reports live in `reports/`; the root holds code, config, caches and running logs.

## Conventions

- **URLs:** everything passes through `canonicalize_url()` before hashing.
- **Caches:** `Cache('file.json', ttl_hours=48)` → `load()` returns `{}` on missing/corrupt; `save(data)`. `FeedHTTPCache`: `load()` once at startup, `save()` once at shutdown.
- **Every JSON cache, state, config, OPML, markdown log or `reports/` write goes through `cache.atomic_write_json` / `atomic_write_text`**, never `open(path, 'w')` or `'a'`: CI commits whatever is on disk, and a truncated cache loads as `{}`. An appending log is read and rewritten whole.
- **Every published feed goes out through `write_feed()`** (sanitize, then atomic write). Never `json.dump` a feed. Text fields are stripped, not escaped.
- **A fetch of a URL taken from feed content goes through `sanitize.get_public()`**, never a bare `requests.get`. It caps the body (`MAX_BODY_BYTES`) and abandons the call at `MAX_FETCH_SECONDS`.
- **API usage:** after every Claude call, `api_usage.record_claude_usage(response.usage, stage='<step>')` (`batch=True` for batch results); `api_usage.record_call('cohere' | 'brave' | 'kagi')` for the others; print `api_usage.format_summary()` at the end. A Brave call in the curator goes through `_take_brave_call()`.
- **Cohere:** check `cohere_integration.is_enabled()`; public functions return falsy when disabled, so always fall back.
- **`anthropic` is pinned at 0.40.0**, older than the `thinking` kwarg (a `TypeError`). Send newer fields through `extra_body`, as `calibration_agent.py` does. Message Batches live under `client.beta.messages.batches`.
- **Haiku 5.5 thinks unless told not to**, and thinking shares `max_tokens`. Every Haiku call passes `extra_body=api_usage.HAIKU_EXTRA_BODY` (batch params take the key directly) and reads the reply with `api_usage.response_text()`, never `content[0]`: a refusal is a 200 with no text. Its tokenizer counts the same text as ~30% more tokens.
- **Cache merge conflicts:** Actions commits caches to `main`; on a local pull conflict, keep the remote version.
- **History comes from the GitHub API, not `git log`:** checkouts are shallow, and `git log --since` answers short with no error. Merged means `merged_at` is set.

## Cross-repo contracts (the highest-risk changes)

`curated-podcast-generator` breaks silently, not loudly, when one of these moves. Change both repos together; the first four are pinned in `tests/test_podcast_feed_contract.py`.

| This repo provides | Read by | Breaks how |
|---|---|---|
| `feed-podcast-{day}.json` on gh-pages, keys in `PODCAST_FEED_CONTRACT` | The podcast script at 08:05 UTC | Missing keys default; the episode changes and the run degrades |
| `generate-feed.yml` + its `run_slot` input | The Cloudflare Worker (`cloudflare/scheduler/src/index.ts`) and `deploy-scheduler.yml` | The nightly never starts; the 10:00 backstop lands after the 08:05 read |
| `refresh-editorial.yml` | The podcast's review job (scheduler PAT) | The episode review stops landing in `feed-local` |
| `_changes`, `date_published` in `weekly-state-article.json` on main | The Sunday Meta Moment (`get_upstream_week_changes`) | That half of the segment goes empty |
| `feed-local.json` | The podcast's `daily-podcast.yml` | — |
| The Brave Search key | Both repos' monthly cap | The podcast's research budget runs out |

## Automation, and who fixes what

- **Bots:** `generate-feed` commits caches to `main` and deploys gh-pages; `refresh-hot` and `refresh-editorial` write gh-pages only; `weekly-maintenance` commits `config/`, logs, `feeds.opml` and `reports/` to `main`, auto-merges the discovery PR and opens the standing-preferences PR. Bot pushes and bot PRs (`GITHUB_TOKEN`) trigger no workflows, so the weekly jobs run the tests themselves before committing.
- **Scheduled Claude tasks that touch this repo** (from the podcast side): the daily **roadmap fixer** may open and merge `claude/roadmap-*` PRs here when the root cause is upstream; the weekly **roadmap triage** only reads. One-shot check-ins after a merge use `/check-nightly <PR>`, which reports and never opens a PR.
- **Before fixing a feed or podcast-pool symptom**, list open PRs and non-main branches on both repos: a fix may already be in flight from the roadmap fixer or another session.

## Decision records

| File | Covers |
|------|--------|
| [scheduling-and-ci.md](docs/decisions/scheduling-and-ci.md) | The Worker ladder, the backstop cron, `USE_SEARCH_APIS`, the `validate` job |
| [scoring.md](docs/decisions/scoring.md) | Ranked slot fill, fitted weights, the deep-scoring reserve, the review corpus, source verdicts |
| [podcast-pool.md](docs/decisions/podcast-pool.md) | Holdover, the theme reserve, raw theme scores, targeted rescore, content exclusion |
| [sources.md](docs/decisions/sources.md) | The feed health agent, rediscovered URLs, comment feeds, item identity, Apple News |

Rules in `.claude/rules/`: `pipeline.md` (the 18 steps, caches, output feeds), `scoring.md` (scoring, ratings, review batch, calibration), `podcast-pool.md`, `sources.md` (sources, feed health, discovery), `ci.md` (workflows).
