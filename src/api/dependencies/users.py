from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models import User


async def get_user_db(session: Annotated[AsyncSession, Depends(get_session)]):
    yield User.get_db(session)
