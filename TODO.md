# Feed Issues & Review

_The AUTO section below is regenerated on every run.
Add your own notes in the **Notes & Review** section — it is never overwritten._

<!-- AUTO:START -->
## Feed Errors — Last 7 Days

_No errors recorded yet — will populate after the first logged run._

## Content Mix — Last 7 Days

_No data yet — will populate after the first logged run._

_Last updated by log\_feed\_results.py · seeded 2026-02-24_

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
