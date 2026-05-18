"""Anomaly API routes for Build 08.

Routes expose existing anomaly alert outputs only and delegate data access to
the anomaly service.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from backend.api.schemas.anomaly_schema import AlertsResponse
from backend.api.services.anomaly_service import (
    DEFAULT_ALERT_PAGE,
    DEFAULT_ALERT_PAGE_SIZE,
    AnomalyServiceError,
    get_alerts_response,
)


router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=AlertsResponse)
def get_alerts(
    territory_id: str | None = Query(default=None, min_length=1),
    severity: str | None = Query(default=None, min_length=1),
    page: Annotated[int, Query(ge=1)] = DEFAULT_ALERT_PAGE,
    page_size: Annotated[int, Query(ge=1, le=50)] = DEFAULT_ALERT_PAGE_SIZE,
) -> AlertsResponse:
    """Return existing anomaly alerts with optional API-level filters."""

    try:
        return get_alerts_response(
            territory_id=territory_id,
            severity=severity,
            page=page,
            page_size=page_size,
        )
    except AnomalyServiceError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
