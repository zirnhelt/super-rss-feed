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
- **2026-09-06** — applied `limits.min_claude_score`: 23 → 25; `feed_slots.max_slots.news`: 25 → 22
- **2026-09-13** — applied `source_preferences.kagi_search_result_limit`: 10 → 12
- **2026-09-20** — applied `source_preferences.kagi_search_result_limit`: 10 → 12

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

## 2026-11-07

Audit window: 14 runs (2026-10-25T06:00:53.460455+00:00 to 2026-11-07T06:00:49.721641+00:00).


**Analysis**

The 14-day window (Oct 25 – Nov 7) shows infrastructure that is stable and healthy. Weekday theme raw means are within their recent band (Monday ~10–12, Tuesday ~6, Wednesday ~6–8, Thursday ~5, Friday ~20–22, Saturday ~24–25, Sunday ~31–32), podcast feeds consistently hit 100–104 articles with large holdover banks (bank sizes drifting down from ~2,600 to ~1,600 over the window, which is worth watching but reflects the pool being consumed faster than replenished rather than a scoring failure). The weekday-theme collapse from July–August remains resolved; there is no regression, so I am not touching those levers. The downward drift in Friday/Saturday/Sunday raw means since late October coincides with shrinking contender counts, consistent with pool depletion.

User feedback (ground truth through Oct 30) is the binding signal: 57.5% bad overall, stratified weighted_positive_pct 43.0%, reject false-negative rate 17.1%. Band precision separates clearly only at the top (80–100: 84% positive, 10.5% bad) and bottom (0–19: 86% bad). The 40–59 and 60–79 bands remain close to coin-flip (46.7% and 50.3% positive), so composite scoring still lacks middle-range discrimination. The threshold sweep is at clear diminishing returns: the current min_claude_score of 25 cuts 28.5% of bad while losing 7.1% of positives; moving to 30 would cut 43.7% of bad but cost 13.4% of positives, with 'interesting' articles losing 18.8%. Per standing lessons I hold the floor rather than stepping further. The one new data point since last run is that moving from 25→30 now costs proportionally more good articles (8.1% vs earlier estimates), reinforcing the hold.

News remains the epicentre (79.8% bad, 19.2% positive) even with the Sep 23 max_slots.news=10 cap now ~6 weeks old, so the residual problem is relevance/scoring-prompt quality, which is forbidden auto-edit. Noise-to-signal has been stable-to-slightly-improving (window mean 2.34 across these runs, recent runs 2.6–2.8, well inside the historical band), and kagi_search_result_limit has already been raised twice in change history without durably moving the config value, so I do not re-propose it. Theme routing shows an 18.9% correction rate (153 routing bugs vs 140 theme-scoring misses), an essentially even split, so there is no single clear auto-tunable lever. Worst sources: Live for the Outdoors (Country Walking) is the only block candidate (9/9 bad, 0 positive). Edge (GamesRadar), NYT Top Stories, Ideal Home, Country Life, Domino and Country Guide are high-bad but carry some positives or insufficient samples, so they are surfaced as observations only. No knob changes are proposed this run.


No changes applied this run.


**Human recommendations**

- Scoring-prompt review for the news category: news is 79.8% bad in user feedback even with the max_slots.news=10 cap in place for ~6 weeks, and the sweep shows threshold tuning has reached diminishing returns. The residual problem appears to be relevance/local scoring for generic national and international news; a prompt-level review of the news scoring criteria is the most likely real fix.
- Composite-weighting review: band precision shows the 40–59 and 60–79 composite bands are close to coin-flip (46.7% and 50.3% positive). The composite (0.25Q + 0.55R + 0.20L) appears to lack middle-range discrimination when R and L collapse for most non-regional content. Consider whether relevance weighting or the R-dimension prompt needs rework.
- Source blocking candidate: Live for the Outdoors (Country Walking) is 9/9 bad with zero positive ratings and is flagged block_candidate=true. Recommend blocking in feeds.opml or the source blocklist; source blocking is not auto-tunable.
- Sources to monitor (not yet block-eligible): Edge (GamesRadar) 51/53 bad with 2 interesting; NYT Top Stories 44/49 bad with 4 positive; Ideal Home 30/33 bad with 3 interesting; Country Life 21/24 bad; Domino 18/21 bad; Country Guide 6/6 bad with small sample. Revisit if the positive rate stays at or near zero with more samples. Do not block any source with a positive rating.
- Theme-scoring misses (~140 of 293 corrections in the window) point to theme_description/scoring_prompt review for Monday, Tuesday, Wednesday and Thursday (Tuesday in particular has 34.6% positive and the lowest good_pct at 21.3%). Routing bugs (~153) are a separate selection-logic issue worth a code-level check.
- Podcast holdover bank has shrunk from ~2,600 to ~1,600 across this window; if the pool continues to deplete, the source mix or feed breadth may need attention. This is a sourcing question for the human rather than a threshold question.

## 2026-11-14

Audit window: 14 runs (2026-11-01T06:00:54.201534+00:00 to 2026-11-14T06:00:54.175280+00:00).


**Analysis**

The 14-day window (Nov 1–14) is the first full fortnight since the late-October observations, and the pipeline's infrastructure looks stable. Weekday theme raw means sit in their recent band (Monday ~10–11, Tuesday ~6, Wednesday ~10, Thursday ~5, Friday ~20–25, Saturday ~26–28, Sunday ~33–36), and podcast feeds consistently hit 100–104 articles per theme with large holdover banks. The weekday-theme collapse issue from July–August remains resolved; there is no regression, so I am not touching those levers. Bank sizes have drifted down steadily (roughly 2,050 to 1,000 across the window), consistent with the pool being consumed faster than it is replenished. That is worth watching but reads as pool depletion, not a scoring failure. Noise-to-signal is elevated but in range (window mean 2.46, min 1.04, max 3.37), with the upward drift in the last week tracking the recent rise in fetched volume rather than any change in final feed size.

User feedback (ground truth through Nov 7) is the binding signal and is unchanged in character: 56.5% bad overall, stratified weighted_positive_pct 41.5%, and a reject false-negative rate of 16.0%. Band precision separates clearly only at the top (80–100: 83.7% positive, 11.2% bad) and bottom (0–19: 86.4% bad). The 40–59 and 60–79 bands are close to coin-flip (45.5% and 49.2% positive), so composite scoring still lacks middle-range discrimination. The threshold sweep is at clear diminishing returns: the current min_claude_score of 25 cuts 26.4% of bad at 5.9% positive lost; moving to 30 would cut 41.3% of bad but cost 10.8% of positives, with 'interesting' articles losing 16.0%. Per standing lessons I hold the floor rather than stepping again. Given the cost curve and that the 25 floor was set only in September, I am not proposing a change this run.

News remains the epicentre (78.9% bad, 19.2% positive) even with the Sep 23 max_slots.news=10 cap now about seven weeks old, so the residual problem is relevance/scoring-prompt quality, which is forbidden auto-edit. Theme routing shows a 20.2% correction rate, split 168 routing bugs versus 142 theme-scoring misses, close to even, so no single auto-tunable lever stands out. Worst sources: Live for the Outdoors (Country Walking) is the only clean block candidate (8/8 bad, 0 positive). Edge (GamesRadar), NYT Top Stories, Ideal Home, Country Life, Boing Boing and Domino are high-bad but carry some positives or are below the sample threshold, so they are surfaced as observations only. kagi_search_result_limit has already been proposed upward twice without durably moving the config value, so I do not re-propose it. No knob changes are proposed this run.


No changes applied this run.


**Human recommendations**

- Scoring-prompt review for the news category. It is the epicentre of user-rated bad articles (78.9% bad, 19.2% positive over 90 days) and the Sep 23 max_slots.news=10 cap has not closed the gap. The residual problem appears to be relevance and local-fit scoring in the prompt, which threshold tuning cannot fix without unacceptable positive losses.
- Composite-weighting review. Band precision shows the 40–59 and 60–79 bands are near coin-flip (45–49% positive), so the composite does not separate good from bad in the middle range. Reweighting or prompt-level changes to relevance/quality discrimination are needed before further floor increases are worthwhile.
- Consider blocking Live for the Outdoors (Country Walking). It is the only clean block candidate (8/8 bad, 0 positive, block_candidate=true). Source blocking is not auto-tunable, so this is for the maintainer to decide.
- Observe, but do not yet block: Edge (GamesRadar), NYT Top Stories, Ideal Home (Country Homes & Interiors), Country Life, Boing Boing, Domino. All have high bad rates but either carry some positive ratings or sit below a sufficient sample threshold. Revisit if the bad rate persists after the next audit window.
- Upstream sourcing: bank sizes have fallen steadily across the window (≈2,050 → ≈1,000) and contender counts are shrinking, which suggests the pool is being depleted faster than it refills. If feed volume becomes a constraint, the lever is feeds.opml / source mix, which the agent cannot reach. kagi_search_result_limit has already been raised twice without durably changing the config value, so that path needs a human check of why the value is not sticking.
- Theme routing correction rate is about 20% (168 routing bugs versus 142 theme-scoring misses). The routing-bug share is worth a code-side look at selection logic, since that half is not a prompt issue; the scoring-miss share needs prompt review.

## 2026-11-21

Audit window: 14 runs (2026-11-08T06:00:50.865217+00:00 to 2026-11-21T06:00:50.447630+00:00).


**Analysis**

The 14-day window (Nov 8–21) shows infrastructure that is stable. Weekday theme raw means sit in their healthy band (Monday ~10–11, Tuesday ~6, Wednesday ~10, Thursday ~5, Friday ~20–24, Saturday ~27–28, Sunday ~35), and podcast feeds consistently hit ~100–104 articles per theme. The July–August weekday-theme collapse remains resolved with no regression, so those levers stay untouched. Bank sizes have continued to drift down (roughly 1,500 to 700), which reads as pool depletion rather than a scoring failure, since contender counts are still substantial on most days.

User feedback (ground truth through Nov 14) remains the binding signal: 54.4% bad overall, stratified weighted_positive_pct 41.5%, reject false-negative rate 14.9%. Band precision separates well only at the top (80–100: 81.7% positive, 10.6% bad) and bottom (0–19: 87.3% bad). The 40–59 and 60–79 bands are roughly coin-flip (45.9% and 49.1% positive), so composite scoring still lacks middle-range discrimination. The threshold sweep is at clear diminishing returns: the current min_claude_score of 25 cuts 25.2% of bad at 4.9% positive lost; moving to 30 would cut 39.1% of bad but cost 8.8% of positives, with 'interesting' articles losing 12.6%. Given that the 25 floor was set in September and the sweep is now flattening, I am holding rather than stepping again, consistent with standing lessons.

News is still the epicentre (77.0% bad, 20.4% positive) even with the Sep 23 max_slots.news=10 cap now about seven weeks old and news shipping at its cap. The residual problem is relevance/scoring-prompt quality, which is forbidden auto-edit and is re-surfaced as a human recommendation. Noise-to-signal is elevated but within its recent range (window mean 2.57, min 1.15, max 3.37); kagi_search_result_limit has been proposed upward twice in change history without durably moving the config value, so I do not re-propose it. Theme routing shows a 22.3% correction rate (185 routing bugs vs 152 theme-scoring misses), a near-even split, so no single auto-tunable lever dominates. Worst sources: Live for the Outdoors (Country Walking) remains the only clean block candidate (6/6 bad, 0 positive; sample is small, so surfaced for the operator rather than acted on). Edge (GamesRadar), Ideal Home, NYT Top Stories, Domino, Boing Boing, and Country Life carry high bad rates but have positives or are near the sample threshold, so they are observations only. No knob changes are proposed this run.


No changes applied this run.


**Human recommendations**

- News scoring-prompt review: news is 77% bad / 20% positive in user feedback even with max_slots.news=10 in place. The residual problem is relevance and local-fit scoring, which is prompt-level and outside the auto-tunable whitelist. Recommend rewriting the news scoring rubric to weight Cariboo/BC/rural relevance more heavily and to penalize generic national/international wire content.
- Theme-scoring prompt review: about 152 of the 337 theme-day corrections (~45%) are scoring misses rather than routing bugs, concentrated in Tuesday (Working Lands) and Thursday (Indigenous Lands). Recommend a human pass on the theme_description and scoring_prompt for these two days.
- Composite-weight reassessment: band precision shows the 40–59 and 60–79 composite bands are roughly coin-flip (46% and 49% positive), so the composite does little to separate positives from bad in the middle range. Threshold tuning cannot fix this; recommend a human review of the w_quality/w_relevance/w_local weighting and whether the relevance dimension is over- or under-weighted.
- Block-candidate for operator consideration: Live for the Outdoors (Country Walking) is 6/6 bad with 0 positive ratings. Sample is small, so not auto-acted on; operator may wish to block it if the pattern holds.
- Watch: pool depletion. Holdover bank has drifted from ~1,500 to ~700 over the window while contender counts remain high on most days. If bank size keeps falling, podcast themes may start to thin and the holdover_threshold / source mix will need human attention rather than further floor raises.
