"""Unit tests for retrieval modules: BM25, RRF fusion, and deduplication."""
import pytest
from app.services.retrieval.bm25 import BM25Retriever, tokenize
from app.services.retrieval.fusion import (
    reciprocal_rank_fusion,
    deduplicate_passages,
    jaccard_similarity,
    select_evidence,
)


def test_tokenize_stopwords_removal():
    tokens = tokenize("The Earth is orbiting around the Sun.")
    assert "the" not in tokens
    assert "is" not in tokens
    assert "earth" in tokens
    assert "orbiting" in tokens
    assert "sun" in tokens


def test_bm25_search():
    passages = [
        "Water boils at 100 degrees Celsius under standard atmospheric pressure.",
        "The Apollo 11 mission successfully landed humans on the Moon in 1969.",
        "Mount Everest is the highest mountain peak above sea level on planet Earth."
    ]
    bm25 = BM25Retriever()
    bm25.build_index(passages)

    results = bm25.search("boiling temperature of water", top_k=2)
    assert len(results) > 0
    top_idx, top_score = results[0]
    assert top_idx == 0
    assert top_score > 0


def test_jaccard_similarity():
    text_a = "The Great Wall of China is visible from space"
    text_b = "The Great Wall of China is visible from space with naked eye"
    text_c = "Photosynthesis converts carbon dioxide into glucose and oxygen"

    sim_ab = jaccard_similarity(text_a, text_b)
    sim_ac = jaccard_similarity(text_a, text_c)

    assert sim_ab > 0.7
    assert sim_ac < 0.1


def test_reciprocal_rank_fusion():
    bm25_rankings = [(0, 10.5), (1, 8.2), (2, 4.1)]
    semantic_rankings = [(1, 0.92), (0, 0.88), (3, 0.65)]

    fused = reciprocal_rank_fusion(bm25_rankings, semantic_rankings, k=60)
    top_indices = [idx for idx, _score in fused]

    # Both index 0 and 1 are ranked high in both lists, so they should be top 2
    assert set(top_indices[:2]) == {0, 1}


def test_deduplication():
    passages = [
        "The Earth revolves around the Sun in 365.25 days.",
        "The Earth revolves around the Sun in 365.25 days approximately.",
        "Vaccines stimulate the human immune system to fight disease.",
    ]
    indices = [0, 1, 2]
    deduped = deduplicate_passages(indices, passages, threshold=0.8)
    assert len(deduped) == 2
    assert 0 in deduped
    assert 2 in deduped
