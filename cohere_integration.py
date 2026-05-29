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
        if 'PRIMARY INTERESTS' in stripped or 'SECONDARY INTERESTS' in stripped:
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
            if ':' in phrase:
                phrase = phrase.split(':')[0].strip()
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
        result = co.rerank(
            model="rerank-english-v3.0",
            query=query,
            documents=documents,
            top_n=len(documents),
        )
        scores: Dict[str, Tuple[int, str]] = {}
        for item in result.results:
            url_hash = articles[item.index].url_hash
            scores[url_hash] = (int(item.relevance_score * 100), '')
        return scores
    except Exception as e:
        print(f"  ⚠️  Cohere Rerank error: {e}")
        return {}


def embed_articles(articles: List[Any]) -> Dict[str, List[float]]:
    """Embed article title + description via Cohere Embed.

    Returns {url_hash: embedding_vector}. Returns {} on error.
    """
    if not articles:
        return {}

    co = get_client()
    texts = [f"{a.title}. {(a.description or '')[:200]}" for a in articles]

    try:
        result = co.embed(
            texts=texts,
            model="embed-english-v3.0",
            input_type="search_document",
            embedding_types=["float"],
        )
        vectors = result.embeddings.float_
        return {articles[i].url_hash: vectors[i] for i in range(len(articles))}
    except Exception as e:
        print(f"  ⚠️  Cohere Embed error: {e}")
        return {}


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
            result = co.rerank(
                model="rerank-english-v3.0",
                query=query,
                documents=documents,
                top_n=len(documents),
            )
            for item in result.results:
                link = articles[item.index].link
                results[link][label] = int(item.relevance_score * 100)
        except Exception as e:
            print(f"  ⚠️  Cohere theme Rerank error [{label}]: {e}")
            for a in articles:
                results[a.link].setdefault(label, 50)

    return results
