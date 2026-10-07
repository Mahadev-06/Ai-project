# ClaimLens Model & Data Cards

## Official Project Title
**AI-Based Misinformation Detection System Using Natural Language Processing, Information Retrieval and Source Credibility Analysis**

---

# SECTION 1: MODEL CARDS

## Model 1: Dense Semantic Encoder
- **Model Identifier:** `sentence-transformers/all-MiniLM-L6-v2`
- **Developer / Organization:** Sentence-Transformers / Hugging Face (fine-tuned from Microsoft MiniLM)
- **Model Type:** Bi-encoder transformer for sentence and passage embeddings
- **Base Architecture:** MiniLM-L6-H384-uncased (6 layers, 384 hidden dimension, 12 attention heads)
- **License:** **Apache 2.0**
- **Intended Use in ClaimLens:** Dense vector retrieval over the evidence corpus. Encodes both claims and corpus passages into a shared vector space for cosine similarity search.
- **Maximum Sequence Length:** **256 wordpiece tokens** (inputs exceeding 256 tokens are truncated with warning)
- **Embedding Dimensions:** **384**
- **Hardware Profile:** Optimized for lightweight CPU and edge inference (~23 MB parameter footprint).

### Limitations & Biases
- Truncates passages longer than 256 tokens; passages must be segmented into coherent paragraphs.
- Trained predominantly on English sentence pairs; does not support cross-lingual semantic retrieval.

---

## Model 2: Natural Language Inference Cross-Encoder
- **Model Identifier:** `cross-encoder/nli-deberta-v3-small`
- **Developer / Organization:** Cross-Encoder team / Microsoft (fine-tuned on SNLI + MultiNLI)
- **Model Type:** Sequence classification cross-encoder
- **Base Architecture:** DeBERTa-v3-small (6 layers, 768 hidden dimension, disentangled attention + enhanced mask decoder)
- **License:** **Apache 2.0**
- **Intended Use in ClaimLens:** Stance detection. Evaluates pair relationship: Premise (retrieved evidence passage) and Hypothesis (extracted claim).
- **Label Mapping:** Resolved dynamically at runtime via `model.config.id2label`:
  - `0`: `contradiction`
  - `1`: `entailment`
  - `2`: `neutral`
- **Maximum Sequence Length:** **512 tokens**
- **Critical Dependencies:** Requires `sentencepiece` for DeBERTa subword BPE tokenization.

### Limitations & Biases
- High quadratic latency relative to bi-encoders; therefore applied strictly to the top $K \le 5$ passages selected by RRF.
- Susceptible to negation traps if sentences contain multi-clause conditional hypotheses.

---

## Model 3: Linguistic Analysis & Named Entity Recognition
- **Model Identifier:** `spacy/en_core_web_sm` (v3.8+)
- **Developer / Organization:** Explosion AI
- **Model Type:** Multi-task convolutional neural network / transition-based parser
- **License:** **MIT**
- **Intended Use in ClaimLens:**
  - Sentence boundary segmentation
  - Named entity extraction (GPE, LOC, ORG, PERSON, DATE, QUANTITY)
  - Part-of-speech and syntactic dependency parsing for filtering non-factual statements.

---

# SECTION 2: DATA CARD (EVIDENCE CORPUS)

## Dataset Details
- **Dataset Name:** ClaimLens Local Evidence Corpus
- **Version:** `1.0.0`
- **Location:** `backend/data/corpus/`
- **Manifest:** `backend/data/corpus/manifest.json`
- **Total Documents:** 30 JSON files
- **Total Passages:** 120+ structured text segments
- **Language:** English (`en-US` / standard English)

## Domain & Topic Coverage
1. **Earth & Atmospheric Sciences:** Earth's shape, continental drift, freshwater distribution, CO2 concentrations.
2. **Space & Astronomy:** Apollo Moon missions, planetary definitions, solar orbit cycles, speed of light.
3. **Health & Medicine:** Human body water content, sensory biology, vaccine eradication history, antibiotic resistance.
4. **Geography & Global Demographics:** World population benchmarks, Sahara and Antarctic desert scopes, Mariana Trench depths, Amazon rainforest boundaries.
5. **Physical & Chemical Sciences:** Speed of sound, periodic table elements, DNA double helix structure, photosynthesis equations, gravity accelerations.
6. **Technological History:** History of the Internet and ARPANET, Great Wall space visibility debunking.

## Provenance & Attribution
All documents are sourced directly or synthesized from authoritative public records:
- **Government Agencies:** NASA, WHO, NOAA, USGS, CDC, IPCC.
- **International Institutions:** World Bank, United Nations, International Astronomical Union.
- **Academic References:** Encyclopedia Britannica and peer-reviewed reference works.

## Licensing & Fair Use
- The corpus is constructed solely for non-commercial educational and academic evaluation purposes under Fair Use.
- Each document includes explicit metadata fields: `publisher`, `source_url`, `retrieved_date`, `attribution`, and `license`.

## Update & Maintenance Guidelines
- Additions to the corpus must adhere to the schema specified in `manifest.json`.
- When updating documents, run `python scripts/build_corpus.py` to revalidate counts and refresh precomputed vector embeddings.
