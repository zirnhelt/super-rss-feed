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

# Project Context

## What This Is

**Super RSS Feed Curator** — an AI-powered RSS aggregator that pulls from 100+ feeds, deduplicates, scores, and publishes 11 categorized JSON feeds plus 7 themed daily podcast feeds via GitHub Pages. Runs twice daily on GitHub Actions. The audience is a single user in Williams Lake, BC (Cariboo region).

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
- When in doubt, ask: "Can I do this with fewer tokens or a cheaper model?"

---

# Codebase Structure

## Active Source Files

| File | Purpose |
|------|---------|
| `super_rss_curator_json.py` | **Main pipeline** — the only curator script that runs. Fetch → filter → dedup → score → categorize → merge → output. |
| `config_loader.py` | Loads and validates all `config/` files. Use its functions rather than opening JSON directly. |
| `cache.py` | `Cache` (TTL JSON dict) and `FeedHTTPCache` (ETag/Last-Modified/skip_until per feed URL). |
| `api_usage.py` | Thread-safe tracker for Claude token counts + Cohere/Brave/Kagi call counts + cost estimate. Call `api_usage.record_claude_usage(usage)` after every Claude response. |
| `cohere_integration.py` | Cohere Rerank + Embed integration. Auto-activates when `COHERE_API_KEY` is set. All public functions are no-ops when disabled — code can always call them. |
| `fetch_images.py` | Scrapes Open Graph images for articles; falls back to favicon. Also harvests `apple.news` article/channel IDs from the same page fetch (`extract_apple_news_ids`). |
| `calibration_agent.py` | Weekly agent that reads `calibration_stats_cache.json` and proposes bounded adjustments to `config/limits.json` and `config/podcast_schedule.json`. Uses `claude-sonnet-4-5`. |
| `feedback_trainer.py` | Weekly agent that reads `feedback/YYYY-MM-DD.json` ratings from `review.html` and updates `config/feedback_examples.txt`. Also injects the archived rollup so signal older than its 30-day window still counts. |
| `feedback_archive.py` | Weekly. Distils feedback older than `feedback_retention_days` into `feedback/feedback_rollup.json`, compresses the raw files into `feedback/archive/YYYY-MM.jsonl.gz`, and maintains the `feedback/reviewed_urls.json` ledger. Statistics are stdlib; one Haiku call per *archived batch* (~monthly, ~$0.013) consolidates the topic/framing `lessons` block. Idempotent; `--dry-run` and `--no-distil` supported. |
| `feed_discovery.py` | Weekly feed discovery — searches Brave/Kagi, scores candidates, writes `feed_discovery_report.json`. |
| `integrate_discoveries.py` | Reconciles `feeds.opml` with reality. `--auto-add-threshold` adds high-confidence discovery candidates; `--heal` is the weekly feed health agent — it re-verifies chronically failing feeds against the live network and relocates, substitutes, retires, or restores them. Writes `FEED_HEALTH_LOG.md`. |
| `corpus_alignment_report.py` | Audits whether upstream interest scores align with per-theme fit scores across the 7-day podcast cache. |
| `article_review_audit.py` | Weekly offline audit joining `feedback/` ratings against pipeline scores, theme routing, and volume trends. Writes `ARTICLE_REVIEW_AUDIT_<date>.md` + `article_review_audit_summary.json` (consumed by `calibration_agent.py` as ground truth and by the weekly report). Stdlib-only, no API calls. |
| `score_scrub_report.py` | Spot-checks live feeds for scoring/scrubbing quality. |
| `generate_weekly_report.py` | Produces `weekly-report-YYYY-WNN.html` from all weekly sub-reports. |
| `log_feed_results.py` | Parses curator stdout, appends a run summary row to `FEED_LOG.md`. |
| `validate_podcast_feeds.py` | Quality **report** on the 7 podcast JSON feeds, run in its own job after the daily deploy. Writes a per-theme table to the job summary and never exits non-zero on a finding. |
| `test_setup.py` | Basic environment/dependency check; run locally before first use. |
| `tools/review_filter_priority.py` | Cohere-powered code review of filter/priority logic; writes `tools/filter_priority_review.md`. |

## Dead Files — Do Not Touch

`super_rss_curator.py`, `super_rss_curator_cached.py`, any `*.backup*`, any `fix_*.py`, `super_rss_curator_json_old.py`

## Configuration (`config/`)

All config is loaded via `config_loader.py`. Never open config files directly in application code.

| File | Purpose |
|------|---------|
| `system.json` | Cache file paths, cache TTLs, base URLs, `lookback_hours` (default 48). |
| `limits.json` | Feed sizes, retention days, per-source caps, score thresholds, dedup parameters, batch sizes. **Tunable by calibration agent.** |
| `filters.json` | `blocked_sources`, `blocked_keywords`, `blocked_keywords_unless_local`, `local_signals`. |
| `categories.json` | Category definitions: name, emoji, description. |
| `category_rules.json` | Per-category include/exclude keyword rules (used when Cohere is active). |
| `news_interests.txt` | The personal interest hierarchy used by the **news head only** (relevance dimension + Cohere interest ranking). Extensive examples included. Edit carefully — this is the most impactful news-feed tuning lever. |
| `quality_charter.txt` | Interest-independent newsworthiness rubric. Drives the absolute quality gate (`q_gate`) and provides background context in theme-scoring prompts. Never mention personal interests here. |
| `scoring_interests.txt` | Legacy single-file profile. Kept as a fallback for `news_interests.txt`/`quality_charter.txt`; no longer read directly by the pipeline. |
| `feeds.json` | Output feed metadata: titles, descriptions, base URL for JSON Feed 1.1. |
| `source_preferences.json` | Source type map (`print`/`broadcast`) with per-type score adjustments and `max_per_source` caps. |
| `feed_slots.json` | Per-category min/max article counts. |
| `podcast_schedule.json` | 7 daily themed podcast feed definitions: label, categories, keywords, scoring_prompt, min_score, holdover_threshold, plus per-day `rescore_sources` and the `targeted_rescore` block (gotcha 14). **Tunable by calibration agent.** |
| `calibration_bounds.json` | Whitelist of auto-tunable config knobs and their safety bounds for the calibration agent. |
| `scoring_weights.json` | Dimensional composite weights for general feeds (`w_quality`, `w_relevance`, `w_local`) and podcast feeds (+ `w_theme`). |
| `scoring_modifiers.json` | `local_keyword_bonus`, `wire_quality_penalty`, `source_type_quality_adjustments`. |
| `topic_queries.json` | Brave/Kagi search queries for topic-driven article discovery. |
| `feedback_examples.txt` | Generated by `feedback_trainer.py` from user ratings; injected into Claude scoring prompt. |

## Feedback History (`feedback/`)

Ratings submitted by `review.html` land in `feedback/YYYY-MM-DD.json`. The directory is
kept bounded by `feedback_archive.py` in three layers — always distil before deleting:

| Layer | File | Lifetime |
|-------|------|----------|
| Raw | `feedback/YYYY-MM-DD.json` | `limits.feedback_retention_days` (90) |
| Distilled | `feedback/feedback_rollup.json` | permanent — statistics **plus** a prose `lessons` block |
| Cold | `feedback/archive/YYYY-MM.jsonl.gz` | permanent, lossless (one original file object per line, ~4.5:1 compressed) |

The rollup has two layers because they capture different things. **Statistics** (verdict
counts by source/category, score-band histograms, day-reassignment and category-retag
matrices, score sums for means) are free but only see what is already a categorical field —
they are blind to topic and framing, which lives in the article title. So when a batch is
actually archived, `distil_lessons()` makes **one Haiku call** that consolidates the batch's
titles into `rollup['lessons']`. It merges rather than appends, so the block stays ~300
words forever. Statistics are folded in *before* the call, so a missing key, `--no-distil`,
or an API error costs only the prose layer — archival always completes.

`feedback/reviewed_urls.json` is a compact `{url: rated_at}` ledger so the curator can
answer "already reviewed?" without parsing the history. `load_reviewed_urls()` unions the
ledger with any live files, so it is correct before, during, and after archival. Pruned at
`limits.feedback_url_ledger_days` (180) — safe because the curator only ever sees articles
from the last 48 h and the longest pool horizon is the 28-day theme holdover.

Consumers: `article_review_audit.py` reads live **and** archived shards (full horizon);
`feedback_trainer.py` reads 30 days of raw plus the rollup; the curator reads only the ledger.

## Output Feeds

11 category feeds + 7 daily podcast feeds, all JSON Feed 1.1 (plus an RSS 2.0 mirror
for `local` — see below):

```
feed-local.json        feed-ai-tech.json      feed-climate.json
feed-homelab.json      feed-wellness.json     feed-news.json
feed-science.json      feed-scifi.json        feed-homestead.json
feed-design.json       feed-outdoors.json

feed-podcast-monday.json    feed-podcast-tuesday.json   feed-podcast-wednesday.json
feed-podcast-thursday.json  feed-podcast-friday.json    feed-podcast-saturday.json
feed-podcast-sunday.json
```

### RSS 2.0 mirrors

Any feed whose `config/feeds.json` entry carries `"rss": true` also gets a
`feed-<category>.xml` RSS 2.0 mirror — currently `local` only. `generate_rss_feed()`
renders it from the finished JSON Feed dict rather than re-walking the articles, so
the two can never drift, and `curated-feeds.opml` points a `type="rss"` outline at
the `.xml` wherever one exists. The mirror is capped at `RSS_MAX_ITEMS` (100) — a
reader only needs a recent window; the JSON feed stays the full retention archive.

Item mapping: `<link>` is the reader-facing `url` (not always the publisher URL),
`<guid isPermaLink="false">` is `id` (always the publisher URL, so read/unread state
survives an Apple News link upgrade), `<description>` is the escaped `content_html`.
To add a mirror for another category, set `"rss": true` on it — nothing else.

## Runtime Cache Files (root directory, committed by CI)

These files persist pipeline state between runs. They live in the repo root and are committed by GitHub Actions after each run. They are also deployed to `gh-pages` so the next run can download the freshest version.

| File | Purpose | TTL |
|------|---------|-----|
| `scored_articles_cache.json` | Article scores keyed by URL hash. Eliminates redundant Claude/Cohere scoring calls. | 48 h |
| `shown_articles_cache.json` | URL → timestamp of articles already surfaced. Prevents re-surfacing. | 14 days |
| `shown_terms_cache.json` | Term sets for cross-run story dedup. | 14 days |
| `wlt_cache.json` | Williams Lake Tribune scraped articles. | 48 h |
| `podcast_articles_cache.json` | Rolling 7-day pool of quality articles for podcast theme scoring. | 7 days |
| `theme_scores_cache.json` | Per-article, per-theme fit scores. Cache version key: `THEME_SCORE_CACHE_VERSION`. | 7 days |
| `podcast_shown_cache.json` | URLs used in each day's podcast episode (prevents re-use within 7 days). | 7 days |
| `image_cache.json` | Open Graph image URLs keyed by article URL. | — |
| `feed_http_cache.json` | Per feed URL: ETag/Last-Modified/skip_until for conditional GET, plus `failures`/`failure_kind` (paid-fallback circuit breaker + backoff ladder) and `resolved_url` (a rediscovered feed location, applied instead of the OPML URL). | — |
| `calibration_stats_cache.json` | Per-run audit stats consumed by the calibration agent. | 14 days |
| `theme_holdover_cache.json` | Cross-week pool of articles that scored well on a future theme. | 28 days |
| `apple_news_cache.json` | Harvested `apple.news` article IDs (by publisher URL) and channel IDs (by source name), scraped for free during the image fetch. | articles 14 days; channels permanent |

## Calibration Memory (`calibration_memory/`)

Persistent memory for the weekly calibration agent:

| File | Purpose |
|------|---------|
| `recurring_issues.json` | Issues seen across multiple calibration runs. |
| `change_history.json` | Log of all config changes the agent has applied. |
| `notes.md` | Free-form notes from the agent across sessions. |

---

# CI/CD Workflows

## `generate-feed.yml` — Daily pipeline

**Schedule:** the 04:00 UTC run (8 PM Pacific the previous day) and its 07:00 UTC
backup rung both arrive as `workflow_dispatch` from a **Cloudflare Worker**, which
lives in the sibling repo at `curated-podcast-generator/cloudflare/scheduler/` and
sends a `run_slot` input. GitHub's cron is best-effort — it delays scheduled
workflows under load and drops the tick outright once the delay passes the next
window — and this feed has a hard downstream deadline: the podcast reads the
scored pool at 08:05 UTC.

**One GitHub cron remains**, `0 10 * * *`, purely as the backstop for the *Worker*
being down, timed to pair with the podcast's own GitHub backstop at 11:05 UTC. On
a normal night it costs ~20 s — it starts, `preflight` sees the day is covered,
and it stands down. Do not remove it, and do not add the two ticks back to the
`schedule:` block; that is what keeps the schedule from depending on one vendor.

**`preflight` gates on `inputs.run_slot`, not `github.event.schedule`.** Anything
that needs to know which rung it is on must read the input — a schedule-triggered
run leaves it empty, which is how the backstop is told apart from a manual run.

**`USE_SEARCH_APIS` was the one that got missed.** It read
`github.event_name == 'schedule' || inputs.use_search_apis`, which was correct
until the ladder moved to the Worker — after that every nightly run arrived as
`workflow_dispatch` with `use_search_apis` defaulting to false, so topic queries
*and* the Brave/Kagi recovery path for failing feeds were off on every real run.
Only the 10:00 UTC backstop had them on, and that one stands down as soon as
preflight sees the day is covered. It now also accepts `inputs.run_slot != ''`.
This is the failure mode to look for whenever sourcing looks thin: a source
channel that is switched off reads exactly like a quiet week.

`weekly-maintenance.yml` and `cleanup-branches.yml` stay on GitHub's cron:
Workers Free allows only 5 Cron Triggers per account, all five are spent on the
two ladders where a late trigger costs the day, and a weekly report arriving an
hour late costs nothing.

Also triggered manually with optional `use_search_apis` flag.

**Steps:**
1. Download existing feeds + caches from `gh-pages` (atomic JSON validation; skips stale files).
2. Bootstrap thin feeds from podcast cache if any category feed < 20 items.
3. Run `python super_rss_curator_json.py feeds.opml`.
4. Log results to `FEED_LOG.md` via `log_feed_results.py`.
5. Bake `REVIEW_PAT` token (reversed) into `review.html` → `output/review.html`.
6. Commit updated cache files to `main`.
7. Deploy `output/` to `gh-pages`, then verify the tip byte-matches this run's output.

**`validate` is a separate job** (`needs: build`) that reads the published feeds
off the gh-pages tip and runs `validate_podcast_feeds.py`. It reports to the job
summary and **never fails**. It used to be two steps inside `build` — one under
`continue-on-error: true`, one re-raising the outcome after the deploy — so its
only possible effect was reddening a run whose feeds had already shipped, and
from 2026-08-30 it did that on every single run. A permanently red check is not
an alarm; it buries the two signals in `build` that do mean something (the
curator, and the gh-pages byte-match verifier). Keep it out of `build`, and keep
it green: recalibrating a charter is a human's weekly job, not a reason to
re-run the pipeline.

**Required secrets:** `ANTHROPIC_API_KEY`
**Optional secrets:** `COHERE_API_KEY`, `BRAVE_API_KEY`, `KAGI_API_KEY`, `REVIEW_PAT`

## `weekly-maintenance.yml` — Sunday 13:00 UTC

Six sequential jobs (each skippable via `workflow_dispatch` inputs):

1. **discovery** — `feed_discovery.py` → `integrate_discoveries.py` → auto-merged PR adding high-confidence feeds (threshold 65).
2. **feed-health** — `integrate_discoveries.py --heal` repairs feeds that have been failing, commits `feeds.opml` + `FEED_HEALTH_LOG.md` to `main`. Runs after discovery, not beside it: both rewrite `feeds.opml`, and `git_push_retry.sh` refuses to auto-resolve conflicts in hand-editable files.
3. **calibration** — `calibration_agent.py` reads 14-day stats, proposes bounded config changes, commits to `main`.
4. **feedback-training** — `feedback_archive.py` distils + archives old ratings, then `feedback_trainer.py` reads `feedback/` ratings, updates `config/feedback_examples.txt`, commits to `main` (including `feedback/`).
5. **quality-review** — `score_scrub_report.py` + `corpus_alignment_report.py` + `article_review_audit.py`, commits reports to `main` (including `article_review_audit_summary.json`, which the next week's calibration run reads).
6. **filter-review** — `tools/review_filter_priority.py` (Cohere), commits `tools/filter_priority_review.md`.
7. **report** — `generate_weekly_report.py`, deploys `weekly-report-*.html` to `gh-pages`.

## `deploy-static.yml` — On push to `main` touching `review.html`

Bakes the `REVIEW_PAT` token and deploys `review.html` to `gh-pages` (keep_files: true).

## `cleanup-branches.yml`

Periodic cleanup of stale branches.

---

# Key Conventions

## Pipeline Architecture (super_rss_curator_json.py)

The pipeline runs in this order. Understand it before touching any stage:

1. **Fetch** — `feedparser` pulls all OPML feeds (last 48 h). Google News proxy URLs are unwrapped. `FeedHTTPCache` handles conditional GET (ETag/Last-Modified) and remembers per-feed failures across runs. Failures escalate through **free** recovery before paid: a 403 gets one retry under a feed-reader User-Agent (`_FEED_READER_UA`), a 404/410 gets `_discover_feed_url()` — `<link rel="alternate">` autodiscovery plus conventional paths, adopting a candidate only if it parses as a feed *with entries* — and the result is cached as `resolved_url` so later runs go direct. Only then do 403/404/421/500/timeout/DNS failures fall back to Brave Search → Kagi → Google News RSS (the last is keyless and runs even when `USE_SEARCH_APIS` is off). Feeds with ≥3 consecutive failures skip Brave and Kagi entirely (free fallback only), and unrecoverable failures (dead DNS, un-rediscoverable 404) back off polling on a 6 h/24 h/72 h ladder.
2. **WLT scrape** — BeautifulSoup scrapes Williams Lake Tribune directly.
3. **Topic news** — Brave News API + Kagi queries from `config/topic_queries.json` (only when `USE_SEARCH_APIS=true`).
4. **Filter** — blocks sources and keywords from `config/filters.json`; `blocked_keywords_unless_local` allows local override.
5. **Prescore gate** — high-volume aggregator sources (e.g. Kagi Small Web) must match at least one keyword from `PRESCORE_KEYWORDS` before reaching paid scoring.
6. **Deduplicate** — URL hash → fuzzy title (`SequenceMatcher`, threshold `dedup_fuzzy_threshold`) → term-set containment. Source priority: local > print > broadcast. + Cohere cosine similarity pass when enabled.
7. **Cross-run dedup** — compares new article term-sets against `shown_terms_cache`.
8. **Score (gated mode)** — two-stage:
   a. **Quality gate** — `score_quality_gate()`: Haiku scores every article's absolute, interest-independent newsworthiness (`q_gate`, 0-100) against `config/quality_charter.txt` (batch `quality_gate.batch_size=30`, cached in `scored_articles_cache`). Local articles bypass the gate; API failure fails open. This is the shared eligibility signal for both news and podcast heads.
   b. **News head** — gate survivors (`q_gate >= quality_gate.gate_floor`) are ordered by Cohere Rerank against `config/news_interests.txt` (ordering only — never converted to a pass/fail score), then the display-bound top slice (2× `feed_slots` max per category) gets full Q/R/L dimensional Haiku scoring with `config/feedback_examples.txt`. Everything else keeps `q_gate` as its score (`gate_scored=True`). Legacy `hybrid`/`cohere-only`/`claude-only` modes remain selectable in `config/scoring_mode.json` for rollback.
9. **Local priority enforcement** — any article matching `local_signals` gets score ≥ 80 and is routed to the `local` feed.
10. **Source preferences** — apply per-type score adjustments from `config/source_preferences.json`.
11. **Quality filter** — drop articles below `min_claude_score` (with per-category floors from `min_score_by_category`).
12. **Final scrub** — Claude Haiku reviews all passing headlines in batches of `haiku_scrub_batch_size=40` to catch sports/celebrity/AI-fluff that passed keyword filters. Floor: `haiku_scrub_floor=10`.
13. **Images** — `fetch_images.py` fetches Open Graph images for up to 50 articles.
14. **Categorize** — assign to 8 feeds using keyword rules + Claude category assignment.
15. **Podcast cache** — pool entry is gated by `q_gate >= quality_gate.podcast_floor` (or `local >= 25`) — no interest score, no keyword gate (theme keywords only boost T at generation time; per-run intake capped at `podcast_candidate_max_per_run`). Theme scores computed in one batch at ingest time against theme charters + the quality charter — the personal interest profile never appears in theme prompts. Days listed in `targeted_rescore` then get a second, single-charter pass over selected articles (`rescore_underserved_themes`, gotcha 14). Per-day `min_score` in `podcast_schedule.json` is a floor on `q_gate`/quality, not the interest composite; the podcast composite (`w_theme=0.65, w_quality=0.25, w_local=0.10, w_relevance=0`) renormalizes over missing dimensions instead of substituting the interest score.
16. **Podcast feed** — all 7 themed feeds regenerated every run from the weekly pool (ingest-time theme scoring means the 6 non-today feeds are pure cache reads, no extra API cost), skipping last 7 days of used articles per theme, routing holdover articles.
17. **Diversify** — per-source caps enforced.
18. **Merge & output** — new articles merged with retained articles (story-overlap dedup); write JSON Feed 1.1 files + `curated-feeds.opml`.

## URL Canonicalization

All URLs pass through `canonicalize_url()` before hashing. This strips UTM and other tracking parameters so two URLs differing only in tracking params are treated as the same article.

## Cache Pattern

```python
cache = Cache('file.json', ttl_hours=48)
data = cache.load()   # returns {} on missing/corrupt file
data[key] = value
cache.save(data)
```

`FeedHTTPCache` has a different interface — call `load()` once at startup, `save()` once at shutdown.

## API Usage Tracking

Every Claude call must be followed by:
```python
api_usage.record_claude_usage(response.usage)
# or for batch:
api_usage.record_claude_usage(result.message.usage, batch=True)
```

For Cohere/Brave/Kagi:
```python
api_usage.record_call('cohere')  # or 'brave', 'kagi'
```

Print the summary at the end of a run:
```python
print(api_usage.format_summary())
```

## Cohere Integration Pattern

All Cohere-powered code paths check `cohere_integration.is_enabled()` first. The module's public functions return falsy/empty values when disabled, so callers can always call them and fall back gracefully:

```python
results = cohere_integration.rerank_articles(articles, query)
if not results:
    results = score_with_claude(articles)
```

## Feed Health Agent Safety

`integrate_discoveries.py --heal` is the only automation that edits the *feed list* rather than
config, so its bounds are about never losing a source by mistake.

**Evidence never decides anything on its own.** A feed becomes a *candidate* from failure
history — `feed_http_cache.json` counts, plus the last 7 days of `FEED_ERRORS.md` as a backstop
for a lost cache — and must clear both floors (`--heal-min-failures` 3, `--heal-min-days` 2)
before it is touched. What actually happens to it is decided by a **fresh probe against the
live network**, in the pipeline's own escalation order: still works → left alone; moved →
relocated; unreachable but still publishing → Google News stand-in; nothing answers → retired.

**Nothing is deleted.** Retirement flips `type="rss"` to `type="retired"`, which `parse_opml()`
stops selecting. The URL, title, reason and date stay in the file, `get_existing_feeds()` still
counts it so discovery cannot re-add it, and `recheck_retired()` restores it automatically once
the source answers again — removing any Google News stand-in that replaced it.

**A broken runner is not a week of dead outlets.** Every verdict is inferred from a failed
request, so before applying anything the agent probes up to 3 feeds with *no* failure history.
If none of them answers, the fault is local and the pass makes no changes at all. `--heal-max-feeds`
(25) caps the blast radius further, spending the budget worst-first.

Google News substitution additionally requires the search feed to carry an article from the last
30 days — the index still answers for a dead outlet, with years-old results, and adopting that
would quietly resurrect a source that stopped publishing.

## Calibration Agent Safety

The calibration agent only modifies keys whitelisted in `config/calibration_bounds.json`. Every proposed change is clamped to `[min, max]` bounds and checked against `global_caps`. A flip-flop guard prevents oscillating changes. All changes are logged to `CALIBRATION_LOG.md` and `calibration_memory/change_history.json`. The agent's prompt includes a fresh (≤14 days) `article_review_audit_summary.json` when present — user review verdicts are treated as ground truth over pipeline-side histograms. Skip/failure reasons are written verbatim to `CALIBRATION_LOG.md` (a "no calibration stats" skip is not a Claude failure).

## Known Gotchas

1. **WLT cache corruption** — `wlt_cache.json` entries can degrade to bare strings. Always guard with `isinstance(v, dict)` before accessing fields.
2. **Cache merge conflicts** — Actions commits caches to `main`; local `git pull` can conflict. Keep the remote version.
3. **Feed HTTP blocking** — some sites reject default User-Agent. Both `fetch_images.py` and feed fetching send custom UA headers.
4. **shown_articles_cache bloat** — cleanup logic runs in `load_shown_cache()` if the file grows past ~300K.
5. **`THEME_SCORE_CACHE_VERSION`** — bump this constant in `super_rss_curator_json.py` whenever the theme score formula changes, to invalidate stale cached scores.
6. **Bootstrap flag** — `python super_rss_curator_json.py --bootstrap-feeds` repopulates thin feeds from the 7-day podcast cache. The CI workflow triggers this automatically when any feed < 20 items.
7. **Feed item `url` is not article identity** — `url` is whatever link the reader should follow; whenever that is not the publisher URL, the publisher URL lives in `external_url` and `id` always stays the publisher URL. Any code reading a written feed back in must use `item_source_link(item)`, never `item['url']`, or those articles stop matching themselves across runs and duplicate nightly. See `FEEDS_MAINTENANCE.md` § "add a source you can read paywall-free".
8. **`applenews://search?term=` is not a real URL** — it was tried and reverted; the scheme launches the News app but has no search path, and feed readers drop non-`http(s)` links entirely. Only `https://apple.news/…` works, and its ID must be **discovered, never constructed** — Apple assigns them opaquely and a fabricated ID is a dead link. `resolve_apple_news_url()` tiers a harvested per-article `A…` ID over a per-publication `T…` channel ID over the publisher URL; only the article tier is promoted to `url` by default. See `FEEDS_MAINTENANCE.md` § "the tiered Apple News resolver".
9. **The theme holdover bank must never fill the podcast candidate pool** — `generate_podcast_feed()` caps its candidate pool at `POOL_CAP` (300) and exempts rescued/holdover articles from the quality sort. Holdover is *not* exempt from the cap itself: `FRESH_POOL_SHARE` (0.5) reserves half the pool for current-week articles and the bank is trimmed worst-first (by banked percentile) to fit. Without that reserve an oversized bank drove the direct-qualify allowance to zero, and the day's feed regenerated purely from holdover — newest item exactly `run_date − 7`, advancing one day per run. Banking is unconditional and percentile-based (`holdover_threshold` 12 means "top 88%"), so the bank grows ~70-100 entries/day/theme every run; `THEME_HOLDOVER_MAX_AVAILABLE_PER_DAY` (400) bounds the available side in `save_theme_holdover_cache()`. Set `PODCAST_POOL_DEBUG=1` to trace fresh-vs-holdover pool composition at every selection stage.

10. **The podcast pool cap must stay theme-aware** — the direct-qualify half of `POOL_CAP` is filled from *two* ranked lists: `THEME_RESERVE_SHARE` (0.4) of the slots go to candidates at or above `THEME_RESERVE_MIN_PCT` (p80) of the day's theme, the rest by upstream `a.score`. `a.score` is the general-interest composite and is theme-blind by construction, so ranking on it alone cuts the most on-theme articles *before* theme scoring ever sees them: on 2026-08-30 the Thursday episode was built entirely from articles with raw charter scores of 10-20 while eight APTN First Nations stories at the 97th-99th theme percentile were dropped for scoring 47-57 upstream against a cutoff of 67. The reserve does not change the pool size, so it costs no extra API calls. Articles with no cached theme score default to percentile 0 and compete on quality as before.

11. **A rediscovered feed URL lives in the cache until the weekly heal promotes it** — when `_discover_feed_url()` finds a moved feed mid-run it writes `resolved_url` into `feed_http_cache.json` rather than rewriting `feeds.opml`, because the OPML is user-curated and a curation run is the wrong place to edit it. The feed works again immediately but the fix is only as durable as the cache, so `--heal` re-verifies the resolved URL each Sunday and writes it into the OPML for real (recording `relocatedFrom`). If the resolved URL later fails it is cleared, so the next run rediscovers from the OPML URL rather than compounding one bad guess.

    **That whole mechanism is inert unless `feed_http_cache.json` is persisted.** It is a runtime cache in a repo that gets a fresh checkout every run: until it was added to the gh-pages download, the `output/` copy and the commit list in `generate-feed.yml`, every failure count reset to zero nightly — the paid-fallback cutoff at 3 consecutive failures could never be reached, the backoff ladder never fired, and each moved feed was rediscovered again the next day. If failure counts ever read as implausibly low, check that plumbing first.

12. **WordPress comment feeds are not article feeds** — `/comments/feed/` (title "Comments for …") carries reader comments: no headline, no body, nothing scoreable. Discovery used to score them like any other feed and four reached `feeds.opml`; they are also disproportionately WAF-blocked, so each cost a failed fetch plus a search fallback every run. `integrate_discoveries.is_comment_feed()` now rejects them at the gate. Never add one by hand.

13. **Percentile-normalized `_theme_score` cannot show charter collapse** — selection ranks *within* a theme (`normalize_theme_scores()`), so the top of a bad distribution is promoted to 90-100 no matter how poor the actual fit; the same Thursday episode showed `_theme_score` 90 for a Windows 11 performance-boost article whose raw charter score was 16. Every item therefore also carries `_theme_score_raw`, the un-rescaled charter output, and `validate_podcast_feeds.py` reports the top-10 mean against a floor.

    **That floor is per theme, because the scale is.** The seven `scoring_prompt`s are independently worded over subjects of very different breadth, so their raw output is not one ladder. Measured top-10 means over the eight runs published 2026-08-30..09-01 are rank-stable and an order of magnitude apart at the ends — sunday 74-85, saturday 62-70, friday 61-69, monday 36-43, thursday 26-36, tuesday 16-22, wednesday 10-18. The original single global `MIN_TOP_RAW_MEAN` (25) drawn across that separated *broad themes from narrow ones*, not healthy from broken: it cut between Thursday and Tuesday, failed Tuesday and Wednesday on every run from the day it was added, and would still have passed a 50% collapse in Sunday.

    **The conclusion originally drawn from that band was wrong, and gotcha 14 is the correction.** This note used to read Wednesday's 10-18 as a narrow charter honestly reporting weak fit. It was a scoring bug. `RAW_FIT_FLOORS` is per weekday, seeded at 0.6x each theme's observed minimum — but tuesday (9) and wednesday (6) were fitted to the *collapsed* scorer and are stale by construction. They are deliberately left un-raised: they still catch a true collapse, and raising them on prediction trades a floor fitted to real numbers for one fitted to hope. **Refit all seven off a measured month once the targeted rescore has been running**, the same way `_SPEECH_RATE_FITS` was refitted from the transcript sidecars in the sibling repo; the report prints every theme's measured value on every run, pass or fail.

14. **A theme's score is only meaningful if something can win it** — `score_all_themes_at_ingest` rates one article against all 7 charters in a single Haiku response, which is cheap and, for the broad themes, fine. But a model asked for 7 numbers at once apportions one general-interest magnitude across them instead of applying each charter independently. Measured on the 2026-09-01 cache: **"Science, Wonder & the Natural World" was the best-fit theme for 82.4% of 2,004 fully-scored articles, and Working Lands, Repair Culture, Arts and Indigenous Lands were best-fit for zero of them.** Repair Culture's maximum over 2,121 articles was 35, against a charter whose own anchors put a teardown at 98 and a Raspberry Pi weather-station build at 68 — Hackaday was supplying ~44 hands-on hardware articles a week throughout, and "Reviving an SD Card With Shorted Capacitors" scored 11. Meanwhile an RCMP shooting story scored 41 on Working Lands, whose charter puts unrelated crime news in its 0-14 OUT OF SCOPE band.

    **The consequence is that sourcing cannot fix a starved theme.** The effect is a fixed per-theme prior, not a reading of the material, so new forestry or repair feeds land in the same 5-12 band and stay below `min_score`. Anyone asked to "enrich" a low-scoring day should check the argmax before touching `feeds.opml`.

    `rescore_underserved_themes()` re-asks the question one charter at a time for the days listed in `podcast_schedule.json` → `targeted_rescore`, reusing `score_articles_for_theme(..., force=True)` (which bypasses both the cached joint score and the Cohere Rerank branch — embedding similarity to the charter text is not a charter judgment either). Candidates come from two places, and **the source list is the load-bearing half**: keyword matching alone misses exactly the articles that matter, because trade-press headlines rarely restate their own beat — "Reviving an SD Card With Shorted Capacitors" contains none of Wednesday's 40 configured keywords. So a day's `rescore_sources` names outlets whose whole output is on-theme *by construction* (Hackaday, iFixit, The Northern Miner, Western Producer); anything broader belongs on the keyword path at `min_keyword_hits` (2, not 1, for the reason the sibling repo's `_build_strict_theme_keywords` exists — one generic word is not evidence). Popular Mechanics and Resilience.org were tried on the source list and removed: they spent the budget on indestructible diamonds and dietary guidelines.

    Cost is bounded on three sides — `score_ceiling` skips what already scores well, `max_articles_per_run` caps a runaway day, and each entry is stamped `rescored` so the work is paid once. At the configured defaults that is at most 4 extra Haiku calls per run (40 articles per theme against a batch size of 30, for two days) while the backlog in the existing pool clears, settling to 1-2 once only each day's new articles are eligible. An article with **no** cached score yet is skipped rather than scored: it is still in flight in the async batch, and becomes eligible next run once there is a score to correct.

    **The standing guard is `run_stats['theme_argmax']`**, not a floor: it records how many articles each theme wins and prints a warning naming any theme that wins none. A per-theme histogram cannot show this — each theme's own distribution merely looked narrow for months. A theme that is best-fit for zero articles is not a narrow theme; it is a theme the scorer has stopped reading the charter for.

---

# Local Development

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY='...'
export COHERE_API_KEY='...'   # optional
export BRAVE_API_KEY='...'    # optional

# Validate config
python config_loader.py

# Full run
python super_rss_curator_json.py feeds.opml

# Recover thin feeds
python super_rss_curator_json.py --bootstrap-feeds
```

**Dependencies** (`requirements.txt`): `feedparser`, `anthropic`, `requests`, `beautifulsoup4`, `cohere`, `tzdata`
