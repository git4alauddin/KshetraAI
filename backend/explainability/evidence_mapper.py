"""Evidence mapping for Build 06 explainability.

This module maps existing priority, recommendation, and anomaly outputs into
structured evidence bundles. It does not generate human-readable explanation
text, calculate scores, create recommendations, detect anomalies, call APIs, or
render frontend content.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import pandas as pd

from backend.explainability.explanation_registry import (
    ExplanationTemplateSpec,
    default_template_for_type,
    load_explanation_template_config,
)


EVIDENCE_OUTPUT_COLUMNS = [
    "entity_id",
    "explanation_type",
    "source_output_type",
    "source_output_id",
    "evidence_items",
    "confidence_level",
    "source_trace_ids",
    "template_id",
    "evidence_trace",
]


class EvidenceMappingError(ValueError):
    """Raised when evidence cannot be mapped safely."""


@dataclass(frozen=True)
class EvidenceItem:
    """One structured evidence item used by explainability."""

    evidence_id: str
    source_field: str
    value: Any
    evidence_type: str

    def to_row(self) -> dict[str, Any]:
        """Return stable evidence item metadata."""

        return {
            "evidence_id": self.evidence_id,
            "source_field": self.source_field,
            "value": self.value,
            "evidence_type": self.evidence_type,
        }


@dataclass(frozen=True)
class EvidenceBundle:
    """Evidence mapped from one upstream intelligence output."""

    entity_id: str
    explanation_type: str
    source_output_type: str
    source_output_id: str
    evidence_items: tuple[EvidenceItem, ...]
    confidence_level: str
    source_trace_ids: tuple[str, ...]
    template_id: str
    template: ExplanationTemplateSpec

    def to_row(self) -> dict[str, Any]:
        """Return a stable evidence bundle row."""

        return {
            "entity_id": self.entity_id,
            "explanation_type": self.explanation_type,
            "source_output_type": self.source_output_type,
            "source_output_id": self.source_output_id,
            "evidence_items": [item.to_row() for item in self.evidence_items],
            "confidence_level": self.confidence_level,
            "source_trace_ids": list(self.source_trace_ids),
            "template_id": self.template_id,
            "evidence_trace": self.to_trace(),
        }

    def to_trace(self) -> dict[str, Any]:
        """Return deterministic evidence trace metadata."""

        return {
            "entity_id": self.entity_id,
            "explanation_type": self.explanation_type,
            "source_output_type": self.source_output_type,
            "source_output_id": self.source_output_id,
            "evidence_count": len(self.evidence_items),
            "source_trace_ids": list(self.source_trace_ids),
            "template_id": self.template_id,
            "confidence_rule_id": self.template.confidence_rule_id,
            "required_evidence_fields": list(self.template.required_evidence_fields),
        }


def map_priority_evidence(
    priority_row: Mapping[str, Any],
    config: Mapping[str, Any] | None = None,
) -> EvidenceBundle:
    """Map a ranked priority row into explainability evidence."""

    template_config = config or load_explanation_template_config()
    template = default_template_for_type("priority", template_config)
    _require_fields(
        priority_row,
        ("entity_id", "priority_score", "priority_level", "priority_trace"),
        "priority",
    )

    priority_trace = _mapping_value(priority_row["priority_trace"], "priority_trace")
    component_scores = _mapping_value(
        priority_row.get("component_scores") or priority_trace.get("component_scores"),
        "component_scores",
    )
    top_components = _top_numeric_items(component_scores)
    if not top_components:
        raise EvidenceMappingError("Priority evidence requires component scores.")

    evidence_items = [
        EvidenceItem(
            evidence_id=f"priority:{component_name}",
            source_field=component_name,
            value=score,
            evidence_type="priority_component",
        )
        for component_name, score in top_components
    ]
    evidence_items.append(
        EvidenceItem(
            evidence_id="priority:priority_score",
            source_field="priority_score",
            value=_to_builtin_value(priority_row["priority_score"]),
            evidence_type="priority_score",
        )
    )

    return EvidenceBundle(
        entity_id=str(priority_row["entity_id"]),
        explanation_type="priority",
        source_output_type=template.source_output_type,
        source_output_id=f"PRIORITY_{_normalize_id(str(priority_row['entity_id']))}",
        evidence_items=tuple(evidence_items),
        confidence_level=str(priority_row.get("confidence_level", "Low")),
        source_trace_ids=("priority_trace", "classification_trace"),
        template_id=template.template_id,
        template=template,
    )


def map_recommendation_evidence(
    recommendation_row: Mapping[str, Any],
    config: Mapping[str, Any] | None = None,
) -> EvidenceBundle:
    """Map a recommendation row into explainability evidence."""

    template_config = config or load_explanation_template_config()
    template = default_template_for_type("recommendation", template_config)
    _require_fields(
        recommendation_row,
        (
            "entity_id",
            "matched_rule_id",
            "recommended_actions",
            "evidence_signals",
            "confidence_level",
            "recommendation_trace",
        ),
        "recommendation",
    )

    evidence_signals = _mapping_value(recommendation_row["evidence_signals"], "evidence_signals")
    if not evidence_signals:
        raise EvidenceMappingError("Recommendation evidence requires evidence_signals.")

    evidence_items = tuple(
        EvidenceItem(
            evidence_id=f"recommendation:{signal}",
            source_field=str(signal),
            value=_to_builtin_value(value),
            evidence_type="recommendation_signal",
        )
        for signal, value in sorted(evidence_signals.items())
    )

    return EvidenceBundle(
        entity_id=str(recommendation_row["entity_id"]),
        explanation_type="recommendation",
        source_output_type=template.source_output_type,
        source_output_id=str(recommendation_row["matched_rule_id"]),
        evidence_items=evidence_items,
        confidence_level=str(recommendation_row["confidence_level"]),
        source_trace_ids=("recommendation_trace",),
        template_id=template.template_id,
        template=template,
    )


def map_anomaly_evidence(
    alert_row: Mapping[str, Any],
    config: Mapping[str, Any] | None = None,
) -> EvidenceBundle:
    """Map an anomaly alert row into explainability evidence."""

    template_config = config or load_explanation_template_config()
    template = default_template_for_type("anomaly", template_config)
    _require_fields(
        alert_row,
        (
            "entity_id",
            "alert_id",
            "alert_type",
            "severity_level",
            "supporting_evidence",
            "confidence_level",
            "anomaly_trace",
        ),
        "anomaly",
    )

    supporting_evidence = alert_row["supporting_evidence"]
    if not isinstance(supporting_evidence, Sequence) or isinstance(supporting_evidence, str):
        raise EvidenceMappingError("Anomaly evidence requires supporting_evidence items.")
    if not supporting_evidence:
        raise EvidenceMappingError("Anomaly evidence requires supporting_evidence items.")

    evidence_items = tuple(
        _evidence_item_from_alert_item(item, index)
        for index, item in enumerate(supporting_evidence, start=1)
    )

    return EvidenceBundle(
        entity_id=str(alert_row["entity_id"]),
        explanation_type="anomaly",
        source_output_type=template.source_output_type,
        source_output_id=str(alert_row["alert_id"]),
        evidence_items=evidence_items,
        confidence_level=str(alert_row["confidence_level"]),
        source_trace_ids=("anomaly_trace",),
        template_id=template.template_id,
        template=template,
    )


def build_evidence_view(
    source_view: pd.DataFrame,
    explanation_type: str,
    config: Mapping[str, Any] | None = None,
) -> pd.DataFrame:
    """Build a stable evidence bundle view for one upstream output type."""

    if source_view.empty:
        return pd.DataFrame(columns=EVIDENCE_OUTPUT_COLUMNS)

    mapper = _mapper_for_type(explanation_type)
    rows = [
        mapper(row, config).to_row()
        for row in source_view.to_dict(orient="records")
    ]
    output = pd.DataFrame(rows, columns=EVIDENCE_OUTPUT_COLUMNS)
    return output.sort_values(
        ["entity_id", "explanation_type", "source_output_id"],
        kind="mergesort",
    ).reset_index(drop=True)


def _mapper_for_type(explanation_type: str):
    if explanation_type == "priority":
        return map_priority_evidence
    if explanation_type == "recommendation":
        return map_recommendation_evidence
    if explanation_type == "anomaly":
        return map_anomaly_evidence
    raise EvidenceMappingError(f"Unsupported evidence explanation_type: {explanation_type}")


def _evidence_item_from_alert_item(
    item: Any,
    index: int,
) -> EvidenceItem:
    if not isinstance(item, Mapping):
        raise EvidenceMappingError("Anomaly supporting_evidence items must be mappings.")
    signal = str(item.get("signal", f"evidence_{index}"))
    if not signal:
        signal = f"evidence_{index}"
    return EvidenceItem(
        evidence_id=f"anomaly:{signal}",
        source_field=signal,
        value=_to_builtin_value(item.get("value")),
        evidence_type="anomaly_signal",
    )


def _require_fields(
    source_row: Mapping[str, Any],
    required_fields: Sequence[str],
    explanation_type: str,
) -> None:
    missing_fields = [field for field in required_fields if field not in source_row]
    if missing_fields:
        raise EvidenceMappingError(
            f"{explanation_type} evidence row is missing required fields: "
            + ", ".join(missing_fields)
        )


def _mapping_value(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise EvidenceMappingError(f"Evidence field must be a mapping: {field}")
    return value


def _top_numeric_items(
    values: Mapping[str, Any],
    limit: int = 3,
) -> tuple[tuple[str, float], ...]:
    numeric_items: list[tuple[str, float]] = []
    for key, value in values.items():
        numeric_value = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
        if pd.isna(numeric_value):
            continue
        numeric_items.append((str(key), round(float(numeric_value), 4)))

    return tuple(
        sorted(
            numeric_items,
            key=lambda item: (-item[1], item[0]),
        )[:limit]
    )


def _normalize_id(value: str) -> str:
    return "".join(
        character if character.isalnum() else "_"
        for character in value.upper()
    ).strip("_")


def _to_builtin_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value
