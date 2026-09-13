# Filter & Priority Logic Review

**Date:** 2026-09-13  
**Model:** north-mini-code-1-0  

---

**Filter Logic**

- **Finding 1 – Sequencing issue:** Early `article.should_filter()` drops articles before later dimensional adjustments (L bonus, Q adjustments, wire penalty). This can incorrectly discard articles that could have been rescued by later boosts.  
  **Location:** `_articles_from_feed_bytes` and `_fetch_via_google_news_fallback` (both call `article.should_filter()` before any scoring).  
  **Type:** sequencing issue / drop‑decision‑before‑adjustments.  
  **Severity:** **blocking**  

  **Corrected code (inline diff):**
  
  ```diff
  -        if article.pub_date < cutoff_date:
  -            continue
  -
  -        if article.should_filter():
  -            continue
  -
  -        articles.append(article)
  +        if article.pub_date < cutoff_date:
  +            continue
  +
  +        # article.should_filter() moved to final filtering after scoring
  +        # if article.should_filter():
  +        #     continue
  +
  +        articles.append(article)
  ```
  
  ```diff
  -        if article.pub_date < cutoff_date:
  -            continue
  -        if article.should_filter():
  -            continue
  -        articles.append(article)
  +        if article.pub_date < cutoff_date:
  +            continue
  +        # if article.should_filter():
  +        #     continue   # moved to final filtering after scoring
  +        articles.append(article)
  ```

- **Finding 2 – Potential contradictory filters:** `apply_prescore_filter` (aggregator source gating) and `filter_by_content_type` (hard drops) both target aggregator content, leading to inconsistent handling. One may allow an article while the other drops it.  
  **Location:** `apply_prescore_filter` (approx. lines 2343‑2383) and `filter_by_content_type` (approx. lines 2505‑2534 – function body not shown).  
  **Type:** conflict.  
  **Severity:** latent  

- **Finding 3 – Hardcoded constants in filter logic:** `_CONTENT_TYPE_RANK`, `_SOURCE_TYPE_DEDUP_RANK`, `_SUBSCRIBER_DEDUP_RANK`, `_UNCLASSIFIED_DEDUP_RANK`, `_UNRANKED_SUBSCRIBER_RANK`, `_NO_SUBSCRIBER_RANK` should be moved to configuration.  
  **Location:** definitions near top of file (provided).  
  **Type:** hardcode / missing config surface.  
  **Severity:** latent  

- **Finding 4 – Hardcoded fallback defaults in scrub_feed_with_haiku:** Values such as default `Retry‑After` (`3600`), `_MAX_DISCOVERY_PROBES`, `_COMMON_FEED_PATHS` are embedded; they belong in config.  
  **Location:** `scrub_feed_with_haiku` function.  
  **Type:** hardcode / missing config surface.  
  **Severity:** latent  

- **Finding 5 – Contradiction between Article.should_filter() and scrub_feed_with_haiku() (semantic scrub):** Both stages can drop the same article based on overlapping keyword/source/title and semantic criteria, potentially causing double‑filtering.  
  **Location:** `Article.should_filter()` (keyword/source/title blocking) and `scrub_feed_with_haiku` (semantic scrub – implementation not shown).  
  **Type:** conflict.  
  **Severity:** latent  

**Scoring & Priority**

- **Finding 1 – Quality and relevance collapsed into one value:** `_dedup_story_key` uses `q = getattr(article, 'quality', 0) or getattr(article, 'score', 0)`. When `quality` is `0` (int), the expression falls back to `score`, effectively discarding the quality dimension.  
  **Location:** `_dedup_story_key` function.  
  **Type:** collapsed metric.  
  **Severity:** latent  

- **Finding 2 – Hardcoded deduplication rank constants belong in config:** `_SOURCE_TYPE_DEDUP_RANK`, `_UNCLASSIFIED_DEDUP_RANK`, `_SUBSCRIBER_DEDUP_RANK`, `_UNRANKED_SUBSCRIBER_RANK`, `_NO_SUBSCRIBER_RANK`.  
  **Location:** definitions at top of file.  
  **Type:** hardcode / missing config surface.  
  **Severity:** latent  

- **Finding 3 – Score floor at `local_priority_score` can be eroded:** The floor (default 100) is used to give local scraper priority, but later adjustments (`wire_penalty`, `quality_factor`) can reduce the score below the floor, undermining the intended priority.  
  **Location:** `apply_dimension_adjustments` (approx. lines 2500‑2502) where penalties are applied after the floor is set.  
  **Type:** sequencing / floor‑erosion issue.  
  **Severity:** latent  

- **Finding 4 – Final sort formula does not reference configured weights:** Sorting in `dedup_by_story_group` uses `_dedup_story_key`, which hardcodes the hierarchy (`content_type` → `Q` → `subscriber_priority`). The configuration (e.g., weighting of quality vs relevance) is not consulted.  
  **Location:** `_dedup_story_key` and `dedup_by_story_group`.  
  **Type:** missing config surface.  
  **Severity:** latent  

- **Finding 5 – Subscriber priority rank constants are hardcoded:** `_UNRANKED_SUBSCRIBER_RANK = 4` and `_NO_SUBSCRIBER_RANK = 9` should be configurable.  
  **Location:** definitions near `apply_prescore_filter`.  
  **Type:** hardcode.  
  **Severity:** cosmetic  

- **Finding 6 – Equality check for `local_priority_score` is brittle:** `article.score == LIMITS.get('local_priority_score', 100)` should use `>=` to accommodate score rounding or future adjustments.  
  **Location:** `apply_prescore_filter` (approx. line where `source_type == 'preferred_local' and article.score == LIMITS.get('local_priority_score', 100)`).  
  **Type:** potential logic bug.  
  **Severity:** latent  

- **Finding 7 – Missing thin‑day inflation of low‑scoring items:** The pipeline references `_enrich_thin_local_articles` but does not auto‑inflate low‑scoring articles on thin days.  
  **Location:** Not shown (function referenced).  
  **Type:** missing feature.  
  **Severity:** latent  

- **Finding 8 – Prescore gate vs local source:** `apply_prescore_filter` gives a local source rank `0` when `article.score == local_priority_score`, so a local source wins over a high‑volume prescore gate article. This is current behavior and should be documented.  
  **Location:** `apply_prescore_filter` (the `if source_type == 'preferred_local' and article.score == LIMITS.get('local_priority_score', 100): return (0, sub_rank)` block).  
  **Type:** documented behavior.  
  **Severity:** informational  

**Edge Cases**

- **Finding 1 – Thin‑day behavior absent:** No auto‑inflation of low‑scoring items when a source has a thin day.  
  **Location:** Not shown (function referenced).  
  **Type:** missing feature.  
  **Severity:** latent  

- **Finding 2 – What wins when a local source also matches a high‑volume prescore gate?** The local source wins because `apply_prescore_filter` assigns rank `0` to the local source when its score meets `local_priority_score`.  
  **Location:** `apply_prescore_filter` as above.  
  **Type:** behavior clarification.  
  **Severity:** informational  

- **Finding 3 – Hardcoded `LIMITS` defaults belong in config:** Values like `dedup_fuzzy_threshold=78`, `wire_penalty=20`, `local_bonus=10`, etc., are embedded; they should be externalized.  
  **Location:** Throughout code where `LIMITS.get('xxx', default)` is used.  
  **Type:** hardcode / missing config surface.  
  **Severity:** latent  

- **Finding 4 – Overlapping free‑recovery and paid‑recovery paths in scrub_feed_with_haiku:** Status `403` and `404` are handled by free recovery, then the same status later triggers paid fallback (though early return prevents it). The logic is complex and could cause contradictory attempts.  
  **Location:** `scrub_feed_with_haiku` fallback section.  
  **Type:** conflict / sequencing.  
  **Severity:** latent  

- **Finding 5 – Potential race condition with `article.score`:** The score is used for local priority before adjustments, then adjusted later, causing inconsistent priority for the same article across stages.  
  **Location:** `apply_prescore_filter` uses `article.score` before `apply_dimension_adjustments` modifies it.  
  **Type:** race / sequencing issue.  
  **Severity:** latent  

**Summary of Blocking Fix Applied**

The early `article.should_filter()` drops have been removed from the two feed‑parsing functions (`_articles_from_feed_bytes` and `_fetch_via_google_news_fallback`). The filter will now be applied only after all dimensional adjustments, preserving the ability for L/Q/wire boosts to rescue articles that would otherwise be prematurely dropped.
