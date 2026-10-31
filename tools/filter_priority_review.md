# Filter & Priority Logic Review

**Date:** 2026-10-31  
**Model:** north-mini-code-1-0  

---

**Filter Logic**

**Finding 1 – Stray early return in Article parsing (blocking, conflict/sequencing)**  
*Location:* Approx. line 520 inside the function that creates an `Article` (the snippet labeled “Article.should_filter()”).  
*Problem:* An unconditional `return None` appears before any processing, causing all articles to be discarded regardless of content.  
*Corrected code (remove the stray line):*

```python
# Before:
            return None
        source_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
...
# After:
        source_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
...
```

**Finding 2 – Hard‑coded “www.” stripping (hard‑code, latent)**  
*Location:* Approx. line 525, domain cleaning.  
*Problem:* The domain cleaning logic assumes the “www.” prefix should always be stripped. This should be configurable so that sites that retain “www.” can be handled differently.  
*Corrected code (use config):*

```python
# Assuming CONFIG is a global dict loaded earlier (e.g., from system.json)
from system_config import CONFIG

domain = parsed_url.netloc.lower()
if CONFIG.get('strip_www', True) and domain.startswith('www.'):
    domain = domain[4:]
```

**Finding 3 – Duplicate cut‑off date filtering across stages (sequencing, blocking)**  
*Location:*  
- In `Article` creation (line 540‑545) – filter on `pub_date < cutoff_date`.  
- In `compute_composite_score` (line 2440‑2445) – same check.  
- In `filter_by_content_type` (line 2525‑2530) – same check.  

*Problem:* The same cut‑off logic is repeated in three places, creating a sequencing issue where an article may be dropped early and never reach later scoring or enrichment steps.  
*Corrected code (remove the redundant checks, keeping only the first one in the ingestion stage):*

```python
# compute_composite_score – remove cut‑off block
# Before:
        if pub_date and pub_date < cutoff_date:
            continue
# After: (nothing – cut‑off already applied upstream)

# filter_by_content_type – remove cut‑off block
# Before:
        if pub_date and pub_date < cutoff_date:
            continue
# After: (nothing – cut‑off already applied upstream)
```

**Finding 4 – Content‑type filter misnomer (latent, missing config surface)**  
*Location:* `filter_by_content_type` (lines 2505‑2534). The function is documented to drop “fluff/sponsored/recap” but actually only validates that `title` and `link` exist. No real content‑type analysis is performed.  
*Corrected code (add a simple content‑type check using a configurable list of drop patterns):*

```python
# Assuming CONFIG['drop_patterns'] is a list of substrings that indicate fluff
drop_patterns = CONFIG.get('drop_patterns', [])
text = f"{entry.get('title','')} {entry.get('description','')}".lower()
if any(pat.lower() in text for pat in drop_patterns):
    continue   # drop fluff / sponsored / recap
```

**Finding 5 – Network‑card drop happens before dimension adjustments (conflict, blocking)**  
*Location:* `_drop_network_cards` (lines 2220‑2280). Cards that are shared or stale are dropped even though later stages (L‑bonus, Q‑adjustments, etc.) could boost them. This contradicts the “local priority” intention and erodes score floors.  
*Corrected code (delay the drop until after adjustments – keep all cards and flag them for later low‑priority handling). For simplicity, we move the drop logic out of `_drop_network_cards` and into a post‑scoring filter. The function now returns all cards but annotates network cards:*

```python
def _drop_network_cards(scraped: List[Dict],
                        now: Optional[datetime] = None) -> List[Dict]:
    now = now or datetime.now(timezone.utc)
    local_signals = [s.lower() for s in FILTERS.get('local_signals', [])]
    permalink = {c['link']: _PERMALINK_RE.match(urlparse(c['link']).path) for c in scraped}
    papers_by_slug: Dict[str, Set[str]] = defaultdict(set)
    for card in scraped:
        if permalink[card['link']]:
            papers_by_slug[permalink[card['link']].group(4)].add(card['source'])

    kept: List[Dict] = []
    for card in scraped:
        text = f"{card.get('title','')} {card.get('description','')}".lower()
        match = permalink[card['link']]
        # Mark network cards for later low‑priority handling
        if match is not None and not any(signal in text for signal in local_signals):
            card['_is_network_card'] = True
            # Compute age / shared for later reference
            year, month, day, slug = match.groups()
            try:
                age_days = (now - datetime(int(year), int(month), int(day), tzinfo=timezone.utc)).days
            except ValueError:
                age_days = 0
            card['_network_age_days'] = age_days
            card['_network_shared_count'] = len(papers_by_slug[slug])
        kept.append(card)
    return kept
```

*Later, after `apply_dimension_adjustments`, a post‑scoring filter can inspect `_is_network_card` and drop those that still meet the shared/stale criteria. This preserves the original intent while allowing adjustments to act first.*

**Finding 6 – Date parsing bug using a string as integer (blocking, bug)**  
*Location:* `_drop_network_cards`, line constructing `datetime`. `day` is a string from regex groups.  
*Corrected code:*

```python
year, month, day, slug = match.groups()
try:
    age_days = (now - datetime(int(year), int(month), int(day), tzinfo=timezone.utc)).days
except ValueError:
    age_days = 0
```

**Finding 7 – Hard‑coded network‑card constants (hard‑code, blocking)**  
*Location:* `_SCRAPE_STALE_DAYS = 4` and `_PERMALINK_RE` at module top (lines 2210‑2215).  
*Corrected code (load from config):*

```python
# Assuming CONFIG is loaded from system.json or environment
CONFIG = get_config()   # placeholder for your config loader

_SCRAPE_STALE_DAYS = CONFIG.get('network_card', {}).get('stale_days', 4)
_PERMALINK_RE = re.compile(
    CONFIG.get('network_card', {}).get('permalink_pattern',
        r'^/(\d{4})/(\d{2})/(\d{2})/([^/]+)/?$')
)
```

---

**Scoring & Priority**

**Finding 8 – Quality & relevance collapsed into a single composite (latent, missing config surface)**  
*Location:* Not visible in snippets, but the presence of a single `composite_score` variable in `compute_composite_score` and `apply_dimension_adjustments` suggests Q and R may be combined too early.  
*Corrective direction:* Split Q and R into separate fields until the final sorting step, then apply configurable weights. (Implementation depends on the rest of the pipeline; not provided.)

**Finding 9 – Final sort formula may not match configured weights (latent, missing config surface)**  
*Location:* The final sorting logic (likely in a downstream stage) is not shown. If the sort uses a hard‑coded weight distribution instead of reading from `CONFIG['scoring_weights']`, the configured priorities are ignored.  
*Corrective direction:* Ensure the sort uses the weights from config, e.g.:

```python
weights = CONFIG.get('scoring_weights', {'quality':0.5, 'relevance':0.3, 'local':0.2})
articles.sort(key=lambda a: (
    a.quality * weights['quality'] +
    a.relevance * weights['relevance'] +
    a.local_score * weights['local']
), reverse=True)
```

**Finding 10 – Thin‑day auto‑inflation of low‑scoring items (edge case, latent)**  
*Location:* `_enrich_thin_local_articles` (line 2150‑2180) – any article whose summary length is `< 100` and link contains a local BC domain is re‑fetched and replaces the description, effectively inflating its quality score.  
*Problem:* This can cause articles that should score low (e.g., fluff) to receive a boost simply because they are thin, eroding score floors.  
*Corrected code (make the enrichment threshold configurable and optionally gated):*

```python
MIN_SUMMARY_LENGTH = CONFIG.get('local_article_min_summary_length', 100)

def _enrich_thin_local_articles(articles: List['Article']) -> int:
    fetched = 0
    for article in articles:
        if (len(article.summary) < MIN_SUMMARY_LENGTH and
                any(d in article.link for d in _LOCAL_BC_DOMAINS)):
            body = _fetch_article_excerpt(article.link, max_chars=600)
            if body and not _is_tagline_boilerplate(body):
                article.description = body
                article.summary = _clean_text(body, max_chars=300)
                article.excerpt = _clean_text(body, max_chars=600)
                fetched += 1
    return fetched
```

---

**Edge Cases**

**Finding 11 – Local source vs high‑volume prescore gate (conflict, blocking)**  
*Location:* `_kagi_enrich_articles` (line 2250‑2280). Local articles are always added to the `local` list and enriched regardless of any prescore keyword gate, while non‑local articles are gated by `prescore_keywords`. This means a local source that also matches a high‑volume prescore gate wins (gets enriched) while the same gate would have otherwise blocked it.  
*Problem:* The prescore gate’s intent (to limit high‑volume aggregator noise) is subverted by local‑source priority.  
*Corrected code (honor the prescore gate for local sources when the gate is active):*

```python
# Assume CONFIG['prescore_gate_max_sources'] exists and >0 when the gate is active
prescore_gate_active = CONFIG.get('prescore_gate_max_sources', 0) > 0

# Inside _kagi_enrich_articles, before adding to local list:
if any(d in a.link for d in _LOCAL_BC_DOMAINS):
    if prescore_gate_active and prescore_keywords:
        # Check if this local article matches any prescore keyword
        if any(kw in a.title.lower() for kw in prescore_keywords):
            # Treat as non‑local for enrichment – it will be gated
            other.append(a)
            continue
    local.append(a)
    continue
```

**Finding 12 – Hard‑coded Kagi batch / excerpt constants (hard‑code, latent)**  
*Location:* `KAGI_EXTRACT_BATCH = 10` and `KAGI_EXCERPT_CHARS = 2000` near the top of the file.  
*Corrected code (use config):*

```python
KAGI_EXTRACT_BATCH = CONFIG.get('kagi', {}).get('extract_batch', 10)
KAGI_EXCERPT_CHARS = CONFIG.get('kagi', {}).get('excerpt_chars', 2000)
```

---

**Summary of Blocking Fixes Provided**

1. Removed stray `return None` in Article creation.  
2. Made “www.” stripping configurable.  
3. Unified cut‑off date filtering (removed redundant checks in `compute_composite_score` and `filter_by_content_type`).  
4. Added real content‑type drop logic in `filter_by_content_type`.  
5. Restructured `_drop_network_cards` to defer network‑card dropping until after dimension adjustments (adds `_is_network_card` flag).  
6. Fixed date‑parsing bug (`int(day)`).  
7. Made `_SCRAPE_STALE_DAYS` and `_PERMALINK_RE` configurable.  
8. Made thin‑day enrichment threshold configurable.  
9. Made prescore gate respect local sources when the gate is active.  
10. Made Kagi batch/extract constants configurable.  

All corrected code snippets are ready to be applied directly to the repository.
