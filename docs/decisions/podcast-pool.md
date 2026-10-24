# The podcast pool: holdover, theme scores and content exclusion

*Moved verbatim from CLAUDE.md on 2026-09-23. CLAUDE.md keeps the standing rules; this file keeps the incidents and the reasoning behind them. Read it before changing the code it describes.*

## The theme holdover bank must never fill the podcast candidate pool (gotcha 9)

`generate_podcast_feed()` caps its candidate pool at `POOL_CAP` (300) and exempts rescued/holdover articles from the quality sort. Holdover is *not* exempt from the cap itself: `FRESH_POOL_SHARE` (0.5) reserves half the pool for current-week articles and the bank is trimmed worst-first (by banked percentile) to fit. Without that reserve an oversized bank drove the direct-qualify allowance to zero, and the day's feed regenerated purely from holdover — newest item exactly `run_date − 7`, advancing one day per run. Banking is unconditional and percentile-based (`holdover_threshold` 12 means "top 88%"), so the bank grows ~70-100 entries/day/theme every run; `THEME_HOLDOVER_MAX_AVAILABLE_PER_DAY` (400) bounds the available side in `save_theme_holdover_cache()`. Set `PODCAST_POOL_DEBUG=1` to trace fresh-vs-holdover pool composition at every selection stage.

## The podcast pool cap must stay theme-aware (gotcha 10)

The direct-qualify half of `POOL_CAP` is filled from *two* ranked lists: `THEME_RESERVE_SHARE` (0.4) of the slots go to candidates at or above `THEME_RESERVE_MIN_PCT` (p80) of the day's theme, the rest by upstream `a.score`. `a.score` is the general-interest composite and is theme-blind by construction, so ranking on it alone cuts the most on-theme articles *before* theme scoring ever sees them: on 2026-08-30 the Thursday episode was built entirely from articles with raw charter scores of 10-20 while eight APTN First Nations stories at the 97th-99th theme percentile were dropped for scoring 47-57 upstream against a cutoff of 67. The reserve does not change the pool size, so it costs no extra API calls. Articles with no cached theme score default to percentile 0 and compete on quality as before.

## Percentile-normalized `_theme_score` cannot show charter collapse (gotcha 13)

Selection ranks *within* a theme (`normalize_theme_scores()`), so the top of a bad distribution is promoted to 90-100 no matter how poor the actual fit; the same Thursday episode showed `_theme_score` 90 for a Windows 11 performance-boost article whose raw charter score was 16. Every item therefore also carries `_theme_score_raw`, the un-rescaled charter output, and `validate_podcast_feeds.py` reports the top-10 mean against a floor.

**That floor is per theme, because the scale is.** The seven `scoring_prompt`s are independently worded over subjects of very different breadth, so their raw output is not one ladder. Measured top-10 means over the eight runs published 2026-08-30..09-01 are rank-stable and an order of magnitude apart at the ends — sunday 74-85, saturday 62-70, friday 61-69, monday 36-43, thursday 26-36, tuesday 16-22, wednesday 10-18. The original single global `MIN_TOP_RAW_MEAN` (25) drawn across that separated *broad themes from narrow ones*, not healthy from broken: it cut between Thursday and Tuesday, failed Tuesday and Wednesday on every run from the day it was added, and would still have passed a 50% collapse in Sunday.

**The conclusion originally drawn from that band was wrong, and gotcha 14 is the correction.** This note used to read Wednesday's 10-18 as a narrow charter honestly reporting weak fit. It was a scoring bug. `RAW_FIT_FLOORS` is per weekday, seeded at 0.6x each theme's observed minimum — but tuesday (9) and wednesday (6) were fitted to the *collapsed* scorer and are stale by construction. They are deliberately left un-raised: they still catch a true collapse, and raising them on prediction trades a floor fitted to real numbers for one fitted to hope. **Refit all seven off a measured month once the targeted rescore has been running**, the same way `_SPEECH_RATE_FITS` was refitted from the transcript sidecars in the sibling repo; the report prints every theme's measured value on every run, pass or fail.

## A theme's score is only meaningful if something can win it (gotcha 14)

`score_all_themes_at_ingest` rates one article against all 7 charters in a single Haiku response, which is cheap and, for the broad themes, fine. But a model asked for 7 numbers at once apportions one general-interest magnitude across them instead of applying each charter independently. Measured on the 2026-09-01 cache: **"Science, Wonder & the Natural World" was the best-fit theme for 82.4% of 2,004 fully-scored articles, and Working Lands, Repair Culture, Arts and Indigenous Lands were best-fit for zero of them.** Repair Culture's maximum over 2,121 articles was 35, against a charter whose own anchors put a teardown at 98 and a Raspberry Pi weather-station build at 68 — Hackaday was supplying ~44 hands-on hardware articles a week throughout, and "Reviving an SD Card With Shorted Capacitors" scored 11. Meanwhile an RCMP shooting story scored 41 on Working Lands, whose charter puts unrelated crime news in its 0-14 OUT OF SCOPE band.

**The consequence is that sourcing cannot fix a starved theme.** The effect is a fixed per-theme prior, not a reading of the material, so new forestry or repair feeds land in the same 5-12 band and stay below `min_score`. Anyone asked to "enrich" a low-scoring day should check the argmax before touching `feeds.opml`.

`rescore_underserved_themes()` re-asks the question one charter at a time for the days listed in `podcast_schedule.json` → `targeted_rescore`, reusing `score_articles_for_theme(..., force=True)` (which bypasses both the cached joint score and the Cohere Rerank branch — embedding similarity to the charter text is not a charter judgment either). Candidates come from two places, and **the source list is the load-bearing half**: keyword matching alone misses exactly the articles that matter, because trade-press headlines rarely restate their own beat — "Reviving an SD Card With Shorted Capacitors" contains none of Wednesday's 40 configured keywords. So a day's `rescore_sources` names outlets whose whole output is on-theme *by construction* (Hackaday, iFixit, The Northern Miner, Western Producer); anything broader belongs on the keyword path at `min_keyword_hits` (2, not 1, for the reason the sibling repo's `_build_strict_theme_keywords` exists — one generic word is not evidence). Popular Mechanics and Resilience.org were tried on the source list and removed: they spent the budget on indestructible diamonds and dietary guidelines.

Cost is bounded on three sides — `score_ceiling` skips what already scores well, `max_articles_per_run` caps a runaway day, and each entry is stamped `rescored` so the work is paid once. At the configured defaults that is at most 4 extra Haiku calls per run (40 articles per theme against a batch size of 30, for two days) while the backlog in the existing pool clears, settling to 1-2 once only each day's new articles are eligible. An article with **no** cached score yet is skipped rather than scored: it is still in flight in the async batch, and becomes eligible next run once there is a score to correct.

**The standing guard is `run_stats['theme_argmax']`**, not a floor: it records how many articles each theme wins and prints a warning naming any theme that wins none. A per-theme histogram cannot show this — each theme's own distribution merely looked narrow for months. A theme that is best-fit for zero articles is not a narrow theme; it is a theme the scorer has stopped reading the charter for.

## The podcast pool filters two subjects the category feeds keep (gotcha 18)

`podcast_content_exclusion()` drops op-eds and crime incidents from
`generate_podcast_feed()`'s candidate pool and nowhere else. "Is this worth
reading?" is what `q_gate` and the charters answer; "is this twenty-two minutes
of two hosts talking?" is a different question, and a crime incident fails it
however well reported — there is nothing for the hosts to weigh that is not
either speculation about a person or a recital of the police release. The
reader still gets the local RCMP story in `feed-local.json`.

Configured in `config/podcast_schedule.json` → `excluded_content`. Opinion is
the existing `content_type` label, so it costs nothing; `content_type_exempt_sources`
is the seam against `news_interests.txt`'s standing judgment that a Western
Producer column on equipment subscriptions is working-lands journalism rather
than a hot take. **Widen the exemption list, never the rule.**

**The crime classifier is fitted, not guessed.** The first version cut 20 of the
1,545 articles cached on 2026-09-18 and 11 were wrong: a gaming monitor "for
shooters", Windows drivers "on trial", "Lone Butte woman sees success in
competitive shooting", and an AI-hallucinated-witnesses story that is exactly
the show's beat. Three narrowing rules took it to 7 hits and 0 false positives:

- **The category gates it** (`categories`: local, news). A crime word inside an
  ai-tech story is describing the subject of the technology, not the story.
- **The title anchors it.** Primary subject is a question of placement, not
  volume — a headline states what a story is about, and the CPJ and Amnesty
  pieces that cite an arrest in their body are press-freedom and human-rights
  reporting.
- **Ambiguous terms need justice context.** 'shooting' is a sport and a verdict;
  'on trial' is a driver deprecation. The unambiguous list (stabbing, homicide,
  manslaughter, drug bust) stands on a title hit alone.

Exemptions clear an article ahead of all three and are the show's actual beats:
cybercrime is ai-tech material, MMIWG and residential schools are Indigenous
Lands material whose subject is the system rather than the incident, a Wildlife
Act sentencing is Wild Spaces, and licence-plate cameras are a surveillance
story. **Refit against the live pool, never against appetite** — missing one
blotter item costs a thin roundup entry; a false positive deletes the day's
strongest story with nothing in the log naming it, which is why the filter
prints its own breakdown.

**Refit 2026-09-23** against 1,515 cached articles, after two Quesnel court
stories led a Working Lands roundup: sentencing, jail and plea phrasing joined the
incident list (4 new catches, 0 false positives), and the "Local Journalism
Initiative" byline is stripped before the exemption check — it matched
`journalism` and cleared local court stories wholesale.

Applied at **one** choke point, after the fresh, rescued and holdover pools
merge. Filtering at intake would bake the rule into `podcast_articles_cache.json`,
so widening a keyword list would leave every already-banked article uncaught.
The sibling repo's `article_holding.json` is the one gap: articles held there
before this shipped were admitted under the old rule and age out on its 14-day
window.

## The pool honours the gate's reject verdict (2026-10-13)

The candidate branch captures the pool **before** the scrub applies the quality
gate's `gate_reject`, on purpose: an article the main feed drops may still score 90 on
a theme. But nothing in the pool step ever read the verdict, so the rubric — the
built-in subjects and every line in `config/standing_preferences.txt` — never reached
the show, although that file's header said it did. On 2026-10-12 a Mother Jones piece
the gate had rejected was a deep-dive source, the day after Mother Jones went into
`blocked_sources`. A join of the pool to the gate's cached verdicts found 36 rejects
among 340 entries with a verdict, 17 of them in that week's feeds. Seven of the 42
aired stories the reader rated bad (since 2026-07-13) had come from the review's
"unfiltered" stratum, which is the gate's reject pile.

What changed:

- **The verdict rides with the entry.** `save_podcast_cache` stores `gate_reject`
  (new entries, and updated when an article is re-judged), the holdover bank copies it,
  and `CachedArticle` reads it. `None` means the gate never ruled, and is kept.
- **One choke point.** `podcast_content_exclusion()` returns `'gate_reject'`, before the
  opinion and crime checks, behind `excluded_content.gate_reject`. `enabled: false` turns
  every exclusion off, this one included (`_gate_reject_honoured()` answers for the
  choke point, the bank and the review page's pool label alike). Not at intake, so the
  rule can be widened without re-fetching. The run prints each dropped title once, up to
  `GATE_REJECT_LOG_CAP` (40, then one line saying the rest are only counted), because a
  rejected civic or election story is the loss worth seeing by name.
- **Blocked sources leave the cache.** `blocked_sources` was only checked at fetch time,
  so 29 Mother Jones items stayed in the pool and 51 in the bank. Both loaders now drop
  them through `_pool_source_excluded()`; see "`blocked_sources` applies to everything
  reused" in sources.md, which also removed the `hn` entry that blocked every
  "...Technica" feed.
- **The bank carries `content_type`, and takes the pool's latest ruling.** None of its
  entries did, so a banked op-ed bypassed the opinion filter. A row banked before an
  article was rejected (or before the rubric moved) kept its old verdict, and the story
  came back out of the bank when its pool entry aged out; `bank_articles_for_all_themes`
  now refreshes existing rows from the pool (`_refresh_bank_row`: a ruling replaces a
  ruling, a missing one never erases one). `update_theme_holdover` writes the same fields.
- **Deep scoring keeps the verdict.** It replaced the scored-cache entry whole and dropped
  `gate_reject`/`gate_rubric`/`gate_world` from every display-bound article, which were
  then judged again the next night. It now updates the entry in place (the same fix landed
  independently on main as part of the first-scrape-night fixes).
- **The pool and the feed are no longer independent for a gate reject.** The gate's
  false negatives were already measured (a floor of about 2.5% of "unfiltered" items had
  show days; `podcast_only` verdicts could not be saved from 2026-10-01 to 2026-10-10, so
  it is a floor). Accepted by the reader on 2026-10-13. **No rating-derived exemptions:**
  the reader's review ratings are training data, not runtime pipeline input.

Crime refit, same day: `faces charges`, `facing charges`, `multiple charges`, `loaded
firearms`, `firearms and drugs` joined the **ambiguous** tier. The three `charges`
phrases satisfy the justice-context test by themselves (`charges` is a context term, as
it already was for `charges laid`); the two firearms phrases still need a police, court
or Crown term. Against the 4,706 unique live pool and bank items they add one hit, an
aired Quesnel story, and no false positives. A vehicle collision is not a crime incident and
the rule is not widened for it; the standing line "Police blotter and crashes" covers
it, and clears those stories from `feed-local.json` too (the reader's choice).

**The verdict is a snapshot, so a new rubric line arrives gradually.** The gate judges
only articles new to its 48-hour cache, and a rubric change re-asks only those. A pool entry
or bank row older than that takes the new ruling only when the article is judged again, so
the 7-day pool and 28-day bank (about 19,000 rows with no verdict at all on 2026-10-13) run
down over those windows rather than at once. The first nightly run after a rubric change
re-asks every article in the gate window (about 42 calls against 19-28, roughly a cent).

Crime exemptions, same day (review): `candidate(s)`, `election(s)`, four B.C. natural-resource
Acts (a regulatory prosecution is Working Lands material), `search and rescue` and `SAR` clear
an article ahead of the incident rules. The 2026-10-13 refit was measured on the cached
corpus only, and the two shapes it missed (a candidate who "faces multiple charges", a company
charged under the Fisheries Act) are the argument for widening the exemption list rather
than the rule.

## Theme keywords match whole words (2026-10-24)

`_keyword_matches` picks the bucket an article fills first in its day's feed (keyword-matched
before bonus), so a false hit outranks on-theme material. The 2026-10-23 Friday (Wild Spaces)
feed carried a B.C. election poll and a Six Flags roller-coaster death as keyword matches,
from bare `trail` ("campaign trail") and `park` ("amusement park"), and the show built its deep
dive from them. The matcher was a substring test, so the same week's pool also had `nation`
hitting "international", `mill` hitting "million", `zine` "magazine", `bat` "battery",
`science` the `sciencealert.com` URL and `Likely` (the town) the adverb.

`_keyword_pattern` now matches whole words with an optional plural; a trailing `*` opts a
keyword into word endings (`flood*`, `research*`), still anchored at the start of a word so
`evolution*` never hits "revolution". Bare words with a common second sense became phrases:
`park` → `national park`, `provincial park`, `BC Parks`…; `trail` → `trail running`,
`trailhead`, `hiking`…; Thursday's `guardian` → `guardian program`, `Indigenous guardian`…;
Saturday's `Likely` → `Likely, B.C.`; Sunday gained `scientist` for the hits the URL used to
supply. Measured on the 4,466-article pool and the week's seven feeds: every article that
lost its last keyword hit was read, and the real stories lost were a handful of marginal ones
(an e-bike "trail to town" review, a Vancouver Island park closure over ancestral graves).

The theme score on the poll (raw 56) was Cohere Rerank, not the Haiku charter: Rerank reads
only the first 400 characters of the `scoring_prompt`, and Friday's "general political news →
0–20" clause starts at character 775. Targeted rescore skipped it twice over (56 is above
`score_ceiling` 55; one keyword hit is under `min_keyword_hits` 2). That is unchanged here.
