"""FastAPI endpoint for Adaptive Mission Sequencer."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from shared.schemas.game_specification import GameSpecification
from app.sequencer.service import adaptive_sequencer

router = APIRouter(prefix="/sequencer", tags=["Adaptive Mission Sequencer"])


class SequenceMissionRequest(BaseModel):
    student_id: str = Field(..., description="Student identifier")
    document_id: str = Field(..., description="Document / Curriculum identifier")


@router.post("/next-mission", response_model=GameSpecification, summary="Sequence the next adaptive mission for a learner")
async def sequence_next_mission(req: SequenceMissionRequest):
    return adaptive_sequencer.sequence_next_mission(
        student_id=req.student_id,
        document_id=req.document_id,
    )
