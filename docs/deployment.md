# Deployment

This covers going from "runs locally" to "runs on the internet." It's guidance,
not a fully automated pipeline — pick the option that matches what you already
have access to.

## Option A: Docker Compose on a single VM

Works on any VPS (DigitalOcean, a college lab server, AWS EC2, etc.) with
Docker installed.

1. Copy the repo to the server, create a real `.env` from `.env.example`
   (real `JWT_SECRET`, real DB credentials).
2. `docker compose up -d --build`
3. Run migrations once: `docker compose exec backend alembic upgrade head`
4. (Optional) seed dev data: `docker compose exec backend python -m app.seed`
5. Put a reverse proxy (nginx or Caddy) in front of ports 3000 (frontend) and
   8000 (backend) for TLS termination and a real domain.

## Option B: Split hosting

- **Frontend** → Vercel (native Next.js support) or Netlify. Set
  `NEXT_PUBLIC_API_URL` to your deployed backend URL.
- **Backend** → Render, Railway, or Fly.io (all support a Dockerfile deploy
  from `backend/Dockerfile` — remember the build context needs to include the
  sibling `ml/` folder, same as `docker-compose.yml` does).
- **Database** → Render/Railway managed Postgres, Neon, or Supabase (Postgres).
- **Redis** → Upstash (serverless Redis) or your host's managed Redis add-on.

## Before going live

- [ ] Generate a real `JWT_SECRET` (see `docs/security.md`)
- [ ] Set `CORS_ORIGINS` to your real frontend domain only
- [ ] Set `DEBUG=false`
- [ ] Add rate limiting (see `docs/security.md` known gaps)
- [ ] Decide on file storage: local disk doesn't survive redeploys on most
      PaaS hosts — switch `STORAGE_PROVIDER=cloudinary` (or add an S3
      implementation alongside `save_image_cloudinary` in
      `app/services/storage_service.py`) for anything beyond a single
      always-on VM with a persistent volume.
- [ ] Decide on `ML_MODE`: demo mode has zero extra deployment requirements;
      production mode needs TensorFlow in the backend image (already in
      `ml/requirements.txt` — merge it into `backend/requirements.txt` or
      install both in the Dockerfile if you're shipping a trained model) and
      enough RAM/CPU (or GPU) to serve inference.
- [ ] Point `docs/testing.md`'s manual checklist at the deployed URLs once,
      before announcing it's live.

## Environment variables that must change between local and prod

| Variable | Local | Production |
|---|---|---|
| `DATABASE_URL` | local/docker Postgres | managed Postgres connection string |
| `JWT_SECRET` | dev placeholder | long random secret, kept out of git |
| `CORS_ORIGINS` | `http://localhost:3000` | your real frontend domain |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | your real backend domain |
| `STORAGE_PROVIDER` | `local` | `cloudinary` (or S3) recommended |
