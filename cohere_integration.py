#!/usr/bin/env python3
"""Cohere API integration for Super RSS Curator.

Activated when COHERE_API_KEY is present in the environment.
Provides Rerank-based article scoring and Embed-based story group clustering
as alternatives to Claude for the relevant pipeline steps.
All public functions are no-ops and return falsy values when disabled.
"""

import os
import re
import math
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import api_usage

_client = None


def is_enabled() -> bool:
    return bool(os.environ.get('COHERE_API_KEY'))


def get_client():
    global _client
    if _client is None:
        import cohere  # imported lazily so the module loads even without cohere installed
        _client = cohere.ClientV2(api_key=os.environ['COHERE_API_KEY'])
    return _client


def cosine_sim(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def build_interest_query(interests_text: str) -> str:
    """Extract key interest phrases from PRIMARY and SECONDARY sections of scoring_interests.txt."""
    phrases = []
    capturing = False
    for line in interests_text.splitlines():
        stripped = line.strip()
        if stripped.startswith('PRIMARY INTERESTS') or stripped.startswith('SECONDARY INTERESTS'):
            capturing = True
            continue
        if capturing and (
            stripped.startswith('CONTEXTUAL')
            or stripped.startswith('SCORING')
            or stripped.startswith('AVOID')
            or stripped == '---'
        ):
            capturing = False
            continue
        if capturing and stripped.startswith('-'):
            phrase = stripped[1:].strip()
            # Drop trailing scoring-rubric commentary (e.g. "— score 70-100 for...")
            # but keep the concrete example terms after the colon — those examples
            # (mining, forestry, land rights, etc.) are the strongest signal for
            # semantic matching and were previously discarded entirely.
            phrase = re.split(r'\s+—\s+score\b', phrase, maxsplit=1, flags=re.IGNORECASE)[0].strip()
            phrases.append(phrase)
    return ', '.join(phrases) if phrases else 'technology, news, climate, local community'


def score_with_rerank(articles: List[Any], interests_text: str) -> Dict[str, Tuple[int, str]]:
    """Score articles using Cohere Rerank against the interest query.

    Returns {url_hash: (score_0_to_100, '')}. Category is left empty so the
    caller can apply the keyword-based categorize_article() fallback.
    """
    if not articles:
        return {}

    co = get_client()
    query = build_interest_query(interests_text)
    documents = [f"{a.title}. {(a.description or '')[:200]}" for a in articles]

    try:
        api_usage.record_call('cohere')
        result = co.rerank(
            model="rerank-english-v3.0",
            query=query,
            documents=documents,
            top_n=len(documents),
        )
        # Rank-percentile normalization: Cohere's absolute relevance scores are
        # calibrated to query specificity, not to the 0-100 scale Claude uses.
        # For a niche interest query (rural BC, homelab, 3D printing…) most general
        # news articles score 0.00–0.05, making the min_claude_score=15 threshold
        # filter out everything. Treating the scores as relative rankings and mapping
        # to percentile bands restores the expected pass rate (~30% of the batch).
        ranked = sorted(result.results, key=lambda x: x.relevance_score, reverse=True)
        n = len(ranked)
        scores: Dict[str, Tuple[int, str]] = {}
        for rank, item in enumerate(ranked):
            url_hash = articles[item.index].url_hash
            p = rank / max(n - 1, 1)  # 0.0 = best article, 1.0 = worst
            if p <= 0.30:
                # Top 30%: score 20–80 → passes min_claude_score filter
                normalized = int(80 - (80 - 20) * p / 0.30)
            else:
                # Bottom 70%: score 0–14 → filtered out by quality threshold
                normalized = int(14 * (1.0 - p) / 0.70)
            scores[url_hash] = (normalized, '')
        return scores
    except Exception as e:
        print(f"  ⚠️  Cohere Rerank error: {e}")
        return {}


def embed_articles(articles: List[Any]) -> Dict[str, List[float]]:
    """Embed article title + description via Cohere Embed.

    Returns {url_hash: embedding_vector}. Returns {} on error.
    Batches requests to stay within the 96-text-per-request API limit.
    """
    if not articles:
        return {}

    co = get_client()
    texts = [f"{a.title}. {(a.description or '')[:200]}" for a in articles]
    BATCH_SIZE = 96

    all_vectors: List[List[float]] = []
    for batch_start in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[batch_start:batch_start + BATCH_SIZE]
        try:
            api_usage.record_call('cohere')
            result = co.embed(
                texts=batch_texts,
                model="embed-english-v3.0",
                input_type="search_document",
                embedding_types=["float"],
            )
            all_vectors.extend(result.embeddings.float_)
        except Exception as e:
            print(f"  ⚠️  Cohere Embed error: {e}")
            return {}

    return {articles[i].url_hash: all_vectors[i] for i in range(len(articles))}


_STOPWORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'has', 'have',
    'had', 'will', 'would', 'could', 'should', 'its', 'it', 'this', 'that',
    'as', 'how', 'why', 'what', 'new', 'says', 'said', 'from', 'about',
    'into', 'than', 'after', 'before', 'over', 'up', 'out', 'if', 'no',
}


def _make_story_label(title: str) -> str:
    words = re.findall(r'\b[a-zA-Z]+\b', title.lower())
    sig = [w for w in words if w not in _STOPWORDS and len(w) > 2]
    return ' '.join(sig[:5])


def cluster_story_groups(articles: List[Any], embeddings: Dict[str, List[float]]) -> None:
    """Assign story_group to articles in-place using embedding cosine similarity (union-find).

    Articles with cosine similarity >= THRESHOLD are considered the same story event.
    Clusters of 2+ get a label derived from the highest-scoring article's title.
    Single articles retain whatever story_group they already have (or None).
    """
    THRESHOLD = 0.90
    n = len(articles)
    if n < 2:
        return

    embs = [embeddings.get(a.url_hash) for a in articles]

    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(n):
        if embs[i] is None:
            continue
        for j in range(i + 1, n):
            if embs[j] is None:
                continue
            if cosine_sim(embs[i], embs[j]) >= THRESHOLD:
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[ri] = rj

    groups: Dict[int, List[int]] = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(i)

    assigned = 0
    for members in groups.values():
        if len(members) < 2:
            continue
        best_idx = max(members, key=lambda i: articles[i].score)
        label = _make_story_label(articles[best_idx].title)
        if not label:
            continue
        for i in members:
            articles[i].story_group = label
        assigned += len(members)

    if assigned:
        print(f"   🔗 Cohere story clustering: grouped {assigned} articles into story clusters")


def score_feed_against_interests(candidate_texts: List[str], interests_text: str) -> float:
    """Return mean cosine similarity (0.0–1.0) between candidate article texts and the interests profile.

    Uses asymmetric embedding: interests as search_query, articles as search_document.
    Returns 0.0 when Cohere is disabled or on error.
    """
    if not is_enabled() or not candidate_texts or not interests_text:
        return 0.0

    co = get_client()
    try:
        api_usage.record_call('cohere')
        query_result = co.embed(
            texts=[interests_text[:2048]],
            model="embed-english-v3.0",
            input_type="search_query",
            embedding_types=["float"],
        )
        query_vec = query_result.embeddings.float_[0]

        api_usage.record_call('cohere')
        doc_result = co.embed(
            texts=candidate_texts[:96],
            model="embed-english-v3.0",
            input_type="search_document",
            embedding_types=["float"],
        )
        doc_vecs = doc_result.embeddings.float_

        if not doc_vecs:
            return 0.0
        return sum(cosine_sim(query_vec, dv) for dv in doc_vecs) / len(doc_vecs)
    except Exception as e:
        print(f"  ⚠️  Cohere feed affinity embed error: {e}")
        return 0.0


def score_scrub_interest(
    articles: List[Any],
    interests_text: str,
) -> Dict[str, float]:
    """Score articles' interest relevance (0-100) via Cohere Rerank for scrub pre-filtering.

    Returns {article.url_hash: interest_score}. Returns {} when Cohere is
    disabled, on error, or given no articles — callers should treat a missing
    url_hash as "unscored" rather than assuming a neutral score.
    """
    if not is_enabled() or not articles:
        return {}

    co = get_client()
    query = build_interest_query(interests_text) if interests_text else 'technology news community'
    documents = [f"{a.title}. {(a.description or '')[:100]}" for a in articles]

    try:
        api_usage.record_call('cohere')
        result = co.rerank(
            model="rerank-english-v3.0",
            query=query,
            documents=documents,
            top_n=len(documents),
        )
        return {articles[item.index].url_hash: item.relevance_score * 100 for item in result.results}
    except Exception as e:
        print(f"  ⚠️  Cohere scrub pre-filter error: {e}")
        return {}


def apply_scrub_threshold(
    articles: List[Any],
    interest_scores: Dict[str, float],
    local_signals: Optional[List[str]] = None,
    threshold: float = 20.0,
) -> Tuple[List[Any], List[Any]]:
    """Split articles into (kept, auto_removed) using cached/fresh interest scores.

    Articles scoring below `threshold` (out of 100) are auto-removed, unless
    their title contains a local signal (those always go to Claude). The
    default of 2.5 is deliberately conservative — the primary scorer already
    filtered the bottom 70%, and the Haiku scrub handles borderline content.
    An article missing from `interest_scores` is treated as neutral (50) and
    kept.
    """
    _local = [s.lower() for s in (local_signals or [])]

    kept, auto_removed = [], []
    for article in articles:
        title_lower = article.title.lower()
        is_local = any(sig in title_lower for sig in _local)
        iscore = interest_scores.get(article.url_hash, 50.0)
        if not is_local and iscore < threshold:
            print(f"  🔮 Pre-filtered (score={iscore:.0f}): {article.title[:80]}")
            auto_removed.append(article)
        else:
            kept.append(article)

    if auto_removed:
        print(f"  🔮 Cohere pre-filter removed {len(auto_removed)}, sending {len(kept)} to Claude")

    return kept, auto_removed


def score_themes_with_rerank(
    articles: List[Any],
    themes: Dict[str, Dict],
) -> Dict[str, Dict[str, int]]:
    """Score articles for multiple podcast themes using Cohere Rerank.

    themes: {day_key: {'label': str, 'scoring_prompt': str}}
    Returns {article_link: {theme_label: score_0_to_100}}.
    One Rerank call is made per theme; all calls are fast and synchronous.
    """
    if not articles or not themes:
        return {}

    co = get_client()
    documents = [f"{a.title}. {(a.description or '')[:200]}" for a in articles]
    results: Dict[str, Dict[str, int]] = {a.link: {} for a in articles}

    for _day_key, theme_cfg in themes.items():
        label = theme_cfg.get('label', _day_key)
        query = (theme_cfg.get('scoring_prompt', '') or label)[:400].strip()

        try:
            api_usage.record_call('cohere')
            result = co.rerank(
                model="rerank-english-v3.0",
                query=query,
                documents=documents,
                top_n=len(documents),
            )
            # Rank-percentile normalization: Cohere's raw relevance scores for niche
            # themes (farming, forestry, local industry) are typically 0.00–0.05, which
            # maps to 0–5 when multiplied directly by 100. This causes all articles to
            # fall below the holdover_threshold floor (~25–30), leaving themed podcasts
            # with near-zero avg theme score and no thematically-selected content.
            # Map to percentile bands so top 30% of matches score 30–80 and the
            # bottom 70% score 0–29, calibrated to the typical holdover_threshold.
            ranked = sorted(result.results, key=lambda x: x.relevance_score, reverse=True)
            n = len(ranked)
            for rank, item in enumerate(ranked):
                link = articles[item.index].link
                p = rank / max(n - 1, 1)  # 0.0 = best, 1.0 = worst
                if p <= 0.30:
                    score = int(80 - 50 * (p / 0.30))   # 80 → 30
                else:
                    score = int(30 * (1.0 - p) / 0.70)  # 30 → 0
                results[link][label] = score
        except Exception as e:
            print(f"  ⚠️  Cohere theme Rerank error [{label}]: {e}")
            for a in articles:
                results[a.link].setdefault(label, 50)

    return results
