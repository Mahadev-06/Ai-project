"""Claim extraction from text using spaCy NLP.

Extracts candidate factual statements using sentence segmentation,
named entity recognition, and heuristic filtering rules.
"""
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ExtractedClaim:
    """A candidate factual claim extracted from input text."""
    claim_id: str
    claim_text: str
    original_sentence: str
    char_start: int
    char_end: int
    score: float  # factual-claim likelihood score
    entities: list[dict] = field(default_factory=list)
    dates: list[str] = field(default_factory=list)
    numbers: list[str] = field(default_factory=list)
    noun_phrases: list[str] = field(default_factory=list)
    has_negation: bool = False
    has_qualifier: bool = False
    has_attribution: bool = False


class ClaimExtractor:
    """Extracts checkable factual claims from text using spaCy."""
    
    QUESTION_PATTERNS = re.compile(r'^(who|what|where|when|why|how|is|are|was|were|do|does|did|can|could|should|would|will)\b', re.IGNORECASE)
    COMMAND_PATTERNS = re.compile(r'^(please|let|make|do|don\'t|stop|go|come|try|help|remember|forget|consider)\b', re.IGNORECASE)
    OPINION_MARKERS = re.compile(r'\b(I think|I believe|I feel|in my opinion|personally|I guess|I suppose|I hope|I wish|we should|you should|it seems to me)\b', re.IGNORECASE)
    NEGATION_WORDS = {'not', 'no', 'never', 'neither', 'nor', 'nobody', 'nothing', 'nowhere', 'hardly', 'scarcely', 'barely', "n't", 'cannot'}
    QUALIFIER_WORDS = {'approximately', 'about', 'roughly', 'nearly', 'almost', 'around', 'estimated', 'reportedly', 'allegedly', 'supposedly', 'possibly', 'probably', 'likely', 'unlikely', 'may', 'might', 'could', 'perhaps'}
    ATTRIBUTION_PATTERNS = re.compile(r'\b(according to|said|stated|claimed|reported|announced|confirmed|denied|argued|suggested)\b', re.IGNORECASE)
    
    def __init__(self, nlp) -> None:
        self.nlp = nlp

    @staticmethod
    def normalize_query_to_proposition(sent_text: str) -> str:
        """Transform user questions or search queries into verifiable claim propositions."""
        s = sent_text.strip()
        is_q = s.endswith('?') or bool(re.match(r'^(who|what|where|when|why|how|is|are|was|were|do|does|did|can|could|should|would|will)\b', s, re.IGNORECASE))
        if not is_q:
            return s.rstrip('.!?').strip() + '.'

        s_clean = s.rstrip('?').strip()

        # Check for alternatives "Is X A or B?" e.g., "Is earth round or flat?"
        m_alt = re.match(r'^(is|are|was|were)\s+([^?]+?)\s+([a-zA-Z0-9]+)\s+or\s+([a-zA-Z0-9]+)$', s_clean, re.IGNORECASE)
        if m_alt:
            verb = m_alt.group(1).lower()
            subj = m_alt.group(2).strip()
            first_opt = m_alt.group(3).strip()
            return f"{subj[:1].upper() + subj[1:]} {verb} {first_opt}."

        # Pattern: Is/Are/Was/Were [Subject] [Predicate]?
        m_aux = re.match(r'^(is|are|was|were)\s+([^?]+)$', s_clean, re.IGNORECASE)
        if m_aux:
            verb = m_aux.group(1).lower()
            rest = m_aux.group(2).strip()
            words = rest.split()
            if len(words) >= 2:
                if words[0].lower() in ('the', 'a', 'an') and len(words) >= 3:
                    subj = f"{words[0]} {words[1]}"
                    pred = " ".join(words[2:])
                else:
                    subj = words[0]
                    pred = " ".join(words[1:])
                return f"{subj[:1].upper() + subj[1:]} {verb} {pred}."
            return f"{rest[:1].upper() + rest[1:]} {verb}."

        # Pattern: Does/Do/Did [Subject] [Predicate]?
        m_do = re.match(r'^(does|do|did)\s+([^?]+)$', s_clean, re.IGNORECASE)
        if m_do:
            rest = m_do.group(2).strip()
            return f"{rest[:1].upper() + rest[1:]}."

        # Pattern: Can/Could/Should/Would [Subject] [Predicate]?
        m_modal = re.match(r'^(can|could|should|would|will)\s+([^?]+)$', s_clean, re.IGNORECASE)
        if m_modal:
            modal = m_modal.group(1).lower()
            rest = m_modal.group(2).strip()
            words = rest.split()
            if len(words) >= 2:
                if words[0].lower() in ('the', 'a', 'an') and len(words) >= 3:
                    subj = f"{words[0]} {words[1]}"
                    pred = " ".join(words[2:])
                else:
                    subj = words[0]
                    pred = " ".join(words[1:])
                return f"{subj[:1].upper() + subj[1:]} {modal} {pred}."
            return f"{rest[:1].upper() + rest[1:]} {modal}."

        clean_wh = re.sub(r'^(who|what|where|when|why|how)\s+(is|are|was|were|did|do|does)?\s*', '', s_clean, flags=re.IGNORECASE).strip()
        if clean_wh:
            return f"{clean_wh[:1].upper() + clean_wh[1:]}."
        return f"{s_clean[:1].upper() + s_clean[1:]}."
    
    def extract_claims(self, text: str, max_claims: int = 6) -> list[ExtractedClaim]:
        """Extract candidate factual claims from text.
        
        Uses spaCy for sentence segmentation, NER, and linguistic features.
        Filters out questions, commands, opinions, and non-factual statements.
        Falls back to converting interrogative inquiries to verifiable propositions.
        Returns scored claims sorted by factual-claim likelihood.
        """
        if not text or not text.strip():
            return []

        if self.nlp is None:
            # Fallback regex sentence splitter when spaCy model is loading/absent
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) >= 5]
            candidates = []
            char_cursor = 0
            for idx, s_text in enumerate(sentences[:max_claims]):
                start_pos = text.find(s_text, char_cursor)
                if start_pos == -1:
                    start_pos = char_cursor
                end_pos = start_pos + len(s_text)
                char_cursor = end_pos

                is_q = s_text.endswith('?') or bool(self.QUESTION_PATTERNS.match(s_text))
                if is_q:
                    continue

                words = set(s_text.lower().split())
                has_neg = bool(words & self.NEGATION_WORDS)
                has_qual = bool(words & self.QUALIFIER_WORDS)
                has_attr = bool(self.ATTRIBUTION_PATTERNS.search(s_text))

                candidates.append(ExtractedClaim(
                    claim_id=f'claim-{idx+1}',
                    claim_text=s_text,
                    original_sentence=s_text,
                    char_start=start_pos,
                    char_end=end_pos,
                    score=0.7,
                    entities=[],
                    dates=[],
                    numbers=[w for w in s_text.split() if any(c.isdigit() for c in w)],
                    noun_phrases=[],
                    has_negation=has_neg,
                    has_qualifier=has_qual,
                    has_attribution=has_attr,
                ))

            if not candidates and sentences:
                for idx, s_text in enumerate(sentences[:max_claims]):
                    prop = self.normalize_query_to_proposition(s_text)
                    candidates.append(ExtractedClaim(
                        claim_id=f'claim-{idx+1}',
                        claim_text=prop,
                        original_sentence=s_text,
                        char_start=0,
                        char_end=len(s_text),
                        score=0.6,
                        entities=[],
                        dates=[],
                        numbers=[w for w in s_text.split() if any(c.isdigit() for c in w)],
                        noun_phrases=[],
                        has_negation=False,
                        has_qualifier=False,
                        has_attribution=False,
                    ))

            return candidates

        doc = self.nlp(text)
        candidates: list[ExtractedClaim] = []
        raw_sents = list(doc.sents)
        
        for sent_idx, sent in enumerate(raw_sents):
            sent_text = sent.text.strip()
            
            # Skip empty or giant sentences
            if len(sent_text) < 4 or len(sent_text) > 500:
                continue
            
            # Skip questions during primary declarative pass
            if sent_text.endswith('?') or self.QUESTION_PATTERNS.match(sent_text):
                continue
            
            # Skip commands/imperatives
            if self.COMMAND_PATTERNS.match(sent_text):
                continue
            
            # Extract linguistic features
            entities = [{'text': ent.text, 'label': ent.label_} for ent in sent.ents]
            noun_phrases = [chunk.text for chunk in sent.noun_chunks]
            
            # Extract dates and numbers
            dates = [ent.text for ent in sent.ents if ent.label_ in ('DATE', 'TIME')]
            numbers = [ent.text for ent in sent.ents if ent.label_ in ('CARDINAL', 'QUANTITY', 'MONEY', 'PERCENT', 'ORDINAL')]
            
            # Check for negation
            sent_tokens = {token.lower_ for token in sent}
            has_negation = bool(sent_tokens & self.NEGATION_WORDS) or any(token.dep_ == 'neg' for token in sent)
            
            # Check for qualifiers
            has_qualifier = bool(sent_tokens & self.QUALIFIER_WORDS)
            
            # Check for attribution
            has_attribution = bool(self.ATTRIBUTION_PATTERNS.search(sent_text))
            
            # Check if it's a pure opinion
            is_opinion = bool(self.OPINION_MARKERS.search(sent_text))
            
            # Score the sentence for factual-claim likelihood
            score = self._score_factuality(sent, entities, numbers, dates, is_opinion, has_attribution)
            
            if score < 0.2:
                continue
            
            claim = ExtractedClaim(
                claim_id=f'claim-{sent_idx}',
                claim_text=sent_text,
                original_sentence=sent_text,
                char_start=sent.start_char,
                char_end=sent.end_char,
                score=score,
                entities=entities,
                dates=dates,
                numbers=numbers,
                noun_phrases=noun_phrases,
                has_negation=has_negation,
                has_qualifier=has_qualifier,
                has_attribution=has_attribution,
            )
            candidates.append(claim)
        
        # Fallback pass: If no claims passed declarative filters (e.g. user entered a question or short query)
        if not candidates and raw_sents:
            for sent_idx, sent in enumerate(raw_sents[:max_claims]):
                sent_text = sent.text.strip()
                if len(sent_text) < 4:
                    continue
                prop_text = self.normalize_query_to_proposition(sent_text)
                entities = [{'text': ent.text, 'label': ent.label_} for ent in sent.ents]
                noun_phrases = [chunk.text for chunk in sent.noun_chunks]
                dates = [ent.text for ent in sent.ents if ent.label_ in ('DATE', 'TIME')]
                numbers = [ent.text for ent in sent.ents if ent.label_ in ('CARDINAL', 'QUANTITY', 'MONEY', 'PERCENT', 'ORDINAL')]
                sent_tokens = {token.lower_ for token in sent}
                has_negation = bool(sent_tokens & self.NEGATION_WORDS) or any(token.dep_ == 'neg' for token in sent)
                has_qualifier = bool(sent_tokens & self.QUALIFIER_WORDS)
                has_attribution = bool(self.ATTRIBUTION_PATTERNS.search(sent_text))

                candidates.append(ExtractedClaim(
                    claim_id=f'claim-{sent_idx+1}',
                    claim_text=prop_text,
                    original_sentence=sent_text,
                    char_start=sent.start_char,
                    char_end=sent.end_char,
                    score=0.6,
                    entities=entities,
                    dates=dates,
                    numbers=numbers,
                    noun_phrases=noun_phrases,
                    has_negation=has_negation,
                    has_qualifier=has_qualifier,
                    has_attribution=has_attribution,
                ))

        # Sort by score descending, take top N
        candidates.sort(key=lambda c: c.score, reverse=True)
        selected = candidates[:max_claims]
        
        # Re-assign sequential IDs
        for i, claim in enumerate(selected):
            claim.claim_id = f'claim-{i+1}'
        
        logger.info(f'Extracted {len(selected)} claims from {len(raw_sents)} sentences')
        return selected
    
    def _score_factuality(self, sent, entities: list, numbers: list, dates: list,
                          is_opinion: bool, has_attribution: bool) -> float:
        """Score a sentence's likelihood of being a checkable factual claim.
        
        Higher score = more likely to be a factual claim worth checking.
        """
        score = 0.3  # base score for declarative sentences
        
        # Boost for named entities (proper nouns, places, orgs)
        if entities:
            score += min(0.2, 0.05 * len(entities))
        
        # Boost for numbers, quantities, dates
        if numbers:
            score += min(0.15, 0.05 * len(numbers))
        if dates:
            score += 0.1
        
        # Boost for having a main verb (suggests complete proposition)
        has_verb = any(token.pos_ == 'VERB' and token.dep_ in ('ROOT', 'relcl', 'advcl', 'ccomp')
                      for token in sent)
        if has_verb:
            score += 0.1
        
        # Boost for geographical entities (often factual)
        geo_entities = [e for e in entities if e['label'] in ('GPE', 'LOC', 'FAC')]
        if geo_entities:
            score += 0.05
        
        # Penalty for opinions
        if is_opinion:
            score -= 0.4
        
        # Slight penalty for attributed claims (they're about what someone said)
        if has_attribution:
            score -= 0.05
        
        # Penalty for extremely short sentences (only 1 or 2 words)
        word_count = len([t for t in sent if not t.is_punct])
        if word_count < 3:
            score -= 0.15
        
        return max(0.0, min(1.0, score))