"""Health API routes for Build 08.

These routes expose service availability only. They do not invoke or duplicate
priority, recommendation, anomaly, explanation, or learning logic.
"""

from __future__ import annotations

from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
def get_health() -> dict[str, str]:
    """Return deterministic backend health status."""

    return {
        "status": "ok",
        "service": "kshetraai-backend",
    }
