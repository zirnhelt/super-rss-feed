# Article Review Audit

_Generated: 2026-09-20 16:58 UTC — ratings window 2026-06-17 → 2026-09-18_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 1606 |
| Rated **bad** — reached you (pipeline failed) | 433 |
| Rated **bad** — correctly rejected (pipeline worked) | 645 |
| Rated **good** | 376 (23.4%) |
| Rated **interesting** | 148 |
| Reweighted good-or-interesting rate of the **shipped** feed | 41.2% (from 24.8% of shipped ratings) |
| Scrub false-negative rate (wanted articles thrown away) | 17.9% of 787 rejects |
| Theme-day corrections (`better_theme`) | 310 (19.4% of day-routed ratings) |
| …where the theme scorer already preferred your day | 123 |
| …where the theme scorer disagreed with you | 187 |
| …of those, actually routed by podcast selection | 0 |
| Category retags | 84 (9.6% of categorized ratings) |

### Sampling strata

The review feed is a **quota** sample: a fixed handful from each score band plus up to 10 scrub rejects. Rates within a stratum are unbiased; the corpus-wide rate is not, because half the ratings come from the reject pile. Reweight before comparing anything across strata.

| Stratum | n | good | interesting | bad | % good | % good+int |
|---|---|---|---|---|---|---|
| unfiltered | 787 | 73 | 68 | 645 | 9.3 | 17.9 |
| border | 317 | 121 | 54 | 142 | 38.2 | 55.2 |
| mid | 307 | 115 | 14 | 178 | 37.5 | 42.0 |
| low | 112 | 21 | 8 | 83 | 18.8 | 25.9 |
| high | 64 | 42 | 2 | 20 | 65.6 | 68.8 |
| floor_fill | 12 | 0 | 2 | 10 | 0.0 | 16.7 |
| unknown | 7 | 4 | 0 | 3 | 57.1 | 57.1 |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 376 | 51.9 | 49.0 | 42.2 | 42.0 |
| interesting | 148 | 40.2 | 47.0 | 27.0 | 23.1 |
| bad | 1081 | 35.5 | 29 | 21.7 | 18.9 |

### Precision by score band

| Score band | n | good | bad | % good | % bad |
|---|---|---|---|---|---|
| 80-100 | 78 | 48 | 28 | 61.5 | 35.9 |
| 60-79 | 225 | 81 | 132 | 36.0 | 58.7 |
| 40-59 | 491 | 155 | 269 | 31.6 | 54.8 |
| 20-39 | 462 | 63 | 348 | 13.6 | 75.3 |
| 0-19 | 350 | 29 | 304 | 8.3 | 86.9 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **25** (manually lowered 20 → 13 on 2026-06-24).

| Floor | Bad cut | % of bad | Good lost | % of good |
|---|---|---|---|---|
| 13 | 68 | 6.3 | 7 | 1.9 |
| 15 | 174 | 16.1 | 19 | 5.1 |
| 20 | 304 | 28.1 | 29 | 7.7 |
| 25 | 394 | 36.4 | 38 | 10.1 |
| 30 | 563 | 52.1 | 73 | 19.4 |
| 35 | 618 | 57.2 | 82 | 21.8 |
| 40 | 652 | 60.3 | 92 | 24.5 |
| 45 | 708 | 65.5 | 111 | 29.5 |
| 50 | 874 | 80.9 | 229 | 60.9 |
| 60 | 921 | 85.2 | 247 | 65.7 |

### By category

| Category | n | good | interesting | bad | % bad |
|---|---|---|---|---|---|
| news | 1157 | 187 | 54 | 916 | 79.2 |
| ai-tech | 135 | 45 | 37 | 53 | 39.3 |
| wellness | 103 | 30 | 20 | 52 | 50.5 |
| local | 67 | 45 | 2 | 20 | 29.9 |
| climate | 36 | 24 | 4 | 8 | 22.2 |
| science | 29 | 23 | 3 | 3 | 10.3 |
| homelab | 26 | 8 | 11 | 7 | 26.9 |
| design | 17 | 2 | 7 | 8 | 47.1 |
| scifi | 14 | 1 | 4 | 9 | 64.3 |
| outdoors | 10 | 4 | 4 | 2 | 20.0 |
| homestead | 5 | 3 | 2 | 0 | 0.0 |
| shared | 4 | 4 | 0 | 0 | 0.0 |
| podcast-sunday | 2 | 0 | 0 | 2 | 100.0 |
| podcast-friday | 1 | 0 | 0 | 1 | 100.0 |

### Sources (≥ 5 ratings)

**Highest good-rate**

| Source | n | good | bad | % good |
|---|---|---|---|---|
| Eagle Feather News | 6 | 6 | 0 | 100.0 |
| The Narwhal | 5 | 4 | 1 | 80.0 |
| EarthSky | 5 | 4 | 1 | 80.0 |
| ScienceDaily | 13 | 10 | 1 | 76.9 |
| ScienceAlert | 13 | 10 | 2 | 76.9 |
| 100 Mile Free Press | 12 | 9 | 3 | 75.0 |
| BC Gov News | 16 | 11 | 5 | 68.8 |
| Williams Lake Tribune | 27 | 18 | 8 | 66.7 |
| APTN News | 11 | 7 | 3 | 63.6 |
| My Cariboo Now | 23 | 13 | 9 | 56.5 |

**Highest bad-rate**

| Source | n | good | bad | % bad |
|---|---|---|---|---|
| Rolling Stone | 24 | 0 | 24 | 100.0 |
| The Atlantic | 13 | 0 | 13 | 100.0 |
| Mother Jones | 10 | 0 | 10 | 100.0 |
| The New Yorker | 9 | 0 | 9 | 100.0 |
| Cottage Life | 8 | 0 | 8 | 100.0 |
| Live for the Outdoors (Country Walking) | 6 | 0 | 6 | 100.0 |
| Edge (GamesRadar) | 32 | 0 | 30 | 93.8 |
| Lifehacker | 27 | 3 | 24 | 88.9 |
| Ideal Home (Country Homes & Interiors) | 27 | 0 | 24 | 88.9 |
| Neowin | 17 | 2 | 15 | 88.2 |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 262 | 90 | 900 |
| breaking | 43 | 20 | 72 |
| analysis | 37 | 20 | 35 |
| feature | 21 | 9 | 36 |
| news | 7 | 5 | 14 |
| opinion | 3 | 3 | 17 |
| recap | 1 | 0 | 3 |
| wire | 2 | 0 | 2 |
| investigation | 0 | 1 | 1 |
| fluff | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 121 | 54 | 142 |
| low | 21 | 8 | 83 |
| high | 42 | 2 | 20 |
| mid | 115 | 14 | 178 |
| unknown | 4 | 0 | 3 |
| unfiltered | 73 | 68 | 645 |
| floor_fill | 0 | 2 | 10 |

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

## 3. Theme-Bucket Routing Accuracy

Of **1599** ratings tied to an aired day, you corrected the day on **310** (19.4%). Additionally 195 good articles were approved for other days.

### Per theme day

| Day | Theme | n | good | bad | % good | Corrected away |
|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 255 | 51 | 171 | 20.0 | 48 |
| tuesday | Working Lands & Industry | 225 | 38 | 171 | 16.9 | 28 |
| wednesday | Repair Culture & Practical Tech | 284 | 84 | 181 | 29.6 | 58 |
| thursday | Indigenous Lands & Innovation | 217 | 41 | 146 | 18.9 | 39 |
| friday | Wild Spaces & Outdoor Life | 265 | 58 | 179 | 21.9 | 52 |
| saturday | Cariboo Local Affairs | 191 | 56 | 127 | 29.3 | 52 |
| sunday | Science, Wonder & the Natural World | 162 | 44 | 103 | 27.2 | 33 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 12 | 9 | 1 | 6 | 7 | 13 |
| tuesday | 7 |  | 5 | 2 | 5 | 3 | 6 |
| wednesday | 8 | 8 |  | 3 | 15 | 11 | 13 |
| thursday | 3 | 6 | 7 |  | 7 | 2 | 14 |
| friday | 6 | 10 | 10 | 5 |  | 7 | 14 |
| saturday | 2 | 4 | 12 | 5 | 9 |  | 20 |
| sunday | 4 | 9 | 9 | 1 | 5 | 5 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 123 |
| Theme scorer disagreed with you (scoring miss) | 187 |
| Theme scores missing on the rating | 0 |

## 3b. Category Retag Accuracy

Of **877** ratings carrying a confirmed/retagged category, you retagged **84** (9.6%) to a different category.

### Category → category correction matrix (shown → corrected)

| Shown | Corrected to | Count |
|---|---|---|
| news | ai-tech | 24 |
| news | homelab | 11 |
| news | wellness | 8 |
| news | outdoors | 6 |
| news | design | 6 |
| news | climate | 5 |
| news | homestead | 5 |
| news | science | 3 |
| news | local | 3 |
| news | scifi | 3 |
| science | climate | 1 |
| science | wellness | 1 |
| science | news | 1 |
| design | homelab | 1 |
| local | news | 1 |
| local | climate | 1 |
| local | wellness | 1 |
| wellness | climate | 1 |
| wellness | ai-tech | 1 |
| wellness | news | 1 |

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
| 2026-W38 | 6 | 1714 | 98 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-09-07T04:01:02.273459+00:00 | 1127 | 622 | 80 | 271 | 135 |
| 2026-09-08T04:01:07.188970+00:00 | 1223 | 751 | 93 | 534 | 81 |
| 2026-09-09T07:01:41.204128+00:00 | 1596 | 1026 | 98 | 766 | 127 |
| 2026-09-10T13:54:05.139005+00:00 | 1884 | 1207 | 98 | 937 | 138 |
| 2026-09-11T04:01:16.036321+00:00 | 1844 | 1147 | 90 | 875 | 128 |
| 2026-09-12T04:01:07.363565+00:00 | 1782 | 1135 | 101 | 879 | 111 |
| 2026-09-13T04:01:03.708594+00:00 | 1442 | 849 | 91 | 635 | 85 |
| 2026-09-14T04:00:50.205860+00:00 | 1129 | 589 | 83 | 406 | 68 |
| 2026-09-15T04:00:46.136006+00:00 | 1433 | 908 | 104 | 668 | 100 |
| 2026-09-16T04:00:53.823654+00:00 | 1785 | 1196 | 105 | 921 | 122 |
| 2026-09-17T04:00:47.641046+00:00 | 1866 | 1203 | 105 | 954 | 103 |
| 2026-09-18T04:00:47.270775+00:00 | 1907 | 1254 | 96 | 938 | 152 |
| 2026-09-19T04:00:36.304046+00:00 | 1852 | 1246 | 93 | 980 | 128 |
| 2026-09-20T04:00:32.093265+00:00 | 1444 | 847 | 85 | 646 | 78 |

### Current category feed sizes

| Feed | Items |
|---|---|
| news | 125 |
| ai-tech | 88 |
| wellness | 51 |
| local | 47 |
| homelab | 46 |
| science | 42 |
| climate | 34 |
| design | 29 |
| outdoors | 9 |
| scifi | 8 |
| homestead | 6 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 22 / 9 |
| Calibration stats runs available | 14 |
| Calibration stats range | 2026-09-07 → 2026-09-20 |
| theme_holdover_cache.json present | True |

**Context:** `calibration_stats_cache.json` was first committed on 2026-07-07, so every weekly calibration run before that found no stats and skipped — the log's repeated "Claude call or response parsing failed" lines were misleading boilerplate, not API failures. The agent's Claude path has effectively never run.

