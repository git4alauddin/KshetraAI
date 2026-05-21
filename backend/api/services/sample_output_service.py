"""Demo-safe sample output helpers for deployed API demos.

The default API path reads processed CSV outputs. When
`KSHETRA_API_DATA_MODE=sample`, routes can serve the committed sanitized JSON
payloads under `demo/sample_outputs/` instead. This keeps cloud demos small and
avoids committing generated processed CSV files.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from backend.api.schemas.anomaly_schema import AlertsResponse
from backend.api.schemas.explainability_schema import ExplanationResponse
from backend.api.schemas.outcome_schema import OutcomeSubmissionResponse
from backend.api.schemas.planning_schema import DailyPlanResponse
from backend.api.schemas.recommendation_schema import RecommendationResponse


DATA_MODE_ENV = "KSHETRA_API_DATA_MODE"
SAMPLE_DATA_MODE = "sample"
DEFAULT_SAMPLE_OUTPUT_DIR = Path("demo") / "sample_outputs"

ModelT = TypeVar("ModelT", bound=BaseModel)


class SampleOutputServiceError(ValueError):
    """Raised when a committed sample payload cannot be served safely."""


def is_sample_data_mode() -> bool:
    """Return whether API routes should serve committed sample JSON payloads."""

    return os.getenv(DATA_MODE_ENV, "").strip().lower() == SAMPLE_DATA_MODE


def get_sample_daily_plan_response(
    *,
    page: int,
    page_size: int,
    sample_dir: Path | str = DEFAULT_SAMPLE_OUTPUT_DIR,
) -> DailyPlanResponse:
    """Return the committed daily-plan sample response."""

    response = _load_sample_model(
        "daily_plan_response.json",
        DailyPlanResponse,
        sample_dir=sample_dir,
    )
    return response.model_copy(update={"page": page, "page_size": page_size})


def get_sample_recommendation_response(
    entity_id: str,
    *,
    sample_dir: Path | str = DEFAULT_SAMPLE_OUTPUT_DIR,
) -> RecommendationResponse:
    """Return the committed recommendation sample response for the demo entity."""

    response = _load_sample_model(
        "recommendation_response.json",
        RecommendationResponse,
        sample_dir=sample_dir,
    )
    if response.entity_id != entity_id:
        raise SampleOutputServiceError(f"No sample recommendation found for entity_id: {entity_id}")
    return response


def get_sample_alerts_response(
    *,
    page: int,
    page_size: int,
    sample_dir: Path | str = DEFAULT_SAMPLE_OUTPUT_DIR,
) -> AlertsResponse:
    """Return the committed alerts sample response."""

    response = _load_sample_model("alerts_response.json", AlertsResponse, sample_dir=sample_dir)
    return response.model_copy(update={"page": page, "page_size": page_size})


def get_sample_explanation_response(
    entity_id: str,
    *,
    sample_dir: Path | str = DEFAULT_SAMPLE_OUTPUT_DIR,
) -> ExplanationResponse:
    """Return the committed explanation sample response for the demo entity."""

    response = _load_sample_model(
        "explanation_response.json",
        ExplanationResponse,
        sample_dir=sample_dir,
    )
    if response.entity_id != entity_id:
        return ExplanationResponse(entity_id=entity_id, explanations=[])
    return response


def get_sample_outcome_response(
    *,
    sample_dir: Path | str = DEFAULT_SAMPLE_OUTPUT_DIR,
) -> OutcomeSubmissionResponse:
    """Return the committed outcome-submission sample response."""

    return _load_sample_model(
        "outcome_submission_response.json",
        OutcomeSubmissionResponse,
        sample_dir=sample_dir,
    )


def _load_sample_model(
    filename: str,
    model_type: type[ModelT],
    *,
    sample_dir: Path | str,
) -> ModelT:
    sample_path = Path(sample_dir) / filename
    if not sample_path.exists():
        raise SampleOutputServiceError(f"Missing sample output: {sample_path}")

    try:
        payload = json.loads(sample_path.read_text(encoding="utf-8"))
        return model_type.model_validate(payload)
    except json.JSONDecodeError as exc:
        raise SampleOutputServiceError(f"Invalid sample JSON: {sample_path}") from exc
    except ValidationError as exc:
        raise SampleOutputServiceError(f"Invalid sample payload: {sample_path}") from exc
