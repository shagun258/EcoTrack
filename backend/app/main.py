import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import admin, analytics, auth, leaderboard, ml, notifications, pickups, recycling_centers, rewards, users, waste, ws
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ecotrack")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="AI-powered smart waste management & recycling platform API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

routers = [
    auth.router,
    users.router,
    waste.router,
    ml.router,
    pickups.router,
    recycling_centers.router,
    rewards.router,
    leaderboard.router,
    notifications.router,
    notifications.complaints_router,
    admin.router,
    analytics.router,
]
for r in routers:
    app.include_router(r)

app.include_router(ws.router)


@app.get("/")
def root():
    return {"name": settings.APP_NAME, "status": "running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENV, "ml_mode": settings.ML_MODE}


# --- Graceful, user-friendly error handling (never leak stack traces) ------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid request data", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )
