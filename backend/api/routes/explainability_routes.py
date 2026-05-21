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
from backend.api.services.sample_output_service import (
    SampleOutputServiceError,
    get_sample_explanation_response,
    is_sample_data_mode,
)


router = APIRouter(tags=["explanations"])


@router.get("/explanations/{entity_id}", response_model=ExplanationResponse)
def get_entity_explanations(entity_id: str) -> ExplanationResponse:
    """Return existing explanations for one entity."""

    try:
        if is_sample_data_mode():
            return get_sample_explanation_response(entity_id)
        return get_explanation_response(entity_id)
    except SampleOutputServiceError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except ExplainabilityServiceError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
