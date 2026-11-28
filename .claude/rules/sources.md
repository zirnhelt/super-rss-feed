---
paths:
  - "super_rss_curator_json.py"
  - "feeds.opml"
  - "integrate_discoveries.py"
  - "feed_discovery.py"
  - "fetch_images.py"
  - "sanitize.py"
  - "config/filters.json"
  - "config/source_preferences.json"
  - "config/category_rules.json"
  - "config/topic_queries.json"
  - "tests/test_kite_*.py"
  - "tests/test_comment_feed_gate.py"
  - "tests/test_feed_health_nightly_block.py"
  - "tests/test_local_excerpts.py"
---

# Sources — see [docs/decisions/sources.md](../../docs/decisions/sources.md)

- **A Kagi News cluster is a source, not a duplicate.** It outranks every single-outlet version in dedup (`_source_priority`), but is still gated and scored like any article. Its content is CC BY-NC with credit to Kagi News; the podcast credits it. Its perspectives, quote, timeline and background ride beside `_excerpt` as `_kite_context` (`KITE_CONTEXT_CHARS`), because summary + talking points already fill the excerpt.
- **One Kite cluster per event.** Kite files a story under World and a region with different headlines; `_collapse_kite_events()` keeps the most widely covered telling, judged on shared outlet URLs (`_same_kite_event`), which title dedup cannot see.
- **"Also in the news" items are ordinary news-feed items** (`select_also_in_the_news`, `kagi_news.digest`): widely covered news clusters no feed carried, marked `_also_in_news` + `_kite_label` and opening with the outlet count and Kagi's credit. They are retained like any item but never count as `published` in `kite_coverage` (the headline miss rate stays the feeds' own selection). The one-item digest and its page went on 2026-11-28; `_is_digest_item` only drops a leftover.
- **Feed article links go through the podcast repo's click Worker** (`system.json` → `clicks.base_url` plus the `CLICKS_KEY` secret; both unset means plain links) for the feeds in `clicks.feeds` (every category feed since 2026-11-28; `apply_click_tracking`, category `feed:<feed>`). `_click_signature` must match the Worker's `sign()` (a test pins it): `url` is the tracked link, `external_url` the publisher URL, `id` unchanged, so read back through `item_source_link()`. Never wrap a podcast feed. Every workflow that calls `generate_json_feed()` needs `CLICKS_KEY` (the refreshes rebuild retained items), but only the nightly writes the exposure ledger (`feedback/clicks/exposure.json`). Clicks are evidence, never ratings.
- **Feed item `url` is not identity.** Code reading a written feed back must use `item_source_link(item)`, never `item['url']`.
- **Apple News IDs are discovered, never constructed.** `resolve_apple_news_url()` tiers article ID > channel ID > publisher URL.
- **A rediscovered feed URL lives in `feed_http_cache.json`** until the weekly heal writes it into `feeds.opml`.
- **Editorial-exempt sources skip story-overlap dedup** (`_story_dedup_exempt()`; URL dedup still applies): templated titles like the episode review's read as repeats of yesterday's.
- **So do headline series** (`source_preferences.json` → `series_title_patterns`, anchored on the kicker, e.g. "MEET THE CANDIDATES:"): each instalment is a different story under the same words. Add a series there, never loosen the overlap thresholds.
- **Editorial-exempt sources ride on top of the slots**, and the podcast's review job dispatches `refresh-editorial.yml` once its review is live, so the review lands the morning it is written. The refresh spends nothing, writes no cache, and only places a source in feeds that already carry it.
- **An editorial source has one home feed** (`source_preferences.json` → `editorial_home_category`). `reader_category()` pins it, the refresh splices only there, and the retention merge drops copies elsewhere (`_misfiled_editorial`). "Feeds that already carry the source" alone let one misfiled review spread to every later one.
- **`blocked_sources` is checked wherever stored articles are reused**, not only at fetch: use `is_blocked_source()` / `_pool_source_excluded()`. A substring entry matches inside other names (`"hn"` once blocked every "…Technica" feed); keep entries whole words or domains.
- **`blocked_keywords` and `blocked_keywords_unless_local` match whole words** (`_keyword_pattern`), never substrings: `"mma"` dropped every "summary", `"nfl"` every "inflation". A stem that needs its inflections ends in `*`.
- **`local` means the Cariboo-Chilcotin.** `apply_dimension_adjustments()` demotes a `local` article with no Cariboo anchor (`_has_cariboo_anchor()`); scraped network cards are dropped by `_drop_network_cards()`. A homepage's top `SCRAPE_TOP_CARDS` cards are read whole; below them, only cards naming a Cariboo place (the Free Press runs its local section there).
- **A place rule goes in code or config, never in `standing_preferences.txt`.** The gate cannot hold "outside the Cariboo" reliably (it rejected Cariboo candidate profiles two nights running); out-of-region civic races are `blocked_keywords_unless_local`, where a place or the outlet name overrides.
- **Comment feeds are not article feeds.** `integrate_discoveries.is_comment_feed()` is the single predicate, applied at the top of `evaluate_candidates()` and in `_probe_page_for_feeds()`. Never add one by hand.
- **A source whose format the reader rejects is demoted by source type, not blocked** (`source_preferences.json` → `source_types`): ArchDaily is `project_showcase` (−10, 2 a day) because its essays rate well and its showcases don't.
- **A niche-interest outlet is routed, not demoted** (`source_types.niche`: Dezeen, Architizer, PyTorch, Dark Reading, Pitchfork, Stereogum). `reader_category()` ships its stories in the Miscellany feed (3 slots, 2 an outlet) instead of their category's; their category stays for scoring and the podcast pool, which reads `_niche` for its weekly closer. Miscellany is `source_routed`: never in the model's category guide, never filed by keyword.
- Some sites reject the default User-Agent: both `fetch_images.py` and feed fetching send custom UA headers.

## Feed health agent (`integrate_discoveries.py --heal`)

Evidence makes a candidate; a **fresh live probe** decides. Nothing is deleted: retirement flips `type="retired"` and `recheck_retired()` restores. If none of 3 healthy control feeds answers, the fault is local and the pass changes nothing. `--heal-max-feeds` caps the blast radius. A probe pass does not clear a feed the nightly has failed for 14+ days (`HEAL_PROBE_OVERRIDE_DAYS`); it is retired `nightlyBlocked` and restored by a 28-day cool-off, not by the probe. `retiredBy="hand"` is never restored. A Google News stand-in needs an article from the last 30 days. Without `--dry-run` it rewrites `feeds.opml`.

## Discovery (`feed_discovery.py`)

Curated OPML lists, Kagi News's `kite_feeds.json` (new hosts only) and Brave search (`BRAVE_SEARCH_TOPICS`, 23 queries a week, counted in `api_usage`). It spends on Brave and Haiku: don't run it locally to test a change; stub `requests.get` instead. Every candidate page and feed is fetched through `sanitize.get_public` (`_fetch_feed`, kept until the candidate is sampled), never `feedparser.parse(url)`.
