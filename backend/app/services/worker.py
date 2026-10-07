"""Background analysis worker for ClaimLens.

Orchestrates the complete verification pipeline:
input processing → claim extraction → evidence retrieval →
stance detection → decision policy → report generation.
"""
import asyncio
import hashlib
import logging
import time
import uuid
import re
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Optional, Any

from app.config import get_settings
from app.schemas.enums import AnalysisStatus, ClaimOutcome, EvidenceMode, EvidenceStance

logger = logging.getLogger(__name__)

# Single thread pool for CPU-bound model inference
_executor = ThreadPoolExecutor(max_workers=1)


class AnalysisWorker:
    """Processes analysis jobs through the full verification pipeline."""

    def __init__(self) -> None:
        self._cancelled_jobs: set[str] = set()

    def request_cancel(self, job_id: str) -> None:
        """Mark a job for cancellation. Currently running model calls finish first."""
        self._cancelled_jobs.add(job_id)
        logger.info(f'Cancellation requested for job {job_id}')

    def _is_cancelled(self, job_id: str) -> bool:
        return job_id in self._cancelled_jobs

    async def process_job(
        self,
        job_id: str,
        input_text: str,
        input_url: Optional[str],
        evidence_mode: str,
        update_callback,
    ) -> dict:
        """Run the full analysis pipeline.

        Args:
            job_id: Unique job identifier
            input_text: The text to analyze
            input_url: Optional article URL
            evidence_mode: 'local' or 'live'
            update_callback: async callable(job_id, stage, status, partial_report)

        Returns:
            Complete report dictionary
        """
        from app.services.model_manager import model_manager
        settings = get_settings()
        report: dict[str, Any] = {
            'input_summary': input_text[:200] + ('...' if len(input_text) > 200 else ''),
            'analysis_date': datetime.now(timezone.utc).isoformat(),
            'evidence_mode': evidence_mode,
            'corpus_version': None,
            'model_versions': model_manager.model_versions,
            'claims': [],
            'coverage_warnings': [],
        }

        try:
            # Stage 1: Input validation
            await update_callback(job_id, 'validating', 'running', None)
            await asyncio.sleep(0.3)
            if self._is_cancelled(job_id):
                return await self._handle_cancel(job_id, report, update_callback)

            processed_text = input_text.strip()
            if not processed_text:
                raise ValueError('Input text is empty after processing')

            # Stage 2: Claim extraction
            await update_callback(job_id, 'extracting', 'running', None)
            await asyncio.sleep(0.35)
            if self._is_cancelled(job_id):
                return await self._handle_cancel(job_id, report, update_callback)

            from app.services.claim_extractor import ClaimExtractor
            extractor = ClaimExtractor(model_manager.nlp)

            claims = await asyncio.get_event_loop().run_in_executor(
                _executor,
                lambda: extractor.extract_claims(processed_text, settings.MAX_CLAIMS_PER_ANALYSIS)
            )
            await asyncio.sleep(0.2)

            if not claims:
                report['claims'] = [{
                    'id': 'claim-1',
                    'claim_text': processed_text[:500],
                    'original_sentence': processed_text[:500],
                    'char_start': 0,
                    'char_end': min(len(processed_text), 500),
                    'outcome': 'not_checkable',
                    'reason': 'No factual propositions suitable for verification were identified in the input text.',
                    'evidence': [],
                    'linguistic_features': {},
                }]
                await update_callback(job_id, 'completed', 'completed', report)
                return report

            if model_manager.nlp:
                total_sentences = len(list(model_manager.nlp(processed_text).sents))
            else:
                total_sentences = len([s for s in re.split(r'(?<=[.!?])\s+', processed_text) if s.strip()]) or len(claims)
            if len(claims) < total_sentences:
                report['coverage_warnings'].append(
                    f'Selected {len(claims)} of {total_sentences} sentences for verification. '
                    f'Statements were selected based on factual-claim likelihood scoring.'
                )

            # Stage 3: Evidence retrieval
            await update_callback(job_id, 'retrieving', 'running', None)
            if self._is_cancelled(job_id):
                return await self._handle_cancel(job_id, report, update_callback)

            evidence_results = await self._retrieve_evidence(
                claims, evidence_mode, settings, report
            )

            # Stage 4: Stance detection and decision
            await update_callback(job_id, 'comparing', 'running', None)
            if self._is_cancelled(job_id):
                return await self._handle_cancel(job_id, report, update_callback)

            claim_results = await self._evaluate_claims(
                claims, evidence_results, settings, report
            )
            report['claims'] = claim_results

            # Stage 5: Finalize report
            await update_callback(job_id, 'preparing', 'running', None)
            await asyncio.sleep(0.4)
            await update_callback(job_id, 'completed', 'completed', report)

            return report

        except asyncio.CancelledError:
            return await self._handle_cancel(job_id, report, update_callback)
        except Exception as e:
            logger.error(f'Job {job_id} failed: {e}', exc_info=True)
            report['coverage_warnings'].append(f'Analysis failed: {str(e)}')
            await update_callback(job_id, 'failed', 'failed', report)
            raise

        finally:
            self._cancelled_jobs.discard(job_id)

    async def _handle_cancel(self, job_id: str, report: dict, update_callback) -> dict:
        """Handle job cancellation."""
        self._cancelled_jobs.discard(job_id)
        report['coverage_warnings'].append('Analysis was cancelled by user.')
        await update_callback(job_id, 'cancelled', 'cancelled', report)
        return report

    async def _retrieve_evidence(
        self,
        claims,
        evidence_mode: str,
        settings,
        report: dict,
    ) -> dict:
        """Retrieve evidence for all claims from the selected source."""
        from app.services.retrieval.corpus import CorpusLoader
        from app.services.retrieval.bm25 import BM25Retriever
        from app.services.retrieval.semantic import SemanticRetriever
        from app.services.retrieval.fusion import select_evidence
        from app.services.model_manager import model_manager

        results: dict[str, list] = {}

        if evidence_mode == 'local':
            # Load corpus
            corpus = CorpusLoader(settings.CORPUS_DIR)
            corpus.load()

            if not corpus.is_loaded or not corpus.passages:
                report['coverage_warnings'].append('Local corpus could not be loaded.')
                return results

            report['corpus_version'] = corpus.version
            passage_texts = corpus.get_passage_texts()

            # Build BM25 index
            bm25 = BM25Retriever()
            bm25.build_index(passage_texts)

            # Build semantic index
            semantic = SemanticRetriever(settings.MODEL_CACHE_DIR)
            semantic.set_encoder(model_manager.encoder)

            await asyncio.get_event_loop().run_in_executor(
                _executor,
                lambda: semantic.build_index(passage_texts, corpus.version)
            )

            # Retrieve for each claim
            for claim in claims:
                query = claim.claim_text

                bm25_results = bm25.search(query, top_k=20)
                semantic_results = await asyncio.get_event_loop().run_in_executor(
                    _executor,
                    lambda q=query: semantic.search(q, top_k=20)
                )

                selected = select_evidence(
                    bm25_results, semantic_results,
                    passage_texts,
                    max_passages=settings.MAX_EVIDENCE_PER_CLAIM,
                )

                # Map indices to passage objects
                evidence_passages = []
                for idx, rrf_score in selected:
                    if idx < len(corpus.passages):
                        passage = corpus.passages[idx]
                        evidence_passages.append({
                            'passage': passage,
                            'relevance_score': rrf_score,
                        })

                results[claim.claim_id] = evidence_passages

        elif evidence_mode in ('live', 'auto', 'hybrid'):
            from app.services.providers.open_search import OpenSearchProvider
            from app.services.providers.brave_search import BraveSearchProvider
            from app.services.providers.factcheck import GoogleFactCheckProvider
            from app.services.retrieval.corpus import Passage
            from app.services.retrieval.fusion import jaccard_similarity

            # 1. Load local corpus
            corpus = CorpusLoader(settings.CORPUS_DIR)
            corpus.load()
            passage_texts = corpus.get_passage_texts() if corpus.is_loaded else []

            bm25 = None
            semantic = None
            if passage_texts:
                report['corpus_version'] = corpus.version
                bm25 = BM25Retriever()
                bm25.build_index(passage_texts)

                if model_manager.encoder:
                    semantic = SemanticRetriever(settings.MODEL_CACHE_DIR)
                    semantic.set_encoder(model_manager.encoder)
                    await asyncio.get_event_loop().run_in_executor(
                        _executor,
                        lambda: semantic.build_index(passage_texts, corpus.version)
                    )

            open_search = OpenSearchProvider()
            brave = BraveSearchProvider(settings.BRAVE_API_KEY)
            factcheck = GoogleFactCheckProvider(settings.GOOGLE_FACTCHECK_API_KEY)

            for claim in claims:
                query = claim.claim_text
                candidates = []

                # A. Local corpus retrieval
                if bm25 and semantic:
                    bm25_res = bm25.search(query, top_k=10)
                    semantic_results = await asyncio.get_event_loop().run_in_executor(
                        _executor,
                        lambda q=query: semantic.search(q, top_k=10)
                    )
                    selected = select_evidence(
                        bm25_res, semantic_results,
                        passage_texts,
                        max_passages=5,
                    )
                    for idx, norm_rel in selected:
                        if idx < len(corpus.passages):
                            candidates.append({
                                'passage': corpus.passages[idx],
                                'relevance_score': norm_rel,
                            })

                # B. Free live open web search (DuckDuckGo - no API key needed)
                try:
                    open_items = await asyncio.get_event_loop().run_in_executor(
                        _executor,
                        lambda q=query: open_search.search(q, max_results=settings.MAX_EVIDENCE_PER_CLAIM)
                    )
                    for idx, item in enumerate(open_items):
                        p = Passage(
                            passage_id=f"web-{uuid.uuid4().hex[:8]}",
                            doc_id=f"web-{idx+1}",
                            title=item.title,
                            publisher=item.publisher or "Web Source",
                            source_url=item.url,
                            retrieved_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                            publication_date=None,
                            text=item.snippet,
                            content_hash=hashlib.sha256(item.snippet.encode('utf-8')).hexdigest()[:16],
                            attribution=item.publisher or "Web Source",
                            license="Public Web",
                            passage_index=idx,
                        )
                        candidates.append({
                            'passage': p,
                            'relevance_score': round(max(0.60, 0.95 - (idx * 0.05)), 4),
                        })
                except Exception as e:
                    logger.warning(f"Free web search failed for claim '{query}': {e}")

                # C. Google Fact Check if configured
                if factcheck.is_configured:
                    try:
                        fc_items = await factcheck.search(query, page_size=3)
                        for fc_item in fc_items:
                            for rev in fc_item.reviews:
                                p = Passage(
                                    passage_id=f"fc-{uuid.uuid4().hex[:8]}",
                                    doc_id=f"fc-{rev.publisher_name.lower().replace(' ', '-')}",
                                    title=rev.title or f"Fact Check by {rev.publisher_name}",
                                    publisher=rev.publisher_name,
                                    source_url=rev.url,
                                    retrieved_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                                    publication_date=rev.review_date,
                                    text=f"Rating: {rev.textual_rating}. Claim: {fc_item.claim_text}. Fact check review: {rev.title}",
                                    content_hash=hashlib.sha256(rev.title.encode('utf-8')).hexdigest()[:16],
                                    attribution=rev.publisher_name,
                                    license="Fair Use / Fact Check Review",
                                    passage_index=0,
                                )
                                candidates.append({
                                    'passage': p,
                                    'relevance_score': 0.90,
                                })
                    except Exception as e:
                        logger.warning(f"Google FactCheck search failed: {e}")

                # D. Brave Search if configured
                if brave.is_configured:
                    try:
                        search_items = await brave.search(query, count=settings.MAX_EVIDENCE_PER_CLAIM)
                        for idx, item in enumerate(search_items):
                            passage_text = item.description
                            if item.extra_snippets:
                                passage_text += " " + " ".join(item.extra_snippets[:2])
                            p = Passage(
                                passage_id=f"brave-{uuid.uuid4().hex[:8]}",
                                doc_id=f"brave-{idx+1}",
                                title=item.title,
                                publisher=item.publisher or "Web Source",
                                source_url=item.url,
                                retrieved_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                                publication_date=item.page_age,
                                text=passage_text.strip(),
                                content_hash=hashlib.sha256(passage_text.encode('utf-8')).hexdigest()[:16],
                                attribution=item.publisher or item.url,
                                license="Web Public",
                                passage_index=idx,
                            )
                            candidates.append({
                                'passage': p,
                                'relevance_score': round(max(0.60, 0.90 - (idx * 0.05)), 4),
                            })
                    except Exception as e:
                        logger.warning(f"Brave search failed: {e}")

                # E. Semantic reranking using Sentence-Transformers if available
                if model_manager.encoder and candidates:
                    try:
                        claim_emb = await asyncio.get_event_loop().run_in_executor(
                            _executor,
                            lambda q=query: model_manager.encoder.encode(q)
                        )
                        c_norm = np.linalg.norm(claim_emb)
                        for cand in candidates:
                            p_text = cand['passage'].text
                            p_emb = await asyncio.get_event_loop().run_in_executor(
                                _executor,
                                lambda t=p_text: model_manager.encoder.encode(t)
                            )
                            p_norm = np.linalg.norm(p_emb)
                            if c_norm > 0 and p_norm > 0:
                                cos_sim = float(np.dot(claim_emb, p_emb) / (c_norm * p_norm))
                                cand['relevance_score'] = round(0.4 * cand['relevance_score'] + 0.6 * max(0.0, cos_sim), 4)
                    except Exception as e:
                        logger.warning(f"Semantic reranking failed: {e}")

                # F. Sort candidates by relevance score descending
                candidates.sort(key=lambda x: x['relevance_score'], reverse=True)

                # G. Deduplicate using Jaccard similarity
                unique_passages = []
                for cand in candidates:
                    is_dup = False
                    for u in unique_passages:
                        if jaccard_similarity(cand['passage'].text, u['passage'].text) >= 0.85:
                            is_dup = True
                            break
                    if not is_dup:
                        unique_passages.append(cand)

                results[claim.claim_id] = unique_passages[:settings.MAX_EVIDENCE_PER_CLAIM]

        return results

    async def _evaluate_claims(
        self,
        claims,
        evidence_results: dict,
        settings,
        report: dict,
    ) -> list[dict]:
        """Evaluate stance and make decisions for each claim."""
        from app.services.evidence.stance import StanceDetector
        from app.services.evidence.policy import DecisionPolicy, EvidenceAssessment
        from app.services.source_analysis import SourceAnalyzer
        from app.services.model_manager import model_manager

        # Initialize components
        stance_detector = None
        if model_manager.nli_model and model_manager.nli_tokenizer:
            stance_detector = StanceDetector(
                model_manager.nli_model,
                model_manager.nli_tokenizer,
                model_manager.nli_label_map,
            )

        policy = DecisionPolicy(
            entailment_threshold=settings.ENTAILMENT_THRESHOLD,
            contradiction_threshold=settings.CONTRADICTION_THRESHOLD,
            min_relevance_score=settings.MIN_RELEVANCE_SCORE,
        )

        source_analyzer = SourceAnalyzer()
        claim_results: list[dict] = []

        for claim in claims:
            evidence_data = evidence_results.get(claim.claim_id, [])
            assessments: list[EvidenceAssessment] = []
            evidence_items: list[dict] = []

            for ev in evidence_data:
                passage = ev['passage']
                relevance_score = ev['relevance_score']

                # Run NLI stance detection
                if stance_detector:
                    stance_result = await asyncio.get_event_loop().run_in_executor(
                        _executor,
                        lambda p=passage.text, c=claim.claim_text: stance_detector.predict(p, c)
                    )

                    # Assess this evidence
                    assessment = policy.assess_evidence(
                        passage_id=passage.passage_id,
                        relevance_score=relevance_score,
                        entailment_score=stance_result.entailment,
                        contradiction_score=stance_result.contradiction,
                        neutral_score=stance_result.neutral,
                    )
                    assessments.append(assessment)

                    # Determine stance label for display
                    if assessment.stance_category == 'supports':
                        stance_label = 'supports'
                    elif assessment.stance_category == 'contradicts':
                        stance_label = 'contradicts'
                    else:
                        stance_label = 'neutral'

                    stance_scores = {
                        'entailment': stance_result.entailment,
                        'contradiction': stance_result.contradiction,
                        'neutral': stance_result.neutral,
                    }
                else:
                    stance_label = 'neutral'
                    stance_scores = {'entailment': 0, 'contradiction': 0, 'neutral': 1}
                    assessment = policy.assess_evidence(
                        passage_id=passage.passage_id,
                        relevance_score=relevance_score,
                        entailment_score=0, contradiction_score=0, neutral_score=1,
                    )
                    assessments.append(assessment)

                # Source credibility
                cred = source_analyzer.analyze(
                    url=passage.source_url,
                    publisher=passage.publisher,
                    publication_date=passage.publication_date,
                    title=passage.title,
                )

                evidence_items.append({
                    'id': passage.passage_id,
                    'doc_id': passage.doc_id,
                    'title': passage.title,
                    'publisher': passage.publisher,
                    'url': passage.source_url,
                    'publication_date': passage.publication_date,
                    'excerpt': passage.text[:500],
                    'full_context': passage.text,
                    'stance': stance_label,
                    'stance_scores': stance_scores,
                    'relevance_score': relevance_score,
                    'source_credibility': {
                        'provenance_category': cred.provenance_category,
                        'signals': [
                            {
                                'name': s.name,
                                'value': s.value,
                                'status': s.status,
                                'supporting_url': s.supporting_url,
                                'reason': s.reason,
                            }
                            for s in cred.signals
                        ],
                    },
                })

            # Make decision
            decision = policy.decide(assessments)

            claim_result = {
                'id': claim.claim_id,
                'claim_text': claim.claim_text,
                'original_sentence': claim.original_sentence,
                'char_start': claim.char_start,
                'char_end': claim.char_end,
                'outcome': decision.outcome,
                'reason': decision.reason,
                'evidence': evidence_items,
                'linguistic_features': {
                    'entities': claim.entities,
                    'dates': claim.dates,
                    'numbers': claim.numbers,
                    'noun_phrases': claim.noun_phrases,
                    'has_negation': claim.has_negation,
                    'has_qualifier': claim.has_qualifier,
                    'has_attribution': claim.has_attribution,
                },
            }
            claim_results.append(claim_result)

        return claim_results


# Singleton worker
analysis_worker = AnalysisWorker()