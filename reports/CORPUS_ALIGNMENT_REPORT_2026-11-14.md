# Cache Corpus Alignment Report

_Generated: 2026-11-14 18:54 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1315 |
| Articles missing theme-score data (skipped) | 159 |
| Direct-qualify (upstream score gates them in for their best theme) | 1262 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 32 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 21 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 13 (1% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 670 |
| analysis | 402 |
| breaking | 188 |
| feature | 148 |
| opinion | 39 |
| recap | 18 |
| wire | 6 |
| fluff | 2 |
| news | 1 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 776 | 47.9 | 78.9 | +31.0 | 730 | 27 | 19 | 9 |
| ai-tech | 174 | 41.9 | 69.0 | +27.0 | 171 | 3 | 0 | 2 |
| science | 138 | 41.3 | 80.6 | +39.3 | 134 | 2 | 2 | 0 |
| climate | 73 | 46.7 | 80.0 | +33.3 | 73 | 0 | 0 | 1 |
| wellness | 59 | 39.8 | 73.9 | +34.1 | 59 | 0 | 0 | 1 |
| local | 34 | 75.4 | 98.9 | +23.5 | 34 | 0 | 0 | 0 |
| design | 27 | 37.4 | 62.0 | +24.5 | 27 | 0 | 0 | 0 |
| homelab | 24 | 42.9 | 82.8 | +39.9 | 24 | 0 | 0 | 0 |
| homestead | 7 | 57.4 | 89.3 | +31.9 | 7 | 0 | 0 | 0 |
| outdoors | 2 | 50.0 | 91.0 | +41.0 | 2 | 0 | 0 | 0 |
| scifi | 1 | 45.0 | 37.0 | -8.0 | 1 | 0 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1315 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 47.7 | 100 | 1089 | 892 |
| Tuesday | Working Lands & Industry | 44.8 | 100 | 988 | 754 |
| Wednesday | Repair Culture & Practical Tech | 47.4 | 100 | 1122 | 897 |
| Thursday | Indigenous Lands & Innovation | 44.1 | 100 | 1029 | 730 |
| Friday | Wild Spaces & Outdoor Life | 48.6 | 100 | 1126 | 941 |
| Saturday | Cariboo Local Affairs | 48.7 | 100 | 1153 | 1056 |
| Sunday | Science, Wonder & the Natural World | 48.9 | 100 | 1096 | 947 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 892 | 1045 | 27 | 17 |
| Tuesday | Working Lands & Industry | 30 | 15 | 754 | 924 | 47 | 17 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 897 | 1077 | 30 | 15 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 730 | 996 | 16 | 17 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 941 | 1083 | 27 | 16 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 1056 | 1141 | 0 | 12 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 947 | 1051 | 30 | 15 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 58 | 25 | news | Megaspeed exec was recruited to spy on Nvidia CEO, according to US intelligence memo |
| 55 | 28 | news | This Photo of the ISS Next to Jupiter Was Two Years in the Making |
| 55 | 27 | wellness | The Libre and Dexcom CGMs shared an arm. They didn’t share a GMI. |
| 55 | 22 | news | Fast by Default: Compile-Time Heuristics for Helion Kernels |
| 52 | 29 | news | The Pulse: Details of incident.io’s AI spend |
| 52 | 28 | news | Do EVs Wear Tires Faster? Here's What The Studies Show |
| 52 | 25 | news | The Design Village: Educating the Next Generation of Designers for Social Transformation |
| 52 | 20 | news | Peanuts Native brings 12 Switch games to Android without an emulator layer |
| 51 | 22 | ai-tech | 'Model weights need the same level of scrutiny as code': Microsoft researchers find AI agents can be backdoored by editing just a few neurons |
| 50 | 29 | news | Digital sovereignty is about resilience, including blocking cyber threats |
| 50 | 25 | ai-tech | AI Models Can Tell When Researchers Plant Concepts in Their Neural Networks. Is It Self-Reflection? |
| 50 | 24 | climate | The climate case for AI has not been made |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 99 | 23 | news | From the streets of Lagos to the Chanel catwalk: how a creative’s thrift-shop style took her to Paris | monday |
| 96 | 21 | news | Israel bars French presidential contender Mélenchon over Gaza flotilla pledge | sunday |
| 95 | 24 | news | Surrey Mayor Doug McCallum calls for immediate action on all campaign promises | thursday |
| 95 | 22 | news | Liberals Expressed Regret To Israeli Ambassador Over Arms Export Pause | thursday |
| 94 | 27 | news | Azerbaijan jails Meclis.info journalists for up to 10 years over Western funding | wednesday |
| 94 | 27 | news | German committee adds patient confidentiality safeguards to intelligence reform | sunday |
| 94 | 24 | news | UK court convicts two Iranians in plot targeting dissident journalists | tuesday |
| 93 | 23 | news | What Mark Zuckerberg, Andy Jassy, Sam Altman, and other tech execs have said about parenting | thursday |
| 91 | 29 | news | STAT+: Alnylam, once in the hunt to be a $100 billion biotech, needs to solve its heart drug problem | tuesday |
| 91 | 28 | news | Qantas Airbus A350-1000ULR sets world-record longest commercial flight | tuesday |
| 90 | 23 | news | DOJ sues Lyft for allegedly denying rides to people with disabilities | sunday |
| 88 | 26 | science | Q&A: From seed funding to scientific breakthroughs | sunday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=25) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 100 | 16 | news | Cognitive distortion pedals | friday |
| 99 | 17 | news | South African authorities arrest nine Zimbabweans over alleged plan to join Russia-Ukraine war | friday |
| 98 | 19 | news | Malaysian lawyers back court review as Najib house-arrest transfer remains stalled | friday |
| 98 | 16 | news | Poland declares mourning after Kraków shooting kills six, injures foreigners | friday |
| 92 | 18 | news | STAT+: Dutch antitrust regulators probe Biogen over test for its MS drug | monday |
| 92 | 18 | news | President Milei welcomes Pope Leo during historic visit to Argentina | monday |
| 92 | 16 | news | Siemens Energy adds €9 billion buyback through 2030 | saturday |
| 90 | 11 | news | Saudi coalition intercepts five missiles as witnesses report Riyadh tower damage | saturday |
| 87 | 24 | science | Cancer-fighting chewing gum slashes HPV levels by up to 93% | friday |
| 87 | 16 | news | On the Inerrancy of the Council of Jerusalem | wednesday |
| 86 | 16 | news | For Over a Decade, They’ve Been the Face of the World’s Most Entrancing Treasure Hunt. Have They Finally Solved Oak Island’s Mystery? | thursday |
| 78 | 14 | news | Biden says cancer diagnosis would have ended 2024 reelection bid | saturday |

---

## Recommendations

- 🌾 21 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=25) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1315 articles analysed · 2026-11-14 18:54 UTC_
