from sqlalchemy.orm import DeclarativeBase

from db.session import sync_engine


class Base(DeclarativeBase):
    pass


# Base.metadata.drop_all(sync_engine)
Base.metadata.create_all(sync_engine)
