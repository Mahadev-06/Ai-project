"""Google Fact Check Tools API client.

Searches known fact-checking databases for authoritative ClaimReview entries.
"""
import logging
from dataclasses import dataclass, field
from typing import Optional, List
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

FACT_CHECK_ENDPOINT = "https://factchecktools.googleapis.com/v1alpha1/claims:search"


@dataclass
class FactCheckReview:
    """Review verdict by an independent fact-checking publisher."""
    publisher_name: str
    publisher_site: Optional[str]
    url: str
    title: str
    review_date: Optional[str]
    textual_rating: str


@dataclass
class FactCheckItem:
    """A claim verified by one or more fact-checking organizations."""
    claim_text: str
    claimant: Optional[str] = None
    claim_date: Optional[str] = None
    reviews: List[FactCheckReview] = field(default_factory=list)


class GoogleFactCheckProvider:
    """Adapter for Google Fact Check Tools API."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.GOOGLE_FACTCHECK_API_KEY
        self.is_configured = bool(self.api_key and self.api_key.strip())

    async def search(
        self,
        query: str,
        language_code: str = "en",
        page_size: int = 5,
    ) -> List[FactCheckItem]:
        """Search Google Fact Check database for relevant debunking articles.
        
        Args:
            query: Claim statement or search terms
            language_code: BCP-47 language tag
            page_size: Maximum claims to retrieve
            
        Returns:
            List of FactCheckItem
        """
        if not self.is_configured:
            logger.info("Google Fact Check API key not configured; skipping fact-check lookup")
            return []

        params = {
            "query": query[:300],
            "languageCode": language_code,
            "pageSize": page_size,
            "key": self.api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.get(
                    FACT_CHECK_ENDPOINT,
                    params=params,
                )

                if response.status_code == 400:
                    logger.warning(f"Google Fact Check API query bad request: {response.text}")
                    return []

                response.raise_for_status()
                data = response.json()

                results: List[FactCheckItem] = []
                claims_data = data.get("claims", [])

                for item in claims_data:
                    reviews: List[FactCheckReview] = []
                    for r in item.get("claimReview", []):
                        pub = r.get("publisher", {})
                        reviews.append(FactCheckReview(
                            publisher_name=pub.get("name", "Unknown Fact-Checker"),
                            publisher_site=pub.get("site"),
                            url=r.get("url", ""),
                            title=r.get("title", ""),
                            review_date=r.get("reviewDate"),
                            textual_rating=r.get("textualRating", "Unrated"),
                        ))

                    results.append(FactCheckItem(
                        claim_text=item.get("text", ""),
                        claimant=item.get("claimant"),
                        claim_date=item.get("claimDate"),
                        reviews=reviews,
                    ))

                logger.info(f"Google Fact Check returned {len(results)} matches for '{query[:50]}...'")
                return results

        except httpx.HTTPError as e:
            logger.error(f"Google Fact Check API request error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error querying Google Fact Check: {e}")
            return []