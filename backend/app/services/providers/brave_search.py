"""Brave Web Search API client.

Searches the live web for evidence snippets and source pages
supporting or refuting claims.
"""
import logging
from dataclasses import dataclass, field
from typing import Optional, List
import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

BRAVE_SEARCH_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"


@dataclass
class SearchResultItem:
    """A single web search result item."""
    title: str
    url: str
    description: str
    page_age: Optional[str] = None
    publisher: Optional[str] = None
    extra_snippets: List[str] = field(default_factory=list)


class BraveSearchProvider:
    """Adapter for Brave Web Search API."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.BRAVE_API_KEY
        self.is_configured = bool(self.api_key and self.api_key.strip())

    async def search(
        self,
        query: str,
        count: int = 5,
        country: str = "US",
        search_lang: str = "en",
    ) -> List[SearchResultItem]:
        """Execute a web search query via Brave Search.
        
        Args:
            query: Claim text or search keywords
            count: Number of results (1-20)
            country: 2-letter ISO country code
            search_lang: Result language filter
            
        Returns:
            List of SearchResultItem
        """
        if not self.is_configured:
            logger.warning("Brave Search API key not configured; skipping live web search")
            return []

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
            "User-Agent": "ClaimLens-MisinformationDetector/1.0",
        }

        params = {
            "q": query[:400],
            "count": min(count, 20),
            "country": country,
            "search_lang": search_lang,
            "extra_snippets": "true",
            "safesearch": "moderate",
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    BRAVE_SEARCH_ENDPOINT,
                    headers=headers,
                    params=params,
                )

                if response.status_code == 429:
                    logger.error("Brave Search API rate limit exceeded (HTTP 429)")
                    return []

                response.raise_for_status()
                data = response.json()

                results: List[SearchResultItem] = []
                web_results = data.get("web", {}).get("results", [])

                for item in web_results:
                    profile = item.get("profile", {})
                    publisher_name = profile.get("name") if isinstance(profile, dict) else None

                    results.append(SearchResultItem(
                        title=item.get("title", "Untitled"),
                        url=item.get("url", ""),
                        description=item.get("description", ""),
                        page_age=item.get("page_age"),
                        publisher=publisher_name,
                        extra_snippets=item.get("extra_snippets", []) or [],
                    ))

                logger.info(f"Brave Search returned {len(results)} items for query: '{query[:60]}...'")
                return results

        except httpx.HTTPError as e:
            logger.error(f"Brave Search API request error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during Brave Search: {e}")
            return []