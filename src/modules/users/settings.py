import datetime

from core.settings import settings

ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA: datetime.timedelta = datetime.timedelta(
    seconds=settings.ACCESS_TOKEN_LIFETIME_SECONDS
)
LOGIN_CODE_EXPIRES_IN_TIMEDELTA: datetime.timedelta = datetime.timedelta(minutes=15)

MAX_LOGIN_ATTEMPTS = 5
