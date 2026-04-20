import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.parser import extract_headings, extract_text


class TestExtractHeadings:
    def test_numbered_headings(self):
        text = "1. Introduction\nSome text here.\n2. Terms and Conditions\nMore text."
        headings = extract_headings(text)
        assert "1. Introduction" in headings
        assert "2. Terms and Conditions" in headings

    def test_all_caps_headings(self):
        text = "CONFIDENTIALITY AGREEMENT\nThis agreement is between...\nTERMS OF SERVICE\nThe following terms..."
        headings = extract_headings(text)
        assert "CONFIDENTIALITY AGREEMENT" in headings
        assert "TERMS OF SERVICE" in headings

    def test_section_prefixed_headings(self):
        text = "Section 1 Definitions\nThe following definitions apply.\nArticle 2 Obligations"
        headings = extract_headings(text)
        assert any("Section 1" in h for h in headings)
        assert any("Article 2" in h for h in headings)

    def test_empty_text(self):
        assert extract_headings("") == []

    def test_no_headings(self):
        text = "This is just a regular paragraph with no headings at all."
        headings = extract_headings(text)
        assert len(headings) == 0


class TestExtractText:
    def test_txt_extraction(self, tmp_path):
        """Extract text from a plain text file."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("This is a test document with some words.", encoding="utf-8")

        text, page_count, word_count = extract_text(str(txt_file), "text/plain")
        assert "test document" in text
        assert page_count == 1
        assert word_count == 8

    def test_txt_encoding_detection(self, tmp_path):
        """Extract text from a file with non-UTF-8 encoding."""
        txt_file = tmp_path / "test_latin.txt"
        txt_file.write_bytes("Héllo wörld café".encode("latin-1"))

        text, _, _ = extract_text(str(txt_file), "text/plain")
        assert len(text) > 0  # Should not crash

    def test_unsupported_mime_type(self, tmp_path):
        """Unsupported MIME type raises ValueError."""
        txt_file = tmp_path / "test.xyz"
        txt_file.write_text("content")

        with pytest.raises(ValueError, match="Unsupported MIME type"):
            extract_text(str(txt_file), "application/x-unknown")
