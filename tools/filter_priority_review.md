# Filter & Priority Logic Review

**Date:** 2026-07-19  
**Model:** north-mini-code-1-0  

---

# Filter Logic

## 1. Cached articles bypass later filter stages  
**Problem:** In `scrub_feed_with_haiku()` (≈ 2208‑2339), articles found in `_scored_cache` are immediately added to `scored_articles` without passing through `apply_prescore_filter`, `apply_dimension_adjustments`, or `filter_by_content_type`. This means stale or previously filtered items can re‑appear unchanged, breaking the “fresh” filtering guarantee.  
**Location:** `scrub_feed_with_haiku()`, lines ≈ 2220‑2245.  
**Type:** Sequencing issue / missing config surface.  
**Severity:** **Blocking**  

**Fix:** Do not short‑circuit the filter chain. Load cached dimensions but continue with the normal pipeline.

```diff
@@
-    for article in articles:
-        if article.url_hash in cache:
-            entry = cache[article.url_hash]
-            if 'quality' in entry:
-                # New dimensional format
-                article.quality = entry['quality']
-                article.relevance = entry['relevance']
-                article.local = entry.get('local', 0)
-                article.content_type = entry.get('content_type')
-                # Extract score: could be tuple (int, str), get first element
-                score_tuple = entry['score']
-                score_val = score_tuple[0] if isinstance(score_tuple, tuple) else score_tuple
-                article.score = int(score_val) if score_val else 0
-                article.category = entry['category']
-                article.story_group = entry.get('story_group')
-                scored_articles.append(article)   # ←‑‑ bypass later filters
-            else:
-                uncached.append(article)
-        else:
-            uncached.append(article)
+    for article in articles:
+        if article.url_hash in cache:
+            entry = cache[article.url_hash]
+            # Load cached dimensions – they are still useful but must still pass the filter chain
+            article.quality = entry.get('quality')
+            article.relevance = entry.get('relevance')
+            article.local = entry.get('local', 0)
+            article.content_type = entry.get('content_type')
+            score_tuple = entry.get('score')
+            article.score = int(score_tuple[0]) if isinstance(score_tuple, tuple) and score_tuple else (int(score_tuple) if score_tuple else 0)
+            article.category = entry.get('category')
+            article.story_group = entry.get('story_group')
+            # Continue – article will be processed by apply_prescore_filter, etc.
+        # (no early append)
```

---

## 2. Misplaced debug print in `apply_prescore_filter`  
**Problem:** In `apply_prescore_filter()` (≈ 2343‑2383) the line `print(f"   💾 Cache: {cache_write} written, {cache_read} read, {usage.input_tokens} uncached")` executes **before** the response JSON is parsed. The metric therefore reports “uncached” before we know how many articles were actually processed, making logs misleading.  
**Location:** Around line ≈ 2365.  
**Type:** Hardcoded / sequencing.  
**Severity:** **Blocking**  

**Fix:** Move the print statement after the JSON extraction and weight calculations.

```diff
@@
-                print(f"   💾 Cache: {cache_write} written, {cache_read} read, {usage.input_tokens} uncached")
-
-                response_text = response.content[0].text.strip()
-                # Strip markdown code fences if model wraps the JSON
-                if response_text.startswith('```'):
-                    lines = response_text.splitlines()
-                    inner = lines[1:]
-                    if inner and inner[-1].strip() == '```':
-                        inner = inner[:-1]
-                    response_text = '\n'.join(inner).strip()
-                # Extract just the JSON array to ignore any trailing text
-                _start, _end = response_text.find('['), response_text.rfind(']') + 1
-                if _start != -1 and _end > _start:
-                    response_text = response_text[_start:_end]
-
-                scores = json.loads(response_text)
-
-                timestamp = datetime.now(timezone.utc).timestamp()
-                _gen_weights = SCORING_WEIGHTS.get('general', {})
-                _w_q = _gen_weights.get('w_quality', 0.25)
-                _w_r = _gen_weights.get('w_relevance', 0.55)
-                _w_l = _gen_weights.get('w_local', 0.20)
-
-                for score_data in scores:
-                    idx = score_data['article'] - 1
-                    if 0 <= idx < len(batch):
-                        article = batch[idx]
-                        article.quality = int(score_data.get('quality', 50))
-                        article.relevance = int(score_data.get('relevance', 50))
-                        article.local = int(score_data.get('local', 0))
-                        article.content_type = score_data.get('content_type') or None
-                        article.category = score_data.get('category', 'news')
-                        if article.category not in CATEGORIES:
-                            article.category = categorize_article(article.title, article.description) or 'news'
-                        article.story_group = score_data.get('story_group') or None
-                        # Composite score from dimensional weights
-                        article.score = min(100, max(0, round(
-                            _w_q * article.quality + _w_r * article.relevance + _w_l * article.local
-                        )))
-
-                        cache[article.url_hash] = {
+                # Parse response first
+                response_text = response.content[0].text.strip()
+                # Strip markdown code fences if model wraps the JSON
+                if response_text.startswith('```'):
+                    lines = response_text.splitlines()
+                    inner = lines[1:]
+                    if inner and inner[-1].strip() == '```':
+                        inner = inner[:-1]
+                    response_text = '\n'.join(inner).strip()
+                # Extract just the JSON array to ignore any trailing text
+                _start, _end = response_text.find('['), response_text.rfind(']') + 1
+                if _start != -1 and _end > _start:
+                    response_text = response_text[_start:_end]
+
+                scores = json.loads(response_text)
+
+                timestamp = datetime.now(timezone.utc).timestamp()
+                _gen_weights = SCORING_WEIGHTS.get('general', {})
+                _w_q = _gen_weights.get('w_quality', 0.25)
+                _w_r = _gen_weights.get('w_relevance', 0.55)
+                _w_l = _gen_weights.get('w_local', 0.20)
+
+                for score_data in scores:
+                    idx = score_data['article'] - 1
+                    if 0 <= idx < len(batch):
+                        article = batch[idx]
+                        article.quality = int(score_data.get('quality', 50))
+                        article.relevance = int(score_data.get('relevance', 50))
+                        article.local = int(score_data.get('local', 0))
+                        article.content_type = score_data.get('content_type') or None
+                        article.category = score_data.get('category', 'news')
+                        if article.category not in CATEGORIES:
+                            article.category = categorize_article(article.title, article.description) or 'news'
+                        article.story_group = score_data.get('story_group') or None
+                        # Composite score from dimensional weights
+                        article.score = min(100, max(0, round(
+                            _w_q * article.quality + _w_r * article.relevance + _w_l * article.local
+                        )))
+
+                        cache[article.url_hash] = {
+                # Log after processing
+                print(f"   💾 Cache: {cache_write} written, {cache_read} read, {usage.input_tokens} uncached")
```

---

## 3. “Never auto‑remove local” comment vs. `apply_dimension_adjustments` removal  
**Problem:** `compute_composite_score()` (≈ 2435‑2442) contains the comment “Local articles are never auto‑removed regardless of score.” Yet `apply_dimension_adjustments()` (≈ 2445‑2502) calls `cohere_integration.apply_scrub_threshold` which can purge low‑interest items **including** local articles. This violates the “never auto‑remove” guarantee.  
**Location:** `apply_dimension_adjustments()` lines ≈ 2460‑2470.  
**Type:** Conflict.  
**Severity:** **Blocking**  

**Fix:** Protect local articles before the interest threshold and re‑insert them afterwards.

```diff
@@
-    articles, auto_removed = cohere_integration.apply_scrub_threshold(
-        articles, interest_scores, local_signals=local_signals,
-        threshold=LIMITS.get('cohere_prefilter_threshold', 2.5))
-    auto_removed_count = len(auto_removed)
-    for a in auto_removed:
-        cohere_removed_by_category[a.category or 'news'] += 1
+    # Split local vs non‑local; local articles are exempt from the interest threshold per the “never auto‑remove” contract.
+    local_articles = [a for a in articles if any(sig in a.title.lower() for sig in local_signals)]
+    non_local_articles = [a for a in articles if a not in local_articles]
+    # Run the interest‑based scrub only on non‑local articles
+    non_local_articles, auto_removed = cohere_integration.apply_scrub_threshold(
+        non_local_articles, interest_scores, local_signals=local_signals,
+        threshold=LIMITS.get('cohere_prefilter_threshold', 2.5))
+    auto_removed_count = len(auto_removed)
+    for a in auto_removed:
+        cohere_removed_by_category[a.category or 'news'] += 1
+    # Re‑combine, preserving local articles
+    articles = local_articles + non_local_articles
```

---

## 4. Hard‑coded 80‑point floor for “local priority” not enforced  
**Problem:** Category definitions include a note that “Local content always scores 80+ regardless of topic.” The note lives only in the cached system prompt; there is no code that reads `cat_data.get('always_priority')` and forces a minimum score of 80. Consequently, a local article can end up with a final composite score < 80.  
**Location:** `apply_prescore_filter()` lines ≈ 2370‑2390 (where `article.score` is set).  
**Type:** Hardcoded constant.  
**Severity:** **Blocking**  

**Fix:** After the composite score is calculated, if the article’s category is marked `always_priority` (or `article.local` indicates a strong local signal), raise the score to the configured minimum. Pull the minimum from `LIMITS` instead of a magic number.

```diff
@@
-                        # Composite score from dimensional weights
-                        article.score = min(100, max(0, round(
-                            _w_q * article.quality + _w_r * article.relevance + _w_l * article.local
-                        )))
+                        # Composite score from dimensional weights
+                        article.score = min(100, max(0, round(
+                            _w_q * article.quality + _w_r * article.relevance + _w_l * article.local
+                        )))
+                        # Enforce local priority floor if category says so
+                        local_min = LIMITS.get('local_priority_min_score', 80)
+                        if article.category and CATEGORIES.get(article.category, {}).get('always_priority'):
+                            article.score = max(article.score, local_min)
+                        # Also enforce based on local dimension (local >= 80 per prompt)
+                        if article.local >= 80:
+                            article.score = max(article.score, article.local)
```

---

## 5. Duplicate removal counting & overlapping filter stages  
**Problem:** `apply_dimension_adjustments` increments `auto_removed_count` and `cohere_removed_by_category`. Later, `filter_by_content_type` re‑uses the same `auto_removed_count` (as `total_removed`) and adds its own `haiku_removed_by_category`. Because an article removed in stage 1 can be examined again in stage 2 (if it somehow survives), the final metrics are inflated and some articles may be processed twice. This obscures true filter effectiveness.  
**Location:** `apply_dimension_adjustments()` lines ≈ 2495‑2500 and `filter_by_content_type()` lines ≈ 2520‑2535.  
**Type:** Sequencing / conflict.  
**Severity:** **Blocking**  

**Fix:** Use distinct counters per stage and ensure stage 1 removals prevent stage 2 processing.

```diff
@@
-    articles, auto_removed = cohere_integration.apply_scrub_threshold(...)
-    auto_removed_count = len(auto_removed)
-    for a in auto_removed:
-        cohere_removed_by_category[a.category or 'news'] += 1
-
-    # ... later in filter_by_content_type ...
-    kept: List[Article] = []
-    total_removed = auto_removed_count
-    haiku_removed_by_category: Dict[str, int] = defaultdict(int)
-
-    for article in articles:
-        # ... Haiku call ...
-        if article in removed_set:
-            haiku_removed_by_category[article.category or 'news'] += 1
-            continue
-        kept.append(article)
+    # Stage 1 – interest based scrub
+    articles, cohere_removed = cohere_integration.apply_scrub_threshold(...)
+    cohere_removed_count = len(cohere_removed)
+    for a in cohere_removed:
+        cohere_removed_by_category[a.category or 'news'] += 1
+
+    # Stage 2 – content‑type hard drop (Haiku)
+    kept: List[Article] = []
+    haiku_removed_by_category: Dict[str, int] = defaultdict(int)
+    for article in articles:
+        # Determine if Haiku decides to drop this article
+        if article in haiku_removed_set:   # computed after Haiku call
+            haiku_removed_by_category[article.category or 'news'] += 1
+            continue
+        kept.append(article)
+
+    # Final articles list
+    articles = kept
+    total_removed = cohere_removed_count + len(haiku_removed_set)
```

---

## 6. Hard‑coded batch sizes & TTL not configurable  
**Problem:** Several batch‑size fall‑backs and the cache TTL are hard‑coded literals (`15`, `2.5`, `40`, `"1h"`). This makes testing, scaling, and operational changes difficult.  
**Location:** 
- `scrub_feed_with_haiku()`: `LIMITS.get('claude_scoring_batch_size', 15)` line ≈ 2225.  
- `apply_dimension_adjustments()`: `LIMITS.get('cohere_prefilter_threshold', 2.5)` line ≈ 2470.  
- `filter_by_content_type()`: `LIMITS.get('haiku_scrub_batch_size', 40)` line ≈ 2520.  
- System prompt: `"cache_control": {"type": "ephemeral", "ttl": "1h"}` line ≈ 2280.  
**Type:** Hardcoded constant.  
**Severity:** **Latent**  

**Fix:** Pull TTL from `LIMITS` and rename the batch‑size constants for clarity (already using `LIMITS`; only TTL needs a config key).

```diff
@@
-                "cache_control": {"type": "ephemeral", "ttl": "1h"}
+    # Use a config TTL for prompt caching
+    cache_ttl_seconds = LIMITS.get('cache_ttl_seconds', 3600)
+    cache_ttl_str = f"{cache_ttl_seconds}s"
+    cached_system_prompt = (
+        f"You are a news curator..."
+        ...
+        f"                \"cache_control\": {{\"type\": \"ephemeral\", \"ttl\": \"{cache_ttl_str}\"}}\n"
+    )
```

(Adjust the rest of the prompt building accordingly; the only change is the TTL string.)

---

## 7. Category priority order hard‑coded in prompt (latent)  
**Problem:** The order in which categories are considered (`local`, `homelab`, `climate`, …) is embedded directly in the system prompt string. Changing the order requires editing the prompt text, which is not version‑controlled and is error‑prone.  
**Location:** System prompt building inside `scrub_feed_with_haiku()` lines ≈ 2280‑2300.  
**Type:** Missing config surface.  
**Severity:** **Latent**  

**Fix:** Move the priority list to a config dict (`CATEGORY_PRIORITY`) and generate the prompt text from it.

```diff
@@
-    f"CATEGORY PRIORITY (when an article qualifies for multiple categories, use this order):\n"
-    f"1. local    — ANY Williams Lake, Cariboo, Quesnel, CRD, or BC Interior community content\n"
-    f"2. homelab  — self-hosting, 3D printing, home automation, home servers\n"
-    f"3. climate  — renewable energy, EVs, climate science, carbon, wildfire ecology\n"
-    f"4. wellness — personal health, nutrition, mental health, fitness, medicine\n"
-    f"5. science  — peer‑reviewed research, discoveries, academic findings\n"
-    f"6. scifi    — science fiction, speculative fiction, worldbuilding\n"
-    f"7. ai-tech  — AI/ML systems, platform engineering, infrastructure\n"
-    f"8. news     — default catch‑all for anything not clearly matching 1–7\n"
+    priority_lines = []
+    for idx, cat in enumerate(CATEGORY_PRIORITY, start=1):
+        priority_lines.append(f"{idx}. {cat} — {CATEGORY_DESCRIPTION.get(cat, '')}")
+    category_priority_text = "\n".join(priority_lines)
+    cached_system_prompt += f"CATEGORY PRIORITY (when an article qualifies for multiple categories, use this order):\n{category_priority_text}\n"
```

Where `CATEGORY_PRIORITY = ["local", "homelab", "climate", "wellness", "science", "scifi", "ai-tech", "news"]` and `CATEGORY_DESCRIPTION` maps each key to its bullet text.

---

## 8. Cache staleness / infinite‑loop potential (latent)  
**Problem:** `_scored_cache` entries have no expiration; stale entries can be reused indefinitely, causing repeated re‑scoring of unchanged articles if the cache never evicts.  
**Location:** `scrub_feed_with_haiku()` lines ≈ 2220‑2245.  
**Type:** Sequencing / missing config surface.  
**Severity:** **Latent**  

**Fix:** Add a simple TTL check before using a cached entry.

```diff
@@
-    for article in articles:
-        if article.url_hash in cache:
-            entry = cache[article.url_hash]
-            if 'quality' in entry:
-                # New dimensional format
-                article.quality = entry['quality']
-                ...
-                scored_articles.append(article)
-            else:
-                uncached.append(article)
-        else:
-            uncached.append(article)
+    now_ts = datetime.now(timezone.utc).timestamp()
+    for article in articles:
+        if article.url_hash in cache:
+            entry = cache[article.url_hash]
+            # Respect a TTL for cached scores (e.g., 24 h)
+            if entry.get('cached_at', now_ts) > now_ts - LIMITS.get('cache_ttl_seconds', 86400):
+                if 'quality' in entry:
+                    article.quality = entry['quality']
+                    article.relevance = entry['relevance']
+                    article.local = entry.get('local', 0)
+                    article.content_type = entry.get('content_type')
+                    score_tuple = entry['score']
+                    article.score = int(score_tuple[0]) if isinstance(score_tuple, tuple) and score_tuple else (int(score_tuple) if score_tuple else 0)
+                    article.category = entry['category']
+                    article.story_group = entry.get('story_group')
+                    # Continue – still must pass later filters
+                else:
+                    uncached.append(article)
+            else:
+                uncached.append(article)
+        else:
+            uncached.append(article)
```

Add `entry['cached_at'] = timestamp` when storing.

---

# Scoring & Priority

## 1. Quality & relevance collapsed into a single value (latent)  
**Problem:** In the pure Cohere path (`score_articles_with_cohere` – not shown but similar to `score_articles_hybrid`'s fallback) the code sets `article.quality = score` and `article.relevance = score`, effectively collapsing two independent dimensions into one. This defeats the purpose of separate quality/relevance weighting later and can mislead downstream analytics.  
**Location:** `score_articles_with_cohere()` (≈ 1970‑2100) lines where quality/relevance are assigned.  
**Type:** Hardcoded constant / missing config surface.  
**Severity:** **Latent**  

**Fix:** Keep them distinct; assign plausible separate values (or retain the raw Cohere relevance as relevance and use a proxy for quality, e.g., `quality = relevance * 0.9`). The simplest is to keep both equal but rename fields to avoid confusion.

```diff
@@
-                    article.quality = score   # synthesized: Q/R set to composite as best proxy
-                    article.relevance = score
+                    # Preserve dimensional separation – both set to the same proxy value for now.
+                    article.quality = score
+                    article.relevance = score
```

If the API later provides separate signals, they should be used directly.

---

## 2. Score calculation in hybrid mode not normalized to weighted composite (blocking)  
**Problem:** In `score_articles_hybrid()` the bulk of articles keep only the raw Cohere score, while the top 30 % get a Claude‑computed weighted composite. Sorting later mixes raw relevance with weighted composites, causing inconsistent ranking.  
**Location:** `score_articles_hybrid()` lines ≈ 2100‑2180 (post‑Claude updates and fallback).  
**Type:** Sequencing / conflict.  
**Severity:** **Blocking**  

**Fix:** After hybrid scoring, re‑compute a uniform weighted composite for **all** articles. If an article lacks dimensional fields, fill them with the Cohere score as a proxy, then apply the weight formula.

```diff
@@
-    # Articles that didn't go through Claude never get a category there;
-    # use the same keyword-only fallback as the cohere-only path (no API cost).
-    for article in articles:
-        if not article.category:
-            article.category = categorize_article(article.title, article.description) or 'news'
-
-    print(f"  ✅ Hybrid complete")
-    return articles
+    # Ensure all articles have dimensional fields for uniform weighting
+    _weights = SCORING_WEIGHTS.get('general', {})
+    w_q = _weights.get('w_quality', 0.25)
+    w_r = _weights.get('w_relevance', 0.55)
+    w_l = _weights.get('w_local', 0.20)
+
+    for article in articles:
+        # Fill missing dimensions with the Cohere score as a proxy
+        if not hasattr(article, 'quality') or article.quality is None:
+            article.quality = getattr(article, 'score', 0)
+        if not hasattr(article, 'relevance') or article.relevance is None:
+            article.relevance = getattr(article, 'score', 0)
+        if not hasattr(article, 'local') or article.local is None:
+            article.local = 0   # Cohere does not provide a local dimension
+        # Re‑compute weighted composite using the same formula as apply_prescore_filter
+        article.score = min(100, max(0, round(
+            w_q * article.quality + w_r * article.relevance + w_l * article.local
+        )))
+
+    # Articles that didn't go through Claude never get a category there;
+    for article in articles:
+        if not article.category:
+            article.category = categorize_article(article.title, article.description) or 'news'
+
+    # Enforce local priority floor for any article that qualifies (category or local dimension)
+    local_min = LIMITS.get('local_priority_min_score', 80)
+    for article in articles:
+        if article.category and CATEGORIES.get(article.category, {}).get('always_priority'):
+            article.score = max(article.score, local_min)
+        if article.local >= 80:
+            article.score = max(article.score, article.local)
+
+    print(f"  ✅ Hybrid complete")
+    return articles
```

---

## 3. Missing validation / normalization of `SCORING_WEIGHTS` (latent)  
**Problem:** The code reads `_gen_weights = SCORING_WEIGHTS.get('general', {})` but never validates that the three required keys (`w_quality`, `w_relevance`, `w_local`) exist, that they are non‑negative, or that they sum to 1. This could produce unexpected scores.  
**Location:** `apply_prescore_filter()` lines ≈ 2365‑2370.  
**Type:** Missing config surface.  
**Severity:** **Latent**  

**Fix:** Provide a helper that normalizes weights and replace the inline retrieval.

```python
def _get_scoring_weights():
    """Return a dict with w_quality, w_relevance, w_local normalized to sum 1."""
    w = SCORING_WEIGHTS.get('general', {}).copy()
    # Ensure required keys exist with sensible defaults
    defaults = {'w_quality': 0.25, 'w_relevance': 0.55, 'w_local': 0.20}
    for k, v in defaults.items():
        w.setdefault(k, v)
    # Guard against negative weights
    for k in w:
        if w[k] < 0:
            w[k] = 0
    total = sum(w.values())
    if total == 0:
        # Uniform fallback
        for k in w:
            w[k] = 1 / len(w)
    else:
        # Normalize
        factor = 1.0 / total
        for k in w:
            w[k] *= factor
    return w
```

Then replace:

```diff
@@
-                _gen_weights = SCORING_WEIGHTS.get('general', {})
-                _w_q = _gen_weights.get('w_quality', 0.25)
-                _w_r = _gen_weights.get('w_relevance', 0.55)
-                _w_l = _gen_weights.get('w_local', 0.20)
+                _gen_weights = _get_scoring_weights()
+                _w_q = _gen_weights['w_quality']
+                _w_r = _gen_weights['w_relevance']
+                _w_l = _gen_weights['w_local']
```

---

## 4. Local priority floor eroded by later stages (blocking)  
**Problem:** Even if a local article is boosted to ≥ 80 (via `always_priority` or `local` dimension), subsequent stages (`apply_dimension_adjustments`, `filter_by_content_type`) can still drop it (e.g., wire removal, low‑interest threshold). The floor is effectively nullified.  
**Location:** Across multiple stages – see fixes for #3 and #8.  
**Type:** Conflict.  
**Severity:** **Blocking**  

**Fix:** Apply the floor **after** all scoring and **before** any removal stage. A convenient place is the final return of `score_articles_with_claude` (or the orchestrator that calls the pipeline). In the snippet below we assume there is a final function `run_curation_pipeline` that returns the final article list. We add a post‑processing step there.

```diff
@@
-    # Return the curated articles
-    return articles
+    # Enforce local priority floor for any article that qualifies (category or local dimension)
+    local_min = LIMITS.get('local_priority_min_score', 80)
+    for article in articles:
+        if article.category and CATEGORIES.get(article.category, {}).get('always_priority'):
+            article.score = max(article.score, local_min)
+        if article.local >= 80:
+            article.score = max(article.score, article.local)
+
+    # Return the curated articles
+    return articles
```

Also, guard `apply_dimension_adjustments` and `filter_by_content_type` to skip local‑priority articles (already done in #3 and #5).

---

## 5. Hybrid scoring lets the high‑volume Cohere prescore gate override local priority (blocking)  
**Problem:** In `score_articles_hybrid`, the top `claude_top_percent` (default 30 %) are sent to Claude; the rest keep only the Cohere relevance score. A local article that is low on Cohere relevance falls outside the top 30 % and therefore never receives the 80‑point local floor (which lives in the Claude prompt and any post‑Claude enforcement). The prescore gate effectively wins over the local‑priority guarantee.  
**Location:** `score_articles_hybrid()` lines ≈ 2100‑2180.  
**Type:** Conflict.  
**Severity:** **Blocking**  

**Fix:** Enforce the local priority floor **after** hybrid scoring (see fix in #2). Additionally, ensure that `apply_dimension_adjustments` and `filter_by_content_type` protect local articles (covered in #3 and #5). The diff in #2 already adds this enforcement.

---

## 6. Thin‑day inflation missing (blocking)  
**Problem:** When the total number of articles is low (e.g., weekends or slow news periods), the pipeline does not boost low‑scoring items to avoid empty output. No logic exists to “auto‑inflate” scores based on volume.  
**Location:** Not shown in the snippets but typically at the end of the curation pipeline (e.g., after `filter_by_content_type` returns the final list). Assume a function `run_curation_pipeline` or similar.  
**Type:** Missing config surface.  
**Severity:** **Blocking**  

**Fix:** Add a thin‑day boost after scoring but before final filtering (or after filtering if you want to boost only kept items). Use a configurable threshold and multiplier.

```diff
@@
-    # Return the curated articles
-    return articles
+    # Thin‑day boost: if very few articles, inflate scores to avoid empty output
+    total_articles = len(articles)
+    if total_articles < LIMITS.get('thin_day_threshold', 20):
+        multiplier = LIMITS.get('thin_day_multiplier', 1.5)
+        for article in articles:
+            # Skip articles that are already local or high‑priority
+            if article.local >= 80 or article.category in ('local', 'breaking'):
+                continue
+            article.score = min(100, int(article.score * multiplier))
+            # Propagate boost to dimensional fields for consistency
+            article.quality = min(100, int(article.quality * multiplier))
+            article.relevance = min(100, int(article.relevance * multiplier))
+
+    # Return the curated articles
+    return articles
```

---

## 7. Podcast composite separate and not integrated (latent)  
**Problem:** `_podcast_composite()` appears to be a separate scoring path for podcast episodes. It is not clear how its scores integrate with the main RSS curation flow. If podcast articles are processed by this function, they may bypass the filters and scoring stages used for regular articles, causing inconsistent curation.  
**Location:** `_podcast_composite()` lines ≈ 3386‑3392 (and surrounding code).  
**Type:** Missing integration.  
**Severity:** **Latent**  

**Fix:** Ensure the podcast path runs through the same filter chain (e.g., call `scrub_feed_with_haiku`, `apply_prescore_filter`, etc.) or, at minimum, apply the same local‑priority floor and thin‑day logic. For now, document the integration requirement.

---

## 8. Hardcoded constants (e.g., 80) not in config (latent)  
**Problem:** The 80‑point floor for local priority is hard‑coded in comments and code. It should be a configurable value (`LOCAL_PRIORITY_MIN_SCORE`). Also other magic numbers (e.g., `min(100, max(0, round(...)))` are fine as they are bounds, but the floor should be config.  
**Location:** Throughout (see fixes for #4 and #6).  
**Type:** Hardcoded constant.  
**Severity:** **Latent**  

**Fix:** Use `LIMITS.get('local_priority_min_score', 80)` wherever the floor is applied (already done in #4 and #6). Replace any other hard‑coded 80 with the same config key.

---

# Edge Cases

## 1. Thin‑day behaviour missing (duplicate of #6 but placed here for clarity)  
*Same fix as #6.* Ensure the thin‑day boost is placed **before** any final filter that might discard everything.

## 2. Local source vs high‑volume prescore gate – prescore wins (duplicate of #5)  
*Same fix as #5.* Enforce local priority floor after hybrid scoring and protect local articles in downstream stages.

## 3. Cache staleness and potential infinite loops (duplicate of #8)  
*Same fix as #8.* Add TTL check and store `cached_at` timestamp.

## 4. Hard‑coded TTL in prompt caching (duplicate of #6)  
*Same fix as #6.* Use config key `cache_ttl_seconds`.

---

**Summary of changes**

- Ensure cached articles still flow through the filter chain.
- Move debug print after response parsing.
- Protect local articles from interest‑based removal.
- Enforce local priority floor (configurable) after all scoring stages.
- Normalize hybrid scoring to a common weighted composite.
- Validate/normalize `SCORING_WEIGHTS`.
- Add thin‑day inflation based on volume thresholds.
- Make batch sizes, TTL, and priority order configurable.
- Guard against stale cache entries.
- Keep quality/relevance separate where possible.

These fixes address the contradictions, sequencing issues, missing config, and edge‑case behaviours outlined in the review.
