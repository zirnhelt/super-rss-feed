# Filter & Priority Logic Review

**Date:** 2026-10-24  
**Model:** north-mini-code-1-0  

---

**Filter Logic**

1. **Hard‑coded stale‑day threshold** – `_SCRAPE_STALE_DAYS = 4` (line ≈2220) is a deployment‑specific value that should be configurable.  
   - **Location:** Global constant in `scrub_feed_with_haiku.py`.  
   - **Type:** Hard‑code / Missing config surface.  
   - **Severity:** Latent – can be changed per environment without code change.  
   - **Fix:** Load from `FILTERS` (or a dedicated `CONFIG` dict).  
     ```diff
     -_SCRAPE_STALE_DAYS = 4
     +_SCRAPE_STALE_DAYS = FILTERS.get('scrape_stale_days', 4)
     ```

2. **Hard‑coded permalink regex** – `_PERMALINK_RE = re.compile(r'^/(\d{4})/(\d{2})/(\d{2})/([^/]+)/?$')` (line ≈2222) should be a configurable pattern.  
   - **Location:** Same file, same region.  
   - **Type:** Hard‑code / Missing config surface.  
   - **Severity:** Latent.  
   - **Fix:**  
     ```diff
     -_PERMALINK_RE = re.compile(r'^/(\d{4})/(\d{2})/(\d{2})/([^/]+)/?$')
     +_PERMALINK_RE = re.compile(FILTERS.get('permalink_pattern',
     +                                 r'^/(\d{4})/(\d{2})/(\d{2})/([^/]+)/?$'))
     ```

3. **Drop decisions made before enrichment** – `_drop_network_cards` (lines 2240‑2290) discards network cards that are shared or stale **before** any thin‑description enrichment (`_enrich_thin_local_articles` / `_kagi_enrich_articles`). This sequencing means a card that could be rescued by a later enrichment is permanently dropped.  
   - **Location:** `_drop_network_cards` called from `scrape_local_news` (line ≈2330).  
   - **Type:** Sequencing issue – premature drop.  
   - **Severity:** **Blocking** – low‑quality but salvageable articles are lost.  
   - **Fix:** Move enrichment before the drop for scraped cards. The simplest fix is to let `_enrich_thin_local_articles` run on the scraped list **before** `_drop_network_cards`. Example rewrite of `scrape_local_news`:  
     ```diff
     def scrape_local_news() -> List[Dict]:
         # ... (scraping code unchanged)
         scraped: List[Dict] = []
         for paper in LOCAL_SCRAPES:
             # ... (scraping logic unchanged)
             scraped.extend({**a, 'source': source, 'base_url': base_url} for a in articles)

         # ---- NEW: enrich thin scraped articles before dropping network cards ----
         # Convert dicts to Article objects (reuse the Article constructor used elsewhere)
         enriched_articles: List[Article] = []
         for entry in scraped:
             # Build a minimal _AttrDict that matches Article.__init__ expectations
             from _AttrDict import _AttrDict
             attr_entry = _AttrDict({
                 'title': entry.get('title', ''),
                 'link': entry.get('link', ''),
                 'description': entry.get('description', ''),
                 'summary': entry.get('description', ''),
                 'published': entry.get('published', ''),
                 'published_parsed': None,
                 'updated_parsed': None,
                 'media_thumbnail': [],
                 'media_content': [],
                 'enclosures': [],
                 'tags': [],
             })
             art = Article(attr_entry, entry.get('source', ''), entry.get('base_url', ''), '')
             # Run the same thin‑article enrichment used for RSS/search results
             if len(art.summary) < FILTERS.get('enrich_summary_threshold', 100):
                 # (re‑use the existing _enrich_thin_local_articles logic – simplified)
                 body = _fetch_article_excerpt(art.link, max_chars=600)
                 if body and not _is_tagline_boilerplate(body):
                     art.description = body
                     art.summary = _clean_text(body, max_chars=300)
                     art.excerpt = _clean_text(body, max_chars=600)
             enriched_articles.append(art)

         # Convert back to dicts for the existing drop logic
         kept_dicts: List[Dict] = []
         for art in enriched_articles:
             kept_dicts.append({
                 'title': art.title,
                 'link': art.link,
                 'description': art.description,
                 'summary': art.summary,
                 'source': art.source,   # Article stores source in .source
                 'base_url': art.html_url,  # Article stores html_url
             })

         kept_dicts = _drop_network_cards(kept_dicts)
         return kept_dicts
     ```

     *Explanation*: The rewrite (shown in compact form) ensures that any scraped article with a thin description gets the same enrichment path as RSS/search results before the network‑card drop runs. Adjust attribute names to match the actual `Article` class if they differ.

4. **Hard‑coded read‑time regex** – `_READ_TIME_RE` (used in `_try_wlt_selector` and `_kagi_enrich_articles`) is a module‑level regex that strips “X min read” boilerplate. It belongs in `FILTERS`.  
   - **Location:** `_try_wlt_selector` (line ≈2420).  
   - **Type:** Hard‑code / Missing config surface.  
   - **Severity:** Latent.  
   - **Fix:** Define regex from config.  
     ```diff
     -_READ_TIME_RE = re.compile(r'\d+\s*min\s*read', re.IGNORECASE)
     +_READ_TIME_RE = re.compile(FILTERS.get('read_time_pattern',
     +                               r'\d+\s*min\s*read', re.IGNORECASE))
     ```

5. **Hard‑coded local BC domains list** – `_LOCAL_BC_DOMAINS` (used in `_enrich_thin_local_articles` and `_kagi_enrich_articles`) is a list of domain strings that should be sourced from `FILTERS`.  
   - **Location:** Top‑of‑file definition (line ≈2100).  
   - **Type:** Hard‑code / Missing config surface.  
   - **Severity:** Latent.  
   - **Fix:**  
     ```diff
     -_LOCAL_BC_DOMAINS = ['vancouversun.com', 'vancouversun.com', 'theprovince.com', ...]
     +_LOCAL_BC_DOMAINS = FILTERS.get('local_bc_domains', [])
     ```

---

**Scoring & Priority**

1. **Hard‑coded enrichment thresholds** – `len(article.summary) < 100` (`_enrich_thin_local_articles`) and `len(a.description.strip()) >= 150` (`_kagi_enrich_articles`) are deployment‑specific cut‑offs.  
   - **Location:** `_enrich_thin_local_articles` (line ≈2180) and `_kagi_enrich_articles` (line ≈2240).  
   - **Type:** Hard‑code / Missing config surface.  
   - **Severity:** Latent – changing thresholds requires code change.  
   - **Fix:** Use config values.  
     ```diff
     # At module top:
     -ENRICH_SUMMARY_THRESHOLD = 100
     -ENRICH_DESCRIPTION_THRESHOLD = 150
     +ENRICH_SUMMARY_THRESHOLD = FILTERS.get('enrich_summary_threshold', 100)
     +ENRICH_DESCRIPTION_THRESHOLD = FILTERS.get('enrich_description_threshold', 150)

     # In _enrich_thin_local_articles:
     -if (len(article.summary) < 100
     +if (len(article.summary) < ENRICH_SUMMARY_THRESHOLD

     # In _kagi_enrich_articles:
     -if len(a.description.strip()) >= 150:
     +if len(a.description.strip()) >= ENRICH_DESCRIPTION_THRESHOLD:
     ```

2. **Hard‑coded Kagi batch & excerpt sizes** – `KAGI_EXTRACT_BATCH = 10`, `KAGI_EXCERPT_CHARS = 2000`, and `max_calls = 40` are all constant limits that should be configurable.  
   - **Location:** Definitions near line ≈2150 (global) and `_kagi_enrich_articles` signature.  
   - **Type:** Hard‑code / Missing config surface.  
   - **Severity:** Latent.  
   - **Fix:** Load from `FILTERS`.  
     ```diff
     -KAGI_EXTRACT_BATCH = 10
     -KAGI_EXCERPT_CHARS = 2000
     -def _kagi_enrich_articles(..., max_calls: int = 40, ...):
     +KAGI_EXTRACT_BATCH = FILTERS.get('kagi_extract_batch', 10)
     +KAGI_EXCERPT_CHARS = FILTERS.get('kagi_excerpt_chars', 2000)
     +def _kagi_enrich_articles(..., max_calls: int = FILTERS.get('kagi_max_calls', 40), ...):
     ```

3. **Hard‑coded user‑agent strings** – `_BROWSER_UA` and `_FEED_READER_UA` are deployment‑specific HTTP headers.  
   - **Location:** In `apply_prescore_filter` region (line ≈2300).  
   - **Type:** Hard‑code / Missing config surface.  
   - **Severity:** Latent.  
   - **Fix:** Pull from config.  
     ```diff
     -_BROWSER_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
     -                  '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
     -_FEED_READER_UA = ('SuperRSSCurator/1.0 (+https://zirnhelt.github.io/super-rss-feed/) '
     -                    'RSS/Atom feed reader')
     +_BROWSER_UA = FILTERS.get('browser_ua',
     +                         ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
     +                          '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'))
     +_FEED_READER_UA = FILTERS.get('feed_reader_ua',
     +                             ('SuperRSSCurator/1.0 (+https://zirnhelt.github.io/super-rss-feed/) '
     +                              'RSS/Atom feed reader'))
     ```

4. **Hard‑coded feed‑discovery constants** – `_COMMON_FEED_PATHS` and `_MAX_DISCOVERY_PROBES` control how aggressively the pipeline looks for alternate RSS locations.  
   - **Location:** Near `_fetch_via_brave_fallback` (line ≈2330).  
   - **Type:** Hard‑code / Missing config surface.  
   - **Severity:** Latent.  
   - **Fix:**  
     ```diff
     -_COMMON_FEED_PATHS = ('/feed/', '/rss/', '/rss.xml', '/feed.xml', '/atom.xml',
     -                       '/index.xml', '/blog/feed/', '/news/feed/',
     -                       '/feeds/posts/default')
     -_MAX_DISCOVERY_PROBES = 6
     +_COMMON_FEED_PATHS = FILTERS.get('common_feed_paths',
     +                               ('/feed/', '/rss/', '/rss.xml', '/feed.xml', '/atom.xml',
     +                                '/index.xml', '/blog/feed/', '/news/feed/',
     +                                '/feeds/posts/default'))
     +_MAX_DISCOVERY_PROBES = FILTERS.get('max_discovery_probes', 6)
     ```

5. **Potential score‑floor erosion** – The `compute_composite_score` → `apply_dimension_adjustments` chain is not visible in the supplied snippets, so we cannot verify whether a later penalty can drop a score below a configured floor.  
   - **Location:** Functions `compute_composite_score`, `apply_dimension_adjustments` (lines 2435‑2502).  
   - **Type:** Missing verification.  
   - **Severity:** Latent (could be blocking if a floor is breached).  
   - **Action Required:** Provide the full bodies of `compute_composite_score` and `apply_dimension_adjustments` (and any floor constants) for definitive review.

---

**Edge Cases**

1. **Thin‑day auto‑inflation** – `_enrich_thin_local_articles` and `_kagi_enrich_articles` automatically fetch full article text when `summary`/`description` are short. This is intended “thin‑day” behaviour, but the decision to inflate rests on hard‑coded thresholds (see Scoring findings). Moving those thresholds to config gives control over how aggressively low‑scoring items are rescued.  

2. **Local source vs high‑volume prescore gate** – `apply_prescore_filter` (aggregator source gating) is not visible, but `_drop_network_cards` **always keeps** cards that contain any `local_signals` even if they are stale/shared. If a local source also matches a high‑volume prescore gate (e.g., a bulk RSS feed that would normally be throttled), the current logic means the prescore gate is bypassed for those cards. This can be a conflict:  
   - **Location:** `_drop_network_cards` (line 2260) and presumed `apply_prescore_filter`.  
   - **Type:** Logic conflict / sequencing.  
   - **Severity:** **Blocking** – a local article that should be limited by volume may slip through.  
   - **Fix:** Apply the prescore gate **before** the local‑signal keep‑logic, or combine the checks. Example modification of `_drop_network_cards` (or the surrounding `scrape_local_news` flow) to respect prescore limits:  
     ```diff
     # In scrape_local_news, after enrichment but before _drop_network_cards:
     # Assume apply_prescore_filter returns a set of sources that are gated out:
     gated_sources = apply_prescore_filter(kept_dicts)  # returns list of source names to drop
     kept_dicts = [c for c in kept_dicts if c.get('source') not in gated_sources]
     kept_dicts = _drop_network_cards(kept_dicts)
     ```  
     *Note*: The exact signature of `apply_prescore_filter` must be checked; the snippet above shows a plausible integration.  

3. **Hard‑coded `_READ_TIME_RE` and `_LOCAL_BC_DOMAINS`** – already listed under Filter Logic for completeness.

4. **Missing verification of final sort formula** – `_podcast_composite` (lines 3386‑3392) and surrounding scoring logic are not visible, so we cannot confirm that the final sort respects the configured weights.  
   - **Location:** `_podcast_composite` and any weight constants (`QUALITY_WEIGHT`, `RELEVANCE_WEIGHT`, etc.).  
   - **Type:** Missing verification.  
   - **Severity:** Latent.  
   - **Action Required:** Provide the full bodies of `_podcast_composite` and any weight definitions.

---

**Summary of Required Additional Code**

To complete a full blocking‑grade review, the following functions need their complete implementations supplied:

- `apply_prescore_filter` (aggregator source gating) – to verify gating logic and its interaction with local‑signal handling.  
- `compute_composite_score` – to confirm Q/R/L weighting, floors, and that later penalties cannot erode a protected minimum.  
- `apply_dimension_adjustments` – to ensure L‑bonuses, Q‑adjustments, and wire‑penalties are applied in the correct order and do not unintentionally zero‑out scores.  
- `filter_by_content_type` – to verify hard‑drop rules (fluff/sponsored/recap) are not contradictory with other filters.  
- `_podcast_composite` – to verify the final sort formula matches any configured weight constants.  

**Next Step:** Please provide the missing full bodies (or the relevant sections) for the five functions above so that the review can be finished and any remaining blocking issues can be fixed.
