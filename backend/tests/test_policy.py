"""Unit tests for the Decision Policy engine."""
import pytest
from app.services.evidence.policy import DecisionPolicy, EvidenceAssessment


def test_supported_outcome():
    policy = DecisionPolicy(entailment_threshold=0.65, contradiction_threshold=0.65)
    assessments = [
        policy.assess_evidence(
            passage_id="p1",
            relevance_score=0.8,
            entailment_score=0.85,
            contradiction_score=0.05,
            neutral_score=0.10
        )
    ]
    decision = policy.decide(assessments)
    assert decision.outcome == "supported"
    assert "supported by 1 evidence passage" in decision.reason


def test_contradicted_outcome():
    policy = DecisionPolicy(entailment_threshold=0.65, contradiction_threshold=0.65)
    assessments = [
        policy.assess_evidence(
            passage_id="p1",
            relevance_score=0.8,
            entailment_score=0.05,
            contradiction_score=0.88,
            neutral_score=0.07
        )
    ]
    decision = policy.decide(assessments)
    assert decision.outcome == "contradicted"
    assert "contradicted by 1 evidence passage" in decision.reason


def test_conflicting_outcome():
    policy = DecisionPolicy(entailment_threshold=0.65, contradiction_threshold=0.65)
    assessments = [
        policy.assess_evidence(
            passage_id="p1",
            relevance_score=0.8,
            entailment_score=0.82,
            contradiction_score=0.05,
            neutral_score=0.13
        ),
        policy.assess_evidence(
            passage_id="p2",
            relevance_score=0.75,
            entailment_score=0.04,
            contradiction_score=0.79,
            neutral_score=0.17
        )
    ]
    decision = policy.decide(assessments)
    assert decision.outcome == "conflicting"
    assert "conflicting evidence" in decision.reason


def test_insufficient_outcome():
    policy = DecisionPolicy(entailment_threshold=0.65, contradiction_threshold=0.65)
    assessments = [
        policy.assess_evidence(
            passage_id="p1",
            relevance_score=0.5,
            entailment_score=0.30,
            contradiction_score=0.20,
            neutral_score=0.50
        )
    ]
    decision = policy.decide(assessments)
    assert decision.outcome == "insufficient"


def test_not_checkable_outcome():
    policy = DecisionPolicy()
    decision = policy.decide([], is_checkable=False)
    assert decision.outcome == "not_checkable"
