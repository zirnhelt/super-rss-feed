# Cache Corpus Alignment Report

_Generated: 2026-08-24 03:18 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1753 |
| Articles missing theme-score data (skipped) | 173 |
| Direct-qualify (upstream score gates them in for their best theme) | 1649 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 7 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 1 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 189 (11% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 1244 |
| analysis | 236 |
| feature | 195 |
| breaking | 166 |
| news | 35 |
| opinion | 23 |
| fluff | 22 |
| recap | 3 |
| wire | 1 |
| investigation | 1 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 1195 | 54.8 | 64.5 | +9.7 | 1135 | 3 | 1 | 117 |
| wellness | 157 | 55.2 | 57.3 | +2.1 | 148 | 0 | 0 | 24 |
| ai-tech | 143 | 51.3 | 50.8 | -0.5 | 129 | 0 | 0 | 28 |
| science | 63 | 44.7 | 56.5 | +11.8 | 60 | 0 | 0 | 4 |
| local | 58 | 74.9 | 94.1 | +19.2 | 58 | 0 | 0 | 0 |
| homelab | 47 | 55.8 | 56.6 | +0.8 | 43 | 0 | 0 | 7 |
| climate | 41 | 53.5 | 70.4 | +16.8 | 39 | 0 | 0 | 4 |
| design | 27 | 46.2 | 55.4 | +9.2 | 23 | 1 | 0 | 5 |
| outdoors | 12 | 37.0 | 49.8 | +12.8 | 7 | 1 | 0 | 0 |
| scifi | 6 | 33.8 | 49.0 | +15.2 | 3 | 2 | 0 | 0 |
| homestead | 4 | 47.8 | 66.0 | +18.2 | 4 | 0 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1753 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 48.4 | 100 | 1488 | 1253 |
| Tuesday | Working Lands & Industry | 44.4 | 100 | 1254 | 979 |
| Wednesday | Repair Culture & Practical Tech | 41.7 | 100 | 1400 | 899 |
| Thursday | Indigenous Lands & Innovation | 46.7 | 100 | 1429 | 1246 |
| Friday | Wild Spaces & Outdoor Life | 49.0 | 100 | 1551 | 1242 |
| Saturday | Cariboo Local Affairs | 49.0 | 100 | 1620 | 1428 |
| Sunday | Science, Wonder & the Natural World | 49.2 | 100 | 1483 | 1258 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 1253 | 1481 | 7 | 0 |
| Tuesday | Working Lands & Industry | 30 | 15 | 979 | 1240 | 14 | 0 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 899 | 1394 | 6 | 0 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 1246 | 1427 | 1 | 1 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 1242 | 1543 | 7 | 1 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 1428 | 1618 | 1 | 1 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 1258 | 1475 | 7 | 1 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 70 | 20 | news | The Truth Behind UFO Sightings over Canada’s Nuclear Facilities | The Walrus |
| 70 | 8 | wellness | Not every AI-in-education tale is a horror story. How the world’s leading education company makes AI that’s actually useful for students |
| 69 | 10 | news | 4 hardworking plants that make small gardens fuller, more structured and beautifully scented |
| 68 | 25 | wellness | Opinion: The global health aid architecture is collapsing. The faith economy isn’t |
| 67 | 29 | wellness | Ebola outbreak: five big questions |
| 67 | 29 | news | How the Iran War Made Africa’s Richest Man Even Richer |
| 67 | 29 | news | Is Silicon Valley in the Justice Dept.’s Sights? |
| 67 | 26 | news | Nvidia wants to stop AI costs skyrocketing with its new software router — but will it really make a difference? |
| 67 | 25 | news | Angie Nixon Goes on Trial in September. She Just Won Florida’s Senate Primary. |
| 67 | 20 | wellness | Does fibermaxxing work? It may depend on your microbiome |
| 67 | 17 | news | "Don’t boycott GTA 6," fired Rockstar devs say: "Support our legal battle instead" and "win justice for the people who helped make it" |
| 67 | 15 | wellness | OpenAI is losing female execs. But data shows women in AI don’t even make it to the C-suite |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 98 | 25 | news | Somalia child hunger crisis deepens after aid cuts, UNICEF says | friday |
| 93 | 26 | news | Ebola continues to spread in the DRC as 16,000 vaccine doses arrive | monday |
| 88 | 25 | news | Declaration of Ward Boston, Jr., Captain, JAGC, USN (Ret.), Concerning the Court of Inquiry into the Attack on USS Liberty | friday |
| 79 | 28 | scifi | Why The Vast of Night Mysteriously Disappeared From Streaming | tuesday |
| 49 | 25 | outdoors | Looking for the perfect hiking daypack? We may have just found it... | wednesday |
| 24 | 27 | scifi | "They don't make 'em like they used to": How flash player games defined an era of indie horror | monday |
| 15 | 16 | design | Nicknamed the Barcode House, This Steely Munich Home Rings Up for €10M - Dwell | sunday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=23) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 32 | 14 | news | A Travel Guide to Barranco Neighborhood in Lima, Peru - AFAR | friday |

---

## Recommendations

- 🌾 1 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=23) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1753 articles analysed · 2026-08-24 03:18 UTC_
