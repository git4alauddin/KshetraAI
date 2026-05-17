"""Anomaly API schemas for Build 08.

These models expose existing alert outputs only. They do not detect anomalies
or classify severity.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AlertResponse(BaseModel):
    """One anomaly or opportunity alert response item."""

    alert_id: str = Field(min_length=1)
    entity_id: str = Field(min_length=1)
    alert_type: str = Field(min_length=1)
    severity_score: float = Field(ge=0, le=100)
    severity_level: str = Field(min_length=1)
    confidence_level: str = Field(min_length=1)


class AlertsResponse(BaseModel):
    """Stable alert list response payload."""

    alerts: list[AlertResponse] = Field(default_factory=list)
