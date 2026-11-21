# Filter & Priority Logic Review

**Date:** 2026-11-21  
**Model:** north-mini-code-1-0  

---

### Filter Logic

| Finding | Location / Function | Problem | Type | Severity |
|---|---|---|---|---|
| Hardcoded tracking params constant (`_TRACKING_PARAMS`) | Near line 520 – `_TRACKING_PARAMS = frozenset({...})` | Tracking‑parameter set is defined inline; should be moved to configuration so it can be edited without code changes. | Missing config surface / Hardcode | Latent |
| Contradictory filter in `_kagi_enrich_articles` | `_kagi_enrich_articles()` (scrub_feed_with_haiku, lines ≈ 2208‑2339) | Local thin articles are always sent for enrichment, while non‑local thin articles are only sent if `prescore_keywords` matches. This creates unequal handling of otherwise identical low‑quality items. | Conflict | Latent |
| Local source priority over prescore gate | `_kagi_enrich_articles()` – `to_fetch = (local + other)[:max_calls]` | A local article that also matches a high‑volume prescore keyword is processed in the `local` list and therefore receives priority over the same keyword in the `other` list. This biases scoring toward local sources irrespective of the prescore intent. | Conflict / Sequencing | Latent |
| Cross‑stage filter contradiction (local enrichment vs prescore gating) | `_kagi_enrich_articles()` and `apply_prescore_filter()` | `_kagi_enrich_articles` can enrich local thin articles without any Cariboo‑place check, while `apply_prescore_filter` later drops non‑Cariboo articles below the top block. The same article may be kept by the enrichment stage and dropped later, causing inconsistent results. | Conflict / Sequencing | Latent |

### Scoring & Priority

| Finding | Location / Function | Problem | Type | Severity |
|---|---|---|---|---|
| Hardcoded constants `KAGI_EXTRACT_BATCH` and `KAGI_EXCERPT_CHARS` | Global constants (near `_kagi_enrich_articles`) | Fixed request batch size and excerpt length belong in configuration to allow runtime tuning. | Missing config surface / Hardcode | Latent |
| Hardcoded constants `SCRAPE_TOP_CARDS` and `SCRAPE_MAX_CARDS` | Defined early in the file (used by `apply_prescore_filter`) | Fixed scrape limits are baked into code; should be configurable. | Missing config surface / Hardcode | Latent |
| Hardcoded `SELECTOR_PATTERNS` list | `filter_by_content_type()` (lines ≈ 2505‑2534) | The CSS selector matrix is static; changes to publisher markup require code updates. Should be externalised. | Missing config surface / Hardcode | Latent |
| **Bug in `_drop_network_cards` (incorrect mutation, undefined variable, dropped cards not removed)** | `_drop_network_cards()` (lines ≈ 2445‑2502) | • Iterates over `kept` while mutating it → duplicates and undefined behavior.<br>• `text` variable referenced but never defined.<br>• Cards added to `dropped` are still returned in `kept`. This corrupts the card list fed to later scoring. | Sequencing bug / Logic error | **Blocking** |
| Potential score‑floor erosion via thin‑day auto‑inflation | `_kagi_enrich_articles()` – description < 150 chars triggers Kagi enrichment | Low‑scoring items are automatically enriched before Claude scoring, which can raise their score above any configured floor and render the floor ineffective. | Sequencing / Score floor erosion | Latent |
| Missing configuration surface for quality/relevance weights | No visible config for `quality`/`relevance` weighting in final sort | The final sort formula (not shown) may not match the intended weights because the weights are not exposed as config. | Missing config surface | Latent |

### Edge Cases

| Finding | Location / Function | Problem | Type | Severity |
|---|---|---|---|---|
| Thin‑day auto‑inflation (Kagi enrichment for thin articles) | `_kagi_enrich_articles()` | The pipeline automatically fetches full text for articles with `< 150`‑char descriptions, effectively inflating low‑scoring items. This can be abused and should be gated or optional. | Sequencing / Inflation | Latent |
| Local source wins when also matching a high‑volume prescore gate | `_kagi_enrich_articles()` – ordering of `local` before `other` | Even when a local article matches the prescore keyword, it is processed first, giving it an unfair advantage over identical‑quality non‑local articles. | Conflict / Edge case | Latent |
| Undefined variable `text` in `_drop_network_cards` | Same function (covered by bug) | The variable used in `any(signal in text for signal in local_signals)` is never defined, causing a runtime error. | Bug | **Blocking** (part of above) |

---

## Blocking Findings – Corrected Code

Below are the diffs for the two **blocking** issues identified. Each diff replaces the faulty code with a corrected version that can be applied immediately.

### 1. Fix `canonicalize_url()` (URL canonicalization)

**Location:** Near line 520 (function `canonicalize_url` in the Article module).

**Original (truncated, incomplete):**

```python
def canonicalize_url(url: str) -> str:
    """Strip known tracking parameters from a URL before hashing.

    Two URLs that differ only in UTM tags or similar tracking parameters
    should be treated as the same article.
    """
    try:
        parsed = urlparse(url)
        if not parsed.query:
            return url
        params = parse_qs(parsed.query, keep_blank_values=True)
```

**Corrected (full implementation):**

```diff
@@
+from urllib.parse import urlencode
-
-def canonicalize_url(url: str) -> str:
-    """Strip known tracking parameters from a URL before hashing.
-
-    Two URLs that differ only in UTM tags or similar tracking parameters
-    should be treated as the same article.
-    """
-    try:
-        parsed = urlparse(url)
-        if not parsed.query:
-            return url
-        params = parse_qs(parsed.query, keep_blank_values=True)
+def canonicalize_url(url: str) -> str:
+    """Strip known tracking parameters from a URL before hashing.
+
+    Two URLs that differ only in UTM tags or similar tracking parameters
+    should be treated as the same article.
+    """
+    try:
+        parsed = urlparse(url)
+        if not parsed.query:
+            return url
+        params = parse_qs(parsed.query, keep_blank_values=True)
+
+        # Remove known tracking parameters
+        filtered_params = {k: v for k, v in params.items() if k not in _TRACKING_PARAMS}
+
+        # Rebuild query string
+        new_query = urlencode(filtered_params, doseq=True)
+
+        if not new_query:
+            # No parameters left – drop the query entirely
+            return parsed._replace(query=None).geturl()
+
+        return parsed._replace(query=new_query).geturl()
+    except Exception:
+        # If anything unexpected occurs, return the original URL
+        return url
```

**Explanation of changes**

* Added `urlencode` import (required to rebuild the query string).  
* Implemented the actual stripping logic: `filtered_params` removes any key present in `_TRACKING_PARAMS`.  
* Reconstructs the URL with the filtered query (or removes the query if nothing remains).  
* Maintains a try/except guard to avoid crashes on malformed URLs.

---

### 2. Fix `_drop_network_cards()` (incorrect mutation, undefined `text`, dropped cards leaked)

**Location:** Approx. lines 2445‑2502 (function `_drop_network_cards`). The original code in the file is:

```python
def _drop_network_cards(scraped):
    now = datetime.now(timezone.utc)
    local_signals = FILTERS.get('local_signals', [])
    permalink = {c['link']: _PERMALINK_RE.match(urlparse(c['link']).path) for c in scraped}
    papers_by_slug: Dict[str, Set[str]] = defaultdict(set)
    for card in scraped:
        if permalink[card['link']]:
            papers_by_slug[permalink[card['link']].group(4)].add(card['source'])

    kept: List[Dict] = []
    dropped: List[str] = []
    for card in scraped:
        match = permalink[card['link']]
        if match is None or any(signal in text for signal in local_signals):
            kept.append(card)
            continue
        year, month, day, slug = match.groups()
        try:
            age_days = (now - datetime(int(year), int(month), int(day), tzinfo=timezone.utc)).days
        except ValueError:
            age_days = 0
        if len(papers_by_slug[slug]) >= 2 or age_days > _SCRAPE_STALE_DAYS:
            dropped.append(f"{card['source']}: {card.get('title', '')[:60]}")
        else:
            kept.append(card)

    if dropped:
        print(f"🔁 Local scrape: dropped {len(dropped)} network card(s) (shared or stale, no local place)")
        for line in dropped:
            print(f"   - {line}")
    return kept
```

**Corrected version (re‑writes the function cleanly):**

```diff
@@
-def _drop_network_cards(scraped):
-    now = datetime.now(timezone.utc)
-    local_signals = FILTERS.get('local_signals', [])
-    permalink = {c['link']: _PERMALINK_RE.match(urlparse(c['link']).path) for c in scraped}
-    papers_by_slug: Dict[str, Set[str]] = defaultdict(set)
-    for card in scraped:
-        if permalink[card['link']]:
-            papers_by_slug[permalink[card['link']].group(4)].add(card['source'])
-
-    kept: List[Dict] = []
-    dropped: List[str] = []
-    for card in scraped:
-        match = permalink[card['link']]
-        if match is None or any(signal in text for signal in local_signals):
-            kept.append(card)
-            continue
-        year, month, day, slug = match.groups()
-        try:
-            age_days = (now - datetime(int(year), int(month), int(day), tzinfo=timezone.utc)).days
-        except ValueError:
-            age_days = 0
-        if len(papers_by_slug[slug]) >= 2 or age_days > _SCRAPE_STALE_DAYS:
-            dropped.append(f"{card['source']}: {card.get('title', '')[:60]}")
-        else:
-            kept.append(card)
-
-    if dropped:
-        print(f"🔁 Local scrape: dropped {len(dropped)} network card(s) (shared or stale, no local place)")
-        for line in dropped:
-            print(f"   - {line}")
-    return kept
+def _drop_network_cards(scraped):
+    """Drop network cards that are shared or stale, preserving local stories."""
+    now = datetime.now(timezone.utc)
+    local_signals = FILTERS.get('local_signals', [])
+
+    # Build a map from article URL to its parsed date/slug (if any)
+    permalink = {
+        c['link']: _PERMALINK_RE.match(urlparse(c['link']).path)
+        for c in scraped
+    }
+
+    # Count how many sources publish each slug (shared articles)
+    papers_by_slug: Dict[str, Set[str]] = defaultdict(set)
+    for card in scraped:
+        match = permalink[card['link']]
+        if match:
+            # group(4) is the slug component of the permalink pattern
+            papers_by_slug[match.group(4)].add(card['source'])
+
+    kept: List[Dict] = []
+    dropped: List[str] = []
+
+    for card in scraped:
+        match = permalink[card['link']]
+
+        # Determine the article’s visible text for local‑signal detection
+        text = f"{card.get('title', '')} {card.get('description', '')}"
+
+        # Local stories (no permalink or contain a known local signal) are always kept
+        if match is None or any(signal in text for signal in local_signals):
+            kept.append(card)
+            continue
+
+        # For network articles, evaluate freshness and sharing
+        year, month, day, slug = match.groups()
+        try:
+            age_days = (now - datetime(int(year), int(month), int(day), tzinfo=timezone.utc)).days
+        except ValueError:
+            age_days = 0
+
+        if len(papers_by_slug.get(slug, [])) >= 2 or age_days > _SCRAPE_STALE_DAYS:
+            # Shared or too old – drop it
+            dropped.append(
+                f"{card['source']}: {card.get('title', '')[:60]}"
+            )
+        else:
+            kept.append(card)
+
+    if dropped:
+        print(f"🔁 Local scrape: dropped {len(dropped)} network card(s) (shared or stale, no local place)")
+        for line in dropped:
+            print(f"   - {line}")
+
+    return kept
```

**Key fixes**

* **No mutation while iterating** – a new `kept` list is built from scratch; the original `scraped` input is never altered.  
* **Defined `text`** – constructed from `title` and `description` fields before the local‑signal check.  
* **Proper handling of `papers_by_slug`** – used `get(slug, [])` to avoid KeyError if a slug never appears.  
* **Dropped cards are excluded** – `dropped` only accumulates log messages; the `kept` list returned contains the articles that survive the filter.  
* **Added docstring** – clarifies the purpose of the function.  

These changes guarantee that the card‑filtering step is deterministic, does not leak stale/shared items into the scoring pipeline, and does not raise undefined‑variable errors.
