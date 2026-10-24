# Cache Corpus Alignment Report

_Generated: 2026-10-24 16:51 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1318 |
| Articles missing theme-score data (skipped) | 139 |
| Direct-qualify (upstream score gates them in for their best theme) | 1204 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 33 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 30 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 81 (6% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 720 |
| analysis | 350 |
| feature | 152 |
| breaking | 150 |
| opinion | 36 |
| recap | 26 |
| wire | 11 |
| news | 8 |
| fluff | 4 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 844 | 47.3 | 68.9 | +21.6 | 759 | 27 | 30 | 59 |
| ai-tech | 161 | 46.7 | 53.1 | +6.4 | 145 | 2 | 0 | 10 |
| science | 109 | 44.6 | 70.1 | +25.5 | 108 | 0 | 0 | 2 |
| wellness | 64 | 39.3 | 58.5 | +19.1 | 59 | 3 | 0 | 4 |
| local | 47 | 76.2 | 93.0 | +16.9 | 47 | 0 | 0 | 1 |
| climate | 45 | 45.7 | 70.6 | +24.9 | 43 | 0 | 0 | 4 |
| homelab | 21 | 49.0 | 82.2 | +33.2 | 21 | 0 | 0 | 0 |
| design | 18 | 44.7 | 54.3 | +9.6 | 15 | 1 | 0 | 0 |
| outdoors | 5 | 49.8 | 53.4 | +3.6 | 4 | 0 | 0 | 0 |
| homestead | 4 | 55.2 | 68.2 | +13.0 | 3 | 0 | 0 | 1 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1318 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 48.4 | 100 | 1071 | 900 |
| Tuesday | Working Lands & Industry | 44.9 | 100 | 945 | 738 |
| Wednesday | Repair Culture & Practical Tech | 42.5 | 100 | 1042 | 694 |
| Thursday | Indigenous Lands & Innovation | 46.9 | 100 | 1086 | 927 |
| Friday | Wild Spaces & Outdoor Life | 49.0 | 100 | 1151 | 941 |
| Saturday | Cariboo Local Affairs | 49.0 | 100 | 1218 | 1081 |
| Sunday | Science, Wonder & the Natural World | 49.2 | 100 | 1110 | 948 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 900 | 1006 | 35 | 30 |
| Tuesday | Working Lands & Industry | 30 | 15 | 738 | 875 | 41 | 29 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 694 | 978 | 35 | 29 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 927 | 1033 | 23 | 30 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 941 | 1081 | 39 | 31 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 1081 | 1194 | 1 | 23 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 948 | 1041 | 38 | 31 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 86 | 18 | local | ‘Just the happiest kid’: Clinical trial brightens future for B.C. boy |
| 69 | 16 | wellness | The Malignant Narrative: Coroner’s Inquests and Clinical Harm |
| 63 | 18 | news | What to Know About Shamonda Virus Following the First Reported Human Infection |
| 60 | 28 | news | Here’s the tea |
| 60 | 26 | news | ANALYSIS: Solar & Storage Growth Drives Down Summer Wholesale Electricity Prices by 42% in Texas & 51% in California |
| 60 | 26 | ai-tech | ‘Thanks again for your help!’: Rogue AI agents on Tencent Cloud tried to crack Alibaba’s Amap, then chatted politely with the team tracking them |
| 60 | 24 | ai-tech | Microsoft: “Frontier AI models, regardless of their origin, cannot be trusted” |
| 60 | 21 | news | Why the Internet Needs a Memory |
| 60 | 21 | news | The Story of Billy Evans and ‘Theranos 2.0’ |
| 60 | 17 | news | Genetic Blueprint of Personality Revealed |
| 60 | 16 | news | Solutions |
| 60 | 13 | news | Sudan As A Mirror For Today’s World |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 100 | 20 | news | Marco Rubio urges Cubans to collaborate with CIA to topple gov’t | friday |
| 98 | 27 | news | US accuses Canada of election interference ahead of midterms | friday |
| 97 | 24 | news | Israel arrests 36 Palestinians in the West Bank, attacks on farmers ramp up | sunday |
| 96 | 23 | news | Voters in Oil-Rich Alberta Reject Leaving Canada | sunday |
| 96 | 23 | news | Iran says two tankers catch fire after hitting mines in Strait of Hormuz | monday |
| 96 | 20 | news | France Imposes Curfews in Parts of Paris and Other Cities After Nationwide Rioting | friday |
| 94 | 24 | news | Hospital in Yemen’s Taiz warns of collapse in days because of Houthi siege | friday |
| 92 | 20 | news | At Cornell, a Subdued Scene on First Weekend of Fraternity Party Ban | sunday |
| 87 | 20 | news | What’s behind Europe’s youth protests? | monday |
| 86 | 25 | wellness | The Ebola crisis is far outpacing the response, Congo's IRC director says | monday |
| 86 | 22 | news | Canadian military identifies four killed as Wainwright fire inquiry continues | friday |
| 84 | 26 | news | ‘I never saw my son, until they handed him over in a bag’: inside El Salvador’s brutal crime crackdown | tuesday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=25) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 100 | 18 | news | Man claims arm broken in violent ICE arrest | sunday |
| 100 | 17 | news | Rubio wants ‘crackdown’ on settler violence after US journalist attack | sunday |
| 100 | 15 | news | Israeli settlers attack European diplomats in the occupied West Bank | friday |
| 99 | 18 | news | Chaos and looting roiled major cities as Europeans poured into the streets to protest rising living costs | sunday |
| 99 | 15 | news | Carrefour CEO says 50 of its stores and almost 20 supermarkets were ransacked during riots in France | sunday |
| 99 | 14 | news | Iranian TV airs video said to show tanker explosion in Hormuz | friday |
| 99 | 13 | news | Albanian police fire rubber bullets as protests against Rama escalate | friday |
| 99 | 12 | news | Paris police issue overnight curfew in 2 areas of French capital to try to prevent further disorder | friday |
| 99 | 12 | news | Saudi-led forces try to break Houthi siege of Taiz with airstrikes | friday |
| 97 | 18 | news | Death Penalty Sought for Andrea Shaw, Who Blamed Toddlers’ Deaths on Vaccines | friday |
| 97 | 18 | news | China's economy accelerates on robust exports as domestic weakness persists | friday |
| 97 | 18 | news | Gaza bodybuilders find solace in strongman competition among the ruins | friday |

---

## Recommendations

- 🌾 30 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=25) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1318 articles analysed · 2026-10-24 16:51 UTC_
