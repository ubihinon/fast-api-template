from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, NameEmail


class EmailPayload(BaseModel):
    recipients: List[Union[NameEmail, str]]
    subject: str
    body: Optional[Union[str, Dict[str, Any]]] = None
    cc: Optional[List[Union[NameEmail, str]]] = None
    bcc: Optional[List[Union[NameEmail, str]]] = None
    reply_to: Optional[List[Union[NameEmail, str]]] = None
    attachments: Optional[List[Any]] = None
