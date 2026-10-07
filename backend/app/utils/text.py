"""Text utilities for ClaimLens."""
import re
from typing import List, Set


def normalize_text(text: str) -> str:
    """Normalize whitespace and control characters."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_words(text: str) -> Set[str]:
    """Extract lowercase alphanumeric words."""
    return set(re.findall(r'[a-z0-9]+', text.lower()))


def jaccard_similarity(text_a: str, text_b: str) -> float:
    """Compute Jaccard similarity coefficient between two texts."""
    words_a = extract_words(text_a)
    words_b = extract_words(text_b)
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def split_sentences(text: str) -> List[str]:
    """Basic rule-based sentence boundary detector."""
    # Split on terminal punctuation followed by space or newline
    raw_sents = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in raw_sents if len(s.strip()) > 5]


def truncate_text(text: str, max_chars: int = 200, ellipsis: str = '...') -> str:
    """Safely truncate text at word boundaries."""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars].rsplit(' ', 1)[0]
    return truncated + ellipsis