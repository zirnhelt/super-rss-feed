# Sources: feed health, rediscovery, comment feeds and article identity

*Moved verbatim from CLAUDE.md on 2026-09-23. CLAUDE.md keeps the standing rules; this file keeps the incidents and the reasoning behind them. Read it before changing the code it describes.*

# Feed Health Agent Safety

`integrate_discoveries.py --heal` is the only automation that edits the *feed list* rather than
config, so its bounds are about never losing a source by mistake.

**Evidence never decides anything on its own.** A feed becomes a *candidate* from failure
history — `feed_http_cache.json` counts, plus the last 7 days of `FEED_ERRORS.md` as a backstop
for a lost cache — and must clear both floors (`--heal-min-failures` 3, `--heal-min-days` 2)
before it is touched. What actually happens to it is decided by a **fresh probe against the
live network**, in the pipeline's own escalation order: still works → left alone; moved →
relocated; unreachable but still publishing → Google News stand-in; nothing answers → retired.

**Nothing is deleted.** Retirement flips `type="rss"` to `type="retired"`, which `parse_opml()`
stops selecting. The URL, title, reason and date stay in the file, `get_existing_feeds()` still
counts it so discovery cannot re-add it, and `recheck_retired()` restores it automatically once
the source answers again — removing any Google News stand-in that replaced it.

**A broken runner is not a week of dead outlets.** Every verdict is inferred from a failed
request, so before applying anything the agent probes up to 3 feeds with *no* failure history.
If none of them answers, the fault is local and the pass makes no changes at all. `--heal-max-feeds`
(25) caps the blast radius further, spending the budget worst-first.

Google News substitution additionally requires the search feed to carry an article from the last
30 days — the index still answers for a dead outlet, with years-old results, and adopting that
would quietly resurrect a source that stopped publishing.

## A rediscovered feed URL lives in the cache until the weekly heal promotes it (gotcha 11)

When `_discover_feed_url()` finds a moved feed mid-run it writes `resolved_url` into `feed_http_cache.json` rather than rewriting `feeds.opml`, because the OPML is user-curated and a curation run is the wrong place to edit it. The feed works again immediately but the fix is only as durable as the cache, so `--heal` re-verifies the resolved URL each Sunday and writes it into the OPML for real (recording `relocatedFrom`). If the resolved URL later fails it is cleared, so the next run rediscovers from the OPML URL rather than compounding one bad guess.

**That whole mechanism is inert unless `feed_http_cache.json` is persisted.** It is a runtime cache in a repo that gets a fresh checkout every run: until it was added to the gh-pages download, the `output/` copy and the commit list in `generate-feed.yml`, every failure count reset to zero nightly — the paid-fallback cutoff at 3 consecutive failures could never be reached, the backoff ladder never fired, and each moved feed was rediscovered again the next day. If failure counts ever read as implausibly low, check that plumbing first.

## WordPress comment feeds are not article feeds (gotcha 12)

`/comments/feed/` (title "Comments for …") carries reader comments: no headline, no body, nothing scoreable. Discovery used to score them like any other feed and four reached `feeds.opml`; they are also disproportionately WAF-blocked, so each cost a failed fetch plus a search fallback every run. `integrate_discoveries.is_comment_feed()` is the single predicate. Never add one by hand.

**A score threshold will never catch them, because they score well.** A comment
entry is titled `Comment on <Article Title> by <Name>`, so `score_articles_with_claude`
is reading the *host blog's* headlines and rating those — "Comments for Investing in
regenerative agriculture" scored 87.5. That number is a true statement about the blog
and a meaningless one about the feed, which is why the check is structural.

**The gate was correct and ran one stage too late.** It sat only in
`add_feeds_to_opml()`/`--heal`, so nothing reached `feeds.opml` — but
`feed_discovery.py` still fetched each one, spent Haiku on it, and wrote it into
`feed_discovery_report.json`, where the weekly report read it back as a source that
"warrants evaluation for inclusion". That recurred in W36, W37 and W38 of 2026 and
reads exactly like a repeat failure of the gate. It now also runs at the top of
`evaluate_candidates()` (one choke point for the OPML, Brave and Kagi paths, ahead of
the cache split so a stale cached score cannot smuggle one back) and in
`_probe_page_for_feeds()`, which drops the comment feed a WordPress post page
advertises beside its site feed — the site feed is on the same page, so the blog is
still discovered. That is how `mariaadey.com/feed/` was added in W37 while its own
comment feed was being recommended separately.

Two forms carry no `/comments/feed` marker and are covered by the title prefix and
the Blogger path respectively: WordPress serves a *per-post* comment feed at
`<post-slug>/feed/` (title "Comments on: …"), and Blogger uses `/feeds/comments/default`.

## Feed item `url` is not article identity (gotcha 7)

`url` is whatever link the reader should follow; whenever that is not the publisher URL, the publisher URL lives in `external_url` and `id` always stays the publisher URL. Any code reading a written feed back in must use `item_source_link(item)`, never `item['url']`, or those articles stop matching themselves across runs and duplicate nightly. See `FEEDS_MAINTENANCE.md` § "add a source you can read paywall-free".

## `applenews://search?term=` is not a real URL (gotcha 8)

It was tried and reverted; the scheme launches the News app but has no search path, and feed readers drop non-`http(s)` links entirely. Only `https://apple.news/…` works, and its ID must be **discovered, never constructed** — Apple assigns them opaquely and a fabricated ID is a dead link. `resolve_apple_news_url()` tiers a harvested per-article `A…` ID over a per-publication `T…` channel ID over the publisher URL; only the article tier is promoted to `url` by default. See `FEEDS_MAINTENANCE.md` § "the tiered Apple News resolver".
