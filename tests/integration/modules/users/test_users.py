"""Integration tests for /users/me endpoints (fastapi-users).

Endpoints under test:
    GET  /api/v1/users/me
    PATCH /api/v1/users/me
"""
import pytest
from httpx import AsyncClient

from modules.users.models import User

ME_URL = "/api/v1/users/me"


@pytest.mark.integration
class TestGetMe:
    async def test_authenticated_returns_user_data(
        self, client: AsyncClient, existing_user: User, auth_headers: dict
    ):
        response = await client.get(ME_URL, headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["id"] == existing_user.id
        assert body["email"] == existing_user.email
        assert body["is_active"] is True
        assert "created_at" in body
        assert "updated_at" in body

    async def test_unauthenticated_returns_401(self, client: AsyncClient):
        response = await client.get(ME_URL)

        assert response.status_code == 401

    async def test_invalid_token_returns_401(self, client: AsyncClient):
        response = await client.get(
            ME_URL, headers={"Authorization": "Bearer invalid-token-xyz"}
        )

        assert response.status_code == 401


@pytest.mark.integration
class TestPatchMe:
    async def test_unauthenticated_returns_401(self, client: AsyncClient):
        response = await client.patch(ME_URL, json={})

        assert response.status_code == 401

    async def test_update_password_returns_200(
        self, client: AsyncClient, existing_user: User, auth_headers: dict
    ):
        response = await client.patch(
            ME_URL,
            json={"password": "new_secure_password_123"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["email"] == existing_user.email

    async def test_empty_patch_returns_200(
        self, client: AsyncClient, auth_headers: dict
    ):
        """PATCH with no fields should be a no-op and return current user."""
        response = await client.patch(ME_URL, json={}, headers=auth_headers)

        assert response.status_code == 200
