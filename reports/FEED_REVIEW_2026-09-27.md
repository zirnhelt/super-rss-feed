# Feed Scoring & Scrubbing Report

_Generated: 2026-09-27 17:46 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 11 |
| Total articles | 436 |
| Stale articles (>48h) | 368 |
| Scrub pass | ✅ ran |
| Flagged for removal | 15 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 97 | 🟡 46.6 | 18–72 | 83 | TechRadar (12) |
| 🌍 Climate & Energy | 36 | 🔴 44.9 | 10–65 | 32 | New Atlas (4) |
| 🏛️ Architecture & Design | 35 | 🟡 49.5 | 37–70 | 30 | ArchDaily (16) |
| 🏠 Homelab & DIY | 32 | 🔴 44.6 | 3–62 | 27 | Popular Woodworking (8) |
| 🌾 Homestead & Hobby Farm | 6 | 🔴 42.3 | 15–60 | 6 | Hobby Farms (4) |
| 🏔️ Williams Lake Local | 37 | 🟢 82.1 | 67–92 | 27 | Williams Lake Tribune (16) |
| 📰 General News | 60 | 🟡 69.9 | 53–76 | 51 | TechRadar (8) |
| 🥾 Outdoors & Recreation | 7 | 🔴 30.7 | 15–50 | 5 | Outside Online (3) |
| 🔬 Science | 51 | 🟡 52.7 | 34–60 | 42 | ScienceDaily (17) |
| 🚀 Sci-Fi & Culture | 9 | 🔴 19.1 | 2–56 | 8 | Kagi Small Web (3) |
| 🌿 Health & Wellness | 66 | 🟡 57.7 | 26–75 | 57 | STAT News (6) |

---

## Per-Feed Detail

### 🟡 🤖 AI/ML & Tech

- **Articles**: 97 (97 scored)
- **Score**: avg 46.6 | min 18 | max 72
- **Stale** (>48h): 83
- **Avg age**: 80.8h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        1
  20–29   │ █████                 10
  30–39   │ ██████                12
  40–49   │ █████████████         26
  50–59   │ ████████████████████  38
  60–69   │ ████                   9
  70–79   │                        1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| TechRadar | 12 | 12% |
| Business Insider | 10 | 10% |
| Kagi Small Web | 7 | 7% |
| Tom's Hardware | 7 | 7% |
| WIRED | 7 | 7% |
| NYT Business | 6 | 6% |
| TechCrunch | 5 | 5% |
| Fast Company | 4 | 4% |

**Low-score articles (≤30):**

- `[ 20]` [Kagi Small Web] Weekend Reading — Invisible as someone else's problem  
  <https://labnotes.org/weekend-reading-invisible-as-someone-elses-problem/>
- `[ 22]` [Business Insider] We asked our Gen Z and millennial reporters and editors about AI agents. Here's where they split.  
  <https://www.businessinsider.com/gen-z-millennials-ai-agents-thoughts-optimism-fears-2026-9>
- `[ 25]` [TechRadar] Bitdefender first to launch free 'temporary' VPN for AI Agents because they're worth it — but you can only use it on Apple M-series Macs for now  
  <https://www.techradar.com/pro/bitdefender-first-to-launch-free-temporary-vpn-for-ai-agents-because-theyre-worth-it-but-you-can-only-use-it-on-apple-m-series-macs-for-now>
- `[ 18]` 🔓 [Macworld] Best iPhone 2026: Every iPhone compared  
  <https://www.macworld.com/article/228816/best-iphone-pro-max-duo-ranked.html>
- `[ 25]` [Android Authority] Some Pixel owners are still missing alarms because of a years-old Clock bug  
  <https://www.androidauthority.com/google-pixel-clock-alarm-bug-not-fixed-yet-3715371/>
- `[ 27]` 🔓 [The Verge] Meta is making a standalone Muse AI gadget  
  <https://www.theverge.com/tech/999750/muse-charm-meta-ai-hardware>
- `[ 29]` [Business Insider] Meta is bringing its Muse AI agent to its glasses  
  <https://www.businessinsider.com/meta-muse-ai-agent-smart-glasses-2026-9>
- `[ 25]` [PyTorch] From Research Project to Open Source Ecosystem: Bring Your Academic PyTorch Project to PyTorchCon NA  
  <https://pytorch.org/blog/from-research-project-to-open-source-ecosystem-bring-your-academic-pytorch-project-to-pytorchcon-na/>
- `[ 24]` [Business Insider] OpenAI wants you to 'blurt out your thoughts' to your phone  
  <https://www.businessinsider.com/openai-boosts-chatgpt-voice-mode-mobile-web-app-2026-9>
- `[ 20]` [TechRadar] ChatGPT got GPT-6, but you can't use it in Chat — confused?  
  <https://www.techradar.com/ai-platforms-assistants/chatgpt/chatgpt-got-gpt-6-but-you-cant-use-it-in-chat-confused-its-time-we-talked-about-the-difference-between-chat-and-work>
- `[ 27]` [Toms Guide] Trump wants to call AI ‘Super Intelligence’ because ‘artificial’ sounds fake — but that’s not even what superintelligence means  
  <https://www.tomsguide.com/ai/trump-wants-to-rebrand-ai-as-super-intelligence-heres-what-that-actually-means>

### 🔴 🌍 Climate & Energy

- **Articles**: 36 (36 scored)
- **Score**: avg 44.9 | min 10 | max 65
- **Stale** (>48h): 32
- **Avg age**: 83.8h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ████                   4
  20–29   │ ██                     2
  30–39   │ █████                  5
  40–49   │ ███████                6
  50–59   │ ████████████████████  17
  60–69   │ ██                     2
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| New Atlas | 4 | 11% |
| Mother Jones | 3 | 8% |
| InsideEVs | 3 | 8% |
| Scientific American | 2 | 6% |
| Popular Mechanics | 2 | 6% |
| TechRadar | 2 | 6% |
| Forbes Innovation | 2 | 6% |
| Kagi Small Web | 2 | 6% |

**Low-score articles (≤30):**

- `[ 20]` [Farmonaut] Climate Change And Farm Resilience  
  <https://news.google.com/rss/articles/CBMiV0FVX3lxTE9EbFYzQ0NWMVNEWEQ3UlVSRkI4VnVvRHFsVzBmVS1rVDhPa0dPM1I4QWRPMk54YkFaTWVTZENUbDVRUGVOOENnMmJ3dUJYRjBIb1luaTBNbw?oc=5>
- `[ 25]` [TechRadar] A EV truck with a TV built into a front trunk for tailgating? Ford wants to patent the idea  
  <https://www.techradar.com/vehicle-tech/hybrid-electric-vehicles/fords-upcoming-fathom-ev-truck-could-have-a-tailgating-friendly-frunk-shelf-so-you-can-put-an-actual-tv-on-there-to-watch-sports-outdoors-at-least-fords-applied-for-a-patent-on-the-idea>
- `[ 15]` [New Atlas] Gorgeous retro rally concept reinvents a legendary piece of wizardry  
  <https://newatlas.com/automotive/renault-legendary-r8-electric-rally-coupe-concept/>
- `[ 12]` [Kagi Small Web] there&rsquo;s a new(ish) dinosaur museum in my hometown which they built because there were a bunch of&hellip;  
  <https://transfemme-shelterdog.tumblr.com/post/828649852945793024>
- `[ 18]` [Kagi Small Web] A new commitment: sharing highlights of my upcoming book here  
  <https://joshuaspodek.com/a-new-commitment-sharing-highlights-of-my-upcoming-book-here>
- `[ 10]` 🔓 [Forbes Innovation] Far From A Hospital, Even A Deadly Outbreak May Go Undetected  
  <https://www.forbes.com/sites/johndrake/2026/09/23/far-from-a-hospital-even-a-deadly-outbreak-may-go-undetected/>

### 🟡 🏛️ Architecture & Design

- **Articles**: 35 (35 scored)
- **Score**: avg 49.5 | min 37 | max 70
- **Stale** (>48h): 30
- **Avg age**: 81.8h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ ██                     2
  40–49   │ ████████████████████  17
  50–59   │ ██████████████        12
  60–69   │ ███                    3
  70–79   │ █                      1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ArchDaily | 16 | 46% ⚠️ |
| Dezeen | 4 | 11% |
| Kagi Small Web | 3 | 9% |
| Canadian Architect | 2 | 6% |
| Architizer | 2 | 6% |
| Business Insider | 1 | 3% |
| Kottke.org | 1 | 3% |
| Popular Mechanics | 1 | 3% |

### 🔴 🏠 Homelab & DIY

- **Articles**: 32 (32 scored)
- **Score**: avg 44.6 | min 3 | max 62
- **Stale** (>48h): 27
- **Avg age**: 81.1h

**Score distribution:**
```
  0–9     │ ████                   2
  10–19   │ ██                     1
  20–29   │ ████████               4
  30–39   │ ██                     1
  40–49   │ █████████████████      8
  50–59   │ ████████████████████   9
  60–69   │ ███████████████        7
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Popular Woodworking | 8 | 25% |
| TechRadar | 4 | 12% |
| How-To Geek | 3 | 9% |
| XDA Developers | 3 | 9% |
| Hackster News | 3 | 9% |
| MakeUseOf | 2 | 6% |
| Kagi Small Web | 2 | 6% |
| Engineering – The GitHub Blog | 1 | 3% |

**Low-score articles (≤30):**

- `[ 23]` 🔓 [Popular Woodworking] The Splinter Report: September 25th  
  <https://www.popularwoodworking.com/editors-blog/the-splinter-report-september-25th/>
- `[ 20]` 🔓 [Popular Woodworking] Resilience and Return  
  <https://www.popularwoodworking.com/editors-blog/resilience-and-return/>
- `[  4]` [Wikipedia  - Recent changes [en]] Cartoon Network  
  <https://en.wikipedia.org/w/index.php?title=Cartoon_Network&diff=1376440321&oldid=1376383065>
- `[  3]` [Kagi Small Web] @plotbunnyfarm replied to your post &ldquo;If it&rsquo;s any help to anyone, here&rsquo;s how the&hellip;&rdquo;:  
  <https://vincentbriggs.tumblr.com/post/828602104281235456>
- `[ 22]` [Dezeen] Grid radiator by Elisa Ossino for Tubes  
  <https://www.dezeen.com/2026/09/23/grid-radiator-elisa-ossino-tubes-dezeen-showroom/>
- `[ 18]` [Kagi Small Web] An Interesting Investigation, More Boxes, and Jellyfin Is Back (Week 38, 2026)  
  <https://www.kylereddoch.me/notes/2026/week-38-2026/>
- `[ 22]` [ArchDaily] Frank Gehry - Illuminations  
  <https://www.archdaily.com/1185548/frank-gehry-illuminations>

### 🔴 🌾 Homestead & Hobby Farm

- **Articles**: 6 (6 scored)
- **Score**: avg 42.3 | min 15 | max 60
- **Stale** (>48h): 6
- **Avg age**: 67.4h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██████████             1
  20–29   │ ██████████             1
  30–39   │                        0
  40–49   │ ██████████             1
  50–59   │ ████████████████████   2
  60–69   │ ██████████             1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Hobby Farms | 4 | 67% |
| Farmonaut | 1 | 17% |
| RealAgriculture | 1 | 17% |

**Low-score articles (≤30):**

- `[ 15]` [Farmonaut] Fruit And Orchard Crops  
  <https://news.google.com/rss/articles/CBMiVEFVX3lxTE9CdkFEZm9tSEx4elVROTduMDdOdDFJWl9fM3g3WE50ZWVHRTMzaEcwclp1c0xQQjI0OXpmdHZlNGR6NE9tWmF2N1lkcFFpaGZmVERKaQ?oc=5>
- `[ 22]` [Hobby Farms] 5 Fall Flowers That Bloom Late Into Autumn  
  <https://www.hobbyfarms.com/fall-flowers-bloom-late-into-autumn/>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 37 (37 scored)
- **Score**: avg 82.1 | min 67 | max 92
- **Stale** (>48h): 27
- **Avg age**: 76.1h
- **Local-flagged**: 37

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │                        0
  60–69   │ ██                     3
  70–79   │ ██████                 7
  80–89   │ ████████████████████  23
  90–100  │ ███                    4
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 16 | 43% ⚠️ |
| My Cariboo Now | 14 | 38% |
| Cariboo Signals Reviews | 1 | 3% |
| Pique Newsmagazine | 1 | 3% |
| Quesnel Cariboo Observer | 1 | 3% |
| The Tyee | 1 | 3% |
| Tom's Hardware | 1 | 3% |
| BC Wildfire Service | 1 | 3% |

### 🟡 📰 General News

- **Articles**: 60 (60 scored)
- **Score**: avg 69.9 | min 53 | max 76
- **Stale** (>48h): 51
- **Avg age**: 82.8h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │                        1
  60–69   │ ████████              17
  70–79   │ ████████████████████  42
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| TechRadar | 8 | 13% |
| WIRED | 7 | 12% |
| The Atlantic | 6 | 10% |
| The Tyee | 5 | 8% |
| Hackaday | 4 | 7% |
| Mother Jones | 3 | 5% |
| Scientific American | 3 | 5% |
| NYT Top Stories | 2 | 3% |

### 🔴 🥾 Outdoors & Recreation

- **Articles**: 7 (7 scored)
- **Score**: avg 30.7 | min 15 | max 50
- **Stale** (>48h): 5
- **Avg age**: 74.7h

**Score distribution:**
```
  0–9     │                        0
  10–19   │ ██████████             1
  20–29   │ ████████████████████   2
  30–39   │ ████████████████████   2
  40–49   │ ██████████             1
  50–59   │ ██████████             1
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Outside Online | 3 | 43% |
| Kagi Small Web | 2 | 29% |
| New Atlas | 1 | 14% |
| phys.org | 1 | 14% |

**Low-score articles (≤30):**

- `[ 15]` [Kagi Small Web] Go West Young Man  
  <https://thestrollingbones.blogspot.com/2026/09/go-west-young-man.html>
- `[ 22]` [New Atlas] 16-sec stackable camp box jumping-jacks into a solo or group cookery  
  <https://newatlas.com/outdoors/16-sec-modular-chuk-box/>
- `[ 20]` [Kagi Small Web] Oakland, California trip report  
  <https://philip.greenspun.com/blog/2026/09/22/oakland-california-trip-report/>

### 🟡 🔬 Science

- **Articles**: 51 (51 scored)
- **Score**: avg 52.7 | min 34 | max 60
- **Stale** (>48h): 42
- **Avg age**: 79.2h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │ █                      2
  40–49   │ █████                 10
  50–59   │ ████████████████████  38
  60–69   │                        1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| ScienceDaily | 17 | 33% |
| ScienceAlert | 5 | 10% |
| Scientific American | 4 | 8% |
| New Atlas | 3 | 6% |
| Popular Mechanics | 3 | 6% |
| Neuroscience News | 2 | 4% |
| Quanta Magazine | 2 | 4% |
| Gizmodo | 2 | 4% |

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 9 (9 scored)
- **Score**: avg 19.1 | min 2 | max 56
- **Stale** (>48h): 8
- **Avg age**: 83.9h

**Score distribution:**
```
  0–9     │ ████████████████████   4
  10–19   │ █████                  1
  20–29   │ ██████████             2
  30–39   │                        0
  40–49   │ █████                  1
  50–59   │ █████                  1
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Kagi Small Web | 3 | 33% |
| Wikipedia  - Recent changes [en] | 2 | 22% |
| Reactor Magazine | 1 | 11% |
| Nautilus | 1 | 11% |
| Edge (GamesRadar) | 1 | 11% |
| Neowin | 1 | 11% |

**Low-score articles (≤30):**

- `[ 22]` [Reactor Magazine] Must Read Short Speculative Fiction: August 2026  
  <https://reactormag.com/must-read-short-speculative-fiction-august-2026/>
- `[  8]` [Kagi Small Web] Okay I have my drink and I&rsquo;m settled in and the results are clear  
  <https://rohirric-hunter.tumblr.com/post/828649643842928640>
- `[  5]` [Wikipedia  - Recent changes [en]] Roy del espacio  
  <https://en.wikipedia.org/w/index.php?title=Roy_del_espacio&diff=1376440380&oldid=1370468198>
- `[  2]` [Wikipedia  - Recent changes [en]] The Mask of Loki  
  <https://en.wikipedia.org/w/index.php?title=The_Mask_of_Loki&diff=1376437483&oldid=1354724207>
- `[ 20]` 🔓 [Edge (GamesRadar)] First Cyberpunk: Edgerunners season 2 teases a bloodbath ahead of another action-packed season  
  <https://www.gamesradar.com/entertainment/anime-shows/first-cyberpunk-edgerunners-season-2-teases-a-bloodbath-ahead-of-what-looks-to-be-another-action-packed-season/>
- `[  5]` [Kagi Small Web] whats the point of two men fucking with reproductive organs that evolved to fuck for the purpose of&hellip;  
  <https://jessaerys.tumblr.com/post/828473846317318145>
- `[ 11]` [Neowin] Stardock announces roguelike deckbuilder Empire in Decay  
  <https://www.neowin.net/news/stardock-announces-roguelike-deckbuilder-empire-in-decay/?utm_source=rss>

### 🟡 🌿 Health & Wellness

- **Articles**: 66 (66 scored)
- **Score**: avg 57.7 | min 26 | max 75
- **Stale** (>48h): 57
- **Avg age**: 83.2h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ █                      2
  30–39   │ ██                     3
  40–49   │ █████                  8
  50–59   │ ██████████████        20
  60–69   │ ████████████████████  28
  70–79   │ ███                    5
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| STAT News | 6 | 9% |
| ScienceDaily | 6 | 9% |
| Neuroscience News | 5 | 8% |
| ScienceAlert | 4 | 6% |
| Nautilus | 4 | 6% |
| Being Patient | 3 | 5% |
| Fast Company | 3 | 5% |
| Science-Based Medicine | 3 | 5% |

**Low-score articles (≤30):**

- `[ 27]` [Toms Guide] Eight Sleep launches Pod 6 smart mattress cover with 20% faster cooling and next-gen biometric tracking — sleep apnea detection coming  
  <https://www.tomsguide.com/wellness/sleep-tech/eight-sleep-pod-6-launch>
- `[ 26]` [Dezeen] Parsons researchers warn of plastic toxicity in American manufactured homes  
  <https://www.dezeen.com/2026/09/22/parsons-plastic-toxicity-american-manufactured-homes/>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (15)

- **[🤖 AI/ML & Tech]** `score 18` — Best iPhone 2026: Every iPhone compared  
  Issue: `clickbait`  
  <https://www.macworld.com/article/228816/best-iphone-pro-max-duo-ranked.html>
- **[🤖 AI/ML & Tech]** `score 20` — ChatGPT got GPT-6, but you can't use it in Chat — confused?  
  Issue: `clickbait`  
  <https://www.techradar.com/ai-platforms-assistants/chatgpt/chatgpt-got-gpt-6-but-you-cant-use-it-in-chat-confused-its-time-we-talked-about-the-difference-between-chat-and-work>
- **[🤖 AI/ML & Tech]** `score 27` — Trump wants to call AI 'Super Intelligence' because 'artificial' sounds fake — but that's not even what superintelligence means  
  Issue: `clickbait`  
  <https://www.tomsguide.com/ai/trump-wants-to-rebrand-ai-as-super-intelligence-heres-what-that-actually-means>
- **[🌍 Climate & Energy]** `score 38` — Bentley's Torcal EV is its quickest car ever, with a polarizing design  
  Issue: `clickbait`  
  <https://newatlas.com/automotive/bentley-torcal-ev-suv-design/>
- **[🌍 Climate & Energy]** `score 36` — Wedged glass & huge wings: Saudi Arabia's 1st EV brand makes a stir  
  Issue: `clickbait`  
  <https://newatlas.com/automotive/saudi-arabia-ev-brand-ceer-exobot-sedan-suv/>
- **[🌍 Climate & Energy]** `score 25` — A EV truck with a TV built into a front trunk for tailgating? Ford wants to patent the idea  
  Issue: `clickbait`  
  <https://www.techradar.com/vehicle-tech/hybrid-electric-vehicles/fords-upcoming-fathom-ev-truck-could-have-a-tailgating-friendly-frunk-shelf-so-you-can-put-an-actual-tv-on-there-to-watch-sports-outdoors-at-least-fords-applied-for-a-patent-on-the-idea>
- **[🌍 Climate & Energy]** `score 15` — Gorgeous retro rally concept reinvents a legendary piece of wizardry  
  Issue: `clickbait`  
  <https://newatlas.com/automotive/renault-legendary-r8-electric-rally-coupe-concept/>
- **[🌍 Climate & Energy]** `score 18` — A new commitment: sharing highlights of my upcoming book here  
  Issue: `clickbait`  
  <https://joshuaspodek.com/a-new-commitment-sharing-highlights-of-my-upcoming-book-here>
- **[🏠 Homelab & DIY]** `score 23` — The Splinter Report: September 25th  
  Issue: `clickbait`  
  <https://www.popularwoodworking.com/editors-blog/the-splinter-report-september-25th/>
- **[🏠 Homelab & DIY]** `score 20` — Resilience and Return  
  Issue: `clickbait`  
  <https://www.popularwoodworking.com/editors-blog/resilience-and-return/>
- **[🏠 Homelab & DIY]** `score 18` — An Interesting Investigation, More Boxes, and Jellyfin Is Back (Week 38, 2026)  
  Issue: `clickbait`  
  <https://www.kylereddoch.me/notes/2026/week-38-2026/>
- **[🥾 Outdoors & Recreation]** `score 15` — Go West Young Man  
  Issue: `clickbait`  
  <https://thestrollingbones.blogspot.com/2026/09/go-west-young-man.html>
- **[🥾 Outdoors & Recreation]** `score 20` — Oakland, California trip report  
  Issue: `clickbait`  
  <https://philip.greenspun.com/blog/2026/09/22/oakland-california-trip-report/>
- **[🚀 Sci-Fi & Culture]** `score 20` — First Cyberpunk: Edgerunners season 2 teases a bloodbath ahead of another action-packed season  
  Issue: `clickbait`  
  <https://www.gamesradar.com/entertainment/anime-shows/first-cyberpunk-edgerunners-season-2-teases-a-bloodbath-ahead-of-what-looks-to-be-another-action-packed-season/>
- **[🌿 Health & Wellness]** `score 27` — Eight Sleep launches Pod 6 smart mattress cover with 20% faster cooling and next-gen biometric tracking — sleep apnea detection coming  
  Issue: `duplicate`  
  <https://www.tomsguide.com/wellness/sleep-tech/eight-sleep-pod-6-launch>

---

## Recommendations

- 🕐 **🤖 AI/ML & Tech** has 83 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌍 Climate & Energy** has 32 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏛️ Architecture & Design** has 30 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏛️ Architecture & Design** is dominated by **ArchDaily** (16 articles, 46%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **🏠 Homelab & DIY** has 27 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌾 Homestead & Hobby Farm** has 6 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 27 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 📊 **🏔️ Williams Lake Local** is dominated by **Williams Lake Tribune** (16 articles, 43%) — consider lowering `max_per_source` or adding a per-type cap in `config/source_preferences.json`.
- 🕐 **📰 General News** has 51 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🥾 Outdoors & Recreation** has a low average score (30.7) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🔬 Science** has 42 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (19.1) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🚀 Sci-Fi & Culture** has 8 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🌿 Health & Wellness** has 57 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 15 article(s) should be removed (`clickbait` ×14, `duplicate` ×1) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 11 feeds · 436 articles · 2026-09-27 17:46 UTC_
