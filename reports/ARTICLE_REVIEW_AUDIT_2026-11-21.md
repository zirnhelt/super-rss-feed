# Article Review Audit

_Generated: 2026-11-21 20:17 UTC — ratings window 2026-08-24 → 2026-11-21 (rolling 90 days; 2632 rated all time)_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 1490 |
| Rated **bad** — reached you (pipeline failed) | 439 |
| Rated **bad** — correctly rejected (pipeline worked) | 338 |
| Rated **good** | 313 (21.0%) |
| Rated **interesting** (wanted, no specific day) | 284 |
| Rated **podcast only** (for the show, not your feed) | 115 |
| Rated good or interesting (raw, quota-biased) | 40.1% |
| Reweighted good-or-interesting rate of the **shipped** feed | 41.5% (from 95.1% of shipped ratings) |
| Scrub false-negative rate (wanted articles thrown away) | 14.7% of 409 rejects |
| Theme-day corrections (`better_theme`) | 359 (24.1% of day-routed ratings) |
| …where the theme scorer already preferred your day | 197 |
| …where the theme scorer disagreed with you | 162 |
| …of those, actually routed by podcast selection | 0 |
| Category retags | 78 (5.2% of categorized ratings) |

## Needs Attention

_Checks one week of numbers cannot make on its own. **Weeks** counts the weekly audits in a row that reported it; at 3+ it has been seen and not acted on._

**Verdict: worse, cycling.** The shipped feed is 39.0% wanted, down 5.2 points from 44.2% 4 weeks ago. 3 finding(s) have been open 3+ weeks, and gate-misses got worse while open: reported every week, none closed.

_**Owner** `fixer` is a defect a session can root-cause and PR; `reader` is yours to decide or rate. **Moved** is the finding's own metric since the audit that opened it._

| Finding | Detail | Weeks | Owner | Next action | Done when | Moved |
|---|---|---|---|---|---|---|
| ⚠️ The gate threw away 38.0% of the rejects you wanted | 19 of 50 rated rejects in 28 days. Most often, all time: NYT Well (14), MacRumors (9), Outside Online (8), 100 Mile Free Press (6), Fast Company (6), The Northern Miner (5). | 7 | fixer | Read the wanted rejects from the named sources in feedback/, find what in quality_charter.txt or the gate prompt rejects them, and fix that one cause. | wanted share of rated rejects under 10% | 11.8 → 38.0 (worse) |
| ⚠️ 5 categories are unmeasured | Under 20 ratings in 28 days: homelab (11), homestead (6), scifi (12), outdoors (5), miscellany (0). Their rates are noise, not "fine"; news took 22.7% of the ratings. | 7 | fixer | Find why rotate_review_categories() leaves these categories short: a 12-a-day batch can give every category the floor. Fix the rotation, not the quota. | every category has 20+ ratings in 28 days | — |
| ⚠️ Places you want that the pool barely carries | 100 mile house: 69.6% wanted, 2 in the pool (0.1%). Baseline 41.9% wanted. | 7 | fixer | Trace the place's own outlets through a run (feed failing, filtered, or unanchored) and fix what keeps them out of the pool; add a source only if none exists. | the place is in 1%+ of the pool | — |
| The feeds missed 84.7% of the week's headlines | 338 of 399 widely covered Kagi News stories in 7 runs reached no feed (dedup 28, gate_reject 33, show_only 5, ranked_out 272). gate_reject is the gate's junk flag, show_only a [show] line outside news, ranked_out the slots or the score. | 2 | reader | Decide whether to build the headlines lane (TODO.md, roadmap B): ranked_out misses are the interest ranking working as designed, not a defect. | under 50% of widely covered stories missed | 85.8 → 84.7 (flat) |

### Sampling strata

The review feed is a **quota** sample: a fixed handful from each score band plus up to 10 scrub rejects. Rates within a stratum are unbiased; the corpus-wide rate is not, because half the ratings come from the reject pile. Reweight before comparing anything across strata.

| Stratum | n | good | interesting | podcast only | bad | % good | % good+int |
|---|---|---|---|---|---|---|---|
| unfiltered | 409 | 18 | 42 | 11 | 338 | 4.4 | 14.7 |
| mid | 279 | 87 | 52 | 2 | 138 | 31.2 | 49.8 |
| near_miss | 258 | 37 | 65 | 70 | 86 | 14.3 | 39.5 |
| promising | 153 | 53 | 52 | 6 | 42 | 34.6 | 68.6 |
| border | 145 | 31 | 33 | 0 | 81 | 21.4 | 44.1 |
| high | 73 | 48 | 17 | 0 | 7 | 65.8 | 89.0 |
| in_feed | 70 | 34 | 9 | 21 | 6 | 48.6 | 61.4 |
| low | 45 | 3 | 6 | 0 | 36 | 6.7 | 20.0 |
| floor_fill | 36 | 2 | 7 | 0 | 27 | 5.6 | 25.0 |
| wildcard | 22 | 0 | 1 | 5 | 16 | 0.0 | 4.5 |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 313 | 61.9 | 65 | 45.0 | 47.1 |
| interesting | 284 | 49.8 | 48.0 | 36.1 | 33.8 |
| podcast_only | 115 | 50.5 | 47 | 57.6 | 49.7 |
| bad | 777 | 40.4 | 40 | 19.2 | 15.2 |

### Precision by score band

| Score band | n | good | interesting | bad | % good | % good+int | % bad |
|---|---|---|---|---|---|---|---|
| 80-100 | 109 | 67 | 22 | 11 | 61.5 | 81.7 | 10.1 |
| 60-79 | 324 | 100 | 58 | 141 | 30.9 | 48.8 | 43.5 |
| 40-59 | 550 | 118 | 135 | 247 | 21.5 | 46.0 | 44.9 |
| 20-39 | 359 | 24 | 54 | 250 | 6.7 | 21.7 | 69.6 |
| 0-19 | 148 | 4 | 15 | 128 | 2.7 | 12.8 | 86.5 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **25** (manually lowered 20 → 13 on 2026-06-24).

`interesting` articles score low on relevance, so a higher floor costs them first. Weigh **% of bad cut** against **% of good+int lost**.

| Floor | Bad cut | % of bad | Good lost | % of good | Interesting lost | % of int | % of good+int |
|---|---|---|---|---|---|---|---|
| 13 | 0 | 0.0 | 0 | 0.0 | 0 | 0.0 | 0.0 |
| 15 | 36 | 4.6 | 1 | 0.3 | 1 | 0.4 | 0.3 |
| 20 | 128 | 16.5 | 4 | 1.3 | 15 | 5.3 | 3.2 |
| 25 | 186 | 23.9 | 9 | 2.9 | 21 | 7.4 | 5.0 |
| 30 | 284 | 36.6 | 16 | 5.1 | 35 | 12.3 | 8.5 |
| 35 | 338 | 43.5 | 20 | 6.4 | 52 | 18.3 | 12.1 |
| 40 | 378 | 48.6 | 28 | 8.9 | 69 | 24.3 | 16.2 |
| 45 | 439 | 56.5 | 45 | 14.4 | 99 | 34.9 | 24.1 |
| 50 | 586 | 75.4 | 127 | 40.6 | 192 | 67.6 | 53.4 |
| 60 | 625 | 80.4 | 146 | 46.6 | 204 | 71.8 | 58.6 |

### By category

| Category | n | good | interesting | bad | % good+int | % bad |
|---|---|---|---|---|---|---|
| news | 687 | 74 | 78 | 514 | 22.1 | 74.8 |
| ai-tech | 192 | 30 | 93 | 61 | 64.1 | 31.8 |
| local | 153 | 79 | 23 | 36 | 66.7 | 23.5 |
| wellness | 121 | 33 | 19 | 56 | 43.0 | 46.3 |
| science | 95 | 38 | 11 | 12 | 51.6 | 12.6 |
| climate | 64 | 26 | 10 | 18 | 56.2 | 28.1 |
| design | 64 | 3 | 19 | 41 | 34.4 | 64.1 |
| homelab | 44 | 17 | 10 | 11 | 61.4 | 25.0 |
| scifi | 27 | 0 | 12 | 14 | 44.4 | 51.9 |
| outdoors | 24 | 4 | 6 | 12 | 41.7 | 50.0 |
| homestead | 19 | 9 | 3 | 2 | 63.2 | 10.5 |

### Sources (≥ 5 ratings)

**Highest good+interesting rate**

| Source | n | good | interesting | bad | % good+int |
|---|---|---|---|---|---|
| Bicycling | 6 | 4 | 2 | 0 | 100.0 |
| MacRumors | 6 | 2 | 3 | 1 | 83.3 |
| XDA Developers | 6 | 4 | 1 | 0 | 83.3 |
| Vancouver Sun | 11 | 5 | 4 | 1 | 81.8 |
| APTN News | 5 | 3 | 1 | 0 | 80.0 |
| Neuroscience News | 5 | 3 | 1 | 0 | 80.0 |
| The Tyee | 34 | 20 | 7 | 3 | 79.4 |
| New Atlas | 13 | 5 | 5 | 2 | 76.9 |
| Williams Lake Tribune | 57 | 34 | 8 | 9 | 73.7 |
| The Walrus | 7 | 0 | 5 | 2 | 71.4 |

**Lowest good+interesting rate** — block candidate only at n ≥ 8 with zero positives of any kind

| Source | n | good | interesting | bad | % good+int | Block candidate |
|---|---|---|---|---|---|---|
| Live for the Outdoors (Country Walking) | 6 | 0 | 0 | 6 | 0.0 |  |
| My East Kootenay Now | 5 | 0 | 0 | 5 | 0.0 |  |
| Edge (GamesRadar) | 44 | 0 | 1 | 43 | 2.3 |  |
| Ideal Home (Country Homes & Interiors) | 20 | 0 | 1 | 19 | 5.0 |  |
| Dwell | 10 | 1 | 0 | 9 | 10.0 |  |
| NYT Top Stories | 48 | 1 | 4 | 42 | 10.4 |  |
| Country Life | 19 | 1 | 1 | 17 | 10.5 |  |
| Country Living UK | 18 | 1 | 1 | 16 | 11.1 |  |
| Boing Boing | 14 | 0 | 2 | 12 | 14.3 |  |
| Country Guide | 7 | 0 | 1 | 6 | 14.3 |  |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 99 | 117 | 529 |
| analysis | 78 | 72 | 73 |
| breaking | 62 | 36 | 70 |
| feature | 46 | 37 | 72 |
| opinion | 7 | 9 | 15 |
| news | 15 | 7 | 10 |
| recap | 2 | 2 | 5 |
| fluff | 3 | 2 | 0 |
| wire | 1 | 1 | 1 |
| investigation | 0 | 1 | 1 |
| essay | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 31 | 33 | 81 |
| low | 3 | 6 | 36 |
| unfiltered | 18 | 42 | 338 |
| high | 48 | 17 | 7 |
| mid | 87 | 52 | 138 |
| floor_fill | 2 | 7 | 27 |
| promising | 53 | 52 | 42 |
| near_miss | 37 | 65 | 86 |
| in_feed | 34 | 9 | 6 |
| wildcard | 0 | 1 | 16 |

### Filler trend (from the corpus alignment reports, kept in weekly_metrics.jsonl)

| Week | Articles analysed | Filler | Filler % |
|---|---|---|---|
| 2026-Q2 (3 wk) | 2234 | 170 | 8 |
| 2026-Q3 (11 wk) | 15198 | 1475 | 10 |
| 2026-W40 | 1340 | 162 | 12 |
| 2026-W41 | 467 | 40 | 9 |
| 2026-W42 | 1333 | 56 | 4 |
| 2026-W43 | 1318 | 81 | 6 |
| 2026-W44 | 1296 | 0 | 0 |
| 2026-W45 | 1322 | 3 | 0 |
| 2026-W46 | 1315 | 13 | 1 |
| 2026-W47 | 1348 | 14 | 1 |

## 3. Theme-Bucket Routing Accuracy

_Day corrections: 24.1% of 1490 — within noise of 2026-W46, so the tables are left out. They print in full in the first audit of each month._

## 3b. Category Retag Accuracy

_Category retags: 5.2% of 1490 — within noise of 2026-W46, so the tables are left out. They print in full in the first audit of each month._

## 4. Volume Trend — Is the Feed Lighter?

_Average per-run articles fetched and passing the quality gate, by ISO week (from FEED_LOG.md). The quality floor was manually dropped 20 → 13 in week 2026-W26._

| Week | Runs | Avg fetched/run | Avg quality/run |
|---|---|---|---|
| 2026-Q1 (6 wk) | 105 | 872 | 198 |
| 2026-Q2 (13 wk) | 193 | 1012 | 102 |
| 2026-Q3 (12 wk) | 94 | 1375 | 80 |
| 2026-W40 | 7 | 1354 | 81 |
| 2026-W41 | 7 | 1367 | 84 |
| 2026-W42 | 7 | 1364 | 80 |
| 2026-W43 | 7 | 1421 | 84 |
| 2026-W44 | 7 | 1492 | 85 |
| 2026-W45 | 7 | 1540 | 88 |
| 2026-W46 | 7 | 1665 | 90 |
| 2026-W47 | 5 | 1844 | 94 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-11-08T06:00:50.865217+00:00 | 1437 | 1118 | 88 | 703 | 175 |
| 2026-11-09T06:00:52.101794+00:00 | 969 | 746 | 78 | 443 | 114 |
| 2026-11-10T06:00:46.995798+00:00 | 1537 | 1164 | 100 | 746 | 194 |
| 2026-11-11T06:00:49.531083+00:00 | 1991 | 1522 | 95 | 1022 | 244 |
| 2026-11-12T06:00:52.324704+00:00 | 1846 | 1438 | 88 | 983 | 193 |
| 2026-11-13T06:00:51.735151+00:00 | 1872 | 1362 | 91 | 919 | 189 |
| 2026-11-14T06:00:54.175280+00:00 | 1918 | 1418 | 88 | 942 | 225 |
| 2026-11-15T06:01:15.252773+00:00 | 1503 | 1114 | 87 | 696 | 196 |
| 2026-11-16T06:00:49.156801+00:00 | 990 | 752 | 81 | 465 | 127 |
| 2026-11-17T06:00:57.397441+00:00 | 1479 | 1105 | 96 | 711 | 163 |
| 2026-11-18T06:00:59.979187+00:00 | 1938 | 1496 | 93 | 955 | 262 |
| 2026-11-19T06:00:54.838421+00:00 | 1981 | 1505 | 103 | 990 | 236 |
| 2026-11-20T06:00:51.255214+00:00 | 1958 | 1481 | 91 | 960 | 233 |
| 2026-11-21T06:00:50.447630+00:00 | 1865 | 1441 | 87 | 951 | 215 |

### Current category feed sizes

| Feed | Items |
|---|---|
| news | 112 |
| ai-tech | 87 |
| climate | 58 |
| local | 55 |
| wellness | 54 |
| homelab | 35 |
| science | 35 |
| design | 25 |
| outdoors | 13 |
| homestead | 12 |
| scifi | 4 |

### Headline coverage (Kagi News, last 7 days)

_Clusters covered by many outlets, over 7 runs: 338 of 399 (84.7%) reached no feed. The digest item lists the news ones; the per-story list is in each nightly's log._

| Outcome | Headlines |
|---|---|
| published | 53 |
| already_shown | 8 |
| dedup | 28 |
| gate_reject | 33 |
| show_only | 5 |
| ranked_out | 272 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 31 / 9 |
| Calibration stats runs available | 14 |
| Calibration stats range | 2026-11-08 → 2026-11-21 |
| theme_holdover_cache.json present | True |

## 6. Week over Week

_Counts are the 7 days to each date; rates cover 28 days. Weeks older than the last 8 fold into one row a quarter (counts summed, rates averaged). Weeks marked * were rebuilt from the ratings archive and carry no cost or scorecard data._

| Week | Through | Rated | good | interesting | podcast only | bad | Notes | Shipped wanted % (reweighted) | Gate miss % | News share of ratings % |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-Q2 (3 wk) |  | 432 | 172 | 7 | 0 | 253 | 12 |  | 22.2 | 79.4 |
| 2026-Q3 (12 wk) |  | 1315 | 235 | 175 | 0 | 905 | 58 | 41.0 | 17.5 | 76.3 |
| 2026-W40* | 2026-10-03 | 188 | 56 | 52 | 0 | 80 | 94 | 43.5 | 15.7 | 62.2 |
| 2026-W41 | 2026-10-10 | 177 | 53 | 29 | 0 | 95 | 84 | 42.5 | 11.8 | 58.3 |
| 2026-W42 | 2026-10-17 | 134 | 32 | 35 | 14 | 53 | 39 | 45.4 | 14.1 | 49.6 |
| 2026-W43 | 2026-10-24 | 84 | 12 | 20 | 23 | 29 | 21 | 44.2 | 16.5 | 42.9 |
| 2026-W44 | 2026-10-31 | 60 | 11 | 13 | 14 | 22 | 11 | 42.4 | 22.6 | 38.0 |
| 2026-W45 | 2026-11-07 | 84 | 12 | 11 | 23 | 38 | 32 | 40.6 | 31.2 | 28.5 |
| 2026-W46 | 2026-11-14 | 84 | 16 | 15 | 23 | 30 | 22 | 38.1 | 32.7 | 24.4 |
| 2026-W47 | 2026-11-21 | 72 | 14 | 17 | 18 | 23 | 14 | 39.0 | 38.0 | 22.7 |

## 7. What Each Score Buys

Graded on the last 4 weeks of ratings (300 rated, 68 news). AUC is the chance a wanted article outscores an unwanted one: 0.5 is a coin flip. The reader model is refit each week on earlier ratings only; it uses the relevance band, so it is not wholly free of the paid pass.

| Signal | Paid by | AUC | AUC, news only |
|---|---|---|---|
| final score | gate + deep_score | 0.701 | 0.696 |
| quality (Q) | deep_score; q_gate elsewhere | 0.606 | 0.5 |
| relevance (R) | deep_score | 0.693 | 0.565 |
| local (L) | deep_score | 0.589 | 0.659 |
| theme fit for that day's theme | theme_ingest / theme / theme_batch | 0.635 | 0.601 |
| reader model | free: your earlier ratings | 0.736 | 0.722 |

### Claude cost by stage (last 7 days)

7 of 7 runs recorded stages; all vendors together est. $1.3138.

| Stage | Calls | Est. cost |
|---|---|---|
| gate | 238 | $0.2059 |
| theme | 185 | $0.1429 |
| deep_score | 112 | $0.1205 |

### Local places: appetite vs. supply

Wanted % among rated articles mentioning the place (baseline 41.9%), against its share of the 1531-article podcast pool.

| Place | Rated | Wanted % | In pool | Pool % |
|---|---|---|---|---|
| williams lake | 96 | 78.1 | 36 | 2.4 |
| cariboo | 129 | 73.6 | 31 | 2.0 |
| quesnel | 57 | 56.1 | 8 | 0.5 |
| 100 mile house | 23 | 69.6 | 2 | 0.1 |
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
| 2026-W47 | The Anthropic price table is stale | 2026-W46 | 1 | none logged |
| 2026-W47 | Local places with almost no ratings | 2026-W43 | 4 | none logged |
| 2026-W46 | Block candidates still unblocked | 2026-W41 | 5 | none logged |

