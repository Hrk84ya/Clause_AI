import io
import pytest
from unittest.mock import patch
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestUploadDocument:
    async def test_upload_valid_pdf(self, async_client: AsyncClient, auth_headers):
        headers = await auth_headers("uploader@example.com", "Password123")

        with patch("src.core.file_storage.magic.from_buffer", return_value="application/pdf"):
            with patch("src.core.file_storage.Path.mkdir"):
                with patch("src.core.file_storage.Path.write_bytes"):
                    response = await async_client.post(
                        "/api/v1/documents/upload",
                        files={"file": ("test.pdf", b"%PDF-1.4 test content", "application/pdf")},
                        headers=headers,
                    )
        assert response.status_code == 202
        data = response.json()
        assert "document_id" in data
        assert "job_id" in data
        assert data["status"] == "pending"

    async def test_upload_without_auth(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.pdf", b"content", "application/pdf")},
        )
        assert response.status_code == 401


class TestListDocuments:
    async def test_list_own_documents(self, async_client: AsyncClient, auth_headers):
        headers = await auth_headers("lister@example.com", "Password123")
        response = await async_client.get("/api/v1/documents", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data


class TestGetDocument:
    async def test_get_nonexistent_document(self, async_client: AsyncClient, auth_headers):
        headers = await auth_headers("getter@example.com", "Password123")
        response = await async_client.get(
            "/api/v1/documents/00000000-0000-0000-0000-000000000000",
            headers=headers,
        )
        assert response.status_code == 404


class TestDeleteDocument:
    async def test_delete_nonexistent_document(self, async_client: AsyncClient, auth_headers):
        headers = await auth_headers("deleter@example.com", "Password123")
        response = await async_client.delete(
            "/api/v1/documents/00000000-0000-0000-0000-000000000000",
            headers=headers,
        )
        assert response.status_code == 404
