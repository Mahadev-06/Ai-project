"""Unit tests for ClaimExtractor."""
import pytest
from app.services.claim_extractor import ClaimExtractor


class MockToken:
    def __init__(self, text, pos="NOUN", dep="dep", lower=None):
        self.text = text
        self.lower_ = (lower or text).lower()
        self.pos_ = pos
        self.dep_ = dep
        self.is_punct = text in {".", ",", "!", "?"}


class MockSpan:
    def __init__(self, text, start_char=0, end_char=None, ents=None, noun_chunks=None, tokens=None):
        self.text = text
        self.start_char = start_char
        self.end_char = end_char or len(text)
        self.ents = ents or []
        self.noun_chunks = noun_chunks or []
        self._tokens = tokens or [MockToken(t) for t in text.split()]

    def __iter__(self):
        return iter(self._tokens)


class MockDoc:
    def __init__(self, sents):
        self.sents = sents

    def __call__(self, text):
        return self


class MockEntity:
    def __init__(self, text, label):
        self.text = text
        self.label_ = label


class MockChunk:
    def __init__(self, text):
        self.text = text


def test_filters_questions():
    nlp = lambda text: MockDoc([
        MockSpan("Is the Earth flat or round?"),
        MockSpan("Water boils at 100 degrees Celsius at sea level.", ents=[
            MockEntity("100 degrees Celsius", "QUANTITY"),
            MockEntity("sea level", "LOC")
        ])
    ])
    extractor = ClaimExtractor(nlp)
    claims = extractor.extract_claims("dummy input")
    assert len(claims) == 1
    assert "Water boils" in claims[0].claim_text


def test_filters_commands():
    nlp = lambda text: MockDoc([
        MockSpan("Please share this post with your friends."),
        MockSpan("The Great Wall of China is located in northern China.", ents=[
            MockEntity("The Great Wall of China", "FAC"),
            MockEntity("northern China", "GPE")
        ])
    ])
    extractor = ClaimExtractor(nlp)
    claims = extractor.extract_claims("dummy input")
    assert len(claims) == 1
    assert "Great Wall" in claims[0].claim_text


def test_linguistic_feature_detection():
    nlp = lambda text: MockDoc([
        MockSpan(
            "The Apollo 11 mission did not land on Mars in 1969.",
            ents=[
                MockEntity("Apollo 11", "ORG"),
                MockEntity("Mars", "LOC"),
                MockEntity("1969", "DATE")
            ],
            tokens=[
                MockToken("The"), MockToken("Apollo"), MockToken("11"), MockToken("mission"),
                MockToken("did"), MockToken("not", dep="neg"), MockToken("land", pos="VERB", dep="ROOT"),
                MockToken("on"), MockToken("Mars"), MockToken("in"), MockToken("1969")
            ]
        )
    ])
    extractor = ClaimExtractor(nlp)
    claims = extractor.extract_claims("dummy")
    assert len(claims) == 1
    c = claims[0]
    assert c.has_negation is True
    assert "1969" in c.dates
