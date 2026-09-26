"""Knowledge Engine implementation for extracting concepts and semantic relationships."""

import re
from typing import Dict, List, Optional
from app.core.logging import get_logger
from app.chunking.models import DocumentChunk
from app.chunking.service import chunking_service
from app.providers.factory import get_llm_provider
from app.knowledge.models import (
    Concept,
    ConceptRelationship,
    KnowledgeExtractionResult,
    RelationshipType,
)

logger = get_logger("app.knowledge.engine")


def _sanitize_concept_id(text: str) -> str:
    """Converts a concept name or title to a clean snake_case identifier."""
    cleaned = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[\s-]+", "_", cleaned)


class KnowledgeEngine:
    """Extracts structured concepts and semantic relationships from educational content chunks."""

    def __init__(self):
        self.llm = get_llm_provider()
        self._concepts_by_doc: Dict[str, List[Concept]] = {}
        self._relationships_by_doc: Dict[str, List[ConceptRelationship]] = {}

    def extract_knowledge(self, document_id: str) -> KnowledgeExtractionResult:
        """Processes all document chunks and extracts structured concepts and dependencies."""
        chunks = chunking_service.get_chunks(document_id)
        logger.info(f"Extracting knowledge from {len(chunks)} chunks in document {document_id}")

        concepts: List[Concept] = []
        relationships: List[ConceptRelationship] = []
        seen_concept_ids = set()

        # Heuristic & structural concept identification across chunks
        for idx, chunk in enumerate(chunks):
            heading = chunk.heading
            text = chunk.text

            # Extract primary concept from heading
            concept_name = re.sub(r"^(?:chapter\s+\d+|unit\s+\d+|\d+(?:\.\d+)*)[:\s\-—]*", "", heading, flags=re.I).strip()
            if not concept_name or concept_name.lower() in ("general", "overview", "introduction"):
                # Try finding from first sentence
                first_sent = text.split(".")[0]
                match = re.search(r"\b([A-Z][a-zA-Z0-9\s\-]{3,30})\b", first_sent)
                if match:
                    concept_name = match.group(1).strip()
                else:
                    concept_name = f"Concept {idx + 1}"

            concept_id = _sanitize_concept_id(concept_name)
            if not concept_id:
                concept_id = f"concept_{idx + 1}"

            if concept_id not in seen_concept_ids:
                seen_concept_ids.add(concept_id)

                # Extract definition (first 1-2 sentences of chunk)
                sentences = [s.strip() for s in text.split(".") if s.strip()]
                definition = ". ".join(sentences[:2]) + "." if sentences else text[:180]

                # Assign difficulty based on chunk index / keywords
                difficulty = min(5, max(1, 1 + (idx // 2)))
                if any(w in text.lower() for w in ("advanced", "complex", "algorithm", "trade-off")):
                    difficulty = min(5, difficulty + 1)

                concepts.append(
                    Concept(
                        concept_id=concept_id,
                        name=concept_name,
                        topic=chunk.chapter or "Computer Science",
                        definition=definition,
                        difficulty=difficulty,
                        importance=0.85,
                        examples=[f"Example of {concept_name} application"],
                        source_chunk_ids=[chunk.chunk_id],
                    )
                )

        # Establish prerequisite & dependency relationships sequentially across concepts
        for i in range(len(concepts) - 1):
            source = concepts[i]
            target = concepts[i + 1]

            relationships.append(
                ConceptRelationship(
                    source_concept_id=source.concept_id,
                    relationship_type=RelationshipType.PREREQUISITE_OF,
                    target_concept_id=target.concept_id,
                    description=f"Understanding {source.name} is necessary before studying {target.name}.",
                )
            )

        # Cache results
        self._concepts_by_doc[document_id] = concepts
        self._relationships_by_doc[document_id] = relationships

        logger.info(f"Extracted {len(concepts)} concepts and {len(relationships)} relationships for {document_id}")

        return KnowledgeExtractionResult(
            document_id=document_id,
            concepts=concepts,
            relationships=relationships,
            total_concepts=len(concepts),
            total_relationships=len(relationships),
        )

    def get_concepts(self, document_id: str) -> List[Concept]:
        """Retrieves cached concepts for a document, extracting if not yet processed."""
        if document_id not in self._concepts_by_doc:
            return self.extract_knowledge(document_id).concepts
        return self._concepts_by_doc[document_id]

    def get_relationships(self, document_id: str) -> List[ConceptRelationship]:
        """Retrieves cached relationships for a document."""
        if document_id not in self._relationships_by_doc:
            return self.extract_knowledge(document_id).relationships
        return self._relationships_by_doc[document_id]


# Global singleton instance
knowledge_engine = KnowledgeEngine()
