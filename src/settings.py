from environs import env

env.read_env()

DATABASE_URL = env('DATABASE_URL', default='postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/postgres')
SYNC_DATABASE_URL = env('SYNC_DATABASE_URL', default='postgresql+psycopg2://postgres:postgres@0.0.0.0:5432/postgres')
