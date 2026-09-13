"""Job status tracking endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from orchestration.pipeline import ArcanaBrainPipeline
from schemas.job import ProcessingJob
from services.deps import get_pipeline

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/{job_id}", response_model=ProcessingJob)
async def get_job_status(
    job_id: str,
    pipeline: ArcanaBrainPipeline = Depends(get_pipeline),
):
    """Retrieve the real-time processing status, progress percentage, or result of an async job."""
    job = pipeline.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return job
