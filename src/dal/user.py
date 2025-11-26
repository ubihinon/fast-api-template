from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from schemas.user import UserSchema


class UserDAL:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, email, name) -> UserSchema:
        user = User(email=email, name=name)
        self.session.add(user)
        res = await self.session.commit()
        return UserSchema.model_validate(user)

    async def get_by_id(self, user_id: int) -> dict:
        user = await self.session.get(User, user_id)
        return UserSchema.model_validate(user).model_dump()

    async def get_by_email(self, email) -> dict:
        query = (
            select(User).where(User.email == email)
        )
        result = await self.session.execute(query)
        res = result.all()
        return UserSchema.model_validate(res).model_dump()

    async def all(self) -> List[UserSchema]:
        query = select(User)
        result = await self.session.execute(query)
        users = result.all()

        return [UserSchema.model_validate(user) for user in users]
