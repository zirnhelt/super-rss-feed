# Cache Corpus Alignment Report

_Generated: 2026-07-05 14:51 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1303 |
| Articles missing theme-score data (skipped) | 98 |
| Direct-qualify (upstream score gates them in for their best theme) | 755 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 145 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 303 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 64 (5% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 1401 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 1068 | 36.4 | 45.1 | +8.7 | 610 | 124 | 261 | 48 |
| wellness | 87 | 35.3 | 45.7 | +10.4 | 51 | 12 | 18 | 2 |
| ai-tech | 46 | 38.0 | 30.1 | -7.9 | 24 | 1 | 9 | 8 |
| local | 31 | 83.5 | 67.3 | -16.2 | 30 | 1 | 0 | 0 |
| science | 21 | 29.2 | 44.9 | +15.7 | 9 | 3 | 7 | 1 |
| homelab | 19 | 41.3 | 39.6 | -1.7 | 13 | 0 | 3 | 3 |
| scifi | 16 | 40.1 | 34.3 | -5.8 | 11 | 1 | 2 | 2 |
| climate | 15 | 24.1 | 41.7 | +17.7 | 7 | 3 | 3 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1303 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 32.6 | 80 | 960 | 667 |
| Tuesday | Working Lands & Industry | 33.1 | 80 | 969 | 641 |
| Wednesday | Repair Culture & Practical Tech | 32.5 | 80 | 1024 | 661 |
| Thursday | Indigenous Lands & Innovation | 32.4 | 80 | 1023 | 732 |
| Friday | Wild Spaces & Outdoor Life | 32.4 | 80 | 1022 | 659 |
| Saturday | Cariboo Local Affairs | 32.5 | 80 | 1114 | 893 |
| Sunday | Science, Wonder & the Natural World | 32.4 | 80 | 957 | 661 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 667 | 674 | 114 | 172 |
| Tuesday | Working Lands & Industry | 30 | 15 | 641 | 667 | 121 | 181 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 661 | 684 | 125 | 215 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 732 | 693 | 109 | 221 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 659 | 694 | 132 | 196 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 893 | 760 | 97 | 257 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 661 | 678 | 124 | 155 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 83 | 28 | news | Homelab Gets Linksys Themed Aesthetic |
| 79 | 29 | news | B.C., feds agree to keep North Coast tanker ban, but still clear way for new pipeline |
| 79 | 5 | news | Alex Karp rips into AI labs: 'These models have been completely, irresponsibly, oversold' |
| 79 | 4 | news | Nvidia RTX 5090 GPUs are so expensive that Intel's Arc Pro B70 is now a genuine bargain for AI — 128GB 4-card configuration costs less than $3800 |
| 78 | 24 | news | Surrey judge sets 4-year sentence for driving ‘rampage’ that led to 13 crashes, 9 victims injured |
| 77 | 21 | news | Cheers and jeers: Alberta Premier rolls through Calgary in Stampede parade |
| 77 | 14 | news | 10 truths every investor should know about the AI gold rush |
| 77 | 11 | news | The AI pendulum is swinging back to a more realistic place, says Don McGuire, CMO of Qualcomm |
| 75 | 10 | ai-tech | OpenAI floats giving Trump administration 5 percent cut of AI boom |
| 74 | 13 | news | Bill Gates says only four jobs are safe from AI — but here are 7 other predictions he's made that didn't age well |
| 74 | 6 | ai-tech | Setting up a local LLM is the easy part—here's what you need to do with it next |
| 73 | 25 | news | At least 15 Yemeni government troops killed in Hodeidah fighting |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 79 | 13 | news | Farmers risk long-term harm to soggy fields by re-working too soon | tuesday |
| 77 | 25 | news | 7 new movies and TV shows to watch on Netflix, Prime Video, HBO Max, and more this weekend (July 3) | monday |
| 77 | 13 | news | Oracle landed a contract to run HR software for the entire U.S. government | thursday |
| 77 | 13 | news | Forest service to remove your voice from public lands decisions | tuesday |
| 74 | 26 | news | Students fly high with new world record for largest paper plane | wednesday |
| 74 | 16 | news | Redodo battery and accessories review | friday |
| 74 | 13 | news | 'Civil War,' 'Summer's Last Resort' and More Movies You Can Stream for Free | monday |
| 74 | 11 | wellness | Read the pitch deck these Stanford grads used to raise $11.6 million for a wearable device to track women's hormones | thursday |
| 72 | 21 | news | Anthropic's Claude Fable 5 Available Again After U.S. Lifts Export Controls | wednesday |
| 71 | 27 | news | Xbox testing disc-to-digital feature that digitizes a physical game collection | friday |
| 71 | 25 | news | Morphing, color-changing liquid stores energy by “charging” into a gel | monday |
| 71 | 13 | news | Scientists reveal what really happens when water is trapped in tiny spaces | friday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=13) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 80 | 7 | news | iFixit Begins Developing a Repairability Scoring Standard with NSF | wednesday |
| 77 | 6 | news | Alty pledges $1.2M to clean up 162 acres of farmland that will be returned to Kahnawà:ke | thursday |
| 75 | 10 | ai-tech | Tim Cook Holds 'Constructive' Talks With EU Over Siri AI Launch | thursday |
| 74 | 11 | news | As war grinds on, Ukrainian climbers build a new outdoor culture inspired by Yosemite | wednesday |
| 72 | 8 | news | Google owes Klarna $1.5 billion for favoring its own price-comparison tool over Klarna's | thursday |
| 70 | 5 | climate | Honda's adorable $25K kei car heads westward | tuesday |
| 69 | 12 | news | Stop screeching about immigration, and get smart about it | tuesday |
| 69 | 11 | news | Summer heat is silently killing your phone's battery—here's how to keep it safe this summer | monday |
| 67 | 12 | news | The Radical Magic of Estelle Shook | tuesday |
| 67 | 9 | wellness | Your SSD has a hidden setting that extends its lifespan | wednesday |
| 67 | 8 | news | The 10 most popular products ZDNET readers bought last month (including during Prime Day) | thursday |
| 66 | 9 | news | Companies join hands to collectively dunk on PlayStation's all-digital future — Domino's pizza, KFC, and GameSir all threaten an end to physical production | thursday |

---

## Recommendations

- 🌾 303 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=13) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1303 articles analysed · 2026-07-05 14:51 UTC_
