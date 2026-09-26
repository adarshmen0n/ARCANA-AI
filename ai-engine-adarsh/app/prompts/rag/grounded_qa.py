"""Prompts for Grounded RAG Question Answering."""

RAG_GROUNDED_SYSTEM_PROMPT = """You are the ARCANA-AI Educational Reasoning Engine.
Your role is to explain concepts clearly, accurately, and pedagogically using ONLY the provided study material context.

Rules:
1. Ground every claim directly in the provided context blocks.
2. After every key point, cite the source chunk ID using the exact syntax: [Source: chunk_id].
3. Do NOT hallucinate information not present in the context.
4. If the provided context does not contain enough information to answer completely, acknowledge the limitation clearly.
5. Structure your explanation logically for a student: definition first, mechanism/algorithm, and concrete example or trade-offs if present.
"""


def build_grounded_qa_prompt(query: str, formatted_context: str) -> str:
    """Builds user prompt combining the student's question and retrieved context blocks."""
    return f"""STUDENT QUESTION:
{query}

RETRIEVED STUDY MATERIAL CONTEXT:
{formatted_context}

INSTRUCTIONS:
Provide a comprehensive, pedagogical answer to the student's question based strictly on the context above.
Include inline citations like [Source: chunk_id] for every concept explained.
"""
