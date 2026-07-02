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
- **Serialization**: `to_dict()` methods are explicit **whitelists**, not `__table__.columns` dumps. `User.to_dict()` returns `id`, `email`, `name` only — the password hash must never appear in any response. `BlogPost.to_dict()` returns the post's own scalar fields plus a nested `author` object (`{id, name}` only — NOT email, and NOT the raw `author_id`), reached via the `author` relationship. Do NOT revert either to a generic column dump — it would break the author embed and/or leak fields.
- **Passwords**: hash with Werkzeug `generate_password_hash`, verify with `check_password_hash`. Never store or return plaintext. The `password` column stores the hash (`Text`).
- **Auth**: JWT via `flask-jwt-extended` (stateless; `Authorization: Bearer <token>`), NOT Flask-Login sessions. Access tokens now; refresh tokens are a planned later addition.
- **Route protection**: mutating routes are gated with `@jwt_required()` (stacked BELOW `@blog_bp.route(...)`, note the parens). GET routes stay public. Inside a protected route, identity comes from `get_jwt_identity()`.
- **Token identity is a STRING**: tokens are minted with `create_access_token(str(user.id))`, so `get_jwt_identity()` returns a str. Convert with `int(...)` before using it as `author_id` or any int FK. Stringify in, int out.
- **Authorship is never trusted from the body**: `BlogPost.author_id` is set from `int(get_jwt_identity())`, never from request JSON. `author` is a FK relationship to `User` (`author_id` column + `relationship(back_populates=...)` on both models). A client cannot forge authorship by sending `author_id`.
- **Login anti-enumeration**: failed logins return one identical vague 401 ("Invalid email or password") for both unknown-email and wrong-password. The service also runs a dummy `check_password_hash` against a module-level `DUMMY_HASH` when the user is missing, to equalize response timing. Do NOT "optimize" that dummy hash away — it closes a timing side-channel.
- **Secrets**: `SECRET_KEY` and `JWT_SECRET_KEY` come from env via `os.environ.get`, loaded from `.env` (gitignored). Never hardcode; `.env.example` holds placeholders only.

## Git workflow
`main` is protected and requires a PR. Work on a branch → commit → push → PR → merge. `.gitattributes` enforces LF normalization.
- **Branch protection**: GitHub branch protection on `main` requires a pull request before merging (0 approvals needed — solo repo) and `enforce_admins` is on, so even the repo owner cannot `git push` directly to `main`; a direct push is rejected and must go through a branch + PR instead.

## Known tech debt
- `BlogPost.date` is a `String`, not a `Date` — loses DB-level sort/range correctness; refactor target.
- `delete_post` and `patch_post` are NOT yet protected with `@jwt_required()` and have no ownership check — any caller can mutate any post. Adding auth + an author-ownership rule is the current work in progress.
- `add_post` calls `.to_dict()` in the controller rather than the service (the service owns serialization elsewhere) — a layering inconsistency to reconcile.
- `db.create_all()` in the factory should eventually become Alembic/Flask-Migrate migrations. Adding the author FK required deleting `instance/blog.db` for a clean rebuild, since `create_all()` does not alter existing tables.

## Working style
The human writes the code themselves and wants review, problem-identification, and concept explanation — not generated fixes unless explicitly asked.
