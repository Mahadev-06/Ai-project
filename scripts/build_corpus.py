"""Corpus indexing and verification utility for ClaimLens.

Validates corpus documents, verifies schema, counts passages,
updates manifest.json, and pre-computes semantic embeddings.
"""
import json
import logging
import os
import sys
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("build_corpus")


def build_and_verify_corpus():
    from app.services.retrieval.corpus import CorpusLoader
    from app.services.retrieval.bm25 import BM25Retriever
    from app.services.retrieval.semantic import SemanticRetriever

    corpus_dir = BASE_DIR / "backend" / "data" / "corpus"
    manifest_file = corpus_dir / "manifest.json"
    docs_dir = corpus_dir / "documents"

    if not manifest_file.exists():
        logger.error(f"Manifest not found at {manifest_file}")
        sys.exit(1)

    loader = CorpusLoader(str(corpus_dir))
    loader.load()

    if not loader.is_loaded:
        logger.error("Failed to load corpus!")
        sys.exit(1)

    logger.info(f"Loaded {len(loader.passages)} passages from {len(list(docs_dir.glob('*.json')))} document files.")

    # Update manifest with actual passage count
    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    manifest_data["document_count"] = len(list(docs_dir.glob("*.json")))
    manifest_data["passage_count"] = len(loader.passages)

    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    logger.info("Updated manifest.json with actual counts.")

    # Test BM25 index
    logger.info("Testing BM25 index construction...")
    bm25 = BM25Retriever()
    texts = loader.get_passage_texts()
    bm25.build_index(texts)

    test_query = "Great Wall of China space visible"
    bm25_matches = bm25.search(test_query, top_k=3)
    logger.info(f"BM25 test search for '{test_query}': {len(bm25_matches)} matches found.")
    for idx, score in bm25_matches:
        logger.info(f"  - [{score:.2f}] {loader.passages[idx].title}: {loader.passages[idx].text[:80]}...")

    # Build Semantic Embeddings
    logger.info("Pre-computing and caching dense embeddings...")
    try:
        from sentence_transformers import SentenceTransformer
        cache_dir = BASE_DIR / "backend" / ".model_cache"
        encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        semantic = SemanticRetriever(str(cache_dir))
        semantic.set_encoder(encoder)
        semantic.build_index(texts, corpus_version=loader.version)

        sem_matches = semantic.search(test_query, top_k=3)
        logger.info(f"Semantic test search for '{test_query}': {len(sem_matches)} matches found.")
        for idx, score in sem_matches:
            logger.info(f"  - [{score:.2f}] {loader.passages[idx].title}: {loader.passages[idx].text[:80]}...")

    except ImportError:
        logger.warning("sentence-transformers not installed in current environment; skipping embedding generation.")
    except Exception as e:
        logger.warning(f"Could not build semantic embeddings now: {e}")

    logger.info("=== Corpus validation and indexing complete! ===")


if __name__ == "__main__":
    build_and_verify_corpus()
