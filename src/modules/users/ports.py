import datetime
from typing import Protocol


class UserNotificationPort(Protocol):
    def send_login_code_email_task(
        self, email: str, login_code: str, expires_in: datetime.timedelta
    ) -> list: ...

    def send_welcome_email_task(self, email: str) -> list: ...
