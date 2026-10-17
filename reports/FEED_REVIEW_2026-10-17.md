# Feed Scoring & Scrubbing Report

_Generated: 2026-10-17 16:39 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 11 |
| Total articles | 417 |
| Stale articles (>48h) | 309 |
| Scrub pass | ✅ ran |
| Flagged for removal | 2 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 90 | 🟡 46.9 | 38–64 | 63 | WIRED (9) |
| 🌍 Climate & Energy | 38 | 🔴 37.9 | 14–71 | 31 | WIRED (4) |
| 🏛️ Architecture & Design | 28 | 🟡 45.4 | 38–63 | 22 | ArchDaily (16) |
| 🏠 Homelab & DIY | 26 | 🔴 41.4 | 18–60 | 20 | Hackster News (5) |
| 🌾 Homestead & Hobby Farm | 12 | 🔴 39.0 | 18–57 | 9 | Hobby Farms (3) |
| 🏔️ Williams Lake Local | 40 | 🟡 64.5 | 0–91 | 23 | Williams Lake Tribune (14) |
| 📰 General News | 70 | 🟡 56.8 | 16–80 | 51 | NYT Top Stories (9) |
| 🥾 Outdoors & Recreation | 9 | 🔴 33.6 | 22–56 | 9 | Outside Online (3) |
| 🔬 Science | 42 | 🟡 48.7 | 36–64 | 34 | ScienceDaily (10) |
| 🚀 Sci-Fi & Culture | 8 | 🔴 22.9 | 5–45 | 6 | Gizmodo (1) |
| 🌿 Health & Wellness | 54 | 🔴 42.9 | 10–73 | 41 | ScienceDaily (9) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 90 (90 scored)
- **Score**: avg 46.9 | min 38 | max 64
- **Stale** (>48h): 63
- **Avg age**: 74.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ ██                     8
  40–49   │ ████████████████████  57
  50–59   │ ████████              23
  60–69   │                        2
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| WIRED | 9 | 10% |
| The Atlantic | 7 | 8% |
| TechRadar | 7 | 8% |
| Tom's Hardware | 7 | 8% |
| Business Insider | 6 | 7% |
| TechCrunch | 4 | 4% |
| ZDNet | 4 | 4% |
| Ars Technica Technology Lab | 3 | 3% |

### 🔴 🌍 Climate & Energy

- **Articles**: 38 (38 scored)
- **Score**: avg 37.9 | min 14 | max 71
- **Stale** (>48h): 31
- **Avg age**: 81.1h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ████                   3
  20–29   │ █████████              6
  30–39   │ ████████████████████  13
  40–49   │ ███████████████       10
  50–59   │ ██████                 4
  60–69   │ █                      1
  70–79   │ █                      1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| WIRED | 4 | 11% |
| NRDC | 3 | 8% |
| New Atlas | 3 | 8% |
| InsideEVs | 3 | 8% |
| Quartz | 3 | 8% |
| Fast Company | 2 | 5% |
| The Guardian Global Development | 2 | 5% |
| TechCrunch | 2 | 5% |

**Low-score articles (≤30):**

- `[ 29]` [Hyperallergic] This Ron DeSantis Statue Can’t Take the Heat  
  <https://hyperallergic.com/this-ron-desantis-statue-cant-take-the-heat/>
- `[ 14]` [Business Insider] For Alejandro González Iñárritu, the scariest part of making 'Digger' wasn't the climate catastrophe  
  <https://www.businessinsider.com/digger-ending-plot-twists-explained-alejandro-gonzalez-inarritu-tom-cruise-2026-10>
- `[ 22]` [New Atlas] Tri-motor hyper-hatch lands as Peugeot's fastest car ever  
  <https://newatlas.com/automotive/peugeot-e-t16-concept-paris-motor-show-2026/>
- `[ 24]` [CleanTechnica] Another Sign That Gasmobiles Are Toast: Honda Adds Muscle To The Wireless EV Charging Movement  
  <https://news.google.com/rss/articles/CBMimgFBVV95cUxPWFE5WFNxU3pPSENHdmRJUzRnaU9QUUpjQWRHTmxRN1VsT3hoRmo5czBheEJ0NDRUbFJ1eS1DMVpIU21Hd0pjZndKU0NWR2xXSnRZam5felF1Ujdtamo3WUdMTDlUbzZZcUFfMUZvLUlMSXhqX2EwczNDYU1hV1RwU2ZNTGM2eWZiUjJmZm5sSWk3WWdBRzR5aUtB?oc=5>
- `[ 19]` [InsideEVs] EV Sales Rebound To Their Highest Level In A Year  
  <https://insideevs.com/news/811825/ev-sales-q3-2026/>
- `[ 22]` [New Atlas] The minivan strikes back as Renault debuts next-gen E-Space concept  
  <https://newatlas.com/automotive/renault-e-space-concept-paris-motor-show-2026/>
- `[ 24]` [InsideEVs] Volkswagen’s Family Of Cheap EVs Already Looks Like A Hit  
  <https://insideevs.com/news/811680/vw-ev-sales-growing-europe/>
- `[ 14]` [Al Jazeera English] Two deaths reported as Hurricane Simon, storm Rachel batter Mexico’s coast  
  <https://www.aljazeera.com/news/2026/10/12/two-deaths-reported-as-hurricane-simon-storm-rachel-batter-mexicos-coast?traffic_source=rss>
- `[ 20]` [New Atlas] Adorable retro EV concept takes the battle to cheap Chinese rivals  
  <https://newatlas.com/automotive/citroen-2-cv-concept-paris-motor-show-2026/>

### 🟡 🏛️ Architecture & Design

- **Articles**: 28 (28 scored)
- **Score**: avg 45.4 | min 38 | max 63
- **Stale** (>48h): 22
- **Avg age**: 77.2h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ █                      2
  40–49   │ ████████████████████  22
  50–59   │ ██                     3
  60–69   │                        1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ArchDaily | 16 | 57% ⚠️ |
| Dezeen | 7 | 25% |
| Architizer | 2 | 7% |
| Vox | 1 | 4% |
| New Atlas | 1 | 4% |
| Canadian Forest Industries | 1 | 4% |

### 🔴 🏠 Homelab & DIY

- **Articles**: 26 (26 scored)
- **Score**: avg 41.4 | min 18 | max 60
- **Stale** (>48h): 20
- **Avg age**: 80.5h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      1
  20–29   │ ██                     2
  30–39   │ █████                  4
  40–49   │ ████████████████████  14
  50–59   │ █████                  4
  60–69   │ █                      1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hackster News | 5 | 19% |
| Hackaday | 5 | 19% |
| Adafruit Blog | 4 | 15% |
| XDA Developers | 3 | 12% |
| Popular Woodworking | 3 | 12% |
| New Atlas | 2 | 8% |
| Make Magazine | 1 | 4% |
| LoRaMeshDevices | 1 | 4% |

**Low-score articles (≤30):**

- `[ 20]` [New Atlas] Shape-shifting camper van makes space for shop's worth of action gear  
  <https://newatlas.com/campervans/storyteller-gear-mode-hauler-camper-van/>
- `[ 23]` 2026 Hackaday Supercon: Workshops are Open!  
  <https://hackaday.com/2026/10/14/2026-hackaday-supercon-workshops-are-open/>
- `[ 18]` [Bambu Lab Blog] Our 3D Printers Just Won Two Parenting Awards  
  <https://blog.bambulab.com/our-3d-printers-just-won-two-parenting-awards/>

### 🔴 🌾 Homestead & Hobby Farm

- **Articles**: 12 (12 scored)
- **Score**: avg 39.0 | min 18 | max 57
- **Stale** (>48h): 9
- **Avg age**: 79.5h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ████                   1
  20–29   │ ████████████           3
  30–39   │                        0
  40–49   │ ████████████████████   5
  50–59   │ ████████████           3
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hobby Farms | 3 | 25% |
| Small Farm Canada | 2 | 17% |
| Country Guide | 1 | 8% |
| CleanTechnica | 1 | 8% |
| The Guardian Global Development | 1 | 8% |
| Canadian Mining Journal | 1 | 8% |
| Civil Eats | 1 | 8% |
| Resilience.org | 1 | 8% |

**Low-score articles (≤30):**

- `[ 20]` [Hobby Farms] Feeding Pumpkin to Chickens: A Mash Recipe  
  <https://www.hobbyfarms.com/recipe-fall-pumpkin-or-squash-mash-chickens/>
- `[ 20]` [Hobby Farms] Apple Tea: How to Make This Fall Recipe  
  <https://www.hobbyfarms.com/recipe-welcome-fall-embrace-nature-with-some-apple-tea/>
- `[ 18]` [Canadian Mining Journal] Boreal Orchards signs ‘re:moss’ deal with major Canadian mining company  
  <https://www.canadianminingjournal.com/news/boreal-orchards-signs-remoss-deal-with-major-canadian-mining-company/>
- `[ 22]` [Maryam Philpott] The Cherry Orchard – Harold Pinter Theatre  
  <https://maryamphilpottblog.wordpress.com/2026/10/12/the-cherry-orchard-harold-pinter-theatre/>

### 🟡 🏔️ Williams Lake Local

- **Articles**: 40 (40 scored)
- **Score**: avg 64.5 | min 0 | max 91
- **Stale** (>48h): 23
- **Avg age**: 60.5h
- **Local-flagged**: 40 (1 with score=0 via local override)

**Score distribution:**
```
  0–9     │ █                      1
  10–19   │ ███                    2
  20–29   │ ███                    2
  30–39   │ █                      1
  40–49   │ █                      1
  50–59   │ ██████████             6
  60–69   │ ██████████             6
  70–79   │ ████████████████████  11
  80–89   │ ██████████████         8
  90–100  │ ███                    2
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 14 | 35% |
| Cariboo Signals Reviews | 6 | 15% |
| My Cariboo Now | 6 | 15% |
| Quesnel Cariboo Observer | 5 | 12% |
| 100 Mile Free Press | 4 | 10% |
| The Tyee | 3 | 8% |
| BC Wildfire Service | 1 | 2% |
| My East Kootenay Now | 1 | 2% |

**Low-score articles (≤30):**

- `[  0]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, October 17, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-17.html>
- `[ 29]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, October 16, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-16.html>
- `[ 16]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, October 15, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-15.html>
- `[ 24]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, October 14, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-14.html>
- `[ 16]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, October 13, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-13.html>

### 🟡 📰 General News

- **Articles**: 70 (70 scored)
- **Score**: avg 56.8 | min 16 | max 80
- **Stale** (>48h): 51
- **Avg age**: 74.5h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        1
  20–29   │ ███                    6
  30–39   │ █                      3
  40–49   │                        1
  50–59   │ ███████               14
  60–69   │ ████████████████████  40
  70–79   │ ██                     4
  80–89   │                        1
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| NYT Top Stories | 9 | 13% |
| NYT Business | 7 | 10% |
| Williams Lake Tribune | 6 | 9% |
| The Tyee | 5 | 7% |
| TechRadar | 5 | 7% |
| Al Jazeera English | 3 | 4% |
| Scientific American | 3 | 4% |
| The Atlantic Culture | 3 | 4% |

**Low-score articles (≤30):**

- `[ 29]` [Al Jazeera English] Healthcare crisis escalating in Yemen’s besieged Taiz  
  <https://www.aljazeera.com/video/newsfeed/2026/10/17/healthcare-crisis-escalating-in-yemens-besieged-taiz?traffic_source=rss>
- `[ 16]` [Al Jazeera English] Iran war live: IRGC says supertanker hit naval mine in Hormuz, catches fire  
  <https://www.aljazeera.com/news/liveblog/2026/10/17/draft-2?traffic_source=rss>
- `[ 28]` [The Guardian Global Development] Saudi Arabia to execute man for being at protests and funerals when he was 15  
  <https://www.theguardian.com/global-development/2026/oct/16/saudi-arabia-to-execute-man-for-being-at-protests-and-funerals-when-he-was-15>
- `[ 27]` 🔓 [NYT Top Stories] How U.S. Support to Ukraine Has Evolved Under Trump  
  <https://www.nytimes.com/2026/10/15/us/politics/ukraine-us-aid-trump.html>
- `[ 22]` [The Guardian Global Development] LGBTQ+ people go into hiding in Senegal as hundreds are arrested  
  <https://www.theguardian.com/global-development/2026/oct/15/senegal-homosexuality-criminalised-anti-lgbtq-arrests-hiv-testing-human-rights-watch>
- `[ 30]` 🔓 [NYT Top Stories] Trump Hands Victories to Putin, Who Offers More War in Return  
  <https://www.nytimes.com/2026/10/13/world/europe/russia-putin-trump-diesel-ukraine.html>
- `[ 27]` [TechRadar] Azerbaijan blocks TikTok, Instagram, and X amid growing protests over hijab rules  
  <https://www.techradar.com/vpn/vpn-services/azerbaijan-blocks-tiktok-instagram-and-x-amid-growing-hijab-protests>
- `[ 26]` 🔓 [NYT Top Stories] NATO Details Plan to Shield Ukraine’s European Allies From Russia  
  <https://www.nytimes.com/2026/10/12/world/europe/nato-strategy-russia-europe.html>
- `[ 30]` [Committee to Protect Journalists] At least 37 journalists detained, several assaulted, while covering protests against India’s election chief  
  <https://cpj.org/2026/10/at-least-37-journalists-detained-several-assaulted-while-covering-protests-against-indias-election-chief/>

### 🔴 🥾 Outdoors & Recreation

- **Articles**: 9 (9 scored)
- **Score**: avg 33.6 | min 22 | max 56
- **Stale** (>48h): 9
- **Avg age**: 82.1h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ████████████████████   4
  30–39   │ ███████████████        3
  40–49   │ █████                  1
  50–59   │ █████                  1
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Outside Online | 3 | 33% |
| Live for the Outdoors (Country Walking) | 2 | 22% |
| AFAR | 1 | 11% |
| MakeUseOf | 1 | 11% |
| Trip Reports | 1 | 11% |
| Bicycling | 1 | 11% |

**Low-score articles (≤30):**

- `[ 23]` 🔓 [AFAR] Where to Fish, Hike, and Unwind in Reno Tahoe  
  <https://www.afar.com/magazine/where-to-fish-hike-and-unwind-in-reno-tahoe>
- `[ 27]` 🔓 [Outside Online] A Missing Dog Survived 34 Days in Yellowstone National Park. Rescuers Just Saved Her.  
  <https://www.outsideonline.com/outdoor-adventure/exploration-survival/yellowstone-dog-luna/>
- `[ 22]` [MakeUseOf] I turned on one Galaxy setting, and my mobile bill got much smaller  
  <https://www.makeuseof.com/galaxy-mobile-data-warning-limit/>
- `[ 25]` 🔓 [Bicycling] Bikepacking America's Longest Multiuse Trail Network  
  <https://www.bicycling.com/rides/a74107699/bikepacking-empire-state-trail-americas-longest-multiuse-trail-network/>

### 🟡 🔬 Science

- **Articles**: 42 (42 scored)
- **Score**: avg 48.7 | min 36 | max 64
- **Stale** (>48h): 34
- **Avg age**: 79.2h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ ███                    4
  40–49   │ ████████████████████  25
  50–59   │ ████████              11
  60–69   │ █                      2
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 10 | 24% |
| ScienceAlert | 7 | 17% |
| Scientific American | 5 | 12% |
| MIT Technology Review | 4 | 10% |
| WIRED | 2 | 5% |
| Singularity Hub | 2 | 5% |
| Quanta Magazine | 2 | 5% |
| MIT News | 2 | 5% |

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 8 (8 scored)
- **Score**: avg 22.9 | min 5 | max 45
- **Stale** (>48h): 6
- **Avg age**: 79.4h

**Score distribution:**
```
  0–9     │ ██████                 1
  10–19   │ █████████████          2
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
| Gizmodo | 1 | 12% |
| Wikipedia  - Recent changes [en] | 1 | 12% |
| Colossal | 1 | 12% |
| Reactor Magazine | 1 | 12% |
| TechRadar | 1 | 12% |
| mjulius | 1 | 12% |
| The Verge | 1 | 12% |
| Scientific American | 1 | 12% |

**Low-score articles (≤30):**

- `[ 14]` [Gizmodo] Zendaya to Star in Alex Garland’s Next Sci-Fi Movie  
  <https://news.google.com/rss/articles/CBMiiAFBVV95cUxPTUlGM2N4THJEWWhaOUxrOERsZXlBRGk3WWVwa0JWVmllazJhbnQ2U0hXamE3YnU3eENpaDYxRV9kQlNTTjh3U19heTRQRXNULUlmN3JmUVBGQkszZTNLeGZjZEtwemxrOTFlbVFoZEthTVpfaHI1ODNfNG9ZemRHRTJudzY4bEd5?oc=5>
- `[  5]` [Wikipedia  - Recent changes [en]] Joseph Quinn  
  <https://en.wikipedia.org/w/index.php?title=Joseph_Quinn&diff=1380506894&oldid=1380177420>
- `[ 24]` [Colossal] Welcome to the ‘Uncanny Valley,’ the Haas Brothers’ Fantastic and Cheeky Universe  
  <https://www.thisiscolossal.com/2026/10/haas-brothers-uncanny-valley-austin-exhibition/>
- `[ 26]` [Reactor Magazine] Jo Walton’s Reading List: September 2026  
  <https://reactormag.com/jo-waltons-reading-list-september-2026/>
- `[ 17]` [TechRadar] 'I’d love to do a proper sci-fi score one day' — Control Resonant composer shares what kind of game he'd like to work on next, says 'one thing is sure: I’m not much good for a My Little Pony game'  
  <https://www.techradar.com/gaming/id-love-to-do-a-proper-sci-fi-score-one-day-control-resonant-composer-shares-what-kind-of-game-hed-like-to-work-on-next-says-one-thing-is-sure-im-not-much-good-for-a-my-little-pony-game>
- `[ 21]` 🔓 [The Verge] No Man’s Sky is coming to the iPhone and iPad  
  <https://www.theverge.com/entertainment/1009541/no-mans-sky-iphone-ipad-launch-date>

### 🔴 🌿 Health & Wellness

- **Articles**: 54 (54 scored)
- **Score**: avg 42.9 | min 10 | max 73
- **Stale** (>48h): 41
- **Avg age**: 77.1h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      2
  20–29   │ ████                   5
  30–39   │ █████████             10
  40–49   │ ████████████████████  22
  50–59   │ ██████████            11
  60–69   │ ██                     3
  70–79   │                        1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 9 | 17% |
| NYT Well | 5 | 9% |
| ScienceAlert | 5 | 9% |
| Scientific American | 4 | 7% |
| Fast Company | 3 | 6% |
| NYT Top Stories | 3 | 6% |
| Business Insider | 3 | 6% |
| NPR Health News | 2 | 4% |

**Low-score articles (≤30):**

- `[ 27]` 🔓 [NYT Top Stories] Pope Leo Has Lung Cancer, Vatican Says  
  <https://www.nytimes.com/2026/10/13/world/europe/pope-leo-lung-surgery.html>
- `[ 27]` 🔓 [Fast Company] Anthropic apparently offering $190,000 for an executive assistant, despite agentic AI advances  
  <https://www.fastcompany.com/91623067/anthropic-apparently-offering-190000-for-an-executive-assistant-despite-agentic-ai-advances>
- `[ 23]` 🔓 [Fast Company] 3 leadership lessons from AI-powered companies  
  <https://www.fastcompany.com/91621833/3-leadership-lessons-from-ai-powered-companies>
- `[ 24]` 🔓 [Scientific American] Sex-changing mouse clones may help fight to save endangered species  
  <https://www.scientificamerican.com/article/sex-changing-mouse-clones-may-help-fight-to-save-endangered-species/>
- `[ 10]` [Small Farm Canada] Women Farmers Face Hidden Airborne Risks  
  <https://www.smallfarmcanada.ca/news/women-farmers-face-hidden-airborne-risks/>
- `[ 10]` [ScienceAlert] A Cheap Deworming Pill Could Help Beat Drug-Resistant Lung Cancer  
  <https://www.sciencealert.com/a-cheap-deworming-pill-could-help-beat-drug-resistant-lung-cancer>
- `[ 26]` [ScienceAlert] Bones, Liver, And Blood Fats All Shift Abruptly at Menopause, Huge Study Finds  
  <https://www.sciencealert.com/bones-liver-and-blood-fats-all-shift-abruptly-at-menopause-huge-study-finds>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (2)

- **[🌍 Climate & Energy]** `score 38` — Everyone Hates ‘Digger.’ It’s the Perfect Climate Movie  
  Issue: `clickbait`  
  <https://www.wired.com/story/everyone-hates-digger-its-perfect-climate-movie/>
- **[🌍 Climate & Energy]** `score 20` — Adorable retro EV concept takes the battle to cheap Chinese rivals  
  Issue: `clickbait`  
  <https://newatlas.com/automotive/citroen-2-cv-concept-paris-motor-show-2026/>

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 63 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 31 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏛️ Architecture & Design** has 22 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏛️ Architecture & Design** is dominated by **ArchDaily** (16 articles, 57%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **🏠 Homelab & DIY** has 20 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌾 Homestead & Hobby Farm** has 9 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 23 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **📰 General News** has 51 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🥾 Outdoors & Recreation** has a low average score (33.6) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🥾 Outdoors & Recreation** has 9 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 34 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (22.9) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🚀 Sci-Fi & Culture** has 6 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌿 Health & Wellness** has 41 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 2 article(s) should be removed (`clickbait` ×2) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 11 feeds · 417 articles · 2026-10-17 16:39 UTC_
