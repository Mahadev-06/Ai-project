"""Input text and URL content processor for ClaimLens.

Normalizes raw user input and safely fetches and parses articles from URLs.
"""
import logging
import re
from dataclasses import dataclass
from typing import Optional, Tuple
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException
from readability import Document

from app.services.providers.safe_fetch import SafeFetcher, SSRFValidationError

logger = logging.getLogger(__name__)


@dataclass
class ProcessedInput:
    """Standardized representation of input for claim analysis."""
    text: str
    title: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[str] = None
    publisher: Optional[str] = None
    source_url: Optional[str] = None
    char_count: int = 0
    language: str = "en"


class InputProcessor:
    """Preprocesses input text or fetches and extracts article content from URLs."""

    @staticmethod
    def normalize_text(text: str) -> str:
        """Clean and normalize whitespace while preserving punctuation and capitalization."""
        if not text:
            return ""
        # Replace non-breaking spaces and irregular whitespace
        text = text.replace('\xa0', ' ').replace('\u200b', '')
        # Collapse multiple blank lines
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        # Collapse horizontal whitespace within lines
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()

    @staticmethod
    def detect_language(text: str) -> str:
        """Detect ISO language code for text."""
        if not text or len(text.strip()) < 15:
            return "en"
        try:
            return detect(text)
        except LangDetectException:
            return "en"

    @classmethod
    async def process_url(cls, url: str) -> ProcessedInput:
        """Safely fetch and extract clean article text and metadata from a web page."""
        try:
            html_content, metadata = await SafeFetcher.fetch(url)
        except SSRFValidationError as e:
            raise ValueError(f"URL access rejected for security: {e}")
        except Exception as e:
            raise ValueError(f"Failed to fetch article from URL: {e}")

        # Parse with readability
        doc = Document(html_content)
        summary_html = doc.summary()
        title = doc.title()

        # Extract readable plain text
        soup = BeautifulSoup(summary_html, 'html.parser')
        paragraphs = [p.get_text().strip() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])]
        clean_text = "\n\n".join([p for p in paragraphs if len(p) > 20])

        if not clean_text or len(clean_text) < 50:
            # Fallback to general text extraction
            raw_soup = BeautifulSoup(html_content, 'html.parser')
            # Remove scripts, styles
            for elem in raw_soup(['script', 'style', 'nav', 'header', 'footer', 'noscript']):
                elem.decompose()
            clean_text = raw_soup.get_text(separator=' ', strip=True)

        clean_text = cls.normalize_text(clean_text)

        # Extract metadata from raw HTML headers
        meta_soup = BeautifulSoup(html_content, 'html.parser')
        author = cls._extract_author(meta_soup)
        pub_date = cls._extract_date(meta_soup)
        publisher = cls._extract_publisher(meta_soup, url)

        lang = cls.detect_language(clean_text)

        return ProcessedInput(
            text=clean_text,
            title=title if title else None,
            author=author,
            publication_date=pub_date,
            publisher=publisher,
            source_url=url,
            char_count=len(clean_text),
            language=lang,
        )

    @classmethod
    def process_raw_text(cls, text: str) -> ProcessedInput:
        """Normalize direct text input."""
        cleaned = cls.normalize_text(text)
        lang = cls.detect_language(cleaned)
        return ProcessedInput(
            text=cleaned,
            char_count=len(cleaned),
            language=lang,
        )

    @staticmethod
    def _extract_author(soup: BeautifulSoup) -> Optional[str]:
        """Try common metadata author tags."""
        author_meta = (
            soup.find('meta', attrs={'name': 'author'}) or
            soup.find('meta', attrs={'property': 'article:author'}) or
            soup.find('meta', attrs={'name': 'twitter:creator'})
        )
        if author_meta and author_meta.get('content'):
            return author_meta['content'].strip()
        return None

    @staticmethod
    def _extract_date(soup: BeautifulSoup) -> Optional[str]:
        """Try common metadata publication date tags."""
        date_meta = (
            soup.find('meta', attrs={'property': 'article:published_time'}) or
            soup.find('meta', attrs={'name': 'publication_date'}) or
            soup.find('meta', attrs={'name': 'date'}) or
            soup.find('time')
        )
        if date_meta:
            content = date_meta.get('content') or date_meta.get('datetime')
            if content:
                return content[:10]  # Standard YYYY-MM-DD prefix
        return None

    @staticmethod
    def _extract_publisher(soup: BeautifulSoup, url: str) -> str:
        """Extract publisher name from OpenGraph, schema, or domain."""
        og_site = soup.find('meta', attrs={'property': 'og:site_name'})
        if og_site and og_site.get('content'):
            return og_site['content'].strip()

        domain = urlparse(url).hostname or ""
        if domain.startswith("www."):
            domain = domain[4:]
        return domain or "Web Source"