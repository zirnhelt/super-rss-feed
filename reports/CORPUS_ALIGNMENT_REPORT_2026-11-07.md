# Cache Corpus Alignment Report

_Generated: 2026-11-07 18:18 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1322 |
| Articles missing theme-score data (skipped) | 147 |
| Direct-qualify (upstream score gates them in for their best theme) | 1247 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 43 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 32 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 3 (0% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 697 |
| analysis | 385 |
| breaking | 178 |
| feature | 132 |
| opinion | 40 |
| recap | 19 |
| fluff | 9 |
| wire | 7 |
| news | 2 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 827 | 46.5 | 79.7 | +33.3 | 762 | 34 | 31 | 2 |
| ai-tech | 183 | 43.2 | 72.2 | +29.0 | 181 | 2 | 0 | 0 |
| science | 111 | 40.1 | 78.8 | +38.7 | 109 | 1 | 1 | 0 |
| wellness | 54 | 41.4 | 70.9 | +29.5 | 50 | 4 | 0 | 0 |
| climate | 48 | 43.4 | 77.7 | +34.3 | 47 | 1 | 0 | 1 |
| local | 42 | 64.6 | 97.8 | +33.3 | 42 | 0 | 0 | 0 |
| homelab | 30 | 47.3 | 86.0 | +38.7 | 30 | 0 | 0 | 0 |
| design | 18 | 39.2 | 71.3 | +32.1 | 17 | 1 | 0 | 0 |
| homestead | 6 | 59.7 | 98.5 | +38.8 | 6 | 0 | 0 | 0 |
| outdoors | 3 | 39.0 | 84.0 | +45.0 | 3 | 0 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1322 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 47.3 | 100 | 1089 | 870 |
| Tuesday | Working Lands & Industry | 44.2 | 100 | 965 | 730 |
| Wednesday | Repair Culture & Practical Tech | 45.7 | 100 | 990 | 789 |
| Thursday | Indigenous Lands & Innovation | 43.0 | 100 | 972 | 972 |
| Friday | Wild Spaces & Outdoor Life | 48.4 | 100 | 1162 | 920 |
| Saturday | Cariboo Local Affairs | 48.5 | 100 | 1218 | 1050 |
| Sunday | Science, Wonder & the Natural World | 49.0 | 100 | 1082 | 953 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 870 | 1019 | 47 | 23 |
| Tuesday | Working Lands & Industry | 30 | 15 | 730 | 876 | 59 | 30 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 789 | 925 | 38 | 27 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 972 | 916 | 27 | 29 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 920 | 1094 | 48 | 20 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 1050 | 1203 | 1 | 14 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 953 | 1019 | 46 | 17 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 60 | 27 | news | New York’s first measles death in 30 years is an omen of worse to come |
| 55 | 21 | news | Protein Can Help Build and Preserve Muscle, But Eating More Has Its Limits |
| 50 | 25 | climate | China Truck Sales Now Majority Electric. What’s Next? |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 97 | 22 | news | A Pro-Russia Strongman at Mar-a-Lago | friday |
| 97 | 20 | news | Bond investors pause Treasury bets before US midterm vote | friday |
| 96 | 26 | news | The Blue Tsunami Swept Doctors and Scientists Into Office | friday |
| 96 | 25 | news | STAT+: Democrats’ midterm landslide spells relief for hospitals | monday |
| 96 | 24 | news | STAT+: MAHA leader Calley Means castigates White House officials as bending to industry | thursday |
| 96 | 22 | climate | Global Icescapes Face Irreversible Damage As World Nears Overshoot | friday |
| 96 | 20 | news | Susan Collins Didn’t Have a Chance | friday |
| 95 | 25 | news | Midterm Wave Sets a Course for ‘Medicare for All’ Fight | friday |
| 94 | 24 | news | Election workers prepare for contested results ahead of U.S. midterms | friday |
| 94 | 23 | news | Researchers Identify Suspicious Activity on Kalshi and Polymarket Before Times/Siena Poll Release | thursday |
| 93 | 25 | news | British healthcare worker with Ebola evacuated from DR Congo to UK | monday |
| 93 | 23 | wellness | Has Trump kept his promises to the MAHA movement? | thursday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=25) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 100 | 19 | news | Adam Kai-Ji Lo, accused in Vancouver's Lapu Lapu Day attack, pleads not guilty | sunday |
| 100 | 19 | news | US judge permanently dismisses Trump’s $10 billion suit against Wall Street Journal | friday |
| 99 | 18 | news | British comedian Russell Brand convicted of rape and three sexual assaults | friday |
| 99 | 18 | news | Apple tells stores to inspect cracked iPhone Duo screens | wednesday |
| 99 | 17 | news | A Midterm Election Guide for Artists and Arts Workers | monday |
| 98 | 19 | news | Tomba Dei Gigante S’Ena e Thimes in Dorgali, Italy | monday |
| 98 | 16 | news | Democrats Sweep Republicans in Nearly Every Race That Matters | friday |
| 98 | 16 | news | Initial results indicate victory for Iotova in Bulgarian presidential vote | friday |
| 92 | 19 | news | Paraguay’s President Removed and Arrested Over Financial Crisis | monday |
| 91 | 10 | news | Saudi Arabia reportedly eyeing Unity buyout after controversial $55 billion EA acquisition | sunday |
| 90 | 18 | news | Israeli settlers seize 8 Palestinian homes in Jericho, displacing dozens | thursday |
| 90 | 15 | news | True or false? How fake online reviews are concerning businesses | tuesday |

---

## Recommendations

- 🌾 32 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=25) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1322 articles analysed · 2026-11-07 18:18 UTC_
