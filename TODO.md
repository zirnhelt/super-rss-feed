# Feed Issues & Review

_The AUTO section below is regenerated on every run.
Add your own notes in the **Notes & Review** section — it is never overwritten._

<!-- AUTO:START -->
## Feed Errors — Last 7 Days

| Date | Slot | Issue | Detail |
|------|------|-------|--------|
| 2026-03-23 | 🌅 4:30 AM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-23 | 🌙 8:30 PM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-22 | 🌅 4:30 AM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-22 | 🌅 4:30 AM Pacific | ⚠️ **The Narwhal** failed | `415 Client Error: Unsupported Media Type for url: https://thenarwhal.ca/feed/` |
| 2026-03-22 | 🌅 4:30 AM Pacific | ⚠️ **Ricochet** failed | `415 Client Error: Unsupported Media Type for url: https://ricochet.media/feed/` |
| 2026-03-22 | 🌅 4:30 AM Pacific | ⚠️ **IndigiNews** failed | `415 Client Error: Unsupported Media Type for url: https://indiginews.com/feed/` |
| 2026-03-22 | 🌅 4:30 AM Pacific | ⚠️ **BC Gov News** failed | `HTTPSConnectionPool(host='news.gov.bc.ca', port=443): Read timed out. (read timeout=10)` |
| 2026-03-22 | 🌙 8:30 PM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-21 | 🌅 4:30 AM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-21 | 🌙 8:30 PM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-20 | 🌅 4:30 AM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-20 | 🌙 8:30 PM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-19 | 🌅 4:30 AM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-19 | 🌙 8:30 PM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-18 | 🌅 4:30 AM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-18 | 🌙 8:30 PM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-17 | 🌅 4:30 AM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-17 | 🌙 8:30 PM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |

## Content Mix — Last 7 Days

| Date | Slot | Quality | Mix (top 3) |
|------|------|---------|-------------|
| 2026-03-23 | 🌅 morning | 231 | news:65(31%), ai-tech:61(29%), homelab:50(24%) |
| 2026-03-23 | 🌙 evening | 348 | ai-tech:123(37%), news:100(30%), homelab:58(18%) |
| 2026-03-22 | 🌅 morning | 111 | ai-tech:39(40%), homelab:29(30%), news:25(26%) |
| 2026-03-22 | 🌙 evening | 189 | news:62(36%), ai-tech:50(29%), homelab:32(19%) |
| 2026-03-21 | 🌅 morning | 136 | news:40(34%), homelab:35(30%), ai-tech:30(26%) |
| 2026-03-21 | 🌙 evening | 159 | news:50(35%), ai-tech:35(25%), homelab:32(23%) |
| 2026-03-20 | 🌅 morning | 220 | ai-tech:67(34%), news:58(29%), homelab:51(26%) |
| 2026-03-20 | 🌙 evening | 352 | news:117(36%), ai-tech:114(35%), homelab:48(15%) |
| 2026-03-19 | 🌅 morning | 234 | news:71(33%), ai-tech:64(30%), homelab:40(19%) |
| 2026-03-19 | 🌙 evening | 383 | ai-tech:152(43%), news:94(27%), homelab:56(16%) |
| 2026-03-18 | 🌅 morning | 262 | ai-tech:83(35%), news:68(29%), homelab:53(22%) |
| 2026-03-18 | 🌙 evening | 390 | news:142(38%), ai-tech:114(31%), homelab:66(18%) |
| 2026-03-17 | 🌅 morning | 272 | news:85(35%), ai-tech:83(35%), homelab:46(19%) |
| 2026-03-17 | 🌙 evening | 369 | ai-tech:115(34%), news:114(34%), homelab:56(17%) |

_Last updated by log\_feed\_results.py · 2026-03-24 13:57 UTC_

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
