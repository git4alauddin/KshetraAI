"""Recommendation API schemas for Build 08.

These models expose existing recommendation outputs only. They do not match
rules, choose actions, or generate recommendations.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class RecommendationResponse(BaseModel):
    """Entity-level contextual recommendation response."""

    entity_id: str = Field(min_length=1)
    risk_or_opportunity: str = ""
    recommended_actions: list[str] = Field(default_factory=list)
    recommended_product_category: str = ""
    confidence_level: str = Field(min_length=1)
