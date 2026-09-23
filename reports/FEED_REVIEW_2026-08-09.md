# Feed Scoring & Scrubbing Report

_Generated: 2026-08-09 14:01 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 11 |
| Total articles | 460 |
| Stale articles (>48h) | 336 |
| Scrub pass | ✅ ran |
| Flagged for removal | 5 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 85 | 🟡 47.8 | 16–62 | 62 | TechRadar (20) |
| 🌍 Climate & Energy | 38 | 🟡 52.0 | 27–74 | 29 | InsideEVs (5) |
| 🏛️ Architecture & Design | 30 | 🟡 49.5 | 43–62 | 23 | ArchDaily (16) |
| 🏠 Homelab & DIY | 23 | 🟡 46.4 | 18–65 | 17 | Hackaday (13) |
| 🌾 Homestead & Hobby Farm | 14 | 🔴 32.1 | 8–53 | 12 | Hobby Farms (5) |
| 🏔️ Williams Lake Local | 40 | 🟢 83.5 | 41–94 | 27 | Williams Lake Tribune (22) |
| 📰 General News | 124 | 🟡 64.2 | 59–74 | 82 | Williams Lake Tribune (14) |
| 🥾 Outdoors & Recreation | 1 | 🔴 20.0 | 20–20 | 1 | New Atlas (1) |
| 🔬 Science | 41 | 🟡 54.2 | 43–62 | 35 | ScienceDaily (24) |
| 🚀 Sci-Fi & Culture | 10 | 🔴 16.0 | 2–46 | 6 | Reactor Magazine (2) |
| 🌿 Health & Wellness | 54 | 🟡 58.7 | 10–76 | 42 | ScienceDaily (8) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 85 (85 scored)
- **Score**: avg 47.8 | min 16 | max 62
- **Stale** (>48h): 62
- **Avg age**: 72.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        1
  20–29   │                        0
  30–39   │ ██                     6
  40–49   │ ████████████████████  42
  50–59   │ ████████████████      34
  60–69   │                        2
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| TechRadar | 20 | 24% |
| WIRED | 15 | 18% |
| TechCrunch | 7 | 8% |
| Neowin | 5 | 6% |
| Tom's Hardware | 5 | 6% |
| The Verge | 3 | 4% |
| ZDNet | 3 | 4% |
| Business Insider | 3 | 4% |

**Low-score articles (≤30):**

- `[ 16]` [Android Authority] ChatGPT could soon let you easily create and use custom WhatsApp stickers  
  <https://www.androidauthority.com/chatgpt-whatsapp-stickers-apk-teardown-3695710/>

### 🟡 🌍 Climate & Energy

- **Articles**: 38 (38 scored)
- **Score**: avg 52.0 | min 27 | max 74
- **Stale** (>48h): 29
- **Avg age**: 73.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ █                      1
  30–39   │ ████                   4
  40–49   │ ██████████             9
  50–59   │ ████████████████████  18
  60–69   │ █████                  5
  70–79   │ █                      1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| InsideEVs | 5 | 13% |
| ScienceDaily | 3 | 8% |
| Mother Jones | 2 | 5% |
| WIRED | 2 | 5% |
| The Narwhal | 2 | 5% |
| ScienceAlert | 2 | 5% |
| Wildfire Today | 2 | 5% |
| The Northern Miner | 2 | 5% |

**Low-score articles (≤30):**

- `[ 27]` 🔓 Hard as It Is to Say, God Loves Donald Trump | The Walrus  
  <https://thewalrus.ca/hard-as-it-is-to-say-god-loves-donald-trump/>

### 🟡 🏛️ Architecture & Design

- **Articles**: 30 (30 scored)
- **Score**: avg 49.5 | min 43 | max 62
- **Stale** (>48h): 23
- **Avg age**: 74.1h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │ ████████████████████  18
  50–59   │ ███████████           10
  60–69   │ ██                     2
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ArchDaily | 16 | 53% ⚠️ |
| Dezeen | 6 | 20% |
| Kagi Small Web | 3 | 10% |
| Canadian Architect | 2 | 7% |
| Homebuilding & Renovating | 1 | 3% |
| WIRED | 1 | 3% |
| Architizer | 1 | 3% |

### 🟡 🏠 Homelab & DIY

- **Articles**: 23 (23 scored)
- **Score**: avg 46.4 | min 18 | max 65
- **Stale** (>48h): 17
- **Avg age**: 75.8h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      1
  20–29   │ █                      1
  30–39   │ █                      1
  40–49   │ ████████████████████  11
  50–59   │ ██████████████         8
  60–69   │ █                      1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hackaday | 13 | 57% ⚠️ |
| Tom's Hardware | 2 | 9% |
| XDA Developers | 2 | 9% |
| MakeUseOf | 1 | 4% |
| Popular Woodworking | 1 | 4% |
| Neowin | 1 | 4% |
| How-To Geek | 1 | 4% |
| TechRadar | 1 | 4% |

**Low-score articles (≤30):**

- `[ 21]` 🔓 [Popular Woodworking] Best Foot Forward  
  <https://www.popularwoodworking.com/editors-blog/best-foot-forward/>
- `[ 18]` [MacRumors] CarPlay is Coming to Pontoon Boats  
  <https://www.macrumors.com/2026/08/04/carplay-is-coming-to-pontoon-boats/>

### 🔴 🌾 Homestead & Hobby Farm

- **Articles**: 14 (14 scored)
- **Score**: avg 32.1 | min 8 | max 53
- **Stale** (>48h): 12
- **Avg age**: 85.0h

**Score distribution:**
```
  0–9     │ ██████████             2
  10–19   │ ███████████████        3
  20–29   │ ██████████             2
  30–39   │                        0
  40–49   │ ███████████████        3
  50–59   │ ████████████████████   4
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hobby Farms | 5 | 36% |
| Small Farm Canada | 3 | 21% |
| Kagi Small Web | 2 | 14% |
| Toms Guide | 1 | 7% |
| Business Insider | 1 | 7% |
| Boing Boing | 1 | 7% |
| Pluralistic | 1 | 7% |

**Low-score articles (≤30):**

- `[  8]` [Kagi Small Web] I have plany of time &hellip;  
  <https://ahedderick.tumblr.com/post/824386537219391488>
- `[  8]` [Kagi Small Web] BOOM  
  <https://ahedderick.tumblr.com/post/824385239490150400>
- `[ 15]` [Business Insider] Alex Gibney's Elon doc isn't even out but Musk is already calling it a 'hit job'  
  <https://www.businessinsider.com/elon-musk-documentary-alex-gibney-hit-job-2026-8>
- `[ 18]` [Hobby Farms] Dutch Bantam: Breed Guide, Eggs, Temperament & Care  
  <https://www.hobbyfarms.com/dutch-bantam/>
- `[ 22]` [Hobby Farms] Chicken Water: How to Keep Your Flock Hydrated  
  <https://www.hobbyfarms.com/make-sure-your-chickens-always-have-plenty-of-water/>
- `[ 12]` [Boing Boing] The world's largest goat tower was built by accident  
  <https://boingboing.net/2026/08/04/goat-tower-illinois.html>
- `[ 22]` Pluralistic: Post-American compute for a post-American Internet (04 Aug 2026)  
  <https://pluralistic.net/2026/08/04/technology-freedom-cooperative/>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 40 (40 scored)
- **Score**: avg 83.5 | min 41 | max 94
- **Stale** (>48h): 27
- **Avg age**: 63.7h
- **Local-flagged**: 40

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │ ██                     2
  50–59   │                        0
  60–69   │                        0
  70–79   │ ███████                7
  80–89   │ ████████████████████  18
  90–100  │ ██████████████        13
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 22 | 55% ⚠️ |
| My Cariboo Now | 12 | 30% |
| 100 Mile Free Press | 2 | 5% |
| Tŝilhqot’in National Government | 1 | 2% |
| The Northern Miner | 1 | 2% |
| BC Gov News | 1 | 2% |
| CFJC Today Kamloops | 1 | 2% |

### 🟡 📰 General News

- **Articles**: 124 (124 scored)
- **Score**: avg 64.2 | min 59 | max 74
- **Stale** (>48h): 82
- **Avg age**: 68.2h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │                        1
  60–69   │ ████████████████████ 118
  70–79   │                        5
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 14 | 11% |
| TechRadar | 14 | 11% |
| NYT Top Stories | 13 | 10% |
| Engadget | 8 | 6% |
| Hackaday | 7 | 6% |
| The Narwhal | 6 | 5% |
| The Tyee | 6 | 5% |
| WIRED | 5 | 4% |

### 🔴 🥾 Outdoors & Recreation

- **Articles**: 1 (1 scored)
- **Score**: avg 20.0 | min 20 | max 20
- **Stale** (>48h): 1
- **Avg age**: 49.9h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ████████████████████   1
  30–39   │                        0
  40–49   │                        0
  50–59   │                        0
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| New Atlas | 1 | 100% |

**Low-score articles (≤30):**

- `[ 20]` [New Atlas] Full-squish trekker built to Roam city and beyond  
  <https://newatlas.com/bicycles/mapfour-roam-trekking-ebike/>

### 🟡 🔬 Science

- **Articles**: 41 (41 scored)
- **Score**: avg 54.2 | min 43 | max 62
- **Stale** (>48h): 35
- **Avg age**: 77.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │ ██                     4
  50–59   │ ████████████████████  31
  60–69   │ ███                    6
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 24 | 59% ⚠️ |
| ScienceAlert | 6 | 15% |
| Nautilus | 3 | 7% |
| WIRED | 2 | 5% |
| Quanta Magazine | 2 | 5% |
| Scientific American | 1 | 2% |
| NYT Top Stories | 1 | 2% |
| STAT News | 1 | 2% |

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 10 (10 scored)
- **Score**: avg 16.0 | min 2 | max 46
- **Stale** (>48h): 6
- **Avg age**: 68.6h

**Score distribution:**
```
  0–9     │ ███████████████        3
  10–19   │ ████████████████████   4
  20–29   │ ██████████             2
  30–39   │                        0
  40–49   │ █████                  1
  50–59   │                        0
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Reactor Magazine | 2 | 20% |
| Neowin | 1 | 10% |
| TechRadar | 1 | 10% |
| Gizmodo | 1 | 10% |
| Wikipedia  - Recent changes [en] | 1 | 10% |
| Kottke.org | 1 | 10% |
| Open Culture | 1 | 10% |
| Kagi Small Web | 1 | 10% |

**Low-score articles (≤30):**

- `[  5]` [Neowin] Weekend PC Game Deals: Witchfire, Avowed, Ninja Gaiden, Ready or Not, and more  
  <https://www.neowin.net/news/weekend-pc-game-deals-witchfire-avowed-ninja-gaiden-ready-or-not-and-more/?utm_source=rss>
- `[ 20]` [TechRadar] I asked ChatGPT, Claude, Gemini and Grok which sci-fi AI they're most like — and their answers were surprisingly different  
  <https://www.techradar.com/ai-platforms-assistants/chatgpt/i-asked-chatgpt-claude-gemini-and-grok-which-sci-fi-ai-theyre-most-like-and-their-answers-were-surprisingly-different>
- `[ 18]` [Gizmodo] A Sweet but Scary Monster Faces a Cruel World in This Sci-Fi Story  
  <https://gizmodo.com/a-sweet-but-scary-monster-faces-a-cruel-world-in-this-sci-fi-story-2000793055>
- `[  2]` [Wikipedia  - Recent changes [en]] Planet of the Apes (TV series)  
  <https://en.wikipedia.org/w/index.php?title=Planet_of_the_Apes_(TV_series)&diff=1368288987&oldid=1345955888>
- `[ 24]` [Kottke.org] Fun little review by Marcin Wichary of a 1984 flying...  
  <https://kottke.org/26/08/0049463-fun-little-review-by-marc>
- `[ 15]` [Kagi Small Web] Book Review: Seafire  
  <https://live.deanebarker.net/library/titles/seafire/>
- `[ 12]` [Reactor Magazine] Here Are the 2026 World Fantasy Award Finalists  
  <https://reactormag.com/here-are-the-2026-world-fantasy-award-finalists/>
- `[ 12]` [Reactor Magazine] Space Pirates and Action-Packed Pulp: Starwolf by Edmond Hamilton  
  <https://reactormag.com/space-pirates-and-action-packed-pulp-starwolf-by-edmond-hamilton/>
- `[  6]` [Business Insider] My family usually books budget-friendly accommodations, but we spent $500 a night on an English estate. It was worth every penny.  
  <https://www.businessinsider.com/splurge-english-manor-house-estate-uk-see-inside-severn-end-2026-8>

### 🟡 🌿 Health & Wellness

- **Articles**: 54 (54 scored)
- **Score**: avg 58.7 | min 10 | max 76
- **Stale** (>48h): 42
- **Avg age**: 73.1h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        1
  20–29   │                        1
  30–39   │                        1
  40–49   │                        1
  50–59   │ ████████████████████  25
  60–69   │ ██████████████        18
  70–79   │ █████                  7
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 8 | 15% |
| NPR Health News | 7 | 13% |
| NYT Business | 3 | 6% |
| Outside Online | 3 | 6% |
| STAT News | 3 | 6% |
| globalnews.ca | 2 | 4% |
| ScienceAlert | 2 | 4% |
| Western Producer | 2 | 4% |

**Low-score articles (≤30):**

- `[ 10]` [STAT News] STAT+: Federal regulators invite industry, researchers, and lobbyists to closed-door meetings on clinical AI  
  <https://www.statnews.com/2026/08/05/federal-regulators-invite-industry-closed-door-meetings-clinical-ai/?utm_campaign=rss>
- `[ 21]` [The Guardian Global Development] Peruvian cardinal hails $150m lead poisoning settlement for 1,300 people as a ‘historic milestone’  
  <https://www.theguardian.com/global-development/2026/aug/05/peruvian-cardinal-historic-milestone-150m-lead-poisoning-settlement-1300-children>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (5)

- **[🤖 AI/ML & Tech]** `score 16` — ChatGPT could soon let you easily create and use custom WhatsApp stickers  
  Issue: `clickbait`  
  <https://www.androidauthority.com/chatgpt-whatsapp-stickers-apk-teardown-3695710/>
- **[🌍 Climate & Energy]** `score 27` — Hard as It Is to Say, God Loves Donald Trump | The Walrus  
  Issue: `clickbait`  
  <https://thewalrus.ca/hard-as-it-is-to-say-god-loves-donald-trump/>
- **[🏠 Homelab & DIY]** `score 21` — Best Foot Forward | Popular Woodworking  
  Issue: `clickbait`  
  <https://www.popularwoodworking.com/editors-blog/best-foot-forward/>
- **[🌾 Homestead & Hobby Farm]** `score 15` — Alex Gibney's Elon doc isn't even out but Musk is already calling it a 'hit job'  
  Issue: `celebrity`  
  <https://www.businessinsider.com/elon-musk-documentary-alex-gibney-hit-job-2026-8>
- **[🚀 Sci-Fi & Culture]** `score 24` — Fun little review by Marcin Wichary of a 1984 flying...  
  Issue: `clickbait`  
  <https://kottke.org/26/08/0049463-fun-little-review-by-marc>

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 62 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 29 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏛️ Architecture & Design** has 23 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏛️ Architecture & Design** is dominated by **ArchDaily** (16 articles, 53%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **🏠 Homelab & DIY** has 17 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏠 Homelab & DIY** is dominated by **Hackaday** (13 articles, 57%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- ⚠️ **🌾 Homestead & Hobby Farm** has a low average score (32.1) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🌾 Homestead & Hobby Farm** has 12 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 27 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏔️ Williams Lake Local** is dominated by **Williams Lake Tribune** (22 articles, 55%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **📰 General News** has 82 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 35 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🔬 Science** is dominated by **ScienceDaily** (24 articles, 59%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (16.0) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🚀 Sci-Fi & Culture** has 6 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌿 Health & Wellness** has 42 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 5 article(s) should be removed (`clickbait` ×4, `celebrity` ×1) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 11 feeds · 460 articles · 2026-08-09 14:01 UTC_
