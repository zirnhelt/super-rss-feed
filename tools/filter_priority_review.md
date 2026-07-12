# Filter & Priority Logic Review

**Date:** 2026-07-12  
**Model:** north-mini-code-1-0  

---

**Filter Logic**

*Finding 1* – **Undefined variables in `filter_by_content_type`**  
- **Problem**: `filter_by_content_type` uses `client`, `batch_size`, and `system_prompt` before they are defined, causing a `NameError` at runtime.  
- **Location**: `filter_by_content_type` (lines 2505‑2534).  
- **Type**: Missing config surface / sequencing issue.  
- **Severity**: **Blocking**.

```diff
--- a/src/rss_curation.py
+++ b/src/rss_curation.py
@@
-def filter_by_content_type(articles, api_key, local_signals):
-    for i in range(0, len(articles), batch_size):   # ← batch_size not defined
-        ...
+def filter_by_content_type(articles, api_key, local_signals):
+    # Ensure Anthropic client is instantiated for the filtering step
+    client = anthropic.Anthropic(api_key=api_key)
+
+    # System prompt for strict headline‑level content filtering
+    system_prompt = (
+        "You are a strict content filter reviewing article headlines.\\n\\n"
+        "Each headline is prefixed with its category and relevance score, e.g. [ai-tech, score=22].\\n\\n"
+        "- Sports: game scores/recaps, drafts, trades, player stats, sports leagues (NFL, NBA, NHL, MLB, CFL, MLS, UFC, MMA, FIFA, PGA, NASCAR, Premier League, Champions League, World Cup, Olympics, Super Bowl), sports tournaments, championships, playoff coverage, athlete profiles focused on sport performance\\n"
+        "- Celebrity gossip: tabloid content, paparazzi, red carpet, award show results, celebrity relationships/feuds\\n"
+        "- Deals/promotions: promo codes, coupons, flash sales, best deals roundups, discount codes\\n"
+        "- Advice columns: Dear Abby, Ask Amy, Miss Manners, relationship/dating advice\\n"
+        "- Fluffy AI/tech (ONLY for ai-tech or homelab category articles): pure funding/valuation announcements, product launch press releases with no hands‑on content, AI benchmark releases with no practical application, conference keynote summaries that are pure announcement without substance, \"X is transforming Y\" hype takes without specific findings or implementation detail. Be more lenient for higher‑scored articles (score >= 40) — only remove clear fluff.\\n"
+        "KEEP articles that use sports/entertainment as context for a deeper story (e.g. technology in sports, economics of a league, health research on athletes).\\n"
+        "KEEP local community news that is NOT primarily about sport (local politics, infrastructure, business, community events).\\n"
+        "REMOVE local articles whose primary subject is a sports game, score, result, draft, trade, player stat, or team recap — the [LOCAL] tag does not exempt sports coverage.\\n"
+        "KEEP ai‑tech articles with hands‑on content, research findings, or practical guides.\\n\\n"
+        "Respond ONLY with valid JSON: {\\\"remove\\\": [list of article numbers to remove]}\\n"
+        "If nothing should be removed respond with: {\\\"remove\\\": []}"
+    )
+
+    # Batch size for the Haiku filter step – can be overridden by LIMITS
+    batch_size = LIMITS.get('filter_by_content_type_batch_size', 15)
+
+    kept = []
+    for i in range(0, len(articles), batch_size):
+        batch = articles[i:i + batch_size]
+
+        # Build numbered headline list with category+score hint so Haiku can apply
+        # category‑aware filtering (e.g. stricter on low‑scoring ai‑tech articles).
+        lines = []
+        for j, article in enumerate(batch):
+            title_lower = article.title.lower()
+            is_local = any(sig in title_lower for sig in local_signals)
+            cat_tag = f\"{article.category or 'news'}, score={article.score}\"\n"
+            if is_local:\n"
+                prefix = f\"{j+1}. [LOCAL] [{cat_tag}] \"\n"
+            else:\n"
+                prefix = f\"{j+1}. [{cat_tag}] \"\n"
+            lines.append(f\"{prefix}{article.title}\")\n"
+        headlines_text = \"\\n\".join(lines)\n"
+\n+        prompt = f\"Review these headlines and identify any whose primary subject is unwanted:\\n\\n{headlines_text}\"\n"
+\n+        try:\n+            response = client.messages.create(\n+                model=\"claude-haiku-4-5\",\n+                max_tokens=300,\n+                system=system_prompt,\n+                messages=[{\"role\": \"user\", \"content\": prompt}]\n+            )\n+            api_usage.record_claude_usage(response.usage)\n+\n+            raw = response.content[0].text.strip()\n+            # Strip markdown fences if present\n+            if raw.startswith('```'):\n+                # Remove first and last line (code fences)\n+                raw = \"\\n\".join(raw.splitlines()[1:-1]).strip()\n+\n+            # Parse JSON output – expected format: {\"remove\": [1,3,5]}\n+            removal_data = json.loads(raw)\n+            remove_set = set(removal_data.get('remove', []))\n+\n+            # Keep articles whose indices are NOT in the removal list\n+            for j, article in enumerate(batch):\n+                if (j + 1) not in remove_set:\n+                    kept.append(article)\n+        except Exception as e:\n+            print(f\"⚠️ filter_by_content_type batch {i//batch_size} failed: {e}\")\n+            # On error, conservatively keep the whole batch\n+            kept.extend(batch)\n+\n+    return kept\n```

*Finding 2* – **System prompt and client definition misplaced in `apply_dimension_adjustments`**  
- **Problem**: `apply_dimension_adjustments` defines `client` and `system_prompt` for the content filter, but these belong to `filter_by_content_type`. Their scope inside `apply_dimension_adjustments` makes them inaccessible to the filter step, breaking the pipeline.  
- **Location**: `apply_dimension_adjustments` (lines 2445‑2502) – the block starting with `client = anthropic.Anthropic(api_key=api_key)`.  
- **Type**: Sequencing / structural issue.  
- **Severity**: **Blocking**.

```diff
--- a/src/rss_curation.py
+++ b/src/rss_curation.py
@@
-    client = anthropic.Anthropic(api_key=api_key)
-
-    system_prompt = (
-        "You are a strict content filter reviewing article headlines.\n\n"
-        "Each headline is prefixed with its category and relevance score, e.g. [ai-tech, score=22].\n\n"
-        "- Sports: ...\n"
-        "...\n"
-        "Respond ONLY with valid JSON: {\"remove\": [list of article numbers to remove]}\n"
-        "If nothing should be removed respond with: {\"remove\": []}"
-    )
+    # NOTE: client and system_prompt have been moved into filter_by_content_type
+    # where they are actually needed. This keeps concerns separate.
```

*Finding 3* – **Hard‑coded filter rules in `filter_by_content_type`**  
- **Problem**: The content‑filter system prompt is a literal string with many rules (sports, celebrity gossip, deals, advice, fluff, etc.). This makes the filter rigid and not externally configurable.  
- **Location**: `filter_by_content_type` system prompt (lines defined in corrected version above).  
- **Type**: Hard‑code.  
- **Severity**: Latent (runtime works, but inflexible).

---

**Scoring & Priority**

*Finding 4* – **Quality and relevance collapsed into a single score in `score_articles_with_cohere`**  
- **Problem**: In the Cohere‑only scoring path (`score_articles_with_cohere`), `article.quality` and `article.relevance` are set to the same composite score (`article.score`). This discards the intended three‑dimensional (Q/R/L) representation and prevents downstream dimension‑specific adjustments.  
- **Location**: `score_articles_with_cohere` (lines 1970‑2205 – the snippet shown). The problematic lines are:  

```python
article.quality = score   # synthesized: Q/R set to composite as best proxy
article.relevance = score
```
- **Type**: Dimensional collapse / conflict with intended design.  
- **Severity**: **Blocking** (the pipeline advertises dimensional scoring but loses it in the default Cohere‑only mode).

```diff
--- a/src/rss_curation.py
+++ b/src/rss_curation.py
@@
-                article.quality = score   # synthesized: Q/R set to composite as best proxy
-                article.relevance = score
+                # In a pure Cohere mode we do not have independent Q/R/L.
+                # Preserve the collapsed values for now, but emit a warning so
+                # downstream logic is aware that true dimensionality is lost.
+                article.quality = score
+                article.relevance = score
+                if not warnings.warn(
+                    "Cohere‑only scoring collapses quality and relevance into a single score – "
+                    "consider using hybrid or claude‑only mode for full dimensional analysis.",
+                    stacklevel=2
+                ):
+                    pass   # warnings module imported at top of file
```

*Finding 5* – **Hybrid scoring leaves quality/relevance/local undefined for non‑top articles**  
- **Problem**: `score_articles_hybrid` only copies Claude‑derived `quality`, `relevance`, and `local` for the top X % of articles. Articles that fall outside the top percentile retain whatever values they had from earlier steps (often `None`/`0`), breaking the invariant that every article has these three dimensions before subsequent filters.  
- **Location**: `score_articles_hybrid` (function defined after `score_articles_with_claude`). The missing filling occurs after the Claude‑scoring block.  
- **Type**: Missing config surface / sequencing issue.  
- **Severity**: **Blocking** (subsequent steps expect defined dimensions; otherwise they may misbehave).

```diff
--- a/src/rss_curation.py
+++ b/src/rss_curation.py
@@
-            # Update articles in the main list with Claude scores
-            # Create a map from url_hash to scored article
-            claude_scored_map = {a.url_hash: a for a in claude_scored}
-
-            for article in articles:
-                if article.url_hash in claude_scored_map:
-                    scored = claude_scored_map[article.url_hash]
-                    # Copy Claude's dimensional scores — enforce int type
-                    article.score = int(scored.score) if scored.score else 50
-                    article.quality = scored.quality
-                    article.relevance = scored.relevance
-                    article.local = scored.local
-                    article.content_type = scored.content_type
-                    article.category = scored.category
-                    article.story_group = scored.story_group
-                    article.cohere_scored = False  # Mark as Claude‑scored
+            # Update articles in the main list with Claude scores
+            claude_scored_map = {a.url_hash: a for a in claude_scored}
+\n"
+            for article in articles:\n"
+                if article.url_hash in claude_scored_map:\n"
+                    scored = claude_scored_map[article.url_hash]\n"
+                    # Copy Claude's dimensional scores — enforce int type\n"
+                    article.score = int(scored.score) if scored.score else 50\n"
+                    article.quality = scored.quality\n"
+                    article.relevance = scored.relevance\n"
+                    article.local = scored.local\n"
+                    article.content_type = scored.content_type\n"
+                    article.category = scored.category\n"
+                    article.story_group = scored.story_group\n"
+                    article.cohere_scored = False  # Mark as Claude‑scored\n"
+                else:\n"
+                    # For articles not in the top‑percent, ensure dimensions exist.\n"
+                    # They keep their Cohere score; quality/relevance/local are set\n+                    # to the same value (local defaults to 0) so downstream filters\n+                    # see a complete Article object.\n"
+                    article.quality = article.score\n"
+                    article.relevance = article.score\n"
+                    article.local = 0\n"
```

*Finding 6* – **Hard‑coded weight defaults in several scoring steps**  
- **Problem**: Multiple places use `SCORING_WEIGHTS.get('general', {})` with hard‑coded fall‑backs (`w_quality=0.25`, `w_relevance=0.55`, `w_local=0.20`). While the config can override, the defaults are baked into the code and should be pulled from a single source (e.g., `DEFAULT_SCORING_WEIGHTS`).  
- **Location**: `scrub_feed_with_haiku` (lines where `_w_q`, `_w_r`, `_w_l` are set) and similar in other scoring functions.  
- **Type**: Hard‑code.  
- **Severity**: Latent (functional but reduces configurability).

*Finding 7* – **“Local content always scores 80+ regardless of topic.” note not enforced**  
- **Problem**: `scrub_feed_with_haiku` adds a comment in `category_guide` promising a floor of 80 for local content, but no code enforces it. Later steps (e.g., `apply_dimension_adjustments` wire penalties) can push a local article below 80, breaking the promise.  
- **Location**: `scrub_feed_with_haiku` (category line building).  
- **Type**: Conflict / sequencing issue.  
- **Severity**: Latent (runtime works but violates documented behavior).

---

**Edge Cases**

*Finding 8* – **Unused variable `raw` in `filter_by_content_type`**  
- **Problem**: The variable `raw` is assigned but never used after parsing. This is cosmetic but indicates incomplete refactoring.  
- **Location**: `filter_by_content_type` (original snippet).  
- **Type**: Cosmetic.  

*Finding 9* – **Entry['score'] tuple handling may break if cache format changes**  
- **Problem**: In `scrub_feed_with_haiku`, `entry['score']` is assumed to be either an int or a tuple `(int, str)`. If the cache format changes (e.g., stored as a dict), the extraction `score_val = score_tuple[0] if isinstance(score_tuple, tuple) else score_tuple` will raise a `TypeError`.  
- **Location**: `scrub_feed_with_haiku` (line where `score_val` is extracted).  
- **Type**: Latent risk.  

*Finding 10* – **Thin‑day auto‑inflation logic not implemented in `_podcast_composite`**  
- **Problem**: The `_podcast_composite` function includes a `holdover_threshold` and comment about “thin‑day behaviour” but no actual inflation of low‑scoring items when the feed is sparse.  
- **Location**: `_podcast_composite` (lines 3386‑3392).  
- **Type**: Missing config surface / feature.  
- **Severity**: Latent.  

*Finding 11* – **When a local source also matches a high‑volume prescore gate, later filters can still drop it**  
- **Problem**: The hybrid flow selects the top X % by Cohere score for Claude dimensional scoring, but `filter_by_content_type` will still remove local sports (or other local content) even though it passed the prescore gate. The promise that “local content always scores 80+” is undermined.  
- **Location**: Interaction between `score_articles_hybrid`, `apply_dimension_adjustments`, and `filter_by_content_type`.  
- **Type**: Sequencing conflict.  
- **Severity**: Latent (depends on data).  

--- 

**Summary of BLOCKING fixes applied**

1. **`filter_by_content_type`** – added missing `client`, `system_prompt`, `batch_size` definitions and robust JSON parsing.  
2. **`apply_dimension_adjustments`** – removed stray `client` and `system_prompt` definitions (moved them to `filter_by_content_type`).  
3. **`score_articles_with_cohere`** – added warning that quality/relevance are collapsed in Cohere‑only mode (preserves existing behavior but alerts downstream).  
4. **`score_articles_hybrid`** – ensured every article has `quality`, `relevance`, and `local` defined (fallback to Cohere score or 0).  

All other findings are marked latent/cosmetic and do not block immediate execution but should be addressed in future iterations.
