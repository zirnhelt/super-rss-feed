# Feed Scoring & Scrubbing Report

_Generated: 2026-08-02 14:45 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 8 |
| Total articles | 394 |
| Stale articles (>48h) | 259 |
| Scrub pass | ✅ ran |
| Flagged for removal | 9 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 76 | 🔴 43.3 | 22–59 | 52 | TechRadar (13) |
| 🌍 Climate & Energy | 28 | 🟡 51.5 | 23–82 | 20 | InsideEVs (3) |
| 🏠 Homelab & DIY | 17 | 🟡 47.5 | 18–65 | 10 | Tom's Hardware (3) |
| 🏔️ Williams Lake Local | 29 | 🟢 80.1 | 48–93 | 17 | Williams Lake Tribune (15) |
| 📰 General News | 150 | 🟡 66.5 | 57–80 | 92 | TechRadar (14) |
| 🔬 Science | 39 | 🟡 50.1 | 20–68 | 26 | ScienceDaily (12) |
| 🚀 Sci-Fi & Culture | 1 | 🔴 18.0 | 18–18 | 1 | Reactor Magazine (1) |
| 🌿 Health & Wellness | 54 | 🟡 49.1 | 10–72 | 41 | ScienceDaily (10) |

---

## Per-Feed Detail

### 🔴 🤖 AI/ML & Tech

- **Articles**: 76 (76 scored)
- **Score**: avg 43.3 | min 22 | max 59
- **Stale** (>48h): 52
- **Avg age**: 70.8h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ █                      4
  30–39   │ ██████                15
  40–49   │ ████████████████████  43
  50–59   │ ██████                14
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| TechRadar | 13 | 17% |
| Business Insider | 8 | 11% |
| Tom's Hardware | 7 | 9% |
| NYT Business | 6 | 8% |
| TechCrunch | 6 | 8% |
| WIRED | 4 | 5% |
| Android Authority | 4 | 5% |
| NYT Top Stories | 4 | 5% |

**Low-score articles (≤30):**

- `[ 22]` [Gizmodo] OpenAI's Rogue AI Models Were Reportedly Acting Like the Guy From Christopher Nolan's 'Memento'  
  <https://gizmodo.com/openais-rogue-ai-models-were-reportedly-acting-like-the-guy-from-christopher-nolans-memento-2000790904>
- `[ 22]` [MacRumors] iPhone 18 Pro Models Could Be Up to $300 More Expensive, Says Analyst  
  <https://www.macrumors.com/2026/07/31/iphone-18-pro-models-300-more-expensive/>
- `[ 27]` [Neowin] Here are all the new features Microsoft added to Excel in July 2026  
  <https://www.neowin.net/news/here-are-all-the-new-features-microsoft-added-to-excel-in-july-2026/?utm_source=rss>
- `[ 28]` [Engadget] WhatsApp now supports encrypted calls on the web  
  <https://www.engadget.com/2225240/whatsapp-now-supports-encrypted-calls-on-the-web/>

### 🟡 🌍 Climate & Energy

- **Articles**: 28 (28 scored)
- **Score**: avg 51.5 | min 23 | max 82
- **Stale** (>48h): 20
- **Avg age**: 65.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ █                      1
  30–39   │ ███                    2
  40–49   │ █████████████          8
  50–59   │ ████████████████████  12
  60–69   │ █████                  3
  70–79   │ █                      1
  80–89   │ █                      1
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| InsideEVs | 3 | 11% |
| Al Jazeera English | 3 | 11% |
| WIRED | 3 | 11% |
| NYT Business | 3 | 11% |
| TechRadar | 2 | 7% |
| Pique Newsmagazine | 1 | 4% |
| ScienceDaily | 1 | 4% |
| Engadget | 1 | 4% |

**Low-score articles (≤30):**

- `[ 23]` 🔓 [NYT Business] Apple’s Siri Got an A.I. Brain Transplant. Try These 5 Prompts to Get Acclimated.  
  <https://www.nytimes.com/2026/07/30/technology/personaltech/apple-siri-ai-prompts.html>

### 🟡 🏠 Homelab & DIY

- **Articles**: 17 (17 scored)
- **Score**: avg 47.5 | min 18 | max 65
- **Stale** (>48h): 10
- **Avg age**: 66.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ████                   1
  20–29   │ ████                   1
  30–39   │ ████████               2
  40–49   │ ████████████████████   5
  50–59   │ ████████████████████   5
  60–69   │ ████████████           3
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Tom's Hardware | 3 | 18% |
| MakeUseOf | 2 | 12% |
| Kagi Small Web | 2 | 12% |
| XDA Developers | 2 | 12% |
| Hackaday | 2 | 12% |
| Daniele Messi. — Writing | 2 | 12% |
| How-To Geek | 1 | 6% |
| TechRadar | 1 | 6% |

**Low-score articles (≤30):**

- `[ 18]` [Kagi Small Web] Memos  
  <https://bln41.de/memos/>
- `[ 22]` [MacRumors] New Apple TV and HomePod Mini Reportedly 'Nearly Ready to Launch'  
  <https://www.macrumors.com/2026/07/28/new-apple-tv-homepod-mini-nearly-ready/>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 29 (29 scored)
- **Score**: avg 80.1 | min 48 | max 93
- **Stale** (>48h): 17
- **Avg age**: 53.1h
- **Local-flagged**: 29

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │ ██                     2
  50–59   │                        0
  60–69   │ █                      1
  70–79   │ ████████████           9
  80–89   │ ████████████████████  14
  90–100  │ ████                   3
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 15 | 52% ⚠️ |
| My Cariboo Now | 11 | 38% |
| Vancouver Sun | 1 | 3% |
| BC Gov News | 1 | 3% |
| The Tyee | 1 | 3% |

### 🟡 📰 General News

- **Articles**: 150 (150 scored)
- **Score**: avg 66.5 | min 57 | max 80
- **Stale** (>48h): 92
- **Avg age**: 67.0h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │ ██████████            33
  60–69   │ ████████████████████  62
  70–79   │ █████████████████     53
  80–89   │                        2
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| TechRadar | 14 | 9% |
| WIRED | 11 | 7% |
| Tom's Hardware | 11 | 7% |
| Hackaday | 10 | 7% |
| NYT Business | 10 | 7% |
| The Tyee | 9 | 6% |
| NYT Top Stories | 7 | 5% |
| ScienceAlert | 7 | 5% |

### 🟡 🔬 Science

- **Articles**: 39 (39 scored)
- **Score**: avg 50.1 | min 20 | max 68
- **Stale** (>48h): 26
- **Avg age**: 68.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ██                     2
  30–39   │                        0
  40–49   │ █████████████         13
  50–59   │ ████████████████████  20
  60–69   │ ████                   4
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 12 | 31% |
| ScienceAlert | 9 | 23% |
| Boing Boing | 7 | 18% |
| Nautilus | 3 | 8% |
| Quanta Magazine | 2 | 5% |
| NPR Health News | 1 | 3% |
| WIRED | 1 | 3% |
| Outside Online | 1 | 3% |

**Low-score articles (≤30):**

- `[ 20]` 🔓 [NYT Business] In Another Wild Day for South Korean Stocks, Market Surges 15 Percent  
  <https://www.nytimes.com/2026/07/31/business/korea-stocks-chips-kospi.html>
- `[ 27]` [TechRadar] Meta smart glasses were the best tech I took on my honeymoon, but privacy concerns kept them from being as frictionless as I wished they could be  
  <https://www.techradar.com/computing/virtual-reality-augmented-reality/meta-smart-glasses-were-the-best-tech-i-took-on-my-honeymoon-but-privacy-concerns-kept-them-from-being-as-frictionless-as-i-wished-they-could-be>

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 1 (1 scored)
- **Score**: avg 18.0 | min 18 | max 18
- **Stale** (>48h): 1
- **Avg age**: 69.8h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ████████████████████   1
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
| Reactor Magazine | 1 | 100% |

**Low-score articles (≤30):**

- `[ 18]` [Reactor Magazine] Martha Wells Book Club: The Element of Fire  
  <https://reactormag.com/martha-wells-book-club-the-element-of-fire/>

### 🟡 🌿 Health & Wellness

- **Articles**: 54 (54 scored)
- **Score**: avg 49.1 | min 10 | max 72
- **Stale** (>48h): 41
- **Avg age**: 74.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ █                      1
  20–29   │ ███                    3
  30–39   │ ██████                 6
  40–49   │ ██████████████        14
  50–59   │ ████████████████████  20
  60–69   │ ████████               8
  70–79   │ ██                     2
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 10 | 19% |
| NPR Health News | 6 | 11% |
| STAT News | 5 | 9% |
| Nautilus | 4 | 7% |
| ScienceAlert | 3 | 6% |
| New Atlas | 3 | 6% |
| Toms Guide | 2 | 4% |
| Global News | 2 | 4% |

**Low-score articles (≤30):**

- `[ 22]` [Android Authority] Google Health is preparing to take over Nest Hub sleep tracking  
  <https://www.androidauthority.com/nest-hub-sleep-tracking-moving-to-google-health-3693527/>
- `[ 30]` [Nautilus] More Testosterone Won’t Make a Better Soldier or a Tougher Man—Aggression and Strength Drive T Levels, Not the Other Way Around  
  <https://nautil.us/more-testosterone-wont-make-a-better-soldier-or-a-tougher-man-aggression-and-strength-drive-t-levels-not-the-other-way-around-1283226/>
- `[ 10]` [New Atlas] Antarctica's penguins carry forever chemicals in their feathers, study reveals  
  <https://newatlas.com/environment/penguins-forever-chemicals-feathers/>
- `[ 26]` 🔓 [Outside Online] A Mushroom Foraging Trip Outside Yellowstone Just Sent 11 People to the Hospital  
  <https://www.outsideonline.com/outdoor-adventure/exploration-survival/montana-yellowstone-wild-mushroom-poisoning/>
- `[ 30]` [Business Insider] Lilian Weng flips from Thinking Machines to OpenAI after saying the startup's pace hurt her health  
  <https://www.businessinsider.com/lilian-weng-returns-to-openai-after-leaving-thinking-machines-lab-2026-7>
- `[ 24]` [TechRadar] It’s hard to feel sorry for AI companies when China is giving them a taste of their own medicine  
  <https://www.techradar.com/pro/its-hard-to-feel-sorry-for-ai-companies-when-china-is-giving-them-a-taste-of-their-own-medicine>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (9)

- **[🤖 AI/ML & Tech]** `score 22` — OpenAI's Rogue AI Models Were Reportedly Acting Like the Guy From Christopher Nolan's 'Memento'  
  Issue: `clickbait`  
  <https://gizmodo.com/openais-rogue-ai-models-were-reportedly-acting-like-the-guy-from-christopher-nolans-memento-2000790904>
- **[🤖 AI/ML & Tech]** `score 22` — iPhone 18 Pro Models Could Be Up to $300 More Expensive, Says Analyst  
  Issue: `clickbait`  
  <https://www.macrumors.com/2026/07/31/iphone-18-pro-models-300-more-expensive/>
- **[🤖 AI/ML & Tech]** `score 27` — Here are all the new features Microsoft added to Excel in July 2026  
  Issue: `clickbait`  
  <https://www.neowin.net/news/here-are-all-the-new-features-microsoft-added-to-excel-in-july-2026/?utm_source=rss>
- **[🌍 Climate & Energy]** `score 23` — Apple's Siri Got an A.I. Brain Transplant. Try These 5 Prompts to Get Acclimated.  
  Issue: `clickbait`  
  <https://www.nytimes.com/2026/07/30/technology/personaltech/apple-siri-ai-prompts.html>
- **[🏠 Homelab & DIY]** `score 18` — Memos  
  Issue: `clickbait`  
  <https://bln41.de/memos/>
- **[🏠 Homelab & DIY]** `score 22` — New Apple TV and HomePod Mini Reportedly 'Nearly Ready to Launch'  
  Issue: `clickbait`  
  <https://www.macrumors.com/2026/07/28/new-apple-tv-homepod-mini-nearly-ready/>
- **[🔬 Science]** `score 20` — In Another Wild Day for South Korean Stocks, Market Surges 15 Percent  
  Issue: `clickbait`  
  <https://www.nytimes.com/2026/07/31/business/korea-stocks-chips-kospi.html>
- **[🔬 Science]** `score 27` — Meta smart glasses were the best tech I took on my honeymoon, but privacy concerns kept them from being as frictionless as I wished they could be  
  Issue: `clickbait`  
  <https://www.techradar.com/computing/virtual-reality-augmented-reality/meta-smart-glasses-were-the-best-tech-i-took-on-my-honeymoon-but-privacy-concerns-kept-them-from-being-as-frictionless-as-i-wished-they-could-be>
- **[🌿 Health & Wellness]** `score 24` — It's hard to feel sorry for AI companies when China is giving them a taste of their own medicine  
  Issue: `duplicate`  
  <https://www.techradar.com/pro/its-hard-to-feel-sorry-for-ai-companies-when-china-is-giving-them-a-taste-of-their-own-medicine>

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 52 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 20 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏠 Homelab & DIY** has 10 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 17 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏔️ Williams Lake Local** is dominated by **Williams Lake Tribune** (15 articles, 52%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **📰 General News** has 92 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🔬 Science** has 26 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌿 Health & Wellness** has 41 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 9 article(s) should be removed (`clickbait` ×8, `duplicate` ×1) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 8 feeds · 394 articles · 2026-08-02 14:45 UTC_
