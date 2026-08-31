# Weekly Feed Maintenance Guide

This document covers how to monitor, tune, and expand the podcast-themed feeds
introduced in March 2026. It is aimed at the weekly review cycle: scan for
broken sources, check theme coverage, and improve keyword lists over time.

---

## What the new feeds add

Each `feed-podcast-{day}.json` now emits three extra fields per article:

| Field | Type | What it means |
|---|---|---|
| `_keyword_matches` | int | How many of the day's theme keywords appear in title + summary |
| `_boosted_score` | int (0–100) | `min(100, hits × 20 + quality × 0.3)` — used by the podcast generator to pick deep-dive articles |
| `_is_bonus` | bool | `true` when zero theme keywords matched (and, on Saturday, the source is not a Cariboo local outlet) |

The `_podcast.theme_description` envelope field now holds a 2–3 sentence
editorial angle per day (not just the short one-liner).

These fields are computed at feed-generation time from the `keywords` array
in `config/podcast_schedule.json`. **That file is the main thing to tune.**

---

## Weekly review checklist

### 1. Check for broken sources (5 min)

Open `TODO.md` — the AUTO section is regenerated on every run and shows
feed errors from the last 7 days.

Most failures now recover on their own. `fetch_feed_articles()` escalates
through **free** recovery before it will spend anything, and it remembers
failures across runs so a dead source stops costing money:

| Failure | What the curator does, in order |
|---|---|
| **403 Forbidden** | Retries once as a self-identified feed reader (`SuperRSSCurator/1.0`). WAFs that block a browser UA from a datacenter IP routinely allowlist declared aggregators. |
| **404 / 410** | Rediscovers the feed: reads `<link rel="alternate">` off the site, then probes conventional paths (`/feed/`, `/rss.xml`, `/atom.xml`, …). A candidate is adopted only if it parses as a feed **with entries**, so a soft-404 HTML page can never be mistaken for one. |
| **DNS / timeout / 421 / 500** | No free recovery exists — goes straight to the fallback chain. |
| **429 / 503** | Honours `Retry-After` and skips the feed until it expires. Never reaches the paid fallbacks. |

Only if free recovery fails does it try Brave → Kagi → Google News. Feeds
that have failed **3 runs in a row** are cut off from Brave and Kagi entirely
and get the keyless Google News fallback only — Brave hits its 402 quota
ceiling mid-run, so a call spent re-confirming a dead source is a call denied
to a recoverable one. Feeds whose failure cannot resolve itself (dead DNS,
404 with no rediscoverable feed) additionally back off polling: 6 h at 2
consecutive failures, 24 h at 4, 72 h at 8. Any successful fetch clears all
of it.

That gets the *run* through a broken feed. Repairing `feeds.opml` itself is
the Sunday `feed-health` job (`integrate_discoveries.py --heal`), which takes
the four follow-ups that used to be yours and does them:

| What you used to do by hand | What the heal pass does |
|---|---|
| Paste a `↩ feed moved → <url>` line into `feeds.opml` | Re-fetches the rediscovered URL and, if it still parses as a feed with entries, writes it into the OPML with `relocatedFrom` recording where it came from |
| Decide what replaces a `⏸ backing off` source | Retires it — `type="rss"` becomes `type="retired"`, which `parse_opml()` stops selecting |
| Swap a hostile-WAF outlet for a Google News search feed | Does exactly that, keeping the original as a retired outline, but only if the search feed carries an article from the last 30 days |
| Notice a source came back and re-add it | `recheck_retired()` probes retired outlines weekly and restores any that answer, deleting the Google News stand-in that replaced it |

Read `FEED_HEALTH_LOG.md` for what it did and why; each row carries the
evidence that qualified the feed. Every change is one word in the OPML to
reverse, and a retired feed is still visible to discovery, so nothing you
retired comes back as a "new" find.

So what still needs you:

- **A feed you disagree about.** The agent is deliberately conservative — it
  needs 3 failures across 2+ days and a live probe before acting — but it
  cannot know that a Google News stand-in reads worse than the real feed did.
  Flip `type="retired"` back to `"rss"`, or delete the `GN …` outline.

- **415 Unsupported Media Type** — feedparser is sending a content-type the
  server rejects. The probe sees the same rejection and will retire the feed;
  if the URL opens fine in a browser, a Google News search feed for that
  outlet is the better replacement.

- **Timeout / RemoteDisconnected** — usually transient, and the backoff ladder
  does not apply (they can resolve on their own). A feed that times out for
  3+ consecutive days will clear the heal floor and be retired on Sunday.

- **A week where nothing was healed and the log says `🛑 None of N known-good
  feeds is reachable`** — that is the network sanity guard: the runner itself
  could not reach anything, so the agent refused to read that as N dead
  outlets. Nothing was changed. If it repeats, the runner's egress is the
  problem, not the feeds.

**Never add a WordPress comment feed** (`/comments/feed/`, or a title
starting "Comments for "). They carry reader comments, not articles, and are
disproportionately WAF-blocked. `integrate_discoveries.is_comment_feed()`
rejects them at the discovery gate; four had already slipped into
`feeds.opml` and were removed.

**For sources added in the March 2026 batch**, pay particular attention to:

| Source | Theme | Known risk |
|---|---|---|
| My East Kootenay Now | Saturday | Same network as My Cariboo Now — watch for 403 |
| APTN News | Thursday | No known issues yet |
| Spacing Magazine | Monday | No known issues yet |
| CBC Arts | Monday | CBC RSS URLs change occasionally |
| GN BC Wildfire and Conservation | Friday | Google News feeds — monitor for relevant volume |
| GN BC Working Lands | Tuesday | Google News feeds — monitor for relevant volume |
| GN Rural BC Infrastructure | Sunday | Google News feeds — monitor for relevant volume |

If a new source fails immediately, consider whether the `mycariboonow.com/feed`
pattern can be replaced with a Google News search feed targeting the same outlet:

```xml
<!-- fallback example for My East Kootenay Now if it 403s -->
<outline type="rss" text="GN East Kootenay Now"
  xmlUrl="https://news.google.com/rss/search?q=site:myeastkootenaynow.com&hl=en&gl=CA&ceid=CA:en"
  htmlUrl="https://news.google.com" />
```

---

### 2. Check new-source contribution (10 min)

Open the current day's `feed-podcast-{day}.json` and look at `_keyword_matches`
across articles. A healthy feed has:

- At least a few articles with `_keyword_matches ≥ 2` near the top
- `_is_bonus: false` on most theme articles
- Local Cariboo sources present in Saturday's feed with `_is_bonus: false`
  even when `_keyword_matches` is 0 (the Saturday exemption)

If the new Google News feeds are producing content but it is all landing in
`_is_bonus: true`, the keywords for that day probably need broadening — see
the tuning section below.

If a new source produces **zero articles** after 3 days, check:
1. The feed URL in `feeds.opml` is reachable
2. The source is not in `config/filters.json` blocklist
3. Articles from the source score ≥ 15 (the `min_claude_score` floor in
   `config/limits.json`)

---

### 3. Tune keywords (when `_boosted_score` is consistently low)

Keywords live in `config/podcast_schedule.json` under each day's `keywords`
array. They are matched case-insensitively against `title + summary`.

**When to add keywords:**
- You notice articles about a relevant topic are landing with
  `_keyword_matches: 0` and `_is_bonus: true`
- A new source covers a topic not yet in the list (e.g. APTN News mentions
  "guardian program" and "UNDRIP" often but Thursday only matches on
  "indigenous" and "first nations")

**When to remove keywords:**
- A keyword is pulling in off-topic articles as theme matches (check
  `_keyword_matches > 0` articles that are clearly wrong)
- A keyword is too generic (e.g. "community" on Wednesday pulls in anything)

**Format** — keywords are plain strings, matched as substrings:
```json
"keywords": [
  "forestry", "ranching", "AgTech", "precision agriculture"
]
```

Multi-word phrases work: `"precision agriculture"` only matches that exact
phrase. Prefer specific multi-word terms for precision; short words
(e.g. `"farm"`) for recall.

**The `_boosted_score` formula:**
```
_boosted_score = min(100, keyword_hits × 20 + ai_quality_score × 0.3)
```

An article with 2 keyword hits and ai_score 70 gets `min(100, 40 + 21) = 61`.
Three hits pushes any article to 60+ regardless of quality score. This means
**keyword tuning has more impact than source quality tuning** for theme
alignment.

**`anti_keywords`** (optional, per-day array) subtract from `keyword_hits`
before the formula above and before `_is_bonus`/`_keyword_matches` are
computed, floored at 0:

```
keyword_hits = positive_keyword_hits - anti_keyword_hits   # floored at 0
```

Use this when two theme days have overlapping keyword sets and articles
dominated by the *other* day's topic are being bucketed here as strong
matches. For example, Sunday (Science) penalizes Indigenous-governance terms
(`"data sovereignty"`, `"OCAP"`, `"land title"`, `"treaty negotiation"`, etc.)
that really belong to Thursday (Indigenous Lands & Innovation).

---

### 4. Update `theme_description` when editorial framing shifts (as needed)

The `_podcast.theme_description` field in each feed is the text passed to
podcast hosts as framing context. It lives under `theme_description` in
`config/podcast_schedule.json`.

Update it when:
- A theme's editorial angle shifts seasonally (e.g. Friday shifts from
  wildfire prep in summer to avalanche/winter access in winter)
- A major local story changes what "Cariboo Voices" means for several weeks
- The podcast generator's prompts change and need new framing alignment

Keep it 2–3 sentences. It is read by Claude when generating the episode, so
clarity and specificity about the Cariboo context matter more than elegance.

---

### 5. Add new sources

**To add a direct RSS source:**

1. Confirm the feed URL works: `curl -I <url>` or open in browser
2. Add to `feeds.opml` with a comment explaining the theme it supports:
   ```xml
   <!-- Haida Gwaii Observer: coastal BC community news — supports Friday/Saturday -->
   <outline type="rss" text="Haida Gwaii Observer"
     xmlUrl="https://www.haidagwaiiobserver.com/feed/"
     htmlUrl="https://www.haidagwaiiobserver.com" />
   ```
3. Add to `config/source_preferences.json` under `source_map` if it is a
   print/broadcast/preferred-local source:
   ```json
   "Haida Gwaii Observer": "print"
   ```
4. Run locally or let the next CI run pick it up. Check `TODO.md` the next day.

**To add a source you can read paywall-free (Apple News+, direct subscription):**

Add it under `subscriber_access.sources` in `config/source_preferences.json`,
keyed by the exact OPML `title`:

```json
"The New Yorker": "Apple News+"
```

The curator then skips the paywall scoring penalty, prefixes the item title with
🔓, and sets `_subscriber_access` on the JSON Feed item.

`url` defaults to the publisher URL — the only link that resolves on every
device and in every reader. For `Apple News` labels the tiered resolver then
tries to upgrade it.

### The tiered Apple News resolver

`resolve_apple_news_url()` returns the best available `https://apple.news/…`
link and which tier produced it:

| Tier | Source of the ID | Lands on | Promoted to `url`? |
|---|---|---|---|
| `article` | `A…` scraped from the publisher's own page | the article itself | yes |
| `channel` | `T…` scraped from the page, else `apple_news_channels.sources` in `config/source_preferences.json` | the publication's channel | only if `use_as_primary_link` |
| — | nothing found | publisher URL is kept | n/a |

Both tiers are https universal links: Apple devices hand off into the News app,
everything else follows Apple's web fallback. An article-tier link is strictly
better than the publisher URL everywhere, so it is always promoted. A
channel-tier link is not — in a desktop browser it lands on the channel rather
than the piece you clicked — so by default it only rides along as
`_apple_news_url`, rendered as a 📰 badge in `index.html` and `review.html`.
Flip `apple_news_channels.use_as_primary_link` to `true` if you read the feed
almost entirely from Apple devices.

When `url` is promoted, the publisher URL moves to `external_url` and `id`
stays the publisher URL — it is the identity key behind cross-run dedup, the
shown/scored caches and the feedback ledger. **Anything reading a written feed
back in must call `item_source_link(item)`** (`external_url or url`), never
`url` directly, or those articles stop matching themselves between runs and
accumulate a duplicate every night. `feed-review.json` opts out of the swap
entirely: every rating is keyed on `art.url` and has to stay joinable with
pipeline links, so Apple News is only ever a badge there.

### Where the IDs come from

Apple assigns `A…` and `T…` IDs opaquely. They cannot be derived from a
publisher URL and the Apple News API is scoped to a publisher's own channel, so
there is no reverse lookup — an ID has to be found in the wild or copied by
hand. **Never construct one**; a wrong ID is a dead link.

`extract_apple_news_ids()` scrapes them from the article HTML that
`fetch_images.py` is already fetching for Open Graph images, so harvesting costs
no extra request and no API spend. An ID is only accepted when the page carries
exactly one distinct candidate of that kind — a related-articles rail makes the
article ID ambiguous, and guessing wrong sends you to the wrong story. Results
persist in `apple_news_cache.json` (article IDs pruned at 14 days, channel IDs
kept forever, first sighting wins).

Coverage grows on its own: channel IDs only need to be seen once to cover every
future article from that publication. For publications whose pages never expose
one, add it by hand — on an Apple device, News app → the channel → ••• → Share
Channel → Copy Link, then take the token after `apple.news/`.

### Why there is no `applenews://` deep link

A previous version set `url` to `applenews://search?term=<title>`. That URL form
does not exist. Apple News registers the `applenews://` scheme, so iOS and macOS
launch the app, but the app only understands the path form mirroring an
`apple.news` share link (`applenews:///A-oPQmJNfTyi9oHKs1xCY3w`) — there is no
search path. The app opened and did nothing. Feed readers were worse: a
non-`http(s)` scheme is never handed to the OS at all, so the link was inert in
Inoreader.

The only real article link is `https://apple.news/A…`. It is an https universal
link: Apple devices hand off into the News app, everything else redirects to the
publisher. Apple assigns the `A…` ID opaquely — it cannot be derived from a
publisher URL, and the Apple News API is scoped to a publisher's own channel, so
there is no reverse lookup. It has to be discovered, which is what the tiered
resolver does.

**To add a Google News fallback feed** (when no direct RSS exists):

```xml
<outline type="rss" text="GN BC Arts Council"
  xmlUrl="https://news.google.com/rss/search?q=%22BC+Arts+Council%22+OR+%22BC+arts+funding%22&hl=en&gl=CA&ceid=CA:en"
  htmlUrl="https://news.google.com" />
```

Google News feeds do not need a `source_preferences.json` entry — they surface
as individual outlet bylines after feedparser resolves the redirect.

**Sources still missing from the CLAUDE.md priority list** (as of March 2026):

| Source | Theme | Status |
|---|---|---|
| First Nations Technology Council | Thursday | No public RSS found; add GN fallback |
| BC Arts Council news | Monday | No RSS; add GN fallback |
| BC Cattlemen's Association | Tuesday | Covered by GN BC Working Lands feed |
| BC Lumber Trade Council / COFI | Tuesday | Covered by GN BC Working Lands feed |
| BC Wildfire Service direct | Friday | No RSS; covered by GN BC Wildfire feed |
| BC Parks news | Friday | No RSS; covered by GN BC Wildfire feed |
| Haida Gwaii Observer | Friday | Check for RSS; direct feed preferred |
| Rural Municipalities of BC / UBCM | Sunday | Covered by GN Rural BC Infrastructure |
| Connecting BC broadband updates | Sunday | Check for RSS |

---

## Source health at a glance

The `_keyword_matches` distribution in a day's feed is a quick health signal:

| Pattern | Diagnosis |
|---|---|
| Most articles have `_keyword_matches: 0`, high `_is_bonus` count | Keywords too narrow — broaden the list |
| `_boosted_score` is high but podcast quality is poor | Keywords too broad — remove generic terms |
| Saturday has local sources with `_is_bonus: true` | Bug: check `LOCAL_BC_SOURCES` set in `generate_podcast_feed()` |
| A theme day has < 10 total articles | Source volume is low — add more sources or a GN search feed |
| New source never appears in any feed | Check 403/415 errors in `TODO.md`; verify score ≥ 15 |

---

## Files touched by this maintenance cycle

| File | What to change |
|---|---|
| `config/podcast_schedule.json` | `keywords`, `theme_description` per day |
| `feeds.opml` | Add/comment-out RSS sources |
| `config/source_preferences.json` | Classify new print/broadcast/local sources |
| `TODO.md` (Notes section) | Record disabled sources and why |
