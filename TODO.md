# Feed Issues & Review

_The AUTO section below is regenerated on every run.
Add your own notes in the **Notes & Review** section — it is never overwritten._

<!-- AUTO:START -->
## Feed Errors — Last 7 Days

| Date | Slot | Issue | Detail |
|------|------|-------|--------|
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **AP News** failed | `404 Client Error: Not Found for url: https://apnews.com/rss` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **Gizmodo** failed | `404 Client Error: Not Found for url: https://gizmodo.com/vip.xml` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **Instructables Blog** failed | `404 Client Error: Not Found for url: https://www.instructables.com/tag/instructables%20blog/rss.xml` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **Noahpinion** failed | `403 Client Error: Forbidden for url: https://noahpinion.substack.com/feed` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **Reuters Top News** failed | `HTTPConnectionPool(host='feeds.reuters.com', port=80): Max retries exceeded with url: /reuters/topNews (Caused by NameRe` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **The Globe and Mail** failed | `404 Client Error: Not Found for url: https://www.theglobeandmail.com/arc/outboundfeeds/rss/` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **Scientific American** failed | `404 Client Error: Not Found for url: https://www.scientificamerican.com/feed/` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **Stratechery** failed | `('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **Techdirt** failed | `520 Server Error: <none> for url: http://www.techdirt.com/techdirt_rss.xml` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **The Marginalian** failed | `HTTPSConnectionPool(host='www.themarginalian.org', port=443): Read timed out. (read timeout=10)` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **Williams Lake Tribune** failed | `404 Client Error: Not Found for url: https://zirnhelt.github.io/wlt-rss-feed/wlt_news.xml` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **CTV News** failed | `404 Client Error: Not Found for url: https://www.ctvnews.ca/rss/ctvnews-ca-top-stories-public-rss-1.822009` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **MacRumors** failed | `404 Client Error: Not Found for url: https://www.macrumors.com/feed/` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **Castanet Kelowna** failed | `HTTPSConnectionPool(host='www.castanet.net', port=443): Read timed out. (read timeout=10)` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **The Tyee** failed | `HTTPSConnectionPool(host='thetyee.ca', port=443): Read timed out. (read timeout=10)` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **All3DP** failed | `403 Client Error: Forbidden for url: https://all3dp.com/feed/` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **The Breach** failed | `HTTPSConnectionPool(host='breachmedia.ca', port=443): Read timed out. (read timeout=10)` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **Ricochet** failed | `404 Client Error: Not Found for url: https://ricochet.media/en/feed` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **All About Bambu** failed | `HTTPSConnectionPool(host='www.allaboutbambu.com', port=443): Max retries exceeded with url: /feed/ (Caused by NameResolu` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **Yale Climate Connections** failed | `('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **Treehugger** failed | `402 Client Error: Payment Required for url: https://www.treehugger.com/rss` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **Longreads** failed | `('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))` |
| 2026-02-24 | 🌅 6 AM Pacific | ⚠️ **Modern Farmer** failed | `HTTPSConnectionPool(host='modernfarmer.com', port=443): Read timed out. (read timeout=10)` |

## Content Mix — Last 7 Days

| Date | Slot | Quality | Mix (top 3) |
|------|------|---------|-------------|
| 2026-02-24 | 🌅 morning | 321 | news:321(100%) |

_Last updated by log\_feed\_results.py · 2026-02-24 15:34 UTC_

<!-- AUTO:END -->



## Notes & Review

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
