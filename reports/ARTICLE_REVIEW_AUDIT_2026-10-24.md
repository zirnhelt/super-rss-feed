# Article Review Audit

_Generated: 2026-10-24 16:51 UTC — ratings window 2026-07-27 → 2026-10-24 (rolling 90 days; 2332 rated all time)_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 1591 |
| Rated **bad** — reached you (pipeline failed) | 427 |
| Rated **bad** — correctly rejected (pipeline worked) | 521 |
| Rated **good** | 310 (19.5%) |
| Rated **interesting** (wanted, no specific day) | 294 |
| Rated **podcast only** (for the show, not your feed) | 37 |
| Rated good or interesting (raw, quota-biased) | 38.0% |
| Reweighted good-or-interesting rate of the **shipped** feed | 43.0% (from 80.8% of shipped ratings) |
| Scrub false-negative rate (wanted articles thrown away) | 16.4% of 628 rejects |
| Theme-day corrections (`better_theme`) | 286 (18.0% of day-routed ratings) |
| …where the theme scorer already preferred your day | 145 |
| …where the theme scorer disagreed with you | 141 |
| …of those, actually routed by podcast selection | 0 |
| Category retags | 116 (7.3% of categorized ratings) |

## Needs Attention

_Checks one week of numbers cannot make on its own. **Weeks** counts the weekly audits in a row that reported it; at 3+ it has been seen and not acted on._

| Finding | Detail | Weeks |
|---|---|---|
| ⚠️ 4 categories are unmeasured | Under 20 ratings in 28 days: homelab (17), homestead (8), scifi (8), outdoors (10). Their rates are noise, not "fine"; news took 42.9% of the ratings. | 3 |
| ⚠️ The gate threw away 16.5% of the rejects you wanted | 18 of 109 rated rejects in 28 days. Most often, all time: NYT Well (14), MacRumors (9), Outside Online (8), Fast Company (6), The Northern Miner (5), The Marginalian (5). | 3 |
| ⚠️ Places you want that the pool barely carries | quesnel: 57.8% wanted, 12 in the pool (0.8%), 100 mile house: 68.2% wanted, 2 in the pool (0.1%). Baseline 39.3% wanted. | 3 |
| ⚠️ Block candidates still unblocked | Live for the Outdoors (Country Walking): n ≥ 8 with nothing wanted. Block them in filters.json or rate why not. | 3 |
| Local places with almost no ratings | Under 5 ratings ever: horsefly, lac la hache. | 1 |

### Sampling strata

The review feed is a **quota** sample: a fixed handful from each score band plus up to 10 scrub rejects. Rates within a stratum are unbiased; the corpus-wide rate is not, because half the ratings come from the reject pile. Reweight before comparing anything across strata.

| Stratum | n | good | interesting | podcast only | bad | % good | % good+int |
|---|---|---|---|---|---|---|---|
| unfiltered | 628 | 31 | 72 | 3 | 521 | 4.9 | 16.4 |
| mid | 279 | 87 | 52 | 2 | 138 | 31.2 | 49.8 |
| border | 240 | 58 | 57 | 0 | 125 | 24.2 | 47.9 |
| promising | 153 | 53 | 52 | 6 | 42 | 34.6 | 68.6 |
| low | 82 | 10 | 10 | 0 | 62 | 12.2 | 24.4 |
| near_miss | 80 | 12 | 23 | 23 | 22 | 15.0 | 43.8 |
| high | 73 | 48 | 17 | 0 | 7 | 65.8 | 89.0 |
| floor_fill | 36 | 2 | 7 | 0 | 27 | 5.6 | 25.0 |
| in_feed | 20 | 9 | 4 | 3 | 4 | 45.0 | 65.0 |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 310 | 58.4 | 49.0 | 41.0 | 42.2 |
| interesting | 294 | 47.6 | 48.0 | 31.1 | 29.3 |
| podcast_only | 37 | 49.4 | 47 | 56.8 | 48.4 |
| bad | 948 | 37.4 | 33.0 | 12.8 | 10.3 |

### Precision by score band

| Score band | n | good | interesting | bad | % good | % good+int | % bad |
|---|---|---|---|---|---|---|---|
| 80-100 | 89 | 58 | 19 | 10 | 65.2 | 86.5 | 11.2 |
| 60-79 | 273 | 82 | 53 | 131 | 30.0 | 49.5 | 48.0 |
| 40-59 | 564 | 130 | 133 | 281 | 23.0 | 46.6 | 49.8 |
| 20-39 | 446 | 32 | 67 | 338 | 7.2 | 22.2 | 75.8 |
| 0-19 | 219 | 8 | 22 | 188 | 3.7 | 13.7 | 85.8 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **25** (manually lowered 20 → 13 on 2026-06-24).

`interesting` articles score low on relevance, so a higher floor costs them first. Weigh **% of bad cut** against **% of good+int lost**.

| Floor | Bad cut | % of bad | Good lost | % of good | Interesting lost | % of int | % of good+int |
|---|---|---|---|---|---|---|---|
| 13 | 0 | 0.0 | 0 | 0.0 | 0 | 0.0 | 0.0 |
| 15 | 49 | 5.2 | 1 | 0.3 | 6 | 2.0 | 1.2 |
| 20 | 188 | 19.8 | 8 | 2.6 | 22 | 7.5 | 5.0 |
| 25 | 282 | 29.7 | 15 | 4.8 | 32 | 10.9 | 7.8 |
| 30 | 437 | 46.1 | 30 | 9.7 | 58 | 19.7 | 14.6 |
| 35 | 495 | 52.2 | 35 | 11.3 | 74 | 25.2 | 18.0 |
| 40 | 526 | 55.5 | 40 | 12.9 | 89 | 30.3 | 21.4 |
| 45 | 587 | 61.9 | 56 | 18.1 | 105 | 35.7 | 26.7 |
| 50 | 776 | 81.9 | 160 | 51.6 | 214 | 72.8 | 61.9 |
| 60 | 807 | 85.1 | 170 | 54.8 | 222 | 75.5 | 64.9 |

### By category

| Category | n | good | interesting | bad | % good+int | % bad |
|---|---|---|---|---|---|---|
| news | 898 | 67 | 90 | 735 | 17.5 | 81.8 |
| ai-tech | 181 | 42 | 83 | 55 | 69.1 | 30.4 |
| wellness | 129 | 37 | 27 | 58 | 49.6 | 45.0 |
| local | 119 | 67 | 20 | 28 | 73.1 | 23.5 |
| science | 66 | 37 | 7 | 8 | 66.7 | 12.1 |
| design | 51 | 4 | 23 | 24 | 52.9 | 47.1 |
| climate | 47 | 23 | 10 | 11 | 70.2 | 23.4 |
| homelab | 42 | 17 | 14 | 9 | 73.8 | 21.4 |
| outdoors | 22 | 5 | 6 | 10 | 50.0 | 45.5 |
| scifi | 19 | 1 | 9 | 9 | 52.6 | 47.4 |
| homestead | 17 | 10 | 5 | 1 | 88.2 | 5.9 |

### Sources (≥ 5 ratings)

**Highest good+interesting rate**

| Source | n | good | interesting | bad | % good+int |
|---|---|---|---|---|---|
| Cariboo Signals Reviews | 5 | 2 | 3 | 0 | 100.0 |
| APTN News | 7 | 4 | 2 | 0 | 85.7 |
| Bicycling | 7 | 4 | 2 | 1 | 85.7 |
| The Tyee | 24 | 14 | 6 | 3 | 83.3 |
| Neuroscience News | 5 | 3 | 1 | 0 | 80.0 |
| Williams Lake Tribune | 41 | 25 | 6 | 8 | 75.6 |
| My Cariboo Now | 36 | 19 | 8 | 8 | 75.0 |
| ScienceDaily | 26 | 15 | 4 | 4 | 73.1 |
| The Walrus | 7 | 1 | 4 | 2 | 71.4 |
| Dezeen | 7 | 0 | 5 | 2 | 71.4 |

**Lowest good+interesting rate** — block candidate only at n ≥ 8 with zero positives of any kind

| Source | n | good | interesting | bad | % good+int | Block candidate |
|---|---|---|---|---|---|---|
| Live for the Outdoors (Country Walking) | 9 | 0 | 0 | 9 | 0.0 | yes |
| Country Guide | 6 | 0 | 0 | 6 | 0.0 |  |
| Edge (GamesRadar) | 52 | 0 | 2 | 50 | 3.8 |  |
| Ideal Home (Country Homes & Interiors) | 33 | 0 | 3 | 30 | 9.1 |  |
| NYT Top Stories | 53 | 2 | 3 | 47 | 9.4 |  |
| Country Life | 24 | 1 | 2 | 21 | 12.5 |  |
| Domino | 21 | 0 | 3 | 18 | 14.3 |  |
| Neowin | 7 | 1 | 0 | 6 | 14.3 |  |
| Maclean's | 7 | 1 | 0 | 6 | 14.3 |  |
| Dwell | 19 | 2 | 1 | 16 | 15.8 |  |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 115 | 146 | 745 |
| analysis | 68 | 63 | 59 |
| breaking | 58 | 32 | 57 |
| feature | 43 | 34 | 55 |
| news | 14 | 8 | 12 |
| opinion | 7 | 5 | 12 |
| recap | 0 | 2 | 6 |
| fluff | 3 | 2 | 0 |
| wire | 2 | 1 | 0 |
| investigation | 0 | 1 | 1 |
| essay | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 58 | 57 | 125 |
| low | 10 | 10 | 62 |
| unfiltered | 31 | 72 | 521 |
| high | 48 | 17 | 7 |
| mid | 87 | 52 | 138 |
| floor_fill | 2 | 7 | 27 |
| promising | 53 | 52 | 42 |
| near_miss | 12 | 23 | 22 |
| in_feed | 9 | 4 | 4 |

### Filler trend (from the corpus alignment reports, kept in weekly_metrics.jsonl)

| Week | Articles analysed | Filler | Filler % |
|---|---|---|---|
| 2026-Q2 (3 wk) | 2234 | 170 | 8 |
| 2026-Q3 (7 wk) | 9098 | 846 | 9 |
| 2026-W36 | 1857 | 176 | 9 |
| 2026-W37 | 1377 | 124 | 9 |
| 2026-W38 | 1397 | 147 | 11 |
| 2026-W39 | 1469 | 182 | 12 |
| 2026-W40 | 1340 | 162 | 12 |
| 2026-W41 | 467 | 40 | 9 |
| 2026-W42 | 1333 | 56 | 4 |
| 2026-W43 | 1318 | 81 | 6 |

## 3. Theme-Bucket Routing Accuracy

Of **1591** ratings tied to an aired day, you corrected the day on **286** (18.0%). Additionally 307 articles were approved for other days.

### Per theme day

`% day fit` counts good + podcast only (the verdicts that name days). `% good+int` is feed fit: wanted in your feed, any day or none.

| Day | Theme | n | good | interesting | podcast only | bad | % day fit | % good+int | Corrected away |
|---|---|---|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 297 | 46 | 66 | 9 | 176 | 18.5 | 37.7 | 46 |
| tuesday | Working Lands & Industry | 256 | 48 | 40 | 4 | 164 | 20.3 | 34.4 | 39 |
| wednesday | Repair Culture & Practical Tech | 246 | 47 | 42 | 4 | 153 | 20.7 | 36.2 | 46 |
| thursday | Indigenous Lands & Innovation | 236 | 47 | 44 | 7 | 138 | 22.9 | 38.6 | 50 |
| friday | Wild Spaces & Outdoor Life | 213 | 45 | 41 | 7 | 119 | 24.4 | 40.4 | 48 |
| saturday | Cariboo Local Affairs | 180 | 45 | 29 | 1 | 105 | 25.6 | 41.1 | 36 |
| sunday | Science, Wonder & the Natural World | 163 | 32 | 32 | 5 | 93 | 22.7 | 39.3 | 21 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 9 | 11 | 1 | 2 | 7 | 16 |
| tuesday | 4 |  | 4 | 2 | 4 | 7 | 18 |
| wednesday | 4 | 9 |  | 2 | 6 | 11 | 14 |
| thursday | 4 | 9 | 5 |  | 1 | 7 | 24 |
| friday | 4 | 9 | 5 | 3 |  | 10 | 17 |
| saturday | 2 | 5 | 5 | 4 | 4 |  | 16 |
| sunday | 2 | 5 | 7 |  | 2 | 5 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 145 |
| Theme scorer disagreed with you (scoring miss) | 141 |
| Theme scores missing on the rating | 0 |

## 3b. Category Retag Accuracy

Of **1591** ratings carrying a confirmed/retagged category, you retagged **116** (7.3%) to a different category.

### Category → category correction matrix (shown → corrected)

| Shown | Corrected to | Count |
|---|---|---|
| news | ai-tech | 34 |
| news | homelab | 13 |
| news | science | 9 |
| news | outdoors | 8 |
| news | homestead | 8 |
| news | wellness | 6 |
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
| 2026-Q1 (6 wk) | 105 | 872 | 198 |
| 2026-Q2 (13 wk) | 193 | 1012 | 102 |
| 2026-Q3 (8 wk) | 62 | 1312 | 76 |
| 2026-W36 | 10 | 1469 | 88 |
| 2026-W37 | 7 | 1557 | 93 |
| 2026-W38 | 7 | 1635 | 95 |
| 2026-W39 | 8 | 1363 | 74 |
| 2026-W40 | 7 | 1354 | 81 |
| 2026-W41 | 7 | 1367 | 84 |
| 2026-W42 | 7 | 1364 | 80 |
| 2026-W43 | 5 | 1574 | 89 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-10-11T04:01:14.442081+00:00 | 1213 | 936 | 80 | 673 | 100 |
| 2026-10-12T04:01:23.209937+00:00 | 804 | 607 | 76 | 419 | 55 |
| 2026-10-13T04:01:10.282845+00:00 | 1052 | 854 | 86 | 653 | 57 |
| 2026-10-14T04:01:01.447572+00:00 | 1493 | 1131 | 81 | 813 | 149 |
| 2026-10-15T04:01:12.929108+00:00 | 1661 | 1273 | 87 | 902 | 187 |
| 2026-10-16T04:01:00.341811+00:00 | 1653 | 1263 | 81 | 912 | 165 |
| 2026-10-17T04:01:54.851437+00:00 | 1634 | 1249 | 77 | 842 | 202 |
| 2026-10-18T04:01:30.784791+00:00 | 1186 | 902 | 73 | 556 | 188 |
| 2026-10-19T06:00:52.957625+00:00 | 870 | 638 | 76 | 402 | 98 |
| 2026-10-20T06:01:01.018722+00:00 | 1288 | 995 | 87 | 661 | 146 |
| 2026-10-21T06:00:50.667801+00:00 | 1601 | 1222 | 85 | 845 | 152 |
| 2026-10-22T06:00:51.678633+00:00 | 1617 | 1239 | 93 | 841 | 181 |
| 2026-10-23T06:01:02.570687+00:00 | 1705 | 1378 | 93 | 991 | 186 |
| 2026-10-24T06:00:57.289163+00:00 | 1657 | 1323 | 87 | 908 | 216 |

### Current category feed sizes

| Feed | Items |
|---|---|
| news | 121 |
| ai-tech | 90 |
| wellness | 55 |
| climate | 48 |
| local | 48 |
| science | 43 |
| homelab | 32 |
| design | 29 |
| homestead | 19 |
| outdoors | 19 |
| scifi | 9 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 27 / 9 |
| Calibration stats runs available | 14 |
| Calibration stats range | 2026-10-11 → 2026-10-24 |
| theme_holdover_cache.json present | True |

## 6. Week over Week

_Counts are the 7 days to each date; rates cover 28 days. Weeks older than the last 8 fold into one row a quarter (counts summed, rates averaged). Weeks marked * were rebuilt from the ratings archive and carry no cost or scorecard data._

| Week | Through | Rated | good | interesting | podcast only | bad | Notes | Shipped wanted % (reweighted) | Gate miss % | News share of ratings % |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-Q2 (3 wk) |  | 432 | 172 | 7 | 0 | 253 | 12 |  | 22.2 | 79.4 |
| 2026-Q3 (8 wk) |  | 768 | 131 | 95 | 0 | 542 | 27 |  | 18.8 | 77.1 |
| 2026-W36* | 2026-09-05 | 89 | 3 | 9 | 0 | 77 | 1 |  | 16.2 | 78.7 |
| 2026-W37* | 2026-09-12 | 135 | 32 | 18 | 0 | 85 | 2 | 40.8 | 15.0 | 76.7 |
| 2026-W38* | 2026-09-19 | 181 | 38 | 19 | 0 | 124 | 5 | 41.2 | 13.8 | 73.1 |
| 2026-W39* | 2026-09-26 | 142 | 31 | 34 | 0 | 77 | 23 | 41.1 | 13.8 | 70.2 |
| 2026-W40* | 2026-10-03 | 188 | 56 | 52 | 0 | 80 | 94 | 43.5 | 15.7 | 62.2 |
| 2026-W41 | 2026-10-10 | 177 | 53 | 29 | 0 | 95 | 84 | 42.5 | 11.8 | 58.3 |
| 2026-W42 | 2026-10-17 | 134 | 32 | 35 | 14 | 53 | 39 | 45.4 | 14.1 | 49.6 |
| 2026-W43 | 2026-10-24 | 84 | 12 | 20 | 23 | 29 | 21 | 44.2 | 16.5 | 42.9 |

## 7. What Each Score Buys

Graded on the last 4 weeks of ratings (583 rated, 250 news). AUC is the chance a wanted article outscores an unwanted one: 0.5 is a coin flip. The reader model is refit each week on earlier ratings only; it uses the relevance band, so it is not wholly free of the paid pass.

| Signal | Paid by | AUC | AUC, news only |
|---|---|---|---|
| final score | gate + deep_score | 0.675 | 0.724 |
| quality (Q) | deep_score; q_gate elsewhere | 0.708 | 0.571 |
| relevance (R) | deep_score | 0.726 | 0.579 |
| local (L) | deep_score | 0.601 | 0.577 |
| theme fit for that day's theme | theme_ingest / theme / theme_batch | 0.66 | 0.664 |
| reader model | free: your earlier ratings | 0.808 | 0.81 |

### Claude cost by stage (last 7 days)

7 of 7 runs recorded stages; all vendors together est. $1.1691.

| Stage | Calls | Est. cost |
|---|---|---|
| gate | 198 | $0.1497 |
| deep_score | 84 | $0.0957 |
| theme | 44 | $0.0522 |

### Local places: appetite vs. supply

Wanted % among rated articles mentioning the place (baseline 39.3%), against its share of the 1457-article podcast pool.

| Place | Rated | Wanted % | In pool | Pool % |
|---|---|---|---|---|
| williams lake | 77 | 76.6 | 35 | 2.4 |
| cariboo | 100 | 73.0 | 35 | 2.4 |
| quesnel | 45 | 57.8 | 12 | 0.8 |
| 100 mile house | 22 | 68.2 | 2 | 0.1 |
| horsefly | 1 | 100.0 | 2 | 0.1 |
| lac la hache | 1 | 100.0 | 2 | 0.1 |

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

