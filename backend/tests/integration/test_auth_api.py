import pytest
from httpx import AsyncClient

# These tests require a running test database.
# They test the full auth flow end-to-end.

pytestmark = pytest.mark.asyncio


class TestRegister:
    async def test_register_success(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/auth/register",
            json={"email": "newuser@example.com", "password": "Password123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["email"] == "newuser@example.com"

    async def test_register_duplicate_email(
        self, async_client: AsyncClient, create_user
    ):
        await create_user("existing@example.com", "Password123")
        response = await async_client.post(
            "/api/v1/auth/register",
            json={"email": "existing@example.com", "password": "Password456"},
        )
        assert response.status_code == 409

    async def test_register_weak_password(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/auth/register",
            json={"email": "user@example.com", "password": "short"},
        )
        assert response.status_code == 422

    async def test_register_password_no_digit(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/auth/register",
            json={"email": "user@example.com", "password": "NoDigitsHere"},
        )
        assert response.status_code == 422


class TestLogin:
    async def test_login_success(self, async_client: AsyncClient, create_user):
        await create_user("login@example.com", "Password123")
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "login@example.com", "password": "Password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, async_client: AsyncClient, create_user):
        await create_user("login2@example.com", "Password123")
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "login2@example.com", "password": "WrongPass1"},
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "Password123"},
        )
        assert response.status_code == 401


class TestRefresh:
    async def test_refresh_success(self, async_client: AsyncClient, create_user):
        await create_user("refresh@example.com", "Password123")
        login_resp = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "refresh@example.com", "password": "Password123"},
        )
        refresh_token = login_resp.json()["refresh_token"]
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    async def test_refresh_invalid_token(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )
        assert response.status_code == 401


class TestLogout:
    async def test_logout_success(self, async_client: AsyncClient, create_user):
        await create_user("logout@example.com", "Password123")
        login_resp = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "logout@example.com", "password": "Password123"},
        )
        tokens = login_resp.json()
        response = await async_client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": tokens["refresh_token"]},
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert response.status_code == 200

        # Subsequent refresh should fail
        refresh_resp = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert refresh_resp.status_code == 401


class TestMe:
    async def test_me_authenticated(self, async_client: AsyncClient, auth_headers):
        headers = await auth_headers("me@example.com", "Password123")
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["email"] == "me@example.com"

    async def test_me_unauthenticated(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 401
