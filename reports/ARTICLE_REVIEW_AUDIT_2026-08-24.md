# Article Review Audit

_Generated: 2026-08-24 03:18 UTC — ratings window 2026-06-17 → 2026-08-22_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 1142 |
| Rated **bad** (fluff/noise that reached you) | 751 (65.8%) |
| Rated **good** | 300 (26.3%) |
| Rated **interesting** | 90 |
| Theme-day corrections (`better_theme`) | 247 (21.8% of day-routed ratings) |
| …caused by selection ignoring its own theme scores | 91 |
| …caused by the theme scorer itself missing | 156 |
| Category retags | 43 (10.4% of categorized ratings) |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 300 | 49.7 | 48.5 | 43.7 | 43.0 |
| interesting | 90 | 36.6 | 42.5 | 29.8 | 24.6 |
| bad | 751 | 34.8 | 29 | 26.5 | 23.5 |

### Precision by score band

| Score band | n | good | bad | % good | % bad |
|---|---|---|---|---|---|
| 80-100 | 57 | 33 | 24 | 57.9 | 42.1 |
| 60-79 | 132 | 56 | 75 | 42.4 | 56.8 |
| 40-59 | 364 | 127 | 192 | 34.9 | 52.7 |
| 20-39 | 323 | 57 | 235 | 17.6 | 72.8 |
| 0-19 | 266 | 27 | 225 | 10.2 | 84.6 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **23** (manually lowered 20 → 13 on 2026-06-24).

| Floor | Bad cut | % of bad | Good lost | % of good |
|---|---|---|---|---|
| 13 | 68 | 9.1 | 7 | 2.3 |
| 15 | 153 | 20.4 | 18 | 6.0 |
| 20 | 225 | 30.0 | 27 | 9.0 |
| 25 | 277 | 36.9 | 35 | 11.7 |
| 30 | 397 | 52.9 | 66 | 22.0 |
| 35 | 433 | 57.7 | 74 | 24.7 |
| 40 | 460 | 61.3 | 84 | 28.0 |
| 45 | 503 | 67.0 | 101 | 33.7 |
| 50 | 610 | 81.2 | 197 | 65.7 |
| 60 | 652 | 86.8 | 211 | 70.3 |

### By category

| Category | n | good | interesting | bad | % bad |
|---|---|---|---|---|---|
| news | 848 | 174 | 34 | 640 | 75.5 |
| ai-tech | 85 | 35 | 19 | 31 | 36.5 |
| wellness | 78 | 21 | 14 | 42 | 53.8 |
| local | 40 | 30 | 0 | 10 | 25.0 |
| climate | 23 | 13 | 4 | 6 | 26.1 |
| science | 17 | 15 | 0 | 2 | 11.8 |
| homelab | 14 | 3 | 7 | 4 | 28.6 |
| design | 12 | 1 | 7 | 4 | 33.3 |
| scifi | 11 | 1 | 2 | 8 | 72.7 |
| shared | 4 | 4 | 0 | 0 | 0.0 |
| homestead | 4 | 2 | 2 | 0 | 0.0 |
| outdoors | 3 | 1 | 1 | 1 | 33.3 |
| podcast-sunday | 2 | 0 | 0 | 2 | 100.0 |
| podcast-friday | 1 | 0 | 0 | 1 | 100.0 |

### Sources (≥ 5 ratings)

**Highest good-rate**

| Source | n | good | bad | % good |
|---|---|---|---|---|
| Eagle Feather News | 6 | 6 | 0 | 100.0 |
| ScienceAlert | 10 | 9 | 1 | 90.0 |
| 100 Mile Free Press | 8 | 7 | 1 | 87.5 |
| ScienceDaily | 7 | 6 | 0 | 85.7 |
| The Narwhal | 5 | 4 | 1 | 80.0 |
| EarthSky | 5 | 4 | 1 | 80.0 |
| Williams Lake Tribune | 17 | 13 | 4 | 76.5 |
| BC Gov News | 14 | 9 | 5 | 64.3 |
| APTN News | 10 | 6 | 3 | 60.0 |
| MakeUseOf | 5 | 3 | 2 | 60.0 |

**Highest bad-rate**

| Source | n | good | bad | % bad |
|---|---|---|---|---|
| Rolling Stone | 14 | 0 | 14 | 100.0 |
| The New Yorker | 5 | 0 | 5 | 100.0 |
| Reactor Magazine | 10 | 1 | 9 | 90.0 |
| Domino | 8 | 0 | 7 | 87.5 |
| Lifehacker | 23 | 3 | 20 | 87.0 |
| Neowin | 15 | 2 | 13 | 86.7 |
| Toms Guide | 37 | 5 | 32 | 86.5 |
| CBC Arts | 13 | 2 | 11 | 84.6 |
| Ideal Home (Country Homes & Interiors) | 13 | 0 | 11 | 84.6 |
| Edge (GamesRadar) | 12 | 0 | 10 | 83.3 |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 228 | 53 | 633 |
| breaking | 23 | 16 | 50 |
| analysis | 26 | 13 | 19 |
| feature | 15 | 6 | 26 |
| opinion | 1 | 1 | 11 |
| news | 4 | 1 | 7 |
| wire | 2 | 0 | 2 |
| recap | 1 | 0 | 2 |
| fluff | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 101 | 37 | 101 |
| low | 19 | 4 | 65 |
| high | 28 | 0 | 16 |
| mid | 85 | 0 | 102 |
| unknown | 4 | 0 | 3 |
| unfiltered | 63 | 49 | 464 |

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
| 2026-08-23 | 1753 | 189 | 11 |
| 2026-08-24 | 1753 | 189 | 11 |

## 3. Theme-Bucket Routing Accuracy

Of **1135** ratings tied to an aired day, you corrected the day on **247** (21.8%). Additionally 126 good articles were approved for other days.

### Per theme day

| Day | Theme | n | good | bad | % good | Corrected away |
|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 166 | 35 | 118 | 21.1 | 33 |
| tuesday | Working Lands & Industry | 151 | 33 | 110 | 21.9 | 27 |
| wednesday | Repair Culture & Practical Tech | 209 | 69 | 127 | 33.0 | 46 |
| thursday | Indigenous Lands & Innovation | 142 | 30 | 93 | 21.1 | 28 |
| friday | Wild Spaces & Outdoor Life | 204 | 49 | 134 | 24.0 | 44 |
| saturday | Cariboo Local Affairs | 146 | 43 | 97 | 29.5 | 40 |
| sunday | Science, Wonder & the Natural World | 117 | 37 | 69 | 31.6 | 29 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 8 | 7 | 1 | 5 | 4 | 8 |
| tuesday | 7 |  | 5 | 2 | 5 | 3 | 5 |
| wednesday | 4 | 7 |  | 2 | 12 | 9 | 12 |
| thursday | 1 | 4 | 6 |  | 6 | 1 | 10 |
| friday | 4 | 7 | 9 | 5 |  | 6 | 13 |
| saturday |  | 3 | 9 | 5 | 8 |  | 15 |
| sunday | 4 | 6 | 8 | 1 | 5 | 5 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 91 |
| Theme scorer disagreed with you (scoring miss) | 156 |
| Theme scores missing on the rating | 0 |

## 3b. Category Retag Accuracy

Of **413** ratings carrying a confirmed/retagged category, you retagged **43** (10.4%) to a different category.

### Category → category correction matrix (shown → corrected)

| Shown | Corrected to | Count |
|---|---|---|
| news | ai-tech | 15 |
| news | wellness | 6 |
| news | design | 5 |
| news | homestead | 4 |
| news | homelab | 3 |
| news | climate | 2 |
| news | scifi | 2 |
| news | outdoors | 2 |
| news | science | 1 |
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
| 2026-W32 | 7 | 1287 | 86 |
| 2026-W33 | 7 | 1563 | 93 |
| 2026-W34 | 11 | 1533 | 80 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-08-09T05:11:33.008313+00:00 | 1436 | 868 | 92 | 506 | 159 |
| 2026-08-10T05:38:25.410529+00:00 | 1252 | 640 | 86 | 330 | 113 |
| 2026-08-11T05:14:55.976214+00:00 | 1503 | 892 | 90 | 540 | 139 |
| 2026-08-12T05:41:50.515518+00:00 | 1696 | 1028 | 101 | 599 | 198 |
| 2026-08-13T05:44:08.311631+00:00 | 1711 | 1058 | 92 | 662 | 169 |
| 2026-08-14T05:41:51.946942+00:00 | 1689 | 988 | 92 | 626 | 165 |
| 2026-08-15T04:37:32.705408+00:00 | 1651 | 980 | 94 | 572 | 205 |
| 2026-08-16T04:41:25.880350+00:00 | 1448 | 793 | 87 | 431 | 185 |
| 2026-08-17T04:50:51.265048+00:00 | 1245 | 632 | 92 | 335 | 110 |
| 2026-08-18T04:41:37.045487+00:00 | 1518 | 875 | 95 | 481 | 169 |
| 2026-08-19T04:42:31.614867+00:00 | 1655 | 1010 | 100 | 609 | 179 |
| 2026-08-20T02:43:14.666473+00:00 | 1745 | 1069 | 88 | 644 | 201 |
| 2026-08-20T04:43:23.571835+00:00 | 1743 | 973 | 77 | 583 | 183 |
| 2026-08-21T04:45:28.371544+00:00 | 1747 | 1045 | 92 | 664 | 162 |
| 2026-08-21T14:18:14.556575+00:00 | 1442 | 1094 | 82 | 687 | 185 |
| 2026-08-22T04:39:16.923783+00:00 | 1743 | 1061 | 96 | 659 | 182 |
| 2026-08-22T13:53:48.407756+00:00 | 1251 | 881 | 86 | 550 | 126 |
| 2026-08-22T14:33:42.637421+00:00 | 1261 | 810 | 62 | 595 | 0 |
| 2026-08-22T14:44:10.741080+00:00 | 1259 | 744 | 45 | 551 | 0 |
| 2026-08-23T04:43:12.336857+00:00 | 1499 | 722 | 61 | 368 | 0 |

### Current category feed sizes

| Feed | Items |
|---|---|
| news | 254 |
| ai-tech | 148 |
| wellness | 108 |
| science | 57 |
| design | 53 |
| local | 46 |
| homelab | 43 |
| climate | 38 |
| outdoors | 20 |
| scifi | 19 |
| homestead | 12 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 18 / 9 |
| Calibration stats runs available | 20 |
| Calibration stats range | 2026-08-09 → 2026-08-23 |
| theme_holdover_cache.json present | True |

**Context:** `calibration_stats_cache.json` was first committed on 2026-07-07, so every weekly calibration run before that found no stats and skipped — the log's repeated "Claude call or response parsing failed" lines were misleading boilerplate, not API failures. The agent's Claude path has effectively never run.

