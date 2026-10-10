# Feed Scoring & Scrubbing Report

_Generated: 2026-10-10 18:03 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 11 |
| Total articles | 438 |
| Stale articles (>48h) | 336 |
| Scrub pass | ✅ ran |
| Flagged for removal | 1 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 84 | 🟡 47.8 | 37–62 | 56 | TechCrunch (7) |
| 🌍 Climate & Energy | 36 | 🔴 42.1 | 8–65 | 26 | InsideEVs (3) |
| 🏛️ Architecture & Design | 29 | 🟡 49.9 | 36–73 | 24 | ArchDaily (7) |
| 🏠 Homelab & DIY | 44 | 🔴 42.1 | 15–61 | 40 | Adafruit Blog (9) |
| 🌾 Homestead & Hobby Farm | 11 | 🔴 36.2 | 0–62 | 9 | Hobby Farms (3) |
| 🏔️ Williams Lake Local | 44 | 🟢 78.5 | 28–94 | 31 | My Cariboo Now (18) |
| 📰 General News | 70 | 🟡 59.2 | 9–76 | 53 | Hackaday (5) |
| 🥾 Outdoors & Recreation | 12 | 🔴 30.7 | 15–55 | 10 | Outside Online (4) |
| 🔬 Science | 41 | 🟡 51.4 | 42–71 | 34 | ScienceDaily (13) |
| 🚀 Sci-Fi & Culture | 9 | 🔴 26.9 | 5–49 | 5 | Open Culture (2) |
| 🌿 Health & Wellness | 58 | 🟡 51.5 | 10–70 | 48 | STAT News (8) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 84 (84 scored)
- **Score**: avg 47.8 | min 37 | max 62
- **Stale** (>48h): 56
- **Avg age**: 74.3h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ ██                     5
  40–49   │ ████████████████████  45
  50–59   │ █████████████         31
  60–69   │ █                      3
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| TechCrunch | 7 | 8% |
| Business Insider | 6 | 7% |
| The Verge | 6 | 7% |
| Fast Company | 6 | 7% |
| TechRadar | 6 | 7% |
| Scientific American | 5 | 6% |
| Neowin | 5 | 6% |
| NYT Top Stories | 4 | 5% |

### 🔴 🌍 Climate & Energy

- **Articles**: 36 (36 scored)
- **Score**: avg 42.1 | min 8 | max 65
- **Stale** (>48h): 26
- **Avg age**: 80.5h

**Score distribution:**
```
  0–9     │ ██                     2
  10–19   │ █████                  4
  20–29   │ █                      1
  30–39   │ ███████                6
  40–49   │ ██████                 5
  50–59   │ ████████████████████  16
  60–69   │ ██                     2
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| InsideEVs | 3 | 8% |
| Scientific American | 2 | 6% |
| Small Wooden House Plans | Micro Cabin Plans | Garden Shed Plans | Cottage Blueprints | 2 | 6% |
| New Atlas | 2 | 6% |
| CleanTechnica | 2 | 6% |
| Mother Jones | 2 | 6% |
| Resilience.org | 2 | 6% |
| The Atlantic | 1 | 3% |

**Low-score articles (≤30):**

- `[ 29]` 🔓 [Scientific American] How Hurricane Isaias got so dangerously strong so fast  
  <https://www.scientificamerican.com/article/how-hurricane-isaias-got-so-dangerously-strong-so-fast/>
- `[  8]` [Small Wooden House Plans | Micro Cabin Plans | Garden Shed Plans | Cottage Blueprints] 5 Professional Apartment Movers in South Florida for 2026  
  <https://www.pinuphouses.com/5-professional-apartment-movers-in-south-florida-for-2026/>
- `[ 10]` [Small Wooden House Plans | Micro Cabin Plans | Garden Shed Plans | Cottage Blueprints] Choosing Roofing Materials for North Texas Weather  
  <https://www.pinuphouses.com/choosing-roofing-materials-for-north-texas-weather/>
- `[ 11]` 🔓 [Fast Company] Coworkers say they distrust each other more than ever  
  <https://www.fastcompany.com/91619105/coworkers-distrust-each-other-now-more-than-ever-survey-suggests>
- `[ 18]` [philg] Elon Musk has made all of the world’s yachts more valuable  
  <https://philip.greenspun.com/blog/2026/10/06/elon-musk-has-made-all-of-the-worlds-yachts-more-valuable/>
- `[  8]` [ArchDaily] Announcement of the Finalists for the European Prize for Urban Public Space  
  <https://www.archdaily.com/1186412/announcement-of-the-finalists-for-the-european-prize-for-urban-public-space>
- `[ 18]` BYD Commercial Vehicle Sales Up 113% in September - CleanTechnica  
  <https://cleantechnica.com/2026/10/05/byd-commercial-vehicle-sales-up-113-in-september/>
- `[ 30]` [TechRadar] BYD is coming for Tesla's global EV sales crown, new sales figures reveal  
  <https://www.techradar.com/vehicle-tech/hybrid-electric-vehicles/tesla-model-y-tops-global-ev-sales-figures-again-but-new-report-reveals-byd-is-closing-fast-with-4-of-the-top-10-models>

### 🟡 🏛️ Architecture & Design

- **Articles**: 29 (29 scored)
- **Score**: avg 49.9 | min 36 | max 73
- **Stale** (>48h): 24
- **Avg age**: 82.1h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ ██                     2
  40–49   │ ████████████████████  15
  50–59   │ ██████████             8
  60–69   │ ████                   3
  70–79   │ █                      1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ArchDaily | 7 | 24% |
| Dezeen | 6 | 21% |
| Dwell | 4 | 14% |
| Country Life | 3 | 10% |
| Architizer | 2 | 7% |
| Canadian Architect | 1 | 3% |
| Articles - passivehouseplus.co.uk | 1 | 3% |
| WIRED | 1 | 3% |

### 🔴 🏠 Homelab & DIY

- **Articles**: 44 (44 scored)
- **Score**: avg 42.1 | min 15 | max 61
- **Stale** (>48h): 40
- **Avg age**: 81.3h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      1
  20–29   │ ██████████             9
  30–39   │ ████████               7
  40–49   │ ██████████             9
  50–59   │ ████████████████████  17
  60–69   │ █                      1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Adafruit Blog | 9 | 20% |
| Hackaday | 5 | 11% |
| MacRumors | 5 | 11% |
| Popular Woodworking | 5 | 11% |
| Hackster News | 4 | 9% |
| Tom's Hardware | 2 | 5% |
| CNET | 2 | 5% |
| Atlas Obscura | 1 | 2% |

**Low-score articles (≤30):**

- `[ 22]` [MacRumors] Leak Details iPhone Features for Apple's LG Home Accessories  
  <https://www.macrumors.com/2026/10/09/leak-details-iphone-features-for-home-accessories/>
- `[ 27]` 🔓 [Popular Woodworking] Work Begun  
  <https://www.popularwoodworking.com/arts-mysteries/work_begun/>
- `[ 20]` [Atlas Obscura] Museo Torre del Vino in Socuéllamos, Spain  
  <https://www.atlasobscura.com/places/museo-torre-del-vino>
- `[ 27]` 🔓 [Popular Woodworking] Plywood Tipper  
  <https://www.popularwoodworking.com/tricks/plywood-tipper/>
- `[ 20]` [ArchDaily] Belgium’s Architecture Offices Through the Lens of Marc Goodwin  
  <https://www.archdaily.com/1034289/belgiums-architecture-offices-through-the-lens-of-marc-goodwin>
- `[ 20]` [MacRumors] Apple Launches Creative Labs Program With The King's Trust  
  <https://www.macrumors.com/2026/10/07/apple-creative-labs-kings-trust/>
- `[ 30]` [Adafruit Blog] A terminal monitor for SDR hardware – written in Rust  
  <https://blog.adafruit.com/2026/10/07/a-terminal-monitor-for-sdr-hardware-written-in-rust/>
- `[ 22]` [MacRumors] Apple's Own Home Security Camera Still Coming Next Year  
  <https://www.macrumors.com/2026/10/07/apple-home-security-camera-still-coming-next-year/>
- `[ 22]` [MacRumors] Apple TV 4K Rumored to Support Four HomePods for Surround Sound  
  <https://www.macrumors.com/2026/10/06/apple-tv-4k-four-homepods-rumor/>
- `[ 15]` [MacRumors] HomePod Mini Waits Reach Eight Weeks Ahead of Rumored Refresh  
  <https://www.macrumors.com/2026/10/06/homepod-mini-waits-reach-eight-weeks/>
- `[ 20]` 🔓 [Popular Woodworking] Squirrel Surprise  
  <https://www.popularwoodworking.com/end-grain/squirrel-surprise/>

### 🔴 🌾 Homestead & Hobby Farm

- **Articles**: 11 (11 scored)
- **Score**: avg 36.2 | min 0 | max 62
- **Stale** (>48h): 9
- **Avg age**: 77.1h

**Score distribution:**
```
  0–9     │ ██████████             2
  10–19   │ █████                  1
  20–29   │ █████                  1
  30–39   │                        0
  40–49   │ ████████████████████   4
  50–59   │ ██████████             2
  60–69   │ █████                  1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hobby Farms | 3 | 27% |
| The Western Producer | 2 | 18% |
| Country Life | 2 | 18% |
| Country Guide | 1 | 9% |
| Beekeeping365 | 1 | 9% |
| Wikipedia  - Recent changes [en] | 1 | 9% |
| ahedderick.tumblr.com | 1 | 9% |

**Low-score articles (≤30):**

- `[ 15]` [Hobby Farms] Can Chickens Eat Green Beans?  
  <https://www.hobbyfarms.com/can-chickens-eat-green-beans/>
- `[ 22]` [Beekeeping365] One Cake a Day  
  <https://beekeeping365.com/2026/10/07/one-cake-a-day/>
- `[  0]` [Wikipedia  - Recent changes [en]] Cider  
  <https://en.wikipedia.org/w/index.php?title=Cider&diff=1378970670&oldid=1378970518>
- `[  5]` [ahedderick.tumblr.com] Move-along Monday  
  <https://ahedderick.tumblr.com/post/829646977621016576>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 44 (44 scored)
- **Score**: avg 78.5 | min 28 | max 94
- **Stale** (>48h): 31
- **Avg age**: 68.6h
- **Local-flagged**: 44

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        1
  30–39   │ █                      2
  40–49   │                        1
  50–59   │                        0
  60–69   │                        1
  70–79   │ ███████                9
  80–89   │ ████████████████████  25
  90–100  │ ████                   5
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| My Cariboo Now | 18 | 41% ⚠️ |
| Williams Lake Tribune | 15 | 34% |
| Cariboo Signals Reviews | 4 | 9% |
| 100 Mile Free Press | 3 | 7% |
| Quesnel Cariboo Observer | 3 | 7% |
| Regional News Archives - Williams Lake Tribune | 1 | 2% |

**Low-score articles (≤30):**

- `[ 28]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, October 9, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-10-09.html>

### 🟡 📰 General News

- **Articles**: 70 (70 scored)
- **Score**: avg 59.2 | min 9 | max 76
- **Stale** (>48h): 53
- **Avg age**: 78.3h

**Score distribution:**
```
  0–9     │                        1
  10–19   │ ██                     3
  20–29   │ ████                   6
  30–39   │ ██                     4
  40–49   │ █                      2
  50–59   │                        0
  60–69   │ ████████████████      24
  70–79   │ ████████████████████  30
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hackaday | 5 | 7% |
| NYT Top Stories | 5 | 7% |
| Committee to Protect Journalists | 5 | 7% |
| NYT Business | 5 | 7% |
| My Cariboo Now | 4 | 6% |
| The Tyee | 4 | 6% |
| The Atlantic | 4 | 6% |
| Al Jazeera English | 3 | 4% |

**Low-score articles (≤30):**

- `[ 12]` [Al Jazeera English] Putin tells Trump peace talks are unlikely, cites Ukraine drone attacks  
  <https://www.aljazeera.com/news/2026/10/10/putin-tells-trump-peace-talks-are-unlikely-cites-ukraine-drone-attacks?traffic_source=rss>
- `[  9]` [Al Jazeera English] Intercommunal clashes kill 71 people in South Sudan  
  <https://www.aljazeera.com/news/2026/10/10/intercommunal-clashes-kill-71-people-in-south-sudan?traffic_source=rss>
- `[ 17]` [Al Jazeera English] South Africa protests turn violent amid rage over asylum ruling  
  <https://www.aljazeera.com/news/2026/10/8/south-africa-protests-turn-violent-amid-rage-over-asylum-ruling?traffic_source=rss>
- `[ 26]` [Business Insider] More than 80 US military aircraft have been damaged so far in the Iran war. Equipment losses could be over $3.3 billion.  
  <https://www.businessinsider.com/us-military-planes-equipment-damaged-iran-war-cost-2026-10>
- `[ 25]` [Committee to Protect Journalists] Thai court to hear criminal defamation charges against investigative reporter Tom Wright  
  <https://cpj.org/2026/10/thai-court-to-hear-criminal-defamation-charges-against-investigative-reporter-tom-wright/>
- `[ 28]` [Tom's Hardware] Ukrainian drones hit Russia's Yandex data centers housing two top supercomputers  
  <https://www.tomshardware.com/tech-industry/data-centers/ukrainian-drones-hit-russias-yandex-data-centers-housing-two-top-supercomputers-major-outage-follows-retaliatory-strike>
- `[ 12]` [Pique Newsmagazine] Nigerian Air Force says plane carrying 25 crashed with no survivors in southern Ondo state  
  <https://www.piquenewsmagazine.com/world-news/nigerian-air-force-says-plane-carrying-25-crashed-with-no-survivors-in-southern-ondo-state-12861163>
- `[ 29]` [Committee to Protect Journalists] Guatemalan journalist Evelio López shot dead after denouncing threats  
  <https://cpj.org/2026/10/guatemalan-journalist-evelio-lopez-shot-dead-after-denouncing-threats/>
- `[ 25]` 🔓 [NYT Top Stories] Potential Iranian Drone Attack Led to Exit of U.S. Aircraft from British Air Base  
  <https://www.nytimes.com/2026/10/05/us/politics/iran-drone-attack-threat.html>
- `[ 20]` 🔓 [NYT Top Stories] Trapped in a Kill Zone, a Ukrainian City Is Beginning to Starve  
  <https://www.nytimes.com/2026/10/05/world/europe/oleshky-ukraine-russia-war-food.html>

### 🔴 🥾 Outdoors & Recreation

- **Articles**: 12 (12 scored)
- **Score**: avg 30.7 | min 15 | max 55
- **Stale** (>48h): 10
- **Avg age**: 73.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ████████████████████   4
  20–29   │ ██████████             2
  30–39   │ ███████████████        3
  40–49   │ █████                  1
  50–59   │ ██████████             2
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Outside Online | 4 | 33% |
| Business Insider | 2 | 17% |
| Live for the Outdoors (Country Walking) | 2 | 17% |
| Atlas Obscura | 1 | 8% |
| Graham | 1 | 8% |
| E.M.Smith | 1 | 8% |
| Gizmodo | 1 | 8% |

**Low-score articles (≤30):**

- `[ 24]` [Atlas Obscura] High Shoals Falls  in Hiawassee, Georgia  
  <https://www.atlasobscura.com/places/high-shoals-falls>
- `[ 15]` [Business Insider] I live in Utah and think these 5 underrated outdoor spots rival the 'Mighty 5' national parks  
  <https://www.businessinsider.com/best-places-in-utah-better-than-national-parks-from-local-2026-10>
- `[ 17]` 🔓 [Live for the Outdoors (Country Walking)] Best walking boots for women 2026: Top picks from our experienced female testing team  
  <https://www.livefortheoutdoors.com/hiking/walking-boots/best-walking-boots-for-women/>
- `[ 15]` [Graham] Kou Leafworm  
  <https://grahamsisland.com/2026/10/07/kou-leafworm/>
- `[ 22]` [E.M.Smith] Plague Panic! – not so much…  
  <https://chiefio.wordpress.com/2026/10/06/plague-panic-not-so-much/>
- `[ 18]` [Business Insider] I turned my passion for the outdoors into a community for startup founders. It's become a side hustle that makes me $10K in revenue.  
  <https://www.businessinsider.com/founders-community-turned-hiking-side-hustle-2026-10>

### 🟡 🔬 Science

- **Articles**: 41 (41 scored)
- **Score**: avg 51.4 | min 42 | max 71
- **Stale** (>48h): 34
- **Avg age**: 79.3h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │ ████████              12
  50–59   │ ████████████████████  27
  60–69   │                        1
  70–79   │                        1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 13 | 32% |
| Scientific American | 7 | 17% |
| WIRED | 3 | 7% |
| ScienceAlert | 2 | 5% |
| Neuroscience News | 2 | 5% |
| STAT News | 2 | 5% |
| Quanta Magazine | 1 | 2% |
| Hackster News | 1 | 2% |

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 9 (9 scored)
- **Score**: avg 26.9 | min 5 | max 49
- **Stale** (>48h): 5
- **Avg age**: 73.6h

**Score distribution:**
```
  0–9     │ ██████                 1
  10–19   │ █████████████          2
  20–29   │ ████████████████████   3
  30–39   │ ██████                 1
  40–49   │ █████████████          2
  50–59   │                        0
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Open Culture | 2 | 22% |
| The Atlantic Culture | 1 | 11% |
| bitterteaandmystery.blogspot.com | 1 | 11% |
| Engadget | 1 | 11% |
| The Verge | 1 | 11% |
| TechRadar | 1 | 11% |
| Andrew Knighton | 1 | 11% |
| Colossal | 1 | 11% |

**Low-score articles (≤30):**

- `[ 27]` 🔓 [The Atlantic Culture] The Guardians  
  <https://www.theatlantic.com/books/2026/10/sebastian-junger-the-guardians-short-story/688935/?utm_source=feed>
- `[  5]` [bitterteaandmystery.blogspot.com] Annual Book Sale 2026: My Son's Books  
  <http://bitterteaandmystery.blogspot.com/2026/10/annual-book-sale-2026-my-sons-books.html>
- `[ 25]` [Engadget] Cyberpunk 2077 is the latest video game to get the movie treatment  
  <https://www.engadget.com/2281714/cyberpunk-2077-is-the-latest-video-game-to-get-the-movie-treatment/>
- `[ 15]` 🔓 [The Verge] Paramount is making a Cyberpunk 2077 film  
  <https://www.theverge.com/games/1008327/paramount-pictures-cyberpunk-2077-film-movie>
- `[ 17]` [TechRadar] Could you stop a rogue AI from escaping? Take our sci-fi security test  
  <https://www.techradar.com/ai-platforms-assistants/imagine-ai-agents-like-meta-muse-and-openais-dots-are-on-the-loose-could-you-stop-them>
- `[ 29]` [Open Culture] In 1704, Isaac Newton Predicted That the World Will End in 2060  
  <https://www.openculture.com/2026/10/isaac-newton-predicted-that-the-world-will-end-in-2060.html>

### 🟡 🌿 Health & Wellness

- **Articles**: 58 (58 scored)
- **Score**: avg 51.5 | min 10 | max 70
- **Stale** (>48h): 48
- **Avg age**: 84.1h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██                     2
  20–29   │ ██                     2
  30–39   │ ███                    3
  40–49   │ ███████████████       15
  50–59   │ ████████████████████  20
  60–69   │ ██████████████        14
  70–79   │ ██                     2
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| STAT News | 8 | 14% |
| ScienceDaily | 7 | 12% |
| NPR Health News | 5 | 9% |
| Fast Company | 4 | 7% |
| ScienceAlert | 3 | 5% |
| NYT Well | 3 | 5% |
| Scientific American | 3 | 5% |
| Forbes Innovation | 2 | 3% |

**Low-score articles (≤30):**

- `[ 10]` [ScienceDaily] A new way to fight gum disease without wiping out good bacteria  
  <https://www.sciencedaily.com/releases/2026/10/261005012230.htm>
- `[ 23]` 🔓 [Fast Company] South Korea’s bank hacks offer a warning about AI-powered cyberattacks  
  <https://www.fastcompany.com/91619252/south-koreas-bank-hacks-offer-a-warning-about-ai-powered-cyberattacks>
- `[ 10]` [Pinterest Engineering Blog - Medium] Metrics Board: Building an Agent-ready Metrics Layer  
  <https://medium.com/pinterest-engineering/metrics-board-building-an-agent-ready-metrics-layer-2c8fefe68756?source=rss----4c5a5f6279b6---4>
- `[ 25]` [STAT News] STAT+: Nobel-winning optogenetics research has led to experimental treatments for blindness and Alzheimer’s  
  <https://www.statnews.com/2026/10/05/2026-nobel-prize-winning-optogenetics-research-explained/?utm_campaign=rss>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (1)

- **[🥾 Outdoors & Recreation]** `score 17` — Best walking boots for women 2026: Top picks from our experienced female testing team  
  Issue: `deals`  
  <https://www.livefortheoutdoors.com/hiking/walking-boots/best-walking-boots-for-women/>

### ⚠️ Borderline but Acceptable (1)

- **[📰 General News]** `score 26` — More than 80 US military aircraft have been damaged so far in the Iran war. Equipment losses could be over $3.3 billion.  
  Note: `clickbait`

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 56 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 26 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏛️ Architecture & Design** has 24 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏠 Homelab & DIY** has 40 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌾 Homestead & Hobby Farm** has 9 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 31 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏔️ Williams Lake Local** is dominated by **My Cariboo Now** (18 articles, 41%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **📰 General News** has 53 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🥾 Outdoors & Recreation** has a low average score (30.7) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🥾 Outdoors & Recreation** has 10 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 34 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (26.9) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🌿 Health & Wellness** has 48 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 1 article(s) should be removed (`deals` ×1) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 11 feeds · 438 articles · 2026-10-10 18:03 UTC_
