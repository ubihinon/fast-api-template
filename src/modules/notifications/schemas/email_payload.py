from typing import Any

from pydantic import BaseModel, NameEmail


class EmailPayload(BaseModel):
    recipients: list[NameEmail | str]
    subject: str
    body: str | dict[str, Any] | None = None
    cc: list[NameEmail | str] | None = None
    bcc: list[NameEmail | str] | None = None
    reply_to: list[NameEmail | str] | None = None
    attachments: list[Any] | None = None
