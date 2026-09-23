# Feed Scoring & Scrubbing Report

_Generated: 2026-08-16 13:43 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 11 |
| Total articles | 483 |
| Stale articles (>48h) | 363 |
| Scrub pass | ✅ ran |
| Flagged for removal | 2 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 90 | 🟡 51.2 | 26–68 | 69 | TechRadar (14) |
| 🌍 Climate & Energy | 49 | 🟡 52.0 | 10–77 | 31 | Al Jazeera English (4) |
| 🏛️ Architecture & Design | 30 | 🟡 52.0 | 35–77 | 27 | ArchDaily (15) |
| 🏠 Homelab & DIY | 27 | 🟡 52.0 | 18–65 | 20 | Hackaday (5) |
| 🌾 Homestead & Hobby Farm | 7 | 🔴 41.7 | 8–65 | 7 | Hobby Farms (2) |
| 🏔️ Williams Lake Local | 46 | 🟢 84.0 | 68–95 | 32 | Williams Lake Tribune (28) |
| 📰 General News | 126 | 🟡 67.1 | 62–74 | 88 | TechRadar (14) |
| 🥾 Outdoors & Recreation | 6 | 🔴 37.0 | 22–44 | 4 | Outside Online (2) |
| 🔬 Science | 41 | 🟡 52.8 | 42–59 | 34 | ScienceDaily (11) |
| 🚀 Sci-Fi & Culture | 8 | 🔴 38.2 | 6–52 | 8 | Neowin (1) |
| 🌿 Health & Wellness | 53 | 🟡 62.8 | 10–77 | 43 | STAT News (8) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 90 (90 scored)
- **Score**: avg 51.2 | min 26 | max 68
- **Stale** (>48h): 69
- **Avg age**: 75.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        1
  30–39   │ ██                     6
  40–49   │ ████████              22
  50–59   │ ████████████████████  54
  60–69   │ ██                     7
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| TechRadar | 14 | 16% |
| WIRED | 9 | 10% |
| Tom's Hardware | 8 | 9% |
| Kagi Small Web | 6 | 7% |
| The Verge | 6 | 7% |
| Boing Boing | 5 | 6% |
| Fast Company | 5 | 6% |
| Business Insider | 3 | 3% |

**Low-score articles (≤30):**

- `[ 26]` [Lifehacker] ChatGPT Can Now Remember Actions You Take on Your Mac  
  <https://lifehacker.com/tech/chatgpt-can-now-remember-actions-you-take-on-your-mac?utm_medium=RSS>

### 🟡 🌍 Climate & Energy

- **Articles**: 49 (49 scored)
- **Score**: avg 52.0 | min 10 | max 77
- **Stale** (>48h): 31
- **Avg age**: 68.5h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        1
  20–29   │                        1
  30–39   │ ██                     3
  40–49   │ ███████                9
  50–59   │ ████████████████████  25
  60–69   │ ██████                 8
  70–79   │ █                      2
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Al Jazeera English | 4 | 8% |
| Mother Jones | 4 | 8% |
| The Narwhal | 4 | 8% |
| InsideEVs | 4 | 8% |
| New Atlas | 3 | 6% |
| Wildfire Today | 2 | 4% |
| NYT Top Stories | 2 | 4% |
| APTN News | 2 | 4% |

**Low-score articles (≤30):**

- `[ 22]` Tick Populations Surge as the Climate Warms, and Farmers Bear the Brunt | Civil Eats  
  <https://civileats.com/2026/08/13/tick-populations-surge-as-the-climate-warms-and-farmers-bear-the-brunt/>
- `[ 10]` [BC Gov News] Reducing health risks from wildfire smoke - BC Gov News  
  <https://news.gov.bc.ca/releases/2026HLTH0070-000945>

### 🟡 🏛️ Architecture & Design

- **Articles**: 30 (30 scored)
- **Score**: avg 52.0 | min 35 | max 77
- **Stale** (>48h): 27
- **Avg age**: 80.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ ███                    2
  40–49   │ ████████████████████  11
  50–59   │ ██████████████████    10
  60–69   │ ██████████             6
  70–79   │ █                      1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ArchDaily | 15 | 50% ⚠️ |
| Dezeen | 5 | 17% |
| Architizer | 3 | 10% |
| Dwell | 2 | 7% |
| Kagi Small Web | 1 | 3% |
| New Atlas | 1 | 3% |
| Canadian Architect | 1 | 3% |
| Boing Boing | 1 | 3% |

### 🟡 🏠 Homelab & DIY

- **Articles**: 27 (27 scored)
- **Score**: avg 52.0 | min 18 | max 65
- **Stale** (>48h): 20
- **Avg age**: 72.2h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██                     2
  20–29   │                        0
  30–39   │ █                      1
  40–49   │ ████                   3
  50–59   │ ████████████████████  14
  60–69   │ ██████████             7
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hackaday | 5 | 19% |
| Tom's Hardware | 4 | 15% |
| Popular Woodworking | 4 | 15% |
| XDA Developers | 3 | 11% |
| New Atlas | 2 | 7% |
| MakeUseOf | 1 | 4% |
| TechRadar | 1 | 4% |
| How-To Geek | 1 | 4% |

**Low-score articles (≤30):**

- `[ 18]` [Dezeen] Eight products that showcase the versatility of wood  
  <https://www.dezeen.com/2026/08/14/kitchens-chairs-seating-tables-lighting-wood-timber-dezeen-showroom/>
- `[ 19]` 🔓 [Williams Lake Tribune] 3-day acting workshop inspires Xatśūll First Nation children, youth  
  <https://wltribune.com/2026/08/12/3-day-acting-workshop-inspires-xatsull-first-nation-children-youth/>

### 🔴 🌾 Homestead & Hobby Farm

- **Articles**: 7 (7 scored)
- **Score**: avg 41.7 | min 8 | max 65
- **Stale** (>48h): 7
- **Avg age**: 91.9h

**Score distribution:**
```
  0–9     │ ██████████             1
  10–19   │ ██████████             1
  20–29   │                        0
  30–39   │ ██████████             1
  40–49   │                        0
  50–59   │ ████████████████████   2
  60–69   │ ████████████████████   2
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hobby Farms | 2 | 29% |
| The Tyee | 1 | 14% |
| Small Farm Canada | 1 | 14% |
| Android Authority | 1 | 14% |
| Civil Eats | 1 | 14% |
| Pique Newsmagazine | 1 | 14% |

**Low-score articles (≤30):**

- `[  8]` [Android Authority] Ultimate Ears WONDERBOOM 4 hits its lowest Amazon price yet  
  <https://www.androidauthority.com/ultimate-ears-wonderboom-4-deal-3697968/>
- `[ 18]` [Hobby Farms] Growing Mushrooms at Home: A Beginner’s Guide  
  <https://www.hobbyfarms.com/growing-mushrooms-at-home/>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 46 (46 scored)
- **Score**: avg 84.0 | min 68 | max 95
- **Stale** (>48h): 32
- **Avg age**: 71.1h
- **Local-flagged**: 46

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │                        0
  60–69   │ █                      2
  70–79   │ ███████                9
  80–89   │ ████████████████████  24
  90–100  │ █████████             11
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 28 | 61% ⚠️ |
| My Cariboo Now | 11 | 24% |
| Regional News Archives - Williams Lake Tribune | 2 | 4% |
| BC Gov News | 2 | 4% |
| Quesnel Cariboo Observer | 1 | 2% |
| CFJC Today Kamloops | 1 | 2% |
| Pique Newsmagazine | 1 | 2% |

### 🟡 📰 General News

- **Articles**: 126 (126 scored)
- **Score**: avg 67.1 | min 62 | max 74
- **Stale** (>48h): 88
- **Avg age**: 70.9h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │                        0
  60–69   │ ████████████████████  87
  70–79   │ ████████              39
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| TechRadar | 14 | 11% |
| NYT Top Stories | 12 | 10% |
| The Tyee | 10 | 8% |
| Al Jazeera English | 6 | 5% |
| Engadget | 6 | 5% |
| Hackaday | 6 | 5% |
| The Atlantic | 5 | 4% |
| NYT Business | 4 | 3% |

### 🔴 🥾 Outdoors & Recreation

- **Articles**: 6 (6 scored)
- **Score**: avg 37.0 | min 22 | max 44
- **Stale** (>48h): 4
- **Avg age**: 88.9h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
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
| Outside Online | 2 | 33% |
| Atlas Obscura | 1 | 17% |
| Bicycling | 1 | 17% |
| AFAR | 1 | 17% |
| Open Culture | 1 | 17% |

**Low-score articles (≤30):**

- `[ 22]` 🔓 [AFAR] Grand Rapids Is the Outdoor Adventure Base Camp You Didn’t Expect  
  <https://www.afar.com/magazine/best-outdoor-adventures-near-grand-rapids>

### 🟡 🔬 Science

- **Articles**: 41 (41 scored)
- **Score**: avg 52.8 | min 42 | max 59
- **Stale** (>48h): 34
- **Avg age**: 78.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │ █████                  9
  50–59   │ ████████████████████  32
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 11 | 27% |
| Scientific American | 5 | 12% |
| ScienceAlert | 5 | 12% |
| Popular Mechanics | 3 | 7% |
| Nautilus | 3 | 7% |
| Hackaday | 3 | 7% |
| Business Insider | 1 | 2% |
| CNET | 1 | 2% |

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 8 (8 scored)
- **Score**: avg 38.2 | min 6 | max 52
- **Stale** (>48h): 8
- **Avg age**: 104.1h

**Score distribution:**
```
  0–9     │ █████                  1
  10–19   │ █████                  1
  20–29   │                        0
  30–39   │ █████                  1
  40–49   │ █████                  1
  50–59   │ ████████████████████   4
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Neowin | 1 | 12% |
| Boing Boing | 1 | 12% |
| Kagi Small Web | 1 | 12% |
| Strange Horizons | 1 | 12% |
| The Marginalian | 1 | 12% |
| Reactor Magazine | 1 | 12% |
| Nautilus | 1 | 12% |
| WIRED | 1 | 12% |

**Low-score articles (≤30):**

- `[ 12]` [Neowin] Sci-fi road trip game Caravan SandWitch is free on the Epic Games Store  
  <https://www.neowin.net/news/sci-fi-road-trip-game-caravan-sandwitch-is-free-on-the-epic-games-store/?utm_source=rss>
- `[  6]` [Boing Boing] Adam Savage is gobsmacked by this hand-drawn Enterprise cutaway  
  <https://boingboing.net/2026/08/12/adam-savage-is-gobsmacked-by-this-hand-drawn-enterprise-cuta.html>

### 🟡 🌿 Health & Wellness

- **Articles**: 53 (53 scored)
- **Score**: avg 62.8 | min 10 | max 77
- **Stale** (>48h): 43
- **Avg age**: 74.9h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        1
  20–29   │                        0
  30–39   │                        1
  40–49   │ █                      2
  50–59   │ ████████              10
  60–69   │ ████████████████████  23
  70–79   │ █████████████         16
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| STAT News | 8 | 15% |
| Fast Company | 5 | 9% |
| ScienceDaily | 4 | 8% |
| NYT Well | 3 | 6% |
| KFF Health News | 3 | 6% |
| Harvard Health Blog | 2 | 4% |
| Nautilus | 2 | 4% |
| Being Patient | 2 | 4% |

**Low-score articles (≤30):**

- `[ 10]` [ScienceDaily] Scientists turn sheep’s wool into a material that helps regrow bone  
  <https://www.sciencedaily.com/releases/2026/08/260812015210.htm>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (2)

- **[🏠 Homelab & DIY]** `score 18` — Eight products that showcase the versatility of wood  
  Issue: `deals`  
  <https://www.dezeen.com/2026/08/14/kitchens-chairs-seating-tables-lighting-wood-timber-dezeen-showroom/>
- **[🥾 Outdoors & Recreation]** `score 22` — Grand Rapids Is the Outdoor Adventure Base Camp You Didn't Expect  
  Issue: `clickbait`  
  <https://www.afar.com/magazine/best-outdoor-adventures-near-grand-rapids>

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 69 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 31 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏛️ Architecture & Design** has 27 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏛️ Architecture & Design** is dominated by **ArchDaily** (15 articles, 50%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **🏠 Homelab & DIY** has 20 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌾 Homestead & Hobby Farm** has 7 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 32 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏔️ Williams Lake Local** is dominated by **Williams Lake Tribune** (28 articles, 61%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **📰 General News** has 88 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 34 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🚀 Sci-Fi & Culture** has 8 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌿 Health & Wellness** has 43 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 2 article(s) should be removed (`deals` ×1, `clickbait` ×1) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 11 feeds · 483 articles · 2026-08-16 13:43 UTC_
