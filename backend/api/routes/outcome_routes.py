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


router = APIRouter(tags=["outcomes"])


@router.post("/outcomes", response_model=OutcomeSubmissionResponse)
def submit_outcome(
    outcome_submission: OutcomeSubmissionRequest,
) -> OutcomeSubmissionResponse:
    """Accept one field outcome submission."""

    try:
        return submit_outcome_response(outcome_submission)
    except OutcomeServiceError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
