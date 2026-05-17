"""Outcome API schemas for Build 08.

These models validate API payloads for outcome submission only. They do not log
outcomes, calculate metrics, or generate learning signals.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class OutcomeSubmissionRequest(BaseModel):
    """Visit outcome submission accepted by the API layer."""

    recommendation_id: str = Field(min_length=1)
    entity_id: str = Field(min_length=1)
    rep_id: str = Field(min_length=1)
    visit_completed: bool
    recommendation_followed: bool
    sale_made: bool
    order_placed: bool
    order_value: float = Field(ge=0)
    alert_validated: bool | Literal["unknown"]
    feedback_category: str = "no_feedback"
    rep_feedback: str = ""
    alert_id: str = ""


class OutcomeSubmissionResponse(BaseModel):
    """Stable response after an outcome submission is accepted."""

    status: str = Field(min_length=1)
    message: str = Field(min_length=1)
    outcome_id: str | None = None
