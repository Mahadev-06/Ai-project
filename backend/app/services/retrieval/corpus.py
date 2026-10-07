"""Local evidence corpus loader and indexer.

Loads versioned corpus documents from JSON files,
parses them into passages for retrieval.
"""
import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class Passage:
    """A text passage from the evidence corpus."""
    passage_id: str
    doc_id: str
    title: str
    publisher: str
    source_url: str
    retrieved_date: str
    publication_date: Optional[str]
    text: str
    content_hash: str
    attribution: str
    license: str
    passage_index: int  # index within document


@dataclass
class CorpusManifest:
    """Metadata about the evidence corpus."""
    version: str
    created_date: str
    description: str
    document_count: int
    passage_count: int
    topics: list[str]
    license_summary: str


class CorpusLoader:
    """Loads and indexes the local evidence corpus."""
    
    def __init__(self, corpus_dir: str) -> None:
        self.corpus_dir = Path(corpus_dir)
        self.manifest: Optional[CorpusManifest] = None
        self.passages: list[Passage] = []
        self._loaded = False
    
    @property
    def is_loaded(self) -> bool:
        return self._loaded
    
    @property
    def version(self) -> str:
        return self.manifest.version if self.manifest else 'unknown'
    
    def load(self) -> None:
        """Load corpus from manifest and document files."""
        manifest_path = self.corpus_dir / 'manifest.json'
        if not manifest_path.exists():
            logger.error(f'Corpus manifest not found: {manifest_path}')
            return
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
        
        self.manifest = CorpusManifest(
            version=manifest_data.get('version', '0.0.0'),
            created_date=manifest_data.get('created_date', ''),
            description=manifest_data.get('description', ''),
            document_count=manifest_data.get('document_count', 0),
            passage_count=0,
            topics=manifest_data.get('topics', []),
            license_summary=manifest_data.get('license_summary', ''),
        )
        
        docs_dir = self.corpus_dir / 'documents'
        if not docs_dir.exists():
            logger.error(f'Documents directory not found: {docs_dir}')
            return
        
        self.passages = []
        doc_files = sorted(docs_dir.glob('*.json'))
        
        for doc_file in doc_files:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    doc_data = json.load(f)
                self._process_document(doc_data)
            except Exception as e:
                logger.error(f'Failed to load document {doc_file.name}: {e}')
        
        self.manifest.passage_count = len(self.passages)
        self._loaded = True
        logger.info(
            f'Corpus loaded: {len(doc_files)} documents, '
            f'{len(self.passages)} passages, version {self.version}'
        )
    
    def _process_document(self, doc_data: dict) -> None:
        """Process a document into overlapping passages."""
        doc_id = doc_data.get('doc_id', '')
        title = doc_data.get('title', '')
        publisher = doc_data.get('publisher', '')
        source_url = doc_data.get('source_url', '')
        retrieved_date = doc_data.get('retrieved_date', '')
        publication_date = doc_data.get('publication_date')
        attribution = doc_data.get('attribution', '')
        doc_license = doc_data.get('license', '')
        
        # Document can have pre-split passages or full text
        passages_data = doc_data.get('passages', [])
        
        if passages_data:
            for idx, passage_text in enumerate(passages_data):
                if not passage_text.strip():
                    continue
                content_hash = hashlib.sha256(passage_text.encode('utf-8')).hexdigest()[:16]
                passage = Passage(
                    passage_id=f'{doc_id}-p{idx}',
                    doc_id=doc_id,
                    title=title,
                    publisher=publisher,
                    source_url=source_url,
                    retrieved_date=retrieved_date,
                    publication_date=publication_date,
                    text=passage_text.strip(),
                    content_hash=content_hash,
                    attribution=attribution,
                    license=doc_license,
                    passage_index=idx,
                )
                self.passages.append(passage)
        else:
            # Split full text into overlapping passages
            full_text = doc_data.get('text', '')
            if full_text:
                chunks = self._split_into_passages(full_text)
                for idx, chunk in enumerate(chunks):
                    content_hash = hashlib.sha256(chunk.encode('utf-8')).hexdigest()[:16]
                    passage = Passage(
                        passage_id=f'{doc_id}-p{idx}',
                        doc_id=doc_id,
                        title=title,
                        publisher=publisher,
                        source_url=source_url,
                        retrieved_date=retrieved_date,
                        publication_date=publication_date,
                        text=chunk,
                        content_hash=content_hash,
                        attribution=attribution,
                        license=doc_license,
                        passage_index=idx,
                    )
                    self.passages.append(passage)
    
    def _split_into_passages(self, text: str, max_words: int = 200,
                              overlap_words: int = 50) -> list[str]:
        """Split text into overlapping passages at sentence boundaries."""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        passages = []
        current_words: list[str] = []
        current_sentences: list[str] = []
        
        for sentence in sentences:
            words = sentence.split()
            if len(current_words) + len(words) > max_words and current_sentences:
                passages.append(' '.join(current_sentences))
                # Keep overlap
                overlap_text = ' '.join(current_sentences[-2:]) if len(current_sentences) >= 2 else ''
                current_sentences = [overlap_text] if overlap_text else []
                current_words = overlap_text.split() if overlap_text else []
            current_sentences.append(sentence)
            current_words.extend(words)
        
        if current_sentences:
            passages.append(' '.join(current_sentences))
        
        return passages
    
    def get_passage_texts(self) -> list[str]:
        """Get all passage texts for indexing."""
        return [p.text for p in self.passages]
    
    def get_passage_by_id(self, passage_id: str) -> Optional[Passage]:
        """Look up a passage by its ID."""
        for p in self.passages:
            if p.passage_id == passage_id:
                return p
        return None