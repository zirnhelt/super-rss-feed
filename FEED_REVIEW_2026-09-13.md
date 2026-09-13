# Feed Scoring & Scrubbing Report

_Generated: 2026-09-13 17:03 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 11 |
| Total articles | 484 |
| Stale articles (>48h) | 367 |
| Scrub pass | ✅ ran |
| Flagged for removal | 12 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 88 | 🟡 46.9 | 18–73 | 63 | TechRadar (9) |
| 🌍 Climate & Energy | 37 | 🟡 47.7 | 22–65 | 29 | InsideEVs (6) |
| 🏛️ Architecture & Design | 28 | 🟡 49.4 | 31–68 | 22 | ArchDaily (20) |
| 🏠 Homelab & DIY | 40 | 🟡 49.1 | 18–62 | 27 | XDA Developers (10) |
| 🌾 Homestead & Hobby Farm | 9 | 🟡 52.3 | 34–65 | 8 | Hobby Farms (4) |
| 🏔️ Williams Lake Local | 41 | 🟢 78.4 | 53–93 | 28 | Williams Lake Tribune (19) |
| 📰 General News | 122 | 🟡 68.1 | 63–75 | 97 | NYT Business (11) |
| 🥾 Outdoors & Recreation | 10 | 🔴 31.9 | 20–48 | 8 | New Atlas (4) |
| 🔬 Science | 44 | 🟡 47.7 | 27–57 | 31 | ScienceDaily (12) |
| 🚀 Sci-Fi & Culture | 7 | 🔴 21.7 | 2–44 | 5 | The Atlantic Culture (1) |
| 🌿 Health & Wellness | 58 | 🟡 58.1 | 10–73 | 49 | Fast Company (9) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 88 (88 scored)
- **Score**: avg 46.9 | min 18 | max 73
- **Stale** (>48h): 63
- **Avg age**: 72.5h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        1
  20–29   │                        1
  30–39   │ ████                   9
  40–49   │ ████████████████████  45
  50–59   │ ████████████          28
  60–69   │ █                      3
  70–79   │                        1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| TechRadar | 9 | 10% |
| Kagi Small Web | 7 | 8% |
| Tom's Hardware | 6 | 7% |
| Business Insider | 6 | 7% |
| Forbes Innovation | 4 | 5% |
| Engadget | 4 | 5% |
| The Verge | 4 | 5% |
| WIRED | 4 | 5% |

**Low-score articles (≤30):**

- `[ 18]` [Kagi Small Web] Enrollment  
  <https://johnmaconline.com/enrollment/#utm_source=rss&utm_medium=rss#utm_source=rss&utm_medium=rss&utm_campaign=enrollment>
- `[ 29]` [Gizmodo] OpenAI Is Beefing With Mathematicians, Will No Longer Sponsor Caltech ‘Mathathon’  
  <https://news.google.com/rss/articles/CBMirgFBVV95cUxOakNrOFEzaXp5NVdQRFlaSmZ3cHJxN2ZxdlpVT3Vaci1pdkNIdU84emcwWmpiTTNZWDJ6MWRNSm4xLTB5ZGZtdEtBaVRXZnhpMjZQUFFVV0YxR0tRbUdvRmFCU0dIYWMwaHlJbG5QODBiQU4za01wd3F1OHI1VXQ0SXBtdWpnT1lLcllRTHptWXpvT184NUkyLTA0WGRGRlFpNkZYdkJzQ0dxYUExNEE?oc=5>

### 🟡 🌍 Climate & Energy

- **Articles**: 37 (37 scored)
- **Score**: avg 47.7 | min 22 | max 65
- **Stale** (>48h): 29
- **Avg age**: 71.5h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ███                    2
  30–39   │ ███████                5
  40–49   │ ████████████████████  13
  50–59   │ ██████████████████    12
  60–69   │ ███████                5
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| InsideEVs | 6 | 16% |
| New Atlas | 3 | 8% |
| Engadget | 3 | 8% |
| Mother Jones | 3 | 8% |
| NYT Business | 3 | 8% |
| TechRadar | 2 | 5% |
| Gizmodo | 2 | 5% |
| Kagi Small Web | 1 | 3% |

**Low-score articles (≤30):**

- `[ 22]` [Kagi Small Web] You Get What You Tolerate  
  <https://drhurd.com/2026/09/12/you-get-what-you-tolerate/>
- `[ 22]` [Business Insider] We once had to melt snow just to flush our toilet. It was one of several unexpected challenges of living off-grid.  
  <https://www.businessinsider.com/lived-off-the-grid-biggest-challenges-inconveniences-surprises-2026-9>

### 🟡 🏛️ Architecture & Design

- **Articles**: 28 (28 scored)
- **Score**: avg 49.4 | min 31 | max 68
- **Stale** (>48h): 22
- **Avg age**: 76.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ ██████                 4
  40–49   │ ███████████████        9
  50–59   │ ████████████████████  12
  60–69   │ █████                  3
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ArchDaily | 20 | 71% ⚠️ |
| Dezeen | 3 | 11% |
| Architizer | 2 | 7% |
| Dwell | 1 | 4% |
| iFixit | 1 | 4% |
| Open Culture | 1 | 4% |

### 🟡 🏠 Homelab & DIY

- **Articles**: 40 (40 scored)
- **Score**: avg 49.1 | min 18 | max 62
- **Stale** (>48h): 27
- **Avg age**: 71.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      1
  20–29   │ ██                     2
  30–39   │ ███                    3
  40–49   │ ███████████           11
  50–59   │ ████████████████████  20
  60–69   │ ███                    3
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| XDA Developers | 10 | 25% |
| Hackaday | 6 | 15% |
| Hackster News | 6 | 15% |
| Popular Woodworking | 4 | 10% |
| Kagi Small Web | 2 | 5% |
| Adafruit Blog | 2 | 5% |
| Android Police | 1 | 2% |
| Make Magazine | 1 | 2% |

**Low-score articles (≤30):**

- `[ 30]` [Make Magazine] Makers Of Orange County Unite This Weekend!  
  <https://makezine.com/article/maker-news/makers-of-orange-county-unite-this-weekend/>
- `[ 25]` 🔓 [Popular Woodworking] Waiting For The Future  
  <https://www.popularwoodworking.com/editors-blog/waiting-for-the-future/>
- `[ 23]` 🔓 [Popular Woodworking] Dutch Tool Chest  
  <https://www.popularwoodworking.com/projects/dutch-tool-chest/>
- `[ 18]` [Wildfire Today] Support grows for 2026 UK wildfire conference  
  <https://wildfiretoday.com/support-grows-for-2026-uk-wildfire-conference/>

### 🟡 🌾 Homestead & Hobby Farm

- **Articles**: 9 (9 scored)
- **Score**: avg 52.3 | min 34 | max 65
- **Stale** (>48h): 8
- **Avg age**: 75.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ ██                     1
  40–49   │                        0
  50–59   │ ████████████████████   7
  60–69   │ ██                     1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hobby Farms | 4 | 44% ⚠️ |
| Country Life | 1 | 11% |
| Small Wooden House Plans | Micro Cabin Plans | Garden Shed Plans | Cottage Blueprints | 1 | 11% |
| Kagi Small Web | 1 | 11% |
| IndigiNews | 1 | 11% |
| New Atlas | 1 | 11% |

### 🟢 🏔️ Williams Lake Local

- **Articles**: 41 (41 scored)
- **Score**: avg 78.4 | min 53 | max 93
- **Stale** (>48h): 28
- **Avg age**: 72.4h
- **Local-flagged**: 41

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │ █                      1
  60–69   │ ████                   4
  70–79   │ ███████████████       15
  80–89   │ ████████████████████  19
  90–100  │ ██                     2
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 19 | 46% ⚠️ |
| My Cariboo Now | 16 | 39% |
| 100 Mile Free Press | 2 | 5% |
| Quesnel Cariboo Observer | 1 | 2% |
| Tŝilhqot’in National Government | 1 | 2% |
| Regional News Archives - Williams Lake Tribune | 1 | 2% |
| BC Gov News | 1 | 2% |

### 🟡 📰 General News

- **Articles**: 122 (122 scored)
- **Score**: avg 68.1 | min 63 | max 75
- **Stale** (>48h): 97
- **Avg age**: 77.2h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │                        0
  60–69   │ ████████████████████  80
  70–79   │ ██████████            42
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| NYT Business | 11 | 9% |
| WIRED | 10 | 8% |
| NYT Top Stories | 9 | 7% |
| The Atlantic | 9 | 7% |
| TechRadar | 7 | 6% |
| Mother Jones | 7 | 6% |
| Williams Lake Tribune | 7 | 6% |
| ScienceDaily | 6 | 5% |

### 🔴 🥾 Outdoors & Recreation

- **Articles**: 10 (10 scored)
- **Score**: avg 31.9 | min 20 | max 48
- **Stale** (>48h): 8
- **Avg age**: 68.9h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ████████████████████   5
  30–39   │ ████████               2
  40–49   │ ████████████           3
  50–59   │                        0
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| New Atlas | 4 | 40% |
| Outside Online | 3 | 30% |
| TechRadar | 1 | 10% |
| Kagi Small Web | 1 | 10% |
| Popular Mechanics | 1 | 10% |

**Low-score articles (≤30):**

- `[ 22]` [New Atlas] Modular folding camp grill is whatever size you need it to be  
  <https://newatlas.com/outdoor-cooking/grilti-ever-modular-camp-grill/>
- `[ 25]` TechRadar's new privacy newsletter is out — read Leave No Trace issue #2 now  
  <https://www.techradar.com/vpn/vpn-privacy-security/techradars-new-privacy-newsletter-is-out-read-leave-no-trace-issue-2-now>
- `[ 27]` 🔓 [Outside Online] The Best Outdoor Adventures in Chattanooga, Tennessee  
  <https://www.outsideonline.com/outdoor-adventure/water-activities/the-best-outdoor-adventures-in-chattanooga-tennessee/>
- `[ 20]` [New Atlas] Freezable titanium plate keeps your cooler chilled longer than ice packs  
  <https://newatlas.com/outdoor-gear/frost-titan-core-titanium-plate-cooling-camping/>
- `[ 22]` 🔓 [Popular Mechanics] Scientists Reversed a Law of Physics by Scrambling Cause and Effect  
  <https://www.popularmechanics.com/science/a73574084/heat-flows-backward/>

### 🟡 🔬 Science

- **Articles**: 44 (44 scored)
- **Score**: avg 47.7 | min 27 | max 57
- **Stale** (>48h): 31
- **Avg age**: 78.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        1
  30–39   │ █                      2
  40–49   │ ████████████████████  22
  50–59   │ █████████████████     19
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 12 | 27% |
| ScienceAlert | 8 | 18% |
| Scientific American | 5 | 11% |
| Popular Mechanics | 4 | 9% |
| Quanta Magazine | 3 | 7% |
| TechRadar | 2 | 5% |
| WIRED | 2 | 5% |
| Nautilus | 1 | 2% |

**Low-score articles (≤30):**

- `[ 27]` 🔓 [NYT Well] The Good List: 6 Things to Bring Joy to Your Day  
  <https://www.nytimes.com/2026/09/09/briefing/09-the-good-list-perfect-september.html>

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 7 (7 scored)
- **Score**: avg 21.7 | min 2 | max 44
- **Stale** (>48h): 5
- **Avg age**: 62.2h

**Score distribution:**
```
  0–9     │ █████████████          2
  10–19   │                        0
  20–29   │ ████████████████████   3
  30–39   │ ██████                 1
  40–49   │ ██████                 1
  50–59   │                        0
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| The Atlantic Culture | 1 | 14% |
| Toms Guide | 1 | 14% |
| Kagi Small Web | 1 | 14% |
| Wikipedia  - Recent changes [en] | 1 | 14% |
| Adafruit Blog | 1 | 14% |
| Reactor Magazine | 1 | 14% |
| Nautilus | 1 | 14% |

**Low-score articles (≤30):**

- `[  8]` [Toms Guide] Think you know the Alien movies? This quiz will put your knowledge of the sci-fi franchise to the ultimate test  
  <https://www.tomsguide.com/entertainment/movies/think-you-know-the-alien-movies-this-quiz-will-put-your-knowledge-of-the-sci-fi-franchise-to-the-ultimate-test>
- `[ 20]` [Kagi Small Web] Five Leagues From the Borderlands: Introducing… Jeff’s Stag Party  
  <https://bedroombattlefields.com/five-leagues-from-the-borderlands-introducing-jeffs-stag-party/>
- `[  2]` [Wikipedia  - Recent changes [en]] Ada Palmer  
  <https://en.wikipedia.org/w/index.php?title=Ada_Palmer&diff=1374301287&oldid=1373690885>
- `[ 22]` [Adafruit Blog] Hexagon Wall Panels – Modular Shallow + Deep with Snug Pegs #3DThursday #3DPrinting  
  <https://blog.adafruit.com/2026/09/10/hexagon-wall-panels-modular-shallow-deep-with-snug-pegs-3dthursday-3dprinting-2/>
- `[ 22]` [Reactor Magazine] Pirate Queens, Tarot Magic, and Fantasy RomComs: Romantasy Report for September and October 2026  
  <https://reactormag.com/romantasy-report-for-september-and-october-2026/>

### 🟡 🌿 Health & Wellness

- **Articles**: 58 (58 scored)
- **Score**: avg 58.1 | min 10 | max 73
- **Stale** (>48h): 49
- **Avg age**: 80.9h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██                     3
  20–29   │                        0
  30–39   │ █                      2
  40–49   │ █                      2
  50–59   │ ██████████            15
  60–69   │ ████████████████████  29
  70–79   │ ████                   7
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Fast Company | 9 | 16% |
| ScienceDaily | 5 | 9% |
| KFF Health News | 4 | 7% |
| STAT News | 4 | 7% |
| Scientific American | 2 | 3% |
| NPR Health News | 2 | 3% |
| Nautilus | 2 | 3% |
| Outside Online | 2 | 3% |

**Low-score articles (≤30):**

- `[ 17]` [STAT News] STAT+: ARPA-H to invest $62 million to develop FDA-authorized AI to help treat heart failure  
  <https://www.statnews.com/2026/09/09/arpa-h-advocate-program-autonomous-ai-bots-for-heart-failure/?utm_campaign=rss>
- `[ 10]` [ScienceAlert] A Low-Plastic Diet Has Detectable Impacts on Urine Levels Within a Week, New Experiment Shows  
  <https://www.sciencealert.com/a-new-study-put-people-on-a-low-plastic-diet-it-changed-the-chemicals-in-their-urine>
- `[ 10]` [ScienceDaily] Your personality may be more genetic than scientists realized  
  <https://www.sciencedaily.com/releases/2026/09/260907201554.htm>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (12)

- **[🤖 AI/ML & Tech]** `score 18` — Enrollment  
  Issue: `clickbait`  
  <https://johnmaconline.com/enrollment/#utm_source=rss&utm_medium=rss#utm_source=rss&utm_medium=rss&utm_campaign=enrollment>
- **[🤖 AI/ML & Tech]** `score 29` — OpenAI Is Beefing With Mathematicians, Will No Longer Sponsor Caltech 'Mathathon'  
  Issue: `clickbait`  
  <https://news.google.com/rss/articles/CBMirgFBVV95cUxOakNrOFEzaXp5NVdQRFlaSmZ3cHJxN2ZxdlpVT3Vaci1pdkNIdU84emcwWmpiTTNZWDJ6MWRNSm4xLTB5ZGZtdEtBaVRXZnhpMjZQUFFVV0YxR0tRbUdvRmFCU0dIYWMwaHlJbG5QODBiQU4za01wd3F1OHI1VXQ0SXBtdWpnT1lLcllRTHptWXpvT184NUkyLTA0WGRGRlFpNkZYdkJzQ0dxYUExNEE?oc=5>
- **[🤖 AI/ML & Tech]** `score 35` — OpenAI's rogue AI agents accessed more websites to communicate than originally believed — defiant LLMs accessed old wikis and abandoned websites to co-ordinate in a bid to dupe assessors  
  Issue: `clickbait`  
  <https://www.tomshardware.com/tech-industry/artificial-intelligence/openais-rogue-ai-agents-accessed-more-websites-to-communicate-than-originally-believed-defiant-llms-accessed-old-wikis-and-abandoned-websites-to-co-ordinate-in-a-bid-to-dupe-assessors>
- **[🌍 Climate & Energy]** `score 22` — You Get What You Tolerate  
  Issue: `clickbait`  
  <https://drhurd.com/2026/09/12/you-get-what-you-tolerate/>
- **[🌍 Climate & Energy]** `score 22` — We once had to melt snow just to flush our toilet. It was one of several unexpected challenges of living off-grid.  
  Issue: `clickbait`  
  <https://www.businessinsider.com/lived-off-the-grid-biggest-challenges-inconveniences-surprises-2026-9>
- **[🏠 Homelab & DIY]** `score 38` — jf  
  Issue: `clickbait`  
  <http://preposter.us/single-michigan-helium-network/jf.html>
- **[🥾 Outdoors & Recreation]** `score 22` — Modular folding camp grill is whatever size you need it to be  
  Issue: `clickbait`  
  <https://newatlas.com/outdoor-cooking/grilti-ever-modular-camp-grill/>
- **[🥾 Outdoors & Recreation]** `score 25` — TechRadar's new privacy newsletter is out — read Leave No Trace issue #2 now  
  Issue: `clickbait`  
  <https://www.techradar.com/vpn/vpn-privacy-security/techradars-new-privacy-newsletter-is-out-read-leave-no-trace-issue-2-now>
- **[🥾 Outdoors & Recreation]** `score 20` — Freezable titanium plate keeps your cooler chilled longer than ice packs  
  Issue: `clickbait`  
  <https://newatlas.com/outdoor-gear/frost-titan-core-titanium-plate-cooling-camping/>
- **[🔬 Science]** `score 27` — The Good List: 6 Things to Bring Joy to Your Day  
  Issue: `clickbait`  
  <https://www.nytimes.com/2026/09/09/briefing/09-the-good-list-perfect-september.html>
- **[🚀 Sci-Fi & Culture]** `score 20` — Five Leagues From the Borderlands: Introducing… Jeff's Stag Party  
  Issue: `clickbait`  
  <https://bedroombattlefields.com/five-leagues-from-the-borderlands-introducing-jeffs-stag-party/>
- **[🚀 Sci-Fi & Culture]** `score 22` — Hexagon Wall Panels – Modular Shallow + Deep with Snug Pegs #3DThursday #3DPrinting  
  Issue: `clickbait`  
  <https://blog.adafruit.com/2026/09/10/hexagon-wall-panels-modular-shallow-deep-with-snug-pegs-3dthursday-3dprinting-2/>

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 63 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 29 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏛️ Architecture & Design** has 22 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏛️ Architecture & Design** is dominated by **ArchDaily** (20 articles, 71%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **🏠 Homelab & DIY** has 27 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌾 Homestead & Hobby Farm** has 8 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🌾 Homestead & Hobby Farm** is dominated by **Hobby Farms** (4 articles, 44%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **🏔️ Williams Lake Local** has 28 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏔️ Williams Lake Local** is dominated by **Williams Lake Tribune** (19 articles, 46%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **📰 General News** has 97 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🥾 Outdoors & Recreation** has a low average score (31.9) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🥾 Outdoors & Recreation** has 8 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 31 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (21.7) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🌿 Health & Wellness** has 49 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 12 article(s) should be removed (`clickbait` ×12) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 11 feeds · 484 articles · 2026-09-13 17:03 UTC_
