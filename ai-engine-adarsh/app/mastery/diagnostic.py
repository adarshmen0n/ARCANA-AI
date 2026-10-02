"""Cognitive Misconception Diagnostic Subsystem for root-cause error analysis."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from app.knowledge.models import Concept
from app.core.logging import get_logger

logger = get_logger("app.mastery.diagnostic")


class MisconceptionCategory(str, Enum):
    OVERGENERALIZATION = "overgeneralization"
    MECHANISTIC_CONFUSION = "mechanistic_confusion"
    INVARIANT_VIOLATION = "invariant_violation"
    COMPUTATIONAL_SLIP = "computational_slip"
    BOUNDARY_CONDITION_ERROR = "boundary_condition_error"


class MisconceptionDiagnosis(BaseModel):
    concept_id: str
    selected_option_id: str
    is_correct: bool
    category: Optional[MisconceptionCategory] = None
    root_cause_explanation: str
    cognitive_conflict_prompt: str
    remedial_nudge: str


class MisconceptionDiagnosticEngine:
    """Diagnoses the precise cognitive fallacy underlying a student's selected answer choice."""

    @staticmethod
    def diagnose_response(
        concept: Concept,
        selected_option_id: str,
        correct_option_id: str,
        challenge_prompt: str,
        options: List[dict],
    ) -> MisconceptionDiagnosis:
        """Performs deep diagnostic analysis on learner response."""
        is_correct = (selected_option_id.strip().upper() == correct_option_id.strip().upper())

        if is_correct:
            return MisconceptionDiagnosis(
                concept_id=concept.concept_id,
                selected_option_id=selected_option_id,
                is_correct=True,
                root_cause_explanation="Student correctly identified and verified the governing architectural invariants.",
                cognitive_conflict_prompt="What secondary trade-off must be managed under this design choice?",
                remedial_nudge="Consolidate mastery by considering high-concurrency or edge-case constraints.",
            )

        cid_lower = concept.concept_id.lower()
        name_lower = concept.name.lower()

        # Domain-specific root-cause diagnostic mapping
        if "fcfs" in cid_lower or "first-come" in name_lower:
            category = MisconceptionCategory.INVARIANT_VIOLATION
            root_cause = (
                "The student likely assumed arrival order guarantees balanced waiting time, "
                "overlooking the Convoy Effect where large CPU bursts paralyze subsequent short tasks."
            )
            conflict = "If Task A takes 1,000ms and Task B takes 1ms, how fair is strict arrival ordering to Task B?"
            nudge = "Trace the waiting time queue: total wait time is dominated by the head of the FIFO queue."

        elif "round_robin" in cid_lower or "round robin" in name_lower:
            category = MisconceptionCategory.BOUNDARY_CONDITION_ERROR
            root_cause = (
                "The student confused the extremes of the time quantum spectrum: "
                "an excessively large quantum degenerates into FCFS, whereas an excessively small quantum saturates CPU overhead."
            )
            conflict = "If the time slice is 1 microsecond and switching takes 10 microseconds, what percentage of work is useful?"
            nudge = "Evaluate the relationship between quantum size, context switch duration, and effective throughput."

        elif "shortest_job" in cid_lower or "sjf" in name_lower:
            category = MisconceptionCategory.OVERGENERALIZATION
            root_cause = (
                "The student assumed mathematical optimality guarantees implementability, "
                "overlooking that future CPU burst lengths cannot be known deterministically in general-purpose systems."
            )
            conflict = "How can an OS accurately dispatch the shortest process before it has even finished running?"
            nudge = "Distinguish between theoretical mathematical optimality and practical heuristic approximation (exponential smoothing)."

        elif "priority" in cid_lower:
            category = MisconceptionCategory.MECHANISTIC_CONFUSION
            root_cause = (
                "The student overlooked the starvation vulnerability of static priority queues, "
                "or confused dynamic Aging with static priority reassignment."
            )
            conflict = "If high-priority threads continuously arrive every millisecond, when will low-priority threads ever run?"
            nudge = "Review how Aging progressively shifts priority over time to prevent indefinite starvation."

        else:
            category = MisconceptionCategory.MECHANISTIC_CONFUSION
            root_cause = f"The student selected an option conflicting with the foundational definition of {concept.name}."
            conflict = f"Does {concept.name} eliminate resource contention or merely govern its distribution?"
            nudge = f"Re-read the core invariant: {concept.definition[:90]}..."

        logger.info(
            f"[Diagnosis] Concept '{concept.concept_id}' Option '{selected_option_id}': "
            f"category={category.value}, cause='{root_cause[:60]}...'"
        )

        return MisconceptionDiagnosis(
            concept_id=concept.concept_id,
            selected_option_id=selected_option_id,
            is_correct=False,
            category=category,
            root_cause_explanation=root_cause,
            cognitive_conflict_prompt=conflict,
            remedial_nudge=nudge,
        )


diagnostic_engine = MisconceptionDiagnosticEngine()
