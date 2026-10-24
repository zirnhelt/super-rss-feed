# Feed Scoring & Scrubbing Report

_Generated: 2026-10-24 16:51 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 11 |
| Total articles | 513 |
| Stale articles (>48h) | 373 |
| Scrub pass | ✅ ran |
| Flagged for removal | 0 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 90 | 🟡 52.5 | 39–64 | 71 | Business Insider (8) |
| 🌍 Climate & Energy | 48 | 🔴 43.8 | 20–67 | 38 | CleanTechnica (8) |
| 🏛️ Architecture & Design | 29 | 🟡 46.6 | 37–59 | 22 | ArchDaily (15) |
| 🏠 Homelab & DIY | 32 | 🔴 41.2 | 20–63 | 22 | Popular Woodworking (10) |
| 🌾 Homestead & Hobby Farm | 19 | 🔴 39.7 | 15–64 | 14 | Hobby Farms (4) |
| 🏔️ Williams Lake Local | 48 | 🟢 70.9 | 0–100 | 32 | Williams Lake Tribune (22) |
| 📰 General News | 121 | 🟡 62.0 | 12–85 | 83 | NYT Top Stories (22) |
| 🥾 Outdoors & Recreation | 19 | 🔴 32.5 | 14–74 | 13 | Outside Online (7) |
| 🔬 Science | 43 | 🟡 51.4 | 35–65 | 34 | ScienceDaily (12) |
| 🚀 Sci-Fi & Culture | 9 | 🔴 22.8 | 8–36 | 5 | Kottke.org (2) |
| 🌿 Health & Wellness | 55 | 🔴 41.4 | 10–69 | 39 | STAT News (5) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 90 (90 scored)
- **Score**: avg 52.5 | min 39 | max 64
- **Stale** (>48h): 71
- **Avg age**: 76.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        1
  40–49   │ ████████████          28
  50–59   │ ████████████████████  44
  60–69   │ ███████               17
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Business Insider | 8 | 9% |
| Tom's Hardware | 8 | 9% |
| TechRadar | 7 | 8% |
| TechCrunch | 6 | 7% |
| Gizmodo | 5 | 6% |
| Fast Company | 4 | 4% |
| Ars Technica Technology Lab | 3 | 3% |
| Engadget | 3 | 3% |

### 🔴 🌍 Climate & Energy

- **Articles**: 48 (48 scored)
- **Score**: avg 43.8 | min 20 | max 67
- **Stale** (>48h): 38
- **Avg age**: 70.9h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ██                     2
  30–39   │ ████████████████████  17
  40–49   │ ███████████████       13
  50–59   │ ███████████████       13
  60–69   │ ███                    3
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| CleanTechnica | 8 | 17% |
| Fast Company | 3 | 6% |
| Quartz | 2 | 4% |
| MIT Technology Review | 2 | 4% |
| The Verge | 2 | 4% |
| ScienceAlert | 2 | 4% |
| Gizmodo | 2 | 4% |
| APTN News | 1 | 2% |

**Low-score articles (≤30):**

- `[ 20]` 🔓 [Fast Company] Stefan Sagmeister’s new shoe designs are actually walking infographics  
  <https://www.fastcompany.com/91623596/stefan-sagmeisters-new-shoe-designs-are-actually-walking-infographics>
- `[ 22]` [MacRumors] GM Says Apple Wallet Car Keys Coming to These Vehicles  
  <https://www.macrumors.com/2026/10/19/gm-vehicles-iphone-apple-wallet-car-keys/>

### 🟡 🏛️ Architecture & Design

- **Articles**: 29 (29 scored)
- **Score**: avg 46.6 | min 37 | max 59
- **Stale** (>48h): 22
- **Avg age**: 80.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ █                      2
  40–49   │ ████████████████████  21
  50–59   │ █████                  6
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ArchDaily | 15 | 52% ⚠️ |
| Dezeen | 6 | 21% |
| Dwell | 4 | 14% |
| Architizer | 2 | 7% |
| Country Life | 1 | 3% |
| Fast Company | 1 | 3% |

### 🔴 🏠 Homelab & DIY

- **Articles**: 32 (32 scored)
- **Score**: avg 41.2 | min 20 | max 63
- **Stale** (>48h): 22
- **Avg age**: 77.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ██████████             8
  30–39   │ ████                   3
  40–49   │ ████████████████████  15
  50–59   │ ████                   3
  60–69   │ ████                   3
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Popular Woodworking | 10 | 31% |
| Adafruit Blog | 5 | 16% |
| Hackaday | 3 | 9% |
| Hackster News | 3 | 9% |
| XDA Developers | 2 | 6% |
| Bicycling | 1 | 3% |
| Android Authority | 1 | 3% |
| MIT News | 1 | 3% |

**Low-score articles (≤30):**

- `[ 27]` 🔓 [Popular Woodworking] The Splinter Report: October 23rd  
  <https://www.popularwoodworking.com/editors-blog/the-splinter-report-october-23rd/>
- `[ 24]` [Adafruit Blog] Meshtastic Lilygo T-Deck Case – 2-Piece Snap-Together with Internal Ribbon Antenna #3DThursday #3DPrinting  
  <https://blog.adafruit.com/2026/10/22/meshtastic-lilygo-t-deck-case-2-piece-snap-together-with-internal-ribbon-antenna-3dthursday-3dprinting/>
- `[ 29]` [Hackster News] Garmin Reopens Its Connect Developer Program for Fitness Wearable Data — With New Business Tiers  
  <https://www.hackster.io/news/garmin-reopens-its-connect-developer-program-for-fitness-wearable-data-with-new-business-tiers-8d657d04723b>
- `[ 22]` [cotidianulagricol.ro] Agriculture groups launch training and scholarships to build farm workforce  
  <https://www.cotidianulagricol.ro/anfa-si-bayer-lanseaza-o-initiativa-de-formare-dedicata-femeilor-din-agricultura-in-cadrul-evenimentului-femei-care-hranesc-romania/>
- `[ 22]` [ArchDaily] Creative Rebellion: Design, Knowledge and Experimentation at interihotel MAD26  
  <https://www.archdaily.com/1186753/creative-rebellion-design-knowledge-and-experimentation-at-interihotel-mad26>
- `[ 20]` 🔓 [Popular Woodworking] ShopNotes Podcast Episode 289 — Pitchin’, Y’all  
  <https://www.popularwoodworking.com/editors-blog/shopnotes-podcast-episode-289-pitchin-yall/>
- `[ 25]` 🔓 [Macworld] ‘HomeView Ultra’ with robot arm may be coming next year  
  <https://www.macworld.com/article/3263708/homeview-ultra-with-robot-arm-may-be-coming-next-year.html>
- `[ 29]` [Hackster News] Olimex Launches Two New Open-Hardware Bidirectional Level Shifters, for Breadboards and UEXT  
  <https://www.hackster.io/news/olimex-launches-two-new-open-hardware-bidirectional-level-shifters-for-breadboards-and-uext-1610f4cdf15c>

### 🔴 🌾 Homestead & Hobby Farm

- **Articles**: 19 (19 scored)
- **Score**: avg 39.7 | min 15 | max 64
- **Stale** (>48h): 14
- **Avg age**: 67.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █████████████          4
  20–29   │ ██████                 2
  30–39   │ ███                    1
  40–49   │ ████████████████████   6
  50–59   │ ████████████████       5
  60–69   │ ███                    1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hobby Farms | 4 | 21% |
| RealAgriculture | 3 | 16% |
| CleanTechnica | 1 | 5% |
| farmonaut.com | 1 | 5% |
| The Tyee | 1 | 5% |
| The Western Producer | 1 | 5% |
| Small Wooden House Plans | Micro Cabin Plans | Garden Shed Plans | Cottage Blueprints | 1 | 5% |
| agrifocusafrica.com | 1 | 5% |

**Low-score articles (≤30):**

- `[ 15]` [Hobby Farms] Pumpkins for Chickens: 4 Ways Your Birds Can Benefit  
  <https://www.hobbyfarms.com/four-ways-pumpkin-can-benefit-chickens/>
- `[ 15]` [Hobby Farms] Black Chickens: Popular and Perfect for Spooky Season  
  <https://www.hobbyfarms.com/2-spooky-chickens-real-farmers-cant-afford-3/>
- `[ 15]` [Hobby Farms] Turnip Jack-O’-Lantern: The Original Halloween Tradition  
  <https://www.hobbyfarms.com/turnip-jack-o-lantern/>
- `[ 22]` [AgWeb] Sixth-Grader, Secret Agent: How One Missouri 4-H Member Is Mastering Western Heritage Shooting  
  <https://news.google.com/rss/articles/CBMisAFBVV95cUxPWVBsQ2k5NUlGblF0bGJDSFk1dHhWUUdvTnRFbzA1bVJSbUFmbFljTEtueW9TN0VseWF1ekxDcEFWNGh1YWx0ZERZb1RRU1dpdWJGcUszVGc3Qmx3WUpVZDY5c0FVVEFzSGJzM01xV2hMUXlGWERkMHpzbnlpTElnRUoxUVdlUm02Um0xeXQ1OHcyclJmNVBzZk5WWi02dGpYYmhPVExOLW1RRG5KWUl2ZA?oc=5>
- `[ 18]` [MIT Technology Review] Nebraska native explores galaxies far, far away  
  <https://www.technologyreview.com/2026/10/20/1145294/nebraska-native-explores-galaxies-far-far-away/>
- `[ 26]` [Dezeen] Golf clubhouse by Graham Baba nods to farm structures in rural Washington  
  <https://www.dezeen.com/2026/10/19/golf-clubhouse-graham-baba-washington-architects/>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 48 (48 scored)
- **Score**: avg 70.9 | min 0 | max 100
- **Stale** (>48h): 32
- **Avg age**: 68.0h
- **Local-flagged**: 48 (1 with score=0 via local override)

**Score distribution:**
```
  0–9     │ █                      1
  10–19   │ ████                   3
  20–29   │ ███                    2
  30–39   │                        0
  40–49   │ ██████                 4
  50–59   │ ███                    2
  60–69   │ ██████                 4
  70–79   │ ████████████████      11
  80–89   │ ████████████████████  13
  90–100  │ ████████████           8
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 22 | 46% ⚠️ |
| 100 Mile Free Press | 6 | 12% |
| My Cariboo Now | 6 | 12% |
| Cariboo Signals Reviews | 5 | 10% |
| Quesnel Cariboo Observer | 5 | 10% |
| Regional News Archives - Williams Lake Tribune | 1 | 2% |
| CFJC Today Kamloops | 1 | 2% |
| BC Wildfire Service | 1 | 2% |

**Low-score articles (≤30):**

- `[  0]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, October 24, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-24.html>
- `[ 26]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, October 23, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-23.html>
- `[ 19]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, October 21, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-21.html>
- `[ 28]` 🔓 [Williams Lake Tribune] Sam Roberts Band, Owen Riegling to headline when the CPKC Holiday Train crosses B.C.  
  <https://wltribune.com/2026/10/20/sam-roberts-band-owen-riegling-to-headline-when-the-cpkc-holiday-train-crosses-b-c/>
- `[ 19]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, October 20, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-20.html>
- `[ 16]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, October 19, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-19.html>

### 🟡 📰 General News

- **Articles**: 121 (121 scored)
- **Score**: avg 62.0 | min 12 | max 85
- **Stale** (>48h): 83
- **Avg age**: 71.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        3
  20–29   │ ██                     9
  30–39   │                        1
  40–49   │                        2
  50–59   │                        3
  60–69   │ ████████████████████  65
  70–79   │ █████████             32
  80–89   │ █                      6
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| NYT Top Stories | 22 | 18% |
| Scientific American | 10 | 8% |
| NYT Business | 9 | 7% |
| WIRED | 9 | 7% |
| The Tyee | 8 | 7% |
| Al Jazeera English | 6 | 5% |
| The Atlantic | 6 | 5% |
| Hackaday | 5 | 4% |

**Low-score articles (≤30):**

- `[ 28]` 🔓 [NYT Top Stories] Iran in ‘Advanced Stages’ of Planning Attacks Against Americans, Officials Say  
  <https://www.nytimes.com/2026/10/23/us/politics/security-warnings-iran-threats.html>
- `[ 12]` [Al Jazeera English] Russia, Ukraine agree to Melania Trump-brokered localised ceasefire  
  <https://www.aljazeera.com/video/newsfeed/2026/10/23/russia-ukraine-agree-to-melania-trump-brokered-localised-ceasefire?traffic_source=rss>
- `[ 28]` [STAT News] STAT+: Treasury proposes major restrictions to U.S. investment in Chinese biotech sector  
  <https://www.statnews.com/2026/10/23/new-china-biotech-limits-coins-act-proposal-us-pharma-reaction/?utm_campaign=rss>
- `[ 24]` 🔓 [The Atlantic] Trump’s Gamble to End the Iran War  
  <https://www.theatlantic.com/national-security/2026/10/trump-iran-war-strikes-after-midterms/689121/?utm_source=feed>
- `[ 29]` [The Guardian Global Development] Tied up and tortured: Israel using US-made electroshock weapons on Palestinian detainees  
  <https://www.theguardian.com/global-development/2026/oct/22/israel-us-made-electroshock-weapons-palestinian-detainees-axon-taser>
- `[ 17]` 🔓 [NYT Top Stories] U.S. and Israel Draw Up Plans for Renewed Strikes on Iran After Elections  
  <https://www.nytimes.com/2026/10/21/us/politics/us-israel-renewed-iran-strikes.html>
- `[ 15]` [cbsnews.com] Russia frees detained American Stephen Hubbard during Ukraine peace talks  
  <https://www.cbsnews.com/news/russia-stephen-hubbard-freed-american-ukraine-war-witkoff-putin/>
- `[ 26]` [The Guardian Global Development] ‘I never saw my son, until they handed him over in a bag’: inside El Salvador’s brutal crime crackdown  
  <https://www.theguardian.com/global-development/2026/oct/21/el-salvador-crackdown-president-bukele-mass-arrest-allegations-torture-killing-prison>
- `[ 23]` 🔓 [NYT Top Stories] Voters in Oil-Rich Alberta Reject Leaving Canada  
  <https://www.nytimes.com/2026/10/19/world/canada/alberta-secession-canada-referendum.html>
- `[ 24]` 🔓 [NYT Top Stories] Indian Democracy Has Found New Life in the Streets  
  <https://www.nytimes.com/2026/10/20/opinion/india-voters-protests.html>
- `[ 20]` 🔓 [NYT Top Stories] Trump’s Push for Deals With Russia Powers His Frustration With Ukraine  
  <https://www.nytimes.com/2026/10/19/us/politics/trump-russia-deals.html>
- `[ 20]` 🔓 [NYT Top Stories] France Imposes Curfews in Parts of Paris and Other Cities After Nationwide Rioting  
  <https://www.nytimes.com/2026/10/19/world/europe/france-protests-riots.html>

### 🔴 🥾 Outdoors & Recreation

- **Articles**: 19 (19 scored)
- **Score**: avg 32.5 | min 14 | max 74
- **Stale** (>48h): 13
- **Avg age**: 75.5h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ████████████████████   6
  20–29   │ ██████████             3
  30–39   │ ██████████             3
  40–49   │ ████████████████████   6
  50–59   │                        0
  60–69   │                        0
  70–79   │ ███                    1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Outside Online | 7 | 37% |
| Business Insider | 2 | 11% |
| Live for the Outdoors (Country Walking) | 2 | 11% |
| Trip Reports | 1 | 5% |
| Chris Glass | 1 | 5% |
| Pique Newsmagazine | 1 | 5% |
| AFAR | 1 | 5% |
| PaddlingLight.com | 1 | 5% |

**Low-score articles (≤30):**

- `[ 14]` [Trip Reports] Replay along Shoshone Lake  
  <https://backcountrypost.com/threads/replay-along-shoshone-lake.12733/>
- `[ 15]` [Business Insider] My kids used to complain on every trail. These 4 changes made family hiking fun again.  
  <https://www.businessinsider.com/how-to-enjoy-family-hiking-with-young-kids-easy-tips-2026-10>
- `[ 20]` [Business Insider] I made a rookie flight-booking mistake that cost me $3,000. These are the 4 things I'll do differently next time.  
  <https://www.businessinsider.com/lessons-learned-from-flight-booking-mistake-costs-advice-2026-10>
- `[ 15]` [Chris Glass] Western Alpine Red Bus Tour  
  <https://chrisglass.com/2026/10/22/western-alpine-red-bus-tour/>
- `[ 20]` 🔓 [Outside Online] A Kayaker Put a Life Vest on Her Dog but Forgot Her Own. Luckily, Rescuers Saved the Day.  
  <https://www.outsideonline.com/outdoor-adventure/water-activities/dog-kayak-rescue-oregon/>
- `[ 27]` 🔓 [AFAR] How to Experience Reno and Lake Tahoe in One Trip  
  <https://www.afar.com/magazine/how-to-experience-reno-and-lake-tahoe-in-one-trip>
- `[ 15]` [guillaumemeigniez.me] Japanese Postcards  
  <https://guillaumemeigniez.me/blog/japan-postcards/>
- `[ 15]` [My East Kootenay Now] Cranbrook sani-dump to close for winter Tuesday  
  <https://www.myeastkootenaynow.com/58936/news/municipal-news/city-of-cranbrook/cranbrook-sani-dump-to-close-for-winter-tuesday/>
- `[ 17]` 🔓 [Forbes Innovation] iPhone Duo Pre-Order Catch-Up: Delivery Dates Leap From December To Launch Day  
  <https://www.forbes.com/sites/davidphelan/2026/10/19/iphone-duo-pre-order-catch-up-delivery-dates-leap-from-december-to-launch-day/>

### 🟡 🔬 Science

- **Articles**: 43 (43 scored)
- **Score**: avg 51.4 | min 35 | max 65
- **Stale** (>48h): 34
- **Avg age**: 81.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        1
  40–49   │ █████████████         16
  50–59   │ ████████████████████  24
  60–69   │ █                      2
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 12 | 28% |
| Scientific American | 10 | 23% |
| WIRED | 4 | 9% |
| ScienceAlert | 3 | 7% |
| Quanta Magazine | 2 | 5% |
| New Atlas | 2 | 5% |
| MIT Technology Review | 2 | 5% |
| news.climate.columbia.edu | 1 | 2% |

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 9 (9 scored)
- **Score**: avg 22.8 | min 8 | max 36
- **Stale** (>48h): 5
- **Avg age**: 68.3h

**Score distribution:**
```
  0–9     │ ██████                 1
  10–19   │ ████████████████████   3
  20–29   │ █████████████          2
  30–39   │ ████████████████████   3
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
| Kottke.org | 2 | 22% |
| Gizmodo | 2 | 22% |
| Adam Whitehead | 1 | 11% |
| Strange Horizons | 1 | 11% |
| Hunter Allen | 1 | 11% |
| Neowin | 1 | 11% |
| Nautilus | 1 | 11% |

**Low-score articles (≤30):**

- `[ 18]` [Adam Whitehead] Iconic BATTLESTAR GALACTICA board game to be reprinted  
  <https://thewertzone.blogspot.com/2026/10/iconic-battlestar-galactica-board-game.html>
- `[  8]` [Hunter Allen] Census Bloodbath: I know what you did last prom night  
  <http://www.kinemalogue.net/2026/10/census-bloodbath-i-know-what-you-did.html>
- `[ 20]` [Gizmodo] ‘Cyberpunk: Edgerunners 2’ Had One Rule: Don’t Look Like Season One  
  <https://news.google.com/rss/articles/CBMirAFBVV95cUxPbGJ0Nnotbk1VODJOdG1XeFduc1k4M3p2U2ZFQWlERHVTUEh4bHlVOHVQUVhJQ0dVOTZFcTNLWEdwQXNuTUs5OEhhVHNjSmM2dWVIN244c19qQTJlc2JmakZERG1NbTk5MnJBVkVGZWg0NHpvV2ZLdkFndE01bHIzMzZpMzZLV0FBLVBXU1hEQmFIMmZrcnpyMXp5UXI3Y18ySG40UkVWS2FsTkZC?oc=5>
- `[ 22]` [Gizmodo] Daisy Ridley Has an Oceanic Sci-Fi Fantasy Series in the Works  
  <https://news.google.com/rss/articles/CBMimAFBVV95cUxQb2RtVmxuTHNiNzQ0YW5icE9XaE9SWDREOFlNSEJxUzFLWjNSMEl0ckM2T2kyeHdmWm9INEZHWXV4dFppa1dPcW4wcmpEQXBoNGRoNEZ3WXJJVm0tMTZyeXkyODFqblJGcG5XX1hINGQ2R1BIdFhYcHd4UmV3UWJuSzh1cHZISmxmWlN6OW1QVElXWXc5d2FrUw?oc=5>
- `[ 15]` [Neowin] AMD driver 26.10.1 lands with Call of Duty: MW4 and Final Fantasy Resonance support  
  <https://www.neowin.net/news/amd-driver-26101-lands-with-call-of-duty-mw4-and-final-fantasy-resonance-support/?utm_source=rss>
- `[ 18]` [Nautilus] “It Feels Like Something Out of Science Fiction”: Astronomers Find First Green Star  
  <https://nautil.us/it-feels-like-something-out-of-science-fiction-astronomers-find-first-green-star-1285927/>

### 🔴 🌿 Health & Wellness

- **Articles**: 55 (55 scored)
- **Score**: avg 41.4 | min 10 | max 69
- **Stale** (>48h): 39
- **Avg age**: 78.5h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██                     3
  20–29   │ █████                  6
  30–39   │ ███████████           12
  40–49   │ ████████████████████  21
  50–59   │ ████████               9
  60–69   │ ███                    4
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| STAT News | 5 | 9% |
| KFF Health News | 5 | 9% |
| ScienceDaily | 5 | 9% |
| ScienceAlert | 5 | 9% |
| Scientific American | 4 | 7% |
| NYT Well | 4 | 7% |
| Being Patient | 3 | 5% |
| Nautilus | 2 | 4% |

**Low-score articles (≤30):**

- `[ 30]` [Business Insider] Amazon is buying billions in Nvidia AI systems it can't yet turn on  
  <https://www.businessinsider.com/amazon-nvidia-ai-gpu-data-centers-power-shortages-2026-10>
- `[ 24]` [ScienceDaily] Scientists finally uncover why statins can cause muscle pain  
  <https://www.sciencedaily.com/releases/2026/10/261019093447.htm>
- `[ 21]` [Being Patient] VOICES: The Young Person Behind the Diagnosis: From Lived Experience to Professional Purpose  
  <https://beingpatient.com/voices-young-onset-alzheimers-daughter-dementia-advocacy/>
- `[ 25]` [NPR Health News] The Ebola crisis is far outpacing the response, Congo's IRC director says  
  <https://www.npr.org/2026/10/19/nx-s1-6005499/the-ebola-crisis-is-far-outpacing-the-response-congos-irc-director-says>
- `[ 10]` [TechCrunch] Apple updates guidelines to ban nudify apps masquerading as regular apps to pass review  
  <https://techcrunch.com/2026/10/19/apple-updates-guidelines-to-ban-nudify-apps-masquerading-as-regular-apps-to-pass-review/>
- `[ 10]` [ScienceDaily] A simple touch can bring dying corals back to life in just 7 weeks  
  <https://www.sciencedaily.com/releases/2026/10/261017230025.htm>
- `[ 29]` 🔓 [Scientific American] The mechanics of honeybee stingers, microplastic health risks and new findings on postmenopausal ovaries  
  <https://www.scientificamerican.com/podcast/episode/the-mechanics-of-honeybee-stingers-microplastic-health-risks-and-new-findings-on-postmenopausal-ovaries/>
- `[ 10]` [ScienceDaily] "Mind-blowing" Alzheimer’s breakthrough: Two hours of sleep restored without clearing brain plaques  
  <https://www.sciencedaily.com/releases/2026/10/261018084421.htm>
- `[ 29]` [KFF Health News] Four Red Flags and One Truth Amid the Peptide Hype  
  <https://kffhealthnews.org/public-health/peptide-hype-experimental-unproven-drugs-red-flags/>
- `[ 20]` [KFF Health News] Readers Are Pleading To Make American Healthcare Greater  
  <https://kffhealthnews.org/letter-to-the-editor/readers-plead-make-american-healthcare-greater-dementia-care-sedation-er-triage-upcoding-october-2026/>

---

## Scrub Pass Findings

### ⚠️ Borderline but Acceptable (1)

- **[🌍 Climate & Energy]** `score 37` — UN warns record El Niño could disrupt weather into 2027  
  Note: `duplicate`

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 71 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 38 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏛️ Architecture & Design** has 22 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏛️ Architecture & Design** is dominated by **ArchDaily** (15 articles, 52%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **🏠 Homelab & DIY** has 22 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌾 Homestead & Hobby Farm** has 14 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 32 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏔️ Williams Lake Local** is dominated by **Williams Lake Tribune** (22 articles, 46%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **📰 General News** has 83 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🥾 Outdoors & Recreation** has a low average score (32.5) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🥾 Outdoors & Recreation** has 13 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 34 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (22.8) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🌿 Health & Wellness** has 39 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.

---

_Report generated by `score_scrub_report.py` · 11 feeds · 513 articles · 2026-10-24 16:51 UTC_
