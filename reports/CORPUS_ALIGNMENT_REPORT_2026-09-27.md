# Cache Corpus Alignment Report

_Generated: 2026-09-27 17:46 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1469 |
| Articles missing theme-score data (skipped) | 141 |
| Direct-qualify (upstream score gates them in for their best theme) | 1358 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 23 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 28 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 182 (12% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 1123 |
| analysis | 159 |
| feature | 131 |
| breaking | 122 |
| news | 44 |
| opinion | 15 |
| fluff | 13 |
| recap | 2 |
| wire | 1 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 1075 | 55.5 | 68.1 | +12.6 | 994 | 19 | 28 | 119 |
| ai-tech | 96 | 48.6 | 51.7 | +3.1 | 89 | 0 | 0 | 14 |
| wellness | 94 | 56.8 | 52.3 | -4.5 | 83 | 2 | 0 | 21 |
| science | 68 | 53.2 | 61.7 | +8.5 | 63 | 0 | 0 | 9 |
| local | 51 | 81.9 | 87.2 | +5.4 | 51 | 0 | 0 | 1 |
| climate | 28 | 54.1 | 67.7 | +13.6 | 28 | 0 | 0 | 3 |
| design | 26 | 47.5 | 37.5 | -9.9 | 20 | 1 | 0 | 11 |
| homelab | 26 | 55.7 | 77.4 | +21.8 | 26 | 0 | 0 | 4 |
| outdoors | 5 | 35.2 | 70.2 | +35.0 | 4 | 1 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1469 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 48.3 | 100 | 1222 | 1023 |
| Tuesday | Working Lands & Industry | 44.9 | 100 | 1088 | 851 |
| Wednesday | Repair Culture & Practical Tech | 42.7 | 100 | 1182 | 793 |
| Thursday | Indigenous Lands & Innovation | 46.8 | 100 | 1214 | 1073 |
| Friday | Wild Spaces & Outdoor Life | 48.8 | 100 | 1299 | 1024 |
| Saturday | Cariboo Local Affairs | 48.8 | 100 | 1355 | 1205 |
| Sunday | Science, Wonder & the Natural World | 49.2 | 100 | 1255 | 1056 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 1023 | 1176 | 21 | 25 |
| Tuesday | Working Lands & Industry | 30 | 15 | 851 | 1041 | 23 | 24 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 793 | 1134 | 22 | 26 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 1073 | 1176 | 14 | 24 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 1024 | 1248 | 25 | 26 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 1205 | 1331 | 0 | 24 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 1056 | 1204 | 23 | 28 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 87 | 16 | local | DOWN TO EARTH: Riding a bike can change your life |
| 76 | 26 | news | What Do We Do About the Cameras Everywhere? |
| 73 | 20 | news | This NATO-backed drone AI picked its own target and struck it, but relied on a human-drawn map to do so |
| 73 | 0 | news | ‘Rethinking the laptop is a big undertaking’ — why Googlebooks are so much more than overpriced Chromebooks, and why Apple should be worried |
| 72 | 28 | wellness | Alzheimer's Is No Longer an Untreatable Disease, Major Report Concludes. Here's Why. |
| 72 | 27 | wellness | How Targeting the Brain’s ‘Zombie’ Cells May Treat Alzheimer’s |
| 72 | 8 | ai-tech | How Shopify built a continual learning loop with PyTorch and vLLM |
| 70 | 27 | wellness | What Scientists Want You to Know About How to Warm Up |
| 70 | 26 | news | The UK Government Faces a Reckoning Over Palantir |
| 70 | 20 | wellness | As president of Botswana, I know how we can make malaria a memory in Africa | Duma Gideon Boko |
| 68 | 27 | news | LNG in the Aquarium of the World: A Direct, Existential, and Unacceptable Risk |
| 68 | 26 | news | I fed Cloudflare, Quad9, NextDNS, and AdGuard the same malicious domains to see who actually stops them |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 100 | 24 | news | Inside the Tiny Unfixable Eye: iPhone 18 Pro and Pro Max Teardown | wednesday |
| 99 | 22 | news | Update: Woodfibre LNG expresses disappointment after Squamish council turns down $142 million offer | thursday |
| 99 | 22 | news | As major powers act unilaterally, experts say UN faces crisis in New York | sunday |
| 98 | 23 | news | Russia bombs Ukrainian data centers in latest escalation | monday |
| 95 | 27 | wellness | Massachusetts Bar Controversy Shines Light On What It Means To Be Immunocompromised | sunday |
| 94 | 21 | news | Photos: Gaza’s children return to class in tents and ruins | sunday |
| 93 | 21 | news | Should you buy a Mac mini now? M6 vs M5 Pro buying advice | wednesday |
| 92 | 20 | news | DR Congo’s Ebola outbreak spreads to two new health zones, WHO says | sunday |
| 90 | 23 | news | Former ‘death squad’ leader appears in military trial in The Gambia | sunday |
| 87 | 20 | news | War is erasing history | thursday |
| 81 | 23 | news | What Israel Knew Before October 7 | sunday |
| 65 | 29 | news | Tim Tebow “Pausing” Christian Seminar Promotion After Our Investigation | tuesday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=25) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 100 | 12 | news | Protesters march on Islamabad over soaring fuel prices | thursday |
| 100 | 8 | news | Powerful explosions at Syrian army site near Aleppo injure at least four | sunday |
| 100 | 7 | news | Bangkok declared disaster zone after heavy rains submerge roads | friday |
| 99 | 11 | news | Ethiopia warns of ‘destruction’ as Tigray rebels launch offensive | friday |
| 99 | 8 | news | Imran Khan’s family says three sisters detained ahead of Islamabad march | saturday |
| 99 | 7 | news | Powerful storm batters US Northeast disrupting power and travel | saturday |
| 98 | 16 | news | After Pursuit, ICE Agent Shoots Venezuelan Immigrant in Austin | friday |
| 98 | 15 | news | What the bond market is telling us as yields spike to 2-decade highs | saturday |
| 98 | 13 | news | Croatian court approves extradition in Nord Stream bombing case | monday |
| 98 | 10 | news | US man convicted in 2023 shooting of three Palestinian students in Vermont | thursday |
| 97 | 16 | news | Journalists attacked while covering violent farmers’ protest in Romania | sunday |
| 97 | 15 | news | Pezeshkian says Iran ‘no longer trusts talks with Washington’ | saturday |

---

## Recommendations

- 🌾 28 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=25) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1469 articles analysed · 2026-09-27 17:46 UTC_
