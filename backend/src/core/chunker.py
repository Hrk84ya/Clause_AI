import re

import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter


# Use tiktoken encoder for text-embedding-3-small
_encoder = tiktoken.get_encoding("cl100k_base")


def _count_tokens(text: str) -> int:
    """Count tokens using tiktoken."""
    return len(_encoder.encode(text))


def _detect_sections(text: str) -> list[tuple[str, str]]:
    """
    Split text into sections based on detected headings.
    Returns list of (section_title, section_content) tuples.
    """
    # Heading patterns
    heading_pattern = re.compile(
        r"^("
        r"\d+[\.\d]*\s+[A-Z]"  # Numbered: "1. Introduction", "1.1 Scope"
        r"|[A-Z][A-Z\s]{5,}$"  # ALL CAPS (6+ chars)
        r"|(?:ARTICLE|SECTION|CLAUSE)\s+"  # Prefixed
        r")",
        re.MULTILINE,
    )

    lines = text.split("\n")
    sections: list[tuple[str, str]] = []
    current_title = "Preamble"
    current_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped and heading_pattern.match(stripped):
            # Save previous section
            if current_lines:
                content = "\n".join(current_lines).strip()
                if content:
                    sections.append((current_title, content))
            current_title = stripped
            current_lines = []
        else:
            current_lines.append(line)

    # Don't forget the last section
    if current_lines:
        content = "\n".join(current_lines).strip()
        if content:
            sections.append((current_title, content))

    # If no headings were detected (only the default Preamble section exists),
    # return entire text as one "Document" section
    if not sections:
        sections = [("Document", text.strip())]
    elif len(sections) == 1 and sections[0][0] == "Preamble":
        sections = [("Document", sections[0][1])]

    return sections


def chunk_document(text: str, doc_id: str) -> list[dict]:
    """
    Split document text into section-aware chunks.

    Each chunk dict contains:
    - content: str
    - section_title: str
    - chunk_index: int
    - token_count: int
    """
    sections = _detect_sections(text)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        length_function=_count_tokens,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[dict] = []
    chunk_index = 0

    for section_title, section_content in sections:
        # Split section into chunks
        split_texts = splitter.split_text(section_content)

        for text_chunk in split_texts:
            token_count = _count_tokens(text_chunk)
            chunks.append(
                {
                    "content": text_chunk,
                    "section_title": section_title,
                    "chunk_index": chunk_index,
                    "token_count": token_count,
                }
            )
            chunk_index += 1

    return chunks
