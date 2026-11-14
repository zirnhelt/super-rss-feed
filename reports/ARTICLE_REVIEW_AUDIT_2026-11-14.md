# Article Review Audit

_Generated: 2026-11-14 18:54 UTC — ratings window 2026-08-17 → 2026-11-14 (rolling 90 days; 2560 rated all time)_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 1510 |
| Rated **bad** — reached you (pipeline failed) | 442 |
| Rated **bad** — correctly rejected (pipeline worked) | 379 |
| Rated **good** | 306 (20.3%) |
| Rated **interesting** (wanted, no specific day) | 285 |
| Rated **podcast only** (for the show, not your feed) | 97 |
| Rated good or interesting (raw, quota-biased) | 39.1% |
| Reweighted good-or-interesting rate of the **shipped** feed | 41.5% (from 91.9% of shipped ratings) |
| Scrub false-negative rate (wanted articles thrown away) | 14.9% of 457 rejects |
| Theme-day corrections (`better_theme`) | 337 (22.3% of day-routed ratings) |
| …where the theme scorer already preferred your day | 185 |
| …where the theme scorer disagreed with you | 152 |
| …of those, actually routed by podcast selection | 0 |
| Category retags | 86 (5.7% of categorized ratings) |

## Needs Attention

_Checks one week of numbers cannot make on its own. **Weeks** counts the weekly audits in a row that reported it; at 3+ it has been seen and not acted on._

| Finding | Detail | Weeks |
|---|---|---|
| ⚠️ 5 categories are unmeasured | Under 20 ratings in 28 days: homelab (10), homestead (3), scifi (9), outdoors (2), miscellany (0). Their rates are noise, not "fine"; news took 24.4% of the ratings. | 6 |
| ⚠️ The gate threw away 32.7% of the rejects you wanted | 17 of 52 rated rejects in 28 days. Most often, all time: NYT Well (14), MacRumors (9), Outside Online (8), Fast Company (6), The Northern Miner (5), WIRED (5). | 6 |
| ⚠️ Places you want that the pool barely carries | 100 mile house: 69.6% wanted, 0 in the pool (0.0%). Baseline 41.2% wanted. | 6 |
| ⚠️ Local places with almost no ratings | Under 5 ratings ever: lac la hache. | 4 |
| The feeds missed 85.8% of the week's headlines | 343 of 400 widely covered Kagi News stories in 7 runs reached no feed (dedup 30, gate_reject 23, show_only 4, ranked_out 286). gate_reject is the gate's junk flag, show_only a [show] line outside news, ranked_out the slots or the score. | 1 |
| The Anthropic price table is stale | CLAUDE.md prices were checked 37 days ago. Refresh them before a cost decision. | 1 |

### Sampling strata

The review feed is a **quota** sample: a fixed handful from each score band plus up to 10 scrub rejects. Rates within a stratum are unbiased; the corpus-wide rate is not, because half the ratings come from the reject pile. Reweight before comparing anything across strata.

| Stratum | n | good | interesting | podcast only | bad | % good | % good+int |
|---|---|---|---|---|---|---|---|
| unfiltered | 457 | 19 | 49 | 10 | 379 | 4.2 | 14.9 |
| mid | 279 | 87 | 52 | 2 | 138 | 31.2 | 49.8 |
| near_miss | 216 | 29 | 54 | 58 | 75 | 13.4 | 38.4 |
| border | 167 | 36 | 39 | 0 | 92 | 21.6 | 44.9 |
| promising | 153 | 53 | 52 | 6 | 42 | 34.6 | 68.6 |
| high | 73 | 48 | 17 | 0 | 7 | 65.8 | 89.0 |
| in_feed | 58 | 29 | 7 | 17 | 5 | 50.0 | 62.1 |
| low | 55 | 3 | 7 | 0 | 45 | 5.5 | 18.2 |
| floor_fill | 36 | 2 | 7 | 0 | 27 | 5.6 | 25.0 |
| wildcard | 16 | 0 | 1 | 4 | 11 | 0.0 | 6.2 |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 306 | 61.8 | 63.5 | 45.4 | 47.2 |
| interesting | 285 | 49.5 | 48 | 35.5 | 33.2 |
| podcast_only | 97 | 51.4 | 47 | 59.4 | 50.9 |
| bad | 821 | 39.7 | 38 | 17.4 | 13.8 |

### Precision by score band

| Score band | n | good | interesting | bad | % good | % good+int | % bad |
|---|---|---|---|---|---|---|---|
| 80-100 | 104 | 65 | 20 | 11 | 62.5 | 81.7 | 10.6 |
| 60-79 | 316 | 97 | 58 | 139 | 30.7 | 49.1 | 44.0 |
| 40-59 | 555 | 117 | 138 | 256 | 21.1 | 45.9 | 46.1 |
| 20-39 | 378 | 23 | 54 | 278 | 6.1 | 20.4 | 73.5 |
| 0-19 | 157 | 4 | 15 | 137 | 2.5 | 12.1 | 87.3 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **25** (manually lowered 20 → 13 on 2026-06-24).

`interesting` articles score low on relevance, so a higher floor costs them first. Weigh **% of bad cut** against **% of good+int lost**.

| Floor | Bad cut | % of bad | Good lost | % of good | Interesting lost | % of int | % of good+int |
|---|---|---|---|---|---|---|---|
| 13 | 0 | 0.0 | 0 | 0.0 | 0 | 0.0 | 0.0 |
| 15 | 40 | 4.9 | 1 | 0.3 | 3 | 1.1 | 0.7 |
| 20 | 137 | 16.7 | 4 | 1.3 | 15 | 5.3 | 3.2 |
| 25 | 207 | 25.2 | 8 | 2.6 | 21 | 7.4 | 4.9 |
| 30 | 321 | 39.1 | 16 | 5.2 | 36 | 12.6 | 8.8 |
| 35 | 377 | 45.9 | 19 | 6.2 | 52 | 18.2 | 12.0 |
| 40 | 415 | 50.5 | 27 | 8.8 | 69 | 24.2 | 16.2 |
| 45 | 476 | 58.0 | 44 | 14.4 | 97 | 34.0 | 23.9 |
| 50 | 632 | 77.0 | 128 | 41.8 | 195 | 68.4 | 54.7 |
| 60 | 671 | 81.7 | 144 | 47.1 | 207 | 72.6 | 59.4 |

### By category

| Category | n | good | interesting | bad | % good+int | % bad |
|---|---|---|---|---|---|---|
| news | 736 | 70 | 80 | 567 | 20.4 | 77.0 |
| ai-tech | 192 | 31 | 93 | 61 | 64.6 | 31.8 |
| local | 145 | 76 | 21 | 35 | 66.9 | 24.1 |
| wellness | 123 | 33 | 22 | 56 | 44.7 | 45.5 |
| science | 88 | 37 | 10 | 11 | 53.4 | 12.5 |
| design | 63 | 3 | 21 | 38 | 38.1 | 60.3 |
| climate | 60 | 26 | 10 | 17 | 60.0 | 28.3 |
| homelab | 43 | 16 | 12 | 10 | 65.1 | 23.3 |
| scifi | 23 | 0 | 8 | 15 | 34.8 | 65.2 |
| outdoors | 20 | 4 | 5 | 10 | 45.0 | 50.0 |
| homestead | 17 | 10 | 3 | 1 | 76.5 | 5.9 |

### Sources (≥ 5 ratings)

**Highest good+interesting rate**

| Source | n | good | interesting | bad | % good+int |
|---|---|---|---|---|---|
| Bicycling | 6 | 4 | 2 | 0 | 100.0 |
| Cariboo Signals Reviews | 5 | 2 | 3 | 0 | 100.0 |
| MacRumors | 6 | 2 | 3 | 1 | 83.3 |
| XDA Developers | 6 | 4 | 1 | 0 | 83.3 |
| The Tyee | 31 | 19 | 6 | 2 | 80.6 |
| Vancouver Sun | 10 | 4 | 4 | 1 | 80.0 |
| APTN News | 5 | 3 | 1 | 0 | 80.0 |
| Neuroscience News | 5 | 3 | 1 | 0 | 80.0 |
| New Atlas | 13 | 5 | 5 | 2 | 76.9 |
| Williams Lake Tribune | 54 | 32 | 7 | 9 | 72.2 |

**Lowest good+interesting rate** — block candidate only at n ≥ 8 with zero positives of any kind

| Source | n | good | interesting | bad | % good+int | Block candidate |
|---|---|---|---|---|---|---|
| My East Kootenay Now | 6 | 0 | 0 | 6 | 0.0 |  |
| Live for the Outdoors (Country Walking) | 6 | 0 | 0 | 6 | 0.0 |  |
| Edge (GamesRadar) | 48 | 0 | 1 | 47 | 2.1 |  |
| Ideal Home (Country Homes & Interiors) | 25 | 0 | 1 | 24 | 4.0 |  |
| NYT Top Stories | 49 | 2 | 3 | 43 | 10.2 |  |
| Domino | 16 | 0 | 2 | 14 | 12.5 |  |
| Boing Boing | 15 | 0 | 2 | 13 | 13.3 |  |
| Country Life | 22 | 1 | 2 | 19 | 13.6 |  |
| Country Guide | 7 | 0 | 1 | 6 | 14.3 |  |
| KFF Health News | 7 | 1 | 0 | 6 | 14.3 |  |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 96 | 121 | 581 |
| analysis | 76 | 73 | 67 |
| breaking | 62 | 36 | 73 |
| feature | 46 | 33 | 67 |
| opinion | 7 | 8 | 16 |
| news | 14 | 8 | 10 |
| recap | 1 | 2 | 5 |
| fluff | 3 | 2 | 0 |
| investigation | 0 | 1 | 1 |
| wire | 1 | 1 | 0 |
| essay | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 36 | 39 | 92 |
| low | 3 | 7 | 45 |
| unfiltered | 19 | 49 | 379 |
| high | 48 | 17 | 7 |
| mid | 87 | 52 | 138 |
| floor_fill | 2 | 7 | 27 |
| promising | 53 | 52 | 42 |
| near_miss | 29 | 54 | 75 |
| in_feed | 29 | 7 | 5 |
| wildcard | 0 | 1 | 11 |

### Filler trend (from the corpus alignment reports, kept in weekly_metrics.jsonl)

| Week | Articles analysed | Filler | Filler % |
|---|---|---|---|
| 2026-Q2 (3 wk) | 2234 | 170 | 8 |
| 2026-Q3 (10 wk) | 13729 | 1293 | 9 |
| 2026-W39 | 1469 | 182 | 12 |
| 2026-W40 | 1340 | 162 | 12 |
| 2026-W41 | 467 | 40 | 9 |
| 2026-W42 | 1333 | 56 | 4 |
| 2026-W43 | 1318 | 81 | 6 |
| 2026-W44 | 1296 | 0 | 0 |
| 2026-W45 | 1322 | 3 | 0 |
| 2026-W46 | 1315 | 13 | 1 |

## 3. Theme-Bucket Routing Accuracy

Of **1510** ratings tied to an aired day, you corrected the day on **337** (22.3%). Additionally 362 articles were approved for other days.

### Per theme day

`% day fit` counts good + podcast only (the verdicts that name days). `% good+int` is feed fit: wanted in your feed, any day or none.

| Day | Theme | n | good | interesting | podcast only | bad | % day fit | % good+int | Corrected away |
|---|---|---|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 262 | 48 | 65 | 17 | 132 | 24.8 | 43.1 | 55 |
| tuesday | Working Lands & Industry | 247 | 46 | 44 | 13 | 144 | 23.9 | 36.4 | 46 |
| wednesday | Repair Culture & Practical Tech | 222 | 47 | 38 | 10 | 127 | 25.7 | 38.3 | 52 |
| thursday | Indigenous Lands & Innovation | 229 | 40 | 36 | 20 | 133 | 26.2 | 33.2 | 55 |
| friday | Wild Spaces & Outdoor Life | 196 | 43 | 35 | 12 | 106 | 28.1 | 39.8 | 51 |
| saturday | Cariboo Local Affairs | 171 | 48 | 34 | 8 | 81 | 32.7 | 48.0 | 43 |
| sunday | Science, Wonder & the Natural World | 183 | 34 | 33 | 17 | 98 | 27.9 | 36.6 | 35 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 12 | 8 | 2 | 2 | 12 | 19 |
| tuesday | 6 |  | 6 | 2 | 2 | 10 | 20 |
| wednesday | 5 | 9 |  | 2 | 6 | 12 | 18 |
| thursday | 4 | 9 | 8 |  | 1 | 7 | 26 |
| friday | 3 | 9 | 5 | 3 |  | 12 | 19 |
| saturday | 4 | 5 | 7 | 4 | 3 |  | 20 |
| sunday | 4 | 8 | 10 |  | 4 | 9 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 185 |
| Theme scorer disagreed with you (scoring miss) | 152 |
| Theme scores missing on the rating | 0 |

## 3b. Category Retag Accuracy

_Category retags: 5.7% of 1510 — within noise of 2026-W45, so the tables are left out. They print in full in the first audit of each month._

## 4. Volume Trend — Is the Feed Lighter?

_Average per-run articles fetched and passing the quality gate, by ISO week (from FEED_LOG.md). The quality floor was manually dropped 20 → 13 in week 2026-W26._

| Week | Runs | Avg fetched/run | Avg quality/run |
|---|---|---|---|
| 2026-Q1 (6 wk) | 105 | 872 | 198 |
| 2026-Q2 (13 wk) | 193 | 1012 | 102 |
| 2026-Q3 (11 wk) | 86 | 1376 | 81 |
| 2026-W39 | 8 | 1363 | 74 |
| 2026-W40 | 7 | 1354 | 81 |
| 2026-W41 | 7 | 1367 | 84 |
| 2026-W42 | 7 | 1364 | 80 |
| 2026-W43 | 7 | 1421 | 84 |
| 2026-W44 | 7 | 1492 | 85 |
| 2026-W45 | 7 | 1540 | 88 |
| 2026-W46 | 5 | 1833 | 92 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-11-01T06:00:54.201534+00:00 | 1331 | 1042 | 77 | 656 | 198 |
| 2026-11-02T06:00:51.242465+00:00 | 897 | 717 | 79 | 385 | 155 |
| 2026-11-03T06:00:57.863283+00:00 | 1392 | 1097 | 92 | 634 | 254 |
| 2026-11-04T06:01:01.726233+00:00 | 1723 | 1310 | 86 | 794 | 292 |
| 2026-11-05T06:00:51.269578+00:00 | 1750 | 1344 | 95 | 869 | 257 |
| 2026-11-06T06:00:54.885401+00:00 | 1764 | 1356 | 89 | 860 | 282 |
| 2026-11-07T06:00:49.721641+00:00 | 1744 | 1358 | 86 | 877 | 254 |
| 2026-11-08T06:00:50.865217+00:00 | 1437 | 1118 | 88 | 703 | 175 |
| 2026-11-09T06:00:52.101794+00:00 | 969 | 746 | 78 | 443 | 114 |
| 2026-11-10T06:00:46.995798+00:00 | 1537 | 1164 | 100 | 746 | 194 |
| 2026-11-11T06:00:49.531083+00:00 | 1991 | 1522 | 95 | 1022 | 244 |
| 2026-11-12T06:00:52.324704+00:00 | 1846 | 1438 | 88 | 983 | 193 |
| 2026-11-13T06:00:51.735151+00:00 | 1872 | 1362 | 91 | 919 | 189 |
| 2026-11-14T06:00:54.175280+00:00 | 1918 | 1418 | 88 | 942 | 225 |

### Current category feed sizes

| Feed | Items |
|---|---|
| news | 104 |
| ai-tech | 88 |
| climate | 63 |
| wellness | 55 |
| homelab | 45 |
| local | 45 |
| science | 41 |
| design | 30 |
| homestead | 19 |
| outdoors | 8 |
| scifi | 6 |

### Headline coverage (Kagi News, last 7 days)

_Clusters covered by many outlets, over 7 runs: 343 of 400 (85.8%) reached no feed. The digest item lists the news ones; the per-story list is in each nightly's log._

| Outcome | Headlines |
|---|---|
| published | 51 |
| already_shown | 6 |
| dedup | 30 |
| gate_reject | 23 |
| show_only | 4 |
| ranked_out | 286 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 30 / 9 |
| Calibration stats runs available | 14 |
| Calibration stats range | 2026-11-01 → 2026-11-14 |
| theme_holdover_cache.json present | True |

## 6. Week over Week

_Counts are the 7 days to each date; rates cover 28 days. Weeks older than the last 8 fold into one row a quarter (counts summed, rates averaged). Weeks marked * were rebuilt from the ratings archive and carry no cost or scorecard data._

| Week | Through | Rated | good | interesting | podcast only | bad | Notes | Shipped wanted % (reweighted) | Gate miss % | News share of ratings % |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-Q2 (3 wk) |  | 432 | 172 | 7 | 0 | 253 | 12 |  | 22.2 | 79.4 |
| 2026-Q3 (11 wk) |  | 1173 | 204 | 141 | 0 | 828 | 35 | 41.0 | 17.8 | 76.9 |
| 2026-W39* | 2026-09-26 | 142 | 31 | 34 | 0 | 77 | 23 | 41.1 | 13.8 | 70.2 |
| 2026-W40* | 2026-10-03 | 188 | 56 | 52 | 0 | 80 | 94 | 43.5 | 15.7 | 62.2 |
| 2026-W41 | 2026-10-10 | 177 | 53 | 29 | 0 | 95 | 84 | 42.5 | 11.8 | 58.3 |
| 2026-W42 | 2026-10-17 | 134 | 32 | 35 | 14 | 53 | 39 | 45.4 | 14.1 | 49.6 |
| 2026-W43 | 2026-10-24 | 84 | 12 | 20 | 23 | 29 | 21 | 44.2 | 16.5 | 42.9 |
| 2026-W44 | 2026-10-31 | 60 | 11 | 13 | 14 | 22 | 11 | 42.4 | 22.6 | 38.0 |
| 2026-W45 | 2026-11-07 | 84 | 12 | 11 | 23 | 38 | 32 | 40.6 | 31.2 | 28.5 |
| 2026-W46 | 2026-11-14 | 84 | 16 | 15 | 23 | 30 | 22 | 38.1 | 32.7 | 24.4 |

## 7. What Each Score Buys

Graded on the last 4 weeks of ratings (312 rated, 76 news). AUC is the chance a wanted article outscores an unwanted one: 0.5 is a coin flip. The reader model is refit each week on earlier ratings only; it uses the relevance band, so it is not wholly free of the paid pass.

| Signal | Paid by | AUC | AUC, news only |
|---|---|---|---|
| final score | gate + deep_score | 0.676 | 0.599 |
| quality (Q) | deep_score; q_gate elsewhere | 0.676 | 0.616 |
| relevance (R) | deep_score | 0.712 | 0.641 |
| local (L) | deep_score | 0.581 | 0.67 |
| theme fit for that day's theme | theme_ingest / theme / theme_batch | 0.662 | 0.656 |
| reader model | free: your earlier ratings | 0.768 | 0.804 |

### Claude cost by stage (last 7 days)

7 of 7 runs recorded stages; all vendors together est. $1.3416.

| Stage | Calls | Est. cost |
|---|---|---|
| gate | 252 | $0.2205 |
| theme | 195 | $0.1536 |
| deep_score | 112 | $0.1206 |

### Local places: appetite vs. supply

Wanted % among rated articles mentioning the place (baseline 41.2%), against its share of the 1474-article podcast pool.

| Place | Rated | Wanted % | In pool | Pool % |
|---|---|---|---|---|
| williams lake | 92 | 77.2 | 32 | 2.2 |
| cariboo | 122 | 73.0 | 30 | 2.0 |
| quesnel | 54 | 55.6 | 12 | 0.8 |
| 100 mile house | 23 | 69.6 | 0 | 0.0 |
| horsefly | 1 | 100.0 | 0 | 0.0 |
| lac la hache | 1 | 100.0 | 1 | 0.1 |

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

| Closed | Finding | Opened | Weeks open | Calibration changes while open |
|---|---|---|---|---|
| 2026-W46 | Block candidates still unblocked | 2026-W41 | 5 | none logged |

