# Draft: undocumented failure modes at the feed → podcast boundary

*Draft, 2026-11-11. Design review only: nothing was run, nothing was changed, nothing is committed.*

Producer: `super-rss-feed`. Consumer: `curated-podcast-generator`. Paths below are prefixed `feed:` or `pod:`.

## How this was checked

- Read in full: both `CLAUDE.md` files, `feed:docs/decisions/scheduling-and-ci.md`, `feed:.claude/rules/{ci,pipeline,podcast-pool}.md`, `feed:tests/test_podcast_feed_contract.py`, `generate-feed.yml`, `refresh-editorial.yml`, `refresh-hot.yml`, `git_push_retry.sh`, `pod:cloudflare/scheduler/src/index.ts`, `pod:SIBLING_REPOS.md` (top half).
- Read by function: `PODCAST_FEED_CONTRACT`, `generate_podcast_feed()` (shown filter, feed literal), the shown-cache stamping in `main()`, `generate_weekly_report.get_week_changes()` / `get_calibration_changes()`; on the podcast side `fetch_podcast_feed`, `_assert_feed_fresh`, `_check_feed_contract`, `get_upstream_week_changes`, `segment`, the curate block of the script stage, `_theme_info`, and the tests for each.
- **Searched, not read end to end:** the other decision records (`scoring.md`, `sources.md`, `podcast-pool.md`, and the podcast's `curation.md`, `operations.md`, `editorial-voice.md`, TTS records, about 300 KB) and the other rule files. "Not documented" below means a keyword search of those files found nothing, which is weaker than having read them.
- Not traced: the curator's behaviour on a same-day rerun with mismatched caches (row 6), each `_theme_info` caller's exact effect (row 3), and how `feed_health_actions.json` reaches the report job (row 8). Those rows say so.

## Ranked scenarios

| # | Scenario | Trigger | Root cause | Blast radius (what airs) | Already covered? | Detection today |
|---|---|---|---|---|---|---|
| 1 | **A feed built the night before airs as today's** | Both feed rungs fail or never start (bad merge, push or deploy failure, rows 4 to 6) while the podcast ladder runs normally at 08:05 | `_assert_feed_fresh` judges the newest *article's* age against 48 h, a limit set when the feed was "rebuilt 3x daily". All seven feeds are now rebuilt every night, so yesterday's build of today's feed always holds an article under 48 h old. `_podcast.generated_at` is written but is not in the contract and is never read | A normal-looking episode from the pool as it stood a day earlier: no evening news, and local stories that aired yesterday are deduped out, so the local lead is thin. Run is green | No. `TestFeedFreshness` tests 6 h and 7 days only (`pod:tests/test_podcast_generator.py:2866`). The 2026-07-03 record covers a week-stale feed | A red `generate-feed` run in the *other* repo. Nothing in the podcast's run report |
| 2 | **The legacy fallback airs what the pool excludes** | One failed GET of `feed-podcast-{day}.json` (single attempt, 10 s), a wrong-shape body, or a feed whose items are all `_is_bonus` | `fetch_podcast_feed` returns `(None, [], [])` and the script stage falls back to `feed-{category}.json` plus `scored_articles_cache.json` joined on **title**. Those feeds never passed the pool's choke point: crime and op-ed exclusion, and `[show]` lines (which `feed-news` ignores by design). The fallback prints a warning and calls no `degrade()`. It also produces an episode, so rungs 2 and 3 never retry the real feed | A public episode that can carry a subject the reader ruled off the show, with no theme selection and no local lane. Zeroed scores if the cache's `title`/`score` keys ever change (unpinned) | No. The 2026-02-16 record describes the fallback as graceful; no test references `fetch_feed_data` or `fetch_scoring_data`; the stale check is not applied to it | One stdout line ("falling back to category feeds") |
| 3 | **Theme label drift, live now on Wednesdays** | A `label` edit in `feed:config/podcast_schedule.json` without the matching `pod:config/themes.json` edit | The feed's `_podcast.theme` replaces `today_theme` and the script filename (`pod:podcast_generator.py:14294`). Every later lookup is an exact name match (`_theme_info`, `config/ambient.json` keys) and returns nothing on a miss. The contract pins the key, not the value | Today: the feed says "Repair Culture & Practical Tech", the show's config says "Gear, Gadgets & Practical Tech". Wednesday runs without its config keywords, source boost and ambient bed. I have not checked a Wednesday run report to confirm the on-air effect | No. Neither contract test looks at values; `curation.md` uses both names without noting the mismatch | None |
| 4 | **A hung first rung blocks the whole ladder** | The curator hangs at 06:00 (a stalled batch poll, a socket that never times out) | `build` has no `timeout-minutes` (default 6 h). Concurrency is at workflow level, so the 07:00 rung waits *before* its preflight, and the 10:00 backstop replaces it as the one pending run. `refresh-hot` stands down all day | Row 1, plus no hot refreshes. The run shows "in progress", not failed, so no failure email either | No. The record covers a late or missing trigger, not a run that starts and never ends | None until someone opens the Actions tab |
| 5 | **The cache push to `main` gates the publish** | `git_push_retry.sh` gives up: five lost races, or a rebase conflict in `TODO.md`, which the nightly stages but `GENERATED_PATTERNS` does not list (it has a hand-edited half) | "Commit cache and log files" runs before the three deploy attempts, which have no `if:` that survives a failed step. A log-file conflict therefore stops the feeds shipping. Rung 2 reruns the full spend and can hit the same conflict | Row 1, and the night's API spend twice | No | Red run; the cause reads as a git error, not a missed feed |
| 6 | **Commit succeeds, deploy fails: the rerun starts from split state** | All three deploy attempts fail, or "Verify gh-pages deploy" fails, after the push to `main` landed | Rung 2 checks out `main` (new `scored_articles_cache`, `shown_articles_cache`) and then overwrites the pool, shown and terms caches with the older gh-pages copies. Preflight's "a same-day repeat is safe: the caches upsert by URL" assumes both stores moved together. **Not traced:** whether run 1's articles re-enter the pool or are skipped as already scored | Possibly a pool missing the night's new articles, so a thin or day-old episode; category feeds may also lose them | No | Rung 1 red, rung 2 green: looks recovered |
| 7 | **The backstop sits after the read it protects** | A failure limited to the feed's dispatches (workflow renamed, PAT loses Actions on that repo only), or the Worker fully down with both GitHub crons late | The feed backstop is 10:00; the podcast's Worker rungs are 08:05, 09:05, 10:05. Feed-only failure: the podcast reads first, by design. Both-down: 10:00 and 11:05 are both best-effort crons with 65 minutes between them, against observed delays of up to six hours | Row 1. The late feed run is then spent for nothing | Partly: the record says the backstop "pairs with" 11:05, which covers only the both-down, on-time case | A Worker alert issue for the rung-2 dispatch, if the PAT can still open issues |
| 8 | **Preflight counts the wrong runs as coverage** | A manual run that succeeded between 00:00 and 05:59 UTC (5 to 11 PM Pacific, when a person is likely to run one), then rung 1 fails | Coverage is "any other run created today with conclusion `success`". That includes the evening manual run and any run that itself stood down (a skipped `build` still concludes `success`) | Rung 2 and the backstop stand down. The podcast gets the evening build: hours stale, missing the late news the 06:00 move was made for | No. Preflight is shell inside YAML with no test | None: every run after rung 1 is green |
| 9 | **`_changes` is partial but freshly dated** | The weekly run crosses 00:00 UTC (a late cron), or the report job is re-run on another day | `get_calibration_changes` keeps only rows whose `run_date` equals the report job's own UTC date, then `date_published` is stamped now. On the podcast side an empty `_changes` under a fresh date returns `[]` with no `degrade()` | The Sunday Meta Moment presents a week with the calibration moves missing, or says nothing about the feed, as if nothing happened. `feed_health_actions.json` staleness not traced | Partly: stale `discovery_actions.json` is documented and fixed; the calibration filter and the empty-list case are not. `test_weekly_state_keeps_the_keys…` pins key names only | One log line in the report job |

**Considered and dropped:** the Brave monthly cap. The sharing, the per-run cap and "read the export first" are all documented, and the podcast recognises the 402. The only uncovered slice is that reruns multiply the curator's 25-call cap and neither repo keeps a month ledger; at 0 to 3 calls a night that is not worth a row. Also dropped: `refresh-editorial` has no stand-down preflight and could cancel a pending nightly, but it is dispatched around 10:05, when the only nightly in play is the no-op backstop.

**Related, smaller:** `_assert_feed_fresh` returns without blocking *and without a degrade row* when no `date_published` parses. That is pinned as intended (`test_unparseable_dates_do_not_block`), but it means a date-format change upstream switches off the only staleness guard silently. Row 1's fix closes it.

## Test specs, top five

All of these stub every API, touch no network, and write nothing under `podcasts/` or `feedback/`.

### 1. Night-old feed (row 1)

- **Repo:** podcast, `tests/test_podcast_generator.py`, class `TestFeedFreshness`. One line in the feed repo.
- **Under test:** `_assert_feed_fresh`, changed to take the feed dict so it can read `_podcast.generated_at`.
- **Fixtures:** (a) `generated_at` 2 h ago, newest item 20 h old. (b) `generated_at` 26 h ago, newest item 20 h old. (c) `generated_at` missing, items fresh. (d) `generated_at` unparseable.
- **Expected:** (a) passes with no row. (b) is night-old: the episode airs, on whichever rung reads it, with a `script/feed-stale` degrade row giving the build's age. **Decided 2026-11-11: a slightly stale feed is better than no episode.** No waiting on rungs 1 and 2: nothing is scheduled to land a fresh feed between 08:05 and 10:05 (the feed backstop starts at 10:00 and takes ten minutes), so waiting adds two hours and a rung of risk for nothing. (c) and (d) degrade `script/feed-contract` and fall back to today's article-age check.
- **Unchanged:** the existing 48 h article-age abort stays. That is the week-old replay of 2026-07-03, which is not "slightly" stale.
- **Threshold:** about 20 h. The read is 2 h after the build on a good night and 26 h after on a missed one.
- **Fix type:** both repos together. Add `generated_at` to `PODCAST_FEED_CONTRACT["_podcast"]` and to `FEED_CONTRACT_FEED_FIELDS`. The field is already written, so the existing writer test pins it with no new test code.

### 2. Legacy fallback (row 2)

- **Repo:** podcast only, `tests/test_podcast_generator.py`.
- **Under test:** `fetch_podcast_feed`, and the fallback branch of the script stage's `script/curate` segment. The branch is inline today; the test needs it lifted into a small function, which is the only refactor asked for here.
- **Fixtures:** (a) `requests.get` raises once, then returns a good feed. (b) `requests.get` always raises; category feeds and the scoring cache are stubbed with canned items. (c) a good feed whose items are all `_is_bonus: true`.
- **Expected:** (a) the retry succeeds and no fallback happens. (b) a `script/feed-fallback` degraded row exists; on slots 1 and 2 the stage exits 76 instead of building from category feeds. (c) stays on the curated feed and does not fall back.
- **Fix type:** podcast code change, not test-only.
- **Still open:** "stale beats nothing" settles row 1, not this one. Here the alternative to nothing is not an older copy of the right feed but a different source that skips the `[show]` and crime/op-ed exclusions. Waiting on slots 1 and 2 is worth it in this case, because the usual cause is a transient fetch error that the next rung clears. Whether the last rung may air from category feeds is an editorial decision.

### 3. Theme label drift (row 3)

- **Repo:** both.
- **Podcast, under test:** `fetch_podcast_feed` plus the theme override. **Fixture:** weekday 2, feed `_podcast.theme` set to a label that is not a `themes.json` name. **Expected:** a `script/feed-contract` degrade naming both labels, and `_theme_info(today_theme)` is not `None` (the show keeps its own name for config lookups).
- **Feed, under test:** `tests/test_podcast_feed_contract.py`, a new `theme_labels` tuple in `PODCAST_FEED_CONTRACT` pinned against the seven `label` values in `config/podcast_schedule.json`. **Expected:** a label edit fails CI until the tuple, and so the paired podcast change, is updated.
- **Fix type:** both repos together, and a data fix first: decide which Wednesday name is right and make `themes.json`, `ambient.json` and `podcast_schedule.json` agree.

### 4. Hung first rung (row 4)

- **Repo:** feed, `tests/test_podcast_feed_contract.py`, beside the `run_slot` test.
- **Under test:** the text of `generate-feed.yml`.
- **Expected:** the `build` job declares `timeout-minutes`, and the value is at most 45, so a rung killed at 06:45 leaves the queued 07:00 rung its ten minutes before 08:05.
- **Fix type:** workflow change plus the test, feed repo only. Check the longest recent `build` duration through the Actions API before picking the number.

### 5. Cache push gates the publish (row 5)

- **Repo:** feed, new cases in `tests/test_podcast_feed_contract.py` or a small `tests/test_workflow_shape.py`.
- **Under test:** `generate-feed.yml` against `.github/scripts/git_push_retry.sh`, both read as text.
- **Expected:** every file named in the "Commit cache and log files" loop matches a `GENERATED_PATTERNS` entry. This fails today on `TODO.md`.
- **Fix type:** feed repo only. Either stop the nightly staging `TODO.md` or split its generated half into its own file; listing it as generated would overwrite hand edits. Moving the deploy ahead of the commit is a separate decision, because it turns row 5 into row 6.

## Should the contract be versioned and consumer-validated?

**Yes to consumer-validated. No to a version number.**

A version field answers "did the shape change on purpose?", and the paired key lists with the writer's AST test already answer that at PR time. Nothing in this table was a shape change. Every row is a feed that is valid but wrong: old, empty, built from the wrong source, or carrying a value the reader cannot use. A version would have passed all nine.

The smallest design that covers them is one field and one check.

- **Field:** `_podcast.generated_at`, already written. Add it to both key lists. Add the seven theme labels to the writer's list (spec 3).
- **Check:** one function on the podcast side, called from `fetch_podcast_feed` in place of `_assert_feed_fresh` and `_check_feed_contract`. It asserts four things about the feed: the keys are present (today's check), `generated_at` parses and is under about 20 h old, `_podcast.theme` is a name in `themes.json`, and the feed has at least one non-bonus item.
- **Where it is loud:** in the podcast's `script/feed` segment, before any spend. A night-old build airs with a `script/feed-stale` degrade row (decided 2026-11-11: slightly stale beats nothing); only the existing 48 h article-age limit still aborts. An unknown label or missing key degrades and airs on the show's own defaults. The same rule goes on the fallback: it never runs without a row.
- **Not needed:** a schema file, a shared package, or a version handshake. One reader, one writer, one nightly file.
