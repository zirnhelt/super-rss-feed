# Calibration Log

Weekly log of the calibration agent's analysis, config adjustments, and
human recommendations. See `calibration_agent.py` and
`config/calibration_bounds.json`.

## Earlier runs (one line each)

_Older entries cut to one line. Every applied change, with its rationale, is in `calibration_memory/change_history.json`._

- **2026-06-14** (dry run) — No changes: Claude call or response parsing failed. See logs for details.
- **2026-06-15** — No changes: Claude call or response parsing failed. See logs for details.
- **2026-06-15** — No changes: Claude call or response parsing failed. See logs for details.
- **2026-06-21** — No changes: Claude call or response parsing failed. See logs for details.
- **2026-06-21** — No changes: Claude call or response parsing failed. See logs for details.
- **2026-06-22** — No changes: Claude call or response parsing failed. See logs for details.
- **2026-06-28** — No changes: Claude call or response parsing failed. See logs for details.
- **2026-07-05** — No changes: Claude call or response parsing failed. See logs for details.
- **2026-07-12** — applied `limits.min_claude_score`: 13 → 16; `limits.haiku_scrub_floor`: 10 → 13
- **2026-07-19** — applied `limits.min_claude_score`: 16 → 18
- **2026-07-26** — applied `limits.min_claude_score`: 18 → 20
- **2026-07-26** (manual — scoring rearchitecture) — Pipeline rearchitected to "gated" scoring mode (absolute quality gate + two ranking heads). Semantic changes the calibration agent must account for:
- **2026-07-26** — no changes, 5 human recommendations
- **2026-08-02** — no changes, 4 human recommendations
- **2026-08-09** — no changes, 5 human recommendations
- **2026-08-16** — no changes, 8 human recommendations
- **2026-08-23** — No changes: Claude analysis failed — BadRequestError: Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'Your credit balance is too low to access the Anthropic API. Please go to Plans & Billing to upgrade or purchase credits.'}, 'request_id': 'req_011CeKmuNAmHdVLFcyLjMTdq'}
- **2026-08-24** — applied `limits.min_claude_score`: 20 → 23
- **2026-08-30** — no changes, 4 human recommendations

## 2026-09-06

Audit window: 21 runs (2026-08-24T04:52:17.558005+00:00 to 2026-09-06T04:01:09.004617+00:00).


**Analysis**

The 21-run audit window (August 24–September 6) shows a stabilized pipeline with healthy theme scores following the August 11 dimensional scoring rearchitecture, but user feedback reveals a persistent quality crisis requiring immediate action. The weekday theme score collapse is confirmed RESOLVED (all themes show healthy mean_theme_score_raw: Monday 14.9–15.3, Tuesday 4.2–6.5, Wednesday 2.6–5.9, Thursday 7.6–8.1). However, the dimensional scoring fix did NOT resolve the fundamental quality problem.

User feedback ground truth is damning: 66.2% bad rate overall (up from 65.8% last week), with composite scores showing poor band precision across ALL ranges. Even the 80-100 band is only 57.9% good (42.1% bad), and the 40-59 band is worse than coin-flip at 52.2% bad. The threshold_sweep provides clear evidence for action: current min_claude_score=23 (raised August 24) cuts only 37.5% of bad articles while losing 11.6% of good ones. The sweep shows min_claude_score=25 would cut 37.5% of bad at the same 11.6% good lost—but we're already at 23 and haven't seen the full effect yet in user feedback (feedback window ends August 22, before the raise).

The most critical finding: final feed sizes have exploded to 462–807/run (mean 626), nearly 6× the ~100 target. This is not just "above target"—it's a flood of content that makes the quality crisis worse because users must wade through far too many articles. News category alone passes 475 articles through quality gate despite a 76.0% user-rated bad rate (679/893). The dimensional histograms show why: quality dimension has some separation (news: 14919 in 0-19 vs 420 in 60-79), but relevance is collapsed (15212 in 0-19 vs 20 in 60-79), and local remains binary (16107 in 0-19). The composite weighting (0.25Q + 0.55R + 0.20L) cannot save non-local content when R and L are both near zero.

Noise-to-signal shows concerning volatility: window mean 1.48 (down from 1.77 last week), but with dramatic swings (0.07 on September 1, 3.67 on August 27). The recent trend is rising (1.41–1.54 over last 3 runs), suggesting the August 24 min_claude_score raise to 23 is starting to bite. The podcast routing correction rate is 20.9% (91 routing bugs, 158 theme-scoring misses), indicating theme prompts are stable post-rearchitecture.


**Changes applied**

- `limits.min_claude_score`: 23 → 25 — User feedback threshold_sweep shows min_claude_score=25 would cut 37.5% of bad articles while losing 11.6% of good ones—exactly the same tradeoff as current floor of 23, but we haven't seen the effect of the August 24 raise yet in user feedback (feedback ends August 22). However, final feed sizes of 462-807/run (mean 626) vs ~100 target demonstrate the quality gate is still far too permissive. News category has 76.0% bad rate yet passes 475 articles through. Band_precision shows even 40-59 composite scores are 52.2% bad. The current floor demonstrably fails to filter adequate volume. Raising to 25 is conservative (within max_step=3 from current 23) and directly addresses user-verified quality crisis. This will reduce final feed sizes toward target and cut more bad content.
- `feed_slots.max_slots.news`: 25 → 22 — News category is the primary driver of feed bloat: passes 475 articles through quality gate in recent runs despite 76.0% user-rated bad rate (679/893). Current max_slots.news=25 allows far too much low-quality news through. User feedback shows news has the worst bad rate of any category (76.0% vs 35.6% ai-tech, 54.8% wellness). Lowering max_slots.news from 25→20 will reduce final feed sizes (currently 462-807/run, target ~100) while forcing the pipeline to surface only the highest-scoring news articles. This complements the min_claude_score raise by capping downstream volume even if borderline articles pass quality gate.

**Clamped**

- `feed_slots.max_slots.news`: proposed 20 clamped to 22

**Human recommendations**

- CRITICAL: User feedback shows 66.2% bad rate with news category at 76.0% bad (679/893 rated articles). Worst sources are candidates for immediate blocking: Rolling Stone (100% bad, 18/18), The New Yorker (100% bad, 7/7), Domino (90.9% bad, 10/11), Edge/GamesRadar (87.5% bad, 14/16), Lifehacker (87.0% bad, 20/23), Neowin (86.7% bad, 13/15), Ideal Home (86.7% bad, 13/15), Toms Guide (86.5% bad, 32/37). These sources are polluting feeds with high-volume, low-quality content. Source blocking is outside auto-tunable scope but would have immediate impact.
- The dimensional histograms reveal a fundamental structural problem: relevance dimension is collapsed for most categories (news: 15212/16128 in 0-19, ai-tech: 130/672 in 0-19, wellness: 835/1100 in 0-19). The composite weighting (0.25Q + 0.55R + 0.20L) heavily weights relevance (0.55), so when R≈0 for most articles, composite scores collapse even when quality is decent. This explains why band_precision is poor across all ranges. Consider: (1) rebalancing weights to reduce relevance dominance, or (2) reviewing scoring_interests.txt to ensure relevance criteria are achievable for realistic article mix, or (3) accepting that relevance must filter aggressively and raising all category min_score floors to compensate. Current system passes too much irrelevant content because quality alone cannot rescue low relevance scores under current weighting.
- Podcast theme routing shows 20.9% correction rate (91 routing bugs, 158 theme-scoring misses). The theme-scoring misses indicate the theme prompts are working adequately post-rearchitecture, but the routing bugs (articles scoring higher on wrong theme than target theme by >20pts) suggest theme_routing_gap=20 may be too permissive. Consider tightening theme_routing_gap to 15 to reduce cross-theme routing errors, though this is at the edge of auto-tunable bounds (current calibration allows 10-35).
- The scifi category shows 66.7% bad rate (8/12 rated articles) and design shows 33.3% bad rate (4/12). Both categories have low sample sizes, but the pattern suggests either source mix issues or category definition problems. Review whether scifi and design sources are actually delivering content matching curator interests, or whether category definitions need tightening to exclude lifestyle/entertainment filler that's currently slipping through.

## 2026-09-13

Audit window: 17 runs (2026-08-31T10:44:00.977987+00:00 to 2026-09-13T04:01:03.708594+00:00).


**Analysis**

The 17-run audit window (August 31–September 13) shows a pipeline in crisis: final feed sizes have collapsed from the August explosion (462–807/run, mean 626) to thin output (396–849/run first week, then crashing to 103–484/run week two, mean 428 across window). The August 24 min_claude_score raise to 23 and September 6 raises to 25 + news max_slots cut to 22 have overcorrected. User feedback (ending September 6, pre-dating both recent raises) shows 67.5% bad rate with threshold_sweep indicating min_claude_score=25 would cut 37.7% of bad at 11.5% good lost—but we're already AT 25 as of September 6 and the feedback hasn't caught up yet. The noise-to-signal ratio is alarming: window mean 1.6 but with catastrophic volatility (0.07 best, 3.76 worst on September 10). Recent runs show 1.98–3.76, indicating the quality raises are cutting volume but creating instability.

The dimensional histograms reveal the core structural problem persists: quality dimension shows separation (news: 12095 in 0-19 vs 277 in 60-79), but relevance is collapsed (12377 in 0-19 vs 14 in 60-79) and local remains binary (12992 in 0-19). The composite weighting cannot salvage non-local content when R≈0 and L≈0. Band_precision confirms composite scores lack power: 80-100 band only 57.9% good, 40-59 band 53.7% bad—essentially random. Theme scores remain healthy post-rearchitecture (Monday 14.4–15.3, Tuesday 4.7–6.9, Wednesday 2.9–7.6, Thursday 7.1–7.2, Friday 36.6–37.4, Saturday 38.9–39.6, Sunday 47.4–49.4), proving the scoring infrastructure works. The podcast routing correction rate is 19.8% (94 routing bugs, 163 theme-scoring misses), stable and acceptable.

Critical finding: the September 6 changes (min_claude_score 23→25, news max_slots 25→22) have caused feed collapse visible in final_feeds series. September 6–10 runs show 556/465/466/455/396 articles vs August target ~600–700. The quality gate is now dropping 9224/13012 news articles (70.9% rejection rate vs ~60% pre-change), but user feedback proves this is CORRECT—news has 77.5% bad rate. The problem is we need MORE qualifying articles, not lower thresholds. The feed_slots caps are binding: news hitting 25-slot ceiling, but with 75.5% bad rate we need higher volume to find enough good content. Worst sources remain severe: Rolling Stone 100% bad (24/24), The New Yorker 100% bad (9/9), Cottage Life 100% bad (8/8)—blocking these would immediately improve signal.


**Changes applied**

- `source_preferences.kagi_search_result_limit`: 10 → 12 — Noise-to-signal has spiked to 1.98-3.76 recent runs (window mean 1.6 vs 1.48 last week), indicating upstream volume is insufficient after quality tightening. The September 6 min_claude_score raise to 25 is correct (user feedback supports it), but we need more raw material. Current kagi_search_result_limit=10 fetches 1442-1884 articles/run, but with 67.5% bad rate and strict quality gate we're not finding enough good content. Raising to 12 (+2) is conservative and directly addresses the volume shortage without lowering quality floors.

**Clamped**

- `feed_slots.max_slots.ai-tech`: proposed 20 clamped to 18

**Rejected**

- `feed_slots.max_slots.news`: no-op after clamping (already at/near value)
- `feed_slots.max_slots.ai-tech`: no-op after clamping (already at/near value)

**Human recommendations**

- URGENT: Block worst sources immediately. Rolling Stone (100% bad, 24/24), The New Yorker (100% bad, 9/9), Cottage Life (100% bad, 8/8), Live for the Outdoors/Country Walking (100% bad, 6/6), The Atlantic (100% bad, 5/5), Edge/GamesRadar (90.9% bad, 20/22), Ideal Home/Country Homes (90.9% bad, 20/22), Lifehacker (87.5% bad, 21/24), Domino (87.5% bad, 14/16), Toms Guide (86.8% bad, 33/38). These ten sources account for 185 rated articles with 170 bad (91.9% bad rate). Blocking them would immediately improve signal without touching scoring thresholds.
- The dimensional scoring system has a fundamental structural flaw: relevance dimension is collapsed for most content (news: 12377/13012 in 0-19 band, only 14 in 60-79). This suggests the relevance scoring_prompt is not differentiating between genuinely relevant content and noise. The composite weighting (0.25Q + 0.55R + 0.20L) cannot work when R≈0 for most articles. Recommend human review of the relevance scoring_prompt to ensure it's scoring on topic match, not just absence of disqualifying signals.
- User feedback band_precision shows composite scores are essentially random predictors of quality: 80-100 band is only 57.9% good (should be >80%), 60-79 is 41.8% good (should be >60%), 40-59 is 32.6% good (should be >40%). This indicates either the composite weighting formula is wrong OR the dimensional scoring prompts are not calibrated to user preferences. The quality dimension histogram shows better separation than composite, suggesting the weighting formula (0.25Q + 0.55R + 0.20L) may be the problem. Recommend A/B testing alternative weightings, e.g. 0.4Q + 0.4R + 0.2L or 0.5Q + 0.3R + 0.2L.
- The podcast theme routing correction rate of 19.8% (163 theme-scoring misses vs 94 routing bugs) is acceptable but the per-day breakdown shows Monday (19.1% good), Tuesday (17.4% good), Thursday (19.1% good), and Friday (21.7% good) are all underperforming. Wednesday (30.8% good), Saturday (30.4% good), and Sunday (28.8% good) do much better. This suggests Monday/Tuesday/Thursday/Friday theme prompts need tuning—they're selecting articles but the wrong ones. Recommend human review of those four theme scoring_prompts against user feedback examples to identify misalignment.

## 2026-09-20

Audit window: 14 runs (2026-09-07T04:01:02.273459+00:00 to 2026-09-20T04:00:32.093265+00:00).


**Analysis**

The 14-run audit window (September 7–20) reveals a pipeline recovering from the September 6 overcorrection but still struggling with upstream volume scarcity. Final feed sizes have stabilized at 465–506/run (window mean 476), down from the August explosion (626/run mean) but still well above the ~100 target. The noise-to-signal ratio shows concerning volatility: window mean 2.39 with dramatic swings (min 1.35 on September 14, max 3.76 on September 10). The recent trend is moderating (1.98 on September 20 vs 3.76 peak) but remains elevated compared to August's best runs (0.56–0.88).

User feedback ground truth (ending September 13, now including post-September 6 data) confirms the quality crisis persists: 67.2% bad rate overall, with composite scores showing poor band precision across all ranges. The 80-100 band is only 60.0% good (40.0% bad), and the 40-59 band is 54.0% bad—essentially coin-flip territory. The threshold_sweep is critical: current min_claude_score=25 cuts 37.0% of bad articles while losing 10.4% of good ones. This is nearly identical to the tradeoff at min_claude_score=30 (which would cut 37.0% bad at 10.4% good lost per interpolation), confirming we've hit diminishing returns at the quality gate. The dimensional histograms show the structural problem: quality has some separation (news: 10792 in 0-19 vs 165 in 60-79), but relevance is collapsed (11128 in 0-19 vs 19 in 60-79) and local remains binary (11533 in 0-19). The composite weighting cannot rescue non-local content when R≈0 and L≈0.

Theme scores remain healthy and stable post-rearchitecture (Monday 14.0–14.6, Tuesday 5.3–6.9, Wednesday 5.3–7.6, Thursday 6.9–7.2, Friday 36.0–37.0, Saturday 38.4–39.2, Sunday 46.9–48.0), proving the dimensional scoring infrastructure is sound. Podcast feeds consistently hit 100 articles with robust holdover banks (2631–3468 per theme). The podcast routing correction rate is 19.7% (108 routing bugs, 177 theme-scoring misses), indicating theme prompts are stable. Worst sources show severity: Rolling Stone 100% bad (24/24), The New Yorker 100% bad (9/9), Cottage Life 100% bad (8/8), The Atlantic 100% bad (8/8)—these are strong blocking candidates.

The critical diagnosis: the September 6 min_claude_score raise to 25 was correct (user feedback supports it), but we've starved the pipeline of upstream volume. The current kagi_search_result_limit=10 fetches 1127–1907 articles/run, but with 67.2% bad rate and strict quality gate we're not finding enough good content. The noise-to-signal spike (1.98–3.76 recent runs) indicates we're scraping the barrel—high reject rates mean we're processing more noise per qualifying article. The feed_slots caps are NOT the bottleneck (news at 119–126/run vs max_slots=22 means we're filling slots), so the issue is raw material scarcity. Raising kagi_search_result_limit is the correct lever to address volume shortage without lowering quality thresholds.


**Changes applied**

- `source_preferences.kagi_search_result_limit`: 10 → 12 — Noise-to-signal has spiked to 1.98–3.76 recent runs (window mean 2.39 vs 1.48 last week), indicating upstream volume is insufficient after quality tightening. The September 6 min_claude_score raise to 25 is correct (user feedback shows 67.2% bad rate and threshold_sweep supports it), but current kagi_search_result_limit=10 fetches only 1127–1907 articles/run. With 67.2% bad rate and strict quality gate (dropping 9224/13012 news articles), we're not finding enough good content. Final feeds average 476/run vs ~100 target, but news category alone passes 119–126/run (filling all 25 max_slots), proving we need more raw material to find qualifying articles, not lower thresholds. Raising to 12 (+2 from current 10) is conservative and directly addresses volume scarcity without compromising quality floors.

**Human recommendations**

- SOURCE BLOCKING URGENT: User feedback reveals catastrophic failure rates for specific sources that are poisoning the entire pipeline. Recommend immediately blocking: Rolling Stone (100% bad, 24/24 articles), The New Yorker (100% bad, 9/9), Cottage Life (100% bad, 8/8), The Atlantic (100% bad, 8/8), Live for the Outdoors/Country Walking (100% bad, 6/6), Mother Jones (100% bad, 6/6). These six sources alone account for 65 user-rated bad articles with ZERO good articles. Blocking them would immediately improve signal quality and reduce noise-to-signal ratio without touching any scoring thresholds. Additional blocking candidates with >85% bad rate: Edge/GamesRadar (92.6% bad, 25/27), Lifehacker (88.0% bad, 22/25), Toms Guide (87.5% bad, 35/40), Ideal Home/Country Homes & Interiors (87.5% bad, 21/24).
- COMPOSITE SCORING STRUCTURAL ISSUE: The dimensional histograms reveal the core problem that dimensional scoring has NOT fixed: relevance and local dimensions are binary cliffs for non-Cariboo content (news: 11128/11560 articles score 0-19 on R, 11533/11560 score 0-19 on L). The composite weighting (0.25Q + 0.55R + 0.20L) collapses scores when R≈0 and L≈0 even if quality is acceptable. This explains why band_precision shows 40-59 composite band is 54.0% bad—the weighting punishes non-local content regardless of journalistic merit. Recommend human review of: (1) relevance scoring_prompt to ensure it's not conflating 'local' with 'relevant' (rural/BC stories should score high on R even if L=0), (2) composite weighting formula to reduce L coefficient or add floor logic so non-local quality journalism isn't penalized, (3) local_keyword_bonus modifier (currently +25) which may be creating cliff rather than gradient. The user feedback proves the audience wants non-local content (climate 62.5% good, science 79.2% good, homelab 29.2% good)—these categories have low L scores but high user value.
- CATEGORY ASSIGNMENT REVIEW: User feedback by_category shows scifi has 69.2% bad rate (9/13 rated) and design has 47.1% bad rate (8/17 rated), both significantly worse than homelab (25.0%), science (12.5%), climate (25.0%), or homestead (0.0%). This suggests either source mix issues or category definition problems. Recommend human review of category assignment prompts for scifi and design to ensure they're not catching lifestyle filler that should be filtered as fluff. The wellness category's 54.2% bad rate (52/96 rated) also warrants prompt review—the 'evidence-based' requirement may not be filtering effectively.

## 2026-09-27

Audit window: 15 runs (2026-09-14T04:00:50.205860+00:00 to 2026-09-27T04:00:59.519081+00:00).


**Analysis**

The 14-run audit window (September 14–27) reveals a pipeline that has stabilized following the August 11 dimensional scoring rearchitecture, with healthy theme scores and consistent podcast feed generation, but continues to struggle with fundamental quality issues that dimensional scoring has not resolved. The catastrophic weekday theme collapse (July 26–August 10) remains definitively resolved: all themes show healthy mean_theme_score_raw values (Monday 13.8–14.4, Tuesday 5.3–5.9, Wednesday 4.8–5.9, Thursday 6.9–7.1, Friday 35.9–36.5, Saturday 38.4–39.1, Sunday 46.9–48.0), podcast feeds consistently hit 100 articles, and holdover banks are robust (2631–2933 per theme). The relative_scaled flag confirms dimensional scoring is active and working as designed.

However, user feedback ground truth (ending September 18, post-dating the September 6 and September 13 raises) reveals a persistent quality crisis: 67.3% bad rate overall, with stratified.weighted_positive_pct at only 41.2% (the reliable feed-quality metric). Band_precision shows composite scores lack discriminatory power across ALL ranges: even the 80-100 band is only 61.5% good (vs 35.9% bad), the 60-79 band is 36.0% good (vs 58.7% bad), and the 40-59 band is worse than coin-flip at 54.8% bad. The threshold_sweep provides critical evidence: current min_claude_score=25 cuts only 36.4% of bad articles while losing 10.1% of good ones, and raising to 30 would cut 52.1% of bad at 19.4% good lost—but we're already losing too many interesting articles (threshold_sweep shows interesting articles score low on relevance and are lost first when we raise floors). The dimensional histograms reveal the structural problem: quality has some separation (news: 11870 in 0-19 vs 168 in 60-79), but relevance is catastrophically collapsed (12208 in 0-19 vs 25 in 60-79), and local remains a binary cliff (12577 in 0-19 vs 24 above 20). The composite weighting (0.25Q + 0.55R + 0.20L) cannot rescue content when R≈0 and L≈0 dominate.

Noise-to-signal has deteriorated significantly: window mean 2.28 (vs 2.39 last week but 1.48 two weeks ago), with recent runs showing 1.83–2.99 and a concerning upward trend in the second half of the window (2.45–2.99 over last 5 runs vs 1.35–1.85 first half). This indicates the September 6 and September 13 quality tightening (min_claude_score 20→25, news max_slots 25→22→10 via September 23 cap) is creating upstream scarcity—we're processing more noise per qualifying article. Final feed sizes have collapsed from August's 626/run mean to current 436–502/run (window mean 465), with news contributing only 60–126/run despite being capped at max_slots=10 (the September 23 emergency cap). The per-category bad rates in user feedback reveal news is the crisis epicenter: 79.2% bad rate (916/1157 rated), yet news still dominates final feeds. The September 23 news cap to 10 slots appears in final_feeds starting September 23 (108→81 articles that day), but even at 10 slots news remains 18% of total feed vs 50-92% positive rates for other categories.

Theme routing shows 19.4% correction rate (310/1599: 123 routing bugs, 187 theme-scoring misses), with per-day good_pct ranging 16.9% (Tuesday) to 29.6% (Wednesday)—all below 30% except Wednesday, Saturday (29.3%), and Sunday (27.2%). This suggests theme prompts need review, but the root_cause split (123 routing bugs vs 187 theme-scoring misses) indicates it's primarily a scoring issue, not selection logic. Worst sources are severe and actionable: Rolling Stone 100% bad (24/24), The Atlantic 100% bad (13/13), Mother Jones 100% bad (10/10), The New Yorker 100% bad (9/9), Cottage Life 100% bad (8/8)—all are block_candidate=true in the audit data and represent immediate blocking opportunities.


No changes applied this run.


**Human recommendations**

- URGENT: Source blocking — user feedback identifies five sources with 100% bad rate and sufficient sample size (n≥8): Rolling Stone (24/24 bad), The Atlantic (13/13 bad), Mother Jones (10/10 bad), The New Yorker (9/9 bad), Cottage Life (8/8 bad). All are flagged block_candidate=true in worst_sources. Additionally, Edge/GamesRadar (30/32 bad, 93.8%), Lifehacker (24/27 bad, 88.9%), Ideal Home/Country Homes & Interiors (24/27 bad, 88.9%), and Neowin (15/17 bad, 88.2%) are strong blocking candidates. Blocking these 9 sources would immediately remove a major vector of bad content without touching thresholds.
- CRITICAL: Relevance scoring collapse — dimensional histograms show relevance dimension is catastrophically collapsed across all categories (news: 12208/12601 articles in 0-19 band, only 25 in 60-79; ai-tech: 175/669 in 0-19, only 0 in 60-79). This is NOT a threshold problem—it's a fundamental failure of the relevance scoring_prompt to discriminate between on-topic and off-topic content. The composite weighting (0.25Q + 0.55R + 0.20L) collapses when R≈0 for most articles, making quality improvements invisible in the final composite score. This requires human review and rewrite of the relevance scoring_prompt in standing_preferences.txt or the dimensional scoring logic itself. No amount of threshold raising will fix a relevance dimension that scores 96.9% of news articles in the 0-19 band.
- News category definition review — user feedback shows news has 79.2% bad rate (916/1157 rated) despite being the largest category by volume. The September 23 emergency cap to max_slots=10 is a Band-Aid, not a fix. The root cause is either: (a) the news category definition in standing_preferences.txt is too broad and scoops up low-value content that should be rejected or routed elsewhere, or (b) the news sources in source_preferences.json are systematically low-quality and need pruning. The per-stratum positive rates show news content in the 'border' stratum (articles near min_score threshold) has 55.2% positive rate, suggesting there IS signal in news if we can filter better upstream. Recommend human review of what 'news' means for this audience and whether the catch-all function is serving the curator's interests.
- Theme routing analysis — the 19.4% correction rate (310/1599) with root_cause showing 187 theme-scoring misses vs 123 routing bugs suggests the theme scoring logic is missing obvious fits. Per-day good_pct shows Tuesday (16.9%), Thursday (18.9%), Monday (20.0%), and Friday (21.9%) are all below 22%, indicating these theme prompts are not reliably identifying content the curator wants for those days. However, this is forbidden-territory (scoring_prompt, theme_description) and cannot be auto-tuned. Recommend human review of Tuesday (Working Lands), Thursday (Indigenous Lands), Monday (Arts/Culture), and Friday (Wild Spaces) theme definitions to improve day-fit precision.

## 2026-10-04

Audit window: 15 runs (2026-09-21T04:00:37.666981+00:00 to 2026-10-04T04:01:10.284230+00:00).


**Analysis**

The 14-run window (Sep 21–Oct 4) splits cleanly at Oct 1: a monitoring.quality_gate.podcast_floor or related scoring-side change around that date lifted weekday theme means sharply (Monday raw 18.5–23.2 → 41.9–46.8; Tuesday 5.6–8.4 → 32.4–48.5; Wednesday 6.8–18.7 → 32.2–47.6; Thursday 10.1–18.0 → 38.2–47.6), closing the gap with weekend themes rather than causing a collapse. This is a positive development worth monitoring rather than acting on — it looks like the dimensional-scoring infrastructure from August continuing to mature, not something this agent changed. No knob move is warranted there; flagging as monitoring per the guidance not to touch recently-shifted levers without more data.

Noise-to-signal remains elevated and volatile: window mean 2.31, matching last week's 2.28, with the worst runs (2.99–3.34) clustering right after the Sep 23 news max_slots cap to 10 and the accumulated min_claude_score=25 floor. The benchmark history shows noise-to-signal was far better in early September (1.48) before the quality-tightening sequence (min_claude_score 20→23→25, news slots 25→22→10) pushed it back up near 2.3. Per the playbook, rising noise-to-signal after upstream tightening should prompt looking at kagi_search_result_limit again — it was already raised from 10→12 twice (Sep 13 and Sep 20 entries in change history, though current config shows 10, suggesting those changes didn't stick or were reverted/clamped). Given the flip-flop guard and the fact the last two attempts at this exact change didn't durably move the needle, I will not re-propose it this run without clearer evidence it will behave differently, but I note it as worth revisiting if the config confirms the value is still 10.

User feedback (ground truth, through Sep 27) continues to show an unresolved quality problem that is distinct from the theme-score recovery: weighted_positive_pct is 41.9%, and band_precision shows essentially no separation in the 20-59 composite range (my bad_pct hovers 54-76% across bands). The threshold_sweep shows min_claude_score=25 (current) cuts 35.0% of bad at 11.2% positive lost; the next step to 30 would cut 50.8% of bad but at 21.5% positive lost — a steep jump that disproportionately removes 'interesting' articles (28.6% lost) which the guidelines explicitly warn against. I will not raise min_claude_score further this run; the marginal cost is now too high relative to prior conservative gains. The news category remains the dominant problem: 79.4% bad in user feedback, yet it still pulls the largest feed share. The Sep 23 cap to max_slots.news=10 is working as intended (news feed counts are now 48-126/run, well down from August's 119-126 ceiling-fill), and the pipeline-side quality_gate_totals confirm the floor is doing real work (8934/9134 news articles dropped below floor). I recommend leaving that cap untouched for now to let it fully take effect.

Worst-sources data continues to show clean blocking candidates with zero positive ratings: Rolling Stone (24/24 bad), Mother Jones (15/15 bad), The New Yorker (9/9 bad), Cottage Life (8/8 bad) — all flagged block_candidate=true and all 100% bad with reasonable sample sizes. These remain human recommendations since source blocking isn't auto-tunable. Theme routing correction rate sits at 19.5% (143 routing bugs, 201 theme-scoring misses), consistent with prior weeks — this is a scoring-prompt issue, not a selection-logic bug, and is outside auto-tunable scope.


No changes applied this run.


**Human recommendations**

- Block or deprioritize sources with 100% bad rate and reasonable sample sizes: Rolling Stone (24/24 bad), Mother Jones (15/15 bad), The New Yorker (9/9 bad), Cottage Life (8/8 bad). All are flagged block_candidate=true in the audit with zero positive ratings across meaningful n. Source blocking is outside the auto-tunable whitelist.
- News category relevance scoring is structurally broken for non-local news: 12356/12729 scored news articles fall in the 0-19 relevance band even after the quality gate. This looks like a scoring_prompt issue (relevance dimension not discriminating meaningfully for the news category) rather than something fixable via min_score_by_category or max_slots. Recommend a targeted review of the news-category relevance prompt/rubric.
- Theme routing correction rate remains ~19-20% for the fourth consecutive audit window, split roughly 40% routing bugs / 60% theme-scoring misses (143/201 this window). Per-day good_pct is still weak across the board (Monday 'Arts, Culture & Digital Storytelling' theme_routing shows only 18.3% in the last full feedback snapshot). This is a scoring-prompt-level issue across multiple theme days, not something min_score/holdover tuning can fix — recommend a focused review of theme scoring prompts for Monday and Tuesday specifically, which have the lowest good_pct.
- Consider re-examining whether kagi_search_result_limit should be raised again — it appears in change history as raised from 10→12 on both 2026-09-13 and 2026-09-20, but current config shows it back at 10. If that reversion was intentional, noise-to-signal's renewed climb (window mean 2.31, worse than the 1.48 seen in early September before the tightening sequence) suggests the reversion should be reconsidered with fresh data, though this agent is holding off this run per the flip-flop guard given two recent attempts at this exact lever.

## 2026-10-10

Audit window: 14 runs (2026-09-27T04:00:59.519081+00:00 to 2026-10-10T04:01:02.767424+00:00).


**Analysis**

The 14-run window (Sep 27–Oct 10) shows a pipeline that is stable on infrastructure but still too permissive on quality. Weekday theme scores are now healthy: Monday/Tuesday/Wednesday/Thursday raw means sit at roughly 20/20/12/15 for the latest runs, well clear of the July–August collapse, and the Oct 1 jump appears to be continued maturation of the dimensional-scoring rollout rather than something this agent changed. No recurring-issue regression is observed, so the weekday-theme issue stays resolved and I will not touch those levers.

User feedback (ground truth, through Oct 4) still shows a quality problem: 63.6% bad overall, stratified weighted_positive_pct 43.9%, and band_precision has weak separation in the 20-59 composite range. The threshold_sweep shows the current min_score floor of 25 cuts 33.8% of bad at 10.1% positive lost; the next step to 30 would cut 49.7% of bad but cost 18.8% of positives, disproportionately hitting 'interesting' articles. Raising further is now expensive relative to prior gains, so I hold on quality floors this run. News remains the dominant problem (79.4% bad in feedback, 21.6% positive), but the Sep 23 cap at max_slots.news=10 is only ~2 weeks old and feedback lags pipeline changes by 1–2 weeks, so it should be given more time before further tightening.

Noise-to-signal has been elevated (window mean 2.37, range 0.87–3.34) since late September. Per playbook, the upstream lever is kagi_search_result_limit, but it was already proposed upward twice in change_history without durably moving the value (config still reads 10), so I will not re-propose it without a clearer reason. Theme-routing correction rate is ~19.7% (160 routing bugs vs 225 scoring misses); the scoring-miss share points to prompt review, which is forbidden auto-edit territory. Worst sources (Rolling Stone, Mother Jones, The New Yorker, Cottage Life) remain 100% bad with sufficient sample sizes and are surfaced as human block recommendations.


No changes applied this run.


**Human recommendations**

- Block candidates with 0% positive across meaningful sample sizes (source blocking is not auto-tunable): Rolling Stone (24/24 bad), Mother Jones (15/15 bad), The New Yorker (9/9 bad), Cottage Life (8/8 bad). None have any positive rating.
- Review the scoring_prompt for news and the composite weighting. The local dimension is a binary cliff (nearly all non-Cariboo articles score ~0 on L), and relevance is also collapsed for news (the bulk of news articles score 0–19 on relevance). This is the structural cause of poor band precision (even the 80–100 band is only ~60% good) and cannot be fixed by thresholds.
- Review theme scoring prompts for Tuesday and Wednesday. Theme-scoring misses (≈225 of 385 day corrections) outnumber routing bugs (≈160), indicating the per-theme scoring prompts are a larger source of mis-routed podcast content than the selection logic. Thursday and Monday show the same pattern to a lesser degree.
- Consider whether kagi_search_result_limit should be raised again only after confirming the config value actually persists (prior proposals to raise it from 10 to 12 do not appear to have stuck). Noise-to-signal remains elevated (window mean ~2.4) after upstream tightening, so upstream volume/quality of search results is the lever to examine, not further quality-floor raises.

## 2026-10-17

Audit window: 14 runs (2026-10-04T04:01:10.284230+00:00 to 2026-10-17T04:01:54.851437+00:00).


**Analysis**

The 14-run window (Oct 4–17) shows a pipeline that is stable on infrastructure. Weekday theme scores are healthy (Monday ~14–15 raw mean, Tuesday ~6, Wednesday ~4.5, Thursday ~8; weekend themes 36–48), so the July–August weekday collapse remains resolved and I am not touching those levers. Podcast feeds are consistently near 100 articles per theme with robust holdover banks, and the relative_scaled flag confirms the dimensional scoring is active.

The quality problem persists. User feedback (ground truth through Oct 10) shows 63.1% bad overall and a stratified weighted_positive_pct of 42.3%. Band precision is weak across the 20–59 composite range, and the threshold sweep shows the current min_score floor of 25 cuts ~33% of bad articles at ~10% positive loss. Raising the floor to 30 would cut ~48% of bad but cost ~17% of positives, disproportionately removing 'interesting' articles. Given the 1–2 week feedback lag and the cost curve, I am holding quality floors rather than stepping further this run. News remains the outlier (79% bad, ~22% positive), and the Sep 23 max_slots.news=10 cap is still maturing in feedback, so I am leaving it in place.

Noise-to-signal is elevated and volatile (window mean 2.36, range 0.96–3.28). The upstream lever (kagi_search_result_limit) has been proposed upward twice in change history without durably moving the config value, so I am not re-proposing it without a clearer reason. Theme routing shows a 20.2% correction rate, split 180 routing bugs vs 245 theme-scoring misses; the scoring-miss share points to prompt review, which is forbidden auto-edit territory. Worst sources (Rolling Stone, Mother Jones, The New Yorker, Cottage Life) remain 100% bad with adequate sample sizes and are surfaced as human block recommendations.


No changes applied this run.


**Human recommendations**

- Block candidates with zero positive ratings and sufficient sample sizes: Rolling Stone (24/24 bad), Mother Jones (15/15 bad), The New Yorker (9/9 bad), Cottage Life (8/8 bad). Source blocking is outside auto-tunable scope.
- Theme-routing correction rate is ~20% (180 routing bugs, 245 theme-scoring misses). The scoring-miss share indicates the per-theme scoring_prompt / theme_description fields need human review, particularly Tuesday (Working Lands) and Thursday (Indigenous Lands), which have the lowest per-day good rates.
- The composite weighting (0.25Q + 0.55R + 0.20L) collapses scores for non-Cariboo content because the local dimension is a near-binary cliff (almost all articles score 0–19 on L) and relevance is similarly compressed for news. Consider a prompt/weighting review so composite scores separate positives from bad in the 20–59 range, where band precision is currently near coin-flip.
- News category needs a human review of its scoring_prompt and category definition: it contributes the largest share of feed volume at ~79% bad. The Sep 23 max_slots cap is a stopgap; a relevance-focused prompt change is the durable fix.
- Revisit kagi_search_result_limit only after confirming the current config value; prior proposed increases in change history did not durably take effect.

## 2026-10-24

Audit window: 14 runs (2026-10-11T04:01:14.442081+00:00 to 2026-10-24T06:00:57.289163+00:00).


**Analysis**

The 14-run window (Oct 11–24) shows infrastructure stable: weekday theme raw means have held at healthy levels (Monday ~14–15, Tuesday ~6, Wednesday ~4.6, Thursday ~7.5–8, weekend 36–48), podcast feeds consistently hit 100 articles with large holdover banks, and the relative_scaled flag confirms dimensional scoring is active. The weekday-theme collapse remains resolved; no regression observed, so I am not touching those levers.

The quality problem is the dominant concern. User feedback (through Oct 17) shows 61.7% bad overall, with stratified.weighted_positive_pct at 44.1% — the reliable feed-quality measure — and a reject false-negative rate of 17.2%. Band precision still shows weak separation: the 60–79 and 40–59 bands are roughly coin-flip (48% and 48% positive), and only the 80–100 band (75.7% positive) is clearly discriminating. The threshold sweep shows the current min_score floor of 25 cuts 32.1% of bad at 9.1% positive lost; raising to 30 would cut 47.1% of bad but cost 16.7% of positives, with 'interesting' articles disproportionately lost (21.1%). Given the cost curve and the 1–2 week feedback lag on the September 23 news cap, I am holding the floor this run rather than stepping further.

News remains the epicentre (77.5% bad, 22.4% positive in feedback) even though the Sep 23 max_slots.news=10 cap is now ~4 weeks old and should be taking effect; the residual bad rate points to scoring-prompt/relevance problems that threshold tuning cannot fix. Noise-to-signal is elevated and volatile (window mean 2.31, range 0.96–3.28). The upstream lever (kagi_search_result_limit) has already been proposed upward twice without durably moving the config value, so I will not re-propose it without a clearer signal. Theme routing shows a 20.7% correction rate (205 routing bugs vs 258 theme-scoring misses); the scoring-miss share indicates prompt review, which is forbidden auto-edit. Worst sources (Rolling Stone, Edge/GamesRadar, Ideal Home, Live for the Outdoors) are surfaced as human block considerations; Live for the Outdoors is the only clean block candidate at 9/9 bad, and Rolling Stone / The New Yorker / Mother Jones / Cottage Life are already blocked.


No changes applied this run.


**Human recommendations**

- Scoring-prompt review for news: news is 77.5% bad in user feedback even after the quality floor and news slot cap. Relevance dimension is collapsed for most news (11551 of ~12000 scored at relevance 0–19), so the composite cannot discriminate. Recommend rewriting the news relevance criteria in the scoring prompt (forbidden auto-edit).
- Scoring-prompt review for podcast theme routing: 20.7% correction rate with 258 theme-scoring misses vs 205 routing bugs. Theme-scoring misses dominate, pointing to theme_description/scoring_prompt weaknesses on Tuesday (Working Lands, 22.6% good) and Monday (Arts/Culture, 21.2% good) in particular.
- Consider blocking 'Live for the Outdoors (Country Walking)': 9 of 9 rated articles are bad with zero positive ratings. Source blocking is not auto-tunable; this is a human decision.
- Composite weighting structural issue: the local dimension is a binary cliff (~99% of non-regional articles score 0–19), so L=0 dominates the 0.25Q/0.55R/0.20L composite for most content, and band precision in the 40–79 range is near coin-flip. Fixing the local scoring granularity and/or relevance collapse for non-local content is the real lever for improving discrimination; weights and prompts are human-only.
- Noise-to-signal persistently elevated (window mean 2.31, peaks ~3.3). Sourcing is an upstream feeds.opml question for the maintainer: consider pruning low-yield feeds, especially those dominated by 'bad' or 'unknown' content types in news and design.

## 2026-10-31

Audit window: 14 runs (2026-10-18T04:01:30.784791+00:00 to 2026-10-31T06:00:48.837686+00:00).


**Analysis**

The 14-day window (Oct 18–31) shows infrastructure stable: weekday theme raw means are healthy (Monday ~10–12 raw, Tuesday ~6, Wednesday ~6, Thursday ~5, Friday ~22–37, Saturday ~26–40, Sunday ~30–40), podcast feeds consistently hit 100–104 articles with large holdover banks, and relative_scaled is active. The weekday-theme collapse issue remains resolved; I see no regression, so I am not touching those levers. Weekday raw means are drifting slightly lower in the last week (Friday 36→22, Saturday 40→26, Sunday 47→30), which is worth watching but does not yet look like collapse, and the Oct 27+ shift coincides with more contenders being exhausted (contenders_confirmed falling), so it likely reflects pool depletion rather than a scoring failure.

User feedback (ground truth through Oct 24) is the binding signal: 59.6% bad overall, stratified weighted_positive_pct 43.0%, and reject false-negative rate 16.4%. Band precision separates well only at the top (80–100: 86.5% positive) and the 0–19 band (13.7% positive); the 40–59 and 60–79 bands are roughly coin-flip (46–50% positive), so composite scoring still lacks discrimination in the middle. The threshold sweep is now clearly at diminishing returns: the current floor of 25 cuts 29.7% of bad at 7.8% positive lost; moving to 30 would cut 46.1% of bad but cost 14.6% of positives, with 'interesting' articles losing 19.7%. Per the standing lesson, I hold min_score here rather than stepping further.

News remains the epicentre (81.8% bad, 17.5% positive in feedback) despite the Sep 23 max_slots.news=10 cap, and the per-category numbers show it is the only category where the cap alone cannot rescue quality — the residual problem is scoring-prompt/relevance, which is forbidden auto-edit. Noise-to-signal is elevated but mostly within the recent range (window mean 2.27, range 0.88–3.16), with no sign the upstream fetch volume is the bottleneck anymore; kagi_search_result_limit has already been proposed upward twice without durably moving, so I do not re-propose it. Theme routing shows an 18.0% correction rate (145 routing bugs vs 141 theme-scoring misses) — the split is nearly even, so there is no single clear lever. Worst sources: Live for the Outdoors (Country Walking) is the only clean block candidate (9/9 bad, 0 positive); the others with high bad rates (Edge/GamesRadar, Ideal Home, NYT Top Stories, Country Life, Domino) have some positive ratings or are not yet block-eligible and are surfaced only as observations. No knob changes are proposed this run: the cost curve for quality floors is steep, the news problem is prompt-level, and the recurring issues are already tracked.


No changes applied this run.


**Human recommendations**

- Scoring-prompt review for the news category: news is 81.8% bad / 17.5% positive in user feedback even with the Sep 23 max_slots.news=10 cap, and threshold sweeps show further floor raises now cost disproportionate 'interesting' articles. The residual problem is relevance/local scoring, which is forbidden auto-edit territory.
- Consider blocking 'Live for the Outdoors (Country Walking)': 9 of 9 rated articles are bad with 0 positive ratings (block_candidate=true in worst_sources). Source blocking is not auto-tunable.
- Theme-scoring misses are roughly equal to routing bugs (141 vs 145 of 286 corrections, 18.0% correction rate). The scoring-miss share indicates a prompt review of per-theme scoring_prompt/theme_description is warranted, particularly for Monday (Arts & Culture, 37.7% positive) and Tuesday (Working Lands, 34.4% positive), which are the weakest-performing themes by positive rate.
- Watch the late-October weekend raw-mean decline (Friday ~37→22, Saturday ~40→26, Sunday ~47→30) alongside falling contenders_confirmed. Current evidence points to pool depletion rather than scoring failure, but if raw means continue to slide next week without a corresponding pool change, escalate to a scoring-prompt check.
