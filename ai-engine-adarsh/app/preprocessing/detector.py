"""Chapter and Section Detection for Educational Documents."""

import re
from typing import List, Optional
from pydantic import BaseModel, Field


class SectionBlock(BaseModel):
    heading: str = Field(..., description="Detected section or chapter title")
    chapter: Optional[str] = Field(None, description="Parent chapter name or number")
    section_number: Optional[str] = Field(None, description="Hierarchical section number (e.g. '5.3.1')")
    content: str = Field(..., description="Text content belonging to this section")
    page_number: Optional[int] = Field(None, description="Starting page number if known")


# Regular expressions for detecting structural boundaries
CHAPTER_PATTERN = re.compile(
    r"(?im)^(?:chapter\s+(\d+|[ivxlcdm]+)[:\s\.\-—]*(.*)|module\s+(\d+)[:\s\.\-—]*(.*)|unit\s+(\d+)[:\s\.\-—]*(.*))$"
)

SECTION_PATTERN = re.compile(
    r"(?m)^(?:\#{1,4}\s+(.*)|(\d+(?:\.\d+)+)\s+([A-Z].*)|([A-Z][A-Z0-9\s]{3,50}:?))$"
)


def detect_sections(text: str, default_page: Optional[int] = None) -> List[SectionBlock]:
    """Scans text for chapter and section headings, segmenting content into structured SectionBlocks."""
    lines = text.splitlines()
    blocks: List[SectionBlock] = []

    current_chapter: Optional[str] = None
    current_heading = "Introduction / Overview"
    current_section_num: Optional[str] = None
    current_content_lines: List[str] = []

    def flush_current():
        nonlocal current_content_lines
        content = "\n".join(current_content_lines).strip()
        if content:
            blocks.append(
                SectionBlock(
                    heading=current_heading,
                    chapter=current_chapter,
                    section_number=current_section_num,
                    content=content,
                    page_number=default_page,
                )
            )
        current_content_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_content_lines.append("")
            continue

        # Check for chapter boundary
        chapter_match = CHAPTER_PATTERN.match(stripped)
        if chapter_match:
            flush_current()
            current_chapter = stripped
            current_heading = stripped
            current_section_num = None
            continue

        # Check for section boundary
        section_match = SECTION_PATTERN.match(stripped)
        if section_match:
            # Avoid matching short sentences or fragments
            if len(stripped) < 80 and not stripped.endswith((".", ",", ";")):
                flush_current()
                if section_match.group(1):  # Markdown # heading
                    current_heading = section_match.group(1).strip()
                    current_section_num = None
                elif section_match.group(2):  # Numbered: 5.3 CPU Scheduling
                    current_section_num = section_match.group(2).strip()
                    current_heading = section_match.group(3).strip()
                else:  # ALL CAPS HEADING
                    current_heading = stripped
                    current_section_num = None
                continue

        current_content_lines.append(stripped)

    # Flush remainder
    flush_current()

    # Fallback if no sections were detected
    if not blocks and text.strip():
        blocks.append(
            SectionBlock(
                heading="General Content",
                chapter=None,
                section_number=None,
                content=text.strip(),
                page_number=default_page,
            )
        )

    return blocks
