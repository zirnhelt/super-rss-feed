# Filter & Priority Logic Review

**Date:** 2026-06-17  
**Model:** north-mini-code-1-0  

---

**Top Findings (most impactful)**
- **Sequencing conflict – early drop before adjustments**  
  *Problem*: `apply_prescore_filter()` discards articles from gated sources based on keyword hits **before** any local boost, source‑type adjustments, or content‑type checks run. A local article that would later receive a 25‑point local boost or a source quality adjustment can be dropped prematurely, reducing local coverage.  
  *Location*: `apply_prescore_filter()` (lines 2343‑2383).  
  *Issue type*: Conflict / sequencing issue.  
  *Severity*: **Blocking** – can cause loss of legitimate local content.

- **Contradictory local handling across stages**  
  *Problem*: The Cohere pre‑filter guarantees that **local articles are never auto‑removed**, yet `filter_by_content_type()` can still drop a recap if `article.local < 50`. Additionally, `Article.should_filter()` blocks non‑local entertainment only when a local signal is absent, but `filter_by_content_type()` unconditionally drops “fluff” regardless of locality. This creates inconsistent treatment of local content between stages.  
  *Location*: `scrub_feed_with_haiku()` (Cohere pre‑filter) and `filter_by_content_type()` (lines 2505‑2534); also `Article.should_filter()` (lines 520‑545).  
  *Issue type*: Conflict across stages.  
  *Severity*: **Blocking** – local articles may be kept by Cohere only to be dropped later.

- **Quality/relevance collapse for Cohere‑scored articles**  
  *Problem*: In `score_articles_with_claude()`, Cohere‑scored articles receive `quality = relevance = article.score`. This merges the two dimensions into a single value, so subsequent `apply_dimension_adjustments()` cannot treat quality and relevance separately, and the final composite formula no longer reflects the configured `w_quality`/`w_relevance` weights for those articles. Sorting by `article.score` therefore deviates from the intended weighted mix for Cohere articles.  
  *Location*: `score_articles_with_claude()` (lines 1970‑2205, where Cohere articles are cached and dimensions are set).  
  *Issue type*: Missing dimensional separation / weight mismatch.  
  *Severity*: **Latent** – scoring drift for Cohere articles may go unnoticed.

---

### Filter Logic
- **Early keyword/source blocking vs later local boost** – `Article.should_filter()` blocks keywords/sources before any dimensional scoring, while `apply_dimension_adjustments()` later adds a 25‑point local boost. A non‑local article that passes the initial keyword check but would be boosted locally can be dropped prematurely.  
  *Location*: `Article.should_filter()` (lines 520‑545) and `apply_dimension_adjustments()` (lines 2445‑2502).  
  *Issue type*: Conflict / sequencing.  
  *Severity*: Latent.

- **Prescore gate caps ignore locality** – `apply_prescore_filter()` caps survivors per source by keyword hits (`max_candidates_per_source`), giving no special consideration to local signals or the later local boost. A local source that would otherwise merit many local articles can have them culled simply because they lack extra hits.  
  *Location*: `apply_prescore_filter()` (lines 2343‑2383).  
  *Issue type*: Sequencing / priority mismatch.  
  *Severity*: Blocking (affects local source representation).

- **Contradictory fluff handling** – `Article.should_filter()` blocks “non‑local entertainment” only when a local signal is missing, but `filter_by_content_type()` drops all `fluff` articles regardless of locality. This double standard can cause a fluff article that slipped through the keyword check to be kept by the first filter only to be removed by the second, wasting earlier processing effort.  
  *Location*: `Article.should_filter()` (lines 520‑545) and `filter_by_content_type()` (lines 2505‑2534).  
  *Issue type*: Conflict across stages.  
  *Severity*: Latent.

### Scoring & Priority
- **Score floor inflation for low‑scoring items** – `apply_dimension_adjustments()` sets `article.score = max(article.score, 80)` for local signals when dimensional scores are missing (the “thin‑day” fallback). This can artificially lift very low‑scoring articles to a high priority, masking genuine performance issues.  
  *Location*: `apply_dimension_adjustments()` (lines 2445‑2502).  
  *Issue type*: Hardcoded inflation / thin‑day behavior.  
  *Severity*: Latent.

- **Source‑type adjustments can be eroded by later penalties** – `apply_dimension_adjustments()` first applies source quality adjustments to `article.quality` (or `article.score`), then later applies a `wire_penalty` to the same `article.quality` if `content_type == 'wire'`. The penalty can partially or fully offset the source boost, leading to unpredictable net effects.  
  *Location*: `apply_dimension_adjustments()` (lines 2445‑2502).  
  *Issue type*: Sequencing / erosion issue.  
  *Severity*: Latent.

- **Hardcoded constants without config surface** –  
  * `batch_size = 40` in `scrub_feed_with_haiku()` (line 2310).  
  * `LIMITS.get('cohere_prefilter_threshold', 2.5)` (line 2240).  
  * `local_bonus` and `wire_penalty` are taken directly from `SCORING_MODIFIERS` but are used as literals elsewhere (e.g., in prints).  
  These values are tightly coupled to the code and make it harder to tune behavior without code changes.  
  *Location*: `scrub_feed_with_haiku()` (lines 2240, 2310) and `apply_dimension_adjustments()` (lines 2450‑2470).  
  *Issue type*: Hardcoded constants / missing config.  
  *Severity*: Latent.

- **Final sort formula mismatch for Cohere articles** – The composite score for regular articles follows `w_quality * Q + w_relevance * R + w_local * L`, but Cohere articles keep the original percentile score (`article.score`) and never recompute. Sorting therefore uses different formulas for different article origins, breaking the intended weight‑balanced priority.  
  *Location*: `score_articles_with_claude()` (Cohere caching) and `compute_composite_score()` (lines 2435‑2442).  
  *Issue type*: Weight mismatch / dimensional collapse.  
  *Severity*: Latent.

### Edge Cases
- **What wins when a local source also matches a high‑volume prescore gate?**  
  The prescore gate (`apply_prescore_filter()`) caps candidates per source by keyword hits, giving priority to articles with more hits. Local boost (`apply_dimension_adjustments()`) does not affect hits, so a non‑local article with higher keyword density can outrank a local article even though the local article would later receive a 25‑point local boost. The gate’s hit‑based ranking therefore wins over later local priority.  
  *Location*: Interaction of `apply_prescore_filter()` (lines 2343‑2383) and `apply_dimension_adjustments()` (lines 2445‑2502).  
  *Issue type*: Priority conflict.  
  *Severity*: Blocking (affects local source representation).

- **Cohere pre‑filter vs later recap filter** – Cohere’s “never auto‑remove local” rule is undermined because `filter_by_content_type()` can still drop a recap if `article.local < 50`. A local recap with low local score survives Cohere but is then removed by the hard content‑type filter, contradicting the intention to protect local content.  
  *Location*: `scrub_feed_with_haiku()` (Cohere logic) and `filter_by_content_type()` (lines 2505‑2534).  
  *Issue type*: Conflict across stages.  
  *Severity*: Blocking.
