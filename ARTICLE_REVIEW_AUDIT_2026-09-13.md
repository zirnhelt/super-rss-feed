# Article Review Audit

_Generated: 2026-09-13 17:03 UTC — ratings window 2026-06-17 → 2026-09-13_

## Executive Summary

| Metric | Value |
|---|---|
| Articles rated (unique URLs) | 1455 |
| Rated **bad** — reached you (pipeline failed) | 371 |
| Rated **bad** — correctly rejected (pipeline worked) | 604 |
| Rated **good** | 345 (23.7%) |
| Rated **interesting** | 131 |
| Reweighted good-or-interesting rate of the **shipped** feed | 44.9% (from 14.1% of shipped ratings) |
| Scrub false-negative rate (wanted articles thrown away) | 17.9% of 737 rejects |
| Theme-day corrections (`better_theme`) | 285 (19.7% of day-routed ratings) |
| …where the theme scorer already preferred your day | 108 |
| …where the theme scorer disagreed with you | 177 |
| …of those, actually routed by podcast selection | 0 |
| Category retags | 69 (9.5% of categorized ratings) |

### Sampling strata

The review feed is a **quota** sample: a fixed handful from each score band plus up to 10 scrub rejects. Rates within a stratum are unbiased; the corpus-wide rate is not, because half the ratings come from the reject pile. Reweight before comparing anything across strata.

| Stratum | n | good | interesting | bad | % good | % good+int |
|---|---|---|---|---|---|---|
| unfiltered | 737 | 71 | 61 | 604 | 9.6 | 17.9 |
| border | 297 | 116 | 50 | 131 | 39.1 | 55.9 |
| mid | 248 | 100 | 10 | 138 | 40.3 | 44.4 |
| low | 107 | 20 | 8 | 79 | 18.7 | 26.2 |
| high | 52 | 34 | 0 | 18 | 65.4 | 65.4 |
| unknown | 7 | 4 | 0 | 3 | 57.1 | 57.1 |
| floor_fill | 7 | 0 | 2 | 5 | 0.0 | 28.6 |

## 1. Scoring Precision vs. Your Verdicts

### Pipeline score by verdict

| Verdict | n | Mean score | Median | Mean quality (Q) | Mean relevance (R) |
|---|---|---|---|---|---|
| good | 345 | 50.8 | 49 | 42.6 | 42.1 |
| interesting | 131 | 38.5 | 45 | 27.2 | 22.7 |
| bad | 978 | 34.8 | 29.0 | 22.5 | 19.6 |

### Precision by score band

| Score band | n | good | bad | % good | % bad |
|---|---|---|---|---|---|
| 80-100 | 65 | 39 | 26 | 60.0 | 40.0 |
| 60-79 | 181 | 70 | 103 | 38.7 | 56.9 |
| 40-59 | 454 | 148 | 245 | 32.6 | 54.0 |
| 20-39 | 430 | 60 | 324 | 14.0 | 75.3 |
| 0-19 | 325 | 28 | 280 | 8.6 | 86.2 |

### Threshold sweep — what a higher quality floor would have done

Current `min_claude_score` floor: **25** (manually lowered 20 → 13 on 2026-06-24).

| Floor | Bad cut | % of bad | Good lost | % of good |
|---|---|---|---|---|
| 13 | 68 | 7.0 | 7 | 2.0 |
| 15 | 174 | 17.8 | 19 | 5.5 |
| 20 | 280 | 28.6 | 28 | 8.1 |
| 25 | 362 | 37.0 | 36 | 10.4 |
| 30 | 519 | 53.1 | 69 | 20.0 |
| 35 | 571 | 58.4 | 78 | 22.6 |
| 40 | 604 | 61.8 | 88 | 25.5 |
| 45 | 656 | 67.1 | 107 | 31.0 |
| 50 | 802 | 82.0 | 219 | 63.5 |
| 60 | 849 | 86.8 | 236 | 68.4 |

### By category

| Category | n | good | interesting | bad | % bad |
|---|---|---|---|---|---|
| news | 1066 | 182 | 52 | 832 | 78.0 |
| ai-tech | 110 | 42 | 27 | 41 | 37.3 |
| wellness | 96 | 25 | 18 | 52 | 54.2 |
| local | 52 | 37 | 1 | 14 | 26.9 |
| climate | 32 | 20 | 4 | 8 | 25.0 |
| homelab | 24 | 7 | 11 | 6 | 25.0 |
| science | 24 | 19 | 2 | 3 | 12.5 |
| design | 17 | 2 | 7 | 8 | 47.1 |
| scifi | 13 | 1 | 3 | 9 | 69.2 |
| outdoors | 9 | 3 | 4 | 2 | 22.2 |
| homestead | 5 | 3 | 2 | 0 | 0.0 |
| shared | 4 | 4 | 0 | 0 | 0.0 |
| podcast-sunday | 2 | 0 | 0 | 2 | 100.0 |
| podcast-friday | 1 | 0 | 0 | 1 | 100.0 |

### Sources (≥ 5 ratings)

**Highest good-rate**

| Source | n | good | bad | % good |
|---|---|---|---|---|
| Eagle Feather News | 6 | 6 | 0 | 100.0 |
| 100 Mile Free Press | 10 | 8 | 2 | 80.0 |
| The Narwhal | 5 | 4 | 1 | 80.0 |
| EarthSky | 5 | 4 | 1 | 80.0 |
| Williams Lake Tribune | 22 | 17 | 5 | 77.3 |
| ScienceAlert | 13 | 10 | 2 | 76.9 |
| ScienceDaily | 10 | 7 | 1 | 70.0 |
| BC Gov News | 15 | 10 | 5 | 66.7 |
| APTN News | 10 | 6 | 3 | 60.0 |
| MakeUseOf | 5 | 3 | 2 | 60.0 |

**Highest bad-rate**

| Source | n | good | bad | % bad |
|---|---|---|---|---|
| Rolling Stone | 24 | 0 | 24 | 100.0 |
| The New Yorker | 9 | 0 | 9 | 100.0 |
| Cottage Life | 8 | 0 | 8 | 100.0 |
| The Atlantic | 8 | 0 | 8 | 100.0 |
| Live for the Outdoors (Country Walking) | 6 | 0 | 6 | 100.0 |
| Mother Jones | 6 | 0 | 6 | 100.0 |
| Edge (GamesRadar) | 27 | 0 | 25 | 92.6 |
| Lifehacker | 25 | 3 | 22 | 88.0 |
| Toms Guide | 40 | 5 | 35 | 87.5 |
| Ideal Home (Country Homes & Interiors) | 24 | 0 | 21 | 87.5 |

## 2. Fluff Quantification

### Verdicts by content type

| Content type | good | interesting | bad |
|---|---|---|---|
| unlabeled | 249 | 80 | 823 |
| breaking | 34 | 18 | 63 |
| analysis | 33 | 19 | 30 |
| feature | 18 | 7 | 32 |
| news | 5 | 4 | 11 |
| opinion | 3 | 2 | 12 |
| recap | 1 | 0 | 3 |
| wire | 2 | 0 | 2 |
| investigation | 0 | 1 | 1 |
| fluff | 0 | 0 | 1 |

### Verdicts by selection bucket

| Bucket | good | interesting | bad |
|---|---|---|---|
| border | 116 | 50 | 131 |
| low | 20 | 8 | 79 |
| high | 34 | 0 | 18 |
| mid | 100 | 10 | 138 |
| unknown | 4 | 0 | 3 |
| unfiltered | 71 | 61 | 604 |
| floor_fill | 0 | 2 | 5 |

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

## 3. Theme-Bucket Routing Accuracy

Of **1448** ratings tied to an aired day, you corrected the day on **285** (19.7%). Additionally 168 good articles were approved for other days.

### Per theme day

| Day | Theme | n | good | bad | % good | Corrected away |
|---|---|---|---|---|---|---|
| monday | Arts, Culture & Digital Storytelling | 224 | 43 | 154 | 19.2 | 40 |
| tuesday | Working Lands & Industry | 195 | 34 | 148 | 17.4 | 27 |
| wednesday | Repair Culture & Practical Tech | 254 | 79 | 158 | 31.1 | 53 |
| thursday | Indigenous Lands & Innovation | 187 | 33 | 130 | 17.6 | 31 |
| friday | Wild Spaces & Outdoor Life | 265 | 58 | 179 | 21.9 | 52 |
| saturday | Cariboo Local Affairs | 191 | 56 | 127 | 29.3 | 52 |
| sunday | Science, Wonder & the Natural World | 132 | 38 | 79 | 28.8 | 30 |

### Day → day correction matrix (shown → should-have-been)

| Shown \ Better | monday | tuesday | wednesday | thursday | friday | saturday | sunday |
|---|---|---|---|---|---|---|---|
| monday |  | 11 | 8 | 1 | 5 | 4 | 11 |
| tuesday | 7 |  | 5 | 2 | 5 | 3 | 5 |
| wednesday | 6 | 8 |  | 2 | 13 | 11 | 13 |
| thursday | 1 | 5 | 7 |  | 7 | 1 | 10 |
| friday | 6 | 10 | 10 | 5 |  | 7 | 14 |
| saturday | 2 | 4 | 12 | 5 | 9 |  | 20 |
| sunday | 4 | 7 | 8 | 1 | 5 | 5 |  |

### Root cause of corrections

| Cause | Count |
|---|---|
| Selection ignored its own theme scores (routing bug) | 108 |
| Theme scorer disagreed with you (scoring miss) | 177 |
| Theme scores missing on the rating | 0 |

## 3b. Category Retag Accuracy

Of **726** ratings carrying a confirmed/retagged category, you retagged **69** (9.5%) to a different category.

### Category → category correction matrix (shown → corrected)

| Shown | Corrected to | Count |
|---|---|---|
| news | ai-tech | 18 |
| news | homelab | 10 |
| news | wellness | 6 |
| news | outdoors | 6 |
| news | design | 6 |
| news | homestead | 5 |
| news | climate | 4 |
| news | local | 3 |
| news | science | 2 |
| news | scifi | 2 |
| science | climate | 1 |
| science | wellness | 1 |
| science | news | 1 |
| design | homelab | 1 |
| local | news | 1 |
| local | climate | 1 |
| wellness | climate | 1 |

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
| 2026-W37 | 6 | 1628 | 95 |

### Current funnel (calibration stats window)

| Run | Fetched | New | Quality passed | Dropped below floor | Scrub removed |
|---|---|---|---|---|---|
| 2026-08-30T09:52:10.114082+00:00 | 1669 | 891 | 76 | 476 | 170 |
| 2026-08-30T11:17:56.653853+00:00 | 1053 | 711 | 57 | 440 | 97 |
| 2026-08-30T12:21:08.068946+00:00 | 1643 | 781 | 50 | 401 | 165 |
| 2026-08-31T10:44:00.977987+00:00 | 1479 | 726 | 93 | 367 | 153 |
| 2026-08-31T14:31:30.879532+00:00 | 1532 | 730 | 79 | 359 | 173 |
| 2026-09-01T04:01:23.708934+00:00 | 1124 | 752 | 95 | 386 | 158 |
| 2026-09-01T07:01:01.055542+00:00 | 891 | 554 | 53 | 291 | 106 |
| 2026-09-01T14:29:28.230822+00:00 | 1477 | 776 | 84 | 434 | 138 |
| 2026-09-02T04:01:04.895939+00:00 | 1723 | 1007 | 89 | 580 | 163 |
| 2026-09-03T04:01:05.181342+00:00 | 1746 | 1134 | 101 | 697 | 192 |
| 2026-09-04T04:01:04.999546+00:00 | 1864 | 1182 | 96 | 750 | 204 |
| 2026-09-05T04:01:30.153057+00:00 | 1842 | 1140 | 99 | 725 | 172 |
| 2026-09-06T04:01:09.004617+00:00 | 1414 | 847 | 92 | 511 | 136 |
| 2026-09-07T04:01:02.273459+00:00 | 1127 | 622 | 80 | 271 | 135 |
| 2026-09-08T04:01:07.188970+00:00 | 1223 | 751 | 93 | 534 | 81 |
| 2026-09-09T07:01:41.204128+00:00 | 1596 | 1026 | 98 | 766 | 127 |
| 2026-09-10T13:54:05.139005+00:00 | 1884 | 1207 | 98 | 937 | 138 |
| 2026-09-11T04:01:16.036321+00:00 | 1844 | 1147 | 90 | 875 | 128 |
| 2026-09-12T04:01:07.363565+00:00 | 1782 | 1135 | 101 | 879 | 111 |
| 2026-09-13T04:01:03.708594+00:00 | 1442 | 849 | 91 | 635 | 85 |

### Current category feed sizes

| Feed | Items |
|---|---|
| news | 122 |
| ai-tech | 88 |
| wellness | 58 |
| science | 44 |
| local | 41 |
| homelab | 40 |
| climate | 37 |
| design | 28 |
| outdoors | 10 |
| homestead | 9 |
| scifi | 7 |

## 5. Process Health

| Check | State |
|---|---|
| Calibration log entries / "No changes" entries | 21 / 9 |
| Calibration stats runs available | 20 |
| Calibration stats range | 2026-08-30 → 2026-09-13 |
| theme_holdover_cache.json present | True |

**Context:** `calibration_stats_cache.json` was first committed on 2026-07-07, so every weekly calibration run before that found no stats and skipped — the log's repeated "Claude call or response parsing failed" lines were misleading boilerplate, not API failures. The agent's Claude path has effectively never run.

