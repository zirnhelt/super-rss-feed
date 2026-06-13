# Cache Corpus Alignment Report

_Generated: 2026-06-13 21:24 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1229 |
| Articles missing theme-score data (skipped) | 0 |
| Direct-qualify (upstream score gates them in for their best theme) | 320 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 24 |
| Stranded (good theme fit, upstream below `min_claude_score`=20 — never bankable) | 1 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 359 (29% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 919 | 51.0 | 21.3 | -29.7 | 290 | 21 | 0 | 289 |
| ai-tech | 95 | 27.0 | 4.8 | -22.2 | 0 | 0 | 0 | 23 |
| wellness | 79 | 35.3 | 15.8 | -19.5 | 13 | 1 | 0 | 16 |
| climate | 34 | 18.0 | 9.9 | -8.1 | 0 | 1 | 0 | 2 |
| local | 30 | 86.6 | 20.8 | -65.7 | 13 | 0 | 0 | 20 |
| science | 28 | 18.3 | 9.6 | -8.7 | 1 | 0 | 0 | 2 |
| homelab | 27 | 18.4 | 7.4 | -11.1 | 1 | 1 | 1 | 3 |
| scifi | 17 | 23.5 | 8.2 | -15.2 | 2 | 0 | 0 | 4 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1229 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 0.7 ⚠️ | 16 | 0 | 0 |
| Tuesday | Working Lands & Industry | 0.0 ⚠️ | 2 | 0 | 0 |
| Wednesday | Gear, Gadgets & Practical Tech | 18.4 | 81 | 340 | 62 |
| Thursday | Indigenous Lands & Innovation | 0.3 ⚠️ | 6 | 0 | 0 |
| Friday | Wild Spaces & Outdoor Life | 3.2 | 25 | 0 | 0 |
| Saturday | Cariboo Local Affairs | 3.5 | 30 | 13 | 2 |
| Sunday | Science, Wonder & the Natural World | 9.9 | 63 | 42 | 12 |

⚠️ **3 of 7 themes have near-zero fit across the entire corpus**: **Arts, Culture & Digital Storytelling** (avg 0.7, max 16), **Working Lands & Industry** (avg 0.0, max 2), **Indigenous Lands & Innovation** (avg 0.3, max 6). This isn't a scoring-threshold problem — essentially nothing in the 7-day candidate pool is even rated as *somewhat* relevant to these themes. Either (a) the upstream interest score is filtering out this content before it ever reaches the podcast cache (so theme-scoring never sees genuinely relevant articles), (b) the feeds themselves aren't surfacing this content, or (c) these theme-scoring prompts are miscalibrated relative to the rest. Worth spot-checking a few raw feed articles for these topics against their theme score directly.


## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 42 | 30 | 0 | 0 | 0 | 0 |
| Tuesday | Working Lands & Industry | 45 | 30 | 0 | 0 | 0 | 0 |
| Wednesday | Gear, Gadgets & Practical Tech | 42 | 25 | 62 | 316 | 23 | 1 |
| Thursday | Indigenous Lands & Innovation | 40 | 25 | 0 | 0 | 0 | 0 |
| Friday | Wild Spaces & Outdoor Life | 42 | 28 | 0 | 0 | 0 | 0 |
| Saturday | Cariboo Local Affairs | 25 | 15 | 2 | 13 | 0 | 0 |
| Sunday | Science, Wonder & the Natural World | 42 | 30 | 12 | 41 | 1 | 0 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 100 | 28 | local | B.C. funds 16 forest resiliency projects in Cariboo-Chilcotin |
| 100 | 20 | local | Williams Lake writer shortlisted for new award recognizing outstanding books in B.C. |
| 100 | 13 | local | Senior’s Advocate of B.C. coming to the Cariboo |
| 100 | 8 | local | Xat’sull First Nation bringing Calling Our People Home event to Williams Lake |
| 100 | 8 | local | Williams Lake class of 2026 makes history says Orange Shirt Day founder |
| 100 | 7 | local | Inomin Mines continues exploration near Williams Lake |
| 100 | 5 | local | Williams Lake rejects jail closure idea, seeks government support on repeat crime |
| 100 | 2 | local | ‘Escaped Alone’ wins best production in Williams Lake |
| 97 | 28 | news | Robert Allan Shaw |
| 92 | 28 | news | Suspected impaired driver found unconscious near B.C. elementary school |
| 92 | 25 | news | Louis Kowalski |
| 90 | 27 | news | Stephen Eduard Ganguin |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 42 | 33 | news | Hardware | wednesday |
| 40 | 38 | news | I'm a seasoned camper, and my #1 tip is to choose your kit wisely — here's what I'd pack | wednesday |
| 40 | 35 | news | OPP officer killed in line of duty near northern Ontario town | wednesday |
| 37 | 24 | news | BP is overhauling its structure into upstream and downstream units under its new CEO | sunday |
| 35 | 41 | climate | NOAA Issues El Nino Advisory | wednesday |
| 35 | 28 | news | HUD Secretary Scott Turner shows how administration is empowering homebuilders | wednesday |
| 32 | 36 | news | Canada confirms opening of Gordie Howe Bridge, despite Trump’s threats | wednesday |
| 31 | 35 | homelab | The biggest lie about 3D printing is that it's still difficult—here's how easy it really is | wednesday |
| 30 | 38 | news | US says it has begun strikes against Iran following crash of Army Apache helicopter off Oman coast | wednesday |
| 30 | 34 | news | IAEA chief says Iran-US nuclear talks in ‘complicated phase’ | wednesday |
| 28 | 36 | news | Meet the Gem, a wearable taking the guesswork out of tracking sun exposure | wednesday |
| 28 | 34 | news | How Americans celebrated the bicentennial - with fireworks, a Freedom Train and Farrah | wednesday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below `min_claude_score`=20 upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 31 | 13 | homelab | These official NASA models are perfect weekend 3D printing projects (Jun 12-14) | wednesday |

---

## Recommendations

- 🚨 Monday (Arts, Culture & Digital Storytelling), Tuesday (Working Lands & Industry), Thursday (Indigenous Lands & Innovation) have essentially no viable candidates in the current corpus. Pull a handful of raw feed articles you'd *expect* to score well for these themes and run them through `score_articles_for_theme` directly — if they score near 0 there too, the theme prompts in `config/podcast_schedule.json` need recalibration; if they score normally, the upstream interest score (or feed sourcing) is the bottleneck keeping this content out of `podcast_articles_cache.json` in the first place.
- 📊 **news** is 919/1229 (75%) of the corpus, and 289 of those (31%) clear the upstream gate while fitting no theme above 30. Consider adding a theme-fit floor to `route_articles_to_best_themes`/`generate_podcast_feed`'s 'direct qualify' path (not just upstream score) so generic news doesn't crowd out better-fitting candidates on its best-scoring (but still weak) day.
- 📍 **local** articles average 86.6 upstream (boosted by the Williams Lake/Cariboo +20 override in `scoring_interests.txt`) but only 20.8 best-theme-fit — 20/30 are filler. Local civic/crime/awards items pass the quality bar on the geographic bonus alone but don't map to any of the 7 themes; Saturday's 'Cariboo Local Affairs' (min_score 25) is the only day designed to absorb these — verify the bonus isn't pushing them into other days' buckets instead.
- 🌾 1 article(s) fit a theme well but score below `min_claude_score`=20 overall and are stranded — see the Stranded Examples table. If these categories matter, consider a per-category `min_score_by_category` floor (as already exists for `ai-tech`) so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1229 articles analysed · 2026-06-13 21:24 UTC_
