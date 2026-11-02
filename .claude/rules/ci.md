---
paths:
  - ".github/**"
  - "requirements*.txt"
---

# CI/CD — see [docs/decisions/scheduling-and-ci.md](../../docs/decisions/scheduling-and-ci.md)

## `generate-feed.yml` — nightly pipeline

- The 06:00 UTC run (11 PM Pacific, so the evening's news makes it) and its 07:00 UTC backup arrive as `workflow_dispatch` from a **Cloudflare Worker** in the sibling repo (`curated-podcast-generator/cloudflare/scheduler/`) with a `run_slot` input. The podcast reads the pool at 08:05 UTC. **The file name and the `run_slot` input are a contract** (pinned in `tests/test_podcast_feed_contract.py`).
- **One GitHub cron remains, `0 10 * * *`**, as the backstop for the Worker being down. Don't remove it; don't add the ladder ticks back.
- **Gate on `inputs.run_slot`, never `github.event.schedule`.** A source channel switched off by a missed gate reads exactly like a quiet week — the `USE_SEARCH_APIS` bug.
- Steps: download feeds and caches from gh-pages → bootstrap thin feeds → run the curator → log to `FEED_LOG.md` → copy `review.html` unchanged → commit caches → deploy `output/` and verify the gh-pages tip byte-matches.
- **`validate` is a separate job that never fails.** A permanently red check buries the signals that matter. Keep it out of `build`.
- Secrets: `ANTHROPIC_API_KEY` (required); `COHERE_API_KEY`, `BRAVE_API_KEY`, `KAGI_API_KEY` (optional).

## `weekly-maintenance.yml` — Saturday 13:23 UTC

Eight jobs in order, each skippable by `workflow_dispatch` input: **discovery** (auto-merged PR at threshold 65) → **feed-health** (`--heal`; after discovery because both rewrite `feeds.opml`) → **calibration** (commits all of `config/`) → **feedback-training** (archive, then train) → **standing-preferences** (a proposal PR, never auto-merged; skipped while one is open) → **quality-review** (the three reports into `reports/`) → **filter-review** → **report** (weekly HTML to gh-pages).

**Bot pushes and bot PRs trigger no workflows** (`GITHUB_TOKEN`), so `tests.yml` never sees them; a bot PR's run shows zero jobs. Every job that commits code-adjacent files (`feeds.opml`, `config/`) runs `config_loader.py` + pytest itself first ("Validate before committing"). Keep that step in front of any new commit or auto-merge.

**It runs Saturday so the podcast's Sunday Meta Moment can cite it.** The report job writes the week's applied changes (feeds added, healed, retired; calibration knobs) to `weekly-state-article.json` → `_changes`, built from the agents' records, never the narrative. The podcast reads `_changes` and `date_published` from `main` (`get_upstream_week_changes`) and ignores a file over 7 days old; renaming either key silently empties that half of the segment. Don't move the run back past Sunday 08:05 UTC.

`git_push_retry.sh` auto-resolves rebase conflicts only in generated files (`GENERATED_PATTERNS`, which includes `reports/*`); a conflict in anything hand-editable fails the step.

**Every workflow installs `requirements-lock.txt`** (`pip freeze`, Python 3.11). Edit `requirements.txt`, then regenerate the lock; `tests/test_requirements_lock.py` fails until you do.

## `tests.yml` — the required check

Job `pytest`: config validation + the suite, on every push to `main` that touches code/config/tests and on **every** pull request. No `paths:` filter on `pull_request`: a filtered-out PR would never start the required check and could never merge.

## Other workflows

- `deploy-static.yml` — copies `review.html` to gh-pages on push.
- `refresh-editorial.yml` — dispatched by the podcast's review job (scheduler PAT); splices new editorial items into gh-pages feeds. Shares the `generate-feed` concurrency group. Its file name is a contract.
- `refresh-hot.yml` — GitHub cron every 2 h at :41. `--refresh-hot` splices clear winners into `local`/`news` between nightlies (`system.json` → `hot_refresh`): plain GETs, the quality gate only, admits above a higher bar (Cariboo anchor, world flag, or score ≥ `min_score`), commits nothing. The first run after Kagi News's 12:00 UTC batch (`kite_batch_max_age_hours`) also reads it, so its news clusters land that afternoon. Its items carry `_hot_refresh`; the nightly merge drops one when it files the same URL or story in **any** category. Stands down while `generate-feed` is queued or running, since a newer pending run in the shared group cancels the older.
- `cleanup-branches.yml` — stale branch cleanup.
