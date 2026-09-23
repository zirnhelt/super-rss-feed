# Cache Corpus Alignment Report

_Generated: 2026-09-13 17:03 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1377 |
| Articles missing theme-score data (skipped) | 106 |
| Direct-qualify (upstream score gates them in for their best theme) | 1278 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 22 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 22 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 124 (9% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 944 |
| analysis | 190 |
| feature | 167 |
| breaking | 119 |
| news | 21 |
| fluff | 20 |
| opinion | 10 |
| investigation | 8 |
| recap | 2 |
| wire | 2 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 958 | 56.1 | 68.4 | +12.3 | 888 | 18 | 19 | 87 |
| ai-tech | 93 | 45.4 | 53.7 | +8.3 | 82 | 2 | 0 | 5 |
| wellness | 87 | 56.3 | 61.3 | +5.0 | 83 | 1 | 0 | 14 |
| science | 64 | 47.1 | 60.0 | +12.8 | 60 | 0 | 1 | 4 |
| homelab | 47 | 51.4 | 79.1 | +27.7 | 47 | 0 | 0 | 4 |
| local | 46 | 78.8 | 90.9 | +12.1 | 46 | 0 | 0 | 0 |
| climate | 37 | 50.3 | 67.2 | +16.9 | 36 | 0 | 0 | 1 |
| design | 34 | 44.2 | 46.0 | +1.8 | 29 | 1 | 0 | 9 |
| homestead | 6 | 52.0 | 94.7 | +42.7 | 6 | 0 | 0 | 0 |
| scifi | 4 | 26.5 | 31.2 | +4.8 | 1 | 0 | 2 | 0 |
| outdoors | 1 | 38.0 | 4.0 | -34.0 | 0 | 0 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1377 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 48.3 | 100 | 1149 | 979 |
| Tuesday | Working Lands & Industry | 44.6 | 100 | 963 | 963 |
| Wednesday | Repair Culture & Practical Tech | 42.7 | 100 | 1125 | 736 |
| Thursday | Indigenous Lands & Innovation | 46.7 | 100 | 1090 | 955 |
| Friday | Wild Spaces & Outdoor Life | 49.0 | 100 | 1200 | 970 |
| Saturday | Cariboo Local Affairs | 48.9 | 100 | 1267 | 1136 |
| Sunday | Science, Wonder & the Natural World | 49.3 | 100 | 1159 | 997 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 979 | 1099 | 30 | 20 |
| Tuesday | Working Lands & Industry | 30 | 15 | 963 | 912 | 32 | 19 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 736 | 1075 | 28 | 22 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 955 | 1050 | 19 | 21 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 970 | 1148 | 31 | 21 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 1136 | 1248 | 1 | 18 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 997 | 1108 | 31 | 20 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 73 | 18 | wellness | ‘In parks you only see dogs, never children’: can Bogotá adapt to its ageing population? |
| 73 | 5 | ai-tech | ‘Killmonger Locs’ Are Everywhere in Video Games. This Artist Is Sick of It |
| 72 | 21 | wellness | I deployed these 2 monitoring tools in my homelab and haven't lost sleep about failures since (September 11 - 13) |
| 71 | 14 | wellness | Seaweed Is Their Way of Life. A Company’s Sweeping Plan Threatens It. |
| 70 | 27 | news | ‘Pretend That I Am Running’: 7 Takeaways From the G.O.P. Midterm Convention |
| 70 | 7 | news | Why Amy Klobuchar Wants to Run a State Beleaguered by Trump |
| 68 | 19 | news | Intel surpasses one million High-NA EUV wafers processed, outpaces the rest of the industry combined — company also trailblazing giant 6×12 photomasks to speed production and lower costs |
| 68 | 12 | news | ZF Wants You To Repair Rather Than Replace Your EV’s Drive Unit |
| 67 | 27 | news | Foldable Phones Are Unpopular. Why Is Apple Selling One? |
| 67 | 9 | news | Lyft Sees a Future for Its Drivers in a Driverless World: Servicing Waymos |
| 67 | 3 | news | Apple Doesn’t Want You to Worry About the New Apple Watch’s Listening Features |
| 67 | 1 | news | First Xiaomi, then the world: why Arm might give phone gaming a huge graphics boost |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 100 | 23 | news | Russian plot to sabotage undersea cables with 'secret weapon' foiled by NATO — clandestine op uncovers training exercise simulating deployment against infrastructure in Norway | friday |
| 100 | 22 | news | Satellite image shows critical Saudi pipeline damaged in drone attack | friday |
| 100 | 21 | news | Gaza hospitals ration power as fuel shortages deepen | sunday |
| 99 | 24 | news | CPJ condemns 15-year prison sentence handed down by Russian authorities to retired Ukrainian journalist Iryna Levchenko | monday |
| 97 | 20 | news | Saudis Shut Down Crucial Pipeline After Drone Attack From Iraq | thursday |
| 95 | 21 | news | Caribbean Revelers Celebrate at Parade, Even as Many Are Missing | friday |
| 94 | 25 | news | Former Old School RuneScape dev gets jail time for stealing $400,000 from players — virtual gold stolen and sold on the black market before Jagex caught the culprit using hidden firewall tweaks | sunday |
| 94 | 22 | news | Do this before you follow a successful person’s advice | monday |
| 93 | 24 | design | Orms plans to add rooftop swimming pool to London's BT Tower | friday |
| 87 | 23 | news | Personal stories of 9/11, 25 years later | thursday |
| 87 | 17 | wellness | My bed sheets were dirty one night after washing until I banned these 3 things from the bedroom | tuesday |
| 85 | 27 | news | ‘Gone in a blink’: Nepal floods sweep away Indian workers who built hotels | sunday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=25) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 100 | 11 | news | Search underway for Indonesian passenger ship carrying at least 240 people after it loses contact | thursday |
| 99 | 16 | news | 9/11 in Realtime | monday |
| 99 | 15 | news | Suspected smugglers on trial over deadliest migrant tragedy in France | sunday |
| 99 | 14 | news | Deadly DRC school fire prompts calls for safety reforms | sunday |
| 99 | 11 | news | Israel bombs southern Lebanon as talks postponed | monday |
| 98 | 17 | news | Russia’s new shelling tactics deepen suffering in Ukraine | sunday |
| 97 | 15 | news | Hundreds of thousands lack adequate shelter at Sudan’s Tawila camp | sunday |
| 96 | 16 | news | Putin lands in India for BRICs summit, shadowed by Iran and Ukraine wars | saturday |
| 95 | 17 | news | Ebola spreads to seventh DRC province as gov’t insists cases are declining | friday |
| 95 | 16 | news | ‘Flamingo Revolution’ enters 100th day against Kushner-linked resort | friday |
| 94 | 18 | news | Veteran Haitian journalist Wesly Renaud Jean abducted, ransom requested | sunday |
| 93 | 7 | news | IAEA warns over Iran nuclear access as Western powers push UN referral | friday |

---

## Recommendations

- 🌾 22 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=25) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1377 articles analysed · 2026-09-13 17:03 UTC_
