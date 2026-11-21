# Cache Corpus Alignment Report

_Generated: 2026-11-21 20:17 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1348 |
| Articles missing theme-score data (skipped) | 183 |
| Direct-qualify (upstream score gates them in for their best theme) | 1288 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 38 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 22 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 14 (1% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 710 |
| analysis | 395 |
| breaking | 188 |
| feature | 147 |
| opinion | 41 |
| recap | 15 |
| wire | 15 |
| news | 13 |
| fluff | 6 |
| essay | 1 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 832 | 47.5 | 79.9 | +32.4 | 784 | 26 | 22 | 10 |
| ai-tech | 195 | 43.1 | 67.7 | +24.6 | 191 | 4 | 0 | 0 |
| science | 106 | 43.8 | 76.0 | +32.2 | 106 | 0 | 0 | 0 |
| wellness | 74 | 40.3 | 72.1 | +31.8 | 70 | 4 | 0 | 2 |
| climate | 69 | 42.8 | 74.8 | +32.0 | 69 | 0 | 0 | 1 |
| local | 31 | 71.1 | 97.6 | +26.6 | 31 | 0 | 0 | 0 |
| homelab | 19 | 46.6 | 75.6 | +29.0 | 17 | 2 | 0 | 1 |
| design | 17 | 39.2 | 63.2 | +23.9 | 16 | 1 | 0 | 0 |
| homestead | 3 | 55.0 | 98.7 | +43.7 | 3 | 0 | 0 | 0 |
| outdoors | 2 | 26.0 | 74.5 | +48.5 | 1 | 1 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1348 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 47.6 | 100 | 1106 | 927 |
| Tuesday | Working Lands & Industry | 44.4 | 100 | 996 | 746 |
| Wednesday | Repair Culture & Practical Tech | 47.6 | 100 | 1156 | 967 |
| Thursday | Indigenous Lands & Innovation | 44.2 | 100 | 1050 | 773 |
| Friday | Wild Spaces & Outdoor Life | 48.6 | 100 | 1154 | 967 |
| Saturday | Cariboo Local Affairs | 48.8 | 100 | 1245 | 1111 |
| Sunday | Science, Wonder & the Natural World | 49.1 | 100 | 1145 | 954 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 927 | 1059 | 35 | 12 |
| Tuesday | Working Lands & Industry | 30 | 15 | 746 | 918 | 57 | 21 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 967 | 1109 | 35 | 12 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 773 | 1006 | 23 | 21 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 967 | 1112 | 32 | 10 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 1111 | 1233 | 0 | 12 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 954 | 1100 | 35 | 10 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 62 | 26 | wellness | Why Sex Matters for Alzheimer’s Biomarkers and Trials |
| 59 | 23 | homelab | How to charge an Anker SOLIX with surplus SolarEdge power |
| 55 | 28 | news | The Tiny Chips That Could Make AI Glasses Something You Actually Want to Wear |
| 55 | 28 | news | Megaspeed Says Alice Huang Left Company in August 2025 |
| 55 | 27 | news | How often do you actually regenerate your desiccant? |
| 55 | 24 | news | Your Brain on Grief, Your Heart on Healing |
| 55 | 21 | news | Microsoft wants to put a dollar value on AI’s work – but can you trust the math? |
| 52 | 29 | wellness | The Speech Patterns of Psychoses |
| 51 | 28 | news | Why adaptability beats capacity for data centers |
| 51 | 25 | climate | Darlington’s First SMR Is Late and Over Budget. Ontario Needs to Rethink the Next Three. |
| 50 | 27 | news | Almost 90% of Europe’s Battery Production at Risk from Franco-German Car Deal |
| 50 | 24 | news | The Metals Company Has a Seabed Mining Production Gap That Its Pilot Has Not Closed |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 98 | 25 | homelab | Build Your Own TARS Robot From Interstellar | wednesday |
| 97 | 27 | wellness | STAT+: FDA rejects Capricor Therapeutics’ Duchenne therapy, a decision that was a long time coming | sunday |
| 96 | 24 | news | As Trump and Xi Mingle, Their Governments Are Arming Up | friday |
| 96 | 24 | news | New York mayor disbands NYPD protest unit, splits counterterrorism duties | friday |
| 95 | 26 | news | In Milwaukee, a Flimsy Story Triggers a Lawsuit—and a Serious Accusation | monday |
| 94 | 25 | news | Ukraine urges IAEA to reject sanctioned Russian nuclear official's appointment | wednesday |
| 94 | 24 | news | The Iran War Has Slipped Into a Dangerous Limbo | sunday |
| 94 | 22 | outdoors | 3 Dead in Plane Crash on Remote North Rim of Grand Canyon National Park | wednesday |
| 93 | 24 | news | Iraq orders army into Iran-backed militia stronghold over oil-smuggling probe | thursday |
| 93 | 20 | news | Widow of Haiti’s slain leader Moise to contest presidential vote | tuesday |
| 92 | 24 | news | Somalia orders UAE ambassador out within 72 hours over sovereignty dispute | sunday |
| 92 | 24 | news | Shenzhen APEC summit puts U.S.-China chip and trade disputes in focus | sunday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=25) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 100 | 18 | news | Estonia to close border crossings with Russia after alleged arson attack | friday |
| 96 | 16 | news | Denmark expels Russian diplomat over alleged plot to kill Ukrainian rapper | friday |
| 93 | 18 | news | Carney, Xi agree to ease trade restrictions | thursday |
| 93 | 17 | news | Miami jury convicts Haitian-American pastor in Moïse assassination plot | tuesday |
| 93 | 16 | news | Panama arrests suspected driver of taxi used in attack on journalist | tuesday |
| 93 | 14 | news | Italy drops school staffing cuts, weighs wider 2027 budget changes | friday |
| 93 | 11 | news | Peoria lifts evacuation after bomb found at Illinois ethanol plant | tuesday |
| 92 | 15 | news | Iran Attacks Bahrain for the Second Time in Days | sunday |
| 92 | 11 | news | Iran war live: Houthis advance in Yemen as Vance rejects ‘forever war’ | monday |
| 90 | 16 | news | UK seeks closer ties with EU after Brexit fail | wednesday |
| 90 | 16 | news | ASEAN keeps Myanmar leaders barred, ties return to peace-plan progress | friday |
| 90 | 12 | news | Iran claims drone strike on US radar in Bahrain; CENTCOM denies damage | friday |

---

## Recommendations

- 🌾 22 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=25) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1348 articles analysed · 2026-11-21 20:17 UTC_
