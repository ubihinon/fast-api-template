from modules.users.dtos.user import UserRead
from modules.users.models import User
from modules.users.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    async def get(self, user_id: int) -> UserRead | None:
        user = await self.session.get(User, user_id)
        return UserRead.model_validate(user) if user else None

    async def get_by_email(self, email: str) -> UserRead | None:
        user_db = User.get_db(self.session)
        user = await user_db.get_by_email(email)
        return UserRead.model_validate(user) if user else None
