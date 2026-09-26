# Security

## Authentication & authorization

- Passwords hashed with bcrypt via `passlib` (`app/core/security.py`) —
  never stored or logged in plain text.
- JWT access tokens (short-lived, default 30 min) + refresh tokens (default 7
  days), signed with `JWT_SECRET` (HS256). The frontend transparently retries a
  request once with a refreshed token on a 401 (`lib/api.ts`).
- Role-based access control via FastAPI dependencies (`require_admin`,
  `require_collector`, `require_roles(...)` in `app/core/deps.py`) — checked on
  the server for every protected route, not just hidden in the UI.
- Object-level checks beyond role: e.g. a user can only view their own pickup
  request unless they're the assigned collector or an admin
  (`app/api/routes/pickups.py::get_pickup`).

## Input validation

- All request bodies validated by Pydantic schemas (`app/schemas/`) — invalid
  data never reaches business logic.
- File uploads: content-type allowlist, size cap (`MAX_UPLOAD_SIZE_MB`), and a
  server-generated UUID filename (`app/services/storage_service.py`) — the
  original filename is never trusted or used to build a path, which also rules
  out path traversal.

## CORS

`CORS_ORIGINS` in `.env` controls allowed origins; defaults to
`http://localhost:3000` for local dev. Tighten this to your real frontend
domain(s) in production — never use `"*"` once real user data is involved.

## Secrets

- `.env` is git-ignored; `.env.example` contains placeholders only.
- No API keys or secrets are hardcoded anywhere in the codebase.
- `JWT_SECRET` in `.env.example` is an obvious placeholder — generate a real
  one before any non-local deployment, e.g.: `python -c "import secrets; print(secrets.token_urlsafe(48))"`

## SQL injection

All database access goes through SQLAlchemy's ORM/query builder with bound
parameters — no raw string-interpolated SQL anywhere in the codebase.

## Error responses

A global exception handler (`app/main.py`) catches unhandled exceptions and
returns a generic `500` message — Python stack traces are logged server-side
only, never sent to the client.

## Rate limiting

Not implemented in this version (would need a dependency like `slowapi` bound
to `REDIS_URL`, which is already configured). This is the first thing to add
before any public deployment — see `docs/deployment.md`.

## Known gaps to close before production

- Stateless JWT logout: a logged-out access token remains technically valid
  until it expires. Add a Redis denylist of token `jti`s if you need true
  server-side revocation.
- No rate limiting yet (see above).
- No email verification on registration.
- No CSRF protection needed currently (Bearer-token API, not cookie-based
  sessions) — revisit if you switch to cookie auth.
