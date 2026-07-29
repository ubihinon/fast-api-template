"""Integration tests for magic link auth endpoints.

Endpoints under test:
    POST /api/v1/auth/magic/login
    POST /api/v1/auth/magic/verify-login
    POST /api/v1/auth/magic/logout
"""
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from modules.users.dtos.user import UserRead
from modules.users.models import User
from modules.users.schemas.responses import LoginAccessTokenResponseSchema, LoginResponse
from modules.users.settings import users_settings

LOGIN_URL = "/api/v1/auth/magic/login"
VERIFY_URL = "/api/v1/auth/magic/verify-login"
LOGOUT_URL = "/api/v1/auth/magic/logout"


# ---------------------------------------------------------------------------
# POST /api/v1/auth/magic/login
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestLogin:
    async def test_new_user_is_created_and_receives_code(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        response = await client.post(LOGIN_URL, json={"email": "brand_new@example.com"})

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
        body = LoginResponse.model_validate(response.json())
        assert body.message == "Code sent to your email"
        mock_email_service.send_login_code_email_task.assert_called_once()

    async def test_existing_user_receives_code(
        self, client: AsyncClient, existing_user: User, mock_email_service: MagicMock
    ):
        response = await client.post(LOGIN_URL, json={"email": existing_user.email})

        assert response.status_code == 200
        LoginResponse.model_validate(response.json())
        mock_email_service.send_login_code_email_task.assert_called_once()

    async def test_code_sent_to_correct_email(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        email = "recipient@example.com"
        await client.post(LOGIN_URL, json={"email": email})

        sent_email = mock_email_service.send_login_code_email_task.call_args.args[0]
        assert sent_email == email

    async def test_inactive_user_returns_403(
        self, client: AsyncClient, inactive_user: User
    ):
        response = await client.post(LOGIN_URL, json={"email": inactive_user.email})

        assert response.status_code == 403

    @pytest.mark.parametrize("payload", [
        {"email": "not-an-email"},
        {"email": "@no-user.com"},
        {"email": ""},
        {},
    ])
    async def test_invalid_payload_returns_422(self, client: AsyncClient, payload: dict):
        response = await client.post(LOGIN_URL, json=payload)

        assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/v1/auth/magic/verify-login
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestVerifyLogin:
    async def test_valid_code_returns_access_token(
        self, client: AsyncClient, seed_user_with_code
    ):
        await seed_user_with_code(email="verify@example.com", code="111111")

        response = await client.post(
            VERIFY_URL, json={"email": "verify@example.com", "code": "111111"}
        )

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
        body = LoginAccessTokenResponseSchema.model_validate(response.json())
        assert len(body.access_token) > 0

    async def test_wrong_code_returns_400(
        self, client: AsyncClient, seed_user_with_code
    ):
        await seed_user_with_code(email="wrong@example.com", code="222222")

        response = await client.post(
            VERIFY_URL, json={"email": "wrong@example.com", "code": "000000"}
        )

        assert response.status_code == 400
        assert response.json()["detail"]

    async def test_expired_code_returns_400(
        self, client: AsyncClient, seed_user_with_code
    ):
        await seed_user_with_code(email="expired@example.com", code="333333", expired=True)

        response = await client.post(
            VERIFY_URL, json={"email": "expired@example.com", "code": "333333"}
        )

        assert response.status_code == 400
        assert response.json()["detail"]

    async def test_nonexistent_email_returns_404(self, client: AsyncClient):
        response = await client.post(
            VERIFY_URL, json={"email": "ghost@example.com", "code": "999999"}
        )

        assert response.status_code == 404

    async def test_max_attempts_returns_403(
        self, client: AsyncClient, db_session: AsyncSession, seed_user_with_code
    ):
        """Seed MAX_LOGIN_ATTEMPTS failed attempts directly in DB to avoid
        relying on exception-driven commit behavior."""
        from modules.users.models import LoginAttempt

        user = await seed_user_with_code(email="brute@example.com", code="444444")

        for _ in range(users_settings.MAX_LOGIN_ATTEMPTS):
            db_session.add(LoginAttempt(
                user_id=user.id,
                email=user.email,
                code_entered="000000",
                is_correct=False,
                ip_address="127.0.0.1",
            ))
        await db_session.commit()

        response = await client.post(
            VERIFY_URL, json={"email": "brute@example.com", "code": "000000"}
        )

        assert response.status_code == 403

    @pytest.mark.parametrize("payload", [
        {"email": "a@b.com"},   # missing code
        {"code": "123456"},     # missing email
        {},
    ])
    async def test_missing_fields_return_422(self, client: AsyncClient, payload: dict):
        response = await client.post(VERIFY_URL, json=payload)
        assert response.status_code == 422

    async def test_code_is_invalidated_after_use(
        self, client: AsyncClient, seed_user_with_code
    ):
        """Second verify attempt with the same code must fail."""
        await seed_user_with_code(email="reuse@example.com", code="555555")

        await client.post(
            VERIFY_URL, json={"email": "reuse@example.com", "code": "555555"}
        )
        second = await client.post(
            VERIFY_URL, json={"email": "reuse@example.com", "code": "555555"}
        )

        assert second.status_code == 400


# ---------------------------------------------------------------------------
# POST /api/v1/auth/magic/logout
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestLogout:
    async def test_unauthenticated_returns_401(self, client: AsyncClient):
        response = await client.post(LOGOUT_URL)

        assert response.status_code == 401

    async def test_logout_with_token_returns_200(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.post(LOGOUT_URL, headers=auth_headers)

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
        LoginResponse.model_validate(response.json())

    async def test_logout_invalidates_token_and_blocks_subsequent_requests(
        self, client: AsyncClient, existing_user: User, auth_headers: dict
    ):
        """Logout with a token revokes it so subsequent requests with the same token return 401."""
        me_resp = await client.get("/api/v1/users/me", headers=auth_headers)
        assert me_resp.status_code == 200

        logout_resp = await client.post(LOGOUT_URL, headers=auth_headers)
        assert logout_resp.status_code == 200

        after_logout = await client.get("/api/v1/users/me", headers=auth_headers)
        assert after_logout.status_code == 401

    async def test_logout_without_authorization_header_returns_400(
        self, client: AsyncClient, existing_user: User
    ):
        """Missing Authorization header returns 400 (auth bypassed via override to reach endpoint logic)."""
        from core.main import app
        from modules.users.fastapi_users_config import current_active_user

        async def _return_user():
            return existing_user

        app.dependency_overrides[current_active_user] = _return_user
        try:
            response = await client.post(LOGOUT_URL)
        finally:
            app.dependency_overrides.pop(current_active_user, None)

        assert response.status_code == 400
        assert "Authorization" in response.json()["detail"]

    async def test_logout_with_invalid_authorization_format_returns_400(
        self, client: AsyncClient, existing_user: User
    ):
        """Authorization header with non-Bearer scheme returns 400."""
        from core.main import app
        from modules.users.fastapi_users_config import current_active_user

        async def _return_user():
            return existing_user

        app.dependency_overrides[current_active_user] = _return_user
        try:
            response = await client.post(
                LOGOUT_URL, headers={"Authorization": "Token some-token-value"}
            )
        finally:
            app.dependency_overrides.pop(current_active_user, None)

        assert response.status_code == 400
        assert "Invalid Authorization" in response.json()["detail"]

    async def test_logout_with_bearer_but_no_token_value_returns_400(
        self, client: AsyncClient, existing_user: User
    ):
        """Authorization: 'Bearer' without a token value returns 400."""
        from core.main import app
        from modules.users.fastapi_users_config import current_active_user

        async def _return_user():
            return existing_user

        app.dependency_overrides[current_active_user] = _return_user
        try:
            response = await client.post(
                LOGOUT_URL, headers={"Authorization": "Bearer"}
            )
        finally:
            app.dependency_overrides.pop(current_active_user, None)

        assert response.status_code == 400


# ---------------------------------------------------------------------------
# Full magic link flow: login → verify → use token → logout
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestFullMagicLinkFlow:
    async def test_complete_flow(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        email = "flow@example.com"

        # Step 1: request login code
        login_resp = await client.post(LOGIN_URL, json={"email": email})
        assert login_resp.status_code == 200

        # Step 2: extract code from email mock
        code = mock_email_service.send_login_code_email_task.call_args.args[1]
        assert len(code) == 6

        # Step 3: verify code → receive token
        verify_resp = await client.post(
            VERIFY_URL, json={"email": email, "code": code}
        )
        assert verify_resp.status_code == 200
        token_body = LoginAccessTokenResponseSchema.model_validate(verify_resp.json())

        # Step 4: use token to access protected endpoint
        headers = {"Authorization": f"Bearer {token_body.access_token}"}
        me_resp = await client.get("/api/v1/users/me", headers=headers)
        assert me_resp.status_code == 200
        me_body = UserRead.model_validate(me_resp.json())
        assert me_body.email == email

        # Step 5: logout
        logout_resp = await client.post(LOGOUT_URL, headers=headers)
        assert logout_resp.status_code == 200
        LoginResponse.model_validate(logout_resp.json())

        # Step 6: token is no longer valid
        after_logout = await client.get("/api/v1/users/me", headers=headers)
        assert after_logout.status_code == 401
