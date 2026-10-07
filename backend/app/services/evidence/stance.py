"""Evidence stance detection using Natural Language Inference.

Uses a cross-encoder NLI model to determine whether evidence
supports, contradicts, or is neutral to a claim.
"""
import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np

try:
    import torch
except ImportError:
    torch = None

logger = logging.getLogger(__name__)


@dataclass
class StanceResult:
    """Result of stance detection for one evidence-claim pair."""
    entailment: float
    contradiction: float
    neutral: float
    predicted_label: str  # 'entailment', 'contradiction', or 'neutral'
    truncated: bool = False  # whether input was truncated


class StanceDetector:
    """Detects the stance of evidence relative to a claim using NLI."""
    
    def __init__(self, model, tokenizer, label_map: dict[int, str]) -> None:
        self.model = model
        self.tokenizer = tokenizer
        self.label_map = label_map  # {0: 'contradiction', 1: 'entailment', 2: 'neutral'}
        self.max_length = getattr(model.config, 'max_position_embeddings', 512)
        
        # Find label indices
        self._ent_idx = self._find_label_idx('entailment')
        self._con_idx = self._find_label_idx('contradiction')
        self._neu_idx = self._find_label_idx('neutral')
    
    def _find_label_idx(self, label: str) -> Optional[int]:
        for idx, name in self.label_map.items():
            if name == label:
                return idx
        return None
    
    def predict(self, evidence_text: str, claim_text: str) -> StanceResult:
        """Predict stance: evidence is premise, claim is hypothesis.
        
        NLI convention: premise=evidence, hypothesis=claim.
        Entailment means the evidence supports the claim.
        Contradiction means the evidence contradicts the claim.
        """
        # Check if truncation would lose important content
        encoded = self.tokenizer(
            evidence_text, claim_text,
            return_tensors='pt',
            truncation=True,
            max_length=self.max_length,
            return_overflowing_tokens=False,
        )
        
        # Detect if truncation occurred
        full_encoded = self.tokenizer(
            evidence_text, claim_text,
            truncation=False,
            return_tensors='pt',
        )
        truncated = full_encoded['input_ids'].shape[1] > self.max_length
        if truncated:
            logger.warning(
                f'Input truncated from {full_encoded["input_ids"].shape[1]} to {self.max_length} tokens. '
                f'Evidence may lose content.'
            )
        
        with torch.no_grad():
            outputs = self.model(**encoded)
        
        logits = outputs.logits[0]
        probs = torch.softmax(logits, dim=-1).numpy()
        
        # Extract scores using resolved label indices
        scores = {}
        for idx, label in self.label_map.items():
            scores[label] = float(probs[idx])
        
        predicted_idx = int(np.argmax(probs))
        predicted_label = self.label_map.get(predicted_idx, 'unknown')
        
        return StanceResult(
            entailment=scores.get('entailment', 0.0),
            contradiction=scores.get('contradiction', 0.0),
            neutral=scores.get('neutral', 0.0),
            predicted_label=predicted_label,
            truncated=truncated,
        )
    
    def predict_batch(self, pairs: list[tuple[str, str]]) -> list[StanceResult]:
        """Predict stance for multiple evidence-claim pairs."""
        results = []
        for evidence, claim in pairs:
            try:
                result = self.predict(evidence, claim)
                results.append(result)
            except Exception as e:
                logger.error(f'Stance prediction failed: {e}')
                results.append(StanceResult(
                    entailment=0.0, contradiction=0.0, neutral=1.0,
                    predicted_label='neutral', truncated=False
                ))
        return results