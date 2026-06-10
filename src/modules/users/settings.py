import datetime

ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA: datetime.timedelta = datetime.timedelta(hours=1)
LOGIN_CODE_EXPIRES_IN_TIMEDELTA: datetime.timedelta = datetime.timedelta(minutes=15)

MAX_LOGIN_ATTEMPTS = 5
