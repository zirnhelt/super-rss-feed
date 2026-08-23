# Feed Scoring & Scrubbing Report

_Generated: 2026-08-23 13:41 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 11 |
| Total articles | 798 |
| Stale articles (>48h) | 510 |
| Scrub pass | ⏭ skipped (--no-scrub) |
| Flagged for removal | 0 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 148 | 🟡 49.6 | 18–65 | 91 | TechRadar (23) |
| 🌍 Climate & Energy | 38 | 🟡 49.0 | 8–80 | 25 | Mother Jones (5) |
| 🏛️ Architecture & Design | 53 | 🔴 41.9 | 18–72 | 36 | ArchDaily (23) |
| 🏠 Homelab & DIY | 43 | 🟡 51.5 | 12–63 | 25 | XDA Developers (11) |
| 🌾 Homestead & Hobby Farm | 12 | 🔴 43.2 | 0–56 | 10 | Hobby Farms (5) |
| 🏔️ Williams Lake Local | 46 | 🟢 72.4 | 40–92 | 25 | My Cariboo Now (19) |
| 📰 General News | 254 | 🟡 63.1 | 22–72 | 165 | NYT Business (22) |
| 🥾 Outdoors & Recreation | 20 | 🔴 34.0 | 8–56 | 13 | Outside Online (8) |
| 🔬 Science | 57 | 🔴 43.0 | 4–60 | 43 | ScienceDaily (11) |
| 🚀 Sci-Fi & Culture | 19 | 🔴 22.3 | 0–50 | 8 | Comments for Solarpunk Magazine (4) |
| 🌿 Health & Wellness | 108 | 🟡 55.1 | 10–77 | 69 | ScienceDaily (14) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 148 (148 scored)
- **Score**: avg 49.6 | min 18 | max 65
- **Stale** (>48h): 91
- **Avg age**: 66.5h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        2
  20–29   │                        4
  30–39   │ ██                     9
  40–49   │ ██████████            43
  50–59   │ ████████████████████  82
  60–69   │ █                      8
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| TechRadar | 23 | 16% |
| Tom's Hardware | 18 | 12% |
| Business Insider | 11 | 7% |
| TechCrunch | 9 | 6% |
| WIRED | 9 | 6% |
| Forbes Innovation | 8 | 5% |
| Kagi Small Web | 8 | 5% |
| Toms Guide | 7 | 5% |

**Low-score articles (≤30):**

- `[ 25]` [My East Kootenay Now] Columbia Valley makes its big screen debut tonight in Invermere  
  <https://news.google.com/rss/articles/CBMiwAFBVV95cUxQa2llMk5XeUhuRkJRWVB5bXlSOU1yREtScVBDQUFKU2NsczBGN2lLTXduOTJLMThVcl9ZdTdVV1FGWjhXMkRaQUZrdW1pcXBPTW5DR0VqdmxTaGZlcTFzdFM0akR2OXhwNnVRS2gxeEJyUDNSUlZXQ2dwYmVhTEM1emVfRXpYRUI2blJwRllYU0o0WXZNclh6czAtMV9FN3VjRW1KdzZoWU94QTMyYVpaTEtPWG1Dcm9xNWt2SVFFXzc?oc=5>
- `[ 22]` [Business Insider] 12 celebrities who support AI  
  <https://www.businessinsider.com/pro-ai-celebrities-investors-companies>
- `[ 18]` [Boing Boing] Trump meets boy rescued from drowning, tells him he probably wouldn't have helped  
  <https://boingboing.net/2026/08/21/trump-lifeguard-rescued-boy.html>
- `[ 22]` [Toms Guide] I asked ChatGPT to find everything the internet knows about me — and it found more than I expected  
  <https://www.tomsguide.com/ai/i-asked-chatgpt-to-find-everything-the-internet-knows-about-me-and-it-found-more-than-i-expected>
- `[ 18]` [Neowin] Logitech G Pro X mechanical keyboard price drops by a staggering 39%  
  <https://www.neowin.net/deals/logitech-g-pro-x-mechanical-keyboard-price-drops-by-a-staggering-39/?utm_source=rss>
- `[ 23]` [Android Authority] Gemini’s Daily Brief could soon land on your Pixel’s lock screen  
  <https://www.androidauthority.com/google-gemini-brief-at-a-glance-apk-teardown-3701108/>

### 🟡 🌍 Climate & Energy

- **Articles**: 38 (38 scored)
- **Score**: avg 49.0 | min 8 | max 80
- **Stale** (>48h): 25
- **Avg age**: 72.9h

**Score distribution:**
```
  0–9     │ ██                     2
  10–19   │                        0
  20–29   │ █                      1
  30–39   │ ███                    3
  40–49   │ █████████              9
  50–59   │ ████████████████████  19
  60–69   │ ██                     2
  70–79   │ █                      1
  80–89   │ █                      1
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Mother Jones | 5 | 13% |
| InsideEVs | 4 | 11% |
| Scientific American | 4 | 11% |
| Comments for Solarpunk Magazine | 2 | 5% |
| Forbes Innovation | 2 | 5% |
| Fast Company | 2 | 5% |
| The Narwhal | 2 | 5% |
| ScienceDaily | 2 | 5% |

**Low-score articles (≤30):**

- `[  8]` [Comments for Solarpunk Magazine] Advertise  
  <https://solarpunkmagazine.com/advertise/>
- `[ 22]` [New Atlas] Ferrari just sold a single super-divisive Luce at 62x its asking price  
  <https://newatlas.com/automotive/ferrari-luce-charity-auction-40-million/>
- `[  8]` [Comments for Solarpunk Magazine] About – Solarpunk Magazine  
  <https://solarpunkmagazine.com/about/>

### 🔴 🏛️ Architecture & Design

- **Articles**: 53 (53 scored)
- **Score**: avg 41.9 | min 18 | max 72
- **Stale** (>48h): 36
- **Avg age**: 67.1h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      2
  20–29   │ ████                   5
  30–39   │ ██████████████        15
  40–49   │ ████████████████████  21
  50–59   │ ████                   5
  60–69   │ ███                    4
  70–79   │                        1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ArchDaily | 23 | 43% ⚠️ |
| Dezeen | 10 | 19% |
| Canadian Architect | 4 | 8% |
| Small Wooden House Plans | Micro Cabin Plans | Garden Shed Plans | Cottage Blueprints | 3 | 6% |
| Architizer | 2 | 4% |
| Dwell | 2 | 4% |
| Wikipedia  - Recent changes [en] | 1 | 2% |
| Hyperallergic | 1 | 2% |

**Low-score articles (≤30):**

- `[ 28]` Meet the Canadian Architect Awards Jury  
  <https://www.canadianarchitect.com/meet-the-canadian-architect-awards-jury-2/>
- `[ 18]` [Dezeen] Heinz adjustable ketchup lid allows for "perfect squeeze"  
  <https://www.dezeen.com/2026/08/21/kraft-heinz-love-lid-ketchup-adjustable/>
- `[ 28]` [Dezeen] Colourful cultural artefact storehouse among projects from London School of Architecture  
  <https://www.dezeen.com/2026/08/21/cultural-artefact-storehouse-london-school-of-architecture-schoolshows/>
- `[ 26]` [ArchDaily] Epitácio 3714 Building / Cité Arquitetura  
  <https://www.archdaily.com/1183785/epitacio-3714-building-cite-arquitetura>
- `[ 18]` [Dezeen] Photos reveal world's tallest hotel in Dubai  
  <https://www.dezeen.com/2026/08/21/ciel-dubai-marina-worlds-tallest-hotel/>
- `[ 20]` [ArchDaily] 12 Colombian Houses Featuring Exposed Brick  
  <https://www.archdaily.com/939644/11-colombian-houses-that-feature-exposed-brick>
- `[ 28]` [ArchDaily] Screened Space Office Building / Studio UF+O  
  <https://www.archdaily.com/1183677/screened-space-office-building-studio-uf-plus-o>

### 🟡 🏠 Homelab & DIY

- **Articles**: 43 (43 scored)
- **Score**: avg 51.5 | min 12 | max 63
- **Stale** (>48h): 25
- **Avg age**: 68.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      1
  20–29   │ ██                     2
  30–39   │ ███                    3
  40–49   │ ████████               7
  50–59   │ ████████████████████  17
  60–69   │ ███████████████       13
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| XDA Developers | 11 | 26% |
| Hackaday | 7 | 16% |
| Popular Woodworking | 5 | 12% |
| Tom's Hardware | 4 | 9% |
| How-To Geek | 4 | 9% |
| MakeUseOf | 3 | 7% |
| Kagi Small Web | 2 | 5% |
| ArchDaily | 1 | 2% |

**Low-score articles (≤30):**

- `[ 12]` [Kagi Small Web] My Jellyfin server highlights  
  <https://www.diversetechgeek.com/my-jellyfin-server-highlights/>
- `[ 20]` 🔓 [Popular Woodworking] Giving Back  
  <https://www.popularwoodworking.com/editors-blog/giving-back/>
- `[ 30]` [Colossal] Sift Through Grace Baldwin’s Giant Junk Drawer Filled with Nostalgia  
  <https://www.thisiscolossal.com/2026/08/grace-baldwin-giant-junk-drawer-sculpture/>
- `[ 27]` Pre-election workshops coming : My East Kootenay Now  
  <https://www.myeastkootenaynow.com/57528/news/elections/2026-municipal-election/pre-election-workshops-coming/>

### 🔴 🌾 Homestead & Hobby Farm

- **Articles**: 12 (12 scored)
- **Score**: avg 43.2 | min 0 | max 56
- **Stale** (>48h): 10
- **Avg age**: 64.9h

**Score distribution:**
```
  0–9     │ ████                   1
  10–19   │ ████                   1
  20–29   │                        0
  30–39   │                        0
  40–49   │ ████████████████████   5
  50–59   │ ████████████████████   5
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hobby Farms | 5 | 42% ⚠️ |
| Small Farm Canada | 4 | 33% |
| Resilience.org | 1 | 8% |
| Civil Eats | 1 | 8% |
| Mother Earth News | 1 | 8% |

**Low-score articles (≤30):**

- `[ 18]` [Small Farm Canada] Miniature Cattle Breeds for Small Farms  
  <https://www.smallfarmcanada.ca/resources/cattle-breeds/>
- `[  0]` Mother Earth News  
  <https://www.motherearthnews.com/>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 46 (46 scored)
- **Score**: avg 72.4 | min 40 | max 92
- **Stale** (>48h): 25
- **Avg age**: 58.0h
- **Local-flagged**: 46

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │ █████                  4
  50–59   │ █                      1
  60–69   │ ████████████████      12
  70–79   │ ████████████████████  15
  80–89   │ ████████████████      12
  90–100  │ ██                     2
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| My Cariboo Now | 19 | 41% ⚠️ |
| Williams Lake Tribune | 15 | 33% |
| 100 Mile Free Press | 4 | 9% |
| Pique Newsmagazine | 2 | 4% |
| Wikipedia  - Recent changes [en] | 1 | 2% |
| Cariboo Signals Reviews | 1 | 2% |
| The Tyee | 1 | 2% |
| IndigiNews | 1 | 2% |

### 🟡 📰 General News

- **Articles**: 254 (254 scored)
- **Score**: avg 63.1 | min 22 | max 72
- **Stale** (>48h): 165
- **Avg age**: 65.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        1
  30–39   │                        3
  40–49   │                        1
  50–59   │ █████                 51
  60–69   │ ████████████████████ 172
  70–79   │ ███                   26
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| NYT Business | 22 | 9% |
| NYT Top Stories | 17 | 7% |
| TechRadar | 15 | 6% |
| The Northern Miner | 15 | 6% |
| Scientific American | 11 | 4% |
| Engadget | 9 | 4% |
| Hackaday | 9 | 4% |
| The New Yorker | 8 | 3% |

**Low-score articles (≤30):**

- `[ 22]` 🔓 [The Atlantic] The Case for Chilling Out About Birth Rates  
  <https://www.theatlantic.com/ideas/2026/08/birth-rate-panic-overblown/688320/?utm_source=feed>

### 🔴 🥾 Outdoors & Recreation

- **Articles**: 20 (20 scored)
- **Score**: avg 34.0 | min 8 | max 56
- **Stale** (>48h): 13
- **Avg age**: 70.3h

**Score distribution:**
```
  0–9     │ ██                     1
  10–19   │ ███████                3
  20–29   │ ███████                3
  30–39   │ ██████████             4
  40–49   │ ████████████████████   8
  50–59   │ ██                     1
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Outside Online | 8 | 40% |
| Live for the Outdoors (Country Walking) | 1 | 5% |
| Bicycling | 1 | 5% |
| Edge (GamesRadar) | 1 | 5% |
| Kagi Small Web | 1 | 5% |
| Comments for The Road Goes Ever On | 1 | 5% |
| AFAR | 1 | 5% |
| Men's Health | 1 | 5% |

**Low-score articles (≤30):**

- `[  8]` [Kagi Small Web] Shōwa-shinzan&nbsp;(昭和新山,&nbsp;Shōwa-shinzan)&nbsp;is a&nbsp;volcanic&nbsp;lava dome&nbsp;in the&nbsp;Shikotsu-Toya National&hellip;  
  <https://youzicha.tumblr.com/post/825645082276495360>
- `[ 25]` 🔓 [Outside Online] How to Follow the 2026 UTMB Mont-Blanc  
  <https://www.outsideonline.com/outdoor-adventure/hiking-and-backpacking/how-to-watch-utmb-mont-blanc/>
- `[ 18]` [Comments for The Road Goes Ever On] West Coast Trail: Pachena Bay to Darling River | The Road Goes Ever On  
  <https://mariaadey.com/2026/08/01/west-coast-trail-pachena-bay-to-darling-river/>
- `[ 22]` 🔓 [Men's Health] Need a Way to Store and Transport Your Outdoor Gear? This Is the Simple Solution.  
  <https://www.menshealth.com/technology-gear/a73455781/gear-haulers-for-outdoor-gear/>
- `[ 29]` 🔓 [Ideal Home (Country Homes & Interiors)] I hated washing up bowls until I discovered this clever style on my camping holiday – I’m now convinced it’s the only choice for my tiny kitchen  
  <https://www.idealhome.co.uk/house-manual/cleaning/collapsable-washing-up-bowls>
- `[ 13]` 🔓 [Outside Online] Perfect Circles: 6 Great Trail Running Loops  
  <https://www.outsideonline.com/adventure-travel/destinations/north-america/perfect-circles-6-great-trail-running-loops/>
- `[ 17]` 🔓 [Outside Online] Hike Through the Swiss Alps With the World’s Most Famous Rescue Dogs  
  <https://www.outsideonline.com/adventure-travel/destinations/europe/hike-through-the-alps-with-saint-bernards/>

### 🔴 🔬 Science

- **Articles**: 57 (57 scored)
- **Score**: avg 43.0 | min 4 | max 60
- **Stale** (>48h): 43
- **Avg age**: 73.1h

**Score distribution:**
```
  0–9     │                        1
  10–19   │                        1
  20–29   │                        0
  30–39   │ ███████████           15
  40–49   │ ████████████████████  27
  50–59   │ ████████              12
  60–69   │                        1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 11 | 19% |
| Scientific American | 10 | 18% |
| Nautilus | 9 | 16% |
| ScienceAlert | 8 | 14% |
| Popular Mechanics | 4 | 7% |
| Quanta Magazine | 2 | 4% |
| New Atlas | 2 | 4% |
| EarthSky | 2 | 4% |

**Low-score articles (≤30):**

- `[ 18]` [Kagi Small Web] Fosi  Audio  MC331  
  <http://preposter.us/single-michigan-helium-network/fosi-audio-mc331.html>
- `[  4]` [Dangerous Minds] Newly discovered species of snake named after Slash  
  <https://dangerousminds.net/weird-news/newly-discovered-species-of-snake-named-after-slash/>
- `[ 30]` [Tom's Hardware] China reportedly orders state agencies to uninstall its government-only edition of Windows 10 — Beijing accelerates planned retirement over data security concerns  
  <https://www.tomshardware.com/software/operating-systems/china-reportedly-orders-state-agencies-to-uninstall-its-government-only-edition-of-windows-10>

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 19 (19 scored)
- **Score**: avg 22.3 | min 0 | max 50
- **Stale** (>48h): 8
- **Avg age**: 53.4h

**Score distribution:**
```
  0–9     │ ████████████████████   5
  10–19   │ ████████████████       4
  20–29   │ ████████████████████   5
  30–39   │                        0
  40–49   │ ████████████████       4
  50–59   │ ████                   1
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Comments for Solarpunk Magazine | 4 | 21% |
| Edge (GamesRadar) | 4 | 21% |
| Toms Guide | 2 | 11% |
| Wikipedia  - Recent changes [en] | 2 | 11% |
| Reactor Magazine | 2 | 11% |
| Tom's Hardware | 1 | 5% |
| MakeUseOf | 1 | 5% |
| Engadget | 1 | 5% |

**Low-score articles (≤30):**

- `[ 18]` [Comments for Solarpunk Magazine] Solarpunk Magazine – Demand Utopia  
  <https://solarpunkmagazine.com/>
- `[ 27]` 🔓 [Edge (GamesRadar)] "They don't make 'em like they used to": How flash player games defined an era of indie horror  
  <https://www.gamesradar.com/games/horror/they-dont-make-em-like-they-used-to-how-flash-player-games-defined-an-era-of-indie-horror/>
- `[ 15]` [MakeUseOf] 7 fantasy book series that are dark enough for Game of Thrones fans  
  <https://www.makeuseof.com/7-fantasy-book-series-dark-game-of-thrones-first-law-broken-earth/>
- `[ 20]` [Engadget] Season two of Netflix's Cyberpunk 2077 anime streams October 20  
  <https://www.engadget.com/2241834/season-two-of-netflixs-cyberpunk-2077-anime-streams-october-20/>
- `[ 12]` [Lifehacker] If You Loved 'Lanterns,' There's One Movie You Need to Watch Next  
  <https://lifehacker.com/entertainment/what-movies-to-watch-after-lanterns?utm_medium=RSS>
- `[ 23]` 🔓 [Edge (GamesRadar)] After over 1,000 hours in Cyberpunk 2077, I'm convinced the Nomads are the best group and lifepath in the RPG  
  <https://www.gamesradar.com/games/cyberpunk/after-over-1-000-hours-in-cyberpunk-2077-im-convinced-the-nomads-are-the-best-group-and-lifepath-in-the-rpg/>
- `[ 15]` [Reactor Magazine] What to Watch and Read This Weekend: Sex and Death, Fast and Furious  
  <https://reactormag.com/what-to-watch-and-read-this-weekend-august-21-2026/>
- `[  0]` [Wikipedia  - Recent changes [en]] Morgan Rice  
  <https://en.wikipedia.org/w/index.php?title=Morgan_Rice&diff=1370505902&oldid=1370483703>
- `[ 27]` 🔓 [Edge (GamesRadar)] Cyberpunk: Edgerunners welcomes us back to Night City with high-octane season 2 trailer and Netflix release date  
  <https://www.gamesradar.com/entertainment/anime-shows/cyberpunk-edgerunners-welcomes-us-back-to-night-city-with-high-octane-season-2-trailer-and-netflix-release-date/>
- `[  2]` [Comments for Solarpunk Magazine] Shop  
  <https://solarpunkmagazine.com/shop/>
- `[  6]` [Comments for Solarpunk Magazine] Blog  
  <https://solarpunkmagazine.com/blog/>
- `[ 27]` 🔓 [Edge (GamesRadar)] Doctor Who writer thinks the sci-fi show might "quietly" disappear: "All good things come to an end"  
  <https://www.gamesradar.com/entertainment/sci-fi-shows/doctor-who-writer-thinks-the-sci-fi-show-might-quietly-disappear-all-good-things-come-to-an-end/>
- `[  8]` [Toms Guide] Loved 'Ex Machina'? You need to stream this free sci-fi movie on Tubi before it leaves  
  <https://www.tomsguide.com/entertainment/streaming/loved-ex-machina-you-need-to-stream-this-free-sci-fi-movie-on-tubi-before-it-leaves>
- `[  8]` [Comments for Solarpunk Magazine] Contact  
  <https://solarpunkmagazine.com/contact/>

### 🟡 🌿 Health & Wellness

- **Articles**: 108 (108 scored)
- **Score**: avg 55.1 | min 10 | max 77
- **Stale** (>48h): 69
- **Avg age**: 64.3h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      3
  20–29   │ █                      2
  30–39   │ ██                     4
  40–49   │ ██████████████        25
  50–59   │ █████████████         24
  60–69   │ ████████████████████  35
  70–79   │ ████████              15
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 14 | 13% |
| Fast Company | 8 | 7% |
| Forbes Innovation | 4 | 4% |
| NYT Well | 4 | 4% |
| Tom's Hardware | 4 | 4% |
| Scientific American | 4 | 4% |
| KFF Health News | 4 | 4% |
| NPR Health News | 4 | 4% |

**Low-score articles (≤30):**

- `[ 22]` [Animikii News River] A new illustrated Indigenous Data Sovereignty primer and more  
  <https://newsriver.animikii.com/archive/a-new-illustrated-indigenous-data-sovereignty/>
- `[ 18]` [Tom's Hardware] Beijing AI bar that offers unlimited free DeepSeek coding tokens with $1.50 drink haemorrhaging cash — 'the bar is completely losing money, ' owner admits  
  <https://www.tomshardware.com/tech-industry/artificial-intelligence/beijing-ai-bar-pours-pints-of-foam-with-free-deepseek-tokens-served-from-two-nvidia-dgx-sparks>
- `[ 10]` [Tom's Hardware] Ajinomoto reportedly cuts critical chip packaging film supply to China by 30% as domestic substitutes race to qualify — ABF restriction comes following Beijing's rare earth export curbs  
  <https://www.tomshardware.com/tech-industry/semiconductors/ajinomoto-reportedly-cuts-abf-chip-packaging-film-supply-to-china-by-30-percent>
- `[ 10]` [Nautilus] How the Narwhal Got Its Twisted Tusk  
  <https://nautil.us/how-the-narwhal-got-its-twisted-tusk-1283930/>
- `[ 26]` [globalnews.ca] B.C. wildfire latest: Thousands of people still out of their homes, but there is some good news  
  <https://globalnews.ca/news/12025175/bc-wildfire-smoke-warnings-news-conference/>

---

## Scrub Pass Findings

_Scrub pass skipped. Re-run without `--no-scrub` to enable._

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 91 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 25 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏛️ Architecture & Design** has 36 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏛️ Architecture & Design** is dominated by **ArchDaily** (23 articles, 43%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **🏠 Homelab & DIY** has 25 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌾 Homestead & Hobby Farm** has 10 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🌾 Homestead & Hobby Farm** is dominated by **Hobby Farms** (5 articles, 42%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **🏔️ Williams Lake Local** has 25 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏔️ Williams Lake Local** is dominated by **My Cariboo Now** (19 articles, 41%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **📰 General News** has 165 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🥾 Outdoors & Recreation** has a low average score (34.0) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🥾 Outdoors & Recreation** has 13 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 43 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (22.3) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🚀 Sci-Fi & Culture** has 8 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌿 Health & Wellness** has 69 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.

---

_Report generated by `score_scrub_report.py` · 11 feeds · 798 articles · 2026-08-23 13:41 UTC_
