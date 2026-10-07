"""Semantic retrieval using sentence-transformers embeddings.

Provides dense vector-based retrieval over corpus passages
using cosine similarity.
"""
import hashlib
import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class SemanticRetriever:
    """Dense semantic retrieval using sentence-transformer embeddings."""
    
    def __init__(self, cache_dir: str = '.model_cache') -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.corpus_embeddings: Optional[np.ndarray] = None
        self.encoder = None
        self._indexed = False
    
    @property
    def is_indexed(self) -> bool:
        return self._indexed
    
    def set_encoder(self, encoder) -> None:
        """Set the sentence-transformer encoder model."""
        self.encoder = encoder
    
    def build_index(self, passages: list[str], corpus_version: str = '') -> None:
        """Build or load cached corpus embeddings."""
        if self.encoder is None:
            logger.error('Encoder not set. Call set_encoder() first.')
            return
        
        # Check cache
        cache_key = self._compute_cache_key(passages, corpus_version)
        cache_path = self.cache_dir / f'corpus_embeddings_{cache_key}.npy'
        
        if cache_path.exists():
            try:
                self.corpus_embeddings = np.load(str(cache_path))
                if self.corpus_embeddings.shape[0] == len(passages):
                    self._indexed = True
                    logger.info(f'Loaded cached embeddings: {self.corpus_embeddings.shape}')
                    return
                else:
                    logger.warning('Cached embeddings count mismatch, re-encoding')
            except Exception as e:
                logger.warning(f'Failed to load cached embeddings: {e}')
        
        # Encode all passages
        logger.info(f'Encoding {len(passages)} passages...')
        self.corpus_embeddings = self.encoder.encode(
            passages,
            show_progress_bar=False,
            batch_size=32,
            convert_to_numpy=True,
            normalize_embeddings=True,  # for cosine similarity via dot product
        )
        
        # Cache embeddings
        try:
            np.save(str(cache_path), self.corpus_embeddings)
            logger.info(f'Cached embeddings to {cache_path}')
        except Exception as e:
            logger.warning(f'Failed to cache embeddings: {e}')
        
        self._indexed = True
        logger.info(f'Semantic index built: {self.corpus_embeddings.shape}')
    
    def search(self, query: str, top_k: int = 20) -> list[tuple[int, float]]:
        """Search by semantic similarity. Returns (passage_index, score) pairs."""
        if not self._indexed or self.encoder is None or self.corpus_embeddings is None:
            return []
        
        # Encode query
        query_embedding = self.encoder.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        
        # Cosine similarity (embeddings are normalized, so dot product = cosine)
        similarities = np.dot(self.corpus_embeddings, query_embedding.T).flatten()
        
        # Get top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = [
            (int(idx), float(similarities[idx]))
            for idx in top_indices
            if similarities[idx] > 0
        ]
        
        return results
    
    def _compute_cache_key(self, passages: list[str], corpus_version: str) -> str:
        """Compute a deterministic cache key from corpus content."""
        content = corpus_version + '|' + str(len(passages))
        # Include first and last passage hashes
        if passages:
            content += '|' + passages[0][:100] + '|' + passages[-1][:100]
        return hashlib.md5(content.encode()).hexdigest()[:12]