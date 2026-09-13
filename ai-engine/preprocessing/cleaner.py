"""Educational text preprocessing and cleaning engine.

Removes extraction artifacts, noise, and repeated headers/footers while
strictly preserving code, mathematics, and pedagogical content.
"""

import re
from typing import List
from schemas.document import ExtractedDocument, Section


class TextCleaner:
    """Cleans educational text while preserving formulas, code, and semantics."""

    # Common running headers/footers, e.g. "Page 12", "Chapter 1", etc.
    PAGE_NUMBER_PATTERN = re.compile(
        r"^(?:page\s+\d+(?:\s+of\s+\d+)?|\d+\s*/\s*\d+|\b\d+\b)$",
        re.IGNORECASE,
    )
    REPEATED_WHITESPACE_PATTERN = re.compile(r"[ \t]+")
    EXCESS_NEWLINES_PATTERN = re.compile(r"\n{3,}")
    HYPHENATED_LINEBREAK_PATTERN = re.compile(r"(\b[a-zA-Z]+)-\n([a-zA-Z]+\b)")

    @classmethod
    def clean_text(cls, text: str) -> str:
        """Clean raw text string while preserving code, tables, and math."""
        if not text:
            return ""

        # Step 1: Repair words broken across line breaks (e.g. 'schedul-\ning' -> 'scheduling')
        cleaned = cls.HYPHENATED_LINEBREAK_PATTERN.sub(r"\1\2", text)

        # Step 2: Normalize carriage returns
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")

        # Step 3: Clean line by line, preserving code or list structures
        lines = cleaned.split("\n")
        cleaned_lines: List[str] = []

        in_code_block = False

        for line in lines:
            stripped = line.strip()

            # Track fenced code blocks
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                cleaned_lines.append(line)
                continue

            if in_code_block:
                # Inside code, preserve exact formatting
                cleaned_lines.append(line)
                continue

            # Drop standalone page numbers or pure noise lines
            if cls.PAGE_NUMBER_PATTERN.match(stripped):
                continue

            # Normalize horizontal whitespace
            normalized_line = cls.REPEATED_WHITESPACE_PATTERN.sub(" ", line).strip()
            cleaned_lines.append(normalized_line)

        # Recombine and compress excessive empty lines
        result = "\n".join(cleaned_lines)
        result = cls.EXCESS_NEWLINES_PATTERN.sub("\n\n", result)
        return result.strip()

    @classmethod
    def preprocess_document(cls, doc: ExtractedDocument) -> ExtractedDocument:
        """Preprocess an extracted document, cleaning all constituent sections."""
        cleaned_sections: List[Section] = []

        for sec in doc.sections:
            cleaned_content = cls.clean_text(sec.content)
            if cleaned_content:
                cleaned_sections.append(
                    Section(
                        section_id=sec.section_id,
                        title=cls.clean_text(sec.title) or sec.title,
                        level=sec.level,
                        content=cleaned_content,
                        page_start=sec.page_start,
                        page_end=sec.page_end,
                        metadata=sec.metadata,
                    )
                )

        cleaned_raw = cls.clean_text(doc.raw_text)

        return ExtractedDocument(
            document_id=doc.document_id,
            filename=doc.filename,
            source_type=doc.source_type,
            title=doc.title,
            sections=cleaned_sections,
            raw_text=cleaned_raw,
            metadata={**doc.metadata, "preprocessed": True},
            created_at=doc.created_at,
        )
