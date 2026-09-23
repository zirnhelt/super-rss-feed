# Feed Scoring & Scrubbing Report

_Generated: 2026-09-20 16:58 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 11 |
| Total articles | 485 |
| Stale articles (>48h) | 393 |
| Scrub pass | ✅ ran |
| Flagged for removal | 2 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 88 | 🟡 53.3 | 38–72 | 69 | WIRED (10) |
| 🌍 Climate & Energy | 34 | 🟡 52.3 | 30–69 | 31 | New Atlas (5) |
| 🏛️ Architecture & Design | 29 | 🟡 53.4 | 34–73 | 23 | ArchDaily (11) |
| 🏠 Homelab & DIY | 46 | 🟡 49.3 | 18–60 | 37 | Adafruit Blog (10) |
| 🌾 Homestead & Hobby Farm | 6 | 🔴 40.0 | 15–54 | 5 | Hobby Farms (2) |
| 🏔️ Williams Lake Local | 47 | 🟢 79.4 | 51–95 | 37 | My Cariboo Now (25) |
| 📰 General News | 125 | 🟡 67.9 | 63–72 | 101 | WIRED (15) |
| 🥾 Outdoors & Recreation | 9 | 🔴 42.0 | 17–62 | 7 | Outside Online (3) |
| 🔬 Science | 42 | 🟡 52.3 | 41–80 | 35 | ScienceDaily (8) |
| 🚀 Sci-Fi & Culture | 8 | 🔴 33.2 | 5–53 | 6 | Kagi Small Web (3) |
| 🌿 Health & Wellness | 51 | 🟡 61.3 | 23–75 | 42 | Fast Company (4) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 88 (88 scored)
- **Score**: avg 53.3 | min 38 | max 72
- **Stale** (>48h): 69
- **Avg age**: 74.9h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        2
  40–49   │ ███████               20
  50–59   │ ████████████████████  56
  60–69   │ ██                     8
  70–79   │                        2
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| WIRED | 10 | 11% |
| TechRadar | 8 | 9% |
| Fast Company | 7 | 8% |
| Tom's Hardware | 7 | 8% |
| Business Insider | 6 | 7% |
| Gizmodo | 4 | 5% |
| Scientific American | 4 | 5% |
| NYT Business | 4 | 5% |

### 🟡 🌍 Climate & Energy

- **Articles**: 34 (34 scored)
- **Score**: avg 52.3 | min 30 | max 69
- **Stale** (>48h): 31
- **Avg age**: 89.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ ██                     2
  40–49   │ ███████████           10
  50–59   │ ████████████████████  17
  60–69   │ █████                  5
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| New Atlas | 5 | 15% |
| InsideEVs | 3 | 9% |
| Mother Jones | 2 | 6% |
| NYT Top Stories | 2 | 6% |
| Gizmodo | 2 | 6% |
| FlowingData | 2 | 6% |
| Resilience.org | 2 | 6% |
| Boing Boing | 1 | 3% |

**Low-score articles (≤30):**

- `[ 30]` [Articles - passivehouseplus.co.uk] Campaigners tell Irish government to publish Climate Action Plan  
  <https://passivehouseplus.co.uk/news/government/campaigners-tell-irish-government-to-publish-climate-action-plan>

### 🟡 🏛️ Architecture & Design

- **Articles**: 29 (29 scored)
- **Score**: avg 53.4 | min 34 | max 73
- **Stale** (>48h): 23
- **Avg age**: 83.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ █                      1
  40–49   │ ██████████             7
  50–59   │ ████████████████████  14
  60–69   │ ████████               6
  70–79   │ █                      1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ArchDaily | 11 | 38% |
| Dezeen | 6 | 21% |
| Dwell | 3 | 10% |
| Canadian Architect | 2 | 7% |
| New Atlas | 1 | 3% |
| TechRadar | 1 | 3% |
| Canadian Forest Industries | 1 | 3% |
| Forbes Innovation | 1 | 3% |

### 🟡 🏠 Homelab & DIY

- **Articles**: 46 (46 scored)
- **Score**: avg 49.3 | min 18 | max 60
- **Stale** (>48h): 37
- **Avg age**: 78.9h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        1
  20–29   │ ██                     3
  30–39   │ █                      2
  40–49   │ ████████              11
  50–59   │ ████████████████████  26
  60–69   │ ██                     3
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Adafruit Blog | 10 | 22% |
| Hackaday | 8 | 17% |
| Hackster News | 6 | 13% |
| Popular Woodworking | 6 | 13% |
| XDA Developers | 4 | 9% |
| MakeUseOf | 3 | 7% |
| Bambu Lab Blog | 3 | 7% |
| How-To Geek | 2 | 4% |

**Low-score articles (≤30):**

- `[ 18]` [Bambu Lab Blog] When 3D printing meets a sweet treat: Bambu Lab and Bambū Desserts & Drinks team up for a one of a kind collaboration  
  <https://blog.bambulab.com/when-3d-printing-meets-a-sweet-treat-bambu-lab-and-bambu-desserts-drinks-team-up-for-a-one-of-a-kind-collaboration/>
- `[ 20]` 🔓 [Popular Woodworking] The Splinter Report: September 18th  
  <https://www.popularwoodworking.com/editors-blog/the-splinter-report-september-18th/>
- `[ 23]` 🔓 [Popular Woodworking] Loud By Design  
  <https://www.popularwoodworking.com/editors-blog/loud-by-design/>
- `[ 22]` [Adafruit Blog] Articulated Skeleton – High Detail Full-Body Figure #3DThursday #3DPrinting  
  <https://blog.adafruit.com/2026/09/17/articulated-skeleton-high-detail-full-body-figure-3dthursday-3dprinting/>

### 🔴 🌾 Homestead & Hobby Farm

- **Articles**: 6 (6 scored)
- **Score**: avg 40.0 | min 15 | max 54
- **Stale** (>48h): 5
- **Avg age**: 84.9h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██████                 1
  20–29   │ ██████                 1
  30–39   │                        0
  40–49   │ ████████████████████   3
  50–59   │ ██████                 1
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hobby Farms | 2 | 33% |
| Country Guide | 1 | 17% |
| IndigiNews | 1 | 17% |
| Scientific American | 1 | 17% |
| Social Media Examiner | Social Media Marketing | 1 | 17% |

**Low-score articles (≤30):**

- `[ 27]` [IndigiNews] Call in the goats: Kanaka Bar calls on herd for help with wildfire risk  
  <https://indiginews.com/features/kanaka-bar-calls-on-herd-for-help-with-wildfire-risk/>
- `[ 15]` [Social Media Examiner | Social Media Marketing] Instagram Email Subscriber Tactic, No-Ad YouTube Strategy, and Industry News  
  <https://www.socialmediaexaminer.com/instagram-email-subscriber-tactic-no-ad-youtube-strategy-and-industry-news/>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 47 (47 scored)
- **Score**: avg 79.4 | min 51 | max 95
- **Stale** (>48h): 37
- **Avg age**: 78.4h
- **Local-flagged**: 47

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │ ██                     3
  60–69   │ █                      2
  70–79   │ ██████████████        16
  80–89   │ ████████████████████  22
  90–100  │ ███                    4
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| My Cariboo Now | 25 | 53% ⚠️ |
| Williams Lake Tribune | 17 | 36% |
| Quesnel Cariboo Observer | 3 | 6% |
| 100 Mile Free Press | 1 | 2% |
| Pique Newsmagazine | 1 | 2% |

### 🟡 📰 General News

- **Articles**: 125 (125 scored)
- **Score**: avg 67.9 | min 63 | max 72
- **Stale** (>48h): 101
- **Avg age**: 77.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │                        0
  60–69   │ ████████████████████  88
  70–79   │ ████████              37
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| WIRED | 15 | 12% |
| NYT Business | 11 | 9% |
| NYT Top Stories | 10 | 8% |
| TechRadar | 8 | 6% |
| The Atlantic | 7 | 6% |
| Williams Lake Tribune | 7 | 6% |
| Scientific American | 7 | 6% |
| Hackaday | 6 | 5% |

### 🔴 🥾 Outdoors & Recreation

- **Articles**: 9 (9 scored)
- **Score**: avg 42.0 | min 17 | max 62
- **Stale** (>48h): 7
- **Avg age**: 77.2h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██████                 1
  20–29   │ ██████                 1
  30–39   │ ██████                 1
  40–49   │ ████████████████████   3
  50–59   │ █████████████          2
  60–69   │ ██████                 1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Outside Online | 3 | 33% |
| Kagi Small Web | 1 | 11% |
| The Road Goes Ever On | 1 | 11% |
| AgWeb | 1 | 11% |
| Vancouver Sun | 1 | 11% |
| Williams Lake Tribune | 1 | 11% |
| Bicycling | 1 | 11% |

**Low-score articles (≤30):**

- `[ 23]` 🔓 [Outside Online] Paddle, Bike, Run at These Adventurous Multisport Events  
  <https://www.outsideonline.com/outdoor-adventure/water-activities/paddle-bike-run-multisport-events/>
- `[ 17]` 🔓 [Outside Online] Trail Running in Wine Country Brought the Joy Back to My Routine  
  <https://www.outsideonline.com/adventure-travel/destinations/north-america/trail-running-vacation-sonoma/>

### 🟡 🔬 Science

- **Articles**: 42 (42 scored)
- **Score**: avg 52.3 | min 41 | max 80
- **Stale** (>48h): 35
- **Avg age**: 81.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │ ██████████            14
  50–59   │ ████████████████████  26
  60–69   │                        1
  70–79   │                        0
  80–89   │                        1
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 8 | 19% |
| Scientific American | 7 | 17% |
| Neuroscience News | 4 | 10% |
| ScienceAlert | 4 | 10% |
| Quanta Magazine | 3 | 7% |
| Popular Mechanics | 3 | 7% |
| Tom's Hardware | 2 | 5% |
| Boing Boing | 2 | 5% |

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 8 (8 scored)
- **Score**: avg 33.2 | min 5 | max 53
- **Stale** (>48h): 6
- **Avg age**: 77.8h

**Score distribution:**
```
  0–9     │ ██████                 1
  10–19   │ ██████                 1
  20–29   │ ██████                 1
  30–39   │ ██████                 1
  40–49   │ ████████████████████   3
  50–59   │ ██████                 1
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Kagi Small Web | 3 | 38% |
| Curated Collections of Complete Audio Fiction | 1 | 12% |
| Reactor Magazine | 1 | 12% |
| Toms Guide | 1 | 12% |
| The Marginalian | 1 | 12% |
| The Atlantic Culture | 1 | 12% |

**Low-score articles (≤30):**

- `[ 18]` [Kagi Small Web] Signal Boost: Tenth Anniversary SOULDANCER Special Edition  
  <https://scifiwright.com/2026/09/signal-boost-tenth-anniversary-souldancer-special-edition/>
- `[  5]` [Curated Collections of Complete Audio Fiction] Laugh-filled Fantasies Fiction Podcast & Audio Fiction Collection  
  <https://www.theend.fyi/collection/laugh-filled-fantasies>
- `[ 20]` [Toms Guide] Prime Video top 10 shows — here’s the 3 worth binge-watching this week (September 16-22)  
  <https://www.tomsguide.com/entertainment/prime-video/prime-video-top-10-shows-heres-the-3-worth-binge-watching-this-week-september-16-22>

### 🟡 🌿 Health & Wellness

- **Articles**: 51 (51 scored)
- **Score**: avg 61.3 | min 23 | max 75
- **Stale** (>48h): 42
- **Avg age**: 77.8h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        1
  30–39   │                        0
  40–49   │                        0
  50–59   │ ███████████           16
  60–69   │ ████████████████████  29
  70–79   │ ███                    5
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Fast Company | 4 | 8% |
| KFF Health News | 4 | 8% |
| ScienceAlert | 4 | 8% |
| WIRED | 3 | 6% |
| STAT News | 3 | 6% |
| NYT Well | 3 | 6% |
| Forbes Innovation | 2 | 4% |
| Outside Online | 2 | 4% |

**Low-score articles (≤30):**

- `[ 23]` [KFF Health News] States Bet Big on Rural Health Startups, With a Silicon Valley Twist  
  <https://kffhealthnews.org/rural-health/rural-health-tech-startups-funding-louisiana/>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (2)

- **[🌾 Homestead & Hobby Farm]** `score 15` — Instagram Email Subscriber Tactic, No-Ad YouTube Strategy, and Industry News  
  Issue: `clickbait`  
  <https://www.socialmediaexaminer.com/instagram-email-subscriber-tactic-no-ad-youtube-strategy-and-industry-news/>
- **[🚀 Sci-Fi & Culture]** `score 20` — Prime Video top 10 shows — here's the 3 worth binge-watching this week (September 16-22)  
  Issue: `clickbait`  
  <https://www.tomsguide.com/entertainment/prime-video/prime-video-top-10-shows-heres-the-3-worth-binge-watching-this-week-september-16-22>

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 69 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 31 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏛️ Architecture & Design** has 23 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏠 Homelab & DIY** has 37 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 37 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏔️ Williams Lake Local** is dominated by **My Cariboo Now** (25 articles, 53%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **📰 General News** has 101 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🥾 Outdoors & Recreation** has 7 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 35 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (33.2) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🚀 Sci-Fi & Culture** has 6 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌿 Health & Wellness** has 42 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 2 article(s) should be removed (`clickbait` ×2) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 11 feeds · 485 articles · 2026-09-20 16:58 UTC_
