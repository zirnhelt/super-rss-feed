# Article Review Audit

_Generated: 2026-08-09 14:01 UTC — ratings window 2026-06-17 → 2026-08-08_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 928 |
| Rated **bad** (fluff/noise that reached you) | 596 (64.2%) |
| Rated **good** | 277 (29.8%) |
| Rated **interesting** | 54 |
| Theme-day corrections (`better_theme`) | 231 (25.1% of day-routed ratings) |
| …caused by selection ignoring its own theme scores | 85 |
| …caused by the theme scorer itself missing | 146 |
| Category retags | 23 (11.6% of categorized ratings) |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 277 | 50.2 | 48 | 44.6 | 44.3 |
| interesting | 54 | 38.6 | 48.0 | 36.8 | 30.4 |
| bad | 596 | 35.8 | 29.0 | 31.4 | 28.3 |

### Precision by score band

| Score band | n | good | bad | % good | % bad |
|---|---|---|---|---|---|
| 80-100 | 56 | 32 | 24 | 57.1 | 42.9 |
| 60-79 | 130 | 56 | 74 | 43.1 | 56.9 |
| 40-59 | 294 | 112 | 149 | 38.1 | 50.7 |
| 20-39 | 217 | 51 | 152 | 23.5 | 70.0 |
| 0-19 | 231 | 26 | 197 | 11.3 | 85.3 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **20** (manually lowered 20 → 13 on 2026-06-24).

| Floor | Bad cut | % of bad | Good lost | % of good |
|---|---|---|---|---|
| 13 | 68 | 11.4 | 7 | 2.5 |
| 15 | 141 | 23.7 | 18 | 6.5 |
| 20 | 197 | 33.1 | 26 | 9.4 |
| 25 | 226 | 37.9 | 33 | 11.9 |
| 30 | 309 | 51.8 | 61 | 22.0 |
| 35 | 329 | 55.2 | 67 | 24.2 |
| 40 | 349 | 58.6 | 77 | 27.8 |
| 45 | 382 | 64.1 | 94 | 33.9 |
| 50 | 458 | 76.8 | 175 | 63.2 |
| 60 | 498 | 83.6 | 189 | 68.2 |

### By category

| Category | n | good | interesting | bad | % bad |
|---|---|---|---|---|---|
| news | 706 | 167 | 28 | 511 | 72.4 |
| ai-tech | 72 | 32 | 14 | 26 | 36.1 |
| wellness | 55 | 19 | 7 | 28 | 50.9 |
| local | 39 | 29 | 0 | 10 | 25.6 |
| climate | 21 | 12 | 3 | 6 | 28.6 |
| science | 14 | 12 | 0 | 2 | 14.3 |
| scifi | 7 | 0 | 0 | 7 | 100.0 |
| homelab | 7 | 2 | 2 | 3 | 42.9 |
| shared | 4 | 4 | 0 | 0 | 0.0 |
| podcast-sunday | 2 | 0 | 0 | 2 | 100.0 |
| podcast-friday | 1 | 0 | 0 | 1 | 100.0 |

### Sources (≥ 5 ratings)

**Highest good-rate**

| Source | n | good | bad | % good |
|---|---|---|---|---|
| Eagle Feather News | 6 | 6 | 0 | 100.0 |
| 100 Mile Free Press | 6 | 6 | 0 | 100.0 |
| ScienceDaily | 5 | 5 | 0 | 100.0 |
| ScienceAlert | 8 | 7 | 1 | 87.5 |
| The Narwhal | 5 | 4 | 1 | 80.0 |
| EarthSky | 5 | 4 | 1 | 80.0 |
| Williams Lake Tribune | 17 | 13 | 4 | 76.5 |
| BC Gov News | 13 | 9 | 4 | 69.2 |
| APTN News | 10 | 6 | 3 | 60.0 |
| MakeUseOf | 5 | 3 | 2 | 60.0 |

**Highest bad-rate**

| Source | n | good | bad | % bad |
|---|---|---|---|---|
| Reactor Magazine | 10 | 1 | 9 | 90.0 |
| Lifehacker | 23 | 3 | 20 | 87.0 |
| Toms Guide | 37 | 5 | 32 | 86.5 |
| Neowin | 14 | 2 | 12 | 85.7 |
| CBC Arts | 13 | 2 | 11 | 84.6 |
| Al Jazeera English | 34 | 5 | 28 | 82.4 |
| Android Authority | 25 | 5 | 20 | 80.0 |
| Open Culture | 5 | 1 | 4 | 80.0 |
| NYT Top Stories | 24 | 3 | 19 | 79.2 |
| Quartz | 19 | 3 | 15 | 78.9 |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 216 | 28 | 497 |
| breaking | 21 | 12 | 43 |
| analysis | 19 | 10 | 13 |
| feature | 14 | 3 | 22 |
| news | 4 | 0 | 7 |
| opinion | 0 | 1 | 9 |
| wire | 2 | 0 | 2 |
| recap | 1 | 0 | 2 |
| fluff | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 86 | 27 | 74 |
| low | 18 | 1 | 47 |
| high | 28 | 0 | 16 |
| mid | 85 | 0 | 102 |
| unknown | 4 | 0 | 3 |
| unfiltered | 56 | 26 | 354 |

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
| 2026-07-26 | 310 | 19 | 6 |
| 2026-08-02 | 1516 | 128 | 8 |
| 2026-08-09 | 1421 | 112 | 8 |

## 3. Theme-Bucket Routing Accuracy

Of **921** ratings tied to an aired day, you corrected the day on **231** (25.1%). Additionally 109 good articles were approved for other days.

### Per theme day

| Day | Theme | n | good | bad | % good | Corrected away |
|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 136 | 32 | 94 | 23.5 | 31 |
| tuesday | Working Lands & Industry | 122 | 33 | 87 | 27.0 | 27 |
| wednesday | Repair Culture & Practical Tech | 177 | 68 | 98 | 38.4 | 45 |
| thursday | Indigenous Lands & Innovation | 113 | 27 | 73 | 23.9 | 26 |
| friday | Wild Spaces & Outdoor Life | 174 | 44 | 117 | 25.3 | 41 |
| saturday | Cariboo Local Affairs | 115 | 40 | 72 | 34.8 | 37 |
| sunday | Science, Wonder & the Natural World | 84 | 29 | 52 | 34.5 | 24 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 7 | 7 | 1 | 5 | 4 | 7 |
| tuesday | 7 |  | 5 | 2 | 5 | 3 | 5 |
| wednesday | 4 | 7 |  | 2 | 12 | 9 | 11 |
| thursday | 1 | 4 | 6 |  | 6 |  | 9 |
| friday | 3 | 6 | 9 | 5 |  | 6 | 12 |
| saturday |  | 3 | 8 | 5 | 7 |  | 14 |
| sunday | 2 | 5 | 7 | 1 | 5 | 4 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 85 |
| Theme scorer disagreed with you (scoring miss) | 146 |
| Theme scores missing on the rating | 0 |

## 3b. Category Retag Accuracy

Of **199** ratings carrying a confirmed/retagged category, you retagged **23** (11.6%) to a different category.

### Category → category correction matrix (shown → corrected)

| Shown | Corrected to | Count |
|---|---|---|
| news | ai-tech | 12 |
| news | wellness | 4 |
| news | climate | 2 |
| news | science | 1 |
| news | homelab | 1 |
| news | local | 1 |
| science | climate | 1 |
| design | homelab | 1 |

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
| 2026-W29 | 7 | 1039 | 68 |
| 2026-W30 | 7 | 1068 | 72 |
| 2026-W31 | 7 | 1065 | 63 |
| 2026-W32 | 6 | 1293 | 86 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-07-26T06:41:43.169266+00:00 | 996 | 521 | 53 | 90 | 23 |
| 2026-07-26T19:16:45.882303+00:00 | 922 | 444 | 69 | 255 | 65 |
| 2026-07-27T07:39:07.608433+00:00 | 876 | 371 | 47 | 223 | 51 |
| 2026-07-28T06:32:23.887103+00:00 | 971 | 561 | 70 | 334 | 92 |
| 2026-07-29T06:37:08.350171+00:00 | 1149 | 704 | 70 | 421 | 127 |
| 2026-07-30T06:33:33.094608+00:00 | 1129 | 696 | 68 | 451 | 105 |
| 2026-07-31T06:49:56.587784+00:00 | 1136 | 695 | 77 | 435 | 114 |
| 2026-08-01T06:35:31.274281+00:00 | 1115 | 673 | 63 | 398 | 131 |
| 2026-08-01T13:12:43.371003+00:00 | 1088 | 585 | 55 | 334 | 118 |
| 2026-08-02T06:39:02.102559+00:00 | 959 | 487 | 62 | 291 | 69 |
| 2026-08-03T07:34:53.939952+00:00 | 919 | 429 | 68 | 228 | 52 |
| 2026-08-04T06:33:41.731980+00:00 | 1219 | 663 | 85 | 380 | 97 |
| 2026-08-05T06:34:09.067011+00:00 | 1368 | 789 | 89 | 459 | 117 |
| 2026-08-06T06:37:00.324899+00:00 | 1347 | 800 | 99 | 490 | 107 |
| 2026-08-07T05:45:17.772762+00:00 | 1353 | 805 | 89 | 460 | 122 |
| 2026-08-08T05:03:53.543600+00:00 | 1336 | 783 | 80 | 452 | 126 |
| 2026-08-09T05:11:33.008313+00:00 | 1436 | 868 | 92 | 506 | 159 |

### Current category feed sizes

| Feed | Items |
|---|---|
| news | 124 |
| ai-tech | 85 |
| wellness | 54 |
| science | 41 |
| local | 40 |
| climate | 38 |
| design | 30 |
| homelab | 23 |
| homestead | 14 |
| scifi | 10 |
| outdoors | 1 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 15 / 8 |
| Calibration stats runs available | 17 |
| Calibration stats range | 2026-07-26 → 2026-08-09 |
| theme_holdover_cache.json present | False |

**Context:** `calibration_stats_cache.json` was first committed on 2026-07-07, so every weekly calibration run before that found no stats and skipped — the log's repeated "Claude call or response parsing failed" lines were misleading boilerplate, not API failures. The agent's Claude path has effectively never run.

