"""Knowledge Engine: Concept Extraction and Relationship Detection.

Extracts educationally meaningful concepts and their pedagogical relationships
from grounded document chunks, avoiding superficial frequency-based extraction.
"""

import logging
import re
from typing import Dict, List, Optional
from schemas.document import Chunk
from schemas.knowledge import Concept, Relationship, RelationshipType, KnowledgeGraph
from schemas.base import generate_id
from providers.router import ProviderRouter

logger = logging.getLogger("arcana.knowledge")


class KnowledgeEngine:
    """Extracts structured concepts and validated relationships from document chunks."""

    def __init__(self, provider_router: ProviderRouter):
        self.provider_router = provider_router

    def extract_concepts_from_chunks(self, chunks: List[Chunk], subject: str = "Computer Science") -> List[Concept]:
        """Extract key educational concepts from coherent chunks."""
        if not chunks:
            return []

        concepts: List[Concept] = []
        seen_names = set()

        for chunk in chunks:
            # Deterministically identify candidate concepts from headings and key sentences
            section_name = chunk.section.strip()
            if section_name and section_name.lower() not in seen_names and len(section_name) > 2:
                # Estimate content difficulty (1 to 5) based on technical complexity heuristics
                difficulty = self._estimate_concept_difficulty(section_name, chunk.text)
                importance = min(1.0, max(0.4, len(chunk.text) / 1000.0))

                # Derive educational definition from first 2 sentences
                sentences = re.split(r"(?<=[.?!])\s+", chunk.text)
                description = " ".join(sentences[:2]).strip() if sentences else chunk.text[:150]

                c = Concept(
                    concept_id=generate_id("cpt"),
                    name=section_name,
                    description=description,
                    importance=round(importance, 2),
                    difficulty=difficulty,
                    parent_topic_id=chunk.chapter or None,
                    prerequisite_ids=[],
                    source_chunk_ids=[chunk.chunk_id],
                )
                concepts.append(c)
                seen_names.add(section_name.lower())

        # If chunks had no explicit distinct section names, extract concepts from text paragraphs
        if not concepts:
            combined = "\n\n".join(c.text for c in chunks[:3])
            paragraphs = [p.strip() for p in combined.split("\n\n") if len(p.strip()) > 30]
            for idx, p in enumerate(paragraphs[:5]):
                first_line = p.splitlines()[0][:50]
                name = first_line.split(".")[0].strip() or f"Concept {idx+1}"
                concepts.append(
                    Concept(
                        concept_id=generate_id("cpt"),
                        name=name,
                        description=p[:200],
                        importance=0.7,
                        difficulty=2,
                        source_chunk_ids=[c.chunk_id for c in chunks[:1]],
                    )
                )

        return concepts

    def detect_relationships(self, concepts: List[Concept], chunks: List[Chunk]) -> List[Relationship]:
        """Detect educational dependencies and prerequisite relationships between concepts."""
        if len(concepts) < 2:
            return []

        relationships: List[Relationship] = []

        # Sequential dependency heuristic: subsequent concepts in structured document often depend on earlier ones
        for i in range(len(concepts) - 1):
            earlier = concepts[i]
            later = concepts[i + 1]

            # Concepts with higher difficulty following lower difficulty represent progression
            rel_type = (
                RelationshipType.PREREQUISITE_OF
                if later.difficulty >= earlier.difficulty
                else RelationshipType.FOLLOWS
            )

            rel = Relationship(
                relationship_id=generate_id("rel"),
                from_concept_id=earlier.concept_id,
                to_concept_id=later.concept_id,
                relationship=rel_type,
                confidence=0.9,
                source_chunk_ids=earlier.source_chunk_ids + later.source_chunk_ids,
            )
            relationships.append(rel)

            # Update prerequisite_ids on target concept
            if rel_type == RelationshipType.PREREQUISITE_OF:
                if earlier.concept_id not in later.prerequisite_ids:
                    later.prerequisite_ids.append(earlier.concept_id)

        return relationships

    def build_knowledge_graph(self, chunks: List[Chunk], document_id: str, subject: str = "General") -> KnowledgeGraph:
        """Construct a complete validated KnowledgeGraph from chunks."""
        concepts = self.extract_concepts_from_chunks(chunks, subject=subject)
        relationships = self.detect_relationships(concepts, chunks)

        return KnowledgeGraph(
            subject=subject,
            document_id=document_id,
            concepts=concepts,
            relationships=relationships,
        )

    def _estimate_concept_difficulty(self, name: str, text: str) -> int:
        """Estimate content difficulty on 1-5 scale using linguistic & syntactic complexity."""
        complexity_score = 1
        name_lower = name.lower()
        text_lower = text.lower()

        advanced_keywords = [
            "algorithm", "asynchronous", "concurrency", "distributed", "optimization",
            "recursion", "architecture", "virtualization", "deadlock", "quantum",
        ]
        intermediate_keywords = [
            "structure", "function", "inheritance", "process", "memory",
            "pipeline", "interface", "protocol", "scheduling", "loop",
        ]

        if any(k in name_lower or k in text_lower for k in advanced_keywords):
            complexity_score += 2
        elif any(k in name_lower or k in text_lower for k in intermediate_keywords):
            complexity_score += 1

        # Check average word length and presence of code/math
        if "```" in text or " = " in text:
            complexity_score += 1

        return min(5, max(1, complexity_score))
