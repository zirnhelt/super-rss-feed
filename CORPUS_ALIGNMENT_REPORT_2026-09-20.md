# Cache Corpus Alignment Report

_Generated: 2026-09-20 16:58 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Articles analysed | 1397 |
| Articles missing theme-score data (skipped) | 127 |
| Direct-qualify (upstream score gates them in for their best theme) | 1256 |
| Rescue-dependent (good theme fit, upstream below day minimum) | 25 |
| Stranded (good theme fit, upstream below per-category quality floor — never bankable) | 46 |
| Filler (upstream ≥ 50 but best theme fit < 30 for ALL 7 themes) | 147 (11% of corpus) |


**Interpretation:** *Filler* articles clear a quality bar on upstream interest score alone and so are eligible to be picked for whichever day's bucket they happen to score (marginally) highest on — even though that score reflects a poor fit for every theme. *Stranded* and *rescue-dependent* articles are the mirror problem: content that fits a theme well but is filtered out (or only conditionally rescued) because the upstream score underrates it.


**Content type breakdown** (fluff/sponsored are hard-dropped before articles enter this cache; their absence here is expected):

| Content type | Count |
|-------------|-------|
| None | 961 |
| feature | 173 |
| analysis | 171 |
| breaking | 144 |
| news | 33 |
| opinion | 18 |
| fluff | 14 |
| recap | 4 |
| investigation | 2 |
| how-to | 2 |
| wire | 2 |


## Per-Category: Upstream Score vs. Best Theme Fit

| Category | n | Avg upstream score | Avg best-theme-fit | Δ (theme − upstream) | Direct | Rescue | Stranded | Filler |
|----------|---|---------------------|---------------------|----------------------|--------|--------|----------|--------|
| news | 957 | 56.0 | 66.4 | +10.3 | 851 | 18 | 46 | 104 |
| ai-tech | 127 | 49.4 | 51.2 | +1.9 | 113 | 2 | 0 | 19 |
| wellness | 85 | 56.8 | 60.2 | +3.4 | 78 | 2 | 0 | 6 |
| local | 64 | 79.1 | 91.9 | +12.8 | 64 | 0 | 0 | 0 |
| science | 55 | 50.8 | 62.0 | +11.2 | 51 | 0 | 0 | 8 |
| homelab | 46 | 49.7 | 82.8 | +33.2 | 46 | 0 | 0 | 0 |
| design | 30 | 43.2 | 39.5 | -3.7 | 20 | 3 | 0 | 8 |
| climate | 27 | 54.3 | 78.3 | +24.0 | 27 | 0 | 0 | 2 |
| outdoors | 4 | 48.8 | 54.0 | +5.2 | 4 | 0 | 0 | 0 |
| scifi | 1 | 53.0 | 30.0 | -23.0 | 1 | 0 | 0 | 0 |
| homestead | 1 | 54.0 | 68.0 | +14.0 | 1 | 0 | 0 | 0 |

A large negative Δ means the upstream interest score runs well ahead of how well that category's articles actually fit any of the 7 themes — a signal that the upstream score for that category may be inflated relative to its real bucket value (e.g. via the local-priority override, or a permissive `news` baseline).


## Theme Coverage Across the Corpus

Distribution of each theme's fit score across **all** 1397 corpus articles (not just that day's primary categories — theme scoring is run against the whole pool):

| Day | Theme | Avg fit | Max fit | ≥ holdover | ≥ min_score |
|-----|-------|---------|---------|------------|-------------|
| Monday | Arts, Culture & Digital Storytelling | 48.4 | 100 | 1160 | 970 |
| Tuesday | Working Lands & Industry | 44.6 | 100 | 941 | 941 |
| Wednesday | Repair Culture & Practical Tech | 42.7 | 100 | 1091 | 733 |
| Thursday | Indigenous Lands & Innovation | 46.6 | 100 | 1101 | 946 |
| Friday | Wild Spaces & Outdoor Life | 48.9 | 100 | 1234 | 1003 |
| Saturday | Cariboo Local Affairs | 48.9 | 100 | 1292 | 1140 |
| Sunday | Science, Wonder & the Natural World | 49.1 | 100 | 1194 | 990 |

## Per-Theme-Day Candidacy

For each day's theme, counts of corpus articles whose **theme-fit score** clears that day's `holdover_threshold`, broken down by how the upstream score would treat them.

| Day | Theme | min_score | holdover | Theme-qualified | Direct (upstream OK) | Rescue-dependent | Unreachable (upstream < min_claude_score) |
|-----|-------|-----------|----------|-----------------|------------------------|------------------|----------------------------------------------|
| Monday | Arts, Culture & Digital Storytelling | 28 | 15 | 970 | 1082 | 32 | 46 |
| Tuesday | Working Lands & Industry | 30 | 15 | 941 | 865 | 33 | 43 |
| Wednesday | Repair Culture & Practical Tech | 28 | 12 | 733 | 1020 | 28 | 43 |
| Thursday | Indigenous Lands & Innovation | 25 | 12 | 946 | 1039 | 17 | 45 |
| Friday | Wild Spaces & Outdoor Life | 28 | 12 | 1003 | 1153 | 34 | 47 |
| Saturday | Cariboo Local Affairs | 18 | 8 | 1140 | 1251 | 0 | 41 |
| Sunday | Science, Wonder & the Natural World | 28 | 15 | 990 | 1114 | 34 | 46 |

'Unreachable' articles fit a theme well but score below `min_claude_score` overall, so the rescue mechanism in `route_articles_to_best_themes` / `generate_podcast_feed` never sees them — they're filtered out before theme routing runs at all.


---

## Filler Examples (clears upstream gate, fits no theme)

Top 12 by upstream score — these are the articles most likely to be picked for a bucket on the strength of upstream score alone, despite scoring below 30 on every one of the 7 daily themes:

| Upstream | Best theme fit | Category | Title |
|---|---|---|---|
| 80 | 18 | science | The Next Gene-Editing Technology May Also Be the Oldest |
| 73 | 5 | design | ‘The fixes are architectural, not bigger pipes’: OpenSSL President on what businesses can expect and how to prepare for a post-quantum internet |
| 71 | 6 | news | Those Viral Bodega Peptides Aren’t Actually Peptides |
| 70 | 24 | news | Trump Wanted Canada as the 51st State. He Ended Up Pushing It Toward the European Union. |
| 70 | 22 | news | If the AI Industry Followed Its Own Research, It Might Have Paused Already |
| 70 | 3 | news | No, Alberta Does Not ‘Subsidize’ the Rest of Canada |
| 68 | 24 | news | Control Resonant PC performance tested: 28 GPUs take us back to the Oldest House and a warped Manhattan cityscape |
| 68 | 22 | wellness | Signs of safety: An investigation of how OHS professionals interpret injury metrics |
| 68 | 8 | news | Lab-Grown Human Brain Tissue Restores Brain Circuitry in Living Mice |
| 67 | 24 | ai-tech | AI watermarking could make LLM guardrail adherence unpredictable — and that could be a big problem for the EU AI Act |
| 67 | 15 | news | Chipotle Is Working With Palantir to Track Food Safety Risks |
| 67 | 13 | news | At DraftKings, AI Targets the Gamblers Likeliest to Lose |

## Rescue-Dependent Examples (good fit, conditional inclusion)

Top 12 by theme-fit score — these only make it into a bucket via the holdover-rescue path, not because the upstream score recognised their relevance:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 100 | 24 | news | Abbott agrees to settlement over closure of largest baby formula plant in the U.S. | monday |
| 98 | 22 | news | In Rare Move, Democrats Try to Block a Sale of Bombs to Israel | friday |
| 96 | 20 | news | UN findings show US strikes on Minab could be war crimes | sunday |
| 95 | 21 | news | Researchers Say They’ve Found the Truth About Thomas Jefferson | sunday |
| 93 | 26 | news | Google Authenticator, Microsoft Authenticator, and Authy are out, because this open-source app replaced them all | friday |
| 92 | 25 | news | Journalist Tuğba Tekerek arrested in Turkey for ‘obscenity’ during LGBTQ+ crackdown | sunday |
| 92 | 21 | news | How the Supreme Court Seized Power to Rule Over the Rest of Us | friday |
| 91 | 27 | news | Poorest countries hit hardest by UK aid cuts under Keir Starmer government, new figures reveal | sunday |
| 90 | 27 | wellness | DR Congo begins Ebola vaccination trials for frontline health workers | friday |
| 88 | 26 | news | Poland lost $230 million in cryptocurrency trying to buy Venezuelan oil in 2023 — USB drives with crypto handed directly to scammers | sunday |
| 86 | 24 | ai-tech | You can use Gemini to help you organize your files on Google Drive | monday |
| 83 | 26 | ai-tech | ChatGPT-6 Astra cracks 108-year-old unsolved WWI German code for the first time — radio message sharing enemy movement intelligence had evaded decoding, 1918 Crimean fleet warning verified against HMS Canterbury logs | sunday |

## Stranded Examples (good fit, never bankable)

Articles scoring ≥ a day's holdover threshold on theme fit, but below their category's quality floor (`min_score_by_category`, falling back to `min_claude_score`=25) upstream — these are filtered out before theme routing ever considers them:

| Best theme fit | Upstream | Category | Title | Best-fit day |
|---|---|---|---|---|
| 100 | 16 | news | Displaced Syrians dig through hills of garbage to make a living | sunday |
| 100 | 12 | news | Panic on board Iranian plane as violent shaking rips cabin apart | monday |
| 100 | 12 | news | Argentina steps up legal campaign against Falkland Islands oil firms | saturday |
| 100 | 10 | news | Protests erupt across Syria over sharp fuel price hikes | sunday |
| 100 | 10 | news | Swedes vote in election that could see far-right in government | friday |
| 100 | 7 | news | Building damaged by strikes collapses in Gaza, killing 21 as perilous living conditions persist | friday |
| 99 | 16 | news | Trump signs sweeping Russia sanctions over Ukraine war | thursday |
| 99 | 14 | news | US Supreme Court rejects Trump mail ballot restrictions ahead of midterms | friday |
| 99 | 10 | news | Israeli quadcopter terrorises homes in Gaza City | friday |
| 99 | 8 | news | Peruvian journalist shot dead after threatening to expose police | friday |
| 99 | 7 | news | Yemen’s Houthis advance on government strongholds of Marib, Taiz | friday |
| 98 | 16 | news | How to force quit on your Windows PC | friday |

---

## Recommendations

- 🌾 46 article(s) fit a theme well but score below their per-category quality floor (`min_score_by_category` in `config/limits.json`, falling back to `min_claude_score`=25) and are stranded — see the Stranded Examples table. Consider lowering or adding a floor for those categories so they survive into the podcast pool.

---

_Report generated by `corpus_alignment_report.py` · 1397 articles analysed · 2026-09-20 16:58 UTC_
