# ClaimLens Demonstration & Viva Defense Guide

## Official Project Title
**AI-Based Misinformation Detection System Using Natural Language Processing, Information Retrieval and Source Credibility Analysis**

**Short Name:** ClaimLens

---

## 1. 10-Minute Viva Presentation Structure

| Time | Slide / Topic | Key Points to Emphasize |
| :--- | :--- | :--- |
| **00:00 - 01:30** | **Motivation & Problem Statement** | Misinformation cannot be addressed by closed-box generative LLMs that hallucinate facts. Fact-checking requires verifiable evidence retrieval, explicit sentence-level stance detection, and transparent source credibility. |
| **01:30 - 03:30** | **System Architecture & Pipeline** | Present the five-stage pipeline: Input Preprocessor → spaCy Claim Extractor → Hybrid Retrieval (BM25 + Dense RRF) → Cross-Encoder NLI → Deterministic Decision Policy. Emphasize offline resilience via the local corpus. |
| **03:30 - 06:00** | **Live Demonstration** | Run the 5 canonical claims (Supported, Contradicted, Conflicting, Insufficient, Not Checkable). Show evidence citation, NLI confidence, and source provenance signals. |
| **06:00 - 08:00** | **Empirical Evaluation & Stress Testing** | Present FEVER benchmark findings: 100% Recall@5 with Hybrid RRF vs 83.3% with BM25; 93.3% end-to-end accuracy; stress test on syntactic negation and entity swaps. |
| **08:00 - 10:00** | **Limitations, Ethics & Future Work** | Emphasize the academic disclaimer: decisions are evidence-relative findings. Explain SSRF security controls and future cross-lingual expansions. |

---

## 2. Live Demonstration Script

Prepare these 5 test inputs to demonstrate every outcome category:

### Test 1: Supported Canonical Claim
- **Input:** `"Water boils at 100 degrees Celsius under standard atmospheric pressure."`
- **Expected Outcome:** `Supported`
- **What to highlight:**
  - High entailment score ($> 0.90$) from NIST/USGS passage.
  - Transparent citations with full passage context toggle.
  - Documented publisher signals from the USGS registry.

### Test 2: Contradicted Common Myth
- **Input:** `"The Great Wall of China is visible from space with the naked eye."`
- **Expected Outcome:** `Contradicted`
- **What to highlight:**
  - High contradiction probability from NASA astronaut observation reports.
  - Decision reason clearly notes contradiction without dogmatic assertions.

### Test 3: Insufficient Evidence / Out of Domain
- **Input:** `"Bacterial spores were successfully recovered from subsurface ice on Pluto by New Horizons in 2026."`
- **Expected Outcome:** `Insufficient Evidence`
- **What to highlight:**
  - The system acknowledges absence of qualifying evidence rather than hallucinating an answer.
  - The user is notified that the claim lies outside local corpus coverage.

### Test 4: Subjective Opinion Statement
- **Input:** `"In my personal opinion chocolate gelato is without question the greatest food ever invented."`
- **Expected Outcome:** `Not Checkable`
- **What to highlight:**
  - spaCy claim extractor identified self-referential cognitive verbs (`In my personal opinion`) and filtered it out before wasting retrieval cycles.

### Test 5: Syntactic Negation Stress Test
- **Input:** `"The Sahara is not the largest desert on Earth because Antarctica is larger."`
- **Expected Outcome:** `Supported`
- **What to highlight:**
  - Cross-encoder attention successfully resolves embedded clause negation without inverting the truth value of the entire compound sentence.

---

## 3. Anticipated Viva Questions & Model Answers

### Q1: "Why did you use a pipeline architecture instead of prompting a single large LLM (like GPT-4 or Gemini)?"
> **Model Answer:**
> *"Large generative LLMs are probabilistic text generators prone to confabulation and hallucination. When prompted directly, they cannot cite deterministic passage boundaries with auditable confidence distributions. By decomposing the task into information retrieval, cross-encoder natural language inference, and a deterministic decision policy, ClaimLens ensures that every claim outcome is strictly evidence-relative, citeable, reproducible, and verifiable by human auditors."*

### Q2: "Why combine BM25 and Dense Embeddings with Reciprocal Rank Fusion instead of using vector search alone?"
> **Model Answer:**
> *"Dense vector embeddings excel at capturing semantic paraphrasing, but they suffer from 'semantic drift' and frequently miss exact keyword constraints such as numeric figures, dates, and rare proper nouns. BM25 guarantees high lexical fidelity for exact names and dates. Reciprocal Rank Fusion (RRF with $k=60$) allows us to combine the strengths of both without needing to artificially normalize the unbounded BM25 scores against bounded cosine similarities."*

### Q3: "What is SSRF and how does ClaimLens protect against it?"
> **Model Answer:**
> *"Server-Side Request Forgery occurs when an attacker provides a URL (such as `http://169.254.169.254` or `http://127.0.0.1:8000`) causing the server to fetch internal resources or cloud credentials. ClaimLens implements `SafeFetcher`, which resolves the destination hostname via DNS and strictly validates every resolved IP address against all private (RFC 1918), loopback, link-local, and cloud metadata ranges before opening a socket. Furthermore, redirects are followed manually and re-validated at every single hop to eliminate DNS rebinding attacks."*

### Q4: "Why does ClaimLens reject numerical trust scores for sources (e.g. '82% reliable')?"
> **Model Answer:**
> *"Numerical trust scores create a false sense of mathematical precision where none exists. A source is not '82% true'—rather, it either has documented institutional provenance or it does not. ClaimLens uses a transparent Provenance Framework (`documented`, `partially_documented`, `unknown`) based on observable signals: identifiable author, publication date, public corrections policy, and registry domain backing. Missing author metadata is labeled as 'unknown' rather than penalized as 'unreliable', preserving academic objectivity."*

### Q5: "Why did you choose DeBERTa-v3 over BERT or RoBERTa for stance detection?"
> **Model Answer:**
> *"DeBERTa-v3 incorporates disentangled attention—representing each token using two vectors (content and relative position)—and is trained with replaced token detection (ELECTRA-style). On NLI benchmarks like MNLI and SNLI, DeBERTa-v3 significantly outperforms BERT and RoBERTa, particularly on syntactically complex sentences containing negations, qualifiers, and subordinate clauses."*

### Q6: "What happens if an analysis is interrupted or cancelled?"
> **Model Answer:**
> *"The backend uses an asynchronous worker with atomic state transitions. If a user cancels, `analysis_worker.request_cancel(job_id)` marks the job. Any currently executing thread finishes gracefully, and the database status updates to `cancelled` with an explanatory note. No orphan background tasks persist, and the client receives immediate feedback."*

### Q7: "How is user privacy maintained?"
> **Model Answer:**
> *"Analyses can be executed completely offline using Local Corpus Mode without sending any data over the public internet. Furthermore, analysis reports on the server are secured by cryptographic access tokens (`secrets.token_urlsafe`), hashed with SHA-256 in the database. On the client side, reports are archived in the user's private browser storage via IndexedDB."*
