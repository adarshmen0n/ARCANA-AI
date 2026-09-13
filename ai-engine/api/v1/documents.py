"""Document processing endpoints."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from orchestration.pipeline import ArcanaBrainPipeline
from schemas.game_spec import GameSpecification
from services.deps import get_pipeline

router = APIRouter(prefix="/documents", tags=["Documents"])


class ProcessTextRequest(BaseModel):
    text: str
    filename: str = "notes.txt"
    subject: str = "Computer Science"
    campaign_title: Optional[str] = None
    async_mode: bool = True


class ProcessResponse(BaseModel):
    mode: str
    job_id: Optional[str] = None
    specification: Optional[Dict[str, Any]] = None
    timings_ms: Optional[Dict[str, float]] = None


@router.post("/process", response_model=ProcessResponse)
async def process_document(
    file: Optional[UploadFile] = File(None),
    subject: str = Form("Computer Science"),
    campaign_title: Optional[str] = Form(None),
    async_mode: bool = Form(True),
    pipeline: ArcanaBrainPipeline = Depends(get_pipeline),
):
    """Process an uploaded educational file (PDF, DOCX, PPTX, TXT) into a Game Specification."""
    if not file:
        raise HTTPException(status_code=400, detail="No file was uploaded.")

    content = await file.read()
    filename = file.filename or "uploaded_document.txt"

    if async_mode:
        job_id = pipeline.submit_async_job(
            file_bytes=content,
            filename=filename,
            subject=subject,
            campaign_title=campaign_title,
        )
        return ProcessResponse(mode="async", job_id=job_id)
    else:
        try:
            result = pipeline.execute_sync(
                file_bytes=content,
                filename=filename,
                subject=subject,
                campaign_title=campaign_title,
            )
            return ProcessResponse(
                mode="sync",
                specification=result.game_specification.model_dump(),
                timings_ms=result.timings_ms,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/process-text", response_model=ProcessResponse)
async def process_raw_text(
    req: ProcessTextRequest,
    pipeline: ArcanaBrainPipeline = Depends(get_pipeline),
):
    """Process raw educational text into a Game Specification."""
    content = req.text.encode("utf-8")

    if req.async_mode:
        job_id = pipeline.submit_async_job(
            file_bytes=content,
            filename=req.filename,
            subject=req.subject,
            campaign_title=req.campaign_title,
        )
        return ProcessResponse(mode="async", job_id=job_id)
    else:
        try:
            result = pipeline.execute_sync(
                file_bytes=content,
                filename=req.filename,
                subject=req.subject,
                campaign_title=req.campaign_title,
            )
            return ProcessResponse(
                mode="sync",
                specification=result.game_specification.model_dump(),
                timings_ms=result.timings_ms,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
