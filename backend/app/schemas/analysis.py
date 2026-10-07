from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict
from datetime import datetime
from .enums import EvidenceMode, AnalysisStatus, ClaimOutcome, EvidenceStance, ProvenanceCategory

class AnalysisRequest(BaseModel):
    input_text: Optional[str] = None
    input_url: Optional[HttpUrl] = None
    evidence_mode: EvidenceMode = EvidenceMode.local

class CredibilitySignal(BaseModel):
    name: str
    value: float
    status: str
    supporting_url: Optional[str] = None
    reason: Optional[str] = None
    last_reviewed: Optional[datetime] = None

class SourceCredibility(BaseModel):
    provenance_category: ProvenanceCategory
    signals: List[CredibilitySignal] = []

class LinguisticFeatures(BaseModel):
    entities: List[str] = []
    dates: List[str] = []
    numbers: List[str] = []
    noun_phrases: List[str] = []
    has_negation: bool = False
    has_qualifier: bool = False
    has_attribution: bool = False

class EvidenceItem(BaseModel):
    id: str
    doc_id: str
    title: Optional[str] = None
    publisher: Optional[str] = None
    url: Optional[str] = None
    publication_date: Optional[datetime] = None
    excerpt: str
    full_context: Optional[str] = None
    stance: EvidenceStance
    stance_scores: Dict[str, float]
    relevance_score: float
    source_credibility: Optional[SourceCredibility] = None

class ClaimResult(BaseModel):
    id: str
    claim_text: str
    original_sentence: str
    char_start: int
    char_end: int
    outcome: ClaimOutcome
    reason: Optional[str] = None
    evidence: List[EvidenceItem] = []
    linguistic_features: LinguisticFeatures

class AnalysisReport(BaseModel):
    input_summary: Optional[str] = None
    analysis_date: datetime
    evidence_mode: EvidenceMode
    corpus_version: str
    model_versions: Dict[str, str]
    claims: List[ClaimResult] = []
    coverage_warnings: List[str] = []

class AnalysisStage(BaseModel):
    name: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None

class AnalysisResponse(BaseModel):
    id: str
    status: AnalysisStatus
    stage: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    report: Optional[AnalysisReport] = None
    access_token: Optional[str] = Field(None, exclude=True)
