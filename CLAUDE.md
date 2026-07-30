# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Run the API server:**
```bash
cd src && uvicorn core.main:app --reload --host 0.0.0.0 --port 8000
```

**Run tests:**
```bash
pytest
```

**Check module boundary violations:**
```bash
PYTHONPATH=src .venv/bin/lint-imports
```

**Run a single test file:**
```bash
pytest tests/unit/modules/users/test_login.py
```

**Run a single test:**
```bash
pytest tests/unit/modules/users/test_login.py::TestClassName::test_method_name
```

**Database migrations:**
```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
```

**Run Celery worker:**
```bash
cd src && celery -A core.celery_app worker --loglevel=info
```

**Run Celery Beat (periodic tasks):**
```bash
cd src && celery -A core.celery_app beat --loglevel=info
```

**CLI (admin management):**
```bash
cd src && python -m cli.main admin --help
```

**Internationalization (i18n):**
```bash
# Extract translatable strings from source code
.venv/bin/pybabel extract --no-location -F babel.cfg -o src/locales/messages.pot src/

# Update existing .po files with new strings
.venv/bin/pybabel update -i src/locales/messages.pot -d src/locales

# Compile .po → .mo (required after editing translations)
.venv/bin/pybabel compile -d src/locales
```

## Architecture

**`src/` is the Python root** — `pythonpath = src` is set in `pytest.ini`, so all imports are relative to `src/`. The app entry point is `src/core/main.py`.

### Core Layer (`src/core/`)
- `main.py` — FastAPI app factory; mounts the users router and optionally the admin panel
- `settings.py` — Single `Settings` class (pydantic-settings) loaded from `.env`. Override via `ENV_FILE` env var.
- `database.py` — SQLAlchemy async engine (`asyncpg`) + sync engine (`psycopg2`) + `get_session()` dependency
- `celery_app.py` — Celery instance with Redis broker/backend; auto-discovers tasks from `core.tasks`
- `celery_beat_schedule.py` — Periodic task schedule
- `i18n.py` — Babel-based i18n: `load_translations()`, `_()` translation function, `current_language` ContextVar
- `limiter.py` — SlowAPI `Limiter` instance; uses Redis (`CELERY_BROKER_URL`) as storage; respects `TRUST_PROXY_HEADERS` for real IP detection
- `logger_setup.py` — `setup_logging()`: configures async queue-based logging with console handler and optional Grafana Loki handler (`GrafanaLokiHandler` + `JsonFormatter`)
- `middleware.py` — `LanguageMiddleware`: detects language from `Accept-Language` header or `?lang=` query param
- `models/` — SQLAlchemy base model (`base.py`), mixins (`mixins.py`), custom types (`types.py`)
- `admin/` — starlette-admin panel (enabled via `ENABLE_ADMIN=True`); uses `DatabaseAuthProvider` for admin-only login

### Modules (`src/modules/`)
Modules follow a layered pattern: **router → service → repository → model**

**Module isolation rule:** modules must not import from each other directly. Cross-module wiring happens only in `core/` (composition root). Enforced by `import-linter` — run `PYTHONPATH=src .venv/bin/lint-imports` to verify. Contracts are defined in `[tool.importlinter]` in `pyproject.toml`.

- `users/` — Full auth module using `fastapi-users` as the user model/manager base, but with a **custom magic link flow** (not standard fastapi-users login). Auth flow: request code via email → verify 6-digit code → receive bearer token. **First login auto-creates the user** if the email does not exist yet (passwordless onboarding).
  - `models/` — SQLAlchemy models: `User`, `AccessToken`, `LoginCode`, `LoginAttempt`
  - `repositories/` — Async SQLAlchemy repository classes (one per model)
  - `services/auth_service.py` — `AuthMagicLinkService` orchestrates the full magic link login/logout flow
  - `dtos/` — Internal data transfer objects (`UserCreate`, `UserRead`, `UserUpdate`, `AccessTokenSchema`)
  - `schemas/` — Pydantic request/response schemas for the API layer
  - `exceptions.py` — Domain exceptions (`UserNotFoundException`, `LoginCodeInvalidException`, `LoginMaxNumberAttemptsException`, etc.)
  - `manager.py` — `UserManager` (fastapi-users `BaseUserManager` subclass)
  - `auth_backend.py` — fastapi-users `AuthenticationBackend` wired to the DB token strategy; `TouchingDatabaseStrategy` subclass lazily updates `last_used_at` on successful auth
  - `dependencies.py` — Module-level FastAPI dependencies
  - `api/dependencies.py` — Endpoint-level dependencies (e.g. `get_auth_magic_link_service`)
  - `api/v1/auth.py` — Auth endpoints: `POST /auth/magic/login`, `/auth/magic/verify-login`, `/auth/magic/logout`, `/auth/magic/logout-all`, `GET /auth/sessions`
  - `api/v1/users.py` — User management endpoints (`/me`, `/{id}` via fastapi-users router)
  - `fastapi_users_config.py` — `fastapi_users` instance and `current_active_user` dependency
  - `settings.py` — Module-level constants (token/code TTLs, max login attempts, rate limit strings)

- `notifications/` — Email notifications via `fastapi-mail`; email tasks dispatched as Celery tasks through `UsersEmailService`
  - `settings.py` — `EmailSettings` (SMTP config loaded from `.env`)
  - `template_renderer.py` — renders Jinja2 HTML templates with Babel i18n support; Jinja2 `Environment` is cached per language; HTML templates use `{{ _("...") }}` for translatable strings
  - `templates/users/` — HTML email templates (`login_code.html`, `welcome.html`); translatable strings use `{{ _("...") }}`, HTML structure stays outside translations

### CLI (`src/cli/`)
Typer-based CLI with an `admin` sub-command group for admin user management.

## Rules

- Do not delete the `.env` file.

### Key env vars
| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Async DB connection |
| `SYNC_DATABASE_URL` | `postgresql+psycopg2://...` | Sync DB (admin/alembic) |
| `SECRET_KEY` | — (required, min 32 chars) | Session secret for admin panel |
| `RESET_PASSWORD_TOKEN_SECRET` | — (required, min 32 chars) | fastapi-users token secret |
| `VERIFICATION_TOKEN_SECRET` | — (required, min 32 chars) | fastapi-users token secret |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Celery broker |
| `CELERY_RESULT_BACKEND_URL` | `redis://localhost:6379/1` | Celery results |
| `CELERY_ALWAYS_EAGER` | `False` | Set `True` in tests to run tasks synchronously |
| `ENABLE_ADMIN` | `True` | Mount starlette-admin at `/admin` |
| `TRUST_PROXY_HEADERS` | `False` | Trust `X-Forwarded-For` (only behind a trusted reverse proxy) |
| `GRAFANA_LOKI_URL` | `` | Log shipping to Grafana Loki (disabled when empty) |
| `SENTRY_DSN` | `` | Sentry error tracking (disabled when empty) |
