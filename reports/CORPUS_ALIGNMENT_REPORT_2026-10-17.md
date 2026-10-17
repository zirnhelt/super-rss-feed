# Cache Corpus Alignment Report

_Generated: 2026-10-17 16:39 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1333 |
| Articles missing theme-score data (skipped) | 110 |
| Direct-qualify (upstream score gates them in for their best theme) | 1216 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 46 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 24 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 56 (4% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 734 |
| analysis | 339 |
| feature | 151 |
| breaking | 125 |
| opinion | 48 |
| recap | 25 |
| fluff | 9 |
| news | 8 |
| wire | 3 |
| essay | 1 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 856 | 45.7 | 70.0 | +24.3 | 778 | 34 | 23 | 37 |
| ai-tech | 159 | 42.1 | 53.9 | +11.8 | 142 | 3 | 0 | 11 |
| science | 101 | 43.0 | 58.2 | +15.3 | 96 | 0 | 1 | 2 |
| wellness | 74 | 41.3 | 66.3 | +25.0 | 64 | 7 | 0 | 4 |
| local | 43 | 72.1 | 93.0 | +20.9 | 43 | 0 | 0 | 1 |
| design | 37 | 40.5 | 57.7 | +17.2 | 32 | 1 | 0 | 0 |
| climate | 29 | 45.4 | 65.1 | +19.7 | 28 | 0 | 0 | 0 |
| homelab | 22 | 45.0 | 88.4 | +43.4 | 22 | 0 | 0 | 1 |
| outdoors | 7 | 39.6 | 55.1 | +15.6 | 6 | 1 | 0 | 0 |
| homestead | 4 | 51.2 | 97.2 | +46.0 | 4 | 0 | 0 | 0 |
| scifi | 1 | 32.0 | 57.0 | +25.0 | 1 | 0 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1333 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 48.4 | 100 | 1124 | 953 |
| Tuesday | Working Lands & Industry | 45.0 | 100 | 952 | 763 |
| Wednesday | Repair Culture & Practical Tech | 42.6 | 100 | 1060 | 710 |
| Thursday | Indigenous Lands & Innovation | 46.7 | 100 | 1077 | 939 |
| Friday | Wild Spaces & Outdoor Life | 49.0 | 100 | 1167 | 955 |
| Saturday | Cariboo Local Affairs | 48.9 | 100 | 1224 | 1093 |
| Sunday | Science, Wonder & the Natural World | 49.3 | 100 | 1131 | 959 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 953 | 1045 | 55 | 24 |
| Tuesday | Working Lands & Industry | 30 | 15 | 763 | 866 | 62 | 24 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 710 | 989 | 47 | 24 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 939 | 1021 | 32 | 24 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 955 | 1086 | 56 | 25 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 1093 | 1207 | 0 | 17 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 959 | 1053 | 55 | 23 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 66 | 21 | local | How Much Can Municipal Candidates Lower Your Taxes? |
| 65 | 25 | news | Google’s quantum Willow chip may be able to grow ‘magic states’ |
| 64 | 28 | science | Triplet of ‘Ghostly’ Galaxies Hints at What Dark Matter Is — and Isn’t |
| 63 | 26 | news | 'Remarkably close to the minimum permitted by physics': this superconducting memory bit runs at an estimated 5x the limit, but at -269°C the fridge shrinks its claimed million-fold edge over today’s chips considerably |
| 60 | 26 | news | Workers Who Fear AI May be More Prone to Slacking Off |
| 60 | 20 | wellness | Why Grand Forks Has Put Money into Health Care |
| 60 | 20 | news | Tough Puzzles at the Community Privacy Residency |
| 60 | 18 | news | Katie Zacharia Was Linked to an AI Rare-Earths Startup. It’s Even Weirder Than It Sounds |
| 60 | 5 | news | Love is infrastructure |
| 58 | 29 | news | Can’t bear to say goodbye to your pet? Biotech’s got you covered. |
| 58 | 29 | news | AI vs. the railroads |
| 58 | 20 | news | Elon Musk's Terafab will reportedly receive its first EUV tool from ASML in mid-2027 |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 99 | 27 | news | A Local Artist's Guide to Detroit's Black History | monday |
| 99 | 27 | news | Abolish Frats | friday |
| 99 | 26 | design | Architecture is "much the same" as music says Daniel Libeskind | monday |
| 99 | 24 | news | Ukrainian drones strike largest data center in Russia, multiple parts of 1.4 million square foot campus knocked offline | monday |
| 99 | 23 | news | STAT+: Jury rules in favor of ousted Cambridge scientist David Sabatini, with $6 million in damages to be awarded | friday |
| 99 | 21 | news | Judge orders the Trump administration to cancel taxpayer-funded promotional TV ads | monday |
| 99 | 20 | news | Two Syrian pipelines damaged amid spate of attacks on energy infrastructure | sunday |
| 97 | 27 | news | Azerbaijan blocks TikTok, Instagram, and X amid growing protests over hijab rules | sunday |
| 97 | 26 | news | Taiz hospitals near collapse as Houthis tighten siege: Yemen government | friday |
| 97 | 23 | news | Elk Valley RCMP urge hunting safety after bullet strikes Fernie home | thursday |
| 97 | 22 | wellness | Pope Leo XIV will have surgery in the coming days to remove a nodule on his lung | friday |
| 96 | 27 | wellness | Pope Leo Has Lung Cancer, Vatican Says | friday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=25) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 100 | 18 | news | Families demand justice after Pakistan school collapse | friday |
| 100 | 16 | news | Global pro-Palestinian protests one year after Gaza ‘ceasefire’ | friday |
| 100 | 15 | news | Peshawar mourns children killed in school roof collapse | monday |
| 100 | 15 | news | Pakistani national killed in second Houthi strike on Riyadh airport | friday |
| 100 | 15 | news | Deadly air strike kills dozens at Sudan gold mine near Egypt border | monday |
| 99 | 19 | news | Want to improve your time management? Lower your expectations | monday |
| 99 | 16 | news | Clashes erupt at protest over university funding law in Argentina | saturday |
| 98 | 16 | news | Argentine students protest on campus over Milei’s austerity | saturday |
| 98 | 12 | news | Houthi missile attack targets Saudi capital Riyadh for third day in a row | friday |
| 97 | 16 | news | Iran war live: IRGC says supertanker hit naval mine in Hormuz, catches fire | friday |
| 93 | 14 | news | At least 139 dead as migrant boat from Djibouti to Yemen capsizes | saturday |
| 92 | 18 | news | Yemeni government’s military says its forces advancing against Houthis | friday |

---

## Recommendations

- 🌾 24 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=25) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1333 articles analysed · 2026-10-17 16:39 UTC_
