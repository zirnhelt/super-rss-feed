# Scoring: ranked slot fill, fitted weights and the review corpus

*Moved verbatim from CLAUDE.md on 2026-09-23. CLAUDE.md keeps the standing rules; this file keeps the incidents and the reasoning behind them. Read it before changing the code it describes.*

# Ranked Slot Fill (`apply_feed_slot_allocation`)

Feed selection is a **ranking** problem, and for a long time it was solved with a
floor. Everything at or above `min_score_for_category` shipped, everything below was
cut, and `limits.min_per_category` patched back the categories that came out empty.

That makes feed size a function of where the day's scores happened to land — the
funnel swung between 50 and 101 articles a run — on a scale whose top band (>=80)
holds ~4% of the pool and whose 30-49 band holds ~50%. It also meant the floor could
not be tightened without starving a niche category, or loosened without flooding
`news`, so the one knob had to serve two purposes and served neither.

Now every category is filled best-first:

- **Pass 1 fills `min_slots` regardless of the floor.** This is what the
  `min_per_category` rescue did, folded in — one mechanism rather than a filter and
  its apology. Those quotas moved into `feed_slots.json`'s `min_slots` (ai-tech 5,
  homelab 3, science 3, scifi/wellness/homestead 2) and the `min_per_category` key is
  gone; a live config key nothing reads is a knob that silently does nothing.
- **Pass 2 fills to `max_slots`, floor-respecting.** Past the guarantee the floor is a
  real quality bar again.

**The floor still bounds quality; it no longer determines volume.** When `FEED_SLOTS`
is empty the old hard-floor filter is the fallback, so a missing config degrades
rather than shipping an unranked pool.

# Weights are fitted, `w_local` is not

`config/scoring_weights.json` was refitted against the 1,193 good/bad ratings by
5-fold CV on the rows carrying real Q/R/L. `news` had been `w_quality 0.65 /
w_relevance 0.15` — two thirds of the weight on the weaker dimension, and the blend
scored **below both of its own components** (composite AUC 0.544, quality 0.527,
relevance 0.609). It is now `0.15 / 0.65 / 0.20`, `general` `0.20 / 0.60 / 0.20`.

**Two things the fit asked for were deliberately not done**, and this is the part to
re-read before refitting:

- **`w_local → 0`.** The optimizer wants it in both heads because local articles are a
  small share of ratings. It encodes an editorial commitment — this is a Cariboo feed
  — not a prediction, and `apply_dimension_adjustments` routes the local keyword bonus
  through the `L` dimension, so zeroing the weight would silently disable local
  boosting entirely. Pinned at 0.20.
- **`w_quality → 0`.** Every fold picks it, and it is a range-restriction artifact:
  `q_gate` has already selected on quality by the time an article gets dimensional Q,
  so residual Q looks uninformative *conditional on surviving the gate*. Local
  articles bypass the gate, which is exactly where Q is still doing real work. The
  conservative Q=0.15/0.20 captures ~83% of the available AUC gain and keeps that.

The weights are **not** in `config/calibration_bounds.json` and should stay out: the
calibration agent tunes against pipeline histograms, and these are fitted against
ground-truth ratings.

## `q_gate` cannot ration relevance scoring (gotcha 16)

The deep-scoring queue decides which
articles ever get a real `relevance` score; anything below the slice cap keeps
`q_gate` as its score for good. `news` gets `2 × max_slots` = 50 slots against ~600
survivors, and the queue was sorted purely by `q_gate` — so ~550 news articles a
night never had relevance computed at all. Measured against the review corpus that
is the wrong signal to ration on: within news gate-only rows `q_gate` separates
kept-from-discarded at **AUC 0.42, worse than chance**, while relevance manages 0.76.

Sorting purely by interest rank is the opposite failure and is why the `q_gate` sort
was written — `news` is a broad survey category and a personalized queue drops the
day's biggest stories out of deep scoring. So the slots are **split**, not
reassigned: `NEWS_INTEREST_RESERVE_SHARE` (0.4) of the queue goes to interest rank
and the rest stays newsworthiness-first, the same shape as `THEME_RESERVE_SHARE` in
the podcast pool. `_interleave_reserved` holds the share at **every prefix length**,
because the consumer truncates the list — a reserve honoured only in the tail is a
reserve of nothing.

## The review corpus is a quota sample and its raw rates mean nothing (gotcha 15)

`review.html`
takes a fixed handful from each score band plus up to 10 scrub rejects, so the
corpus-wide good-rate describes the sampling design, not the feed. On 2026-08-25
`SHOW_BUCKETS` additionally dropped `high` and `mid`, which made every subsequent
rating a near-miss or a reject and left **no way to detect a quality regression at
the top of the feed, because the top was never shown**. The audit read 23.9% good
/ 67.5% bad on a feed measuring ~41% good once reweighted, and 563 of those 881
"bad" verdicts were on articles the scrub had correctly rejected — the pipeline
working, counted as the pipeline failing.

Every review item now carries `_stratum_weight` (pool size / number sampled from
that stratum) and `_shipped`, `SHOW_BUCKETS` covers all five strata again, and
`article_review_audit.py:stratified_estimate()` reports per-stratum rates plus a
reweighted estimate with its coverage. **Rates within a stratum are unbiased; the
corpus-wide rate is not.** Never compare across strata without reweighting, and
never quote the headline good-rate as a feed quality number.

The same report's `theme_routing` root-cause split is measuring a counterfactual:
`today` is the weekday the rating was made, not a routing decision, and
`podcast_routed` is **0** — essentially every rated article comes from a *category*
feed, so "the theme scorer already preferred your day" is not evidence of a bug in
`generate_podcast_feed()`. The theme-scorer disagreement half is still real signal.

## Source-level verdicts must count `interesting`, not just `good` (gotcha 17)

Filtering the
rating corpus on good/bad alone showed nine outlets with zero good ever and made
them look like free cuts. Four of them (Edge, Ideal Home, Domino, Country Life) carry
`interesting` ratings; blocking them would have removed material the reader wanted.
Only three outlets have zero positive rating of **any** kind at n>=8, where the
rule-of-three upper bound on their true positive rate is <=37.5%: Rolling Stone (24),
The New Yorker (9), Cottage Life (8). Those are in `filters.blocked_sources`. Two
more (The Atlantic n=5, Live for the Outdoors n=6) are held back as too thin.

## The reject rubric's scoped rules leak (2026-09-23)

The gate sees each article as `[category]` plus title, and one rubric covers every
category. The "Fluffy AI/tech" rule said *ONLY for ai-tech or homelab*, but its
wording ("raises $X million", "valued at", "goes public") matched business headlines
tagged `[news]`, and Haiku applied it there anyway: over two nights it flagged ~20
mining, commodity and tech-finance items ("Capstone sells Mexican mine", "Cameco …
Westinghouse listing", "Province invests $11M in … critical mineral processing").
"Deals/promotions" had the same risk, since a takeover is also called a deal.

The fix names the scope in both directions (the rule never applies to any other
tag) and makes "deals" retail. The reader's ratings still reject most routine
mining news (Northern Miner 10 good / 16 bad: financings, drill results, sponsored
posts, foreign takeovers bad; BC and Canadian policy, industry structure good), so
that judgment moved into `config/standing_preferences.txt` as an explicit line with
its own KEEP clause, instead of riding on a misapplied AI rule.

The same night the US-politics line (PR #308) dropped "Carney Downplays Trump's
Threat", "Trump rejects AI regulation … in U.N. address" and a story on NIH
funding. Its KEEP clause now names a Canadian principal actor, a US leader's
AI-policy stance and US science agencies explicitly. The model does not generalise a
KEEP clause's examples; list the case or expect it flagged.

Verdicts are cached with the score for 48 h, the same as the lookback window, so a
rubric edit reaches every article by the second night.

**Follow-up, 2026-09-24.** The first run under that fix still dropped B.C. election
coverage: "A fourth B.C. NDP cabinet minister says she won't seek re-election", "B.C.
Greens Leader Lowan to run in Saanich North", and the night before "Key dates for the
2026 B.C. provincial election". The US-politics line lists "elections and campaigns",
and Haiku read that as elections anywhere. The line now opens "(the United States
only, never Canada)", and the pipeline's own rubric carries a KEEP for Canadian
politics at every level, which no reader line can override. These drops also reach
the podcast pool, whose Saturday show covers the local election.

The same night showed the cache hides a rubric fix: a verdict is cached with the
score for 48 h, so a story wrongly rejected stays rejected for as long as it is
eligible. Each verdict now carries `gate_rubric`, a hash of the rubric that made it,
and a verdict from a different rubric is asked again (verdict-only; the cached score
is kept). The cost is one re-verdict pass over the cache when the rubric changes,
including when a standing-preference PR is merged: about 10 to 35 Haiku batches, a
few cents.
