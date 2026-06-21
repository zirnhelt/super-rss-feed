# Cache Corpus Alignment Report

_Generated: 2026-06-21 15:18 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 441 |
| Articles missing theme-score data (skipped) | 391 |
| Direct-qualify (upstream score gates them in for their best theme) | 274 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 10 |
| Stranded (good theme fit, upstream below `min_claude_score`=20 — never bankable) | 5 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 60 (14% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 630 |
| unknown | 202 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 272 | 64.2 | 54.7 | -9.5 | 224 | 4 | 0 | 41 |
| ai-tech | 60 | 19.8 | 14.6 | -5.1 | 7 | 2 | 3 | 6 |
| wellness | 50 | 41.2 | 32.1 | -9.1 | 20 | 3 | 1 | 8 |
| local | 27 | 79.2 | 59.1 | -20.1 | 22 | 0 | 0 | 4 |
| climate | 14 | 10.3 | 17.3 | +7.0 | 0 | 0 | 1 | 0 |
| homelab | 9 | 16.4 | 18.6 | +2.1 | 1 | 0 | 0 | 1 |
| scifi | 9 | 15.7 | 16.1 | +0.4 | 0 | 1 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 441 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 28.6 | 80 | 150 | 116 |
| Tuesday | Working Lands & Industry | 28.7 | 80 | 150 | 107 |
| Wednesday | Repair Culture & Practical Tech | 26.7 | 80 | 183 | 105 |
| Thursday | Indigenous Lands & Innovation | 28.2 | 80 | 195 | 121 |
| Friday | Wild Spaces & Outdoor Life | 28.8 | 80 | 166 | 115 |
| Saturday | Cariboo Local Affairs | 28.5 | 80 | 299 | 199 |
| Sunday | Science, Wonder & the Natural World | 28.9 | 80 | 152 | 117 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 42 | 30 | 116 | 147 | 2 | 1 |
| Tuesday | Working Lands & Industry | 45 | 30 | 107 | 147 | 3 | 0 |
| Wednesday | Repair Culture & Practical Tech | 42 | 25 | 105 | 179 | 4 | 0 |
| Thursday | Indigenous Lands & Innovation | 40 | 25 | 121 | 187 | 4 | 4 |
| Friday | Wild Spaces & Outdoor Life | 42 | 28 | 115 | 163 | 3 | 0 |
| Saturday | Cariboo Local Affairs | 25 | 15 | 199 | 287 | 1 | 11 |
| Sunday | Science, Wonder & the Natural World | 42 | 30 | 117 | 151 | 1 | 0 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 90 | 27 | local | Cariboo, northern B.C. under severe thunderstorm watch |
| 85 | 27 | local | Signed, sealed and delivered: Canada Post and CUPW sign off : My Cariboo Now |
| 85 | 26 | local | Lac La Hache Library temporarily closing this summer for renovations |
| 85 | 20 | local | New Tumbler Ridge school among projects in Ottawa-B.C. funding agreement : My Cariboo Now |
| 82 | 28 | news | Why transparent AI matters for enterprise trust |
| 80 | 23 | news | 'Investors suffered damages': Microsoft shareholders file class action lawsuit over its huge increase in AI and cloud spending |
| 80 | 12 | news | Social capital and community resilience: A conversation with Daniel Aldrich |
| 79 | 18 | ai-tech | Two-thirds of Americans think AI is advancing too quickly |
| 78 | 21 | news | Why most AI projects don’t deliver ROI and how to fix it |
| 78 | 20 | news | ‘Unidentified substance’ poured on to Port Coquitlam Terry Fox statue: RCMP |
| 76 | 18 | homelab | 3 homelab tools that finally simplified my self-hosting setup (June 19 - 21) |
| 75 | 25 | news | PHOTOS: B.C. photographer captures rare moment of herons raised by eagle |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 80 | 42 | news | I’m a travel photographer, and this Canon PowerShot is the one compact camera I’m packing for my next city break — plus it's on sale for it's lowest price yet | tuesday |
| 62 | 41 | news | "La Croix des Fiancés" (The Fiancés Cross) in Jalhay, Belgium | wednesday |
| 62 | 40 | news | Federal grant delays could jeopardize essential disability services, research | sunday |
| 58 | 42 | news | Norway seeks to ban trade with illegal Israeli settlements in Palestine | tuesday |
| 36 | 32 | wellness | Buildings May Soon Have ‘Immune Systems’ That Fight Airborne Disease | thursday |
| 30 | 40 | scifi | Revealing Tyrant in the Cracks by Hache Pueyo | wednesday |
| 28 | 39 | ai-tech | Trader and podcast host Ed Elson unpacks why he's bearish on coming mega-IPOs | thursday |
| 28 | 38 | ai-tech | Nearly half of American adults now use AI, but concerns are also growing | thursday |
| 27 | 31 | wellness | Flu outbreak tests new Pentagon vaccine policy | wednesday |
| 26 | 33 | wellness | Six of the biggest health news stories today | thursday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below `min_claude_score`=20 upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 48 | 10 | wellness | Quartz countertops may be causing a public health crisis in the US | monday |
| 27 | 8 | climate | Xiaomi May Have Just Invented a Robot Arm for EV Charging | thursday |
| 25 | 18 | ai-tech | Anthropic got hit by export rules nobody understands | thursday |
| 19 | 12 | ai-tech | Google's New AI 'Information Agents' Can Send You Alerts on Topics You Care About | saturday |
| 16 | 5 | ai-tech | Google’s latest Android XR demo gives smart glasses a killer use case | saturday |

---

## Recommendations

- 🌾 5 article(s) fit a theme well but score below `min_claude_score`=20 overall and are stranded — see the Stranded Examples table. If these categories matter, consider a per-category `min_score_by_category` floor (as already exists for `ai-tech`) so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 441 articles analysed · 2026-06-21 15:18 UTC_
