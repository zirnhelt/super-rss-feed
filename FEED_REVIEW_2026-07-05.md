# Feed Scoring & Scrubbing Report

_Generated: 2026-07-05 14:51 UTC_

## Executive Summary

| Metric | Value |
|--------|-------|
| Feeds reviewed | 8 |
| Total articles | 393 |
| Stale articles (>48h) | 286 |
| Scrub pass | ✅ ran |
| Flagged for removal | 6 |
| Scoring model | dimensional Q/R/L composite |


_Note: content_type filtering (fluff/sponsored hard-drop) runs before publication, so those types are absent from feed JSONs by design. The `_score` field here reflects the composite score (0.25·Q + 0.55·R + 0.20·L)._


## Feed Summary

| Feed | Articles | Avg Score | Score Range | Stale | Top Source |
|------|----------|-----------|-------------|-------|------------|
| 🤖 AI/ML & Tech | 45 | 🔴 19.9 | 1–75 | 36 | Business Insider (6) |
| 🌍 Climate & Energy | 16 | 🔴 13.9 | 1–43 | 13 | New Atlas (2) |
| 🏠 Homelab & DIY | 13 | 🔴 26.9 | 0–76 | 9 | How-To Geek (5) |
| 🏔️ Williams Lake Local | 16 | 🟢 79.6 | 20–90 | 12 | Williams Lake Tribune (6) |
| 📰 General News | 222 | 🟡 65.2 | 41–85 | 153 | Al Jazeera English (37) |
| 🔬 Science | 22 | 🔴 14.1 | 0–59 | 15 | EarthSky (2) |
| 🚀 Sci-Fi & Culture | 11 | 🔴 22.7 | 1–69 | 9 | Reactor Magazine (3) |
| 🌿 Health & Wellness | 48 | 🔴 35.0 | 9–74 | 39 | New Atlas (9) |

---

## Per-Feed Detail

### 🔴 🤖 AI/ML & Tech

- **Articles**: 45 (45 scored)
- **Score**: avg 19.9 | min 1 | max 75
- **Stale** (>48h): 36
- **Avg age**: 68.8h

**Score distribution:**
```
  0–9     │ ████████████████████  25
  10–19   │ █████                  7
  20–29   │                        1
  30–39   │ ██                     3
  40–49   │ ██                     3
  50–59   │ █                      2
  60–69   │                        1
  70–79   │ ██                     3
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Business Insider | 6 | 13% |
| Quartz | 4 | 9% |
| TechCrunch | 3 | 7% |
| Android Authority | 3 | 7% |
| Engadget | 3 | 7% |
| Toms Guide | 2 | 4% |
| MacRumors | 2 | 4% |
| CNET | 2 | 4% |

**Low-score articles (≤30):**

- `[  3]` [The Marginalian] The Pain in You and the God in You: Carl Jung on the Relationship Between Psychological Suffering and Creativity  
  <https://www.themarginalian.org/2026/07/04/carl-jung-neurosis-creativity/>
- `[  3]` [TechCrunch] What is Mistral AI? Everything to know about the OpenAI competitor  
  <https://techcrunch.com/2026/07/04/what-is-mistral-ai-everything-to-know-about-the-openai-competitor/>
- `[  2]` [Daniele Messi. — Writing] Ethical AI Agents 2026: Bias Mitigation &amp; Responsible Development  
  <https://daniele-messi.com/en/blog/ethical-ai-agents-2026-bias-mitigation-responsible-development/>
- `[  1]` [Toms Guide] Is AI male or female? I went looking for the answer — and it completely changed how I think about ChatGPT  
  <https://www.tomsguide.com/ai/is-ai-male-or-female-i-went-looking-for-the-answer-and-it-completely-changed-how-i-think-about-chatgpt>
- `[  5]` [Kagi Small Web] ECM Special VIII: John Abercrombie  
  <https://ecmreviews.com/2026/07/03/ecm-special-viii-john-abercrombie/>
- `[  5]` [MacRumors] iPhone 18 With 9GB RAM Still Won't Support Two New iOS 27 Features  
  <https://www.macrumors.com/2026/07/03/iphone-18-wont-support-two-ios-27-features/>
- `[  6]` [Boing Boing] No AI for Al. "Weird Al" Yankovic yanks AI commercial  
  <https://boingboing.net/2026/07/03/no-ai-for-al-weird-al-yankovic-yanks-ai-commercial.html>
- `[  4]` [Quartz] OpenAI is buying a cloud startup to supercharge its AI coding tool  
  <https://qz.com/openai-acquires-ona-cloud-startup-codex-061126>
- `[  8]` [Quartz] Florida is suing OpenAI and Sam Altman, making it the first state to target the company over AI safety  
  <https://qz.com/florida-sues-openai-sam-altman-chatgpt-safety-060126>
- `[  3]` [Business Insider] Target eliminated a daily headache for drive-up workers with a new tech fix  
  <https://www.businessinsider.com/target-removed-a-drive-up-worker-frustration-with-tech-fix-2026-7>
- `[  2]` [Toms Guide] These 3 ChatGPT prompts helped me conquer my gaming backlog — and gave me a summer playlist to enjoy  
  <https://www.tomsguide.com/ai/these-3-chatgpt-prompts-helped-me-conquer-my-gaming-backlog-and-gave-me-a-summer-playlist-to-enjoy>
- `[  4]` [Android Authority] Gemini’s Error 1099 is locking users out, but this unofficial fix could help  
  <https://www.androidauthority.com/google-gemini-error-1099-fix-3684008/>
- `[ 15]` [Hackaday] Chain-of-Thought Spoofing Targets Reasoning AI Models  
  <https://hackaday.com/2026/07/02/chain-of-thought-spoofing-targets-reasoning-ai-models/>
- `[  6]` [CNET] Darren Aronofsky's '1776' AI Video Series Is Unhinged, and I Can't Look Away  
  <https://www.cnet.com/tech/services-and-software/darren-aronofsky-on-this-day-1776-ai-series-midseason-review/>
- `[  6]` [Business Insider] Alexandr Wang says Meta's coming AI has caught up with OpenAI's flagship model  
  <https://www.businessinsider.com/meta-ai-model-catches-up-openai-gpt-5-says-2026-7>

### 🔴 🌍 Climate & Energy

- **Articles**: 16 (16 scored)
- **Score**: avg 13.9 | min 1 | max 43
- **Stale** (>48h): 13
- **Avg age**: 72.6h

**Score distribution:**
```
  0–9     │ ████████████████████  10
  10–19   │ ████                   2
  20–29   │ ██                     1
  30–39   │ ██                     1
  40–49   │ ████                   2
  50–59   │                        0
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| New Atlas | 2 | 12% |
| Kagi Small Web | 2 | 12% |
| Resilience.org | 2 | 12% |
| NYT Business | 2 | 12% |
| Quartz | 1 | 6% |
| NYT Top Stories | 1 | 6% |
| InsideEVs | 1 | 6% |
| The Narwhal | 1 | 6% |

**Low-score articles (≤30):**

- `[  5]` [New Atlas] Honda's adorable $25K kei car heads westward  
  <https://newatlas.com/automotive/honda-super-n-launched/>
- `[ 20]` [Kagi Small Web] Mathew Cappucci: Americans “Uncomfortable with Science”  
  <https://thinc.blog/2026/07/03/mathew-cappucci-americans-uncomfortable-with-science/>
- `[  6]` [Quartz] Do solar panels in space produce way more power? Here's the math behind the claim  
  <https://qz.com/space-solar-panels-8x-power-claim-math-061526>
- `[  8]` 🔓 [NYT Top Stories] Burger vs. Bratwurst: A Climate Guide to Your July 4 Cookout  
  <https://www.nytimes.com/2026/07/03/upshot/hamburger-beef-july4-climate-guide.html>
- `[  5]` [Resilience.org] Nebraska soil, mid-east oil: Geopolitical crisis exposes the fragility of industrial farming and the case for rebuilding food systems  
  <https://www.resilience.org/stories/2026-07-03/nebraska-soil-mid-east-oil-geopolitical-crisis-exposes-the-fragility-of-industrial-farming-and-the-case-for-rebuilding-food-systems/>
- `[ 12]` [InsideEVs] BYD Reclaimed The EV Sales Crown Despite Tesla's Huge Quarter  
  <https://insideevs.com/news/800489/byd-tesla-ev-crown-quarter/>
- `[  1]` [TechCrunch] Rivian raises EV sales forecast as Q2 production ramps up  
  <https://techcrunch.com/2026/07/02/rivian-thinks-it-will-sell-more-evs-than-expected-this-year/>
- `[  7]` 🔓 [NYT Business] Jaguar’s Electric Future: Curves Are Out, and Blunt Is In  
  <https://www.nytimes.com/2026/07/02/business/jaguar-electric-cars.html>
- `[  5]` [Resilience.org] What change of power in Colombia could mean for world’s fossil-fuel transition  
  <https://www.resilience.org/stories/2026-07-02/qa-what-change-of-power-in-colombia-could-mean-for-worlds-fossil-fuel-transition/>
- `[  6]` Pluralistic: The difference between "today's task" and "accretive work" (02 Jul 2026)  
  <https://pluralistic.net/2026/07/02/canonization/>
- `[  4]` [ScienceDaily] Climate scientist who “proved” humanity is warming Earth says government report got it wrong  
  <https://www.sciencedaily.com/releases/2026/06/260625060214.htm>
- `[ 13]` [The Guardian Global Development] ‘Witch-hunt’ in Niger as military regime rounds up LGBTQ+ population  
  <https://www.theguardian.com/world/2026/jul/01/witch-hunt-in-niger-as-military-regime-rounds-up-lgbtq-population>
- `[  9]` 🔓 [NYT Business] BMW Will Build a New Electric S.U.V. in South Carolina  
  <https://www.nytimes.com/2026/06/30/business/bmw-electric-vehicles-south-carolina.html>

### 🔴 🏠 Homelab & DIY

- **Articles**: 13 (13 scored)
- **Score**: avg 26.9 | min 0 | max 76
- **Stale** (>48h): 9
- **Avg age**: 75.6h

**Score distribution:**
```
  0–9     │ ████████████████████   6
  10–19   │ ██████                 2
  20–29   │                        0
  30–39   │                        0
  40–49   │                        0
  50–59   │ ██████████             3
  60–69   │ ███                    1
  70–79   │ ███                    1
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| How-To Geek | 5 | 38% |
| Daniele Messi. — Writing | 2 | 15% |
| Kagi Small Web | 1 | 8% |
| Hackaday | 1 | 8% |
| XDA Developers | 1 | 8% |
| Lifehacker | 1 | 8% |
| LoRaMeshDevices | 1 | 8% |
| Make Magazine | 1 | 8% |

**Low-score articles (≤30):**

- `[  3]` [Kagi Small Web] Welcome! Introduce yourself  
  <https://linuxcommunity.io/t/welcome-introduce-yourself/6712?page=45#post_904>
- `[ 10]` Hackaday Podcast Episode 376: Modern Retro Projects, Retro Modern Projects, and the Teen Years for 3D Printing  
  <https://hackaday.com/2026/07/03/hackaday-podcast-episode-376-modern-retro-projects-retro-modern-projects-and-the-teen-years-for-3d-printing/>
- `[  8]` [How-To Geek] 3 hilariously pointless Home Assistant projects to try this weekend (Jul 3-5)  
  <https://www.howtogeek.com/home-assistant-projects-to-try-this-weekend-jul-3-5/>
- `[  0]` [XDA Developers] Home Assistant 2026.7 just killed the steep learning curve for building automations  
  <https://www.xda-developers.com/home-assistant-2026-07-update/>
- `[  5]` [How-To Geek] Home Assistant gets a big update that fixes three everyday smart home headaches  
  <https://www.howtogeek.com/home-assistant-gets-a-big-update-that-fixes-three-everyday-smart-home-headaches/>
- `[  7]` [How-To Geek] This simple home assistant trick fixed my biggest Wi-Fi annoyance  
  <https://www.howtogeek.com/control-your-home-network-with-your-voice/>
- `[  7]` [Lifehacker] 10 Hacks Every Apple Home User Should Know  
  <https://lifehacker.com/tech/best-hacks-every-apple-home-user-should-know?utm_medium=RSS>
- `[ 10]` [Make Magazine] Instant Prints! OpenCAL Layerless 3D Printing  
  <https://makezine.com/projects/instant-prints-opencal-layerless-3d-printing/>

### 🟢 🏔️ Williams Lake Local

- **Articles**: 16 (16 scored)
- **Score**: avg 79.6 | min 20 | max 90
- **Stale** (>48h): 12
- **Avg age**: 74.5h
- **Local-flagged**: 16

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │ ██                     1
  30–39   │ ██                     1
  40–49   │                        0
  50–59   │                        0
  60–69   │                        0
  70–79   │                        0
  80–89   │ ████████████████████   9
  90–100  │ ███████████            5
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Williams Lake Tribune | 6 | 38% |
| My Cariboo Now | 6 | 38% |
| 100 Mile Free Press | 3 | 19% |
| The Tyee | 1 | 6% |

**Low-score articles (≤30):**

- `[ 20]` 🔓 [Williams Lake Tribune] Dominion Day celebrations return to Barkerville for 158th year  
  <https://wltribune.com/2026/07/02/dominion-day-celebrations-return-to-barkerville-for-158th-year/>

### 🟡 📰 General News

- **Articles**: 222 (222 scored)
- **Score**: avg 65.2 | min 41 | max 85
- **Stale** (>48h): 153
- **Avg age**: 62.6h

**Score distribution:**
```
  0–9     │                        0
  10–19   │                        0
  20–29   │                        0
  30–39   │                        0
  40–49   │ █████                 24
  50–59   │ ████████████          50
  60–69   │ ████████████          50
  70–79   │ ████████████████████  81
  80–89   │ ████                  17
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Al Jazeera English | 37 | 17% |
| NYT Top Stories | 19 | 9% |
| Williams Lake Tribune | 14 | 6% |
| Global News | 14 | 6% |
| Boing Boing | 14 | 6% |
| Pique Newsmagazine | 13 | 6% |
| Quartz | 12 | 5% |
| Business Insider | 12 | 5% |

### 🔴 🔬 Science

- **Articles**: 22 (22 scored)
- **Score**: avg 14.1 | min 0 | max 59
- **Stale** (>48h): 15
- **Avg age**: 62.5h

**Score distribution:**
```
  0–9     │ ██████████████████     9
  10–19   │ ████████████████████  10
  20–29   │                        0
  30–39   │ ██                     1
  40–49   │ ██                     1
  50–59   │ ██                     1
  60–69   │                        0
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| EarthSky | 2 | 9% |
| TechRadar | 2 | 9% |
| Kagi Small Web | 2 | 9% |
| New Atlas | 1 | 5% |
| OpenMedia | 1 | 5% |
| ScienceAlert | 1 | 5% |
| Quartz | 1 | 5% |
| Business Insider | 1 | 5% |

**Low-score articles (≤30):**

- `[ 10]` [EarthSky] Thank you Guy Ottewell, and happy 90th birthday!  
  <https://earthsky.org/human-world/guy-ottewell-astronomical-calendar-companion/>
- `[ 10]` [New Atlas] Plasma jet is captured in 'most detailed X-ray view ever'  
  <https://refractor.io/space/plasma-jet-nasa/>
- `[ 11]` [TechRadar] 'Advances in quantum research and development have shifted the risk horizon': Microsoft says it is ramping up its quantum computing security work  
  <https://www.techradar.com/pro/security/advances-in-quantum-research-and-development-have-shifted-the-risk-horizon-microsoft-reveals-it-is-ramping-up-its-quantum-computing-security-work>
- `[  4]` Reports | OpenMedia  
  <https://openmedia.org/reports>
- `[ 13]` [ScienceAlert] Physicists Simulated a Black Hole in a Lab. Then It Started to 'Evaporate'.  
  <https://www.sciencealert.com/physicists-simulated-a-black-hole-in-a-lab-then-it-started-to-evaporate>
- `[  0]` [Kagi Small Web] Synthesis is harder than analysis  
  <https://surfingcomplexity.blog/2026/07/03/synthesis-is-harder-than-analysis/>
- `[  7]` [Quartz] Elizabeth Warren urged the SEC to delay SpaceX's IPO before its Nasdaq debut  
  <https://qz.com/elizabeth-warren-sec-spacex-ipo-delay-061026>
- `[  3]` [EarthSky] Top 10 cool things about stars that you probably didn’t know  
  <https://earthsky.org/space/10-cool-things-about-stars/>
- `[  8]` [Business Insider] Brands smell blood in the water after PlayStation axes game discs — and they're roasting Sony for it  
  <https://www.businessinsider.com/sony-digital-shift-playstation-games-spurs-online-backlash-jokes-2026-7>
- `[ 13]` [ZDNet] Considering plug-in solar at home? Electrical experts say to watch for these 6 safety risks  
  <https://www.zdnet.com/article/plug-in-solar-poses-6-safety-risks-say-industry-groups-when-to-call-a-pro/>
- `[ 13]` [TechCrunch] Boeing-owned Wisk Aero accused of firing manager who raised safety concerns  
  <https://techcrunch.com/2026/07/02/boeing-owned-wisk-aero-accused-of-firing-manager-who-raised-safety-concerns/>
- `[ 14]` [TechRadar] 'I will quit buying games' — Sony is killing physical discs in 2028 and now unhappy fans are concerned about what it means for game ownership  
  <https://www.techradar.com/gaming/i-will-quit-buying-games-sony-is-killing-physical-discs-in-2028-and-now-unhappy-fans-are-concerned-about-what-it-means-for-game-ownership>
- `[  1]` [MacRumors] iPhone 18 Pro Could Use Qualcomm Modem in the US and C2 Elsewhere  
  <https://www.macrumors.com/2026/07/02/iphone-18-pro-could-use-qualcomm-modem-in-the-us/>
- `[ 12]` [Quanta Magazine] Astrophysicists Puzzle Over Webb’s New Universe  
  <https://www.quantamagazine.org/astrophysicists-puzzle-over-webbs-new-universe-20260702/>
- `[ 17]` [100 Mile Free Press] Empty Birch Avenue businesses a concern for council  
  <https://100milefreepress.net/2026/07/02/empty-birch-avenue-businesses-a-concern-for-council/>

### 🔴 🚀 Sci-Fi & Culture

- **Articles**: 11 (11 scored)
- **Score**: avg 22.7 | min 1 | max 69
- **Stale** (>48h): 9
- **Avg age**: 87.6h

**Score distribution:**
```
  0–9     │ ████████████████████   5
  10–19   │ ████████               2
  20–29   │                        0
  30–39   │ ████                   1
  40–49   │ ████                   1
  50–59   │ ████                   1
  60–69   │ ████                   1
  70–79   │                        0
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| Reactor Magazine | 3 | 27% |
| Kagi Small Web | 2 | 18% |
| CNET | 1 | 9% |
| MakeUseOf | 1 | 9% |
| Boing Boing | 1 | 9% |
| TechRadar | 1 | 9% |
| The Verge | 1 | 9% |
| CBC Arts | 1 | 9% |

**Low-score articles (≤30):**

- `[  1]` [CNET] A Private Eye With a Supernatural Secret? This Sci-Fi Noir Series Is an Absolute Must-See  
  <https://www.cnet.com/tech/services-and-software/collin-farrell-sugar-sci-fi-noir-apple-tv/>
- `[  1]` [MakeUseOf] The best fantasy series on HBO isn't the one everyone is talking about  
  <https://www.makeuseof.com/best-fantasy-series-hbo-house-of-the-dragon-knight-of-the-seven-kingdoms/>
- `[  7]` [TechRadar] Bosgame VTI-490 review: This mini PC packs in more power than expected and handled network editing like a workstation  
  <https://www.techradar.com/pro/bosgame-vti-490-mini-pc-review>
- `[  6]` [Kagi Small Web] Raiden (Amiga/Falcon) and Space Junk (Atari Falcon) Source Code  
  <https://www.gamesthatwerent.com/2026/07/raiden-space-junk-sources/>
- `[ 11]` [Reactor Magazine] Victoria Aveyard’s Tempest Picked Up for TV Adaptation Before Publication  
  <https://reactormag.com/victoria-aveyards-tempest-fantasy-adaptation/>
- `[  6]` [Kagi Small Web] Turks Fruit (1973, Paul Verhoeven)  
  <https://deeperintomovies.net/journal/archives/18714>
- `[ 17]` [The Verge] 007 First Light&#8217;s developer lays off staff but claims its next franchise will continue  
  <https://www.theverge.com/games/959713/io-interactive-project-fantasy-layoffs>

### 🔴 🌿 Health & Wellness

- **Articles**: 48 (48 scored)
- **Score**: avg 35.0 | min 9 | max 74
- **Stale** (>48h): 39
- **Avg age**: 76.0h

**Score distribution:**
```
  0–9     │ ███                    3
  10–19   │ ████████████████████  16
  20–29   │ █████                  4
  30–39   │ ██                     2
  40–49   │ ██████████             8
  50–59   │ ██████                 5
  60–69   │ ████████               7
  70–79   │ ███                    3
  80–89   │                        0
  90–100  │                        0
```

**Sources (top 8):**

| Source | Count | % of feed |
|--------|-------|-----------|
| New Atlas | 9 | 19% |
| STAT News | 6 | 12% |
| Boing Boing | 4 | 8% |
| Al Jazeera English | 3 | 6% |
| CFJC Today Kamloops | 2 | 4% |
| MacRumors | 2 | 4% |
| NYT Top Stories | 2 | 4% |
| Global News | 2 | 4% |

**Low-score articles (≤30):**

- `[  9]` [New Atlas] Three-in-one pill cuts heart failure hospitalizations by 60%  
  <https://refractor.io/heart-disease/three-in-one-pill-heart-failure-trial/>
- `[ 12]` [Kagi Small Web] July 3, 2026  
  <https://somethingpositive.net/2026/07/03/july-3-2026/>
- `[ 10]` [Boing Boing] 38 scientists want to ban "mirror life"  
  <https://boingboing.net/2026/07/03/38-scientists-want-to-ban-mirror-life.html>
- `[ 10]` The MacRumors Show: Latest iPhone 18 Pro Leaks and Rumors  
  <https://www.macrumors.com/2026/07/03/the-macrumors-show-latest-iphone-18-pro-rumors/>
- `[ 13]` [New Atlas] Hot dog warning ahead of US holiday sausage bonanza  
  <https://refractor.io/diet-nutrition/hot-dog-health-warning/>
- `[ 11]` [Al Jazeera English] Russia’s advance collapses in Ukraine, ‘40,000’ troops killed in June  
  <https://www.aljazeera.com/news/2026/7/3/russian-advance-collapses-in-ukraine-as-anxiety-rises-in-moscow?traffic_source=rss>
- `[  9]` [New Atlas] Unregulated peptides pose higher risks for women  
  <https://refractor.io/diet-nutrition/men-women-risks-unregulated-peptides/>
- `[ 13]` 🔓 [NYT Business] Will Late-Night TV Work on YouTube?  
  <https://www.nytimes.com/2026/07/03/business/media/youtube-julian-shapiro-barnum-late-night.html>
- `[ 10]` 🔓 [NYT Top Stories] Has the MAHA Movement Given Up?  
  <https://www.nytimes.com/2026/07/03/magazine/maha-movement-survival-rfk.html>
- `[ 10]` [New Atlas] Artificial sweeteners face growing scrutiny over long-term health risks  
  <https://refractor.io/diet-nutrition/artificial-sweeteners-gut-metabolism/>
- `[ 29]` 🔓 [NYT Well] Clusters of Severe Stomach Illness Reported Across the U.S.  
  <https://www.nytimes.com/2026/07/02/well/cyclospora-infection-united-states.html>
- `[ 13]` [TechRadar] ‘Back pain in the morning? Can't touch your toes?' —  An ergonomic expert shares tips to stay healthy if you're spending lots of time at your desk  
  <https://www.techradar.com/gaming/ergonomic-expert-shares-tips-to-stay-healthy-if-youre-spending-lots-of-time-at-your-desk>
- `[ 10]` [STAT News] STAT+: Roche drug sets new standard for KRAS-driven lung cancer  
  <https://www.statnews.com/2026/07/02/biotech-news-roche-drug-sets-new-standard-for-kras-driven-lung-cancer/?utm_campaign=rss>
- `[ 10]` [NPR Health News] The U.S. healthcare system is in crisis. A Supreme Court ruling could make things worse  
  <https://www.npr.org/2026/07/02/nx-s1-5878415/haitian-tps-healthcare-immigration-supreme-court>
- `[ 14]` [The Guardian Global Development] ‘I pray for a miracle’: the African women held for years in India’s detention centres  
  <https://www.theguardian.com/global-development/2026/jul/02/women-india-detention-migration-foreigners-trafficking-victims-african-refugees>

---

## Scrub Pass Findings

### 🗑️ Recommended for Removal (6)

- **[🤖 AI/ML & Tech]** `score 36` — Neon Buys 'Artificial,' a Film About OpenAI, After Amazon Dropped It  
  Issue: `celebrity`  
  <https://www.nytimes.com/2026/06/30/business/media/openai-movie-artificial-neon-amazon.html>
- **[🔬 Science]** `score 17` — Empty Birch Avenue businesses a concern for council  
  Issue: `duplicate`  
  <https://100milefreepress.net/2026/07/02/empty-birch-avenue-businesses-a-concern-for-council/>
- **[🚀 Sci-Fi & Culture]** `score 37` — Her Private Hell Trailer Will Make You Say "WTF?" (Complimentary)  
  Issue: `clickbait`  
  <https://reactormag.com/her-private-hell-trailer-sci-fi/>
- **[🚀 Sci-Fi & Culture]** `score 17` — 007 First Light's developer lays off staff but claims its next franchise will continue  
  Issue: `celebrity`  
  <https://www.theverge.com/games/959713/io-interactive-project-fantasy-layoffs>
- **[🌿 Health & Wellness]** `score 37` — Sketchy Rumor Claims Apple Watch Series 12 Could Introduce Sensor in Band  
  Issue: `clickbait`  
  <https://www.macrumors.com/2026/07/03/apple-watch-series-12-sensor-in-band/>
- **[🌿 Health & Wellness]** `score 34` — Turn's out RFK's carnivore diet is unhealthy. Who would have guessed?  
  Issue: `celebrity`  
  <https://boingboing.net/2026/07/01/turns-out-rfks-carnivore-diet-is-unhealthy-who-would-have-guessed.html>

---

## Recommendations

- ⚠️ **🤖 AI/ML & Tech** has a low average score (19.9) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🤖 AI/ML & Tech** has 36 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🌍 Climate & Energy** has a low average score (13.9) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🌍 Climate & Energy** has 13 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🏠 Homelab & DIY** has a low average score (26.9) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🏠 Homelab & DIY** has 9 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **🏔️ Williams Lake Local** has 12 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🕐 **📰 General News** has 153 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🔬 Science** has a low average score (14.1) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🔬 Science** has 15 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🚀 Sci-Fi & Culture** has a low average score (22.7) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🚀 Sci-Fi & Culture** has 9 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- ⚠️ **🌿 Health & Wellness** has a low average score (35.0) — consider tightening category rules or raising `min_claude_score` in `config/limits.json`.
- 🕐 **🌿 Health & Wellness** has 39 articles older than 48h — verify `feed_retention_days` in `config/limits.json` and that the workflow ran recently.
- 🗑️ 6 article(s) should be removed (`celebrity` ×3, `clickbait` ×2, `duplicate` ×1) — add matching keywords to `config/filters.json` blocked_keywords to prevent recurrence.

---

_Report generated by `score_scrub_report.py` · 8 feeds · 393 articles · 2026-07-05 14:51 UTC_
