# Feed Scoring & Scrubbing Report

_Generated: 2026-09-06 16:14 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 11 |
| Total articles | 556 |
| Stale articles (>48h) | 438 |
| Scrub pass | ✅ ran |
| Flagged for removal | 7 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 103 | 🟡 48.4 | 25–72 | 79 | Kagi Small Web (11) |
| 🌍 Climate & Energy | 45 | 🟡 51.0 | 8–76 | 41 | Mother Jones (4) |
| 🏛️ Architecture & Design | 33 | 🟡 45.2 | 20–68 | 30 | ArchDaily (12) |
| 🏠 Homelab & DIY | 52 | 🟡 54.0 | 8–66 | 36 | Hackaday (10) |
| 🌾 Homestead & Hobby Farm | 10 | 🔴 44.8 | 2–58 | 8 | Hobby Farms (3) |
| 🏔️ Williams Lake Local | 46 | 🟢 79.4 | 44–91 | 31 | My Cariboo Now (23) |
| 📰 General News | 143 | 🟡 65.9 | 31–72 | 110 | NYT Top Stories (17) |
| 🥾 Outdoors & Recreation | 8 | 🔴 36.2 | 15–57 | 7 | Outside Online (2) |
| 🔬 Science | 38 | 🟡 47.7 | 32–59 | 31 | ScienceDaily (10) |
| 🚀 Sci-Fi & Culture | 10 | 🔴 27.1 | 12–54 | 9 | Kagi Small Web (3) |
| 🌿 Health & Wellness | 68 | 🟡 58.0 | 12–78 | 56 | Fast Company (8) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 103 (103 scored)
- **Score**: avg 48.4 | min 25 | max 72
- **Stale** (>48h): 79
- **Avg age**: 80.1h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ █                      3
  30–39   │ ███                    9
  40–49   │ ████████████████████  47
  50–59   │ ███████████████       37
  60–69   │ ██                     5
  70–79   │                        2
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Kagi Small Web | 11 | 11% |
| TechRadar | 10 | 10% |
| WIRED | 9 | 9% |
| Fast Company | 8 | 8% |
| Tom's Hardware | 7 | 7% |
| Business Insider | 7 | 7% |
| TechCrunch | 6 | 6% |
| Forbes Innovation | 5 | 5% |

**Low-score articles (≤30):**

- `[ 26]` [Android Authority] Google’s new Gemini feature aimed at multitaskers is starting to roll out  
  <https://www.androidauthority.com/gemini-overlay-minimize-button-rollout-3707874/>
- `[ 25]` [Android Authority] Gemini hands Lyria 3.5 the mic as the music model makes its debut on the app  
  <https://www.androidauthority.com/latest-lyria-model-comes-to-gemini-app-3707842/>
- `[ 28]` [Android Authority] Gemini could finally let you use your phone while it thinks about what to say  
  <https://www.androidauthority.com/gemini-overlay-minimize-apk-teardown-3705317/>

### 🟡 🌍 Climate & Energy

- **Articles**: 45 (45 scored)
- **Score**: avg 51.0 | min 8 | max 76
- **Stale** (>48h): 41
- **Avg age**: 85.3h

**Score distribution:**
```
  0–9     │                        1
  10–19   │                        0
  20–29   │ █                      2
  30–39   │ ██                     3
  40–49   │ ████████               9
  50–59   │ ████████████████████  22
  60–69   │ ██████                 7
  70–79   │                        1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Mother Jones | 4 | 9% |
| InsideEVs | 3 | 7% |
| Forbes Innovation | 2 | 4% |
| Kagi Small Web | 2 | 4% |
| APTN News | 2 | 4% |
| The Northern Miner | 2 | 4% |
| FlowingData | 2 | 4% |
| Resilience.org | 2 | 4% |

**Low-score articles (≤30):**

- `[ 29]` [Kagi Small Web] Edouardo forms, NHC worries  
  <https://enkiops.org/2026/09/01/edouardo-forms-nhc-worries/>
- `[  8]` [ArchDaily] Climate Infrastructure at Human Scale: From Water Management to Urban Cooling  
  <https://www.archdaily.com/1184153/climate-infrastructure-at-human-scale-from-water-management-to-urban-cooling>
- `[ 23]` [FlowingData] Uncounted heat-related deaths  
  <https://flowingdata.com/2026/09/01/uncounted-heat-related-deaths/>

### 🟡 🏛️ Architecture & Design

- **Articles**: 33 (33 scored)
- **Score**: avg 45.2 | min 20 | max 68
- **Stale** (>48h): 30
- **Avg age**: 87.1h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ███                    2
  30–39   │ ████████████           7
  40–49   │ ████████████████████  11
  50–59   │ ████████████████████  11
  60–69   │ ███                    2
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ArchDaily | 12 | 36% |
| Dwell | 6 | 18% |
| Dezeen | 4 | 12% |
| Canadian Architect | 3 | 9% |
| Kagi Small Web | 2 | 6% |
| New Atlas | 1 | 3% |
| The New Yorker | 1 | 3% |
| The Passive House Network | 1 | 3% |

**Low-score articles (≤30):**

- `[ 20]` [ArchDaily] Mr. Fool Moves a Mountain / Schwartz and Architecture  
  <https://www.archdaily.com/1183499/mr-fool-moves-a-mountain-schwartz-and-architecture>
- `[ 27]` [ArchDaily] 210 South 12th Building / RSHP  
  <https://www.archdaily.com/1184462/210-south-12th-building-rshp>
- `[ 30]` 🔓 [The New Yorker] Donald Trump’s Capital Makeover  
  <https://www.newyorker.com/magazine/2026/09/14/donald-trumps-capital-makeover>

### 🟡 🏠 Homelab & DIY

- **Articles**: 52 (52 scored)
- **Score**: avg 54.0 | min 8 | max 66
- **Stale** (>48h): 36
- **Avg age**: 80.3h

**Score distribution:**
```
  0–9     │                        1
  10–19   │                        1
  20–29   │                        1
  30–39   │                        0
  40–49   │ █████                  7
  50–59   │ ████████████████████  25
  60–69   │ █████████████         17
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hackaday | 10 | 19% |
| Adafruit Blog | 9 | 17% |
| XDA Developers | 8 | 15% |
| How-To Geek | 8 | 15% |
| Popular Woodworking | 6 | 12% |
| Hackster News | 3 | 6% |
| Kagi Small Web | 2 | 4% |
| New Atlas | 2 | 4% |

**Low-score articles (≤30):**

- `[  8]` [Adafruit Blog] Cursed Skull Desk Lamp – Bambu LED Kit 001 with Golden Flame Cutout #3DThursday #3DPrinting  
  <https://blog.adafruit.com/2026/09/03/cursed-skull-desk-lamp-bambu-led-kit-001-with-golden-flame-cutout-3dthursday-3dprinting/>
- `[ 10]` [Adafruit Blog] John Park’s Workshop — LIVE TODAY 9/3/26  
  <https://blog.adafruit.com/2026/09/03/john-parks-workshop-live-today-9-3-26/>
- `[ 20]` 🔓 [Popular Woodworking] The Ol’ 1–2  
  <https://www.popularwoodworking.com/woodworking-mistakes/the-ol-1-2/>

### 🔴 🌾 Homestead & Hobby Farm

- **Articles**: 10 (10 scored)
- **Score**: avg 44.8 | min 2 | max 58
- **Stale** (>48h): 8
- **Avg age**: 70.8h

**Score distribution:**
```
  0–9     │ ██                     1
  10–19   │ ██                     1
  20–29   │                        0
  30–39   │                        0
  40–49   │ ██                     1
  50–59   │ ████████████████████   7
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hobby Farms | 3 | 30% |
| The Atlantic Culture | 1 | 10% |
| RealAgriculture | 1 | 10% |
| Resilience.org | 1 | 10% |
| Neowin | 1 | 10% |
| Grainews | 1 | 10% |
| AgWeb | 1 | 10% |
| Wikipedia  - Recent changes [en] | 1 | 10% |

**Low-score articles (≤30):**

- `[ 10]` [Neowin] Save 79% on a lifetime subscription to iScanner  
  <https://www.neowin.net/deals/save-79-on-a-lifetime-subscription-to-iscanner/?utm_source=rss>
- `[  2]` [Wikipedia  - Recent changes [en]] Beau Monde Mall  
  <https://en.wikipedia.org/w/index.php?title=Beau_Monde_Mall&diff=1372624914&oldid=1372580933>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 46 (46 scored)
- **Score**: avg 79.4 | min 44 | max 91
- **Stale** (>48h): 31
- **Avg age**: 71.3h
- **Local-flagged**: 46

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │ ██                     2
  50–59   │                        0
  60–69   │ █                      1
  70–79   │ ██████████████████    18
  80–89   │ ████████████████████  19
  90–100  │ ██████                 6
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| My Cariboo Now | 23 | 50% ⚠️ |
| Williams Lake Tribune | 16 | 35% |
| Quesnel Cariboo Observer | 3 | 7% |
| CFJC Today Kamloops | 2 | 4% |
| Cariboo Signals Reviews | 1 | 2% |
| 100 Mile Free Press | 1 | 2% |

### 🟡 📰 General News

- **Articles**: 143 (143 scored)
- **Score**: avg 65.9 | min 31 | max 72
- **Stale** (>48h): 110
- **Avg age**: 81.3h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        1
  40–49   │                        0
  50–59   │                        3
  60–69   │ ████████████████████ 112
  70–79   │ ████                  27
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| NYT Top Stories | 17 | 12% |
| NYT Business | 13 | 9% |
| TechRadar | 12 | 8% |
| Hackaday | 8 | 6% |
| The Northern Miner | 7 | 5% |
| The Atlantic | 7 | 5% |
| The New Yorker | 6 | 4% |
| The Verge | 5 | 3% |

### 🔴 🥾 Outdoors & Recreation

- **Articles**: 8 (8 scored)
- **Score**: avg 36.2 | min 15 | max 57
- **Stale** (>48h): 7
- **Avg age**: 91.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██████████             2
  20–29   │ █████                  1
  30–39   │                        0
  40–49   │ ████████████████████   4
  50–59   │ █████                  1
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Outside Online | 2 | 25% |
| Boing Boing | 2 | 25% |
| Atlas Obscura | 2 | 25% |
| PaddlingLight.com | 1 | 12% |
| Hyperallergic | 1 | 12% |

**Low-score articles (≤30):**

- `[ 24]` [Boing Boing] Too much "human poo" in the Brecon Beacons  
  <https://boingboing.net/2026/09/04/too-much-human-poo-in-the-brecon-beacons.html>
- `[ 18]` [Atlas Obscura] Waldkunstpfad in Darmstadt, Germany  
  <https://www.atlasobscura.com/places/waldkunstpfad>
- `[ 15]` [Atlas Obscura] Adam’s Gulch  in Ketchum, Idaho  
  <https://www.atlasobscura.com/places/adams-gulch>

### 🟡 🔬 Science

- **Articles**: 38 (38 scored)
- **Score**: avg 47.7 | min 32 | max 59
- **Stale** (>48h): 31
- **Avg age**: 73.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ ████                   4
  40–49   │ ███████████████       15
  50–59   │ ████████████████████  19
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 10 | 26% |
| Scientific American | 5 | 13% |
| ScienceAlert | 3 | 8% |
| WIRED | 3 | 8% |
| Nautilus | 3 | 8% |
| Popular Mechanics | 3 | 8% |
| Quanta Magazine | 2 | 5% |
| Adafruit Blog | 2 | 5% |

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 10 (10 scored)
- **Score**: avg 27.1 | min 12 | max 54
- **Stale** (>48h): 9
- **Avg age**: 98.1h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ████████████████████   5
  20–29   │ ████████               2
  30–39   │                        0
  40–49   │ ████████               2
  50–59   │ ████                   1
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Kagi Small Web | 3 | 30% |
| Reactor Magazine | 2 | 20% |
| The Atlantic | 1 | 10% |
| MakeUseOf | 1 | 10% |
| Neowin | 1 | 10% |
| Edge (GamesRadar) | 1 | 10% |
| Colossal | 1 | 10% |

**Low-score articles (≤30):**

- `[ 15]` [MakeUseOf] Hulu buried one of its smartest sci-fi thrillers inside a sinister Silicon Valley lab  
  <https://www.makeuseof.com/hulu-buried-smartest-sci-fi-thrillers-inside-sinister-silicon-valley-lab/>
- `[ 12]` [Kagi Small Web] Books read, August 2026  
  <https://swan-tower.dreamwidth.org/1139912.html>
- `[ 15]` [Neowin] Sci-fi adventure Alone With You is free on Epic Games Store  
  <https://www.neowin.net/news/sci-fi-adventure-alone-with-you-is-free-on-epic-games-store/?utm_source=rss>
- `[ 29]` 🔓 [Edge (GamesRadar)] Final Fantasy 7 Revelation boss is "very much aware" you hate Chadley for being a socially inept doofus, but he will soon have "a very integral part" in the story anyway  
  <https://www.gamesradar.com/games/final-fantasy/final-fantasy-7-revelation-boss-is-very-much-aware-you-hate-chadley-for-being-a-socially-inept-doofus-but-he-will-soon-have-a-very-integral-part-in-the-story-anyway/>
- `[ 16]` [Colossal] Watercolors by kelogsloops Traverse the Emotional Terrain of Love and Loss  
  <https://www.thisiscolossal.com/2026/09/kelogsloops-watercolors-fantasy-memento-mori-paintings/>
- `[ 16]` [Reactor Magazine] Eight Versions of Fairy Tales That Tell a Different Story  
  <https://reactormag.com/eight-versions-of-fairy-tales-that-tell-a-different-story/>
- `[ 26]` [Kagi Small Web] A Tribute to Yayoi Kusama  
  <https://the-easel.com/link/a-tribute-to-yayoi-kusama/>

### 🟡 🌿 Health & Wellness

- **Articles**: 68 (68 scored)
- **Score**: avg 58.0 | min 12 | max 78
- **Stale** (>48h): 56
- **Avg age**: 87.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        1
  20–29   │ ██                     3
  30–39   │                        0
  40–49   │ █████                  7
  50–59   │ ██████████████        20
  60–69   │ ████████████████████  27
  70–79   │ ███████               10
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Fast Company | 8 | 12% |
| ScienceDaily | 6 | 9% |
| Kagi Small Web | 6 | 9% |
| ScienceAlert | 4 | 6% |
| NYT Well | 4 | 6% |
| STAT News | 4 | 6% |
| Mother Jones | 3 | 4% |
| NPR Health News | 3 | 4% |

**Low-score articles (≤30):**

- `[ 22]` 🔓 [Fast Company] Social media companies are using AI and face scans to spot more kids on their platforms  
  <https://www.fastcompany.com/91599859/instagram-meta-openai-age-checks-verification>
- `[ 24]` [STAT News] STAT+: FDA clears Stryker’s ‘surgical cockpit’ that uses Apple’s VR headset, Vision Pro  
  <https://www.statnews.com/2026/09/01/fda-stryker-surgical-cockpit-apple-vr-headset-health-tech/?utm_campaign=rss>
- `[ 12]` 🔓 [Forbes Innovation] The Human Premium  
  <https://www.forbes.com/sites/cathyrubin/2026/09/01/the-human-premium/>
- `[ 22]` [Kagi Small Web] Kevlin Henney on Code Refactoring – Semaphore  
  <https://wiert.me/2026/09/01/kevlin-henney-on-code-refactoring-semaphore/>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (7)

- **[🤖 AI/ML & Tech]** `score 36` — Your leaders are not okay  
  Issue: `clickbait`  
  <https://www.fastcompany.com/91595175/your-leaders-are-not-okay>
- **[🌍 Climate & Energy]** `score 29` — Edouardo forms, NHC worries  
  Issue: `duplicate`  
  <https://enkiops.org/2026/09/01/edouardo-forms-nhc-worries/>
- **[🏛️ Architecture & Design]** `score 30` — Donald Trump's Capital Makeover  
  Issue: `clickbait`  
  <https://www.newyorker.com/magazine/2026/09/14/donald-trumps-capital-makeover>
- **[🏛️ Architecture & Design]** `score 34` — Rental Revamp: How Two Budding Besties Built a Full-On Addition to Their L.A. Home  
  Issue: `clickbait`  
  <https://www.dwell.com/article/rental-revamp-cami-arboles-rockii-navarro-silver-lake-los-angeles-7456b8ab>
- **[🚀 Sci-Fi & Culture]** `score 15` — Hulu buried one of its smartest sci-fi thrillers inside a sinister Silicon Valley lab  
  Issue: `clickbait`  
  <https://www.makeuseof.com/hulu-buried-smartest-sci-fi-thrillers-inside-sinister-silicon-valley-lab/>
- **[🚀 Sci-Fi & Culture]** `score 29` — Final Fantasy 7 Revelation boss is "very much aware" you hate Chadley for being a socially inept doofus, but he will soon have "a very integral part" in the story anyway  
  Issue: `clickbait`  
  <https://www.gamesradar.com/games/final-fantasy/final-fantasy-7-revelation-boss-is-very-much-aware-you-hate-chadley-for-being-a-socially-inept-doofus-but-he-will-soon-have-a-very-integral-part-in-the-story-anyway/>
- **[🌿 Health & Wellness]** `score 22` — Social media companies are using AI and face scans to spot more kids on their platforms  
  Issue: `clickbait`  
  <https://www.fastcompany.com/91599859/instagram-meta-openai-age-checks-verification>

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 79 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 41 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏛️ Architecture & Design** has 30 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏠 Homelab & DIY** has 36 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌾 Homestead & Hobby Farm** has 8 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 31 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏔️ Williams Lake Local** is dominated by **My Cariboo Now** (23 articles, 50%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **📰 General News** has 110 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🥾 Outdoors & Recreation** has 7 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 31 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (27.1) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🚀 Sci-Fi & Culture** has 9 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌿 Health & Wellness** has 56 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 7 article(s) should be removed (`clickbait` ×6, `duplicate` ×1) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 11 feeds · 556 articles · 2026-09-06 16:14 UTC_
