# Article Review Audit

_Generated: 2026-11-07 18:18 UTC — ratings window 2026-08-10 → 2026-11-07 (rolling 90 days; 2476 rated all time)_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 1533 |
| Rated **bad** — reached you (pipeline failed) | 442 |
| Rated **bad** — correctly rejected (pipeline worked) | 424 |
| Rated **good** | 304 (19.8%) |
| Rated **interesting** (wanted, no specific day) | 288 |
| Rated **podcast only** (for the show, not your feed) | 74 |
| Rated good or interesting (raw, quota-biased) | 38.6% |
| Reweighted good-or-interesting rate of the **shipped** feed | 41.5% (from 88.0% of shipped ratings) |
| Scrub false-negative rate (wanted articles thrown away) | 16.0% of 513 rejects |
| Theme-day corrections (`better_theme`) | 310 (20.2% of day-routed ratings) |
| …where the theme scorer already preferred your day | 168 |
| …where the theme scorer disagreed with you | 142 |
| …of those, actually routed by podcast selection | 0 |
| Category retags | 97 (6.3% of categorized ratings) |

## Needs Attention

_Checks one week of numbers cannot make on its own. **Weeks** counts the weekly audits in a row that reported it; at 3+ it has been seen and not acted on._

| Finding | Detail | Weeks |
|---|---|---|
| ⚠️ 5 categories are unmeasured | Under 20 ratings in 28 days: homelab (12), homestead (5), climate (17), scifi (9), outdoors (7). Their rates are noise, not "fine"; news took 28.5% of the ratings. | 5 |
| ⚠️ The gate threw away 31.2% of the rejects you wanted | 20 of 64 rated rejects in 28 days. Most often, all time: NYT Well (14), MacRumors (9), Outside Online (8), Fast Company (6), The Northern Miner (5), WIRED (5). | 5 |
| ⚠️ Places you want that the pool barely carries | 100 mile house: 69.6% wanted, 6 in the pool (0.4%). Baseline 40.4% wanted. | 5 |
| ⚠️ Block candidates still unblocked | Live for the Outdoors (Country Walking): n ≥ 8 with nothing wanted. Block them in filters.json or rate why not. | 5 |
| ⚠️ Local places with almost no ratings | Under 5 ratings ever: horsefly. | 3 |

### Sampling strata

The review feed is a **quota** sample: a fixed handful from each score band plus up to 10 scrub rejects. Rates within a stratum are unbiased; the corpus-wide rate is not, because half the ratings come from the reject pile. Reweight before comparing anything across strata.

| Stratum | n | good | interesting | podcast only | bad | % good | % good+int |
|---|---|---|---|---|---|---|---|
| unfiltered | 513 | 24 | 58 | 7 | 424 | 4.7 | 16.0 |
| mid | 279 | 87 | 52 | 2 | 138 | 31.2 | 49.8 |
| border | 194 | 44 | 43 | 0 | 107 | 22.7 | 44.8 |
| near_miss | 167 | 20 | 43 | 46 | 58 | 12.0 | 37.7 |
| promising | 153 | 53 | 52 | 6 | 42 | 34.6 | 68.6 |
| high | 73 | 48 | 17 | 0 | 7 | 65.8 | 89.0 |
| low | 65 | 4 | 9 | 0 | 52 | 6.2 | 20.0 |
| in_feed | 44 | 22 | 6 | 11 | 5 | 50.0 | 63.6 |
| floor_fill | 36 | 2 | 7 | 0 | 27 | 5.6 | 25.0 |
| wildcard | 9 | 0 | 1 | 2 | 6 | 0.0 | 11.1 |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 304 | 61.0 | 60.0 | 44.1 | 45.7 |
| interesting | 288 | 48.6 | 48.0 | 33.7 | 31.6 |
| podcast_only | 74 | 51.0 | 48.0 | 58 | 50.2 |
| bad | 866 | 38.9 | 37.0 | 15.7 | 12.6 |

### Precision by score band

| Score band | n | good | interesting | bad | % good | % good+int | % bad |
|---|---|---|---|---|---|---|---|
| 80-100 | 98 | 62 | 20 | 11 | 63.3 | 83.7 | 11.2 |
| 60-79 | 301 | 93 | 55 | 136 | 30.9 | 49.2 | 45.2 |
| 40-59 | 558 | 120 | 134 | 267 | 21.5 | 45.5 | 47.8 |
| 20-39 | 400 | 24 | 61 | 300 | 6.0 | 21.2 | 75.0 |
| 0-19 | 176 | 5 | 18 | 152 | 2.8 | 13.1 | 86.4 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **25** (manually lowered 20 → 13 on 2026-06-24).

`interesting` articles score low on relevance, so a higher floor costs them first. Weigh **% of bad cut** against **% of good+int lost**.

| Floor | Bad cut | % of bad | Good lost | % of good | Interesting lost | % of int | % of good+int |
|---|---|---|---|---|---|---|---|
| 13 | 0 | 0.0 | 0 | 0.0 | 0 | 0.0 | 0.0 |
| 15 | 47 | 5.4 | 1 | 0.3 | 4 | 1.4 | 0.8 |
| 20 | 152 | 17.6 | 5 | 1.6 | 18 | 6.2 | 3.9 |
| 25 | 229 | 26.4 | 9 | 3.0 | 26 | 9.0 | 5.9 |
| 30 | 358 | 41.3 | 18 | 5.9 | 46 | 16.0 | 10.8 |
| 35 | 419 | 48.4 | 23 | 7.6 | 61 | 21.2 | 14.2 |
| 40 | 452 | 52.2 | 29 | 9.5 | 79 | 27.4 | 18.2 |
| 45 | 511 | 59.0 | 45 | 14.8 | 103 | 35.8 | 25.0 |
| 50 | 682 | 78.8 | 135 | 44.4 | 202 | 70.1 | 56.9 |
| 60 | 719 | 83.0 | 149 | 49.0 | 213 | 74.0 | 61.1 |

### By category

| Category | n | good | interesting | bad | % good+int | % bad |
|---|---|---|---|---|---|---|
| news | 786 | 72 | 79 | 620 | 19.2 | 78.9 |
| ai-tech | 185 | 32 | 89 | 59 | 65.4 | 31.9 |
| local | 135 | 72 | 21 | 33 | 68.9 | 24.4 |
| wellness | 128 | 34 | 24 | 62 | 45.3 | 48.4 |
| science | 80 | 37 | 9 | 8 | 57.5 | 10.0 |
| design | 63 | 4 | 25 | 33 | 46.0 | 52.4 |
| climate | 47 | 22 | 8 | 14 | 63.8 | 29.8 |
| homelab | 43 | 15 | 13 | 11 | 65.1 | 25.6 |
| scifi | 24 | 1 | 9 | 14 | 41.7 | 58.3 |
| outdoors | 23 | 5 | 6 | 11 | 47.8 | 47.8 |
| homestead | 19 | 10 | 5 | 1 | 78.9 | 5.3 |

### Sources (≥ 5 ratings)

**Highest good+interesting rate**

| Source | n | good | interesting | bad | % good+int |
|---|---|---|---|---|---|
| Bicycling | 6 | 4 | 2 | 0 | 100.0 |
| Cariboo Signals Reviews | 5 | 2 | 3 | 0 | 100.0 |
| MacRumors | 6 | 2 | 3 | 1 | 83.3 |
| The Tyee | 28 | 17 | 6 | 2 | 82.1 |
| Vancouver Sun | 10 | 4 | 4 | 1 | 80.0 |
| APTN News | 5 | 3 | 1 | 0 | 80.0 |
| XDA Developers | 5 | 3 | 1 | 0 | 80.0 |
| Neuroscience News | 5 | 3 | 1 | 0 | 80.0 |
| New Atlas | 13 | 5 | 5 | 2 | 76.9 |
| Williams Lake Tribune | 50 | 30 | 7 | 9 | 74.0 |

**Lowest good+interesting rate** — block candidate only at n ≥ 8 with zero positives of any kind

| Source | n | good | interesting | bad | % good+int | Block candidate |
|---|---|---|---|---|---|---|
| Live for the Outdoors (Country Walking) | 8 | 0 | 0 | 8 | 0.0 | yes |
| My East Kootenay Now | 6 | 0 | 0 | 6 | 0.0 |  |
| Country Guide | 6 | 0 | 0 | 6 | 0.0 |  |
| Edge (GamesRadar) | 53 | 0 | 2 | 51 | 3.8 |  |
| NYT Top Stories | 51 | 2 | 2 | 46 | 7.8 |  |
| Ideal Home (Country Homes & Interiors) | 32 | 0 | 3 | 29 | 9.4 |  |
| Country Life | 23 | 1 | 2 | 20 | 13.0 |  |
| Boing Boing | 15 | 0 | 2 | 13 | 13.3 |  |
| Domino | 21 | 0 | 3 | 18 | 14.3 |  |
| KFF Health News | 7 | 1 | 0 | 6 | 14.3 |  |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 102 | 131 | 639 |
| analysis | 73 | 68 | 64 |
| breaking | 59 | 33 | 67 |
| feature | 46 | 35 | 62 |
| opinion | 7 | 7 | 17 |
| news | 13 | 8 | 10 |
| recap | 0 | 2 | 5 |
| fluff | 3 | 2 | 0 |
| investigation | 0 | 1 | 1 |
| wire | 1 | 1 | 0 |
| essay | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 44 | 43 | 107 |
| low | 4 | 9 | 52 |
| unfiltered | 24 | 58 | 424 |
| high | 48 | 17 | 7 |
| mid | 87 | 52 | 138 |
| floor_fill | 2 | 7 | 27 |
| promising | 53 | 52 | 42 |
| near_miss | 20 | 43 | 58 |
| in_feed | 22 | 6 | 5 |
| wildcard | 0 | 1 | 6 |

### Filler trend (from the corpus alignment reports, kept in weekly_metrics.jsonl)

| Week | Articles analysed | Filler | Filler % |
|---|---|---|---|
| 2026-Q2 (3 wk) | 2234 | 170 | 8 |
| 2026-Q3 (9 wk) | 12332 | 1146 | 9 |
| 2026-W38 | 1397 | 147 | 11 |
| 2026-W39 | 1469 | 182 | 12 |
| 2026-W40 | 1340 | 162 | 12 |
| 2026-W41 | 467 | 40 | 9 |
| 2026-W42 | 1333 | 56 | 4 |
| 2026-W43 | 1318 | 81 | 6 |
| 2026-W44 | 1296 | 0 | 0 |
| 2026-W45 | 1322 | 3 | 0 |

## 3. Theme-Bucket Routing Accuracy

Of **1533** ratings tied to an aired day, you corrected the day on **310** (20.2%). Additionally 334 articles were approved for other days.

### Per theme day

`% day fit` counts good + podcast only (the verdicts that name days). `% good+int` is feed fit: wanted in your feed, any day or none.

| Day | Theme | n | good | interesting | podcast only | bad | % day fit | % good+int | Corrected away |
|---|---|---|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 264 | 48 | 66 | 12 | 138 | 22.7 | 43.2 | 50 |
| tuesday | Working Lands & Industry | 250 | 44 | 42 | 11 | 153 | 22.0 | 34.4 | 43 |
| wednesday | Repair Culture & Practical Tech | 226 | 46 | 34 | 6 | 140 | 23.0 | 35.4 | 47 |
| thursday | Indigenous Lands & Innovation | 232 | 42 | 41 | 13 | 136 | 23.7 | 35.8 | 50 |
| friday | Wild Spaces & Outdoor Life | 199 | 45 | 35 | 10 | 109 | 27.6 | 40.2 | 50 |
| saturday | Cariboo Local Affairs | 175 | 47 | 35 | 5 | 88 | 29.7 | 46.9 | 39 |
| sunday | Science, Wonder & the Natural World | 187 | 32 | 35 | 17 | 102 | 26.2 | 35.8 | 31 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 10 | 8 | 2 | 1 | 11 | 18 |
| tuesday | 6 |  | 5 | 2 | 2 | 8 | 20 |
| wednesday | 5 | 9 |  | 2 | 5 | 11 | 15 |
| thursday | 4 | 9 | 7 |  | 1 | 7 | 22 |
| friday | 4 | 9 | 5 | 3 |  | 11 | 18 |
| saturday | 4 | 5 | 5 | 4 | 2 |  | 19 |
| sunday | 3 | 8 | 9 |  | 3 | 8 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 168 |
| Theme scorer disagreed with you (scoring miss) | 142 |
| Theme scores missing on the rating | 0 |

## 3b. Category Retag Accuracy

Of **1533** ratings carrying a confirmed/retagged category, you retagged **97** (6.3%) to a different category.

### Category → category correction matrix (shown → corrected)

| Shown | Corrected to | Count |
|---|---|---|
| news | ai-tech | 23 |
| news | homelab | 11 |
| news | science | 9 |
| news | outdoors | 8 |
| news | homestead | 8 |
| news | scifi | 6 |
| news | design | 6 |
| news | climate | 5 |
| news | wellness | 4 |
| news | local | 4 |
| science | wellness | 3 |
| science | news | 1 |
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
| 2026-Q3 (10 wk) | 79 | 1353 | 79 |
| 2026-W38 | 7 | 1635 | 95 |
| 2026-W39 | 8 | 1363 | 74 |
| 2026-W40 | 7 | 1354 | 81 |
| 2026-W41 | 7 | 1367 | 84 |
| 2026-W42 | 7 | 1364 | 80 |
| 2026-W43 | 7 | 1421 | 84 |
| 2026-W44 | 7 | 1492 | 85 |
| 2026-W45 | 5 | 1675 | 90 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-10-25T06:00:53.460455+00:00 | 1214 | 966 | 71 | 638 | 159 |
| 2026-10-26T06:01:01.288019+00:00 | 865 | 697 | 75 | 443 | 99 |
| 2026-10-27T06:00:53.007214+00:00 | 1336 | 1055 | 84 | 684 | 185 |
| 2026-10-28T06:00:47.270840+00:00 | 1699 | 1341 | 89 | 930 | 182 |
| 2026-10-29T06:00:53.599263+00:00 | 1739 | 1350 | 81 | 916 | 189 |
| 2026-10-30T06:00:56.669293+00:00 | 1779 | 1429 | 91 | 938 | 226 |
| 2026-10-31T06:00:48.837686+00:00 | 1664 | 1290 | 93 | 872 | 202 |
| 2026-11-01T06:00:54.201534+00:00 | 1331 | 1042 | 77 | 656 | 198 |
| 2026-11-02T06:00:51.242465+00:00 | 897 | 717 | 79 | 385 | 155 |
| 2026-11-03T06:00:57.863283+00:00 | 1392 | 1097 | 92 | 634 | 254 |
| 2026-11-04T06:01:01.726233+00:00 | 1723 | 1310 | 86 | 794 | 292 |
| 2026-11-05T06:00:51.269578+00:00 | 1750 | 1344 | 95 | 869 | 257 |
| 2026-11-06T06:00:54.885401+00:00 | 1764 | 1356 | 89 | 860 | 282 |
| 2026-11-07T06:00:49.721641+00:00 | 1744 | 1358 | 86 | 877 | 254 |

### Current category feed sizes

| Feed | Items |
|---|---|
| news | 109 |
| ai-tech | 92 |
| wellness | 55 |
| climate | 54 |
| local | 45 |
| science | 41 |
| homelab | 36 |
| design | 27 |
| homestead | 20 |
| outdoors | 7 |
| scifi | 5 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 29 / 9 |
| Calibration stats runs available | 14 |
| Calibration stats range | 2026-10-25 → 2026-11-07 |
| theme_holdover_cache.json present | True |

## 6. Week over Week

_Counts are the 7 days to each date; rates cover 28 days. Weeks older than the last 8 fold into one row a quarter (counts summed, rates averaged). Weeks marked * were rebuilt from the ratings archive and carry no cost or scorecard data._

| Week | Through | Rated | good | interesting | podcast only | bad | Notes | Shipped wanted % (reweighted) | Gate miss % | News share of ratings % |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-Q2 (3 wk) |  | 432 | 172 | 7 | 0 | 253 | 12 |  | 22.2 | 79.4 |
| 2026-Q3 (10 wk) |  | 992 | 166 | 122 | 0 | 704 | 30 | 40.8 | 18.2 | 77.2 |
| 2026-W38* | 2026-09-19 | 181 | 38 | 19 | 0 | 124 | 5 | 41.2 | 13.8 | 73.1 |
| 2026-W39* | 2026-09-26 | 142 | 31 | 34 | 0 | 77 | 23 | 41.1 | 13.8 | 70.2 |
| 2026-W40* | 2026-10-03 | 188 | 56 | 52 | 0 | 80 | 94 | 43.5 | 15.7 | 62.2 |
| 2026-W41 | 2026-10-10 | 177 | 53 | 29 | 0 | 95 | 84 | 42.5 | 11.8 | 58.3 |
| 2026-W42 | 2026-10-17 | 134 | 32 | 35 | 14 | 53 | 39 | 45.4 | 14.1 | 49.6 |
| 2026-W43 | 2026-10-24 | 84 | 12 | 20 | 23 | 29 | 21 | 44.2 | 16.5 | 42.9 |
| 2026-W44 | 2026-10-31 | 60 | 11 | 13 | 14 | 22 | 11 | 42.4 | 22.6 | 38.0 |
| 2026-W45 | 2026-11-07 | 84 | 12 | 11 | 23 | 38 | 32 | 40.6 | 31.2 | 28.5 |

## 7. What Each Score Buys

Graded on the last 4 weeks of ratings (362 rated, 103 news). AUC is the chance a wanted article outscores an unwanted one: 0.5 is a coin flip. The reader model is refit each week on earlier ratings only; it uses the relevance band, so it is not wholly free of the paid pass.

| Signal | Paid by | AUC | AUC, news only |
|---|---|---|---|
| final score | gate + deep_score | 0.669 | 0.692 |
| quality (Q) | deep_score; q_gate elsewhere | 0.679 | 0.625 |
| relevance (R) | deep_score | 0.721 | 0.654 |
| local (L) | deep_score | 0.593 | 0.67 |
| theme fit for that day's theme | theme_ingest / theme / theme_batch | 0.677 | 0.682 |
| reader model | free: your earlier ratings | 0.785 | 0.827 |

### Claude cost by stage (last 7 days)

7 of 7 runs recorded stages; all vendors together est. $1.2918.

| Stage | Calls | Est. cost |
|---|---|---|
| theme | 243 | $0.1848 |
| gate | 219 | $0.1701 |
| deep_score | 94 | $0.1024 |

### Local places: appetite vs. supply

Wanted % among rated articles mentioning the place (baseline 40.4%), against its share of the 1469-article podcast pool.

| Place | Rated | Wanted % | In pool | Pool % |
|---|---|---|---|---|
| williams lake | 87 | 77.0 | 36 | 2.5 |
| cariboo | 113 | 72.6 | 37 | 2.5 |
| quesnel | 50 | 54.0 | 14 | 1.0 |
| 100 mile house | 23 | 69.6 | 6 | 0.4 |
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

