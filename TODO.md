# Feed Issues & Review

_The AUTO section below is regenerated on every run.
Add your own notes in the **Notes & Review** section — it is never overwritten._

<!-- AUTO:START -->
## Feed Errors — Last 7 Days

| Date | Slot | Issue | Detail |
|------|------|-------|--------|
| 2026-08-14 | 🌙 8:30 PM Pacific | ⚠️ **Mother Earth News** failed | `500 Server Error: Internal Server Error for url: https://www.motherearthnews.com/feed/` |
| 2026-08-14 | 🌙 8:30 PM Pacific | ⚠️ **Old House Journal** failed | `HTTPSConnectionPool(host='www.oldhouseonline.com', port=443): Max retries exceeded with url: /feed/ (Caused by NameResol` |
| 2026-08-13 | 🌙 8:30 PM Pacific | ⚠️ **Kagi Small Web** failed | `503 Server Error: Service Unavailable for url: https://kagi.com/api/v1/smallweb/feed` |
| 2026-08-13 | 🌙 8:30 PM Pacific | ⚠️ **Mother Earth News** failed | `500 Server Error: Internal Server Error for url: https://www.motherearthnews.com/feed/` |
| 2026-08-13 | 🌙 8:30 PM Pacific | ⚠️ **Old House Journal** failed | `HTTPSConnectionPool(host='www.oldhouseonline.com', port=443): Max retries exceeded with url: /feed/ (Caused by NameResol` |
| 2026-08-12 | 🌙 8:30 PM Pacific | ⚠️ **Mother Earth News** failed | `500 Server Error: Internal Server Error for url: https://www.motherearthnews.com/feed/` |
| 2026-08-12 | 🌙 8:30 PM Pacific | ⚠️ **Old House Journal** failed | `HTTPSConnectionPool(host='www.oldhouseonline.com', port=443): Max retries exceeded with url: /feed/ (Caused by NameResol` |
| 2026-08-11 | 🌙 8:30 PM Pacific | ⚠️ **Mother Earth News** failed | `500 Server Error: Internal Server Error for url: https://www.motherearthnews.com/feed/` |
| 2026-08-11 | 🌙 8:30 PM Pacific | ⚠️ **Old House Journal** failed | `HTTPSConnectionPool(host='www.oldhouseonline.com', port=443): Max retries exceeded with url: /feed/ (Caused by NameResol` |

_Full error history: [FEED_ERRORS.md](FEED_ERRORS.md)._

## Content Mix — Last 7 Days

| Date | Slot | Quality | Mix (top 3) |
|------|------|---------|-------------|
| 2026-08-17 | 🌙 evening | 95 | news:25(26%), ai-tech:18(19%), wellness:10(11%) |
| 2026-08-16 | 🌙 evening | 92 | news:25(27%), ai-tech:15(16%), homelab:10(11%) |
| 2026-08-15 | 🌙 evening | 87 | news:25(29%), ai-tech:17(20%), climate:10(11%) |
| 2026-08-14 | 🌙 evening | 94 | news:25(27%), ai-tech:18(19%), climate:12(13%) |
| 2026-08-13 | 🌙 evening | 92 | news:25(27%), ai-tech:18(20%), wellness:10(11%) |
| 2026-08-12 | 🌙 evening | 92 | news:25(27%), ai-tech:18(20%), wellness:10(11%) |
| 2026-08-11 | 🌙 evening | 101 | news:25(25%), ai-tech:18(18%), local:11(11%) |

_Last updated by log\_feed\_results.py · 2026-08-18 04:49 UTC_

<!-- AUTO:END -->



























































































































































































































































































































































































## Notes & Review

### 2026-08-15 — Widened the search-fallback trigger instead of dropping two sources

`Mother Earth News` (homestead, `500` on all 8 runs since 2026-08-03) and
`Old House Journal` (design, DNS `NameResolutionError` on all 7 runs since
2026-08-08) both wanted to be kept — they're not dead, the pipeline just
wasn't trying to save them. `fetch_feed_articles()`'s Brave → Kagi → Google
News fallback chain only fired on `status in (403, 404, 421) or is_timeout`;
a `500` and a `ConnectionError` (which is what a DNS failure raises — it's
not an `HTTPError` at all, so `status` was always `None` for it) both fell
straight through to "failed, return []" with no fallback attempt.

Widened `should_try_fallback` in `super_rss_curator_json.py` to also cover
`status == 500` and `requests.exceptions.ConnectionError`. `503` stays
excluded on purpose — it already gets a `Retry-After` skip_until circuit
breaker, so also hitting paid Brave/Kagi APIs for it would burn quota on a
source we're already backing off from. Left both sources active in
`feeds.opml`; watch `FEED_ERRORS.md` next run — if they're still coming up
`✗` with 0 fallback articles even after this, that's real evidence (not
just an undertested code path) and removal per the usual rules is fair
game.

### 2026-06-14 — Added newsletter sources from Cariboo Signals inbox label

Added three newsletters to `feeds.opml`, sourced from recurring senders in
the "Cariboo Signals" Gmail label:
- **Canadaland** (`https://www.canadaland.com/feed/`) — Canadian media/
  politics/AI commentary.
- **Animikii News River** (`https://newsriver.animikii.com/rss`) — Indigenous
  tech, land stewardship, and data sovereignty newsletter; strong fit for
  Thursday's Indigenous Lands & Innovation theme.
- **OpenMedia** (`https://openmedia.org/feed`) — Canadian digital-rights/
  AI-policy advocacy.

These feed URLs were not curl-verified (no general internet egress from this
session). If any of them show up with 403/415 errors in the Feed Errors
section after the next run, fix or remove per the usual maintenance rules.
Skipped from the same label: The Line (lapsed paid Substack subscription)
and Far & Wide (beehiiv RSS URL isn't guessable — would need the dashboard
URL from the user).

### 2026-06-12 — Feed quality audit: dead-source cleanup and tagging fixes

Removed six sources from `feeds.opml` that have failed on every run for
weeks/months with no recoverable fix (per the 403/415/timeout rules in
`FEEDS_MAINTENANCE.md`):
- **Country Guide** — `403 Forbidden` on every run since at least Feb 2026.
- **CBC Kamloops** / **CBC Prince George** — `rss.cbc.ca` lineup endpoints
  time out / `400 Bad Request` on every run; Local feed is already 🟢 healthy
  (avg 85.1) without them.
- **First Nations Technology Council** — times out on every run; no public
  RSS found, GN fallback feeds 503'd and were already removed in March.
- **Hakai Magazine** and **Machine Learning Blog (ML@CMU)** — both return
  `403/415` even with the existing browser User-Agent + `Accept` headers
  already in `fetch_feed_articles()` (confirmed via curl — Cloudflare WAF
  block, not a header issue). Hakai is a strong topical fit for Sunday's
  Science theme; revisit if a working feed URL/route is found.

Also made config/tagging changes from the 2026-06-12 feed quality audit:
- `config/source_preferences.json` — added a `personal_listicle` source type
  (-10 score, max 4/feed) and mapped `XDA Developers` to it, to curb its 42%
  share of Homelab & DIY.
- `config/limits.json` — added `min_score_by_category.ai-tech: 30` (with
  matching support in `super_rss_curator_json.py`'s quality filter) to raise
  the AI/ML & Tech category's average score above the 33.1 baseline.
- `config/category_rules.json` — tightened `climate` and `science` `include`
  lists from broad single-word terms to multi-word, topic-specific phrases,
  to reduce tangential articles diluting those categories' averages (23.5
  and 23.1).
- `config/filters.json` + `Article.should_filter()` — replaced ~11 literal
  `"I ___"` / `"My ___"` blocklist keyword entries with two
  `blocked_title_patterns` regexes for first-person anecdote listicles.

### 2026-02-24 — Initial observations (from code analysis)

These are seeded from reading the codebase and the Actions run at
https://github.com/zirnhelt/super-rss-feed/actions/runs/22340201860/job/64641609257

**Feed errors / things to watch:**
- [ ] **CFJC Today Kamloops** — broadcast source, known to time out (User-Agent blocking mentioned in ROADMAP)
- [ ] **Williams Lake Tribune scraper** — bespoke HTML scraper; check for 0-article runs which indicate layout changes
- [ ] Any feed returning `✗` in the run log → add to blocked-UA workaround list (see `config/filters.json`)

**Content mix observations:**
- `ai-tech` typically dominates (40–50% of articles) — consider whether `min_claude_score` or per-source caps need tightening
- `local` content is thin on weekdays (~3–5 articles/run) — WLT Tribune posts lightly Mon–Fri
- `news` is the catch-all fallback — high counts there may indicate categorisation misses worth investigating
- Run at 22340201860 completed in 5m 11s (2026-02-24) — baseline for timing regressions

**Known issues from ROADMAP to track against:**
- [ ] Stronger deduplication for near-duplicate articles (e.g. wire service reprints)
- [ ] Improved sports filtering for local content (rec centres, arenas getting through)
- [ ] Categorisation accuracy — watch for ai-tech articles that should be homelab or science
- [ ] Feed blocking workarounds for sites rejecting the default User-Agent

**How this log works:**
- `FEED_LOG.md` — per-run detail (pipeline counts, category mix, errors, feed sizes)
- `TODO.md` (this file) — auto section above is rewritten each run; your notes below are never touched
- After 7 days, FEED_LOG entries compress to a weekly summary row
