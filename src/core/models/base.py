from sqlalchemy.orm import DeclarativeBase, registry

mapper_registry = registry()


class Base(DeclarativeBase):
    registry = mapper_registry
