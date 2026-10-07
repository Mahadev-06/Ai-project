"""Analysis API endpoints.

POST /analyses - Create and enqueue analysis
GET  /analyses/{id} - Get job status and report
POST /analyses/{id}/cancel - Request cancellation
DELETE /analyses/{id} - Remove job data
"""
import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import re
from fastapi import APIRouter, HTTPException, Header, BackgroundTasks, status
from langdetect import detect, LangDetectException

from app.config import get_settings
from app.models.database import AsyncSessionLocal, AnalysisJob
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.schemas.enums import AnalysisStatus, EvidenceMode
from app.utils.security import generate_token, hash_token, verify_token

logger = logging.getLogger(__name__)
router = APIRouter()

# Track active jobs count
_active_jobs = 0
_active_lock = asyncio.Lock()


async def _run_analysis(job_id: str, input_text: str, input_url: Optional[str],
                        evidence_mode: str) -> None:
    """Background task that runs the analysis worker."""
    global _active_jobs
    from app.services.worker import analysis_worker

    async def update_callback(jid: str, stage: str, job_status: str,
                              report: Optional[dict]) -> None:
        """Update job status in the database."""
        async with AsyncSessionLocal() as session:
            job = await session.get(AnalysisJob, jid)
            if job is None:
                return
            job.stage = stage
            job.status = AnalysisStatus(job_status) if job_status in AnalysisStatus.__members__ else job.status
            job.updated_at = datetime.now(timezone.utc)
            if report is not None:
                job.report_json = report
            if job_status in ('completed', 'failed', 'cancelled', 'partial'):
                job.completed_at = datetime.now(timezone.utc)
            await session.commit()

    try:
        await analysis_worker.process_job(
            job_id=job_id,
            input_text=input_text,
            input_url=input_url,
            evidence_mode=evidence_mode,
            update_callback=update_callback,
        )
    except Exception as e:
        logger.error(f'Analysis job {job_id} failed: {e}', exc_info=True)
        async with AsyncSessionLocal() as session:
            job = await session.get(AnalysisJob, job_id)
            if job:
                job.status = AnalysisStatus.failed
                job.stage = 'failed'
                job.completed_at = datetime.now(timezone.utc)
                job.report_json = job.report_json or {}
                if isinstance(job.report_json, dict):
                    job.report_json['coverage_warnings'] = job.report_json.get('coverage_warnings', [])
                    job.report_json['coverage_warnings'].append(f'Analysis failed: {str(e)[:200]}')
                await session.commit()
    finally:
        async with _active_lock:
            _active_jobs = max(0, _active_jobs - 1)


@router.post('', status_code=status.HTTP_202_ACCEPTED)
async def create_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Create and enqueue a new analysis job."""
    global _active_jobs
    settings = get_settings()

    # Check queue capacity
    async with _active_lock:
        if _active_jobs >= settings.MAX_QUEUE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f'Server is busy. Maximum {settings.MAX_QUEUE_SIZE} concurrent analyses allowed.',
            )

    # Validate input
    input_text = (request.input_text or '').strip()
    input_url = request.input_url

    if not input_text and not input_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Either input_text or input_url must be provided.',
        )

    if input_text and len(input_text) > settings.MAX_INPUT_CHARS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Input text exceeds maximum of {settings.MAX_INPUT_CHARS} characters.',
        )

    # Language detection
    if input_text and len(input_text) > 20:
        try:
            lang = detect(input_text)
            if lang != 'en':
                # Check for common false positives on short sentences
                words = [w.lower() for w in re.findall(r'[a-zA-Z]+', input_text)]
                en_stop = {
                    'the', 'is', 'at', 'in', 'on', 'of', 'and', 'to', 'a', 'an',
                    'water', 'boils', 'sea', 'level', 'from', 'with', 'by', 'that',
                    'this', 'are', 'was', 'were', 'has', 'have', 'had', 'not',
                    'but', 'or', 'for', 'it', 'its', 'earth', 'sun', 'moon',
                    'mountain', 'tallest', 'degrees'
                }
                foreign_stop = {
                    'el', 'la', 'los', 'las', 'del', 'al', 'por', 'para', 'con',
                    'en', 'y', 'es', 'son', 'un', 'una', 'unos', 'unas', 'pero',
                    'mas', 'como', 'su', 'sus', 'le', 'les', 'de', 'du', 'des',
                    'est', 'dans', 'pour', 'qui', 'que', 'und', 'der', 'die',
                    'das', 'den', 'dem', 'des', 'ein', 'eine', 'nicht', 'mit',
                    'auf', 'für', 'von', 'im', 'ist'
                }
                en_count = sum(1 for w in words if w in en_stop)
                foreign_count = sum(1 for w in words if w in foreign_stop)
                if foreign_count >= en_count:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f'Detected language "{lang}". ClaimLens currently supports English only. '
                               f'Non-English text may produce unreliable results.',
                    )
        except LangDetectException:
            pass  # Short text or uncertain detection — proceed conservatively

    # Validate evidence mode
    evidence_mode = request.evidence_mode or 'auto'

    # Create job
    job_id = str(uuid.uuid4())
    access_token = generate_token()
    token_hash = hash_token(access_token)

    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=settings.JOB_RETENTION_HOURS)

    async with AsyncSessionLocal() as session:
        job = AnalysisJob(
            id=job_id,
            status=AnalysisStatus.queued,
            stage='queued',
            input_text=input_text if input_text else None,
            input_url=str(input_url) if input_url else None,
            evidence_mode=EvidenceMode(evidence_mode),
            access_token_hash=token_hash,
            created_at=now,
            updated_at=now,
            expires_at=expires,
        )
        session.add(job)
        await session.commit()

    # Increment active count and start background task
    async with _active_lock:
        _active_jobs += 1

    background_tasks.add_task(
        _run_analysis, job_id, input_text or '', input_url, evidence_mode,
    )

    logger.info(f'Analysis job {job_id} created (mode={evidence_mode})')

    return {
        'id': job_id,
        'status': 'queued',
        'stage': 'queued',
        'created_at': now.isoformat(),
        'access_token': access_token,
    }


@router.get('/{job_id}')
async def get_analysis(job_id: str, authorization: str = Header(default='')):
    """Get analysis status and report."""
    token = authorization.replace('Bearer ', '').strip()

    async with AsyncSessionLocal() as session:
        job = await session.get(AnalysisJob, job_id)

        if not job:
            raise HTTPException(status_code=404, detail='Analysis not found')

        # Verify access token
        if not token or not verify_token(token, job.access_token_hash):
            raise HTTPException(status_code=403, detail='Invalid or missing access token')

        return {
            'id': job.id,
            'status': job.status.value if hasattr(job.status, 'value') else str(job.status),
            'stage': job.stage,
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'input_text': job.input_text,
            'input_url': job.input_url,
            'evidence_mode': job.evidence_mode.value if hasattr(job.evidence_mode, 'value') else str(job.evidence_mode),
            'report': job.report_json,
        }


@router.post('/{job_id}/cancel')
async def cancel_analysis(job_id: str, authorization: str = Header(default='')):
    """Request cancellation of a running analysis."""
    token = authorization.replace('Bearer ', '').strip()

    async with AsyncSessionLocal() as session:
        job = await session.get(AnalysisJob, job_id)

        if not job:
            raise HTTPException(status_code=404, detail='Analysis not found')

        if not token or not verify_token(token, job.access_token_hash):
            raise HTTPException(status_code=403, detail='Invalid or missing access token')

        if job.status in (AnalysisStatus.completed, AnalysisStatus.failed, AnalysisStatus.cancelled):
            return {'status': str(job.status.value), 'detail': 'Job already finished'}

        # Request cancellation from worker
        from app.services.worker import analysis_worker
        analysis_worker.request_cancel(job_id)

        job.status = AnalysisStatus.cancelled
        job.updated_at = datetime.now(timezone.utc)
        await session.commit()

    return {'status': 'cancelled', 'detail': 'Cancellation requested. Currently running model call may finish first.'}


@router.delete('/{job_id}')
async def delete_analysis(job_id: str, authorization: str = Header(default='')):
    """Delete an analysis and its data."""
    token = authorization.replace('Bearer ', '').strip()

    async with AsyncSessionLocal() as session:
        job = await session.get(AnalysisJob, job_id)

        if not job:
            raise HTTPException(status_code=404, detail='Analysis not found')

        if not token or not verify_token(token, job.access_token_hash):
            raise HTTPException(status_code=403, detail='Invalid or missing access token')

        await session.delete(job)
        await session.commit()

    return {'status': 'deleted'}