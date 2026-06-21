# Filter & Priority Logic Review

**Date:** 2026-06-21  
**Model:** north-mini-code-1-0  

---

**Filter Logic**

**1. Duplicate prescore filter logic** – *Conflict / Hardcoded duplication* – **Blocking**  
The identical prescore keyword + per‑source‑cap gate appears in two places:  
- `scrub_feed_with_haiku` (lines ≈ 2208‑2339) – misnamed, contains the prescore filter.  
- `apply_prescore_filter` (lines ≈ 2343‑2383) – the intended prescore gate.  

Having the same logic in two functions causes contradictory gating and unnecessary work.  
**Fix:** Remove the duplicate implementation from `scrub_feed_with_haiku`. Keep `apply_prescore_filter` as the sole prescore gate.  

```diff
-    # ----- DUPLICATE PRE‑SCORE FILTER (remove) -----
-    """
-    config = SOURCE_PREFS.get('prescore_keyword_filter', {})
-    gated_sources = set(config.get('sources', []))
-    if not gated_sources:
-        return articles
-
-    max_candidates = config.get('max_candidates_per_source', 15)
-
-    local_signals_lower = [s.lower() for s in FILTERS.get('local_signals', [])]
-
-    kept = []
-    candidates_by_source = defaultdict(list)
-    dropped = 0
-    for article in articles:
-        if article.source not in gated_sources:
-            kept.append(article)
-            continue
-        text = f"{article.title} {article.description}".lower()
-        is_local = any(sig in text for sig in local_signals_lower)
-        hits = sum(1 for kw in PRESCORE_KEYWORDS if kw in text)
-        # Local articles pass through even with zero keyword hits — the pipeline's
-        # local-preservation rules must have a chance to run. Non-local zero-hit
-        # articles are dropped as off-topic for this feed's interests.
-        if hits == 0 and not is_local:
-            dropped += 1
-            continue
-        article._prescore_hits = hits
-        article._prescore_is_local = is_local
-        candidates_by_source[article.source].append(article)
-
-    for source, candidates in candidates_by_source.items():
-        # Sort local articles first, then by keyword-hit density, so local content
-        # is never bumped off the per-source cap by higher-hit non-local articles.
-        candidates.sort(key=lambda a: (a._prescore_is_local, a._prescore_hits), reverse=True)
-        kept.extend(candidates[:max_candidates])
-        dropped += max(0, len(candidates) - max_candidates)
-
-    if dropped:
-        print(f"🔎 Prescore keyword filter ({', '.join(sorted(gated_sources))}): dropped {dropped} articles")
-
-    return kept
```

**2. Early zero‑hit drop in `apply_prescore_filter`** – *Sequencing issue* – **Blocking**  
In `apply_prescore_filter` (≈ line 2360) the code drops every non‑local article that has **zero** prescore keyword hits (`if hits == 0 and not is_local:`). This decision is made **before** any dimension‑level adjustments (local boost, thin‑day floor, source quality adjustments). Articles that would be rescued by those later steps are therefore lost.  
**Fix:** Allow zero‑hit non‑local articles to pass; let later stages apply preservation logic.  

```diff
-        # Local articles pass through even with zero keyword hits — the pipeline's
-        # local-preservation rules must have a chance to run. Non-local zero-hit
-        # articles are dropped as off-topic for this feed's interests.
-        if hits == 0 and not is_local:
-            dropped += 1
-            continue
+        # Allow all articles to proceed; local‑preservation rules and later
+        # dimension adjustments will handle zero‑hit items.
```

---

**Scoring & Priority**

**1. Thin‑day floor erosion by later penalties** – *Sequencing issue* – **Blocking**  
`apply_dimension_adjustments` (≈ lines 2445‑2502) first lifts any article whose score is below `local_thin_day_floor` (default 80) to that floor and marks it `category='local'`. Afterwards, source‑type quality adjustments and the optional wire penalty can reduce `article.quality`. When the composite score is recomputed, the final `article.score` can fall **below** the floor, erasing the floor boost. The floor is never re‑enforced after those later changes.  
**Fix:** Re‑apply the thin‑day floor for **every** article after **all** adjustments (including source adjustments, wire penalty, and recompute). This guarantees the floor survives.  

```diff
        # Recompute composite only when dimensional scores are present
        if has_dimensions:
            article.score = compute_composite_score(article)

        # Ensure thin‑day floor survives any later adjustments
        article.score = max(article.score, local_thin_day_floor)
```

*The above block is inserted directly after the `if has_dimensions:` recompute block (and thus also applies to non‑dimensional articles after their source adjustments, because the enforcement runs once per article at the end of the loop).*

---

**Edge Cases**

**1. Thin‑day auto‑inflation of low‑scoring items** – *Edge case / Hardcoded limit* – **Latent**  
The pipeline automatically inflates any article with `score < local_thin_day_floor` (default 80) to that floor and sets `category='local'`. This can mask genuinely poor content and is better exposed as a configurable threshold rather than an implicit “auto‑inflate” behaviour.

**2. Local source vs high‑volume prescore gate** – *Conflict resolution* – **Latent**  
When a source is both a local source (contains a local signal) and listed in the high‑volume prescore gate, the current logic gives local articles priority (zero‑hit pass‑through). This is intentional and no functional conflict is observed; local content wins as designed.
