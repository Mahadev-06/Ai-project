"""Model pre-caching and verification script for ClaimLens.

Downloads and validates:
1. spaCy model: en_core_web_sm
2. Sentence Transformer: sentence-transformers/all-MiniLM-L6-v2
3. Cross-Encoder NLI: cross-encoder/nli-deberta-v3-small
"""
import logging
import sys
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("setup_models")


def download_spacy(model_name: str = "en_core_web_sm"):
    logger.info(f"Downloading/Verifying spaCy model: {model_name}...")
    import spacy
    try:
        spacy.load(model_name)
        logger.info(f"spaCy model '{model_name}' is already installed.")
    except Exception:
        import subprocess
        cmd = [sys.executable, "-m", "spacy", "download", model_name]
        logger.info(f"Executing: {' '.join(cmd)}")
        subprocess.check_call(cmd)
        logger.info(f"Successfully downloaded {model_name}.")


def download_sentence_transformer(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    logger.info(f"Downloading/Verifying Sentence Transformer: {model_name}...")
    from sentence_transformers import SentenceTransformer
    start = time.time()
    model = SentenceTransformer(model_name)
    emb = model.encode(["ClaimLens verification embedding check."])
    logger.info(f"Sentence Transformer ready ({time.time() - start:.1f}s, dimension: {emb.shape[1]}).")


def download_nli_cross_encoder(model_name: str = "cross-encoder/nli-deberta-v3-small"):
    logger.info(f"Downloading/Verifying NLI Cross-Encoder: {model_name}...")
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    import torch

    start = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()

    # Orientation check
    test_p = "The Earth revolves around the Sun."
    test_h = "The Earth is in orbit around a star."
    inputs = tokenizer(test_p, test_h, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits[0]
        probs = torch.softmax(logits, dim=-1).numpy()

    logger.info(
        f"NLI Cross-Encoder ready ({time.time() - start:.1f}s). "
        f"Labels: {model.config.id2label}. Orientation probabilities: {probs.tolist()}"
    )


def main():
    logger.info("=== ClaimLens Offline Model Pre-caching ===")
    try:
        download_spacy()
        download_sentence_transformer()
        download_nli_cross_encoder()
        logger.info("=== All models downloaded, validated, and cached successfully! ===")
    except Exception as e:
        logger.error(f"Model setup failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
