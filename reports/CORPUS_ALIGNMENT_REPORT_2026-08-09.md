# Cache Corpus Alignment Report

_Generated: 2026-08-09 14:01 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1421 |
| Articles missing theme-score data (skipped) | 82 |
| Direct-qualify (upstream score gates them in for their best theme) | 1400 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 10 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 2 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 112 (8% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 922 |
| analysis | 214 |
| breaking | 203 |
| feature | 129 |
| fluff | 18 |
| opinion | 7 |
| investigation | 4 |
| news | 3 |
| wire | 2 |
| recap | 1 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 998 | 53.5 | 51.3 | -2.2 | 985 | 7 | 2 | 72 |
| wellness | 109 | 54.6 | 45.0 | -9.6 | 106 | 1 | 0 | 18 |
| ai-tech | 100 | 46.9 | 41.2 | -5.7 | 98 | 0 | 0 | 11 |
| science | 71 | 51.7 | 48.7 | -3.0 | 70 | 1 | 0 | 3 |
| local | 52 | 84.4 | 65.2 | -19.2 | 52 | 0 | 0 | 0 |
| climate | 42 | 54.1 | 49.1 | -5.1 | 42 | 0 | 0 | 1 |
| homelab | 27 | 49.2 | 42.3 | -6.9 | 27 | 0 | 0 | 2 |
| design | 20 | 48.2 | 40.6 | -7.6 | 19 | 0 | 0 | 5 |
| scifi | 2 | 35.0 | 30.0 | -5.0 | 1 | 1 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1421 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 8.2 | 66 | 231 | 30 |
| Tuesday | Working Lands & Industry | 3.2 | 30 | 23 | 1 |
| Wednesday | Repair Culture & Practical Tech | 9.0 | 42 | 418 | 19 |
| Thursday | Indigenous Lands & Innovation | 4.7 | 30 | 88 | 5 |
| Friday | Wild Spaces & Outdoor Life | 37.6 | 75 | 1371 | 1080 |
| Saturday | Cariboo Local Affairs | 39.4 | 89 | 1414 | 1362 |
| Sunday | Science, Wonder & the Natural World | 49.1 | 89 | 1366 | 1252 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 30 | 227 | 3 | 1 |
| Tuesday | Working Lands & Industry | 30 | 15 | 1 | 23 | 0 | 0 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 19 | 411 | 5 | 2 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 5 | 87 | 1 | 0 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 1080 | 1358 | 11 | 2 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 1362 | 1413 | 0 | 1 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 1252 | 1353 | 11 | 2 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 73 | 29 | wellness | Polystyrene Foam can be Gasoline With Some Help |
| 72 | 29 | wellness | The Council on Chiropractic Education reaffirms the subluxation, backs off primary care (sort of) |
| 67 | 19 | news | Global memory shortage forces top PC makers like HP and Asus to turn to CXMT chips — but what will Samsung and Micron think? |
| 65 | 29 | news | Vitamin C may fight cancer — but not the way scientists once thought |
| 65 | 27 | wellness | A protein older than blood circulation could transform cancer immunotherapy |
| 64 | 26 | news | ‘Danger no longer only comes from the hitmen, but from the state’: the Honduran farmers labelled terrorists for protecting their land |
| 63 | 27 | news | Security's AI advantage will go to the organizations already built for accountability |
| 63 | 25 | news | ‘Playing around with your favourite artist’s song is an ultimate expression of fandom’: Spotify is taking another step into participatory music tools with its upcoming AI remix feature — but it signals red flags for industry professionals |
| 63 | 5 | news | The Only Way to Hike the Secluded, Multiday Colorado Trail Is by Riding a Train From This Outdoorsy City |
| 62 | 21 | news | (Almost) everybody in Canada wants a pipeline. Nobody wants to pay for it |
| 62 | 20 | news | I ran a dumpstate analysis on my Samsung phone and found 3 useful system diagnostics |
| 62 | 20 | news | Dress made of living mycelium can renew and repair itself |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 79 | 27 | news | AI-assisted staging draws boos at the Richard Wagner festival in Germany | sunday |
| 74 | 25 | news | Trump pauses ‘massive attack’ on Iran, says new talks to begin | sunday |
| 68 | 18 | wellness | Simple Exercises You Can Do at Your Desk | sunday |
| 57 | 20 | news | I put the Lenovo IdeaPad Slim 3i Gen 11 to work — it’s a great $799 laptop (if on sale) | sunday |
| 50 | 25 | news | I use the 'bird cage' prompt to keep my ChatGPT projects separate — now I can't work without it | sunday |
| 49 | 20 | news | I trekked the Cascade Mountains with the Apple Watch Ultra 3 vs Garmin Instinct 3 vs Samsung Galaxy Watch Ultra 2 — this is the one I'd take on my next hike | sunday |
| 47 | 23 | science | Latest Pentagon UFO files release includes video of mysterious ‘cold orbs’ | sunday |
| 39 | 24 | scifi | Fun little review by Marcin Wichary of a 1984 flying... | sunday |
| 34 | 26 | news | 5 ways to add storage to a laptop without upgrading its SSD | sunday |
| 25 | 24 | news | Galaxy Z Fold 8 vs Fold 8 Ultra camera test: Is the telephoto zoom worth the extra $200? | sunday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=20) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 76 | 18 | news | Gaza students overcome Israel’s genocide to mark Tawjihi results | sunday |
| 72 | 14 | news | Myanmar's detained former leader Aung San Suu Kyi has rare meeting with International Red Cross | sunday |

---

## Recommendations

- 🌾 2 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=20) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1421 articles analysed · 2026-08-09 14:01 UTC_
