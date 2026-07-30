import datetime
import uuid
from typing import Annotated

from sqlalchemy import UUID, text
from sqlalchemy.orm import mapped_column

UUIDPK = Annotated[UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]
IntPK = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
CreatedAt = Annotated[
    datetime.datetime, mapped_column(server_default=text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"), nullable=False)
]
UpdatedAt = Annotated[
    datetime.datetime, mapped_column(
        server_default=text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')"),
        onupdate=datetime.datetime.now(datetime.UTC),
        nullable=False
    )
]

UserIdType = int
