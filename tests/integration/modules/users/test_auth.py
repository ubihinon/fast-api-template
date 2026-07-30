"""Integration tests for magic link auth endpoints.

Endpoints under test:
    POST /api/v1/auth/magic/login
    POST /api/v1/auth/magic/verify-login
    POST /api/v1/auth/magic/logout
    POST /api/v1/auth/magic/logout-all
    GET  /api/v1/auth/sessions
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
LOGOUT_ALL_URL = "/api/v1/auth/magic/logout-all"
SESSIONS_URL = "/api/v1/auth/sessions"
REVOKE_SESSION_URL = "/api/v1/auth/sessions/{token_id}"
LOGIN_HISTORY_URL = "/api/v1/auth/login-history"


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

    async def test_logout_with_token_returns_204(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.post(LOGOUT_URL, headers=auth_headers)

        assert response.status_code == 204
        assert response.content == b""

    async def test_logout_invalidates_token_and_blocks_subsequent_requests(
        self, client: AsyncClient, existing_user: User, auth_headers: dict
    ):
        """Logout with a token revokes it so subsequent requests with the same token return 401."""
        me_resp = await client.get("/api/v1/users/me", headers=auth_headers)
        assert me_resp.status_code == 200

        logout_resp = await client.post(LOGOUT_URL, headers=auth_headers)
        assert logout_resp.status_code == 204

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
# GET /api/v1/auth/sessions
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetSessions:
    async def test_unauthenticated_returns_401(self, client: AsyncClient):
        response = await client.get(SESSIONS_URL)

        assert response.status_code == 401

    async def test_returns_active_sessions(self, client: AsyncClient, auth_headers: dict):
        response = await client.get(SESSIONS_URL, headers=auth_headers)

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
        sessions = response.json()
        assert isinstance(sessions, list)
        assert len(sessions) >= 1
        session = sessions[0]
        assert "id" in session
        assert "created_at" in session
        assert "expires_at" in session
        assert "last_used_at" in session
        assert "ip_address" in session
        assert "token" not in session

    async def test_invalidated_session_not_in_list(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        """After logout, the revoked session must not appear in the sessions list of another active session."""
        email = "sessions_revoke@example.com"

        # create two sessions
        await client.post(LOGIN_URL, json={"email": email})
        code1 = mock_email_service.send_login_code_email_task.call_args[0][1]
        token1 = (await client.post(VERIFY_URL, json={"email": email, "code": code1})).json()["access_token"]

        await client.post(LOGIN_URL, json={"email": email})
        code2 = mock_email_service.send_login_code_email_task.call_args[0][1]
        token2 = (await client.post(VERIFY_URL, json={"email": email, "code": code2})).json()["access_token"]

        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}

        assert len((await client.get(SESSIONS_URL, headers=headers2)).json()) == 2

        # logout session 1
        await client.post(LOGOUT_URL, headers=headers1)

        # session 1 is gone from the list; session 2 still active
        sessions = (await client.get(SESSIONS_URL, headers=headers2)).json()
        assert len(sessions) == 1

    async def test_logout_all_clears_all_sessions(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        """After logout-all, no sessions remain for any of the tokens."""
        email = "sessions_check@example.com"

        await client.post(LOGIN_URL, json={"email": email})
        code1 = mock_email_service.send_login_code_email_task.call_args[0][1]
        token1 = (await client.post(VERIFY_URL, json={"email": email, "code": code1})).json()["access_token"]

        await client.post(LOGIN_URL, json={"email": email})
        code2 = mock_email_service.send_login_code_email_task.call_args[0][1]
        token2 = (await client.post(VERIFY_URL, json={"email": email, "code": code2})).json()["access_token"]

        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}

        sessions = (await client.get(SESSIONS_URL, headers=headers1)).json()
        assert len(sessions) == 2

        await client.post(LOGOUT_ALL_URL, headers=headers1)

        assert (await client.get(SESSIONS_URL, headers=headers1)).status_code == 401
        assert (await client.get(SESSIONS_URL, headers=headers2)).status_code == 401


# ---------------------------------------------------------------------------
# POST /api/v1/auth/magic/logout-all
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestLogoutAll:
    async def test_unauthenticated_returns_401(self, client: AsyncClient):
        response = await client.post(LOGOUT_ALL_URL)

        assert response.status_code == 401

    async def test_logout_all_returns_204(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(LOGOUT_ALL_URL, headers=auth_headers)

        assert response.status_code == 204
        assert response.content == b""

    async def test_logout_all_invalidates_all_tokens(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        """Two sessions exist; logout-all revokes both."""
        email = "logout_all@example.com"

        # obtain two tokens via two separate verify flows
        await client.post(LOGIN_URL, json={"email": email})
        code1 = mock_email_service.send_login_code_email_task.call_args[0][1]
        verify1 = await client.post(VERIFY_URL, json={"email": email, "code": code1})
        token1 = verify1.json()["access_token"]

        await client.post(LOGIN_URL, json={"email": email})
        code2 = mock_email_service.send_login_code_email_task.call_args[0][1]
        verify2 = await client.post(VERIFY_URL, json={"email": email, "code": code2})
        token2 = verify2.json()["access_token"]

        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}

        # both tokens work before logout-all
        assert (await client.get("/api/v1/users/me", headers=headers1)).status_code == 200
        assert (await client.get("/api/v1/users/me", headers=headers2)).status_code == 200

        # logout-all using first token
        assert (await client.post(LOGOUT_ALL_URL, headers=headers1)).status_code == 204

        # both tokens are now invalid
        assert (await client.get("/api/v1/users/me", headers=headers1)).status_code == 401
        assert (await client.get("/api/v1/users/me", headers=headers2)).status_code == 401


# ---------------------------------------------------------------------------
# DELETE /api/v1/auth/sessions/{token_id}
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestRevokeSession:
    async def test_unauthenticated_returns_401(self, client: AsyncClient):
        response = await client.delete(REVOKE_SESSION_URL.format(token_id=1))

        assert response.status_code == 401

    async def test_revoke_own_session_returns_204(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        email = "revoke_own@example.com"
        await client.post(LOGIN_URL, json={"email": email})
        code = mock_email_service.send_login_code_email_task.call_args[0][1]
        token = (await client.post(VERIFY_URL, json={"email": email, "code": code})).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        sessions = (await client.get(SESSIONS_URL, headers=headers)).json()
        token_id = sessions[0]["id"]

        response = await client.delete(REVOKE_SESSION_URL.format(token_id=token_id), headers=headers)

        assert response.status_code == 204
        assert response.content == b""

    async def test_revoked_session_no_longer_authenticates(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        """After revoking a session it must not appear in the list and its token must be rejected."""
        email = "revoke_auth@example.com"

        await client.post(LOGIN_URL, json={"email": email})
        code1 = mock_email_service.send_login_code_email_task.call_args[0][1]
        token1 = (await client.post(VERIFY_URL, json={"email": email, "code": code1})).json()["access_token"]

        await client.post(LOGIN_URL, json={"email": email})
        code2 = mock_email_service.send_login_code_email_task.call_args[0][1]
        token2 = (await client.post(VERIFY_URL, json={"email": email, "code": code2})).json()["access_token"]

        headers1 = {"Authorization": f"Bearer {token1}"}
        headers2 = {"Authorization": f"Bearer {token2}"}

        sessions = (await client.get(SESSIONS_URL, headers=headers2)).json()
        assert len(sessions) == 2

        # revoke token1 using token1 itself
        sessions_via_1 = (await client.get(SESSIONS_URL, headers=headers1)).json()
        own_id = sessions_via_1[0]["id"]  # most recent = first (ordered by created_at desc)
        await client.delete(REVOKE_SESSION_URL.format(token_id=own_id), headers=headers1)

        # token1 is now invalid
        assert (await client.get("/api/v1/users/me", headers=headers1)).status_code == 401
        # token2 still works
        assert (await client.get("/api/v1/users/me", headers=headers2)).status_code == 200

    async def test_revoke_nonexistent_session_returns_404(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.delete(REVOKE_SESSION_URL.format(token_id=999999), headers=auth_headers)

        assert response.status_code == 404
        assert response.json()["detail"] == "Session not found"

    async def test_cannot_revoke_another_users_session(
        self, client: AsyncClient, mock_email_service: MagicMock, db_session
    ):
        """IDOR check: user A cannot revoke user B's session."""
        from modules.users.models import User

        # create user B with a session
        user_b = User(email="user_b_idor@example.com", hashed_password="x", is_active=True, is_verified=True)
        db_session.add(user_b)
        await db_session.commit()
        await db_session.refresh(user_b)

        await client.post(LOGIN_URL, json={"email": user_b.email})
        code_b = mock_email_service.send_login_code_email_task.call_args[0][1]
        token_b = (await client.post(VERIFY_URL, json={"email": user_b.email, "code": code_b})).json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}
        sessions_b = (await client.get(SESSIONS_URL, headers=headers_b)).json()
        session_b_id = sessions_b[0]["id"]

        # user A tries to revoke user B's session
        email_a = "user_a_idor@example.com"
        await client.post(LOGIN_URL, json={"email": email_a})
        code_a = mock_email_service.send_login_code_email_task.call_args[0][1]
        token_a = (await client.post(VERIFY_URL, json={"email": email_a, "code": code_a})).json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        response = await client.delete(REVOKE_SESSION_URL.format(token_id=session_b_id), headers=headers_a)

        assert response.status_code == 404  # not 403 — don't leak existence
        # user B's session is untouched
        assert (await client.get("/api/v1/users/me", headers=headers_b)).status_code == 200

    async def test_revoke_already_inactive_session_returns_404(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        """Revoking a session that is already inactive (or already revoked) returns 404."""
        email = "revoke_twice@example.com"
        await client.post(LOGIN_URL, json={"email": email})
        code = mock_email_service.send_login_code_email_task.call_args[0][1]
        token = (await client.post(VERIFY_URL, json={"email": email, "code": code})).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        sessions = (await client.get(SESSIONS_URL, headers=headers)).json()
        token_id = sessions[0]["id"]

        first = await client.delete(REVOKE_SESSION_URL.format(token_id=token_id), headers=headers)
        assert first.status_code == 204

        # second attempt — token is already invalid so we get 401, not 404
        second = await client.delete(REVOKE_SESSION_URL.format(token_id=token_id))
        assert second.status_code == 401


# ---------------------------------------------------------------------------
# GET /api/v1/auth/login-history
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGetLoginHistory:
    async def test_unauthenticated_returns_401(self, client: AsyncClient):
        response = await client.get(LOGIN_HISTORY_URL)

        assert response.status_code == 401

    async def test_empty_history_returns_empty_page(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get(LOGIN_HISTORY_URL, headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["items"] == []
        assert body["next_cursor"] is None

    async def test_successful_login_appears_in_history(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        email = "history_ok@example.com"
        await client.post(LOGIN_URL, json={"email": email})
        code = mock_email_service.send_login_code_email_task.call_args[0][1]
        token = (await client.post(VERIFY_URL, json={"email": email, "code": code})).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get(LOGIN_HISTORY_URL, headers=headers)

        assert response.status_code == 200
        items = response.json()["items"]
        assert len(items) >= 1
        entry = items[0]
        assert entry["is_correct"] is True
        assert "id" in entry
        assert "created_at" in entry
        assert "ip_address" in entry
        assert "user_agent" in entry
        assert "code_entered" not in entry
        assert "email" not in entry

    async def test_failed_attempt_appears_in_history(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        email = "history_fail@example.com"
        await client.post(LOGIN_URL, json={"email": email})
        await client.post(VERIFY_URL, json={"email": email, "code": "000000"})  # wrong code

        await client.post(LOGIN_URL, json={"email": email})
        code2 = mock_email_service.send_login_code_email_task.call_args[0][1]
        token = (await client.post(VERIFY_URL, json={"email": email, "code": code2})).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        items = (await client.get(LOGIN_HISTORY_URL, headers=headers)).json()["items"]
        assert any(not e["is_correct"] for e in items)

    async def test_history_ordered_newest_first(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        email = "history_order@example.com"

        await client.post(LOGIN_URL, json={"email": email})
        await client.post(VERIFY_URL, json={"email": email, "code": "000000"})  # fail

        await client.post(LOGIN_URL, json={"email": email})
        code2 = mock_email_service.send_login_code_email_task.call_args[0][1]
        token = (await client.post(VERIFY_URL, json={"email": email, "code": code2})).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        items = (await client.get(LOGIN_HISTORY_URL, headers=headers)).json()["items"]
        assert len(items) >= 2
        ids = [e["id"] for e in items]
        assert ids == sorted(ids, reverse=True)

    async def test_cursor_pagination(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        """Full cursor-based pagination walk: page 1 → next_cursor → page 2."""
        email = "history_cursor@example.com"

        # produce 3 attempts (2 fails + 1 success)
        await client.post(LOGIN_URL, json={"email": email})
        await client.post(VERIFY_URL, json={"email": email, "code": "000000"})
        await client.post(LOGIN_URL, json={"email": email})
        await client.post(VERIFY_URL, json={"email": email, "code": "000000"})
        await client.post(LOGIN_URL, json={"email": email})
        code = mock_email_service.send_login_code_email_task.call_args[0][1]
        token = (await client.post(VERIFY_URL, json={"email": email, "code": code})).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # page 1: limit=2
        page1 = (await client.get(LOGIN_HISTORY_URL, headers=headers, params={"limit": 2})).json()
        assert len(page1["items"]) == 2
        assert page1["next_cursor"] is not None

        # page 2: use next_cursor
        page2 = (await client.get(
            LOGIN_HISTORY_URL, headers=headers,
            params={"limit": 2, "cursor": page1["next_cursor"]}
        )).json()
        assert len(page2["items"]) >= 1

        # no overlap between pages
        ids_p1 = {e["id"] for e in page1["items"]}
        ids_p2 = {e["id"] for e in page2["items"]}
        assert ids_p1.isdisjoint(ids_p2)

        # last page has no next_cursor
        assert page2["next_cursor"] is None

    @pytest.mark.parametrize("params,expected_status", [
        ({"limit": 0}, 422),
        ({"limit": 201}, 422),
        ({"cursor": 0}, 422),
    ])
    async def test_invalid_params_return_422(
        self, client: AsyncClient, auth_headers: dict, params: dict, expected_status: int
    ):
        response = await client.get(LOGIN_HISTORY_URL, headers=auth_headers, params=params)

        assert response.status_code == expected_status

    async def test_user_sees_only_own_history(
        self, client: AsyncClient, mock_email_service: MagicMock
    ):
        """User A's history must not contain User B's attempts."""
        email_a = "history_isolation_a@example.com"
        email_b = "history_isolation_b@example.com"

        await client.post(LOGIN_URL, json={"email": email_a})
        code_a = mock_email_service.send_login_code_email_task.call_args[0][1]
        token_a = (await client.post(VERIFY_URL, json={"email": email_a, "code": code_a})).json()["access_token"]

        await client.post(LOGIN_URL, json={"email": email_b})
        code_b = mock_email_service.send_login_code_email_task.call_args[0][1]
        await client.post(VERIFY_URL, json={"email": email_b, "code": code_b})

        headers_a = {"Authorization": f"Bearer {token_a}"}
        items_a = (await client.get(LOGIN_HISTORY_URL, headers=headers_a)).json()["items"]

        # user A has exactly 1 attempt (their own successful login)
        assert len([e for e in items_a if e["is_correct"]]) == 1


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
        assert logout_resp.status_code == 204

        # Step 6: token is no longer valid
        after_logout = await client.get("/api/v1/users/me", headers=headers)
        assert after_logout.status_code == 401
