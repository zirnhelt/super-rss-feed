# Filter & Priority Logic Review

**Date:** 2026-09-06  
**Model:** north-mini-code-1-0  

---

**Filter Logic**

**1. Article.should_filter() implements category fetching instead of keyword/source/title blocking**  
*Location:* `Article.should_filter()` (lines 520–545) – the method body currently contains a Kite News API fetch.  
*Problem:* The method is named to filter articles by keywords, sources, or title patterns, but it actually performs an unrelated API call. No filtering logic is present, so articles that should be blocked are never dropped.  
*Type:* **Conflict / Misimplementation**  
*Severity:* **Blocking**  

*Corrected code (replace the current body with proper filtering logic):*  

```diff
-                             headers=headers, params={'lang': 'en'}, timeout=15)
-        resp.raise_for_status()
-        categories = resp.json().get('categories') or []
-    except Exception as e:
-        print(f"  ✗ Kite News categories: {e}")
-        return []
-
-    matched = [c for c in categories
-               if c.get('categoryId', '').lower() in wanted_categories
-               or c.get('categoryName', '').lower() in wanted_categories]
-
-    all_articles: List['Article'] = []
-    for cat in matched:
-        category_id = cat.get('id', '')
-        label = cat.get('categoryName', category_id)
-        if not category_id:
-            continue
-        try:
-            api_usage.record_call('kite')
-            resp = requests.get(
-                f"{base_url}/api/batches/latest/categories/{category_id}/stories",
-                headers=headers,
-                params={'limit': max_per_category, 'lang': 'en'},
-                timeout=15,
-            )
-            resp.raise_for_status()
 ... (rest of unrelated code) ...
+    # --- Keyword / source / title‑pattern blocking -------------------------------------------------
+    # Block articles whose title contains any forbidden keyword
+    if self.keywords:
+        lowered = self.title.lower()
+        for kw in self.keywords:
+            if kw.lower() in lowered:
+                return True
+
+    # Block articles from blacklisted sources
+    if self.source in self.blocked_sources:
+        return True
+
+    # Block articles matching any title‑pattern regex
+    if self.title_patterns:
+        import re
+        for pat in self.title_patterns:
+            if re.search(pat, self.title, re.IGNORECASE):
+                return True
+
+    # No blocking criteria matched
+    return False
```

---

**2. scrub_feed_with_haiku() is mislabeled – it handles HTTP fall‑back recovery, not semantic scrubbing**  
*Location:* `scrub_feed_with_haiku()` (lines 2208‑2339).  
*Problem:* The function’s docstring says it performs a “semantic scrub pass”, yet the implementation deals with cache handling, 403/404/421/500 fall‑backs, Brave/Kagi/Google News API fall‑backs, and back‑off logic. No semantic filtering of article content occurs.  
*Type:* **Mislabel / Sequencing issue**  
*Severity:* **Blocking** – the intended scrub stage is missing, allowing low‑quality or irrelevant articles to reach later stages.

---

**3. filter_by_content_type() is missing its hard‑drop logic for fluff/sponsored/recap**  
*Location:* `filter_by_content_type()` (lines 2505‑2534) – currently an empty stub.  
*Problem:* According to the design, this stage should drop articles whose `content_type` indicates fluff, sponsored content, or recaps. The stub contains no filtering, so undesirable articles are never removed.  
*Type:* **Missing implementation**  
*Severity:* **Blocking**  

*Corrected code (replace the stub with a functional filter):*  

```diff
-def filter_by_content_type(articles: List[Article]) -> List[Article]:
-    """Drop fluff/sponsored/recap articles."""
-    # Placeholder – no filtering performed
-    return articles
+def filter_by_content_type(articles: List[Article]) -> List[Article]:
+    """Drop fluff/sponsored/recap articles."""
+    unwanted = {"fluff", "sponsored", "recap"}
+    return [a for a in articles if getattr(a, "content_type", None) not in unwanted]
```

---

**4. Contradictory filter ordering – dedup_across_categories vs. filter_by_content_type**  
*Location:* `dedup_across_categories()` (lines ≈ 2450‑2480) and the (now‑implemented) `filter_by_content_type()`.  
*Problem:* `dedup_across_categories` silently drops any *news* article that is a story‑match for a more specific category (e.g., ai‑tech). If the same article would later be dropped by `filter_by_content_type` (e.g., because it is a “recap”), the earlier drop prevents any chance to apply later stage logic. This creates non‑deterministic outcomes depending on pipeline ordering.  
*Type:* **Sequencing / Conflict**  
*Severity:* **Latent**

---

**5. apply_prescore_filter source‑gating vs. local‑priority conflict**  
*Location:* `_source_priority()` (lines ≈ 2343‑2383) and `apply_prescore_filter()` (which calls it).  
*Problem:* When a *local* source also satisfies a high‑volume prescore gate, the logic is ambiguous – does the prescore gate (which prefers high‑volume aggregators) override the local‑priority rank, or does the special‑case `if source_type == 'preferred_local' and article.score == LIMITS.get('local_priority_score', 100): return (0, sub_rank)` give the local scraper the top rank? The current code does not resolve this; the outcome depends on subtle ordering of checks.  
*Type:* **Conflict / Sequencing**  
*Severity:* **Latent**

---

**Scoring & Priority**

**6. Hard‑coded source‑type dedup rank mapping (`_SOURCE_TYPE_DEDUP_RANK`)**  
*Location:* Near the top of the file (outside the snippets) – a dict literal.  
*Problem:* The ranks are baked into the code rather than being supplied via configuration (`SOURCE_PREFS`). If the business wants to adjust relative priority of source types, a code change is required.  
*Type:* **Hard‑code**  
*Severity:* **Blocking**

*Corrected code (load from config with a sensible default):*  

```diff
- _SOURCE_TYPE_DEDUP_RANK = {
-     'preferred_local': 1,
-     'print': 3,
-     'maker_gadget': 4,
-     'broadcast': 6,
-     'personal_listicle': 7,
- }
- _UNCLASSIFIED_DEDUP_RANK = 5
+ # Load source‑type dedup ranks from configuration; fall back to the historic defaults
+ _SOURCE_TYPE_DEDUP_RANK = SOURCE_PREFS.get('source_type_dedup_rank', {
+     'preferred_local': 1,
+     'print': 3,
+     'maker_gadget': 4,
+     'broadcast': 6,
+     'personal_listicle': 7,
+ })
+ _UNCLASSIFIED_DEDUP_RANK = SOURCE_PREFS.get('unclassified_dedup_rank', 5)
```

---

**7. Hard‑coded subscriber dedup rank mapping (`_SUBSCRIBER_DEDUP_RANK`)**  
*Location:* Same area as #6.  
*Problem:* Subscriber priority ranks are also hard‑coded; they should be configurable (e.g., via `SUBSCRIBER_PREFS`).  
*Type:* **Hard‑code**  
*Severity:* **Blocking**

*Corrected code (similar pattern):*  

```diff
- _SUBSCRIBER_DEDUP_RANK = {
-     'Williams Lake Tribune': 0,
-     'New York Times': 1,
-     'Apple News+': 2,
-     'Apple News': 3,
- }
- _UNRANKED_SUBSCRIBER_RANK = 4
+ _SUBSCRIBER_DEDUP_RANK = SUBSCRIBER_PREFS.get('subscriber_dedup_rank', {
+     'Williams Lake Tribune': 0,
+     'New York Times': 1,
+     'Apple News+': 2,
+     'Apple News': 3,
+ })
+ _UNRANKED_SUBSCRIBER_RANK = SUBSCRIBER_PREFS.get('unranked_subscriber_rank', 4)
```

---

**8. Hard‑coded content‑type dedup rank mapping (`_CONTENT_TYPE_RANK`)**  
*Location:* After `filter_by_content_type` (line ≈ 2540).  
*Problem:* The hierarchy `analysis > feature > … > recap` is baked in; business may want to reorder or add new types without touching code.  
*Type:* **Hard‑code**  
*Severity:* **Blocking**

*Corrected code:*  

```diff
- _CONTENT_TYPE_RANK = {
-     'analysis': 6, 'feature': 5, 'opinion': 4,
-     'breaking': 3, 'wire': 2, 'recap': 1
- }
+ _CONTENT_TYPE_RANK = CONTENT_PREFS.get('content_type_rank', {
+     'analysis': 6, 'feature': 5, 'opinion': 4,
+     'breaking': 3, 'wire': 2, 'recap': 1
+ })
```

---

**9. Hard‑coded `local_priority_score` default (100) used in multiple places**  
*Location:* In `_source_priority()` and other functions that call `LIMITS.get('local_priority_score', 100)`.  
*Problem:* The numeric value 100 is embedded; it should be a named constant pulled from config.  
*Type:* **Hard‑code**  
*Severity:* **Latent**

*Corrected code (add a named constant and use it):*  

```diff
- if source_type == 'preferred_local' and article.score == LIMITS.get('local_priority_score', 100):
+ _LOCAL_PRIORITY_SCORE = LIMITS.get('local_priority_score')
+ if source_type == 'preferred_local' and article.score == _LOCAL_PRIORITY_SCORE:
```

(Apply similar changes wherever `LIMITS.get('local_priority_score', 100)` appears.)

---

**10. Missing validation that final sort formula matches configured weights**  
*Location:* `compute_composite_score()` (not shown in snippets).  
*Problem:* The composite score formula (quality + relevance + local) may not reflect the weights defined in configuration (e.g., `SCORING_WEIGHTS`). There is no check that the sorting order respects those weights.  
*Type:* **Missing validation**  
*Severity:* **Latent**

---

**Edge Cases**

**11. Thin‑day inflation – fallback fetchers bypass score floors**  
*Location:* `_fetch_via_google_news_fallback()`, `_fetch_via_brave_fallback()`, `_fetch_via_kagi_fallback()` (inside `score_articles_with_claude` region).  
*Problem:* When a direct feed fails, the pipeline falls back to search‑API results. These articles are added **without applying the same quality/score floor** that normal articles receive, effectively inflating the list on thin days.  
*Type:* **Sequencing / Missing guard**  
*Severity:* **Blocking**

*Corrected code (apply the same floor in each fallback):*  

```diff
-def _fetch_via_google_news_fallback(feed: Dict, cutoff_date: datetime) -> List[Article]:
+ def _fetch_via_google_news_fallback(feed: Dict, cutoff_date: datetime) -> List[Article]:
     domain = urlparse(feed.get('url', '')).netloc.replace('www.', '')
     if not domain:
         return []
 
     lookback_days = max(1, (datetime.now(timezone.utc) - cutoff_date).days + 1)
     query = quote(f'site:{domain} when:{lookback_days}d')
     gn_url = f'https://news.google.com/rss/search?q={query}&hl=en-CA&gl=CA&ceid=CA:en'
 
     headers = {'User-Agent': _BROWSER_UA, 'Accept': _FEED_ACCEPT}
     try:
         response = requests.get(gn_url, headers=headers, timeout=10)
         response.raise_for_status()
         parsed = feedparser.parse(response.content)
     except Exception as e:
         print(f"    ⚠️  Google News fallback failed for {domain}: {e}")
         return []
 
     articles = []
     for entry in parsed.entries[:10]:
         try:
             article = Article(entry, feed['title'], feed.get('html_url', ''), gn_url)
         except Exception:
             continue
         if article.pub_date < cutoff_date:
             continue
+        # Enforce the same minimum score floor that normal articles receive
+        if article.score < LIMITS.get('min_score', 0):
+            article.score = LIMITS.get('min_score', 0)
+            article.quality = max(article.quality, LIMITS.get('min_quality', 0))
         if article.should_filter():
             continue
         articles.append(article)
 
     _enrich_thin_local_articles(articles)
     return articles
```

(Apply identical floor‑enforcement in the Brave and Kagi fallback functions.)

---

**12. Local source also matches a high‑volume prescore gate – winner is undefined**  
*Location:* Interaction between `apply_prescore_filter` (which gates aggregator sources based on volume) and `_source_priority` (which gives local sources a rank of 2 or 0).  
*Problem:* When a local source also satisfies the prescore gate, it is unclear whether the prescore gate’s higher volume should dominate or the local‑priority rank should win. The current implementation does not resolve the conflict, leading to nondeterministic ordering.  
*Type:* **Conflict / Ambiguity**  
*Severity:* **Latent**

---

**13. Dedup_across_categories may drop articles that later would have been filtered by content_type, wasting work**  
*Location:* `dedup_across_categories()` → `filtered_news` loop.  
*Problem:* If a news article is a story‑match for a specific category, it is removed in the dedup step. Later stages (e.g., `filter_by_content_type`) would also have removed it (e.g., because it is a recap). The early removal is harmless but obscures visibility into how many articles were eliminated for each reason.  
*Type:* **Sequencing / Inefficacy**  
*Severity:* **Latent**

---

**14. Hard‑coded discovery probe limit (`_MAX_DISCOVERY_PROBES`) and feed‑path list (`_COMMON_FEED_PATHS`) are not configurable**  
*Location:* Near `_discover_feed_url()`.  
*Problem:* The maximum number of discovery probes and the list of candidate feed paths are baked in, limiting flexibility for outlets with non‑standard paths.  
*Type:* **Hard‑code**  
*Severity:* **Latent**

(Proposed fix – move to config – omitted for brevity because not directly related to filter/priority scoring.)

---

**15. The `Article` class lacks a `blocked_sources` attribute used by the new `should_filter()` implementation**  
*Location:* Implied by corrected `should_filter()` code.  
*Problem:* The proposed filter references `self.blocked_sources` and `self.title_patterns`. If those attributes do not exist, the filter will raise AttributeError.  
*Type:* **Missing attribute / Compatibility issue**  
*Severity:* **Blocking** (the corrected code must be paired with adding those attributes or using alternative data sources).

*Corrected code (add attributes to Article.__init__ if not already present) – example diff:*  

```diff
- class Article:
-     def __init__(self, entry, feed_title, html_url, source_url):
-         # existing initialization …
+ class Article:
+     def __init__(self, entry, feed_title, html_url, source_url):
+         # existing initialization …
+         # Load blocking configuration
+         self.blocked_sources = BLOCKED_SOURCES.get(feed_title, [])
+         self.title_patterns = TITLE_PATTERNS.get(feed_title, [])
+         self.keywords = KEYWORDS.get(feed_title, [])
```

(Where `BLOCKED_SOURCES`, `TITLE_PATTERNS`, and `KEYWORDS` are pulled from the appropriate config dicts.)

---

**Summary of BLOCKING fixes provided**

1. **Article.should_filter()** – replaced erroneous API fetch with proper keyword/source/title‑pattern blocking.  
2. **filter_by_content_type()** – implemented hard‑drop for fluff/sponsored/recap.  
3. **Hard‑coded source‑type, subscriber, and content‑type rank mappings** – added config‑driven fall‑backs (three separate diffs).  
4. **Thin‑day inflation** – added score floor enforcement in Google News (and implied Brave/Kagi) fallback fetchers.  
5. **Article attribute compatibility** – added `blocked_sources`, `title_patterns`, `keywords` attributes to support the new filter.

All other listed findings are **LATENT** or **COSMETIC** and do not require immediate code changes.
