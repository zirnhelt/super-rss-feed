# Weekly Feed Maintenance Guide

This document covers how to monitor, tune, and expand the podcast-themed feeds
introduced in March 2026. It is aimed at the weekly review cycle: scan for
broken sources, check theme coverage, and improve keyword lists over time.

---

## What the new feeds add

Each `feed-podcast-{day}.json` now emits three extra fields per article:

| Field | Type | What it means |
|---|---|---|
| `_keyword_matches` | int | How many of the day's theme keywords appear in title + summary |
| `_boosted_score` | int (0–100) | `min(100, hits × 20 + quality × 0.3)` — used by the podcast generator to pick deep-dive articles |
| `_is_bonus` | bool | `true` when zero theme keywords matched (and, on Saturday, the source is not a Cariboo local outlet) |

The `_podcast.theme_description` envelope field now holds a 2–3 sentence
editorial angle per day (not just the short one-liner).

These fields are computed at feed-generation time from the `keywords` array
in `config/podcast_schedule.json`. **That file is the main thing to tune.**

---

## Weekly review checklist

### 1. Check for broken sources (5 min)

Open `TODO.md` — the AUTO section is regenerated on every run and shows
feed errors from the last 7 days. Look for:

- **403 Forbidden** — the site is blocking the GitHub Actions user-agent.
  Comment the source out in `feeds.opml` and add a note.
  Example: My Cariboo Now has been 403-ing since at least March 2026.

- **415 Unsupported Media Type** — feedparser is sending a content-type the
  server rejects. Try opening the feed URL in a browser; if it works, add a
  `User-Agent` override or replace with a Google News search feed for that
  outlet.

- **Timeout / RemoteDisconnected** — usually transient. If it persists for
  3+ consecutive days, comment it out and open a TODO.

**For sources added in the March 2026 batch**, pay particular attention to:

| Source | Theme | Known risk |
|---|---|---|
| My East Kootenay Now | Saturday | Same network as My Cariboo Now — watch for 403 |
| APTN News | Thursday | No known issues yet |
| Spacing Magazine | Monday | No known issues yet |
| CBC Arts | Monday | CBC RSS URLs change occasionally |
| GN BC Wildfire and Conservation | Friday | Google News feeds — monitor for relevant volume |
| GN BC Working Lands | Tuesday | Google News feeds — monitor for relevant volume |
| GN Rural BC Infrastructure | Sunday | Google News feeds — monitor for relevant volume |

If a new source fails immediately, consider whether the `mycariboonow.com/feed`
pattern can be replaced with a Google News search feed targeting the same outlet:

```xml
<!-- fallback example for My East Kootenay Now if it 403s -->
<outline type="rss" text="GN East Kootenay Now"
  xmlUrl="https://news.google.com/rss/search?q=site:myeastkootenaynow.com&hl=en&gl=CA&ceid=CA:en"
  htmlUrl="https://news.google.com" />
```

---

### 2. Check new-source contribution (10 min)

Open the current day's `feed-podcast-{day}.json` and look at `_keyword_matches`
across articles. A healthy feed has:

- At least a few articles with `_keyword_matches ≥ 2` near the top
- `_is_bonus: false` on most theme articles
- Local Cariboo sources present in Saturday's feed with `_is_bonus: false`
  even when `_keyword_matches` is 0 (the Saturday exemption)

If the new Google News feeds are producing content but it is all landing in
`_is_bonus: true`, the keywords for that day probably need broadening — see
the tuning section below.

If a new source produces **zero articles** after 3 days, check:
1. The feed URL in `feeds.opml` is reachable
2. The source is not in `config/filters.json` blocklist
3. Articles from the source score ≥ 15 (the `min_claude_score` floor in
   `config/limits.json`)

---

### 3. Tune keywords (when `_boosted_score` is consistently low)

Keywords live in `config/podcast_schedule.json` under each day's `keywords`
array. They are matched case-insensitively against `title + summary`.

**When to add keywords:**
- You notice articles about a relevant topic are landing with
  `_keyword_matches: 0` and `_is_bonus: true`
- A new source covers a topic not yet in the list (e.g. APTN News mentions
  "guardian program" and "UNDRIP" often but Thursday only matches on
  "indigenous" and "first nations")

**When to remove keywords:**
- A keyword is pulling in off-topic articles as theme matches (check
  `_keyword_matches > 0` articles that are clearly wrong)
- A keyword is too generic (e.g. "community" on Wednesday pulls in anything)

**Format** — keywords are plain strings, matched as substrings:
```json
"keywords": [
  "forestry", "ranching", "AgTech", "precision agriculture"
]
```

Multi-word phrases work: `"precision agriculture"` only matches that exact
phrase. Prefer specific multi-word terms for precision; short words
(e.g. `"farm"`) for recall.

**The `_boosted_score` formula:**
```
_boosted_score = min(100, keyword_hits × 20 + ai_quality_score × 0.3)
```

An article with 2 keyword hits and ai_score 70 gets `min(100, 40 + 21) = 61`.
Three hits pushes any article to 60+ regardless of quality score. This means
**keyword tuning has more impact than source quality tuning** for theme
alignment.

---

### 4. Update `theme_description` when editorial framing shifts (as needed)

The `_podcast.theme_description` field in each feed is the text passed to
podcast hosts as framing context. It lives under `theme_description` in
`config/podcast_schedule.json`.

Update it when:
- A theme's editorial angle shifts seasonally (e.g. Friday shifts from
  wildfire prep in summer to avalanche/winter access in winter)
- A major local story changes what "Cariboo Voices" means for several weeks
- The podcast generator's prompts change and need new framing alignment

Keep it 2–3 sentences. It is read by Claude when generating the episode, so
clarity and specificity about the Cariboo context matter more than elegance.

---

### 5. Add new sources

**To add a direct RSS source:**

1. Confirm the feed URL works: `curl -I <url>` or open in browser
2. Add to `feeds.opml` with a comment explaining the theme it supports:
   ```xml
   <!-- Haida Gwaii Observer: coastal BC community news — supports Friday/Saturday -->
   <outline type="rss" text="Haida Gwaii Observer"
     xmlUrl="https://www.haidagwaiiobserver.com/feed/"
     htmlUrl="https://www.haidagwaiiobserver.com" />
   ```
3. Add to `config/source_preferences.json` under `source_map` if it is a
   print/broadcast/preferred-local source:
   ```json
   "Haida Gwaii Observer": "print"
   ```
4. Run locally or let the next CI run pick it up. Check `TODO.md` the next day.

**To add a Google News fallback feed** (when no direct RSS exists):

```xml
<outline type="rss" text="GN BC Arts Council"
  xmlUrl="https://news.google.com/rss/search?q=%22BC+Arts+Council%22+OR+%22BC+arts+funding%22&hl=en&gl=CA&ceid=CA:en"
  htmlUrl="https://news.google.com" />
```

Google News feeds do not need a `source_preferences.json` entry — they surface
as individual outlet bylines after feedparser resolves the redirect.

**Sources still missing from the CLAUDE.md priority list** (as of March 2026):

| Source | Theme | Status |
|---|---|---|
| First Nations Technology Council | Thursday | No public RSS found; add GN fallback |
| BC Arts Council news | Monday | No RSS; add GN fallback |
| BC Cattlemen's Association | Tuesday | Covered by GN BC Working Lands feed |
| BC Lumber Trade Council / COFI | Tuesday | Covered by GN BC Working Lands feed |
| BC Wildfire Service direct | Friday | No RSS; covered by GN BC Wildfire feed |
| BC Parks news | Friday | No RSS; covered by GN BC Wildfire feed |
| Haida Gwaii Observer | Friday | Check for RSS; direct feed preferred |
| Rural Municipalities of BC / UBCM | Sunday | Covered by GN Rural BC Infrastructure |
| Connecting BC broadband updates | Sunday | Check for RSS |

---

## Source health at a glance

The `_keyword_matches` distribution in a day's feed is a quick health signal:

| Pattern | Diagnosis |
|---|---|
| Most articles have `_keyword_matches: 0`, high `_is_bonus` count | Keywords too narrow — broaden the list |
| `_boosted_score` is high but podcast quality is poor | Keywords too broad — remove generic terms |
| Saturday has local sources with `_is_bonus: true` | Bug: check `LOCAL_BC_SOURCES` set in `generate_podcast_feed()` |
| A theme day has < 10 total articles | Source volume is low — add more sources or a GN search feed |
| New source never appears in any feed | Check 403/415 errors in `TODO.md`; verify score ≥ 15 |

---

## Files touched by this maintenance cycle

| File | What to change |
|---|---|
| `config/podcast_schedule.json` | `keywords`, `theme_description` per day |
| `feeds.opml` | Add/comment-out RSS sources |
| `config/source_preferences.json` | Classify new print/broadcast/local sources |
| `TODO.md` (Notes section) | Record disabled sources and why |
