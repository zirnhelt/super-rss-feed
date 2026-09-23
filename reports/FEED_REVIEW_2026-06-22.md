# Feed Scoring & Scrubbing Report

_Generated: 2026-06-22 03:29 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 8 |
| Total articles | 547 |
| Stale articles (>48h) | 488 |
| Scrub pass | ✅ ran |
| Flagged for removal | 18 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 80 | 🔴 21.1 | 0–80 | 72 | TechRadar (10) |
| 🌍 Climate & Energy | 24 | 🔴 10.5 | 0–51 | 20 | ScienceDaily (4) |
| 🏠 Homelab & DIY | 11 | 🔴 14.3 | 0–76 | 10 | XDA Developers (3) |
| 🏔️ Williams Lake Local | 30 | 🟢 78.2 | 22–90 | 26 | Williams Lake Tribune (15) |
| 📰 General News | 324 | 🟡 61.4 | 20–99 | 287 | Al Jazeera English (43) |
| 🔬 Science | 0 | 🔴 0.0 | 0–0 | 0 | — (0) |
| 🚀 Sci-Fi & Culture | 12 | 🔴 19.9 | 2–83 | 11 | Boing Boing (3) |
| 🌿 Health & Wellness | 66 | 🔴 38.5 | 6–75 | 62 | STAT News (11) |

---

## Per-Feed Detail

### 🔴 🤖 AI/ML & Tech

- **Articles**: 80 (80 scored)
- **Score**: avg 21.1 | min 0 | max 80
- **Stale** (>48h): 72
- **Avg age**: 91.5h

**Score distribution:**
```
  0–9     │ ████████████████████  41
  10–19   │ ███████               15
  20–29   │                        1
  30–39   │ █                      4
  40–49   │ ██                     6
  50–59   │ █                      4
  60–69   │                        2
  70–79   │ ██                     6
  80–89   │                        1
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| TechRadar | 10 | 12% |
| Business Insider | 8 | 10% |
| CNET | 6 | 8% |
| Kagi Small Web | 6 | 8% |
| Toms Guide | 5 | 6% |
| The Verge | 5 | 6% |
| Android Authority | 4 | 5% |
| Neowin | 4 | 5% |

**Low-score articles (≤30):**

- `[  0]` [XDA Developers] A Microsoft researcher built a goat-powered LLM in Age of Empires II to prove it's not sentient  
  <https://www.xda-developers.com/a-microsoft-researcher-built-an-llm-in-age-of-empires-using-goats-to-prove-its-not-sentient/>
- `[  8]` [The Verge] The Atlantic created a searchable database of the music used to train AI  
  <https://www.theverge.com/ai-artificial-intelligence/953183/the-atlantic-searchable-database-music-ai-training-data>
- `[  1]` [MacRumors] Apple Unveiled These Five New Apps Last Week  
  <https://www.macrumors.com/2026/06/20/apple-unveiled-these-five-new-apps/>
- `[  9]` [TechCrunch] Every new iOS 27 feature that’s worth knowing about  
  <https://techcrunch.com/2026/06/20/every-new-ios-27-feature-thats-worth-knowing-about/>
- `[  6]` [Business Insider] The math behind Silicon Valley's  millionaire factory  
  <https://www.businessinsider.com/spacex-anthropic-openai-engineers-filthy-rich-2026-6>
- `[  4]` [Business Insider] Apple may have finally fixed its most embarrassing software  
  <https://www.businessinsider.com/siri-ai-review-apple-fixes-features-ios27-2026-6>
- `[  8]` [New Atlas] Uber, Wayve and Stellantis join forces to progress robotaxi technology  
  <https://newatlas.com/automotive/uber-wayve-stellantis-robotaxi-technology/>
- `[  0]` Download ChatGPT (free) for Windows, macOS, Android, APK, iOS and Web App | Gizmodo  
  <https://gizmodo.com/download/chatgpt>
- `[  1]` [New Atlas] Nvidia RTX Spark platform is AI workhorse first, gamer's friend second  
  <https://newatlas.com/consumer-tech/nvidia-rtx-spark-superchip-ai/>
- `[  3]` [New Atlas] Canyon Predict is a traffic-shy cyclist's dream come true  
  <https://newatlas.com/bicycles/canyon-predict-concept-bike/>
- `[  7]` [TechRadar] Dutton Ranch season 2 'deserves to be made' according to one star — confirming Yellowstone spinoff cast is 'waiting in hope' for Paramount+ renewal  
  <https://www.techradar.com/streaming/paramount-plus/dutton-ranch-season-2-renewal-comment>
- `[  3]` [Al Jazeera English] How is China using AI in the classroom?  
  <https://www.aljazeera.com/video/the-take-2/2026/6/19/how-is-china-using-ai-in-the-classroom?traffic_source=rss>
- `[  5]` [TechRadar] Microsoft warns AI agents are being 'AutoJack'-ed to deliver RCE payloads by browsing untrusted websites  
  <https://www.techradar.com/pro/security/microsoft-warns-ai-agents-are-being-autojack-ed-to-deliver-rce-payloads-by-browsing-untrusted-websites>
- `[  7]` [TechRadar] Why cybersecurity needs hybrid AI, not platform consolidation  
  <https://www.techradar.com/pro/why-cybersecurity-needs-hybrid-ai-not-platform-consolidation>
- `[ 18]` [TechRadar] As growth gets harder, AI emerges as the key to MSP success  
  <https://www.techradar.com/pro/as-growth-gets-harder-ai-emerges-as-the-key-to-msp-success>

### 🔴 🌍 Climate & Energy

- **Articles**: 24 (24 scored)
- **Score**: avg 10.5 | min 0 | max 51
- **Stale** (>48h): 20
- **Avg age**: 94.6h

**Score distribution:**
```
  0–9     │ ████████████████████  14
  10–19   │ ███████████            8
  20–29   │ █                      1
  30–39   │                        0
  40–49   │                        0
  50–59   │ █                      1
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 4 | 17% |
| InsideEVs | 3 | 12% |
| NYT Business | 2 | 8% |
| Kagi Small Web | 2 | 8% |
| WIRED | 2 | 8% |
| Atlas Obscura | 1 | 4% |
| New Atlas | 1 | 4% |
| Kottke.org | 1 | 4% |

**Low-score articles (≤30):**

- `[ 16]` 🔓 [NYT Business] A Humble 3-Wheel Electric Vehicle Lands Toyota in Federal Court  
  <https://www.nytimes.com/2026/06/20/business/toyota-africa-electric-vehicles-lawsuit.html>
- `[ 13]` [ScienceDaily] A single cobalt shock could trigger global EV battery supply chaos  
  <https://www.sciencedaily.com/releases/2026/06/260619101402.htm>
- `[  1]` [ScienceDaily] The first primates may have evolved in the cold, not the tropics  
  <https://www.sciencedaily.com/releases/2026/06/260616103124.htm>
- `[  8]` [ScienceDaily] Hidden geological process offsets carbon emissions from thawing permafrost  
  <https://www.sciencedaily.com/releases/2026/06/260619101343.htm>
- `[ 20]` [Atlas Obscura] Grotte Scladina in Andenne, Belgium  
  <https://www.atlasobscura.com/places/grotte-scladina>
- `[  3]` [New Atlas] Tesla Cybercab specs revealed, full autonomy still unclear  
  <https://newatlas.com/automotive/tesla-cybercab-specs/>
- `[ 11]` [Kottke.org] Record winter temperatures in Antarctic raise fears over...  
  <https://kottke.org/26/06/0049177-record-winter-temperature>
- `[ 14]` 🔓 [NYT Top Stories] The Major Oak, Ancient Tree of Robin Hood Legend, Has Died  
  <https://www.nytimes.com/2026/06/18/world/europe/major-oak-tree-dies.html>
- `[  6]` [ScienceAlert] World's Richest 10% Are Costing Earth Trillions, Study Finds  
  <https://www.sciencealert.com/worlds-richest-10-are-costing-earth-trillions-study-finds>
- `[  8]` [InsideEVs] Forget Solid-State. This EV Battery Breakthrough Is Ready To Upend The Market Now  
  <https://insideevs.com/news/799157/general-motors-silicon-anodes-solid-state-batteries/>
- `[ 10]` [ScienceDaily] These bees have nowhere to hide from extreme heat  
  <https://www.sciencedaily.com/releases/2026/06/260617032157.htm>
- `[  8]` [CNET] Xiaomi May Have Just Invented a Robot Arm for EV Charging  
  <https://www.cnet.com/roadshow/news/xiaomi-robot-arm-ev-charging-reports/>
- `[ 19]` 🔓 [Williams Lake Tribune] BC Hydro unveils plan to increase capacity by 7% through dam upgrades  
  <https://wltribune.com/2026/06/17/bc-hydro-unveils-plan-to-increase-capacity-by-7-through-dam-upgrades/>
- `[  7]` [Quartz] Do solar panels in space produce way more power? Here's the math behind the claim  
  <https://qz.com/space-solar-panels-8x-power-claim-math-061526>
- `[  2]` [Kagi Small Web] Challenge 37  
  <https://antharris.co/2026/06/17/challenge-37/>

### 🔴 🏠 Homelab & DIY

- **Articles**: 11 (11 scored)
- **Score**: avg 14.3 | min 0 | max 76
- **Stale** (>48h): 10
- **Avg age**: 79.7h

**Score distribution:**
```
  0–9     │ ████████████████████   9
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │ ██                     1
  60–69   │                        0
  70–79   │ ██                     1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| XDA Developers | 3 | 27% |
| How-To Geek | 2 | 18% |
| MacRumors | 1 | 9% |
| New Atlas | 1 | 9% |
| Tom's Hardware | 1 | 9% |
| Make Magazine | 1 | 9% |
| TechRadar | 1 | 9% |
| CNET | 1 | 9% |

**Low-score articles (≤30):**

- `[  0]` [XDA Developers] 6 Jellyfin settings that transformed my media server from frustrating to genuinely premium  
  <https://www.xda-developers.com/best-jellyfin-features-that-took-my-media-server-to-the-next-level/>
- `[  0]` [XDA Developers] This self-hosted research tool does what NotebookLM does, but without the daily limits  
  <https://www.xda-developers.com/self-hosted-notebooklm-alternative-without-daily-limits/>
- `[  5]` The MacRumors Show: Hands-On With iOS 27, Brutal watchOS 27 Cuts, and More  
  <https://www.macrumors.com/2026/06/19/the-macrumors-show-hands-on-with-ios-27/>
- `[  6]` [How-To Geek] 3 Home Assistant projects to do more with your tech this weekend (June 19-21)  
  <https://www.howtogeek.com/home-assistant-projects-to-try-this-weekend-june-19-21/>
- `[  2]` [Tom's Hardware] Bambu Lab launches PLA Pure filament — New material boasts kid-safe toy certifications and "asbestos-free" talc  
  <https://www.tomshardware.com/3d-printing/bambu-lab-launches-pla-pure-filament-new-material-boasts-kid-safe-toy-certifications-and-asbestos-free-talc>
- `[  0]` [XDA Developers] The setup day most Bambu Lab owners skip is the only one that matters  
  <https://www.xda-developers.com/setup-day-most-bambu-lab-owners-skip-matters/>
- `[  5]` [Make Magazine] Learn SketchUp by Modeling DIY Lego Bricks  
  <https://makezine.com/projects/learn-sketchup-by-modeling-diy-lego-bricks/>
- `[  9]` [TechRadar] 'Quirky design, unbeatable speed and quality': Bambu Lab's 5-star 3D printer for beginners just dropped to an unmissable price in the 4th anniversary sale  
  <https://www.techradar.com/pro/quirky-design-unbeatable-speed-and-quality-bambu-labs-5-star-3d-printer-for-beginners-just-dropped-to-an-unmissable-price-in-the-4th-anniversary-sale>
- `[  0]` [CNET] Best Home Security Cameras for Apple HomeKit and Siri in 2026  
  <https://www.cnet.com/home/security/best-home-security-cameras-with-apple-homekit-and-siri/>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 30 (30 scored)
- **Score**: avg 78.2 | min 22 | max 90
- **Stale** (>48h): 26
- **Avg age**: 82.7h
- **Local-flagged**: 30

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ███                    2
  30–39   │ ███                    2
  40–49   │                        0
  50–59   │                        0
  60–69   │ █                      1
  70–79   │ █                      1
  80–89   │ ████████████████████  13
  90–100  │ ████████████████      11
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 15 | 50% ⚠️ |
| My Cariboo Now | 11 | 37% |
| CFJC Today Kamloops | 2 | 7% |
| 100 Mile Free Press | 1 | 3% |
| Quesnel Cariboo Observer | 1 | 3% |

**Low-score articles (≤30):**

- `[ 22]` 🔓 [Williams Lake Tribune] Lytton wildfire grows to 100 hectares, Highway 1 impacted  
  <https://wltribune.com/2026/06/19/10-hectare-wildfire-discovered-4-km-south-of-lytton/>
- `[ 23]` 🔓 [Williams Lake Tribune] Eric Peter Johansen  
  <https://wltribune.com/2026/06/19/eric-peter-johansen/>

### 🟡 📰 General News

- **Articles**: 324 (324 scored)
- **Score**: avg 61.4 | min 20 | max 99
- **Stale** (>48h): 287
- **Avg age**: 88.5h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ███                   14
  30–39   │ ██                    11
  40–49   │ █████████             42
  50–59   │ ██████████████        64
  60–69   │ ██████████████████    78
  70–79   │ ████████████████████  86
  80–89   │ ██████                28
  90–100  │                        1
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Al Jazeera English | 43 | 13% |
| Boing Boing | 25 | 8% |
| Pique Newsmagazine | 23 | 7% |
| TechRadar | 19 | 6% |
| Global News | 18 | 6% |
| Williams Lake Tribune | 17 | 5% |
| Business Insider | 17 | 5% |
| NYT Top Stories | 13 | 4% |

**Low-score articles (≤30):**

- `[ 25]` Free shuttle to serve Spirit of the Rockies Festival : My East Kootenay Now  
  <https://www.myeastkootenaynow.com/56081/news/transit/free-shuttle-to-serve-spirit-of-the-rockies-festival/>
- `[ 26]` [XDA Developers] Bambu's A2L shows why larger build plates are becoming the real differentiator for budget printers  
  <https://www.xda-developers.com/bambu-a2l-larger-build-plates-budget-printers/>
- `[ 21]` [Nautilus] If You’re Counting on Calcium and Vitamin D Supplements to Prevent Fractures, Think Again  
  <https://nautil.us/if-youre-counting-on-calcium-and-vitamin-d-supplements-to-prevent-fractures-think-again-1282054/>
- `[ 26]` 🔓 [NYT Top Stories] Claiming an Antifa Plot, U.S. Charges 15 in Minneapolis With Conspiracy  
  <https://www.nytimes.com/2026/06/16/us/minnesota-immigration-charges-antifa.html>
- `[ 22]` [APTN News] Forum les arts et la ville : comment collaborer pour l’avenir culturel autochtone  
  <https://www.aptnnews.ca/reportages/forum-les-arts-et-la-ville-comment-collaborer-pour-lavenir-culturel-autochtone/>
- `[ 28]` [APTN News] Kwé – un festival qui t’emporte à la rencontre des peuples autochtones  
  <https://www.aptnnews.ca/reportages/kwe-un-festival-qui-temporte-a-la-rencontre-des-peuples-autochtones/>
- `[ 25]` [How-To Geek] These are the 7 travel apps I install before every trip  
  <https://www.howtogeek.com/travel-apps-i-install-before-every-trip/>
- `[ 22]` 🔓 [Williams Lake Tribune] New well-being plan for children aims for better coordination in B.C. government  
  <https://wltribune.com/2026/06/16/new-well-being-plan-for-children-aims-for-better-coordination-in-b-c-government/>
- `[ 21]` 🔓 [Williams Lake Tribune] No structures lost in suspicious West Kelowna wildfire: Fire Chief  
  <https://wltribune.com/2026/06/16/no-structures-lost-in-suspicious-west-kelowna-wildfire-fire-chief/>
- `[ 22]` [Kottke.org] A million new SpaceX satellites will destroy the night...  
  <https://kottke.org/26/06/0049147-a-million-new-spacex-sate>
- `[ 23]` [NYT Well] These Dating Apps Want You to Meet at the Gym  
  <https://www.nytimes.com/2026/06/16/well/move/dating-apps-fitness-hyrox.html>
- `[ 27]` [NYT Well] Can Prescription Eyeglasses Protect You From the Sun?  
  <https://www.nytimes.com/2026/06/16/well/eyeglasses-uv-protection.html>
- `[ 22]` 🔓 [Williams Lake Tribune] ‘Extremely concerning’: B.C. environmentalists outraged by minister’s caribou comments  
  <https://wltribune.com/2026/06/16/extremely-concerning-b-c-environmentalists-outraged-by-ministers-caribou-comments/>
- `[ 20]` [Android Authority] This new wearable is trying to save you from yourself (and your phone)  
  <https://www.androidauthority.com/jaye-band-launch-3676173/>

### 🔴 🔬 Science

- **Articles**: 0 (0 scored)
- **Score**: avg 0.0 | min 0 | max 0
- **Stale** (>48h): 0
- **Avg age**: 0.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │                        0
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 12 (12 scored)
- **Score**: avg 19.9 | min 2 | max 83
- **Stale** (>48h): 11
- **Avg age**: 84.8h

**Score distribution:**
```
  0–9     │ ████████████████████   4
  10–19   │ ████████████████████   4
  20–29   │ ██████████             2
  30–39   │                        0
  40–49   │ █████                  1
  50–59   │                        0
  60–69   │                        0
  70–79   │                        0
  80–89   │ █████                  1
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Boing Boing | 3 | 25% |
| Reactor Magazine | 3 | 25% |
| Neowin | 1 | 8% |
| The Verge | 1 | 8% |
| Quartz | 1 | 8% |
| Pluralistic | 1 | 8% |
| Kagi Small Web | 1 | 8% |
| TechRadar | 1 | 8% |

**Low-score articles (≤30):**

- `[  5]` [Neowin] Weekend PC Game Deals: Cyberpunk 2077, Split Fiction, Sonic Racing, and more  
  <https://www.neowin.net/news/weekend-pc-game-deals-cyberpunk-2077-split-fiction-sonic-racing-and-more/>
- `[ 13]` [Boing Boing] Cyberdeck with punishingly minimal 30% keyboard  
  <https://boingboing.net/2026/06/19/cyberdeck-with-punishingly-minimal-30-keyboard.html>
- `[ 13]` [Boing Boing] The man who built the spaceships for 2001, Alien, and Empire has died  
  <https://boingboing.net/2026/06/19/the-man-who-built-the-spaceships-for-2001-alien-and-empire-has-died.html>
- `[ 12]` [The Verge] In season 2 of Sugar, Colin Farrell’s quirky detective becomes much more human  
  <https://www.theverge.com/entertainment/951638/sugar-season-2-colin-farrell-interview-apple-tv>
- `[ 23]` [Quartz] 5 of the best book subscription boxes for avid readers  
  <https://qz.com/-best-book-subscription-boxes-for-avid-readers-readers-digest>
- `[ 25]` [Boing Boing] Becoming a British royal with nothing more than confidence and an accent  
  <https://boingboing.net/2026/06/18/becoming-a-british-royal-with-nothing-more-than-confidence-and-an-accent.html>
- `[  6]` [Reactor Magazine] Five Anime for Fans of John Carpenter  
  <https://reactormag.com/five-anime-for-fans-of-john-carpenter/>
- `[  4]` Pluralistic: The (real) dead economy theory (17 Jun 2026)  
  <https://pluralistic.net/2026/06/17/its-the-stupid-economy-stupid/>
- `[  2]` [Kagi Small Web] Book review: New British Drama in 15 Scenes  
  <https://loureviews.blog/2026/06/17/book-review-new-british-drama-in-15-scenes/>
- `[ 13]` [Reactor Magazine] Five Very Different Science Fictional Takes on Space Habitats  
  <https://reactormag.com/five-very-different-science-fictional-takes-on-space-habitats/>

### 🔴 🌿 Health & Wellness

- **Articles**: 66 (66 scored)
- **Score**: avg 38.5 | min 6 | max 75
- **Stale** (>48h): 62
- **Avg age**: 93.2h

**Score distribution:**
```
  0–9     │ ███                    3
  10–19   │ ████████████████████  18
  20–29   │ ███                    3
  30–39   │ ███████                7
  40–49   │ ███████████████       14
  50–59   │ █████                  5
  60–69   │ ███████████           10
  70–79   │ ██████                 6
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| STAT News | 11 | 17% |
| New Atlas | 7 | 11% |
| Business Insider | 5 | 8% |
| NYT Top Stories | 5 | 8% |
| Quartz | 4 | 6% |
| NPR Health News | 3 | 5% |
| ScienceAlert | 3 | 5% |
| ScienceDaily | 3 | 5% |

**Low-score articles (≤30):**

- `[ 11]` [ScienceAlert] Sugar-Free Diets May Have a Hidden Side Effect, Study in Mice Suggests  
  <https://www.sciencealert.com/sugar-free-diets-may-have-a-hidden-side-effect-study-in-mice-suggests>
- `[ 17]` [Cool Tools] Book Freak #214: Thoughts Without a Thinker  
  <https://kk.org/cooltools/book-freak-214-thoughts-without-a-thinker/>
- `[ 10]` [New Atlas] Quartz countertops may be causing a public health crisis in the US  
  <https://refractor.io/society-health/quartz-countertops-public-health-crisis-us/>
- `[ 13]` [New Atlas] Skyscraper-style tiny house sleeps two in a compact footprint  
  <https://newatlas.com/tiny-houses/la-ruche-quadrapol/>
- `[ 26]` [NPR Health News] Tick season is getting worse. Can managing deer help?  
  <https://www.npr.org/2026/06/19/nx-s1-5856461/tick-deer-alpha-gal-lonestar>
- `[ 10]` [The Guardian Global Development] Midwives on frontline of childbirth deaths crisis denied visas for key summit  
  <https://www.theguardian.com/global-development/2026/jun/19/midwives-africa-asia-mother-baby-childbirth-deaths-crisis-denied-visas-summit-portugal>
- `[ 12]` [NYT Well] Dads Get Postpartum Depression, Too  
  <https://www.nytimes.com/2026/06/19/well/postpartum-depression-men-fathers.html>
- `[ 11]` [NYT Well] How to Exercise Before and After a Joint Replacement  
  <https://www.nytimes.com/2026/06/19/well/move/exercise-hip-knee-replacement-surgery.html>
- `[ 10]` [Toms Guide] This is what's really causing your tomato leaves to curl — and how to actually fix it  
  <https://www.tomsguide.com/home/gardening/this-is-whats-really-causing-your-tomato-leaves-to-curl-and-how-to-actually-fix-it>
- `[ 27]` [Boing Boing] The ancient practice of mummifying a man in honey to sell as medicine  
  <https://boingboing.net/2026/06/18/the-ancient-practice-of-mummifying-a-man-in-honey-to-sell-as-medicine.html>
- `[ 10]` [STAT News] STAT+: Cambrian’s experimental longevity drug mimics exercise  
  <https://www.statnews.com/2026/06/18/biotech-news-cambrians-experimental-longevity-drug-mimics-exercise/?utm_campaign=rss>
- `[ 13]` [ScienceDaily] Researchers found 8 common food additives linked to high blood pressure and heart disease  
  <https://www.sciencedaily.com/releases/2026/06/260617032204.htm>
- `[ 10]` [New Atlas] Hair-loss pill passes critical test with 80% success rate  
  <https://newatlas.com/health-wellbeing/hair-loss-pill-human-trial/>
- `[ 13]` 🔓 [NYT Top Stories] We Ran the Numbers. Remote Work Is Bad for Us.  
  <https://www.nytimes.com/2026/06/17/opinion/remote-work-depression.html>
- `[ 13]` [CNET] FDA Clears Solius Pro, the First Over-the-Counter Home UVB Panel for Vitamin D  
  <https://www.cnet.com/health/fda-clears-solius-pro-first-over-the-counter-home-uvb-panel-vitamin-d/>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (18)

- **[🤖 AI/ML & Tech]** `score 39` — Trader and podcast host Ed Elson unpacks why he's bearish on coming mega-IPOs  
  Issue: `clickbait`  
  <https://www.businessinsider.com/profg-podcast-ed-elson-ipos-stocks-spacex-openai-anthropic-spcx-2026-6>
- **[🤖 AI/ML & Tech]** `score 40` — Allbirds is now Smartbirds, and its AI-focused CEO says 'people won't even remember the shoes'  
  Issue: `clickbait`  
  <https://www.businessinsider.com/company-formerly-known-as-allbirds-talks-about-its-ai-pivot-2026-6>
- **[🌍 Climate & Energy]** `score 20` — Grotte Scladina in Andenne, Belgium  
  Issue: `duplicate`  
  <https://www.atlasobscura.com/places/grotte-scladina>
- **[🏔️ Williams Lake Local]** `score 23` — Eric Peter Johansen  
  Issue: `clickbait`  
  <https://wltribune.com/2026/06/19/eric-peter-johansen/>
- **[📰 General News]** `score 26` — Bambu's A2L shows why larger build plates are becoming the real differentiator for budget printers  
  Issue: `clickbait`  
  <https://www.xda-developers.com/bambu-a2l-larger-build-plates-budget-printers/>
- **[📰 General News]** `score 21` — If You're Counting on Calcium and Vitamin D Supplements to Prevent Fractures, Think Again  
  Issue: `clickbait`  
  <https://nautil.us/if-youre-counting-on-calcium-and-vitamin-d-supplements-to-prevent-fractures-think-again-1282054/>
- **[📰 General News]** `score 25` — These are the 7 travel apps I install before every trip  
  Issue: `deals`  
  <https://www.howtogeek.com/travel-apps-i-install-before-every-trip/>
- **[📰 General News]** `score 31` — Your expensive earbuds still sound awful on calls, and this is why  
  Issue: `clickbait`  
  <https://www.makeuseof.com/your-expensive-earbuds-still-sound-awful-on-calls-this-is-why/>
- **[📰 General News]** `score 23` — These Dating Apps Want You to Meet at the Gym  
  Issue: `advice`  
  <https://www.nytimes.com/2026/06/16/well/move/dating-apps-fitness-hyrox.html>
- **[📰 General News]** `score 27` — Can Prescription Eyeglasses Protect You From the Sun?  
  Issue: `advice`  
  <https://www.nytimes.com/2026/06/16/well/eyeglasses-uv-protection.html>
- **[📰 General News]** `score 20` — This new wearable is trying to save you from yourself (and your phone)  
  Issue: `clickbait`  
  <https://www.androidauthority.com/jaye-band-launch-3676173/>
- **[🚀 Sci-Fi & Culture]** `score 23` — 5 of the best book subscription boxes for avid readers  
  Issue: `deals`  
  <https://qz.com/-best-book-subscription-boxes-for-avid-readers-readers-digest>
- **[🚀 Sci-Fi & Culture]** `score 25` — Becoming a British royal with nothing more than confidence and an accent  
  Issue: `celebrity`  
  <https://boingboing.net/2026/06/18/becoming-a-british-royal-with-nothing-more-than-confidence-and-an-accent.html>
- **[🌿 Health & Wellness]** `score 40` — RFK Jr. is making it a hot sauerkraut summer at the White House  
  Issue: `celebrity`  
  <https://www.businessinsider.com/sauerkraut-diet-rfk-jr-health-benefits-what-to-know-2026-6>
- **[🌿 Health & Wellness]** `score 17` — Book Freak #214: Thoughts Without a Thinker  
  Issue: `clickbait`  
  <https://kk.org/cooltools/book-freak-214-thoughts-without-a-thinker/>
- **[🌿 Health & Wellness]** `score 33` — Six of the biggest health news stories today  
  Issue: `duplicate`  
  <https://www.statnews.com/2026/06/18/health-news-high-end-infant-formula-synthetic-opioids-ftc/?utm_campaign=rss>
- **[🌿 Health & Wellness]** `score 25` — Takeaways From the Runoff and Primary Elections in Georgia, Alabama and Oklahoma  
  Issue: `clickbait`  
  <https://www.nytimes.com/2026/06/17/us/politics/georgia-alabama-elections-trump-takeaways.html>
- **[🌿 Health & Wellness]** `score 17` — Mental Health Can Complicate Family Planning  
  Issue: `advice`  
  <https://www.nytimes.com/2026/06/17/well/mind/mental-health-family-children.html>

---

## Recommendations

- ⚠️ **🤖 AI/ML & Tech** has a low average score (21.1) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🤖 AI/ML & Tech** has 72 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🌍 Climate & Energy** has a low average score (10.5) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🌍 Climate & Energy** has 20 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🏠 Homelab & DIY** has a low average score (14.3) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🏠 Homelab & DIY** has 10 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 26 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏔️ Williams Lake Local** is dominated by **Williams Lake Tribune** (15 articles, 50%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **📰 General News** has 287 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (19.9) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🚀 Sci-Fi & Culture** has 11 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌿 Health & Wellness** has 62 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 18 article(s) should be removed (`clickbait` ×9, `advice` ×3, `duplicate` ×2, `deals` ×2, `celebrity` ×2) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 8 feeds · 547 articles · 2026-06-22 03:29 UTC_
