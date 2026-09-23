# Article Review Audit

_Generated: 2026-07-19 14:31 UTC — ratings window 2026-06-17 → 2026-07-19_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 667 |
| Rated **bad** (fluff/noise that reached you) | 431 (64.6%) |
| Rated **good** | 222 (33.3%) |
| Rated **interesting** | 14 |
| Theme-day corrections (`better_theme`) | 181 (27.4% of day-routed ratings) |
| …caused by selection ignoring its own theme scores | 57 |
| …caused by the theme scorer itself missing | 124 |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 222 | 52.9 | 49.0 | 47.6 | 47.6 |
| interesting | 14 | 40.4 | 48.0 | 48.9 | 42.4 |
| bad | 431 | 38.8 | 37 | 38.6 | 36.0 |

### Precision by score band

| Score band | n | good | bad | % good | % bad |
|---|---|---|---|---|---|
| 80-100 | 53 | 30 | 23 | 56.6 | 43.4 |
| 60-79 | 127 | 54 | 73 | 42.5 | 57.5 |
| 40-59 | 210 | 84 | 115 | 40.0 | 54.8 |
| 20-39 | 117 | 38 | 79 | 32.5 | 67.5 |
| 0-19 | 160 | 16 | 141 | 10.0 | 88.1 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **18** (manually lowered 20 → 13 on 2026-06-24).

| Floor | Bad cut | % of bad | Good lost | % of good |
|---|---|---|---|---|
| 13 | 68 | 15.8 | 7 | 3.2 |
| 15 | 123 | 28.5 | 13 | 5.9 |
| 20 | 141 | 32.7 | 16 | 7.2 |
| 25 | 146 | 33.9 | 18 | 8.1 |
| 30 | 198 | 45.9 | 40 | 18.0 |
| 35 | 209 | 48.5 | 45 | 20.3 |
| 40 | 220 | 51.0 | 54 | 24.3 |
| 45 | 246 | 57.1 | 69 | 31.1 |
| 50 | 297 | 68.9 | 124 | 55.9 |
| 60 | 335 | 77.7 | 138 | 62.2 |

### By category

| Category | n | good | interesting | bad | % bad |
|---|---|---|---|---|---|
| news | 531 | 151 | 11 | 369 | 69.5 |
| ai-tech | 38 | 16 | 2 | 20 | 52.6 |
| local | 32 | 25 | 0 | 7 | 21.9 |
| wellness | 31 | 12 | 0 | 19 | 61.3 |
| climate | 11 | 6 | 0 | 5 | 45.5 |
| science | 8 | 8 | 0 | 0 | 0.0 |
| scifi | 5 | 0 | 0 | 5 | 100.0 |
| homelab | 4 | 0 | 1 | 3 | 75.0 |
| shared | 4 | 4 | 0 | 0 | 0.0 |
| podcast-sunday | 2 | 0 | 0 | 2 | 100.0 |
| podcast-friday | 1 | 0 | 0 | 1 | 100.0 |

### Sources (≥ 5 ratings)

**Highest good-rate**

| Source | n | good | bad | % good |
|---|---|---|---|---|
| Eagle Feather News | 5 | 5 | 0 | 100.0 |
| Williams Lake Tribune | 16 | 13 | 3 | 81.2 |
| The Narwhal | 5 | 4 | 1 | 80.0 |
| BC Gov News | 9 | 7 | 2 | 77.8 |
| New Atlas | 12 | 9 | 3 | 75.0 |
| APTN News | 7 | 5 | 2 | 71.4 |
| My Cariboo Now | 12 | 8 | 4 | 66.7 |
| MakeUseOf | 5 | 3 | 2 | 60.0 |
| Nautilus | 7 | 4 | 3 | 57.1 |
| The Northern Miner | 10 | 5 | 5 | 50.0 |

**Highest bad-rate**

| Source | n | good | bad | % bad |
|---|---|---|---|---|
| My East Kootenay Now | 7 | 0 | 7 | 100.0 |
| Lifehacker | 16 | 1 | 15 | 93.8 |
| Toms Guide | 23 | 2 | 21 | 91.3 |
| Neowin | 10 | 1 | 9 | 90.0 |
| Reactor Magazine | 9 | 1 | 8 | 88.9 |
| Al Jazeera English | 25 | 3 | 22 | 88.0 |
| Atlas Obscura | 7 | 1 | 6 | 85.7 |
| CBC Arts | 12 | 2 | 10 | 83.3 |
| NPR Health News | 6 | 1 | 5 | 83.3 |
| Business Insider | 27 | 5 | 22 | 81.5 |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 193 | 9 | 369 |
| breaking | 11 | 2 | 30 |
| analysis | 10 | 3 | 5 |
| feature | 6 | 0 | 11 |
| opinion | 0 | 0 | 9 |
| news | 1 | 0 | 4 |
| wire | 0 | 0 | 2 |
| recap | 1 | 0 | 0 |
| fluff | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 61 | 8 | 52 |
| low | 12 | 0 | 35 |
| high | 28 | 0 | 16 |
| mid | 85 | 0 | 102 |
| unknown | 4 | 0 | 3 |
| unfiltered | 32 | 6 | 223 |

### Filler trend (from corpus alignment reports)

| Report date | Articles analysed | Filler | Filler % |
|---|---|---|---|
| 2026-06-13 | 1229 | 359 | 29 |
| 2026-06-15 | 1249 | 356 | 29 |
| 2026-06-21 | 441 | 60 | 14 |
| 2026-06-22 | 441 | 60 | 14 |
| 2026-06-28 | 490 | 46 | 9 |
| 2026-07-05 | 1303 | 64 | 5 |
| 2026-07-19 | 1228 | 36 | 3 |

## 3. Theme-Bucket Routing Accuracy

Of **660** ratings tied to an aired day, you corrected the day on **181** (27.4%). Additionally 57 good articles were approved for other days.

### Per theme day

| Day | Theme | n | good | bad | % good | Corrected away |
|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 69 | 23 | 43 | 33.3 | 22 |
| tuesday | Working Lands & Industry | 77 | 22 | 55 | 28.6 | 19 |
| wednesday | Repair Culture & Practical Tech | 145 | 64 | 79 | 44.1 | 42 |
| thursday | Indigenous Lands & Innovation | 75 | 18 | 56 | 24.0 | 17 |
| friday | Wild Spaces & Outdoor Life | 134 | 40 | 90 | 29.9 | 37 |
| saturday | Cariboo Local Affairs | 89 | 32 | 56 | 36.0 | 29 |
| sunday | Science, Wonder & the Natural World | 71 | 19 | 49 | 26.8 | 15 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 6 | 4 | 1 | 4 | 1 | 6 |
| tuesday | 5 |  | 3 | 2 | 3 | 2 | 4 |
| wednesday | 4 | 6 |  | 2 | 11 | 9 | 10 |
| thursday |  | 3 | 5 |  | 5 |  | 4 |
| friday | 2 | 4 | 9 | 5 |  | 6 | 11 |
| saturday |  | 1 | 7 | 5 | 3 |  | 13 |
| sunday |  | 4 | 5 |  | 3 | 3 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 57 |
| Theme scorer disagreed with you (scoring miss) | 124 |
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
| 2026-W27 | 12 | 972 | 48 |
| 2026-W28 | 6 | 969 | 59 |
| 2026-W29 | 6 | 1077 | 70 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-07-07T07:48:19.436969+00:00 | 886 | 563 | 56 | 194 | 55 |
| 2026-07-08T06:34:04.031946+00:00 | 1062 | 673 | 56 | 237 | 60 |
| 2026-07-08T23:15:33.099996+00:00 | 1024 | 683 | 71 | 220 | 55 |
| 2026-07-09T07:49:21.144314+00:00 | 1165 | 627 | 43 | 209 | 52 |
| 2026-07-10T07:42:43.434127+00:00 | 1193 | 681 | 75 | 195 | 52 |
| 2026-07-11T06:20:12.119039+00:00 | 1171 | 628 | 65 | 190 | 36 |
| 2026-07-12T06:40:10.545685+00:00 | 941 | 479 | 57 | 132 | 39 |
| 2026-07-13T07:28:29.183589+00:00 | 800 | 375 | 55 | 43 | 17 |
| 2026-07-14T06:17:35.491468+00:00 | 1032 | 560 | 73 | 85 | 18 |
| 2026-07-15T06:21:17.984425+00:00 | 1168 | 646 | 79 | 106 | 27 |
| 2026-07-16T06:25:01.108796+00:00 | 1231 | 692 | 76 | 131 | 38 |
| 2026-07-17T06:22:32.363219+00:00 | 1191 | 689 | 80 | 116 | 47 |
| 2026-07-18T06:10:19.075806+00:00 | 1126 | 643 | 71 | 106 | 28 |
| 2026-07-19T06:35:54.116378+00:00 | 946 | 551 | 62 | 81 | 22 |

### Current category feed sizes

| Feed | Items |
|---|---|
| news | 123 |
| ai-tech | 65 |
| wellness | 47 |
| local | 40 |
| science | 38 |
| climate | 35 |
| homelab | 12 |
| scifi | 6 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 10 / 8 |
| Calibration stats runs available | 14 |
| Calibration stats range | 2026-07-07 → 2026-07-19 |
| theme_holdover_cache.json present | False |

**Context:** `calibration_stats_cache.json` was first committed on 2026-07-07, so every weekly calibration run before that found no stats and skipped — the log's repeated "Claude call or response parsing failed" lines were misleading boilerplate, not API failures. The agent's Claude path has effectively never run.

