"""Health check endpoint."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "constaty-api",
        "version": "0.1.0",
    }