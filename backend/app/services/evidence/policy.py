"""Decision policy for mapping evidence stance to claim outcomes.

Implements configurable thresholds and rules for determining
whether a claim is supported, contradicted, conflicting, or insufficient.
"""
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class EvidenceAssessment:
    """Assessment of a single evidence passage for a claim."""
    passage_id: str
    relevance_score: float
    stance_label: str  # 'entailment', 'contradiction', 'neutral'
    entailment_score: float
    contradiction_score: float
    neutral_score: float
    entity_match: bool = True
    date_match: bool = True
    is_qualifying: bool = False  # meets all thresholds
    stance_category: str = 'neutral'  # 'supports', 'contradicts', 'context_only'


@dataclass
class ClaimDecision:
    """Final decision for a claim based on all evidence."""
    outcome: str  # 'supported', 'contradicted', 'conflicting', 'insufficient', 'not_checkable'
    reason: str
    supporting_count: int = 0
    contradicting_count: int = 0
    neutral_count: int = 0
    assessments: list[EvidenceAssessment] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class DecisionPolicy:
    """Maps evidence stance scores to claim outcomes.

    Thresholds are provisional and should be validated against
    held-out examples before being considered calibrated.
    """

    def __init__(
        self,
        entailment_threshold: float = 0.65,
        contradiction_threshold: float = 0.65,
        min_relevance_score: float = 0.25,
    ) -> None:
        self.entailment_threshold = entailment_threshold
        self.contradiction_threshold = contradiction_threshold
        self.min_relevance_score = min_relevance_score

    def assess_evidence(
        self,
        passage_id: str,
        relevance_score: float,
        entailment_score: float,
        contradiction_score: float,
        neutral_score: float,
        entity_match: bool = True,
        date_match: bool = True,
    ) -> EvidenceAssessment:
        """Assess a single evidence passage for a claim."""
        assessment = EvidenceAssessment(
            passage_id=passage_id,
            relevance_score=relevance_score,
            stance_label='neutral',
            entailment_score=entailment_score,
            contradiction_score=contradiction_score,
            neutral_score=neutral_score,
            entity_match=entity_match,
            date_match=date_match,
        )

        # Check if evidence is relevant enough
        if relevance_score < self.min_relevance_score:
            assessment.stance_category = 'context_only'
            assessment.is_qualifying = False
            return assessment

        # Check entity and date alignment
        if not entity_match or not date_match:
            assessment.stance_category = 'context_only'
            assessment.is_qualifying = False
            assessment.stance_label = 'neutral'
            return assessment

        # Determine stance
        if entailment_score >= self.entailment_threshold:
            assessment.stance_label = 'entailment'
            assessment.stance_category = 'supports'
            assessment.is_qualifying = True
        elif contradiction_score >= self.contradiction_threshold:
            assessment.stance_label = 'contradiction'
            assessment.stance_category = 'contradicts'
            assessment.is_qualifying = True
        else:
            assessment.stance_label = 'neutral'
            assessment.stance_category = 'context_only'
            assessment.is_qualifying = False

        return assessment

    def decide(
        self,
        assessments: list[EvidenceAssessment],
        is_checkable: bool = True,
    ) -> ClaimDecision:
        """Make a final decision based on all evidence assessments.

        Decision rules:
        - not_checkable: no factual proposition identified
        - supported: qualifying support, no qualifying contradiction
        - contradicted: qualifying contradiction, no qualifying support
        - conflicting: both qualifying support and contradiction
        - insufficient: no qualifying evidence either way
        """
        if not is_checkable:
            return ClaimDecision(
                outcome='not_checkable',
                reason='No factual proposition suitable for verification was identified in this text.',
                assessments=assessments,
            )

        supporting = [a for a in assessments if a.is_qualifying and a.stance_category == 'supports']
        contradicting = [a for a in assessments if a.is_qualifying and a.stance_category == 'contradicts']
        context_only = [a for a in assessments if a.stance_category == 'context_only']

        warnings: list[str] = []

        if not assessments:
            return ClaimDecision(
                outcome='insufficient',
                reason='No evidence was retrieved for this claim. This does not mean the claim is false — it may be outside the corpus coverage.',
                warnings=['No evidence retrieved'],
            )

        if supporting and contradicting:
            return ClaimDecision(
                outcome='conflicting',
                reason=self._build_conflicting_reason(supporting, contradicting),
                supporting_count=len(supporting),
                contradicting_count=len(contradicting),
                neutral_count=len(context_only),
                assessments=assessments,
                warnings=warnings,
            )

        if supporting and not contradicting:
            return ClaimDecision(
                outcome='supported',
                reason=self._build_supported_reason(supporting),
                supporting_count=len(supporting),
                contradicting_count=0,
                neutral_count=len(context_only),
                assessments=assessments,
                warnings=warnings,
            )

        if contradicting and not supporting:
            return ClaimDecision(
                outcome='contradicted',
                reason=self._build_contradicted_reason(contradicting),
                supporting_count=0,
                contradicting_count=len(contradicting),
                neutral_count=len(context_only),
                assessments=assessments,
                warnings=warnings,
            )

        # Neither supporting nor contradicting
        return ClaimDecision(
            outcome='insufficient',
            reason=self._build_insufficient_reason(assessments),
            supporting_count=0,
            contradicting_count=0,
            neutral_count=len(context_only),
            assessments=assessments,
            warnings=warnings,
        )

    def _build_supported_reason(self, supporting: list[EvidenceAssessment]) -> str:
        count = len(supporting)
        return (
            f"This claim is supported by {count} evidence passage(s). "
            f"The retrieved evidence directly aligns with and confirms the statement."
        )

    def _build_contradicted_reason(self, contradicting: list[EvidenceAssessment]) -> str:
        count = len(contradicting)
        return (
            f"This claim is contradicted by {count} evidence passage(s). "
            f"The retrieved evidence presents authoritative information that refutes the statement."
        )

    def _build_conflicting_reason(
        self, supporting: list[EvidenceAssessment], contradicting: list[EvidenceAssessment]
    ) -> str:
        return (
            f"This claim has conflicting evidence: {len(supporting)} source(s) support it "
            f"while {len(contradicting)} source(s) contradict it. "
            f"The claim may require more specific context, temporal qualification, or scientific consensus."
        )

    def _build_insufficient_reason(self, assessments: list[EvidenceAssessment]) -> str:
        if not assessments:
            return "No evidence passages were retrieved for this claim."
        return (
            f"Retrieved {len(assessments)} passage(s), but none met the confidence threshold "
            f"to be classified as clearly supporting or contradicting. "
            f"The evidence is either topically related but not decisive, or insufficient in coverage."
        )