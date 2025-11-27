from sqlalchemy.ext.asyncio import AsyncSession

from repositories.user import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def register_user(self, email: str, name: str):
        user = await self.repository.create(email, name)
        return user

    async def get_user(self, email: str):
        user = await self.repository.get_by_email(email)
        return user

    async def get_user_by_id(self, user_id: int):
        user = await self.repository.get_by_id(user_id)
        return user

    async def get_users(self):
        users = await self.repository.all()
        return users
