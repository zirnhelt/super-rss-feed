# Cache Corpus Alignment Report

_Generated: 2026-10-31 18:00 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1296 |
| Articles missing theme-score data (skipped) | 126 |
| Direct-qualify (upstream score gates them in for their best theme) | 1244 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 35 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 17 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 0 (0% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 654 |
| analysis | 385 |
| breaking | 171 |
| feature | 133 |
| opinion | 44 |
| recap | 19 |
| fluff | 7 |
| news | 5 |
| wire | 4 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 784 | 47.9 | 82.3 | +34.4 | 741 | 28 | 15 | 0 |
| ai-tech | 196 | 43.1 | 74.6 | +31.4 | 192 | 3 | 1 | 0 |
| science | 92 | 46.6 | 81.9 | +35.3 | 91 | 0 | 1 | 0 |
| wellness | 71 | 39.1 | 72.0 | +32.9 | 67 | 4 | 0 | 0 |
| climate | 46 | 43.7 | 85.4 | +41.7 | 46 | 0 | 0 | 0 |
| local | 41 | 72.5 | 98.0 | +25.5 | 41 | 0 | 0 | 0 |
| design | 28 | 41.5 | 67.0 | +25.5 | 28 | 0 | 0 | 0 |
| homelab | 27 | 50.1 | 88.2 | +38.1 | 27 | 0 | 0 | 0 |
| homestead | 6 | 56.2 | 97.2 | +41.0 | 6 | 0 | 0 | 0 |
| outdoors | 5 | 44.4 | 93.0 | +48.6 | 5 | 0 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1296 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 46.9 | 100 | 1018 | 893 |
| Tuesday | Working Lands & Industry | 43.9 | 100 | 942 | 679 |
| Wednesday | Repair Culture & Practical Tech | 43.1 | 100 | 1048 | 760 |
| Thursday | Indigenous Lands & Innovation | 42.1 | 100 | 1010 | 639 |
| Friday | Wild Spaces & Outdoor Life | 48.5 | 100 | 1081 | 917 |
| Saturday | Cariboo Local Affairs | 48.4 | 100 | 1154 | 1049 |
| Sunday | Science, Wonder & the Natural World | 48.8 | 100 | 1064 | 937 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 893 | 969 | 36 | 13 |
| Tuesday | Working Lands & Industry | 30 | 15 | 679 | 875 | 49 | 18 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 760 | 988 | 42 | 18 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 639 | 970 | 25 | 15 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 917 | 1041 | 30 | 10 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 1049 | 1145 | 0 | 9 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 937 | 1023 | 32 | 9 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 100 | 26 | news | Apple issues iPhone Duo hinge guidance as repairs and software gaps emerge | wednesday |
| 98 | 28 | news | Codelco accounting scandal claims eight more employees | tuesday |
| 98 | 20 | news | Redistricting Isn’t Going as Republicans Planned | friday |
| 96 | 20 | news | Democrats and Republicans Share Dueling Health Care Messages in Final Midterms Push | monday |
| 95 | 26 | wellness | Rising Healthcare Premiums Expose Deep Systemic Inefficiencies | monday |
| 95 | 21 | news | One open source app replaced three apps and freed 12GB of storage on my phone | wednesday |
| 93 | 26 | news | Is There a ‘Safest Seat’ in a Train Crash? Experts Say It’s Not So Simple. | friday |
| 93 | 25 | news | CPJ outraged by Egypt court conviction of journalist Lina Attalah, order of Mada Masr’s closure | monday |
| 93 | 25 | wellness | I trained for a marathon with the Pixel Watch 5; Google's Health Coach guided me all the way through | friday |
| 93 | 22 | news | A week with iPhone Duo: Folding refined, if not perfected | thursday |
| 92 | 24 | news | Israel’s Parties Gird for Wrangling to Form a Government, With No Clear Path | sunday |
| 92 | 24 | news | A researcher claims Samsung TVs use connected devices with mics to listen in on you | sunday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=25) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 98 | 21 | science | Rare Nanotyrannus dinosaur skeleton sells for $47.3 million in New York | sunday |
| 98 | 17 | news | Ex-FBI chief Comey defiant in the face of third prosecution | friday |
| 96 | 17 | news | Bavarian government vows to restore Hitler-era Eagle’s Nest after fire | monday |
| 95 | 17 | news | Could Lula Be on the Brink of Defeat in Brazil’s Election? | friday |
| 94 | 14 | news | Vote Against the Agenda of the Most Polluter-Positive President in Living Memory | thursday |
| 92 | 19 | news | Iran says four tankers on fire after striking mines in Hormuz | tuesday |
| 90 | 13 | news | France protests draw nearly 1,000 arrests as clashes follow peaceful marches | thursday |
| 90 | 9 | ai-tech | I got Gemini and ChatGPT to argue about which is the best phone, and the results are in | friday |
| 89 | 15 | news | Lula wins fourth Brazilian term as Bolsonaro seeks annulment | monday |
| 84 | 19 | news | Aleksandar Vucic Concedes Defeat in Serbian Election | monday |
| 84 | 18 | news | María Corina Machado Returns to Venezuela | monday |
| 83 | 19 | news | ‘Pull Out the Sick Trees’: Xi’s Constant Purges Pave Way for Next Term | thursday |

---

## Recommendations

- 🌾 17 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=25) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1296 articles analysed · 2026-10-31 18:00 UTC_
