# SETUP_GUIDE.md — Exact commands to get EcoTrack running

Written for a CSE student on **Windows using PowerShell**. Where a step
differs on macOS/Linux, that's noted too. Every command below says which
folder to run it from.

---

## Option 1: Docker (fastest, fewest moving parts)

### Step 1 — Install Docker Desktop

Download from https://www.docker.com/products/docker-desktop/ and install it.
Confirm it's running:

```powershell
docker --version
docker compose version
```

### Step 2 — Configure environment variables

From the project root (`EcoTrack\`):

```powershell
Copy-Item .env.example .env
notepad .env
```

At minimum, change `JWT_SECRET` to any long random string. Save and close.

### Step 3 — Start everything

```powershell
docker compose up -d --build
```

First run takes a few minutes (downloading Postgres/Redis/Node/Python images).

### Step 4 — Run migrations and seed data

```powershell
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed
```

### Step 5 — Open the app

Frontend: http://localhost:3000
Backend API docs: http://localhost:8000/docs

Log in with `admin@example.com` / `EcoTrack@123` (or any account from the
README's seed data table).

### Stopping / restarting

```powershell
docker compose down          # stop everything
docker compose up -d         # start again (no rebuild needed)
docker compose logs -f backend   # watch backend logs
```

---

## Option 2: Run everything natively (no Docker)

### Step 1 — Install prerequisites

- **Node.js 20+**: https://nodejs.org (LTS version). Confirm: `node --version`
- **Python 3.11+**: https://www.python.org/downloads/ — during install, check
  "Add python.exe to PATH". Confirm: `python --version`
- **PostgreSQL 16**: https://www.postgresql.org/download/windows/ — during
  install, remember the password you set for the `postgres` user.
- **Redis**: on Windows, the easiest path is Docker just for Redis
  (`docker run -d -p 6379:6379 redis:7-alpine`), or use WSL2 and install Redis
  there. Native Windows Redis builds are unofficial/outdated.

### Step 2 — Create the database

Open "SQL Shell (psql)" from the Start menu (installed with PostgreSQL):

```sql
CREATE USER ecotrack WITH PASSWORD 'ecotrack';
CREATE DATABASE ecotrack OWNER ecotrack;
```

### Step 3 — Backend setup

From the project root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item ..\.env.example .env
notepad .env
```

In `.env`, set:
```
DATABASE_URL=postgresql+psycopg2://ecotrack:ecotrack@localhost:5432/ecotrack
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=<any long random string>
```

Run migrations and seed data:
```powershell
alembic upgrade head
python -m app.seed
```

Start the backend:
```powershell
uvicorn app.main:app --reload
```

Leave this terminal running. Backend is now at http://localhost:8000 — check
http://localhost:8000/docs to confirm it's up.

### Step 4 — Frontend setup

Open a **new** PowerShell window:

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
```

`.env.local` should contain:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start the frontend:
```powershell
npm run dev
```

Open http://localhost:3000

### Step 5 (optional) — Train your own ML model

Open a **third** PowerShell window (with the backend's venv, or a new one):

```powershell
cd EcoTrack
python -m venv ml-venv
.\ml-venv\Scripts\Activate.ps1
pip install -r ml\requirements.txt
```

Put training images in `ml\dataset\raw\<Category>\*.jpg` for each of the 8
categories, then:
```powershell
python -m ml.preprocessing.dataset_prep
python ml\train.py
python ml\evaluate.py
```

When training finishes, edit `backend\.env`, set `ML_MODE=production`, and
restart the backend (Ctrl+C in its terminal, then `uvicorn app.main:app --reload`
again).

---

## Running the tests

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest tests/ -v
```

```powershell
cd EcoTrack
python -m pytest ml\tests\ -v
```

```powershell
cd frontend
npm run build
```

---

## macOS / Linux notes

Everywhere above that says `.\venv\Scripts\Activate.ps1`, use
`source venv/bin/activate` instead. Everywhere that says `Copy-Item a b`, use
`cp a b`. Everything else is identical.
