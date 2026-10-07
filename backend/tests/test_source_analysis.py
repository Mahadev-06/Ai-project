"""Unit tests for SourceAnalyzer and credibility signals."""
import pytest
from app.services.source_analysis import SourceAnalyzer, PUBLISHER_REGISTRY


def test_registry_publisher_documented():
    analyzer = SourceAnalyzer()
    res = analyzer.analyze(
        url="https://www.nasa.gov/mission_pages/apollo/apollo11.html",
        publisher="NASA",
        author="John Smith",
        publication_date="2024-05-12",
        title="Apollo 11 Mission Overview"
    )
    assert res.provenance_category == "documented"
    assert res.is_registry_entry is True
    assert res.publisher_name == "NASA"

    # Check that editorial policy signal was observed
    ed_signal = next(s for s in res.signals if s.name == "Editorial/corrections policy")
    assert ed_signal.status == "observed"


def test_unregistered_partially_documented():
    analyzer = SourceAnalyzer()
    res = analyzer.analyze(
        url="https://some-tech-blog.example.org/article",
        publisher="Tech Blog",
        author="Alice Researcher",
        publication_date="2024-01-10",
        title="New Discoveries"
    )
    assert res.provenance_category == "partially_documented"
    assert res.is_registry_entry is False


def test_unknown_provenance():
    analyzer = SourceAnalyzer()
    res = analyzer.analyze(
        url=None,
        publisher=None,
        author=None,
        publication_date=None,
    )
    assert res.provenance_category == "unknown"
