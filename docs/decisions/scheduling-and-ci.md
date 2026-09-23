# Scheduling and CI: the daily pipeline workflow

*Moved verbatim from CLAUDE.md on 2026-09-23. CLAUDE.md keeps the standing rules; this file keeps the incidents and the reasoning behind them. Read it before changing the code it describes.*

# `generate-feed.yml` — Daily pipeline

**Schedule:** the 04:00 UTC run (8 PM Pacific the previous day) and its 07:00 UTC
backup rung both arrive as `workflow_dispatch` from a **Cloudflare Worker**, which
lives in the sibling repo at `curated-podcast-generator/cloudflare/scheduler/` and
sends a `run_slot` input. GitHub's cron is best-effort — it delays scheduled
workflows under load and drops the tick outright once the delay passes the next
window — and this feed has a hard downstream deadline: the podcast reads the
scored pool at 08:05 UTC.

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

**Required secrets:** `ANTHROPIC_API_KEY`
**Optional secrets:** `COHERE_API_KEY`, `BRAVE_API_KEY`, `KAGI_API_KEY`
