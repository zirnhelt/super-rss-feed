# Feed Scoring & Scrubbing Report

_Generated: 2026-11-14 18:54 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 11 |
| Total articles | 504 |
| Stale articles (>48h) | 399 |
| Scrub pass | ✅ ran |
| Flagged for removal | 1 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 88 | 🟡 47.6 | 18–68 | 68 | WIRED (8) |
| 🌍 Climate & Energy | 63 | 🟡 48.9 | 9–76 | 52 | CleanTechnica (7) |
| 🏛️ Architecture & Design | 30 | 🔴 43.4 | 33–57 | 25 | ArchDaily (16) |
| 🏠 Homelab & DIY | 45 | 🔴 39.7 | 15–60 | 35 | Hackaday (5) |
| 🌾 Homestead & Hobby Farm | 19 | 🔴 44.6 | 12–74 | 18 | RealAgriculture (6) |
| 🏔️ Williams Lake Local | 45 | 🟡 70.0 | 0–100 | 31 | Williams Lake Tribune (15) |
| 📰 General News | 104 | 🟡 61.3 | 21–87 | 77 | NYT Top Stories (10) |
| 🥾 Outdoors & Recreation | 8 | 🔴 41.2 | 22–60 | 6 | Outside Online (3) |
| 🔬 Science | 41 | 🟡 49.0 | 35–64 | 35 | Quanta Magazine (5) |
| 🚀 Sci-Fi & Culture | 6 | 🔴 26.0 | 15–45 | 5 | Reactor Magazine (3) |
| 🌿 Health & Wellness | 55 | 🔴 40.4 | 10–62 | 47 | ScienceDaily (6) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 88 (88 scored)
- **Score**: avg 47.6 | min 18 | max 68
- **Stale** (>48h): 68
- **Avg age**: 77.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        1
  20–29   │                        0
  30–39   │                        1
  40–49   │ ████████████████████  59
  50–59   │ ███████               23
  60–69   │ █                      4
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| WIRED | 8 | 9% |
| TechRadar | 8 | 9% |
| Fast Company | 5 | 6% |
| Tom's Hardware | 5 | 6% |
| The Atlantic | 4 | 5% |
| TechCrunch | 3 | 3% |
| Forbes Innovation | 3 | 3% |
| thehackernews.com | 3 | 3% |

**Low-score articles (≤30):**

- `[ 18]` [Reactor Magazine] A Fitting Conclusion: In the Hall of the Martian King by John Barnes  
  <https://reactormag.com/a-fitting-conclusion-in-the-hall-of-the-martian-king-by-john-barnes/>

### 🟡 🌍 Climate & Energy

- **Articles**: 63 (63 scored)
- **Score**: avg 48.9 | min 9 | max 76
- **Stale** (>48h): 52
- **Avg age**: 84.8h

**Score distribution:**
```
  0–9     │                        1
  10–19   │                        1
  20–29   │                        0
  30–39   │ ████                   7
  40–49   │ ████████████████████  30
  50–59   │ ██████████            15
  60–69   │ ████                   7
  70–79   │ █                      2
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| CleanTechnica | 7 | 11% |
| ABC News | 4 | 6% |
| Gizmodo | 4 | 6% |
| MIT Technology Review | 4 | 6% |
| The Tyee | 3 | 5% |
| Outside Online | 2 | 3% |
| durhamradionews.com | 2 | 3% |
| Scientific American | 2 | 3% |

**Low-score articles (≤30):**

- `[ 19]` [TechRadar] Google pushes ahead with plans for $17 billion Wyoming data center despite US midterms dashing support for AI across the US  
  <https://www.techradar.com/pro/google-pushes-ahead-with-plans-for-usd17-billion-wyoming-data-center-despite-us-midterms-dashing-support-for-ai-across-the-us>
- `[  9]` [MIT Technology Review] The Download: empty AI climate claims, and an Nvidia investigation  
  <https://www.technologyreview.com/2026/11/09/1148176/the-download-empty-ai-climate-claims-and-an-nvidia-investigation/>

### 🔴 🏛️ Architecture & Design

- **Articles**: 30 (30 scored)
- **Score**: avg 43.4 | min 33 | max 57
- **Stale** (>48h): 25
- **Avg age**: 82.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ ██████████             9
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
| ArchDaily | 16 | 53% ⚠️ |
| Dezeen | 5 | 17% |
| Architizer | 2 | 7% |
| Popular Mechanics | 1 | 3% |
| Small Wooden House Plans | Micro Cabin Plans | Garden Shed Plans | Cottage Blueprints | 1 | 3% |
| Canadian Architect | 1 | 3% |
| Adafruit Blog | 1 | 3% |
| Dwell | 1 | 3% |

### 🔴 🏠 Homelab & DIY

- **Articles**: 45 (45 scored)
- **Score**: avg 39.7 | min 15 | max 60
- **Stale** (>48h): 35
- **Avg age**: 75.3h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ███                    3
  20–29   │ ████                   4
  30–39   │ ███████████           11
  40–49   │ ████████████████████  20
  50–59   │ ██████                 6
  60–69   │ █                      1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hackaday | 5 | 11% |
| Bambu Lab Community Forum - Latest posts | 5 | 11% |
| Popular Woodworking | 4 | 9% |
| Adafruit Blog | 3 | 7% |
| TechRadar | 2 | 4% |
| How-To Geek | 2 | 4% |
| XDA Developers | 2 | 4% |
| 3D Printing Industry | 2 | 4% |

**Low-score articles (≤30):**

- `[ 22]` [Ben Yafai] Uses  
  <https://ben.yaf.ai/uses>
- `[ 22]` [9to5google.com] Google fixes Nest camera bug and expands Gemini controls  
  <https://9to5google.com/2026/11/11/google-home-update-nest-hub-gemini-cameras/>
- `[ 22]` [3dprinting.com] SINTX completes 3D-printing facility, targets implant availability in 2027  
  <https://3dprinting.com/news/sintx-completes-3d-printing-facility-buildout-for-sin-peek-platform-targets-initial-product-availability-in-2027/>
- `[ 15]` [Bambu Lab Blog] Bambu Lab to present the Bambu Circle programme and showcase H3C and R1 at Formnext 2026  
  <https://blog.bambulab.com/bambu-lab-to-present-the-bambu-circle-programme-and-showcase-h3c-and-r1-at-formnext-2026/>
- `[ 15]` [Wikipedia  - Recent changes [en]] Channel (programming)  
  <https://en.wikipedia.org/w/index.php?title=Channel_(programming)&diff=1384984315&oldid=1384951126>
- `[ 30]` [Engadget] How SCSKiller is trying to fix shader stuttering in PC games  
  <https://www.engadget.com/2307815/scskiller-fix-shader-stuttering-pc-games/>
- `[ 18]` [ifun.de] Amazon enables Alexa+ in the browser for German test users  
  <https://www.ifun.de/alexa-im-browser-amazon-schaltet-alexa-com-in-deutschland-frei-294610/>
- `[ 27]` 🔓 [Popular Woodworking] ShopNotes Podcast Episode 291 — I Mean… Okay.  
  <https://www.popularwoodworking.com/editors-blog/shopnotes-podcast-episode-291-i-mean-okay/>

### 🔴 🌾 Homestead & Hobby Farm

- **Articles**: 19 (19 scored)
- **Score**: avg 44.6 | min 12 | max 74
- **Stale** (>48h): 18
- **Avg age**: 95.3h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██████                 2
  20–29   │ ██████                 2
  30–39   │ ██████                 2
  40–49   │ ██████████             3
  50–59   │ ████████████████████   6
  60–69   │ ██████████             3
  70–79   │ ███                    1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| RealAgriculture | 6 | 32% |
| Hobby Farms | 3 | 16% |
| Small Farm Canada | 2 | 11% |
| tsln.com | 1 | 5% |
| Williams Lake Tribune | 1 | 5% |
| agrapress.it | 1 | 5% |
| MacRumors | 1 | 5% |
| agbz.ru | 1 | 5% |

**Low-score articles (≤30):**

- `[ 22]` [Hobby Farms] Turkey Eggs: Size, Taste, Nutrition and Uses  
  <https://www.hobbyfarms.com/turkey-eggs/>
- `[ 20]` 🔓 [Williams Lake Tribune] QUIZ: Considering the effects of war  
  <https://wltribune.com/2026/11/11/quiz-considering-the-effects-of-war/>
- `[ 12]` [Hobby Farms] Turkey Recipes: 3 Classic Favorites Anytime  
  <https://www.hobbyfarms.com/three-traditional-turkey-recipes-home/>
- `[ 14]` [MacRumors] Next iPad Air Likely to Have These 10 New Features  
  <https://www.macrumors.com/2026/11/10/next-ipad-air-10-likely-new-features/>

### 🟡 🏔️ Williams Lake Local

- **Articles**: 45 (45 scored)
- **Score**: avg 70.0 | min 0 | max 100
- **Stale** (>48h): 31
- **Avg age**: 76.1h
- **Local-flagged**: 45 (1 with score=0 via local override)

**Score distribution:**
```
  0–9     │ █                      1
  10–19   │ █████                  3
  20–29   │ ███                    2
  30–39   │                        0
  40–49   │ █                      1
  50–59   │ ███████                4
  60–69   │ ██████████████         8
  70–79   │ █████████              5
  80–89   │ ████████████████████  11
  90–100  │ ██████████████████    10
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 15 | 33% |
| My Cariboo Now | 10 | 22% |
| 100 Mile Free Press | 7 | 16% |
| Cariboo Signals Reviews | 6 | 13% |
| Quesnel Cariboo Observer | 4 | 9% |
| Canadian Forest Industries | 1 | 2% |
| Pique Newsmagazine | 1 | 2% |
| Tŝilhqot’in National Government | 1 | 2% |

**Low-score articles (≤30):**

- `[  0]` [Cariboo Signals Reviews] Episode Review — Cariboo Local Affairs, November 14, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-14.html>
- `[ 16]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, November 13, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-13.html>
- `[ 27]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, November 12, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-12.html>
- `[ 19]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, November 11, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-11.html>
- `[ 21]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, November 10, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-10.html>
- `[ 11]` [Cariboo Signals Reviews] Episode Review — Cariboo Signals, November 9, 2026  
  <https://zirnhelt.github.io/curated-podcast-generator/podcasts/reviews/episode-review-2026-11-09.html>

### 🟡 📰 General News

- **Articles**: 104 (103 scored)
- **Score**: avg 61.3 | min 21 | max 87
- **Stale** (>48h): 77
- **Avg age**: 76.1h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ █                      5
  30–39   │ █                      4
  40–49   │ █                      5
  50–59   │ ████                  11
  60–69   │ ████████████████████  55
  70–79   │ ██████                18
  80–89   │ █                      5
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| NYT Top Stories | 10 | 10% |
| NYT Business | 9 | 9% |
| The Atlantic | 6 | 6% |
| The Tyee | 6 | 6% |
| Scientific American | 5 | 5% |
| The Guardian Global Development | 5 | 5% |
| Al Jazeera English | 5 | 5% |
| WIRED | 5 | 5% |

**Low-score articles (≤30):**

- `[ 22]` [theguardian.com] UK and EU seek Brexit reset deal before November 20 summit  
  <https://www.theguardian.com/politics/2026/nov/12/win-win-deal-with-eu-could-be-done-andy-burmham-says>
- `[ 21]` [cnbc.com] France summons Iran envoy and seeks EU sanctions over supermarket hack  
  <https://www.cnbc.com/2026/11/10/iran-fridge-cyberattacks-france.html>
- `[ 28]` 🔓 [NYT Business] Why U.S. Business Deals Are Unlikely to Get Putin to Give Any Ground  
  <https://www.nytimes.com/2026/11/10/world/europe/putin-trump-abu-dhabi-talks.html>
- `[ 28]` [orf.at] Drone strikes kill two power-plant workers near Ukraine’s occupied nuclear site  
  <https://orf.at/stories/3447731/>
- `[ 26]` 🔓 [NYT Business] How Indispensable Is Jensen Huang?  
  <https://www.nytimes.com/2026/11/09/business/dealbook/nvidia-huang-spy.html>

### 🔴 🥾 Outdoors & Recreation

- **Articles**: 8 (8 scored)
- **Score**: avg 41.2 | min 22 | max 60
- **Stale** (>48h): 6
- **Avg age**: 73.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ██████                 1
  30–39   │ ████████████████████   3
  40–49   │ ██████                 1
  50–59   │ █████████████          2
  60–69   │ ██████                 1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Outside Online | 3 | 38% |
| Wildfire Today | 1 | 12% |
| Trip Reports | 1 | 12% |
| CleanTechnica | 1 | 12% |
| Live for the Outdoors (Country Walking) | 1 | 12% |
| The Road Goes Ever On | 1 | 12% |

**Low-score articles (≤30):**

- `[ 22]` [Trip Reports] Backpacking | Backcountry Post  
  <https://backcountrypost.com/forums/backpacking.20/>

### 🟡 🔬 Science

- **Articles**: 41 (41 scored)
- **Score**: avg 49.0 | min 35 | max 64
- **Stale** (>48h): 35
- **Avg age**: 80.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ ██                     3
  40–49   │ ████████████████████  21
  50–59   │ █████████████         14
  60–69   │ ██                     3
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Quanta Magazine | 5 | 12% |
| ScienceDaily | 4 | 10% |
| Scientific American | 4 | 10% |
| ScienceAlert | 3 | 7% |
| Nautilus | 2 | 5% |
| WIRED | 2 | 5% |
| science.nasa.gov | 2 | 5% |
| 3D Printing Industry | 1 | 2% |

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 6 (6 scored)
- **Score**: avg 26.0 | min 15 | max 45
- **Stale** (>48h): 5
- **Avg age**: 91.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █████                  1
  20–29   │ ████████████████████   4
  30–39   │                        0
  40–49   │ █████                  1
  50–59   │                        0
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Reactor Magazine | 3 | 50% |
| Columbia Journalism Review | 1 | 17% |
| Forbes Innovation | 1 | 17% |
| Mike Brooks | 1 | 17% |

**Low-score articles (≤30):**

- `[ 22]` [Columbia Journalism Review] Picture Perfect  
  <https://www.cjr.org/laurels-and-darts/appalachian-williford-midterm-elections-boone-north-carolina-free-press-reingold-weiss-el-sayed-islamophobia-michigan-get-huge-clavicular-looksmaxxing.php>
- `[ 20]` [Reactor Magazine] M. John Harrison’s The End of Everything Wins the Booker Prize  
  <https://reactormag.com/m-john-harrisons-the-end-of-everything-booker-prize/>
- `[ 28]` [Reactor Magazine] A Fitting Conclusion: In the Hall of the Martian King by John Barnes  
  <https://reactormag.com/a-fitting-conclusion-in-the-hall-of-the-martian-king-by-john-barnes/>
- `[ 26]` [Mike Brooks] Quatermass and the Pit (1967) – Review  
  <https://manapop.com/film/quatermass-and-the-pit-1967-review/>
- `[ 15]` [Reactor Magazine] Five Out-of-Print Collections From the Cutting Edge of Disco-Era Science Fiction  
  <https://reactormag.com/five-out-of-print-collections-from-the-cutting-edge-of-disco-era-science-fiction/>

### 🔴 🌿 Health & Wellness

- **Articles**: 55 (55 scored)
- **Score**: avg 40.4 | min 10 | max 62
- **Stale** (>48h): 47
- **Avg age**: 81.9h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ████                   6
  20–29   │ ██                     3
  30–39   │ ███████               10
  40–49   │ ████████████████████  27
  50–59   │ █████                  7
  60–69   │ █                      2
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 6 | 11% |
| Being Patient | 3 | 5% |
| Business Insider | 3 | 5% |
| Outside Online | 3 | 5% |
| STAT News | 3 | 5% |
| NYT Well | 2 | 4% |
| NYT Top Stories | 2 | 4% |
| Scientific American | 2 | 4% |

**Low-score articles (≤30):**

- `[ 10]` 🔓 [Williams Lake Tribune] Alberta First Nation sues B.C. over Site C dam impacts  
  <https://wltribune.com/2026/11/10/alberta-first-nation-sues-b-c-over-site-c-dam-impacts/>
- `[ 17]` 🔓 [Outside Online] Is Your Sodium Intake Impacting Your Hiking Performance? A Dietitian Explains Why It Matters.  
  <https://www.outsideonline.com/health/nutrition/sodium-intake-impacts-hiking-performance/>
- `[ 17]` [scitechdaily.com] Stanford researchers use brain scans to flag Alzheimer’s risk years earlier  
  <https://scitechdaily.com/hidden-brain-signals-could-predict-alzheimers-years-before-symptoms-appear/>
- `[ 27]` [newspaceeconomy.ca] Researchers test AI systems for satellite servicing, imaging and astronomy  
  <https://newspaceeconomy.ca/2026/11/09/are-we-designing-earth-observation-satellites-backwards-in-the-age-of-artificial-intelligence/>
- `[ 22]` [Business Insider] Elon Musk predicts a future of abundance where, if you 'wish for a castle,' AI will build it for you  
  <https://www.businessinsider.com/elon-musk-ai-abundance-castle-robotics-productivity-universal-high-income-2026-11>
- `[ 10]` [ScienceAlert] It's Not Just You – Pandemic Stress Really Was Linked to Faster Epigenetic Aging, But Only in One Generation  
  <https://www.sciencealert.com/pandemic-stress-linked-to-faster-epigenetic-aging-but-only-in-one-generation>
- `[ 10]` [Tom's Hardware] Wearable sleep trackers are using your brainwaves to train AI models without explicit user consent  
  <https://www.tomshardware.com/peripherals/wearable-tech/wearable-sleep-trackers-are-using-your-brainwaves-to-train-ai-models-without-explicit-user-consent-tens-of-millions-of-hours-of-eeg-data-harvested>
- `[ 20]` [Android Authority] Digital Wellbeing v1.50 beta gives us our first look at Weekly Insights and Gemini integration  
  <https://www.androidauthority.com/google-digital-wellbeing-weekly-insights-apk-teardown-3732858/>
- `[ 11]` 🔓 [Scientific American] Bursts of ‘pink noise’ during sleep could help your brain clean itself  
  <https://www.scientificamerican.com/article/bursts-of-pink-noise-during-sleep-could-help-your-brain-clean-itself/>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (1)

- **[🏠 Homelab & DIY]** `score 15` — Channel (programming)  
  Issue: `clickbait`  
  <https://en.wikipedia.org/w/index.php?title=Channel_(programming)&diff=1384984315&oldid=1384951126>

### ⚠️ Borderline but Acceptable (2)

- **[🏠 Homelab & DIY]** `score 22` — SINTX completes 3D-printing facility, targets implant availability in 2027  
  Note: `clickbait`
- **[🏠 Homelab & DIY]** `score 40` — Sunlu FilaDC i10 dryer cabinet, and other dry filament topics  
  Note: `clickbait`

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 68 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 52 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏛️ Architecture & Design** has 25 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏛️ Architecture & Design** is dominated by **ArchDaily** (16 articles, 53%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **🏠 Homelab & DIY** has 35 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌾 Homestead & Hobby Farm** has 18 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 31 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **📰 General News** has 77 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🥾 Outdoors & Recreation** has 6 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 35 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (26.0) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🌿 Health & Wellness** has 47 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 1 article(s) should be removed (`clickbait` ×1) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 11 feeds · 504 articles · 2026-11-14 18:54 UTC_
