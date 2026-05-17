"""Outcome API service helpers for Build 08.

This service delegates outcome normalization to the existing Build 07 outcome
logger and formats the API response. It does not calculate metrics, generate
feedback analytics, create recalibration signals, or write production data.
"""

from __future__ import annotations

from collections.abc import Sequence

from backend.api.schemas.outcome_schema import (
    OutcomeSubmissionRequest,
    OutcomeSubmissionResponse,
)
from backend.learning.outcome_logger import OutcomeLoggingError, log_outcome


class OutcomeServiceError(ValueError):
    """Raised when an outcome submission cannot be accepted by the API layer."""


def submit_outcome_response(
    outcome_submission: OutcomeSubmissionRequest,
    *,
    known_recommendation_ids: Sequence[str] | None = None,
) -> OutcomeSubmissionResponse:
    """Validate and normalize one outcome submission through the learning layer."""

    try:
        outcome_record = log_outcome(
            outcome_submission.model_dump(),
            known_recommendation_ids=known_recommendation_ids,
        )
    except OutcomeLoggingError as exc:
        raise OutcomeServiceError(str(exc)) from exc

    return OutcomeSubmissionResponse(
        status="success",
        message="Outcome recorded successfully.",
        outcome_id=outcome_record.outcome_id,
    )
