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
