"""Hierarchical semantic chunker for ARCANA AI Brain.

Splits documents along structural boundaries (chapters, sections, subsections,
and coherent paragraph groups) rather than arbitrary character offsets.
"""

import re
from typing import List, Optional
from schemas.document import ExtractedDocument, Section, Chunk
from schemas.base import generate_id


class SemanticChunker:
    """Versioned hierarchical semantic chunking engine."""

    VERSION = "1.0"

    def __init__(self, max_chunk_size: int = 800, min_chunk_size: int = 150, overlap: int = 100):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.overlap = overlap

    def chunk_document(self, doc: ExtractedDocument) -> List[Chunk]:
        """Convert an ExtractedDocument into coherent, traceable semantic chunks."""
        chunks: List[Chunk] = []

        for sec in doc.sections:
            sec_chunks = self._chunk_section(sec, doc.document_id, doc.title)
            chunks.extend(sec_chunks)

        # Fallback if document had no structured sections
        if not chunks and doc.raw_text.strip():
            fallback_sec = Section(
                section_id=generate_id("sec"),
                title=doc.title,
                level=1,
                content=doc.raw_text,
            )
            chunks = self._chunk_section(fallback_sec, doc.document_id, doc.title)

        return chunks

    def _chunk_section(self, section: Section, document_id: str, document_title: str) -> List[Chunk]:
        """Split a single section into coherent semantic chunks respecting paragraph boundaries."""
        paragraphs = [p.strip() for p in section.content.split("\n\n") if p.strip()]
        if not paragraphs:
            return []

        chunks: List[Chunk] = []
        current_buffer: List[str] = []
        current_len = 0

        for p in paragraphs:
            p_len = len(p)

            # If a single paragraph is larger than max_chunk_size, split by sentences
            if p_len > self.max_chunk_size:
                # Flush current buffer first
                if current_buffer:
                    chunk_text = "\n\n".join(current_buffer)
                    chunks.append(
                        self._create_chunk(
                            document_id=document_id,
                            chapter=document_title,
                            section=section.title,
                            text=chunk_text,
                            page_start=section.page_start,
                            page_end=section.page_end,
                            metadata={"level": section.level},
                        )
                    )
                    current_buffer = []
                    current_len = 0

                sentence_chunks = self._split_large_paragraph(p)
                for s_chunk in sentence_chunks:
                    chunks.append(
                        self._create_chunk(
                            document_id=document_id,
                            chapter=document_title,
                            section=section.title,
                            text=s_chunk,
                            page_start=section.page_start,
                            page_end=section.page_end,
                            metadata={"level": section.level, "sub_split": True},
                        )
                    )
                continue

            # Check if adding this paragraph exceeds maximum chunk size
            if current_len + p_len + 2 > self.max_chunk_size and current_len >= self.min_chunk_size:
                chunk_text = "\n\n".join(current_buffer)
                chunks.append(
                    self._create_chunk(
                        document_id=document_id,
                        chapter=document_title,
                        section=section.title,
                        text=chunk_text,
                        page_start=section.page_start,
                        page_end=section.page_end,
                        metadata={"level": section.level},
                    )
                )

                # Keep overlap from last paragraph if small enough
                last_p = current_buffer[-1] if current_buffer else ""
                if len(last_p) <= self.overlap:
                    current_buffer = [last_p, p]
                    current_len = len(last_p) + 2 + p_len
                else:
                    current_buffer = [p]
                    current_len = p_len
            else:
                current_buffer.append(p)
                current_len += p_len + 2

        if current_buffer:
            chunk_text = "\n\n".join(current_buffer)
            chunks.append(
                self._create_chunk(
                    document_id=document_id,
                    chapter=document_title,
                    section=section.title,
                    text=chunk_text,
                    page_start=section.page_start,
                    page_end=section.page_end,
                    metadata={"level": section.level},
                )
            )

        return chunks

    def _split_large_paragraph(self, text: str) -> List[str]:
        """Split a long paragraph along sentence boundaries."""
        sentences = re.split(r"(?<=[.?!])\s+", text)
        result: List[str] = []
        buf: List[str] = []
        buf_len = 0

        for s in sentences:
            s_len = len(s)
            if buf_len + s_len + 1 > self.max_chunk_size and buf:
                result.append(" ".join(buf))
                buf = [s]
                buf_len = s_len
            else:
                buf.append(s)
                buf_len += s_len + 1

        if buf:
            result.append(" ".join(buf))
        return result

    def _create_chunk(
        self,
        document_id: str,
        chapter: str,
        section: str,
        text: str,
        page_start: Optional[int],
        page_end: Optional[int],
        metadata: dict,
    ) -> Chunk:
        return Chunk(
            chunk_id=generate_id("chk"),
            document_id=document_id,
            chapter=chapter,
            section=section,
            text=text.strip(),
            page_start=page_start,
            page_end=page_end,
            chunking_version=self.VERSION,
            metadata=metadata,
        )
