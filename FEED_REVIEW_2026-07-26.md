# Feed Scoring & Scrubbing Report

_Generated: 2026-07-26 14:43 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 8 |
| Total articles | 359 |
| Stale articles (>48h) | 257 |
| Scrub pass | ✅ ran |
| Flagged for removal | 9 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 69 | 🔴 44.5 | 22–66 | 49 | TechRadar (11) |
| 🌍 Climate & Energy | 23 | 🟡 46.6 | 22–61 | 16 | InsideEVs (7) |
| 🏠 Homelab & DIY | 12 | 🔴 39.1 | 8–58 | 10 | XDA Developers (3) |
| 🏔️ Williams Lake Local | 49 | 🟢 82.4 | 49–94 | 35 | Williams Lake Tribune (30) |
| 📰 General News | 123 | 🔴 44.7 | 29–79 | 81 | NYT Top Stories (11) |
| 🔬 Science | 34 | 🟡 46.6 | 20–60 | 27 | ScienceDaily (11) |
| 🚀 Sci-Fi & Culture | 6 | 🔴 16.3 | 0–33 | 5 | MakeUseOf (1) |
| 🌿 Health & Wellness | 43 | 🔴 39.9 | 13–55 | 34 | STAT News (8) |

---

## Per-Feed Detail

### 🔴 🤖 AI/ML & Tech

- **Articles**: 69 (69 scored)
- **Score**: avg 44.5 | min 22 | max 66
- **Stale** (>48h): 49
- **Avg age**: 74.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        1
  30–39   │ ████████              16
  40–49   │ ████████████████████  40
  50–59   │ ████                   9
  60–69   │ █                      3
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| TechRadar | 11 | 16% |
| Business Insider | 10 | 14% |
| TechCrunch | 9 | 13% |
| Tom's Hardware | 8 | 12% |
| WIRED | 5 | 7% |
| Engadget | 4 | 6% |
| Quartz | 4 | 6% |
| Boing Boing | 3 | 4% |

**Low-score articles (≤30):**

- `[ 22]` [Toms Guide] Prime Video's upcoming AI makeover could completely change how you decide what to watch next  
  <https://www.tomsguide.com/entertainment/prime-video/prime-videos-upcoming-ai-makeover-could-completely-change-how-you-decide-what-to-watch-next>

### 🟡 🌍 Climate & Energy

- **Articles**: 23 (23 scored)
- **Score**: avg 46.6 | min 22 | max 61
- **Stale** (>48h): 16
- **Avg age**: 75.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ███                    2
  30–39   │ █                      1
  40–49   │ ████████████████████  11
  50–59   │ ████████████           7
  60–69   │ ███                    2
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| InsideEVs | 7 | 30% |
| WIRED | 3 | 13% |
| TechCrunch | 2 | 9% |
| NYT Top Stories | 1 | 4% |
| Williams Lake Tribune | 1 | 4% |
| TechRadar | 1 | 4% |
| Engadget | 1 | 4% |
| Wildfire Today | 1 | 4% |

**Low-score articles (≤30):**

- `[ 23]` 🔓 [Williams Lake Tribune] B.C. allowing Tilbury gas terminal expansion to circumvent Utilities Commission  
  <https://wltribune.com/2026/07/24/b-c-allowing-tilbury-gas-terminal-expansion-to-circumvent-utilities-commission/>
- `[ 22]` [InsideEVs] Subaru's Biggest EV Yet Just Got Delayed  
  <https://insideevs.com/news/802574/2027-subaru-getaway-ev-delay/>

### 🔴 🏠 Homelab & DIY

- **Articles**: 12 (12 scored)
- **Score**: avg 39.1 | min 8 | max 58
- **Stale** (>48h): 10
- **Avg age**: 84.2h

**Score distribution:**
```
  0–9     │ ██████████             2
  10–19   │                        0
  20–29   │                        0
  30–39   │ ███████████████        3
  40–49   │ ████████████████████   4
  50–59   │ ███████████████        3
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| XDA Developers | 3 | 25% |
| New Atlas | 2 | 17% |
| Android Authority | 1 | 8% |
| MakeUseOf | 1 | 8% |
| How-To Geek | 1 | 8% |
| Boing Boing | 1 | 8% |
| MacRumors | 1 | 8% |
| Tom's Hardware | 1 | 8% |

**Low-score articles (≤30):**

- `[  8]` [MacRumors] Apple Raises iCloud+ Prices in 8 Countries  
  <https://www.macrumors.com/2026/07/17/apple-icloud-plus-price-increase/>
- `[ 30]` [New Atlas] Extra-wide tiny house puts a terrace up top and sleeps five inside  
  <https://newatlas.com/tiny-houses/white-pine-backcountry-tiny-homes/>
- `[  9]` [New Atlas] 3D printing breakthrough produces custom contact lenses in 20 minutes  
  <https://newatlas.com/3d-printing/3d-printed-custom-contact-lenses-20-minutes/>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 49 (49 scored)
- **Score**: avg 82.4 | min 49 | max 94
- **Stale** (>48h): 35
- **Avg age**: 66.7h
- **Local-flagged**: 49

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
  90–100  │ █████████             11
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 30 | 61% ⚠️ |
| My Cariboo Now | 9 | 18% |
| BC Gov News | 3 | 6% |
| Pique Newsmagazine | 2 | 4% |
| 100 Mile Free Press | 2 | 4% |
| Quesnel Cariboo Observer | 2 | 4% |
| The Northern Miner | 1 | 2% |

### 🔴 📰 General News

- **Articles**: 123 (123 scored)
- **Score**: avg 44.7 | min 29 | max 79
- **Stale** (>48h): 81
- **Avg age**: 66.8h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        2
  30–39   │ ████████████████████  49
  40–49   │ ███████████████       39
  50–59   │ ████████              20
  60–69   │ ██                     7
  70–79   │ ██                     6
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| NYT Top Stories | 11 | 9% |
| NYT Business | 10 | 8% |
| Pique Newsmagazine | 8 | 7% |
| BC Gov News | 8 | 7% |
| Western Producer | 7 | 6% |
| Boing Boing | 6 | 5% |
| Williams Lake Tribune | 6 | 5% |
| Global News | 5 | 4% |

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

- **Articles**: 34 (34 scored)
- **Score**: avg 46.6 | min 20 | max 60
- **Stale** (>48h): 27
- **Avg age**: 74.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ██                     2
  30–39   │ █████                  4
  40–49   │ ██████████████████    13
  50–59   │ ████████████████████  14
  60–69   │ █                      1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 11 | 32% |
| ScienceAlert | 9 | 26% |
| Nautilus | 4 | 12% |
| Boing Boing | 3 | 9% |
| EarthSky | 2 | 6% |
| STAT News | 2 | 6% |
| Kagi Small Web | 2 | 6% |
| WIRED | 1 | 3% |

**Low-score articles (≤30):**

- `[ 29]` [Boing Boing] The stubborn old belief that certain weather precedes earthquakes  
  <https://boingboing.net/2026/07/25/earthquake-weather.html>
- `[ 30]` [Boing Boing] A chemist invented a fake Frenchman to justify capital L for liters  
  <https://boingboing.net/2026/07/24/claude-litre-fake-scientist.html>
- `[ 20]` [EarthSky] Another new Psyche mission flyby image of Mars  
  <https://earthsky.org/space/psyche-mission-fly-by-mars-may-15-2026-pics/>

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 6 (6 scored)
- **Score**: avg 16.3 | min 0 | max 33
- **Stale** (>48h): 5
- **Avg age**: 77.1h

**Score distribution:**
```
  0–9     │ ████████████████████   2
  10–19   │ ██████████             1
  20–29   │ ████████████████████   2
  30–39   │ ██████████             1
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
| MakeUseOf | 1 | 17% |
| The Marginalian | 1 | 17% |
| Toms Guide | 1 | 17% |
| CBC Arts | 1 | 17% |
| Kottke.org | 1 | 17% |
| Reactor Magazine | 1 | 17% |

**Low-score articles (≤30):**

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

- **Articles**: 43 (43 scored)
- **Score**: avg 39.9 | min 13 | max 55
- **Stale** (>48h): 34
- **Avg age**: 73.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █████                  4
  20–29   │ ██                     2
  30–39   │ ████████████████████  14
  40–49   │ █████████████████     12
  50–59   │ ███████████████       11
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| STAT News | 8 | 19% |
| ScienceAlert | 5 | 12% |
| Business Insider | 4 | 9% |
| ScienceDaily | 3 | 7% |
| NPR Health News | 3 | 7% |
| NYT Well | 2 | 5% |
| TechRadar | 2 | 5% |
| Global News | 2 | 5% |

**Low-score articles (≤30):**

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
- `[ 16]` [The Guardian Global Development] Healthy diet too expensive for one in three people globally, UN report finds  
  <https://www.theguardian.com/global-development/2026/jul/21/healthy-diet-too-expensive-for-one-in-three-people-globally-un-report-finds>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (9)

- **[🤖 AI/ML & Tech]** `score 38` — Chick-fil-A warned customers their loyalty accounts were breached in a hack  
  Issue: `clickbait`  
  <https://qz.com/chick-fil-a-data-breach-loyalty-accounts-credential-stuffing-072226>
- **[🤖 AI/ML & Tech]** `score 36` — Rental giant Carla leaks user names, emails, and phone numbers ahead of summer holiday break  
  Issue: `clickbait`  
  <https://www.techradar.com/pro/security/rental-giant-carla-leaks-user-names-emails-and-phone-numbers-ahead-of-summer-holiday-break>
- **[🌍 Climate & Energy]** `score 22` — Subaru's Biggest EV Yet Just Got Delayed  
  Issue: `clickbait`  
  <https://insideevs.com/news/802574/2027-subaru-getaway-ev-delay/>
- **[📰 General News]** `score 33` — The time two guys bolted a Ford Pinto to a Cessna and called it a flying car  
  Issue: `clickbait`  
  <https://boingboing.net/2026/07/25/ave-mizar.html>
- **[📰 General News]** `score 32` — Britain's £36 million peanut farm harvested less than it planted  
  Issue: `clickbait`  
  <https://boingboing.net/2026/07/24/tanganyika-groundnut-scheme.html>
- **[📰 General News]** `score 36` — 19th Century Japanese Woodblock Prints Creatively Illustrate the Inner Workings of the Human Body  
  Issue: `clickbait`  
  <https://www.openculture.com/2026/07/japanese-woodblock-prints-illustrate-the-human-body.html>
- **[📰 General News]** `score 38` — Bear Dies After Getting Stranded Atop Electric Pole in New Mexico  
  Issue: `clickbait`  
  <https://www.nytimes.com/2026/07/23/us/new-mexico-bear-electrical-pole-death.html>
- **[📰 General News]** `score 35` — Amid Cyclospora Outbreak Tied to Lettuce, America Skips Salads  
  Issue: `clickbait`  
  <https://www.nytimes.com/2026/07/23/business/cyclospora-lettuce-salad.html>
- **[📰 General News]** `score 37` — The Mary Pit Head in Fife, Scotland  
  Issue: `clickbait`  
  <https://www.atlasobscura.com/places/the-mary-pit-head>

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 49 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 16 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏠 Homelab & DIY** has 10 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 35 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏔️ Williams Lake Local** is dominated by **Williams Lake Tribune** (30 articles, 61%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **📰 General News** has 81 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 27 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (16.3) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🌿 Health & Wellness** has 34 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 9 article(s) should be removed (`clickbait` ×9) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 8 feeds · 359 articles · 2026-07-26 14:43 UTC_
