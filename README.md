# 🌱 EcoTrack — AI-Powered Smart Waste Management & Recycling Platform

A full-stack platform connecting citizens, waste collectors, recycling centers,
and administrators — with AI-based waste image classification, map-based
recycling center discovery, pickup scheduling, and a rewards/leaderboard system.
It also helps users log daily activities related to waste and recycling.

Built as a CSE portfolio / final-year project. Every feature in this README has
been exercised against a real database and a real HTTP client during
development (see `docs/testing.md` for exact results) — this is not a mockup.

---

## 1. What EcoTrack is

Citizens report waste (with a photo), the system classifies it automatically,
suggests where to recycle it, and lets them schedule a pickup. Collectors get a
queue of assigned pickups to work through. Admins manage users, verify reports,
configure recycling centers, and see platform-wide analytics.

## 2. Problem statement

Waste sorting and recycling participation is low partly because it's
inconvenient: people don't know what category something falls into, where to
take it, or how to arrange collection. EcoTrack removes each of those frictions
and adds a light gamification layer (points, badges, a leaderboard) to
encourage participation.

## 3. Features

- Email/password auth with JWT access + refresh tokens, bcrypt password hashing,
  role-based access control (USER / COLLECTOR / ADMIN)
- Waste reporting with photo upload → AI classification (8 categories) →
  recyclability + disposal recommendation
- NLP-based possible-duplicate-report detection (TF-IDF + cosine similarity)
- Map-based recycling center finder (Leaflet + OpenStreetMap, no paid API key
  needed) with filtering by waste type and distance
- Pickup scheduling with a 6-state status workflow and a collector dashboard
- Real-time status push over WebSockets (falls back gracefully to polling via
  normal page loads if the socket isn't connected)
- Reward points, badges, and a weekly/monthly/all-time leaderboard
- Admin dashboard: user management, report verification, recycling center CRUD,
  analytics charts (Recharts)
- Dockerized (Postgres + Redis + backend + frontend), Alembic migrations, a
  seed script, and a pytest suite for both the backend and the ML module

## 4. Architecture

See `docs/architecture.md` for diagrams. Short version: Next.js frontend →
FastAPI backend → PostgreSQL, with a standalone `ml/` package the backend calls
into for image classification, and Redis available for caching/background work.

## 5. Technology stack

**Frontend:** Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS,
Framer Motion, Lucide icons, React Hook Form + Zod, Recharts, Leaflet/React-Leaflet

**Backend:** Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, JWT
(python-jose), passlib/bcrypt, WebSockets

**Database:** PostgreSQL 16 · **Cache:** Redis 7

**ML:** MobileNetV2 transfer learning (TensorFlow/Keras) for the trainable
model, plus a genuine lightweight heuristic classifier that works with zero
setup in "demo mode" (see `docs/ml.md`)

## 6. Folder structure

```
EcoTrack/
├── frontend/          Next.js app (App Router)
├── backend/           FastAPI app
│   ├── app/
│   │   ├── api/routes/      route handlers
│   │   ├── services/        business logic (ml, storage, rewards, duplicates, notifications)
│   │   ├── models/          SQLAlchemy models
│   │   ├── schemas/         Pydantic schemas
│   │   └── core/            config, security, dependencies
│   ├── alembic/              migrations
│   ├── tests/                 pytest suite
│   └── app/seed.py            dev data seeder
├── ml/                Standalone ML package (train/evaluate/predict)
│   └── tests/                 pytest suite
├── database/schema.sql Plain-SQL schema reference
├── docs/               architecture, database, api, ml, deployment, security, testing
├── docker-compose.yml
├── .env.example
├── README.md            (this file)
└── SETUP_GUIDE.md        exact copy-paste commands, Windows-first
```

## 7. Prerequisites

- Node.js 20+ and npm
- Python 3.11+
- PostgreSQL 16 (or use the Docker Compose service)
- Redis 7 (or use the Docker Compose service)
- Docker + Docker Compose (optional, but the easiest path)

## 8. Installation (quick path with Docker)

```bash
git clone <this-repo-url> EcoTrack && cd EcoTrack
cp .env.example .env          # edit JWT_SECRET at minimum
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed
```

Frontend: http://localhost:3000 · Backend docs: http://localhost:8000/docs

For a from-scratch, no-Docker walkthrough (Windows PowerShell commands
included), see **SETUP_GUIDE.md**.

## 9. PostgreSQL setup

Via Docker Compose it's automatic. Running your own instance instead: create a
database and user matching whatever you put in `DATABASE_URL`, e.g.:
```sql
CREATE USER ecotrack WITH PASSWORD 'ecotrack';
CREATE DATABASE ecotrack OWNER ecotrack;
```

## 10. Redis setup

Via Docker Compose it's automatic. Standalone: install Redis and point
`REDIS_URL` at it (default `redis://localhost:6379/0`).

## 11. Environment variables

Copy `.env.example` to `.env` (root, for Docker Compose) and/or
`backend/.env` (for running the backend directly) and `frontend/.env.local`
(for `NEXT_PUBLIC_API_URL`). Every variable is documented inline in
`.env.example`. Never commit a real `.env`.

## 12. Database migration

```bash
cd backend
alembic upgrade head
```

## 13. Seed data

```bash
cd backend
python -m app.seed
```

Creates an admin, a collector, and two citizen accounts, plus sample recycling
centers, a waste report, and pickups. **Development-only credentials** (all
share one password):

| Role | Email | Password |
|---|---|---|
| Admin | `admin@example.com` | `EcoTrack@123` |
| Collector | `collector@example.com` | `EcoTrack@123` |
| Citizen | `asha@example.com` | `EcoTrack@123` |
| Citizen | `rohan@example.com` | `EcoTrack@123` |

Never reuse these anywhere real.

## 14. Running the frontend

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

## 15. Running the backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload   # http://localhost:8000
```

## 16. Running the ML module

Demo mode needs nothing extra — the backend already uses it by default. To
train your own model:
```bash
pip install -r ml/requirements.txt
# put images in ml/dataset/raw/<Category>/*.jpg first
python -m ml.preprocessing.dataset_prep
python ml/train.py
python ml/evaluate.py
```
Then set `ML_MODE=production` in `backend/.env` and restart the backend.
Full details in `docs/ml.md`.

## 17. Running tests

```bash
cd backend && pytest tests/ -v        # 16 tests
python -m pytest ml/tests/ -v         # 5 tests (run from repo root)
cd frontend && npm run build          # type-checks + verifies the production build
```

## 18. Running with Docker

```bash
docker compose up -d --build
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.seed
```

`docker-compose.yml` builds the backend with the project root as its build
context (so it can copy the sibling `ml/` package) — don't try to
`docker build` the `backend/` folder in isolation.

## 19. API documentation

http://localhost:8000/docs (Swagger) once the backend is running. Reference
tables in `docs/api.md`.

## 20. ML architecture

`docs/ml.md` — covers both the demo heuristic and the MobileNetV2
transfer-learning pipeline for a real trained model.

## 21. Deployment

`docs/deployment.md` — Docker-Compose-on-a-VM and split-hosting (Vercel +
Render/Railway) options, plus a pre-launch checklist.

## 22. Troubleshooting

- **`ModuleNotFoundError: No module named 'ml'`** from the backend — make sure
  you're running uvicorn from inside `backend/` with `ml/` present as a sibling
  directory one level up (this is the default repo layout; don't move `backend/`
  without also moving `ml/`).
- **bcrypt / passlib errors on registration** — this project pins
  `bcrypt==4.0.1` in `backend/requirements.txt` specifically because newer
  bcrypt releases break passlib 1.7.4's backend detection. If you've upgraded
  it, downgrade back to `4.0.1` or wait for a passlib release that supports the
  new bcrypt API.
- **CORS errors in the browser** — check `CORS_ORIGINS` in your backend `.env`
  includes your frontend's exact origin (protocol + host + port).
- **Images don't load in the app** — confirm `NEXT_PUBLIC_API_URL` in the
  frontend's `.env.local` matches where the backend is actually running; the
  frontend fetches uploaded images from `${NEXT_PUBLIC_API_URL}${image_url}`.
- **`ML_MODE=production` returns 503** — the trained model file doesn't exist
  yet at `ml/models/waste_classifier.h5`. Train one (`docs/ml.md`) or switch
  back to `ML_MODE=demo`.

## 23. Future improvements

- Real-time collector location tracking on the map during an active pickup
- Push notifications (web push / mobile) in addition to the in-app feed
- Multi-image reports (before/after photos)
- Admin-configurable reward point values via a settings table instead of a
  Python dict
- Proper rate limiting and request throttling
- i18n for languages beyond English

---

Also see: `SETUP_GUIDE.md` for copy-paste commands · `docs/` for deep dives on
each subsystem.
