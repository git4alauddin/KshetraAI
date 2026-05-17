"""Recommendation API service helpers for Build 08.

This service reads existing recommendation outputs and formats API responses.
It does not match rules, select actions, score confidence, or generate new
recommendations.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pandas as pd

from backend.api.schemas.recommendation_schema import RecommendationResponse


DEFAULT_RECOMMENDATION_OUTPUTS_PATH = Path("datasets/processed/recommendation_outputs.csv")


class RecommendationServiceError(ValueError):
    """Raised when recommendation output cannot be exposed safely."""


class RecommendationNotFoundError(LookupError):
    """Raised when no existing recommendation is available for an entity."""


def get_recommendation_response(
    entity_id: str,
    *,
    recommendation_outputs: pd.DataFrame | None = None,
    data_path: Path | str = DEFAULT_RECOMMENDATION_OUTPUTS_PATH,
) -> RecommendationResponse:
    """Return one entity recommendation from existing recommendation outputs."""

    source_view = (
        recommendation_outputs
        if recommendation_outputs is not None
        else _load_view(data_path)
    )
    if source_view.empty:
        raise RecommendationNotFoundError(f"No recommendation found for entity_id: {entity_id}")

    _require_columns(source_view, ("entity_id", "recommended_actions", "confidence_level"))
    matching_rows = source_view[source_view["entity_id"].astype(str) == str(entity_id)]
    if matching_rows.empty:
        raise RecommendationNotFoundError(f"No recommendation found for entity_id: {entity_id}")

    row = _sort_matches(matching_rows).iloc[0].to_dict()
    return RecommendationResponse(
        entity_id=_text_value(row["entity_id"], "entity_id"),
        risk_or_opportunity=str(
            row.get("risk_or_opportunity", row.get("matched_rule_id", ""))
            or ""
        ),
        recommended_actions=_actions(row["recommended_actions"]),
        recommended_product_category=str(row.get("recommended_product_category", "") or ""),
        confidence_level=_text_value(row["confidence_level"], "confidence_level"),
    )


def _load_view(data_path: Path | str) -> pd.DataFrame:
    resolved_path = Path(data_path)
    if not resolved_path.exists():
        return pd.DataFrame()
    return pd.read_csv(resolved_path)


def _sort_matches(matching_rows: pd.DataFrame) -> pd.DataFrame:
    if "priority_order" in matching_rows.columns:
        return matching_rows.sort_values("priority_order", kind="mergesort").reset_index(drop=True)
    if "matched_rule_id" in matching_rows.columns:
        return matching_rows.sort_values("matched_rule_id", kind="mergesort").reset_index(drop=True)
    return matching_rows.reset_index(drop=True)


def _actions(value: Any) -> list[str]:
    if isinstance(value, list):
        actions = value
    elif isinstance(value, tuple):
        actions = list(value)
    elif isinstance(value, str):
        actions = _actions_from_string(value)
    else:
        raise RecommendationServiceError("recommended_actions must be a list or serialized list.")

    normalized_actions = [str(action).strip() for action in actions if str(action).strip()]
    if not normalized_actions:
        raise RecommendationServiceError("recommended_actions cannot be empty.")
    return normalized_actions


def _actions_from_string(value: str) -> list[Any]:
    stripped_value = value.strip()
    if not stripped_value:
        return []
    try:
        parsed_value = ast.literal_eval(stripped_value)
    except (SyntaxError, ValueError):
        return [stripped_value]
    if isinstance(parsed_value, (list, tuple)):
        return list(parsed_value)
    return [parsed_value]


def _require_columns(dataframe: pd.DataFrame, required_columns: tuple[str, ...]) -> None:
    missing_columns = [column for column in required_columns if column not in dataframe.columns]
    if missing_columns:
        raise RecommendationServiceError(
            "Recommendation outputs are missing columns: "
            + ", ".join(missing_columns)
        )


def _text_value(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise RecommendationServiceError(f"{field} cannot be empty.")
    return text
