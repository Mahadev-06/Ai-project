"""Centralized model management for ClaimLens.

Loads spaCy, Sentence Transformers, and NLI models once.
Tracks readiness state and model versions.
"""
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any

import numpy as np

try:
    import torch
except ImportError:
    torch = None

logger = logging.getLogger(__name__)


class ModelManager:
    """Singleton manager for all ML models used in the pipeline."""
    
    _instance: Optional['ModelManager'] = None
    
    def __new__(cls) -> 'ModelManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self.nlp = None  # spaCy model
        self.encoder = None  # SentenceTransformer
        self.nli_model = None  # NLI AutoModel
        self.nli_tokenizer = None  # NLI tokenizer
        self.nli_label_map: Dict[int, str] = {}  # resolved from model config
        self._ready = False
        self._model_versions: Dict[str, str] = {}
        self._load_errors: list[str] = []
    
    @property
    def is_ready(self) -> bool:
        return self._ready and self.nlp is not None and self.encoder is not None and self.nli_model is not None
    
    @property
    def model_versions(self) -> Dict[str, str]:
        return self._model_versions.copy()
    
    @property
    def load_errors(self) -> list[str]:
        return self._load_errors.copy()
    
    def load_all(self, embedding_model: str = 'sentence-transformers/all-MiniLM-L6-v2',
                 nli_model: str = 'cross-encoder/nli-deberta-v3-small',
                 spacy_model: str = 'en_core_web_sm') -> None:
        """Load all models. Call once at startup."""
        self._load_errors = []
        self._load_spacy(spacy_model)
        self._load_encoder(embedding_model)
        self._load_nli(nli_model)
        self._ready = len(self._load_errors) == 0
        if self._ready:
            self._run_orientation_check()
            logger.info('All models loaded successfully')
        else:
            logger.error(f'Model loading errors: {self._load_errors}')
    
    def _load_spacy(self, model_name: str) -> None:
        try:
            import spacy
            start = time.time()
            self.nlp = spacy.load(model_name)
            elapsed = time.time() - start
            self._model_versions['spacy'] = f'{model_name} (spacy {spacy.__version__})'
            logger.info(f'spaCy model loaded in {elapsed:.1f}s')
        except Exception as e:
            self._load_errors.append(f'spaCy ({model_name}): {e}')
            logger.error(f'Failed to load spaCy model: {e}')
    
    def _load_encoder(self, model_name: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer
            start = time.time()
            self.encoder = SentenceTransformer(model_name)
            elapsed = time.time() - start
            self._model_versions['encoder'] = model_name
            logger.info(f'Sentence encoder loaded in {elapsed:.1f}s')
        except Exception as e:
            self._load_errors.append(f'Encoder ({model_name}): {e}')
            logger.error(f'Failed to load encoder: {e}')
    
    def _load_nli(self, model_name: str) -> None:
        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            start = time.time()
            self.nli_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.nli_model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.nli_model.eval()
            
            # Resolve label mapping from model config - NEVER hardcode
            config = self.nli_model.config
            if hasattr(config, 'id2label') and config.id2label:
                self.nli_label_map = {int(k): v.lower() for k, v in config.id2label.items()}
            else:
                # Fallback based on model documentation, but log warning
                logger.warning('No id2label in model config, using documented defaults')
                self.nli_label_map = {0: 'contradiction', 1: 'entailment', 2: 'neutral'}
            
            elapsed = time.time() - start
            self._model_versions['nli'] = model_name
            logger.info(f'NLI model loaded in {elapsed:.1f}s, labels: {self.nli_label_map}')
        except Exception as e:
            self._load_errors.append(f'NLI ({model_name}): {e}')
            logger.error(f'Failed to load NLI model: {e}')
    
    def _run_orientation_check(self) -> None:
        """Verify NLI model produces expected results for a known pair."""
        if self.nli_model is None or self.nli_tokenizer is None:
            return
        try:
            test_premise = 'A person is walking in a park.'
            test_hypothesis = 'A person is moving.'
            inputs = self.nli_tokenizer(
                test_premise, test_hypothesis,
                return_tensors='pt', truncation=True, max_length=512
            )
            with torch.no_grad():
                outputs = self.nli_model(**inputs)
            logits = outputs.logits[0]
            probs = torch.softmax(logits, dim=-1).numpy()
            
            # Find entailment label index
            ent_idx = None
            for idx, label in self.nli_label_map.items():
                if label == 'entailment':
                    ent_idx = idx
                    break
            
            if ent_idx is not None and probs[ent_idx] > 0.5:
                logger.info(f'NLI orientation check passed: entailment={probs[ent_idx]:.3f}')
            else:
                logger.warning(f'NLI orientation check: unexpected scores {dict(zip(self.nli_label_map.values(), probs))}')
        except Exception as e:
            logger.warning(f'NLI orientation check failed: {e}')
    
    def get_nli_label_index(self, label: str) -> Optional[int]:
        """Get the model's index for a given label name."""
        for idx, name in self.nli_label_map.items():
            if name == label:
                return idx
        return None


model_manager = ModelManager()