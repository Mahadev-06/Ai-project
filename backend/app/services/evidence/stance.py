"""Evidence stance detection using Natural Language Inference.

Uses a cross-encoder NLI model to determine whether evidence
supports, contradicts, or is neutral to a claim.
"""
import logging
import re
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
    
    def _predict_single(self, premise: str, hypothesis: str) -> StanceResult:
        """Run cross-encoder inference for a single premise-hypothesis pair."""
        encoded = self.tokenizer(
            premise, hypothesis,
            return_tensors='pt',
            truncation=True,
            max_length=self.max_length,
            return_overflowing_tokens=False,
        )
        
        with torch.no_grad():
            outputs = self.model(**encoded)
        
        logits = outputs.logits[0]
        probs = torch.softmax(logits, dim=-1).numpy()
        
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
            truncated=False,
        )

    def predict(self, evidence_text: str, claim_text: str) -> StanceResult:
        """Predict stance with sentence-level extraction for compound evidence."""
        # Clean premise text (strip leading dates like 'Aug 29, 2025 · ')
        clean_evidence = re.sub(r'^[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4}\s*[\-\u2013\u2014·•]+\s*', '', evidence_text.strip())
        
        # 1. Full passage prediction
        base_result = self._predict_single(clean_evidence, claim_text)
        
        # 2. Check individual sentences if multi-sentence
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_evidence) if len(s.strip()) >= 15]
        if len(sentences) <= 1:
            return base_result
            
        best_result = base_result
        best_signal = max(base_result.entailment, base_result.contradiction)
        
        for sent in sentences[:5]:
            sent_res = self._predict_single(sent, claim_text)
            sent_signal = max(sent_res.entailment, sent_res.contradiction)
            # If an individual sentence has a clear non-neutral signal that exceeds the full paragraph
            if sent_signal > best_signal and (sent_res.entailment >= 0.40 or sent_res.contradiction >= 0.40):
                best_signal = sent_signal
                best_result = sent_res
                
        return best_result
    
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