# Feed Issues & Review

_The AUTO section below is regenerated on every run.
Add your own notes in the **Notes & Review** section — it is never overwritten._

<!-- AUTO:START -->
## Feed Errors — Last 7 Days

| Date | Slot | Issue | Detail |
|------|------|-------|--------|
| 2026-03-19 | 🌙 8:30 PM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-18 | 🌅 4:30 AM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-18 | 🌙 8:30 PM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-17 | 🌅 4:30 AM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-17 | 🌙 8:30 PM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-16 | 🌅 4:30 AM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-16 |  unknown | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-16 | 🌙 8:30 PM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-15 | 🌅 4:30 AM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-15 |  unknown | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-15 | 🌙 8:30 PM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-14 | 🌅 4:30 AM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-14 |  unknown | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |
| 2026-03-14 | 🌙 8:30 PM Pacific | ⚠️ **My Cariboo Now** failed | `403 Client Error: Forbidden for url: https://www.mycariboonow.com/feed` |

## Content Mix — Last 7 Days

| Date | Slot | Quality | Mix (top 3) |
|------|------|---------|-------------|
| 2026-03-19 | 🌙 evening | 383 | ai-tech:152(43%), news:94(27%), homelab:56(16%) |
| 2026-03-18 | 🌅 morning | 262 | ai-tech:83(35%), news:68(29%), homelab:53(22%) |
| 2026-03-18 | 🌙 evening | 390 | news:142(38%), ai-tech:114(31%), homelab:66(18%) |
| 2026-03-17 | 🌅 morning | 272 | news:85(35%), ai-tech:83(35%), homelab:46(19%) |
| 2026-03-17 | 🌙 evening | 369 | ai-tech:115(34%), news:114(34%), homelab:56(17%) |
| 2026-03-16 | 🌅 morning | 233 | news:72(35%), ai-tech:67(33%), homelab:35(17%) |
| 2026-03-16 |  unknown | 271 | ai-tech:103(42%), news:74(30%), homelab:41(17%) |
| 2026-03-16 | 🌙 evening | 151 | ai-tech:46(35%), news:45(34%), homelab:18(14%) |
| 2026-03-15 | 🌅 morning | 126 | news:41(37%), homelab:33(30%), ai-tech:26(24%) |
| 2026-03-15 |  unknown | 97 | ai-tech:29(33%), homelab:26(29%), news:25(28%) |
| 2026-03-15 | 🌙 evening | 103 | ai-tech:34(37%), news:31(34%), homelab:12(13%) |
| 2026-03-14 | 🌅 morning | 132 | ai-tech:34(29%), homelab:34(29%), news:32(27%) |
| 2026-03-14 |  unknown | 100 | news:29(32%), ai-tech:27(30%), homelab:21(23%) |
| 2026-03-14 | 🌙 evening | 74 | ai-tech:24(36%), news:21(31%), homelab:10(15%) |

_Last updated by log\_feed\_results.py · 2026-03-21 13:25 UTC_

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
