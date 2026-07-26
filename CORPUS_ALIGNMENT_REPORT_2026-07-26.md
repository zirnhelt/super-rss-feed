# Cache Corpus Alignment Report

_Generated: 2026-07-26 14:43 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 756 |
| Articles missing theme-score data (skipped) | 491 |
| Direct-qualify (upstream score gates them in for their best theme) | 298 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 55 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 325 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 21 (3% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 608 |
| breaking | 239 |
| analysis | 137 |
| feature | 102 |
| fluff | 64 |
| news | 62 |
| recap | 15 |
| wire | 11 |
| opinion | 9 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 483 | 18.2 | 41.4 | +23.2 | 112 | 32 | 283 | 0 |
| ai-tech | 90 | 35.8 | 34.2 | -1.6 | 64 | 0 | 17 | 6 |
| wellness | 63 | 25.5 | 40.8 | +15.3 | 28 | 18 | 12 | 3 |
| local | 47 | 78.7 | 62.7 | -16.0 | 46 | 0 | 0 | 6 |
| science | 35 | 39.3 | 39.8 | +0.5 | 26 | 0 | 6 | 4 |
| climate | 24 | 31.1 | 43.8 | +12.7 | 13 | 5 | 4 | 0 |
| homelab | 12 | 34.3 | 43.5 | +9.2 | 7 | 0 | 3 | 2 |
| scifi | 2 | 37.0 | 21.0 | -16.0 | 2 | 0 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 756 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 26.7 | 80 | 491 | 267 |
| Tuesday | Working Lands & Industry | 26.6 | 80 | 489 | 229 |
| Wednesday | Repair Culture & Practical Tech | 26.7 | 80 | 544 | 265 |
| Thursday | Indigenous Lands & Innovation | 26.8 | 80 | 550 | 318 |
| Friday | Wild Spaces & Outdoor Life | 26.7 | 80 | 544 | 261 |
| Saturday | Cariboo Local Affairs | 26.3 | 80 | 610 | 437 |
| Sunday | Science, Wonder & the Natural World | 26.9 | 80 | 489 | 268 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 267 | 234 | 46 | 211 |
| Tuesday | Working Lands & Industry | 30 | 15 | 229 | 219 | 54 | 216 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 265 | 247 | 52 | 245 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 318 | 255 | 37 | 258 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 261 | 254 | 58 | 232 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 437 | 319 | 20 | 271 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 268 | 241 | 52 | 196 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 90 | 10 | local | ‘Are you ready’: Clearwater mayor advises on wildfire preparedness as Cariboo blazes force evacuations |
| 89 | 29 | local | ‘This is just silly’: B.C.’s Eby threatens U.S. access to Canadian minerals over tariffs |
| 86 | 28 | local | TNRD extends evacuation alert to all properties in Loon Lake community |
| 85 | 26 | local | The Cariboo’s Junior A hockey teams have learned where their upcoming battles lie : My Cariboo Now |
| 85 | 24 | local | Rule Symposium Video: Cariboo deep hits point to larger mine, says Roosen |
| 81 | 26 | local | Jean Wallace Bishopp |
| 62 | 6 | homelab | Home Assistant Predictive Energy Control with Local ML 2026 |
| 60 | 27 | science | A healthier global diet could cut farm emissions by 85% |
| 60 | 17 | ai-tech | ‘Powerful AI systems can go rogue, behave in extremely dangerous ways, or even resist human intervention’: A bill requiring AI systems to have a ‘kill switch’ is now in Congress |
| 59 | 13 | science | China’s Tianwen-1 captures interstellar comet 3I/ATLAS near Mars |
| 58 | 22 | homelab | This free browser tool beats Bambu Lab at its own game |
| 57 | 29 | ai-tech | 250 Eiffel Towers' worth of waste: The AI boom's toxic hardware problem |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 80 | 26 | news | French wildfires trigger mass evacuations around Bordeaux | wednesday |
| 80 | 20 | news | Wildfire forces another 55,000 people to evacuate in southwest France | friday |
| 80 | 11 | climate | Province, partners strengthen Cowichan watershed through estuary restoration | sunday |
| 79 | 26 | news | Body of missing 10-year-old boy recovered in Nutimik Lake, search continues for 13-year-old brother | sunday |
| 78 | 25 | news | La Casa del Serpentello in Vignale Monferrato, Italy | wednesday |
| 78 | 24 | news | Sons of immigrant killed by ICE in Texas share grief, demand accountability | wednesday |
| 77 | 24 | news | Government Surveillance Power Rebuked as Landowners Win Massive Property Rights Battle - AgWeb | tuesday |
| 75 | 12 | wellness | Instagram without* scrolling | thursday |
| 74 | 22 | news | Dinos with swords, making music with gnomes and other new indie games worth checking out | monday |
| 73 | 28 | news | John Deere Expands C-Series Lineup with High-Capacity C1450T Air Cart - AgWeb | tuesday |
| 72 | 17 | wellness | The Good List: 6 Things to Bring Joy and Delight to Your Day | thursday |
| 71 | 11 | wellness | Health Care Agency Discontinues Dozens of Active Research Awards | thursday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=20) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 80 | 16 | news | Firefighters battle fire after fertiliser explosion in England | wednesday |
| 80 | 15 | news | "AI moves fast. Human hearts move slow." | thursday |
| 79 | 16 | news | Trump’s HIV funding cuts having ‘severe and devastating’ impact around the world | thursday |
| 78 | 11 | news | Robertson set for another season with Dallas Stars after signing for $12 million | friday |
| 78 | 7 | news | Minnesota United plays to scoreless draw against visiting Whitecaps | friday |
| 77 | 18 | news | In photos: High-flying insanity at the 2026 Farnborough Air Show | thursday |
| 77 | 16 | news | We bought a house and regretted it after 2 years. Now, we own an apartment instead. | friday |
| 77 | 16 | news | Judge hears evidence against singer D4vd in killing, dismemberment of teen | monday |
| 77 | 9 | news | We Saw the Future of Outdoor Gear at OMA. It’s Cheaper, Lighter, and More Practical. | wednesday |
| 76 | 10 | news | Chris Brown pleads guilty to charge over London nightclub fight | tuesday |
| 76 | 10 | news | STAT+: Advocates say federal funding is being cut from groups fighting HIV | thursday |
| 76 | 8 | news | Kensington Palace marks Prince George's 13th birthday with new photo | tuesday |

---

## Recommendations

- 🌾 325 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=20) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 756 articles analysed · 2026-07-26 14:43 UTC_
