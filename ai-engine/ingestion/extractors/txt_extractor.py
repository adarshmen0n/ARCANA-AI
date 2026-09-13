"""Plaintext extractor for TXT files."""

import re
from typing import List
from schemas.document import ExtractedDocument, Section
from schemas.base import generate_id
from .base import BaseExtractor


class TextExtractor(BaseExtractor):
    """Deterministic extractor for plaintext (.txt) documents."""

    def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = file_bytes.decode("latin-1", errors="replace")

        lines = text.splitlines()
        sections: List[Section] = []
        current_title = "Overview"
        current_lines: List[str] = []
        current_level = 1

        for line in lines:
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if header_match:
                if current_lines:
                    sections.append(
                        Section(
                            section_id=generate_id("sec"),
                            title=current_title,
                            level=current_level,
                            content="\n".join(current_lines).strip(),
                            page_start=1,
                            page_end=1,
                        )
                    )
                    current_lines = []
                current_level = len(header_match.group(1))
                current_title = header_match.group(2).strip()
            else:
                current_lines.append(line)

        if current_lines:
            sections.append(
                Section(
                    section_id=generate_id("sec"),
                    title=current_title,
                    level=current_level,
                    content="\n".join(current_lines).strip(),
                    page_start=1,
                    page_end=1,
                )
            )

        title = filename.rsplit(".", 1)[0].replace("_", " ").title()
        return ExtractedDocument(
            document_id=generate_id("doc"),
            filename=filename,
            source_type="txt",
            title=title,
            sections=sections,
            raw_text=text,
            metadata={"line_count": len(lines), "char_count": len(text)},
        )
