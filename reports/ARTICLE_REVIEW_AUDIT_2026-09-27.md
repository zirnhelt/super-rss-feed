# Article Review Audit

_Generated: 2026-09-27 17:46 UTC — ratings window 2026-06-17 → 2026-09-27_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 1775 |
| Rated **bad** — reached you (pipeline failed) | 482 |
| Rated **bad** — correctly rejected (pipeline worked) | 684 |
| Rated **good** | 416 (23.4%) |
| Rated **interesting** (wanted, no specific day) | 189 |
| Rated good or interesting (raw, quota-biased) | 34.1% |
| Reweighted good-or-interesting rate of the **shipped** feed | 41.9% (from 34.7% of shipped ratings) |
| Scrub false-negative rate (wanted articles thrown away) | 17.7% of 832 rejects |
| Theme-day corrections (`better_theme`) | 344 (19.5% of day-routed ratings) |
| …where the theme scorer already preferred your day | 143 |
| …where the theme scorer disagreed with you | 201 |
| …of those, actually routed by podcast selection | 0 |
| Category retags | 112 (10.7% of categorized ratings) |

### Sampling strata

The review feed is a **quota** sample: a fixed handful from each score band plus up to 10 scrub rejects. Rates within a stratum are unbiased; the corpus-wide rate is not, because half the ratings come from the reject pile. Reweight before comparing anything across strata.

| Stratum | n | good | interesting | bad | % good | % good+int |
|---|---|---|---|---|---|---|
| unfiltered | 832 | 75 | 72 | 684 | 9.0 | 17.7 |
| mid | 362 | 132 | 29 | 201 | 36.5 | 44.5 |
| border | 337 | 122 | 60 | 155 | 36.2 | 54.0 |
| low | 118 | 22 | 8 | 88 | 18.6 | 25.4 |
| high | 77 | 50 | 6 | 21 | 64.9 | 72.7 |
| promising | 23 | 10 | 10 | 3 | 43.5 | 87.0 |
| floor_fill | 19 | 1 | 4 | 14 | 5.3 | 26.3 |
| unknown | 7 | 4 | 0 | 3 | 57.1 | 57.1 |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 416 | 52.8 | 49.0 | 41.3 | 41.1 |
| interesting | 189 | 43.1 | 48 | 28.4 | 25.1 |
| bad | 1169 | 36.2 | 29 | 21.0 | 18.2 |

### Precision by score band

| Score band | n | good | interesting | bad | % good | % good+int | % bad |
|---|---|---|---|---|---|---|---|
| 80-100 | 92 | 56 | 6 | 30 | 60.9 | 67.4 | 32.6 |
| 60-79 | 272 | 96 | 24 | 152 | 35.3 | 44.1 | 55.9 |
| 40-59 | 552 | 167 | 86 | 299 | 30.3 | 45.8 | 54.2 |
| 20-39 | 493 | 67 | 54 | 372 | 13.6 | 24.5 | 75.5 |
| 0-19 | 366 | 30 | 19 | 316 | 8.2 | 13.4 | 86.3 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **25** (manually lowered 20 → 13 on 2026-06-24).

`interesting` articles score low on relevance, so a higher floor costs them first. Weigh **% of bad cut** against **% of good+int lost**.

| Floor | Bad cut | % of bad | Good lost | % of good | Interesting lost | % of int | % of good+int |
|---|---|---|---|---|---|---|---|
| 13 | 68 | 5.8 | 7 | 1.7 | 2 | 1.1 | 1.5 |
| 15 | 178 | 15.2 | 19 | 4.6 | 9 | 4.8 | 4.6 |
| 20 | 316 | 27.0 | 30 | 7.2 | 19 | 10.1 | 8.1 |
| 25 | 409 | 35.0 | 39 | 9.4 | 29 | 15.3 | 11.2 |
| 30 | 594 | 50.8 | 76 | 18.3 | 54 | 28.6 | 21.5 |
| 35 | 653 | 55.9 | 87 | 20.9 | 68 | 36.0 | 25.6 |
| 40 | 688 | 58.9 | 97 | 23.3 | 73 | 38.6 | 28.1 |
| 45 | 750 | 64.2 | 119 | 28.6 | 81 | 42.9 | 33.1 |
| 50 | 934 | 79.9 | 246 | 59.1 | 153 | 81.0 | 66.0 |
| 60 | 987 | 84.4 | 264 | 63.5 | 159 | 84.1 | 69.9 |

### By category

| Category | n | good | interesting | bad | % good+int | % bad |
|---|---|---|---|---|---|---|
| news | 1240 | 193 | 62 | 985 | 20.6 | 79.4 |
| ai-tech | 160 | 49 | 53 | 58 | 63.8 | 36.2 |
| wellness | 116 | 36 | 21 | 58 | 49.1 | 50.0 |
| local | 85 | 55 | 6 | 24 | 71.8 | 28.2 |
| climate | 40 | 26 | 5 | 9 | 77.5 | 22.5 |
| science | 38 | 30 | 5 | 3 | 92.1 | 7.9 |
| homelab | 29 | 10 | 11 | 8 | 72.4 | 27.6 |
| design | 22 | 2 | 11 | 9 | 59.1 | 40.9 |
| scifi | 19 | 1 | 8 | 10 | 47.4 | 52.6 |
| outdoors | 12 | 5 | 5 | 2 | 83.3 | 16.7 |
| homestead | 7 | 5 | 2 | 0 | 100.0 | 0.0 |
| shared | 4 | 4 | 0 | 0 | 100.0 | 0.0 |
| podcast-sunday | 2 | 0 | 0 | 2 | 0.0 | 100.0 |
| podcast-friday | 1 | 0 | 0 | 1 | 0.0 | 100.0 |

### Sources (≥ 5 ratings)

**Highest good+interesting rate**

| Source | n | good | interesting | bad | % good+int |
|---|---|---|---|---|---|
| Eagle Feather News | 6 | 6 | 0 | 0 | 100.0 |
| ScienceDaily | 15 | 11 | 3 | 1 | 93.3 |
| Scientific American | 13 | 7 | 5 | 1 | 92.3 |
| ScienceAlert | 15 | 12 | 1 | 2 | 86.7 |
| Bicycling | 6 | 3 | 2 | 1 | 83.3 |
| The Narwhal | 5 | 4 | 0 | 1 | 80.0 |
| EarthSky | 5 | 4 | 0 | 1 | 80.0 |
| 100 Mile Free Press | 12 | 9 | 0 | 3 | 75.0 |
| Williams Lake Tribune | 33 | 22 | 2 | 9 | 72.7 |
| APTN News | 11 | 7 | 1 | 3 | 72.7 |

**Lowest good+interesting rate** — block candidate only at n ≥ 8 with zero positives of any kind

| Source | n | good | interesting | bad | % good+int | Block candidate |
|---|---|---|---|---|---|---|
| Rolling Stone | 24 | 0 | 0 | 24 | 0.0 | yes |
| Mother Jones | 15 | 0 | 0 | 15 | 0.0 | yes |
| The New Yorker | 9 | 0 | 0 | 9 | 0.0 | yes |
| Cottage Life | 8 | 0 | 0 | 8 | 0.0 | yes |
| Live for the Outdoors (Country Walking) | 7 | 0 | 0 | 7 | 0.0 |  |
| FlowingData | 5 | 0 | 0 | 5 | 0.0 |  |
| Country Guide | 5 | 0 | 0 | 5 | 0.0 |  |
| Edge (GamesRadar) | 38 | 0 | 2 | 36 | 5.3 |  |
| Ideal Home (Country Homes & Interiors) | 31 | 0 | 3 | 28 | 9.7 |  |
| Lifehacker | 27 | 3 | 0 | 24 | 11.1 |  |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 280 | 109 | 972 |
| breaking | 49 | 26 | 76 |
| analysis | 42 | 28 | 38 |
| feature | 26 | 15 | 44 |
| news | 10 | 6 | 15 |
| opinion | 4 | 4 | 17 |
| recap | 1 | 0 | 3 |
| wire | 2 | 0 | 2 |
| fluff | 2 | 0 | 1 |
| investigation | 0 | 1 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 122 | 60 | 155 |
| low | 22 | 8 | 88 |
| high | 50 | 6 | 21 |
| mid | 132 | 29 | 201 |
| unknown | 4 | 0 | 3 |
| unfiltered | 75 | 72 | 684 |
| floor_fill | 1 | 4 | 14 |
| promising | 10 | 10 | 3 |

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

## 3. Theme-Bucket Routing Accuracy

Of **1768** ratings tied to an aired day, you corrected the day on **344** (19.5%). Additionally 231 good articles were approved for other days.

### Per theme day

`% good` is day fit. `% good+int` adds articles wanted for any day with no specific fit.

| Day | Theme | n | good | interesting | bad | % good | % good+int | Corrected away |
|---|---|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 284 | 52 | 42 | 190 | 18.3 | 33.1 | 49 |
| tuesday | Working Lands & Industry | 255 | 47 | 21 | 187 | 18.4 | 26.7 | 35 |
| wednesday | Repair Culture & Practical Tech | 314 | 88 | 25 | 201 | 28.0 | 36.0 | 61 |
| thursday | Indigenous Lands & Innovation | 243 | 48 | 38 | 157 | 19.8 | 35.4 | 46 |
| friday | Wild Spaces & Outdoor Life | 292 | 68 | 33 | 190 | 23.3 | 34.6 | 62 |
| saturday | Cariboo Local Affairs | 218 | 65 | 15 | 138 | 29.8 | 36.7 | 58 |
| sunday | Science, Wonder & the Natural World | 162 | 44 | 15 | 103 | 27.2 | 36.4 | 33 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 13 | 9 | 1 | 6 | 7 | 13 |
| tuesday | 10 |  | 6 | 2 | 6 | 3 | 8 |
| wednesday | 8 | 10 |  | 3 | 15 | 11 | 14 |
| thursday | 3 | 7 | 7 |  | 7 | 3 | 19 |
| friday | 7 | 13 | 12 | 5 |  | 8 | 17 |
| saturday | 2 | 5 | 12 | 6 | 10 |  | 23 |
| sunday | 4 | 9 | 9 | 1 | 5 | 5 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 143 |
| Theme scorer disagreed with you (scoring miss) | 201 |
| Theme scores missing on the rating | 0 |

## 3b. Category Retag Accuracy

Of **1046** ratings carrying a confirmed/retagged category, you retagged **112** (10.7%) to a different category.

### Category → category correction matrix (shown → corrected)

| Shown | Corrected to | Count |
|---|---|---|
| news | ai-tech | 32 |
| news | homelab | 12 |
| news | science | 9 |
| news | wellness | 8 |
| news | outdoors | 8 |
| news | scifi | 6 |
| news | design | 6 |
| news | homestead | 6 |
| news | climate | 5 |
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
| 2026-W39 | 7 | 1448 | 76 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-09-14T04:00:50.205860+00:00 | 1129 | 589 | 83 | 406 | 68 |
| 2026-09-15T04:00:46.136006+00:00 | 1433 | 908 | 104 | 668 | 100 |
| 2026-09-16T04:00:53.823654+00:00 | 1785 | 1196 | 105 | 921 | 122 |
| 2026-09-17T04:00:47.641046+00:00 | 1866 | 1203 | 105 | 954 | 103 |
| 2026-09-18T04:00:47.270775+00:00 | 1907 | 1254 | 96 | 938 | 152 |
| 2026-09-19T04:00:36.304046+00:00 | 1852 | 1246 | 93 | 980 | 128 |
| 2026-09-20T04:00:32.093265+00:00 | 1444 | 847 | 85 | 646 | 78 |
| 2026-09-21T04:00:37.666981+00:00 | 1156 | 596 | 79 | 415 | 67 |
| 2026-09-22T04:00:45.058198+00:00 | 1533 | 960 | 96 | 700 | 117 |
| 2026-09-23T04:00:36.238364+00:00 | 1584 | 1211 | 88 | 840 | 214 |
| 2026-09-24T04:01:46.118750+00:00 | 1550 | 1172 | 72 | 809 | 240 |
| 2026-09-24T04:28:37.248975+00:00 | 1026 | 742 | 49 | 492 | 172 |
| 2026-09-25T04:01:06.669897+00:00 | 1596 | 1194 | 77 | 831 | 230 |
| 2026-09-26T04:00:58.760213+00:00 | 1616 | 1190 | 80 | 771 | 265 |
| 2026-09-27T04:00:59.519081+00:00 | 1234 | 934 | 67 | 596 | 209 |

### Current category feed sizes

| Feed | Items |
|---|---|
| ai-tech | 97 |
| wellness | 66 |
| news | 60 |
| science | 51 |
| local | 37 |
| climate | 36 |
| design | 35 |
| homelab | 32 |
| scifi | 9 |
| outdoors | 7 |
| homestead | 6 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 23 / 9 |
| Calibration stats runs available | 15 |
| Calibration stats range | 2026-09-14 → 2026-09-27 |
| theme_holdover_cache.json present | True |

**Context:** `calibration_stats_cache.json` was first committed on 2026-07-07, so every weekly calibration run before that found no stats and skipped — the log's repeated "Claude call or response parsing failed" lines were misleading boilerplate, not API failures. The agent's Claude path has effectively never run.

