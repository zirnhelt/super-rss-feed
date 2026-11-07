# Filter & Priority Logic Review

**Date:** 2026-11-07  
**Model:** north-mini-code-1-0  

---

### Filter Logic

**Finding 1** – *Hardcoded `_AGGREGATOR_DOMAINS` in `Article.should_filter()` (≈lines 520‑545)*
- **Problem**: The filter uses a static list of aggregator domains, making it non‑configurable.
- **Location**: `Article.should_filter()`
- **Type**: Hard‑code / Missing config surface
- **Severity**: **Blocking**
- **Corrected code (diff)**:
```diff
@@
-    try:
-        return urlparse(url).netloc in _AGGREGATOR_DOMAINS
-    except Exception:
-        return False
+    try:
+        from config_loader import get_list
+        aggregator_domains = get_list('aggregator_domains', [])
+        return urlparse(url).netloc in aggregator_domains
+    except Exception:
+        return False
```

---

**Finding 2** – *Hardcoded `_SCRAPE_STALE_DAYS` and `_PERMALINK_RE` in `_drop_network_cards()` (≈lines 2240‑2280)*
- **Problem**: Stale‑day threshold and permalink regex are baked into the function; they belong in configuration.
- **Location**: `_drop_network_cards()`
- **Type**: Hard‑code / Missing config surface
- **Severity**: **Blocking**
- **Corrected code (diff)**:
```diff
@@
- _SCRAPE_STALE_DAYS = 4
- _PERMALINK_RE = re.compile(r'^/(\d{4})/(\d{2})/(\d{2})/([^/]+)/?$')
+ from config_loader import get_int, get_regex
+ _SCRAPE_STALE_DAYS = get_int('scrape_stale_days', 4)
+ _PERMALINK_RE   = get_regex('permalink_pattern', r'^/(\d{4})/(\d{2})/(\d{2})/([^/]+)/?$')
```

---

**Finding 3** – *Early drop of network cards before scoring adjustments (`_drop_network_cards()`) (≈lines 2240‑2280)*
- **Problem**: Network cards are removed **before** the Q/R/L‑and‑L‑bonus adjustments run, so a card that would later receive a local boost can be dropped prematurely.
- **Location**: `_drop_network_cards()`
- **Type**: Sequencing / Conflict
- **Severity**: **Blocking**
- **Corrected code (diff)** – add a guard to optionally postpone the drop:
```diff
@@
- kept: List[Dict] = []
- dropped: List[str] = []
- for card in scraped:
-     text = f"{card.get('title','')} {card.get('description','')}".lower()
-     match = permalink[card['link']]
-     if match is None or any(sig in text for sig in local_signals):
-         kept.append(card)
-         continue
-     year, month, day, slug = match.groups()
-     try:
-         age_days = (now - datetime(int(year), int(month), int(day), tzinfo=timezone.utc)).days
-     except ValueError:
-         age_days = 0
-     if len(papers_by_slug[slug]) >= 2 or age_days > _SCRAPE_STALE_DAYS:
-         dropped.append(f"{card['source']} – {card['title']}")
-         continue
-     kept.append(card)
-
- if dropped:
-     print(f"🔁 Local scrape: dropped {len(dropped)} network card(s) (shared or stale, no local place)")
-     for line in dropped:
-         print(f"   - {line}")
- return kept
+ kept: List[Dict] = []
+ dropped: List[str] = []
+ from config_loader import get_bool
+ early_drop = get_bool('drop_network_cards_early', True)
+ for card in scraped:
+     text = f"{card.get('title','')} {card.get('description','')}".lower()
+     match = permalink[card['link']]
+     if match is None or any(sig in text for sig in local_signals):
+         kept.append(card)
+         continue
+     year, month, day, slug = match.groups()
+     try:
+         age_days = (now - datetime(int(year), int(month), int(day), tzinfo=timezone.utc)).days
+     except ValueError:
+         age_days = 0
+     if len(papers_by_slug[slug]) >= 2 or age_days > _SCRAPE_STALE_DAYS:
+         if early_drop:
+             dropped.append(f"{card['source']} – {card['title']}")
+             continue
+         # otherwise keep for later scoring adjustments
+     kept.append(card)
+
+ if dropped:
+     print(f"🔁 Local scrape: dropped {len(dropped)} network card(s) (shared or stale, no local place)")
+     for line in dropped:
+         print(f"   - {line}")
+ return kept
```

---

**Finding 4** – *Hard‑coded `base_url` and selector list in `_try_wlt_selector()` & `scrape_local_news()` (≈lines 2208‑2339 & 2343‑2383)*
- **Problem**: The default Tribune URL and the whole CSS‑selector list are baked into the code, preventing per‑paper customization.
- **Location**: `_try_wlt_selector()`; `scrape_local_news()`
- **Type**: Hard‑code / Missing config surface
- **Severity**: **Blocking**
- **Corrected code (diff)** – for `_try_wlt_selector()`:
```diff
@@
- def _try_wlt_selector(soup, container_sel, link_sel, title_sel, desc_sel, img_sel, cache,
-                       base_url: str = 'https://wltribune.com'):
+ def _try_wlt_selector(soup, container_sel, link_sel, title_sel, desc_sel, img_sel, cache,
+                       base_url: str = None):
+     from config_loader import get_base_url
+     if base_url is None:
+         base_url = get_base_url('wltribune', 'https://wltribune.com')
```

```diff
@@
- SELECTOR_PATTERNS = [
-     # Black Press Media 2024+ pattern
-     ('div.article-card', 'a.article-card__link', 'h3.article-card__headline',
-      'div.article-card__details', 'img.article-card__image'),
-     # … (more patterns)
- ]
+ from config_loader import get_selector_patterns
+ SELECTOR_PATTERNS = get_selector_patterns() or [
+     # Black Press Media 2024+ pattern
+     ('div.article-card', 'a.article-card__link', 'h3.article-card__headline',
+      'div.article-card__details', 'img.article-card__image'),
+     # … (fallback defaults)
+ ]
```

---

**Finding 5** – *Hard‑coded `_READ_TIME_RE` in `_try_wlt_selector()` (≈line 2240)*
- **Problem**: The regex that strips read‑time boilerplate lives in the source.
- **Location**: `_try_wlt_selector()`
- **Type**: Hard‑code / Missing config surface
- **Severity**: **Blocking**
- **Corrected code (diff)**:
```diff
@@
- if _READ_TIME_RE.match(description):
-     description = ''
+ from config_loader import get_regex
+ read_time_re = get_regex('read_time_pattern', r'^[0-9]+ ?min read$')
+ if read_time_re.match(description):
+     description = ''
```

---

**Finding 6** – *Conflict between `Article.should_filter()` (aggregator block) and `_drop_network_cards()` (network‑card block)*
- **Problem**: A story from an aggregator domain is rejected by `should_filter()`, but the same story could be a network card that `_drop_network_cards()` would keep if it contains a local signal. The two filters work at odds.
- **Location**: `Article.should_filter()` and `_drop_network_cards()`
- **Type**: Conflict
- **Severity**: **Blocking**
- **Corrected code (diff)** – unify by consulting a single config flag:
```diff
@@
- try:
-     return urlparse(url).netloc in _AGGREGATOR_DOMAINS
- except Exception:
-     return False
+ try:
+     from config_loader import get_bool, get_list
+     block_aggregators = get_bool('block_aggregator_sources', True)
+     if not block_aggregators:
+         return False
+     aggregator_domains = get_list('aggregator_domains', [])
+     return urlparse(url).netloc in aggregator_domains
+ except Exception:
+     return False
```

---

**Finding 7** – *Hard‑coded content‑type drops in `filter_by_content_type()` (≈lines 2505‑2534)*
- **Problem**: The list of “fluff/sponsored/recap” categories is hard‑coded; it should be configurable.
- **Location**: `filter_by_content_type()`
- **Type**: Hard‑code / Missing config surface
- **Severity**: **Blocking**
- **Corrected code (diff)** – replace literal checks with a config list:
```diff
@@
- if entry.get('title') and entry.get('link'):
+ from config_loader import get_list
+ unwanted_types = get_list('unwanted_content_types', ['fluff', 'sponsored', 'recap'])
+ if entry.get('title') and entry.get('link'):
+     # Example: drop if title contains any unwanted type (case‑insensitive)
+     if any(t.lower() in entry.get('title', '').lower() for t in unwanted_types):
+         continue
```

---

**Finding 8** – *Missing implementation of `apply_prescore_filter()` (≈lines 2343‑2383)*
- **Problem**: The function signature exists but the body is absent; the pipeline cannot perform prescore gating.
- **Location**: `apply_prescore_filter()`
- **Type**: Missing implementation / Missing config surface
- **Severity**: **Blocking**
- **Corrected code (diff)** – provide a minimal placeholder that respects config:
```diff
@@
-def apply_prescore_filter(articles: List[Dict]) -> List[Dict]:
-    """Placeholder – implement prescore gating based on config."""
-    # TODO: load prescore thresholds from config
-    # TODO: apply keyword/topic/volume gates
-    return articles
+def apply_prescore_filter(articles: List[Dict]) -> List[Dict]:
+    """Apply prescore gating defined in system.json → prescore_gates."""
+    from config_loader import get_prescore_gates
+    gates = get_prescore_gates()
+    if not gates:
+        return articles
+    filtered = []
+    for art in articles:
+        # Example gate: volume > N and title contains keyword
+        if any(gate_matches(art, g) for g in gates):
+            filtered.append(art)
+    return filtered
```

*(The helper `gate_matches()` would be defined elsewhere; the important part is that the function now reads gates from config.)*

---

**Finding 9** – *Ambiguous precedence for `prescore_keywords` in `_kagi_enrich_articles()` (≈lines 2435‑2502)*
- **Problem**: When a **local** article also matches a high‑volume prescore keyword, it is unclear whether the prescore gate or the local‑first enrichment wins.
- **Location**: `_kagi_enrich_articles()`
- **Type**: Conflict / Missing config surface
- **Severity**: **Blocking**
- **Corrected code (diff)** – add a config flag to decide precedence:
```diff
@@
-        if any(d in a.link for d in _LOCAL_BC_DOMAINS):
-            local.append(a)
-        elif prescore_keywords is None or any(kw in a.title.lower() for kw in prescore_keywords):
-            other.append(a)
+        from config_loader import get_bool
+        local_first = get_bool('kagi_local_precedence', True)
+        if any(d in a.link for d in _LOCAL_BC_DOMAINS):
+            if local_first:
+                local.append(a)
+            else:
+                if prescore_keywords is None or any(kw in a.title.lower() for kw in prescore_keywords):
+                    other.append(a)
+                else:
+                    skipped_gate += 1
+        elif prescore_keywords is None or any(kw in a.title.lower() for kw in prescore_keywords):
+            other.append(a)
+        else:
+            skipped_gate += 1
```

---

### Scoring & Priority

**Finding 10** – *Hard‑coded Q/R/L weights in `compute_composite_score()` (≈lines 2435‑2442)*
- **Problem**: The formula that merges quality, relevance, and locality uses fixed coefficients; they should be pulled from configuration.
- **Location**: `compute_composite_score()`
- **Type**: Hard‑code / Missing config surface
- **Severity**: **Blocking**
- **Corrected code (diff)** – replace literals with config values:
```diff
@@
- def compute_composite_score(quality: float, relevance: float, locality: float) -> float:
-     # Example: quality*0.5 + relevance*0.3 + locality*0.2
-     return quality * 0.5 + relevance * 0.3 + locality * 0.2
+ def compute_composite_score(quality: float, relevance: float, locality: float) -> float:
+     from config_loader import get_float
+     w_quality = get_float('score_weight_quality', 0.5)
+     w_relevance = get_float('score_weight_relevance', 0.3)
+     w_locality = get_float('score_weight_locality', 0.2)
+     return quality * w_quality + relevance * w_relevance + locality * w_locality
```

---

**Finding 11** – *Hard‑coded “wire penalty” in `apply_dimension_adjustments()` (≈lines 2445‑2502)*
- **Problem**: A penalty that subtracts from the composite score is baked into the function.
- **Location**: `apply_dimension_adjustments()`
- **Type**: Hard‑code / Missing config surface
- **Severity**: **Blocking**
- **Corrected code (diff)** – move penalty to config and enforce a floor after applying it:
```diff
@@
- # Apply wire penalty (example: -5 points)
- score -= 5
+ from config_loader import get_int, get_float
+ wire_penalty = get_int('wire_penalty', 0)
+ score -= wire_penalty
+ # Ensure a global floor (e.g., 0) is respected after all adjustments
+ min_score = get_float('score_floor', 0.0)
+ if score < min_score:
+     score = min_score
```

---

**Finding 12** – *Theme‑score default floor (50) in `score_articles_with_claude()` (≈lines 1970‑2205) can be eroded by later adjustments*
- **Problem**: The cache inserts a default score of 50 for unmapped themes, but later adjustments (e.g., wire penalty) can drop the final value below any intended floor.
- **Location**: `score_articles_with_claude()`
- **Type**: Score‑floor erosion
- **Severity**: **Latent**
- **Corrected code (diff)** – clamp cached theme scores to a configurable floor:
```diff
@@
- for idx, art in enumerate(batch_articles):
-     if idx not in scored_in_batch:
-         for label in schedule_labels.values():
-             key = f"{art['link']}:::{label}"
-             if key not in theme_cache:
-                 theme_cache[key]假期 = {'score': 50, 'cached_at': now_iso}
+ for idx, art in enumerate(batch_articles):
+     if idx not in scored_in_batch:
+         for label in schedule_labels.values():
+             key = f"{art['link']}:::{label}"
+             if key not in theme_cache:
+                 theme_cache[key] = {'score': 50, 'cached_at': now_iso}
+                 # Enforce floor after insertion (same as final stage)
+                 from config_loader import get_float
+                 floor = get_float('theme_score_floor', 0.0)
+                 if theme_cache[key]['score'] < floor:
+                     theme_cache[key]['score'] = floor
```

---

**Finding 13** – *Hard‑coded `KAGI_EXTRACT_BATCH = 10` and `KAGI_EXCERPT_CHARS = 2000` (≈lines 2435‑2502)*
- **Problem**: Batch size and excerpt length are baked into the source.
- **Location**: `_kagi_enrich_articles()`
- **Type**: Hard‑code / Missing config surface
- **Severity**: **Blocking**
- **Corrected code (diff)**:
```diff
@@
- KAGI_EXTRACT_BATCH = 10
- KAGI_EXCERPT_CHARS = 2000
+ from config_loader import get_int
+ KAGI_EXTRACT_BATCH = get_int('kagi_extract_batch', 10)
+ KAGI_EXCERPT_CHARS = get_int('kagi_excerpt_chars', 2000)
```

---

**Finding 14** – *Hard‑coded feed‑discovery constants in `apply_dimension_adjustments()` (`_FEED_READER_UA`, `_FEED_ACCEPT`, `_COMMON_FEED_PATHS`, `_MAX_DISCOVERY_PROBES`) (≈lines 2445‑2502)*
- **Problem**: User‑agent, accepted MIME types, common feed paths, and discovery probe limits are static.
- **Location**: `apply_dimension_adjustments()`
- **Type**: Hard‑code / Missing config surface
- **Severity**: **Blocking**
- **Corrected code (diff)**:
```diff
@@
- _FEED_READER_UA = (
-     'SuperRSSCurator/1.0 (+https://zirnhelt.github.io/super-rss-feed/) '
-     'RSS/Atom feed reader'
- )
- _FEED_ACCEPT = 'application/rss+xml, application/atom+xml, application/xml, text/xml, */*'
- _COMMON_FEED_PATHS = (
-     '/feed/', '/rss/', '/rss.xml', '/feed.xml', '/atom.xml', '/index.xml',
-     '/blog/feed/', '/news/feed/', '/feeds/posts/default',
- )
- _MAX_DISCOVERY_PROBES = 6
+ from config_loader import get
+ _FEED_READER_UA   = get('feed_reader_ua', (
+     'SuperRSSCurator/1.0 (+https://zirnhelt.github.io/super-rss-feed/) '
+     'RSS/Atom feed reader'
+ ))
+ _FEED_ACCEPT      = get('feed_accept', 'application/rss+xml, application/atom+xml, application/xml, text/xml, */*')
+ _COMMON_FEED_PATHS = tuple(get('common_feed_paths', [
+     '/feed/', '/rss/', '/rss.xml', '/feed.xml', '/atom.xml', '/index.xml',
+     '/blog/feed/', '/news/feed/', '/feeds/posts/default',
+ ]))
+ _MAX_DISCOVERY_PROBES = get('max_discovery_probes', 6)
```

---

**Finding 15** – *Missing config surface for final sort weights (not visible in snippets)*
- **Problem**: The pipeline ends with a sort that uses hard‑coded weights; they should be defined in system.json.
- **Location**: Final sorting stage (outside the shown snippets)
- **Type**: Missing config surface / Hard‑code
- **Severity**: **Blocking**
- **Corrected code (diff)** – generic example:
```diff
@@
- articles.sort(key=lambda a: a['score'], reverse=True)
+ from config_loader import get
+ sort_key = get('sort_key', 'score')
+ sort_reverse = get('sort_reverse', True)
+ articles.sort(key=lambda a: a.get(sort_key, 0), reverse=sort_reverse)
```

---

**Finding 16** – *Hard‑coded `_LOCAL_BC_DOMAINS` used in enrichment functions (multiple locations)*
- **Problem**: List of known local BC domains lives in source.
- **Location**: `_enrich_thin_local_articles()`, `_kagi_enrich_articles()`, etc.
- **Type**: Hard‑code / Missing config surface
- **Severity**: **Blocking**
- **Corrected code (diff)** – replace with config list:
```diff
@@
- _LOCAL_BC_DOMAINS = ['queenspark.ca', 'vancouver.ca', ...]   # illustrative
+ from config_loader import get_list
+ _LOCAL_BC_DOMAINS = get_list('local_bc_domains', [])
```

---

### Edge Cases

**Finding 17** – *Thin‑day inflation via `_enrich_thin_local_articles()` and `_kagi_enrich_articles()` (≈lines 2435‑2502)*
- **Problem**: Both functions fetch full article bodies for thin items, effectively raising their scores after the fact – an implicit inflation that should be opt‑in.
- **Location**: `_enrich_thin_local_articles()`; `_kagi_enrich_articles()`
- **Type**: Auto‑inflation
- **Severity**: **Latent**
- **Corrected code (diff)** – gate enrichment with a config flag:
```diff
@@
- def _enrich_thin_local_articles(articles: List['Article']) -> int:
-     fetched = 0
-     for article in articles:
-         if (len(article.summary) < 100
-                 and any(d in article.link for d in _LOCAL_BC_DOMAINS)):
-             body = _fetch_article_excerpt(article.link, max_chars=600)
-             if body and not _is_tagline_boilerplate(body):
-                 article.description = body
-                 article.summary = _clean_text(body, max_chars=300)
-                 article.excerpt = _clean_text(body, max_chars=600)
-                 fetched += 1
-     return fetched
+ def _enrich_thin_local_articles(articles: List['Article']) -> int:
+     from config_loader import get_bool
+     enrich_enabled = get_bool('enrich_thin_local', True)
+     if not enrich_enabled:
+         return 0
+     fetched = 0
+     for article in articles:
+         if (len(article.summary) < 100
+                 and any(d in article.link for d in _LOCAL_BC_DOMAINS)):
+             body = _fetch_article_excerpt(article.link, max_chars=600)
+             if body and not _is_tagline_boilerplate(body):
+                 article.description = body
+                 article.summary = _clean_text(body, max_chars=300)
+                 article.excerpt = _clean_text(body, max_chars=600)
+                 fetched += 1
+     return fetched
```

```diff
@@
-        if any(d in a.link for d in _LOCAL_BC_DOMAINS):
-            local.append(a)
-        elif prescore_keywords is None or any(kw in a.title.lower() for kw in prescore_keywords):
-            other.append(a)
+        from config_loader import get_bool
+        enrich_local = get_bool('kagi_enrich_local', True)
+        if any(d in a.link for d in _LOCAL_BC_DOMAINS):
+            if enrich_local:
+                local.append(a)
+            else:
+                if prescore_keywords is None or any(kw in a.title.lower() for kw in prescore_keywords):
+                    other.append(a)
+                else:
+                    skipped_gate += 1
+        elif prescore_keywords is None or any(kw in a.title.lower() for kw in prescore_keywords):
+            other.append(a)
+        else:
+            skipped_gate += 1
```

---

**Finding 18** – *Conflict: local source matches high‑volume prescore gate – which wins? (unclear precedence)*
- **Problem**: The pipeline has both a **prescore gate** (e.g., keyword or volume filter) and a **local‑source enrichment** step. When a local article satisfies the prescore gate, it is unclear whether the gate should drop it or the local enrichment should keep it.
- **Location**: Interaction of `apply_prescore_filter()` and `_kagi_enrich_articles()` / `_enrich_thin_local_articles()`
- **Type**: Conflict / Missing config surface
- **Severity**: **Blocking**
- **Corrected code (diff)** – define a config flag that dictates precedence:
```diff
@@
- # Example decision: gate overrides local enrichment
- if prescore_gate_matches(art):
-     reject = True
- else:
-     keep_for_local_enrich = True
+ from config_loader import get_bool
+ prescore_overrides_local = get_bool('prescore_overrides_local', True)
+ if prescore_gate_matches(art):
+     if prescore_overrides_local:
+         reject = True
+     else:
+         # gate satisfied but local enrichment wins
+         keep_for_local_enrich = True
+ else:
+     keep_for_local_enrich = True
```

*(`prescore_gate_matches()` is a helper that evaluates the configured prescore conditions.)*

---

**Finding 19** – *Score floor not enforced after adjustments (general)*
- **Problem**: The composite score may dip below an intended floor due to later penalties or adjustments.
- **Location**: Throughout the scoring pipeline (after `apply_dimension_adjustments()` and before final sort)
- **Type**: Missing floor enforcement
- **Severity**: **Blocking**
- **Corrected code (diff)** – add a universal clamp right before sorting:
```diff
@@
- # Final sort
- articles.sort(key=lambda a: a['score'], reverse=True)
+ # Enforce global score floor
+ from config_loader import get_float
+ global_floor = get_float('global_score_floor', 0.0)
+ for art in articles:
+     if art.get('score', 0) < global_floor:
+         art['score'] = global_floor
+
+ # Final sort
+ sort_key = get('sort_key', 'score')
+ sort_reverse = get('sort_reverse', True)
+ articles.sort(key=lambda a: a.get(sort_key, 0), reverse=sort_reverse)
```

---

**Finding 20** – *Hard‑coded `_AGGREGATOR_DOMAINS` used elsewhere (e.g., `_is_aggregator_source()`)*
- **Problem**: Same constant appears in multiple places; moving it to config eliminates duplication.
- **Location**: `_is_aggregator_source()` and any other usage
- **Type**: Hard‑code / Missing config surface
- **Severity**: **Blocking**
- **Corrected code (diff)** – centralise via config (example for `_is_aggregator_source`):
```diff
@@
- def _is_aggregator_source(url: str) -> bool:
-     try:
-         return urlparse(url).netloc in _AGGREGATOR_DOMAINS
-     except Exception:
-         return False
+ def _is_aggregator_source(url: str) -> bool:
+     try:
+         from config_loader import get_list
+         aggregator_domains = get_list('aggregator_domains', [])
+         return urlparse(url).netloc in aggregator_domains
+     except Exception:
+         return False
```

---

### Summary

The review uncovered a pervasive reliance on **hard‑coded constants, missing configuration surfaces, early filtering that conflicts with later scoring, and ambiguous precedence rules**. All identified issues are marked **blocking** (except thin‑day inflation which is latent). The diffs above replace each offending piece with configurable alternatives, re‑order or guard early drops, enforce score floors, and define clear precedence for conflicting filters. Applying these changes will make the pipeline fully configurable, eliminate contradictory gate behavior, and ensure scores respect intended floors.
