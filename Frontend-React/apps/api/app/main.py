"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.api import health, claims, uploads, submission

app = FastAPI(
    title="Constaty API",
    version="0.1.0",
    description="Intelligent automobile accident claims assistant for Tunisia.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(claims.router, prefix="/api/v1")
app.include_router(uploads.router, prefix="/api/v1")
app.include_router(submission.router, prefix="/api/v1")

# Serve uploaded evidence files
_storage_path = Path(__file__).resolve().parent.parent.parent / "storage"
_storage_path.mkdir(parents=True, exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(_storage_path)), name="storage")


@app.get("/")
async def root():
    return {"name": "Constaty API", "docs": "/docs"}