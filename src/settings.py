from environs import env

env.read_env()

DATABASE_URL = env('DATABASE_URL', default='postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/postgres')
SYNC_DATABASE_URL = env('SYNC_DATABASE_URL', default='postgresql+psycopg2://postgres:postgres@0.0.0.0:5432/postgres')


ACCESS_TOKEN_LIFETIME_SECONDS = 3600

RESET_PASSWORD_TOKEN_SECRET = env('RESET_PASSWORD_TOKEN_SECRET', default='<PASSWORD>')
VERIFICATION_TOKEN_SECRET = env('VERIFICATION_TOKEN_SECRET', default='<PASSWORD>')

BEARER_TRANSPORT_TOKEN_URL = 'api/v1/auth/login'
