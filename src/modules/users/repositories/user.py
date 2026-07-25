from modules.users.models import User
from modules.users.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    async def get(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        user_db = User.get_db(self.session)
        return await user_db.get_by_email(email)
