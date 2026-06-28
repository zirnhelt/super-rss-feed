# Cache Corpus Alignment Report

_Generated: 2026-06-28 14:58 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 490 |
| Articles missing theme-score data (skipped) | 51 |
| Direct-qualify (upstream score gates them in for their best theme) | 252 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 71 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 120 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 46 (9% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 541 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 335 | 37.6 | 45.0 | +7.4 | 167 | 47 | 101 | 22 |
| wellness | 63 | 29.8 | 35.5 | +5.7 | 31 | 16 | 8 | 4 |
| ai-tech | 38 | 48.6 | 28.8 | -19.8 | 23 | 1 | 6 | 13 |
| local | 24 | 84.3 | 60.8 | -23.5 | 23 | 0 | 0 | 5 |
| climate | 16 | 30.5 | 36.9 | +6.4 | 7 | 7 | 1 | 1 |
| scifi | 7 | 19.9 | 13.3 | -6.6 | 1 | 0 | 2 | 1 |
| homelab | 6 | 5.2 | 20.0 | +14.8 | 0 | 0 | 2 | 0 |
| science | 1 | 6.0 | 12.0 | +6.0 | 0 | 0 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 490 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 26.7 | 80 | 317 | 171 |
| Tuesday | Working Lands & Industry | 26.7 | 80 | 318 | 148 |
| Wednesday | Repair Culture & Practical Tech | 26.7 | 80 | 353 | 171 |
| Thursday | Indigenous Lands & Innovation | 26.6 | 80 | 352 | 206 |
| Friday | Wild Spaces & Outdoor Life | 26.7 | 80 | 354 | 171 |
| Saturday | Cariboo Local Affairs | 26.7 | 80 | 397 | 283 |
| Sunday | Science, Wonder & the Natural World | 26.7 | 80 | 319 | 171 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 171 | 205 | 51 | 61 |
| Tuesday | Working Lands & Industry | 30 | 15 | 148 | 200 | 51 | 67 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 171 | 217 | 52 | 84 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 206 | 213 | 48 | 91 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 171 | 225 | 59 | 70 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 283 | 257 | 48 | 92 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 171 | 210 | 53 | 56 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 90 | 27 | local | Ribbon cut for Tsilhqot’in Equine Therapy Centre west of Williams Lake |
| 90 | 26 | local | Resident, cat escape early morning house fire in West Quesnel |
| 85 | 27 | local | ORV use on 100 Mile House roads subject of public meeting |
| 85 | 24 | local | Inviting residents of 100 Mile House to comment on timber supply review |
| 85 | 8 | local | HOMETOWN HERO: Sgt. Matt Isaak helps keep Quesnel’s streets safe |
| 80 | 29 | news | Marianne Lake, a Potential Dimon Successor, Leaves JPMorgan |
| 80 | 25 | news | Dramatically redesigned GMKtec EVO-X3 shown bearing Lisa Su’s signature of approval — flagship AI mini PC workstation is built around AMD’s Ryzen AI Max+ 395 'Strix Halo' processor, again |
| 79 | 23 | ai-tech | Price of 25-year-old DDR2 memory set to more than double — thanks to AI-driven RAM-armageddon |
| 78 | 23 | ai-tech | Is China Closing the A.I. Gap Faster Than Expected? |
| 77 | 29 | news | Tech workers are spending nights and weekends learning new AI tools. They say they can't afford not to. |
| 77 | 22 | news | Is your job 'AI-resilient'? Find your risk score with our career calculator |
| 76 | 29 | news | AI researchers continue to leave Google for its rivals |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 80 | 23 | wellness | How controlling my charger with a smart plug saved my phone's long-term health | thursday |
| 80 | 15 | news | Modern laptops are getting less repairable, and my 12-year-old laptop proves it | wednesday |
| 80 | 14 | news | Hackaday Podcast Episode 375: Rebuilding Tech on Our Terms and the Hero Nerd | thursday |
| 74 | 19 | news | B.C. premier visiting China to pitch LNG project as province’s ‘really big fish’ | tuesday |
| 71 | 23 | news | Last chance to save up to 55% on these brilliant Hoto tools for PC builders and hobbyists, starting from $14 — super low prices set to end soon on cordless electric screwdrivers, drills, flashlights, vacuum cleaners, and more | wednesday |
| 70 | 27 | news | World's first 100% electric hydrofoil pilot boat hits the water | wednesday |
| 68 | 26 | wellness | Missing just one night of sleep impacts your brain’s connections | monday |
| 68 | 15 | news | Justin Trudeau's youngest son joins Son of a Critch as an extra | tuesday |
| 66 | 22 | news | Adjustable Dumbbells Are My Favorite Home Gym Upgrade, and These Sets Are up to 31% Off for Prime Day | friday |
| 66 | 17 | news | Osoyoos Indian Band set to restore native plants, species in wildfire-ravaged forests | thursday |
| 66 | 14 | news | Cramming a Mini-ITX Gaming PC into a 3D Printed Steam Machine Sized Case | wednesday |
| 65 | 13 | news | Best Investments Over the Last 100 Years? Almost All Are Tech Companies. | thursday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=13) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 76 | 7 | news | Hawaii is turning ocean plastic and fishing nets into roads | thursday |
| 75 | 8 | homelab | Stop using external hard drives for your home server | thursday |
| 74 | 7 | news | Agriculture news and commodity markets - AgWeb | tuesday |
| 70 | 12 | news | Hello Kitty Cafe in Las Vegas, Nevada | thursday |
| 70 | 7 | news | Archaic Hominin Species Buried Only Their Women | thursday |
| 59 | 12 | news | How to See the Giant Asteroid That Will Pass by Earth This Weekend | friday |
| 59 | 6 | wellness | Reports | OpenMedia | tuesday |
| 58 | 8 | news | This Chinese company is reportedly developing a feature Apple and Samsung can only dream of | thursday |
| 58 | 8 | news | Garmin's Most Basic Running Watch Is Now Cheaper Than Ever | friday |
| 57 | 13 | ai-tech | Top Stories: Massive Apple Price Increases, iOS 27 Beta 2, and More | friday |
| 57 | 12 | news | At Cannes Lions, summer fashion mirrored marketers' renewed emphasis on creative credibility | tuesday |
| 56 | 12 | news | Your dog’s walk offers clues of early signs of canine dementia | monday |

---

## Recommendations

- 🌾 120 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=13) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 490 articles analysed · 2026-06-28 14:58 UTC_
