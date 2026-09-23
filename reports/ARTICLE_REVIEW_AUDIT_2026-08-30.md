# Article Review Audit

_Generated: 2026-08-30 17:17 UTC — ratings window 2026-06-17 → 2026-08-28_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 1201 |
| Rated **bad** (fluff/noise that reached you) | 795 (66.2%) |
| Rated **good** | 303 (25.2%) |
| Rated **interesting** | 102 |
| Theme-day corrections (`better_theme`) | 249 (20.9% of day-routed ratings) |
| …caused by selection ignoring its own theme scores | 91 |
| …caused by the theme scorer itself missing | 158 |
| Category retags | 46 (9.7% of categorized ratings) |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 303 | 49.6 | 49 | 43.7 | 43.0 |
| interesting | 102 | 37.2 | 46.0 | 29.5 | 24.6 |
| bad | 795 | 34.4 | 29 | 25.2 | 22.3 |

### Precision by score band

| Score band | n | good | bad | % good | % bad |
|---|---|---|---|---|---|
| 80-100 | 57 | 33 | 24 | 57.9 | 42.1 |
| 60-79 | 132 | 56 | 75 | 42.4 | 56.8 |
| 40-59 | 381 | 129 | 199 | 33.9 | 52.2 |
| 20-39 | 351 | 58 | 258 | 16.5 | 73.5 |
| 0-19 | 280 | 27 | 239 | 9.6 | 85.4 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **23** (manually lowered 20 → 13 on 2026-06-24).

| Floor | Bad cut | % of bad | Good lost | % of good |
|---|---|---|---|---|
| 13 | 68 | 8.6 | 7 | 2.3 |
| 15 | 161 | 20.3 | 18 | 5.9 |
| 20 | 239 | 30.1 | 27 | 8.9 |
| 25 | 298 | 37.5 | 35 | 11.6 |
| 30 | 427 | 53.7 | 67 | 22.1 |
| 35 | 468 | 58.9 | 75 | 24.8 |
| 40 | 497 | 62.5 | 85 | 28.1 |
| 45 | 541 | 68.1 | 102 | 33.7 |
| 50 | 653 | 82.1 | 200 | 66.0 |
| 60 | 696 | 87.5 | 214 | 70.6 |

### By category

| Category | n | good | interesting | bad | % bad |
|---|---|---|---|---|---|
| news | 893 | 176 | 38 | 679 | 76.0 |
| ai-tech | 87 | 35 | 21 | 31 | 35.6 |
| wellness | 84 | 21 | 16 | 46 | 54.8 |
| local | 41 | 30 | 1 | 10 | 24.4 |
| climate | 23 | 13 | 4 | 6 | 26.1 |
| science | 18 | 15 | 1 | 2 | 11.1 |
| homelab | 15 | 3 | 7 | 5 | 33.3 |
| scifi | 12 | 1 | 3 | 8 | 66.7 |
| design | 12 | 1 | 7 | 4 | 33.3 |
| homestead | 5 | 3 | 2 | 0 | 0.0 |
| shared | 4 | 4 | 0 | 0 | 0.0 |
| outdoors | 4 | 1 | 2 | 1 | 25.0 |
| podcast-sunday | 2 | 0 | 0 | 2 | 100.0 |
| podcast-friday | 1 | 0 | 0 | 1 | 100.0 |

### Sources (≥ 5 ratings)

**Highest good-rate**

| Source | n | good | bad | % good |
|---|---|---|---|---|
| Eagle Feather News | 6 | 6 | 0 | 100.0 |
| 100 Mile Free Press | 8 | 7 | 1 | 87.5 |
| ScienceAlert | 11 | 9 | 1 | 81.8 |
| The Narwhal | 5 | 4 | 1 | 80.0 |
| EarthSky | 5 | 4 | 1 | 80.0 |
| Williams Lake Tribune | 17 | 13 | 4 | 76.5 |
| ScienceDaily | 8 | 6 | 0 | 75.0 |
| BC Gov News | 14 | 9 | 5 | 64.3 |
| APTN News | 10 | 6 | 3 | 60.0 |
| MakeUseOf | 5 | 3 | 2 | 60.0 |

**Highest bad-rate**

| Source | n | good | bad | % bad |
|---|---|---|---|---|
| Rolling Stone | 18 | 0 | 18 | 100.0 |
| The New Yorker | 7 | 0 | 7 | 100.0 |
| Domino | 11 | 0 | 10 | 90.9 |
| Edge (GamesRadar) | 16 | 0 | 14 | 87.5 |
| Lifehacker | 23 | 3 | 20 | 87.0 |
| Neowin | 15 | 2 | 13 | 86.7 |
| Ideal Home (Country Homes & Interiors) | 15 | 0 | 13 | 86.7 |
| Toms Guide | 37 | 5 | 32 | 86.5 |
| Maclean's | 7 | 1 | 6 | 85.7 |
| CBC Arts | 13 | 2 | 11 | 84.6 |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 229 | 60 | 674 |
| breaking | 25 | 16 | 52 |
| analysis | 26 | 15 | 20 |
| feature | 15 | 7 | 26 |
| news | 4 | 3 | 7 |
| opinion | 1 | 1 | 11 |
| wire | 2 | 0 | 2 |
| recap | 1 | 0 | 2 |
| fluff | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 103 | 44 | 106 |
| low | 19 | 5 | 69 |
| high | 28 | 0 | 16 |
| mid | 85 | 0 | 102 |
| unknown | 4 | 0 | 3 |
| unfiltered | 64 | 53 | 499 |

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

## 3. Theme-Bucket Routing Accuracy

Of **1194** ratings tied to an aired day, you corrected the day on **249** (20.9%). Additionally 129 good articles were approved for other days.

### Per theme day

| Day | Theme | n | good | bad | % good | Corrected away |
|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 180 | 36 | 128 | 20.0 | 34 |
| tuesday | Working Lands & Industry | 165 | 34 | 121 | 20.6 | 27 |
| wednesday | Repair Culture & Practical Tech | 209 | 69 | 127 | 33.0 | 46 |
| thursday | Indigenous Lands & Innovation | 142 | 30 | 93 | 21.1 | 28 |
| friday | Wild Spaces & Outdoor Life | 220 | 49 | 147 | 22.3 | 44 |
| saturday | Cariboo Local Affairs | 146 | 43 | 97 | 29.5 | 40 |
| sunday | Science, Wonder & the Natural World | 132 | 38 | 79 | 28.8 | 30 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 8 | 7 | 1 | 5 | 4 | 9 |
| tuesday | 7 |  | 5 | 2 | 5 | 3 | 5 |
| wednesday | 4 | 7 |  | 2 | 12 | 9 | 12 |
| thursday | 1 | 4 | 6 |  | 6 | 1 | 10 |
| friday | 4 | 7 | 9 | 5 |  | 6 | 13 |
| saturday |  | 3 | 9 | 5 | 8 |  | 15 |
| sunday | 4 | 7 | 8 | 1 | 5 | 5 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 91 |
| Theme scorer disagreed with you (scoring miss) | 158 |
| Theme scores missing on the rating | 0 |

## 3b. Category Retag Accuracy

Of **472** ratings carrying a confirmed/retagged category, you retagged **46** (9.7%) to a different category.

### Category → category correction matrix (shown → corrected)

| Shown | Corrected to | Count |
|---|---|---|
| news | ai-tech | 15 |
| news | wellness | 6 |
| news | design | 5 |
| news | homestead | 5 |
| news | homelab | 3 |
| news | climate | 2 |
| news | local | 2 |
| news | scifi | 2 |
| news | outdoors | 2 |
| news | science | 1 |
| science | climate | 1 |
| science | wellness | 1 |
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

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
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

### Current category feed sizes

| Feed | Items |
|---|---|
| news | 220 |
| ai-tech | 120 |
| wellness | 85 |
| science | 49 |
| design | 42 |
| homelab | 42 |
| local | 40 |
| climate | 37 |
| outdoors | 17 |
| scifi | 14 |
| homestead | 10 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 19 / 9 |
| Calibration stats runs available | 23 |
| Calibration stats range | 2026-08-17 → 2026-08-30 |
| theme_holdover_cache.json present | True |

**Context:** `calibration_stats_cache.json` was first committed on 2026-07-07, so every weekly calibration run before that found no stats and skipped — the log's repeated "Claude call or response parsing failed" lines were misleading boilerplate, not API failures. The agent's Claude path has effectively never run.

