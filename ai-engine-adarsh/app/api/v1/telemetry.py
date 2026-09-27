"""FastAPI endpoints for Telemetry processing emitted by the Game Engine."""

from typing import List
from fastapi import APIRouter
from shared.schemas.game_event import GameEvent
from app.telemetry.service import telemetry_service, TelemetryProcessingResult

router = APIRouter(prefix="/telemetry", tags=["Game Engine Telemetry"])


@router.post("/events", response_model=TelemetryProcessingResult, summary="Process incoming GameEvent telemetry from Game Engine")
async def process_game_event(event: GameEvent):
    return telemetry_service.process_event(event)


@router.get("/students/{student_id}", response_model=List[GameEvent], summary="List telemetry events for a specific student")
async def get_student_events(student_id: str):
    return telemetry_service.get_events_for_student(student_id)
