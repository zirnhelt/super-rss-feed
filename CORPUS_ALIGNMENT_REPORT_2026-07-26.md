# Cache Corpus Alignment Report

_Generated: 2026-07-26 20:24 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 310 |
| Articles missing theme-score data (skipped) | 1083 |
| Direct-qualify (upstream score gates them in for their best theme) | 251 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 15 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 43 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 19 (6% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 708 |
| breaking | 260 |
| analysis | 154 |
| feature | 106 |
| fluff | 66 |
| news | 61 |
| recap | 15 |
| opinion | 12 |
| wire | 11 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 221 | 41.8 | 47.5 | +5.7 | 169 | 13 | 38 | 15 |
| ai-tech | 34 | 41.9 | 42.6 | +0.8 | 32 | 0 | 2 | 0 |
| science | 18 | 40.7 | 49.6 | +8.8 | 15 | 1 | 2 | 1 |
| wellness | 14 | 44.6 | 50.5 | +5.9 | 13 | 1 | 0 | 1 |
| local | 10 | 79.5 | 62.8 | -16.7 | 10 | 0 | 0 | 0 |
| climate | 7 | 40.7 | 62.3 | +21.6 | 6 | 0 | 1 | 0 |
| homelab | 6 | 53.8 | 36.8 | -17.0 | 6 | 0 | 0 | 2 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 310 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 7.2 | 64 | 39 | 3 |
| Tuesday | Working Lands & Industry | 3.0 | 33 | 4 | 1 |
| Wednesday | Repair Culture & Practical Tech | 8.4 | 29 | 96 | 4 |
| Thursday | Indigenous Lands & Innovation | 4.3 | 19 | 12 | 0 |
| Friday | Wild Spaces & Outdoor Life | 36.4 | 66 | 295 | 234 |
| Saturday | Cariboo Local Affairs | 37.7 | 71 | 310 | 288 |
| Sunday | Science, Wonder & the Natural World | 46.4 | 87 | 292 | 264 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 3 | 27 | 4 | 8 |
| Tuesday | Working Lands & Industry | 30 | 15 | 1 | 4 | 0 | 0 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 4 | 73 | 9 | 14 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 0 | 11 | 0 | 1 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 234 | 239 | 15 | 41 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 288 | 269 | 1 | 40 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 264 | 234 | 15 | 43 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 73 | 27 | news | A USB plug for humans? Electricity outlet test delivers microwatts of power, but transfers data at 16Mbps |
| 64 | 12 | news | Farm Hell: Family Seeks Justice After 10-Year Battle Over Devastating Irrigation Penalties - AgWeb |
| 63 | 28 | news | Trump Is Pushing Nuclear Energy, Including Saudi Deal. His Family and Supporters Could Benefit. |
| 63 | 20 | news | Delta Pen Plotter Draws In Multiple Colors |
| 62 | 24 | homelab | Home Assistant Predictive Energy Control with Local ML 2026 |
| 58 | 28 | news | The Latest - openmedia.org |
| 58 | 25 | news | The Best Subscription-Free Home Security Cameras I’ve Tried |
| 58 | 20 | news | ‘The Odyssey’ Was Made for Imax 70mm. Good Luck Watching It That Way |
| 58 | 19 | news | Samsung Galaxy Z Fold 8 Hands-On: Shorter and Wider Is Actually Better |
| 58 | 16 | news | Your AI calorie-tracking app may be off by 345 calories |
| 55 | 29 | news | TEAMGROUP NV10000 review: PCIe Gen5 x4 3D NAND with read speeds over 10000MB/s |
| 55 | 27 | science | CRISPR makes prostate cancer vulnerable to immunotherapy |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 82 | 22 | news | 2 Jewish-owned Toronto bakeries vandalized, shots fired at 1 | sunday |
| 70 | 27 | news | Trio of foragers found safe after spending night in bush in northern Saskatchewan | sunday |
| 67 | 22 | news | Romania summons Russian envoy as it shoots down third intruding drone | sunday |
| 66 | 26 | news | Former ‘60 Minutes’ Reporter Cecilia Vega Details Claims of Meddling | sunday |
| 65 | 22 | news | Online nihilist networks targeted in international crackdown | sunday |
| 62 | 26 | science | Walking shark discovered in Papua New Guinea | sunday |
| 60 | 26 | news | Israel and the cost paradox of the Iran war | sunday |
| 59 | 22 | news | Senegal’s Faye launches a new party, formalising his split with Sonko | sunday |
| 57 | 25 | news | High-value CFMoto adventure tourer smooths ride with smart suspension | sunday |
| 55 | 21 | news | Money, mansions, and the IPO ripple effect | sunday |
| 55 | 20 | news | Trump Seems Trapped by Iran War, Even as He Wields the World’s Biggest Hammer | sunday |
| 54 | 25 | news | We asked Tom's Guide readers, 'Which fitness tracking metrics do you trust the least?' Here's the surprising answer | sunday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=20) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 85 | 14 | news | Israeli settlers burn two mosques in occupied West Bank | sunday |
| 77 | 14 | news | Typhoon Noul batters Southeast China | sunday |
| 75 | 17 | news | Berlin Pride Event Attacker Killed in Police Shootout, Officials Say | sunday |
| 72 | 19 | news | Manitoba MLA among victims of multiple home break-ins, man arrested | sunday |
| 72 | 14 | news | Israel launches military incursion into Syria amid UN condemnation | sunday |
| 71 | 17 | news | U.S.-Iran War Pauses for 2nd Straight Day With Both Sides Holding Off on Strikes | sunday |
| 70 | 12 | news | Al-Sharaa praises Trump’s decision to remove Syria from terrorism list | sunday |
| 66 | 19 | news | Tunisia grapples with five years of crisis since Saied’s power grab | sunday |
| 62 | 13 | news | Pro-Ukraine group claims it helped hack Russian drone air defense system, shooting down Su-57 in friendly fire incident — Moscow confirms fifth-generation fighter jet crashed in 'technical malfunction' | sunday |
| 60 | 13 | news | BAE Systems unveils Brontanax autonomous loyal wingman | sunday |
| 59 | 18 | news | Lockheed Martin unveils counter-drone system that can ‘neutralize up to 50 enemy drones in a single mission’ — sensor-agnostic system uses High Power Microwave to purge enemies from the sky | friday |
| 58 | 17 | science | Concerns over major irrigation project prompt advocates to hold water assembly | sunday |

---

## Recommendations

- 🌾 43 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=20) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 310 articles analysed · 2026-07-26 20:24 UTC_
