# Cache Corpus Alignment Report

_Generated: 2026-10-10 18:03 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 467 |
| Articles missing theme-score data (skipped) | 964 |
| Direct-qualify (upstream score gates them in for their best theme) | 432 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 11 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 7 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 40 (9% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 920 |
| analysis | 180 |
| feature | 141 |
| breaking | 120 |
| news | 28 |
| opinion | 23 |
| fluff | 7 |
| recap | 6 |
| wire | 5 |
| how-to | 1 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 344 | 53.2 | 71.5 | +18.3 | 318 | 10 | 6 | 35 |
| ai-tech | 40 | 45.1 | 57.4 | +12.3 | 38 | 0 | 0 | 2 |
| science | 26 | 43.2 | 61.4 | +18.2 | 21 | 1 | 1 | 1 |
| wellness | 23 | 44.9 | 55.4 | +10.5 | 21 | 0 | 0 | 2 |
| local | 14 | 83.3 | 94.4 | +11.1 | 14 | 0 | 0 | 0 |
| design | 9 | 41.8 | 64.6 | +22.8 | 9 | 0 | 0 | 0 |
| climate | 8 | 48.0 | 89.9 | +41.9 | 8 | 0 | 0 | 0 |
| homelab | 3 | 47.0 | 88.3 | +41.3 | 3 | 0 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 467 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 51.1 | 100 | 388 | 339 |
| Tuesday | Working Lands & Industry | 48.8 | 100 | 339 | 339 |
| Wednesday | Repair Culture & Practical Tech | 44.8 | 100 | 371 | 245 |
| Thursday | Indigenous Lands & Innovation | 50.3 | 100 | 378 | 320 |
| Friday | Wild Spaces & Outdoor Life | 51.3 | 100 | 414 | 342 |
| Saturday | Cariboo Local Affairs | 51.6 | 100 | 434 | 380 |
| Sunday | Science, Wonder & the Natural World | 52.0 | 100 | 403 | 341 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 339 | 369 | 12 | 7 |
| Tuesday | Working Lands & Industry | 30 | 15 | 339 | 313 | 19 | 7 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 245 | 356 | 10 | 5 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 320 | 365 | 6 | 7 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 342 | 395 | 12 | 7 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 380 | 429 | 0 | 5 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 341 | 384 | 12 | 7 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 68 | 11 | news | ‘Life behind each name’: Victoria monument honours Japanese Canadians interned during WW2 |
| 67 | 10 | news | What Is Zionism? |
| 65 | 22 | news | What has Michelin really changed? Top Vancouver restaurateurs weigh in |
| 65 | 14 | news | Vagus Nerve Stimulation Could Help New Skills Stick |
| 65 | 8 | news | When States Act, Markets Follow: The Ripple Effects of PFAS and Chemical Safety Policies |
| 63 | 29 | news | "US could be writing its own losing ticket": Amazon warns against 100+ AI data center bans as it pledges $1 billion to defuse AI backlash |
| 63 | 24 | news | Texas Pediatricians Face Paxton Investigations for Vaccinating Children |
| 62 | 10 | wellness | Epigenetic Editing Could Wipe Out Chronic Hepatitis B Infections |
| 60 | 28 | news | ‘How Does That Happen?’: America’s Execution System Is Long Flawed |
| 60 | 26 | news | The Easy Bike Maintenance Job That Can Make Every Ride Feel Better—Clean and Lube Your Chain |
| 60 | 19 | news | US approves first data center-specific small nuclear reactor — the BWRX-300 may be covering not just the UK, but America too |
| 60 | 10 | news | 'It's the most significant opportunity for self-builders in a generation' – could grey belt land finally unlock your dream home? |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 100 | 21 | news | Man jailed for using 1,000 bots to fraudulently make $8m from his AI music | monday |
| 98 | 24 | news | Tunisia sentences blogger Hajer Awadi to 26 months over social media post | monday |
| 98 | 23 | news | China allegedly intercepted UPS-shipped F-35 parts after employee missed email warning | sunday |
| 90 | 24 | news | Criminal defamation threat hangs over dozens of Angolan journalists ahead of 2027 vote | thursday |
| 88 | 25 | news | Thai court to hear criminal defamation charges against investigative reporter Tom Wright | friday |
| 78 | 26 | news | More than 80 US military aircraft have been damaged so far in the Iran war. Equipment losses could be over $3.3 billion. | friday |
| 67 | 26 | news | Microsoft rivals the MacBook Pro with an Nvidia chip and repairable design | wednesday |
| 66 | 24 | news | After Thirty Years, Fox Remains the House Ailes Built | sunday |
| 37 | 22 | news | ‘Medicare for All’ Message Attracts Voters Buckling Under Medical Bills | friday |
| 32 | 28 | news | Recovering Signal Decay, Three Songs at a Time | tuesday |
| 32 | 28 | science | Forget Las Vegas—Archaeologists Just Found 1,000 Dice Underneath an Ancient City | tuesday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=25) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 98 | 9 | news | Intercommunal clashes kill 71 people in South Sudan | thursday |
| 96 | 17 | news | Israel shuts down British consulate in occupied East Jerusalem | friday |
| 94 | 18 | news | Mexico investigates video said to show cartel members fighting for Ukraine | friday |
| 93 | 17 | news | South Africa protests turn violent amid rage over asylum ruling | sunday |
| 85 | 12 | news | Iran war live: Kremlin says Trump welcomed Russia’s effort in Iran deal | friday |
| 74 | 12 | news | Putin tells Trump peace talks are unlikely, cites Ukraine drone attacks | saturday |
| 39 | 21 | science | Single Orangutan Moms Set up Playdates for Their Kids | monday |

---

## Recommendations

- 🌾 7 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=25) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 467 articles analysed · 2026-10-10 18:03 UTC_
