# FastAPI Template

A production-ready FastAPI starter template with a complete authentication system, async PostgreSQL, Celery task queue, admin panel, and observability stack — ready to clone and build upon.

## Features

- **Magic Link Authentication** — passwordless login via 6-digit email codes (no passwords stored)
- **Async PostgreSQL** — SQLAlchemy 2.0 with `asyncpg` driver and Alembic migrations
- **Celery + Redis** — background task queue with Beat scheduler and Flower monitoring UI
- **Admin Panel** — starlette-admin with role-based access at `/admin`
- **Rate Limiting** — per-endpoint limits via SlowAPI
- **Email Notifications** — async SMTP via `aiosmtplib` with Celery task dispatch
- **Observability** — Sentry error tracking, Grafana Loki log shipping, structured logging
- **CORS** — configurable allowed origins
- **CLI** — Typer-based admin management commands
- **Type-safe** — fully typed with mypy; linted with Ruff

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI 0.138+ |
| ORM | SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 16 |
| Migrations | Alembic |
| Auth | fastapi-users + custom magic link flow |
| Task queue | Celery 5 + Redis |
| Email | aiosmtplib |
| Admin | starlette-admin |
| CLI | Typer |
| Validation | Pydantic v2 |
| Linting | Ruff |
| Type checking | mypy |
| Testing | pytest + pytest-asyncio + httpx |
| Python | 3.13 |

## Project Structure

```
.
├── src/
│   ├── core/               # App factory, settings, DB, Celery, admin panel
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── settings.py     # Pydantic-settings config (loaded from .env)
│   │   ├── database.py     # Async + sync SQLAlchemy engines
│   │   ├── celery_app.py   # Celery instance
│   │   ├── admin/          # starlette-admin setup and auth provider
│   │   └── models/         # SQLAlchemy base model and mixins
│   ├── modules/
│   │   ├── users/          # Auth module (magic link flow, user CRUD)
│   │   │   ├── api/v1/     # REST endpoints: auth + users
│   │   │   ├── models/     # User, AccessToken, LoginCode, LoginAttempt
│   │   │   ├── repositories/
│   │   │   └── services/   # AuthMagicLinkService, UserService
│   │   └── notifications/  # Email service with Celery task dispatch
│   └── cli/                # Typer CLI (admin user management)
├── tests/
│   ├── unit/               # Pure unit tests (mocked dependencies)
│   └── integration/        # Full-stack tests against real PostgreSQL
├── alembic/                # DB migration scripts
├── docker-compose.yml
└── pyproject.toml
```

## Authentication Flow

This template uses a **magic link / OTP** flow instead of passwords:

1. `POST /api/v1/auth/magic/login` — user submits their email; a 6-digit code is sent via email
2. `POST /api/v1/auth/magic/verify-login` — user submits email + code; receives a Bearer token
3. `POST /api/v1/auth/magic/logout` — invalidates the current token

All protected endpoints expect `Authorization: Bearer <token>`.

## Getting Started

### Prerequisites

- Python 3.13
- PostgreSQL 16
- Redis 7
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### 1. Clone the repository

```bash
git clone https://github.com/your-org/fastapi-template.git
cd fastapi-template
```

### 2. Create a virtual environment and install dependencies

With `uv` (recommended):

```bash
uv venv --python 3.13
source .venv/bin/activate
uv sync
```

With `pip`:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. Configure environment variables

Copy the template env file and fill in the required values:

```bash
cp .env.template .env
```

Minimum required variables:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/postgres
SYNC_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/postgres

# Security — must be at least 32 characters
SECRET_KEY=your-secret-key-at-least-32-characters-long
RESET_PASSWORD_TOKEN_SECRET=your-reset-password-secret-32-chars
VERIFICATION_TOKEN_SECRET=your-verification-secret-32-characters

# Redis / Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND_URL=redis://localhost:6379/1

# Email (SMTP)
MAIL_USERNAME=your@email.com
MAIL_PASSWORD=your-smtp-password
MAIL_FROM=your@email.com

# Optional
ENABLE_ADMIN=True
SENTRY_DSN=
GRAFANA_LOKI_URL=
```

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. Start the API server

```bash
cd src && uvicorn core.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:

- API: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- Admin panel: `http://localhost:8000/admin` (if `ENABLE_ADMIN=True`)

## Docker

Start the full stack (PostgreSQL, Redis, FastAPI, Celery worker, Celery Beat, Flower):

```bash
docker-compose up -d
```

Services:

| Service | URL |
|---|---|
| FastAPI | http://localhost:8000 |
| Flower (Celery UI) | http://localhost:5555 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

## Running Celery

**Worker** (processes background tasks):

```bash
cd src && celery -A core.celery_app worker --loglevel=info
```

**Beat** (periodic task scheduler):

```bash
cd src && celery -A core.celery_app beat --loglevel=info
```

**Flower** (monitoring UI):

```bash
cd src && celery -A core.celery_app flower --port=5555
```

## CLI

Manage admin users via the built-in CLI:

```bash
cd src && python -m cli.main admin --help
```

## Running Tests

### Unit tests

Unit tests use mocked dependencies and require no running services:

```bash
pytest tests/unit
```

### Integration tests

Integration tests run against a real PostgreSQL instance. Make sure your database is running and `DATABASE_URL` in `.env` is correct, then:

```bash
pytest tests/integration
```

### All tests

```bash
pytest
```

### Single test file or test case

```bash
pytest tests/unit/modules/users/test_login.py
pytest tests/unit/modules/users/test_login.py::TestClassName::test_method_name
```

## Code Quality

**Lint:**

```bash
.venv/bin/ruff check src/
```

**Auto-fix:**

```bash
.venv/bin/ruff check src/ --fix
```

**Format:**

```bash
.venv/bin/ruff format src/
```

**Type check:**

```bash
.venv/bin/mypy src/
```

## Adding a New Module

1. Create `src/modules/<your_module>/` with the standard layout: `models/`, `repositories/`, `services/`, `api/v1/`, `schemas/`
2. Define your SQLAlchemy models inheriting from `src/core/models/base.py`
3. Generate a migration: `alembic revision --autogenerate -m "add <your_module> tables"`
4. Apply it: `alembic upgrade head`
5. Register your router in `src/core/main.py`

## Environment Variables Reference

| Variable | Default | Required | Description |
|---|---|---|---|
| `DATABASE_URL` | — | Yes | Async DB connection string (`asyncpg`) |
| `SYNC_DATABASE_URL` | — | Yes | Sync DB connection string (`psycopg2`) |
| `SECRET_KEY` | — | Yes | Session secret (min 32 chars) |
| `RESET_PASSWORD_TOKEN_SECRET` | — | Yes | Token secret (min 32 chars) |
| `VERIFICATION_TOKEN_SECRET` | — | Yes | Token secret (min 32 chars) |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | No | Celery broker |
| `CELERY_RESULT_BACKEND_URL` | `redis://localhost:6379/1` | No | Celery result backend |
| `CELERY_ALWAYS_EAGER` | `False` | No | Run tasks synchronously (useful in tests) |
| `ENABLE_ADMIN` | `True` | No | Mount admin panel at `/admin` |
| `ENVIRONMENT` | `development` | No | `development` / `production` |
| `DEBUG` | `False` | No | Enable debug mode |
| `LOG_LEVEL` | `error` | No | Logging level |
| `CORS_ORIGINS` | `[]` | No | Allowed CORS origins (JSON list) |
| `RATE_LIMIT_LOGIN` | `10/minute` | No | Rate limit for login endpoint |
| `RATE_LIMIT_VERIFY` | `10/minute` | No | Rate limit for verify endpoint |
| `SENTRY_DSN` | — | No | Sentry DSN for error tracking |
| `GRAFANA_LOKI_URL` | — | No | Grafana Loki endpoint for log shipping |
| `GRAFANA_API_USERNAME` | — | No | Grafana API username |
| `GRAFANA_API_PASSWORD` | — | No | Grafana API password |

## Contributing

Contributions are welcome. Please open an issue before submitting a large pull request to discuss what you would like to change.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and ensure all tests pass: `pytest`
4. Run linting and type checks: `ruff check src/ && mypy src/`
5. Open a pull request against `main`

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
