# Feed Scoring & Scrubbing Report

_Generated: 2026-10-04 17:30 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 11 |
| Total articles | 402 |
| Stale articles (>48h) | 321 |
| Scrub pass | ✅ ran |
| Flagged for removal | 6 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 87 | 🟡 53.2 | 27–70 | 66 | Fast Company (10) |
| 🌍 Climate & Energy | 39 | 🟡 47.3 | 8–70 | 33 | TechRadar (3) |
| 🏛️ Architecture & Design | 27 | 🟡 48.4 | 32–65 | 21 | ArchDaily (8) |
| 🏠 Homelab & DIY | 36 | 🟡 50.2 | 15–64 | 30 | Adafruit Blog (9) |
| 🌾 Homestead & Hobby Farm | 9 | 🔴 40.7 | 12–78 | 7 | Atlas Obscura (2) |
| 🏔️ Williams Lake Local | 34 | 🟢 79.6 | 37–93 | 25 | Williams Lake Tribune (11) |
| 📰 General News | 65 | 🟡 63.6 | 17–73 | 49 | TechRadar (6) |
| 🥾 Outdoors & Recreation | 4 | 🔴 42.2 | 5–58 | 3 | The Road Goes Ever On (1) |
| 🔬 Science | 40 | 🟡 51.9 | 34–64 | 35 | ScienceDaily (13) |
| 🚀 Sci-Fi & Culture | 8 | 🔴 31.6 | 10–42 | 6 | Edge (GamesRadar) (1) |
| 🌿 Health & Wellness | 53 | 🟡 56.9 | 22–73 | 46 | ScienceDaily (7) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 87 (87 scored)
- **Score**: avg 53.2 | min 27 | max 70
- **Stale** (>48h): 66
- **Avg age**: 75.5h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        1
  30–39   │                        0
  40–49   │ ██████████            25
  50–59   │ ████████████████████  48
  60–69   │ █████                 12
  70–79   │                        1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Fast Company | 10 | 11% |
| Tom's Hardware | 8 | 9% |
| WIRED | 8 | 9% |
| The Verge | 7 | 8% |
| TechRadar | 7 | 8% |
| Business Insider | 6 | 7% |
| TechCrunch | 5 | 6% |
| Kagi Small Web | 4 | 5% |

**Low-score articles (≤30):**

- `[ 27]` 🔓 [The Verge] Protesters gather at OpenAI’s DevDay  
  <https://www.theverge.com/ai-artificial-intelligence/1002201/openai-sam-altman-openai-devday-protests-ice-data-centers>

### 🟡 🌍 Climate & Energy

- **Articles**: 39 (39 scored)
- **Score**: avg 47.3 | min 8 | max 70
- **Stale** (>48h): 33
- **Avg age**: 86.5h

**Score distribution:**
```
  0–9     │ █                      1
  10–19   │ █                      1
  20–29   │ ██                     2
  30–39   │ █████                  4
  40–49   │ █████████████         11
  50–59   │ ████████████████████  16
  60–69   │ ███                    3
  70–79   │ █                      1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| TechRadar | 3 | 8% |
| Mother Jones | 3 | 8% |
| NRDC | 3 | 8% |
| InsideEVs | 2 | 5% |
| TechCrunch | 2 | 5% |
| Gizmodo | 2 | 5% |
| Scientific American | 2 | 5% |
| New Atlas | 2 | 5% |

**Low-score articles (≤30):**

- `[ 20]` [Atlas Obscura] Ancient Hon Chuong Cham Tower in De Gi, Vietnam  
  <https://www.atlasobscura.com/places/ancient-hon-chuong-cham-tower>
- `[ 27]` [Gizmodo] Ford CEO Says Europe Is Lost To Chinese Electric Vehicles  
  <https://news.google.com/rss/articles/CBMikgFBVV95cUxNcGlyc0g5OHlqVGtMUjNaYVN1WVIxTFZlX3RFdFRPbzlUQ1Y5b01KamZBd25QbFdXaFJObUcwV1BaTWRONzFVVnlDcjYzak93bUQ0VWhzSHdDWmhCb1FqRlBVLTBtVzhnaGRQc0Zaclk3SFlBY2liMkVaSjMySW16WkNkcDNTNC1NUzFWMnh3MEVkQQ?oc=5>
- `[  8]` [Boing Boing] Chat Pile's songs are bleak, but their live show is a blast  
  <https://boingboing.net/2026/09/30/chat-pile-live-sacramento-ace-of-spades.html>
- `[ 18]` [Kagi Small Web] LET’S HEAR IT FOR ANTÓNIO GUTERRES!  
  <https://jonathonporritt.com/antonio-guterres-climate-quotes/>

### 🟡 🏛️ Architecture & Design

- **Articles**: 27 (27 scored)
- **Score**: avg 48.4 | min 32 | max 65
- **Stale** (>48h): 21
- **Avg age**: 78.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ ████████               5
  40–49   │ █████████████          8
  50–59   │ ████████████████████  12
  60–69   │ ███                    2
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ArchDaily | 8 | 30% |
| Dezeen | 6 | 22% |
| Canadian Architect | 4 | 15% |
| Dwell | 2 | 7% |
| Forbes Innovation | 1 | 4% |
| Kottke.org | 1 | 4% |
| Kagi Small Web | 1 | 4% |
| New Atlas | 1 | 4% |

### 🟡 🏠 Homelab & DIY

- **Articles**: 36 (36 scored)
- **Score**: avg 50.2 | min 15 | max 64
- **Stale** (>48h): 30
- **Avg age**: 80.3h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      1
  20–29   │ ███                    3
  30–39   │ ██                     2
  40–49   │ ██████                 6
  50–59   │ ████████████████████  18
  60–69   │ ██████                 6
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Adafruit Blog | 9 | 25% |
| XDA Developers | 5 | 14% |
| Popular Woodworking | 4 | 11% |
| Hackster News | 3 | 8% |
| Engadget | 2 | 6% |
| Kagi Small Web | 2 | 6% |
| How-To Geek | 2 | 6% |
| Hackaday | 2 | 6% |

**Low-score articles (≤30):**

- `[ 15]` [Kagi Small Web] A Prayer for Blessing of Pets  
  <https://liberationtheologylutheran.blogspot.com/2026/10/a-prayer-for-blessing-of-pets.html>
- `[ 26]` [Neowin] Google Home September update adds new setup improvements and audio preview  
  <https://www.neowin.net/news/google-home-september-update-adds-new-setup-improvements-and-audio-preview/?utm_source=rss>
- `[ 27]` [Android Authority] Nanoleaf will soon let you control your smart lights with ChatGPT and Claude  
  <https://www.androidauthority.com/nanoleaf-smart-lights-mcp-chatgpt-claude-3717231/>
- `[ 20]` [Adafruit Blog] Candy Bar Brain – Halloween Specimen Chamber  
  <https://blog.adafruit.com/2026/09/29/candy-bar-brain-halloween-specimen-chamber/>

### 🔴 🌾 Homestead & Hobby Farm

- **Articles**: 9 (9 scored)
- **Score**: avg 40.7 | min 12 | max 78
- **Stale** (>48h): 7
- **Avg age**: 72.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ████████████████████   3
  20–29   │ ██████                 1
  30–39   │                        0
  40–49   │ ██████                 1
  50–59   │ █████████████          2
  60–69   │ ██████                 1
  70–79   │ ██████                 1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Atlas Obscura | 2 | 22% |
| Canadian Forest Industries | 1 | 11% |
| Boing Boing | 1 | 11% |
| Scientific American | 1 | 11% |
| RealAgriculture | 1 | 11% |
| The Western Producer | 1 | 11% |
| Logging and Sawmilling Journal | 1 | 11% |
| Small Farm Canada | 1 | 11% |

**Low-score articles (≤30):**

- `[ 12]` [Canadian Forest Industries] Lucidyne  
  <https://www.woodbusiness.ca/ve-sponsor/lucidyne/>
- `[ 18]` [Boing Boing] Rob Ullman drew a 48-page comic about his single day in Zion National Park  
  <https://boingboing.net/2026/10/02/fountain-pen-rob-ullman-24-hours-in-zion.html>
- `[ 22]` [Atlas Obscura] Grand Vista Sanitarium in Richmond, California  
  <https://www.atlasobscura.com/places/grande-vista-sanitarium-belgum-sanitarium>
- `[ 18]` [Atlas Obscura] The Best Haunted Hotels to Book for a Spooky Getaway  
  <https://www.atlasobscura.com/articles/best-haunted-hotels-for-a-spooky-getaway>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 34 (34 scored)
- **Score**: avg 79.6 | min 37 | max 93
- **Stale** (>48h): 25
- **Avg age**: 76.3h
- **Local-flagged**: 34

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ █                      1
  40–49   │                        0
  50–59   │ ██                     2
  60–69   │                        0
  70–79   │ ███████████           10
  80–89   │ ████████████████████  17
  90–100  │ ████                   4
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 11 | 32% |
| My Cariboo Now | 9 | 26% |
| 100 Mile Free Press | 6 | 18% |
| Quesnel Cariboo Observer | 3 | 9% |
| Cariboo Signals Reviews | 3 | 9% |
| BC Wildfire Service | 1 | 3% |
| The Northern Miner | 1 | 3% |

### 🟡 📰 General News

- **Articles**: 65 (65 scored)
- **Score**: avg 63.6 | min 17 | max 73
- **Stale** (>48h): 49
- **Avg age**: 75.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        1
  20–29   │ ██                     4
  30–39   │ █                      2
  40–49   │ █                      2
  50–59   │                        0
  60–69   │ ████████████████████  29
  70–79   │ ██████████████████    27
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| TechRadar | 6 | 9% |
| Hackaday | 5 | 8% |
| NYT Business | 5 | 8% |
| Scientific American | 5 | 8% |
| The Atlantic | 4 | 6% |
| Committee to Protect Journalists | 4 | 6% |
| Al Jazeera English | 3 | 5% |
| The Tyee | 3 | 5% |

**Low-score articles (≤30):**

- `[ 17]` [Al Jazeera English] G7 nations bow to US pressure and avoid crippling diesel ban  
  <https://www.aljazeera.com/video/newsfeed/2026/10/3/g7-nations-bow-to-us-pressure-and-avoid-crippling-diesel-ban?traffic_source=rss>
- `[ 25]` 🔓 [NYT Top Stories] ‘Ready to Blow His Stack’: How Biden Nearly Cut Off Netanyahu Over Gaza  
  <https://www.nytimes.com/2026/10/01/us/politics/mcgurk-biden-netanyahu-gaza.html>
- `[ 27]` 🔓 [The Atlantic] The Baltic States Prepare for War  
  <https://www.theatlantic.com/magazine/2026/11/baltic-defense-russia/688692/?utm_source=feed>
- `[ 27]` 🔓 [The Atlantic] A Near-Disaster on Flydubai  
  <https://www.theatlantic.com/ideas/2026/09/flydubai-plane-attack-israel/688848/?utm_source=feed>
- `[ 29]` 🔓 [The Atlantic] Trump’s Latest Appeal to Russia Could Outrage Even His Allies  
  <https://www.theatlantic.com/national-security/2026/09/trump-russia-putin-ukraine-sanctions/688808/?utm_source=feed>

### 🔴 🥾 Outdoors & Recreation

- **Articles**: 4 (4 scored)
- **Score**: avg 42.2 | min 5 | max 58
- **Stale** (>48h): 3
- **Avg age**: 79.9h

**Score distribution:**
```
  0–9     │ ██████████             1
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │ ██████████             1
  50–59   │ ████████████████████   2
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| The Road Goes Ever On | 1 | 25% |
| Outside Online | 1 | 25% |
| Kagi Small Web | 1 | 25% |
| ScienceAlert | 1 | 25% |

**Low-score articles (≤30):**

- `[  5]` [Kagi Small Web] 'Verity': Not enough trashy fun  
  <http://denersteinunleashed.blogspot.com/2026/09/verity-not-enough-trashy-fun.html>

### 🟡 🔬 Science

- **Articles**: 40 (40 scored)
- **Score**: avg 51.9 | min 34 | max 64
- **Stale** (>48h): 35
- **Avg age**: 80.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ █                      1
  40–49   │ ███████████████       15
  50–59   │ ████████████████████  19
  60–69   │ █████                  5
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 13 | 32% |
| ScienceAlert | 6 | 15% |
| Scientific American | 5 | 12% |
| EarthSky | 3 | 8% |
| WIRED | 1 | 2% |
| Popular Mechanics | 1 | 2% |
| STAT News | 1 | 2% |
| Gizmodo | 1 | 2% |

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 8 (8 scored)
- **Score**: avg 31.6 | min 10 | max 42
- **Stale** (>48h): 6
- **Avg age**: 83.5h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █████████████          2
  20–29   │ ██████                 1
  30–39   │ █████████████          2
  40–49   │ ████████████████████   3
  50–59   │                        0
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Edge (GamesRadar) | 1 | 12% |
| CBC Arts | 1 | 12% |
| Open Culture | 1 | 12% |
| Kagi Small Web | 1 | 12% |
| Kottke.org | 1 | 12% |
| EBSCO | 1 | 12% |
| Vancouver Sun | 1 | 12% |
| Reactor Magazine | 1 | 12% |

**Low-score articles (≤30):**

- `[ 29]` 🔓 [Edge (GamesRadar)] Final Fantasy 7 Revelation lead says making each game in the trilogy complete was "non-negotiable"  
  <https://www.gamesradar.com/games/final-fantasy/final-fantasy-7-revelation-lead-explains-that-making-each-game-in-the-rpg-trilogy-a-complete-experience-was-non-negotiable-from-the-beginning/>
- `[ 10]` [Kottke.org] Eternal Family is a media service that shows “a...  
  <https://kottke.org/26/09/0049709-eternal-family>
- `[ 18]` [EBSCO] How Reading Challenges Can Meet Reader Needs  
  <https://about.ebsco.com/blogs/novelist/how-reading-challenges-can-meet-reader-needs>

### 🟡 🌿 Health & Wellness

- **Articles**: 53 (53 scored)
- **Score**: avg 56.9 | min 22 | max 73
- **Stale** (>48h): 46
- **Avg age**: 80.8h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        1
  30–39   │                        0
  40–49   │ ███                    5
  50–59   │ ████████████████████  30
  60–69   │ █████████             14
  70–79   │ ██                     3
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 7 | 13% |
| ScienceAlert | 7 | 13% |
| Neuroscience News | 5 | 9% |
| Fast Company | 4 | 8% |
| The Atlantic | 3 | 6% |
| KFF Health News | 3 | 6% |
| Scientific American | 3 | 6% |
| Nautilus | 2 | 4% |

**Low-score articles (≤30):**

- `[ 22]` [ScienceDaily] Children at risk for depression get “stuck” on sad faces  
  <https://www.sciencedaily.com/releases/2026/09/260927225022.htm>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (6)

- **[🌍 Climate & Energy]** `score 18` — LET'S HEAR IT FOR ANTÓNIO GUTERRES!  
  Issue: `clickbait`  
  <https://jonathonporritt.com/antonio-guterres-climate-quotes/>
- **[🏠 Homelab & DIY]** `score 15` — A Prayer for Blessing of Pets  
  Issue: `off-topic`  
  <https://liberationtheologylutheran.blogspot.com/2026/10/a-prayer-for-blessing-of-pets.html>
- **[🌾 Homestead & Hobby Farm]** `score 18` — Rob Ullman drew a 48-page comic about his single day in Zion National Park  
  Issue: `off-topic`  
  <https://boingboing.net/2026/10/02/fountain-pen-rob-ullman-24-hours-in-zion.html>
- **[🌾 Homestead & Hobby Farm]** `score 22` — Grand Vista Sanitarium in Richmond, California  
  Issue: `off-topic`  
  <https://www.atlasobscura.com/places/grande-vista-sanitarium-belgum-sanitarium>
- **[🌾 Homestead & Hobby Farm]** `score 18` — The Best Haunted Hotels to Book for a Spooky Getaway  
  Issue: `off-topic`  
  <https://www.atlasobscura.com/articles/best-haunted-hotels-for-a-spooky-getaway>
- **[🚀 Sci-Fi & Culture]** `score 18` — How Reading Challenges Can Meet Reader Needs  
  Issue: `off-topic`  
  <https://about.ebsco.com/blogs/novelist/how-reading-challenges-can-meet-reader-needs>

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 66 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 33 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏛️ Architecture & Design** has 21 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏠 Homelab & DIY** has 30 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌾 Homestead & Hobby Farm** has 7 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 25 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **📰 General News** has 49 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 35 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (31.6) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🚀 Sci-Fi & Culture** has 6 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌿 Health & Wellness** has 46 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 6 article(s) should be removed (`off-topic` ×5, `clickbait` ×1) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 11 feeds · 402 articles · 2026-10-04 17:30 UTC_
