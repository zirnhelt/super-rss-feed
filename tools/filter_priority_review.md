# Filter & Priority Logic Review

**Date:** 2026-10-17  
**Model:** north-mini-code-1-0  

---

### Filter Logic

**Finding 1** – *Missing keyword/source/title‑pattern blocking in Article creation* (latent)  
- **Location**: Article.__init__ (lines 520‑545, comment references “keyword/source/title‑pattern blocking”) – the code builds an Article but never applies any keyword, source or title‑pattern block; it only checks for empty title and a cutoff date.  
- **Problem**: The comment promises a filter that does not exist, so the pipeline can admit articles that should be filtered out (e.g., “politics”, blocked domains, title patterns like “Advertisement”).  
- **Fix**: Add a common filter step using the same config surface as the rest of the pipeline (e.g., `FILTERS.get('blocked_keywords', [])`, `FILTERS.get('blocked_sources', [])`, `FILTERS.get('blocked_title_patterns', [])`).  

```python
# After building the article but before the date check
blocked_keywords = FILTERS.get('blocked_keywords', [])
blocked_sources  = FILTERS.get('blocked_sources', [])
blocked_title_patterns = FILTERS.get('blocked_title_patterns', [])

# Description/keyword filter
if any(kw.lower() in article.description.lower() for kw in blocked_keywords):
    return None

# Source filter (domain matches blocked source list)
if article.domain in blocked_sources:
    return None

# Title pattern filter (simple fnmatch support)
import fnmatch
title_lower = article.title.lower()
if any(fnmatch.fnmatch(title_lower, pat.lower()) for pat in blocked_title_patterns):
    return None
```

**Finding 2** – *Contradictory filter application – fallback fetch bypasses keyword/source/title blocking* (blocking)  
- **Location**: `_fetch_via_brave_fallback` and `_fetch_via_kagi_fallback` inside `scrub_feed_with_haiku()` (lines 2208‑2339). They build `Article` objects from search results but never run the same keyword/source/title block that the regular feed path uses.  
- **Problem**: An article that would be rejected by the feed path can slip in via a fallback, breaking the consistency of the filter stage.  
- **Fix**: Re‑use the same blocking logic (or a shared helper) for fallback articles. The simplest is to move the block into a small helper and call it for every Article before returning it.

```python
def _apply_content_block_filter(article):
    """Return True if the article should be kept, False if it must be dropped."""
    blocked_keywords = FILTERS.get('blocked_keywords', [])
    blocked_sources  = FILTERS.get('blocked_sources', [])
    blocked_title_patterns = FILTERS.get('blocked_title_patterns', [])

    # description/keyword
    if any(kw.lower() in article.description.lower() for kw in blocked_keywords):
        return False
    # source
    if article.domain in blocked_sources:
        return False
    # title pattern
    import fnmatch
    if any(fnmatch.fnmatch(article.title.lower(), pat.lower()) for pat in blocked_title_patterns):
        return False
    return True

# Inside _fetch_via_brave_fallback (after Article is created)
if not _apply_content_block_filter(article):
    continue   # drop this article, do not add to the list
articles.append(article)
```

Apply the same helper in `_fetch_via_kagi_fallback` and any other place that creates Articles from external sources (e.g., `apply_prescore_filter`).

**Finding 3** – *Early unconditional drop in `apply_prescore_filter` before scoring adjustments* (blocking)  
- **Location**: `apply_prescore_filter()` (lines 2343‑2383). The snippet shows an indented `return []` at the top of the function – effectively discarding all articles before any per‑article scoring or dimension work.  
- **Problem**: The prescore gate is meant to gate *aggregator* sources, not to throw away every article. If the condition evaluates true (e.g., feed is an aggregator with no explicit allow‑list), the pipeline ends prematurely, eroding any later score‑floor or penalty logic.  
- **Fix**: Replace the blanket early return with a per‑article filter that respects the aggregator gating while still letting other articles through.

```python
def apply_prescore_filter(feed: dict, results: list, cutoff_date: datetime) -> List[Article]:
    """Aggregator source gating – keep only articles that satisfy the prescore rule."""
    allowed_sources = feed.get('allowed_sources', [])
    aggregator_flag = feed.get('aggregator', False)

    filtered = []
    for r in results:
        # Build the Article (same as existing code)
        entry = _AttrDict({
            'title': (r.get('title') or '').strip(),
            'link': r.get('url', ''),
            'description': (r.get('snippet') or '')[:500],
            'summary': (r.get('snippet') or '')[:500],
            'published': r.get('published') or '',
            # ... other fields ...
        })
        if not entry.get('title') or not entry.get('link'):
            continue
        article = Article(entry, feed['title'], feed.get('html_url', ''), feed['url'])
        # Date cut‑off – keep existing behaviour
        pub_date = None
        if article.pub_date and article.pub_date < cutoff_date:
            continue

        # Aggregator source gating – only drop if the feed is an aggregator *and* the article’s source isn’t allowed
        if aggregator_flag and allowed_sources and article.domain not in allowed_sources:
            continue

        # Apply the shared content block filter so the fallback path isn’t bypassed
        if not _apply_content_block_filter(article):
            continue

        filtered.append(article)

    return filtered
```

**Finding 4** – *Network‑card drop before any scoring adjustments* (latent)  
- **Location**: `_drop_network_cards()` (inside `score_articles_with_claude`, lines ~1970‑2205). Cards are removed based on duplicate slug, age or local‑signal presence **before** the dimension adjustments and composite scoring run.  
- **Problem**: A network card that is old or syndicated elsewhere is discarded even though later adjustments (e.g., L‑bonus for local relevance) could have rescued it, and the prescore gate may have already accepted it. This creates a sequencing conflict.  
- **Fix**: Move the drop logic into a **post‑scoring** stage (e.g., after `apply_dimension_adjustments` and `compute_composite_score`). If the card still fails the drop criteria after scoring, then discard it; otherwise keep it for final ranking.

```python
# Re‑factor _drop_network_cards into a post‑scoring filter
def _drop_network_cards_post_score(scored_articles: List[Article], now: datetime = None) -> List[Article]:
    now = now or datetime.now(timezone.utc)
    local_signals = [s.lower() for s in FILTERS.get('local_signals', [])]
    # Keep only articles that either have a local signal in title/description or are young/unique
    kept = []
    for art in scored_articles:
        text = f"{art.title} {art.description}".lower()
        # Local signal wins – keep regardless of age/duplication
        if any(sig in text for sig in local_signals):
            kept.append(art)
            continue

        # Extract permalink date if present (network cards have a /YYYY/MM/DD/slug/ shape)
        parsed = urlparse(art.link)
        m = _PERMALINK_RE.match(parsed.path)
        if not m:
            # No permalink – assume it’s a network card and drop it
            continue
        year, month, day, slug = map(int, (m.group(1), m.group(2), m.group(3), m.group(4)))
        try:
            age_days = (now - datetime(year, month, day, tzinfo=timezone.utc)).days
        except ValueError:
            age_days = 0
        # Shared slug detection – we need a global map; keep a simple in‑function version for illustration
        # In production this map is built once per run from the scraped list.
        if _SHARED_SLUGS.get(slug, 0) >= 2 or age_days > _SCRAPE_STALE_DAYS:
            # drop
            continue
        kept.append(art)
    return kept

# Usage: after scoring, call _drop_network_cards_post_score(scored_articles)
```

**Finding 5** – *`compute_composite_score` is mis‑implemented – it validates a feed, not scores articles* (blocking)  
- **Location**: The function that currently parses a feed body and returns a boolean (lines 2435‑2442). No attribute `composite_score` is ever added to Article objects.  
- **Problem**: Because the real composite scorer is missing, the final sort uses whatever default ordering exists (or none), breaking the configured Q/R/L weight matrix.  
- **Fix**: Rewrite the function to actually compute a weighted composite score using the configured weights (e.g., `SCORING_WEIGHTS.get('composite', {...})`). Assume Article objects already have `quality_score`, `relevance_score`, `local_score`, `theme_score` fields (or compute them if missing). Add a `composite_score` attribute and return the articles sorted by it.

```python
def compute_composite_score(articles: List[Article]) -> List[Article]:
    """Calculate the weighted composite score for each article.
    Expects the following optional attributes on Article:
      quality_score   – numeric (0‑1)
      relevance_score – numeric (0‑1)
      local_score     – numeric (0‑1)
      theme_score     – numeric (0‑1)
    Falls back to 0 when an attribute is missing.
    """
    # Load weight configuration – fall back to sensible defaults if missing
    w = SCORING_WEIGHTS.get('composite', {
        'quality': 0.4,
        'relevance': 0.4,
        'local': 0.1,
        'theme': 0.1,
    })

    for art in articles:
        q = getattr(art, 'quality_score', 0) or 0
        r = getattr(art, 'relevance_score', 0) or 0
        l = getattr(art, 'local_score', 0) or 0
        t = getattr(art, 'theme_score', 0) or 0

        art.composite_score = (
            q * w['quality'] +
            r * w['relevance'] +
            l * w['local'] +
            t * w['theme']
        )
    # Sort descending – higher composite wins
    articles.sort(key=lambda a: a.composite_score, reverse=True)
    return articles
```

**Finding 6** – *`apply_dimension_adjustments` is actually feed‑rediscovery code, not scoring adjustments* (blocking)  
- **Location**: The block that defines `_fetch_url_bytes`, `_autodiscovery_links`, `_discover_feed_url` (lines 2445‑2502) is misnamed; no L‑bonus, Q‑adjustments or wire‑penalty are applied.  
- **Problem**: Because the real dimensional tuning never runs, later stages (e.g., `_podcast_composite`) operate on raw Article objects, so the configured bonuses/penalties never affect the final ranking.  
- **Fix**: Provide a proper `apply_dimension_adjustments` that modifies the Article’s dimensional scores based on config.

```python
def apply_dimension_adjustments(articles: List[Article]) -> List[Article]:
    """Apply L‑bonus, Q‑adjustments and a wire‑penalty.
    All tuning constants are taken from the SCORING_WEIGHTS dict so they can be
    overridden without touching code.
    """
    cfg = SCORING_WEIGHTS.get('dimension', {})
    # Local‑signal bonus (L‑bonus)
    local_signals = {s.lower() for s in FILTERS.get('local_signals', [])}
    for art in articles:
        text = f"{art.title} {art.description}".lower()
        if any(sig in text for sig in local_signals):
            art.local_score = (getattr(art, 'local_score', 0) or 0) + cfg.get('local_bonus', 0.15)

        # Quality adjustments – richer description → higher quality
        desc_len = len(art.description or '')
        if desc_len > 500:
            art.quality_score = (getattr(art, 'quality_score', 0) or 0) + cfg.get('quality_bonus_long', 0.1)
        elif desc_len < 100:
            art.quality_score = (getattr(art, 'quality_score', 0) or 0) - cfg.get('quality_penalty_short', 0.05)

        # Wire‑penalty – penalise feeds that are extremely high‑volume (e.g., >10k subs)
        if art.feed_volume > cfg.get('high_volume_threshold', 10000):
            art.quality_score = (getattr(art, 'quality_score', 0) or 0) - cfg.get('wire_penalty', 0.2)

    return articles
```

**Finding 7** – *Hard‑coded constants that belong in config* (hard‑code)  
- **Location**: `_SCRAPE_STALE_DAYS = 4`, `_MAX_DISCOVERY_PROBES = 6`, `SELECTOR_PATTERNS` inside `scrape_local_news`. These values are baked into the source and cannot be overridden without a code change.  
- **Problem**: Different deployments may want different stale‑day thresholds, probe limits, or CSS selectors; hard‑coding makes the pipeline inflexible.  
- **Fix**: Move them to a central configuration dict (e.g., `PIPELINE_CONFIG`). Example:

```python
# In the module header or a dedicated config_loader
PIPELINE_CONFIG = {
    'scrape': {
        'stale_days': 4,
        'max_discovery_probes': 6,
        'selector_patterns': [
            ('div.article-card', 'a.article-card__link', 'h3.article-card__headline',
             'div.article-card__details', 'img.article-card__image'),
            # … rest of patterns …
        ],
    },
    # other sections …
}

# Replace uses
_SCRAPE_STALE_DAYS = PIPELINE_CONFIG['scrape']['stale_days']
_MAX_DISCOVERY_PROBES = PIPELINE_CONFIG['scrape']['max_discovery_probes']
SELECTOR_PATTERNS = PIPELINE_CONFIG['scrape']['selector_patterns']
```

All other references to the constants are updated accordingly.

**Finding 8** – *Thin‑day auto‑inflation is not configurable* (latent)  
- **Location**: Inside `score_articles_with_claude` there is logic that fetches an excerpt when `len(description) < 100` and later `_enrich_thin_local_articles`. This is the “thin‑day” behavior that inflates low‑scoring items.  
- **Problem**: The inflation runs unconditionally; there is no flag to turn it off, and it does not respect the same scoring‑floor logic that would otherwise protect low‑scorers.  
- **Fix**: Guard the enrichment behind a config flag and make the threshold configurable.

```python
# At the top of the module (or load via config_loader)
THIN_DAY_CFG = {
    'enabled': True,
    'desc_threshold': 100,
    'max_excerpt_chars': 600,
    'local_enrich_enabled': True,
}

# Inside the article loop (e.g., after building `description`)
if THIN_DAY_CFG['enabled'] and len(description) < THIN_DAY_CFG['desc_threshold']:
    body = _fetch_article_excerpt(full_url, max_chars=THIN_DAY_CFG['max_excerpt_chars'])
    if body:
        description = body

# Later, after all articles are collected
if THIN_DAY_CFG['local_enrich_enabled']:
    _enrich_thin_local_articles(articles)
```

**Finding 9** – *Unclear precedence when a local source also matches a high‑volume prescore gate* (latent)  
- **Location**: The pipeline has a prescore gate (`apply_prescore_filter`) that may admit high‑volume aggregator feeds, and a local‑signal detection (`_drop_network_cards` / `FILTERS['local_signals']`). No explicit rule decides which wins when an article belongs to a local paper **and** also satisfies the prescore gate.  
- **Problem**: The final ranking could be dominated by volume‑based scoring, drowning out local relevance, or vice‑versa, depending on arbitrary ordering.  
- **Fix**: Introduce a deterministic “local‑wins” rule after the composite score is calculated. If an article’s local relevance (e.g., `local_score` > 0 or a local signal is present) **and** its composite score is within a small epsilon of the best score, bump it above non‑local entries.

```python
def apply_local_precedence(scored_articles: List[Article]) -> List[Article]:
    """Give priority to local articles when scores are close."""
    if not scored_articles:
        return []

    # Determine a tolerance – e.g., 1 % of the max composite score
    max_score = max(a.composite_score for a in scored_articles)
    tolerance = max_score * 0.01

    # Separate local vs non‑local
    local = []
    other = []
    for a in scored_articles:
        has_local = any(sig.lower() in f"{a.title} {a.description}".lower()
                        for sig in FILTERS.get('local_signals', []))
        if has_local:
            local.append(a)
        else:
            other.append(a)

    # Keep non‑local list unchanged
    result = other

    # Insert local articles, bumping them ahead of any non‑local article whose score
    # is within tolerance.
    for loc in local:
        insert_pos = len(result)
        for i, oth in enumerate(result):
            if abs(oth.composite_score - loc.composite_score) <= tolerance:
                insert_pos = i
                break
        result.insert(insert_pos, loc)

    return result
```

Then call `apply_local_precedence(compute_composite_score(articles))` before the final output stage.

---

### Scoring & Priority

**Finding 1** – *`compute_composite_score` is mis‑implemented* (blocking) – *see Fix 5 above*.

**Finding 2** – *`apply_dimension_adjustments` is mis‑implemented* (blocking) – *see Fix 6 above*.

**Finding 3** – *Quality and relevance appear collapsed* (latent) – the current implementation does not keep Q and R separate after `apply_dimension_adjustments`. If downstream steps need separate scores, they are lost. The fix above preserves them as independent attributes (`quality_score`, `relevance_score`).

**Finding 4** – *Final sort formula does not match configured weights* (latent) – because the real composite scorer was missing, the pipeline sorted on whatever default ordering existed (often by date or URL hash). The new `compute_composite_score` now reads `SCORING_WEIGHTS['composite']` and respects the configured weights, restoring the intended ranking.

---

### Edge Cases

**Finding 1** – *Hard‑coded constants* (`_SCRAPE_STALE_DAYS`, `_MAX_DISCOVERY_PROBES`, `SELECTOR_PATTERNS`) (hard‑code) – *see Fix 7 above*.

**Finding 2** – *Thin‑day auto‑inflation* (latent) – *see Fix 8 above*.

**Finding 3** – *Local source vs high‑volume prescore gate precedence* (latent) – *see Fix 9 above*.

**Finding 4** – *Fallback fetch bypasses content block filter* (blocking) – *see Fix 2 above*.

**Finding 5** – *Early unconditional drop in `apply_prescore_filter`* (blocking) – *see Fix 3 above*.

**Finding 6** – *Network cards dropped before scoring* (latent) – *see Fix 4 above*.

---

**Summary of Blocking Changes (apply immediately):**

1. Add shared `_apply_content_block_filter` and call it in Article creation (Article.__init__) and all fallback paths.  
2. Replace early `return []` in `apply_prescore_filter` with per‑article aggregator gating.  
3. Rewrite `compute_composite_score` to calculate weighted composite scores.  
4. Rewrite `apply_dimension_adjustments` to apply L‑bonus, Q‑adjustments, and wire‑penalty using config.  
5. Move `_SCRAPE_STALE_DAYS`, `_MAX_DISCOVERY_PROBES`, `SELECTOR_PATTERNS` to `PIPELINE_CONFIG`.  

These changes eliminate contradictory filters, protect score floors from premature drops, align scoring with configuration, and make the pipeline more configurable and maintainable.
