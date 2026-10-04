# Article Review Audit

_Generated: 2026-10-04 17:30 UTC — ratings window 2026-06-17 → 2026-10-04_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 1964 |
| Rated **bad** — reached you (pipeline failed) | 531 |
| Rated **bad** — correctly rejected (pipeline worked) | 716 |
| Rated **good** | 469 (23.9%) |
| Rated **interesting** (wanted, no specific day) | 243 |
| Rated **podcast only** (for the show, not your feed) | 0 |
| Rated good or interesting (raw, quota-biased) | 36.3% |
| Reweighted good-or-interesting rate of the **shipped** feed | 43.9% (from 43.9% of shipped ratings) |
| Scrub false-negative rate (wanted articles thrown away) | 17.3% of 867 rejects |
| Theme-day corrections (`better_theme`) | 385 (19.7% of day-routed ratings) |
| …where the theme scorer already preferred your day | 160 |
| …where the theme scorer disagreed with you | 225 |
| …of those, actually routed by podcast selection | 0 |
| Category retags | 119 (9.6% of categorized ratings) |

### Sampling strata

The review feed is a **quota** sample: a fixed handful from each score band plus up to 10 scrub rejects. Rates within a stratum are unbiased; the corpus-wide rate is not, because half the ratings come from the reject pile. Reweight before comparing anything across strata.

| Stratum | n | good | interesting | podcast only | bad | % good | % good+int |
|---|---|---|---|---|---|---|---|
| unfiltered | 867 | 76 | 74 | 0 | 716 | 8.8 | 17.3 |
| mid | 408 | 150 | 42 | 0 | 216 | 36.8 | 47.1 |
| border | 358 | 124 | 67 | 0 | 167 | 34.6 | 53.4 |
| low | 125 | 22 | 8 | 0 | 95 | 17.6 | 24.0 |
| high | 96 | 63 | 11 | 0 | 21 | 65.6 | 77.1 |
| promising | 77 | 28 | 36 | 0 | 13 | 36.4 | 83.1 |
| floor_fill | 26 | 2 | 5 | 0 | 19 | 7.7 | 26.9 |
| unknown | 7 | 4 | 0 | 0 | 3 | 57.1 | 57.1 |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 469 | 54.2 | 49 | 42.0 | 42.2 |
| interesting | 243 | 45.7 | 48 | 29.9 | 27.9 |
| bad | 1250 | 36.6 | 30.0 | 20.6 | 17.9 |

### Precision by score band

| Score band | n | good | interesting | bad | % good | % good+int | % bad |
|---|---|---|---|---|---|---|---|
| 80-100 | 111 | 69 | 11 | 30 | 62.2 | 72.1 | 27.0 |
| 60-79 | 319 | 114 | 37 | 168 | 35.7 | 47.3 | 52.7 |
| 40-59 | 635 | 187 | 119 | 329 | 29.4 | 48.2 | 51.8 |
| 20-39 | 519 | 68 | 55 | 396 | 13.1 | 23.7 | 76.3 |
| 0-19 | 380 | 31 | 21 | 327 | 8.2 | 13.7 | 86.1 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **25** (manually lowered 20 → 13 on 2026-06-24).

`interesting` articles score low on relevance, so a higher floor costs them first. Weigh **% of bad cut** against **% of good+int lost**.

| Floor | Bad cut | % of bad | Good lost | % of good | Interesting lost | % of int | % of good+int |
|---|---|---|---|---|---|---|---|
| 13 | 68 | 5.4 | 7 | 1.5 | 2 | 0.8 | 1.3 |
| 15 | 181 | 14.5 | 19 | 4.1 | 9 | 3.7 | 3.9 |
| 20 | 327 | 26.2 | 31 | 6.6 | 21 | 8.6 | 7.3 |
| 25 | 423 | 33.8 | 41 | 8.7 | 31 | 12.8 | 10.1 |
| 30 | 621 | 49.7 | 78 | 16.6 | 56 | 23.0 | 18.8 |
| 35 | 684 | 54.7 | 89 | 19.0 | 70 | 28.8 | 22.3 |
| 40 | 723 | 57.8 | 99 | 21.1 | 76 | 31.3 | 24.6 |
| 45 | 790 | 63.2 | 123 | 26.2 | 86 | 35.4 | 29.4 |
| 50 | 996 | 79.7 | 268 | 57.1 | 189 | 77.8 | 64.2 |
| 60 | 1052 | 84.2 | 286 | 61.0 | 195 | 80.2 | 67.6 |

### By category

| Category | n | good | interesting | bad | % good+int | % bad |
|---|---|---|---|---|---|---|
| news | 1325 | 204 | 82 | 1039 | 21.6 | 78.4 |
| ai-tech | 187 | 53 | 71 | 63 | 66.3 | 33.7 |
| wellness | 133 | 42 | 23 | 67 | 48.9 | 50.4 |
| local | 110 | 71 | 11 | 27 | 74.5 | 24.5 |
| climate | 48 | 30 | 7 | 11 | 77.1 | 22.9 |
| science | 45 | 36 | 6 | 3 | 93.3 | 6.7 |
| homelab | 35 | 13 | 13 | 9 | 74.3 | 25.7 |
| design | 28 | 2 | 13 | 13 | 53.6 | 46.4 |
| scifi | 20 | 1 | 8 | 11 | 45.0 | 55.0 |
| outdoors | 14 | 5 | 5 | 4 | 71.4 | 28.6 |
| homestead | 12 | 8 | 4 | 0 | 100.0 | 0.0 |
| shared | 4 | 4 | 0 | 0 | 100.0 | 0.0 |
| podcast-sunday | 2 | 0 | 0 | 2 | 0.0 | 100.0 |
| podcast-friday | 1 | 0 | 0 | 1 | 0.0 | 100.0 |

### Sources (≥ 5 ratings)

**Highest good+interesting rate**

| Source | n | good | interesting | bad | % good+int |
|---|---|---|---|---|---|
| Eagle Feather News | 6 | 6 | 0 | 0 | 100.0 |
| ScienceDaily | 19 | 14 | 4 | 1 | 94.7 |
| ScienceAlert | 18 | 15 | 1 | 2 | 88.9 |
| EarthSky | 6 | 5 | 0 | 1 | 83.3 |
| Bicycling | 6 | 3 | 2 | 1 | 83.3 |
| Scientific American | 16 | 7 | 6 | 3 | 81.2 |
| The Narwhal | 5 | 4 | 0 | 1 | 80.0 |
| 100 Mile Free Press | 17 | 12 | 1 | 4 | 76.5 |
| Williams Lake Tribune | 40 | 27 | 3 | 9 | 75.0 |
| APTN News | 12 | 7 | 2 | 3 | 75.0 |

**Lowest good+interesting rate** — block candidate only at n ≥ 8 with zero positives of any kind

| Source | n | good | interesting | bad | % good+int | Block candidate |
|---|---|---|---|---|---|---|
| Rolling Stone | 24 | 0 | 0 | 24 | 0.0 | yes |
| Mother Jones | 19 | 0 | 0 | 19 | 0.0 | yes |
| The New Yorker | 9 | 0 | 0 | 9 | 0.0 | yes |
| Cottage Life | 8 | 0 | 0 | 8 | 0.0 | yes |
| Live for the Outdoors (Country Walking) | 7 | 0 | 0 | 7 | 0.0 |  |
| FlowingData | 5 | 0 | 0 | 5 | 0.0 |  |
| ArchDaily | 5 | 0 | 0 | 5 | 0.0 |  |
| Country Guide | 5 | 0 | 0 | 5 | 0.0 |  |
| Edge (GamesRadar) | 41 | 0 | 2 | 39 | 4.9 |  |
| Ideal Home (Country Homes & Interiors) | 31 | 0 | 3 | 28 | 9.7 |  |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 296 | 131 | 1033 |
| breaking | 59 | 34 | 79 |
| analysis | 53 | 40 | 48 |
| feature | 37 | 22 | 48 |
| news | 13 | 8 | 16 |
| opinion | 5 | 4 | 18 |
| recap | 1 | 1 | 4 |
| wire | 3 | 1 | 2 |
| fluff | 2 | 1 | 1 |
| investigation | 0 | 1 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 124 | 67 | 167 |
| low | 22 | 8 | 95 |
| high | 63 | 11 | 21 |
| mid | 150 | 42 | 216 |
| unknown | 4 | 0 | 3 |
| unfiltered | 76 | 74 | 716 |
| floor_fill | 2 | 5 | 19 |
| promising | 28 | 36 | 13 |

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
| 2026-09-13 | 1377 | 124 | 9 |
| 2026-09-20 | 1397 | 147 | 11 |
| 2026-09-27 | 1469 | 182 | 12 |
| 2026-10-04 | 1340 | 162 | 12 |

## 3. Theme-Bucket Routing Accuracy

Of **1957** ratings tied to an aired day, you corrected the day on **385** (19.7%). Additionally 280 articles were approved for other days.

### Per theme day

`% day fit` counts good + podcast only (the verdicts that name days). `% good+int` is feed fit: wanted in your feed, any day or none.

| Day | Theme | n | good | interesting | podcast only | bad | % day fit | % good+int | Corrected away |
|---|---|---|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 311 | 61 | 48 | 0 | 202 | 19.6 | 35.0 | 52 |
| tuesday | Working Lands & Industry | 282 | 58 | 26 | 0 | 198 | 20.6 | 29.8 | 44 |
| wednesday | Repair Culture & Practical Tech | 341 | 97 | 36 | 0 | 208 | 28.4 | 39.0 | 70 |
| thursday | Indigenous Lands & Innovation | 270 | 55 | 44 | 0 | 171 | 20.4 | 36.7 | 52 |
| friday | Wild Spaces & Outdoor Life | 319 | 77 | 40 | 0 | 201 | 24.1 | 36.7 | 70 |
| saturday | Cariboo Local Affairs | 245 | 71 | 24 | 0 | 150 | 29.0 | 38.8 | 62 |
| sunday | Science, Wonder & the Natural World | 189 | 46 | 25 | 0 | 117 | 24.3 | 37.6 | 35 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 13 | 11 | 1 | 6 | 7 | 14 |
| tuesday | 10 |  | 7 | 2 | 6 | 5 | 14 |
| wednesday | 8 | 13 |  | 3 | 16 | 14 | 16 |
| thursday | 3 | 10 | 8 |  | 7 | 4 | 20 |
| friday | 7 | 13 | 14 | 5 |  | 11 | 20 |
| saturday | 2 | 6 | 12 | 7 | 10 |  | 25 |
| sunday | 4 | 9 | 10 | 1 | 6 | 5 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 160 |
| Theme scorer disagreed with you (scoring miss) | 225 |
| Theme scores missing on the rating | 0 |

## 3b. Category Retag Accuracy

Of **1235** ratings carrying a confirmed/retagged category, you retagged **119** (9.6%) to a different category.

### Category → category correction matrix (shown → corrected)

| Shown | Corrected to | Count |
|---|---|---|
| news | ai-tech | 34 |
| news | homelab | 13 |
| news | science | 10 |
| news | wellness | 8 |
| news | outdoors | 8 |
| news | homestead | 8 |
| news | climate | 6 |
| news | scifi | 6 |
| news | design | 6 |
| news | local | 5 |
| science | wellness | 3 |
| science | climate | 1 |
| science | news | 1 |
| design | homelab | 1 |
| local | news | 1 |
| local | climate | 1 |
| local | wellness | 1 |
| local | ai-tech | 1 |
| wellness | climate | 1 |
| wellness | ai-tech | 1 |
| wellness | news | 1 |
| wellness | science | 1 |
| ai-tech | scifi | 1 |

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
| 2026-W36 | 10 | 1469 | 88 |
| 2026-W37 | 7 | 1557 | 93 |
| 2026-W38 | 7 | 1635 | 95 |
| 2026-W39 | 8 | 1363 | 74 |
| 2026-W40 | 6 | 1450 | 82 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-09-21T04:00:37.666981+00:00 | 1156 | 596 | 79 | 415 | 67 |
| 2026-09-22T04:00:45.058198+00:00 | 1533 | 960 | 96 | 700 | 117 |
| 2026-09-23T04:00:36.238364+00:00 | 1584 | 1211 | 88 | 840 | 214 |
| 2026-09-24T04:01:46.118750+00:00 | 1550 | 1172 | 72 | 809 | 240 |
| 2026-09-24T04:28:37.248975+00:00 | 1026 | 742 | 49 | 492 | 172 |
| 2026-09-25T04:01:06.669897+00:00 | 1596 | 1194 | 77 | 831 | 230 |
| 2026-09-26T04:00:58.760213+00:00 | 1616 | 1190 | 80 | 771 | 265 |
| 2026-09-27T04:00:59.519081+00:00 | 1234 | 934 | 67 | 596 | 209 |
| 2026-09-28T04:01:26.045743+00:00 | 762 | 579 | 63 | 355 | 123 |
| 2026-09-29T04:00:55.720608+00:00 | 1131 | 911 | 84 | 602 | 174 |
| 2026-09-30T04:01:13.201271+00:00 | 1601 | 1230 | 84 | 802 | 285 |
| 2026-10-01T04:01:33.771128+00:00 | 1614 | 1274 | 89 | 827 | 286 |
| 2026-10-02T04:01:10.254540+00:00 | 1610 | 1253 | 83 | 801 | 294 |
| 2026-10-03T04:01:16.901145+00:00 | 1598 | 1213 | 83 | 758 | 273 |
| 2026-10-04T04:01:10.284230+00:00 | 1144 | 867 | 70 | 524 | 209 |

### Current category feed sizes

| Feed | Items |
|---|---|
| ai-tech | 87 |
| news | 65 |
| wellness | 53 |
| science | 40 |
| climate | 39 |
| homelab | 36 |
| local | 34 |
| design | 27 |
| homestead | 9 |
| scifi | 8 |
| outdoors | 4 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 24 / 9 |
| Calibration stats runs available | 15 |
| Calibration stats range | 2026-09-21 → 2026-10-04 |
| theme_holdover_cache.json present | True |

**Context:** `calibration_stats_cache.json` was first committed on 2026-07-07, so every weekly calibration run before that found no stats and skipped — the log's repeated "Claude call or response parsing failed" lines were misleading boilerplate, not API failures. The agent's Claude path has effectively never run.

