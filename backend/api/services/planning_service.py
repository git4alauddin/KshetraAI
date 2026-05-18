"""Planning API service helpers for Build 08.

This service reads existing ranked visit outputs and formats API responses. It
does not calculate priority scores, classify priority, rank entities, or run
feature engineering.
"""

from __future__ import annotations

from pathlib import Path
from math import ceil
from typing import Any

import pandas as pd

from backend.api.schemas.planning_schema import DailyPlanResponse, RankedEntityResponse


DEFAULT_RANKED_VISIT_LIST_PATH = Path("datasets/processed/ranked_visit_list.csv")
DEFAULT_DAILY_PLAN_PAGE = 1
DEFAULT_DAILY_PLAN_PAGE_SIZE = 3


class PlanningServiceError(ValueError):
    """Raised when planning output cannot be exposed safely."""


def get_daily_plan_response(
    *,
    rep_id: str | None = None,
    territory_id: str | None = None,
    date: str | None = None,
    page: int = DEFAULT_DAILY_PLAN_PAGE,
    page_size: int = DEFAULT_DAILY_PLAN_PAGE_SIZE,
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
            page=page,
            page_size=page_size,
            total_count=0,
            total_pages=0,
            ranked_entities=[],
        )

    _require_columns(source_view, ("entity_id", "priority_score", "priority_level"))
    _validate_pagination(page=page, page_size=page_size)
    filtered_view = _apply_filters(source_view, rep_id=rep_id, territory_id=territory_id, date=date)
    ranked_view = _with_daily_plan_rank(filtered_view)
    total_count = len(ranked_view)
    total_pages = ceil(total_count / page_size) if total_count else 0
    page_view = _page_slice(ranked_view, page=page, page_size=page_size)
    ranked_entities = [
        _ranked_entity(row, fallback_rank=index + 1)
        for index, row in enumerate(page_view.to_dict(orient="records"))
    ]
    return DailyPlanResponse(
        rep_id=rep_id,
        territory_id=territory_id,
        date=date,
        page=page,
        page_size=page_size,
        total_count=total_count,
        total_pages=total_pages,
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

    if "priority_score" in output.columns:
        return output.sort_values(
            ["priority_score", "entity_id"],
            ascending=[False, True],
            kind="mergesort",
        ).reset_index(drop=True)
    return output.reset_index(drop=True)


def _with_daily_plan_rank(ranked_visit_list: pd.DataFrame) -> pd.DataFrame:
    output = ranked_visit_list.reset_index(drop=True).copy()
    output["rank"] = range(1, len(output) + 1)
    return output


def _page_slice(ranked_visit_list: pd.DataFrame, *, page: int, page_size: int) -> pd.DataFrame:
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    return ranked_visit_list.iloc[start_index:end_index].reset_index(drop=True)


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


def _validate_pagination(*, page: int, page_size: int) -> None:
    if page < 1:
        raise PlanningServiceError("page must be at least 1.")
    if page_size < 1:
        raise PlanningServiceError("page_size must be at least 1.")
    if page_size > 50:
        raise PlanningServiceError("page_size must be at most 50.")


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
