# Article Review Audit

_Generated: 2026-07-11 22:52 UTC — ratings window 2026-06-17 → 2026-07-11_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 556 |
| Rated **bad** (fluff/noise that reached you) | 352 (63.3%) |
| Rated **good** | 194 (34.9%) |
| Rated **interesting** | 10 |
| Theme-day corrections (`better_theme`) | 159 (28.8% of day-routed ratings) |
| …caused by selection ignoring its own theme scores | 45 |
| …caused by the theme scorer itself missing | 114 |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 194 | 54.3 | 49.0 | 48.7 | 48.3 |
| interesting | 10 | 37.2 | 47.5 | 40.1 | 37.6 |
| bad | 352 | 41.8 | 44.0 | 40.6 | 39.5 |

### Precision by score band

| Score band | n | good | bad | % good | % bad |
|---|---|---|---|---|---|
| 80-100 | 50 | 28 | 22 | 56.0 | 44.0 |
| 60-79 | 125 | 53 | 72 | 42.4 | 57.6 |
| 40-59 | 174 | 66 | 101 | 37.9 | 58.0 |
| 20-39 | 94 | 36 | 58 | 38.3 | 61.7 |
| 0-19 | 113 | 11 | 99 | 9.7 | 87.6 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **13** (manually lowered 20 → 13 on 2026-06-24).

| Floor | Bad cut | % of bad | Good lost | % of good |
|---|---|---|---|---|
| 13 | 66 | 18.8 | 7 | 3.6 |
| 15 | 89 | 25.3 | 8 | 4.1 |
| 20 | 99 | 28.1 | 11 | 5.7 |
| 25 | 104 | 29.5 | 13 | 6.7 |
| 30 | 141 | 40.1 | 33 | 17.0 |
| 35 | 149 | 42.3 | 38 | 19.6 |
| 40 | 157 | 44.6 | 47 | 24.2 |
| 45 | 180 | 51.1 | 60 | 30.9 |
| 50 | 220 | 62.5 | 100 | 51.5 |
| 60 | 258 | 73.3 | 113 | 58.2 |

### By category

| Category | n | good | interesting | bad | % bad |
|---|---|---|---|---|---|
| news | 459 | 139 | 9 | 311 | 67.8 |
| local | 29 | 24 | 0 | 5 | 17.2 |
| ai-tech | 26 | 12 | 1 | 13 | 50.0 |
| wellness | 25 | 10 | 0 | 15 | 60.0 |
| climate | 5 | 5 | 0 | 0 | 0.0 |
| scifi | 4 | 0 | 0 | 4 | 100.0 |
| science | 4 | 4 | 0 | 0 | 0.0 |
| podcast-sunday | 2 | 0 | 0 | 2 | 100.0 |
| podcast-friday | 1 | 0 | 0 | 1 | 100.0 |
| homelab | 1 | 0 | 0 | 1 | 100.0 |

### Sources (≥ 5 ratings)

**Highest good-rate**

| Source | n | good | bad | % good |
|---|---|---|---|---|
| Williams Lake Tribune | 16 | 13 | 3 | 81.2 |
| The Narwhal | 5 | 4 | 1 | 80.0 |
| Nautilus | 5 | 4 | 1 | 80.0 |
| BC Gov News | 9 | 7 | 2 | 77.8 |
| New Atlas | 12 | 9 | 3 | 75.0 |
| My Cariboo Now | 11 | 8 | 3 | 72.7 |
| APTN News | 6 | 4 | 2 | 66.7 |
| MakeUseOf | 5 | 3 | 2 | 60.0 |
| TechRadar | 17 | 9 | 8 | 52.9 |
| The Northern Miner | 8 | 4 | 4 | 50.0 |

**Highest bad-rate**

| Source | n | good | bad | % bad |
|---|---|---|---|---|
| My East Kootenay Now | 7 | 0 | 7 | 100.0 |
| Al Jazeera English | 20 | 1 | 19 | 95.0 |
| Lifehacker | 16 | 1 | 15 | 93.8 |
| Toms Guide | 18 | 2 | 16 | 88.9 |
| CBC Arts | 9 | 1 | 8 | 88.9 |
| Neowin | 9 | 1 | 8 | 88.9 |
| Reactor Magazine | 8 | 1 | 7 | 87.5 |
| Atlas Obscura | 6 | 1 | 5 | 83.3 |
| NPR Health News | 6 | 1 | 5 | 83.3 |
| Tom's Hardware | 11 | 2 | 9 | 81.8 |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 183 | 9 | 335 |
| breaking | 4 | 1 | 8 |
| analysis | 4 | 0 | 1 |
| feature | 2 | 0 | 1 |
| news | 0 | 0 | 3 |
| opinion | 0 | 0 | 2 |
| recap | 1 | 0 | 0 |
| fluff | 0 | 0 | 1 |
| wire | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 46 | 4 | 40 |
| low | 10 | 0 | 25 |
| high | 28 | 0 | 16 |
| mid | 85 | 0 | 102 |
| unknown | 0 | 0 | 3 |
| unfiltered | 25 | 6 | 166 |

### Filler trend (from corpus alignment reports)

| Report date | Articles analysed | Filler | Filler % |
|---|---|---|---|
| 2026-06-13 | 1229 | 359 | 29 |
| 2026-06-15 | 1249 | 356 | 29 |
| 2026-06-21 | 441 | 60 | 14 |
| 2026-06-22 | 441 | 60 | 14 |
| 2026-06-28 | 490 | 46 | 9 |
| 2026-07-05 | 1303 | 64 | 5 |

## 3. Theme-Bucket Routing Accuracy

Of **553** ratings tied to an aired day, you corrected the day on **159** (28.8%). Additionally 34 good articles were approved for other days.

### Per theme day

| Day | Theme | n | good | bad | % good | Corrected away |
|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 46 | 15 | 29 | 32.6 | 15 |
| tuesday | Working Lands & Industry | 63 | 19 | 44 | 30.2 | 16 |
| wednesday | Repair Culture & Practical Tech | 129 | 61 | 67 | 47.3 | 40 |
| thursday | Indigenous Lands & Innovation | 62 | 17 | 44 | 27.4 | 16 |
| friday | Wild Spaces & Outdoor Life | 118 | 36 | 79 | 30.5 | 33 |
| saturday | Cariboo Local Affairs | 64 | 27 | 37 | 42.2 | 24 |
| sunday | Science, Wonder & the Natural World | 71 | 19 | 49 | 26.8 | 15 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 4 | 3 | 1 | 2 | 1 | 4 |
| tuesday | 5 |  | 2 | 2 | 1 | 2 | 4 |
| wednesday | 4 | 5 |  | 2 | 11 | 9 | 9 |
| thursday |  | 2 | 5 |  | 5 |  | 4 |
| friday | 1 | 3 | 9 | 5 |  | 5 | 10 |
| saturday |  | 1 | 6 | 4 | 1 |  | 12 |
| sunday |  | 4 | 5 |  | 3 | 3 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 45 |
| Theme scorer disagreed with you (scoring miss) | 114 |
| Theme scores missing on the rating | 0 |

## 4. Volume Trend — Is the Feed Lighter?

_Average per-run articles fetched and passing the quality gate, by ISO week (from FEED_LOG.md). The quality floor was manually dropped 20 → 13 in week 2026-W26._

| Week | Runs | Avg fetched/run | Avg quality/run |
|---|---|---|---|
| 2026-W09 | 19 | 810 | 162 |
| 2026-W10 | 22 | 875 | 188 |
| 2026-W11 | 21 | 899 | 195 |
| 2026-W12 | 15 | 869 | 249 |
| 2026-W13 | 14 | 911 | 243 |
| 2026-W14 | 14 | 875 | 165 |
| 2026-W15 | 14 | 913 | 143 |
| 2026-W16 | 14 | 903 | 168 |
| 2026-W17 | 14 | 895 | 178 |
| 2026-W18 | 11 | 924 | 166 |
| 2026-W19 | 11 | 973 | 194 |
| 2026-W20 | 12 | 1012 | 179 |
| 2026-W21 | 11 | 958 | 175 |
| 2026-W22 | 15 | 973 | 91 |
| 2026-W23 | 10 | 892 | 72 |
| 2026-W24 | 28 | 854 | 34 |
| 2026-W25 | 33 | 1385 | 24 |
| 2026-W26 | 8 | 1138 | 42 |
| 2026-W27 | 12 | 973 | 48 |
| 2026-W28 | 5 | 974 | 60 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-07-07T07:48:19.436969+00:00 | 886 | 563 | 56 | 194 | 55 |
| 2026-07-08T06:34:04.031946+00:00 | 1062 | 673 | 56 | 237 | 60 |
| 2026-07-08T23:15:33.099996+00:00 | 1024 | 683 | 71 | 220 | 55 |
| 2026-07-09T07:49:21.144314+00:00 | 1165 | 627 | 43 | 209 | 52 |
| 2026-07-10T07:42:43.434127+00:00 | 1193 | 681 | 75 | 195 | 52 |
| 2026-07-11T06:20:12.119039+00:00 | 1171 | 628 | 65 | 190 | 36 |

### Current category feed sizes

| Feed | Items |
|---|---|
| news | 500 |
| ai-tech | 190 |
| homelab | 127 |
| wellness | 83 |
| science | 62 |
| climate | 58 |
| local | 44 |
| scifi | 9 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 8 / 8 |
| Calibration stats runs available | 6 |
| Calibration stats range | 2026-07-07 → 2026-07-11 |
| theme_holdover_cache.json present | False |

**Context:** `calibration_stats_cache.json` was first committed on 2026-07-07, so every weekly calibration run before that found no stats and skipped — the log's repeated "Claude call or response parsing failed" lines were misleading boilerplate, not API failures. The agent's Claude path has effectively never run.

