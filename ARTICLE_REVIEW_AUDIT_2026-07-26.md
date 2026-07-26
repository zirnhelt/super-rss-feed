# Article Review Audit

_Generated: 2026-07-26 20:24 UTC — ratings window 2026-06-17 → 2026-07-26_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 741 |
| Rated **bad** (fluff/noise that reached you) | 467 (63.0%) |
| Rated **good** | 250 (33.7%) |
| Rated **interesting** | 24 |
| Theme-day corrections (`better_theme`) | 207 (28.2% of day-routed ratings) |
| …caused by selection ignoring its own theme scores | 73 |
| …caused by the theme scorer itself missing | 134 |
| Category retags | 5 (41.7% of categorized ratings) |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 250 | 51.5 | 48.5 | 47.2 | 47.1 |
| interesting | 24 | 40.6 | 48.0 | 53.0 | 44.8 |
| bad | 467 | 37.9 | 35 | 37.9 | 34.7 |

### Precision by score band

| Score band | n | good | bad | % good | % bad |
|---|---|---|---|---|---|
| 80-100 | 56 | 32 | 24 | 57.1 | 42.9 |
| 60-79 | 128 | 55 | 73 | 43.0 | 57.0 |
| 40-59 | 239 | 99 | 122 | 41.4 | 51.0 |
| 20-39 | 133 | 41 | 89 | 30.8 | 66.9 |
| 0-19 | 185 | 23 | 159 | 12.4 | 85.9 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **20** (manually lowered 20 → 13 on 2026-06-24).

| Floor | Bad cut | % of bad | Good lost | % of good |
|---|---|---|---|---|
| 13 | 68 | 14.6 | 7 | 2.8 |
| 15 | 137 | 29.3 | 18 | 7.2 |
| 20 | 159 | 34.0 | 23 | 9.2 |
| 25 | 166 | 35.5 | 27 | 10.8 |
| 30 | 222 | 47.5 | 49 | 19.6 |
| 35 | 233 | 49.9 | 55 | 22.0 |
| 40 | 248 | 53.1 | 64 | 25.6 |
| 45 | 276 | 59.1 | 81 | 32.4 |
| 50 | 332 | 71.1 | 149 | 59.6 |
| 60 | 370 | 79.2 | 163 | 65.2 |

### By category

| Category | n | good | interesting | bad | % bad |
|---|---|---|---|---|---|
| news | 569 | 162 | 12 | 395 | 69.4 |
| ai-tech | 50 | 20 | 8 | 22 | 44.0 |
| wellness | 41 | 15 | 2 | 24 | 58.5 |
| local | 36 | 28 | 0 | 8 | 22.2 |
| climate | 16 | 10 | 1 | 5 | 31.2 |
| science | 10 | 10 | 0 | 0 | 0.0 |
| scifi | 7 | 0 | 0 | 7 | 100.0 |
| homelab | 5 | 1 | 1 | 3 | 60.0 |
| shared | 4 | 4 | 0 | 0 | 0.0 |
| podcast-sunday | 2 | 0 | 0 | 2 | 100.0 |
| podcast-friday | 1 | 0 | 0 | 1 | 100.0 |

### Sources (≥ 5 ratings)

**Highest good-rate**

| Source | n | good | bad | % good |
|---|---|---|---|---|
| Eagle Feather News | 6 | 6 | 0 | 100.0 |
| 100 Mile Free Press | 6 | 6 | 0 | 100.0 |
| ScienceAlert | 5 | 5 | 0 | 100.0 |
| Williams Lake Tribune | 16 | 13 | 3 | 81.2 |
| BC Gov News | 10 | 8 | 2 | 80.0 |
| The Narwhal | 5 | 4 | 1 | 80.0 |
| New Atlas | 12 | 9 | 3 | 75.0 |
| APTN News | 8 | 5 | 3 | 62.5 |
| My Cariboo Now | 13 | 8 | 5 | 61.5 |
| MakeUseOf | 5 | 3 | 2 | 60.0 |

**Highest bad-rate**

| Source | n | good | bad | % bad |
|---|---|---|---|---|
| Neowin | 11 | 1 | 10 | 90.9 |
| Reactor Magazine | 10 | 1 | 9 | 90.0 |
| Al Jazeera English | 27 | 3 | 24 | 88.9 |
| Lifehacker | 17 | 2 | 15 | 88.2 |
| My East Kootenay Now | 8 | 1 | 7 | 87.5 |
| NPR Health News | 7 | 1 | 6 | 85.7 |
| Toms Guide | 26 | 4 | 22 | 84.6 |
| CBC Arts | 12 | 2 | 10 | 83.3 |
| Quartz | 17 | 3 | 14 | 82.4 |
| NYT Business | 20 | 3 | 16 | 80.0 |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 199 | 9 | 385 |
| breaking | 17 | 7 | 39 |
| feature | 13 | 1 | 18 |
| analysis | 16 | 6 | 8 |
| opinion | 0 | 1 | 9 |
| news | 3 | 0 | 5 |
| wire | 1 | 0 | 2 |
| recap | 1 | 0 | 0 |
| fluff | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 74 | 13 | 57 |
| low | 12 | 0 | 39 |
| high | 28 | 0 | 16 |
| mid | 85 | 0 | 102 |
| unknown | 4 | 0 | 3 |
| unfiltered | 47 | 11 | 250 |

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

## 3. Theme-Bucket Routing Accuracy

Of **734** ratings tied to an aired day, you corrected the day on **207** (28.2%). Additionally 85 good articles were approved for other days.

### Per theme day

| Day | Theme | n | good | bad | % good | Corrected away |
|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 79 | 26 | 49 | 32.9 | 25 |
| tuesday | Working Lands & Industry | 92 | 27 | 64 | 29.3 | 23 |
| wednesday | Repair Culture & Practical Tech | 145 | 64 | 79 | 44.1 | 42 |
| thursday | Indigenous Lands & Innovation | 85 | 20 | 60 | 23.5 | 19 |
| friday | Wild Spaces & Outdoor Life | 148 | 42 | 100 | 28.4 | 39 |
| saturday | Cariboo Local Affairs | 101 | 38 | 60 | 37.6 | 35 |
| sunday | Science, Wonder & the Natural World | 84 | 29 | 52 | 34.5 | 24 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 7 | 4 | 1 | 4 | 3 | 6 |
| tuesday | 6 |  | 5 | 2 | 3 | 2 | 5 |
| wednesday | 4 | 6 |  | 2 | 11 | 9 | 10 |
| thursday | 1 | 3 | 5 |  | 6 |  | 4 |
| friday | 3 | 5 | 9 | 5 |  | 6 | 11 |
| saturday |  | 3 | 8 | 5 | 6 |  | 13 |
| sunday | 2 | 5 | 7 | 1 | 5 | 4 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 73 |
| Theme scorer disagreed with you (scoring miss) | 134 |
| Theme scores missing on the rating | 0 |

## 3b. Category Retag Accuracy

Of **12** ratings carrying a confirmed/retagged category, you retagged **5** (41.7%) to a different category.

### Category → category correction matrix (shown → corrected)

| Shown | Corrected to | Count |
|---|---|---|
| news | wellness | 2 |
| news | climate | 1 |
| news | science | 1 |
| news | ai-tech | 1 |

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

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-07-13T07:28:29.183589+00:00 | 800 | 375 | 55 | 43 | 17 |
| 2026-07-14T06:17:35.491468+00:00 | 1032 | 560 | 73 | 85 | 18 |
| 2026-07-15T06:21:17.984425+00:00 | 1168 | 646 | 79 | 106 | 27 |
| 2026-07-16T06:25:01.108796+00:00 | 1231 | 692 | 76 | 131 | 38 |
| 2026-07-17T06:22:32.363219+00:00 | 1191 | 689 | 80 | 116 | 47 |
| 2026-07-18T06:10:19.075806+00:00 | 1126 | 643 | 71 | 106 | 28 |
| 2026-07-19T06:35:54.116378+00:00 | 946 | 551 | 62 | 81 | 22 |
| 2026-07-20T06:54:16.599439+00:00 | 809 | 386 | 55 | 38 | 19 |
| 2026-07-21T06:34:55.714447+00:00 | 941 | 554 | 71 | 78 | 33 |
| 2026-07-22T06:35:25.137439+00:00 | 1128 | 675 | 81 | 116 | 26 |
| 2026-07-23T06:34:57.460147+00:00 | 1179 | 694 | 77 | 99 | 38 |
| 2026-07-24T06:32:08.133283+00:00 | 1151 | 674 | 70 | 111 | 28 |
| 2026-07-25T06:23:48.943095+00:00 | 1157 | 696 | 80 | 129 | 25 |
| 2026-07-26T06:41:43.169266+00:00 | 996 | 521 | 53 | 90 | 23 |
| 2026-07-26T19:16:45.882303+00:00 | 922 | 444 | 69 | 255 | 65 |

### Current category feed sizes

| Feed | Items |
|---|---|
| news | 144 |
| ai-tech | 71 |
| local | 50 |
| wellness | 47 |
| science | 37 |
| climate | 23 |
| homelab | 14 |
| scifi | 8 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 13 / 8 |
| Calibration stats runs available | 15 |
| Calibration stats range | 2026-07-13 → 2026-07-26 |
| theme_holdover_cache.json present | False |

**Context:** `calibration_stats_cache.json` was first committed on 2026-07-07, so every weekly calibration run before that found no stats and skipped — the log's repeated "Claude call or response parsing failed" lines were misleading boilerplate, not API failures. The agent's Claude path has effectively never run.

