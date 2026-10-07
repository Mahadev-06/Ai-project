import { Layers, ShieldCheck, Cpu, Sliders, AlertCircle } from 'lucide-react';

export default function MethodologyPage() {
  return (
    <div className="max-w-4xl mx-auto py-8 space-y-12">
      {/* Title Header */}
      <div className="border-b border-charcoal/15 pb-8">
        <span className="text-xs font-mono uppercase tracking-widest text-charcoal/60 font-semibold">
          Academic Documentation & System Specification
        </span>
        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-charcoal tracking-tight mt-2 mb-3">
          AI-Based Misinformation Detection System Using Natural Language Processing, Information Retrieval and Source Credibility Analysis
        </h1>
        <p className="text-sm font-medium text-charcoal/70">
          Application Codename: <strong>ClaimLens</strong> • University AI Capstone Project
        </p>
      </div>

      {/* Mandatory Academic Disclaimer */}
      <div className="p-5 border border-charcoal/20 bg-charcoal/5 rounded-lg text-sm text-charcoal/80 space-y-2">
        <div className="flex items-center gap-2 font-bold text-charcoal">
          <AlertCircle size={18} /> Foundational Project Disclaimer
        </div>
        <p className="leading-relaxed">
          This system assists human evidence review. It can miss context, retrieve incomplete information,
          or make classification errors. Results are evidence-relative findings derived strictly from the
          corpus or search results consulted, not guarantees of absolute or universal truth.
        </p>
      </div>

      {/* Core Pipeline Architecture */}
      <div className="space-y-6">
        <h2 className="text-2xl font-serif font-bold text-charcoal flex items-center gap-2.5">
          <Layers size={22} /> Five-Stage AI Pipeline
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs">
          <div className="p-3.5 border border-charcoal/15 rounded-md bg-white space-y-1">
            <span className="font-mono text-charcoal/50 font-semibold">STAGE 1</span>
            <h3 className="font-bold text-charcoal text-sm">Input Processor</h3>
            <p className="text-charcoal/70">
              Whitespace normalization, language detection (English only), SSRF-protected article extraction.
            </p>
          </div>

          <div className="p-3.5 border border-charcoal/15 rounded-md bg-white space-y-1">
            <span className="font-mono text-charcoal/50 font-semibold">STAGE 2</span>
            <h3 className="font-bold text-charcoal text-sm">Claim Extraction</h3>
            <p className="text-charcoal/70">
              spaCy sentence segmentation, named entity recognition, grammatical role filtering.
            </p>
          </div>

          <div className="p-3.5 border border-charcoal/15 rounded-md bg-white space-y-1">
            <span className="font-mono text-charcoal/50 font-semibold">STAGE 3</span>
            <h3 className="font-bold text-charcoal text-sm">Hybrid Retrieval</h3>
            <p className="text-charcoal/70">
              BM25Okapi + Sentence Transformers dense vectors fused with Reciprocal Rank Fusion (k=60).
            </p>
          </div>

          <div className="p-3.5 border border-charcoal/15 rounded-md bg-white space-y-1">
            <span className="font-mono text-charcoal/50 font-semibold">STAGE 4</span>
            <h3 className="font-bold text-charcoal text-sm">Stance Detection</h3>
            <p className="text-charcoal/70">
              Cross-encoder DeBERTa-v3 NLI: Premise=Evidence, Hypothesis=Claim.
            </p>
          </div>

          <div className="p-3.5 border border-charcoal/15 rounded-md bg-white space-y-1">
            <span className="font-mono text-charcoal/50 font-semibold">STAGE 5</span>
            <h3 className="font-bold text-charcoal text-sm">Decision Policy</h3>
            <p className="text-charcoal/70">
              Threshold evaluation, entity verification, deterministic templates, and credibility signals.
            </p>
          </div>
        </div>
      </div>

      {/* Model Cards & Specifications */}
      <div className="space-y-6">
        <h2 className="text-2xl font-serif font-bold text-charcoal flex items-center gap-2.5">
          <Cpu size={22} /> Model Specifications
        </h2>

        <div className="border border-charcoal/15 rounded-lg overflow-hidden text-xs sm:text-sm">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-charcoal text-ivory">
                <th className="p-3">Component</th>
                <th className="p-3">Model / Library</th>
                <th className="p-3">License</th>
                <th className="p-3">Specifications</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-charcoal/10 bg-white">
              <tr>
                <td className="p-3 font-semibold text-charcoal">Linguistic NLP</td>
                <td className="p-3 font-mono text-xs">spaCy (en_core_web_sm)</td>
                <td className="p-3">MIT</td>
                <td className="p-3 text-charcoal/70">Sentence boundary, POS tagging, NER (GPE, DATE, ORG, PERSON)</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-charcoal">Dense Embeddings</td>
                <td className="p-3 font-mono text-xs">sentence-transformers/all-MiniLM-L6-v2</td>
                <td className="p-3">Apache-2.0</td>
                <td className="p-3 text-charcoal/70">384 dimensions, max 256 wordpiece tokens, normalized cosine scoring</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-charcoal">Sparse Retrieval</td>
                <td className="p-3 font-mono text-xs">rank_bm25 (BM25Okapi)</td>
                <td className="p-3">Apache-2.0</td>
                <td className="p-3 text-charcoal/70">k1=1.5, b=0.75, English stopword pruning</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-charcoal">Natural Language Inference</td>
                <td className="p-3 font-mono text-xs">cross-encoder/nli-deberta-v3-small</td>
                <td className="p-3">Apache-2.0</td>
                <td className="p-3 text-charcoal/70">Softmax logits; label mapping resolved dynamically from model config</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="text-xs text-charcoal/60 italic">
          Note: All pretrained models are utilized as-is without proprietary fine-tuning, ensuring reproducible zero-shot evaluation.
        </p>
      </div>

      {/* Decision Policy Thresholds */}
      <div className="space-y-6">
        <h2 className="text-2xl font-serif font-bold text-charcoal flex items-center gap-2.5">
          <Sliders size={22} /> Decision Policy & Classification Rules
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs sm:text-sm">
          <div className="p-4 border border-charcoal/15 rounded-lg bg-ivory space-y-2">
            <h3 className="font-bold text-charcoal text-sm">Classification Thresholds</h3>
            <ul className="space-y-1 text-charcoal/80">
              <li>• <strong>Entailment Threshold:</strong> 0.65 (evidence supports claim)</li>
              <li>• <strong>Contradiction Threshold:</strong> 0.65 (evidence refutes claim)</li>
              <li>• <strong>Minimum Retrieval Score:</strong> 0.25 (below this, marked as context only)</li>
              <li>• <strong>Deduplication Jaccard Threshold:</strong> 0.85 (prunes near-duplicate passages)</li>
            </ul>
          </div>

          <div className="p-4 border border-charcoal/15 rounded-lg bg-ivory space-y-2">
            <h3 className="font-bold text-charcoal text-sm">Outcome Mapping</h3>
            <ul className="space-y-1 text-charcoal/80">
              <li>• <strong>Supported:</strong> Qualifying support, no qualifying contradiction.</li>
              <li>• <strong>Contradicted:</strong> Qualifying contradiction, no qualifying support.</li>
              <li>• <strong>Conflicting Evidence:</strong> Both qualifying support and contradiction.</li>
              <li>• <strong>Insufficient Evidence:</strong> No retrieved passage exceeds confidence thresholds.</li>
              <li>• <strong>Not Checkable:</strong> No verifiable empirical proposition identified.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Source Credibility Rubric */}
      <div className="space-y-6">
        <h2 className="text-2xl font-serif font-bold text-charcoal flex items-center gap-2.5">
          <ShieldCheck size={22} /> Transparent Source Credibility Rubric
        </h2>

        <div className="p-5 border border-charcoal/15 rounded-lg bg-white space-y-3 text-xs sm:text-sm text-charcoal/80">
          <p className="leading-relaxed">
            Rather than producing opaque, misleading numerical credibility scores (e.g., "78% reliable"),
            ClaimLens reports qualitative <strong>Provenance Categories</strong> based on observable signals:
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
            <div className="p-3 border border-charcoal rounded bg-charcoal text-ivory">
              <span className="font-bold block mb-1">Documented</span>
              <p className="text-xs text-ivory/80">
                Verified institutional publisher in registry with documented editorial policies, corrections procedures, and domain expertise.
              </p>
            </div>

            <div className="p-3 border border-charcoal rounded bg-charcoal/5 text-charcoal">
              <span className="font-bold block mb-1">Partially Documented</span>
              <p className="text-xs text-charcoal/70">
                Source with recognized domain, publication date, and cited author, but without verified registry editorial credentials.
              </p>
            </div>

            <div className="p-3 border border-charcoal/30 border-dashed rounded text-charcoal/80">
              <span className="font-bold block mb-1">Unknown Provenance</span>
              <p className="text-xs text-charcoal/60">
                Aggregated, anonymized, or self-published web pages lacking identifiable publisher or author attribution.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* References */}
      <div className="border-t border-charcoal/15 pt-6 text-xs text-charcoal/60 space-y-2 font-mono">
        <h3 className="font-serif font-bold text-charcoal text-sm not-italic">Key Academic References</h3>
        <p>1. Thorne, J., et al. (2018). FEVER: a large-scale dataset for Fact Extraction and VERification. NAACL-HLT.</p>
        <p>2. Cormack, G. V., Clarke, C. L., & Buettcher, S. (2009). Reciprocal rank fusion outperforms Condorcet and individual machine learning methods. SIGIR.</p>
        <p>3. He, P., Gao, J., & Chen, W. (2021). DeBERTaV3: Improving DeBERTa using ELECTRA-Style Pre-Training with Gradient-Disentangled Embedding. ICLR.</p>
      </div>
    </div>
  );
}
