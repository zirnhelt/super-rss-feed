# Article Review Audit

_Generated: 2026-08-16 13:44 UTC — ratings window 2026-06-17 → 2026-08-16_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 1050 |
| Rated **bad** (fluff/noise that reached you) | 684 (65.1%) |
| Rated **good** | 293 (27.9%) |
| Rated **interesting** | 72 |
| Theme-day corrections (`better_theme`) | 242 (23.2% of day-routed ratings) |
| …caused by selection ignoring its own theme scores | 88 |
| …caused by the theme scorer itself missing | 154 |
| Category retags | 35 (10.9% of categorized ratings) |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 293 | 49.6 | 48 | 43.8 | 43.2 |
| interesting | 72 | 36.7 | 46.0 | 31.0 | 25.8 |
| bad | 684 | 35.2 | 29.0 | 28.3 | 25.4 |

### Precision by score band

| Score band | n | good | bad | % good | % bad |
|---|---|---|---|---|---|
| 80-100 | 56 | 32 | 24 | 57.1 | 42.9 |
| 60-79 | 130 | 56 | 74 | 43.1 | 56.9 |
| 40-59 | 336 | 122 | 176 | 36.3 | 52.4 |
| 20-39 | 274 | 56 | 195 | 20.4 | 71.2 |
| 0-19 | 254 | 27 | 215 | 10.6 | 84.6 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **20** (manually lowered 20 → 13 on 2026-06-24).

| Floor | Bad cut | % of bad | Good lost | % of good |
|---|---|---|---|---|
| 13 | 68 | 9.9 | 7 | 2.4 |
| 15 | 149 | 21.8 | 18 | 6.1 |
| 20 | 215 | 31.4 | 27 | 9.2 |
| 25 | 254 | 37.1 | 35 | 11.9 |
| 30 | 355 | 51.9 | 65 | 22.2 |
| 35 | 387 | 56.6 | 73 | 24.9 |
| 40 | 410 | 59.9 | 83 | 28.3 |
| 45 | 449 | 65.6 | 100 | 34.1 |
| 50 | 545 | 79.7 | 191 | 65.2 |
| 60 | 586 | 85.7 | 205 | 70.0 |

### By category

| Category | n | good | interesting | bad | % bad |
|---|---|---|---|---|---|
| news | 783 | 172 | 30 | 581 | 74.2 |
| ai-tech | 78 | 33 | 16 | 29 | 37.2 |
| wellness | 69 | 21 | 9 | 38 | 55.1 |
| local | 39 | 29 | 0 | 10 | 25.6 |
| climate | 22 | 12 | 4 | 6 | 27.3 |
| science | 17 | 15 | 0 | 2 | 11.8 |
| homelab | 12 | 3 | 5 | 4 | 33.3 |
| scifi | 9 | 1 | 1 | 7 | 77.8 |
| design | 8 | 1 | 4 | 3 | 37.5 |
| shared | 4 | 4 | 0 | 0 | 0.0 |
| outdoors | 3 | 1 | 1 | 1 | 33.3 |
| homestead | 3 | 1 | 2 | 0 | 0.0 |
| podcast-sunday | 2 | 0 | 0 | 2 | 100.0 |
| podcast-friday | 1 | 0 | 0 | 1 | 100.0 |

### Sources (≥ 5 ratings)

**Highest good-rate**

| Source | n | good | bad | % good |
|---|---|---|---|---|
| Eagle Feather News | 6 | 6 | 0 | 100.0 |
| ScienceDaily | 6 | 6 | 0 | 100.0 |
| ScienceAlert | 10 | 9 | 1 | 90.0 |
| 100 Mile Free Press | 8 | 7 | 1 | 87.5 |
| The Narwhal | 5 | 4 | 1 | 80.0 |
| EarthSky | 5 | 4 | 1 | 80.0 |
| Williams Lake Tribune | 17 | 13 | 4 | 76.5 |
| BC Gov News | 14 | 9 | 5 | 64.3 |
| APTN News | 10 | 6 | 3 | 60.0 |
| MakeUseOf | 5 | 3 | 2 | 60.0 |

**Highest bad-rate**

| Source | n | good | bad | % bad |
|---|---|---|---|---|
| Rolling Stone | 8 | 0 | 8 | 100.0 |
| Reactor Magazine | 10 | 1 | 9 | 90.0 |
| Lifehacker | 23 | 3 | 20 | 87.0 |
| Toms Guide | 37 | 5 | 32 | 86.5 |
| Neowin | 14 | 2 | 12 | 85.7 |
| Edge (GamesRadar) | 7 | 0 | 6 | 85.7 |
| CBC Arts | 13 | 2 | 11 | 84.6 |
| Dwell | 6 | 1 | 5 | 83.3 |
| NYT Top Stories | 28 | 3 | 23 | 82.1 |
| Al Jazeera English | 35 | 5 | 28 | 80.0 |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 225 | 42 | 575 |
| breaking | 22 | 13 | 45 |
| analysis | 23 | 11 | 18 |
| feature | 15 | 5 | 24 |
| opinion | 1 | 1 | 10 |
| news | 4 | 0 | 7 |
| wire | 2 | 0 | 2 |
| recap | 1 | 0 | 2 |
| fluff | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 96 | 31 | 90 |
| low | 19 | 3 | 56 |
| high | 28 | 0 | 16 |
| mid | 85 | 0 | 102 |
| unknown | 4 | 0 | 3 |
| unfiltered | 61 | 38 | 417 |

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
| 2026-08-16 | 1224 | 182 | 15 |

## 3. Theme-Bucket Routing Accuracy

Of **1043** ratings tied to an aired day, you corrected the day on **242** (23.2%). Additionally 120 good articles were approved for other days.

### Per theme day

| Day | Theme | n | good | bad | % good | Corrected away |
|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 150 | 33 | 105 | 22.0 | 32 |
| tuesday | Working Lands & Industry | 137 | 33 | 101 | 24.1 | 27 |
| wednesday | Repair Culture & Practical Tech | 193 | 69 | 113 | 35.8 | 46 |
| thursday | Indigenous Lands & Innovation | 128 | 30 | 80 | 23.4 | 28 |
| friday | Wild Spaces & Outdoor Life | 189 | 48 | 123 | 25.4 | 44 |
| saturday | Cariboo Local Affairs | 146 | 43 | 97 | 29.5 | 40 |
| sunday | Science, Wonder & the Natural World | 100 | 33 | 62 | 33.0 | 25 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 7 | 7 | 1 | 5 | 4 | 8 |
| tuesday | 7 |  | 5 | 2 | 5 | 3 | 5 |
| wednesday | 4 | 7 |  | 2 | 12 | 9 | 12 |
| thursday | 1 | 4 | 6 |  | 6 | 1 | 10 |
| friday | 4 | 7 | 9 | 5 |  | 6 | 13 |
| saturday |  | 3 | 9 | 5 | 8 |  | 15 |
| sunday | 2 | 6 | 7 | 1 | 5 | 4 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 88 |
| Theme scorer disagreed with you (scoring miss) | 154 |
| Theme scores missing on the rating | 0 |

## 3b. Category Retag Accuracy

Of **321** ratings carrying a confirmed/retagged category, you retagged **35** (10.9%) to a different category.

### Category → category correction matrix (shown → corrected)

| Shown | Corrected to | Count |
|---|---|---|
| news | ai-tech | 13 |
| news | wellness | 5 |
| news | design | 3 |
| news | homestead | 3 |
| news | climate | 2 |
| news | homelab | 2 |
| news | outdoors | 2 |
| news | science | 1 |
| news | local | 1 |
| news | scifi | 1 |
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
| 2026-W32 | 7 | 1287 | 86 |
| 2026-W33 | 6 | 1616 | 93 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-08-02T06:39:02.102559+00:00 | 959 | 487 | 62 | 291 | 69 |
| 2026-08-03T07:34:53.939952+00:00 | 919 | 429 | 68 | 228 | 52 |
| 2026-08-04T06:33:41.731980+00:00 | 1219 | 663 | 85 | 380 | 97 |
| 2026-08-05T06:34:09.067011+00:00 | 1368 | 789 | 89 | 459 | 117 |
| 2026-08-06T06:37:00.324899+00:00 | 1347 | 800 | 99 | 490 | 107 |
| 2026-08-07T05:45:17.772762+00:00 | 1353 | 805 | 89 | 460 | 122 |
| 2026-08-08T05:03:53.543600+00:00 | 1336 | 783 | 80 | 452 | 126 |
| 2026-08-09T05:11:33.008313+00:00 | 1436 | 868 | 92 | 506 | 159 |
| 2026-08-10T05:38:25.410529+00:00 | 1252 | 640 | 86 | 330 | 113 |
| 2026-08-11T05:14:55.976214+00:00 | 1503 | 892 | 90 | 540 | 139 |
| 2026-08-12T05:41:50.515518+00:00 | 1696 | 1028 | 101 | 599 | 198 |
| 2026-08-13T05:44:08.311631+00:00 | 1711 | 1058 | 92 | 662 | 169 |
| 2026-08-14T05:41:51.946942+00:00 | 1689 | 988 | 92 | 626 | 165 |
| 2026-08-15T04:37:32.705408+00:00 | 1651 | 980 | 94 | 572 | 205 |
| 2026-08-16T04:41:25.880350+00:00 | 1448 | 793 | 87 | 431 | 185 |

### Current category feed sizes

| Feed | Items |
|---|---|
| news | 126 |
| ai-tech | 90 |
| wellness | 53 |
| climate | 49 |
| local | 46 |
| science | 41 |
| design | 30 |
| homelab | 27 |
| scifi | 8 |
| homestead | 7 |
| outdoors | 6 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 16 / 8 |
| Calibration stats runs available | 15 |
| Calibration stats range | 2026-08-02 → 2026-08-16 |
| theme_holdover_cache.json present | True |

**Context:** `calibration_stats_cache.json` was first committed on 2026-07-07, so every weekly calibration run before that found no stats and skipped — the log's repeated "Claude call or response parsing failed" lines were misleading boilerplate, not API failures. The agent's Claude path has effectively never run.

