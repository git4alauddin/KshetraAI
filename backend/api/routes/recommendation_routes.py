"""Recommendation API routes for Build 08.

Routes expose existing recommendation outputs only and delegate all data access
to the recommendation service.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.api.schemas.recommendation_schema import RecommendationResponse
from backend.api.services.recommendation_service import (
    RecommendationNotFoundError,
    RecommendationServiceError,
    get_recommendation_response,
)
from backend.api.services.sample_output_service import (
    SampleOutputServiceError,
    get_sample_recommendation_response,
    is_sample_data_mode,
)


router = APIRouter(tags=["recommendations"])


@router.get("/recommendations/{entity_id}", response_model=RecommendationResponse)
def get_entity_recommendation(entity_id: str) -> RecommendationResponse:
    """Return an existing recommendation for one entity."""

    try:
        if is_sample_data_mode():
            return get_sample_recommendation_response(entity_id)
        return get_recommendation_response(entity_id)
    except SampleOutputServiceError as exc:
        raise HTTPException(status_code=404, detail={"error": str(exc)}) from exc
    except RecommendationNotFoundError as exc:
        raise HTTPException(status_code=404, detail={"error": str(exc)}) from exc
    except RecommendationServiceError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
