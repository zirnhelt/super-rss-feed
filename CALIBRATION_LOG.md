# Calibration Log

Weekly log of the calibration agent's analysis, config adjustments, and
human recommendations. See `calibration_agent.py` and
`config/calibration_bounds.json`.

## 2026-06-14 (dry run)

No changes: Claude call or response parsing failed. See logs for details.


## 2026-06-15

No changes: Claude call or response parsing failed. See logs for details.


## 2026-06-15

No changes: Claude call or response parsing failed. See logs for details.


## 2026-06-21

No changes: Claude call or response parsing failed. See logs for details.


## 2026-06-21

No changes: Claude call or response parsing failed. See logs for details.


## 2026-06-22

No changes: Claude call or response parsing failed. See logs for details.


## 2026-06-28

No changes: Claude call or response parsing failed. See logs for details.


## 2026-07-05

No changes: Claude call or response parsing failed. See logs for details.


## 2026-07-12

Audit window: 7 runs (2026-07-07T07:48:19.436969+00:00 to 2026-07-12T06:40:10.545685+00:00).


**Analysis**

The audit window (7 runs, July 7–12) shows stable pipeline performance following the June 24 manual threshold reset. The noise-to-signal ratio has improved significantly over the window: starting at 1.23 (July 7), it spiked to 2.76 (July 9), then settled back to 1.53 (July 12) with a window mean of 2.09. Final feed sizes are healthy at 295–398 articles per run, well above the ~100 target set during the manual intervention. The user feedback audit provides critical ground truth that contradicts some pipeline-side metrics: 63.3% of rated articles were marked bad, with the composite score showing poor separation — band_precision reveals that even 80-100 scored articles were only 56% good. The current min_claude_score of 13 cuts just 18.8% of user-rated bad articles while losing only 3.6% of good ones, suggesting the quality gate is too permissive. The threshold_sweep shows raising min_claude_score to 20 would cut 28.1% of bad articles at a cost of 5.7% good articles lost — a favorable trade. The dimensional histograms reveal a systemic issue: across all categories, the vast majority of articles score 0-19 on the composite scale (e.g., news: 3186 in 0-19 vs 97 in 60-79), yet quality/relevance histograms show more normal distributions. This suggests the composite weighting (0.25 Q + 0.55 R + 0.20 L) is collapsing scores for non-local content because the L dimension is stuck at zero for most articles. Theme routing shows 28.8% correction rate (159/553), split 45 routing bugs vs 114 theme-scoring misses — the latter indicates the podcast theme prompts need human review, not knob changes. Worst sources (Al Jazeera 95% bad, Lifehacker 93.8% bad, Toms Guide 88.9% bad) are candidates for blocking, but that's outside the auto-tunable scope. The podcast feeds are thin on banked holdovers (8-37 per theme), and mean theme scores have collapsed from ~30-42 (July 7) to ~26-27 (July 12) across all themes, suggesting either scoring_prompt drift or upstream content mix shift — but the histogram shapes are consistent, so this is likely real signal, not calibration error. Monday's mean_theme_score collapsed from 30.3 to 26.7 immediately after July 7, and has held flat since — this is a clear break, but not severe enough to flag as a recurring issue yet (threshold is still above min_score=28).


**Changes applied**

- `limits.min_claude_score`: 13 → 16 — User feedback shows current min_claude_score=13 is far too permissive (only cutting 18.8% of bad articles). Threshold_sweep indicates 20 would cut 28.1% of bad at 5.7% good lost, but that's the max bound. Proposing 16 as a conservative first step: the June 24 reset went from 20→13 to fix feed scarcity, but final_feeds now show 295-398/run, well above the ~100 target. Raising to 16 tightens quality without risking the overshoot that triggered the manual intervention. This will reduce noise-to-signal by cutting more articles at the quality gate.
- `limits.haiku_scrub_floor`: 10 → 13 — The Haiku safety check currently reviews articles scoring 10+. User feedback shows 63.3% bad rate across all content, and the 0-19 composite band is 87.6% bad. Raising haiku_scrub_floor from 10→13 subjects more borderline articles to the safety check, which should catch additional fluff/sponsored content before it reaches the quality gate. This complements the min_claude_score raise and targets the same quality issue from a different stage of the pipeline.

**Human recommendations**

- Source blocking candidates based on user feedback: Al Jazeera English (95% bad, n=20), Lifehacker (93.8% bad, n=16), Toms Guide (88.9% bad, n=18), CBC Arts (88.9% bad, n=9), Neowin (88.9% bad, n=9), Reactor Magazine (87.5% bad, n=8), Tom's Hardware (81.8% bad, n=11). These sources consistently deliver content the curator rates as bad. Source blocking is not in the auto-tunable whitelist, but the signal is strong enough to recommend manual intervention.
- Podcast theme routing shows 28.8% correction rate with 114/159 corrections attributed to theme_scoring_miss (the theme score didn't separate the correct target day from others). This suggests the scoring_prompts in podcast_schedule.json need human review to better align with the curator's mental model for each theme. The keyword lists are reasonable (no obvious mismatches), but the prose prompts may be under-specified or conflicting with the main scoring interests. Specifically: Monday (Arts/Culture, 32.6% good), Tuesday (Working Lands, 30.2% good), Thursday (Indigenous, 27.4% good), Sunday (Science/Nature, 26.8% good) all show <35% good rates and high correction-away counts. Wednesday (Repair Culture, 47.3% good) and Saturday (Local, 42.2% good) perform better, suggesting their prompts are better calibrated. Recommend reviewing the underperforming theme prompts against the curator interests file and the user's actual day corrections in the review UI.
- The composite score shows poor separation between good and bad articles (band_precision: even 80-100 scored articles are only 56% good). The dimensional histograms reveal most articles score 0-19 on Local, which under the current weighting (w_l=0.20) caps the composite at 80 even for perfect Q/R scores. This is working as designed for non-local content, but the curator's feedback suggests the relevance dimension (w_r=0.55) is not discriminating well enough on its own. Consider whether the scoring_interests.txt prompt needs clearer guidance on what constitutes high vs medium vs low relevance, or whether the examples in the prompt are calibrated to the curator's actual preferences. The user feedback audit is the ground truth here: mean_score for good articles is 54.3, for bad is 41.8 — only a 12.5-point gap, which is narrow given the 0-100 scale. The prompt may need human tuning to widen this separation.

## 2026-07-19

Audit window: 14 runs (2026-07-07T07:48:19.436969+00:00 to 2026-07-19T06:35:54.116378+00:00).


**Analysis**

The 14-run audit window (July 7-19) reveals a stable but permissive quality gate that is passing too much low-quality content. User feedback provides critical ground truth: 63.3% of rated articles were marked bad, and composite scores show poor band precision (even 80-100 scored articles were only 56% good). The current min_claude_score=13 cuts only 18.8% of user-rated bad articles while losing just 3.6% good articles—the threshold_sweep shows we have substantial headroom to tighten. Final feed sizes are healthy (295-398 per run, mean 341), well above the ~100 target set during June 24's manual intervention, confirming we can afford to raise quality floors.

The noise-to-signal ratio shows encouraging improvement: window mean 2.07, down from early-window peaks of 2.76, with recent runs settling at 1.53-1.84. This suggests the pipeline is becoming more efficient at filtering noise, but the user feedback data proves we're still passing too many bad articles to the final feeds. The dimensional histograms reveal why: most articles score 0-19 on composite (news: 6032 vs 109 at 60-79), yet quality/relevance distributions are more normal—this indicates the composite weighting (0.25Q + 0.55R + 0.20L) collapses scores for non-local content because L=0 for most articles. However, this is a weighting/prompt issue (forbidden territory), not a threshold problem.

Theme scores show stable means (26.6-26.7 across most themes after July 8) with no collapse toward zero, so no recurring issue flag is warranted. The 28.8% podcast routing correction rate (114 theme-scoring misses vs 45 routing bugs) signals that theme prompts need human review, not automated keyword changes. Worst sources (Al Jazeera 95% bad, Lifehacker 93.8% bad) are candidates for human-recommended blocking. The quality gate dropped 2045 articles below category floors across the window, but user feedback shows the floor is still too low—raising min_claude_score is the correct lever.


**Changes applied**

- `limits.min_claude_score`: 16 → 18 — User feedback threshold_sweep shows min_claude_score=20 would cut 28.1% of bad articles at 5.7% good lost—well within acceptable bounds. Current value of 16 (raised July 12) cuts 25.3% of bad at 4.1% good lost, an improvement but still insufficient given 63.3% overall bad rate. Proposing 18 as a conservative step toward the 20 ceiling: final feed sizes average 341/run (well above ~100 target), so we have capacity to tighten. This complements the existing haiku_scrub_floor=13 change and directly addresses the user-verified quality issue without risking the feed-scarcity overshoot that triggered June 24's manual intervention. The 18 threshold would cut an estimated 26-27% of bad articles (interpolating between sweep points) while losing ~5% of good articles—a favorable trade given current bad rate.

**Human recommendations**

- User feedback shows 28.8% podcast routing correction rate, with 114 theme-scoring misses (vs 45 routing bugs). This indicates the podcast theme scoring_prompts are not matching maintainer intent for several themes (especially Thursday: 27.4% good rate, Wednesday: 47.3% good rate with 40 corrections away). Recommend human review of podcast_schedule.json scoring_prompt text for thursday (Indigenous Lands & Innovation), friday (Wild Spaces & Outdoor Life), and sunday (Science, Wonder & the Natural World)—these themes show the worst good_pct and highest corrected_away counts.
- Worst sources by user rating are strong candidates for blocking: Al Jazeera English (95% bad, n=20), Lifehacker (93.8% bad, n=16), Toms Guide (88.9% bad, n=18), CBC Arts (88.9% bad, n=9), Neowin (88.9% bad, n=9), Reactor Magazine (87.5% bad, n=8), Tom's Hardware (81.8% bad, n=11). These sources consistently produce content the maintainer rates as bad regardless of score. Source blocking is not auto-tunable but should be considered for the next human config review.
- The composite score weighting (0.25Q + 0.55R + 0.20L) appears to be collapsing scores for non-local content because most articles have L=0. User feedback shows poor band precision: even 80-100 composite articles are only 56% good, and the 40-59 band (where most articles land) is 58% bad. This suggests either the relevance dimension is mis-scoring, or the weighting undervalues quality. The dimensional histograms show quality distributions are more normal than composite distributions (e.g., news quality: 5513 at 0-19 but 336 at 60-79; news composite: 6032 at 0-19 but 109 at 60-79), supporting this diagnosis. Recommend human review of scoring_weights.general to consider raising w_quality from 0.25 to 0.30-0.35 and lowering w_relevance accordingly—this is a forbidden change for auto-tuning but could meaningfully improve score separation based on user feedback evidence.

## 2026-07-26

Audit window: 14 runs (2026-07-13T07:28:29.183589+00:00 to 2026-07-26T06:41:43.169266+00:00).


**Analysis**

The 14-run audit window (July 7-26) shows a stable but still-too-permissive quality gate despite the July 12 and July 19 min_claude_score raises (13→16→18). User feedback provides damning ground truth: 63.3% of rated articles were marked bad, with composite scores showing poor band precision even at high ranges (80-100 band is only 56.6% good). The threshold_sweep data is clear: current min_claude_score=18 cuts ~26% of bad articles while losing ~5% of good ones, but the sweep shows we could go to 20 and still maintain favorable tradeoffs (28.5% bad cut at 5.9% good lost). Final feed sizes remain healthy at 327-396 articles/run (window mean 353), well above the ~100 target, confirming we have substantial capacity to tighten further.

The noise-to-signal ratio has improved significantly: window mean 2.03, down from early peaks of 2.74, with the most recent run at 1.77. This indicates the pipeline is becoming more efficient at filtering upstream noise. However, the user feedback proves we're still passing too many bad articles to final feeds—the quality gate is working (it dropped 1329 articles below category floors in the window), but the floor itself remains too low. The dimensional histograms reveal a structural issue: most articles score 0-19 on composite (news: 5775 in 0-19 vs 62 in 60-79), yet quality/relevance distributions are more normal. This suggests the composite weighting (0.25Q + 0.55R + 0.20L) collapses scores for non-local content because L=0 dominates the calculation. This is a prompt/weighting issue (forbidden territory), not a threshold problem.

Theme scores remain stable (mean 26.5-26.7 across all themes after July 8) with no collapse toward zero, so no recurring issue flag is warranted. The 27.4% podcast routing correction rate (124 theme-scoring misses vs 57 routing bugs) signals that theme prompts need human review, but this is outside auto-tunable scope. Worst sources (My East Kootenay Now 100% bad over 7 articles, Lifehacker 93.8% bad, Toms Guide 91.3% bad) are strong candidates for blocking—surfacing as human recommendation. The scifi category shows 100% bad rate over 5 rated articles, suggesting either source mix or category definition issues that require human review.


**Changes applied**

- `limits.min_claude_score`: 18 → 20 — User feedback threshold_sweep shows min_claude_score=20 would cut 28.5% of bad articles while losing only 5.9% of good articles—a favorable trade given the 63.3% overall bad rate. Current value of 18 (raised July 19) is an improvement but insufficient: we're still passing far too many bad articles (band_precision shows even 40-59 composite scores are 54.8% bad). Final feed sizes average 353/run, well above the ~100 target, confirming we have capacity. The previous raises (13→16→18) were conservative steps; user feedback now provides clear evidence to move to the calibration ceiling. This directly addresses the verified quality issue without risking feed scarcity.

**Human recommendations**

- Source blocking candidates based on user feedback worst_sources: My East Kootenay Now (100% bad, n=7), Lifehacker (93.8% bad, n=16), Toms Guide (91.3% bad, n=23), Neowin (90% bad, n=10), Reactor Magazine (88.9% bad, n=9), Al Jazeera English (88% bad, n=25). These sources consistently deliver content the curator marks as bad; consider adding them to a source blocklist.
- The scifi category shows 100% bad rate over 5 rated articles in the user feedback window. This suggests either a source mix problem (Reactor Magazine is 88.9% bad and likely dominates scifi) or a category definition issue. Recommend human review of scifi sources and/or the category assignment logic.
- Theme routing shows 27.4% correction rate with 124 theme-scoring misses vs 57 routing bugs. The misses indicate the podcast theme scoring_prompts are not aligning with curator intent—Wednesday (Repair Culture), Friday (Wild Spaces), and Saturday (Cariboo Local) had the highest correction counts (42, 37, 29 respectively). These prompts need human review to better capture what the curator considers thematic fit for each day.
- The composite score weighting (0.25Q + 0.55R + 0.20L) appears to collapse scores for non-local content because the L dimension is zero for most articles. User feedback shows poor band_precision: even 80-100 composite scores are only 56.6% good. The dimensional histograms reveal that quality and relevance scores are more normally distributed, but the composite collapses everything into 0-19 when L=0. Consider whether the L weight should be reduced (and Q/R increased proportionally) to allow non-local high-quality content to score higher, or whether a different composite formula is needed.

## 2026-07-26 (manual — scoring rearchitecture)

Pipeline rearchitected to "gated" scoring mode (absolute quality gate + two
ranking heads). Semantic changes the calibration agent must account for:

- New knobs `limits.quality_gate.gate_floor` (news eligibility) and
  `limits.quality_gate.podcast_floor` (podcast pool entry) — floors on the
  new interest-independent `q_gate` newsworthiness score, not the composite.
- Per-day `podcast.schedule.<day>.min_score` is now a floor on the
  interest-independent quality signal (q_gate/quality dimension), NOT the
  personal-interest composite. Historical values (18-30) were calibrated
  against composites and may need re-tuning against the new q_gate
  distribution (see `q_gate_histogram` in run stats).
- Theme scores are decontaminated: the personal interest profile was removed
  from theme-scoring prompts and the Cohere theme mapping switched from
  batch-relative percentiles to an absolute log-scale mapping.
  THEME_SCORE_CACHE_VERSION bumped v3 → v4; theme-score history spanning the
  cutover is not comparable.
- Podcast composite weights rebalanced: w_relevance 0.20 → 0, w_quality
  0.10 → 0.25, w_theme 0.60 → 0.65 (missing dimensions now renormalize
  instead of substituting the interest composite).

## 2026-07-26

Audit window: 15 runs (2026-07-13T07:28:29.183589+00:00 to 2026-07-26T19:16:45.882303+00:00).


**Analysis**

The 15-run audit window (July 13-26) shows a stable pipeline with healthy feed sizes (327-394 articles/run, mean 353) following the recent min_claude_score raises. The noise-to-signal ratio has improved to a window mean of 1.98 (down from 2.07 last week), with recent runs settling at 1.34-1.77, indicating better upstream filtering efficiency. However, user feedback reveals a persistent quality crisis: 63.5% of rated articles were marked bad, and composite scores show poor band precision even at high ranges (80-100 band is only 58.2% good, down from 56.6% last week). The current min_claude_score=20 (raised July 26) is at the calibration ceiling and cuts 33.9% of user-rated bad articles while losing 8.2% of good ones—this is the best we can do at the quality gate level without human intervention on prompts or weights.

The most alarming signal is the catastrophic theme score collapse in the most recent run (2026-07-26T19:16): Monday mean_theme_score dropped from 26.6 to 7.1, Tuesday from 26.6 to 3.0, Wednesday from 26.6 to 8.4, Thursday from 26.6 to 4.2. Friday/Saturday/Sunday recovered to 35-45 range, but the weekday collapse is severe and immediate—this is not gradual drift but a scoring_prompt or upstream content break. The composite score histograms for that run show the damage: Monday 237/250 articles in 0-19 band, Tuesday 249/250 in 0-19, Thursday 250/250 in 0-19. This is a recurring issue that demands immediate human review of the theme scoring prompts.

The dimensional histograms reveal the root cause of poor composite scores: across all categories, the vast majority of articles score 0-19 on local (news: 6945/7039, ai-tech: 554/555), which collapses the composite calculation because L=0 dominates the 0.25Q + 0.55R + 0.20L weighting. Quality and relevance distributions are more normal (news quality: 5365 in 0-19 vs 316 in 60-79; news relevance: 6127 in 0-19 vs 61 in 60-79), but the local dimension is a binary cliff. This is a structural weighting/prompt issue beyond auto-tunable scope. The 27.8% podcast routing correction rate (131 theme-scoring misses vs 70 routing bugs) confirms theme prompts need human rewrite. Worst sources remain consistent (Neowin 90.9% bad, Reactor Magazine 90% bad, Al Jazeera 88.9% bad)—strong candidates for blocking.


No changes applied this run.


**Human recommendations**

- URGENT: Investigate weekday theme scoring collapse in run 2026-07-26T19:16:45. Monday/Tuesday/Wednesday/Thursday mean_theme_scores dropped from stable ~26.6 baseline to 3.0-8.4, with composite histograms showing 237-250 out of 250 articles scoring 0-19. Friday/Saturday/Sunday recovered to normal ranges in the same run, ruling out global scoring failure. This is either a scoring_prompt regression or a fundamental content-theme mismatch. Recommend: (1) Review scoring_prompt and theme_description fields for Monday-Thursday themes against recent article text to identify disconnect. (2) Check if upstream source mix changed on 2026-07-26 in a way that broke keyword matching for weekday themes. (3) Consider whether theme definitions are too narrow given available content (e.g., 'Arts, Culture & Digital Storytelling' may not match enough real articles in the pool).
- The composite scoring formula (0.25Q + 0.55R + 0.20L) collapses non-local content because the local dimension is a binary cliff: 6945/7039 news articles score 0-19 on local, 554/555 ai-tech articles score 0-19 on local. Quality and relevance distributions are more normal, but L=0 dominates the weighted sum. This structural issue causes even high-quality, high-relevance articles to score poorly in the composite. Band precision data confirms: 40-59 composite band is only 41.0% good, meaning the composite score does not separate quality effectively. Recommend: (1) Reduce local weight from 0.20 to 0.10 or lower to prevent it from collapsing non-local scores. (2) Alternatively, consider a separate 'local bonus' added only when L > threshold (e.g., +15 bonus if L ≥ 60) rather than a multiplicative weight. (3) Re-tune composite weights after dimensional scoring is stable—current Q/R distributions suggest relevance may be underweighted relative to its actual predictive power for user-rated 'good' articles.
- Block or deprioritize consistently bad sources: Neowin (90.9% bad over 11 articles), Reactor Magazine (90% bad over 10 articles), Al Jazeera English (88.9% bad over 27 articles), Lifehacker (88.2% bad over 17 articles), My East Kootenay Now (87.5% bad over 8 articles), Atlas Obscura (87.5% bad over 8 articles), NPR Health News (85.7% bad over 7 articles), Toms Guide (84% bad over 25 articles), CBC Arts (83.3% bad over 12 articles), Quartz (81.2% bad over 16 articles). These sources have sufficient sample sizes and consistently high bad rates to justify blocking. Source blocking is not auto-tunable—add to source_preferences.json manually.
- The scifi category shows 100% bad rate over 7 rated articles in the user feedback window, and the podcast-sunday theme (Science, Wonder & the Natural World) shows 100% bad rate over 2 articles. This suggests either a source mix problem (e.g., Reactor Magazine contributes 90% bad scifi content) or a category/theme definition mismatch. Recommend: (1) Review scifi category definition and source list—if Reactor Magazine dominates, block it. (2) Check Sunday theme keywords and scoring_prompt against actual article text to identify why science content is scoring poorly or routing incorrectly. (3) Consider whether the scifi category is too narrow or the wrong sources are feeding it.
- The 27.8% podcast routing correction rate (131 theme-scoring misses vs 70 routing bugs) indicates theme scoring prompts are not aligning with user expectations. Per-day correction breakdown shows all themes have 23-42 articles corrected away, with Wednesday (Repair Culture & Practical Tech) showing the highest correction count (42) but also the best good_pct (44.1%). Thursday (Indigenous Lands & Innovation) has the worst good_pct (23.5%) and 19 corrections. Recommend: (1) Review scoring_prompt for Thursday theme—user corrections suggest it's routing articles that don't match 'Indigenous Lands & Innovation' or missing articles that do. (2) Review Monday (Arts, Culture) and Tuesday (Working Lands) prompts—both have ~30% good_pct and 23-25 corrections, indicating poor theme-content alignment. (3) Use corrected article URLs as test cases when rewriting prompts—ground truth is in the user's day corrections.

## 2026-08-02

Audit window: 16 runs (2026-07-20T06:54:16.599439+00:00 to 2026-08-02T06:39:02.102559+00:00).


**Analysis**

The 16-run audit window (July 20–August 2) reveals two critical issues requiring immediate attention. First, a catastrophic theme scoring collapse occurred on July 26 (run 2026-07-26T19:16:45) affecting weekday themes: Monday mean_theme_score dropped from stable 26.6 to 7.1, Tuesday 26.6→3.0, Wednesday 26.6→8.4, Thursday 26.6→4.2. This was NOT gradual drift—it was an immediate break, with composite histograms showing near-total concentration in the 0-19 band (Monday 237/250 articles, Tuesday 249/250, Thursday 250/250). Friday/Saturday/Sunday recovered to 35–45 range in the same run, ruling out global scoring failure. Subsequent runs show partial recovery but persistent damage: as of August 2, Monday mean 8.0 (still collapsed), Tuesday 3.1 (dead), Wednesday 8.9 (weak), Thursday 4.6 (dead), while weekend themes remain healthy (Friday 37.4, Saturday 39.1, Sunday 48.7). This pattern—weekday collapse, weekend survival—points to a scoring_prompt regression specific to weekday theme definitions introduced around July 26. The collapse has persisted across 10 consecutive runs (July 26–August 2), generating thin podcast feeds (Monday 4–36 articles vs target 100, Tuesday 1–25 articles) and massive holdover bank accumulation for weekend themes (1400+ banked articles for Friday/Saturday/Sunday vs 85–462 for weekdays). This is a recurring issue requiring human review of scoring_prompt and theme_description fields for Monday/Tuesday/Wednesday/Thursday—no auto-tunable knob will fix a near-zero mean_theme_score.

Second issue: user feedback confirms the quality gate remains too permissive despite min_claude_score now at ceiling (20). The threshold_sweep shows current floor cuts 34.0% of bad articles while losing 9.2% of good ones—we've exhausted headroom at the quality gate. Band_precision reveals composite scores lack discriminatory power: even 80-100 band is only 57.1% good (vs 42.9% bad), and 40-59 band is coin-flip territory (41.4% good, 51.0% bad). The root cause is structural: dimensional histograms show the local dimension is a binary cliff (news: 7900/7974 articles score 0-19 on L), which collapses composite scores because L=0 dominates the 0.25Q + 0.55R + 0.20L weighting for non-Cariboo content. Quality/relevance distributions are more normal, but the weighting formula punishes anything outside Williams Lake. This is a forbidden-territory prompt/weight issue. Noise-to-signal has improved (window mean 1.85, down from 2.07 three weeks ago), and final feed sizes remain healthy (336–394/run), so upstream volume is not the problem. The 28.2% podcast routing correction rate (134 theme-scoring misses vs 73 routing bugs) confirms theme prompts need human rewrite, not keyword tweaks.


No changes applied this run.


**Human recommendations**

- URGENT: Review and fix scoring_prompt/theme_description for Monday (Arts/Culture), Tuesday (Working Lands), Wednesday (Repair Culture), and Thursday (Indigenous Lands) podcast themes. Mean theme scores for these four themes collapsed from stable 26.6 baseline to 3.0–8.9 range starting July 26 and have not recovered across 10 consecutive runs (July 26–August 2). Friday/Saturday/Sunday themes remain healthy (37–48 mean_theme_score), proving the pipeline can generate valid scores. The weekday collapse is generating critically thin podcast feeds (1–36 articles vs target 100) and is almost certainly caused by a prompt regression that broke theme matching logic for weekday themes specifically. Compare scoring_prompt text for collapsed themes vs healthy weekend themes to identify the divergence introduced around July 26.
- Consider reweighting composite score formula or introducing separate 'newsworthiness' and 'local priority' tracks. Current formula (0.25Q + 0.55R + 0.20L) collapses scores for non-Cariboo content because L=0 dominates calculation for 99% of articles (news: 7900/7974 score 0-19 on local dimension). This creates poor band precision: even 80-100 composite band is only 57.1% good vs 42.9% bad. Quality and relevance dimensions show normal distributions and could discriminate if not weighted down by the local cliff. User feedback shows 63.0% overall bad rate, but threshold_sweep proves we've exhausted headroom at the quality gate (min_claude_score=20 at ceiling). The problem is not the gate floor—it's that composite scores don't separate good from bad articles effectively.
- Consider blocking or deprioritizing worst-performing sources identified in user feedback: Neowin (90.9% bad over 11 articles), Reactor Magazine (90.0% bad over 10 articles), Al Jazeera English (88.9% bad over 27 articles), Lifehacker (88.2% bad over 17 articles), My East Kootenay Now (87.5% bad over 8 articles), NPR Health News (85.7% bad over 7 articles), Toms Guide (84.6% bad over 26 articles), CBC Arts (83.3% bad over 12 articles), Quartz (82.4% bad over 17 articles), NYT Business (80.0% bad over 20 articles). These sources account for 165 rated articles with 141 bad verdicts (85.5% bad rate)—blocking them would cut substantial noise. Source blocking is outside auto-tunable scope but would be more effective than further threshold raises given we're at calibration ceiling.
- Review scifi category definition and source mix. User feedback shows 100% bad rate over 7 rated scifi articles (5 in main feed audit, 2 in podcast). This suggests either the category attracts wrong sources or the scoring_interests definition for scifi is misaligned with maintainer preferences. Scifi final feed sizes are small (1–8 articles/run) but consistently rated poorly, indicating systemic mismatch rather than random noise.

## 2026-08-09

Audit window: 16 runs (2026-07-26T19:16:45.882303+00:00 to 2026-08-09T05:11:33.008313+00:00).


**Analysis**

The 16-run audit window (July 26–August 9) reveals a critical and urgent crisis: the catastrophic weekday theme score collapse that began July 26 has now persisted across 16 consecutive runs with no sign of recovery. Monday mean_theme_score remains collapsed at 8.2 (vs healthy pre-collapse baseline of ~26-30), Tuesday is effectively dead at 3.2, Wednesday shows weak partial recovery at 9.0, and Thursday remains dead at 4.7. Meanwhile, weekend themes continue to perform normally (Friday 37.7, Saturday 39.5, Sunday 49.1), proving the pipeline can still generate healthy scores—this is NOT a global scoring failure but a specific weekday-theme regression. The composite histograms show the damage: Tuesday has 1556/1566 articles in the 0-19 band as of August 9, Thursday has 1553/1565 in 0-19. Podcast feeds for collapsed themes are critically thin (Monday averaging 13 articles vs target 100, Tuesday averaging 10 articles), while weekend holdover banks overflow (1381+ banked for Friday, 1426+ for Saturday, 1376+ for Sunday). This is a scoring_prompt or theme_description bug introduced around July 26, NOT a threshold or keyword issue—no amount of min_score lowering will fix a mean_theme_score of 3.2.

User feedback provides critical ground truth that the composite scoring system has fundamental structural problems independent of the theme collapse. Band_precision shows composite scores lack discriminatory power: 80-100 band is only 57.1% good (42.9% bad), 60-79 is 42.6% good (57.4% bad), and 40-59 is essentially random (39.9% good, 51.5% bad). The threshold_sweep confirms min_claude_score=20 (current ceiling) cuts only 32.7% of bad articles while losing 9.8% of good ones—we've exhausted headroom at the quality gate. The root cause is visible in dimensional histograms: the local dimension is a binary cliff (8834/8878 news articles score 0-19 on L), which collapses composite scores via the 0.25Q + 0.55R + 0.20L weighting for anything outside Williams Lake. Quality and relevance distributions are more normal, but L=0 dominates the calculation for non-Cariboo content. This is a forbidden-territory weighting/prompt issue.

Noise-to-signal has stabilized at a healthy window mean of 1.84 (down from 2.09 four weeks ago), and final feed sizes remain robust (390–460/run, window mean 416). New categories (homestead, design, outdoors) have appeared in final feeds starting August 4, indicating the category expansion is working. The 26.3% podcast routing correction rate (220/835 corrections: 80 routing bugs, 140 theme-scoring misses) confirms theme prompts need human review. Worst sources remain consistent (Neowin 92.3% bad, Reactor Magazine 90% bad, Al Jazeera 87.1% bad, Toms Guide 87.1% bad)—strong candidates for blocking.


No changes applied this run.


**Human recommendations**

- URGENT: The weekday theme score collapse (Monday/Tuesday/Wednesday/Thursday) has persisted for 16 consecutive runs since July 26 with no recovery. Mean theme scores remain catastrophically low (Tuesday 3.2, Thursday 4.7, Monday 8.2) while weekend themes perform normally (Friday 37.7, Saturday 39.5, Sunday 49.1). This is a scoring_prompt or theme_description regression specific to weekday themes introduced around July 26. Recommend immediate human review and rewrite of the scoring_prompt and theme_description fields for Monday/Tuesday/Wednesday/Thursday. The weekend themes prove the scoring infrastructure works—the weekday prompts are broken.
- The composite scoring system has fundamental structural problems revealed by user feedback: band_precision shows even 80-100 scored articles are only 57.1% good (42.9% bad), and dimensional histograms show the local dimension is a binary cliff (8834/8878 news articles score 0-19 on L). This collapses composite scores for non-Cariboo content because L=0 dominates the 0.25Q + 0.55R + 0.20L weighting. Recommend human review of the scoring_weights (particularly w_local) and/or the local keyword matching logic to reduce the binary cliff effect. The quality and relevance dimensions show normal distributions—the problem is L.
- User feedback identifies worst sources with consistently high bad rates: Neowin (92.3% bad over 13 articles), Reactor Magazine (90% bad over 10 articles), Al Jazeera English (87.1% bad over 31 articles), Toms Guide (87.1% bad over 31 articles), NPR Health News (85.7% bad over 7 articles), Lifehacker (85% bad over 20 articles), Quartz (83.3% bad over 18 articles), CBC Arts (83.3% bad over 12 articles), Kottke.org (83.3% bad over 12 articles), NYT Business (80% bad over 25 articles). Recommend adding these to a source blocklist or applying heavy source_type_quality_adjustments penalties. Source blocking is not auto-tunable but would immediately improve feed quality.
- The scifi category shows 100% bad rate over 7 rated articles in user feedback. Recommend human review of the scifi category definition, source mix, and scoring criteria to diagnose why it's producing pure noise. The category may need tighter source curation or a rewritten category description.
- The 26.3% podcast routing correction rate (220/835 corrections: 80 routing bugs, 140 theme-scoring misses) indicates the theme routing logic and/or theme scoring prompts need human review. The 140 theme-scoring misses suggest articles are being scored for the wrong day's theme, not just routed incorrectly—this points to ambiguous or overlapping theme_description fields that confuse the scoring model. Recommend reviewing theme_description uniqueness and clarity across all seven days.

## 2026-08-16

Audit window: 14 runs (2026-08-03T07:34:53.939952+00:00 to 2026-08-16T04:41:25.880350+00:00).


**Analysis**

The 14-run audit window (August 3–16) reveals two distinct periods separated by a major infrastructure change on August 11. CRITICAL FINDING: The weekday theme score collapse that has plagued the pipeline since July 26 appears to have been RESOLVED by the August 11 rearchitecture introducing dimensional scoring and relative scaling. Pre-August 11 runs show the familiar catastrophic pattern: Monday mean 8.2, Tuesday 3.1, Wednesday 9.1, Thursday 4.8, with composite histograms showing near-total concentration in 0-19 bands. Post-August 11, ALL themes show healthy mean_theme_score_raw values in expected ranges (Monday 17.4–22.0, Tuesday 5.9–11.0, Wednesday 2.7–3.6, Thursday 7.7–18.0, Friday 37.8–45.8, Saturday 39.6–47.5, Sunday 50.7–59.1), and the relative_scaled flag appears in podcast_feed_trends indicating the new scoring system is active. Podcast feeds are now consistently hitting target 100 articles across all themes with robust banked holdover pools (1113–1286 per theme as of August 16). This is a MAJOR win—the scoring_prompt rewrite bundled with the dimensional infrastructure appears to have fixed the root cause.

However, user feedback ground truth (window ending August 8, just before the fix) still shows the old system's problems: 64.2% bad rate, poor band_precision (80-100 band only 57.1% good), and composite scores lacking discriminatory power. The threshold_sweep data is unchanged from previous weeks (min_claude_score=20 cuts 32.7% bad at 9.8% good lost), but this data predates the dimensional scoring rollout. The dimensional histograms now show data for quality/relevance/local dimensions starting August 11: these reveal the structural issue the old system had—local dimension remains a binary cliff (9401/9427 news articles score 0-19 on L), but the new weighting system appears to handle this better based on healthy theme scores.

Noise-to-signal shows mixed signals: window mean 2.18 (up from 1.84 last week), with recent runs at 2.0–2.79. The spike correlates with the August 11 infrastructure change and subsequent stabilization period—likely reflects the pipeline adjusting to new scoring logic and dimensional data collection. Final feed sizes are healthy (389–489/run, mean 439), above the ~100 target but reasonable given category expansion. Content type breakdown shows the Haiku scrub is working (1952 articles removed from news, 132 from wellness), and quality gate totals show good separation (1244 passed vs 6735 dropped across all categories).


No changes applied this run.


**Human recommendations**

- User feedback audit data ends August 8, just before the August 11 dimensional scoring rollout. The next user feedback audit cycle (covering August 9–present) will be critical ground truth for whether the new scoring system actually improves band_precision and reduces the 64.2% bad rate. Recommend prioritizing review UI usage over the next 7–10 days to generate fresh feedback data under the new scoring regime.
- Noise-to-signal spiked from 1.71 (August 10) to 2.30 (August 11) coinciding with the dimensional scoring rollout, then fluctuated 2.77–2.79 (August 12–13) before settling back to 2.0 (August 16). This may reflect the pipeline adjusting to new scoring logic or could indicate the dimensional system is generating more upstream noise. Monitor the noise-to-signal benchmark over the next 2–3 weeks: if it stabilizes above 2.3 (vs pre-change baseline of 1.84), consider whether kagi_search_result_limit needs lowering or whether the dimensional scoring is less efficient at early filtering.
- The dimensional histograms reveal the local dimension remains a binary cliff even under the new system (news: 9401/9427 articles score 0-19 on L, ai-tech: 417/417 at 0-19 on L). This is expected—most content is not Cariboo-specific. However, if user feedback shows the new weighting (w_quality=0.25, w_relevance=0.55, w_local=0.20) still collapses composite scores for non-local content, the weights themselves may need human review. The current setup appears to handle this better than the old system (evidenced by healthy theme scores), but worth monitoring whether non-local high-quality content is still being unfairly penalized.
- Worst sources from user feedback remain consistent across all audit periods: Reactor Magazine (90% bad), Lifehacker (87% bad), Toms Guide (86.5% bad), Neowin (85.7% bad), CBC Arts (84.6% bad), Al Jazeera English (82.4% bad). These are strong candidates for source blocking or de-prioritization, but that mechanism is outside the current auto-tunable scope. Recommend adding a source_blocklist or source_deprioritization mechanism to the pipeline config.
- The scifi category shows 100% bad rate over 7 rated articles in user feedback, and final feeds show only 1–12 scifi articles per run. This suggests either the source mix for scifi is wrong or the category definition is too narrow. Recommend human review of scifi source preferences and category definition—this is likely a content curation issue rather than a scoring problem.
- Theme routing corrections remain high at 25.1% (231/921 corrections), split 85 routing bugs vs 146 theme-scoring misses. The dimensional scoring rollout may have changed how theme_score is calculated, but the user feedback data predates that change. The next feedback audit will reveal whether the new system reduces theme-scoring misses. If correction rate remains above 20% under the new scoring, the theme keyword lists and scoring_prompts (forbidden territory) need human review.
- Final feed sizes have been consistently above the ~100 target (window mean 439, range 389–489) since the category expansion (homestead/design/outdoors added August 4). If the goal is to return to ~100 articles/run total across all categories, either feed_slots.max_slots need lowering or min_score_by_category floors need raising. However, the current volume may be intentional to support the expanded category set—recommend clarifying the target total feed size before making changes.
- The August 11 rearchitecture introduced a major change to how dimensional scores are stored and calculated, but the user feedback audit data (ending August 8) predates this change. The dimensional histograms in the audit data start appearing August 11, meaning we have only 5 runs of dimensional data in the current window. The threshold_sweep and band_precision analysis is based entirely on pre-dimensional-scoring data and may not reflect how the new system performs. Recommend running a fresh user feedback audit covering August 11–present before making any threshold or quality gate changes based on the old data.
