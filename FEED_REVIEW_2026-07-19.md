# Feed Scoring & Scrubbing Report

_Generated: 2026-07-19 14:31 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 8 |
| Total articles | 366 |
| Stale articles (>48h) | 250 |
| Scrub pass | ✅ ran |
| Flagged for removal | 13 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 65 | 🔴 39.0 | 15–54 | 43 | TechRadar (13) |
| 🌍 Climate & Energy | 35 | 🟡 46.1 | 11–69 | 28 | Pique Newsmagazine (4) |
| 🏠 Homelab & DIY | 12 | 🔴 26.7 | 2–61 | 8 | Hackaday (3) |
| 🏔️ Williams Lake Local | 40 | 🟢 82.2 | 53–95 | 28 | Williams Lake Tribune (21) |
| 📰 General News | 123 | 🔴 42.8 | 25–69 | 78 | NYT Top Stories (11) |
| 🔬 Science | 38 | 🟡 51.6 | 32–59 | 27 | ScienceDaily (14) |
| 🚀 Sci-Fi & Culture | 6 | 🔴 12.7 | 2–39 | 3 | Reactor Magazine (2) |
| 🌿 Health & Wellness | 47 | 🔴 40.1 | 13–55 | 35 | STAT News (17) |

---

## Per-Feed Detail

### 🔴 🤖 AI/ML & Tech

- **Articles**: 65 (65 scored)
- **Score**: avg 39.0 | min 15 | max 54
- **Stale** (>48h): 43
- **Avg age**: 69.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██                     4
  20–29   │ █                      3
  30–39   │ ██████████████        23
  40–49   │ ████████████████████  32
  50–59   │ █                      3
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| TechRadar | 13 | 20% |
| Business Insider | 10 | 15% |
| TechCrunch | 6 | 9% |
| Engadget | 5 | 8% |
| WIRED | 3 | 5% |
| NYT Business | 3 | 5% |
| CNET | 3 | 5% |
| Quartz | 2 | 3% |

**Low-score articles (≤30):**

- `[ 26]` [MacRumors] Report: Apple Sends Legal Letters to Dozens of OpenAI Employees  
  <https://www.macrumors.com/2026/07/17/apple-sends-legal-letters-openai/>
- `[ 17]` [TechRadar] 'You're giving ballistic ⁠missiles to individuals with Mythos': JPMorgan CEO Jamie Dimon says Anthropic's AI model poses some serious risks  
  <https://www.techradar.com/pro/youre-giving-ballistic-missiles-to-individuals-with-mythos-jpmorgan-ceo-jamie-dimon-says-anthropics-ai-model-poses-some-serious-risks>
- `[ 22]` [Business Insider] Former Intel CEO says the chipmaker went off the rails ‘when it started to be run by business people’  
  <https://www.businessinsider.com/intel-decline-reasons-pat-gelsinger-former-ceo-2026-7>
- `[ 17]` [Engadget] OpenAI launches a physical keypad for controlling agents  
  <https://www.engadget.com/2215952/openai-launches-a-physical-keypad-for-controlling-agents/>
- `[ 15]` [TechRadar] RayNeo X3 Pro review: These AI+AR Smart Glasses are technically impressive, but far from easy to use  
  <https://www.techradar.com/pro/rayneo-x3-pro-ai-ar-smart-glasses-review>
- `[ 17]` [Hackaday] UDP Broadcasting and the Joys of IPv4 Subnetting  
  <https://hackaday.com/2026/07/14/udp-broadcasting-and-the-joys-of-ipv4-subnetting/>
- `[ 25]` [Android Authority] Chrome on Android is getting a navigation bar redesign to make room for Gemini  
  <https://www.androidauthority.com/chrome-android-navigation-bar-gemini-3687175/>

### 🟡 🌍 Climate & Energy

- **Articles**: 35 (35 scored)
- **Score**: avg 46.1 | min 11 | max 69
- **Stale** (>48h): 28
- **Avg age**: 80.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █████                  3
  20–29   │ █                      1
  30–39   │ █████                  3
  40–49   │ ████████████████████  12
  50–59   │ ██████████████████    11
  60–69   │ ████████               5
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Pique Newsmagazine | 4 | 11% |
| NYT Top Stories | 4 | 11% |
| Engadget | 4 | 11% |
| InsideEVs | 4 | 11% |
| Al Jazeera English | 3 | 9% |
| The Maple | 2 | 6% |
| Resilience.org | 2 | 6% |
| NYT Business | 1 | 3% |

**Low-score articles (≤30):**

- `[ 17]` [The Guardian Global Development] ‘I’m sorry but I’m unable to speak’: hero of India’s Cockroach party weakens on 19th day of hunger strike  
  <https://www.theguardian.com/global-development/2026/jul/17/indian-protester-hunger-strike-modi-government-sonam-wangchuk>
- `[ 20]` [Kagi Small Web] Record wildfires in Europe  
  <https://stallman.org/archives/2026-may-aug.html#16_July_2026_(Record_wildfires_in_Europe)>
- `[ 13]` [The Maple] Mark Carney Appoints Former Oil Executive As U.S. Diplomat  
  <https://www.readthemaple.com/mark-carney-appoints-former-oil-executive-as-u-s-diplomat/>
- `[ 11]` [IndigiNews] As disasters worsen, Indigenous peoples threatened by a ‘crisis communication gap’  
  <https://indiginews.com/news/crisis-communication-gap-threatens-indigenous-peoples/>

### 🔴 🏠 Homelab & DIY

- **Articles**: 12 (12 scored)
- **Score**: avg 26.7 | min 2 | max 61
- **Stale** (>48h): 8
- **Avg age**: 78.3h

**Score distribution:**
```
  0–9     │ ████████████████████   6
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │ █████████████          4
  50–59   │ ███                    1
  60–69   │ ███                    1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hackaday | 3 | 25% |
| Android Authority | 2 | 17% |
| How-To Geek | 1 | 8% |
| CNET | 1 | 8% |
| MakeUseOf | 1 | 8% |
| Outside Online | 1 | 8% |
| Tom's Hardware | 1 | 8% |
| TechRadar | 1 | 8% |

**Low-score articles (≤30):**

- `[  5]` [Hackaday] Flex Filament Stuck To Your Build Platform? Reach For The Isopropanol  
  <https://hackaday.com/2026/07/17/flex-filament-stuck-to-your-build-platform-reach-for-the-isopropanol/>
- `[  3]` [MakeUseOf] Plex, Jellyfin, and Kodi all fix the same TV problem, but I'd only recommend one  
  <https://www.makeuseof.com/plex-jellyfin-kodi-all-fix-same-tv-problem-but-id-only-recommend-one/>
- `[  5]` [Hackaday] Cut And Fold Your 3D Printer’s Next Cover  
  <https://hackaday.com/2026/07/15/cut-and-fold-your-3d-printers-next-cover/>
- `[  6]` 🔓 [WIRED] Plex Keeps Getting Worse. Is Jellyfin a Decent Replacement?  
  <https://www.wired.com/story/plex-keeps-getting-worse-is-jellyfin-a-decent-replacement/>
- `[  6]` [Android Authority] Looking for the best way to run Home Assistant? Our readers have their say  
  <https://www.androidauthority.com/platform-home-assistant-poll-results-3687211/>
- `[  2]` [Android Authority] How AtomForm is making 3D printing accessible to everyone  
  <https://www.androidauthority.com/atomform-jagger-shang-interview-3685768/>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 40 (40 scored)
- **Score**: avg 82.2 | min 53 | max 95
- **Stale** (>48h): 28
- **Avg age**: 64.7h
- **Local-flagged**: 40

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │ █                      1
  60–69   │ ██                     2
  70–79   │ █████████████         11
  80–89   │ ████████████████████  16
  90–100  │ ████████████          10
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 21 | 52% ⚠️ |
| My Cariboo Now | 11 | 28% |
| Quesnel Cariboo Observer | 4 | 10% |
| 100 Mile Free Press | 4 | 10% |

### 🔴 📰 General News

- **Articles**: 123 (123 scored)
- **Score**: avg 42.8 | min 25 | max 69
- **Stale** (>48h): 78
- **Avg age**: 67.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ███                    8
  30–39   │ ████████████████████  44
  40–49   │ ██████████████████    40
  50–59   │ █████████             20
  60–69   │ █████                 11
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| NYT Top Stories | 11 | 9% |
| NYT Business | 10 | 8% |
| The Northern Miner | 8 | 7% |
| Global News | 7 | 6% |
| TechRadar | 7 | 6% |
| Western Producer | 6 | 5% |
| Pique Newsmagazine | 6 | 5% |
| APTN News | 6 | 5% |

**Low-score articles (≤30):**

- `[ 28]` [MacRumors] Apple and DOJ Hold Early Settlement Talks in iPhone Antitrust Case  
  <https://www.macrumors.com/2026/07/17/apple-doj-antitrust-settlement/>
- `[ 25]` [Al Jazeera English] A giant cake for Venezuelan quake child survivors as death toll passes 5000  
  <https://www.aljazeera.com/video/newsfeed/2026/7/19/a-giant-cake-for-venezuelan-quake-child-survivors-as-death-toll-passes-5000?traffic_source=rss>
- `[ 28]` [Global News] Amber Alert issued for missing 11-year-old vulnerable child in Calgary  
  <https://globalnews.ca/news/11971232/calgary-police-cctv-image-search-missing-11-year-old/>
- `[ 30]` [Global News] Doug Ford visits Thunder Bay as northern Ontario fires force evacuations  
  <https://globalnews.ca/news/11971117/doug-ford-thunder-bay-wildfires-evacuees/>
- `[ 30]` [TechRadar] Ukraine reveals secret strike squadron of civilian planes transformed into deadly reusable drone bombers that can drop 100Kg bombs 1200 miles deep inside Russia  
  <https://www.techradar.com/pro/ukraine-just-revealed-a-secret-strike-squadron-of-civilian-planes-transformed-into-deadly-reusable-drone-bombers-that-can-drop-100kg-bombs-1200-miles-deep-inside-russia>
- `[ 28]` [Noahpinion] America's political economy is pretty bleak right now  
  <https://www.noahpinion.blog/p/americas-political-economy-is-pretty>
- `[ 28]` [APTN News] APTN Nouvelles nationales – 17 juillet 2026  
  <https://www.aptnnews.ca/national-news/aptn-nouvelles-nationales-17-juillet-2026/>
- `[ 27]` [Atlas Obscura] Grace Episcopal Church of City Island in Bronx, New York  
  <https://www.atlasobscura.com/places/grace-episcopal-church-of-city-island>
- `[ 26]` 🔓 [NYT Business] Pentagon’s Escort Policy for Journalists Is Temporarily Restored  
  <https://www.nytimes.com/2026/07/17/business/media/pentagon-reporters-nytimes.html>
- `[ 27]` [Boing Boing] Explore a snapshot of a massive million-by-million block Minecraft server  
  <https://boingboing.net/2026/07/17/explore-a-snapshot-of-a-massive-million-by-million-block-minecraft-server.html>

### 🟡 🔬 Science

- **Articles**: 38 (38 scored)
- **Score**: avg 51.6 | min 32 | max 59
- **Stale** (>48h): 27
- **Avg age**: 73.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ ██                     3
  40–49   │ ███                    5
  50–59   │ ████████████████████  30
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 14 | 37% |
| ScienceAlert | 10 | 26% |
| STAT News | 2 | 5% |
| Nautilus | 2 | 5% |
| New Atlas | 1 | 3% |
| CNET | 1 | 3% |
| Boing Boing | 1 | 3% |
| Quartz | 1 | 3% |

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 6 (6 scored)
- **Score**: avg 12.7 | min 2 | max 39
- **Stale** (>48h): 3
- **Avg age**: 59.6h

**Score distribution:**
```
  0–9     │ ████████████████████   3
  10–19   │ █████████████          2
  20–29   │                        0
  30–39   │ ██████                 1
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
| Reactor Magazine | 2 | 33% |
| New Atlas | 1 | 17% |
| Cool Tools | 1 | 17% |
| Noahpinion | 1 | 17% |
| Toms Guide | 1 | 17% |

**Low-score articles (≤30):**

- `[  5]` [New Atlas] 'World's 1st mass-produced humanoid robot' motors to market in China  
  <https://newatlas.com/robotics/u1-worlds-first-mass-produced-humanoid-robot/>
- `[  8]` [Reactor Magazine] What to Watch and Read This Weekend: The Air Is Smoke, the Lettuce Is Bad, but the Vampire Is Lestat  
  <https://reactormag.com/what-to-watch-read-this-weekend-july-17-2026/>
- `[  2]` [Noahpinion] Book Review: "Power and Progress"  
  <https://www.noahpinion.blog/p/book-review-power-and-progress-874>
- `[ 11]` [Toms Guide] Every Christopher Nolan movie, ranked from worst to best  
  <https://www.tomsguide.com/entertainment/movies/every-christopher-nolan-movie-ranked-from-worst-to-best>
- `[ 11]` [Reactor Magazine] Christopher Nolan Says The Odyssey Addresses a Fantasy Movie Gap “That Hadn’t Been Filled”  
  <https://reactormag.com/christopher-nolan-the-odyssey-fantasy-gap/>

### 🔴 🌿 Health & Wellness

- **Articles**: 47 (47 scored)
- **Score**: avg 40.1 | min 13 | max 55
- **Stale** (>48h): 35
- **Avg age**: 77.5h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ███                    3
  20–29   │ ██                     2
  30–39   │ ████████████████████  16
  40–49   │ █████████████████     14
  50–59   │ ███████████████       12
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| STAT News | 17 | 36% |
| ScienceDaily | 7 | 15% |
| ScienceAlert | 4 | 9% |
| Quartz | 4 | 9% |
| New Atlas | 2 | 4% |
| NYT Well | 2 | 4% |
| Global News | 2 | 4% |
| NPR Health News | 2 | 4% |

**Low-score articles (≤30):**

- `[ 26]` [Engadget] Don't lose sleep over reports of 260 Starlink satellites deorbiting  
  <https://www.engadget.com/2212810/spacex-starlink-satellites-deorbit-reports/>
- `[ 28]` [STAT News] Pete Hegseth’s announcement of annual testosterone screenings for service members divides medical experts  
  <https://www.statnews.com/2026/07/16/hegseth-testosterone-testing-proposal-reactions-range-promising-crazy/?utm_campaign=rss>
- `[ 30]` [STAT News] STAT+: Medicare wants to shake up how it pays for clinical AI  
  <https://www.statnews.com/2026/07/16/medicare-shake-clinical-ai-rpm-payments-health-tech/?utm_campaign=rss>
- `[ 13]` [ScienceDaily] This drug could help millions keep their kidneys working longer  
  <https://www.sciencedaily.com/releases/2026/07/260712011753.htm>
- `[ 14]` [The Guardian Global Development] Uganda calls for travel restrictions to be lifted after last Ebola patient discharged  
  <https://www.theguardian.com/global-development/2026/jul/16/uganda-travel-restrictions-last-ebola-patient-discharged>
- `[ 15]` 🔓 [NYT Business] Leonard Abramson, Health Care Innovator and Philanthropist, Dies at 93  
  <https://www.nytimes.com/2026/07/14/health/leonard-abramson-dead.html>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (13)

- **[🤖 AI/ML & Tech]** `score 31` — Dave Eggers told OpenAI staff that ChatGPT was 'silencing an entire generation'  
  Issue: `clickbait`  
  <https://www.theverge.com/ai-artificial-intelligence/967630/dave-eggers-openai-chatgpt-silencing-an-entire-generation>
- **[🤖 AI/ML & Tech]** `score 26` — Report: Apple Sends Legal Letters to Dozens of OpenAI Employees  
  Issue: `clickbait`  
  <https://www.macrumors.com/2026/07/17/apple-sends-legal-letters-openai/>
- **[🤖 AI/ML & Tech]** `score 17` — 'You're giving ballistic missiles to individuals with Mythos': JPMorgan CEO Jamie Dimon says Anthropic's AI model poses some serious risks  
  Issue: `clickbait`  
  <https://www.techradar.com/pro/youre-giving-ballistic-missiles-to-individuals-with-mythos-jpmorgan-ceo-jamie-dimon-says-anthropics-ai-model-poses-some-serious-risks>
- **[🤖 AI/ML & Tech]** `score 38` — When LLM becomes equivalent to Bitcoin mining, the industry is unavoidably migrating t...  
  Issue: `clickbait`  
  <https://agora.echelon.pl/objects/627b1d7b-804d-488b-9b1a-ba74d50fabed>
- **[🤖 AI/ML & Tech]** `score 38` — xAI sued a Grok user for allegedly generating deepfakes of child sexual abuse  
  Issue: `clickbait`  
  <https://qz.com/xai-sues-grok-user-child-sexual-abuse-deepfakes-071626>
- **[🤖 AI/ML & Tech]** `score 22` — Former Intel CEO says the chipmaker went off the rails 'when it started to be run by business people'  
  Issue: `clickbait`  
  <https://www.businessinsider.com/intel-decline-reasons-pat-gelsinger-former-ceo-2026-7>
- **[🤖 AI/ML & Tech]** `score 15` — RayNeo X3 Pro review: These AI+AR Smart Glasses are technically impressive, but far from easy to use  
  Issue: `clickbait`  
  <https://www.techradar.com/pro/rayneo-x3-pro-ai-ar-smart-glasses-review>
- **[🌍 Climate & Energy]** `score 17` — 'I'm sorry but I'm unable to speak': hero of India's Cockroach party weakens on 19th day of hunger strike  
  Issue: `clickbait`  
  <https://www.theguardian.com/global-development/2026/jul/17/indian-protester-hunger-strike-modi-government-sonam-wangchuk>
- **[📰 General News]** `score 31` — 24 years later, this Denzel crime thriller movie is still a scathing indictment of American healthcare  
  Issue: `clickbait`  
  <https://www.tomsguide.com/entertainment/movies/24-years-later-this-denzel-crime-thriller-movie-is-still-a-scathing-indictment-of-american-healthcare>
- **[📰 General News]** `score 31` — The next prenup provision: What happens if your spouse cheats on you with AI?  
  Issue: `clickbait`  
  <https://www.businessinsider.com/prenups-ai-infidelity-cheating-chatbot-companions-virtual-relationships-2026-7>
- **[📰 General News]** `score 35` — Penshurst Medieval Dole Table in Penshurst, England  
  Issue: `clickbait`  
  <https://www.atlasobscura.com/places/penshurst-medieval-dole-table>
- **[📰 General News]** `score 27` — Grace Episcopal Church of City Island in Bronx, New York  
  Issue: `clickbait`  
  <https://www.atlasobscura.com/places/grace-episcopal-church-of-city-island>
- **[📰 General News]** `score 27` — Explore a snapshot of a massive million-by-million block Minecraft server  
  Issue: `clickbait`  
  <https://boingboing.net/2026/07/17/explore-a-snapshot-of-a-massive-million-by-million-block-minecraft-server.html>

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 43 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 28 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🏠 Homelab & DIY** has a low average score (26.7) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🏠 Homelab & DIY** has 8 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 28 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏔️ Williams Lake Local** is dominated by **Williams Lake Tribune** (21 articles, 52%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **📰 General News** has 78 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 27 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (12.7) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🌿 Health & Wellness** has 35 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 13 article(s) should be removed (`clickbait` ×13) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 8 feeds · 366 articles · 2026-07-19 14:31 UTC_
