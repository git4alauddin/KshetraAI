"""Planning API routes for Build 08.

Routes remain thin request/response handlers and delegate processed-output
access to the planning service.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from backend.api.schemas.planning_schema import DailyPlanResponse
from backend.api.services.planning_service import (
    DEFAULT_DAILY_PLAN_PAGE,
    DEFAULT_DAILY_PLAN_PAGE_SIZE,
    PlanningServiceError,
    get_daily_plan_response,
)
from backend.api.services.sample_output_service import (
    SampleOutputServiceError,
    get_sample_daily_plan_response,
    is_sample_data_mode,
)


router = APIRouter(tags=["planning"])


@router.get("/daily-plan", response_model=DailyPlanResponse)
def get_daily_plan(
    rep_id: str | None = Query(default=None, min_length=1),
    territory_id: str | None = Query(default=None, min_length=1),
    date: str | None = Query(default=None, min_length=1),
    page: Annotated[int, Query(ge=1)] = DEFAULT_DAILY_PLAN_PAGE,
    page_size: Annotated[int, Query(ge=1, le=50)] = DEFAULT_DAILY_PLAN_PAGE_SIZE,
) -> DailyPlanResponse:
    """Return existing ranked visit outputs as a daily plan response."""

    try:
        if is_sample_data_mode():
            return get_sample_daily_plan_response(page=page, page_size=page_size)
        return get_daily_plan_response(
            rep_id=rep_id,
            territory_id=territory_id,
            date=date,
            page=page,
            page_size=page_size,
        )
    except SampleOutputServiceError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except PlanningServiceError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
