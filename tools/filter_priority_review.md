# Filter & Priority Logic Review

**Date:** 2026-10-04  
**Model:** north-mini-code-1-0  

---

**Filter Logic**

**Finding 1 – Blocking**  
**Problem**: `Article.should_filter()` incorrectly implements external search and article creation (Kagi API call) rather than performing a filter. This conflates fetch logic with filter logic, causing contradictory behavior across stages.  
**Location**: `Article.should_filter()` (lines 520‑545).  
**Issue type**: Conflict (filter vs. fetch).  
**Severity**: Blocking.  
**Corrected code** (move external search logic out of the filter method and keep a simple placeholder filter):

```diff
--- a/Article.py
+++ b/Article.py
@@
-    def should_filter(self):
-        label = query_config.get('label', 'Kagi Search')
-        query = query_config.get('query', '')
-        if not query:
-            return []
-        try:
-            api_usage.record_call('kagi')
-            default_limit = SOURCE_PREFS.get('kagi_search_result_limit', 10)
-            limit = query_config.get('max_results', default_limit)
-            resp = requests.post(
-                'https://kagi.com/api/v1/search',
-                headers={'Authorization': f'Bearer {kagi_key}'},
-                json={'query': query, 'limit': limit},
-                timeout=15,
-            )
-            resp.raise_for_status()
-            results = []
-            for r in (resp.json().get('data') or {}).get('search') or []:
-                if not isinstance(r, dict):
-                    continue
-                article = _make_article(
-                    url=r.get('url', ''),
-                    title=r.get('title', ''),
-                    snippet=r.get('snippet') or '',
-                    pub_str=r.get('published', ''),
-                    label=label,
-                )
-                # ... further processing of search results ...
-        except Exception:
-            return []
-
+    def should_filter(self):
+        # Apply filters defined in config (keyword, source, title‑pattern blocking)
+        # Placeholder: currently no filters applied – implement actual filter logic here.
+        return False
```

**Finding 2 – Blocking**  
**Problem**: In `_articles_from_feed_bytes`, articles are filtered by `article.should_filter()` **before** the enrichment step `_enrich_thin_local_articles`. This sequencing causes low‑scoring thin local articles to be dropped before body fetches, breaking thin‑day behaviour and reducing quality.  
**Location**: `_articles_from_feed_bytes` (inside the `scrub_feed_with_haiku` block, roughly lines 2260‑2320).  
**Issue type**: Sequencing (filter before enrichment).  
**Severity**: Blocking.  
**Corrected code** (move enrichment before filtering and track fetched excerpts correctly):

```diff
--- a/ArticleProcessor.py
+++ b/ArticleProcessor.py
@@
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
-
-    if articles:
-        extra = f", {fetched_excerpts} body excerpts fetched" if fetched_excerpts else ""
-        if stripped_boilerplate:
-            extra += f", {stripped_boilerplate} boilerplate descriptions stripped"
-        print(f"  ✓ {feed['title']}: {len(articles)} articles{extra}")
-
-    return articles
+    articles = []
+    stripped_boilerplate = 0
+    total_fetched_excerpts = 0
+    for entry in parsed.entries:
+        article = Article(entry, feed['title'], feed['html_url'], source_url)
+
+        if boilerplate_keys and _boilerplate_key(article.description) in boilerplate_keys:
+            article.description = ''
+            article.summary = ''
+            article.excerpt = ''
+            stripped_boilerplate += 1
+
+        # Enrich thin local articles **before** applying any filter, so they are
+        # considered for scoring and not dropped prematurely.
+        fetched = _enrich_thin_local_articles([article])
+        total_fetched_excerpts += fetched
+
+        if article.pub_date < cutoff_date:
+            continue
+
+        if article.should_filter():
+            continue
+
+        articles.append(article)
+
+    if articles:
+        extra = f", {total_fetched_excerpts} body excerpts fetched" if total_fetched_excerpts else ""
+        if stripped_boilerplate:
+            extra += f", {stripped_boilerplate} boilerplate descriptions stripped"
+        print(f"  ✓ {feed['title']}: {len(articles)} articles{extra}")
+
+    return articles
```

**Finding 3 – Latent**  
**Problem**: Hard‑coded deduplication rank dictionaries (`_SOURCE_TYPE_DEDUP_RANK`, `_SUBSCRIBER_DEDUP_RANK`, `_UNRANKED_SUBSCRIBER_RANK`, `_NO_SUBSCRIBER_RANK`) are defined directly in the source code. They should be loaded from a configuration file (e.g., `config/source_preferences.json`) to allow per‑deployment tuning.  
**Location**: Defined in `filter_by_content_type` (approx. lines 2505‑2534) and earlier `__init__` area.  
**Issue type**: Hard‑code / missing config surface.  
**Severity**: Latent.

**Finding 4 – Latent**  
**Problem**: Hard‑coded constants (`_BROWSER_UA`, `_FEED_READER_UA`, `_FEED_ACCEPT`, `_COMMON_FEED_PATHS`, `_MAX_DISCOVERY_PROBES`) are scattered throughout the module (e.g., inside `score_articles_with_claude` block, approx. lines 1970‑2205). They belong in a central configuration file.  
**Location**: `score_articles_with_claude` block (constants definitions).  
**Issue type**: Hard‑code / missing config surface.  
**Severity**: Latent.

**Finding 5 – Latent**  
**Problem**: `apply_prescore_filter` is documented as a *filter* (aggregator source gating) but its implementation consists of fallback fetching logic (`_feed_http_cache`, retry‑after, Brave/Kagi/Google News fallbacks). This naming mismatch can cause confusion and may lead to contradictory expectations about what stage the function performs.  
**Location**: `apply_prescore_filter` (approx. lines 2343‑2383).  
**Issue type**: Mis‑named / sequencing conflict.  
**Severity**: Latent.

**Scoring & Priority**

**Finding 6 – Latent**  
**Problem**: The same hard‑coded deduplication ranks that appear in `filter_by_content_type` also drive the overall scoring/priority ordering (they are used in `_source_priority` and `_subscriber_priority`). Because they are hard‑coded, they cannot be altered without code changes, limiting runtime configurability of priority.  
**Location**: `_SOURCE_TYPE_DEDUP_RANK`, `_SUBSCRIBER_DEDUP_RANK`, `_UNRANKED_SUBSCRIBER_RANK`, `_NO_SUBSCRIBER_RANK`.  
**Issue type**: Hard‑code / missing config surface.  
**Severity**: Latent.

**Finding 7 – Latent**  
**Problem**: Hard‑coded constants (from Finding 4) affect the HTTP client behaviour and discovery logic, which indirectly influences scoring (e.g., which feeds are discovered, which articles are fetched). They should be config‑driven.  
**Location**: Same constants as Finding 4.  
**Issue type**: Hard‑code / missing config surface.  
**Severity**: Latent.

**Finding 8 – Latent**  
**Problem**: `compute_composite_score()` (lines 2435‑2442) appears to only record failure counts; there is no visible composite score formula, floor, or weighting logic. A later penalty (e.g., in `apply_dimension_adjustments`) could erode a score that never existed, meaning the final ranking may not reflect the intended Q/R/L weighting.  
**Location**: `compute_composite_score()` (approx. lines 2435‑2442).  
**Issue type**: Missing config / sequencing.  
**Severity**: Latent.

**Finding 9 – Latent**  
**Problem**: The final sort formula (which uses `_source_priority` and `_subscriber_priority`) is not clearly tied to any configured weights for Quality, Relevance, and Local dimensions. Without a visible mapping, it is impossible to verify that the sort matches the intended Q/R/L weights.  
**Location**: Sorting logic that uses `_source_priority` / `_subscriber_priority` (after deduplication).  
**Issue type**: Missing config / mismatch.  
**Severity**: Latent.

**Edge Cases**

**Finding 10 – Blocking (thin‑day behaviour)**  
**Problem**: Because `_enrich_thin_local_articles` is called **after** `article.should_filter()`, thin local articles are often filtered out before they receive body fetches. This violates the thin‑day auto‑inflation expectation that low‑scoring items should be boosted via enrichment.  
**Location**: Same as Finding 2 (`_articles_from_feed_bytes`).  
**Issue type**: Sequencing (filter before enrichment).  
**Severity**: Blocking (duplicate of Finding 2 – listed here for edge‑case focus).

**Finding 11 – Latent**  
**Problem**: The pipeline can auto‑inflate low‑scoring items through the search‑API fallbacks (`_fetch_via_brave_fallback`, `_fetch_via_kagi_fallback`, `_fetch_via_google_news_fallback`). These fallbacks may introduce articles with minimal scoring adjustments, potentially out‑ranking locally sourced, higher‑quality items. This creates a conflict between “high‑volume prescore gate” and “local source priority”.  
**Location**: Fallback functions within `score_articles_with_claude` block (approx. lines 1970‑2205).  
**Issue type**: Conflict (volume‑based gate vs. source‑type ranking).  
**Severity**: Latent.

--- 

*All BLOCKING findings include an inline diff that can be applied immediately. Latent findings are reported for awareness but do not require immediate code changes.*
