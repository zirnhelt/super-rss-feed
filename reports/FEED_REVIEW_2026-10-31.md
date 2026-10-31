# Feed Scoring & Scrubbing Report

_Generated: 2026-10-31 18:00 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 11 |
| Total articles | 477 |
| Stale articles (>48h) | 351 |
| Scrub pass | ✅ ran |
| Flagged for removal | 0 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 82 | 🟡 50.3 | 43–64 | 62 | TechRadar (7) |
| 🌍 Climate & Energy | 58 | 🔴 42.3 | 10–70 | 44 | CleanTechnica (12) |
| 🏛️ Architecture & Design | 27 | 🔴 44.3 | 33–59 | 21 | ArchDaily (15) |
| 🏠 Homelab & DIY | 32 | 🔴 44.3 | 16–68 | 21 | Adafruit Blog (9) |
| 🌾 Homestead & Hobby Farm | 13 | 🔴 43.2 | 18–60 | 8 | RealAgriculture (2) |
| 🏔️ Williams Lake Local | 52 | 🟡 66.1 | 0–100 | 30 | Williams Lake Tribune (19) |
| 📰 General News | 106 | 🟡 61.1 | 19–85 | 81 | NYT Top Stories (12) |
| 🥾 Outdoors & Recreation | 7 | 🔴 38.4 | 12–59 | 4 | Outside Online (3) |
| 🔬 Science | 43 | 🟡 51.0 | 30–65 | 37 | ScienceDaily (13) |
| 🚀 Sci-Fi & Culture | 5 | 🔴 28.0 | 10–42 | 4 | Boing Boing (1) |
| 🌿 Health & Wellness | 52 | 🔴 41.5 | 10–56 | 39 | STAT News (6) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 82 (82 scored)
- **Score**: avg 50.3 | min 43 | max 64
- **Stale** (>48h): 62
- **Avg age**: 75.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │ ████████████████████  50
  50–59   │ ██████████            26
  60–69   │ ██                     6
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| TechRadar | 7 | 9% |
| Adafruit Blog | 6 | 7% |
| WIRED | 5 | 6% |
| Tom's Hardware | 5 | 6% |
| NYT Business | 4 | 5% |
| TechCrunch | 3 | 4% |
| Scientific American | 3 | 4% |
| Forbes Innovation | 3 | 4% |

### 🔴 🌍 Climate & Energy

- **Articles**: 58 (58 scored)
- **Score**: avg 42.3 | min 10 | max 70
- **Stale** (>48h): 44
- **Avg age**: 76.2h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      2
  20–29   │ █                      2
  30–39   │ ███████████████       19
  40–49   │ ████████████████████  25
  50–59   │ ████                   5
  60–69   │ ███                    4
  70–79   │                        1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| CleanTechnica | 12 | 21% |
| InsideEVs | 4 | 7% |
| Gizmodo | 3 | 5% |
| NRDC | 3 | 5% |
| New Atlas | 2 | 3% |
| The Tyee | 2 | 3% |
| The Verge | 2 | 3% |
| MIT News | 1 | 2% |

**Low-score articles (≤30):**

- `[ 30]` [CleanTechnica] BYD’s Doubling Production in Brazil  
  <https://cleantechnica.com/2026/10/27/byds-doubling-production-in-brazil/>
- `[ 10]` [CleanTechnica] US President Trump Will Absolutely Love This New Underwater Renewable Energy Machine  
  <https://cleantechnica.com/2026/10/26/renewable-energy-kite-harvests-underwater-tides/>
- `[ 27]` [InsideEVs] Audi Recalls 9,048 Q4 E-Trons Because The Battery Could Catch On Fire  
  <https://insideevs.com/news/813290/audi-q4-etron-battery-recall/>
- `[ 29]` [InsideEVs] Chery Joins China’s EV Charging Race With A Bold Promise  
  <https://insideevs.com/news/813243/chery-ultra-fast-charging-demonstration/>
- `[ 10]` [dagenslantbruk.se] Swedish farmers’ federation says spring budget leaves input-cost crisis unresolved  
  <http://www.dagenslantbruk.se/lantbrukets-kostnadskris-la-mnas-ola-st>

### 🔴 🏛️ Architecture & Design

- **Articles**: 27 (27 scored)
- **Score**: avg 44.3 | min 33 | max 59
- **Stale** (>48h): 21
- **Avg age**: 76.3h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ ███████                6
  40–49   │ ████████████████████  17
  50–59   │ ████                   4
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ArchDaily | 15 | 56% ⚠️ |
| Dezeen | 6 | 22% |
| Architizer | 2 | 7% |
| Popular Woodworking | 1 | 4% |
| New Atlas | 1 | 4% |
| Canadian Architect | 1 | 4% |
| Articles - passivehouseplus.co.uk | 1 | 4% |

### 🔴 🏠 Homelab & DIY

- **Articles**: 32 (32 scored)
- **Score**: avg 44.3 | min 16 | max 68
- **Stale** (>48h): 21
- **Avg age**: 69.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      1
  20–29   │ █████                  4
  30–39   │ ██                     2
  40–49   │ ████████████████████  14
  50–59   │ ████████████           9
  60–69   │ ██                     2
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Adafruit Blog | 9 | 28% |
| Popular Woodworking | 4 | 12% |
| Hackaday | 4 | 12% |
| LoRaMeshDevices | 2 | 6% |
| Make Magazine | 2 | 6% |
| Paul Buetow aka snonux | 1 | 3% |
| Colossal | 1 | 3% |
| blog.zolty.systems | 1 | 3% |

**Low-score articles (≤30):**

- `[ 20]` [Colossal] 17th-Century Embroidery Meets Hand-Carved Wooden Vessels by Aspen Golann  
  <https://www.thisiscolossal.com/2026/10/aspen-golann-woodworking-embroidery-vessels-sculpture/>
- `[ 22]` [LoRaMeshDevices] Experience Seamless Connectivity and Long-Range Communication with LILYGO T-Beam Meshtastic LORA32 915MHz ESP32  
  <https://www.lorameshdevices.com/lilygo-t-beam-meshtastic-lora32-915mhz-esp32-ttgo-development-board-wifi-ble-ch9102f-chip-soldered-oled-module-meshtstic-version>
- `[ 16]` [Adafruit Blog] Twisty Stress-Relief Eyeball #3DThursday #3DPrinting  
  <https://blog.adafruit.com/2026/10/29/twisty-stress-relief-eyeball-3dthursday-3dprinting/>
- `[ 24]` [Atlas Obscura] Hazelnut Inn in Chilliwack, British Columbia  
  <https://www.atlasobscura.com/places/hazelnut-inn>
- `[ 22]` [fullmetalbrackets.com] Streamers are becoming like cable and video games prices are ridiculous, so I went back to pirating like the old days  
  <https://fullmetalbrackets.com/blog/streamers-are-becoming-like-cable-and-video-games-prices-are-ridiculous-so-i-went-back-to-pirating-like-the-old-days/>

### 🔴 🌾 Homestead & Hobby Farm

- **Articles**: 13 (13 scored)
- **Score**: avg 43.2 | min 18 | max 60
- **Stale** (>48h): 8
- **Avg age**: 72.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ████████               2
  20–29   │ ████                   1
  30–39   │ ████████               2
  40–49   │ ████████               2
  50–59   │ ████████████████████   5
  60–69   │ ████                   1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| RealAgriculture | 2 | 15% |
| Civil Eats | 2 | 15% |
| The Marginalian | 1 | 8% |
| Beekeeping365 | 1 | 8% |
| nnmt.net.vn | 1 | 8% |
| Kottke.org | 1 | 8% |
| AgWeb | 1 | 8% |
| comprerural.com | 1 | 8% |

**Low-score articles (≤30):**

- `[ 18]` [Beekeeping365] Telling the Bees  
  <https://beekeeping365.com/2026/10/30/telling-the-bees-2/>
- `[ 18]` [Kottke.org] Star Wars: The Radio Drama  
  <https://kottke.org/26/10/star-wars-the-radio-drama>
- `[ 22]` [comprerural.com] European farms build outdoor egg businesses as Kazakhstan adds 20,500-bird house  
  <https://www.comprerural.com/agricultor-cria-2-800-galinhas-entre-arvores-e-usa-alpacas-contra-predadores/>

### 🟡 🏔️ Williams Lake Local

- **Articles**: 52 (52 scored)
- **Score**: avg 66.1 | min 0 | max 100
- **Stale** (>48h): 30
- **Avg age**: 66.2h
- **Local-flagged**: 52 (1 with score=0 via local override)

**Score distribution:**
```
  0–9     │ █                      1
  10–19   │ ███████                4
  20–29   │                        0
  30–39   │ █████                  3
  40–49   │ █████████              5
  50–59   │ ██████████████         8
  60–69   │ █████                  3
  70–79   │ ████████████████████  11
  80–89   │ ████████████           7
  90–100  │ ██████████████████    10
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 19 | 37% |
| My Cariboo Now | 11 | 21% |
| 100 Mile Free Press | 9 | 17% |
| Cariboo Signals Reviews | 6 | 12% |
| Quesnel Cariboo Observer | 6 | 12% |
| BC Wildfire Service | 1 | 2% |

**Low-score articles (≤30):**

- `[  0]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, October 31, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-31.html>
- `[ 16]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, October 30, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-30.html>
- `[ 16]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, October 29, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-29.html>
- `[ 16]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, October 28, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-28.html>
- `[ 19]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, October 27, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-27.html>

### 🟡 📰 General News

- **Articles**: 106 (106 scored)
- **Score**: avg 61.1 | min 19 | max 85
- **Stale** (>48h): 81
- **Avg age**: 74.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        2
  20–29   │ ██                     5
  30–39   │ ██                     5
  40–49   │                        2
  50–59   │ ██████                15
  60–69   │ ████████████████████  45
  70–79   │ ████████████          29
  80–89   │ █                      3
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| NYT Top Stories | 12 | 11% |
| The Tyee | 9 | 8% |
| Al Jazeera English | 7 | 7% |
| NYT Business | 7 | 7% |
| The Atlantic | 7 | 7% |
| WIRED | 6 | 6% |
| TechRadar | 4 | 4% |
| The Verge | 4 | 4% |

**Low-score articles (≤30):**

- `[ 19]` [Al Jazeera English] Iran says four tankers on fire after striking mines in Hormuz  
  <https://www.aljazeera.com/video/newsfeed/2026/10/31/iran-says-four-tankers-on-fire-after-striking-mines-in-hormuz?traffic_source=rss>
- `[ 30]` 🔓 [NYT Business] Binance Grapples With ‘Security Incident’ That May Cause $6.3 Billion in Losses  
  <https://www.nytimes.com/2026/10/29/technology/binance-grapples-with-security-incident-that-may-cause-6-3-billion-in-losses.html>
- `[ 22]` [theguardian.com] China expels 33 senior officials as Xi tightens party discipline  
  <https://www.theguardian.com/world/2026/oct/30/china-expels-record-number-communist-party-xi-jinping-purges-officials-fifth-plenum>
- `[ 22]` 🔓 [NYT Top Stories] Vance Proposes Restarting Peace Talks in Outreach to Iranian Official  
  <https://www.nytimes.com/2026/10/28/us/politics/vance-peace-talks-letter-iran.html>
- `[ 19]` 🔓 [NYT Top Stories] Flávio Bolsonaro Lands in Miami After Fleeing Brazil  
  <https://www.nytimes.com/2026/10/28/world/americas/flavio-bolsonaro-us-miami-brazil-trump.html>
- `[ 20]` 🔓 [The Atlantic] Israeli Election Results Hazy, Try Again  
  <https://www.theatlantic.com/ideas/2026/10/israel-election-outcome-possibilities/689184/?utm_source=feed>
- `[ 30]` 🔓 [Forbes Innovation] Congo Reports Over 10,000 Ebola Cases, Sparking Concerns of Wider Spread  
  <https://www.forbes.com/sites/saibala/2026/10/27/congo-reports-over-10000-ebola-cases-sparking-concerns-of-wider-spread/>
- `[ 22]` [ScienceAlert] An Armored Amphibian That Lived Its Whole Life at Sea? It's a Fossil First  
  <https://www.sciencealert.com/an-armored-amphibian-that-lived-its-whole-life-at-sea-its-a-fossil-first>
- `[ 30]` [STAT News] STAT+: House lawmaker probes PBMs for ‘punitive’ audits of independent pharmacies  
  <https://www.statnews.com/pharmalot/2026/10/26/lawmaker-probes-pbms-for-punitive-audits-independent-pharmacies/?utm_campaign=rss>
- `[ 24]` [The Guardian Global Development] US forces accused of ‘weaponising’ Somalia’s floods by trapping women and children in the path of El Niño  
  <https://www.theguardian.com/global-development/2026/oct/26/us-forces-accused-of-weaponising-somalia-flood-el-nino>

### 🔴 🥾 Outdoors & Recreation

- **Articles**: 7 (7 scored)
- **Score**: avg 38.4 | min 12 | max 59
- **Stale** (>48h): 4
- **Avg age**: 64.0h

**Score distribution:**
```
  0–9     │                        0
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
| Outside Online | 3 | 43% |
| Live for the Outdoors (Country Walking) | 1 | 14% |
| The Road Goes Ever On | 1 | 14% |
| Wildfire Today | 1 | 14% |
| nautil.us | 1 | 14% |

**Low-score articles (≤30):**

- `[ 25]` 🔓 [Outside Online] Go Further in Québec’s Winter Wilderness  
  <https://www.outsideonline.com/adventure-travel/destinations/north-america/go-further-in-quebecs-winter-wilderness/>
- `[ 12]` [The Road Goes Ever On] Hiking Skywalk South  
  <https://mariaadey.com/2026/10/27/hiking-skywalk-south/>

### 🟡 🔬 Science

- **Articles**: 43 (43 scored)
- **Score**: avg 51.0 | min 30 | max 65
- **Stale** (>48h): 37
- **Avg age**: 79.2h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ █                      1
  40–49   │ █████████████████     17
  50–59   │ ████████████████████  20
  60–69   │ █████                  5
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 13 | 30% |
| ScienceAlert | 5 | 12% |
| Scientific American | 4 | 9% |
| Quanta Magazine | 3 | 7% |
| Nautilus | 2 | 5% |
| space.com | 1 | 2% |
| nasa.gov | 1 | 2% |
| Singularity Hub | 1 | 2% |

**Low-score articles (≤30):**

- `[ 30]` [space.com] ISS astronauts install seventh upgraded solar array during 100th US spacewalk  
  <https://www.space.com/space-exploration/international-space-station/100-us-spacewalks-from-the-iss-astronauts-deploy-new-solar-array-on-landmark-eva>

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 5 (5 scored)
- **Score**: avg 28.0 | min 10 | max 42
- **Stale** (>48h): 4
- **Avg age**: 73.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ████████████████████   2
  20–29   │                        0
  30–39   │ ████████████████████   2
  40–49   │ ██████████             1
  50–59   │                        0
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Boing Boing | 1 | 20% |
| Reactor Magazine | 1 | 20% |
| Scientific American | 1 | 20% |
| Edge (GamesRadar) | 1 | 20% |
| Péter Lodri | 1 | 20% |

**Low-score articles (≤30):**

- `[ 15]` 🔓 [Edge (GamesRadar)] CD Projekt Red can't stop updating Cyberpunk 2077: "Keeps giving us reasons to return to it"  
  <https://www.gamesradar.com/games/cyberpunk/cd-projekt-red-just-cant-stop-updating-cyberpunk-2077-this-world-keeps-giving-us-reasons-to-return-to-it/>
- `[ 10]` [Péter Lodri] Kárpátia — Tábori posta & The Brett Shaw Sci-Fi Cycle (Shaw-ciklus) — the dreamstate machine  
  <https://pocoo.vaked.dev/posts/2026-10-26-karpatia-tabori-posta-brett-shaw-cycle>

### 🔴 🌿 Health & Wellness

- **Articles**: 52 (52 scored)
- **Score**: avg 41.5 | min 10 | max 56
- **Stale** (>48h): 39
- **Avg age**: 78.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      2
  20–29   │                        0
  30–39   │ ███████████           16
  40–49   │ ████████████████████  28
  50–59   │ ████                   6
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| STAT News | 6 | 12% |
| Being Patient | 5 | 10% |
| ScienceAlert | 5 | 10% |
| ScienceDaily | 4 | 8% |
| Neuroscience News | 4 | 8% |
| KFF Health News | 4 | 8% |
| Forbes Innovation | 3 | 6% |
| Fast Company | 3 | 6% |

**Low-score articles (≤30):**

- `[ 11]` 🔓 [Fast Company] Former DOGE staffers say they just hacked Anthropic in less than 12 hours  
  <https://www.fastcompany.com/91630974/former-doge-staffers-say-they-just-hacked-anthropic-in-less-than-12-hours>
- `[ 10]` [ScienceAlert] Spiders Can Rack Up REM-Like Sleep Debt (And May Even Dream), Just Like Humans  
  <https://www.sciencealert.com/spiders-can-rack-up-rem-like-sleep-debt-and-may-even-dream-just-like-humans>

---

## Scrub Pass Findings

### ⚠️ Borderline but Acceptable (1)

- **[🌍 Climate & Energy]** `score 27` — Audi Recalls 9,048 Q4 E-Trons Because The Battery Could Catch On Fire  
  Note: `duplicate`

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 62 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 44 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏛️ Architecture & Design** has 21 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏛️ Architecture & Design** is dominated by **ArchDaily** (15 articles, 56%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **🏠 Homelab & DIY** has 21 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌾 Homestead & Hobby Farm** has 8 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 30 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **📰 General News** has 81 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 37 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌿 Health & Wellness** has 39 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.

---

_Report generated by `score_scrub_report.py` · 11 feeds · 477 articles · 2026-10-31 18:00 UTC_
