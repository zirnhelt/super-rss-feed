# Article Review Audit

_Generated: 2026-10-10 18:03 UTC — ratings window 2026-06-17 → 2026-10-10_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 2114 |
| Rated **bad** — reached you (pipeline failed) | 586 |
| Rated **bad** — correctly rejected (pipeline worked) | 744 |
| Rated **good** | 516 (24.4%) |
| Rated **interesting** (wanted, no specific day) | 263 |
| Rated **podcast only** (for the show, not your feed) | 0 |
| Rated good or interesting (raw, quota-biased) | 36.8% |
| Reweighted good-or-interesting rate of the **shipped** feed | 42.3% (from 49.5% of shipped ratings) |
| Scrub false-negative rate (wanted articles thrown away) | 16.9% of 896 rejects |
| Theme-day corrections (`better_theme`) | 425 (20.2% of day-routed ratings) |
| …where the theme scorer already preferred your day | 180 |
| …where the theme scorer disagreed with you | 245 |
| …of those, actually routed by podcast selection | 0 |
| Category retags | 121 (8.7% of categorized ratings) |

## Needs Attention

_Checks one week of numbers cannot make on its own. **Weeks** counts the weekly audits in a row that reported it; at 3+ it has been seen and not acted on._

| Finding | Detail | Weeks |
|---|---|---|
| 6 categories are unmeasured | Under 20 ratings in 28 days: homelab (12), homestead (6), climate (16), scifi (4), design (17), outdoors (5). Their rates are noise, not "fine"; news took 58.3% of the ratings. | 1 |
| The gate threw away 11.8% of the rejects you wanted | 20 of 169 rated rejects in 28 days. Most often, all time: NYT Well (13), MacRumors (8), Outside Online (8), The Northern Miner (5), The Marginalian (5), Cool Tools (5). | 1 |
| Nobody has used "podcast_only" | 0 of 365 ratings in 14 days. If it is never the answer, every metric that counts it is reading one channel. | 1 |
| Places you want that the pool barely carries | williams lake: 84.1% wanted, 11 in the pool (0.8%), quesnel: 56.2% wanted, 10 in the pool (0.7%), 100 mile house: 70.0% wanted, 2 in the pool (0.1%). Baseline 36.9% wanted. | 1 |
| Local places with almost no ratings | Under 5 ratings ever: horsefly, lac la hache. | 1 |
| Block candidates still unblocked | Mother Jones: n ≥ 8 with nothing wanted. Block them in filters.json or rate why not. | 1 |
| Calibration change never landed: source_preferences.kagi_search_result_limit | Logged 2026-09-20 as 10 → 12; config still says 10. | 1 |

### Sampling strata

The review feed is a **quota** sample: a fixed handful from each score band plus up to 10 scrub rejects. Rates within a stratum are unbiased; the corpus-wide rate is not, because half the ratings come from the reject pile. Reweight before comparing anything across strata.

| Stratum | n | good | interesting | podcast only | bad | % good | % good+int |
|---|---|---|---|---|---|---|---|
| unfiltered | 896 | 76 | 75 | 0 | 744 | 8.5 | 16.9 |
| mid | 445 | 161 | 50 | 0 | 234 | 36.2 | 47.4 |
| border | 374 | 130 | 68 | 0 | 176 | 34.8 | 52.9 |
| low | 130 | 22 | 8 | 0 | 100 | 16.9 | 23.1 |
| promising | 117 | 48 | 40 | 0 | 29 | 41.0 | 75.2 |
| high | 113 | 73 | 16 | 0 | 23 | 64.6 | 78.8 |
| floor_fill | 32 | 2 | 6 | 0 | 24 | 6.2 | 25.0 |
| unknown | 7 | 4 | 0 | 0 | 3 | 57.1 | 57.1 |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 516 | 54.8 | 49.0 | 42.4 | 42.9 |
| interesting | 263 | 47.2 | 48 | 29.8 | 28.0 |
| bad | 1333 | 37.1 | 33 | 20.3 | 17.8 |

### Precision by score band

| Score band | n | good | interesting | bad | % good | % good+int | % bad |
|---|---|---|---|---|---|---|---|
| 80-100 | 128 | 79 | 16 | 32 | 61.7 | 74.2 | 25.0 |
| 60-79 | 360 | 125 | 45 | 190 | 34.7 | 47.2 | 52.8 |
| 40-59 | 700 | 213 | 125 | 362 | 30.4 | 48.3 | 51.7 |
| 20-39 | 534 | 68 | 55 | 411 | 12.7 | 23.0 | 77.0 |
| 0-19 | 392 | 31 | 22 | 338 | 7.9 | 13.5 | 86.2 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **25** (manually lowered 20 → 13 on 2026-06-24).

`interesting` articles score low on relevance, so a higher floor costs them first. Weigh **% of bad cut** against **% of good+int lost**.

| Floor | Bad cut | % of bad | Good lost | % of good | Interesting lost | % of int | % of good+int |
|---|---|---|---|---|---|---|---|
| 13 | 68 | 5.1 | 7 | 1.4 | 2 | 0.8 | 1.2 |
| 15 | 185 | 13.9 | 19 | 3.7 | 9 | 3.4 | 3.6 |
| 20 | 338 | 25.4 | 31 | 6.0 | 22 | 8.4 | 6.8 |
| 25 | 437 | 32.8 | 41 | 7.9 | 32 | 12.2 | 9.4 |
| 30 | 642 | 48.2 | 78 | 15.1 | 57 | 21.7 | 17.3 |
| 35 | 708 | 53.1 | 89 | 17.2 | 71 | 27.0 | 20.5 |
| 40 | 749 | 56.2 | 99 | 19.2 | 77 | 29.3 | 22.6 |
| 45 | 824 | 61.8 | 126 | 24.4 | 87 | 33.1 | 27.3 |
| 50 | 1054 | 79.1 | 294 | 57.0 | 195 | 74.1 | 62.8 |
| 60 | 1111 | 83.3 | 312 | 60.5 | 202 | 76.8 | 66.0 |

### By category

| Category | n | good | interesting | bad | % good+int | % bad |
|---|---|---|---|---|---|---|
| news | 1402 | 219 | 90 | 1093 | 22.0 | 78.0 |
| ai-tech | 200 | 59 | 72 | 69 | 65.5 | 34.5 |
| wellness | 150 | 48 | 24 | 77 | 48.0 | 51.3 |
| local | 128 | 81 | 16 | 30 | 75.8 | 23.4 |
| climate | 51 | 31 | 8 | 12 | 76.5 | 23.5 |
| science | 51 | 41 | 6 | 4 | 92.2 | 7.8 |
| homelab | 39 | 15 | 13 | 11 | 71.8 | 28.2 |
| design | 34 | 3 | 15 | 16 | 52.9 | 47.1 |
| scifi | 22 | 1 | 9 | 12 | 45.5 | 54.5 |
| outdoors | 16 | 5 | 6 | 5 | 68.8 | 31.2 |
| homestead | 14 | 9 | 4 | 1 | 92.9 | 7.1 |
| shared | 4 | 4 | 0 | 0 | 100.0 | 0.0 |
| podcast-sunday | 2 | 0 | 0 | 2 | 0.0 | 100.0 |
| podcast-friday | 1 | 0 | 0 | 1 | 0.0 | 100.0 |

### Sources (≥ 5 ratings)

**Highest good+interesting rate**

| Source | n | good | interesting | bad | % good+int |
|---|---|---|---|---|---|
| Eagle Feather News | 6 | 6 | 0 | 0 | 100.0 |
| ScienceAlert | 20 | 17 | 1 | 2 | 90.0 |
| Bicycling | 7 | 4 | 2 | 1 | 85.7 |
| EarthSky | 6 | 5 | 0 | 1 | 83.3 |
| ScienceDaily | 23 | 15 | 4 | 4 | 82.6 |
| The Narwhal | 5 | 4 | 0 | 1 | 80.0 |
| Dezeen | 5 | 0 | 4 | 1 | 80.0 |
| Williams Lake Tribune | 46 | 32 | 4 | 9 | 78.3 |
| Scientific American | 18 | 8 | 6 | 4 | 77.8 |
| APTN News | 13 | 8 | 2 | 3 | 76.9 |

**Lowest good+interesting rate** — block candidate only at n ≥ 8 with zero positives of any kind

| Source | n | good | interesting | bad | % good+int | Block candidate |
|---|---|---|---|---|---|---|
| Mother Jones | 25 | 0 | 0 | 25 | 0.0 | yes |
| Live for the Outdoors (Country Walking) | 7 | 0 | 0 | 7 | 0.0 |  |
| ArchDaily | 6 | 0 | 0 | 6 | 0.0 |  |
| FlowingData | 5 | 0 | 0 | 5 | 0.0 |  |
| Country Guide | 5 | 0 | 0 | 5 | 0.0 |  |
| Edge (GamesRadar) | 47 | 0 | 2 | 45 | 4.3 |  |
| Ideal Home (Country Homes & Interiors) | 32 | 0 | 3 | 29 | 9.4 |  |
| Neowin | 18 | 2 | 0 | 16 | 11.1 |  |
| Country Life | 23 | 1 | 2 | 20 | 13.0 |  |
| The Atlantic | 29 | 0 | 4 | 25 | 13.8 |  |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 309 | 142 | 1092 |
| breaking | 66 | 36 | 86 |
| analysis | 66 | 42 | 55 |
| feature | 46 | 25 | 55 |
| news | 17 | 8 | 17 |
| opinion | 6 | 5 | 20 |
| recap | 1 | 1 | 4 |
| wire | 3 | 1 | 2 |
| fluff | 2 | 2 | 1 |
| investigation | 0 | 1 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 130 | 68 | 176 |
| low | 22 | 8 | 100 |
| high | 73 | 16 | 23 |
| mid | 161 | 50 | 234 |
| unknown | 4 | 0 | 3 |
| unfiltered | 76 | 75 | 744 |
| floor_fill | 2 | 6 | 24 |
| promising | 48 | 40 | 29 |

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
| 2026-10-10 | 467 | 40 | 9 |

## 3. Theme-Bucket Routing Accuracy

Of **2107** ratings tied to an aired day, you corrected the day on **425** (20.2%). Additionally 322 articles were approved for other days.

### Per theme day

`% day fit` counts good + podcast only (the verdicts that name days). `% good+int` is feed fit: wanted in your feed, any day or none.

| Day | Theme | n | good | interesting | podcast only | bad | % day fit | % good+int | Corrected away |
|---|---|---|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 337 | 66 | 58 | 0 | 213 | 19.6 | 36.8 | 57 |
| tuesday | Working Lands & Industry | 309 | 67 | 29 | 0 | 213 | 21.7 | 31.1 | 52 |
| wednesday | Repair Culture & Practical Tech | 367 | 106 | 36 | 0 | 225 | 28.9 | 38.7 | 79 |
| thursday | Indigenous Lands & Innovation | 297 | 63 | 46 | 0 | 188 | 21.2 | 36.7 | 59 |
| friday | Wild Spaces & Outdoor Life | 337 | 83 | 42 | 0 | 211 | 24.6 | 37.1 | 76 |
| saturday | Cariboo Local Affairs | 245 | 71 | 24 | 0 | 150 | 29.0 | 38.8 | 62 |
| sunday | Science, Wonder & the Natural World | 215 | 56 | 28 | 0 | 130 | 26.0 | 39.1 | 40 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 13 | 14 | 1 | 6 | 7 | 16 |
| tuesday | 10 |  | 7 | 3 | 6 | 8 | 18 |
| wednesday | 8 | 14 |  | 4 | 16 | 17 | 20 |
| thursday | 4 | 11 | 9 |  | 7 | 4 | 24 |
| friday | 7 | 14 | 14 | 6 |  | 14 | 21 |
| saturday | 2 | 6 | 12 | 7 | 10 |  | 25 |
| sunday | 4 | 9 | 13 | 1 | 7 | 6 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 180 |
| Theme scorer disagreed with you (scoring miss) | 245 |
| Theme scores missing on the rating | 0 |

## 3b. Category Retag Accuracy

Of **1385** ratings carrying a confirmed/retagged category, you retagged **121** (8.7%) to a different category.

### Category → category correction matrix (shown → corrected)

| Shown | Corrected to | Count |
|---|---|---|
| news | ai-tech | 35 |
| news | homelab | 13 |
| news | science | 10 |
| news | wellness | 8 |
| news | outdoors | 8 |
| news | homestead | 8 |
| news | climate | 7 |
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
| 2026-W40 | 7 | 1354 | 81 |
| 2026-W41 | 5 | 1511 | 87 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-09-27T04:00:59.519081+00:00 | 1234 | 934 | 67 | 596 | 209 |
| 2026-09-28T04:01:26.045743+00:00 | 762 | 579 | 63 | 355 | 123 |
| 2026-09-29T04:00:55.720608+00:00 | 1131 | 911 | 84 | 602 | 174 |
| 2026-09-30T04:01:13.201271+00:00 | 1601 | 1230 | 84 | 802 | 285 |
| 2026-10-01T04:01:33.771128+00:00 | 1614 | 1274 | 89 | 827 | 286 |
| 2026-10-02T04:01:10.254540+00:00 | 1610 | 1253 | 83 | 801 | 294 |
| 2026-10-03T04:01:16.901145+00:00 | 1598 | 1213 | 83 | 758 | 273 |
| 2026-10-04T04:01:10.284230+00:00 | 1144 | 867 | 70 | 524 | 209 |
| 2026-10-05T04:01:10.024407+00:00 | 778 | 581 | 73 | 330 | 121 |
| 2026-10-06T04:01:07.354818+00:00 | 1235 | 969 | 87 | 586 | 229 |
| 2026-10-07T04:01:15.911467+00:00 | 1520 | 1174 | 88 | 727 | 267 |
| 2026-10-08T04:01:11.858888+00:00 | 1568 | 1193 | 87 | 791 | 237 |
| 2026-10-09T04:01:05.317620+00:00 | 1638 | 1230 | 92 | 864 | 174 |
| 2026-10-10T04:01:02.767424+00:00 | 1594 | 1243 | 81 | 932 | 135 |

### Current category feed sizes

| Feed | Items |
|---|---|
| ai-tech | 84 |
| news | 70 |
| wellness | 58 |
| homelab | 44 |
| local | 44 |
| science | 41 |
| climate | 36 |
| design | 29 |
| outdoors | 12 |
| homestead | 11 |
| scifi | 9 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 25 / 9 |
| Calibration stats runs available | 14 |
| Calibration stats range | 2026-09-27 → 2026-10-10 |
| theme_holdover_cache.json present | True |

**Context:** `calibration_stats_cache.json` was first committed on 2026-07-07, so every weekly calibration run before that found no stats and skipped — the log's repeated "Claude call or response parsing failed" lines were misleading boilerplate, not API failures. The agent's Claude path has effectively never run.

## 6. Week over Week

_Counts are the 7 days to each date; rates cover 28 days. Weeks marked * were rebuilt from the ratings archive and carry no cost or scorecard data._

| Week | Through | Rated | good | interesting | podcast only | bad | Notes | Shipped wanted % (reweighted) | Gate miss % | News share of ratings % |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-W30* | 2026-07-25 | 77 | 25 | 8 | 0 | 44 | 1 |  | 16.6 | 76.2 |
| 2026-W31* | 2026-08-01 | 99 | 18 | 11 | 0 | 70 | 7 |  | 16.6 | 74.5 |
| 2026-W32* | 2026-08-08 | 99 | 15 | 21 | 0 | 63 | 7 |  | 21.3 | 72.2 |
| 2026-W33* | 2026-08-15 | 106 | 15 | 15 | 0 | 76 | 2 |  | 23.5 | 74.5 |
| 2026-W34* | 2026-08-22 | 108 | 8 | 21 | 0 | 79 | 2 |  | 21.7 | 78.4 |
| 2026-W35* | 2026-08-29 | 59 | 3 | 12 | 0 | 44 | 3 |  | 20.2 | 78.2 |
| 2026-W36* | 2026-09-05 | 89 | 3 | 9 | 0 | 77 | 1 |  | 16.2 | 78.7 |
| 2026-W37* | 2026-09-12 | 135 | 32 | 18 | 0 | 85 | 2 | 40.8 | 15.0 | 76.7 |
| 2026-W38* | 2026-09-19 | 181 | 38 | 19 | 0 | 124 | 5 | 41.2 | 13.8 | 73.1 |
| 2026-W39* | 2026-09-26 | 142 | 31 | 34 | 0 | 77 | 23 | 41.1 | 13.8 | 70.2 |
| 2026-W40* | 2026-10-03 | 188 | 56 | 52 | 0 | 80 | 94 | 43.5 | 15.7 | 62.2 |
| 2026-W41 | 2026-10-10 | 177 | 53 | 29 | 0 | 95 | 84 | 42.5 | 11.8 | 58.3 |

## 7. What Each Score Buys

Graded on the last 4 weeks of ratings (688 rated, 401 news). AUC is the chance a wanted article outscores an unwanted one: 0.5 is a coin flip. The reader model is refit each week on earlier ratings only; it uses the relevance band, so it is not wholly free of the paid pass.

| Signal | Paid by | AUC | AUC, news only |
|---|---|---|---|
| final score | gate + deep_score | 0.714 | 0.724 |
| quality (Q) | deep_score; q_gate elsewhere | 0.689 | 0.535 |
| relevance (R) | deep_score | 0.701 | 0.539 |
| local (L) | deep_score | 0.591 | 0.531 |
| theme fit for that day's theme | theme_ingest / theme / theme_batch | 0.662 | 0.672 |
| reader model | free: your earlier ratings | 0.821 | 0.805 |

### Claude cost by stage (last 7 days)

5 of 7 runs recorded stages; all vendors together est. $2.3677.

| Stage | Calls | Est. cost |
|---|---|---|
| gate | 151 | $0.8167 |
| deep_score | 51 | $0.2950 |
| theme | 20 | $0.0541 |

### Local places: appetite vs. supply

Wanted % among rated articles mentioning the place (baseline 36.9%), against its share of the 1431-article podcast pool.

| Place | Rated | Wanted % | In pool | Pool % |
|---|---|---|---|---|
| williams lake | 44 | 84.1 | 11 | 0.8 |
| cariboo | 63 | 74.6 | 30 | 2.1 |
| quesnel | 32 | 56.2 | 10 | 0.7 |
| 100 mile house | 20 | 70.0 | 2 | 0.1 |
| horsefly | 1 | 100.0 | 0 | 0.0 |
| lac la hache | 1 | 100.0 | 0 | 0.0 |

## 8. Did Calibration Changes Land?

_Status is checked for the latest change to each knob. Before/after is the reweighted wanted rate of the shipped feed over 14 days either side (weighted ratings in brackets): everything else changed too, so read it as a correlation._

| Date | Knob | Change | In config now? | Before | After |
|---|---|---|---|---|---|
| 2026-07-12 | limits.min_claude_score | 13 → 16 | superseded | — | — |
| 2026-07-12 | limits.haiku_scrub_floor | 10 → 13 | in config | — | — |
| 2026-07-19 | limits.min_claude_score | 16 → 18 | superseded | — | — |
| 2026-07-26 | limits.min_claude_score | 18 → 20 | superseded | — | — |
| 2026-08-24 | limits.min_claude_score | 20 → 23 | superseded | — | — |
| 2026-09-06 | limits.min_claude_score | 23 → 25 | in config | — | 41.2% (201) |
| 2026-09-06 | feed_slots.max_slots.news | 25 → 22 | changed since (10) | — | 41.2% (201) |
| 2026-09-13 | source_preferences.kagi_search_result_limit | 10 → 12 | superseded | 40.8% (80) | 41.2% (223) |
| 2026-09-20 | source_preferences.kagi_search_result_limit | 10 → 12 | not in config | 41.2% (201) | 45.6% (255) |

