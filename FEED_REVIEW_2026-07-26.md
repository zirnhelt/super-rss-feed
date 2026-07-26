# Feed Scoring & Scrubbing Report

_Generated: 2026-07-26 20:24 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 8 |
| Total articles | 394 |
| Stale articles (>48h) | 249 |
| Scrub pass | ✅ ran |
| Flagged for removal | 12 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 71 | 🔴 43.2 | 22–66 | 44 | Business Insider (15) |
| 🌍 Climate & Energy | 23 | 🟡 45.3 | 22–60 | 15 | InsideEVs (7) |
| 🏠 Homelab & DIY | 14 | 🔴 44.3 | 8–59 | 7 | XDA Developers (3) |
| 🏔️ Williams Lake Local | 50 | 🟢 82.6 | 49–94 | 36 | Williams Lake Tribune (31) |
| 📰 General News | 144 | 🟡 49.0 | 29–99 | 87 | NYT Top Stories (13) |
| 🔬 Science | 37 | 🟡 47.9 | 29–60 | 24 | ScienceDaily (14) |
| 🚀 Sci-Fi & Culture | 8 | 🔴 19.5 | 0–46 | 5 | MakeUseOf (2) |
| 🌿 Health & Wellness | 47 | 🔴 41.0 | 13–58 | 31 | STAT News (9) |

---

## Per-Feed Detail

### 🔴 🤖 AI/ML & Tech

- **Articles**: 71 (71 scored)
- **Score**: avg 43.2 | min 22 | max 66
- **Stale** (>48h): 44
- **Avg age**: 61.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ █                      3
  30–39   │ █████████             18
  40–49   │ ████████████████████  40
  50–59   │ ███                    7
  60–69   │ █                      3
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Business Insider | 15 | 21% |
| TechRadar | 14 | 20% |
| TechCrunch | 8 | 11% |
| Tom's Hardware | 5 | 7% |
| Engadget | 4 | 6% |
| Toms Guide | 3 | 4% |
| Kagi Small Web | 3 | 4% |
| Boing Boing | 3 | 4% |

**Low-score articles (≤30):**

- `[ 22]` [Toms Guide] These 7 Gemini prompts made me much more productive in Google Workspace — and they'll do the same for you  
  <https://www.tomsguide.com/ai/these-7-gemini-prompts-made-me-much-more-productive-in-google-workspace-and-theyll-do-the-same-for-you>
- `[ 22]` [Toms Guide] Prime Video's upcoming AI makeover could completely change how you decide what to watch next  
  <https://www.tomsguide.com/entertainment/prime-video/prime-videos-upcoming-ai-makeover-could-completely-change-how-you-decide-what-to-watch-next>
- `[ 24]` [Toms Guide] New to ChatGPT Work? These 7 prompts turn it into a personal assistant  
  <https://www.tomsguide.com/ai/chatgpt/new-to-chatgpt-work-these-7-prompts-turn-it-into-a-personal-assistant>

### 🟡 🌍 Climate & Energy

- **Articles**: 23 (23 scored)
- **Score**: avg 45.3 | min 22 | max 60
- **Stale** (>48h): 15
- **Avg age**: 61.1h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ███                    2
  30–39   │ █                      1
  40–49   │ ████████████████████  13
  50–59   │ █████████              6
  60–69   │ █                      1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| InsideEVs | 7 | 30% |
| WIRED | 4 | 17% |
| Al Jazeera English | 3 | 13% |
| Business Insider | 1 | 4% |
| NYT Top Stories | 1 | 4% |
| Williams Lake Tribune | 1 | 4% |
| TechRadar | 1 | 4% |
| Engadget | 1 | 4% |

**Low-score articles (≤30):**

- `[ 23]` 🔓 [Williams Lake Tribune] B.C. allowing Tilbury gas terminal expansion to circumvent Utilities Commission  
  <https://wltribune.com/2026/07/24/b-c-allowing-tilbury-gas-terminal-expansion-to-circumvent-utilities-commission/>
- `[ 22]` [InsideEVs] Subaru's Biggest EV Yet Just Got Delayed  
  <https://insideevs.com/news/802574/2027-subaru-getaway-ev-delay/>

### 🔴 🏠 Homelab & DIY

- **Articles**: 14 (14 scored)
- **Score**: avg 44.3 | min 8 | max 59
- **Stale** (>48h): 7
- **Avg age**: 53.7h

**Score distribution:**
```
  0–9     │ ████                   1
  10–19   │                        0
  20–29   │                        0
  30–39   │ ████████████           3
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
| XDA Developers | 3 | 21% |
| How-To Geek | 2 | 14% |
| Tom's Hardware | 2 | 14% |
| Hackaday | 1 | 7% |
| Kagi Small Web | 1 | 7% |
| Android Authority | 1 | 7% |
| MakeUseOf | 1 | 7% |
| Boing Boing | 1 | 7% |

**Low-score articles (≤30):**

- `[  8]` [MacRumors] Apple Raises iCloud+ Prices in 8 Countries  
  <https://www.macrumors.com/2026/07/17/apple-icloud-plus-price-increase/>
- `[ 30]` [New Atlas] Extra-wide tiny house puts a terrace up top and sleeps five inside  
  <https://newatlas.com/tiny-houses/white-pine-backcountry-tiny-homes/>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 50 (50 scored)
- **Score**: avg 82.6 | min 49 | max 94
- **Stale** (>48h): 36
- **Avg age**: 68.5h
- **Local-flagged**: 50

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │                        1
  50–59   │                        0
  60–69   │ ██                     3
  70–79   │ █████████             11
  80–89   │ ████████████████████  23
  90–100  │ ██████████            12
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 31 | 62% ⚠️ |
| My Cariboo Now | 10 | 20% |
| Pique Newsmagazine | 2 | 4% |
| 100 Mile Free Press | 2 | 4% |
| BC Gov News | 2 | 4% |
| Quesnel Cariboo Observer | 2 | 4% |
| The Northern Miner | 1 | 2% |

### 🟡 📰 General News

- **Articles**: 144 (144 scored)
- **Score**: avg 49.0 | min 29 | max 99
- **Stale** (>48h): 87
- **Avg age**: 60.5h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        2
  30–39   │ ████████████████████  47
  40–49   │ ███████████████       37
  50–59   │ ████████              20
  60–69   │ ██████████            25
  70–79   │ █████                 12
  80–89   │                        0
  90–100  │                        1
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| NYT Top Stories | 13 | 9% |
| NYT Business | 10 | 7% |
| Pique Newsmagazine | 8 | 6% |
| BC Gov News | 8 | 6% |
| TechRadar | 7 | 5% |
| Western Producer | 7 | 5% |
| Business Insider | 6 | 4% |
| Boing Boing | 6 | 4% |

**Low-score articles (≤30):**

- `[ 29]` Grains Rally to Fresh Highs Adding Risk Premium: Cattle Plunge Looking for a Low - AgWeb  
  <https://www.agweb.com/markets/market-analysis/grains-rally-fresh-highs-adding-risk-premium-cattle-plunge-looking-low>
- `[ 29]` 🔓 [NYT Top Stories] Former Head of All-Girls School Indicted, Accused of Ignoring Abuse Reports  
  <https://www.nytimes.com/2026/07/22/us/head-of-miss-halls-school-indicted.html>
- `[ 30]` 🔓 [NYT Top Stories] Trump Administration Pressures Some Immigrants to Self-Deport With Fines Up to $1.8 Million  
  <https://www.nytimes.com/2026/07/22/us/immigration-civil-fines-self-deportation.html>
- `[ 30]` [Boing Boing] Germany told parents to destroy this talking doll  
  <https://boingboing.net/2026/07/22/my-friend-cayla.html>

### 🟡 🔬 Science

- **Articles**: 37 (37 scored)
- **Score**: avg 47.9 | min 29 | max 60
- **Stale** (>48h): 24
- **Avg age**: 60.3h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ █                      1
  30–39   │ █████                  4
  40–49   │ ████████████████████  16
  50–59   │ ██████████████████    15
  60–69   │ █                      1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 14 | 38% |
| ScienceAlert | 9 | 24% |
| Nautilus | 4 | 11% |
| Boing Boing | 3 | 8% |
| Kagi Small Web | 3 | 8% |
| CNET | 1 | 3% |
| WIRED | 1 | 3% |
| EarthSky | 1 | 3% |

**Low-score articles (≤30):**

- `[ 29]` [Boing Boing] The stubborn old belief that certain weather precedes earthquakes  
  <https://boingboing.net/2026/07/25/earthquake-weather.html>
- `[ 30]` [Boing Boing] A chemist invented a fake Frenchman to justify capital L for liters  
  <https://boingboing.net/2026/07/24/claude-litre-fake-scientist.html>

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 8 (8 scored)
- **Score**: avg 19.5 | min 0 | max 46
- **Stale** (>48h): 5
- **Avg age**: 65.6h

**Score distribution:**
```
  0–9     │ ████████████████████   2
  10–19   │ ████████████████████   2
  20–29   │ ████████████████████   2
  30–39   │ ██████████             1
  40–49   │ ██████████             1
  50–59   │                        0
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| MakeUseOf | 2 | 25% |
| Kagi Small Web | 1 | 12% |
| The Marginalian | 1 | 12% |
| Toms Guide | 1 | 12% |
| CBC Arts | 1 | 12% |
| Kottke.org | 1 | 12% |
| Reactor Magazine | 1 | 12% |

**Low-score articles (≤30):**

- `[ 12]` [MakeUseOf] 7 obscure fantasy series to read instead of waiting for The Winds of Winter  
  <https://www.makeuseof.com/7-obscure-fantasy-series-the-winds-of-winter/>
- `[ 13]` [MakeUseOf] 7 Shakespeare adaptations you didn't know were Shakespeare adaptations  
  <https://www.makeuseof.com/7-undercover-shakespeare-adaptations-ex-machina-warm-bodies/>
- `[ 23]` [The Marginalian] Dostoyevsky in Love  
  <https://www.themarginalian.org/2026/07/23/dostoyevsky-in-love/>
- `[  1]` [Toms Guide] 'Star Trek: Strange New Worlds' season 4 review: The sci-fi prequel continues to boldly go into entertaining territory  
  <https://www.tomsguide.com/entertainment/netflix/star-trek-strange-new-worlds-season-4-review-the-sci-fi-prequel-continues-to-boldly-go-into-entertaining-territory>
- `[  0]` [CBC Arts] Meet the Canadian woman who was Matt Damon's stunt double in The Odyssey  
  <https://www.cbc.ca/news/entertainment/canadian-stunt-woman-odyssey-9.7279649?cmp=rss>
- `[ 28]` [Kottke.org] Unclassifiable Artists  
  <https://kottke.org/26/07/unclassifiable-artists>

### 🔴 🌿 Health & Wellness

- **Articles**: 47 (47 scored)
- **Score**: avg 41.0 | min 13 | max 58
- **Stale** (>48h): 31
- **Avg age**: 62.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █████                  4
  20–29   │ ██                     2
  30–39   │ ███████████████       12
  40–49   │ ████████████████████  16
  50–59   │ ████████████████      13
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| STAT News | 9 | 19% |
| ScienceAlert | 6 | 13% |
| NPR Health News | 5 | 11% |
| Business Insider | 3 | 6% |
| ScienceDaily | 3 | 6% |
| NYT Well | 2 | 4% |
| NYT Business | 2 | 4% |
| TechRadar | 2 | 4% |

**Low-score articles (≤30):**

- `[ 15]` Pluralistic: Apple's robo-repo (25 Jul 2026)  
  <https://pluralistic.net/2026/07/25/cruel-cruelty-oh-cruelty/>
- `[ 21]` 🔓 [Williams Lake Tribune] B.C. Nurses’ Union to end strike, accept mediators’ recommendations  
  <https://wltribune.com/2026/07/24/b-c-nurses-union-to-end-strike-accept-mediators-recommendations/>
- `[ 18]` [TechRadar] ‘When I'm peering down the lens… the rest of the world vanishes. It's just me and the photo’ — research shows the mental health benefits of a daily photography habit  
  <https://www.techradar.com/cameras/photography/when-im-peering-down-the-lens-the-rest-of-the-world-vanishes-its-just-me-and-the-photo-research-shows-the-mental-health-benefits-of-a-daily-photography-habit>
- `[ 24]` [Gizmodo] 27-Year-Old Woman Dies After Getting 'Anti-Aging' Therapy at Bronx Wellness Clinic  
  <https://gizmodo.com/27-year-old-woman-dies-after-getting-anti-aging-therapy-at-bronx-wellness-clinic-2000787876>
- `[ 13]` [ScienceAlert] One Diet Helped Aging Mice Lose Fat While Preserving Muscle  
  <https://www.sciencealert.com/scientists-found-a-diet-that-helped-aging-mice-lose-fat-while-preserving-muscle>
- `[ 13]` [STAT News] STAT+: Trump administration quietly picks Timothy Westlake to lead mental health agency  
  <https://www.statnews.com/2026/07/23/trump-nominates-timothy-westlake-samhsa/?utm_campaign=rss>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (12)

- **[🤖 AI/ML & Tech]** `score 22` — These 7 Gemini prompts made me much more productive in Google Workspace — and they'll do the same for you  
  Issue: `clickbait`  
  <https://www.tomsguide.com/ai/these-7-gemini-prompts-made-me-much-more-productive-in-google-workspace-and-theyll-do-the-same-for-you>
- **[🤖 AI/ML & Tech]** `score 22` — Prime Video's upcoming AI makeover could completely change how you decide what to watch next  
  Issue: `clickbait`  
  <https://www.tomsguide.com/entertainment/prime-video/prime-videos-upcoming-ai-makeover-could-completely-change-how-you-decide-what-to-watch-next>
- **[🤖 AI/ML & Tech]** `score 24` — New to ChatGPT Work? These 7 prompts turn it into a personal assistant  
  Issue: `clickbait`  
  <https://www.tomsguide.com/ai/chatgpt/new-to-chatgpt-work-these-7-prompts-turn-it-into-a-personal-assistant>
- **[🤖 AI/ML & Tech]** `score 38` — Chick-fil-A warned customers their loyalty accounts were breached in a hack  
  Issue: `duplicate`  
  <https://qz.com/chick-fil-a-data-breach-loyalty-accounts-credential-stuffing-072226>
- **[🤖 AI/ML & Tech]** `score 36` — Rental giant Carla leaks user names, emails, and phone numbers ahead of summer holiday break  
  Issue: `duplicate`  
  <https://www.techradar.com/pro/security/rental-giant-carla-leaks-user-names-emails-and-phone-numbers-ahead-of-summer-holiday-break>
- **[🌍 Climate & Energy]** `score 22` — Subaru's Biggest EV Yet Just Got Delayed  
  Issue: `clickbait`  
  <https://insideevs.com/news/802574/2027-subaru-getaway-ev-delay/>
- **[📰 General News]** `score 34` — Government Surveillance Power Rebuked as Landowners Win Massive Property Rights Battle - AgWeb  
  Issue: `clickbait`  
  <https://www.agweb.com/news/business/farmland/government-surveillance-power-rebuked-landowners-win-massive-property-righ>
- **[📰 General News]** `score 33` — The time two guys bolted a Ford Pinto to a Cessna and called it a flying car  
  Issue: `clickbait`  
  <https://boingboing.net/2026/07/25/ave-mizar.html>
- **[📰 General News]** `score 33` — Engine and cabin air filters: the $30 DIY fix that extends your car's life  
  Issue: `clickbait`  
  <https://www.howtogeek.com/engine-cabin-air-filters-diy-fix-extends-your-cars-life/>
- **[📰 General News]** `score 34` — Trump's Trigger Warnings  
  Issue: `clickbait`  
  <https://www.theatlantic.com/culture/2026/07/trump-smithsonian-signs/688069/?utm_source=feed>
- **[📰 General News]** `score 32` — Britain's £36 million peanut farm harvested less than it planted  
  Issue: `clickbait`  
  <https://boingboing.net/2026/07/24/tanganyika-groundnut-scheme.html>
- **[📰 General News]** `score 36` — 19th Century Japanese Woodblock Prints Creatively Illustrate the Inner Workings of the Human Body  
  Issue: `clickbait`  
  <https://www.openculture.com/2026/07/japanese-woodblock-prints-illustrate-the-human-body.html>

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 44 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 15 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏠 Homelab & DIY** has 7 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 36 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏔️ Williams Lake Local** is dominated by **Williams Lake Tribune** (31 articles, 62%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **📰 General News** has 87 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 24 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (19.5) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🌿 Health & Wellness** has 31 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 12 article(s) should be removed (`clickbait` ×10, `duplicate` ×2) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 8 feeds · 394 articles · 2026-07-26 20:24 UTC_
