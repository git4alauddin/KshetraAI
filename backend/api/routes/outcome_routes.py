"""Outcome API routes for Build 08.

Routes accept validated outcome submissions and delegate normalization to the
outcome service. They do not calculate metrics or generate learning signals.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.api.schemas.outcome_schema import (
    OutcomeSubmissionRequest,
    OutcomeSubmissionResponse,
)
from backend.api.services.outcome_service import OutcomeServiceError, submit_outcome_response
from backend.api.services.sample_output_service import (
    SampleOutputServiceError,
    get_sample_outcome_response,
    is_sample_data_mode,
)


router = APIRouter(tags=["outcomes"])


@router.post("/outcomes", response_model=OutcomeSubmissionResponse)
def submit_outcome(
    outcome_submission: OutcomeSubmissionRequest,
) -> OutcomeSubmissionResponse:
    """Accept one field outcome submission."""

    try:
        if is_sample_data_mode():
            return get_sample_outcome_response()
        return submit_outcome_response(outcome_submission)
    except SampleOutputServiceError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except OutcomeServiceError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
