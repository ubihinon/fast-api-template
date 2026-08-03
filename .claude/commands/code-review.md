You are a code review sub-agent for this FastAPI project. Run all checks below sequentially, collect results, then fix all issues found.

## Step 1: Ruff (linting + formatting)

Run:
```
.venv/bin/ruff check src/ 2>&1
.venv/bin/ruff check tests/ 2>&1
```

Auto-fix where possible:
```
.venv/bin/ruff check --fix src/
.venv/bin/ruff check --fix tests/
```

Then manually fix any remaining errors that ruff could not auto-fix.

## Step 2: Mypy (type checking)

Run:
```
.venv/bin/mypy src/ 2>&1
.venv/bin/mypy tests/ 2>&1
```

Fix all type errors. Re-run until mypy reports no issues.

## Step 3: Import linter (module boundary violations)

Run:
```
PYTHONPATH=src .venv/bin/lint-imports 2>&1
```

Report any contract violations. Module isolation rule: modules must NOT import from each other directly — cross-module wiring happens only in `core/`. Fix any violations found.

## Step 4: Summary report

After all fixes, output a structured report:

```
## Code Review Report

### Ruff
- Fixed: <list of fixed issues or "none">
- Remaining: <list or "none">

### Mypy
- Fixed: <list of fixed issues or "none">
- Remaining: <list or "none">

### Import Linter
- Violations: <list or "none">
- Fixed: <list or "none">

### Overall status: PASSED / FAILED
```

If any issues could not be fixed automatically, explain why and suggest manual steps.
