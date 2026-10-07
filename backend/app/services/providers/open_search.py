"""Free open web search provider using DuckDuckGo.

Enables real-time web evidence retrieval without requiring external API keys.
"""
import logging
from typing import List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class OpenSearchResultItem:
    """A single web search result item from free open search."""
    title: str
    url: str
    snippet: str
    publisher: Optional[str] = None


class OpenSearchProvider:
    """Free web search adapter using DDGS."""

    def __init__(self) -> None:
        self.is_configured = True

    def search(self, query: str, max_results: int = 5) -> List[OpenSearchResultItem]:
        """Search the live web using DuckDuckGo."""
        results: List[OpenSearchResultItem] = []
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(query, max_results=max_results))
                for item in raw_results:
                    title = item.get("title", "")
                    url = item.get("href", "")
                    body = item.get("body", "")

                    # Extract readable publisher domain
                    publisher = "Web Source"
                    if "://" in url:
                        domain = url.split("://")[1].split("/")[0]
                        publisher = domain.replace("www.", "").capitalize()

                    if body and len(body.strip()) > 15:
                        results.append(OpenSearchResultItem(
                            title=title,
                            url=url,
                            snippet=body.strip(),
                            publisher=publisher,
                        ))
        except Exception as e:
            logger.warning(f"Open web search error for query '{query}': {e}")
        return results
