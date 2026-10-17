# Article Review Audit

_Generated: 2026-10-17 16:39 UTC — ratings window 2026-06-17 → 2026-10-17_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 2248 |
| Rated **bad** — reached you (pipeline failed) | 622 |
| Rated **bad** — correctly rejected (pipeline worked) | 761 |
| Rated **good** | 548 (24.4%) |
| Rated **interesting** (wanted, no specific day) | 298 |
| Rated **podcast only** (for the show, not your feed) | 14 |
| Rated good or interesting (raw, quota-biased) | 37.6% |
| Reweighted good-or-interesting rate of the **shipped** feed | 44.1% (from 53.7% of shipped ratings) |
| Scrub false-negative rate (wanted articles thrown away) | 17.2% of 922 rejects |
| Theme-day corrections (`better_theme`) | 463 (20.7% of day-routed ratings) |
| …where the theme scorer already preferred your day | 205 |
| …where the theme scorer disagreed with you | 258 |
| …of those, actually routed by podcast selection | 0 |
| Category retags | 121 (8.0% of categorized ratings) |

## Needs Attention

_Checks one week of numbers cannot make on its own. **Weeks** counts the weekly audits in a row that reported it; at 3+ it has been seen and not acted on._

| Finding | Detail | Weeks |
|---|---|---|
| 4 categories are unmeasured | Under 20 ratings in 28 days: homelab (17), homestead (9), scifi (5), outdoors (9). Their rates are noise, not "fine"; news took 49.6% of the ratings. | 2 |
| The gate threw away 14.1% of the rejects you wanted | 19 of 135 rated rejects in 28 days. Most often, all time: NYT Well (13), MacRumors (9), Outside Online (8), Fast Company (6), The Northern Miner (5), The Marginalian (5). | 2 |
| Places you want that the pool barely carries | 100 mile house: 71.4% wanted, 4 in the pool (0.3%). Baseline 38.3% wanted. | 2 |
| Block candidates still unblocked | Live for the Outdoors (Country Walking): n ≥ 8 with nothing wanted. Block them in filters.json or rate why not. | 2 |

### Sampling strata

The review feed is a **quota** sample: a fixed handful from each score band plus up to 10 scrub rejects. Rates within a stratum are unbiased; the corpus-wide rate is not, because half the ratings come from the reject pile. Reweight before comparing anything across strata.

| Stratum | n | good | interesting | podcast only | bad | % good | % good+int |
|---|---|---|---|---|---|---|---|
| unfiltered | 922 | 78 | 81 | 1 | 761 | 8.5 | 17.2 |
| mid | 466 | 172 | 52 | 2 | 240 | 36.9 | 48.1 |
| border | 384 | 132 | 70 | 0 | 182 | 34.4 | 52.6 |
| promising | 153 | 53 | 52 | 6 | 42 | 34.6 | 68.6 |
| low | 133 | 22 | 10 | 0 | 101 | 16.5 | 24.1 |
| high | 117 | 76 | 17 | 0 | 23 | 65.0 | 79.5 |
| floor_fill | 36 | 2 | 7 | 0 | 27 | 5.6 | 25.0 |
| near_miss | 24 | 5 | 7 | 5 | 7 | 20.8 | 50.0 |
| unknown | 7 | 4 | 0 | 0 | 3 | 57.1 | 57.1 |
| in_feed | 6 | 4 | 2 | 0 | 0 | 66.7 | 100.0 |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 548 | 55.1 | 49.0 | 43.7 | 44.3 |
| interesting | 298 | 46.9 | 48.0 | 31.8 | 29.6 |
| podcast_only | 14 | 50.6 | 47.5 | 65.4 | 57.3 |
| bad | 1386 | 37.3 | 33.0 | 21.0 | 18.2 |

### Precision by score band

| Score band | n | good | interesting | bad | % good | % good+int | % bad |
|---|---|---|---|---|---|---|---|
| 80-100 | 136 | 85 | 18 | 32 | 62.5 | 75.7 | 23.5 |
| 60-79 | 380 | 135 | 48 | 194 | 35.5 | 48.2 | 51.1 |
| 40-59 | 774 | 227 | 144 | 394 | 29.3 | 47.9 | 50.9 |
| 20-39 | 557 | 70 | 63 | 422 | 12.6 | 23.9 | 75.8 |
| 0-19 | 401 | 31 | 25 | 344 | 7.7 | 14.0 | 85.8 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **25** (manually lowered 20 → 13 on 2026-06-24).

`interesting` articles score low on relevance, so a higher floor costs them first. Weigh **% of bad cut** against **% of good+int lost**.

| Floor | Bad cut | % of bad | Good lost | % of good | Interesting lost | % of int | % of good+int |
|---|---|---|---|---|---|---|---|
| 13 | 68 | 4.9 | 7 | 1.3 | 2 | 0.7 | 1.1 |
| 15 | 186 | 13.4 | 19 | 3.5 | 9 | 3.0 | 3.3 |
| 20 | 344 | 24.8 | 31 | 5.7 | 25 | 8.4 | 6.6 |
| 25 | 445 | 32.1 | 41 | 7.5 | 36 | 12.1 | 9.1 |
| 30 | 653 | 47.1 | 78 | 14.2 | 63 | 21.1 | 16.7 |
| 35 | 721 | 52.0 | 89 | 16.2 | 78 | 26.2 | 19.7 |
| 40 | 766 | 55.3 | 101 | 18.4 | 88 | 29.5 | 22.3 |
| 45 | 852 | 61.5 | 133 | 24.3 | 103 | 34.6 | 27.9 |
| 50 | 1095 | 79.0 | 305 | 55.7 | 224 | 75.2 | 62.5 |
| 60 | 1160 | 83.7 | 328 | 59.9 | 232 | 77.9 | 66.2 |

### By category

| Category | n | good | interesting | bad | % good+int | % bad |
|---|---|---|---|---|---|---|
| news | 1443 | 226 | 97 | 1119 | 22.4 | 77.5 |
| ai-tech | 219 | 62 | 83 | 73 | 66.2 | 33.3 |
| wellness | 160 | 51 | 27 | 80 | 48.8 | 50.0 |
| local | 143 | 90 | 19 | 31 | 76.2 | 21.7 |
| science | 64 | 44 | 7 | 7 | 79.7 | 10.9 |
| climate | 61 | 33 | 11 | 16 | 72.1 | 26.2 |
| homelab | 45 | 18 | 14 | 12 | 71.1 | 26.7 |
| design | 45 | 4 | 20 | 21 | 53.3 | 46.7 |
| scifi | 23 | 1 | 9 | 13 | 43.5 | 56.5 |
| outdoors | 21 | 5 | 6 | 10 | 52.4 | 47.6 |
| homestead | 17 | 10 | 5 | 1 | 88.2 | 5.9 |
| shared | 4 | 4 | 0 | 0 | 100.0 | 0.0 |
| podcast-sunday | 2 | 0 | 0 | 2 | 0.0 | 100.0 |
| podcast-friday | 1 | 0 | 0 | 1 | 0.0 | 100.0 |

### Sources (≥ 5 ratings)

**Highest good+interesting rate**

| Source | n | good | interesting | bad | % good+int |
|---|---|---|---|---|---|
| Eagle Feather News | 7 | 7 | 0 | 0 | 100.0 |
| Cariboo Signals Reviews | 5 | 2 | 3 | 0 | 100.0 |
| ScienceAlert | 22 | 18 | 1 | 2 | 86.4 |
| Bicycling | 7 | 4 | 2 | 1 | 85.7 |
| Dezeen | 6 | 0 | 5 | 1 | 83.3 |
| The Narwhal | 5 | 4 | 0 | 1 | 80.0 |
| ScienceDaily | 28 | 18 | 4 | 4 | 78.6 |
| Williams Lake Tribune | 51 | 35 | 5 | 9 | 78.4 |
| 100 Mile Free Press | 22 | 15 | 2 | 5 | 77.3 |
| The Tyee | 28 | 14 | 7 | 7 | 75.0 |

**Lowest good+interesting rate** — block candidate only at n ≥ 8 with zero positives of any kind

| Source | n | good | interesting | bad | % good+int | Block candidate |
|---|---|---|---|---|---|---|
| Live for the Outdoors (Country Walking) | 9 | 0 | 0 | 9 | 0.0 | yes |
| Country Guide | 6 | 0 | 0 | 6 | 0.0 |  |
| FlowingData | 5 | 0 | 0 | 5 | 0.0 |  |
| Edge (GamesRadar) | 49 | 0 | 2 | 47 | 4.1 |  |
| Ideal Home (Country Homes & Interiors) | 33 | 0 | 3 | 30 | 9.1 |  |
| Neowin | 18 | 2 | 0 | 16 | 11.1 |  |
| Country Life | 24 | 1 | 2 | 21 | 12.5 |  |
| NYT Top Stories | 68 | 5 | 4 | 59 | 13.2 |  |
| Lifehacker | 28 | 3 | 1 | 24 | 14.3 |  |
| Domino | 21 | 0 | 3 | 18 | 14.3 |  |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 310 | 151 | 1113 |
| analysis | 82 | 58 | 65 |
| breaking | 71 | 39 | 92 |
| feature | 54 | 30 | 68 |
| news | 17 | 8 | 17 |
| opinion | 7 | 6 | 21 |
| recap | 1 | 2 | 5 |
| fluff | 3 | 2 | 1 |
| wire | 3 | 1 | 2 |
| investigation | 0 | 1 | 1 |
| essay | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 132 | 70 | 182 |
| low | 22 | 10 | 101 |
| high | 76 | 17 | 23 |
| mid | 172 | 52 | 240 |
| unknown | 4 | 0 | 3 |
| unfiltered | 78 | 81 | 761 |
| floor_fill | 2 | 7 | 27 |
| promising | 53 | 52 | 42 |
| near_miss | 5 | 7 | 7 |
| in_feed | 4 | 2 | 0 |

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
| 2026-10-17 | 1333 | 56 | 4 |

## 3. Theme-Bucket Routing Accuracy

Of **2241** ratings tied to an aired day, you corrected the day on **463** (20.7%). Additionally 362 articles were approved for other days.

### Per theme day

`% day fit` counts good + podcast only (the verdicts that name days). `% good+int` is feed fit: wanted in your feed, any day or none.

| Day | Theme | n | good | interesting | podcast only | bad | % day fit | % good+int | Corrected away |
|---|---|---|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 364 | 69 | 65 | 8 | 222 | 21.2 | 36.8 | 67 |
| tuesday | Working Lands & Industry | 336 | 75 | 38 | 1 | 222 | 22.6 | 33.6 | 59 |
| wednesday | Repair Culture & Practical Tech | 379 | 110 | 39 | 2 | 228 | 29.6 | 39.3 | 85 |
| thursday | Indigenous Lands & Innovation | 309 | 66 | 49 | 1 | 193 | 21.7 | 37.2 | 62 |
| friday | Wild Spaces & Outdoor Life | 349 | 87 | 45 | 2 | 214 | 25.5 | 37.8 | 82 |
| saturday | Cariboo Local Affairs | 269 | 79 | 29 | 0 | 161 | 29.4 | 40.1 | 67 |
| sunday | Science, Wonder & the Natural World | 235 | 58 | 33 | 0 | 143 | 24.7 | 38.7 | 41 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 15 | 15 | 2 | 6 | 9 | 20 |
| tuesday | 10 |  | 9 | 4 | 6 | 9 | 21 |
| wednesday | 8 | 15 |  | 4 | 16 | 19 | 23 |
| thursday | 4 | 11 | 9 |  | 7 | 6 | 25 |
| friday | 7 | 14 | 14 | 8 |  | 15 | 24 |
| saturday | 2 | 7 | 13 | 9 | 10 |  | 26 |
| sunday | 4 | 9 | 13 | 1 | 7 | 7 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 205 |
| Theme scorer disagreed with you (scoring miss) | 258 |
| Theme scores missing on the rating | 0 |

## 3b. Category Retag Accuracy

Of **1519** ratings carrying a confirmed/retagged category, you retagged **121** (8.0%) to a different category.

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
| 2026-W41 | 7 | 1367 | 84 |
| 2026-W42 | 5 | 1499 | 82 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-10-04T04:01:10.284230+00:00 | 1144 | 867 | 70 | 524 | 209 |
| 2026-10-05T04:01:10.024407+00:00 | 778 | 581 | 73 | 330 | 121 |
| 2026-10-06T04:01:07.354818+00:00 | 1235 | 969 | 87 | 586 | 229 |
| 2026-10-07T04:01:15.911467+00:00 | 1520 | 1174 | 88 | 727 | 267 |
| 2026-10-08T04:01:11.858888+00:00 | 1568 | 1193 | 87 | 791 | 237 |
| 2026-10-09T04:01:05.317620+00:00 | 1638 | 1230 | 92 | 864 | 174 |
| 2026-10-10T04:01:02.767424+00:00 | 1594 | 1243 | 81 | 932 | 135 |
| 2026-10-11T04:01:14.442081+00:00 | 1213 | 936 | 80 | 673 | 100 |
| 2026-10-12T04:01:23.209937+00:00 | 804 | 607 | 76 | 419 | 55 |
| 2026-10-13T04:01:10.282845+00:00 | 1052 | 854 | 86 | 653 | 57 |
| 2026-10-14T04:01:01.447572+00:00 | 1493 | 1131 | 81 | 813 | 149 |
| 2026-10-15T04:01:12.929108+00:00 | 1661 | 1273 | 87 | 902 | 187 |
| 2026-10-16T04:01:00.341811+00:00 | 1653 | 1263 | 81 | 912 | 165 |
| 2026-10-17T04:01:54.851437+00:00 | 1634 | 1249 | 77 | 842 | 202 |

### Current category feed sizes

| Feed | Items |
|---|---|
| ai-tech | 90 |
| news | 70 |
| wellness | 54 |
| science | 42 |
| local | 40 |
| climate | 38 |
| design | 28 |
| homelab | 26 |
| homestead | 12 |
| outdoors | 9 |
| scifi | 8 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 26 / 9 |
| Calibration stats runs available | 14 |
| Calibration stats range | 2026-10-04 → 2026-10-17 |
| theme_holdover_cache.json present | True |

**Context:** `calibration_stats_cache.json` was first committed on 2026-07-07, so every weekly calibration run before that found no stats and skipped — the log's repeated "Claude call or response parsing failed" lines were misleading boilerplate, not API failures. The agent's Claude path has effectively never run.

## 6. Week over Week

_Counts are the 7 days to each date; rates cover 28 days. Weeks marked * were rebuilt from the ratings archive and carry no cost or scorecard data._

| Week | Through | Rated | good | interesting | podcast only | bad | Notes | Shipped wanted % (reweighted) | Gate miss % | News share of ratings % |
|---|---|---|---|---|---|---|---|---|---|---|
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
| 2026-W42 | 2026-10-17 | 134 | 32 | 35 | 14 | 53 | 39 | 45.4 | 14.1 | 49.6 |

## 7. What Each Score Buys

Graded on the last 4 weeks of ratings (641 rated, 318 news). AUC is the chance a wanted article outscores an unwanted one: 0.5 is a coin flip. The reader model is refit each week on earlier ratings only; it uses the relevance band, so it is not wholly free of the paid pass.

| Signal | Paid by | AUC | AUC, news only |
|---|---|---|---|
| final score | gate + deep_score | 0.7 | 0.728 |
| quality (Q) | deep_score; q_gate elsewhere | 0.699 | 0.558 |
| relevance (R) | deep_score | 0.722 | 0.563 |
| local (L) | deep_score | 0.6 | 0.553 |
| theme fit for that day's theme | theme_ingest / theme / theme_batch | 0.657 | 0.68 |
| reader model | free: your earlier ratings | 0.812 | 0.809 |

### Claude cost by stage (last 7 days)

7 of 7 runs recorded stages; all vendors together est. $1.0844.

| Stage | Calls | Est. cost |
|---|---|---|
| gate | 205 | $0.1574 |
| deep_score | 80 | $0.0904 |
| theme | 46 | $0.0549 |

### Local places: appetite vs. supply

Wanted % among rated articles mentioning the place (baseline 38.3%), against its share of the 1443-article podcast pool.

| Place | Rated | Wanted % | In pool | Pool % |
|---|---|---|---|---|
| williams lake | 69 | 78.3 | 40 | 2.8 |
| cariboo | 94 | 73.4 | 28 | 1.9 |
| quesnel | 44 | 59.1 | 14 | 1.0 |
| 100 mile house | 21 | 71.4 | 4 | 0.3 |
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
| 2026-09-20 | source_preferences.kagi_search_result_limit | 10 → 12 | superseded | 41.2% (201) | 45.6% (255) |

