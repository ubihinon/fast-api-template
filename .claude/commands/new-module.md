You are a sub-agent that scaffolds a new module in this FastAPI project. The project root is the current working directory. Python source root is `src/`.

## Input

The user will provide a module name (e.g. `products`, `orders`, `payments`). If no name is provided, ask for it before proceeding.

Extract the module name from the user's message. Use it in:
- snake_case for directories, files, variables (e.g. `products`)
- PascalCase for class names (e.g. `Products`, `ProductsService`, `ProductsRepository`)
- kebab-case for API URL prefix (e.g. `products`)

Use `MODULE_NAME` as placeholder below — replace it everywhere with the actual name.

---

## Architecture rules (MUST follow)

- Modules must NOT import from each other directly. Cross-module wiring happens only in `core/`.
- Every new module must be added to the import-linter independence contract in `pyproject.toml`.
- The router must be registered in `src/core/main.py`.
- All imports must be absolute from `src/` (e.g. `from modules.MODULE_NAME.models import ...`).
- Use `IdIntPkMixin` and `CreatedUpdatedMixin` from `core.models.mixins` for all models.
- Use `Base` from `core.models.base` for all models.
- Repositories extend `BaseRepository` from `modules.users.repositories.base` (note: BaseRepository lives in users module — copy the pattern, do NOT import from users).
- Services receive repository instances via `__init__` (dependency injection).
- Pydantic schemas use `from pydantic import BaseModel` and `model_config = {"from_attributes": True}` where needed.

---

## Files to create

### 1. `src/modules/MODULE_NAME/__init__.py`
Empty file.

### 2. `src/modules/MODULE_NAME/models/__init__.py`
```python
from .MODULE_NAME import MODULE_NAME_PascalCase

__all__ = ["MODULE_NAME_PascalCase"]
```

### 3. `src/modules/MODULE_NAME/models/MODULE_NAME.py`
SQLAlchemy model with `IdIntPkMixin`, `CreatedUpdatedMixin`, `Base`. Use `__tablename__` and `__table_args__` with `{"schema": "MODULE_NAME"}`. Add at least a `name: Mapped[str]` column as a placeholder.

Example:
```python
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base
from core.models.mixins import CreatedUpdatedMixin, IdIntPkMixin


class MODULE_NAME_PascalCase(IdIntPkMixin, CreatedUpdatedMixin, Base):
    __tablename__ = "MODULE_NAME"
    __table_args__ = {"schema": "MODULE_NAME"}

    name: Mapped[str] = mapped_column(nullable=False)
```

### 4. `src/modules/MODULE_NAME/repositories/__init__.py`
```python
from .MODULE_NAME import MODULE_NAME_PascalCaseRepository

__all__ = ["MODULE_NAME_PascalCaseRepository"]
```

### 5. `src/modules/MODULE_NAME/repositories/base.py`
```python
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
```

### 6. `src/modules/MODULE_NAME/repositories/MODULE_NAME.py`
Repository with basic CRUD: `create`, `get_by_id`, `get_all`, `delete`.

```python
from sqlalchemy import select

from modules.MODULE_NAME.models import MODULE_NAME_PascalCase
from modules.MODULE_NAME.repositories.base import BaseRepository


class MODULE_NAME_PascalCaseRepository(BaseRepository):
    async def create(self, name: str) -> MODULE_NAME_PascalCase:
        obj = MODULE_NAME_PascalCase(name=name)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def get_by_id(self, obj_id: int) -> MODULE_NAME_PascalCase | None:
        result = await self.session.execute(
            select(MODULE_NAME_PascalCase).where(MODULE_NAME_PascalCase.id == obj_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[MODULE_NAME_PascalCase]:
        result = await self.session.execute(select(MODULE_NAME_PascalCase))
        return list(result.scalars().all())

    async def delete(self, obj: MODULE_NAME_PascalCase) -> None:
        await self.session.delete(obj)
        await self.session.flush()
```

### 7. `src/modules/MODULE_NAME/services/__init__.py`
Empty file.

### 8. `src/modules/MODULE_NAME/services/MODULE_NAME_service.py`
Service class that receives the repository via `__init__`.

```python
from sqlalchemy.ext.asyncio import AsyncSession

from modules.MODULE_NAME.models import MODULE_NAME_PascalCase
from modules.MODULE_NAME.repositories import MODULE_NAME_PascalCaseRepository


class MODULE_NAME_PascalCaseService:
    def __init__(self, session: AsyncSession, repository: MODULE_NAME_PascalCaseRepository):
        self.session = session
        self.repository = repository

    async def create(self, name: str) -> MODULE_NAME_PascalCase:
        obj = await self.repository.create(name=name)
        await self.session.commit()
        return obj

    async def get_by_id(self, obj_id: int) -> MODULE_NAME_PascalCase | None:
        return await self.repository.get_by_id(obj_id)

    async def get_all(self) -> list[MODULE_NAME_PascalCase]:
        return await self.repository.get_all()

    async def delete(self, obj_id: int) -> bool:
        obj = await self.repository.get_by_id(obj_id)
        if not obj:
            return False
        await self.repository.delete(obj)
        await self.session.commit()
        return True
```

### 9. `src/modules/MODULE_NAME/schemas/__init__.py`
Empty file.

### 10. `src/modules/MODULE_NAME/schemas/requests.py`
```python
from pydantic import BaseModel


class Create_MODULE_NAME_PascalCaseRequest(BaseModel):
    name: str
```

### 11. `src/modules/MODULE_NAME/schemas/responses.py`
```python
import datetime

from pydantic import BaseModel


class MODULE_NAME_PascalCaseResponse(BaseModel):
    id: int
    name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
```

### 12. `src/modules/MODULE_NAME/exceptions.py`
```python
class MODULE_NAME_PascalCaseNotFoundException(Exception):
    def __init__(self, obj_id: int):
        super().__init__(f"MODULE_NAME_PascalCase with id={obj_id} not found")
```

### 13. `src/modules/MODULE_NAME/dependencies.py`
FastAPI dependency that provides the service:

```python
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from modules.MODULE_NAME.repositories import MODULE_NAME_PascalCaseRepository
from modules.MODULE_NAME.services.MODULE_NAME_service import MODULE_NAME_PascalCaseService


def get_MODULE_NAME_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MODULE_NAME_PascalCaseService:
    repository = MODULE_NAME_PascalCaseRepository(session)
    return MODULE_NAME_PascalCaseService(session=session, repository=repository)
```

### 14. `src/modules/MODULE_NAME/api/__init__.py`
Empty file.

### 15. `src/modules/MODULE_NAME/api/v1/__init__.py`
```python
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from .MODULE_NAME import router as MODULE_NAME_router

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/api/v1", dependencies=[Depends(http_bearer)])
router.include_router(MODULE_NAME_router)
```

### 16. `src/modules/MODULE_NAME/api/v1/MODULE_NAME.py`
REST endpoints: `GET /MODULE_NAME`, `POST /MODULE_NAME`, `GET /MODULE_NAME/{id}`, `DELETE /MODULE_NAME/{id}`.

```python
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from modules.MODULE_NAME.dependencies import get_MODULE_NAME_service
from modules.MODULE_NAME.exceptions import MODULE_NAME_PascalCaseNotFoundException
from modules.MODULE_NAME.schemas.requests import Create_MODULE_NAME_PascalCaseRequest
from modules.MODULE_NAME.schemas.responses import MODULE_NAME_PascalCaseResponse
from modules.MODULE_NAME.services.MODULE_NAME_service import MODULE_NAME_PascalCaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/MODULE_NAME", tags=["MODULE_NAME_PascalCase"])


@router.get("", response_model=list[MODULE_NAME_PascalCaseResponse])
async def get_all(
    service: Annotated[MODULE_NAME_PascalCaseService, Depends(get_MODULE_NAME_service)],
) -> list[MODULE_NAME_PascalCaseResponse]:
    items = await service.get_all()
    return [MODULE_NAME_PascalCaseResponse.model_validate(i) for i in items]


@router.post("", response_model=MODULE_NAME_PascalCaseResponse, status_code=status.HTTP_201_CREATED)
async def create(
    request_data: Create_MODULE_NAME_PascalCaseRequest,
    service: Annotated[MODULE_NAME_PascalCaseService, Depends(get_MODULE_NAME_service)],
) -> MODULE_NAME_PascalCaseResponse:
    obj = await service.create(name=request_data.name)
    return MODULE_NAME_PascalCaseResponse.model_validate(obj)


@router.get("/{obj_id}", response_model=MODULE_NAME_PascalCaseResponse)
async def get_by_id(
    obj_id: int,
    service: Annotated[MODULE_NAME_PascalCaseService, Depends(get_MODULE_NAME_service)],
) -> MODULE_NAME_PascalCaseResponse:
    obj = await service.get_by_id(obj_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return MODULE_NAME_PascalCaseResponse.model_validate(obj)


@router.delete("/{obj_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    obj_id: int,
    service: Annotated[MODULE_NAME_PascalCaseService, Depends(get_MODULE_NAME_service)],
) -> None:
    deleted = await service.delete(obj_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
```

---

## Files to modify

### `src/core/main.py`

Add the import after existing router imports:
```python
from modules.MODULE_NAME.api.v1 import router as MODULE_NAME_router
```

Add after `app.include_router(users_router)`:
```python
app.include_router(MODULE_NAME_router)
```

### `pyproject.toml`

In `[[tool.importlinter.contracts]]` section, add `modules.MODULE_NAME` to the `modules` list:
```toml
modules = [
    "modules.users",
    "modules.notifications",
    "modules.MODULE_NAME",
]
```

---

## After creating all files

1. Run `PYTHONPATH=src .venv/bin/lint-imports 2>&1` to verify no contract violations.
2. Report a summary of all created/modified files.
3. Remind the user to:
   - Run `alembic revision --autogenerate -m "add MODULE_NAME module"` to create a migration
   - Run `alembic upgrade head` to apply it
