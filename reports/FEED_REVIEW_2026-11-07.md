# Feed Scoring & Scrubbing Report

_Generated: 2026-11-07 18:18 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 11 |
| Total articles | 491 |
| Stale articles (>48h) | 368 |
| Scrub pass | ✅ ran |
| Flagged for removal | 6 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 92 | 🟡 49.7 | 33–64 | 72 | WIRED (7) |
| 🌍 Climate & Energy | 54 | 🔴 39.4 | 10–69 | 40 | CleanTechnica (11) |
| 🏛️ Architecture & Design | 27 | 🔴 44.5 | 36–60 | 21 | ArchDaily (16) |
| 🏠 Homelab & DIY | 36 | 🔴 41.5 | 15–68 | 30 | Popular Woodworking (6) |
| 🌾 Homestead & Hobby Farm | 20 | 🟡 50.0 | 25–65 | 16 | Hobby Farms (5) |
| 🏔️ Williams Lake Local | 45 | 🟡 62.1 | 0–100 | 29 | My Cariboo Now (16) |
| 📰 General News | 109 | 🟡 58.2 | 17–83 | 75 | Scientific American (10) |
| 🥾 Outdoors & Recreation | 7 | 🔴 35.9 | 12–60 | 7 | Outside Online (4) |
| 🔬 Science | 41 | 🟡 45.6 | 26–53 | 31 | ScienceDaily (14) |
| 🚀 Sci-Fi & Culture | 5 | 🔴 27.4 | 22–32 | 4 | Gizmodo (2) |
| 🌿 Health & Wellness | 55 | 🔴 41.0 | 10–73 | 43 | STAT News (7) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 92 (92 scored)
- **Score**: avg 49.7 | min 33 | max 64
- **Stale** (>48h): 72
- **Avg age**: 80.2h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ █                      3
  40–49   │ ████████████████████  46
  50–59   │ ██████████████        34
  60–69   │ ███                    9
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| WIRED | 7 | 8% |
| TechRadar | 6 | 7% |
| MIT Technology Review | 6 | 7% |
| Fast Company | 5 | 5% |
| Ars Technica Technology Lab | 4 | 4% |
| Tom's Hardware | 4 | 4% |
| NYT Business | 3 | 3% |
| Forbes Innovation | 2 | 2% |

### 🔴 🌍 Climate & Energy

- **Articles**: 54 (54 scored)
- **Score**: avg 39.4 | min 10 | max 69
- **Stale** (>48h): 40
- **Avg age**: 79.5h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██                     3
  20–29   │ ████                   5
  30–39   │ ████████████          15
  40–49   │ ████████████████████  24
  50–59   │ █████                  6
  60–69   │                        1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| CleanTechnica | 11 | 20% |
| Forbes Innovation | 3 | 6% |
| NRDC | 3 | 6% |
| NYT Business | 2 | 4% |
| Wildfire Today | 2 | 4% |
| Al Jazeera English | 2 | 4% |
| New Atlas | 2 | 4% |
| climatechangenews.com | 2 | 4% |

**Low-score articles (≤30):**

- `[ 10]` [Business Insider] The rise and fall of the controversial Cybertruck, from a shattered window to celeb spottings to protests  
  <https://www.businessinsider.com/tesla-cybertruck-discontinued-images-famous-moments-elon-musk-2026-11>
- `[ 20]` 🔓 [Country Living UK] Could the polar vortex bring snow to the UK this winter? How it may affect our weather  
  <https://www.countryliving.com/uk/homes-interiors/gardens/a74358302/polar-vortex-snow-uk-winter/>
- `[ 20]` [CleanTechnica] You Need A New Car? Go Electric! It’s Superior Technology. Part 2  
  <https://cleantechnica.com/2026/11/05/you-need-a-new-car-go-electric-its-superior-technology-part-2/>
- `[ 18]` [New Atlas] New VW California camper van brings HUGE improvement at under 75K  
  <https://newatlas.com/campervans/2027-vw-california-uk-launch/>
- `[ 25]` [APTN News] Algonquin activist says Carney government needs more focus on climate change initiatives  
  <https://www.aptnnews.ca/nation-to-nation/algonquin-activist-says-carney-government-needs-more-focus-on-climate-change-initiatives/>
- `[ 27]` [TechRadar] GM recalls almost 70,000 EVs over braking glitch  
  <https://www.techradar.com/vehicle-tech/hybrid-electric-vehicles/gm-issues-recall-for-almost-70-000-evs-software-failure-could-cause-brake-failures-in-some-chevrolet-and-cadillac-cars>
- `[ 16]` [New Atlas] Kia Weekender tiny camper amplifies van life on a whole new continent  
  <https://newatlas.com/campervans/kombilife-kia-weekender-electric-camper-van/>
- `[ 22]` [InsideEVs] Finding And Using BP Pulse EV Chargers Just Got A Whole Lot Easier  
  <https://insideevs.com/news/814227/bp-pulse-chargehub-roaming-app-integration/>
- `[ 30]` [The Guardian Global Development] The Amazon’s canary in the coalmine: what a tropical fish can tell us about climate upheaval  
  <https://www.theguardian.com/global-development/2026/nov/03/the-amazons-canary-in-the-coalmine-what-a-tropical-fish-can-tell-us-about-climate-upheaval>
- `[ 30]` [NRDC] At COP31, Overlap Between Self-Interest and Climate Action Has Never Been Stronger  
  <https://www.nrdc.org/press-releases/cop31-overlap-between-self-interest-and-climate-action-has-never-been-stronger>
- `[ 30]` [ScienceDaily] NASA reveals a haunting skull hidden in Antarctica’s ice  
  <https://www.sciencedaily.com/releases/2026/11/261101010538.htm>

### 🔴 🏛️ Architecture & Design

- **Articles**: 27 (27 scored)
- **Score**: avg 44.5 | min 36 | max 60
- **Stale** (>48h): 21
- **Avg age**: 73.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ ███                    3
  40–49   │ ████████████████████  18
  50–59   │ █████                  5
  60–69   │ █                      1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ArchDaily | 16 | 59% ⚠️ |
| Dezeen | 4 | 15% |
| Dwell | 3 | 11% |
| Architizer | 2 | 7% |
| MIT News | 1 | 4% |
| Articles - passivehouseplus.co.uk | 1 | 4% |

### 🔴 🏠 Homelab & DIY

- **Articles**: 36 (36 scored)
- **Score**: avg 41.5 | min 15 | max 68
- **Stale** (>48h): 30
- **Avg age**: 78.3h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██                     2
  20–29   │ ████████               6
  30–39   │ █████                  4
  40–49   │ ████████████████████  14
  50–59   │ ███████████            8
  60–69   │ ██                     2
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Popular Woodworking | 6 | 17% |
| Adafruit Blog | 5 | 14% |
| Bambu Lab Community Forum - Latest posts | 4 | 11% |
| Hackster News | 3 | 8% |
| Hackaday | 2 | 6% |
| XDA Developers | 2 | 6% |
| MakeUseOf | 2 | 6% |
| Tom's Hardware | 2 | 6% |

**Low-score articles (≤30):**

- `[ 25]` 🔓 [Popular Woodworking] The Splinter Report: November 6th  
  <https://www.popularwoodworking.com/editors-blog/the-splinter-report-november-6th/>
- `[ 27]` 🔓 [Popular Woodworking] From The Inside Out  
  <https://www.popularwoodworking.com/editors-blog/from-the-inside-out/>
- `[ 22]` [Bambu Lab Community Forum - Latest posts] Boosts not received  
  <https://forum.bambulab.com/t/boosts-not-received/178137#post_7>
- `[ 17]` 🔓 [Popular Woodworking] Varnishing Hang Up  
  <https://www.popularwoodworking.com/tricks/varnishing-hang-up/>
- `[ 22]` [Atlas Obscura] Egiategia in Ciboure, France  
  <https://www.atlasobscura.com/places/egiategia>
- `[ 20]` [Bambu Lab Community Forum - Latest posts] RE: Bambu Studio 2.9.1 Public Release - Any reason for X1C to upgrade  
  <https://forum.bambulab.com/t/re-bambu-studio-2-9-1-public-release-any-reason-for-x1c-to-upgrade/262009#post_2>
- `[ 30]` [Android Authority] Smart homes are in disarray after daylight saving time baffles Google Nest devices (Update)  
  <https://www.androidauthority.com/google-nest-devices-baffled-by-dst-3731238/>
- `[ 24]` [Tom's Hardware] Bambu Lab H3C 3D printer review: A nine-tool monster  
  <https://www.tomshardware.com/3d-printing/bambu-lab-h3c-3d-printer-review>
- `[ 15]` EBSCO Information Services Extends Call for Proposals Deadline for EBSCO User Group 2027  
  <https://about.ebsco.com/news-center/press-releases/ebsco-information-services-extends-call-proposals-deadline-ebsco-user>

### 🟡 🌾 Homestead & Hobby Farm

- **Articles**: 20 (20 scored)
- **Score**: avg 50.0 | min 25 | max 65
- **Stale** (>48h): 16
- **Avg age**: 83.9h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ██                     1
  30–39   │ █████                  2
  40–49   │ ████████████           5
  50–59   │ ████████████████████   8
  60–69   │ ██████████             4
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hobby Farms | 5 | 25% |
| RealAgriculture | 2 | 10% |
| The Western Producer | 2 | 10% |
| Grainews | 2 | 10% |
| Small Farm Canada | 1 | 5% |
| Fast Company | 1 | 5% |
| topagrar.pl | 1 | 5% |
| Country Life | 1 | 5% |

**Low-score articles (≤30):**

- `[ 25]` 🔓 [Fast Company] 3.6 million ladders sold at Lowe’s, Costco, and Amazon are being recalled after fall-related brain injuries, broken bones reported  
  <https://www.fastcompany.com/91637200/ladders-recalled-after-serious-falls-broken-bones-brain-injuries>

### 🟡 🏔️ Williams Lake Local

- **Articles**: 45 (45 scored)
- **Score**: avg 62.1 | min 0 | max 100
- **Stale** (>48h): 29
- **Avg age**: 65.5h
- **Local-flagged**: 45 (1 with score=0 via local override)

**Score distribution:**
```
  0–9     │ ██                     1
  10–19   │ ████                   2
  20–29   │ ██████                 3
  30–39   │ ██                     1
  40–49   │ ████████               4
  50–59   │ ████████████           6
  60–69   │ ██████████████████     9
  70–79   │ ████████████████████  10
  80–89   │ ████████               4
  90–100  │ ██████████             5
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| My Cariboo Now | 16 | 36% |
| Williams Lake Tribune | 12 | 27% |
| Cariboo Signals Reviews | 6 | 13% |
| 100 Mile Free Press | 4 | 9% |
| Quesnel Cariboo Observer | 4 | 9% |
| Regional News Archives - Williams Lake Tribune | 1 | 2% |
| Canadian Mining Journal | 1 | 2% |
| BC Wildfire Service | 1 | 2% |

**Low-score articles (≤30):**

- `[  0]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, November 7, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-07.html>
- `[ 16]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, November 6, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-06.html>
- `[ 24]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, November 5, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-05.html>
- `[ 21]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, November 4, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-04.html>
- `[ 11]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, November 3, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-03.html>
- `[ 24]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, November 2, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-02.html>

### 🟡 📰 General News

- **Articles**: 109 (109 scored)
- **Score**: avg 58.2 | min 17 | max 83
- **Stale** (>48h): 75
- **Avg age**: 72.1h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        2
  20–29   │ ███                    9
  30–39   │ ██                     6
  40–49   │ █                      3
  50–59   │ █████                 14
  60–69   │ ████████████████████  50
  70–79   │ █████████             24
  80–89   │                        1
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Scientific American | 10 | 9% |
| Al Jazeera English | 9 | 8% |
| NYT Business | 7 | 6% |
| TechRadar | 7 | 6% |
| Hackaday | 6 | 6% |
| The Tyee | 5 | 5% |
| WIRED | 5 | 5% |
| Williams Lake Tribune | 4 | 4% |

**Low-score articles (≤30):**

- `[ 25]` [Al Jazeera English] Governing party ahead in early results of New Zealand’s knife-edge vote  
  <https://www.aljazeera.com/news/2026/11/7/governing-party-leads-in-new-zealands-knife-edge-vote-early-results?traffic_source=rss>
- `[ 30]` [Pique Newsmagazine] Polls close in a New Zealand election expected to be the tightest in years, with early results due  
  <https://www.piquenewsmagazine.com/world-news/polls-close-in-a-new-zealand-election-expected-to-be-the-tightest-in-years-with-early-results-due-12990587>
- `[ 19]` 🔓 [NYT Business] Paraguay’s President Removed and Arrested Over Financial Crisis  
  <https://www.nytimes.com/2026/11/06/world/americas/paraguay-president-removed-ueno.html>
- `[ 23]` 🔓 [NYT Top Stories] A Summit in China With Trump and Putin? That Might be Awkward for Xi.  
  <https://www.nytimes.com/2026/11/06/world/asia/china-trump-putin-xi-summit.html>
- `[ 26]` [apnews.com] Paraguay president submits resignation as Ueno collapse freezes millions of accounts  
  <https://apnews.com/article/ueno-bank-collapse-paraguay-banking-crisis-santiago-pena-impeachment-eccea1c9a64808b5cd7e6e1d5542084f>
- `[ 24]` 🔓 [NYT Business] Klaus-Michael Kühne Has Died. His Company Played a Dark Role in Nazi Germany.  
  <https://www.nytimes.com/2026/11/05/world/europe/klaus-michael-kuhne-dead.html>
- `[ 25]` [Al Jazeera English] Democrats won Congress. But can they deliver on their promises?  
  <https://www.aljazeera.com/news/2026/11/5/democrats-won-congress-but-can-they-deliver-on-their-promises?traffic_source=rss>
- `[ 23]` [Hyperallergic] France Opens War Crimes Investigation Into Israeli Airstrike That Killed Artist Ali Cherri's Parents  
  <https://hyperallergic.com/france-opens-war-crimes-investigation-into-israeli-airstrike-that-killed-artist-ali-cherris-parents/>
- `[ 25]` [The Guardian Global Development] British healthcare worker with Ebola evacuated from DR Congo to UK  
  <https://www.theguardian.com/world/2026/nov/04/british-healthcare-worker-ebola-evacuated-drc-to-uk-document-shows>
- `[ 24]` [Tom's Hardware] Chinese survey ship loitering near undersea cable ignores Philippine demands to withdraw  
  <https://www.tomshardware.com/tech-industry/chinese-survey-ship-loitering-near-undersea-cable-ignores-philippine-demands-to-withdraw-evasive-action-point-to-growing-prc-threats-to-data-lines-in-the-pacific>
- `[ 24]` 🔓 [NYT Business] Gulf Economies, Torn by War in Iran, Desperately Need a Return to Normal  
  <https://www.nytimes.com/2026/11/02/business/iran-war-gulf-economies.html>
- `[ 17]` [firstpost.com] Israeli opposition backs Eisenkot as Arab parties hold balance of power  
  <https://www.firstpost.com/world/israel-opposition-leaders-to-meet-as-gadi-eisenkot-seeks-backing-to-form-next-government-14057229.html>

### 🔴 🥾 Outdoors & Recreation

- **Articles**: 7 (7 scored)
- **Score**: avg 35.9 | min 12 | max 60
- **Stale** (>48h): 7
- **Avg age**: 89.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██████████             1
  20–29   │ ████████████████████   2
  30–39   │ ████████████████████   2
  40–49   │                        0
  50–59   │ ██████████             1
  60–69   │ ██████████             1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Outside Online | 4 | 57% |
| Vancouver Sun | 1 | 14% |
| Williams Lake Tribune | 1 | 14% |
| Wikipedia  - Recent changes [en] | 1 | 14% |

**Low-score articles (≤30):**

- `[ 22]` [Vancouver Sun] Being prepared means staying safe on the mountains: North Shore Rescue  
  <https://vancouversun.com/news/be-prepared-stay-safe-north-shore-rescue>
- `[ 12]` [Wikipedia  - Recent changes [en]] Northern Warm Temperate Rainforest  
  <https://en.wikipedia.org/w/index.php?title=Northern_Warm_Temperate_Rainforest&diff=1383537628&oldid=1383537343>
- `[ 28]` 🔓 [Outside Online] “Should I Jump? Should I Not Jump?” How Resisting Panic Saved a Climber Stuck on a One Foot Ledge  
  <https://www.outsideonline.com/outdoor-adventure/exploration-survival/should-i-jump-should-i-not-jump-how-resisting-panic-saved-a-climber-stuck-on-a-one-foot-ledge/>

### 🟡 🔬 Science

- **Articles**: 41 (41 scored)
- **Score**: avg 45.6 | min 26 | max 53
- **Stale** (>48h): 31
- **Avg age**: 75.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        1
  30–39   │                        1
  40–49   │ ████████████████████  33
  50–59   │ ███                    6
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 14 | 34% |
| Nautilus | 4 | 10% |
| Scientific American | 3 | 7% |
| New Atlas | 2 | 5% |
| Popular Mechanics | 2 | 5% |
| 3D Printing Industry | 2 | 5% |
| ScienceAlert | 2 | 5% |
| science.org | 2 | 5% |

**Low-score articles (≤30):**

- `[ 26]` [Nautilus] The Female Iron Age Queen Who Helped Bring Britain to its Knees  
  <https://nautil.us/the-female-iron-age-queen-who-helped-bring-britain-to-its-knees-1286361/>

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 5 (5 scored)
- **Score**: avg 27.4 | min 22 | max 32
- **Stale** (>48h): 4
- **Avg age**: 69.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ████████████████████   3
  30–39   │ █████████████          2
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
| Gizmodo | 2 | 40% |
| Strange Horizons | 1 | 20% |
| Forbes Innovation | 1 | 20% |
| Adafruit Blog | 1 | 20% |

**Low-score articles (≤30):**

- `[ 22]` [Gizmodo] ‘The Institute’ Season 2: Ben Barnes on Stephen King Sci-Fi Series  
  <https://news.google.com/rss/articles/CBMirAFBVV95cUxNZm8xOHYwdGZTLWxmeUNiOTMzZF9hd0VqbVJPbTlSWUVWUl96djEzZEpsblVqc1FSVldSbFhYWUtGXzJkWEtLNkY3bTdCWDhkM2xzSW05RExzcllxbGV6OVNlZWpiNzllYktWT2JoWUpXMWh6UUItUHlwVmk5Mk1uQ0t3YlljZUVPZmtXSXIxUkp4aUlaWXdJTmEtMDVIVE9PZzBKNlRpSG8wUEhX?oc=5>
- `[ 30]` [Gizmodo] ‘The Institute’ Season 2 Adds AI to Its List of Dystopian Horrors  
  <https://news.google.com/rss/articles/CBMimgFBVV95cUxQczd0MWp1QWVjSzkxd0tGQm9rS0hKZGd3S2l2T25TaF90ODVhMGMzMjZQem51T3RjUlFXbldGQ1Q5Q190Yl9USW1FekZfeTVmTHZrSk5SMkc1cEszV1ZXcGFlNVlUazRaeGd3TE5PLUVud1B3WVNfSEFZMVRvQW1jZmxMb2x1TmJ1NUNlVy1RWG4tLVpLc21aaHRn?oc=5>
- `[ 26]` 🔓 [Forbes Innovation] A Singular Talent, A Generous Collaborator, And A True Gentleman  
  <https://www.forbes.com/sites/johnwerner/2026/11/03/a-singular-talent-a-generous-collaborator-and-a-true-gentleman/>
- `[ 27]` [Adafruit Blog] Alien flora and fauna  #ArtTuesday  
  <https://blog.adafruit.com/2026/11/03/alien-flora-and-fauna-arttuesday/>

### 🔴 🌿 Health & Wellness

- **Articles**: 55 (55 scored)
- **Score**: avg 41.0 | min 10 | max 73
- **Stale** (>48h): 43
- **Avg age**: 78.8h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ████                   6
  20–29   │                        0
  30–39   │ ███████████           14
  40–49   │ ████████████████████  25
  50–59   │ ███████                9
  60–69   │                        0
  70–79   │                        1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| STAT News | 7 | 13% |
| ScienceDaily | 7 | 13% |
| Nautilus | 4 | 7% |
| Being Patient | 4 | 7% |
| NYT Well | 3 | 5% |
| NPR Health News | 3 | 5% |
| Science-Based Medicine | 3 | 5% |
| PsyBlog | 2 | 4% |

**Low-score articles (≤30):**

- `[ 17]` [ScienceDaily] Scientists trick cancer cells into making the drugs that kill them  
  <https://www.sciencedaily.com/releases/2026/11/261101010552.htm>
- `[ 10]` [ncsc.gov.uk] UK cyber agency warns AI-powered ransomware could hit critical infrastructure by 2028  
  <https://www.ncsc.gov.uk/news/cyber-chief-uk-facing-ai-powered-attacks-on-critical-infrastructure-in-two-years>
- `[ 10]` [Amol Agrawal] AI boom: Lessons from Great Depression  
  <https://mostlyeconomics.wordpress.com/2026/11/03/ai-boom-lessons-from-great-depression/>
- `[ 10]` [ScienceDaily] Scientists reverse liver cell aging and cut Alzheimer’s-linked protein in half  
  <https://www.sciencedaily.com/releases/2026/10/261031221155.htm>
- `[ 10]` [STAT News] STAT+: Psilocybin’s lasting benefits prove elusive in mice  
  <https://www.statnews.com/2026/11/02/biotech-news-psilocybin-lasting-benefits-prove-elusive-in-mice/?utm_campaign=rss>
- `[ 10]` [ScienceDaily] Scientists discover that some “unhealthy” diets can boost cancer immunotherapy in mice  
  <https://www.sciencedaily.com/releases/2026/10/261029072132.htm>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (6)

- **[🌍 Climate & Energy]** `score 20` — Could the polar vortex bring snow to the UK this winter? How it may affect our weather  
  Issue: `clickbait`  
  <https://www.countryliving.com/uk/homes-interiors/gardens/a74358302/polar-vortex-snow-uk-winter/>
- **[🌍 Climate & Energy]** `score 20` — You Need A New Car? Go Electric! It's Superior Technology. Part 2  
  Issue: `clickbait`  
  <https://cleantechnica.com/2026/11/05/you-need-a-new-car-go-electric-its-superior-technology-part-2/>
- **[🌍 Climate & Energy]** `score 18` — New VW California camper van brings HUGE improvement at under 75K  
  Issue: `clickbait`  
  <https://newatlas.com/campervans/2027-vw-california-uk-launch/>
- **[🌍 Climate & Energy]** `score 16` — Kia Weekender tiny camper amplifies van life on a whole new continent  
  Issue: `clickbait`  
  <https://newatlas.com/campervans/kombilife-kia-weekender-electric-camper-van/>
- **[🌍 Climate & Energy]** `score 22` — Finding And Using BP Pulse EV Chargers Just Got A Whole Lot Easier  
  Issue: `clickbait`  
  <https://insideevs.com/news/814227/bp-pulse-chargehub-roaming-app-integration/>
- **[🏠 Homelab & DIY]** `score 15` — EBSCO Information Services Extends Call for Proposals Deadline for EBSCO User Group 2027  
  Issue: `clickbait`  
  <https://about.ebsco.com/news-center/press-releases/ebsco-information-services-extends-call-proposals-deadline-ebsco-user>

### ⚠️ Borderline but Acceptable (1)

- **[🏠 Homelab & DIY]** `score 24` — Bambu Lab H3C 3D printer review: A nine-tool monster  
  Note: `clickbait`

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 72 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 40 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏛️ Architecture & Design** has 21 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏛️ Architecture & Design** is dominated by **ArchDaily** (16 articles, 59%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **🏠 Homelab & DIY** has 30 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌾 Homestead & Hobby Farm** has 16 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 29 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **📰 General News** has 75 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🥾 Outdoors & Recreation** has 7 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 31 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌿 Health & Wellness** has 43 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 6 article(s) should be removed (`clickbait` ×6) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 11 feeds · 491 articles · 2026-11-07 18:18 UTC_
