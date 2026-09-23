# Article Review Audit

_Generated: 2026-09-06 16:14 UTC — ratings window 2026-06-17 → 2026-09-06_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 1305 |
| Rated **bad** (fluff/noise that reached you) | 881 (67.5%) |
| Rated **good** | 312 (23.9%) |
| Rated **interesting** | 111 |
| Theme-day corrections (`better_theme`) | 257 (19.8% of day-routed ratings) |
| …caused by selection ignoring its own theme scores | 94 |
| …caused by the theme scorer itself missing | 163 |
| Category retags | 49 (8.5% of categorized ratings) |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 312 | 49.4 | 49.0 | 43.6 | 42.9 |
| interesting | 111 | 37.2 | 44 | 29.4 | 24.7 |
| bad | 881 | 34.0 | 29 | 23.6 | 20.7 |

### Precision by score band

| Score band | n | good | bad | % good | % bad |
|---|---|---|---|---|---|
| 80-100 | 57 | 33 | 24 | 57.9 | 42.1 |
| 60-79 | 134 | 56 | 77 | 41.8 | 57.5 |
| 40-59 | 417 | 136 | 224 | 32.6 | 53.7 |
| 20-39 | 396 | 59 | 297 | 14.9 | 75.0 |
| 0-19 | 301 | 28 | 259 | 9.3 | 86.0 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **25** (manually lowered 20 → 13 on 2026-06-24).

| Floor | Bad cut | % of bad | Good lost | % of good |
|---|---|---|---|---|
| 13 | 68 | 7.7 | 7 | 2.2 |
| 15 | 172 | 19.5 | 19 | 6.1 |
| 20 | 259 | 29.4 | 28 | 9.0 |
| 25 | 332 | 37.7 | 36 | 11.5 |
| 30 | 478 | 54.3 | 69 | 22.1 |
| 35 | 526 | 59.7 | 77 | 24.7 |
| 40 | 556 | 63.1 | 87 | 27.9 |
| 45 | 604 | 68.6 | 104 | 33.3 |
| 50 | 735 | 83.4 | 208 | 66.7 |
| 60 | 780 | 88.5 | 223 | 71.5 |

### By category

| Category | n | good | interesting | bad | % bad |
|---|---|---|---|---|---|
| news | 978 | 178 | 42 | 758 | 77.5 |
| ai-tech | 93 | 37 | 24 | 32 | 34.4 |
| wellness | 87 | 22 | 17 | 47 | 54.0 |
| local | 43 | 30 | 1 | 12 | 27.9 |
| climate | 25 | 15 | 4 | 6 | 24.0 |
| science | 18 | 15 | 1 | 2 | 11.1 |
| homelab | 17 | 4 | 7 | 6 | 35.3 |
| design | 14 | 2 | 7 | 5 | 35.7 |
| scifi | 12 | 1 | 3 | 8 | 66.7 |
| outdoors | 6 | 1 | 3 | 2 | 33.3 |
| homestead | 5 | 3 | 2 | 0 | 0.0 |
| shared | 4 | 4 | 0 | 0 | 0.0 |
| podcast-sunday | 2 | 0 | 0 | 2 | 100.0 |
| podcast-friday | 1 | 0 | 0 | 1 | 100.0 |

### Sources (≥ 5 ratings)

**Highest good-rate**

| Source | n | good | bad | % good |
|---|---|---|---|---|
| Eagle Feather News | 6 | 6 | 0 | 100.0 |
| The Narwhal | 5 | 4 | 1 | 80.0 |
| EarthSky | 5 | 4 | 1 | 80.0 |
| 100 Mile Free Press | 9 | 7 | 2 | 77.8 |
| Williams Lake Tribune | 17 | 13 | 4 | 76.5 |
| ScienceAlert | 12 | 9 | 2 | 75.0 |
| ScienceDaily | 8 | 6 | 0 | 75.0 |
| BC Gov News | 14 | 9 | 5 | 64.3 |
| New Atlas | 20 | 12 | 7 | 60.0 |
| APTN News | 10 | 6 | 3 | 60.0 |

**Highest bad-rate**

| Source | n | good | bad | % bad |
|---|---|---|---|---|
| Rolling Stone | 24 | 0 | 24 | 100.0 |
| The New Yorker | 9 | 0 | 9 | 100.0 |
| Cottage Life | 8 | 0 | 8 | 100.0 |
| Live for the Outdoors (Country Walking) | 6 | 0 | 6 | 100.0 |
| The Atlantic | 5 | 0 | 5 | 100.0 |
| Edge (GamesRadar) | 22 | 0 | 20 | 90.9 |
| Ideal Home (Country Homes & Interiors) | 22 | 0 | 20 | 90.9 |
| Lifehacker | 24 | 3 | 21 | 87.5 |
| Domino | 16 | 0 | 14 | 87.5 |
| Toms Guide | 38 | 5 | 33 | 86.8 |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 232 | 65 | 747 |
| breaking | 28 | 17 | 55 |
| analysis | 28 | 17 | 26 |
| feature | 16 | 7 | 28 |
| opinion | 1 | 2 | 12 |
| news | 4 | 3 | 7 |
| recap | 1 | 0 | 3 |
| wire | 2 | 0 | 2 |
| fluff | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 109 | 47 | 123 |
| low | 20 | 7 | 74 |
| high | 28 | 0 | 16 |
| mid | 85 | 0 | 102 |
| unknown | 4 | 0 | 3 |
| unfiltered | 66 | 57 | 563 |

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
| 2026-08-30 | 1646 | 180 | 11 |
| 2026-09-06 | 1857 | 176 | 9 |

## 3. Theme-Bucket Routing Accuracy

Of **1298** ratings tied to an aired day, you corrected the day on **257** (19.8%). Additionally 137 good articles were approved for other days.

### Per theme day

| Day | Theme | n | good | bad | % good | Corrected away |
|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 194 | 37 | 137 | 19.1 | 35 |
| tuesday | Working Lands & Industry | 195 | 34 | 148 | 17.4 | 27 |
| wednesday | Repair Culture & Practical Tech | 224 | 69 | 142 | 30.8 | 46 |
| thursday | Indigenous Lands & Innovation | 157 | 30 | 106 | 19.1 | 28 |
| friday | Wild Spaces & Outdoor Life | 235 | 51 | 160 | 21.7 | 46 |
| saturday | Cariboo Local Affairs | 161 | 49 | 106 | 30.4 | 45 |
| sunday | Science, Wonder & the Natural World | 132 | 38 | 79 | 28.8 | 30 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 9 | 7 | 1 | 5 | 4 | 9 |
| tuesday | 7 |  | 5 | 2 | 5 | 3 | 5 |
| wednesday | 4 | 7 |  | 2 | 12 | 9 | 12 |
| thursday | 1 | 4 | 6 |  | 6 | 1 | 10 |
| friday | 5 | 7 | 10 | 5 |  | 6 | 13 |
| saturday | 1 | 3 | 11 | 5 | 9 |  | 16 |
| sunday | 4 | 7 | 8 | 1 | 5 | 5 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 94 |
| Theme scorer disagreed with you (scoring miss) | 163 |
| Theme scores missing on the rating | 0 |

## 3b. Category Retag Accuracy

Of **576** ratings carrying a confirmed/retagged category, you retagged **49** (8.5%) to a different category.

### Category → category correction matrix (shown → corrected)

| Shown | Corrected to | Count |
|---|---|---|
| news | ai-tech | 15 |
| news | wellness | 6 |
| news | design | 6 |
| news | homestead | 5 |
| news | homelab | 3 |
| news | outdoors | 3 |
| news | climate | 2 |
| news | local | 2 |
| news | scifi | 2 |
| news | science | 1 |
| science | climate | 1 |
| science | wellness | 1 |
| science | news | 1 |
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
| 2026-W34 | 12 | 1510 | 81 |
| 2026-W35 | 9 | 1694 | 82 |
| 2026-W36 | 9 | 1507 | 89 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-08-23T04:43:12.336857+00:00 | 1499 | 722 | 61 | 368 | 0 |
| 2026-08-24T04:52:17.558005+00:00 | 1258 | 662 | 84 | 343 | 135 |
| 2026-08-25T04:44:57.412857+00:00 | 1567 | 970 | 95 | 551 | 190 |
| 2026-08-26T04:46:47.117660+00:00 | 1800 | 1109 | 90 | 702 | 191 |
| 2026-08-27T13:58:12.125095+00:00 | 1915 | 1114 | 92 | 714 | 183 |
| 2026-08-27T15:05:45.877374+00:00 | 1982 | 1083 | 77 | 626 | 207 |
| 2026-08-28T13:14:49.706465+00:00 | 1407 | 1035 | 97 | 640 | 168 |
| 2026-08-28T16:29:37.468548+00:00 | 1971 | 1080 | 78 | 589 | 242 |
| 2026-08-29T10:57:50.654175+00:00 | 1882 | 1054 | 80 | 603 | 197 |
| 2026-08-30T09:52:10.114082+00:00 | 1669 | 891 | 76 | 476 | 170 |
| 2026-08-30T11:17:56.653853+00:00 | 1053 | 711 | 57 | 440 | 97 |
| 2026-08-30T12:21:08.068946+00:00 | 1643 | 781 | 50 | 401 | 165 |
| 2026-08-31T10:44:00.977987+00:00 | 1479 | 726 | 93 | 367 | 153 |
| 2026-08-31T14:31:30.879532+00:00 | 1532 | 730 | 79 | 359 | 173 |
| 2026-09-01T04:01:23.708934+00:00 | 1124 | 752 | 95 | 386 | 158 |
| 2026-09-01T07:01:01.055542+00:00 | 891 | 554 | 53 | 291 | 106 |
| 2026-09-01T14:29:28.230822+00:00 | 1477 | 776 | 84 | 434 | 138 |
| 2026-09-02T04:01:04.895939+00:00 | 1723 | 1007 | 89 | 580 | 163 |
| 2026-09-03T04:01:05.181342+00:00 | 1746 | 1134 | 101 | 697 | 192 |
| 2026-09-04T04:01:04.999546+00:00 | 1864 | 1182 | 96 | 750 | 204 |
| 2026-09-05T04:01:30.153057+00:00 | 1842 | 1140 | 99 | 725 | 172 |
| 2026-09-06T04:01:09.004617+00:00 | 1414 | 847 | 92 | 511 | 136 |

### Current category feed sizes

| Feed | Items |
|---|---|
| news | 143 |
| ai-tech | 103 |
| wellness | 68 |
| homelab | 52 |
| local | 46 |
| climate | 45 |
| science | 38 |
| design | 33 |
| homestead | 10 |
| scifi | 10 |
| outdoors | 8 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 20 / 9 |
| Calibration stats runs available | 22 |
| Calibration stats range | 2026-08-23 → 2026-09-06 |
| theme_holdover_cache.json present | True |

**Context:** `calibration_stats_cache.json` was first committed on 2026-07-07, so every weekly calibration run before that found no stats and skipped — the log's repeated "Claude call or response parsing failed" lines were misleading boilerplate, not API failures. The agent's Claude path has effectively never run.

