# Feed Scoring & Scrubbing Report

_Generated: 2026-08-30 17:17 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 11 |
| Total articles | 676 |
| Stale articles (>48h) | 460 |
| Scrub pass | ✅ ran |
| Flagged for removal | 5 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 120 | 🟡 46.4 | 12–59 | 89 | Tom's Hardware (19) |
| 🌍 Climate & Energy | 37 | 🟡 47.7 | 0–63 | 26 | InsideEVs (4) |
| 🏛️ Architecture & Design | 42 | 🔴 43.6 | 13–72 | 30 | ArchDaily (16) |
| 🏠 Homelab & DIY | 42 | 🟡 51.4 | 17–62 | 26 | XDA Developers (10) |
| 🌾 Homestead & Hobby Farm | 10 | 🔴 19.1 | 2–53 | 9 | Small Farm Canada (3) |
| 🏔️ Williams Lake Local | 40 | 🟢 74.7 | 27–91 | 30 | Williams Lake Tribune (21) |
| 📰 General News | 220 | 🟡 63.2 | 34–82 | 140 | NYT Business (23) |
| 🥾 Outdoors & Recreation | 17 | 🔴 29.4 | 8–50 | 11 | Outside Online (9) |
| 🔬 Science | 49 | 🟡 46.2 | 10–64 | 34 | ScienceDaily (19) |
| 🚀 Sci-Fi & Culture | 14 | 🔴 26.6 | 8–58 | 11 | Edge (GamesRadar) (3) |
| 🌿 Health & Wellness | 85 | 🟡 52.4 | 10–76 | 54 | Scientific American (6) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 120 (120 scored)
- **Score**: avg 46.4 | min 12 | max 59
- **Stale** (>48h): 89
- **Avg age**: 64.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        1
  20–29   │ █                      3
  30–39   │ ███████               19
  40–49   │ ██████████████████    46
  50–59   │ ████████████████████  51
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Tom's Hardware | 19 | 16% |
| WIRED | 12 | 10% |
| Business Insider | 12 | 10% |
| TechRadar | 11 | 9% |
| TechCrunch | 10 | 8% |
| Fast Company | 5 | 4% |
| ZDNet | 5 | 4% |
| Android Authority | 4 | 3% |

**Low-score articles (≤30):**

- `[ 12]` [Neowin] Sonos Arc Ultra Soundbar with Dolby Atmos gets $200 price drop  
  <https://www.neowin.net/deals/sonos-arc-ultra-soundbar-with-dolby-atmos-gets-200-price-drop/?utm_source=rss>
- `[ 28]` [Tom's Hardware] DLSS 5 has already been ported to work on RTX 4000 Series graphics cards — incompatible CUDA instructions get patched to work on previous-gen hardware  
  <https://www.tomshardware.com/pc-components/gpus/exclusive-dlss-5-has-already-been-ported-to-work-on-rtx-4000-series-graphics-cards-incompatible-cuda-instructions-get-patched-to-work-on-previous-gen-hardware>
- `[ 30]` [Android Authority] Gemini Notebook now imports your Google Play Books titles, turning shelfware into notes  
  <https://www.androidauthority.com/google-gemini-notebook-lm-play-books-3704207/>
- `[ 27]` [TechCrunch] Plaud’s new earphones come with an eSIM-enabled case for talking to AI agents  
  <https://techcrunch.com/2026/08/27/plauds-new-earphones-come-with-an-esim-enabled-case-for-talking-to-ai-agents/>
- `[ 28]` 🔓 [Fast Company] Women are sounding the alarm on AI. Leaders should listen  
  <https://www.fastcompany.com/91584377/women-are-sounding-the-alarm-on-ai-leaders-should-listen-ai-dangers-women-technology>
- `[ 30]` [Neowin] Google's latest speech-to-text Gemini model offers a platter of new features  
  <https://www.neowin.net/news/googles-latest-speech-to-text-gemini-model-offers-a-platter-of-new-features/?utm_source=rss>

### 🟡 🌍 Climate & Energy

- **Articles**: 37 (37 scored)
- **Score**: avg 47.7 | min 0 | max 63
- **Stale** (>48h): 26
- **Avg age**: 63.0h

**Score distribution:**
```
  0–9     │ ██                     2
  10–19   │                        0
  20–29   │ █                      1
  30–39   │ ██                     2
  40–49   │ █████████              9
  50–59   │ ████████████████████  20
  60–69   │ ███                    3
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| InsideEVs | 4 | 11% |
| Mother Jones | 3 | 8% |
| Civil Eats | 2 | 5% |
| NYT Business | 2 | 5% |
| Scientific American | 2 | 5% |
| The Atlantic | 1 | 3% |
| Al Jazeera English | 1 | 3% |
| TechRadar | 1 | 3% |

**Low-score articles (≤30):**

- `[  0]` [Civil Eats] Wendy Johnson  
  <https://civileats.com/author/wjohnson/>
- `[  8]` [The Guardian Global Development] Moringa lattes and tigernut kebabs: the Ghanaians ‘taking back the power’ of their food  
  <https://www.theguardian.com/global-development/2026/aug/26/moringa-lattes-and-tigernut-kebabs-the-young-ghanaians-taking-back-the-power-of-their-food>
- `[ 29]` 🔓 [Fast Company] Forget bamboo. This startup wants the next toilet paper to be made from rice straw  
  <https://www.fastcompany.com/91594365/paddy-toilet-paper-made-from-rice-straw>

### 🔴 🏛️ Architecture & Design

- **Articles**: 42 (42 scored)
- **Score**: avg 43.6 | min 13 | max 72
- **Stale** (>48h): 30
- **Avg age**: 62.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      1
  20–29   │ ██                     2
  30–39   │ █████████████████     13
  40–49   │ ████████████████████  15
  50–59   │ ██████████             8
  60–69   │ █                      1
  70–79   │ ██                     2
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ArchDaily | 16 | 38% |
| Dezeen | 7 | 17% |
| Articles - passivehouseplus.co.uk | 2 | 5% |
| Canadian Architect | 2 | 5% |
| Architizer | 2 | 5% |
| Tom's Hardware | 2 | 5% |
| Old House Journal | 1 | 2% |
| New Atlas | 1 | 2% |

**Low-score articles (≤30):**

- `[ 13]` 🔓 Old House Journal Products &amp; Services Directory  
  <https://oldhouseonline.com/>
- `[ 24]` [ArchDaily] Casa Loto / Ezequiel Farca Studio  
  <https://www.archdaily.com/1183850/casa-loto-ezequiel-farca-studio>
- `[ 23]` [ArchDaily] A12 Apartment / DKA  
  <https://www.archdaily.com/1183511/a12-apartment-dka>
- `[ 30]` [ArchDaily] Tomaz Building / IDEIA1  
  <https://www.archdaily.com/1184135/tomaz-building-ideia1>

### 🟡 🏠 Homelab & DIY

- **Articles**: 42 (42 scored)
- **Score**: avg 51.4 | min 17 | max 62
- **Stale** (>48h): 26
- **Avg age**: 56.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      1
  20–29   │                        0
  30–39   │ ███                    3
  40–49   │ ███████████████       13
  50–59   │ ████████████████████  17
  60–69   │ █████████              8
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| XDA Developers | 10 | 24% |
| Hackaday | 6 | 14% |
| Tom's Hardware | 5 | 12% |
| TechRadar | 4 | 10% |
| Popular Woodworking | 4 | 10% |
| LoRaMeshDevices | 2 | 5% |
| How-To Geek | 2 | 5% |
| MakeUseOf | 1 | 2% |

**Low-score articles (≤30):**

- `[ 17]` 🔓 [Popular Woodworking] Kitchen Cabinet Essentials  
  <https://www.popularwoodworking.com/article/kitchen-cabinet-essentials/>

### 🔴 🌾 Homestead & Hobby Farm

- **Articles**: 10 (10 scored)
- **Score**: avg 19.1 | min 2 | max 53
- **Stale** (>48h): 9
- **Avg age**: 61.2h

**Score distribution:**
```
  0–9     │ ████████████████████   4
  10–19   │ ███████████████        3
  20–29   │ █████                  1
  30–39   │                        0
  40–49   │                        0
  50–59   │ ██████████             2
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Small Farm Canada | 3 | 30% |
| Kagi Small Web | 2 | 20% |
| Mother Earth News | 2 | 20% |
| Wikipedia  - Recent changes [en] | 1 | 10% |
| MacRumors | 1 | 10% |
| The Guardian Global Development | 1 | 10% |

**Low-score articles (≤30):**

- `[  2]` [Wikipedia  - Recent changes [en]] Jessie M. Scott  
  <https://en.wikipedia.org/w/index.php?title=Jessie_M._Scott&diff=1372120314&oldid=1337954980>
- `[  8]` [Kagi Small Web] 3 Days in the City of Angels - The Getty Center Museum  
  <https://justalittlefurther.com/just-a-little-further/2026/8/26/3-days-in-the-city-of-angels-the-getty-museums>
- `[  8]` [Mother Earth News] Free Guides on Self-Sufficiency  
  <https://www.motherearthnews.com/free-guides/>
- `[  8]` [Kagi Small Web] GIRLS THAT&rsquo;S FUCKING TERRIFYING,, PLEASE FACTORY RESET YOUR PHONES GET NEW ONES IF YOU HAVE TO GET&hellip;  
  <https://aniseandspearmint.tumblr.com/post/826144852135837696>
- `[ 12]` [MacRumors] Pikachu Visits Apple Park, Meets Tim Cook and John Ternus  
  <https://www.macrumors.com/2026/08/27/pikachu-apple-park-cook-ternus/>
- `[ 22]` [Small Farm Canada] Garden Hoops  
  <https://www.smallfarmcanada.ca/news/garden-hoops/>
- `[ 10]` [Mother Earth News] Crystal Schmidt  
  <https://www.motherearthnews.com/speakers/crystal-schmidt/>
- `[ 18]` Business Bootcamp for New Farmers| Small Farm Canada - Small Farm Canada  
  <https://www.smallfarmcanada.ca/headliners/registration-opens-for-business-bootcamp-for-new-farmers/>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 40 (40 scored)
- **Score**: avg 74.7 | min 27 | max 91
- **Stale** (>48h): 30
- **Avg age**: 65.6h
- **Local-flagged**: 40

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ██                     2
  30–39   │ █                      1
  40–49   │ ██                     2
  50–59   │ ██                     2
  60–69   │ █                      1
  70–79   │ ███████████           11
  80–89   │ ████████████████████  20
  90–100  │ █                      1
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 21 | 52% ⚠️ |
| My Cariboo Now | 12 | 30% |
| 100 Mile Free Press | 3 | 8% |
| Quesnel Cariboo Observer | 1 | 2% |
| Regional News Archives - Williams Lake Tribune | 1 | 2% |
| The Narwhal | 1 | 2% |
| The Tyee | 1 | 2% |

**Low-score articles (≤30):**

- `[ 27]` [My Cariboo Now] ICBC reminding drivers to monitor speeds in school zones  
  <https://news.google.com/rss/articles/CBMipwFBVV95cUxNSWZ5LV9pMHJvcHZLOUhqaHpBRWxrZklBWHpEc0tMdldhNGlSc0Rxb2FFMS1RdjIwY01adHBmaXNxbjlnNW1EaVR4SWRsaDZOUjY4OEZhTHRrTVZXUDhGOXpiY1Y4Wnp0em1DNXV0cXlMMnFMVmNvd2VFUlcycW9Lc0gzN0RzcW92M1FudlI0bTVvZ0pZZXgycEVUMGNGMXhVM2xzTHVmdw?oc=5>
- `[ 27]` [My Cariboo Now] Distracted driving is believed to be a factor in single vehicle collision  
  <https://news.google.com/rss/articles/CBMivAFBVV95cUxOQzcySUVIUXZxOWJybGMwRDFHVmc2QUpYR3ZEdHotTkdTTkp5WTk1Y2E1UkJlOUlHTkVKNnlOaUhqX21POUJZV0JLMERjcnNKTzFFY1RVUEdSaTlhTDgxa1VtdkdTdG1GTzhfMzl5REloelhQLTVPenVnYy1uanFHSVZhQUpCRDdxZ3BRUFRySDJDazVWQUtINkpLYzlpelFmQ1g5eG5KTGZUWlBpM2RuclhNTnhtU1JkMHNOUA?oc=5>

### 🟡 📰 General News

- **Articles**: 220 (220 scored)
- **Score**: avg 63.2 | min 34 | max 82
- **Stale** (>48h): 140
- **Avg age**: 60.2h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        1
  40–49   │                        1
  50–59   │ █████                 46
  60–69   │ ████████████████████ 156
  70–79   │ █                     15
  80–89   │                        1
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| NYT Business | 23 | 10% |
| NYT Top Stories | 17 | 8% |
| TechRadar | 16 | 7% |
| Williams Lake Tribune | 12 | 5% |
| Hackaday | 9 | 4% |
| Engadget | 9 | 4% |
| The Atlantic | 9 | 4% |
| WIRED | 7 | 3% |

### 🔴 🥾 Outdoors & Recreation

- **Articles**: 17 (17 scored)
- **Score**: avg 29.4 | min 8 | max 50
- **Stale** (>48h): 11
- **Avg age**: 64.0h

**Score distribution:**
```
  0–9     │ ██████████             2
  10–19   │ ██████████             2
  20–29   │ ████████████████████   4
  30–39   │ ████████████████████   4
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
| Outside Online | 9 | 53% ⚠️ |
| Live for the Outdoors (Country Walking) | 1 | 6% |
| The Verge | 1 | 6% |
| Kagi Small Web | 1 | 6% |
| Toms Guide | 1 | 6% |
| New Atlas | 1 | 6% |
| EarthSky | 1 | 6% |
| AFAR | 1 | 6% |

**Low-score articles (≤30):**

- `[  8]` 🔓 [Live for the Outdoors (Country Walking)] Hiking | LFTO - live for the outdoors  
  <https://www.livefortheoutdoors.com/hiking/>
- `[ 13]` 🔓 [The Verge] Vicariously hike the Appalachian in the gorgeous A Trail Tale  
  <https://www.theverge.com/entertainment/986461/hike-appalachian-trail-pixel-art-a-trail-tale>
- `[ 20]` 🔓 [Outside Online] LISTEN: The 19-Year Search for Michelle Vanek, Part 1  
  <https://www.outsideonline.com/outdoor-adventure/exploration-survival/michelle-vanek-podcast/>
- `[ 23]` 🔓 [Outside Online] He Set Out for a Day Hike on Granite Peak, Montana’s Highest Mountain. An 800-Foot Fall Killed Him.  
  <https://www.outsideonline.com/outdoor-adventure/hiking-and-backpacking/hiker-death-granite-peak-montana/>
- `[ 13]` 🔓 [Outside Online] The Ultimate Adventure Weekend  
  <https://www.outsideonline.com/culture/active-families/the-ultimate-adventure-weekend/>
- `[ 20]` [New Atlas] Laptop fire pit slims down portable campfires  
  <https://newatlas.com/outdoor-gear/rte-laptop-foldable-fire-pit/>
- `[  8]` [EarthSky] National parks from space: How many can you name?  
  <https://earthsky.org/earth/national-parks-from-space-quiz/>
- `[ 20]` [Atlas Obscura] Chickahominy Riverfront Park in Williamsburg, Virginia  
  <https://www.atlasobscura.com/places/chickahominy-riverfront-park>

### 🟡 🔬 Science

- **Articles**: 49 (49 scored)
- **Score**: avg 46.2 | min 10 | max 64
- **Stale** (>48h): 34
- **Avg age**: 61.9h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      2
  20–29   │ █                      2
  30–39   │ ████                   5
  40–49   │ █████████████████     18
  50–59   │ ████████████████████  21
  60–69   │                        1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 19 | 39% |
| ScienceAlert | 4 | 8% |
| Scientific American | 4 | 8% |
| EarthSky | 3 | 6% |
| Maclean's | 2 | 4% |
| NYT Top Stories | 2 | 4% |
| Popular Mechanics | 2 | 4% |
| Quanta Magazine | 2 | 4% |

**Low-score articles (≤30):**

- `[ 10]` 🔓 [Maclean's] Give a gift subscription  
  <https://secure.macleans.ca/H533FOTM>
- `[ 10]` 🔓 [Maclean's] Macleans  
  <https://secure.macleans.ca/>
- `[ 25]` [Toms Guide] Fantastic foams and supercritical science — why running shoes have improved so much in the past 10 years, explained by an expert who makes them  
  <https://www.tomsguide.com/wellness/running/fantastic-foams-and-supercritical-science-why-running-shoes-have-improved-so-much-in-the-past-10-years-explained-by-an-expert-who-makes-them>
- `[ 28]` [benchmark.pl] NASA sets Roman telescope launch for August 30  
  <https://www.benchmark.pl/teleskop-roman-mial-byc-szpiegiem-zostal-naukowcem-7323288797038656a>

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 14 (14 scored)
- **Score**: avg 26.6 | min 8 | max 58
- **Stale** (>48h): 11
- **Avg age**: 71.5h

**Score distribution:**
```
  0–9     │ ██████████             2
  10–19   │ ████████████████████   4
  20–29   │ ████████████████████   4
  30–39   │ █████                  1
  40–49   │ ██████████             2
  50–59   │ █████                  1
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Edge (GamesRadar) | 3 | 21% |
| Reactor Magazine | 3 | 21% |
| MakeUseOf | 2 | 14% |
| Comments for Solarpunk Magazine | 2 | 14% |
| NYT Top Stories | 1 | 7% |
| Global News | 1 | 7% |
| Android Authority | 1 | 7% |
| Scientific American | 1 | 7% |

**Low-score articles (≤30):**

- `[ 26]` 🔓 [NYT Top Stories] Book Review: ‘The Disappearers,’ by Marlon James  
  <https://www.nytimes.com/2026/08/30/books/review/the-disappearers-marlon-james.html>
- `[  8]` [MakeUseOf] September's best Kindle releases span cozy romance to epic fantasy, here's what to pre-order  
  <https://www.makeuseof.com/best-releases-coming-to-kindle-in-september-2026/>
- `[  8]` [Comments for Solarpunk Magazine] Submissions  
  <https://solarpunkmagazine.com/submissions/>
- `[ 27]` 🔓 [Edge (GamesRadar)] After avoiding game-key cards with Cyberpunk 2077, CD Projekt Red says The Witcher 3 Remastered's Switch 2 physical edition details will come "when the time is right"  
  <https://www.gamesradar.com/games/the-witcher/after-avoiding-game-key-cards-with-cyberpunk-2077-cd-projekt-red-says-the-witcher-3-remastereds-switch-2-physical-edition-details-will-come-when-the-time-is-right/>
- `[ 10]` [Comments for Solarpunk Magazine] Celebrating Five Years of Solarpunk Magazine&#39;s Journey  
  <https://solarpunkmagazine.com/solarpunk-magazine-year-5-issue-25/>
- `[ 17]` [Global News] FAN EXPO Canada returns to Toronto for 30th year  
  <https://globalnews.ca/news/12038497/fan-expo-canada-returns-to-toronto-for-30th-year/>
- `[ 18]` [Android Authority] Cyberpunk 2077 meets the Commodore 64 in this gloriously retro crossover  
  <https://www.androidauthority.com/commodore-64-cyberpunk-edition-3703517/>
- `[ 12]` [Reactor Magazine] Grant Morrison Wants More Sci-Fi in Lanterns: “Why Try to Make a Green Lantern Show on a Budget?”  
  <https://reactormag.com/grant-morrison-sci-fi-lanterns-hbo/>
- `[ 25]` 🔓 [Edge (GamesRadar)] Final Fantasy 7 Revelation Gamescom trailer gives us our first look at Ruby, Emerald, and Ultima Weapon  
  <https://www.gamesradar.com/games/final-fantasy/final-fantasy-7-revelation-gamescom-trailer-gives-us-our-first-look-at-ruby-emerald-and-ultima-weapon/>
- `[ 29]` 🔓 [Edge (GamesRadar)] Final Fantasy Resonance is getting the endgame content that Final Fantasy 16 could have done with  
  <https://www.gamesradar.com/games/final-fantasy/final-fantasy-resonance-is-getting-the-endgame-content-that-final-fantasy-16-could-have-done-with/>

### 🟡 🌿 Health & Wellness

- **Articles**: 85 (85 scored)
- **Score**: avg 52.4 | min 10 | max 76
- **Stale** (>48h): 54
- **Avg age**: 61.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ███                    4
  20–29   │ ███████               10
  30–39   │ ██                     3
  40–49   │ ██████                 9
  50–59   │ ████████████████████  26
  60–69   │ ██████████████████    24
  70–79   │ ██████                 9
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Scientific American | 6 | 7% |
| ScienceDaily | 6 | 7% |
| Nautilus | 5 | 6% |
| Business Insider | 4 | 5% |
| STAT News | 4 | 5% |
| ScienceAlert | 3 | 4% |
| Fast Company | 3 | 4% |
| Toms Guide | 3 | 4% |

**Low-score articles (≤30):**

- `[ 15]` [Harvard Health Blog] Health Information and Medical Information - Medical Conditions ...  
  <https://www.health.harvard.edu/topics>
- `[ 22]` [Kagi Small Web] showing up with breakfast  
  <https://ablerism.micro.blog/2026/08/29/showing-up-with-breakfast.html>
- `[ 28]` [TechCrunch] The Theragun Sense makes everyday recovery surprisingly easy  
  <https://techcrunch.com/2026/08/29/the-theragun-sense-makes-everyday-recovery-surprisingly-easy/>
- `[ 22]` [Business Insider] A gut health scientist and dietitian has a simple rule for making balanced, tasty smoothies  
  <https://www.businessinsider.com/gut-health-scientist-simple-rule-balanced-smoothie-sugar-026-8>
- `[ 15]` [Toms Guide] I turned my yellowed pillow bright white again using a $1 medicine cabinet staple  
  <https://www.tomsguide.com/mattresses/pillows-bedding/i-turned-my-yellowed-pillow-bright-white-again-using-a-usd1-medicine-cabinet-staple>
- `[ 27]` 🔓 [Edge (GamesRadar)] Mayday directors say the Top Gun-homaging action-comedy got Tom Cruise's permission to use footage from the '80s classic  
  <https://www.gamesradar.com/entertainment/action-movies/mayday-directors-say-the-top-gun-homaging-action-comedy-got-tom-cruises-permission-to-use-footage-from-the-80s-classic/>
- `[ 22]` [Atlas Obscura] Cape Bear Lighthouse and Marconi Station in Murray Harbour, Prince Edward Island  
  <https://www.atlasobscura.com/places/cape-bear-lighthouse-and-marconi-station>
- `[ 28]` [ZDNet] This Linux and Windows app makes managing all your documents easier  
  <https://www.zdnet.com/article/this-linux-and-windows-app-makes-managing-all-of-your-documents-easier/>
- `[ 29]` [STAT News] At a federal autism advisory committee meeting, members double down on long-debunked theories  
  <https://www.statnews.com/2026/08/28/health-news-federal-autism-adcomm-doubles-down-on-debunked-theory/?utm_campaign=rss>
- `[ 10]` [ScienceAlert] Scientists Put Three Weight-Loss Diets Head to Head. Only One Changed The Liver.  
  <https://www.sciencealert.com/uniquely-beneficial-effect-study-suggests-keto-diet-is-healthiest-for-weight-loss-heres-why>
- `[ 10]` [Nautilus] What’s the Secret to Bats’ Super Longevity?  
  <https://nautil.us/whats-the-secret-to-bats-super-longevity-1284461/>
- `[ 28]` 🔓 [Outside Online] Rachel Entrekin Is Pushing the Limits of Human Endurance. She Also Pets Every Dog She Sees.  
  <https://www.outsideonline.com/health/training-performance/rachel-entrekin-ultrarunner/>
- `[ 24]` [ScienceDaily] What you eat before age 2 may affect your health 70 years later  
  <https://www.sciencedaily.com/releases/2026/08/260824065522.htm>
- `[ 25]` [ScienceDaily] One asteroid strike may explain two mysteries of Mars’ moon Deimos  
  <https://www.sciencedaily.com/releases/2026/08/260824065516.htm>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (5)

- **[🌍 Climate & Energy]** `score 32` — More Fucked Today than Yesterday  
  Issue: `clickbait`  
  <https://kottke.org/26/08/0049525-more-fucked-today-than-ye>
- **[🏠 Homelab & DIY]** `score 17` — Kitchen Cabinet Essentials  
  Issue: `deals`  
  <https://www.popularwoodworking.com/article/kitchen-cabinet-essentials/>
- **[🌾 Homestead & Hobby Farm]** `score 18` — Business Bootcamp for New Farmers  
  Issue: `advice`  
  <https://www.smallfarmcanada.ca/headliners/registration-opens-for-business-bootcamp-for-new-farmers/>
- **[🥾 Outdoors & Recreation]** `score 20` — LISTEN: The 19-Year Search for Michelle Vanek, Part 1  
  Issue: `clickbait`  
  <https://www.outsideonline.com/outdoor-adventure/exploration-survival/michelle-vanek-podcast/>
- **[🥾 Outdoors & Recreation]** `score 23` — He Set Out for a Day Hike on Granite Peak, Montana's Highest Mountain. An 800-Foot Fall Killed Him.  
  Issue: `clickbait`  
  <https://www.outsideonline.com/outdoor-adventure/hiking-and-backpacking/hiker-death-granite-peak-montana/>

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 89 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 26 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏛️ Architecture & Design** has 30 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏠 Homelab & DIY** has 26 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🌾 Homestead & Hobby Farm** has a low average score (19.1) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🌾 Homestead & Hobby Farm** has 9 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 30 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏔️ Williams Lake Local** is dominated by **Williams Lake Tribune** (21 articles, 52%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **📰 General News** has 140 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🥾 Outdoors & Recreation** has a low average score (29.4) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🥾 Outdoors & Recreation** has 11 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🥾 Outdoors & Recreation** is dominated by **Outside Online** (9 articles, 53%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **🔬 Science** has 34 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (26.6) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🚀 Sci-Fi & Culture** has 11 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌿 Health & Wellness** has 54 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 5 article(s) should be removed (`clickbait` ×3, `deals` ×1, `advice` ×1) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 11 feeds · 676 articles · 2026-08-30 17:17 UTC_
