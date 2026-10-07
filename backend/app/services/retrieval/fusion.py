"""Reciprocal Rank Fusion for combining retrieval results.

Merges BM25 and semantic retrieval rankings into a single
ranked list with deduplication.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


import re


def jaccard_similarity(text_a: str, text_b: str) -> float:
    """Compute Jaccard similarity between two texts."""
    words_a = set(re.findall(r'\b[\w\.]+\b', text_a.lower()))
    words_b = set(re.findall(r'\b[\w\.]+\b', text_b.lower()))
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def reciprocal_rank_fusion(
    bm25_results: list[tuple[int, float]],
    semantic_results: list[tuple[int, float]],
    k: int = 60,
) -> list[tuple[int, float]]:
    """Combine two ranked lists using Reciprocal Rank Fusion.
    
    RRF score = sum(1 / (k + rank_i)) across all ranking lists.
    k=60 is the standard parameter from the original paper.
    
    Args:
        bm25_results: (passage_index, score) from BM25
        semantic_results: (passage_index, score) from semantic search
        k: RRF parameter (default 60)
    
    Returns:
        Merged (passage_index, rrf_score) sorted by score descending.
    """
    rrf_scores: dict[int, float] = {}
    
    # Add BM25 rankings
    for rank, (idx, _score) in enumerate(bm25_results):
        rrf_scores[idx] = rrf_scores.get(idx, 0.0) + 1.0 / (k + rank + 1)
    
    # Add semantic rankings
    for rank, (idx, _score) in enumerate(semantic_results):
        rrf_scores[idx] = rrf_scores.get(idx, 0.0) + 1.0 / (k + rank + 1)
    
    # Sort by RRF score
    sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_results


def deduplicate_passages(
    passage_indices: list[int],
    passage_texts: list[str],
    threshold: float = 0.85,
) -> list[int]:
    """Remove near-duplicate passages based on Jaccard similarity.
    
    Keeps the first occurrence (highest ranked) of each group.
    """
    kept: list[int] = []
    kept_texts: list[str] = []
    
    for idx in passage_indices:
        if idx >= len(passage_texts):
            continue
        text = passage_texts[idx]
        is_duplicate = False
        
        for kept_text in kept_texts:
            if jaccard_similarity(text, kept_text) >= threshold:
                is_duplicate = True
                break
        
        if not is_duplicate:
            kept.append(idx)
            kept_texts.append(text)
    
    return kept


def select_evidence(
    bm25_results: list[tuple[int, float]],
    semantic_results: list[tuple[int, float]],
    passage_texts: list[str],
    max_passages: int = 5,
    rrf_k: int = 60,
    dedup_threshold: float = 0.85,
) -> list[tuple[int, float]]:
    """Full evidence selection pipeline.
    
    1. Merge rankings with RRF
    2. Deduplicate near-identical passages
    3. Select top-k diverse passages
    """
    # Merge
    fused = reciprocal_rank_fusion(bm25_results, semantic_results, k=rrf_k)
    
    # Deduplicate
    fused_indices = [idx for idx, _ in fused]
    unique_indices = deduplicate_passages(fused_indices, passage_texts, dedup_threshold)
    
    # Select top passages with normalized relevance score in [0.0, 1.0]
    num_rankers = (1 if bm25_results else 0) + (1 if semantic_results else 0)
    max_possible_rrf = (num_rankers / (rrf_k + 1)) if num_rankers > 0 else 1.0

    rrf_score_map = dict(fused)
    selected = [
        (idx, round(min(1.0, rrf_score_map.get(idx, 0.0) / max_possible_rrf), 4))
        for idx in unique_indices[:max_passages]
    ]
    
    logger.info(
        f'Evidence selection: {len(bm25_results)} BM25 + {len(semantic_results)} semantic '
        f'-> {len(fused)} fused -> {len(unique_indices)} unique -> {len(selected)} selected'
    )
    
    return selected