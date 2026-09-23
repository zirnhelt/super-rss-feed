# Cache Corpus Alignment Report

_Generated: 2026-09-06 16:14 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1857 |
| Articles missing theme-score data (skipped) | 184 |
| Direct-qualify (upstream score gates them in for their best theme) | 1751 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 12 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 9 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 176 (9% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 1201 |
| analysis | 283 |
| breaking | 260 |
| feature | 228 |
| opinion | 25 |
| fluff | 19 |
| news | 13 |
| wire | 7 |
| recap | 4 |
| interview | 1 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 1286 | 54.0 | 67.9 | +13.9 | 1221 | 6 | 9 | 115 |
| ai-tech | 154 | 46.4 | 49.3 | +2.8 | 137 | 2 | 0 | 24 |
| wellness | 128 | 55.6 | 53.9 | -1.7 | 116 | 1 | 0 | 24 |
| science | 71 | 47.2 | 61.8 | +14.6 | 71 | 0 | 0 | 5 |
| local | 65 | 81.0 | 90.8 | +9.8 | 65 | 0 | 0 | 1 |
| homelab | 65 | 53.4 | 79.5 | +26.1 | 61 | 2 | 0 | 1 |
| climate | 54 | 52.6 | 70.4 | +17.8 | 52 | 0 | 0 | 4 |
| design | 21 | 45.5 | 46.6 | +1.0 | 19 | 0 | 0 | 2 |
| homestead | 5 | 58.2 | 88.6 | +30.4 | 5 | 0 | 0 | 0 |
| outdoors | 4 | 43.0 | 41.8 | -1.2 | 2 | 0 | 0 | 0 |
| scifi | 4 | 32.2 | 36.5 | +4.2 | 2 | 1 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1857 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 48.3 | 100 | 1572 | 1328 |
| Tuesday | Working Lands & Industry | 45.1 | 100 | 1348 | 1107 |
| Wednesday | Repair Culture & Practical Tech | 43.0 | 100 | 1472 | 1037 |
| Thursday | Indigenous Lands & Innovation | 46.8 | 100 | 1505 | 1310 |
| Friday | Wild Spaces & Outdoor Life | 49.0 | 100 | 1636 | 1325 |
| Saturday | Cariboo Local Affairs | 48.9 | 100 | 1711 | 1510 |
| Sunday | Science, Wonder & the Natural World | 49.2 | 100 | 1576 | 1342 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 1328 | 1548 | 15 | 9 |
| Tuesday | Working Lands & Industry | 30 | 15 | 1107 | 1320 | 20 | 8 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 1037 | 1448 | 15 | 9 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 1310 | 1485 | 11 | 9 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 1325 | 1612 | 15 | 9 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 1510 | 1703 | 0 | 8 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 1342 | 1553 | 14 | 9 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 80 | 18 | local | QUIZ: A tasty celebration of food |
| 78 | 28 | wellness | Inside the Perimenopause Industrial Complex |
| 73 | 27 | wellness | ‘Unparalleled’ study finds psilocybin protects against nerve damage from chemotherapy |
| 73 | 2 | wellness | What A $4,000 Membership Says About American Emergency Care |
| 72 | 21 | wellness | Closer to Zero Does Not Mean Closer to the Truth — How RoBMA Overcorrects Real Effects |
| 72 | 21 | ai-tech | 在Kubernetes中部署LiteLLM |
| 71 | 19 | wellness | Ivermectin and Hydroxychloroquine Six Years On |
| 68 | 21 | news | unhoused Archives - Ricochet Media |
| 68 | 21 | design | After the vibe-coding rush comes the debugging hangover |
| 67 | 28 | news | Metal Gear Solid 4's DLC might only be saved thanks to the uncelebrated work of fan preservationists |
| 67 | 24 | news | The power of a hand held: Treaty 6, 150 years later |
| 67 | 24 | wellness | Meta Pushes Its New AI Agent on Employees—but Eases Off on Tokenmaxxing |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 99 | 26 | news | UN sounds climate alarm as China-Taiwan row threatens to overshadow forum | friday |
| 93 | 26 | scifi | A Tribute to Yayoi Kusama | friday |
| 92 | 20 | news | Defamation charges filed against 2 Peruvian journalists in connection with their reporting | friday |
| 91 | 24 | news | Iran war live: IRGC claims attacks on 3 oil tankers and 3 US-linked ships | monday |
| 87 | 25 | homelab | How I turned my Galaxy phone into a pocket toolbox for measuring, leveling, scanning, and more | wednesday |
| 80 | 22 | news | Explore the globe in field recordings | monday |
| 76 | 20 | news | More than 1,000 dead from catastrophic Nepal-China floods | thursday |
| 69 | 29 | ai-tech | I gave Claude, Gemini, and ChatGPT the same wrong fact, and only one of them caught it | tuesday |
| 69 | 29 | wellness | Paxlovid did not help long Covid, study finds | tuesday |
| 65 | 26 | news | The living care for ancestors and wandering spirits at Malaysia's Hungry Ghost Festival | friday |
| 57 | 24 | homelab | TP-Link reveals 'world's first Wi-Fi 8 lineup' at IFA 2026 with Archer 9 Ultra router and Deco 8 Ultra mesh Wi-Fi system | friday |
| 29 | 19 | ai-tech | PSA: Gemini can adjust system settings on any Pixel running Android 17 | thursday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=25) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 96 | 14 | news | Iran says US bombed a wedding party in Sirik, killing five people | saturday |
| 96 | 10 | news | Vance privately addresses Republican Jewish Coalition during tension over Israel and antisemitism | saturday |
| 95 | 16 | news | Flash flood in Grand Canyon leaves 1 dead and several missing, National Park Service says | thursday |
| 91 | 19 | news | Why is piracy picking up off Somalia’s coast again? | monday |
| 87 | 17 | news | What to know about Germany’s drone attack accusations against Russia | friday |
| 85 | 17 | news | U.S. Strikes Iran Over Strait of Hormuz Mines, Trump Says | friday |
| 83 | 17 | news | Teen faces life over livestream of San Diego mosque attack | sunday |
| 82 | 6 | news | What to know about the evidence that led to a conviction in Tupac Shakur's killing | friday |
| 81 | 14 | news | The SweetNight CoolNest is my favorite budget cooling mattress but is this $350 alternative better for side sleepers? I put them to the test | wednesday |

---

## Recommendations

- 🌾 9 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=25) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1857 articles analysed · 2026-09-06 16:14 UTC_
