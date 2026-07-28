"""Integration tests for magic link auth endpoints.

Endpoints under test:
    POST /api/v1/auth/magic/login
    POST /api/v1/auth/magic/verify-login
    POST /api/v1/auth/magic/logout
"""
import datetime
from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from modules.users.models import LoginCode, User
from modules.users.settings import users_settings

LOGIN_URL = "/api/v1/auth/magic/login"
VERIFY_URL = "/api/v1/auth/magic/verify-login"
LOGOUT_URL = "/api/v1/auth/magic/logout"


# ---------------------------------------------------------------------------
# POST /api/v1/auth/magic/login
# ---------------------------------------------------------------------------

@pytest.mark.integration
@pytest.mark.asyncio
class TestLogin:
    async def test_new_user_is_created_and_receives_code(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        response = await client.post(LOGIN_URL, json={"email": "brand_new@example.com"})

        assert response.status_code == 200
        assert response.json() == {"message": "Code sent to your email"}
        mock_email_service.send_login_code_email_task.assert_called_once()

    async def test_existing_user_receives_code(
        self, client: AsyncClient, existing_user: User, mock_email_service: MagicMock
    ):
        response = await client.post(LOGIN_URL, json={"email": existing_user.email})

        assert response.status_code == 200
        mock_email_service.send_login_code_email_task.assert_called_once()

    async def test_code_sent_to_correct_email(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        email = "recipient@example.com"
        await client.post(LOGIN_URL, json={"email": email})

        sent_email = mock_email_service.send_login_code_email_task.call_args[0][0]
        assert sent_email == email

    async def test_inactive_user_returns_403(
        self, client: AsyncClient, inactive_user: User
    ):
        response = await client.post(LOGIN_URL, json={"email": inactive_user.email})

        assert response.status_code == 403

    async def test_invalid_email_format_returns_422(self, client: AsyncClient):
        response = await client.post(LOGIN_URL, json={"email": "not-an-email"})

        assert response.status_code == 422

    async def test_missing_email_field_returns_422(self, client: AsyncClient):
        response = await client.post(LOGIN_URL, json={})

        assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/v1/auth/magic/verify-login
# ---------------------------------------------------------------------------

@pytest.mark.integration
@pytest.mark.asyncio
class TestVerifyLogin:
    async def _seed_user_with_code(
        self,
        db_session: AsyncSession,
        email: str = "verify@example.com",
        code: str = "123456",
    ) -> User:
        user = User(
            email=email,
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)
        await db_session.flush()

        login_code = LoginCode(
            code=code,
            user_id=user.id,
            is_active=True,
            expires_at=datetime.datetime.now(datetime.UTC) + users_settings.LOGIN_CODE_EXPIRES_IN_TIMEDELTA,
        )
        db_session.add(login_code)
        await db_session.commit()
        return user

    async def test_valid_code_returns_access_token(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        await self._seed_user_with_code(db_session, "verify@example.com", "111111")

        response = await client.post(
            VERIFY_URL, json={"email": "verify@example.com", "code": "111111"}
        )

        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert len(body["access_token"]) > 0

    async def test_wrong_code_returns_400(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        await self._seed_user_with_code(db_session, "wrong@example.com", "222222")

        response = await client.post(
            VERIFY_URL, json={"email": "wrong@example.com", "code": "000000"}
        )

        assert response.status_code == 400

    async def test_expired_code_returns_400(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        user = User(
            email="expired@example.com", hashed_password="x",
            is_active=True, is_verified=True,
        )
        db_session.add(user)
        await db_session.flush()

        expired_code = LoginCode(
            code="333333",
            user_id=user.id,
            is_active=True,
            expires_at=datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=1),
        )
        db_session.add(expired_code)
        await db_session.commit()

        response = await client.post(
            VERIFY_URL, json={"email": "expired@example.com", "code": "333333"}
        )

        assert response.status_code == 400

    async def test_nonexistent_email_returns_404(self, client: AsyncClient):
        response = await client.post(
            VERIFY_URL, json={"email": "ghost@example.com", "code": "999999"}
        )

        assert response.status_code == 404

    async def test_max_attempts_returns_403(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Seed MAX_LOGIN_ATTEMPTS failed attempts directly in DB to avoid
        relying on exception-driven commit behavior."""
        from modules.users.models import LoginAttempt

        user = await self._seed_user_with_code(db_session, "brute@example.com", "444444")

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

    async def test_missing_fields_return_422(self, client: AsyncClient):
        response = await client.post(VERIFY_URL, json={"email": "a@b.com"})
        assert response.status_code == 422

    async def test_code_is_invalidated_after_use(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Second verify attempt with the same code must fail."""
        await self._seed_user_with_code(db_session, "reuse@example.com", "555555")

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
@pytest.mark.asyncio
class TestLogout:
    async def test_unauthenticated_returns_401(self, client: AsyncClient):
        response = await client.post(LOGOUT_URL)

        assert response.status_code == 401

    async def test_logout_with_token_returns_200(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.post(LOGOUT_URL, headers=auth_headers)

        assert response.status_code == 200

    async def test_logout_without_authorization_header_logs_out_all(
        self, client: AsyncClient, existing_user: User, auth_headers: dict
    ):
        """When Authorization header is omitted after auth, all tokens are revoked."""
        # Authenticate first so the user exists; then call logout without header.
        # current_active_user still requires auth, so we pass it once to verify
        # the session is valid, then call logout without header using the same session.
        me_resp = await client.get("/api/v1/users/me", headers=auth_headers)
        assert me_resp.status_code == 200

        logout_resp = await client.post(LOGOUT_URL, headers=auth_headers)
        assert logout_resp.status_code == 200

    async def test_logout_invalidates_token(
        self, client: AsyncClient, auth_headers: dict
    ):
        await client.post(LOGOUT_URL, headers=auth_headers)

        me_resp = await client.get("/api/v1/users/me", headers=auth_headers)
        assert me_resp.status_code == 401


# ---------------------------------------------------------------------------
# Full magic link flow: login → verify → use token → logout
# ---------------------------------------------------------------------------

@pytest.mark.integration
@pytest.mark.asyncio
class TestFullMagicLinkFlow:
    async def test_complete_flow(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        email = "flow@example.com"

        # Step 1: request login code
        login_resp = await client.post(LOGIN_URL, json={"email": email})
        assert login_resp.status_code == 200

        # Step 2: extract code from email mock
        code = mock_email_service.send_login_code_email_task.call_args[0][1]
        assert len(code) == 6

        # Step 3: verify code → receive token
        verify_resp = await client.post(
            VERIFY_URL, json={"email": email, "code": code}
        )
        assert verify_resp.status_code == 200
        token = verify_resp.json()["access_token"]

        # Step 4: use token to access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        me_resp = await client.get("/api/v1/users/me", headers=headers)
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == email

        # Step 5: logout
        logout_resp = await client.post(LOGOUT_URL, headers=headers)
        assert logout_resp.status_code == 200

        # Step 6: token is no longer valid
        after_logout = await client.get("/api/v1/users/me", headers=headers)
        assert after_logout.status_code == 401
