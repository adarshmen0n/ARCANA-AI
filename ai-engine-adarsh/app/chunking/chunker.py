"""Semantic and Structural Chunker implementation."""

import re
from typing import List, Optional
from app.chunking.models import ChunkingConfig, DocumentChunk
from app.preprocessing.detector import SectionBlock


def split_into_sentences(text: str) -> List[str]:
    """Splits text into sentences using punctuation boundaries while keeping punctuation."""
    # Split on period, exclamation, or question mark followed by whitespace or newline
    parts = re.split(r"((?<=[.?!])\s+)", text)
    sentences: List[str] = []
    current = ""
    for part in parts:
        current += part
        if re.search(r"[.?!]\s*$", current) or "\n" in current:
            if current.strip():
                sentences.append(current.strip())
            current = ""
    if current.strip():
        sentences.append(current.strip())
    return sentences if sentences else [text]


class SemanticChunker:
    """Segments structured educational text into semantic chunks with overlap and metadata."""

    def __init__(self, config: Optional[ChunkingConfig] = None):
        self.config = config or ChunkingConfig()

    def chunk_sections(self, document_id: str, sections: List[SectionBlock]) -> List[DocumentChunk]:
        """Processes structured SectionBlocks into a sequence of DocumentChunks."""
        chunks: List[DocumentChunk] = []
        chunk_index = 0
        doc_prefix = document_id.replace("-", "")[:8]

        for section in sections:
            section_text = section.content.strip()
            if not section_text:
                continue

            # If section text fits comfortably within chunk size, keep it as a coherent single chunk
            if len(section_text) <= self.config.chunk_size_chars:
                token_est = max(1, len(section_text) // 4)
                chunk_id = f"chk-{doc_prefix}-{chunk_index:04d}"
                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        text=section_text,
                        page_number=section.page_number,
                        chapter=section.chapter,
                        section=section.section_number,
                        heading=section.heading,
                        chunk_index=chunk_index,
                        token_count=token_est,
                        character_count=len(section_text),
                    )
                )
                chunk_index += 1
                continue

            # Section exceeds target size: split by paragraphs and sentences with overlap
            sentences = split_into_sentences(section_text)
            current_chunk_sentences: List[str] = []
            current_len = 0

            for sentence in sentences:
                sentence_len = len(sentence)
                if current_len + sentence_len > self.config.chunk_size_chars and current_chunk_sentences:
                    chunk_text = " ".join(current_chunk_sentences).strip()
                    token_est = max(1, len(chunk_text) // 4)
                    chunk_id = f"chk-{doc_prefix}-{chunk_index:04d}"

                    chunks.append(
                        DocumentChunk(
                            chunk_id=chunk_id,
                            document_id=document_id,
                            text=chunk_text,
                            page_number=section.page_number,
                            chapter=section.chapter,
                            section=section.section_number,
                            heading=section.heading,
                            chunk_index=chunk_index,
                            token_count=token_est,
                            character_count=len(chunk_text),
                        )
                    )
                    chunk_index += 1

                    # Retain overlap sentences from tail
                    overlap_sentences: List[str] = []
                    overlap_len = 0
                    for s in reversed(current_chunk_sentences):
                        if overlap_len + len(s) <= self.config.chunk_overlap_chars:
                            overlap_sentences.insert(0, s)
                            overlap_len += len(s)
                        else:
                            break

                    current_chunk_sentences = overlap_sentences
                    current_len = overlap_len

                current_chunk_sentences.append(sentence)
                current_len += sentence_len

            # Flush remaining sentences in section
            if current_chunk_sentences:
                chunk_text = " ".join(current_chunk_sentences).strip()
                if len(chunk_text) >= self.config.min_chunk_size_chars or not chunks:
                    token_est = max(1, len(chunk_text) // 4)
                    chunk_id = f"chk-{doc_prefix}-{chunk_index:04d}"
                    chunks.append(
                        DocumentChunk(
                            chunk_id=chunk_id,
                            document_id=document_id,
                            text=chunk_text,
                            page_number=section.page_number,
                            chapter=section.chapter,
                            section=section.section_number,
                            heading=section.heading,
                            chunk_index=chunk_index,
                            token_count=token_est,
                            character_count=len(chunk_text),
                        )
                    )
                    chunk_index += 1

        return chunks
