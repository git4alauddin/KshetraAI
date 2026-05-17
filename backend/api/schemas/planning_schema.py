"""Planning API schemas for Build 08.

These models define API transport contracts only. They do not calculate
priority scores, ranks, or visit plans.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class DailyPlanQuery(BaseModel):
    """Optional filters accepted by the daily plan endpoint."""

    rep_id: str | None = Field(default=None, min_length=1)
    territory_id: str | None = Field(default=None, min_length=1)
    date: str | None = Field(default=None, min_length=1)


class RankedEntityResponse(BaseModel):
    """One ranked entity row exposed through the planning API."""

    rank: int = Field(ge=1)
    entity_id: str = Field(min_length=1)
    entity_name: str = ""
    priority_score: float = Field(ge=0, le=100)
    priority_level: str = Field(min_length=1)
    main_reason: str = ""


class DailyPlanResponse(BaseModel):
    """Stable daily plan response payload."""

    rep_id: str | None = None
    territory_id: str | None = None
    date: str | None = None
    ranked_entities: list[RankedEntityResponse] = Field(default_factory=list)
