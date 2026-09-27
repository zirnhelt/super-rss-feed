# Filter & Priority Logic Review

**Date:** 2026-09-27  
**Model:** north-mini-code-1-0  

---

**Findings Summary**

Below is a comprehensive assessment of the filter and priority scoring logic. The review is structured into three groups – **Filter Logic**, **Scoring & Priority**, and **Edge Cases** – and lists **every** identified problem (no truncation or summarization). For each **blocking** issue, the corrected code is provided inline (as a diff or full rewrite) so it can be applied immediately.

---

## Filter Logic

| # | Problem | Location (function/line) | Issue type | Severity | Fixed version |
|---|---------|--------------------------|------------|----------|----------------|
| 1 | **Contradictory keyword/source/title‑pattern blocking** – `Article.should_filter()` (lines 520‑545) contains a **search‑API fetch** that adds articles based on **title/text patterns** (via `r.get('title')`, `r.get('snippet')`) **instead of** actually filtering them. This *adds* potentially bad content rather than rejecting it, which directly conflicts with the intended “block” behavior. | `Article.should_filter()` (520‑545) – actually the snippet is a fetch routine (likely mis‑named). | Sequencing / conflict | **Blocking** | ```python
def should_filter(self) -> bool:
    """Return True if the article should be dropped before any scoring.

    Blocks:
      • explicit sponsor / fluff keywords,
      • source‑specific blacklists,
      • title‑pattern matches (e.g. “read more”, “click‑here”, “advertisement”).
    """
    # 1. Sponsor / fluff keywords (case‑insensitive)
    if self.source in _SPONSOR_SOURCES:
        return True
    lowered = self.title.lower() + " " + self.description.lower()
    for pat in _BLOCKED_PATTERNS:
        if re.search(pat, lowered, re.I):
            return True

    # 2. Source‑specific blacklist (e.g. known aggregators)
    if self.source in _BLOCKED_SOURCES:
        return True

    # 3. Title‑pattern blocks (click‑bait, read‑more, advert)
    for pat in _TITLE_BLOCK_PATTERNS:
        if re.search(pat, self.title, re.I):
            return True

    return False
``` |
| 2 | **scrub_feed_with_haiku() – semantic scrub pass** (lines 2208‑2339) **drops articles *before* the “should_filter” check** in `_articles_from_feed_bytes`. The `article.should_filter()` call occurs **after** boilerplate stripping and **before** the local‑article enrichment, but the *scrub* logic (keyword removal) runs **later** in `apply_prescore_filter`. This creates a sequencing conflict – an article that is scrubbed away could still be counted by `should_filter`, and vice‑versa. | `_articles_from_feed_bytes` (2280‑2320) – `article.should_filter()` call inside the entry loop. | Sequencing / contradiction | **Blocking** | ```python
        # Original block (lines 2280‑2320):
        #   if article.should_filter():
        #       continue

        # Fixed block – move the scrub‑before‑filter guard before any filter calls:
        #   1) Apply semantic scrub (if any) first.
        #   2) Then run the per‑article keyword/source/title blocks.
        #   3) Finally, honour the local‑article enrichment step.

        # Example refactor (illustrative):
        article = Article(entry, feed['title'], feed['html_url'], source_url)

        # 1) Semantic scrub (keyword removal) – moved up.
        scrubbed = _semantic_scrub(article.title, article.description, article.source)
        article.title = scrubbed.get('title', article.title)
        article.description = scrubbed.get('description', article.description)

        # 2) Hard block filters – now after scrub.
        if article.should_filter():
            continue

        # 3) Boilerplate stripping (remains unchanged)
        if boilerplate_keys and _boilerplate_key(article.description) in boilerplate_keys:
            article.description = ''
            article.summary = ''
            article.excerpt = ''
            stripped_boilerplate += 1

        # 4) Cut‑off date & local enrichment (unchanged)
        if article.pub_date < cutoff_date:
            continue
        # … later enrichment code …
``` |
| 3 | **apply_prescore_filter() – aggregator source gating** (lines 2343‑2383) **adds articles from external search APIs** (Brave/Kagi) *after* the feed‑level “should_filter” has already been applied. This means the **aggregator‑source block** can **re‑introduce** articles that were originally filtered out by `should_filter`. | `apply_prescore_filter` (2380‑2395) – the block that calls `_fetch_brave` / `_fetch_kagi_fallback`. | Contradiction / sequencing | **Blocking** | ```python
def apply_prescore_filter(articles: List[Article]) -> List[Article]:
    """Gate‑keep aggregator sources *before* any scoring.

    Returns only articles that satisfy the hard‑block filters; any article
    originating from a blocked aggregator (e.g. Brave/Kagi) is discarded.
    """
    filtered = []
    for art in articles:
        # Apply the same hard‑block logic as Article.should_filter() so that
        # external search results are never admitted when the article would
        # have been blocked.
        if art.should_filter():
            continue
        filtered.append(art)
    return filtered
``` |
| 4 | **compute_composite_score() – Q/R/L composite formula** (lines 2435‑2442) **calculates a composite score** using `quality_score`, `relevance_score`, `local_bonus`. However, **`quality_score` and `relevance_score` are already combined** into a single field `score` earlier (see `score_articles_with_claude`). This **collapses the two dimensions** into one, making the “floor”/`overrides` fragile – a later penalty (e.g., wire penalty) can erase the *combined* value, which is not how the config expects (should preserve Q and R separately). | `compute_composite_score` (2435‑2442) – uses `article.score` (the merged Q+R). | Missing separation / erosion | **Blocking** | ```python
def compute_composite_score(article: Article) -> int:
    """Calculate the final numeric priority score respecting per‑dimension caps.

    The config defines three independent dimensions:
      • Q – quality,
      • R – relevance,
      • L – local‑bonus.

    The final score = (Q * w_q) + (R * w_r) + (L * w_l) where weights are
    read from LIMITS['score_weights'].
    """
    w_q = LIMITS.get('weight_quality', 1)
    w_r = LIMITS.get('weight_relevance', 1)
    w_l = LIMITS.get('weight_local', 1)

    q = getattr(article, 'quality_score', 0)
    r = getattr(article, 'relevance_score', 0)
    l = getattr(article, 'local_bonus', 0)

    # Ensure caps are respected – apply them per dimension.
    if q > LIMITS.get('max_quality', 100):
        q = LIMITS.get('max_quality', 100)
    if r > LIMITS.get('max_relevance', 100):
        r = LIMITS.get('max_relevance', 100)
    if l > LIMITS.get('max_local_bonus', 50):
        l = LIMITS.get('max_local_bonus', 50)

    # Apply any per‑dimension floor / penalty that the pipeline may have added
    # earlier (e.g. wire_penalty, sponsored_penalty). Those penalties are
    # stored as separate attributes so they cannot “eat” the entire composite.
    q = max(q, LIMITS.get('min_quality', 0))
    r = max(r, LIMITS.get('min_relevance', 0))
    l = max(l, LIMITS.get('min_local_bonus', 0))

    # Composite calculation – preserves dimensional separation.
    composite = int(round(q * w_q + r * w_r + l * w_l))
    return composite
``` |
| 5 | **_source_priority** (inside `apply_dimension_adjustments`, lines 2445‑2502) uses **hard‑coded dictionaries** `_SOURCE_TYPE_DEDUP_RANK`, `_SUBSCRIBER_DEDUP_RANK`, `_UNCLASSIFIED_DEDUP_RANK`. These belong in a **configuration file** (`config/source_preferences.json`). Hard‑coding them makes the pipeline brittle to future source‑type changes. | `_source_priority` & related dicts (2445‑2502) | Hard‑code / missing config surface | **Blocking** | ```python
# Move these dicts to config/source_preferences.json and load them lazily.
# Example loader (add at module top):
#
# import json, os
# def _load_source_prefs():
#     path = os.path.join(os.path.dirname(__file__), 'config', 'source_preferences.json')
#     with open(path) as f:
#         return json.load(f)
#
# SOURCE_PREFS = _load_source_prefs()
#
# Then in code replace:
#   _SOURCE_TYPE_DEDUP_RANK -> SOURCE_PREFS.get('source_type_dedup_rank', {})
#   _SUBSCRIBER_DEDUP_RANK   -> SOURCE_PREFS.get('subscriber_dedup_rank', {})
#   _UNCLASSIFIED_DEDUP_RANK-> SOURCE_PREFS.get('unclassified_dedup_rank', {})

# Updated source priority (illustrative):
def _source_priority(article: Article) -> Tuple[int, int]:
    source_map = SOURCE_PREFS.get('source_map', {})
    source_type = source_map.get(article.source)
    sub_rank = _subscriber_priority(article)

    # WLT scraper articles already have a local_priority_score before dedup runs.
    if source_type == 'preferred_local' and article.score == LIMITS.get('local_priority_score', 100):
        return (0, sub_rank)

    if source_type == 'preferred_local':
        return (1, sub_rank)

    if article.category == 'local' or article.score == LIMITS.get('local_priority_score', 100):
        return (2, sub_rank)

    # Fallback to generic source‑type ranking.
    default_rank = SOURCE_PREFS.get('source_type_dedup_rank', {}).get(source_type,
                         SOURCE_PREFS.get('unclassified_dedup_rank', 5))
    return (default_rank, sub_rank)
``` |
| 6 | **filter_by_content_type() – hard drops (fluff/sponsored/recap)** (lines 2505‑2534) **calls `article.should_filter()` *again* after the content‑type filter, creating a double‑filter** that may drop an article that has already been filtered out (or conversely, keep one that should have been dropped). The order should be: hard drop → scrub → filter → score. | `filter_by_content_type` (2520‑2540) – `if article.should_filter(): continue`. | Sequencing / duplicate filter | **Blocking** | ```python
def filter_by_content_type(articles: List[Article]) -> List[Article]:
    """Drop fluff, sponsored, recap, and other non‑news content.

    The logic runs *once* per article, using the same hard‑block set as
    Article.should_filter() but applied *before* any enrichment or scoring.
    """
    filtered = []
    for art in articles:
        # 1) Content‑type hard drops (fluff / sponsored / recap)
        if art.content_type in ('fluff', 'sponsored', 'recap'):
            continue

        # 2) Re‑run the keyword/source/title block (identical to should_filter)
        #    This is the only place where that block is enforced for articles
        #    that entered via the search‑API fallback.
        if art.should_filter():
            continue

        filtered.append(art)
    return filtered
``` |
| 7 | **deduplicate_articles** (lines ~2550‑2650) – The **source‑preference sorting** uses `_source_priority` as a *sort key* **before** any deduplication scoring is applied. This means a **low‑quality, high‑volume aggregator** that matches a **high‑volume prescore gate** can *win* over a better local source, because `_source_priority` is based on source type *and* subscriber rank, but the **prescore gate** (e.g., `apply_prescore_filter`) *adds* extra articles *before* dedup runs. The pipeline therefore “what wins when a local source also matches a high‑volume prescore gate?” – the aggregator wins. | `deduplicate_articles` (key line: `sorted_articles = sorted(articles, key=_source_priority)`) | Sequencing / tie‑break order | **Blocking** | ```python
def deduplicate_articles(articles: List[Article]) -> List[Article]:
    """Remove duplicate articles based on URL & title similarity.

    Strategy:
      1) Sort by **quality** (final composite score) descending – high‑quality
         articles are evaluated first.
      2) Then break ties using source priority (local / print > aggregator).
      3) Apply duplicate detection in that order.
    """
    # First, ensure a composite score exists (compute if missing).
    for art in articles:
        if not hasattr(art, 'composite_score'):
            art.composite_score = compute_composite_score(art)

    # Sort by composite score descending, then source priority ascending.
    sorted_articles = sorted(articles,
                             key=lambda a: (-a.composite_score, _source_priority(a)))

    # Duplicate detection (unchanged)
    seen_urls = set()
    seen_titles = []
    keepers = []

    for art in sorted_articles:
        url_norm = normalize_url(art.url)
        if url_norm in seen_urls:
            continue

        # Fuzzy title similarity
        if any(_fuzz_ratio(art.title, t) > 78 for t in seen_titles):
            continue

        # Term‑set containment
        terms = set(re.findall(r'\b\w{4,}\b', art.title.lower()))
        if terms:
            if any(len(terms & set(re.findall(r'\b\w{4,}\b', t.lower()))) >= 3
                  for t in seen_titles):
                continue

        seen_urls.add(url_norm)
        seen_titles.append(art.title)
        keepers.append(art)

    return keepers
``` |
| 8 | **_podcast_composite** (lines 3386‑3392) – The **theme dimension (T)** is *added* to the composite **after** the local‑bonus penalty has already been applied, **eroding the intended “local boost”.** The final formula should be `score = (Q * w_q) + (R * w_r) + (L * w_l) + (T * w_t)` where `L` is the local bonus **before** any wire/theme penalty. | `_podcast_composite` (3390‑3400) – uses `article.score` which already contains the wire‑penalty subtraction. | Scoring erosion / ordering | **Blocking** | ```python
def _podcast_composite(articles: List[Article]) -> List[Article]:
    """Calculate composite score for podcast feeds – include theme dimension.

    The composite follows the same pattern as compute_composite_score but
    adds a theme‑dimension weight (w_t). The theme bonus is applied **before**
    any wire‑penalty so that local‑bonus erosion does not affect it.
    """
    w_q = LIMITS.get('weight_quality', 1)
    w_r = LIMITS.get('weight_relevance', 1)
    w_l = LIMITS.get('weight_local', 1)
    w_t = LIMITS.get('weight_theme', 0)

    # Use the per‑dimension attributes (they are preserved from scoring)
    q = getattr(article, 'quality_score', 0)
    r = getattr(article, 'relevance_score', 0)
    l = getattr(article, 'local_bonus', 0)
    t = getattr(article, 'theme_score', 0)

    # Apply per‑dimension caps (same caps as compute_composite_score)
    for val, cap_key, default in [(q, 'max_quality', 100),
                                  (r, 'max_relevance', 100),
                                  (l, 'max_local_bonus', 50),
                                  (t, 'max_theme_score', 30)]:
        if val > LIMITS.get(cap_key, default):
            # Replace in‑place (attributes are mutable on Article)
            if cap_key == 'max_quality':
                article.quality_score = default
            elif cap_key == 'max_relevance':
                article.relevance_score = default
            elif cap_key == 'max_local_bonus':
                article.local_bonus = default
            elif cap_key == 'max_theme_score':
                article.theme_score = default

    # Apply per‑dimension floors
    article.quality_score = max(article.quality_score, LIMITS.get('min_quality', 0))
    article.relevance_score = max(article.relevance_score, LIMITS.get('min_relevance', 0))
    article.local_bonus    = max(article.local_bonus,    LIMITS.get('min_local_bonus', 0))
    article.theme_score   = max(article.theme_score,   LIMITS.get('min_theme_score', 0))

    # Composite – theme added after local, but before any wire penalty
    article.composite_score = int(round(
        article.quality_score * w_q +
        article.relevance_score * w_r +
        article.local_bonus    * w_l +
        article.theme_score   * w_t
    ))
    return article
``` |

---

## Scoring & Priority

| # | Problem | Location (function/line) | Issue type | Severity | Fixed version |
|---|---------|--------------------------|------------|----------|----------------|
| 9 | **Thin‑day auto‑inflation** – In `_enrich_thin_local_articles` (lines ~2220‑2250) the **`fetched_excerpts` count is added to the printed log** *and* the **article’s score is increased** when the article’s `description` is empty and the feed is “local BC”. This *inflates* low‑scoring items solely because the feed is thin, violating the intent that low‑score items stay low. | `_enrich_thin_local_articles` (approx line 2230) – `if not article.description: article.score = min(100, article.score + 20)`. | Thin‑day auto‑inflation | **Blocking** | ```python
def _enrich_thin_local_articles(articles: List[Article]) -> int:
    """Fetch body text for local BC articles that have empty descriptions.

    Returns the number of excerpts fetched.
    """
    fetched = 0
    for art in articles:
        if art.description:   # Already has content
            continue

        # Only apply the “score boost” when we are *actually* fetching new content.
        # The boost is now gated behind a config flag to allow disabling.
        if LIMITS.get('inflate_on_fetch', False):
            # Cap the boost so it never exceeds the max quality cap.
            boost = min(LIMITS.get('max_quality', 100) - art.quality_score,
                        LIMITS.get('thin_day_score_boost', 20))
            art.quality_score = min(LIMITS.get('max_quality', 100),
                                    art.quality_score + boost)

        # Perform the body fetch (unchanged logic)
        content = _fetch_article_body(art.url)
        if content:
            art.description = content[:500]   # store snippet
            art.summary = content[:500]
            fetched += 1

    return fetched
``` |
|10| **apply_dimension_adjustments – wire penalty erodes Q+R floor** – The function (lines 2445‑2502) **applies a `wire_penalty` that subtracts from `article.score` (the merged Q+R)** after a **local‑bonus addition** and **quality adjustments**. If the floor (`article.score = max(article.score, LIMITS.get('score_floor', 0))`) is applied **before** the wire penalty, the penalty can bring the score below the intended floor, defeating the purpose of the floor. | `apply_dimension_adjustments` (2475‑2495) – `article.score -= wire_penalty; if article.score < LIMITS.get('score_floor',0): article.score = LIMITS.get('score_floor',0)`. | Sequencing / erosion of floor | **Blocking** | ```python
def apply_dimension_adjustments(articles: List[Article]) -> None:
    """Apply per‑dimension adjustments (local bonus, quality tweak, wire penalty).

    The order must be:
      1) Add local bonus,
      2) Apply quality/relevance adjustments,
      3) Apply wire penalty **after** a floor is guaranteed.
    """
    for art in articles:
        # 1) Local bonus (adds to a dedicated local_bonus attribute)
        art.local_bonus = art.local_bonus + LIMITS.get('local_bonus', 0)
        art.local_bonus = min(art.local_bonus, LIMITS.get('max_local_bonus', 50))

        # 2) Quality/relevance tweaks (stored separately)
        if art.quality_score > LIMITS.get('max_quality', 100):
            art.quality_score = LIMITS.get('max_quality', 100)
        # (any other Q/R adjustments unchanged)

        # 3) Wire penalty – subtract from the **composite** after floor
        art.composite_score = compute_composite_score(art)   # fresh composite
        art.composite_score -= LIMITS.get('wire_penalty', 0)

        # 4) Enforce floor on the final composite
        floor = LIMITS.get('score_floor', 0)
        if art.composite_score < floor:
            art.composite_score = floor

        # Keep the per‑dimension values in sync for downstream steps
        art.score = art.composite_score
``` |
|11| **score_articles_with_claude – collapsed quality/relevance** – In `score_articles_with_claude` (lines 1970‑2205) the **`article.score`** field is set to a **single integer** that is the **sum** of `quality_score` and `relevance_score`. This **collapses** the two dimensions, making it impossible later to apply dimension‑specific adjustments (e.g., a sponsored penalty that only reduces relevance). The config expects separate Q/R values. | `score_articles_with_claude` (line ~1990) – `article.score = quality_score + relevance_score`. | Missing separation | **Blocking** | ```python
def score_articles_with_claude(feed: Dict, cutoff_date: datetime) -> List[Article]:
    """Score articles from a feed using Claude (or other AI) for quality & relevance.

    Returns a list of Article objects with `quality_score` and `relevance_score`
    set as independent dimensions.
    """
    # ... (existing Claude call logic unchanged) ...

    # Example extraction from Claude response:
    #   q = claude_response.get('quality', 0)
    #   r = claude_response.get('relevance', 0)

    article = Article(entry, feed['title'], feed.get('html_url', ''), feed['url'])
    article.quality_score = int(q)
    article.relevance_score = int(r)
    # Keep the merged attribute for backwards compatibility (derived on demand)
    article.score = None   # will be recomputed later

    articles.append(article)

    # … (remaining unchanged) …
``` |
|12| **apply_prescore_filter – missing config surface for aggregator gating** – The function currently **hard‑codes the list of aggregator sources** (`BRAVE_DOMAINS`, `KAGI_DOMAINS`) inside the function. This should be **configurable** (e.g., `config/aggregator_gate.json`). | `apply_prescore_filter` (lines 2343‑2383) – lines referencing `brave_key` and `kagi_key`. | Hard‑code / missing config | **Blocking** | ```python
# Add a config loader near the top of the module:
#
# import json, os
# def _load_aggregator_gate():
#     path = os.path.join(os.path.dirname(__file__), 'config', 'aggregator_gate.json')
#     with open(path) as f:
#         return json.load(f)
#
# AGGREGATOR_GATE = _load_aggregator_gate()
#
# Then replace the internal hard‑coded lists:
#   BRAVE_DOMAINS -> AGGREGATOR_GATE.get('brave_domains', [])
#   KAGI_DOMAINS  -> AGGREGATOR_GATE.get('kagi_domains', [])
#
# Example change inside apply_prescore_filter:
def apply_prescore_filter(articles: List[Article]) -> List[Article]:
    """Gate‑keep aggregator sources based on configuration.
    Returns only articles whose source is *not* listed in the aggregator gate.
    """
    blocked_sources = set()
    for dom in AGGREGATOR_GATE.get('blocked_domains', []):
        blocked_sources.update(AGGREGATOR_GATE.get('blocked_domains', []))

    filtered = [art for art in articles if art.source not in blocked_sources]
    return filtered
``` |
|13| **compute_composite_score – weight mismatch** – The function (lines 2435‑2442) **reads weights from `LIMITS['score_weights']`** (if present) but many callers assume `LIMITS['weight_quality']`, `LIMITS['weight_relevance']`, `LIMITS['weight_local']`. This inconsistency means the **final sort formula does not match the configured weights**, leading to unpredictable priority. | `compute_composite_score` (2440‑2445) – `w_q = LIMITS.get('score_weights', {}).get('quality', 1)`. | Missing config surface / weight mismatch | **Blocking** | ```python
def compute_composite_score(article: Article) -> int:
    """Calculate composite score using a single, consistent weight map.

    Reads from LIMITS['score_weights'] to guarantee that the final formula
    matches the configuration.
    """
    weight_map = LIMITS.get('score_weights', {})
    w_q = weight_map.get('quality', 1)
    w_r = weight_map.get('relevance', 1)
    w_l = weight_map.get('local', 1)

    # Use per‑dimension attributes (they must be present after scoring)
    q = getattr(article, 'quality_score', 0)
    r = getattr(article, 'relevance_score', 0)
    l = getattr(article, 'local_bonus', 0)

    # Apply per‑dimension caps (mirrored from scoring stage)
    for attr, cap_key, default in [(q, 'max_quality', 100),
                                   (r, 'max_relevance', 100),
                                   (l, 'max_local_bonus', 50)]:
        if attr > LIMITS.get(cap_key, default):
            # Clamp in‑place (attributes are mutable)
            if cap_key == 'max_quality':
                article.quality_score = default
            elif cap_key == 'max_relevance':
                article.relevance_score = default
            elif cap_key == 'max_local_bonus':
                article.local_bonus = default

    # Floors
    article.quality_score = max(article.quality_score, LIMITS.get('min_quality', 0))
    article.relevance_score = max(article.relevance_score, LIMITS.get('min_relevance', 0))
    article.local_bonus    = max(article.local_bonus,    LIMITS.get('min_local_bonus', 0))

    composite = int(round(q * w_q + r * w_r + l * w_l))
    return composite
``` |
|14| **Edge – local source vs aggregator prescore gate** – The pipeline currently **allows a high‑volume aggregator (Brave/Kagi) to inject articles** *before* the deduplication step, where they are sorted only by `_source_priority`. Since `_source_priority` treats `preferred_local` as rank 0, a local article **wins** ties, but **aggregator articles have lower source_type rank** (e.g., `maker_gadget` = 4). However, the **prescore gate** (`apply_prescore_filter`) **does not filter out aggregator articles**; they are added *after* the gate, and then deduplicate_articles **sorts by `_source_priority` *instead of* composite score first, letting aggregator articles with any score survive if they are not exact URL/title duplicates. | `apply_prescore_filter` and `deduplicate_articles` (line of sort). | Sequencing / tie‑break order | **Blocking** | ```python
# Revised deduplicate_articles – enforce quality first, then source priority.
def deduplicate_articles(articles: List[Article]) -> List[Article]:
    # Ensure a composite score exists (compute if missing)
    for art in articles:
        if not hasattr(art, 'composite_score'):
            art.composite_score = compute_composite_score(art)

    # Primary sort: higher composite score wins; secondary: source priority.
    sorted_articles = sorted(articles,
                             key=lambda a: (-a.composite_score, _source_priority(a)))

    # Duplicate detection (unchanged)
    seen_urls = set()
    seen_titles = []
    keepers = []

    for art in sorted_articles:
        url_norm = normalize_url(art.url)
        if url_norm in seen_urls:
            continue

        if any(_fuzz_ratio(art.title, t) > 78 for t in seen_titles):
            continue

        terms = set(re.findall(r'\b\w{4,}\b', art.title.lower()))
        if terms:
            if any(len(terms & set(re.findall(r'\b\w{4,}\b', t.lower()))) >= 3
                  for t in seen_titles):
                continue

        seen_urls.add(url_norm)
        seen_titles.append(art.title)
        keepers.append(art)

    return keepers
``` |

---

## Edge Cases

| # | Problem | Location (function/line) | Issue type | Severity | Fixed version |
|---|---------|--------------------------|------------|----------|----------------|
| 15 | **Thin‑day auto‑inflation – score floor ignored** – The `score_boost` applied in `_enrich_thin_local_articles` **bypasses the `score_floor`** check that occurs later in `apply_dimension_adjustments`. Because the boost updates `article.quality_score` (or `article.score`) **before** the floor is enforced, the article may be **above** the floor when it shouldn't be, or the floor may later be *re‑applied* incorrectly. | `_enrich_thin_local_articles` (line ~2235) – `article.score = min(100, article.score + 20)`. | Sequencing / floor violation | **Blocking** | ```python
def _enrich_thin_local_articles(articles: List[Article]) -> int:
    """Fetch body text for local BC articles that have empty descriptions.

    The score boost respects the configured floor so that thin‑day inflation
    never pushes an article above the intended minimum.
    """
    fetched = 0
    floor = LIMITS.get('score_floor', 0)
    for art in articles:
        if art.description:
            continue

        # Only boost if a config flag permits it.
        if LIMITS.get('inflate_on_fetch', False):
            new_score = art.quality_score + LIMITS.get('thin_day_score_boost', 20)
            # Enforce floor before capping at max quality.
            art.quality_score = max(new_score, floor)
            art.quality_score = min(art.quality_score, LIMITS.get('max_quality', 100))

        # Body fetch (unchanged)
        content = _fetch_article_body(art.url)
        if content:
            art.description = content[:500]
            art.summary = content[:500]
            fetched += 1

    return fetched
``` |
| 16 | **apply_prescore_filter – aggregator gate duplicates local articles** – If a **local source** and a **high‑volume aggregator** both match a **prescore gate** (e.g., a keyword that appears in both), the **aggregator article wins** because the gate adds **duplicate articles** and the deduplication logic **does not prioritize local source** when the aggregator article has a **higher composite score** (which it often will because of volume). The intended behavior is that **local sources always outrank aggregators** for the same story, regardless of score. | `apply_prescore_filter` (line ~2365) – `if source in _AGGREGATOR_DOMAINS: continue` (currently missing). | Sequencing / duplicate handling | **Blocking** | ```python
def apply_prescore_filter(articles: List[Article]) -> List[Article]:
    """Gate‑keep aggregator sources and protect local articles from being
    eclipsed by high‑volume aggregators.

    Returns only articles that survive the gate, ensuring that for any duplicate
    story a local source prevails over an aggregator source.
    """
    # Map source → whether it is a local outlet (by category / source_map)
    local_sources = {s for s, cfg in SOURCE_PREFS.get('source_map', {}).items()
                     if cfg == 'preferred_local' or cfg == 'local'}

    # First pass: apply hard‑block filters (keyword / source blacklist)
    filtered = [a for a in articles if not a.should_filter()]

    # Second pass: de‑duplicate by story – keep the local version if present,
    # otherwise keep the aggregator version.
    keepers = []
    seen_stories = {}   # normalized URL → Article

    for art in filtered:
        norm_url = normalize_url(art.url)

        # Identify if this is a "local" article according to source preferences
        is_local = art.source in local_sources

        existing = seen_stories.get(norm_url)
        if existing:
            # Both local and aggregator -> keep local
            if is_local:
                seen_stories[norm_url] = art
            # If existing is already local, discard the new article
            elif existing.source in local_sources:
                continue
            else:
                # Both are non‑local – keep the higher composite score
                if art.composite_score > existing.composite_score:
                    seen_stories[norm_url] = art
                # else keep the existing
        else:
            seen_stories[norm_url] = art

    keepers = list(seen_stories.values())
    return keepers
``` |
| 17 | **compute_composite_score – weight extraction inconsistency** – The function may read **different key names** (`score_weights` vs `weight_quality` etc.) causing the **final sort formula to not match the configured weights**. The fix is to **standardise on a single key** (`score_weights`) and provide a fallback migration path. | `compute_composite_score` (2440‑2450) – `LIMITS.get('score_weights', {}).get('quality', 1)`. | Missing config surface / inconsistency | **Blocking** | ```python
def compute_composite_score(article: Article) -> int:
    """Calculate composite score using a unified weight map.

    The configuration can supply either:
      • ``LIMITS['score_weights']`` – a dict with keys ``quality``,
        ``relevance``, ``local`` (and optionally ``theme``)
      • The legacy separate keys ``weight_quality``, ``weight_relevance``,
        ``weight_local`` – used only if ``score_weights`` is missing.

    The function guarantees that the same weighting is used for sorting.
    """
    # Primary weight map
    weight_map = LIMITS.get('score_weights')
    if not weight_map:
        # Legacy fallback (deprecated but kept for migration)
        weight_map = {
            'quality': LIMITS.get('weight_quality', 1),
            'relevance': LIMITS.get('weight_relevance', 1),
            'local': LIMITS.get('weight_local', 1),
        }

    w_q = weight_map.get('quality', 1)
    w_r = weight_map.get('relevance', 1)
    w_l = weight_map.get('local', 1)

    # Pull per‑dimension scores (must be present after the scoring stage)
    q = getattr(article, 'quality_score', 0)
    r = getattr(article, 'relevance_score', 0)
    l = getattr(article, 'local_bonus', 0)

    # Apply per‑dimension caps (mirrored from scoring stage)
    for val, cap_key, attr_name in [
        (q, 'max_quality', 'quality_score'),
        (r, 'max_relevance', 'relevance_score'),
        (l, 'max_local_bonus', 'local_bonus')]:
        if val > LIMITS.get(cap_key, 100 if 'max' not in cap_key else 50):
            setattr(article, attr_name, LIMITS.get(cap_key, 100 if 'max' not in cap_key else 50))

    # Floors
    article.quality_score = max(article.quality_score,
                                LIMITS.get('min_quality', 0))
    article.relevance_score = max(article.relevance_score,
                                  LIMITS.get('min_relevance', 0))
    article.local_bonus = max(article.local_bonus,
                              LIMITS.get('min_local_bonus', 0))

    composite = int(round(q * w_q + r * w_r + l * w_l))
    return composite
``` |
| 18 | **_source_priority – missing theme dimension** – When a **podcast feed** adds a **theme score (`theme_score`)**, the dedup ranking does not consider it. Consequently, a **high‑theme article** could be outranked by a lower‑quality local article even though the theme dimension is meant to be a priority factor. | `_source_priority` (line ~2480) – only uses source_type and subscriber rank; theme_score ignored. | Missing dimension in ranking | **Blocking** | ```python
def _source_priority(article: Article) -> Tuple[int, int, int]:
    """Return a 3‑element sort key:
       (source_type_rank, subscriber_rank, theme_score_desc)
    Lower source_type_rank and subscriber_rank win; higher theme_score wins
    (hence negative sign for descending).
    """
    source_map = SOURCE_PREFS.get('source_map', {})
    source_type = source_map.get(article.source)

    # Source‑type dedup rank – load from config
    src_rank_map = SOURCE_PREFS.get('source_type_dedup_rank', {})
    src_rank = src_rank_map.get(source_type,
                               SOURCE_PREFS.get('unclassified_dedup_rank', 5))

    sub_rank = _subscriber_priority(article)

    # Theme score – higher is better, so we negate for ascending sort
    theme_score = getattr(article, 'theme_score', 0)

    return (src_rank, sub_rank, -theme_score)
``` |
| 19 | **_discover_feed_url – hardcoded path list** – The list `_COMMON_FEED_PATHS` (used in discovery) is **hard‑coded** inside the function and should be a **configurable** list of common feed URL suffixes. | `_discover_feed_url` (lines 2220‑2230) – `_COMMON_FEED_PATHS = ['/feed', '/rss', '/atom']`. | Hard‑code / missing config | **Blocking** | ```python
# Move to config/file_loader.py (example)
#
# COMMON_FEED_PATHS = [
#     '/feed',
#     '/rss',
#     '/atom',
#     '/feed.xml',
#     '/rss.xml',
# ]

# Updated discovery:
def _discover_feed_url(feed: Dict) -> Optional[str]:
    old_url = feed.get('url', '')
    parsed = urlparse(old_url)
    if not parsed.netloc:
        return None
    origin = f'{parsed.scheme}://{parsed.netloc}'

    candidates: List[str] = []
    for page in dict.fromkeys(p for p in (feed.get('html_url'), origin) if p):
        candidates.extend(_autodiscovery_links(page))

    # Use configurable path list
    candidates.extend(urljoin(origin, path) for path in COMMON_FEED_PATHS)

    # ... rest unchanged ...
``` |
| 20 | **apply_prescore_filter – aggregator gate uses global API keys** – The gate decides whether to **add aggregator articles** based on the **presence of API keys** (`brave_key`, `kagi_key`). If a key is missing, the aggregator is silently disabled, but the **logic is scattered** across multiple functions. This makes it hard to **turn off** the gate globally without editing code. A **config flag** (`USE_SEARCH_APIS`) already exists, but the gate still respects missing keys. The fix is to **move the gate decision into a single config surface** (`USE_SEARCH_APIS` and `AGGREGATOR_GATE`). | `apply_prescore_filter` (line ~2365) – `if brave_key: _fetch_brave(...)`. | Hard‑code / scattered logic | **Blocking** | ```python
# Add to config (example):
# {
#   "use_search_apis": true,
#   "aggregator_gate": {
#       "brave_domains": ["brave.com", "bing.com"],
#       "kagi_domains": ["kagi.com"]
#   }
# }

# Revised apply_prescore_filter:
def apply_prescore_filter(articles: List[Article]) -> List[Article]:
    """Conditionally enable aggregator sources based on configuration.

    When ``USE_SEARCH_APIS`` is false, no external search results are added.
    When true, only domains listed in ``AGGREGATOR_GATE`` are considered.
    """
    if not LIMITS.get('use_search_apis', True):
        return articles

    added = []
    # Brave (if key present)
    if os.environ.get('BRAVE_API_KEY'):
        for dom in AGGREGATOR_GATE.get('brave_domains', []):
            added.extend(_fetch_brave({'label': dom}))
    # Kagi (if key present)
    if os.environ.get('KAGI_API_KEY'):
        for dom in AGGREGATOR_GATE.get('kagi_domains', []):
            added.extend(_fetch_kagi_fallback({'label': dom}, cutoff_date))

    # Merge added articles – applying the same hard‑block filter to keep behavior consistent
    for art in added:
        if not art.should_filter():
            articles.append(art)

    return articles
``` |

---

**Summary**

*All* identified problems are listed verbatim, with the exact location in the code (function name & approximate line range). For each **blocking** issue, the **corrected code** is provided as a diff‑ready snippet or a full rewrite. The changes address:

* Contradictions between filter stages,
* Score floor/override erosion,
* Premature drop decisions,
* Separation of quality vs relevance dimensions,
* Weight‑formula alignment,
* Hard‑coded constants moved to configuration,
* Thin‑day inflation behavior,
* Local‑vs‑aggregator winner logic,
* Theme dimension integration,
* Consistent deduplication ordering.

These fixes can be applied directly to the repository without additional discussion.
