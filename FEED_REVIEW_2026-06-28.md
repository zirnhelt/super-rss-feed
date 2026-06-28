# Feed Scoring & Scrubbing Report

_Generated: 2026-06-28 14:58 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 8 |
| Total articles | 231 |
| Stale articles (>48h) | 152 |
| Scrub pass | ✅ ran |
| Flagged for removal | 6 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 33 | 🟡 55.3 | 17–79 | 23 | Business Insider (6) |
| 🌍 Climate & Energy | 10 | 🔴 28.5 | 8–70 | 7 | New Atlas (2) |
| 🏠 Homelab & DIY | 5 | 🔴 3.4 | 0–12 | 3 | XDA Developers (3) |
| 🏔️ Williams Lake Local | 19 | 🟢 83.6 | 18–90 | 11 | Williams Lake Tribune (9) |
| 📰 General News | 114 | 🟢 72.8 | 62–87 | 70 | Al Jazeera English (21) |
| 🔬 Science | 1 | 🔴 6.0 | 6–6 | 1 | The Marginalian (1) |
| 🚀 Sci-Fi & Culture | 6 | 🔴 21.2 | 7–75 | 6 | Boing Boing (1) |
| 🌿 Health & Wellness | 43 | 🔴 34.7 | 10–81 | 31 | STAT News (8) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 33 (33 scored)
- **Score**: avg 55.3 | min 17 | max 79
- **Stale** (>48h): 23
- **Avg age**: 71.5h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ███                    2
  20–29   │ █                      1
  30–39   │ ██████                 4
  40–49   │ ██████████             6
  50–59   │ ████████               5
  60–69   │ █████                  3
  70–79   │ ████████████████████  12
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Business Insider | 6 | 18% |
| NYT Business | 4 | 12% |
| Quartz | 4 | 12% |
| Android Authority | 3 | 9% |
| Engadget | 2 | 6% |
| TechCrunch | 2 | 6% |
| STAT News | 2 | 6% |
| Gizmodo | 1 | 3% |

**Low-score articles (≤30):**

- `[ 21]` [Business Insider] Microsoft's Satya Nadella says every company should build its own AI model  
  <https://www.businessinsider.com/satya-nadella-said-every-company-should-build-own-ai-model-2026-6>
- `[ 17]` [Engadget] Apple executive in charge of Vision Pro is reportedly leaving for OpenAI  
  <https://www.engadget.com/2203115/apple-executive-vision-pro-leaving-for-openai/>
- `[ 17]` 🔓 [The Atlantic Culture] <em>Supergirl</em> Crashes and Burns  
  <https://www.theatlantic.com/culture/2026/06/supergirl-movie-2026-review/687712/?utm_source=feed>

### 🔴 🌍 Climate & Energy

- **Articles**: 10 (10 scored)
- **Score**: avg 28.5 | min 8 | max 70
- **Stale** (>48h): 7
- **Avg age**: 71.3h

**Score distribution:**
```
  0–9     │ ████████████████████   4
  10–19   │ █████                  1
  20–29   │ █████                  1
  30–39   │ █████                  1
  40–49   │ █████                  1
  50–59   │                        0
  60–69   │ █████                  1
  70–79   │ █████                  1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| New Atlas | 2 | 20% |
| Kagi Small Web | 2 | 20% |
| Wildfire Today | 1 | 10% |
| Kottke.org | 1 | 10% |
| NYT Top Stories | 1 | 10% |
| NYT Business | 1 | 10% |
| Nautilus | 1 | 10% |
| The Narwhal | 1 | 10% |

**Low-score articles (≤30):**

- `[  9]` Wildfire risk to heighten globally in 2026 due to ‘historic’ El Niño – Wildfire Today  
  <https://wildfiretoday.com/wildfire-risk-to-heighten-globally-in-2026-due-to-historic-el-nino/>
- `[  8]` [New Atlas] VW gives California camper van game-changing 4-season comfort boost  
  <https://newatlas.com/campervans/volkswagen-refreshed-multivan-camper/>
- `[  9]` [New Atlas] Skeletal electric street buggy accelerates (to 19) in under 2.5 secs  
  <https://newatlas.com/automotive/amble-one-ev/>
- `[ 16]` 🔓 [NYT Business] How Honda’s Pledge to Go All-Electric Unraveled  
  <https://www.nytimes.com/2026/06/25/business/honda-ev-electric-pledge.html>
- `[  9]` [Kagi Small Web] How EPA rollbacks could harm air and water  
  <https://stallman.org/archives/2026-mar-jun.html#23_June_2026_(How_EPA_rollbacks_could_harm_air_and_water)>
- `[ 26]` [Kagi Small Web] Paying for climate damage under proposed UN tax  
  <https://stallman.org/archives/2026-mar-jun.html#23_June_2026_(Paying_for_climate_damage_under_proposed_UN_tax)>

### 🔴 🏠 Homelab & DIY

- **Articles**: 5 (5 scored)
- **Score**: avg 3.4 | min 0 | max 12
- **Stale** (>48h): 3
- **Avg age**: 54.3h

**Score distribution:**
```
  0–9     │ ████████████████████   4
  10–19   │ █████                  1
  20–29   │                        0
  30–39   │                        0
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
| XDA Developers | 3 | 60% |
| New Atlas | 2 | 40% |

**Low-score articles (≤30):**

- `[  4]` [New Atlas] 3D-printed origami eliminates huge costs of manufacturing molds  
  <https://newatlas.com/3d-printing/origami-inspired-3d-printing-no-molds/>
- `[  0]` [XDA Developers] Your old office PC is secretly a transcoding beast for Plex and Jellyfin with one cheap upgrade  
  <https://www.xda-developers.com/your-old-office-pc-transcoding-beast-with-one-upgrade/>
- `[  1]` [New Atlas] Compact laser engraver levels up your DIY crafts setup  
  <https://newatlas.com/electronics/hanboost-t1-compact-laser-engraver/>
- `[  0]` [XDA Developers] Memos is the dumbest note app I've ever self-hosted, and that's exactly why I use it daily  
  <https://www.xda-developers.com/memos-is-the-dumbest-note-app-i-use-daily/>
- `[ 12]` [XDA Developers] Vaultwarden has been running on a Raspberry Pi Zero in a drawer for a year, and it's the most underrated thing I host  
  <https://www.xda-developers.com/vaultwarden-on-raspberry-pi-zero-most-underrated-thing-i-host/>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 19 (19 scored)
- **Score**: avg 83.6 | min 18 | max 90
- **Stale** (>48h): 11
- **Avg age**: 54.9h
- **Local-flagged**: 19

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██                     1
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │                        0
  60–69   │                        0
  70–79   │                        0
  80–89   │ ████████████████████  10
  90–100  │ ████████████████       8
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 9 | 47% ⚠️ |
| My Cariboo Now | 7 | 37% |
| BC Gov News | 1 | 5% |
| Quesnel Cariboo Observer | 1 | 5% |
| 100 Mile Free Press | 1 | 5% |

**Low-score articles (≤30):**

- `[ 18]` 🔓 [Williams Lake Tribune] NOTICE OF DISPOSITION: Moduline-Olympian Manufactured Home  
  <https://wltribune.com/2026/06/25/notice-of-disposition-moduline-olympian-manufactured-home/>

### 🟢 📰 General News

- **Articles**: 114 (114 scored)
- **Score**: avg 72.8 | min 62 | max 87
- **Stale** (>48h): 70
- **Avg age**: 63.8h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │                        0
  60–69   │ ████████████          39
  70–79   │ ████████████████████  63
  80–89   │ ███                   12
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Al Jazeera English | 21 | 18% |
| Boing Boing | 15 | 13% |
| Business Insider | 10 | 9% |
| Williams Lake Tribune | 10 | 9% |
| Engadget | 8 | 7% |
| NYT Business | 6 | 5% |
| Global News | 5 | 4% |
| BC Gov News | 5 | 4% |

### 🔴 🔬 Science

- **Articles**: 1 (1 scored)
- **Score**: avg 6.0 | min 6 | max 6
- **Stale** (>48h): 1
- **Avg age**: 91.5h

**Score distribution:**
```
  0–9     │ ████████████████████   1
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

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| The Marginalian | 1 | 100% |

**Low-score articles (≤30):**

- `[  6]` [The Marginalian] Diatoms and the Meaning of Life  
  <https://www.themarginalian.org/2026/06/24/diatom-atlas-adolf-schmidt/>

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 6 (6 scored)
- **Score**: avg 21.2 | min 7 | max 75
- **Stale** (>48h): 6
- **Avg age**: 95.7h

**Score distribution:**
```
  0–9     │ ████████████████████   3
  10–19   │ █████████████          2
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │                        0
  60–69   │                        0
  70–79   │ ██████                 1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Boing Boing | 1 | 17% |
| TechRadar | 1 | 17% |
| Quartz | 1 | 17% |
| Strange Horizons | 1 | 17% |
| Gizmodo | 1 | 17% |
| Reactor Magazine | 1 | 17% |

**Low-score articles (≤30):**

- `[  9]` [Boing Boing] Steam Summer Sale is back with Witcher 3 at $4, Cyberpunk under $20  
  <https://boingboing.net/2026/06/25/steam-summer-sale-is-back-with-witcher-3-at-4-cyberpunk-under-20.html>
- `[ 16]` [TechRadar] 'This is no longer science fiction, this is reality': The future of shipping could be the world’s smartest sticky label  
  <https://www.techradar.com/pro/this-is-no-longer-science-fiction-this-is-reality-the-future-of-shipping-could-be-the-worlds-smartest-sticky-label>
- `[  8]` [Quartz] 26 facts about deep space that will genuinely unsettle you  
  <https://qz.com/deep-space-unsettling-facts>
- `[  7]` [Strange Horizons] The Young Die Old by Nguyễn Bình Phương, translated by Khải Q. Nguyễn  
  <https://strangehorizons.com/wordpress/non-fiction/the-young-die-old-by-nguyen-binh-phuong-translated-by-khai-q-nguyen/>
- `[ 12]` [Reactor Magazine] Five Sci-Fi and Fantasy Found Footage Movies  
  <https://reactormag.com/five-sci-fi-and-fantasy-found-footage-movies/>

### 🔴 🌿 Health & Wellness

- **Articles**: 43 (43 scored)
- **Score**: avg 34.7 | min 10 | max 81
- **Stale** (>48h): 31
- **Avg age**: 70.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ████████████████████  14
  20–29   │ █████                  4
  30–39   │ ████████████           9
  40–49   │ ███████                5
  50–59   │ ████                   3
  60–69   │ █████                  4
  70–79   │ ████                   3
  80–89   │ █                      1
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| STAT News | 8 | 19% |
| New Atlas | 5 | 12% |
| NYT Well | 4 | 9% |
| Boing Boing | 3 | 7% |
| Atlas Obscura | 3 | 7% |
| ScienceDaily | 2 | 5% |
| The Verge | 2 | 5% |
| Williams Lake Tribune | 2 | 5% |

**Low-score articles (≤30):**

- `[ 11]` [ScienceDaily] New vitamin B12 therapy shows promise against deadly brain cancer  
  <https://www.sciencedaily.com/releases/2026/06/260622091518.htm>
- `[ 28]` [New Atlas] Massive study upends what we believe about vitamin D, calcium and fractures  
  <https://refractor.io/diet-nutrition/vitamin-d-calcium-reducing-fractures/>
- `[ 23]` [Android Police] How controlling my charger with a smart plug saved my phone's long-term health  
  <https://www.androidpolice.com/controlling-charger-with-smart-plug-saved-phones-long-term-health/>
- `[ 11]` [The Verge] The Guardian&#8217;s Kai Wright refuses to buy a new phone  
  <https://www.theverge.com/report/958695/kai-wright-npr-guardian-interview-questionnaire>
- `[ 10]` [Quartz] 20 things your sleep schedule reveals about your health  
  <https://qz.com/sleep-schedule-reveals-about-your-health>
- `[ 26]` [New Atlas] Missing just one night of sleep impacts your brain’s connections  
  <https://refractor.io/brain/missing-sleep-impact-brain-connections/>
- `[ 13]` [Android Authority] Polled readers love the Fitbit Air, but there’s still room for a Google smart ring  
  <https://www.androidauthority.com/fitbit-air-google-smart-ring-poll-results-3681747/>
- `[ 11]` [New Atlas] Your brain runs on autopilot – until a surprise triggers a memory update  
  <https://refractor.io/learning-memory/surprises-brain-record-information-differently/>
- `[ 17]` 🔓 [NYT Business] Medical Journal Retracts Study Claiming Cancer Therapy Is More Effective When Given in the Morning  
  <https://www.nytimes.com/2026/06/25/business/china-cancer-treatment-research-retraction.html>
- `[ 11]` [STAT News] STAT+: Proposed CDC science office could tighten political control at agency  
  <https://www.statnews.com/2026/06/25/cdc-new-science-office-tighter-political-control/?utm_campaign=rss>
- `[ 23]` 🔓 [Williams Lake Tribune] Yukon hantavirus cruise ship passenger discharged from B.C. hospital, still recovering  
  <https://wltribune.com/2026/06/25/yukon-hantavirus-cruise-ship-passenger-discharged-from-b-c-hospital-still-recovering/>
- `[ 30]` [STAT News] STAT+: The China debate gets louder in Washington  
  <https://www.statnews.com/2026/06/25/biotech-news-the-china-debate-gets-louder-in-washington/?utm_campaign=rss>
- `[ 16]` [Engadget] Can your smartwatch detect sleep apnea?  
  <https://www.engadget.com/2200959/can-smartwatch-detect-sleep-apnea/>
- `[ 12]` [NYT Well] Fermented Food: Does Eating Kimchi or Sauerkraut Have Health Benefits?  
  <https://www.nytimes.com/2026/06/25/well/eat/fermented-food-health-benefits.html>
- `[ 30]` [Engadget] Lumysi hid an activity tracker in a bracelet because wearables are gauche, darling  
  <https://www.engadget.com/2199703/lumsi-hid-an-activity-tracker-in-a-bracelet-because-wearables-are-gauche-darling/>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (6)

- **[🤖 AI/ML & Tech]** `score 17` — Supergirl Crashes and Burns  
  Issue: `clickbait`  
  <https://www.theatlantic.com/culture/2026/06/supergirl-movie-2026-review/687712/?utm_source=feed>
- **[🤖 AI/ML & Tech]** `score 33` — A Reddit user gave an AI agent 6 months and $50,000 to find him a wife — and it reveals where AI is headed next  
  Issue: `clickbait`  
  <https://www.tomsguide.com/ai/a-reddit-user-gave-an-ai-agent-6-months-and-usd50-000-to-find-him-a-wife-and-it-reveals-where-ai-is-headed-next>
- **[🏔️ Williams Lake Local]** `score 18` — NOTICE OF DISPOSITION: Moduline-Olympian Manufactured Home  
  Issue: `clickbait`  
  <https://wltribune.com/2026/06/25/notice-of-disposition-moduline-olympian-manufactured-home/>
- **[🚀 Sci-Fi & Culture]** `score 16` — 'This is no longer science fiction, this is reality': The future of shipping could be the world's smartest sticky label  
  Issue: `clickbait`  
  <https://www.techradar.com/pro/this-is-no-longer-science-fiction-this-is-reality-the-future-of-shipping-could-be-the-worlds-smartest-sticky-label>
- **[🌿 Health & Wellness]** `score 33` — Fall asleep fast in a heatwave with this magnesium-packed bedtime iced tea — here's why it works and how to make it  
  Issue: `clickbait`  
  <https://www.tomsguide.com/wellness/sleep/fall-asleep-fast-in-a-heatwave-with-this-magnesium-packed-bedtime-iced-tea-heres-why-it-works-and-how-to-make-it>
- **[🌿 Health & Wellness]** `score 32` — The Ship of Doom in Skopje, North Macedonia  
  Issue: `clickbait`  
  <https://www.atlasobscura.com/places/the-ship-of-doom>

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 23 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🌍 Climate & Energy** has a low average score (28.5) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🌍 Climate & Energy** has 7 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 11 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏔️ Williams Lake Local** is dominated by **Williams Lake Tribune** (9 articles, 47%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **📰 General News** has 70 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (21.2) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🚀 Sci-Fi & Culture** has 6 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🌿 Health & Wellness** has a low average score (34.7) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🌿 Health & Wellness** has 31 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 6 article(s) should be removed (`clickbait` ×6) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 8 feeds · 231 articles · 2026-06-28 14:58 UTC_
