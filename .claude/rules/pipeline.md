---
paths:
  - "super_rss_curator_json.py"
  - "cache.py"
  - "sanitize.py"
  - "api_usage.py"
  - "cohere_integration.py"
  - "fetch_images.py"
  - "*_cache.json"
  - "config/feeds.json"
  - "config/system.json"
---

# Pipeline, caches and output feeds

## Pipeline Architecture (`super_rss_curator_json.py`)

1. **Fetch** — `feedparser`, last 48 h, conditional GET via `FeedHTTPCache`. Free recovery before paid: 403 → feed-reader UA retry; 404/410 → `_discover_feed_url()` (cached as `resolved_url`). Then Brave → Kagi → Google News RSS. ≥3 consecutive failures skip Brave/Kagi; unrecoverable failures back off 6 h / 24 h / 72 h. Every Brave call goes through `_take_brave_call()`, capped by `system.json` → `brave.max_calls_per_run`.
2. **Local scrapes** — `scrape_local_news()` scrapes the homepages in `system.json` → `local_scrapes` (Tribune, Quesnel Observer, 100 Mile Free Press): their RSS is mostly provincial syndication. See [sources.md](../../docs/decisions/sources.md).
3. **Topic news** — Brave News + Kagi from `topic_queries.json`, only when `USE_SEARCH_APIS=true` **and** `system.json` → `topic_queries.enabled`. **Off since 2026-09-23, kept off after the trial (reviewed 2026-10-11)**: ~47 Brave calls a night for 1 of 467 category items. The run log prints `Topic queries: disabled`.
   **Kagi News** (`fetch_kite_news`, `system.json` → `kagi_news`, free): 27 Kite categories (12 stories each since 2026-11-07, one cluster per event via `_collapse_kite_events`), each story a cluster already merged across outlets and summarised. It enters as the finished version of its story: wins same-story dedup over any non-local outlet, yields to any outlet article published after its batch (Kite cuts one a day at 12:00 UTC, 18 h before the nightly; `_dedup_wins`), links the outlet its summary cites first (never `articles[0]`), and carries its summary + talking points as `_excerpt` with `_kite_sources` so the podcast uses the body as-is.
4. **Filter** — `filters.json`: blocked sources, keywords (`blocked_keywords_unless_local` allows a local override), title patterns, URL path patterns, and bare homepages.
5. **Prescore gate** — high-volume aggregators must match a `PRESCORE_KEYWORDS` term before paid scoring.
6. **Deduplicate** — URL hash → fuzzy title → term-set containment (source priority local > print > broadcast), plus Cohere similarity when enabled.
7. **Cross-run dedup** against `shown_terms_cache`.
8. **Score (gated)** — the only scoring mode:
   a. **Quality gate** (`score_quality_gate()`): one Haiku pass returns `q_gate` (0-100, against `quality_charter.txt`) **and** a `gate_reject` verdict against `GATE_REJECT_RUBRIC` **and** a `gate_world` flag against `GATE_WORLD_RUBRIC`, all cached. Local articles bypass the score but not the rejection. API failure fails open.
   b. **News head**: gate survivors are ordered by Cohere Rerank against `news_interests.txt` (ordering only), then the display-bound slice (`quality_gate.deep_slice_multiplier` × `max_slots` per category, 6 since Haiku 5.5) gets full Q/R/L Haiku scoring with `feedback_examples.txt`; the rest keep `q_gate`.
9. **Local priority** — `local_signals` matches get score ≥ 80 and the `local` feed.
10. **Source preferences** — per-type adjustments.
11. **Scrub** — `scrub_feed_with_haiku()` applies step 8a's verdicts (`_feed_rejects`: `x` everywhere, a `[show]` match `s` everywhere but news). **It makes no API call**; name and `(kept, scrub_stats)` contract kept for the calibration agent.
12. **Slot allocation** — `apply_feed_slot_allocation()`, ranked (see the scoring rule).
13. **Images** — up to 50 articles.
14. **Categorize** — keyword rules + Claude category assignment.
15. **Podcast cache** — entry gated by `q_gate >= quality_gate.podcast_floor` (or `local >= 25`); theme scores computed once at ingest against the charters + quality charter (never the interest profile); `targeted_rescore` days (all seven since Haiku 5.5) get a single-charter second pass.
16. **Podcast feeds** — all 7 regenerated every run from the pool (pure cache reads for the other 6 days).
17. **Diversify** — per-source caps.
18. **Merge & output** — JSON Feed files + `curated-feeds.opml`. Before writing, `kite_coverage()` gives each Kagi cluster an outcome (`run_stats.kite_coverage`), and `build_kite_digest()` puts one digest item on top of `feed-news.json`.

## Output Feeds

11 category feeds (`feed-local.json`, `feed-ai-tech.json`, `feed-climate.json`, `feed-homelab.json`, `feed-wellness.json`, `feed-news.json`, `feed-science.json`, `feed-scifi.json`, `feed-homestead.json`, `feed-design.json`, `feed-outdoors.json`) and 7 podcast feeds (`feed-podcast-{monday..sunday}.json`), all JSON Feed 1.1, published to gh-pages.

**RSS 2.0 mirrors:** a feed with `"rss": true` in `config/feeds.json` (currently `local`) also gets `feed-<category>.xml`, rendered by `generate_rss_feed()` from the finished JSON Feed dict so the two can't drift, capped at `RSS_MAX_ITEMS` (100). `<guid>` is `id` (always the publisher URL).

## Runtime Cache Files (root, committed by CI, mirrored to gh-pages)

| File | Purpose | TTL |
|------|---------|-----|
| `scored_articles_cache.json` | Scores by URL hash; avoids re-scoring. | 48 h |
| `shown_articles_cache.json` | Articles already surfaced (`_shown_cache`, a TTL `Cache`). | 14 days |
| `shown_terms_cache.json` | Term sets for cross-run story dedup. | 14 days |
| `wlt_cache.json` | Local paper scrapes (all of `local_scrapes`, keyed by URL hash). | 48 h |
| `podcast_articles_cache.json` | Rolling pool for podcast theme scoring. | 7 days |
| `theme_scores_cache.json` | Per-article, per-theme fit. Version key `THEME_SCORE_CACHE_VERSION`. | 7 days |
| `podcast_shown_cache.json` | URLs used per day's episode. | 7 days |
| `feed_http_cache.json` | Conditional-GET state, failure counts/kind, `resolved_url`. **Must be persisted** or the backoff and paid-fallback cutoff never fire. | — |
| `calibration_stats_cache.json` | Per-run stats for the calibration agent. | 14 days |
| `theme_holdover_cache.json` | Cross-week bank of future-theme articles. | 28 days |
| `apple_news_cache.json` | Harvested `apple.news` IDs. | articles 14 days |

On gh-pages only (downloaded by `generate-feed.yml`, never committed): `image_cache.json` (Open Graph image URLs) and `extract_cache.json` (Kagi Extract text by URL hash, 48 h; thin articles only, 10 pages a request; an extracted article's `_excerpt` carries 2000 chars, which the podcast reads as the story body).

`calibration_memory/` holds the calibration agent's `recurring_issues.json`, `change_history.json` and `notes.md`.

## Cache gotchas

- `wlt_cache.json` entries can degrade to bare strings: guard with `isinstance(v, dict)` before accessing fields.
- Bump `THEME_SCORE_CACHE_VERSION` whenever the theme score formula changes.
- **Deep scoring merges into the scored cache** (`update`, never replace), or the gate's verdict is lost and asked again.
- `--bootstrap-feeds` refills thin feeds from the podcast cache (and re-scores: it spends); CI runs it when any feed has < 20 items.
