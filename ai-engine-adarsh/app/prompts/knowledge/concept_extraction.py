"""Prompts for Knowledge and Concept Extraction."""

CONCEPT_EXTRACTION_SYSTEM_PROMPT = """You are the ARCANA-AI Knowledge Engineering Specialist.
Your objective is to transform raw educational text into structured concepts and dependency relationships.

For each concept identified:
1. Generate a standardized machine key (lowercase, snake_case, e.g., 'cpu_scheduling_fcfs').
2. Provide a clear, educational definition.
3. Assign difficulty from 1 (Very Easy / Foundational) to 5 (Advanced / Complex).
4. Discover relationships:
   - 'prerequisite_of': Concept A must be understood before Concept B.
   - 'depends_on': Concept B relies on understanding Concept A.
   - 'part_of': Concept B is a sub-component of Concept A.
   - 'follows': Concept B logically appears after Concept A in learning sequence.
"""


def build_concept_extraction_prompt(section_title: str, text: str) -> str:
    """Builds prompt instructing LLM to extract concepts and relationships from educational text."""
    return f"""SECTION: {section_title}

TEXT CONTENT:
{text}

TASK:
Extract all distinct educational concepts from the text above and specify how they are related.
Ensure every concept includes its definition, difficulty (1-5), and explicit prerequisite relationships.
"""
