## Context

Why this change was needed. What problem does it solve? Any architectural tradeoffs or constraints worth noting?

## Summary

What changed. Keep this concise — the Context section explains the motivation and tradeoffs above.

## New dependencies or breaking changes

- Any additions to `requirements.txt`? Version pinned? Compatibility notes?
- Any changes to output/config format? Schema updates to JSON feeds or cached state files?
- None if not applicable.

## API cost impact

- Did Claude model choice, batch size, or call frequency change?
- Cohere/Brave/Kagi call volume changes?
- Net impact on daily/weekly API costs?
- None if not applicable.

## Config changes

- Files under `config/` touched? Which ones?
- Did `calibration_bounds.json` whitelist need updating to allow new tunable knobs?
- Any changes to scoring weights, thresholds, or category definitions?
- None if not applicable.

## Testing

- What test? (unit test, integration run, local `super_rss_curator_json.py` run, dry-run, etc.)
- Command or steps to reproduce verification?
- None if verification is obvious from the diff and commit message.
