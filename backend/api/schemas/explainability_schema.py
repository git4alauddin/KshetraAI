"""Explainability API schemas for Build 08.

These models expose existing explanation outputs only. They do not generate
evidence, confidence, or reasoning text.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExplanationItemResponse(BaseModel):
    """One explanation item for a priority, recommendation, or alert."""

    explanation_type: str = Field(min_length=1)
    summary_text: str = Field(min_length=1)
    evidence_items: list[str] = Field(default_factory=list)
    confidence_level: str = Field(min_length=1)


class ExplanationResponse(BaseModel):
    """Stable entity explanation response payload."""

    entity_id: str = Field(min_length=1)
    explanations: list[ExplanationItemResponse] = Field(default_factory=list)
