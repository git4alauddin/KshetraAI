"""Reasoning formatting for Build 06 explainability.

This module formats generated explanation records into stable, downstream-ready
reasoning payloads. It does not implement API routes, frontend rendering,
priority scoring, recommendation generation, anomaly detection, or uncontrolled
LLM generation.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import pandas as pd


REASONING_OUTPUT_COLUMNS = [
    "entity_id",
    "explanation_type",
    "source_output_type",
    "source_output_id",
    "safe_explanation_text",
    "evidence_summary",
    "confidence_level",
    "confidence_reasoning",
    "evidence_items",
    "source_trace_ids",
    "template_used",
    "safety_validation_status",
    "reasoning_payload",
]


class ReasoningFormattingError(ValueError):
    """Raised when explanation reasoning cannot be formatted safely."""


@dataclass(frozen=True)
class FormattedReasoning:
    """Downstream-ready reasoning payload for one generated explanation."""

    entity_id: str
    explanation_type: str
    source_output_type: str
    source_output_id: str
    safe_explanation_text: str
    evidence_summary: str
    confidence_level: str
    confidence_reasoning: str
    evidence_items: list[dict[str, Any]]
    source_trace_ids: list[str]
    template_used: str
    safety_validation_status: str

    def to_row(self) -> dict[str, Any]:
        """Return a stable formatted reasoning row."""

        return {
            "entity_id": self.entity_id,
            "explanation_type": self.explanation_type,
            "source_output_type": self.source_output_type,
            "source_output_id": self.source_output_id,
            "safe_explanation_text": self.safe_explanation_text,
            "evidence_summary": self.evidence_summary,
            "confidence_level": self.confidence_level,
            "confidence_reasoning": self.confidence_reasoning,
            "evidence_items": self.evidence_items,
            "source_trace_ids": self.source_trace_ids,
            "template_used": self.template_used,
            "safety_validation_status": self.safety_validation_status,
            "reasoning_payload": self.to_payload(),
        }

    def to_payload(self) -> dict[str, Any]:
        """Return structured reasoning payload for later API/frontend layers."""

        return {
            "summary": self.safe_explanation_text,
            "evidence": self.evidence_items,
            "evidence_summary": self.evidence_summary,
            "confidence": {
                "level": self.confidence_level,
                "reasoning": self.confidence_reasoning,
            },
            "traceability": {
                "source_output_type": self.source_output_type,
                "source_output_id": self.source_output_id,
                "source_trace_ids": self.source_trace_ids,
                "template_used": self.template_used,
            },
            "safety": {
                "validation_status": self.safety_validation_status,
            },
        }


def format_reasoning_record(explanation_row: Mapping[str, Any]) -> FormattedReasoning:
    """Format one generated explanation row for downstream consumption."""

    _validate_explanation_row(explanation_row)
    evidence_items = _evidence_items(explanation_row)
    source_trace_ids = _source_trace_ids(explanation_row)
    safe_text = str(explanation_row["summary_text"]).strip()
    if not safe_text:
        raise ReasoningFormattingError("Explanation summary_text cannot be blank.")

    safety_status = str(explanation_row["safety_validation_status"])
    if safety_status != "Safe":
        raise ReasoningFormattingError(
            f"Only Safe explanations can be formatted; found {safety_status}."
        )

    return FormattedReasoning(
        entity_id=str(explanation_row["entity_id"]),
        explanation_type=str(explanation_row["explanation_type"]),
        source_output_type=str(explanation_row["source_output_type"]),
        source_output_id=str(explanation_row["source_output_id"]),
        safe_explanation_text=safe_text,
        evidence_summary=_summarize_evidence(evidence_items),
        confidence_level=str(explanation_row["confidence_level"]),
        confidence_reasoning=str(explanation_row["confidence_reasoning"]),
        evidence_items=evidence_items,
        source_trace_ids=source_trace_ids,
        template_used=str(explanation_row["template_used"]),
        safety_validation_status=safety_status,
    )


def build_reasoning_view(explanation_view: pd.DataFrame) -> pd.DataFrame:
    """Build stable formatted reasoning rows from generated explanations."""

    if explanation_view.empty:
        return pd.DataFrame(columns=REASONING_OUTPUT_COLUMNS)

    rows = [
        format_reasoning_record(row).to_row()
        for row in explanation_view.to_dict(orient="records")
    ]
    output = pd.DataFrame(rows, columns=REASONING_OUTPUT_COLUMNS)
    return output.sort_values(
        ["entity_id", "explanation_type", "source_output_id"],
        kind="mergesort",
    ).reset_index(drop=True)


def _validate_explanation_row(explanation_row: Mapping[str, Any]) -> None:
    required_fields = (
        "entity_id",
        "explanation_type",
        "source_output_type",
        "source_output_id",
        "summary_text",
        "evidence_items",
        "confidence_level",
        "confidence_reasoning",
        "source_trace_ids",
        "template_used",
        "safety_validation_status",
    )
    missing_fields = [field for field in required_fields if field not in explanation_row]
    if missing_fields:
        raise ReasoningFormattingError(
            "Explanation row is missing reasoning fields: "
            + ", ".join(missing_fields)
        )


def _evidence_items(explanation_row: Mapping[str, Any]) -> list[dict[str, Any]]:
    evidence_items = explanation_row["evidence_items"]
    if not isinstance(evidence_items, list) or not evidence_items:
        raise ReasoningFormattingError("Reasoning formatting requires evidence_items.")

    invalid_items = [
        item for item in evidence_items
        if not isinstance(item, Mapping) or "source_field" not in item
    ]
    if invalid_items:
        raise ReasoningFormattingError("Evidence items must include source_field metadata.")
    return [dict(item) for item in evidence_items]


def _source_trace_ids(explanation_row: Mapping[str, Any]) -> list[str]:
    source_trace_ids = explanation_row["source_trace_ids"]
    if not isinstance(source_trace_ids, list) or not source_trace_ids:
        raise ReasoningFormattingError("Reasoning formatting requires source_trace_ids.")
    return [str(trace_id) for trace_id in source_trace_ids]


def _summarize_evidence(
    evidence_items: Sequence[Mapping[str, Any]],
    limit: int = 3,
) -> str:
    summaries = [
        _format_evidence_item(item)
        for item in evidence_items[:limit]
    ]
    return "; ".join(summaries)


def _format_evidence_item(item: Mapping[str, Any]) -> str:
    source_field = str(item["source_field"]).replace("_", " ")
    value = item.get("value")
    if _is_missing(value):
        return source_field
    return f"{source_field}: {value}"


def _is_missing(value: Any) -> bool:
    if isinstance(value, (list, tuple, dict)):
        return False
    return bool(pd.isna(value))
