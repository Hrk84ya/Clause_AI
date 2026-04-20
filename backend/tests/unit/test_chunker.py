import pytest
from src.core.chunker import chunk_document, _count_tokens, _detect_sections


class TestDetectSections:
    def test_numbered_sections(self):
        text = "1. Introduction\nThis is the intro.\n2. Terms\nThese are the terms."
        sections = _detect_sections(text)
        assert len(sections) >= 2
        assert any("Introduction" in title for title, _ in sections)

    def test_no_sections(self):
        text = "Just a plain paragraph with no headings."
        sections = _detect_sections(text)
        assert len(sections) == 1
        assert sections[0][0] == "Document"


class TestChunkDocument:
    def test_short_document(self):
        """Short document produces at least one chunk."""
        text = "This is a short legal document about terms and conditions."
        chunks = chunk_document(text, "test-doc-id")
        assert len(chunks) >= 1
        assert chunks[0]["chunk_index"] == 0
        assert chunks[0]["token_count"] > 0
        assert chunks[0]["section_title"] is not None

    def test_long_document_produces_multiple_chunks(self):
        """A document with ~5000 words should produce multiple chunks."""
        # Generate a long document
        paragraph = "This is a sample legal clause that discusses the terms and conditions of the agreement between the parties involved. " * 50
        text = f"1. Introduction\n{paragraph}\n2. Terms\n{paragraph}\n3. Conditions\n{paragraph}"

        chunks = chunk_document(text, "test-doc-id")
        assert len(chunks) >= 5  # Should produce several chunks

        # Check chunk indices are sequential
        for i, chunk in enumerate(chunks):
            assert chunk["chunk_index"] == i

    def test_no_chunk_exceeds_900_tokens(self):
        """No chunk should exceed 900 tokens."""
        paragraph = "This is a sample legal clause. " * 200
        text = f"1. Section One\n{paragraph}\n2. Section Two\n{paragraph}"

        chunks = chunk_document(text, "test-doc-id")
        for chunk in chunks:
            assert chunk["token_count"] <= 900, f"Chunk {chunk['chunk_index']} has {chunk['token_count']} tokens"

    def test_section_titles_populated(self):
        """Chunks from sections with headings should have section_title set."""
        text = "1. Introduction\nSome intro text here.\n2. Definitions\nSome definitions here."
        chunks = chunk_document(text, "test-doc-id")
        for chunk in chunks:
            assert chunk["section_title"] is not None
            assert len(chunk["section_title"]) > 0


class TestCountTokens:
    def test_count_tokens(self):
        """Token count should be reasonable for known text."""
        text = "Hello world"
        count = _count_tokens(text)
        assert count == 2  # "Hello" and "world" are typically 2 tokens

    def test_empty_string(self):
        assert _count_tokens("") == 0
