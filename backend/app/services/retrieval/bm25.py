"""BM25 text retrieval using rank-bm25.

Provides sparse keyword-based retrieval over corpus passages.
"""
import logging
import re
from typing import Optional

import numpy as np
from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)

# Simple English stopwords
STOPWORDS = {
    'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'can', 'shall', 'to', 'of', 'in', 'for',
    'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'between', 'out', 'off', 'over',
    'under', 'again', 'further', 'then', 'once', 'and', 'but', 'or',
    'nor', 'not', 'so', 'yet', 'both', 'each', 'few', 'more', 'most',
    'other', 'some', 'such', 'than', 'too', 'very', 'just', 'also',
    'it', 'its', 'this', 'that', 'these', 'those', 'he', 'she', 'they',
    'we', 'you', 'i', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
    'his', 'our', 'their', 'what', 'which', 'who', 'whom', 'when',
    'where', 'how', 'all', 'any', 'if', 'no', 'about', 'up',
}


def tokenize(text: str) -> list[str]:
    """Tokenize text: lowercase, split on non-alphanumeric, remove stopwords."""
    tokens = re.findall(r'[a-z0-9]+', text.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


class BM25Retriever:
    """BM25-based sparse retrieval over corpus passages."""
    
    def __init__(self) -> None:
        self.index: Optional[BM25Okapi] = None
        self.corpus_tokens: list[list[str]] = []
        self._indexed = False
    
    @property
    def is_indexed(self) -> bool:
        return self._indexed
    
    def build_index(self, passages: list[str]) -> None:
        """Build BM25 index from passage texts."""
        self.corpus_tokens = [tokenize(p) for p in passages]
        self.index = BM25Okapi(self.corpus_tokens)
        self._indexed = True
        logger.info(f'BM25 index built with {len(passages)} passages')
    
    def search(self, query: str, top_k: int = 20) -> list[tuple[int, float]]:
        """Search the index. Returns list of (passage_index, score)."""
        if not self._indexed or self.index is None:
            return []
        
        query_tokens = tokenize(query)
        if not query_tokens:
            return []
        
        scores = self.index.get_scores(query_tokens)
        
        # Get top-k indices sorted by score
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = [
            (int(idx), float(scores[idx]))
            for idx in top_indices
            if scores[idx] > 0
        ]
        
        return results