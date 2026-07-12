# Calibration Agent Notes

Free-text journal for the weekly calibration agent. Each run appends a dated
entry summarizing its reasoning, anything notable observed in the audit
window, and context useful for future runs that isn't captured in
`recurring_issues.json` or `change_history.json`.

---

## 2026-06-24 — Manual threshold reset (human intervention)

Pipeline audit showed the main-feed quality gate was cutting ~94% of new articles
(559 new → 33 quality) because `min_claude_score` was set to 20 and `feed_slots`
capped total output at 57. Yesterday's podcast threshold change (cf580d2) didn't
touch these knobs at all.

Changes applied manually:
- `limits.min_claude_score`: 20 → 13 (target: allow borderline-quality content through)
- `feed_slots.max_slots`: raised all categories to calibration ceilings (57 → 104 total capacity)
- `calibration_bounds.json` defaults updated to match — do not drift these back up without
  evidence that article counts are consistently above ~120/day.

Goal is ~100 quality articles per run. If calibration data shows consistent overshoot
(>130/day), raising `min_claude_score` to 15–16 is the first dial to touch.

## 2026-07-12

The audit window (7 runs, July 7–12) shows stable pipeline performance following the June 24 manual threshold reset. The noise-to-signal ratio has improved significantly over the window: starting at 1.23 (July 7), it spiked to 2.76 (July 9), then settled back to 1.53 (July 12) with a window mean of 2.09. Final feed sizes are healthy at 295–398 articles per run, well above the ~100 target set during the manual intervention. The user feedback audit provides critical ground truth that contradicts some pipeline-side metrics: 63.3% of rated articles were marked bad, with the composite score showing poor separation — band_precision reveals that even 80-100 scored articles were only 56% good. The current min_claude_score of 13 cuts just 18.8% of user-rated bad articles while losing only 3.6% of good ones, suggesting the quality gate is too permissive. The threshold_sweep shows raising min_claude_score to 20 would cut 28.1% of bad articles at a cost of 5.7% good articles lost — a favorable trade. The dimensional histograms reveal a systemic issue: across all categories, the vast majority of articles score 0-19 on the composite scale (e.g., news: 3186 in 0-19 vs 97 in 60-79), yet quality/relevance histograms show more normal distributions. This suggests the composite weighting (0.25 Q + 0.55 R + 0.20 L) is collapsing scores for non-local content because the L dimension is stuck at zero for most articles. Theme routing shows 28.8% correction rate (159/553), split 45 routing bugs vs 114 theme-scoring misses — the latter indicates the podcast theme prompts need human review, not knob changes. Worst sources (Al Jazeera 95% bad, Lifehacker 93.8% bad, Toms Guide 88.9% bad) are candidates for blocking, but that's outside the auto-tunable scope. The podcast feeds are thin on banked holdovers (8-37 per theme), and mean theme scores have collapsed from ~30-42 (July 7) to ~26-27 (July 12) across all themes, suggesting either scoring_prompt drift or upstream content mix shift — but the histogram shapes are consistent, so this is likely real signal, not calibration error. Monday's mean_theme_score collapsed from 30.3 to 26.7 immediately after July 7, and has held flat since — this is a clear break, but not severe enough to flag as a recurring issue yet (threshold is still above min_score=28).
