"""Unit tests for AuthMagicLinkService.logout."""
import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.users.settings import users_settings
from modules.users.exceptions import AccessTokenNotFound
from modules.users.models import AccessToken, User
from modules.users.repositories import AccessTokenRepository
from modules.users.services.auth_service import AuthMagicLinkService


async def _create_token(session: AsyncSession, user: User, token: str = "test-token-abc") -> AccessToken:
    repo = AccessTokenRepository(session)
    access_token = await repo.create(
        token=token,
        user_id=user.id,
        expires_at=datetime.datetime.now(datetime.UTC) + users_settings.ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA,
    )
    await session.commit()
    return access_token


@pytest.mark.unit
@pytest.mark.asyncio
class TestLogout:
    async def test_with_token_deactivates_it(
        self, auth_service: AuthMagicLinkService, test_session, user_factory
    ):
        user = await user_factory(test_session)
        await _create_token(test_session, user)

        await auth_service.logout(user.id, token="test-token-abc")

        row = (await test_session.execute(
            select(AccessToken).where(AccessToken.token == "test-token-abc")
        )).scalar_one()
        assert row.is_active is False

    async def test_without_token_deactivates_all(
        self, auth_service: AuthMagicLinkService, test_session, user_factory
    ):
        user = await user_factory(test_session)
        for i in range(3):
            await _create_token(test_session, user, token=f"token-{i}")

        await auth_service.logout(user.id)

        rows = (await test_session.execute(
            select(AccessToken).where(AccessToken.user_id == user.id)
        )).scalars().all()
        assert all(not t.is_active for t in rows)

    async def test_nonexistent_token_raises(
        self, auth_service: AuthMagicLinkService, test_session, user_factory
    ):
        user = await user_factory(test_session)

        with pytest.raises(AccessTokenNotFound):
            await auth_service.logout(user.id, token="does-not-exist")
