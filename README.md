# FastAPI Template

A production-ready FastAPI starter template with a complete authentication system, async PostgreSQL, Celery task queue, admin panel, and observability stack — ready to clone and build upon.

## Features

- **Magic Link Authentication** — passwordless login via 6-digit email codes (no passwords stored)
- **Async PostgreSQL** — SQLAlchemy 2.0 with `asyncpg` driver and Alembic migrations
- **Celery + Redis** — background task queue with Beat scheduler and Flower monitoring UI
- **Admin Panel** — starlette-admin with role-based access at `/admin`
- **Rate Limiting** — per-endpoint limits via SlowAPI
- **Email Notifications** — async SMTP via `fastapi-mail` with Celery task dispatch
- **Observability** — Sentry error tracking, Grafana Loki log shipping, structured logging
- **CORS** — configurable allowed origins
- **CLI** — Typer-based admin management commands
- **Internationalization (i18n)** — Babel-based translations with `Accept-Language` header and `?lang=` query param support
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
| Email | fastapi-mail |
| Admin | starlette-admin |
| CLI | Typer |
| Validation | Pydantic v2 |
| i18n | Babel 2.18 |
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
│   │   ├── i18n.py         # Babel i18n: load_translations(), _() function
│   │   ├── limiter.py      # SlowAPI limiter (Redis-backed, proxy-aware)
│   │   ├── logger_setup.py # Async queue logging + Grafana Loki handler
│   │   ├── middleware.py   # LanguageMiddleware (Accept-Language / ?lang=)
│   │   ├── admin/          # starlette-admin setup and auth provider
│   │   └── models/         # SQLAlchemy base model, mixins, custom types
│   ├── modules/
│   │   ├── users/          # Auth module (magic link flow, user CRUD)
│   │   │   ├── api/v1/     # REST endpoints: auth + users
│   │   │   ├── models/     # User, AccessToken, LoginCode, LoginAttempt
│   │   │   ├── repositories/
│   │   │   ├── services/   # AuthMagicLinkService
│   │   │   ├── dtos/       # Internal data transfer objects
│   │   │   ├── schemas/    # API request/response schemas
│   │   │   ├── exceptions.py
│   │   │   ├── manager.py  # UserManager (fastapi-users)
│   │   │   └── auth_backend.py
│   │   └── notifications/  # Email service with Celery task dispatch
│   ├── common/             # Shared utilities
│   └── cli/                # Typer CLI (admin user management)
├── tests/
│   ├── unit/               # Pure unit tests (mocked dependencies)
│   └── integration/        # Full-stack tests against real PostgreSQL
├── alembic/                # DB migration scripts
├── babel.cfg               # Babel extraction config
├── docker-compose.yml
└── pyproject.toml
```

## Authentication Flow

This template uses a **magic link / OTP** flow instead of passwords:

1. `POST /api/v1/auth/magic/login` — user submits their email; a 6-digit code is sent via email. **If the email does not exist, a new user is created automatically** (passwordless onboarding — no separate registration step).
2. `POST /api/v1/auth/magic/verify-login` — user submits email + code; receives a Bearer token
3. `POST /api/v1/auth/magic/logout` — invalidates the current token (single session)
4. `POST /api/v1/auth/magic/logout-all` — invalidates all active tokens for the user (all devices)
5. `GET /api/v1/auth/sessions` — lists all active sessions with metadata: `created_at`, `expires_at`, `last_used_at`, `ip_address`
6. `DELETE /api/v1/auth/sessions/{token_id}` — revokes a specific session by ID; user can only revoke their own sessions (IDOR-safe)
7. `GET /api/v1/auth/login-history` — cursor-based paginated login attempt history (`limit`, `cursor`); returns `{ items, next_cursor }`; `code_entered` is never exposed

All protected endpoints expect `Authorization: Bearer <token>`.

## Getting Started

### Prerequisites

- Python 3.13
- PostgreSQL 16
- Redis 7
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### 1. Clone the repository

```bash
git clone https://github.com/ubihinon/fast-api-template.git
cd fast-api-template
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
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME=FastAPI Application

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

**Check module boundary violations:**

```bash
PYTHONPATH=src .venv/bin/lint-imports
```

## Internationalization (i18n)

The API supports multiple languages via Babel. The language is detected automatically from the `Accept-Language` request header or the `?lang=` query parameter.

**Supported languages:** `en` (default), `ru`

**Translation files:** `src/locales/<lang>/LC_MESSAGES/messages.po`

### Workflow for adding new translatable strings

**In Python code** — wrap the string in `_()`:
```python
from core.i18n import _
raise SomeException(_("Your message here"))
```

**In HTML email templates** — use `{{ _("...") }}` directly in Jinja2 templates. Keep HTML structure outside of translated strings:
```html
<!-- correct: HTML outside, plain text inside _() -->
{{ _("This code is valid for") }} <strong>{{ code_expires_in }}</strong>.

<!-- wrong: HTML inside _() breaks autoescape and makes translation harder -->
{% trans %}This code is valid for <strong>{{ code_expires_in }}</strong>.{% endtrans %}
```

Templates are rendered by `src/modules/notifications/template_renderer.py`, which sets up a Jinja2 `Environment` with Babel translations installed and caches it per language.

After adding or changing strings, extract, update, translate, and compile:
```bash
.venv/bin/pybabel extract --no-location -F babel.cfg -o src/locales/messages.pot src/
.venv/bin/pybabel update -i src/locales/messages.pot -d src/locales
# Edit src/locales/ru/LC_MESSAGES/messages.po
.venv/bin/pybabel compile -d src/locales
```

### Adding a new language

```bash
.venv/bin/pybabel init -i src/locales/messages.pot -d src/locales -l <lang_code>
.venv/bin/pybabel compile -d src/locales
```

Then add the language code to `SUPPORTED_LANGUAGES` in `src/core/i18n.py`.

## Adding a New Module

1. Create `src/modules/<your_module>/` with the standard layout: `models/`, `repositories/`, `services/`, `api/v1/`, `schemas/`
2. Define your SQLAlchemy models inheriting from `src/core/models/base.py`
3. Generate a migration: `alembic revision --autogenerate -m "add <your_module> tables"`
4. Apply it: `alembic upgrade head`
5. Register your router in `src/core/main.py`

## Environment Variables Reference

### Core

| Variable | Default | Required | Description |
|---|---|---|---|
| `APP_NAME` | `FastAPI Template` | No | Application name shown in OpenAPI docs |
| `APP_VERSION` | `1.0.0` | No | Application version shown in OpenAPI docs |
| `DATABASE_URL` | — | Yes | Async DB connection string (`asyncpg`) |
| `SYNC_DATABASE_URL` | — | Yes | Sync DB connection string (`psycopg2`, used by Alembic and admin) |
| `SECRET_KEY` | — | Yes | Session secret for admin panel (min 32 chars) |
| `HOST` | `0.0.0.0` | No | Bind host |
| `PORT` | `8000` | No | Bind port |
| `ENVIRONMENT` | `development` | No | Environment name (e.g. `production`) |
| `DEBUG` | `False` | No | Enable debug mode |
| `LOG_LEVEL` | `error` | No | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `ENABLE_ADMIN` | `True` | No | Mount starlette-admin at `/admin` |
| `ADMIN_PASSWORD_MIN_LENGTH` | `8` | No | Minimum admin password length |
| `CORS_ORIGINS` | `[]` | No | Allowed CORS origins as a JSON list |
| `CORS_ALLOW_CREDENTIALS` | `True` | No | Allow cookies/auth headers in CORS requests |
| `TRUST_PROXY_HEADERS` | `False` | No | Trust `X-Forwarded-For` (enable only behind a trusted reverse proxy) |

### Celery

| Variable | Default | Required | Description |
|---|---|---|---|
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | No | Celery broker URL |
| `CELERY_RESULT_BACKEND_URL` | `redis://localhost:6379/1` | No | Celery result backend URL |
| `CELERY_ALWAYS_EAGER` | `False` | No | Run tasks synchronously (set `True` in tests) |

### Auth / Tokens

| Variable | Default | Required | Description |
|---|---|---|---|
| `RESET_PASSWORD_TOKEN_SECRET` | — | Yes | Secret for password reset tokens (min 32 chars) |
| `VERIFICATION_TOKEN_SECRET` | — | Yes | Secret for email verification tokens (min 32 chars) |
| `BEARER_TRANSPORT_TOKEN_URL` | `api/v1/auth/magic/login` | No | Token URL shown in OpenAPI docs |
| `ACCESS_TOKEN_LIFETIME_SECONDS` | `3600` | No | Access token TTL in seconds |
| `LOGIN_CODE_EXPIRES_IN_TIMEDELTA` | `0:15:00` | No | Magic link code TTL (timedelta string, e.g. `0:15:00`) |
| `MAX_LOGIN_ATTEMPTS` | `5` | No | Max failed code attempts before lockout |
| `RATE_LIMIT_LOGIN` | `10/minute` | No | Rate limit for the login endpoint |
| `RATE_LIMIT_VERIFY` | `10/minute` | No | Rate limit for the verify-login endpoint |
| `RATE_LIMIT_SESSIONS` | `30/minute` | No | Rate limit for the sessions list endpoint |

### Email (SMTP)

| Variable | Default | Required | Description |
|---|---|---|---|
| `MAIL_USERNAME` | — | No | SMTP username |
| `MAIL_PASSWORD` | — | No | SMTP password |
| `MAIL_FROM` | — | No | Sender email address |
| `MAIL_PORT` | `587` | No | SMTP port |
| `MAIL_SERVER` | `smtp.gmail.com` | No | SMTP server host |
| `MAIL_FROM_NAME` | `FastAPI Application` | No | Sender display name |
| `MAIL_STARTTLS` | `True` | No | Use STARTTLS |
| `MAIL_SSL_TLS` | `False` | No | Use SSL/TLS (mutually exclusive with STARTTLS) |
| `USE_CREDENTIALS` | `True` | No | Authenticate with SMTP server |
| `VALIDATE_CERTS` | `True` | No | Validate TLS certificates |
| `SUPPRESS_SEND` | `False` | No | Disable actual email sending (useful in tests) |

### Observability

| Variable | Default | Required | Description |
|---|---|---|---|
| `SENTRY_DSN` | — | No | Sentry DSN — Sentry is disabled when empty |
| `SENTRY_TRACES_SAMPLE_RATE` | `1.0` | No | Sentry performance traces sample rate (0.0–1.0) |
| `SENTRY_PROFILE_SESSION_SAMPLE_RATE` | `1.0` | No | Sentry profiling sample rate (0.0–1.0) |
| `GRAFANA_LOKI_URL` | — | No | Grafana Loki push endpoint — log shipping disabled when empty |
| `GRAFANA_API_USERNAME` | — | No | Grafana API username |
| `GRAFANA_API_PASSWORD` | — | No | Grafana API password |

## Contributing

Contributions are welcome. Please open an issue before submitting a large pull request to discuss what you would like to change.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes and ensure all tests pass: `pytest`
4. Run linting and type checks: `ruff check src/ && mypy src/ && PYTHONPATH=src lint-imports`
5. Open a pull request against `main`

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
