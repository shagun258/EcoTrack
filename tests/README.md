# Tests

Test suites live next to the code they test, which is the standard layout for
each ecosystem involved:

- **Backend tests:** `backend/tests/` (pytest) — run with `cd backend && pytest tests/ -v`
- **ML tests:** `ml/tests/` (pytest) — run with `python -m pytest ml/tests/ -v` from the repo root
- **Frontend:** `npm run build` in `frontend/` type-checks the whole app; add
  component/form tests under `frontend/__tests__/` and run with `npm test`
  (Vitest is already in `frontend/package.json`)

See `docs/testing.md` for what's covered and the exact commands.
