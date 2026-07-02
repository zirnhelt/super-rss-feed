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

# Project Context

## What This Is

**Super RSS Feed Curator** — an AI-powered RSS aggregator that pulls from 80+ feeds, deduplicates, scores, and publishes 8 categorized JSON feeds plus 7 themed daily podcast feeds via GitHub Pages. Runs twice daily on GitHub Actions. The audience is a single user in Williams Lake, BC (Cariboo region).

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
| `fetch_images.py` | Scrapes Open Graph images for articles; falls back to favicon. |
| `calibration_agent.py` | Weekly agent that reads `calibration_stats_cache.json` and proposes bounded adjustments to `config/limits.json` and `config/podcast_schedule.json`. Uses `claude-sonnet-4-5`. |
| `feedback_trainer.py` | Weekly agent that reads `feedback/YYYY-MM-DD.json` ratings from `review.html` and updates `config/feedback_examples.txt`. |
| `feed_discovery.py` | Weekly feed discovery — searches Brave/Kagi, scores candidates, writes `feed_discovery_report.json`. |
| `integrate_discoveries.py` | Auto-adds high-confidence discovery candidates to `feeds.opml`. |
| `corpus_alignment_report.py` | Audits whether upstream interest scores align with per-theme fit scores across the 7-day podcast cache. |
| `score_scrub_report.py` | Spot-checks live feeds for scoring/scrubbing quality. |
| `generate_weekly_report.py` | Produces `weekly-report-YYYY-WNN.html` from all weekly sub-reports. |
| `log_feed_results.py` | Parses curator stdout, appends a run summary row to `FEED_LOG.md`. |
| `validate_podcast_feeds.py` | Sanity-checks the 7 podcast JSON feeds after each run. |
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
| `scoring_interests.txt` | The master interest hierarchy sent to Claude for scoring. Extensive examples included. Edit carefully — this is the most impactful tuning lever. |
| `feeds.json` | Output feed metadata: titles, descriptions, base URL for JSON Feed 1.1. |
| `source_preferences.json` | Source type map (`print`/`broadcast`) with per-type score adjustments and `max_per_source` caps. |
| `feed_slots.json` | Per-category min/max article counts. |
| `podcast_schedule.json` | 7 daily themed podcast feed definitions: label, categories, keywords, scoring_prompt, min_score, holdover_threshold. **Tunable by calibration agent.** |
| `calibration_bounds.json` | Whitelist of auto-tunable config knobs and their safety bounds for the calibration agent. |
| `scoring_weights.json` | Dimensional composite weights for general feeds (`w_quality`, `w_relevance`, `w_local`) and podcast feeds (+ `w_theme`). |
| `scoring_modifiers.json` | `local_keyword_bonus`, `wire_quality_penalty`, `source_type_quality_adjustments`. |
| `topic_queries.json` | Brave/Kagi search queries for topic-driven article discovery. |
| `feedback_examples.txt` | Generated by `feedback_trainer.py` from user ratings; injected into Claude scoring prompt. |

## Output Feeds

8 category feeds + 7 daily podcast feeds, all JSON Feed 1.1:

```
feed-local.json        feed-ai-tech.json      feed-climate.json
feed-homelab.json      feed-wellness.json     feed-news.json
feed-science.json      feed-scifi.json

feed-podcast-monday.json    feed-podcast-tuesday.json   feed-podcast-wednesday.json
feed-podcast-thursday.json  feed-podcast-friday.json    feed-podcast-saturday.json
feed-podcast-sunday.json
```

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
| `feed_http_cache.json` | ETag/Last-Modified/skip_until per feed URL for conditional GET. | — |
| `calibration_stats_cache.json` | Per-run audit stats consumed by the calibration agent. | 14 days |
| `theme_holdover_cache.json` | Cross-week pool of articles that scored well on a future theme. | 28 days |

## Calibration Memory (`calibration_memory/`)

Persistent memory for the weekly calibration agent:

| File | Purpose |
|------|---------|
| `recurring_issues.json` | Issues seen across multiple calibration runs. |
| `change_history.json` | Log of all config changes the agent has applied. |
| `notes.md` | Free-form notes from the agent across sessions. |

---

# CI/CD Workflows

## `generate-feed.yml` — Twice-daily pipeline

**Schedule:** Once daily at 04:00 UTC (8 PM Pacific previous day). Also triggered manually with optional `use_search_apis` flag.

**Steps:**
1. Download existing feeds + caches from `gh-pages` (atomic JSON validation; skips stale files).
2. Bootstrap thin feeds from podcast cache if any category feed < 20 items.
3. Run `python super_rss_curator_json.py feeds.opml`.
4. Log results to `FEED_LOG.md` via `log_feed_results.py`.
5. Validate podcast feeds via `validate_podcast_feeds.py`.
6. Bake `REVIEW_PAT` token (reversed) into `review.html` → `output/review.html`.
7. Commit updated cache files to `main`.
8. Deploy `output/` to `gh-pages`.

**Required secrets:** `ANTHROPIC_API_KEY`
**Optional secrets:** `COHERE_API_KEY`, `BRAVE_API_KEY`, `KAGI_API_KEY`, `REVIEW_PAT`

## `weekly-maintenance.yml` — Sunday 13:00 UTC

Six sequential jobs (each skippable via `workflow_dispatch` inputs):

1. **discovery** — `feed_discovery.py` → `integrate_discoveries.py` → auto-merged PR adding high-confidence feeds (threshold 65).
2. **calibration** — `calibration_agent.py` reads 14-day stats, proposes bounded config changes, commits to `main`.
3. **feedback-training** — `feedback_trainer.py` reads `feedback/` ratings, updates `config/feedback_examples.txt`, commits to `main`.
4. **quality-review** — `score_scrub_report.py` + `corpus_alignment_report.py`, commits reports to `main`.
5. **filter-review** — `tools/review_filter_priority.py` (Cohere), commits `tools/filter_priority_review.md`.
6. **report** — `generate_weekly_report.py`, deploys `weekly-report-*.html` to `gh-pages`.

## `deploy-static.yml` — On push to `main` touching `review.html`

Bakes the `REVIEW_PAT` token and deploys `review.html` to `gh-pages` (keep_files: true).

## `cleanup-branches.yml`

Periodic cleanup of stale branches.

---

# Key Conventions

## Pipeline Architecture (super_rss_curator_json.py)

The pipeline runs in this order. Understand it before touching any stage:

1. **Fetch** — `feedparser` pulls all OPML feeds (last 48 h). Google News proxy URLs are unwrapped. Feeds failing with 403/404/421/timeout fall back to Brave Search → Kagi → Google News RSS (the last is keyless and runs even when `USE_SEARCH_APIS` is off). `FeedHTTPCache` handles conditional GET (ETag/Last-Modified).
2. **WLT scrape** — BeautifulSoup scrapes Williams Lake Tribune directly.
3. **Topic news** — Brave News API + Kagi queries from `config/topic_queries.json` (only when `USE_SEARCH_APIS=true`).
4. **Filter** — blocks sources and keywords from `config/filters.json`; `blocked_keywords_unless_local` allows local override.
5. **Prescore gate** — high-volume aggregator sources (e.g. Kagi Small Web) must match at least one keyword from `PRESCORE_KEYWORDS` before reaching paid scoring.
6. **Deduplicate** — URL hash → fuzzy title (`SequenceMatcher`, threshold `dedup_fuzzy_threshold`) → term-set containment. Source priority: local > print > broadcast. + Cohere cosine similarity pass when enabled.
7. **Cross-run dedup** — compares new article term-sets against `shown_terms_cache`.
8. **Score** — Claude Haiku batch scoring (batch size `claude_scoring_batch_size=15`) using `config/scoring_interests.txt` + `config/feedback_examples.txt`. Cohere Rerank replaces this step when enabled.
9. **Local priority enforcement** — any article matching `local_signals` gets score ≥ 80 and is routed to the `local` feed.
10. **Source preferences** — apply per-type score adjustments from `config/source_preferences.json`.
11. **Quality filter** — drop articles below `min_claude_score` (with per-category floors from `min_score_by_category`).
12. **Final scrub** — Claude Haiku reviews all passing headlines in batches of `haiku_scrub_batch_size=40` to catch sports/celebrity/AI-fluff that passed keyword filters. Floor: `haiku_scrub_floor=10`.
13. **Images** — `fetch_images.py` fetches Open Graph images for up to 50 articles.
14. **Categorize** — assign to 8 feeds using keyword rules + Claude category assignment.
15. **Podcast cache** — quality articles saved to rolling 7-day pool; theme scores computed in one batch at ingest time.
16. **Podcast feed** — today's themed feed generated from the weekly pool, skipping last 7 days of used articles, routing holdover articles.
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

## Calibration Agent Safety

The calibration agent only modifies keys whitelisted in `config/calibration_bounds.json`. Every proposed change is clamped to `[min, max]` bounds and checked against `global_caps`. A flip-flop guard prevents oscillating changes. All changes are logged to `CALIBRATION_LOG.md` and `calibration_memory/change_history.json`.

## Known Gotchas

1. **WLT cache corruption** — `wlt_cache.json` entries can degrade to bare strings. Always guard with `isinstance(v, dict)` before accessing fields.
2. **Cache merge conflicts** — Actions commits caches to `main`; local `git pull` can conflict. Keep the remote version.
3. **Feed HTTP blocking** — some sites reject default User-Agent. Both `fetch_images.py` and feed fetching send custom UA headers.
4. **shown_articles_cache bloat** — cleanup logic runs in `load_shown_cache()` if the file grows past ~300K.
5. **`THEME_SCORE_CACHE_VERSION`** — bump this constant in `super_rss_curator_json.py` whenever the theme score formula changes, to invalidate stale cached scores.
6. **Bootstrap flag** — `python super_rss_curator_json.py --bootstrap-feeds` repopulates thin feeds from the 7-day podcast cache. The CI workflow triggers this automatically when any feed < 20 items.

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
