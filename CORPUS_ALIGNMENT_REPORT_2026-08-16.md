# Cache Corpus Alignment Report

_Generated: 2026-08-16 13:44 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1224 |
| Articles missing theme-score data (skipped) | 272 |
| Direct-qualify (upstream score gates them in for their best theme) | 1159 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 5 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 2 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 182 (15% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 894 |
| feature | 196 |
| analysis | 195 |
| breaking | 161 |
| opinion | 20 |
| news | 13 |
| fluff | 12 |
| recap | 2 |
| wire | 2 |
| investigation | 1 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 810 | 57.9 | 63.4 | +5.5 | 766 | 5 | 2 | 125 |
| wellness | 120 | 59.3 | 54.4 | -4.9 | 113 | 0 | 0 | 24 |
| ai-tech | 101 | 48.8 | 60.6 | +11.8 | 97 | 0 | 0 | 11 |
| science | 57 | 50.6 | 61.1 | +10.5 | 57 | 0 | 0 | 3 |
| local | 50 | 83.4 | 86.8 | +3.4 | 50 | 0 | 0 | 1 |
| climate | 38 | 55.2 | 69.2 | +14.0 | 37 | 0 | 0 | 4 |
| homelab | 22 | 54.6 | 57.7 | +3.1 | 21 | 0 | 0 | 5 |
| design | 17 | 54.9 | 30.3 | -24.6 | 12 | 0 | 0 | 8 |
| outdoors | 4 | 41.5 | 44.5 | +3.0 | 3 | 0 | 0 | 0 |
| homestead | 3 | 59.0 | 51.0 | -8.0 | 2 | 0 | 0 | 1 |
| scifi | 2 | 41.0 | 22.0 | -19.0 | 1 | 0 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1224 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 48.6 | 100 | 1044 | 884 |
| Tuesday | Working Lands & Industry | 45.0 | 100 | 883 | 700 |
| Wednesday | Repair Culture & Practical Tech | 42.1 | 100 | 961 | 630 |
| Thursday | Indigenous Lands & Innovation | 46.8 | 100 | 993 | 879 |
| Friday | Wild Spaces & Outdoor Life | 49.4 | 100 | 1075 | 885 |
| Saturday | Cariboo Local Affairs | 49.3 | 100 | 1131 | 988 |
| Sunday | Science, Wonder & the Natural World | 49.7 | 100 | 1047 | 881 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 884 | 1036 | 5 | 3 |
| Tuesday | Working Lands & Industry | 30 | 15 | 700 | 875 | 5 | 3 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 630 | 952 | 6 | 3 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 879 | 987 | 3 | 3 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 885 | 1067 | 5 | 3 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 988 | 1130 | 0 | 1 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 881 | 1039 | 5 | 3 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 86 | 24 | local | Toxic Drug Alert for the Northern Health region |
| 77 | 22 | wellness | TSMC reportedly has $1 billion of Apple chips awaiting delivery of DRAM — will this be what powers the iPhone 18 Pro? |
| 77 | 22 | wellness | Can ‘magic mushrooms’ help treat cocaine dependence? |
| 74 | 28 | news | The High Cost of Danielle Smith’s Book Ban |
| 73 | 22 | wellness | Has science finally made up its mind about coffee’s health benefits? | Scientific American |
| 73 | 19 | news | Newmont backs junior Headwater on 3rd Nevada project |
| 72 | 28 | wellness | How Alzheimer’s Is Diagnosed — and Why It’s So Often Gotten Wrong |
| 72 | 28 | news | Elon Musk’s DOGE Promised Savings, But It’s Cost Us a Fortune |
| 72 | 5 | wellness | Why Aging May Be a Program, Not a Breakdown |
| 72 | 2 | wellness | 🔗 Job queues are deceptively tricky |
| 70 | 22 | wellness | Sustainability’s skeptics keep declaring victory. Tom Szaky keeps proving them wrong |
| 70 | 18 | news | The Real Reason Data Center Gas Power Plants Are So Dirty |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 99 | 24 | news | US President Trump says he will declare Strait of Hormuz US territory | friday |
| 98 | 21 | news | Here's how to format a USB drive on Windows | wednesday |
| 92 | 27 | news | CR letter to CPSC on Sensory Gel Squishy Toys | friday |
| 80 | 25 | news | Where did all the money go if the US is running out of weapons? | wednesday |
| 22 | 27 | news | Comparing `changeset` and `release-please` for our repositories at $dayjob | wednesday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=20) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 98 | 18 | news | Al Jazeera reporter on the ground as Colombia quake death toll rises | monday |
| 76 | 15 | news | Ukraine claims it found over 5,000 foreign-made components in over 200 Russian weapon systems, with missiles, drones, and armored vehicles particularly concerning | friday |

---

## Recommendations

- 🌾 2 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=20) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1224 articles analysed · 2026-08-16 13:44 UTC_
