import os

files = {
    "app/__init__.py": "# app init",
    "app/schemas/__init__.py": "# schemas init",
    "app/models/__init__.py": "# models init",
    "app/api/__init__.py": "# api init",
    "app/services/__init__.py": "# services init",
    "app/services/retrieval/__init__.py": "# retrieval init",
    "app/services/evidence/__init__.py": "# evidence init",
    "app/services/providers/__init__.py": "# providers init",
    "app/utils/__init__.py": "# utils init",

    "app/models/database.py": """
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import String, JSON, DateTime, Enum as SQLEnum, Text
from datetime import datetime
import uuid
from app.config import settings
from app.schemas.enums import AnalysisStatus, EvidenceMode

Base = declarative_base()
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class AnalysisJob(Base):
    __tablename__ = 'analysis_jobs'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status: Mapped[AnalysisStatus] = mapped_column(SQLEnum(AnalysisStatus), default=AnalysisStatus.queued)
    stage: Mapped[str] = mapped_column(String(255), nullable=True)
    input_text: Mapped[str] = mapped_column(Text, nullable=True)
    input_url: Mapped[str] = mapped_column(String(2048), nullable=True)
    evidence_mode: Mapped[EvidenceMode] = mapped_column(SQLEnum(EvidenceMode), default=EvidenceMode.local)
    access_token_hash: Mapped[str] = mapped_column(String(255), nullable=True)
    report_json: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
""",
    "app/api/router.py": """
from fastapi import APIRouter
from . import health, analyses

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(analyses.router, prefix="/analyses", tags=["analyses"])
""",
    "app/api/health.py": """
from fastapi import APIRouter
from app.schemas.health import HealthResponse, ReadinessResponse

router = APIRouter()

@router.get("", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", version="0.1.0")

@router.get("/readiness", response_model=ReadinessResponse)
async def readiness_check():
    return ReadinessResponse(
        status="ok",
        models={"nli": "loaded", "embedding": "loaded"},
        corpus="v1",
        providers={"brave": "ok", "google_factcheck": "ok"}
    )
""",
    "app/api/analyses.py": """
from fastapi import APIRouter, HTTPException, Depends, Header
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.schemas.enums import AnalysisStatus
from app.models.database import AsyncSessionLocal, AnalysisJob
import uuid
from datetime import datetime

router = APIRouter()

@router.post("", response_model=AnalysisResponse, status_code=202)
async def create_analysis(request: AnalysisRequest):
    job_id = str(uuid.uuid4())
    token = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        new_job = AnalysisJob(
            id=job_id,
            input_text=request.input_text,
            input_url=str(request.input_url) if request.input_url else None,
            evidence_mode=request.evidence_mode,
            status=AnalysisStatus.queued,
            access_token_hash=token,
            created_at=datetime.utcnow()
        )
        session.add(new_job)
        await session.commit()
    
    return AnalysisResponse(
        id=job_id,
        status=AnalysisStatus.queued,
        created_at=datetime.utcnow(),
        access_token=token
    )

@router.get("/{id}", response_model=AnalysisResponse)
async def get_analysis(id: str, authorization: str = Header(...)):
    async with AsyncSessionLocal() as session:
        job = await session.get(AnalysisJob, id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        # In a real app we verify access_token_hash
        return AnalysisResponse(
            id=job.id,
            status=job.status,
            stage=job.stage,
            created_at=job.created_at,
            completed_at=job.completed_at
        )

@router.post("/{id}/cancel")
async def cancel_analysis(id: str):
    async with AsyncSessionLocal() as session:
        job = await session.get(AnalysisJob, id)
        if job:
            job.status = AnalysisStatus.cancelled
            await session.commit()
    return {"status": "cancelled"}

@router.delete("/{id}")
async def delete_analysis(id: str):
    async with AsyncSessionLocal() as session:
        job = await session.get(AnalysisJob, id)
        if job:
            await session.delete(job)
            await session.commit()
    return {"status": "deleted"}
""",
    "app/main.py": """
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.api.router import api_router
from app.models.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Init models here in a background thread or lazy load
    yield

app = FastAPI(title="ClaimLens API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
""",
    "app/services/model_manager.py": """
import spacy
from sentence_transformers import SentenceTransformer
from transformers import pipeline

class ModelManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance
        
    def _init(self):
        self.nlp = None
        self.encoder = None
        self.nli = None
        
    def load_models(self, embedding_model: str, nli_model: str):
        # Dummy implementations or lazy load for production 
        pass

model_manager = ModelManager()
""",
    "app/services/input_processor.py": """
from bs4 import BeautifulSoup
import httpx
from readability import Document
from langdetect import detect

class InputProcessor:
    @staticmethod
    async def process_url(url: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
        doc = Document(resp.text)
        soup = BeautifulSoup(doc.summary(), 'lxml')
        return soup.get_text(separator=' ', strip=True)
    
    @staticmethod
    def detect_lang(text: str) -> str:
        return detect(text)
""",
    "app/services/claim_extractor.py": """
class ClaimExtractor:
    def __init__(self, nlp):
        self.nlp = nlp
        
    def extract_claims(self, text: str, max_claims: int = 6):
        # spacy implementation
        return []
""",
    "app/services/retrieval/corpus.py": """
class CorpusManager:
    def load_corpus(self, path: str):
        pass
""",
    "app/services/retrieval/bm25.py": """
from rank_bm25 import BM25Okapi

class BM25Retriever:
    def __init__(self, corpus):
        self.corpus = corpus
        tokenized = [doc.split() for doc in corpus]
        self.bm25 = BM25Okapi(tokenized)
""",
    "app/services/retrieval/semantic.py": """
class SemanticRetriever:
    def __init__(self, encoder, corpus):
        self.encoder = encoder
        self.embeddings = self.encoder.encode(corpus)
""",
    "app/services/retrieval/fusion.py": """
class ReciprocalRankFusion:
    def fuse(self, lists, k=60):
        scores = {}
        for lst in lists:
            for rank, item in enumerate(lst):
                scores[item] = scores.get(item, 0) + 1 / (k + rank + 1)
        return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
""",
    "app/services/evidence/stance.py": """
class StanceDetector:
    def __init__(self, model):
        self.model = model
    def get_stance(self, premise, hypothesis):
        return {"supports": 0.5, "contradicts": 0.1, "neutral": 0.4}
""",
    "app/services/evidence/policy.py": """
from app.schemas.enums import ClaimOutcome

class PolicyEngine:
    def evaluate(self, stances):
        return ClaimOutcome.insufficient
""",
    "app/services/source_analysis.py": """
class SourceAnalyzer:
    def analyze(self, url):
        return None
""",
    "app/services/worker.py": """
import asyncio

class Worker:
    async def process_job(self, job_id: str):
        pass
""",
    "app/services/providers/safe_fetch.py": """
import httpx

class SafeFetch:
    @staticmethod
    async def fetch(url):
        async with httpx.AsyncClient() as client:
            return await client.get(url)
""",
    "app/services/providers/brave_search.py": """
import httpx
from app.config import settings

class BraveSearch:
    def search(self, query):
        pass
""",
    "app/services/providers/factcheck.py": """
class GoogleFactCheck:
    def search(self, query):
        pass
""",
    "app/utils/security.py": """
import hashlib
import secrets

def generate_token():
    return secrets.token_urlsafe(32)

def hash_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()
""",
    "app/utils/text.py": """
def normalize_text(text: str) -> str:
    return text.strip()

def jaccard_similarity(a: str, b: str) -> float:
    set_a, set_b = set(a.split()), set(b.split())
    if not set_a or not set_b: return 0.0
    return len(set_a & set_b) / len(set_a | set_b)
"""
}

base_dir = r"c:\\Users\\Lenovo\\Desktop\\ai project\\backend"

for path, content in files.items():
    full_path = os.path.join(base_dir, path.replace("/", os.sep))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\\n")
print("Files generated successfully.")
