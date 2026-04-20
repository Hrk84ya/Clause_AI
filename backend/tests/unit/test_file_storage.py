import io

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

# Note: These tests mock the magic library and file system operations
# to avoid needing actual files


class TestValidateFile:
    @pytest.mark.asyncio
    async def test_valid_pdf(self):
        """Valid PDF file passes validation."""
        from src.core.file_storage import validate_file

        # Create a mock UploadFile with PDF magic bytes
        mock_file = MagicMock()
        pdf_content = b"%PDF-1.4" + b"\x00" * 1000

        read_count = 0

        async def mock_read(size=None):
            nonlocal read_count
            read_count += 1
            if size:
                return pdf_content[:size]
            return pdf_content

        async def mock_seek(pos):
            pass

        mock_file.read = mock_read
        mock_file.seek = mock_seek

        with patch("src.core.file_storage.magic.from_buffer", return_value="application/pdf"):
            mime = await validate_file(mock_file)
            assert mime == "application/pdf"

    @pytest.mark.asyncio
    async def test_invalid_mime_type(self):
        """Unsupported file type raises 415."""
        from src.core.file_storage import validate_file

        mock_file = MagicMock()
        content = b"fake executable content" * 100

        async def mock_read(size=None):
            if size:
                return content[:size]
            return content

        async def mock_seek(pos):
            pass

        mock_file.read = mock_read
        mock_file.seek = mock_seek

        with patch("src.core.file_storage.magic.from_buffer", return_value="application/x-executable"):
            with pytest.raises(HTTPException) as exc_info:
                await validate_file(mock_file)
            assert exc_info.value.status_code == 415

    @pytest.mark.asyncio
    async def test_oversized_file(self):
        """File over size limit raises 413."""
        from src.core.file_storage import validate_file

        mock_file = MagicMock()
        # Create content larger than 20MB
        content = b"x" * (21 * 1024 * 1024)

        async def mock_read(size=None):
            if size:
                return content[:size]
            return content

        async def mock_seek(pos):
            pass

        mock_file.read = mock_read
        mock_file.seek = mock_seek

        with patch("src.core.file_storage.magic.from_buffer", return_value="application/pdf"):
            with pytest.raises(HTTPException) as exc_info:
                await validate_file(mock_file)
            assert exc_info.value.status_code == 413


class TestDeleteDocumentFiles:
    def test_delete_existing_directory(self, tmp_path):
        """Delete removes the document directory."""
        from src.core.file_storage import delete_document_files

        # Create a fake document directory
        doc_dir = tmp_path / "user1" / "doc1"
        doc_dir.mkdir(parents=True)
        (doc_dir / "original.pdf").write_bytes(b"fake pdf")

        with patch("src.core.file_storage.settings") as mock_settings:
            mock_settings.upload_dir = str(tmp_path)
            delete_document_files("user1", "doc1")

        assert not doc_dir.exists()

    def test_delete_nonexistent_directory(self, tmp_path):
        """Delete on non-existent directory doesn't raise."""
        from src.core.file_storage import delete_document_files

        with patch("src.core.file_storage.settings") as mock_settings:
            mock_settings.upload_dir = str(tmp_path)
            # Should not raise
            delete_document_files("user1", "nonexistent")
