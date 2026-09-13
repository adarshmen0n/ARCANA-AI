"""Analytics and closed-loop adaptive learning endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from schemas.personalization import GameplayEvent, StudentState, NextAction
from schemas.learning_graph import LearningGraph
from personalization.mastery_engine import MasteryEngine
from personalization.adaptive_engine import AdaptiveEngine
from orchestration.pipeline import ArcanaBrainPipeline
from services.deps import get_pipeline

router = APIRouter(prefix="/analytics", tags=["Analytics & Adaptation"])


class EventBatchRequest(BaseModel):
    state: StudentState
    events: list[GameplayEvent]


class AdaptationResponse(BaseModel):
    updated_state: StudentState
    next_action: NextAction


@router.post("/events", response_model=AdaptationResponse)
async def process_gameplay_events(
    req: EventBatchRequest,
    pipeline: ArcanaBrainPipeline = Depends(get_pipeline),
):
    """Process gameplay events from Dasarth's Game Engine, update mastery, and calculate next learning action."""
    current_state = req.state
    for evt in req.events:
        current_state = MasteryEngine.process_gameplay_event(current_state, evt)

    # Use default/active learning graph or construct a basic graph
    active_graph = LearningGraph(nodes={}, topological_order=[])
    next_action = AdaptiveEngine.determine_next_action(active_graph, current_state)

    return AdaptationResponse(
        updated_state=current_state,
        next_action=next_action,
    )
