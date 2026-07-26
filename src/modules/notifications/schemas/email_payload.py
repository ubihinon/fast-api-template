from typing import Any

from pydantic import BaseModel, NameEmail


class EmailPayload(BaseModel):
    recipients: list[NameEmail]
    subject: str
    body: str | dict[str, Any] | None = None
    cc: list[NameEmail] | None = None
    bcc: list[NameEmail] | None = None
    reply_to: list[NameEmail] | None = None
    attachments: list[Any] | None = None
