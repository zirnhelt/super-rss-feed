# Filter & Priority Logic Review

**Date:** 2026-06-18  
**Model:** north-mini-code-1-0  

---

## Top Findings
- **Article.should_filter** incorrectly blocks local sports news via generic keyword filters before the later “KEEP all local community news” rule takes effect. *(Filter Logic conflict – blocking)*
- **apply_prescore_filter** drops articles from gated sources (including local ones) based solely on interest keywords, ignoring local signals, causing premature removal of local content that should be preserved later. *(Sequencing / conflict – blocking)*

---

### Filter Logic
- **Early keyword filter overrides local exception**
  - **Problem:** `Article.should_filter` returns `True` for any article whose title/description contains a blocked keyword (e.g., “sports”), regardless of the article’s source being local. Later stages (e.g., `scrub_feed_with_haiku` and `filter_by_content_type`) explicitly say “KEEP all local community news even if sports‑related.” This creates a contradiction where a local article that mentions sports is dropped before the local‑preservation logic runs.
  - **Location:** `Article.should_filter` (≈ lines 520‑545).
  - **Type:** Conflict (filter vs. later exception).
  - **Severity:** **Blocking** – local news that matches a blocked keyword is permanently removed.

- **Haiku leniency vs. hard‑coded fluff removal**
  - **Problem:** The Haiku system prompt is instructed to be lenient for AI/tech articles with a score ≥ 40 (“only remove clear fluff”). However, `filter_by_content_type` unconditionally drops any article whose `content_type` is `fluff`, regardless of score or category. This effectively nullifies Haiku’s leniency and removes high‑scoring AI/tech fluff that should have been kept.
  - **Location:** `scrub_feed_with_haiku` (system prompt) and `filter_by_content_type` (≈ lines 2505‑2534).
  - **Type:** Conflict / Hard‑coded threshold.
  - **Severity:** **Latent** – only matters if Claude assigns `content_type='fluff'` to a high‑scoring AI/tech article; the later filter will still drop it despite the intended leniency.

- **Prescore gate ignores local signals**
  - **Problem:** `apply_prescore_filter` drops articles from sources listed in `prescore_keyword_filter.sources` unless they contain at least one `CATEGORY_RULES` interest keyword. It does **not** consider `FILTERS['local_signals']`, so a local article from a gated source will be dropped even though the pipeline’s later stages treat all local content as priority (e.g., automatic category = `local` and score floor).
  - **Location:** `apply_prescore_filter` (≈ lines 2343‑2383).
  - **Type:** Sequencing / Conflict (gate before local boost).
  - **Severity:** **Blocking** – local articles from gated sources can be removed before any local‑preservation adjustments run.

### Scoring & Priority
- **Hard‑coded score floor (thin‑day) value**
  - **Problem:** The thin‑day fallback consistently uses the literal `80` (`article.score = max(article.score, 80)`) in both `apply_dimension_adjustments` and `filter_by_content_type`. This numeric floor should be configurable (e.g., via `SCORING_MODIFIERS` or `CONFIG`). The default is baked into the logic.
  - **Location:** `apply_dimension_adjustments` (local‑boost block) and `filter_by_content_type` (local‑pass block).
  - **Type:** Hard‑coded constant.
  - **Severity:** **Cosmetic** (functionality works, but the value belongs in config).

- **Hard‑coded adjustment defaults**
  - **Problem:** `SCORING_MODIFIERS` fallbacks are literal values: `local_keyword_bonus` defaults to `25`, `wire_quality_penalty` defaults to `-10`. Likewise, `LIMITS` fallbacks (`cohere_prefilter_threshold = 2.5`, `haiku_scrub_batch_size = 40`) and the Claude scoring batch size (`15`) are all hard‑coded. These should be read from configuration rather than being embedded as defaults.
  - **Location:** `apply_dimension_adjustments` (local_bonus, wire_penalty); `scrub_feed_with_haiku` (LIMITS.get calls); `score_articles_with_claude` (batch_size = 15).
  - **Type:** Hard‑coded constant.
  - **Severity:** **Cosmetic** (affects only the rare case where config is missing; still a maintainability issue).

- **AI/tech fluff removal threshold**
  - **Problem:** `filter_by_content_type` uses a literal `article.score < 30` to decide whether to strip AI/tech fluff. This threshold is not exposed as a config parameter, making it impossible to adjust the stringency without code changes.
  - **Location:** `filter_by_content_type` (AI/tech block).
  - **Type:** Hard‑coded constant.
  - **Severity:** **Cosmetic** (tuning only).

- **Composite‑score formula matches config weights**
  - **Problem:** `compute_composite_score` reads `SCORING_WEIGHTS['general']` for `w_quality`, `w_relevance`, `w_local`. No deviation is observed, so the final sort (presumably based on `article.score`) aligns with the configured weights. *No issue found*—the implementation correctly uses the configuration.
  - **Location:** `compute_composite_score` (≈ lines 2435‑2442).
  - **Type:** None.
  - **Severity:** N/A.

### Edge Cases
- **Thin‑day inflation is limited to local content**
  - **Problem:** The pipeline’s “thin‑day” behavior only floors `article.score` to `80` for articles that satisfy `local_signals`. Non‑local articles receive no automatic floor, even on days with very low volume. This asymmetry could lead to legitimate local news being unfairly deprioritized on low‑volume days if it fails other filters.
  - **Location:** `apply_dimension_adjustments` and `filter_by_content_type` (local‑pass block).
  - **Type:** Design / sequencing issue.
  - **Severity:** **Latent** – only noticeable when the feed is unusually sparse and local articles are low‑scoring.

- **Drop decisions made before local boost**
  - **Problem:** Both `Article.should_filter` and `apply_prescore_filter` can eliminate articles **before** `apply_dimension_adjustments` runs. Consequently, a local article that would have received the `local_keyword_bonus` and the `80` thin‑day floor is already gone, defeating the pipeline’s local‑preservation intent.
  - **Location:** `Article.should_filter` and `apply_prescore_filter`.
  - **Type:** Sequencing / premature drop.
  - **Severity:** **Blocking** – the local‑priority adjustments become moot for any article removed earlier.

- **Local source vs. prescore gate outcome**
  - **Problem:** When a source appears in the `prescore_keyword_filter.sources` list, the gate’s keyword‑based survival rule dominates over the later local‑priority logic. A local article from such a source will be dropped if it lacks a matching interest keyword, even though the pipeline’s “KEEP all local community news” rule would otherwise protect it.
  - **Location:** `apply_prescore_filter` (keyword test) combined with later local handling.
  - **Type:** Conflict (gate precedence).
  - **Severity:** **Blocking** – the gate’s rule currently wins, contradicting the pipeline’s stated local‑news guarantee.
