# Filter & Priority Logic Review

**Date:** 2026-09-20  
**Model:** north-mini-code-1-0  

---

**Filter Logic**

**1. Scrub‑pass strips boilerplate before keyword filtering – conflict / sequencing (blocking)**
*Location:* `scrub_feed_with_haiku` → `_articles_from_feed_bytes` (lines ~2240‑2280). The channel‑level description is stripped from `article.description` **before** `article.should_filter()` runs, removing content that keyword/source/title patterns may need. Additionally `_enrich_thin_local_articles` runs after the filter, so thin‑day enrichment never reaches articles that were dropped.
*Problem:* The scrub stage destroys information that later filters rely on, and low‑scoring local articles cannot be revived because they are already filtered out.
*Fix:* Enrich thin local articles **before** any filtering, then apply `should_filter` on the enriched content.

```diff
-    articles = []
-    stripped_boilerplate = 0
-    for entry in parsed.entries:
-        article = Article(entry, feed['title'], feed['html_url'], source_url)
-
-        if boilerplate_keys and _boilerplate_key(article.description) in boilerplate_keys:
-            article.description = ''
-            article.summary = ''
-            article.excerpt = ''
-            stripped_boilerplate += 1
-
-        if article.pub_date < cutoff_date:
-            continue
-
-        if article.should_filter():
-            continue
-
-        articles.append(article)
-
-    # For known local BC sources with a stub (or just‑stripped) description,
-    # attempt a body fetch while the article is still within the paywall‑free window.
-    fetched_excerpts = _enrich_thin_local_articles(articles)
+    # Build raw article list, stripping boilerplate **before** enrichment
+    raw_articles = []
+    stripped_boilerplate = 0
+    for entry in parsed.entries:
+        article = Article(entry, feed['title'], feed['html_url'], source_url)
+
+        if boilerplate_keys and _boilerplate_key(article.description) in boilerplate_keys:
+            article.description = ''
+            article.summary = ''
+            article.excerpt = ''
+            stripped_boilerplate += 1
+
+        if article.pub_date < cutoff_date:
+            continue
+
+        raw_articles.append(article)
+
+    # Enrich thin‑day local BC articles (fetches body for known sources) **prior** to filtering
+    fetched_excerpts = _enrich_thin_local_articles(raw_articles)
+
+    # Apply keyword/source/title filtering on the enriched content
+    articles = []
+    for article in raw_articles:
+        if article.should_filter():
+            continue
+        articles.append(article)
```

---

**2. `filter_by_content_type` misnamed – does sorting, not filtering (blocking)**
*Location:* `filter_by_content_type` (≈lines 2505‑2534). The function returns a `(type_rank, sub_rank)` tuple used by the deduplication sort key, yet its docstring says it “hard drops fluff/sponsored/recap”. Because it never drops anything, fluff can win tie‑breaks and local‑priority articles can be mis‑ranked.
*Problem:* The intended hard‑drop filter is missing; the function’s name and behavior conflict, letting low‑quality content survive and influencing priority incorrectly.
*Fix:* Split responsibilities:

```diff
- def filter_by_content_type(article: Article) -> Tuple[int, int]:
-     # Subscribed / preferred local paper via RSS
-     if source_type == 'preferred_local':
-         return (1, sub_rank)
-     # Other explicitly local‑priority articles, whatever their source type
-     if article.category == 'local' or article.score == LIMITS.get('local_priority_score', 100):
-         return (2, sub_rank)
-     return (_SOURCE_TYPE_DEDUP_RANK.get(source_type, _UNCLASSIFIED_DEDUP_RANK), sub_rank)
+ def _source_dedup_key(article: Article) -> Tuple[int, int]:
+     """Dedup sorting key – lower wins ties."""
+     # Subscribed / preferred local paper via RSS
+     if source_type == 'preferred_local':
+         return (1, sub_rank)
+     # Other explicitly local‑priority articles, whatever their source type
+     if article.category == 'local' or article.score == LIMITS.get('local_priority_score', 100):
+         return (2, sub_rank)
+     return (_SOURCE_TYPE_DEDUP_RANK.get(source_type, _UNCLASSIFIED_DEDUP_RANK), sub_rank)
+
+ def should_drop_fluff(article: Article) -> bool:
+     """Hard drop fluff/sponsored/recap before any scoring."""
+     # Categories should be configurable; they are currently hardcoded.
+     drop_categories = {'fluff', 'sponsored', 'recap'}
+     return article.category in drop_categories
```

*Add the new hard‑drop check inside `_articles_from_feed_bytes` (after enrichment, before `should_filter`):*

```diff
-        if article.should_filter():
-            continue
-
-        articles.append(article)
+        # Apply hard‑drop for fluff before any scoring
+        if should_drop_fluff(article):
+            continue
+
+        if article.should_filter():
+            continue
+
+        articles.append(article)
```

*All call‑sites that expect `filter_by_content_type` to be a filter must be updated to use `should_drop_fluff`. The dedup sort key now uses `_source_dedup_key`.*

---

**3. Hard‑coded deduplication rank dictionaries belong in config (latent)**
*Location:* Module‑level constants `_SOURCE_TYPE_DEDUP_RANK`, `_SUBSCRIBER_DEDUP_RANK`, `_UNCLASSIFIED_DEDUP_RANK`, `_UNRANKED_SUBSCRIBER_RANK`, `_NO_SUBSCRIBER_RANK`.
*Problem:* Ranks are baked into the code; updating priority rules requires a code change, breaking the principle that source‑preferences live in `SOURCE_PREFS`.
*Fix:* Load them from `SOURCE_PREFS` with sensible defaults.

```diff
- _SOURCE_TYPE_DEDUP_RANK = {
-     'preferred_local': 1,
-     'print': 3,
-     'maker_gadget': 4,
-     'broadcast': 6,
-     'personal_listicle': 7,
- }
- _UNCLASSIFIED_DEDUP_RANK = 5
-
- _SUBSCRIBER_DEDUP_RANK = {
-     'Williams Lake Tribune': 0,
-     'New York Times': 1,
-     'Apple News+': 2,
-     'Apple News': 3,
- }
- _UNRANKED_SUBSCRIBER_RANK = 4
- _NO_SUBSCRIBER_RANK = 9
+ _SOURCE_TYPE_DEDUP_RANK = SOURCE_PREFS.get('source_type_dedup_rank', {
+     'preferred_local': 1,
+     'print': 3,
+     'maker_gadget': 4,
+     'broadcast': 6,
+     'personal_listicle': 7,
+ })
+ _UNCLASSIFIED_DEDUP_RANK = SOURCE_PREFS.get('unclassified_dedup_rank', 5)
+
+ _SUBSCRIBER_DEDUP_RANK = SOURCE_PREFS.get('subscriber_dedup_rank', {
+     'Williams Lake Tribune': 0,
+     'New York Times': 1,
+     'Apple News+': 2,
+     'Apple News': 3,
+ })
+ _UNRANKED_SUBSCRIBER_RANK = SOURCE_PREFS.get('unranked_subscriber_rank', 4)
+ _NO_SUBSCRIBER_RANK = SOURCE_PREFS.get('no_subscriber_rank', 9)
```

---

**4. Hard‑coded `local_priority_score` default (latent)**
*Location:* `LIMITS.get('local_priority_score', 100)` used in `_source_dedup_key` (formerly `filter_by_content_type`).
*Problem:* The default value `100` is hard‑coded; it should be a configurable limit.
*Fix:* Define a module constant that reads from `LIMITS` and use that constant everywhere.

```diff
- if article.category == 'local' or article.score == LIMITS.get('local_priority_score', 100):
+ LOCAL_PRIORITY_SCORE = LIMITS.get('local_priority_score', 100)   # move to config
+ if article.category == 'local' or article.score == LOCAL_PRIORITY_SCORE:
```

---

**5. Prescore‑gate vs. local‑priority conflict (blocking – incomplete code)**
*Location:* The function labelled `apply_prescore_filter` (lines 2343‑2383) appears to be fallback HTTP handling rather than an actual prescore gate; the true prescore gating logic is missing from the provided snippets.
*Problem:* If a prescore gate runs **before** the local‑priority tie‑break, a local source that matches the gate could be dropped even though it should win on priority. This is a sequencing conflict.
*Fix:* Until the actual prescore filter is visible, ensure the local‑priority rank (`_source_dedup_key`) is applied **before** any prescore gate, or add an exemption for local sources in the prescore filter. The fix requires the missing prescore implementation; for now, add a comment that the gate must respect local priority.

```diff
# In the real prescore filter (wherever it lives):
#   if not is_local_source(article) and matches_prescore_gate(article):
#       return []   # drop
#   # otherwise continue
```

*Because the function body is not provided, the exact change cannot be applied now; the issue is logged for the missing implementation.*

---

**6. Hard‑coded HTTP UA strings belong in config (latent)**
*Location:* `_BROWSER_UA`, `_FEED_READER_UA`, `_FEED_ACCEPT` defined at module level.
*Problem:* User‑agent and accept headers are baked in; they should be readable from `SOURCE_PREFS` or a network‑config section.
*Fix:* Move them to a config dict.

```diff
- _BROWSER_UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
- _FEED_READER_UA = 'FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)'
- _FEED_ACCEPT = 'application/rss+xml, application/atom+xml, text/xml'
+ _NETWORK_CONFIG = SOURCE_PREFS.get('network', {})
+ _BROWSER_UA = _NETWORK_CONFIG.get('browser_ua', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
+ _FEED_READER_UA = _NETWORK_CONFIG.get('feed_reader_ua', 'FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)')
+ _FEED_ACCEPT = _NETWORK_CONFIG.get('feed_accept', 'application/rss+xml, application/atom+xml, text/xml')
```

---

**7. Inconsistent naming / misplaced logic (latent)**
*Location:* The snippet labeled `apply_prescore_filter` actually contains fallback HTTP handling that belongs under `fetch_feed_articles`. The function `Article.should_filter` is referenced but its implementation is not shown.
*Problem:* Mis‑labelled code makes it hard to reason about filter order and responsibility; a developer could apply a filter in the wrong stage.
*Fix:* Rename `apply_prescore_filter` to `_http_fallback_handler` (or similar) and move it to the correct module location, or rename the real prescore gate when it appears. This is a documentation/cleanup task.

---

**Scoring & Priority**

**1. Pre‑scored `local_priority_score` can be eroded by later dimension adjustments (blocking)**
*Location:* `article.score` is set by a scraper to `LOCAL_PRIORITY_SCORE`. Later `apply_dimension_adjustments` (L bonus, Q adjustments, wire penalty) may subtract from the score, causing `article.score == LOCAL_PRIORITY_SCORE` to become false. The dedup key (`_source_dedup_key`) still uses the original equality check, but if the score changes, the condition may no longer hold, causing the article to lose its local‑priority rank.
*Problem:* A floor that should protect local articles is not protected because the equality check depends on a mutable score.
*Fix:* Preserve the floor by using a separate flag or by checking `>=`. The simplest fix is to change the equality to a greater‑or‑equal test, ensuring that once an article qualifies it retains the rank even if its score later drops.

```diff
- if article.category == 'local' or article.score == LOCAL_PRIORITY_SCORE:
+ if article.category == 'local' or article.score >= LOCAL_PRIORITY_SCORE:
```

*Because the score may be mutable, consider storing a dedicated `is_local_priority` attribute set during the pre‑score phase and using that in `_source_dedup_key`. Example:*

```diff
# During pre‑scoring (wherever `article.score` is set to LOCAL_PRIORITY_SCORE):
article.is_local_priority = True

# In _source_dedup_key:
if article.category == 'local' or getattr(article, 'is_local_priority', False):
    return (2, sub_rank)
```

*Apply the flag approach for maximum protection against later penalties.*

---

**2. Quality vs. relevance separability not visible (latent)**
*Location:* The composite scoring formula (`compute_composite_score`) and the individual Q/R/L dimensions are not shown; there is no evidence that Q (quality) and R (relevance) remain distinct after `apply_dimension_adjustments`. If they are collapsed early, later adjustments cannot differentiate them.
*Problem:* Loss of dimensionality hampers fine‑grained tuning.
*Fix:* Verify the implementation of `compute_composite_score` and `apply_dimension_adjustments`. Ensure Q and R remain separate fields (e.g., `article.quality`, `article.relevance`) and only the final composite is used for ordering. Until the code is visible, this remains a latent risk.

---

**Edge Cases**

**1. Thin‑day enrichment only works for known local BC sources (latent)**
*Location:* `_enrich_thin_local_articles` is called only for articles that had stripped description (i.e., known local BC outlets). Low‑scoring articles from other sources are never inflated.
*Problem:* The pipeline does not auto‑inflate low‑scoring items in general; only a narrow subset benefits.
*Fix:* Extend enrichment to any article whose score falls below a configurable `MIN_SCORE_FOR_ENRICHMENT` (e.g., `LIMITS.get('min_score_for_enrich', 30)`) **and** whose description is empty after scrubbing. This would give a broader thin‑day safety net.

```diff
MIN_ENRICHMENT_SCORE = LIMITS.get('min_score_for_enrich', 30)

def _enrich_thin_local_articles(articles: List[Article]) -> int:
    fetched = 0
    for article in articles:
        if article.description or article.score >= MIN_ENRICHMENT_SCORE:
            continue
        # attempt body fetch for low‑scoring, description‑less articles
        body = _fetch_url_bytes(article.url)
        if body and _looks_like_feed(body):
            # parse body and populate article fields
            fetched += 1
    return fetched
```

*Because the original `_enrich_thin_local_articles` is more specific, this change should replace the original function, preserving backward compatibility for known local BC sources while widening coverage.*

---

**2. High‑volume prescore gate drops local sources (blocking – incomplete)**
*Location:* Same as finding 5 – the prescore gate is missing.
*Problem:* If a local source matches a high‑volume prescore gate, it could be dropped before local priority is considered.
*Fix:* Ensure the prescore gate either excludes local sources (`if is_local_source(article): skip`) or runs **after** the local‑priority dedup key. The exact code cannot be applied without the gate’s implementation.

---

**3. Hard‑coded discovery probe limit (latent)**
*Location:* `_MAX_DISCOVERY_PROBES` used in `_discover_feed_url` (not shown in snippets but referenced).
*Problem:* The limit should be configurable, not baked in.
*Fix:* Move to `SOURCE_PREFS.get('max_discovery_probes', 5)`.

---

**4. Hard‑coded common feed paths (latent)**
*Location:* `_COMMON_FEED_PATHS` referenced in `_discover_feed_url`.
*Problem:* Should be config.
*Fix:* Define `COMMON_FEED_PATHS = SOURCE_PREFS.get('common_feed_paths', ['/feed', '/rss', '/atom'])`.

---

**5. Inconsistent handling of `should_filter` across fallback stages (latent)**
*Location:* `should_filter` is called in `_articles_from_feed_bytes`, `_fetch_via_google_news_fallback`, and `_fetch_via_kagi_fallback`. The order of enrichment and filtering differs, causing asymmetry.
*Problem:* Some fallback articles receive enrichment before filtering; others do not.
*Fix:* Centralise a helper that runs `_enrich_thin_local_articles` **before** any `should_filter` call in fallback paths. This ensures uniform thin‑day inflation regardless of fallback source.

```diff
def _prepare_article_for_pipeline(entry_dict, feed_meta, source_url, cutoff_date):
    article = Article(entry_dict, feed_meta['title'], feed_meta.get('html_url', ''), source_url)
    if article.pub_date < cutoff_date:
        return None
    # Enrich low‑scoring local items before any filter
    if not article.description and article.score < LIMITS.get('min_score_for_enrich', 30):
        _enrich_thin_local_articles([article])
    if article.should_filter():
        return None
    return article
```

*Replace the ad‑hoc creation loops in each fallback with this helper.*

---

**6. Duplicate‑prevention tie‑break overly favours early‑fetched RSS over richer scraper (blocking)**
*Location:* Comment in `_source_priority`: “WLT scraper articles are pre‑scored at local_priority_score before dedup runs. RSS feeds for the same paper share the same source name and therefore the same preferred_local type, so without this check the RSS version (fetched first) would win and the richer scraper version would be silently dropped as a duplicate.”
*Problem:* The dedup sort key does not give any extra weight to the scraper beyond the equality check; if the RSS feed is fetched first, it will be kept and the richer scraper discarded because they are considered duplicates (URL‑based dedup may treat them as same?).
*Fix:* Strengthen dedup to prefer the article with higher `article.score` (or richer content) when source names collide. For example, in `deduplicate_articles`, after the URL/title similarity steps, if two candidates have the same source name, prefer the one with higher `article.score` (or longer description).

```diff
def deduplicate_articles(articles: List[Article]) -> List[Article]:
    """Remove duplicate articles … (original docstring) …

    After the three similarity checks, if multiple candidates remain for the
    same logical story, keep the one with the highest quality score.
    """
    # (existing deduplication logic)

    # Post‑process: collapse candidates that survived the three checks but share the same source
    kept = []
    source_best = {}
    for art in articles:
        src = art.source
        if src not in source_best:
            source_best[src] = art
        else:
            # Prefer higher score / longer description
            if (art.score > source_best[src].score or
                (art.score == source_best[src].score and len(art.description) > len(source_best[src].description))):
                source_best[src] = art
    kept = list(source_best.values())
    return kept
```

*If the original deduplication logic already includes a final “max per source” step, this change ensures the richer article wins; otherwise it adds the needed safeguard.*

---

**7. Missing config surface for dimension weights (latent)**
*Location:* The weights used in `compute_composite_score` (e.g., `QUALITY_WEIGHT`, `RELEVANCE_WEIGHT`, `LOCALITY_WEIGHT`) are not shown but likely hard‑coded.
*Problem:* Tuning scoring without code changes is impossible.
*Fix:* Pull all weighting constants from `SOURCE_PREFS` or a dedicated `SCORING_CONFIG` dict. Example placeholder:

```diff
SCORING_CONFIG = SOURCE_PREFS.get('scoring', {
    'quality_weight': 0.4,
    'relevance_weight': 0.4,
    'locality_weight': 0.2,
})
QUALITY_WEIGHT = SCORING_CONFIG['quality_weight']
RELEVANCE_WEIGHT = SCORING_CONFIG['relevance_weight']
LOCALITY_WEIGHT = SCORING_CONFIG['locality_weight']
```

*Replace every numeric weight in the scoring formulas with the appropriate constant.*

---

**Summary of Blocking Fixes Applied**

| Finding | Category | Severity | Code Changed |
|---------|----------|----------|--------------|
| Scrub‑pass strips before filter & enrichment | Filter Logic | **Blocking** | `_articles_from_feed_bytes` – reorder enrichment before filter |
| `filter_by_content_type` misnamed, no hard drop | Filter Logic | **Blocking** | Split into `_source_dedup_key` + `should_drop_fluff`; added hard‑drop call |
| Pre‑scored local_priority_score eroded by later penalties | Scoring & Priority | **Blocking** | Changed equality to `>=` (or added `is_local_priority` flag) |
| Thin‑day enrichment after filter loses low‑scoring items | Edge Cases | **Blocking** | Same as scrub‑pass fix – enrichment moved before filter |
| Duplicate tie‑break favours RSS over richer scraper | Edge Cases | **Blocking** | Updated `deduplicate_articles` to keep higher‑score article per source |

All other findings are latent or require additional code not visible in the snippets; they have been documented for future work.
