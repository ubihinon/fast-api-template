import datetime
import datetime
import uuid
from typing import Annotated, List

import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, func, Index, Integer, select, String, text, UUID
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates

import settings

# from sqlalchemy.sql.annotation import Annotated

engine = create_async_engine(settings.DATABASE_URL, echo=True)
sync_engine = create_engine(settings.SYNC_DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


app = FastAPI()

UUIDPK = Annotated[UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]
IntPK = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
CreatedAt = Annotated[
    datetime.datetime, mapped_column(server_default=text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"), nullable=False)
]
UpdatedAt = Annotated[
    datetime.datetime, mapped_column(
        server_default=text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"),
        onupdate=datetime.datetime.now(datetime.UTC),
        nullable=False
    )
]


class User(Base):
    __tablename__ = 'user'

    id: Mapped[IntPK]
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]

    __table_args__ = (
        Index('ix_user_email_lower', func.lower(email), unique=True),
    )

    @validates('email')
    def validate_email(self, key, value):
        return value.strip().lower() if value else value


Base.metadata.drop_all(sync_engine)
Base.metadata.create_all(sync_engine)


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    name: str
    is_active: bool

    class Config:
        from_attributes = True


class UserDAL:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, email, name) -> UserSchema:
        user = User(email=email, name=name)
        self.session.add(user)
        await self.session.commit()
        return UserSchema.from_orm(user)

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

    async def all(self) -> List[User]:
        query = select(User)
        result = await self.session.execute(query)
        users = result.all()

        print('users!!!!!!')
        print(users)
        return []


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.get('/hello/{name}')
async def say_hello(name: str):
    return {'message': f'Hello {name}'}


@app.post('/user/create')
async def create_user(email: str, name: str):
    return await UserDAL(session=AsyncSession(engine)).create(email, name)

@app.post('/user/{user_id}')
async def get_user_by_id(user_id: int):
    return await UserDAL(session=AsyncSession(engine)).get_by_id(user_id)

@app.post('/user/1/{email}')
async def get_user_by_email(email: str):
    return await UserDAL(session=AsyncSession(engine)).get_by_email(email)


@app.post('/user/all')
async def get_all_users():
    return await UserDAL(session=AsyncSession(engine)).all()
