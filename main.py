import datetime
import datetime
import uuid
from typing import Annotated, List

import sqlalchemy
from fastapi import FastAPI
from sqlalchemy import create_engine, select, String, text, UUID
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

import settings

# from sqlalchemy.sql.annotation import Annotated

engine = create_async_engine(settings.DATABASE_URL, echo=True)
sync_engine = create_engine(settings.SYNC_DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


app = FastAPI()


UUIDPK = Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True)]
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

    id: Mapped[UUIDPK]
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[CreatedAt]
    updated_at: Mapped[UpdatedAt]


# Base.metadata.create_all(bind=sync_engine, tables=[User])
Base.metadata.create_all(sync_engine)
# sqlalchemy.create_all(engine)
class UserDAL:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, email, name) -> User:
        user = User(email=email, name=name)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get(self, email):
        result = await self.session.get(User, {'email': email})
        return result

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
