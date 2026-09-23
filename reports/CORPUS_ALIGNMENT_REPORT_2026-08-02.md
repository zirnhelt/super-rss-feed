# Cache Corpus Alignment Report

_Generated: 2026-08-02 14:45 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1516 |
| Articles missing theme-score data (skipped) | 65 |
| Direct-qualify (upstream score gates them in for their best theme) | 1395 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 50 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 60 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 128 (8% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 1067 |
| breaking | 223 |
| analysis | 153 |
| feature | 79 |
| news | 25 |
| fluff | 17 |
| opinion | 10 |
| wire | 6 |
| recap | 1 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 1237 | 50.4 | 49.5 | -0.9 | 1121 | 45 | 60 | 114 |
| ai-tech | 79 | 42.9 | 42.9 | -0.0 | 77 | 2 | 0 | 3 |
| wellness | 54 | 51.9 | 47.2 | -4.7 | 53 | 1 | 0 | 8 |
| science | 51 | 49.7 | 53.4 | +3.7 | 50 | 1 | 0 | 1 |
| local | 40 | 80.2 | 66.8 | -13.5 | 40 | 0 | 0 | 0 |
| climate | 34 | 53.1 | 61.6 | +8.5 | 33 | 1 | 0 | 0 |
| homelab | 20 | 53.1 | 41.4 | -11.8 | 20 | 0 | 0 | 2 |
| scifi | 1 | 50.0 | 38.0 | -12.0 | 1 | 0 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1516 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 8.2 | 71 | 226 | 34 |
| Tuesday | Working Lands & Industry | 3.2 | 33 | 26 | 1 |
| Wednesday | Repair Culture & Practical Tech | 9.2 | 57 | 462 | 26 |
| Thursday | Indigenous Lands & Innovation | 4.7 | 32 | 85 | 4 |
| Friday | Wild Spaces & Outdoor Life | 37.6 | 84 | 1458 | 1165 |
| Saturday | Cariboo Local Affairs | 39.3 | 83 | 1506 | 1423 |
| Sunday | Science, Wonder & the Natural World | 49.0 | 90 | 1447 | 1313 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 34 | 162 | 26 | 38 |
| Tuesday | Working Lands & Industry | 30 | 15 | 1 | 18 | 3 | 5 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 26 | 376 | 35 | 51 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 4 | 72 | 2 | 11 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 1165 | 1347 | 51 | 60 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 1423 | 1455 | 0 | 51 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 1313 | 1336 | 51 | 60 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 83 | 20 | news | The Secrets Behind Samsung’s Privacy Screen |
| 80 | 14 | news | '8K Blu-ray would be a technical feat in search of a problem to solve’: I talked to the Blu-ray Disc Association, player manufacturers and TV makers about what comes after 4K Blu-ray, and the future of physical media |
| 76 | 23 | news | The ban on robot vacuums won’t make them safer, only worse |
| 73 | 19 | news | Google Earth&#8217;s AI deepfake tool only lasted one day |
| 72 | 22 | news | Anthropic says its models went rogue and hacked 3 companies during testing |
| 72 | 20 | news | Re-examining the DDR4 gaming gap with Intel’s LGA 1700 CPUs in mid-2026 — performance drops of 14% on average, and up to 25% in some games |
| 72 | 19 | news | Hugging Face Has a Deepfake Nudes Problem |
| 72 | 18 | news | FBTriton Infra: Upstream Ingestion, Hierarchical Validation, Ideals vs Realities |
| 72 | 11 | wellness | Prompt Injection Is SQL Injection. We're Repeating History. |
| 70 | 29 | news | The major labels propose rules to keep AI slop off the charts |
| 70 | 27 | wellness | The dead doctor and a dicey diet: how a ban made a hero of Egypt’s rogue medic |
| 70 | 17 | news | First your age, next your identity: Inside the 'hack' that broke the EU age verification app's privacy promises |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 86 | 27 | news | Sketch released of suspect in attempted child abduction in Abbotsford | sunday |
| 83 | 26 | news | Coquitlam Search and Rescue volunteer found dead on Squamish trail | sunday |
| 83 | 25 | news | Judge denies states’ motion to postpone Medicaid work requirement | sunday |
| 82 | 22 | news | 2 Jewish-owned Toronto bakeries vandalized, shots fired at 1 | sunday |
| 80 | 26 | news | Another scuba diver dies off Whytecliff Park in West Vancouver | sunday |
| 79 | 24 | climate | Firefighters battle wildfires in Spain’s eastern Castellon province | sunday |
| 79 | 22 | news | Search for Parker continues in Calgary as Amber Alert expires | sunday |
| 78 | 20 | news | Iran holds funeral for Revolutionary Guard members reportedly killed in US | sunday |
| 76 | 24 | news | UN slams Israel’s expansion of illegal settlements in occupied West Bank | sunday |
| 76 | 21 | news | Haitians living in fear as Temporary Protected Status ends in the US | sunday |
| 75 | 26 | news | Trump Will End Subsidies for Medicare Drug Premiums | sunday |
| 75 | 24 | news | After fleeing Sudan’s war, refugees battle thirst in Chad’s camps | sunday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=20) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 87 | 14 | news | Protests in Lima as Keiko Fujimori sworn in as Peru president | sunday |
| 85 | 14 | news | Israeli settlers burn two mosques in occupied West Bank | sunday |
| 85 | 10 | news | Israeli soldiers mutiny at notorious Sde Teiman base | sunday |
| 84 | 15 | news | Families sleep in cars after homes destroyed in Japan earthquake | sunday |
| 83 | 16 | news | Protests erupt in Libya’s Tripoli as anger grows over power cuts | sunday |
| 83 | 9 | news | Spain deploys military to Ceuta after deadly migrant surge | sunday |
| 82 | 18 | news | Peru’s ex-president Humala released after conviction overturned | sunday |
| 82 | 17 | news | Trump says Iran talks taking place during pause in US military strikes | sunday |
| 82 | 14 | news | Russia and Ukraine trade attacks, killing 10, including child in Chernihiv | sunday |
| 80 | 17 | news | Malaysia detains more than 100 Rohingya seeking help from the UN | sunday |
| 80 | 14 | news | Mother of infant found dead in New Westminster gets over four years in prison | sunday |
| 80 | 12 | news | Myanmar court sentences activists to 37 years over election protest | sunday |

---

## Recommendations

- 🌾 60 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=20) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1516 articles analysed · 2026-08-02 14:45 UTC_
