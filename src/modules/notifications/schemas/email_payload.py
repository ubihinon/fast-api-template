from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, EmailStr


class EmailPayload(BaseModel):
    # supports following formats "user@example.com" and "Name <user@example.com>"
    recipients: List[Union[EmailStr, str]]
    subject: str
    body: Optional[Union[str, Dict[str, Any]]] = None
    cc: Optional[List[Union[EmailStr, str]]] = None
    bcc: Optional[List[Union[EmailStr, str]]] = None
    reply_to: Optional[List[Union[EmailStr, str]]] = None
    attachments: Optional[List[Any]] = None
