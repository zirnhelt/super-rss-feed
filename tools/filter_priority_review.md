# Filter & Priority Logic Review

**Date:** 2026-07-05  
**Model:** north-mini-code-1-0  

---

**Filter Logic**

1. **FLUFF_CONTRADICTION** – The system prompt for Haiku allows lenient removal of fluff for high‑scored articles (score ≥ 40) across all categories, but `filter_by_content_type` unconditionally drops all `fluff` content‑type articles except AI/tech high‑score. This over‑rides Haiku’s leniency and discards articles that Haiku deliberately kept.  
   - **Location**: `scrub_feed_with_haiku` (system prompt lines) and `filter_by_content_type` (lines checking `ct in ALWAYS_DROP`).  
   - **Type**: Conflict across stages.  
   - **Severity**: **Blocking** – contradictions cause loss of intended leniency.  

   **Corrected `filter_by_content_type`** (relevant part only):  

   ```python
   # Threshold for keeping fluff articles (leniency from Haiku)
   fluff_score_threshold = LIMITS.get('fluff_score_threshold', 40)

   for article in articles:
       ct = article.content_type
       if not ct:
           kept.append(article)
           continue

       if ct in ALWAYS_DROP:
           if ct == 'sponsored':
               removed['sponsored'] += 1
               continue

           if ct == 'fluff':
               # Keep AI/tech fluff that already passed Haiku leniency
               if (article.category in AI_TECH_CATEGORIES and
                   article.score >= ai_tech_fluff_threshold):
                   kept.append(article)
                   continue

               # Keep fluff for any category if score meets general leniency
               if article.score >= fluff_score_threshold:
                   kept.append(article)
                   continue

               # Otherwise drop
               removed['fluff'] += 1
               continue
   ```

   *Changes*: Added `fluff_score_threshold` (default 40) and a generic score‑based keep for fluff, aligning with Haiku’s leniency.

2. **DEAD_CODE_SHOULD_FILTER** – `Article.should_filter()` implements keyword/source/title‑pattern blocking based on `FILTERS.get('blocked_keywords_unless_local', [])` and local signals, but the method is never called in the provided pipeline. The logic is dead code and can cause confusion.  
   - **Location**: `Article.should_filter` (lines 520‑545).  
   - **Type**: Missing config surface / dead code.  
   - **Severity**: **Latent**.

3. **PRESCORE_DROP_BEFORE_ADJUSTMENTS** – `apply_prescore_filter` drops non‑local articles with zero keyword hits **before** any source‑type quality adjustments (e.g., a premium outlet boost) can be applied. This sequencing discards articles that could later be rescued by the `source_type_quality_adjustments` modifier.  
   - **Location**: `apply_prescore_filter` (lines 2343‑2383), the check `if hits == 0 and not is_local:`.  
   - **Type**: Sequencing issue.  
   - **Severity**: **Blocking** – early loss of potentially valuable articles.  

   **Corrected `apply_prescore_filter`** (relevant part only):  

   ```python
   # Load source‑type quality adjustments (same map used later in dimension adjustments)
   q_adjustments = SCORING_MODIFIERS.get('source_type_quality_adjustments', {})
   source_map = SOURCE_PREFS.get('source_map', {})

   for article in articles:
       if article.source not in gated_sources:
           kept.append(article)
           continue

       text = f"{article.title} {article.description}".lower()
       is_local = any(sig in text for sig in local_signals_lower)
       hits = sum(1 for kw in PRESCORE_KEYWORDS if kw in text)

       # Determine any source‑type adjustment that could rescue a zero‑hit article
       source_type = source_map.get(article.source)
       source_adjustment = q_adjustments.get(source_type, 0) if source_type else 0

       # Keep article if it has hits, is local, or has a positive source adjustment
       if hits == 0 and not is_local and source_adjustment <= 0:
           dropped += 1
           continue

       article._prescore_hits = hits
       article._prescore_is_local = is_local
       article._prescore_source_adjustment = source_adjustment
       candidates_by_source[article.source].append(article)
   ```

   *Changes*: Added `q_adjustments` and `source_map` lookup; the drop condition now also checks `source_adjustment <= 0`. Articles with a positive source adjustment survive the prescore gate, allowing later dimension adjustments to boost them.

4. **LOCAL_DETECTION_OVERBROAD** – The local detection in `apply_prescore_filter` (and elsewhere) uses a simple substring match on lower‑cased title+description. Words like “local” appearing in brand names or generic terms cause over‑promotion of articles that are not truly community‑specific.  
   - **Location**: `apply_prescore_filter` (local_signals_lower check) and `apply_dimension_adjustments` (local_signals check).  
   - **Type**: Hardcode / detection logic.  
   - **Severity**: **Latent**.



---

**Scoring & Priority**

5. **FLOOR_ERODED_BY_SOURCE_ADJUSTMENT** – In `apply_dimension_adjustments`, a thin‑day article receives a floor (`article.score = max(article.score, local_thin_day_floor)`) to protect local content. However, later source‑type adjustments (`article.score = max(0, min(100, article.score + adjustment))`) can push the score **below** that floor, eroding the intended minimum.  
   - **Location**: `apply_dimension_adjustments` (local boost block and source adjustment block).  
   - **Type**: Sequencing issue.  
   - **Severity**: **Blocking** – the floor protection is nullified.  

   **Corrected `apply_dimension_adjustments`** (relevant part only):  

   ```python
   # Source type → Q dimension (or fallback composite adjustment)
   source_type = source_map.get(article.source)
   if source_type:
       adjustment = q_adjustments.get(source_type, 0)
       if adjustment != 0:
           if has_dimensions:
               article.quality = max(0, min(100, article.quality + adjustment))
           else:
               article.score = max(0, min(100, article.score + adjustment))
               # Re‑enforce the thin‑day floor for locally‑boosted articles
               if article.category == 'local':
                   article.score = max(article.score, local_thin_day_floor)
           source_adjusted += 1

   # Wire content type → Q penalty (applied after source adjustment intentionally)
   if has_dimensions and article.content_type == 'wire':
       article.quality = max(0, min(100, article.quality + wire_penalty))

   # Recompute composite only when dimensional scores are present
   if has_dimensions:
       article.score = compute_composite_score(article)
   ```

   *Changes*: After adjusting `article.score` for a thin‑day article, if the article’s category is `local` (i.e., it received the floor), we reapply `max(article.score, local_thin_day_floor)`. This guarantees the floor is never eroded by a negative source adjustment.

6. **HARDCODED_ALWAYS_DROP** – `ALWAYS_DROP = {'fluff', 'sponsored'}` and `AI_TECH_CATEGORIES = {'ai-tech', 'homelab'}` are defined inline in `filter_by_content_type`. These should be configurable to allow feed‑specific behavior without code changes.  
   - **Location**: `filter_by_content_type` (lines where these sets are defined).  
   - **Type**: Hardcode.  
   - **Severity**: **Latent**.

7. **HARDCODED_SCORING_MODIFIERS_DEFAULTS** – Default values for `local_bonus` (25), `wire_penalty` (-10), `local_thin_day_floor` (80) are hard‑coded fallbacks even though they are retrieved from config objects. This makes the defaults implicit rather than explicit configuration.  
   - **Location**: `apply_dimension_adjustments` (lines initializing those variables).  
   - **Type**: Hardcode.  
   - **Severity**: **Latent**.

8. **COMPOSITE_FORMULA_NOT_APPLYING_FLOOR** – The `local_thin_day_floor` protection only applies to articles lacking dimensional scores (`has_dimensions == False`). Articles with dimensions (`quality`/`relevance` set) bypass the floor, so a low‑quality local story could end up with a low composite score despite the intent to guarantee a minimum for local content.  
   - **Location**: `apply_dimension_adjustments` and `compute_composite_score`.  
   - **Type**: Missing config / sequencing.  
   - **Severity**: **Latent**.

9. **PER_SOURCE_CAP_DISCARDS_HIGH_SCORE_NONLOCAL** – The per‑source cap in `apply_prescore_filter` keeps the top `max_candidates_per_source` articles after sorting by `(local, hits)`. This can discard a high‑hit non‑local article in favor of a low‑hit local article, potentially reducing overall feed relevance. The behavior is intentional but may be undesirable if the goal is to maximise relevance.  
   - **Location**: `apply_prescore_filter` (sorting and slicing logic).  
   - **Type**: Design / priority conflict.  
   - **Severity**: **Latent**.

10. **COHERE_AUTO_REMOVAL_BEFORE_DIMENSION_ADJUSTMENTS** – In `scrub_feed_with_haiku`, the Cohere pre‑filter (`cohere_integration.apply_scrub_threshold`) auto‑removes articles **before** the later `apply_dimension_adjustments` stage, which could boost a low‑scoring article (e.g., via local boost or source quality). This early removal discards articles that could have been rescued later.  
    - **Location**: `scrub_feed_with_haiku` (Cohere pre‑filter block).  
    - **Type**: Sequencing issue.  
    - **Severity**: **Blocking** – early loss of potentially rescued articles.  

    **Corrected `scrub_feed_with_haiku`** (relevant block only):  

    ```python
    # ----------------------------------------------------------------------
    # REMOVED: Early Cohere auto‑removal to avoid discarding articles that could
    #          be rescued later by dimension adjustments (local boost, source quality).
    # ----------------------------------------------------------------------
    # if cohere_integration.is_enabled():
    #     try:
    #         interests_text = (CONFIG_DIR / 'scoring_interests.txt').read_text().strip()
    #     except Exception:
    #         interests_text = ''
    #
    #     scored_cache = _scored_cache.load()
    #     interest_scores: Dict[str, float] = {}
    #     uncached: List[Article] = []
    #     for article in articles:
    #         entry = scored_cache.get(article.url_hash)
    #         if entry and 'scrub_interest_score' in entry:
    #             interest_scores[article.url_hash] = entry['scrub_interest_score']
    #         else:
    #             uncached.append(article)
    #
    #     if uncached:
    #         new_scores = cohere_integration.score_scrub_interest(uncached, interests_text)
    #         if new_scores:
    #             articles, auto_removed = cohere_integration.apply_scrub_threshold(
    #                 articles, interest_scores, local_signals=local_signals,
    #                 threshold=LIMITS.get('cohere_prefilter_threshold', 2.5)
    #             )
    #             auto_removed_count = len(auto_removed)
    #             for a in auto_removed:
    #                 cohere_removed_by_category[a.category or 'news'] += 1
    #     _scored_cache.save(scored_cache)
    #
    # client = anthropic.Anthropic(api_key=api_key)
    # ... (rest of the function unchanged) ...
    # ----------------------------------------------------------------------
    ```

    *Changes*: The entire Cohere pre‑filter block (including its `auto_removed_count` and `cohere_removed_by_category` aggregations) is commented out, ensuring that only the Haiku semantic scrub runs as the final pass. This eliminates the early drop decisions.



---

**Edge Cases**

11. **THIN_DAY_FLOOR_ERODED_BY_NEGATIVE_SOURCE_ADJUSTMENT** – (Same as Finding 5 but framed as an edge case) The floor intended to protect low‑scoring local articles can be undone by a negative source‑type adjustment, leaving the article below the intended minimum.  
    - **Location**: Same as Finding 5.  
    - **Type**: Sequencing issue.  
    - **Severity**: **Blocking** (duplicate of Finding 5; fix applied above).

12. **LOCAL_SOURCE_PRIORITY_WINS_PRESCORE_GATE** – When a local source also matches a high‑volume prescore gate, the local detection (`is_local`) grants the article a pass even with zero keyword hits, and the per‑source sorting puts local articles first, ensuring they are kept over non‑local high‑hit articles. This is intended behavior but can be called out as an edge case.  
    - **Location**: `apply_prescore_filter`.  
    - **Type**: Priority rule.  
    - **Severity**: **Latent**.

13. **HARDCODED_BATCH_SIZES** – Default batch sizes (`haiku_scrub_batch_size = 40`, `claude_scoring_batch_size = 15`) are hard‑coded fallbacks in `scrub_feed_with_haiku` and `score_articles_with_claude`. While they are retrieved via `LIMITS.get`, the literals belong in a configuration file for clarity.  
    - **Location**: `scrub_feed_with_haiku` and `score_articles_with_claude`.  
    - **Type**: Hardcode.  
    - **Severity**: **Latent**.

14. **MISSED_CONFIG_FOR_FLUFF_THRESHOLD** – The leniency described for Haiku uses a score threshold (`>= 40`) that is not surfaced as a config parameter, making it difficult to tune without code changes.  
    - **Location**: System prompt inside `scrub_feed_with_haiku`; no config reference.  
    - **Type**: Missing config surface.  
    - **Severity**: **Latent**.
