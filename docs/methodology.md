# ClaimLens Scientific & Engineering Methodology

## Official Project Title
**AI-Based Misinformation Detection System Using Natural Language Processing, Information Retrieval and Source Credibility Analysis**

---

## 1. Abstract & Problem Statement

Automated fact-checking and misinformation detection require more than simple text generation: they demand transparent, verifiable, and evidence-grounded decision pipelines. ClaimLens decomposes the verification task into five explicit stages:

1. **Input Normalization & Article Parsing**
2. **Grammar-Aware Claim Extraction**
3. **Hybrid Information Retrieval (BM25 + Dense Semantic RRF)**
4. **Cross-Encoder Natural Language Inference (NLI)**
5. **Deterministic Decision Policy & Source Provenance Analysis**

Every verdict emitted by ClaimLens is directly anchored to specific, citeable text passages with observable similarity and stance confidence scores.

---

## 2. Stage 1: Input Preprocessing & Security Boundary

When text is submitted directly, whitespace is regularized and checked with `langdetect`. To prevent linguistic skew from models fine-tuned on English corpora, non-English inputs are rejected at the API boundary with an explanatory notification.

When a URL is submitted, the backend invokes `SafeFetcher` to mitigate Server-Side Request Forgery (SSRF) and DNS rebinding:
- Only HTTP/HTTPS URLs on standard ports (80, 443, 8080, 8443) are permitted.
- Resolved IP addresses are verified against all private, loopback, link-local, and cloud metadata ranges (`169.254.169.254`).
- Redirects are traversed sequentially, with re-validation of hostnames and IP addresses at each hop.
- `readability-lxml` extracts the core semantic article, filtering away boilerplates, navigation bars, and embedded scripts.

---

## 3. Stage 2: Factual Claim Extraction

Rather than treating every sentence as a checkable claim, ClaimLens filters and ranks sentences using spaCy's `en_core_web_sm` pipeline.

### 3.1 Heuristic Filtering
1. **Questions:** Sentences ending with `?` or matching interrogative patterns (`^(who|what|where|when|why|how|is|are|was|were)\b`) are pruned.
2. **Commands & Imperatives:** Sentences matching imperative verbs (`^(please|let|make|do|don't|remember)\b`) are pruned.
3. **Subjective Opinions:** Sentences matching self-referential cognitive verbs (`\b(I think|I believe|in my opinion|I feel)\b`) are penalized.

### 3.2 Factual Scoring Formulation
Sentences are scored for checkable empirical density via:

$$\text{Score}(s) = \text{clamp}\Big(0.30 + \min(0.20, 0.05 \cdot N_{\text{ent}}) + \min(0.15, 0.05 \cdot N_{\text{num}}) + 0.10 \cdot \mathbb{I}_{\text{date}} + 0.10 \cdot \mathbb{I}_{\text{root\_verb}} - 0.40 \cdot \mathbb{I}_{\text{opinion}}, 0.0, 1.0\Big)$$

Where:
- $N_{\text{ent}}$ is the count of named entities (GPE, LOC, ORG, PERSON).
- $N_{\text{num}}$ is the count of numeric tokens or quantities.
- $\mathbb{I}_{\text{date}}$ is an indicator for temporal tokens.
- $\mathbb{I}_{\text{opinion}}$ is an indicator for opinion markers.

The top $K \le 6$ scored sentences are promoted as candidate claims.

---

## 4. Stage 3: Hybrid Information Retrieval

Evidence retrieval combines sparse keyword matching with dense semantic embeddings to balance exact lexical overlap (such as named entities and dates) with paraphrased semantic intent.

### 4.1 Sparse Retrieval: BM25Okapi
Corpus passages are tokenized, lowercased, and stripped of standard English stopwords. Passages are scored via BM25:

$$\text{BM25}(D, Q) = \sum_{q \in Q} \text{IDF}(q) \cdot \frac{f(q, D) \cdot (k_1 + 1)}{f(q, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$

With default parameters $k_1 = 1.5$ and $b = 0.75$.

### 4.2 Dense Semantic Retrieval: Sentence Transformers
Passages and queries are mapped into a 384-dimensional dense vector space using `sentence-transformers/all-MiniLM-L6-v2`:

$$\mathbf{e}_q = \text{Encoder}(q), \quad \mathbf{e}_d = \text{Encoder}(d)$$

Cosine similarity is computed via dot products over $L_2$-normalized vectors:

$$\text{Sim}(q, d) = \mathbf{e}_q \cdot \mathbf{e}_d$$

### 4.3 Reciprocal Rank Fusion (RRF)
To avoid calibrating disparate score scales (unbounded BM25 scores vs. $[0, 1]$ cosine similarities), rankings are combined using Reciprocal Rank Fusion with smoothing constant $k = 60$:

$$\text{RRF}(d) = \frac{1}{60 + r_{\text{BM25}}(d)} + \frac{1}{60 + r_{\text{dense}}(d)}$$

### 4.4 Lexical Deduplication
Passages with Jaccard word-set similarity $\ge 0.85$ are pruned, retaining the higher-ranked occurrence to maximize evidence diversity across the top 5 passages.

---

## 5. Stage 4: Cross-Encoder Natural Language Inference (NLI)

Selected evidence passages and claims are fed to `cross-encoder/nli-deberta-v3-small`. Unlike bi-encoders, the cross-encoder jointly attends over both sequences simultaneously:

$$[\text{CLS}] \circ \text{Evidence Passage} \circ [\text{SEP}] \circ \text{Claim Statement} \circ [\text{SEP}]$$

Softmax over the output logits yields three probability distributions:
- $P(\text{Entailment})$: Evidence logically supports the claim.
- $P(\text{Contradiction})$: Evidence logically refutes the claim.
- $P(\text{Neutral})$: Evidence neither proves nor disproves the claim.

*Note:* Label indices (`id2label`) are inspected dynamically from the model configuration at runtime rather than hardcoded, preventing label inversion bugs.

---

## 6. Stage 5: Decision Policy & Credibility Analysis

### 6.1 Policy Rules & Thresholds

| Condition | Outcome | Explanation |
| :--- | :--- | :--- |
| Any passage $P(\text{Entailment}) \ge 0.65$ AND no passage $P(\text{Contradiction}) \ge 0.65$ | **Supported** | Cited evidence verifies the empirical assertion. |
| Any passage $P(\text{Contradiction}) \ge 0.65$ AND no passage $P(\text{Entailment}) \ge 0.65$ | **Contradicted** | Cited evidence refutes the empirical assertion. |
| At least one passage $P(\text{Entailment}) \ge 0.65$ AND at least one passage $P(\text{Contradiction}) \ge 0.65$ | **Conflicting Evidence** | Multiple authoritative sources provide contradictory stances. |
| No passage exceeds $0.65$ confidence OR retrieval score $< 0.25$ | **Insufficient Evidence** | Corpus lacks conclusive data on this specific claim. |
| Sentence lacks empirical assertion | **Not Checkable** | Sentence is a subjective opinion, greeting, or command. |

### 6.2 Source Provenance Framework

ClaimLens rejects subjective "trust scores" (e.g., "78% trustworthy"), adopting the qualitative **Source Provenance Framework**:
- **Documented Provenance:** Source domain is verified in the institutional registry (`PUBLISHER_REGISTRY`), has a public corrections and editorial policy, and exhibits demonstrated domain expertise.
- **Partially Documented:** Source has identifiable author, publication date, and registered web domain, but lacks documented editorial policies.
- **Unknown Provenance:** Unattributed or self-published web pages lacking editorial disclosure.
