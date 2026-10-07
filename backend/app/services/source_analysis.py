"""Source credibility analysis for evidence passages.

Implements a transparent rubric with page-level and publisher-level
metadata signals. Uses descriptive provenance categories rather
than opaque numerical trust scores.
"""
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class CredibilitySignal:
    """A single credibility signal for a source."""
    name: str
    value: str
    status: str  # 'observed', 'unknown', 'not_applicable'
    supporting_url: Optional[str] = None
    reason: str = ''
    last_reviewed: Optional[str] = None


@dataclass
class SourceCredibilityResult:
    """Complete credibility assessment for a source."""
    provenance_category: str  # 'documented', 'partially_documented', 'unknown'
    signals: list[CredibilitySignal] = field(default_factory=list)
    publisher_name: Optional[str] = None
    domain: Optional[str] = None
    is_registry_entry: bool = False


# Version-controlled publisher registry for well-documented sources
PUBLISHER_REGISTRY: dict[str, dict] = {
    'nasa.gov': {
        'name': 'NASA',
        'type': 'government_agency',
        'description': 'U.S. National Aeronautics and Space Administration',
        'expertise': ['space', 'earth science', 'astronomy', 'aeronautics'],
        'has_editorial_policy': True,
        'corrections_url': None,
        'reviewed': True,
        'review_date': '2024-09-01',
    },
    'who.int': {
        'name': 'World Health Organization',
        'type': 'international_organization',
        'description': 'United Nations specialized agency for public health',
        'expertise': ['health', 'medicine', 'epidemiology', 'disease'],
        'has_editorial_policy': True,
        'corrections_url': None,
        'reviewed': True,
        'review_date': '2024-09-01',
    },
    'cdc.gov': {
        'name': 'Centers for Disease Control and Prevention',
        'type': 'government_agency',
        'description': 'U.S. national public health agency',
        'expertise': ['disease', 'health', 'vaccines', 'epidemiology'],
        'has_editorial_policy': True,
        'corrections_url': None,
        'reviewed': True,
        'review_date': '2024-09-01',
    },
    'noaa.gov': {
        'name': 'National Oceanic and Atmospheric Administration',
        'type': 'government_agency',
        'description': 'U.S. agency for oceanic and atmospheric science',
        'expertise': ['climate', 'weather', 'ocean', 'atmosphere'],
        'has_editorial_policy': True,
        'corrections_url': None,
        'reviewed': True,
        'review_date': '2024-09-01',
    },
    'usgs.gov': {
        'name': 'U.S. Geological Survey',
        'type': 'government_agency',
        'description': 'U.S. science agency for natural resources and hazards',
        'expertise': ['geology', 'earthquakes', 'water', 'maps'],
        'has_editorial_policy': True,
        'corrections_url': None,
        'reviewed': True,
        'review_date': '2024-09-01',
    },
    'worldbank.org': {
        'name': 'World Bank',
        'type': 'international_organization',
        'description': 'International financial institution for development',
        'expertise': ['economics', 'development', 'poverty', 'finance'],
        'has_editorial_policy': True,
        'corrections_url': None,
        'reviewed': True,
        'review_date': '2024-09-01',
    },
    'nature.com': {
        'name': 'Nature',
        'type': 'academic_journal',
        'description': 'Peer-reviewed multidisciplinary scientific journal',
        'expertise': ['science', 'research'],
        'has_editorial_policy': True,
        'corrections_url': 'https://www.nature.com/nature-portfolio/editorial-policies/corrections',
        'reviewed': True,
        'review_date': '2024-09-01',
    },
    'britannica.com': {
        'name': 'Encyclopedia Britannica',
        'type': 'encyclopedia',
        'description': 'General knowledge reference work',
        'expertise': ['general knowledge'],
        'has_editorial_policy': True,
        'corrections_url': None,
        'reviewed': True,
        'review_date': '2024-09-01',
    },
}


class SourceAnalyzer:
    """Analyzes source credibility using transparent signals."""

    def __init__(self, registry: Optional[dict] = None) -> None:
        self.registry = registry or PUBLISHER_REGISTRY

    def analyze(
        self,
        url: Optional[str] = None,
        publisher: Optional[str] = None,
        author: Optional[str] = None,
        publication_date: Optional[str] = None,
        title: Optional[str] = None,
    ) -> SourceCredibilityResult:
        """Analyze source credibility based on available metadata."""
        signals: list[CredibilitySignal] = []
        domain = self._extract_domain(url) if url else None

        # Check publisher registry
        registry_entry = None
        is_registry = False
        if domain:
            # Check against registry (match base domain)
            for reg_domain, entry in self.registry.items():
                if domain.endswith(reg_domain):
                    registry_entry = entry
                    is_registry = True
                    break

        # Signal 1: Identifiable publisher
        if publisher and publisher.strip():
            signals.append(CredibilitySignal(
                name='Identifiable publisher',
                value=publisher,
                status='observed',
                reason='Publisher name is available in the source metadata.',
            ))
        elif registry_entry:
            signals.append(CredibilitySignal(
                name='Identifiable publisher',
                value=registry_entry['name'],
                status='observed',
                reason='Publisher identified from domain registry.',
            ))
        else:
            signals.append(CredibilitySignal(
                name='Identifiable publisher',
                value='Unknown',
                status='unknown',
                reason='Publisher name could not be determined from available metadata.',
            ))

        # Signal 2: Author
        if author and author.strip():
            signals.append(CredibilitySignal(
                name='Identifiable author',
                value=author,
                status='observed',
                reason='Author name is available.',
            ))
        else:
            signals.append(CredibilitySignal(
                name='Identifiable author',
                value='Not available',
                status='unknown',
                reason='Author name is not available. Missing author metadata is not equivalent to an unreliable source.',
            ))

        # Signal 3: Publication date
        if publication_date and publication_date.strip():
            signals.append(CredibilitySignal(
                name='Publication date',
                value=publication_date,
                status='observed',
                reason='Publication date is available for temporal context.',
            ))
        else:
            signals.append(CredibilitySignal(
                name='Publication date',
                value='Not available',
                status='unknown',
                reason='Publication date could not be determined.',
            ))

        # Signal 4: Editorial policy
        if registry_entry and registry_entry.get('has_editorial_policy'):
            corrections_url = registry_entry.get('corrections_url', '')
            signals.append(CredibilitySignal(
                name='Editorial/corrections policy',
                value='Available',
                status='observed',
                supporting_url=corrections_url or None,
                reason='This publisher is known to have editorial review processes.',
                last_reviewed=registry_entry.get('review_date'),
            ))
        else:
            signals.append(CredibilitySignal(
                name='Editorial/corrections policy',
                value='Not verified',
                status='unknown',
                reason='No information about editorial policies is available for this source.',
            ))

        # Signal 5: Institutional expertise
        if registry_entry and registry_entry.get('expertise'):
            expertise = ', '.join(registry_entry['expertise'])
            signals.append(CredibilitySignal(
                name='Relevant expertise',
                value=expertise,
                status='observed',
                reason=f'{registry_entry["name"]} has documented expertise in these areas.',
                last_reviewed=registry_entry.get('review_date'),
            ))

        # Signal 6: Source URL
        if url:
            signals.append(CredibilitySignal(
                name='Source URL',
                value=url,
                status='observed',
                reason='Original source URL is available for verification.',
            ))

        # Determine provenance category
        provenance = self._determine_provenance(signals, registry_entry)

        publisher_name = None
        if registry_entry:
            publisher_name = registry_entry['name']
        elif publisher:
            publisher_name = publisher

        return SourceCredibilityResult(
            provenance_category=provenance,
            signals=signals,
            publisher_name=publisher_name,
            domain=domain,
            is_registry_entry=is_registry,
        )

    def _determine_provenance(
        self,
        signals: list[CredibilitySignal],
        registry_entry: Optional[dict],
    ) -> str:
        """Determine provenance category based on available signals.

        Categories describe available documentation, not a guarantee of accuracy.
        """
        observed_count = sum(1 for s in signals if s.status == 'observed')

        if registry_entry and observed_count >= 4:
            return 'documented'
        elif observed_count >= 2:
            return 'partially_documented'
        else:
            return 'unknown'

    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.hostname or ''
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return None