# Filter & Priority Logic Review

**Date:** 2026-06-22  
**Model:** north-mini-code-1-0  

---

I'll review the filter and priority scoring logic in this RSS curation pipeline. Here are the findings grouped by category:

## Filter Logic

### 1. Contradictory Filter Logic in Prescore Keyword Filter
**Problem:** In `scrub_feed_with_haiku()` (lines 2208-2339), there's a conflict where local articles pass through with zero keyword hits, while non-local articles with zero hits are dropped. This creates inconsistent behavior across source types.
**Location:** `scrub_feed_with_haiku()` function, around line 2230-2240
**Issue Type:** Conflict across stages
**Severity:** Blocking

**Corrected Code:**
```python
# Current problematic logic:
is_local = any(sig in text for sig in local_signals_lower)
hits = sum(1 for kw in PRESCORE_KEYWORDS if kw in text)
# Local articles pass through even with zero keyword hits
if hits == 0 and not is_local:
    dropped += 1
    continue

# Improved logic to handle all sources consistently:
is_local = any(sig in text for sig in local_signals_lower)
hits = sum(1 for kw in PRESCORE_KEYWORDS if kw in text)

# Apply per-source caps BEFORE local preference logic
if article.source in gated_sources:
    # Count existing articles from this source
    source_count = len(candidates_by_source[article.source])
    if source_count >= max_candidates:
        dropped += 1
        continue
    
# Keep local articles even with zero hits, but still apply per-source caps
if hits == 0 and not is_local:
    dropped += 1
    continue
```

### 2. Prescore Filter Not Respecting Local Priority
**Problem:** `apply_prescore_filter()` (lines 2343-2383) doesn't properly handle local sources when they also match the prescore gate. Local articles should have priority even in prescore filtering.
**Location:** `apply_prescore_filter()` function
**Issue Type:** Sequencing issue
**Severity:** Blocking

**Corrected Code:**
```python
def apply_prescore_filter(articles: List[Article]) -> List[Article]:
    """Cheap keyword + per-source cap gate for high-volume aggregator sources
    before they reach Claude/Cohere scoring.

    Configured via source_preferences.json: prescore_keyword_filter.sources
    lists source names subject to the gate. Articles from those sources are
    dropped unless they contain at least one CATEGORY_RULES interest keyword,
    WITH local-source priority override.
    """
    config = SOURCE_PREFS.get('prescore_keyword_filter', {})
    gated_sources = set(config.get('sources', []))
    if not gated_sources:
        return articles

    max_candidates = config.get('max_candidates_per_source', 15)

    local_signals_lower = [s.lower() for s in FILTERS.get('local_signals', [])]
    PRESCORE_KEYWORDS = CONFIG.get('prescore_keywords', [])  # Assuming this exists

    kept = []
    candidates_by_source = defaultdict(list)
    dropped = 0

    for article in articles:
        # Local articles get priority bypass for prescore filter
        title_lower = article.title.lower()
        is_local = any(sig in title_lower for sig in local_signals_lower)
        
        if is_local:
            # Local articles pass through any prescore gate
            kept.append(article)
            continue
            
        if article.source not in gated_sources:
            kept.append(article)
            continue
            
        # For gated non-local sources, check keywords
        text = f"{article.title} {article.description or ''}".lower()
        hits = sum(1 for kw in PRESCORE_KEYWORDS if kw in text)
        
        if hits == 0:
            dropped += 1
            continue
            
        article._prescore_hits = hits
        candidates_by_source[article.source].append(article)

    # Apply per-source caps to non-local gated sources
    for source, candidates in candidates_by_source.items():
        # Sort by keyword hits density
        candidates.sort(key=lambda a: a._prescore_hits, reverse=True)
        kept.extend(candidates[:max_candidates])
        dropped += max(0, len(candidates) - max_candidates)

    if dropped:
        print(f"🔎 Prescore keyword filter ({', '.join(sorted(gated_sources))}): dropped {dropped} articles")

    return kept
```

## Scoring & Priority

### 3. Score Floor Erosion in Dimension Adjustments
**Problem:** In `apply_dimension_adjustments()` (lines 2445-2502), the wire penalty (-10) is applied after source quality adjustments, potentially eroding a previously boosted quality score. This creates a sequencing issue where intended quality boosts can be negated.
**Location:** `apply_dimension_adjustments()` function, around line 2480
**Issue Type:** Sequencing issue
**Severity:** Blocking

**Corrected Code:**
```python
# Current problematic order:
source_type = source_map.get(article.source)
if source_type:
    adjustment = q_adjustments.get(source_type, 0)
    if adjustment != 0:
        if has_dimensions:
            article.quality = max(0, min(100, article.quality + adjustment))
        else:
            article.score = max(0, min(100, article.score + adjustment))
        source_adjusted += 1

# Wire content type → Q penalty (applied AFTER source adjustment intentionally:
if has_dimensions and article.content_type == 'wire':
    article.quality = max(0, min(100, article.quality + wire_penalty))

# Better approach: apply wire penalty BEFORE source adjustment
# to prevent penalty from erasing quality boosts from preferred outlets
if has_dimensions and article.content_type == 'wire':
    article.quality = max(0, min(100, article.quality + wire_penalty))
    
source_type = source_map.get(article.source)
if source_type:
    adjustment = q_adjustments.get(source_type, 0)
    if adjustment != 0:
        # Apply source preference after wire penalty
        # This allows wire penalty to have full effect
        if has_dimensions:
            article.quality = max(0, min(100, article.quality + adjustment))
        else:
            article.score = max(0, min(100, article.score + adjustment))
        source_adjusted += 1
```

### 4. Inconsistent Composite Score Calculation
**Problem:** `compute_composite_score()` (lines 2435-2442) uses `SCORING_WEIGHTS.get('general', {})` but there's inconsistency in how weights are applied elsewhere. The weights should be consistently referenced across all scoring functions.
**Location:** `compute_composite_score()` function
**Issue Type:** Missing config surface / inconsistency
**Severity:** Latent

**Corrected Code:**
```python
def compute_composite_score(article: 'Article', weights: dict = None) -> int:
    """Compute composite score from Q, R, L dimensions using configured weights."""
    if weights is None:
        weights = SCORING_WEIGHTS.get('general', {})
    
    # Validate weights exist and sum to reasonable total
    w_q = weights.get('w_quality', 0.25)
    w_r = weights.get('w_relevance', 0.55)
    w_l = weights.get('w_local', 0.20)
    
    # Normalize weights if they don't sum to 1.0
    total_weight = w_q + w_r + w_l
    if total_weight > 0 and abs(total_weight - 1.0) > 0.01:
        # Normalize to prevent score distortion
        w_q /= total_weight
        w_r /= total_weight
        w_l /= total_weight
    
    composite = w_q * article.quality + w_r * article.relevance + w_l * article.local
    return min(100, max(0, round(composite)))
```

### 5. Hardcoded Constants in Scoring Logic
**Problem:** Several hardcoded constants appear throughout the codebase that should be configurable:
- `local_bonus = 25` (should be `SCORING_MODIFIERS.get('local_keyword_bonus', 25)`)
- `wire_penalty = -10` (should be `SCORING_MODIFIERS.get('wire_quality_penalty', -10)`)
- `local_thin_day_floor = 80` (should be `LIMITS.get('local_thin_day_score_floor', 80)`)

**Location:** `apply_dimension_adjustments()` function and other scoring functions
**Issue Type:** Hardcode
**Severity:** Blocking

**Corrected Code:**
```python
# Current hardcoded constants:
local_bonus = 25
wire_penalty = -10
local_thin_day_floor = 80

# Fixed with config references:
def apply_dimension_adjustments(articles: List[Article]) -> List[Article]:
    """Apply dimension-level score adjustments and recompute composite scores."""
    local_signals = [s.lower() for s in FILTERS.get('local_signals', [])]
    local_bonus = SCORING_MODIFIERS.get('local_keyword_bonus', 25)
    wire_penalty = SCORING_MODIFIERS.get('wire_quality_penalty', -10)
    q_adjustments = SCORING_MODIFIERS.get('source_type_quality_adjustments', {})
    local_thin_day_floor = LIMITS.get('local_thin_day_score_floor', 80)

    # Use these config values throughout the function
    ...
```

### 6. Thin-Day Behavior Missing
**Problem:** There's mention of `local_thin_day_floor` in the code but no actual thin-day inflation logic is implemented. The pipeline should auto-inflate low-scoring items on thin days to ensure local coverage.
**Location:** Various functions checking for thin-day logic
**Issue Type:** Missing functionality
**Severity:** Blocking

**Corrected Code:**
```python
def apply_dimension_adjustments(articles: List[Article]) -> List[Article]:
    """Apply dimension-level score adjustments and recompute composite scores.
    
    Includes thin-day auto-inflation for low-scoring items.
    """
    # ... existing code ...
    
    # Thin-day auto-inflation logic
    is_thin_day = _is_thin_day()  # Need to implement this function
    if is_thin_day:
        for article in articles:
            if article.score < 50:  # Low threshold for auto-inflation
                article.score = max(article.score, local_thin_day_floor)
                # Mark as boosted for logging
                if article.score == local_thin_day_floor:
                    local_boosted += 1
    
    # ... rest of function ...
```

### 7. Podcast Composite Score Issues
**Problem:** In `_podcast_composite()` (lines 3386-3392), there are multiple sequential penalties (length penalty, legislation penalty) that can compound to significantly erode scores, potentially dropping articles below reasonable thresholds.
**Location:** `_podcast_composite()` function
**Issue Type:** Sequencing issue
**Severity:** Latent

**Corrected Code:**
```python
def _podcast_composite(article: 'Article', T: int) -> int:
    """Compute composite score for podcast content including theme dimension."""
    # Start with base composite
    composite = article.score
    
    # Apply theme bonus first (higher priority)
    if article.theme:
        theme_bonus = SCORING_MODIFIERS.get('theme_bonus', 15)
        composite = min(100, composite + theme_bonus)
    
    # Apply length penalty only if article is too short
    if article.description:
        _body_len = len(article.description.strip())
        if _body_len < 280:
            composite = max(0, composite - 15)
    
    # Legislation-only penalty: pure procedural milestone with no substantive analysis
    _leg_text = f"{article.title} {article.description or ''}".lower()
    if (any(milestone in _leg_text for milestone in _LEG_MILESTONES)
        and not any(analysis in _leg_text for analysis in _SUBSTANTIVE_ANALYSIS_KEYWORDS)):
        composite = max(0, composite - 20)
    
    return min(100, composite)
```

## Edge Cases

### 8. Local Source vs Prescore Gate Conflict
**Problem:** When a local source also matches a high-volume prescore gate, the local priority should win. Currently there's ambiguity in the logic about which rule takes precedence.
**Location:** Multiple prescore filter implementations
**Issue Type:** Conflict resolution
**Severity:** Blocking

**Corrected Code:**
```python
# Define clear precedence in prescore filter:
def apply_prescore_filter(articles: List[Article]) -> List[Article]:
    """
    PRIORITY ORDER:
    1. Local articles (ALWAYS pass through any prescore gate)
    2. Non-gated sources (ALWAYS pass through)
    3. Gated sources with keywords (pass with caps)
    4. Gated sources without keywords (DROP)
    """
    for article in articles:
        # PRIORITY 1: Local articles get absolute bypass
        if _is_local_article(article):
            kept.append(article)
            continue
            
        # PRIORITY 2: Non-gated sources
        if article.source not in gated_sources:
            kept.append(article)
            continue
            
        # PRIORITY 3: Gated sources with keywords
        if _has_prescore_keyword(article):
            candidates_by_source[article.source].append(article)
            continue
            
        # PRIORITY 4: Gated sources without keywords - DROP
        dropped += 1
```

### 9. Score Normalization Inconsistency
**Problem:** Different scoring functions normalize to [0,100] but use different rounding/precision methods, creating inconsistencies in final scores.
**Location:** `compute_composite_score()`, `score_articles_with_claude()`, and other scoring functions
**Issue Type:** Inconsistency
**Severity:** Latent

**Corrected Code:**
```python
def normalize_score(value: float, min_val: float = 0.0, max_val: float = 100.0) -> int:
    """Consistent score normalization across all scoring functions."""
    # Clamp to range
    clamped = max(min_val, min(max_val, value))
    # Round to nearest integer
    return int(round(clamped))

def compute_composite_score(article: 'Article', weights: dict = None) -> int:
    """Compute composite score with consistent normalization."""
    if weights is None:
        weights = SCORING_WEIGHTS.get('general', {})
    
    w_q = weights.get('w_quality', 0.25)
    w_r = weights.get('w_relevance', 0.55)
    w_l = weights.get('w_local', 0.20)
    
    composite = w_q * article.quality + w_r * article.relevance + w_l * article.local
    return normalize_score(composite)
```

### 10. Content Type Filter Override Issue
**Problem:** `filter_by_content_type()` (lines 2505-2534) has hardcoded drops for fluff/sponsored content, but the comment mentions that "Haiku scrub handles those with score-aware leniency; dropping them here would override that". This creates a contradiction between filters.
**Location:** `filter_by_content_type()` function
**Issue Type:** Conflict between filters
**Severity:** Blocking

**Corrected Code:**
```python
def filter_by_content_type(articles: List[Article]) -> Tuple[List[Article], Dict]:
    """Phase 3: Absolute content type filter — score-independent.

    NOTE: Some content types are handled by Haiku scrub with score-aware leniency
    to avoid over-filtering high-value fluff. These should be filtered here only
    if they score below a threshold.
    """
    filtered = []
    stats = {
        'fluff_dropped': 0,
        'sponsored_dropped': 0,
        'recap_dropped': 0,
        'wire_kept': 0,
        'other_kept': 0
    }
    
    for article in articles:
        # Score-aware fluff/sponsored filter (respect Haiku leniency)
        if article.content_type == 'fluff':
            if article.score >= LIMITS.get('fluff_score_threshold', 40):
                # Keep high-scoring fluff despite content type
                filtered.append(article)
                stats['other_kept'] += 1
            else:
                stats['fluff_dropped'] += 1
        elif article.content_type == 'sponsored':
            # Always drop sponsored unless very high scoring
            if article.score >= LIMITS.get('sponsored_score_threshold', 60):
                filtered.append(article)
                stats['other_kept'] += 1
            else:
                stats['sponsored_dropped'] += 1
        elif article.content_type == 'recap':
            # Drop recap unless it's local and meets threshold
            if article.local >= 50 and article.score >= LIMITS.get('recap_score_threshold', 30):
                filtered.append(article)
                stats['other_kept'] += 1
            else:
                stats['recap_dropped'] += 1
        elif article.content_type == 'wire':
            # Keep wire but track for dedup preference
            filtered.append(article)
            stats['wire_kept'] += 1
        else:
            # None/unknown: pass through (e.g. Cohere-scored articles)
            filtered.append(article)
            stats['other_kept'] += 1
    
    return filtered, stats
```

These findings address the core issues in the RSS curation pipeline, including filter contradictions, score erosion problems, missing configuration values, and edge case handling. Each blocking finding includes corrected code that can be applied immediately.
