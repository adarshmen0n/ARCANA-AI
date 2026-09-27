"""Question Generator producing grounded challenges aligned with Bloom's taxonomy and progressive hints."""

import uuid
from typing import List, Optional
from shared.schemas.game_specification import ChallengeOption
from app.knowledge.models import Concept
from app.generation.models import GeneratedQuestion
from app.generation.hint_generator import hint_generator
from app.objectives.generator import DIFFICULTY_TO_BLOOM
from app.objectives.models import BloomTaxonomyLevel
from app.core.logging import get_logger

logger = get_logger("app.generation.question_generator")


class QuestionGenerator:
    """Generates pedagogically valid assessment challenges with options, progressive hints, and explanations."""

    def generate_question(
        self,
        concept: Concept,
        difficulty: int = 2,
        challenge_type: str = "mcq",
    ) -> GeneratedQuestion:
        """Generates a question tailored to concept, difficulty, and Bloom's taxonomy level."""
        difficulty = max(1, min(5, difficulty))
        bloom_level = DIFFICULTY_TO_BLOOM.get(difficulty, BloomTaxonomyLevel.UNDERSTAND)
        cid = f"q_{concept.concept_id}_{uuid.uuid4().hex[:6]}"

        # Domain-aware question construction for CPU Scheduling & Systems
        name = concept.name
        c_lower = name.lower()

        if "first-come" in c_lower or "fcfs" in c_lower:
            prompt = (
                f"Under the {name} algorithm, three processes P1 (burst=24ms), P2 (burst=3ms), "
                f"and P3 (burst=3ms) arrive simultaneously at time 0 in order P1, P2, P3. "
                f"What is the average waiting time for these processes?"
            )
            options = [
                ChallengeOption(id="A", text="17 ms"),
                ChallengeOption(id="B", text="27 ms"),
                ChallengeOption(id="C", text="3 ms"),
                ChallengeOption(id="D", text="30 ms"),
            ]
            correct_id = "A"
            explanation = (
                "P1 waits 0ms, P2 waits 24ms, and P3 waits 27ms. "
                "The total waiting time is 0 + 24 + 27 = 51ms. "
                "Average waiting time = 51 / 3 = 17ms. This illustrates the convoy effect in FCFS."
            )
            correct_summary = "processes are executed strictly in order of arrival, leading to large waiting times if a long burst leads"

        elif "round robin" in c_lower or "round_robin" in c_lower:
            prompt = (
                f"In {name}, what occurs when the time quantum is chosen to be excessively large?"
            )
            options = [
                ChallengeOption(id="A", text="The algorithm degenerates into First-Come First-Served (FCFS) behavior"),
                ChallengeOption(id="B", text="Context switching overhead completely saturates the CPU"),
                ChallengeOption(id="C", text="Processes suffer from severe starvation"),
                ChallengeOption(id="D", text="The system throughput drops to zero"),
            ]
            correct_id = "A"
            explanation = (
                "If the time quantum is larger than the longest process burst time, "
                "every process runs to completion on its first turn, behaving identically to FCFS."
            )
            correct_summary = "very large time quanta eliminate preemption, causing Round Robin to behave like FCFS"

        elif "shortest job" in c_lower or "sjf" in c_lower:
            prompt = (
                f"Why is {name} provably optimal in minimizing average waiting time, yet difficult to implement in practice?"
            )
            options = [
                ChallengeOption(id="A", text="It is impossible to know the exact length of future CPU bursts in advance"),
                ChallengeOption(id="B", text="It requires an infinite number of priority queues"),
                ChallengeOption(id="C", text="It cannot be preempted under any circumstances"),
                ChallengeOption(id="D", text="It causes excessive context switches compared to all other algorithms"),
            ]
            correct_id = "A"
            explanation = (
                "SJF is mathematically optimal for average wait time, but general-purpose operating systems cannot "
                "predict future burst lengths with certainty, relying instead on exponential averaging heuristics."
            )
            correct_summary = "future CPU burst durations cannot be known precisely in advance in real systems"

        elif "priority" in c_lower:
            prompt = (
                f"What major risk does a strict {name} algorithm present, and what is the standard solution?"
            )
            options = [
                ChallengeOption(id="A", text="Starvation of low-priority processes; solved by Aging"),
                ChallengeOption(id="B", text="Convoy effect; solved by increasing the time slice"),
                ChallengeOption(id="C", text="Deadlock; solved by preemption of all resources"),
                ChallengeOption(id="D", text="Thrashing; solved by adding more physical RAM"),
            ]
            correct_id = "A"
            explanation = (
                "Indefinite blocking (starvation) can occur if higher priority processes continuously arrive. "
                "Aging gradually increases the priority of processes waiting in the ready queue over time."
            )
            correct_summary = "starvation is prevented by aging waiting processes over time"

        else:
            # Pedagogical Bloom-matched generic generator
            prompt = f"Which of the following statements best characterizes {concept.name} within {concept.topic}?"
            options = [
                ChallengeOption(id="A", text=f"It represents: {concept.definition}"),
                ChallengeOption(id="B", text=f"It disables resource sharing and eliminates all concurrency guarantees."),
                ChallengeOption(id="C", text=f"It is exclusively executed in user-space without kernel coordination."),
                ChallengeOption(id="D", text=f"It guarantees zero latency regardless of process workload or resource contention."),
            ]
            correct_id = "A"
            explanation = f"Correct. {concept.definition}"
            correct_summary = f"{concept.name} is defined as: {concept.definition[:80]}"

        # Generate progressive 3-tier hints
        hints = hint_generator.generate_progressive_hints(
            concept=concept,
            prompt=prompt,
            correct_answer_summary=correct_summary,
            difficulty=difficulty,
        )

        return GeneratedQuestion(
            challenge_id=cid,
            concept_id=concept.concept_id,
            bloom_level=bloom_level,
            difficulty=difficulty,
            challenge_type=challenge_type if challenge_type in ["mcq", "concept_puzzle", "boss_override", "calculation"] else "mcq",
            prompt=prompt,
            options=options,
            correct_option_id=correct_id,
            hints=hints,
            explanation=explanation,
        )


question_generator = QuestionGenerator()
