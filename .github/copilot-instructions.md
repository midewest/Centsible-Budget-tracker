## Centsible Budget Tracker — Copilot instructions

Purpose: Give AI coding agents the minimal, repository-specific knowledge to be immediately productive.

Quick repo context

- Top-level files: `PRD and Roadmap.md`, `prompt rules.md`
- App folder: `Centsible Budget tracker/` (contains `rules.md` with technical and business rules)

High-value conventions (do not change without confirming):

- Language: Python. Follow PEP 8 (4-space indent, 79-char soft limit).
- Database: SQLAlchemy ORM used for DB operations. Prefer ORM models + sessions; use transactions for writes.
- Security: Passwords must be hashed (Werkzeug PBKDF2); CSRF protection required for forms; validate/sanitize inputs.
- Testing: Unit tests expected for new functionality; the repo expects high coverage for critical paths (rules.md requests ~90%).

Developer workflows (assumptions noted):

- Set up virtualenv: `python -m venv .venv` and activate in PowerShell: `.\\.venv\\Scripts\\Activate.ps1`.
- Install deps (assumption: `requirements.txt` exists or will be created): `pip install -r requirements.txt`.
- Run tests (assumed test runner): `pytest -q` — write pytest-style unit tests under `tests/` or next to modules.
- Linting/formatting: follow PEP8. If tooling is added, prefer `flake8`/`ruff` and `black` for formatting.

Project-specific patterns and examples

- DB writes: always use transactions and session scope. Example pattern: begin session, add, commit inside try/except and rollback on error.
- Avoid N+1 queries: when loading relationships for reports or listing, use eager loading (e.g. `joinedload()` / `selectinload()` with SQLAlchemy).
- Password handling example (follow this exact approach):

  from werkzeug.security import generate_password_hash, check_password_hash

  # store

  pw_hash = generate_password_hash(password, method='pbkdf2:sha256')

  # verify

  check_password_hash(pw_hash, candidate_password)

- Reporting and exports: CSV/PDF export points are business-critical (see `Centsible Budget tracker/rules.md`). Keep export code isolated and test CSV formatting and encoding.

Integration points and expectations

- External services: none discovered in repo files. If integrating third-party APIs, add configuration to environment variables and document keys in a secrets-safe way.
- Migrations: no migration tooling was found; if adding models, include migrations (Alembic recommended) and include a migration script in PR.

What to look for in code reviews

- Tests for any behavioral change (happy path + at least one edge case).
- DB changes accompanied by migrations and index updates (per rules, index frequently queried fields).
- Security: no raw password storage, inputs sanitized, prepared statements for raw SQL.

Notes & assumptions

- I inferred test and tooling commands (pytest, virtualenv, requirements.txt) because the repository contains Python rules but no explicit CI or tooling files were found. Confirm preferred test runner and CI before adding automation.

Where to find authoritative guidance in this repo

- `prompt rules.md` — high-level AI/dev guidance and process expectations.
- `Centsible Budget tracker/rules.md` — concrete technical rules (DB, security, testing, business rules).

If you want, I can:

- Add a basic `requirements.txt`, `pytest` scaffolding, and a small CI workflow template.
- Create an `ALEMBIC` skeleton and one sample migration when new models are added.

If anything above is incorrect or you want additional examples (tests, sample model, migration), tell me which area and I will update the file.
