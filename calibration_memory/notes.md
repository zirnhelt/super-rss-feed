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
