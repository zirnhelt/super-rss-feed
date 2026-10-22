# Scheduling and CI: the daily pipeline workflow

*Moved verbatim from CLAUDE.md on 2026-09-23. CLAUDE.md keeps the standing rules; this file keeps the incidents and the reasoning behind them. Read it before changing the code it describes.*

# `generate-feed.yml` — Daily pipeline

**Schedule:** the 06:00 UTC run (11 PM Pacific the previous day) and its 07:00 UTC
backup rung both arrive as `workflow_dispatch` from a **Cloudflare Worker**, which
lives in the sibling repo at `curated-podcast-generator/cloudflare/scheduler/` and
sends a `run_slot` input. GitHub's cron is best-effort — it delays scheduled
workflows under load and drops the tick outright once the delay passes the next
window — and this feed has a hard downstream deadline: the podcast reads the
scored pool at 08:05 UTC.

The first rung was 04:00 UTC (9 PM) until 2026-10-18, when it moved to 06:00 because
evening news missed the run (the 2026-10-17 municipal election results; see Hot
refresh below). A run takes about ten minutes, so the 07:00 backup still has an hour
of slack behind it and finishes well before 08:05. B.C. is on permanent UTC-7, so
06:00 is 11 PM all year.

**One GitHub cron remains**, `0 10 * * *`, purely as the backstop for the *Worker*
being down, timed to pair with the podcast's own GitHub backstop at 11:05 UTC. On
a normal night it costs ~20 s — it starts, `preflight` sees the day is covered,
and it stands down. Do not remove it, and do not add the two ticks back to the
`schedule:` block; that is what keeps the schedule from depending on one vendor.

**`preflight` gates on `inputs.run_slot`, not `github.event.schedule`.** Anything
that needs to know which rung it is on must read the input — a schedule-triggered
run leaves it empty, which is how the backstop is told apart from a manual run.

**`USE_SEARCH_APIS` was the one that got missed.** It read
`github.event_name == 'schedule' || inputs.use_search_apis`, which was correct
until the ladder moved to the Worker — after that every nightly run arrived as
`workflow_dispatch` with `use_search_apis` defaulting to false, so topic queries
*and* the Brave/Kagi recovery path for failing feeds were off on every real run.
Only the 10:00 UTC backstop had them on, and that one stands down as soon as
preflight sees the day is covered. It now also accepts `inputs.run_slot != ''`.
This is the failure mode to look for whenever sourcing looks thin: a source
channel that is switched off reads exactly like a quiet week.

`weekly-maintenance.yml` and `cleanup-branches.yml` stay on GitHub's cron:
Workers Free allows only 5 Cron Triggers per account, all five are spent on the
two ladders where a late trigger costs the day, and a weekly report arriving an
hour late costs nothing.

**The weekly run moved from Sunday 13:00 UTC to Saturday 13:23 UTC on
2026-10-05**, so the podcast's Sunday Meta Moment can draw on it. On Sunday it
landed five hours after the Meta Moment was written, so the show could only
ever hear about the week before last, and the weekly agents' own commits
("Weekly calibration agent run") name a job, not a change, so the podcast
skips them. The report job now writes the week's applied changes to
`weekly-state-article.json` → `_changes`: one plain line per feed added,
healed, retired or restored and per calibration knob moved, built from the
agents' records (`discovery_actions.json`, `feed_health_actions.json`,
`change_history.json`), never from the model-written narrative: the Meta
Moment's guard treats every input line as fact, and a narrative is a model's
reading of the facts. The podcast reads the file from `main` and uses it only while
`date_published` is under 7 days old, so a Saturday run that slips past Sunday
08:05 UTC airs the following Sunday, never twice. GitHub cron has been seen
running up to six hours late, and Saturday 13:23 leaves about nineteen.

`discovery_actions.json` is committed by the discovery PR as well as uploaded as
an artifact, so a week whose discovery job failed used to report last week's
additions as new. The report job now deletes it when discovery did not succeed.

Also triggered manually with optional `use_search_apis` flag.

**Steps:**
1. Download existing feeds + caches from `gh-pages` (atomic JSON validation; skips stale files).
2. Bootstrap thin feeds from podcast cache if any category feed < 20 items.
3. Run `python super_rss_curator_json.py feeds.opml`.
4. Log results to `FEED_LOG.md` via `log_feed_results.py`.
5. Copy `review.html` → `output/review.html` unchanged. **No credential ever goes into a page**: a GitHub token was baked into this public page from 2026-06-17 until it was revoked on 2026-09-23. The page now asks for a fine-grained token (super-rss-feed only, Contents read/write) in a password field when saving, filled from a password manager, and keeps it only while it is open — never in browser storage, which any script on `zirnhelt.github.io` could read.
6. Commit updated cache files to `main`.
7. Deploy `output/` to `gh-pages`, then verify the tip byte-matches this run's output.

**`validate` is a separate job** (`needs: build`) that reads the published feeds
off the gh-pages tip and runs `validate_podcast_feeds.py`. It reports to the job
summary and **never fails**. It used to be two steps inside `build` — one under
`continue-on-error: true`, one re-raising the outcome after the deploy — so its
only possible effect was reddening a run whose feeds had already shipped, and
from 2026-08-30 it did that on every single run. A permanently red check is not
an alarm; it buries the two signals in `build` that do mean something (the
curator, and the gh-pages byte-match verifier). Keep it out of `build`, and keep
it green: recalibrating a charter is a human's weekly job, not a reason to
re-run the pipeline.

## Dependencies are installed from a lock (2026-10-04)

`requirements.txt` pinned only the six top-level packages, so each run still resolved the ~30
transitive ones fresh: a new `httpx`, `pydantic` or `urllib3` reached the nightly run unannounced.
Every workflow now installs `requirements-lock.txt`, the `pip freeze` of a clean Python 3.11 venv
built from `requirements.txt`, in the same format as the podcast repo's lock (no hashes; the podcast
has none either). The first lock is exactly what `generate-feed.yml` installed on 2026-10-04, so
nothing was upgraded. `requirements.txt` stays the human-edited source;
`tests/test_requirements_lock.py` fails when a pin there and the lock disagree, so a bump in one
file alone cannot reach CI silently.

## Hot refresh between nightlies (2026-10-18)

The nightly fetched at 04:00 UTC, 9 PM Pacific. On 2026-10-17 the B.C. municipal
election results were mostly out by 9 PM and none made the run, so the feed carried
them a day late. Rerunning the nightly every couple of hours would multiply the
spend and fight the podcast caches; `refresh-hot.yml` instead runs
`--refresh-hot` (`refresh_hot_feeds()`) every two hours on GitHub cron:

- **Fetch** every OPML feed and the local scrapes with plain GETs (`_fetch_feed_plain()`,
  shared with the editorial refresh). No conditional GET, no paid fallbacks:
  the HTTP state and the backoff ladder belong to the nightly. Kagi News (free) is read
  only by the first run after its 12:00 UTC batch (`kite_batch_max_age_hours`), with
  the nightly's 48 h article cutoff; see [sources.md](sources.md).
- **Delta**: an article whose hash is in `scored_articles_cache.json` (from `main`) was
  judged by the nightly; the shown caches and the published feeds hold what was placed.
  Only the remainder published in the last `lookback_hours` (6) is considered.
- **Score** with the quality gate only, and only candidates headed for a `hot_refresh`
  category. No Cohere, no deep scoring. A typical two hours is a few dozen articles,
  one or two Haiku calls: well under a cent a run.
- **Admit** above a higher bar than the nightly's, which also fills `min_slots`
  regardless of the floor: a Cariboo-anchored local story, a gate world flag, or a
  score at `min_score` (65, the gate's top band, ~5% of a night). Capped per category
  per run. A gate outage admits nothing: the nightly is the safety net, so this pass
  fails closed where the nightly fails open.

It writes no cache and commits nothing to `main`. The next nightly sees each placed
article as new and judges it with the full pipeline; the item's `_hot_refresh` mark
makes the merge drop it when the nightly picks the same URL or story in any category,
not only its own, since the refresh's category is a keyword guess. A nightly rewrite
clears the mark. The podcast pool is untouched: a story placed overnight reaches the
show through the next nightly.

It stands down while `generate-feed` is queued or running. GitHub keeps one pending
run per concurrency group and cancels the older, so a refresh that queued behind a
waiting nightly would cancel it.

**Required secrets:** `ANTHROPIC_API_KEY`
**Optional secrets:** `COHERE_API_KEY`, `BRAVE_API_KEY`, `KAGI_API_KEY`
