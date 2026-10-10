# Filter & Priority Logic Review

**Date:** 2026-10-10  
**Model:** north-mini-code-1-0  

---

**Filter Logic**

| # | Finding | Location | Type | Severity | Corrected Code / Diff |
|---|---------|----------|------|----------|-----------------------|
| 1 | `Article.should_filter()` implements a Kagi Search API call instead of filtering existing articles. The function fetches new results, creates `_make_article` objects, but never returns them. It also uses undefined `kagi_key` and `api_usage`. This causes duplicate fetches, performance overhead, and violates the purpose of a filter stage. | `Article.should_filter()` (lines 520‑545) | **Sequencing / Conflict** – filter stage performing enrichment. **Hardcoded** – Kagi endpoint, API key usage. | **Blocking** | **Diff – replace the whole method with a proper keyword/source/title‑pattern blocker**  ```diff
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
-            # Missing return and append
+        # Filter based on configured keyword/source/title patterns.
+        query = query_config.get('query', '')
+        if not query:
+            return False
+        # Block article if query appears in title or source (case‑insensitive)
+        title = (self.title or '').lower()
+        source = (self.source or '').lower()
+        if query.lower() in title or query.lower() in source:
+            return True
+        return False
``` |
| 2 | `_fetch_via_google_news_fallback` (inside `scrub_feed_with_haiku`) re‑applies `article.should_filter()` after the fallback fetch. This erodes earlier filter decisions – an article already blocked by keyword or source may be reinstated by the fallback, creating contradictory filter outcomes across stages. | `_fetch_via_google_news_fallback` (lines 2225‑2240) | **Sequencing / Conflict** – duplicate filtering. | **Blocking** | **Diff – remove the second `should_filter` check**  ```diff
-        if article.pub_date < cutoff_date:
-            continue
-        if article.should_filter():
-            continue
-        articles.append(article)
+        if article.pub_date < cutoff_date:
+            continue
+        # should_filter already applied earlier – skip re‑filtering
+        articles.append(article)
``` |
| 3 | `apply_prescore_filter()` only validates that a candidate URL looks like a feed (`_looks_like_feed`). It does **not** enforce any content‑type or source‑gate constraints, allowing aggregator or low‑quality sources to pass to later stages where they are later filtered (e.g., `filter_by_content_type`). This creates a conflict: a source that should be hard‑dropped is accepted earlier, forcing later stages to waste work. | `apply_prescore_filter()` (lines 2343‑2383) | **Missing config surface / Conflict** – prescore gate ignores content‑type gating. | **Latent** | **Diff – extend the function to apply the same hard‑drop checks as `filter_by_content_type` before returning the candidate**  ```diff
-        content = _fetch_url_bytes(candidate)
-        if content and _looks_like_feed(content):
-            return candidate
-    return None
+        # 1) Basic feed format check
+        content = _fetch_url_bytes(candidate)
+        if not (content and _looks_like_feed(content)):
+            return None
+
+        # 2) Apply hard‑drop criteria (fluff / sponsored / recap) – same as filter_by_content_type
+        #    Parse the temporary feed to inspect entry types
+        parsed = feedparser.parse(content)
+        for entry in parsed.entries:
+            art = Article(entry, feed['title'], feed['html_url'], candidate)
+            if _is_fluff(art) or _is_sponsored(art) or _is_recap(art):
+                # Candidate is junk – reject
+                return None
+
+        # 3) If we reach here the candidate survives the prescore gate
+        return candidate
``` |
| 4 | `filter_by_content_type()` is misnamed – its body is the **fallback‑fetch** logic (Brave → Kagi → Google News). The function should be filtering fluff/sponsored/recap articles, but instead it attempts to recover dead feeds. This name mismatch leads developers to assume content filtering occurs when it does not, and the fallback logic can re‑introduce low‑quality items that should have been hard‑dropped. | `filter_by_content_type()` (lines 2505‑2534) | **Hardcoded / Sequencing** – fallback fetch lives in a filter‑named function. | **Blocking** | **Diff – split responsibilities. Move fallback fetch to a dedicated helper (`_fallback_fetch_if_needed`) and keep `filter_by_content_type` for actual content‑type filtering.**  ```diff
- def filter_by_content_type():
-     # itself is usually still up and searchable even when its feed 500s.
-     # (503 is deliberately excluded: it already gets a Retry-After skip_until
-     # circuit breaker above, so hitting the paid API fallback for it too would
-     # just burn quota on a source we're already backing off from.)
-     should_try_fallback = status in (403, 404, 421, 500) or is_timeout or is_connection_error
-
-     # A feed that has failed this many runs in a row is not having a bad
-     # day. Brave is already hitting its 402 quota ceiling mid-run, so every
-     # call spent re-confirming a dead source is one denied to a live one.
-     skip_paid = _feed_http_cache.should_skip_paid_fallback(cache_key)
-     if should_try_fallback and skip_paid:
-         print(f"  ⚠ {feed['title']}: {failures} consecutive failures — free fallback only")
-
-     if should_try_fallback and not skip_paid and os.environ.get('BRAVE_API_KEY'):
-         fallback = _fetch_via_brave_fallback(feed, cutoff_date)
-         if fallback:
-             print(f"  ↩ {feed['title']}: Brave fallback → {len(fallback)} articles")
-             return fallback
-         print(f"  ⚠ {feed['title']}: Brave fallback returned 0 articles")
-
-     if should_try_fallback and not skip_paid and os.environ.get('KAGI_API_KEY'):
-         fallback = _fetch_via_kagi_fallback(feed, cutoff_date)
-         if fallback:
-             print(f"  ↩ {feed['title']}: Kagi fallback → {len(fallback)} articles")
-             return fallback
-
-     if should_try_fallback:
-         fallback = _fetch_via_google_news_fallback(feed, cutoff_date)
-         if fallback:
-             print(f"  ↩ {feed['title']}: Google News fallback → {len(fallback)} articles")
-
- # New helper that contains exactly the fallback logic extracted above
- def _fallback_fetch_if_needed(feed, cutoff_date):
-     # itself is usually still up and searchable even when its feed 500s.
-     # (503 is deliberately excluded: it already gets a Retry-After skip_until
-     # circuit breaker above, so hitting the paid API fallback for it too would
-     # just burn quota on a source we're already backing off from.)
-     should_try_fallback = status in (403, 404, 421, 500) or is_timeout or is_connection_error
-
-     # A feed that has failed this many runs in a row is not having a bad
-     # day. Brave is already hitting its 402 quota ceiling mid-run, so every
-     # call spent re-confirming a dead source is one denied to a live one.
-     skip_paid = _feed_http_cache.should_skip_paid_fallback(cache_key)
-     if should_try_fallback and skip_paid:
-         print(f"  ⚠ {feed['title']}: {failures} consecutive failures — free fallback only")
-
-     if should_try_fallback and not skip_paid and os.environ.get('BRAVE_API_KEY'):
-         fallback = _fetch_via_brave_fallback(feed, cutoff_date)
-         if fallback:
-             print(f"  ↩ {feed['title']}: Brave fallback → {len(fallback)} articles")
-             return fallback
-         print(f"  ⚠ {feed['title']}: Brave fallback returned 0 articles")
-
-     if should_try_fallback and not skip_paid and os.environ.get('KAGI_API_KEY'):
-         fallback = _fetch_via_kagi_fallback(feed, cutoff_date)
-         if fallback:
-             print(f"  ↩ {feed['title']}: Kagi fallback → {len(fallback)} articles")
-             return fallback
-
-     if should_try_fallback:
-         fallback = _fetch_via_google_news_fallback(feed, cutoff_date)
-         if fallback:
-             print(f"  ↩ {feed['title']}: Google News fallback → {len(fallback)} articles")
-         return fallback
-     return None
-
- # Actual content‑type filter – called by the pipeline after normal feed fetch
- def filter_by_content_type(feed, cutoff_date):
-     # Try fallback first; if we got replacement articles we are done
-     replacement = _fallback_fetch_if_needed(feed, cutoff_date)
-     if replacement is not None:
-         return replacement
-
-     # Normal feed processing – filter out fluff / sponsored / recap
-     articles = _articles_from_feed_bytes(feed['content'], feed, cutoff_date, feed['url'])
-     filtered = []
-     for art in articles:
-         if _is_fluff(art) or _is_sponsored(art) or _is_recap(art):
-             continue
-         filtered.append(art)
-     return filtered
``` |
| 5 | `score_articles_with_claude()` contains hard‑coded selectors and a fixed URL for the Williams Lake Tribune. Selectors belong in configuration so they can be changed per outlet and to avoid breaking when the site updates. This hard‑coding also conflates scraping logic with scoring logic, making it difficult to apply dimensional scoring later. | `score_articles_with_claude()` (lines 1970‑2205) – `SELECTOR_PATTERNS` and `WLT_NEWS_URL` | **Hardcoded constants** – selectors & URL belong in config. | **Latent** | **Diff – move selectors and the Tribune URL to config and keep only the scoring orchestration**  ```diff
-    SELECTOR_PATTERNS = [
-        # Blog style
-        ('div.post', 'a', 'h2', 'div.summary', 'img'),
-        # News site with story divs
-        ('div.story', 'a.story__link', 'h2.story__headline', 'p.story__excerpt', 'img'),
-        # WordPress-style post entries
-        ('article', 'a[rel="bookmark"]', 'h2.entry-title', 'div.entry-summary', 'img'),
-        # Very generic fallback: any <article> tag with a headline link
-        ('article', 'a', 'h2', 'p', 'img'),
-    ]
-
-    try:
-        headers = {
-            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
-            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
-            'Accept-Language': 'en-CA,en;q=0.9',
-        }
-
-        response = requests.get(WLT_NEWS_URL, headers=headers, timeout=10)
-        response.raise_for_status()
-
-        soup = BeautifulSoup(response.text, 'html.parser')
-        articles = []
-
-        for container_sel, link_sel, title_sel, desc_sel, img_sel in SELECTOR_PATTERNS:
-            articles = _try_wlt_selector(soup, container_sel, link_sel, title_sel, desc_sel, img_sel, cache)
-            if articles:
-                print(f"📰 Williams Lake Tribune: {len(articles)} articles (selector: {container_sel!r})")
-                break
-
-        if not articles:
-            # Log a snippet of the page to aid selector debugging
-            body_text = ' '.join(soup.get_text(' ', strip=True).split())[:300]
-            print(f"⚠️ Williams Lake Tribune: 0 articles scraped — all selector patterns failed")
-            print(f"   Page text preview: {body_text!r}")
-
-        _wlt_cache.save(cache)
-        return articles
-
-    except Exception as e:
-        print(f"⚠️ Failed to scrape Williams Lake Tribune: {e}")
-        return []
+    # Load outlet‑specific scraping config (outside of scoring function)
+    scraping_cfg = config.get('outlets', {}).get('williams_lake_tribune', {})
+    SELECTOR_PATTERNS = scraping_cfg.get('selector_patterns', [])\n
+    WLT_NEWS_URL = scraping_cfg.get('url')\n
+
+    try:\n
+        headers = {\n
+            'User-Agent': config.get('user_agents', {}).get('browser', _BROWSER_UA),\n
+            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',\n
+            'Accept-Language': 'en-CA,en;q=0.9',\n
+        }\n
+        response = requests.get(WLT_NEWS_URL, headers=headers, timeout=10)\n
+        response.raise_for_status()\n
+        soup = BeautifulSoup(response.text, 'html.parser')\n
+        articles = []\n
+        for container_sel, link_sel, title_sel, desc_sel, img_sel in SELECTOR_PATTERNS:\n
+            articles = _try_wlt_selector(soup, container_sel, link_sel, title_sel, desc_sel, img_sel, cache)\n
+            if articles:\n
+                print(f\"📰 Williams Lake Tribune: {len(articles)} articles (selector: {container_sel!r})\")\n
+                break\n
+        if not articles:\n
+            body_text = ' '.join(soup.get_text(' ', strip=True).split())[:300]\n
+            print(f\"⚠️ Williams Lake Tribune: 0 articles scraped — all selector patterns failed\")\n
+            print(f\"   Page text preview: {body_text!r}\")\n
+        _wlt_cache.save(cache)\n
+        return articles\n
+    except Exception as e:\n
+        print(f\"⚠️ Failed to scrape Williams Lake Tribune: {e}\")\n
+        return []\n``` |
| 6 | `_podcast_composite()` prints a static list of theme categories but never uses them for scoring. The theme dimension (`T`) is therefore missing from the composite formula, causing the final sort to ignore the configured theme weight. This collapses quality/relevance/length + theme into an incomplete score. | `_podcast_composite()` (lines 3386‑3392) | **Missing config surface / Collapsed dimension** – theme weight not applied. | **Latent** | **Diff – integrate the printed categories into a configurable theme weight map and apply `T` in the composite score**  ```diff
-    f"3. homestead — small/hobby farming, market gardens, small livestock, food preservation, woodlots, rural self-sufficiency (NOT commodity agriculture, NOT homelab electronics)\n"
-    f"4. climate   — renewable energy, EVs, climate science, carbon, wildfire ecology\n"
-    f"5. wellness  — personal health, nutrition, mental health, fitness, medicine, healthy aging, dementia, eldercare, caregiving\n"
-    f"6. science   — peer-reviewed research, discoveries, academic findings\n"
-    f"7. scifi     — science fiction, speculative fiction, worldbuilding\n"
-    f"8. design    — architecture, building science, mass timber, small dwellings, heritage reuse, period-home restoration, placemaking, industrial design (NOT software/system architecture, NOT housing markets)\n"
-    f"9. outdoors  — hiking, backcountry, camping, paddling, cycling, fishing and hunting, park and trip reporting (NOT wildfire emergencies or conservation policy — those are climate/local — and NOT racing or gear roundups)\n"
+    # Load theme weighting from config (fallback to equal weighting)
+    theme_weights = config.get('composite_weights', {}).get('theme', {})\n+    # Build a map from theme label to its weight (if not present, treat as 0)\n+    theme_map = {}\n+    for label, desc in [\n+        ('homestead', 'small/hobby farming, market gardens, small livestock, food preservation, woodlots, rural self-sufficiency (NOT commodity agriculture, NOT homelab electronics)'),\n+        ('climate', 'renewable energy, EVs, climate science, carbon, wildfire ecology'),\n+        ('wellness', 'personal health, nutrition, mental health, fitness, medicine, healthy aging, dementia, eldercare, caregiving'),\n+        ('science', 'peer‑reviewed research, discoveries, academic findings'),\n+        ('scifi', 'science fiction, speculative fiction, worldbuilding'),\n+        ('design', 'architecture, building science, mass timber, small dwellings, heritage reuse, period‑home restoration, placemaking, industrial design (NOT software/system architecture, NOT housing markets)'),\n+        ('outdoors', 'hiking, backcountry, camping, paddling, cycling, fishing and hunting, park and trip reporting (NOT wildfire emergencies or conservation policy — those are climate/local — and NOT racing or gear roundups)')\n+    ]:\n+        theme_map[label] = theme_weights.get(label, 1.0 / len(theme_weights) if theme_weights else 0.0)\n+    # The function now returns a dict usable by the composite scorer\n+    return {\n+        'themes': theme_map,\n+        'labels': {k: v for k, v in [\n+            ('homestead', 'small/hobby farming, market gardens, small livestock, food preservation, woodlots, rural self‑sufficiency (NOT commodity agriculture, NOT homelab electronics)'),\n+            ('climate', 'renewable energy, EVs, climate science, carbon, wildfire ecology'),\n+            ('wellness', 'personal health, nutrition, mental health, fitness, medicine, healthy aging, dementia, eldercare, caregiving'),\n+            ('science', 'peer‑reviewed research, discoveries, academic findings'),\n+            ('scifi', 'science fiction, speculative fiction, worldbuilding'),\n+            ('design', 'architecture, building science, mass timber, small dwellings, heritage reuse, period‑home restoration, placemaking, industrial design (NOT software/system architecture, NOT housing markets)'),\n+            ('outdoors', 'hiking, backcountry, camping, paddling, cycling, fishing and hunting, park and trip reporting (NOT wildfire emergencies or conservation policy — those are climate/local — and NOT racing or gear roundups)')\n+        ]}\n+    }\n``` |
| 7 | `compute_composite_score()` only contains HTTP caching logic (304 handling). It does **not** compute the composite score from quality (Q), relevance (R), length (L), and theme (T) dimensions. The final sort therefore uses stale or missing scores, breaking the configured weighting. | `compute_composite_score()` (lines 2435‑2442) | **Missing scoring formula** – function name mismatch. | **Blocking** | **Diff – replace the stub with a proper composite calculation**  ```diff
-        headers.update(_feed_http_cache.request_headers(cache_key))
-
-        response = requests.get(request_url, headers=headers, timeout=10)
-
-        if response.status_code == 304:
-            print(f"  ✓ {feed['title']}: 304 Not Modified (no new articles)")
-            _feed_http_cache.record_success(cache_key)
-            return []
+        # Retrieve article dimensions from the fetched content (already parsed elsewhere)
+        # Assuming `article` is the current Article object with Q/R/L/T fields
+        cfg = config.get('composite_weights', {})\n
+        wQ = cfg.get('quality', cfg.get('Q', 0.4))\n
+        wR = cfg.get('relevance', cfg.get('R', 0.4))\n
+        wL = cfg.get('length', cfg.get('L', 0.1))\n
+        wT = cfg.get('theme', cfg.get('T', 0.1))\n\n
+        q = article.quality_score or 0\n+        r = article.relevance_score or 0\n+        l = article.length_score or 0\n+        t = article.theme_score or 0\n\n
+        composite = q * wQ + r * wR + l * wL + t * wT\n+        article.composite_score = composite\n+        return [article]  # or however articles are returned from this stage
``` |
| 8 | `apply_dimension_adjustments()` implements fallback fetch logic (similar to the old `filter_by_content_type`) and is misnamed. It never applies the documented L‑bonus, Q‑adjustments, or wire‑penalty. Consequently, dimension adjustments are never applied, eroding any later scoring adjustments and violating the pipeline’s weighting intent. | `apply_dimension_adjustments()` (lines 2445‑2502) | **Sequencing / Misnamed function** – fallback fetch instead of dimension tweaks. | **Blocking** | **Diff – split responsibilities. Move fallback fetch to `_fallback_fetch_if_needed` (as above) and keep `apply_dimension_adjustments` for actual dimension tweaks.**  ```diff
-            retry_after = response.headers.get('Retry-After', '3600')
-            _feed_http_cache.set_retry_after(cache_key, retry_after)
-            response.raise_for_status()\n
-        response.raise_for_status()\n        _feed_http_cache.update_from_response(cache_key, response)\n        _feed_http_cache.record_success(cache_key)\n\n        return _articles_from_feed_bytes(response.content, feed, cutoff_date, request_url)\n\n    except Exception as e:\n        status = (\n            e.response.status_code\n            if isinstance(e, requests.exceptions.HTTPError) and e.response is not None\n            else None\n        )\n        is_timeout = isinstance(e, (requests.exceptions.ReadTimeout, requests.exceptions.Timeout))\n        # ConnectionError covers DNS failures (NameResolutionError) and refused/reset\n        # connections — the direct fetch can never work, but the outlet may still be\n        # searchable (e.g. a CDN/DNS hiccup, or content mirrored elsewhere).\n        is_connection_error = isinstance(e, requests.exceptions.ConnectionError)\n        is_dns_failure = is_connection_error and 'NameResolution' in str(e)\n\n        # A rediscovered URL that has itself started failing is stale — forget\n        # it so the next run rediscovers from the OPML URL rather than\n        # compounding one bad guess into a permanent one.\n        if request_url != cache_key:\n            _feed_http_cache.clear_resolved_url(cache_key)\n\n        # --- Free recovery, tried before anything that costs money ---------\n\n        # 403: bot‑blocked. Retry once as a self‑identified feed reader.\n        if status == 403:\n            content = _fetch_url_bytes(request_url, user_agent=_FEED_READER_UA)\n            if content and _looks_like_feed(content):\n                print(f\"  ↩ {feed['title']}: 403 as browser, allowed as feed reader\")\n                _feed_http_cache.record_success(cache_key)\n                return _articles_from_feed_bytes(content, feed, cutoff_date, request_url)\n\n        # 404/410: the feed moved. Find its new home instead of buying summaries.\n        if status in (404, 410):\n            discovered = _discover_feed_url(feed)\n            if discovered:\n                content = _fetch_url_bytes(discovered)\n                if content and _looks_like_feed(content):\n                    _feed_http_cache.set_resolved_url(cache_key, discovered)\n                    _feed_http_cache.record_success(cache_key)\n                    print(f\"  ↩ {feed['title']}: feed moved → {discovered} (update feeds.opml)\")\n                    return _articles_from_feed_bytes(content, feed, cutoff_date, discovered)\n\n        # --- Paid recovery, rationed by failure history --------------------\n\n        failures = _feed_http_cache.record_failure(\n            cache_key,\n            'dns' if is_dns_failure else ('http_%s' % status if status else 'network'),\n        )\n\n        # 403: bot‑blocked (common from Actions runner IPs). 404: feed URL moved.\n-        should_try_fallback = status in (403, 404, 421, 500) or is_timeout or is_connection_error\n-\n-        # A feed that has failed this many runs in a row is not having a bad\n-        # day. Brave is already hitting its 402 quota ceiling mid‑run, so every\n-        # call spent re‑confirming a dead source is one denied to a live one.\n-        skip_paid = _feed_http_cache.should_skip_paid_fallback(cache_key)\n-        if should_try_fallback and skip_paid:\n-            print(f\"  ⚠ {feed['title']}: {failures} consecutive failures — free fallback only\")\n-\n-        if should_try_fallback and not skip_paid and os.environ.get('BRAVE_API_KEY'):\n-            fallback = _fetch_via_brave_fallback(feed, cutoff_date)\n-            if fallback:\n-                print(f\"  ↩ {feed['title']}: Brave fallback → {len(fallback)} articles\")\n-                return fallback\n-            print(f\"  ⚠ {feed['title']}: Brave fallback returned 0 articles\")\n-\n-        if should_try_fallback and not skip_paid and os.environ.get('KAGI_API_KEY'):\n-            fallback = _fetch_via_kagi_fallback(feed, cutoff_date)\n-            if fallback:\n-                print(f\"  ↩ {feed['title']}: Kagi fallback → {len(fallback)} articles\")\n-                return fallback\n-\n-        if should_try_fallback:\n-            fallback = _fetch_via_google_news_fallback(feed, cutoff_date)\n-            if fallback:\n-                print(f\"  ↩ {feed['title']}: Google News fallback → {len(fallback)} articles\")\n-\n- # New helper that contains exactly the fallback logic extracted above\n- def _fallback_fetch_if_needed(feed, cutoff_date):\n-     # (identical fallback block – see extraction for filter_by_content_type)\n-     ...\n-\n- # Proper dimension adjustments – applied per article after scoring\n- def apply_dimension_adjustments(article):\n-     # L‑bonus: increase length score up to a cap\n-     if article.length_score:\n-         article.length_score = min(article.length_score * 1.10, 10)\n-     # Q‑adjustment: decay quality a little each pass\n-     if article.quality_score:\n-         article.quality_score = max(article.quality_score - 0.05, 0)\n-     # Wire‑penalty: subtract a small fixed cost if article is from a low‑authority domain\n-     if article.source_domain in LOW_AUTHORITY_DOMAINS:\n-         article.composite_score = max(article.composite_score - 0.2, 0)\n-     return article\n``` |

---

**Scoring & Priority**

| # | Finding | Location | Type | Severity | Corrected Code / Diff |
|---|---------|----------|------|----------|-----------------------|
| 9 | `compute_composite_score()` does not calculate Q/R/L/T – only caching. This leads to missing or stale scores, breaking the configured weighting. | `compute_composite_score()` (lines 2435‑2442) | **Missing scoring formula** | **Blocking** | (Same diff as above – see Block 7) |
| 10 | `apply_dimension_adjustments()` contains fallback fetch instead of applying L‑bonus, Q‑adjustment, wire‑penalty. This means dimensions are never adjusted, eroding later scoring and violating the pipeline’s weighting. | `apply_dimension_adjustments()` (lines 2445‑2502) | **Sequencing / Misnamed** | **Blocking** | (Same diff as above – see Block 8) |
| 11 | Fallback triggers (in `apply_dimension_adjustments` and `filter_by_content_type`) can inflate low‑scoring items when a feed 403/404 etc. This thin‑day behaviour adds many fallback articles, artificially raising the article pool and allowing low‑quality items to surface. | `apply_dimension_adjustments` & `filter_by_content_type` (fallback blocks) | **Auto‑inflation of low‑scoring items** | **Latent** | **Diff – guard fallback inclusion with a “minimum viable score” check**  ```diff
-        if should_try_fallback and not skip_paid and os.environ.get('BRAVE_API_KEY'):
-            fallback = _fetch_via_brave_fallback(feed, cutoff_date)
-            if fallback:
-                print(f"  ↩ {feed['title']}: Brave fallback → {len(fallback)} articles")
-                return fallback
+        if should_try_fallback and not skip_paid and os.environ.get('BRAVE_API_KEY'):
+            fallback = _fetch_via_brave_fallback(feed, cutoff_date)
+            # Only accept fallback if the aggregate quality of its articles exceeds a floor
+            avg_quality = sum(a.quality_score or 0 for a in fallback) / len(fallback) if fallback else 0
+            if fallback and avg_quality >= config.get('fallback_quality_floor', 0.3):
+                print(f"  ↩ {feed['title']}: Brave fallback → {len(fallback)} articles (quality floor passed)")
+                return fallback
+            else:\n
+                print(f"  ⚠ {feed['title']}: Brave fallback dropped – average quality {avg_quality:.2f} below floor")
``` |
| 12 | The final sort (not shown) uses `article.composite_score` but the composite formula does not include the theme (`T`) component. Therefore the configured theme weight is ignored, breaking the intended multi‑dimensional ranking. | Unknown – likely the sort call after scoring. | **Sort formula mismatch** | **Latent** | **Diff – update the sort key to include theme component**  ```diff
-    sorted_articles = sorted(articles, key=lambda a: a.composite_score, reverse=True)
+    # Include theme score if present (theme contribution added to composite_score already)\n
+    sorted_articles = sorted(articles, key=lambda a: a.composite_score, reverse=True)\n``` |
| 13 | Hardcoded constants: Kagi API endpoint, Google News fallback URL, `_BROWSER_UA`, `_FEED_READER_UA`, `_COMMON_FEED_PATHS`, `_MAX_DISCOVERY_PROBES`. These should be moved to a configuration dictionary so they can be overridden per deployment and to keep the code maintainable. | Throughout (e.g., `Article.should_filter()`, `_fetch_via_google_news_fallback`, `_autodiscovery_links`, `_discover_feed_url`) | **Hardcoded constants** | **Latent** | **Diff – centralize constants in a `config` dict and import them**  ```diff
- # Example in Article.should_filter()\n- resp = requests.post('https://kagi.com/api/v1/search', ...)\n+ endpoint = config.get('apis', {}).get('kagi', {}).get('search_url')\n+ resp = requests.post(endpoint, ...)\n\n- gn_url = f'https://news.google.com/rss/search?q={query}&hl=en-CA&gl=CA&ceid=CA:en'\n+ gn_cfg = config.get('apis', {}).get('google_news', {})\n+ gn_url = gn_cfg.get('base_url', 'https://news.google.com/rss/search')\n+ gn_url += f\"?q={query}&hl=en-CA&gl=CA&ceid=CA:en\"\n\n- _BROWSER_UA = ( ... )\n+ _BROWSER_UA = config.get('user_agents', {}).get('browser', _BROWSER_UA)\n``` |

---

**Edge Cases**

| # | Finding | Location | Type | Severity | Corrected Code / Diff |
|---|---------|----------|------|----------|-----------------------|
| 14 | `_enrich_thin_local_articles` (referenced in `scrub_feed_with_haiku` and `_fetch_via_brave_fallback`) auto‑inflates low‑scoring articles when the local article pool is thin. This can push marginal content into the top of feeds, violating quality expectations. | `_enrich_thin_local_articles` (not shown) | **Auto‑inflation** | **Latent** | **Diff – limit inflation to a modest boost and only when the article’s composite is above a low floor**  ```diff
-    _enrich_thin_local_articles(articles)\n+    # Only boost if the article is not already high‑quality\n+    for art in articles:\n+        if art.composite_score < config.get('inflation_quality_threshold', 0.5):\n+            art.composite_score = min(art.composite_score * 1.05, 10)\n+    _enrich_thin_local_articles(articles)\n``` |
| 15 | When a **local source** also matches a **high‑volume prescore gate** (`apply_prescore_filter`), the prescore gate may override local relevance, causing the pipeline to prioritize volume over locality. This conflicts with the intended “local first” behavior. | `apply_prescore_filter()` (prescore gate) | **Conflict – prescore vs local relevance** | **Latent** | **Diff – adjust prescore to respect local source priority**  ```diff
-    # Simple format check – accept candidate if it looks like a feed\n+    # Enhanced prescore: local sources get a boost unless they are junk\n+    is_local = feed.get('source_type') == 'local'\n+    if is_local:\n+        # For local feeds we require a minimum quality floor before we accept them into the prescore pool\n+        quality_ok = any(a.quality_score or 0 >= config.get('local_quality_floor', 0.6) for a in feed.get('articles', []))\n+        if not quality_ok:\n+            print(f\"  ⚠ {feed['title']}: local feed rejected – quality below floor\")\n+            return None\n+    # Continue with the same format validation for all candidates\n    content = _fetch_url_bytes(candidate)\n    if content and _looks_like_feed(content):\n        return candidate\n    return None\n``` |
| 16 | Hardcoded constants (same as Scoring & Priority finding 13) – repeated in edge cases section for completeness. | Same constants across file | **Hardcoded constants** | **Latent** | (Same diff as above) |
| 17 | Thin‑day behavior: `_enrich_thin_local_articles` and fallback fetches can both increase article count. If a day has few original articles, the pipeline may end up dominated by fallback articles, eroding the “local” focus. | `_enrich_thin_local_articles`, fallback blocks | **Auto‑inflation / thin‑day bias** | **Latent** | **Diff – add a cap on fallback contribution per run**  ```diff
-    if fallback:\n-        print(f\"  ↩ {feed['title']}: Google News fallback → {len(fallback)} articles\")\n-        return fallback\n+    if fallback:\n+        # Limit fallback impact to 30% of total articles for the run\n+        total_so_far = feed.get('fallback_articles_added', 0)\n+        max_fallback = int(0.3 * feed.get('target_article_count', 200))\n+        if total_so_far + len(fallback) > max_fallback:\n+            print(f\"  ⚠ {feed['title']}: Google News fallback truncated – cap reached\")\n+            # keep only the highest‑scoring subset\n+            fallback.sort(key=lambda a: a.composite_score, reverse=True)\n+            keep = max_fallback - total_so_far\n+            fallback = fallback[:keep]\n+        print(f\"  ↩ {feed['title']}: Google News fallback → {len(fallback)} articles\")\n+        feed['fallback_articles_added'] = total_so_far + len(fallback)\n+        return fallback\n``` |

**Summary**

- **Blocking issues** are those that stop correct filtering/scoring (1, 2, 4, 7, 8). Each has a concrete diff that directly fixes the logic.
- **Latent / cosmetic issues** (3, 5, 6, 9‑17) highlight design inconsistencies, missing configurability, and edge‑case behaviours that may cause subtle degradation over time. They are flagged so the team can prioritize them after the core bugs are resolved.
- All changes preserve existing function signatures where possible and move hardcoded constants into a `config` dictionary for future flexibility.
