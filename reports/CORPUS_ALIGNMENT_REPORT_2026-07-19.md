# Cache Corpus Alignment Report

_Generated: 2026-07-19 14:31 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1228 |
| Articles missing theme-score data (skipped) | 31 |
| Direct-qualify (upstream score gates them in for their best theme) | 492 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 130 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 476 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 36 (3% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 585 |
| breaking | 278 |
| feature | 125 |
| analysis | 122 |
| fluff | 77 |
| news | 36 |
| opinion | 19 |
| wire | 11 |
| recap | 5 |
| investigation | 1 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 801 | 18.7 | 40.5 | +21.9 | 186 | 93 | 425 | 3 |
| ai-tech | 109 | 33.0 | 37.9 | +4.9 | 76 | 5 | 15 | 2 |
| wellness | 100 | 26.6 | 40.1 | +13.5 | 50 | 24 | 18 | 3 |
| science | 75 | 42.1 | 41.1 | -0.9 | 61 | 1 | 10 | 13 |
| local | 63 | 80.4 | 64.5 | -16.0 | 62 | 0 | 1 | 6 |
| climate | 52 | 41.7 | 45.0 | +3.4 | 39 | 7 | 2 | 6 |
| homelab | 15 | 35.1 | 43.3 | +8.1 | 10 | 0 | 2 | 1 |
| scifi | 12 | 34.2 | 37.2 | +3.0 | 8 | 0 | 2 | 2 |
| unknown | 1 | 7.0 | 29.0 | +22.0 | 0 | 0 | 1 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1228 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 26.7 | 80 | 796 | 428 |
| Tuesday | Working Lands & Industry | 26.8 | 80 | 801 | 376 |
| Wednesday | Repair Culture & Practical Tech | 26.6 | 80 | 880 | 426 |
| Thursday | Indigenous Lands & Innovation | 26.6 | 80 | 881 | 510 |
| Friday | Wild Spaces & Outdoor Life | 26.6 | 80 | 878 | 428 |
| Saturday | Cariboo Local Affairs | 26.8 | 80 | 1000 | 712 |
| Sunday | Science, Wonder & the Natural World | 26.6 | 80 | 795 | 428 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 428 | 373 | 121 | 302 |
| Tuesday | Working Lands & Industry | 30 | 15 | 376 | 361 | 132 | 308 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 426 | 401 | 134 | 345 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 510 | 416 | 100 | 365 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 428 | 417 | 131 | 330 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 712 | 550 | 30 | 420 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 428 | 394 | 126 | 275 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 92 | 26 | local | HANSEN: Inclement weather causes road damage, fire in Lac La Hache |
| 92 | 23 | local | Highway 1 remains closed at Boston Bar due to wildfires |
| 90 | 26 | local | Trains, fictional mining town characters at Williams Lake Station House Gallery |
| 85 | 22 | local | CARIBOO OUTDOORS: Kokanee Fishing 101 in the South Cariboo |
| 75 | 26 | local | $8M worth of illicit cannabis seized in four separate enforcement actions in B.C. |
| 73 | 23 | local | Alberta RCMP search for 2 missing children, 2 wanted adults possibly in Okanagan |
| 62 | 19 | science | Deep-sea life has a secret food source scientists never expected |
| 61 | 19 | homelab | Bambu Lab A2L review: This 3D printer makes large-format printing look easy |
| 60 | 9 | climate | 'The end of an era': China enforces mandatory rule to cull inefficient solar panels, signals end of ultra-cheap PV price wars |
| 59 | 25 | science | Are there aliens on exoplanet K2-18b? Scientists just scanned it for signals |
| 58 | 22 | science | Koalas nearly went extinct before humans arrived, DNA study reveals |
| 58 | 21 | climate | Chinese solar company says its new cell has an efficiency of 35.5 percent |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 80 | 27 | news | Grace Episcopal Church of City Island in Bronx, New York | wednesday |
| 80 | 25 | news | St. Stephen's Day Storm Memorial in Budapest, Hungary | tuesday |
| 80 | 23 | news | Back-to-School Shoppers Are Using More Tech Tools but Buying Fewer Tech Goods | thursday |
| 80 | 22 | news | Drone video shows scale of major wildfire in northern Spain | wednesday |
| 80 | 21 | news | Friedrich Ebert Memorial in Heidelberg, Germany | tuesday |
| 79 | 15 | ai-tech | The Quest for ‘Technological Sovereignty’ in Europe (and Why It’s So Hard) | thursday |
| 78 | 24 | news | More details emerge about Vancouver stranger assault suspect | sunday |
| 78 | 23 | news | Sand sculptures damaged by vandals at Vancouver Island beach festival, organizers say | friday |
| 78 | 21 | news | United Airlines flights delayed nationwide after 'technology outage' | thursday |
| 78 | 21 | news | Pont de la Bâtiaz in Martigny, Switzerland | wednesday |
| 78 | 20 | news | Falling debris from intercepted Iranian strikes sparks fires in Kuwait | wednesday |
| 78 | 20 | news | Subpoenas issued to NY Times reporters seen as 'unprecedented' threat to press freedom | monday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=18) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 80 | 8 | news | Flyers lock up Trevor Zegras with a 4-year deal worth $9.125M per year | friday |
| 80 | 6 | news | Benchmarking Repairability Scores with an Asus Tablet | wednesday |
| 79 | 13 | news | If I only had $100 to refresh my patio and garden, these are the 13 outdoor deals I'd buy | friday |
| 78 | 17 | news | Building stronger tourism economy in the Kootenays | tuesday |
| 78 | 13 | news | Chloe Fineman exits SNL after 7 seasons | monday |
| 78 | 12 | local | A $14,400 jackpot, one winner, absolute carnage — a perfect Crash to Pass : My Cariboo Now | monday |
| 78 | 8 | news | Sam Antonacci's two-run homer kick-starts White Sox 12-4 rout of Blue Jays | sunday |
| 78 | 8 | news | Giant participation trophy appears on the National Mall for Trump's Iran War "effort" | wednesday |
| 78 | 6 | news | Federal Antitrust Agencies Settle Cases on Farm Equipment Repair and Egg Prices | Civil Eats | tuesday |
| 77 | 7 | news | This Luddite Puppet Hopes You’re Not Reading This on Your Smartphone | thursday |
| 77 | 5 | news | Why Repairability Is So Important During RAMageddon | wednesday |
| 76 | 17 | news | Thunderstorms, Flooding and Strong Winds Sweep the Northeast | wednesday |

---

## Recommendations

- 🌾 476 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=18) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1228 articles analysed · 2026-07-19 14:31 UTC_
