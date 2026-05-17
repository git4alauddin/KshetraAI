"""Explainability API service helpers for Build 08.

This service reads existing explanation outputs and formats API responses. It
does not map evidence, assess confidence, or generate explanation text.
"""

from __future__ import annotations

import ast
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pandas as pd

from backend.api.schemas.explainability_schema import (
    ExplanationItemResponse,
    ExplanationResponse,
)


DEFAULT_EXPLANATION_OUTPUTS_PATH = Path("datasets/processed/explanation_outputs.csv")


class ExplainabilityServiceError(ValueError):
    """Raised when explanation output cannot be exposed safely."""


def get_explanation_response(
    entity_id: str,
    *,
    explanation_outputs: pd.DataFrame | None = None,
    data_path: Path | str = DEFAULT_EXPLANATION_OUTPUTS_PATH,
) -> ExplanationResponse:
    """Return stable explanation response from existing explanation outputs."""

    source_view = (
        explanation_outputs
        if explanation_outputs is not None
        else _load_view(data_path)
    )
    if source_view.empty:
        return ExplanationResponse(entity_id=entity_id, explanations=[])

    _require_columns(
        source_view,
        ("entity_id", "explanation_type", "summary_text", "evidence_items", "confidence_level"),
    )
    matching_rows = source_view[source_view["entity_id"].astype(str) == str(entity_id)]
    if matching_rows.empty:
        return ExplanationResponse(entity_id=entity_id, explanations=[])

    sorted_rows = _sort_matches(matching_rows)
    explanations = [
        _explanation_item(row)
        for row in sorted_rows.to_dict(orient="records")
    ]
    return ExplanationResponse(entity_id=entity_id, explanations=explanations)


def _load_view(data_path: Path | str) -> pd.DataFrame:
    resolved_path = Path(data_path)
    if not resolved_path.exists():
        return pd.DataFrame()
    return pd.read_csv(resolved_path)


def _sort_matches(matching_rows: pd.DataFrame) -> pd.DataFrame:
    sort_columns = [
        column
        for column in ("explanation_type", "source_output_id")
        if column in matching_rows.columns
    ]
    if not sort_columns:
        return matching_rows.reset_index(drop=True)
    return matching_rows.sort_values(sort_columns, kind="mergesort").reset_index(drop=True)


def _explanation_item(row: dict[str, Any]) -> ExplanationItemResponse:
    return ExplanationItemResponse(
        explanation_type=_text_value(row["explanation_type"], "explanation_type"),
        summary_text=_text_value(row["summary_text"], "summary_text"),
        evidence_items=_evidence_items(row["evidence_items"]),
        confidence_level=_text_value(row["confidence_level"], "confidence_level"),
    )


def _evidence_items(value: Any) -> list[str]:
    evidence_items = _parse_evidence_items(value)
    normalized_items = [_evidence_item_text(item) for item in evidence_items]
    output = [item for item in normalized_items if item]
    if not output:
        raise ExplainabilityServiceError("evidence_items cannot be empty.")
    return output


def _parse_evidence_items(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
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
    raise ExplainabilityServiceError("evidence_items must be a list or serialized list.")


def _evidence_item_text(item: Any) -> str:
    if isinstance(item, Mapping):
        source_field = str(item.get("source_field", "") or "").strip()
        description = str(item.get("description", "") or "").strip()
        value = item.get("value")
        if description:
            return description
        if source_field and value is not None:
            return f"{source_field}: {value}"
        if source_field:
            return source_field
        return ""
    return str(item or "").strip()


def _require_columns(dataframe: pd.DataFrame, required_columns: tuple[str, ...]) -> None:
    missing_columns = [column for column in required_columns if column not in dataframe.columns]
    if missing_columns:
        raise ExplainabilityServiceError(
            "Explanation outputs are missing columns: "
            + ", ".join(missing_columns)
        )


def _text_value(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ExplainabilityServiceError(f"{field} cannot be empty.")
    return text
