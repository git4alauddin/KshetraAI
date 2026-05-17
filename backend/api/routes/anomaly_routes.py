"""Anomaly API routes for Build 08.

Routes expose existing anomaly alert outputs only and delegate data access to
the anomaly service.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from backend.api.schemas.anomaly_schema import AlertsResponse
from backend.api.services.anomaly_service import AnomalyServiceError, get_alerts_response


router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=AlertsResponse)
def get_alerts(
    territory_id: str | None = Query(default=None, min_length=1),
    severity: str | None = Query(default=None, min_length=1),
) -> AlertsResponse:
    """Return existing anomaly alerts with optional API-level filters."""

    try:
        return get_alerts_response(territory_id=territory_id, severity=severity)
    except AnomalyServiceError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
