from environs import env
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

env.read_env()

DATABASE_URL = env('DATABASE_URL', default='postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/postgres')
SYNC_DATABASE_URL = env('SYNC_DATABASE_URL', default='postgresql+psycopg2://postgres:postgres@0.0.0.0:5432/postgres')


engine = create_async_engine(DATABASE_URL, echo=True)
sync_engine = create_engine(SYNC_DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
