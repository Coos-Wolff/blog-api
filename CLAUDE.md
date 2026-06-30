# Blog REST API

Flask JSON REST API for a blog (migrated from a server-rendered/WTForms build — there is **no** HTML/templates/forms; every response is JSON). Python on Windows, SQLAlchemy 2.x, SQLite.

## Commands
- Run: `python run.py` (serves on port 5003, debug on)
- Manual API tests live in `http/blog.http` (JetBrains HTTP client)

## Architecture
Layered: **controller (routes) → service → repository**. Keep the layers strict.
- **Controllers** (`routes.py`) translate HTTP only: parse the request, validate request *shape* (missing/empty fields → 400), call a service, map results and exceptions to status codes. No business logic, no DB access.
- **Services** (`service.py`) own business logic and rules. They take/return plain data, never `Flask`/`jsonify`/status codes. Entities are serialized to dicts here (`.to_dict()`) before returning to the controller.
- **Repositories** (`repository.py`) own all DB access. Each write wraps `commit()` in try/except with `db.session.rollback()` then re-raises.
- App uses the **application factory** pattern (`create_app` in `__init__.py`).
- Extensions (`db`, `jwt`, `Base`) live in `extensions.py` and import only from libraries — nothing from this package. Models and the factory import from `extensions`. This keeps imports one-directional and avoids circular-import cycles. Do NOT move `db`/`Base` back into `models.py`.
- `models.py` imports `db` from `extensions`; there must be exactly ONE `SQLAlchemy` instance.
- The factory imports the model classes so `db.create_all()` sees them — those imports are load-bearing, not dead. Do not remove them.

## Conventions
- **Validation split**: request-shape validation in the controller (→ HTTP 4xx); business-rule validation in the service (→ raise an exception). Don't return status codes from services.
- **Errors**: domain rules raise custom exceptions (e.g. `EmailAlreadyExistsError`); generic bad input raises `ValueError`. Controllers catch and map to status codes (e.g. email-taken → 409).
- **Serialization**: `User.to_dict()` is a **whitelist** (`id`, `email`, `name` only) — the password hash must never appear in any response. Prefer whitelist `to_dict()` over dumping `__table__.columns` for anything with sensitive fields.
- **Passwords**: hash with Werkzeug `generate_password_hash`, verify with `check_password_hash`. Never store or return plaintext. The `password` column stores the hash (`Text`).
- **Auth**: JWT via `flask-jwt-extended` (stateless; `Authorization: Bearer <token>`), NOT Flask-Login sessions. Access tokens now; refresh tokens are a planned later addition.
- **Secrets**: `SECRET_KEY` and `JWT_SECRET_KEY` come from env via `os.environ.get`, loaded from `.env` (gitignored). Never hardcode; `.env.example` holds placeholders only.

## Git workflow
`main` is protected and requires a PR. Work on a branch → commit → push → PR → merge. `.gitattributes` enforces LF normalization.

## Known tech debt
- `BlogPost.date` is a `String`, not a `Date` — loses DB-level sort/range correctness; refactor target.
- `BlogPost.to_dict()` still uses the blacklist-style `__table__.columns` dump (fine for now — no sensitive fields, but don't copy the pattern to models that have them).
- `db.create_all()` in the factory should eventually become Alembic/Flask-Migrate migrations.
