# Testing

## Backend (pytest)

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

Tests run against an isolated SQLite file (`test_ecotrack.db`), created fresh
and torn down automatically by the `_create_tables` fixture in
`tests/conftest.py` — they never touch your development PostgreSQL database.

Coverage:
- `test_auth.py` — registration, login, duplicate email, wrong password, token
  validation
- `test_permissions.py` — role-based access control, ownership checks
- `test_waste_and_ml.py` — waste report submission, ML prediction shape, reward
  points awarded, bad file type rejected, standalone `/api/ml/classify`

Verified locally: **16/16 passing.**

## ML (pytest)

```bash
python -m pytest ml/tests/ -v
```

Runs without TensorFlow installed (demo-mode tests only need Pillow/NumPy).
Covers: demo prediction returns a valid category, determinism (same image →
same result), production mode raises a clear error when no trained model file
exists (rather than silently faking a result), and response shape.

Verified locally: **5/5 passing.**

## Frontend

```bash
cd frontend
npm install
npm run build   # type-checks + production build
```

The production build has been verified to compile with zero TypeScript errors
across all 17 routes. A `vitest` dev-dependency is included in `package.json`
for component/form-validation tests as the project grows; add spec files under
`frontend/__tests__/` and run `npm test`.

## Manual end-to-end check

1. `docker compose up` (or run backend + frontend separately, see
   `SETUP_GUIDE.md`)
2. `python -m app.seed` (from `backend/`) to create dev users
3. Log in as `asha@example.com` / `EcoTrack@123`
4. Report a waste item with a photo → confirm a category + confidence shows up
5. Schedule a pickup → log in as `collector@example.com` → accept and progress
   it through PICKED_UP → COMPLETED
6. Log in as `admin@example.com` → check `/admin` shows updated totals
