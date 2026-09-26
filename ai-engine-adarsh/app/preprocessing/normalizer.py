"""Text normalization, noise reduction, and formatting cleanup."""

import re
import unicodedata


def repair_hyphenation(text: str) -> str:
    """Repairs words broken across lines by hyphens (e.g. 'sched-\\nuling' -> 'scheduling')."""
    # Matches a word character, hyphen, newline (and optional whitespace), followed by lowercase word character
    return re.sub(r"(\b[a-zA-Z]+)-\s*\n\s*([a-zA-Z]+\b)", r"\1\2", text)


def clean_whitespace(text: str) -> str:
    """Collapses duplicate whitespace while preserving intentional paragraph breaks."""
    # Replace non-breaking and special spaces with standard space
    text = text.replace("\u00a0", " ").replace("\u200b", "")

    # Replace tabs with spaces
    text = text.replace("\t", " ")

    # Remove trailing/leading spaces on each individual line and collapse duplicate inline spaces
    lines = [re.sub(r"[ ]{2,}", " ", line.strip()) for line in text.splitlines()]

    # Collapse 3 or more consecutive blank lines into 2
    cleaned_text = "\n".join(lines)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

    return cleaned_text.strip()


def remove_document_artifacts(text: str) -> str:
    """Removes common document noise such as standalone page numbers and header artifacts."""
    # Strip patterns like: 'Page 1 of 50', 'Page 12', '- 12 -'
    text = re.sub(r"(?im)^\s*page\s+\d+(\s+of\s+\d+)?\s*$", "", text)
    text = re.sub(r"(?m)^\s*[-—]\s*\d+\s*[-—]\s*$", "", text)

    # Strip non-printable ASCII control characters except \n and \r
    text = "".join(ch for ch in text if ch in ("\n", "\r") or (ord(ch) >= 32 and ord(ch) != 127))

    return text


def normalize_text(text: str) -> str:
    """Master normalization pipeline for raw extracted educational text."""
    if not text:
        return ""

    # 1. Unicode NFKC Normalization (standardizes ligatures, accented chars, full-width glyphs)
    text = unicodedata.normalize("NFKC", text)

    # 2. Repair line-break hyphenations
    text = repair_hyphenation(text)

    # 3. Remove header/footer artifacts & control characters
    text = remove_document_artifacts(text)

    # 4. Clean whitespace & collapse duplicate newlines
    text = clean_whitespace(text)

    return text
