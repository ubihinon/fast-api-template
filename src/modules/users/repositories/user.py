import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.users.manager import UserManager
from modules.users.models import User
from modules.users.schemas.user import UserCreate, UserRead


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # async def create(self, email) -> UserRead:
    #     user_create = UserCreate(
    #         email=email,
    #         password=secrets.token_urlsafe(32),
    #         is_active=True,
    #         is_verified=True
    #     )
    #     user = await self.create_user_manager().create(user_create)
    #     self.session.add(user)
    #     await self.session.flush()
    #     return UserRead.model_validate(user)

    async def get(self, user_id: int) -> UserRead:
        user = await self.session.get(User, user_id)
        return UserRead.model_validate(user) if user else None

    async def get_by_email(self, email: str) -> UserRead:
        pass
        # user = await User.get_db(self.session).get_by_email(email)
        # return UserRead.model_validate(user) if user else None

    # async def all(self) -> List[UserSchema]:
    #     query = select(User)
    #     result = await self.session.execute(query)
    #     users = result.all()
    #
    #     return [UserSchema.model_validate(user) for user in users] if users else []

    def create_user_manager(self):
        user_db = User.get_db(self.session)
        return UserManager(user_db)
