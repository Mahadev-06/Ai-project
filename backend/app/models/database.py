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