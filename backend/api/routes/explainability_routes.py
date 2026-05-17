"""Explainability API routes for Build 08.

Routes expose existing explanation outputs only and delegate data access to the
explainability service.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.api.schemas.explainability_schema import ExplanationResponse
from backend.api.services.explainability_service import (
    ExplainabilityServiceError,
    get_explanation_response,
)


router = APIRouter(tags=["explanations"])


@router.get("/explanations/{entity_id}", response_model=ExplanationResponse)
def get_entity_explanations(entity_id: str) -> ExplanationResponse:
    """Return existing explanations for one entity."""

    try:
        return get_explanation_response(entity_id)
    except ExplainabilityServiceError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
