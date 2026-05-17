"""Planning API routes for Build 08.

Routes remain thin request/response handlers and delegate processed-output
access to the planning service.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from backend.api.schemas.planning_schema import DailyPlanResponse
from backend.api.services.planning_service import (
    PlanningServiceError,
    get_daily_plan_response,
)


router = APIRouter(tags=["planning"])


@router.get("/daily-plan", response_model=DailyPlanResponse)
def get_daily_plan(
    rep_id: str | None = Query(default=None, min_length=1),
    territory_id: str | None = Query(default=None, min_length=1),
    date: str | None = Query(default=None, min_length=1),
) -> DailyPlanResponse:
    """Return existing ranked visit outputs as a daily plan response."""

    try:
        return get_daily_plan_response(
            rep_id=rep_id,
            territory_id=territory_id,
            date=date,
        )
    except PlanningServiceError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
