from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models import AccessToken


async def get_access_token_db(session: Annotated[AsyncSession, Depends(get_session)]):
    yield AccessToken.get_db(session)
