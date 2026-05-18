"""FastAPI application entrypoint for KshetraAI Build 08.

The API layer is intentionally thin: it registers transport routes and leaves
all intelligence logic inside the existing backend modules.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.anomaly_routes import router as anomaly_router
from backend.api.routes.explainability_routes import router as explainability_router
from backend.api.routes.health_routes import router as health_router
from backend.api.routes.outcome_routes import router as outcome_router
from backend.api.routes.planning_routes import router as planning_router
from backend.api.routes.recommendation_routes import router as recommendation_router


API_TITLE = "KshetraAI Backend"
API_VERSION = "0.1.0"
LOCAL_FRONTEND_ORIGINS = (
    "http://127.0.0.1:5173",
    "http://localhost:5173",
)


def create_app() -> FastAPI:
    """Create the FastAPI app with stable route registration."""

    app = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        description="Controlled API layer for KshetraAI operational intelligence.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(LOCAL_FRONTEND_ORIGINS),
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(planning_router)
    app.include_router(recommendation_router)
    app.include_router(anomaly_router)
    app.include_router(explainability_router)
    app.include_router(outcome_router)
    return app


app = create_app()
