"""FastAPI application entrypoint for KshetraAI Build 08.

The API layer is intentionally thin: it registers transport routes and leaves
all intelligence logic inside the existing backend modules.
"""

from __future__ import annotations

from fastapi import FastAPI

from backend.api.routes.health_routes import router as health_router


API_TITLE = "KshetraAI Backend"
API_VERSION = "0.1.0"


def create_app() -> FastAPI:
    """Create the FastAPI app with stable route registration."""

    app = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        description="Controlled API layer for KshetraAI operational intelligence.",
    )
    app.include_router(health_router)
    return app


app = create_app()
