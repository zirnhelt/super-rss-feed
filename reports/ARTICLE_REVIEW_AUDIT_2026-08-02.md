# Article Review Audit

_Generated: 2026-08-02 14:45 UTC — ratings window 2026-06-17 → 2026-08-02_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 842 |
| Rated **bad** (fluff/noise that reached you) | 545 (64.7%) |
| Rated **good** | 264 (31.4%) |
| Rated **interesting** | 33 |
| Theme-day corrections (`better_theme`) | 220 (26.3% of day-routed ratings) |
| …caused by selection ignoring its own theme scores | 80 |
| …caused by the theme scorer itself missing | 140 |
| Category retags | 15 (13.3% of categorized ratings) |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 264 | 50.8 | 48.0 | 46.0 | 45.8 |
| interesting | 33 | 40.6 | 48 | 43.6 | 37.1 |
| bad | 545 | 36.6 | 29 | 33.5 | 30.5 |

### Precision by score band

| Score band | n | good | bad | % good | % bad |
|---|---|---|---|---|---|
| 80-100 | 56 | 32 | 24 | 57.1 | 42.9 |
| 60-79 | 129 | 55 | 74 | 42.6 | 57.4 |
| 40-59 | 268 | 107 | 138 | 39.9 | 51.5 |
| 20-39 | 182 | 44 | 131 | 24.2 | 72.0 |
| 0-19 | 207 | 26 | 178 | 12.6 | 86.0 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **20** (manually lowered 20 → 13 on 2026-06-24).

| Floor | Bad cut | % of bad | Good lost | % of good |
|---|---|---|---|---|
| 13 | 68 | 12.5 | 7 | 2.7 |
| 15 | 139 | 25.5 | 18 | 6.8 |
| 20 | 178 | 32.7 | 26 | 9.8 |
| 25 | 197 | 36.1 | 30 | 11.4 |
| 30 | 274 | 50.3 | 54 | 20.5 |
| 35 | 291 | 53.4 | 60 | 22.7 |
| 40 | 309 | 56.7 | 70 | 26.5 |
| 45 | 339 | 62.2 | 87 | 33.0 |
| 50 | 408 | 74.9 | 163 | 61.7 |
| 60 | 447 | 82.0 | 177 | 67.0 |

### By category

| Category | n | good | interesting | bad | % bad |
|---|---|---|---|---|---|
| news | 644 | 163 | 16 | 465 | 72.2 |
| ai-tech | 63 | 28 | 10 | 25 | 39.7 |
| wellness | 45 | 16 | 3 | 26 | 57.8 |
| local | 38 | 29 | 0 | 9 | 23.7 |
| climate | 19 | 10 | 3 | 6 | 31.6 |
| science | 13 | 12 | 0 | 1 | 7.7 |
| scifi | 7 | 0 | 0 | 7 | 100.0 |
| homelab | 6 | 2 | 1 | 3 | 50.0 |
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
| ScienceAlert | 7 | 6 | 1 | 85.7 |
| BC Gov News | 10 | 8 | 2 | 80.0 |
| The Narwhal | 5 | 4 | 1 | 80.0 |
| Williams Lake Tribune | 17 | 13 | 4 | 76.5 |
| New Atlas | 16 | 10 | 5 | 62.5 |
| MakeUseOf | 5 | 3 | 2 | 60.0 |
| Cool Tools | 5 | 3 | 2 | 60.0 |

**Highest bad-rate**

| Source | n | good | bad | % bad |
|---|---|---|---|---|
| Neowin | 13 | 1 | 12 | 92.3 |
| Reactor Magazine | 10 | 1 | 9 | 90.0 |
| Al Jazeera English | 31 | 4 | 27 | 87.1 |
| Toms Guide | 31 | 4 | 27 | 87.1 |
| NPR Health News | 7 | 1 | 6 | 85.7 |
| Lifehacker | 20 | 3 | 17 | 85.0 |
| Quartz | 18 | 3 | 15 | 83.3 |
| CBC Arts | 12 | 2 | 10 | 83.3 |
| Kottke.org | 12 | 2 | 10 | 83.3 |
| NYT Business | 25 | 4 | 20 | 80.0 |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 207 | 15 | 454 |
| breaking | 19 | 9 | 43 |
| feature | 14 | 1 | 19 |
| analysis | 17 | 7 | 10 |
| opinion | 0 | 1 | 9 |
| news | 4 | 0 | 6 |
| wire | 2 | 0 | 2 |
| recap | 1 | 0 | 1 |
| fluff | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 81 | 18 | 69 |
| low | 14 | 0 | 44 |
| high | 28 | 0 | 16 |
| mid | 85 | 0 | 102 |
| unknown | 4 | 0 | 3 |
| unfiltered | 52 | 15 | 311 |

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

## 3. Theme-Bucket Routing Accuracy

Of **835** ratings tied to an aired day, you corrected the day on **220** (26.3%). Additionally 98 good articles were approved for other days.

### Per theme day

| Day | Theme | n | good | bad | % good | Corrected away |
|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 109 | 29 | 75 | 26.6 | 28 |
| tuesday | Working Lands & Industry | 106 | 30 | 75 | 28.3 | 25 |
| wednesday | Repair Culture & Practical Tech | 161 | 66 | 91 | 41.0 | 44 |
| thursday | Indigenous Lands & Innovation | 98 | 23 | 68 | 23.5 | 22 |
| friday | Wild Spaces & Outdoor Life | 162 | 43 | 109 | 26.5 | 40 |
| saturday | Cariboo Local Affairs | 115 | 40 | 72 | 34.8 | 37 |
| sunday | Science, Wonder & the Natural World | 84 | 29 | 52 | 34.5 | 24 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 7 | 6 | 1 | 4 | 3 | 7 |
| tuesday | 7 |  | 5 | 2 | 3 | 3 | 5 |
| wednesday | 4 | 7 |  | 2 | 11 | 9 | 11 |
| thursday | 1 | 4 | 5 |  | 6 |  | 6 |
| friday | 3 | 6 | 9 | 5 |  | 6 | 11 |
| saturday |  | 3 | 8 | 5 | 7 |  | 14 |
| sunday | 2 | 5 | 7 | 1 | 5 | 4 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 80 |
| Theme scorer disagreed with you (scoring miss) | 140 |
| Theme scores missing on the rating | 0 |

## 3b. Category Retag Accuracy

Of **113** ratings carrying a confirmed/retagged category, you retagged **15** (13.3%) to a different category.

### Category → category correction matrix (shown → corrected)

| Shown | Corrected to | Count |
|---|---|---|
| news | ai-tech | 7 |
| news | wellness | 3 |
| news | climate | 1 |
| news | science | 1 |
| news | homelab | 1 |
| news | local | 1 |
| science | climate | 1 |

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

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-07-20T06:54:16.599439+00:00 | 809 | 386 | 55 | 38 | 19 |
| 2026-07-21T06:34:55.714447+00:00 | 941 | 554 | 71 | 78 | 33 |
| 2026-07-22T06:35:25.137439+00:00 | 1128 | 675 | 81 | 116 | 26 |
| 2026-07-23T06:34:57.460147+00:00 | 1179 | 694 | 77 | 99 | 38 |
| 2026-07-24T06:32:08.133283+00:00 | 1151 | 674 | 70 | 111 | 28 |
| 2026-07-25T06:23:48.943095+00:00 | 1157 | 696 | 80 | 129 | 25 |
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

### Current category feed sizes

| Feed | Items |
|---|---|
| news | 150 |
| ai-tech | 76 |
| wellness | 54 |
| science | 39 |
| local | 29 |
| climate | 28 |
| homelab | 17 |
| scifi | 1 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 14 / 8 |
| Calibration stats runs available | 16 |
| Calibration stats range | 2026-07-20 → 2026-08-02 |
| theme_holdover_cache.json present | False |

**Context:** `calibration_stats_cache.json` was first committed on 2026-07-07, so every weekly calibration run before that found no stats and skipped — the log's repeated "Claude call or response parsing failed" lines were misleading boilerplate, not API failures. The agent's Claude path has effectively never run.

