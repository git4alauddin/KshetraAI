"""Planning API service helpers for Build 08.

This service reads existing ranked visit outputs and formats API responses. It
does not calculate priority scores, classify priority, rank entities, or run
feature engineering.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from backend.api.schemas.planning_schema import DailyPlanResponse, RankedEntityResponse


DEFAULT_RANKED_VISIT_LIST_PATH = Path("datasets/processed/ranked_visit_list.csv")


class PlanningServiceError(ValueError):
    """Raised when planning output cannot be exposed safely."""


def get_daily_plan_response(
    *,
    rep_id: str | None = None,
    territory_id: str | None = None,
    date: str | None = None,
    ranked_visit_list: pd.DataFrame | None = None,
    data_path: Path | str = DEFAULT_RANKED_VISIT_LIST_PATH,
) -> DailyPlanResponse:
    """Return a stable daily plan response from existing ranked outputs."""

    source_view = ranked_visit_list if ranked_visit_list is not None else _load_view(data_path)
    if source_view.empty:
        return DailyPlanResponse(
            rep_id=rep_id,
            territory_id=territory_id,
            date=date,
            ranked_entities=[],
        )

    _require_columns(source_view, ("entity_id", "priority_score", "priority_level"))
    filtered_view = _apply_filters(source_view, rep_id=rep_id, territory_id=territory_id, date=date)
    ranked_entities = [
        _ranked_entity(row, fallback_rank=index + 1)
        for index, row in enumerate(filtered_view.to_dict(orient="records"))
    ]
    return DailyPlanResponse(
        rep_id=rep_id,
        territory_id=territory_id,
        date=date,
        ranked_entities=ranked_entities,
    )


def _load_view(data_path: Path | str) -> pd.DataFrame:
    resolved_path = Path(data_path)
    if not resolved_path.exists():
        return pd.DataFrame()
    return pd.read_csv(resolved_path)


def _apply_filters(
    ranked_visit_list: pd.DataFrame,
    *,
    rep_id: str | None,
    territory_id: str | None,
    date: str | None,
) -> pd.DataFrame:
    output = ranked_visit_list.copy()
    for column, value in (
        ("rep_id", rep_id),
        ("territory_id", territory_id),
        ("date", date),
    ):
        if value is not None and column in output.columns:
            output = output[output[column].astype(str) == str(value)]

    if "rank" in output.columns:
        return output.sort_values("rank", kind="mergesort").reset_index(drop=True)
    if "priority_score" in output.columns:
        return output.sort_values(
            ["priority_score", "entity_id"],
            ascending=[False, True],
            kind="mergesort",
        ).reset_index(drop=True)
    return output.reset_index(drop=True)


def _ranked_entity(row: dict[str, Any], *, fallback_rank: int) -> RankedEntityResponse:
    return RankedEntityResponse(
        rank=_int_value(row.get("rank", fallback_rank), "rank"),
        entity_id=_text_value(row["entity_id"], "entity_id"),
        entity_name=str(row.get("entity_name", "") or ""),
        priority_score=_float_value(row["priority_score"], "priority_score"),
        priority_level=_text_value(row["priority_level"], "priority_level"),
        main_reason=str(row.get("main_reason", row.get("reason", "")) or ""),
    )


def _require_columns(dataframe: pd.DataFrame, required_columns: tuple[str, ...]) -> None:
    missing_columns = [column for column in required_columns if column not in dataframe.columns]
    if missing_columns:
        raise PlanningServiceError(
            "Ranked visit list is missing columns: "
            + ", ".join(missing_columns)
        )


def _text_value(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise PlanningServiceError(f"{field} cannot be empty.")
    return text


def _float_value(value: Any, field: str) -> float:
    numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric_value):
        raise PlanningServiceError(f"{field} must be numeric.")
    return float(numeric_value)


def _int_value(value: Any, field: str) -> int:
    numeric_value = _float_value(value, field)
    if numeric_value < 1:
        raise PlanningServiceError(f"{field} must be at least 1.")
    return int(numeric_value)
