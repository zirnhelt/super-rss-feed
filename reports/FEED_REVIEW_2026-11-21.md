# Feed Scoring & Scrubbing Report

_Generated: 2026-11-21 20:17 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 11 |
| Total articles | 490 |
| Stale articles (>48h) | 388 |
| Scrub pass | ✅ ran |
| Flagged for removal | 0 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 87 | 🟡 50.5 | 42–64 | 66 | WIRED (6) |
| 🌍 Climate & Energy | 58 | 🟡 45.7 | 32–64 | 51 | CleanTechnica (9) |
| 🏛️ Architecture & Design | 25 | 🔴 40.5 | 24–50 | 22 | ArchDaily (21) |
| 🏠 Homelab & DIY | 35 | 🔴 39.2 | 17–60 | 29 | Bambu Lab Community Forum - Latest posts (9) |
| 🌾 Homestead & Hobby Farm | 12 | 🔴 43.0 | 15–62 | 12 | Hobby Farms (5) |
| 🏔️ Williams Lake Local | 55 | 🟡 63.0 | 0–100 | 39 | Williams Lake Tribune (19) |
| 📰 General News | 112 | 🟡 58.4 | 0–90 | 81 | NYT Top Stories (14) |
| 🥾 Outdoors & Recreation | 13 | 🔴 33.5 | 17–57 | 12 | Outside Online (7) |
| 🔬 Science | 35 | 🟡 51.0 | 46–67 | 28 | ScienceDaily (7) |
| 🚀 Sci-Fi & Culture | 4 | 🔴 24.2 | 15–33 | 4 | CleanTechnica (1) |
| 🌿 Health & Wellness | 54 | 🔴 44.0 | 10–77 | 44 | ScienceDaily (6) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 87 (87 scored)
- **Score**: avg 50.5 | min 42 | max 64
- **Stale** (>48h): 66
- **Avg age**: 76.8h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │ ████████████████████  43
  50–59   │ ████████████████      36
  60–69   │ ███                    8
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| WIRED | 6 | 7% |
| NYT Business | 4 | 5% |
| TechRadar | 4 | 5% |
| Forbes Innovation | 4 | 5% |
| TechCrunch | 4 | 5% |
| ZDNet | 3 | 3% |
| Tom's Hardware | 3 | 3% |
| Fast Company | 3 | 3% |

### 🟡 🌍 Climate & Energy

- **Articles**: 58 (58 scored)
- **Score**: avg 45.7 | min 32 | max 64
- **Stale** (>48h): 51
- **Avg age**: 84.1h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ █████                  9
  40–49   │ ████████████████████  32
  50–59   │ ██████████            16
  60–69   │                        1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| CleanTechnica | 9 | 16% |
| Scientific American | 3 | 5% |
| CNET | 2 | 3% |
| WIRED | 2 | 3% |
| Psychology Headlines Around the World | 2 | 3% |
| ABC News | 2 | 3% |
| InsideEVs | 2 | 3% |
| Nautilus | 2 | 3% |

### 🔴 🏛️ Architecture & Design

- **Articles**: 25 (25 scored)
- **Score**: avg 40.5 | min 24 | max 50
- **Stale** (>48h): 22
- **Avg age**: 87.8h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ██                     2
  30–39   │ █████                  5
  40–49   │ ████████████████████  17
  50–59   │ █                      1
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ArchDaily | 21 | 84% ⚠️ |
| Canadian Architect | 1 | 4% |
| The Atlantic Culture | 1 | 4% |
| Adafruit Blog | 1 | 4% |
| 3D Printing Industry | 1 | 4% |

**Low-score articles (≤30):**

- `[ 24]` [ArchDaily] Link House / Openideas Architects  
  <https://www.archdaily.com/1010840/link-house-openideas-architects>
- `[ 29]` [ArchDaily] Brazil in Focus: This Month in Architecture, Cultural Heritage and Climate Resilience  
  <https://www.archdaily.com/1188685/brazil-in-focus-this-month-in-architecture-cultural-heritage-and-climate-resilience>

### 🔴 🏠 Homelab & DIY

- **Articles**: 35 (35 scored)
- **Score**: avg 39.2 | min 17 | max 60
- **Stale** (>48h): 29
- **Avg age**: 77.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██                     2
  20–29   │ ██████                 5
  30–39   │ ████████               7
  40–49   │ ████████████████████  16
  50–59   │ █████                  4
  60–69   │ █                      1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Bambu Lab Community Forum - Latest posts | 9 | 26% |
| Adafruit Blog | 5 | 14% |
| MakeUseOf | 3 | 9% |
| 3D Printing Industry | 3 | 9% |
| Popular Woodworking | 3 | 9% |
| smarthomeassistent.de | 3 | 9% |
| XDA Developers | 1 | 3% |
| simon42.com | 1 | 3% |

**Low-score articles (≤30):**

- `[ 20]` [Bambu Lab Community Forum - Latest posts] Bambu Labs E1 is here  
  <https://forum.bambulab.com/t/bambu-labs-e1-is-here/263088#post_16>
- `[ 18]` [MakeUseOf] I self-host almost everything, but these subscriptions are still worth paying for  
  <https://www.makeuseof.com/subscriptions-worth-paying-for-even-when-you-self-host/>
- `[ 20]` [homekits.de] IKEA lists Liljebagge radiator thermostat for €14.99 in Germany  
  <https://homekits.de/ikea-liljebagge-im-deutschen-ikea-onlineshop-gelistet/>
- `[ 22]` [homekitnews.com] Aqara launches six Matter lights with Thread and Zigbee  
  <https://homekitnews.com/2026/11/17/aqara-launches-six-new-smart-lights-with-matter-over-thread-zigbee/>
- `[ 17]` 🔓 [Fast Company] The ‘recession indicators’ visible at your workplace  
  <https://www.fastcompany.com/91641298/the-recession-indicators-visible-at-your-workplace>
- `[ 22]` 🔓 [Popular Mechanics] How to Turn Dad’s Garage Into the Ultimate DIY Workshop  
  <https://www.popularmechanics.com/home/tools/a74334314/how-to-turn-dads-garage-into-the-ultimate-diy-workshop/>
- `[ 22]` [phoronix.com] Purism seeks 2,500 preorders for $1,599 RISC-V Linux phone  
  <https://www.phoronix.com/news/Librem-5-v2-Announced>

### 🔴 🌾 Homestead & Hobby Farm

- **Articles**: 12 (12 scored)
- **Score**: avg 43.0 | min 15 | max 62
- **Stale** (>48h): 12
- **Avg age**: 94.2h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █████                  1
  20–29   │ █████                  1
  30–39   │ ██████████             2
  40–49   │ ███████████████        3
  50–59   │ ████████████████████   4
  60–69   │ █████                  1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hobby Farms | 5 | 42% ⚠️ |
| RealAgriculture | 3 | 25% |
| agro-tv.ro | 1 | 8% |
| dagenslantbruk.se | 1 | 8% |
| Small Farm Canada | 1 | 8% |
| northernag.net | 1 | 8% |

**Low-score articles (≤30):**

- `[ 15]` [Hobby Farms] What Can Chickens Eat? A Guide to Holiday Leftovers  
  <https://www.hobbyfarms.com/8-tips-for-sharing-holiday-leftovers-with-your-chickens/>
- `[ 20]` [Hobby Farms] Chicken Coop Decorating Ideas: Safe and Festive for Christmas  
  <https://www.hobbyfarms.com/decorating-chicken-coops-for-christmas/>

### 🟡 🏔️ Williams Lake Local

- **Articles**: 55 (55 scored)
- **Score**: avg 63.0 | min 0 | max 100
- **Stale** (>48h): 39
- **Avg age**: 68.1h
- **Local-flagged**: 55 (4 with score=0 via local override)

**Score distribution:**
```
  0–9     │ ██████                 4
  10–19   │ █                      1
  20–29   │ █                      1
  30–39   │ █████                  3
  40–49   │ █████████████          8
  50–59   │ ███████████████        9
  60–69   │ ██████                 4
  70–79   │ █████████████          8
  80–89   │ ████████               5
  90–100  │ ████████████████████  12
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 19 | 35% |
| 100 Mile Free Press | 12 | 22% |
| My Cariboo Now | 9 | 16% |
| Quesnel Cariboo Observer | 7 | 13% |
| Cariboo Signals Reviews | 6 | 11% |
| Tŝilhqot’in National Government | 1 | 2% |
| BC Wildfire Service | 1 | 2% |

**Low-score articles (≤30):**

- `[  0]` [Cariboo Signals Reviews] Episode Review — Cariboo Local Affairs, November 21, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-21.html>
- `[ 10]` [Cariboo Signals Reviews] Episode Review — Wild Spaces & Outdoor Life, November 20, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-20.html>
- `[  0]` [Cariboo Signals Reviews] Episode Review — Indigenous Lands & Innovation, November 19, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-19.html>
- `[  0]` [Cariboo Signals Reviews] Episode Review — Repair Culture & Practical Tech, November 18, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-18.html>
- `[  0]` [Cariboo Signals Reviews] Episode Review — Working Lands & Industry, November 17, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-17.html>
- `[ 20]` [Cariboo Signals Reviews] Episode Review — Arts, Culture & Digital Storytelling, November 16, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-16.html>

### 🟡 📰 General News

- **Articles**: 112 (111 scored)
- **Score**: avg 58.4 | min 0 | max 90
- **Stale** (>48h): 81
- **Avg age**: 73.8h

**Score distribution:**
```
  0–9     │                        2
  10–19   │ █                      4
  20–29   │ ██                     8
  30–39   │ █                      5
  40–49   │                        2
  50–59   │ █                      4
  60–69   │ ████████████████████  60
  70–79   │ ███████               22
  80–89   │ █                      3
  90–100  │                        1
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| NYT Top Stories | 14 | 12% |
| NYT Business | 13 | 12% |
| Scientific American | 13 | 12% |
| The Guardian Global Development | 7 | 6% |
| Hackaday | 7 | 6% |
| The Tyee | 6 | 5% |
| The Atlantic | 6 | 5% |
| Cariboo Signals Reviews | 5 | 4% |

**Low-score articles (≤30):**

- `[  0]` [Cariboo Signals Reviews] Episode Review — Cariboo Local Affairs, November 21, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-21.html>
- `[ 28]` [Al Jazeera English] Gen Z protests sweep Europe over wars, rising costs and climate  
  <https://www.aljazeera.com/video/newsfeed/2026/11/21/gen-z-protests-sweep-europe-over-wars-rising-costs-and-climate?traffic_source=rss>
- `[ 16]` [Al Jazeera English] Denmark expels Russian diplomat over alleged plot to kill Ukrainian rapper  
  <https://www.aljazeera.com/news/2026/11/21/denmark-expels-russian-diplomat-over-alleged-plot-to-kill-ukrainian-rapper?traffic_source=rss>
- `[  0]` [Cariboo Signals Reviews] Episode Review — Wild Spaces & Outdoor Life, November 20, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-20.html>
- `[ 29]` [404 Media] High-End Furniture Marketplace AptDeco Is Taking People’s Furniture and Not Paying Them  
  <https://www.404media.co/high-end-furniture-marketplace-aptdeco-is-taking-peoples-furniture-and-not-paying-them/>
- `[ 24]` [middleeastmonitor.com] Gulf states condemn Iranian strikes as Kuwait reserves right to respond  
  <https://www.middleeastmonitor.com/20261118-kuwait-condemns-repeated-iranian-attacks-reserves-right-to-respond/>
- `[ 18]` [Cariboo Signals Reviews] Episode Review — Repair Culture & Practical Tech, November 18, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-18.html>
- `[ 24]` 🔓 [The Atlantic] The Iran War Has Slipped Into a Dangerous Limbo  
  <https://www.theatlantic.com/national-security/2026/11/iran-war-trump-limbo/689471/?utm_source=feed>
- `[ 12]` [arabtimesonline.com] Iran claims drone strike on US radar in Bahrain; CENTCOM denies damage  
  <https://www.arabtimesonline.com/news/irans-claim-of-striking-us-base-in-bahrain-is-false-centcom-declares/>
- `[ 18]` [Cariboo Signals Reviews] Episode Review — Working Lands & Industry, November 17, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-17.html>
- `[ 24]` 🔓 [NYT Business] As Trump and Xi Mingle, Their Governments Are Arming Up  
  <https://www.nytimes.com/2026/11/17/business/trump-xi-meeting-tensions.html>
- `[ 28]` [The Guardian Global Development] ‘I’m not ready to go to jail’: co-founder of Egypt’s last independent media outlet faces prison  
  <https://www.theguardian.com/global-development/2026/nov/17/lina-attalah-mada-masr-editor-egypt-independent-media-prison-censorship>
- `[ 24]` [english.aawsat.com] Iraq orders army into Iran-backed militia stronghold over oil-smuggling probe  
  <https://english.aawsat.com/node/5342044>
- `[ 28]` [The Guardian Global Development] ‘These men feel protected’: how Mexico’s first femicide squad is turning the tide on record killings  
  <https://www.theguardian.com/global-development/2026/nov/16/femicide-crisis-mexico-judge-killed-my-mother-one-more-time>

### 🔴 🥾 Outdoors & Recreation

- **Articles**: 13 (13 scored)
- **Score**: avg 33.5 | min 17 | max 57
- **Stale** (>48h): 12
- **Avg age**: 91.9h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ███                    1
  20–29   │ ██████████             3
  30–39   │ ████████████████████   6
  40–49   │ ███                    1
  50–59   │ ██████                 2
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Outside Online | 7 | 54% ⚠️ |
| Trip Reports | 1 | 8% |
| ABC News | 1 | 8% |
| Atlas Obscura | 1 | 8% |
| Live for the Outdoors (Country Walking) | 1 | 8% |
| Williams Lake Tribune | 1 | 8% |
| TechRadar | 1 | 8% |

**Low-score articles (≤30):**

- `[ 27]` 🔓 [Outside Online] Grand Theft Auto 6 Has an Entire National Park. I Spent the Night Exploring It.  
  <https://www.outsideonline.com/outdoor-adventure/exploration-survival/grand-theft-auto-6-national-park-mount-kalaga/>
- `[ 22]` [Atlas Obscura] Glass Wonders Gallery in Karpacz, Poland  
  <https://www.atlasobscura.com/places/glass-wonders-gallery>
- `[ 30]` 🔓 [Live for the Outdoors (Country Walking)] The most dangerous mountains in the UK – and the hiking routes causing the most issues  
  <https://www.livefortheoutdoors.com/hiking/advice/most-dangerous-mountains-in-the-uk/>
- `[ 22]` 🔓 [Outside Online] 3 Dead in Plane Crash on Remote North Rim of Grand Canyon National Park  
  <https://www.outsideonline.com/outdoor-adventure/exploration-survival/grand-canyon-north-rim-plane-crash/>
- `[ 17]` [TechRadar] 'Massive moments like this are prime hunting season for scammers': Surfshark joins the GTA VI excitement with an in-app easter egg — but warns of the risks the launch brings  
  <https://www.techradar.com/vpn/vpn-privacy-security/massive-moments-like-this-are-prime-hunting-season-for-scammers-surfshark-joins-the-gta-vi-excitement-with-an-in-app-easter-egg-but-warns-of-the-risks-the-launch-brings>
- `[ 30]` 🔓 [Outside Online] Why Your Body Is Begging You to Run More Trails Instead of Roads  
  <https://www.outsideonline.com/health/training-performance/road-vs-trail-running-muscle-damage-study/>

### 🟡 🔬 Science

- **Articles**: 35 (35 scored)
- **Score**: avg 51.0 | min 46 | max 67
- **Stale** (>48h): 28
- **Avg age**: 75.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │ ████████████████████  18
  50–59   │ ███████████████       14
  60–69   │ ███                    3
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 7 | 20% |
| Scientific American | 7 | 20% |
| MIT News | 3 | 9% |
| Quanta Magazine | 2 | 6% |
| scientificamerican.com | 2 | 6% |
| The Tyee | 2 | 6% |
| sciencealert.com | 2 | 6% |
| Williams Lake Tribune | 1 | 3% |

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 4 (4 scored)
- **Score**: avg 24.2 | min 15 | max 33
- **Stale** (>48h): 4
- **Avg age**: 79.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██████████             1
  20–29   │ ████████████████████   2
  30–39   │ ██████████             1
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
| CleanTechnica | 1 | 25% |
| Reactor Magazine | 1 | 25% |
| iansales | 1 | 25% |
| sherringham.net | 1 | 25% |

**Low-score articles (≤30):**

- `[ 15]` [CleanTechnica] The Return Of Project Hail Mary … And Next Steps For Artemis, Too  
  <https://cleantechnica.com/2026/11/19/the-return-of-project-hail-mary-and-next-steps-for-artemis-too/>
- `[ 20]` [Reactor Magazine] Cold War Science Fiction Stories That Imagine America’s Inevitable Defeat  
  <https://reactormag.com/cold-war-science-fiction-stories-that-imagine-americas-inevitable-defeat/>
- `[ 29]` [iansales] The Black Locomotive, Rian Hughes  
  <https://iansales.com/2026/11/18/the-black-locomotive-rian-hughes/>

### 🔴 🌿 Health & Wellness

- **Articles**: 54 (54 scored)
- **Score**: avg 44.0 | min 10 | max 77
- **Stale** (>48h): 44
- **Avg age**: 83.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      2
  20–29   │                        1
  30–39   │ ██████████            13
  40–49   │ ████████████████████  26
  50–59   │ ████                   6
  60–69   │ ███                    5
  70–79   │                        1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 6 | 11% |
| Being Patient | 5 | 9% |
| STAT News | 3 | 6% |
| ScienceAlert | 3 | 6% |
| NYT Well | 3 | 6% |
| Nautilus | 3 | 6% |
| Scientific American | 3 | 6% |
| CleanTechnica | 2 | 4% |

**Low-score articles (≤30):**

- `[ 21]` 🔓 [Outside Online] Astronaut Christina Koch Made History on Artemis II. But She Still Loves to Sleep in a Tent.  
  <https://www.outsideonline.com/outdoor-adventure/exploration-survival/2026-outsiders-of-the-year-christina-koch/>
- `[ 10]` [CleanTechnica] Environmental, Public Health Experts Testify During Public Hearings on Methane Pollution Rollback Proposal  
  <https://cleantechnica.com/2026/11/16/environmental-public-health-experts-testify-during-public-hearings-on-methane-pollution-rollback-proposal/>
- `[ 18]` [zdnet.com] AI agents expand cyber risks as companies struggle to enforce controls  
  <https://www.zdnet.com/innovation/google-cloud-ciso-perspectives-2027-ai-security-defenses/>

---

## Scrub Pass Findings

### ⚠️ Borderline but Acceptable (1)

- **[🏠 Homelab & DIY]** `score 20` — Bambu Labs E1 is here  
  Note: `clickbait`

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 66 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 51 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏛️ Architecture & Design** has 22 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏛️ Architecture & Design** is dominated by **ArchDaily** (21 articles, 84%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **🏠 Homelab & DIY** has 29 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌾 Homestead & Hobby Farm** has 12 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🌾 Homestead & Hobby Farm** is dominated by **Hobby Farms** (5 articles, 42%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **🏔️ Williams Lake Local** has 39 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **📰 General News** has 81 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🥾 Outdoors & Recreation** has a low average score (33.5) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🥾 Outdoors & Recreation** has 12 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🥾 Outdoors & Recreation** is dominated by **Outside Online** (7 articles, 54%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **🔬 Science** has 28 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌿 Health & Wellness** has 44 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.

---

_Report generated by `score_scrub_report.py` · 11 feeds · 490 articles · 2026-11-21 20:17 UTC_
