from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from schemas.user import UserSchema


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, email, name) -> UserSchema:
        user = User(email=email, name=name)
        self.session.add(user)
        await self.session.flush()
        return UserSchema.model_validate(user)

    async def get_by_id(self, user_id: int) -> UserSchema:
        user = await self.session.get(User, user_id)
        return UserSchema.model_validate(user) if user else {}

    async def get_by_email(self, email) -> UserSchema:
        query = (
            select(User).where(User.email == email)
        )
        result = await self.session.execute(query)
        user = result.all()
        return UserSchema.model_validate(user) if user else {}

    async def all(self) -> List[UserSchema]:
        query = select(User)
        result = await self.session.execute(query)
        users = result.all()

        return [UserSchema.model_validate(user) for user in users] if users else []
