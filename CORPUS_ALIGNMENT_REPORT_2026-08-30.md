# Cache Corpus Alignment Report

_Generated: 2026-08-30 17:17 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1646 |
| Articles missing theme-score data (skipped) | 157 |
| Direct-qualify (upstream score gates them in for their best theme) | 1552 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 10 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 4 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 180 (11% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 1114 |
| analysis | 226 |
| breaking | 191 |
| feature | 180 |
| news | 27 |
| fluff | 21 |
| opinion | 18 |
| recap | 11 |
| investigation | 10 |
| wire | 5 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 1154 | 55.4 | 65.4 | +10.0 | 1103 | 5 | 4 | 121 |
| ai-tech | 134 | 46.9 | 47.5 | +0.5 | 116 | 1 | 0 | 15 |
| wellness | 133 | 56.2 | 56.1 | -0.1 | 121 | 1 | 0 | 26 |
| science | 63 | 47.8 | 62.1 | +14.3 | 60 | 1 | 0 | 2 |
| local | 43 | 80.5 | 86.3 | +5.8 | 43 | 0 | 0 | 1 |
| homelab | 43 | 52.3 | 65.2 | +12.9 | 41 | 0 | 0 | 3 |
| climate | 37 | 50.6 | 64.4 | +13.8 | 35 | 1 | 0 | 4 |
| design | 29 | 49.7 | 49.3 | -0.3 | 23 | 1 | 0 | 7 |
| outdoors | 6 | 43.0 | 73.7 | +30.7 | 6 | 0 | 0 | 0 |
| scifi | 3 | 45.7 | 38.3 | -7.3 | 3 | 0 | 0 | 1 |
| homestead | 1 | 50.0 | 46.0 | -4.0 | 1 | 0 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1646 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 48.3 | 100 | 1341 | 1150 |
| Tuesday | Working Lands & Industry | 44.7 | 100 | 1196 | 949 |
| Wednesday | Repair Culture & Practical Tech | 42.2 | 100 | 1324 | 889 |
| Thursday | Indigenous Lands & Innovation | 47.0 | 100 | 1369 | 1196 |
| Friday | Wild Spaces & Outdoor Life | 48.9 | 100 | 1439 | 1168 |
| Saturday | Cariboo Local Affairs | 48.9 | 100 | 1515 | 1339 |
| Sunday | Science, Wonder & the Natural World | 49.2 | 100 | 1407 | 1166 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 1150 | 1324 | 13 | 4 |
| Tuesday | Working Lands & Industry | 30 | 15 | 949 | 1176 | 17 | 3 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 889 | 1306 | 14 | 4 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 1196 | 1359 | 6 | 4 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 1168 | 1420 | 15 | 4 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 1339 | 1513 | 0 | 2 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 1166 | 1390 | 13 | 4 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 81 | 15 | local | Prediction market trading is gambling according to B.C. regulator |
| 76 | 22 | wellness | ‘They find themselves obsessed, forgoing sleep and self-care’ — what ‘AI psychosis’ looks like, and why experts question the term |
| 73 | 2 | wellness | What Shark DNA Can Teach Us About The Biology Of Aging |
| 73 | 1 | wellness | Testosterone Matters In Women’s Health. Research And Clinical Practice Need To Catch Up. |
| 72 | 27 | wellness | How Much of a Problem is AI’s Water Use? |
| 72 | 12 | wellness | What’s the Secret to Bats’ Super Longevity? |
| 72 | 3 | design | Hot Chips 2026: Intel dives deep on Crescent Island AI accelerator — larger caches and deeper XMX engines target maximum AI FLOPS per watt |
| 72 | 2 | design | Hot Chips 2026: IBM's first dual-ISA core natively executes ARM and z/Architecture in the same core; all cores run at 5.7 GHz base frequency — next-gen mainframe AI processor is built on 2nm node with 11 cores |
| 71 | 27 | news | Why Did John Ratcliffe Go to Moscow? |
| 70 | 29 | news | Did Meta’s Big Settlement Actually Help It? |
| 70 | 25 | wellness | ‘Intrinsic Capacity’: The Most Important Longevity Term You’ve Never Heard Of |
| 70 | 20 | design | Hot Chips 2026: Nvidia presents Groq 3 LPX architecture and unveils its first third-party inference benchmark — LP30-based rack already in production, company says |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 97 | 26 | climate | I drove the Audi Q6 e-tron and BMW iX xDrive45 for a week — here’s mid-size luxury SUV I recommend | tuesday |
| 96 | 23 | news | Isolated by raging floodwaters, Nepal’s miracle home amid the devastation | thursday |
| 95 | 27 | news | Startup raises $7 million to build backpack-portable 8.8-ounce drone interceptors — Mara claims 20x cost advantage over other interceptors, priced one-for-one against attack drones | friday |
| 93 | 25 | news | Outshine Frozen Fruit Bars Recalled Due to Glass Fragments via @ConsumerReports | friday |
| 92 | 25 | science | Fantastic foams and supercritical science — why running shoes have improved so much in the past 10 years, explained by an expert who makes them | wednesday |
| 72 | 20 | design | Miami votes to restore Hilario Candela's Marine Stadium | sunday |
| 61 | 24 | news | The new reMarkable Paper Pure wowed us with its 'flawless' pad-and-pen experience, but it's far from the only great handwriting tablet on the market — here are our top alternatives | wednesday |
| 56 | 27 | wellness | How to Master the Bulgarian Split Squat to Grow Your Leg Muscles | friday |
| 46 | 23 | news | A week with the Google Pixel 11 changed my mind about Gemini (for the better) | wednesday |
| 20 | 22 | ai-tech | I flipped one toggle in Google Keep; it solved my cluttered note problem | wednesday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=23) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 99 | 18 | news | Dutch court hands life sentence to Rwandan man for genocide role | tuesday |
| 96 | 12 | news | UK has billions in contracts with firms tied to illegal Israeli settlements | friday |
| 93 | 19 | news | What is HDMI passthrough on soundbars, and do you really need it for your TV setup? | friday |
| 62 | 16 | news | Google Health gets better workout logging, improved maps, and Health Connect fixes | monday |

---

## Recommendations

- 🌾 4 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=23) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1646 articles analysed · 2026-08-30 17:17 UTC_
