# Cache Corpus Alignment Report

_Generated: 2026-10-04 17:30 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1340 |
| Articles missing theme-score data (skipped) | 136 |
| Direct-qualify (upstream score gates them in for their best theme) | 1257 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 10 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 20 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 162 (12% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 1010 |
| analysis | 166 |
| feature | 145 |
| breaking | 98 |
| news | 20 |
| fluff | 15 |
| opinion | 10 |
| wire | 4 |
| recap | 4 |
| investigation | 4 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 964 | 55.9 | 68.9 | +13.0 | 911 | 9 | 20 | 99 |
| ai-tech | 104 | 51.9 | 49.4 | -2.5 | 95 | 0 | 0 | 23 |
| wellness | 86 | 56.1 | 49.3 | -6.8 | 76 | 0 | 0 | 23 |
| science | 49 | 52.0 | 65.8 | +13.8 | 49 | 0 | 0 | 3 |
| local | 45 | 81.1 | 86.6 | +5.6 | 44 | 0 | 0 | 2 |
| homelab | 35 | 56.0 | 78.0 | +22.0 | 31 | 0 | 0 | 3 |
| climate | 31 | 53.6 | 67.8 | +14.2 | 28 | 1 | 0 | 3 |
| design | 20 | 48.6 | 41.0 | -7.6 | 17 | 0 | 0 | 6 |
| homestead | 2 | 72.5 | 99.0 | +26.5 | 2 | 0 | 0 | 0 |
| outdoors | 2 | 50.5 | 83.5 | +33.0 | 2 | 0 | 0 | 0 |
| scifi | 2 | 45.5 | 60.5 | +15.0 | 2 | 0 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1340 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 47.7 | 100 | 1097 | 964 |
| Tuesday | Working Lands & Industry | 45.4 | 100 | 996 | 845 |
| Wednesday | Repair Culture & Practical Tech | 43.9 | 100 | 1108 | 815 |
| Thursday | Indigenous Lands & Innovation | 46.4 | 85 | 1115 | 978 |
| Friday | Wild Spaces & Outdoor Life | 47.9 | 100 | 1169 | 959 |
| Saturday | Cariboo Local Affairs | 48.0 | 100 | 1238 | 1096 |
| Sunday | Science, Wonder & the Natural World | 48.0 | 100 | 1145 | 951 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 964 | 1067 | 11 | 19 |
| Tuesday | Working Lands & Industry | 30 | 15 | 845 | 959 | 16 | 21 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 815 | 1075 | 12 | 21 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 978 | 1085 | 9 | 21 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 959 | 1137 | 12 | 20 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 1096 | 1219 | 0 | 19 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 951 | 1113 | 12 | 20 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 93 | 5 | local | ‘An investment B.C. has to make’: Conservatives aim to increase wildfire protection |
| 81 | 23 | local | Williams Lake Mustangs open BCHC season with back-to-back wins |
| 73 | 29 | news | Trump’s Mass Detention Machine in Pennsylvania |
| 73 | 21 | news | Space Lasers Are About to Get Their First Real Test Generating Energy |
| 70 | 24 | news | BC Ferries Heads to $1.3-Billion Deal with US-Owned Fuel Supplier |
| 70 | 19 | news | Need for speed: Ukraine actively seeking Formula 1 expertise to design future Magura naval unmanned vehicles like ultra-lightweight racing machines |
| 70 | 17 | ai-tech | 'It is possible that threat actors are finding it more accessible or efficient to use LLMs and AI tools': Google warns that AI explosion will lead to more dangerous and advanced security threats |
| 70 | 13 | wellness | Glucosamine, a popular joint supplement, linked to faster Alzheimer’s progression |
| 70 | 8 | wellness | Nine Patients Received a Personalized Kidney Cancer Vaccine. None Had a Recurrence. |
| 68 | 17 | news | A lack of professional AI guidelines leads to feelings of “AI shame,” a new study finds |
| 68 | 13 | climate | The Data Center Backlash Should Also Be a Climate Reckoning. It Isn’t Yet |
| 67 | 26 | news | How to Beat Surveillance Pricing Before It Bleeds You Dry |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 97 | 23 | news | Taiwan's chip talisman snack faces production halt after 94% strike vote | friday |
| 95 | 22 | news | 7 iOS 27 features that make old iPhones exciting again (no Apple Intelligence needed) | friday |
| 85 | 27 | news | A Near-Disaster on Flydubai | monday |
| 85 | 26 | news | Trump’s new America.gov uses Gemini and Grok to navigate government services — these 5 prompts show what it can do | monday |
| 70 | 21 | news | My Galaxy's battery said it was healthy until AccuBattery told me the truth | wednesday |
| 58 | 22 | news | Google Health's home screen widget is bare-bones, so I replaced it with these better widgets | monday |
| 55 | 24 | news | I created a digital Monster Manual in Google Canvas to instantly recall D&D lore | monday |
| 43 | 21 | news | Inside Malaysia's gambit to make its pungent durian the most wanted | monday |
| 39 | 23 | climate | Trump rolls back a major Biden-era car rule. Here’s how it could affect your next vehicle | wednesday |
| 26 | 24 | news | Archaeologists Found Something in the Way of Canal Construction: 546 Dead Bodies | tuesday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=25) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 100 | 18 | news | Israeli settlers attack Palestinian farmers during olive harvest | monday |
| 100 | 17 | news | Pot banging protests across Spain over housing crisis | friday |
| 100 | 15 | news | Ethiopian army reportedly recaptures strategic town as fighting spreads | friday |
| 100 | 11 | news | Deadly strike hits market in Yemen’s Taiz | sunday |
| 100 | 10 | news | Schools ablaze as student protests spread across France | sunday |
| 99 | 17 | news | G7 nations bow to US pressure and avoid crippling diesel ban | sunday |
| 99 | 16 | news | Houthis claim strike on Saudi energy facility as Yemen fighting intensifies | friday |
| 99 | 14 | news | UK Foreign Secretary confronted by activists over Palestine Action ban | friday |
| 98 | 10 | news | Israeli strikes continue in southern Lebanon despite ceasefire | friday |
| 98 | 9 | news | US and Australia suspend diplomatic operations in Brazil before election | friday |
| 98 | 7 | news | Italian court convicts three Egyptian agents for kidnap of Giulio Regeni | friday |
| 97 | 12 | news | Co-pilot who nearly crashed FlyDubai flight was banned from flying by Oman over extremism concerns | friday |

---

## Recommendations

- 🌾 20 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=25) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1340 articles analysed · 2026-10-04 17:30 UTC_
