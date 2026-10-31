# Article Review Audit

_Generated: 2026-10-31 18:00 UTC — ratings window 2026-08-03 → 2026-10-30 (rolling 90 days; 2392 rated all time)_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 1550 |
| Rated **bad** — reached you (pipeline failed) | 427 |
| Rated **bad** — correctly rejected (pipeline worked) | 465 |
| Rated **good** | 307 (19.8%) |
| Rated **interesting** (wanted, no specific day) | 298 |
| Rated **podcast only** (for the show, not your feed) | 51 |
| Rated good or interesting (raw, quota-biased) | 39.0% |
| Reweighted good-or-interesting rate of the **shipped** feed | 43.0% (from 84.3% of shipped ratings) |
| Scrub false-negative rate (wanted articles thrown away) | 17.1% of 568 rejects |
| Theme-day corrections (`better_theme`) | 293 (18.9% of day-routed ratings) |
| …where the theme scorer already preferred your day | 153 |
| …where the theme scorer disagreed with you | 140 |
| …of those, actually routed by podcast selection | 0 |
| Category retags | 106 (6.8% of categorized ratings) |

## Needs Attention

_Checks one week of numbers cannot make on its own. **Weeks** counts the weekly audits in a row that reported it; at 3+ it has been seen and not acted on._

| Finding | Detail | Weeks |
|---|---|---|
| ⚠️ 5 categories are unmeasured | Under 20 ratings in 28 days: homelab (13), homestead (5), climate (15), scifi (9), outdoors (9). Their rates are noise, not "fine"; news took 38.0% of the ratings. | 4 |
| ⚠️ The gate threw away 22.6% of the rejects you wanted | 19 of 84 rated rejects in 28 days. Most often, all time: NYT Well (14), MacRumors (9), Outside Online (8), Fast Company (6), The Northern Miner (5), WIRED (5). | 4 |
| ⚠️ Places you want that the pool barely carries | 100 mile house: 68.2% wanted, 4 in the pool (0.3%). Baseline 39.9% wanted. | 4 |
| ⚠️ Block candidates still unblocked | Live for the Outdoors (Country Walking): n ≥ 8 with nothing wanted. Block them in filters.json or rate why not. | 4 |
| Local places with almost no ratings | Under 5 ratings ever: horsefly. | 2 |

### Sampling strata

The review feed is a **quota** sample: a fixed handful from each score band plus up to 10 scrub rejects. Rates within a stratum are unbiased; the corpus-wide rate is not, because half the ratings come from the reject pile. Reweight before comparing anything across strata.

| Stratum | n | good | interesting | podcast only | bad | % good | % good+int |
|---|---|---|---|---|---|---|---|
| unfiltered | 568 | 28 | 69 | 5 | 465 | 4.9 | 17.1 |
| mid | 279 | 87 | 52 | 2 | 138 | 31.2 | 49.8 |
| border | 216 | 51 | 52 | 0 | 113 | 23.6 | 47.7 |
| promising | 153 | 53 | 52 | 6 | 42 | 34.6 | 68.6 |
| near_miss | 118 | 15 | 33 | 33 | 37 | 12.7 | 40.7 |
| low | 75 | 8 | 10 | 0 | 57 | 10.7 | 24.0 |
| high | 73 | 48 | 17 | 0 | 7 | 65.8 | 89.0 |
| floor_fill | 36 | 2 | 7 | 0 | 27 | 5.6 | 25.0 |
| in_feed | 30 | 15 | 6 | 5 | 4 | 50.0 | 70.0 |
| wildcard | 2 | 0 | 0 | 0 | 2 | 0.0 | 0.0 |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 307 | 59.7 | 56 | 42.2 | 43.7 |
| interesting | 298 | 48.0 | 48.0 | 32.4 | 30.3 |
| podcast_only | 51 | 51.4 | 48 | 57.4 | 49.5 |
| bad | 892 | 38.1 | 34.0 | 14.0 | 11.3 |

### Precision by score band

| Score band | n | good | interesting | bad | % good | % good+int | % bad |
|---|---|---|---|---|---|---|---|
| 80-100 | 95 | 60 | 20 | 10 | 63.2 | 84.2 | 10.5 |
| 60-79 | 286 | 89 | 55 | 133 | 31.1 | 50.3 | 46.5 |
| 40-59 | 557 | 124 | 136 | 270 | 22.3 | 46.7 | 48.5 |
| 20-39 | 412 | 29 | 65 | 307 | 7.0 | 22.8 | 74.5 |
| 0-19 | 200 | 5 | 22 | 172 | 2.5 | 13.5 | 86.0 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **25** (manually lowered 20 → 13 on 2026-06-24).

`interesting` articles score low on relevance, so a higher floor costs them first. Weigh **% of bad cut** against **% of good+int lost**.

| Floor | Bad cut | % of bad | Good lost | % of good | Interesting lost | % of int | % of good+int |
|---|---|---|---|---|---|---|---|
| 13 | 0 | 0.0 | 0 | 0.0 | 0 | 0.0 | 0.0 |
| 15 | 49 | 5.5 | 1 | 0.3 | 6 | 2.0 | 1.2 |
| 20 | 172 | 19.3 | 5 | 1.6 | 22 | 7.4 | 4.5 |
| 25 | 254 | 28.5 | 12 | 3.9 | 31 | 10.4 | 7.1 |
| 30 | 390 | 43.7 | 25 | 8.1 | 56 | 18.8 | 13.4 |
| 35 | 447 | 50.1 | 30 | 9.8 | 71 | 23.8 | 16.7 |
| 40 | 479 | 53.7 | 34 | 11.1 | 87 | 29.2 | 20.0 |
| 45 | 540 | 60.5 | 50 | 16.3 | 104 | 34.9 | 25.5 |
| 50 | 717 | 80.4 | 147 | 47.9 | 212 | 71.1 | 59.3 |
| 60 | 749 | 84.0 | 158 | 51.5 | 223 | 74.8 | 63.0 |

### By category

| Category | n | good | interesting | bad | % good+int | % bad |
|---|---|---|---|---|---|---|
| news | 840 | 72 | 89 | 670 | 19.2 | 79.8 |
| ai-tech | 180 | 36 | 87 | 55 | 68.3 | 30.6 |
| wellness | 130 | 36 | 27 | 60 | 48.5 | 46.2 |
| local | 126 | 68 | 21 | 30 | 70.6 | 23.8 |
| science | 71 | 35 | 9 | 7 | 62.0 | 9.9 |
| design | 56 | 4 | 23 | 28 | 48.2 | 50.0 |
| climate | 45 | 24 | 8 | 10 | 71.1 | 22.2 |
| homelab | 41 | 16 | 14 | 9 | 73.2 | 22.0 |
| outdoors | 23 | 5 | 6 | 11 | 47.8 | 47.8 |
| scifi | 21 | 1 | 9 | 11 | 47.6 | 52.4 |
| homestead | 17 | 10 | 5 | 1 | 88.2 | 5.9 |

### Sources (≥ 5 ratings)

**Highest good+interesting rate**

| Source | n | good | interesting | bad | % good+int |
|---|---|---|---|---|---|
| Cariboo Signals Reviews | 5 | 2 | 3 | 0 | 100.0 |
| InsideEVs | 7 | 5 | 1 | 1 | 85.7 |
| Bicycling | 7 | 4 | 2 | 1 | 85.7 |
| The Tyee | 26 | 16 | 6 | 3 | 84.6 |
| APTN News | 6 | 4 | 1 | 0 | 83.3 |
| XDA Developers | 5 | 3 | 1 | 0 | 80.0 |
| Neuroscience News | 5 | 3 | 1 | 0 | 80.0 |
| Williams Lake Tribune | 45 | 27 | 7 | 7 | 75.6 |
| MacRumors | 8 | 2 | 4 | 2 | 75.0 |
| ScienceAlert | 18 | 12 | 1 | 1 | 72.2 |

**Lowest good+interesting rate** — block candidate only at n ≥ 8 with zero positives of any kind

| Source | n | good | interesting | bad | % good+int | Block candidate |
|---|---|---|---|---|---|---|
| Live for the Outdoors (Country Walking) | 9 | 0 | 0 | 9 | 0.0 | yes |
| My East Kootenay Now | 7 | 0 | 0 | 7 | 0.0 |  |
| Country Guide | 6 | 0 | 0 | 6 | 0.0 |  |
| Edge (GamesRadar) | 53 | 0 | 2 | 51 | 3.8 |  |
| NYT Top Stories | 49 | 2 | 2 | 44 | 8.2 |  |
| Ideal Home (Country Homes & Interiors) | 33 | 0 | 3 | 30 | 9.1 |  |
| Country Life | 24 | 1 | 2 | 21 | 12.5 |  |
| Lifehacker | 8 | 0 | 1 | 7 | 12.5 |  |
| Domino | 21 | 0 | 3 | 18 | 14.3 |  |
| Maclean's | 7 | 1 | 0 | 6 | 14.3 |  |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 110 | 143 | 682 |
| analysis | 72 | 67 | 59 |
| breaking | 58 | 34 | 59 |
| feature | 43 | 35 | 59 |
| news | 13 | 8 | 11 |
| opinion | 7 | 5 | 15 |
| recap | 0 | 2 | 5 |
| fluff | 3 | 2 | 0 |
| investigation | 0 | 1 | 1 |
| wire | 1 | 1 | 0 |
| essay | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 51 | 52 | 113 |
| low | 8 | 10 | 57 |
| unfiltered | 28 | 69 | 465 |
| high | 48 | 17 | 7 |
| mid | 87 | 52 | 138 |
| floor_fill | 2 | 7 | 27 |
| promising | 53 | 52 | 42 |
| near_miss | 15 | 33 | 37 |
| in_feed | 15 | 6 | 4 |
| wildcard | 0 | 0 | 2 |

### Filler trend (from the corpus alignment reports, kept in weekly_metrics.jsonl)

| Week | Articles analysed | Filler | Filler % |
|---|---|---|---|
| 2026-Q2 (3 wk) | 2234 | 170 | 8 |
| 2026-Q3 (8 wk) | 10955 | 1022 | 9 |
| 2026-W37 | 1377 | 124 | 9 |
| 2026-W38 | 1397 | 147 | 11 |
| 2026-W39 | 1469 | 182 | 12 |
| 2026-W40 | 1340 | 162 | 12 |
| 2026-W41 | 467 | 40 | 9 |
| 2026-W42 | 1333 | 56 | 4 |
| 2026-W43 | 1318 | 81 | 6 |
| 2026-W44 | 1296 | 0 | 0 |

## 3. Theme-Bucket Routing Accuracy

_Day corrections: 18.9% of 1550 — within noise of 2026-W43, so the tables are left out. They print in full in the first audit of each month._

## 3b. Category Retag Accuracy

_Category retags: 6.8% of 1550 — within noise of 2026-W43, so the tables are left out. They print in full in the first audit of each month._

## 4. Volume Trend — Is the Feed Lighter?

_Average per-run articles fetched and passing the quality gate, by ISO week (from FEED_LOG.md). The quality floor was manually dropped 20 → 13 in week 2026-W26._

| Week | Runs | Avg fetched/run | Avg quality/run |
|---|---|---|---|
| 2026-Q1 (6 wk) | 105 | 872 | 198 |
| 2026-Q2 (13 wk) | 193 | 1012 | 102 |
| 2026-Q3 (9 wk) | 72 | 1334 | 78 |
| 2026-W37 | 7 | 1557 | 93 |
| 2026-W38 | 7 | 1635 | 95 |
| 2026-W39 | 8 | 1363 | 74 |
| 2026-W40 | 7 | 1354 | 81 |
| 2026-W41 | 7 | 1367 | 84 |
| 2026-W42 | 7 | 1364 | 80 |
| 2026-W43 | 7 | 1421 | 84 |
| 2026-W44 | 5 | 1643 | 88 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-10-18T04:01:30.784791+00:00 | 1186 | 902 | 73 | 556 | 188 |
| 2026-10-19T06:00:52.957625+00:00 | 870 | 638 | 76 | 402 | 98 |
| 2026-10-20T06:01:01.018722+00:00 | 1288 | 995 | 87 | 661 | 146 |
| 2026-10-21T06:00:50.667801+00:00 | 1601 | 1222 | 85 | 845 | 152 |
| 2026-10-22T06:00:51.678633+00:00 | 1617 | 1239 | 93 | 841 | 181 |
| 2026-10-23T06:01:02.570687+00:00 | 1705 | 1378 | 93 | 991 | 186 |
| 2026-10-24T06:00:57.289163+00:00 | 1657 | 1323 | 87 | 908 | 216 |
| 2026-10-25T06:00:53.460455+00:00 | 1214 | 966 | 71 | 638 | 159 |
| 2026-10-26T06:01:01.288019+00:00 | 865 | 697 | 75 | 443 | 99 |
| 2026-10-27T06:00:53.007214+00:00 | 1336 | 1055 | 84 | 684 | 185 |
| 2026-10-28T06:00:47.270840+00:00 | 1699 | 1341 | 89 | 930 | 182 |
| 2026-10-29T06:00:53.599263+00:00 | 1739 | 1350 | 81 | 916 | 189 |
| 2026-10-30T06:00:56.669293+00:00 | 1779 | 1429 | 91 | 938 | 226 |
| 2026-10-31T06:00:48.837686+00:00 | 1664 | 1290 | 93 | 872 | 202 |

### Current category feed sizes

| Feed | Items |
|---|---|
| news | 106 |
| ai-tech | 82 |
| climate | 58 |
| local | 52 |
| wellness | 52 |
| science | 43 |
| homelab | 32 |
| design | 27 |
| homestead | 13 |
| outdoors | 7 |
| scifi | 5 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 28 / 9 |
| Calibration stats runs available | 14 |
| Calibration stats range | 2026-10-18 → 2026-10-31 |
| theme_holdover_cache.json present | True |

## 6. Week over Week

_Counts are the 7 days to each date; rates cover 28 days. Weeks older than the last 8 fold into one row a quarter (counts summed, rates averaged). Weeks marked * were rebuilt from the ratings archive and carry no cost or scorecard data._

| Week | Through | Rated | good | interesting | podcast only | bad | Notes | Shipped wanted % (reweighted) | Gate miss % | News share of ratings % |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-Q2 (3 wk) |  | 432 | 172 | 7 | 0 | 253 | 12 |  | 22.2 | 79.4 |
| 2026-Q3 (9 wk) |  | 857 | 134 | 104 | 0 | 619 | 28 |  | 18.5 | 77.3 |
| 2026-W37* | 2026-09-12 | 135 | 32 | 18 | 0 | 85 | 2 | 40.8 | 15.0 | 76.7 |
| 2026-W38* | 2026-09-19 | 181 | 38 | 19 | 0 | 124 | 5 | 41.2 | 13.8 | 73.1 |
| 2026-W39* | 2026-09-26 | 142 | 31 | 34 | 0 | 77 | 23 | 41.1 | 13.8 | 70.2 |
| 2026-W40* | 2026-10-03 | 188 | 56 | 52 | 0 | 80 | 94 | 43.5 | 15.7 | 62.2 |
| 2026-W41 | 2026-10-10 | 177 | 53 | 29 | 0 | 95 | 84 | 42.5 | 11.8 | 58.3 |
| 2026-W42 | 2026-10-17 | 134 | 32 | 35 | 14 | 53 | 39 | 45.4 | 14.1 | 49.6 |
| 2026-W43 | 2026-10-24 | 84 | 12 | 20 | 23 | 29 | 21 | 44.2 | 16.5 | 42.9 |
| 2026-W44 | 2026-10-31 | 60 | 11 | 13 | 14 | 22 | 11 | 42.4 | 22.6 | 38.0 |

## 7. What Each Score Buys

Graded on the last 4 weeks of ratings (455 rated, 173 news). AUC is the chance a wanted article outscores an unwanted one: 0.5 is a coin flip. The reader model is refit each week on earlier ratings only; it uses the relevance band, so it is not wholly free of the paid pass.

| Signal | Paid by | AUC | AUC, news only |
|---|---|---|---|
| final score | gate + deep_score | 0.678 | 0.739 |
| quality (Q) | deep_score; q_gate elsewhere | 0.704 | 0.59 |
| relevance (R) | deep_score | 0.724 | 0.603 |
| local (L) | deep_score | 0.601 | 0.607 |
| theme fit for that day's theme | theme_ingest / theme / theme_batch | 0.665 | 0.674 |
| reader model | free: your earlier ratings | 0.8 | 0.828 |

### Claude cost by stage (last 7 days)

7 of 7 runs recorded stages; all vendors together est. $1.2271.

| Stage | Calls | Est. cost |
|---|---|---|
| theme | 255 | $0.1988 |
| gate | 205 | $0.1567 |
| deep_score | 93 | $0.1025 |

### Local places: appetite vs. supply

Wanted % among rated articles mentioning the place (baseline 39.9%), against its share of the 1422-article podcast pool.

| Place | Rated | Wanted % | In pool | Pool % |
|---|---|---|---|---|
| williams lake | 82 | 78.0 | 35 | 2.5 |
| cariboo | 107 | 72.0 | 45 | 3.2 |
| quesnel | 48 | 56.2 | 16 | 1.1 |
| 100 mile house | 22 | 68.2 | 4 | 0.3 |
| horsefly | 1 | 100.0 | 1 | 0.1 |
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

## 9. Closed Findings

_A Needs Attention finding that stopped firing, with how long it ran and the calibration changes applied while it was open. "None logged" means a hand fix or drift: check git log for that span. One week open usually means it sat on a threshold._

_None closed yet._

