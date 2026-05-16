"""Build 05 anomaly detection orchestration.

This module wires baseline preparation, deviation detection, severity
classification, alert generation, and trace logging. It does not implement
priority ranking, recommendations, explanations, APIs, frontend behavior, or
ML anomaly models.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from backend.anomaly.alert_generator import (
    DETERMINISTIC_DETECTED_AT,
    build_alert_view,
    build_trace_log_view,
)
from backend.anomaly.baseline_engine import build_baseline_feature_view
from backend.anomaly.deviation_detector import build_deviation_view
from backend.anomaly.severity_classifier import add_severity_classification


@dataclass(frozen=True)
class AnomalyDetectionOutputs:
    """Generated anomaly output views for downstream consumers."""

    baseline_feature_view: pd.DataFrame
    deviation_view: pd.DataFrame
    severity_view: pd.DataFrame
    anomaly_alerts: pd.DataFrame
    anomaly_trace_log: pd.DataFrame

    def to_mapping(self) -> dict[str, pd.DataFrame]:
        """Return deterministic named output views."""

        return {
            "baseline_feature_view": self.baseline_feature_view,
            "deviation_view": self.deviation_view,
            "severity_view": self.severity_view,
            "anomaly_alerts": self.anomaly_alerts,
            "anomaly_trace_log": self.anomaly_trace_log,
        }


def build_anomaly_outputs(
    anomaly_feature_view: pd.DataFrame,
    *,
    detected_at: str = DETERMINISTIC_DETECTED_AT,
) -> AnomalyDetectionOutputs:
    """Run the deterministic Build 05 anomaly detection flow."""

    baseline_feature_view = build_baseline_feature_view(anomaly_feature_view)
    deviation_view = build_deviation_view(baseline_feature_view)
    severity_view = add_severity_classification(deviation_view)
    anomaly_alerts = build_alert_view(severity_view, detected_at=detected_at)
    anomaly_trace_log = build_trace_log_view(anomaly_alerts)

    return AnomalyDetectionOutputs(
        baseline_feature_view=baseline_feature_view,
        deviation_view=deviation_view,
        severity_view=severity_view,
        anomaly_alerts=anomaly_alerts,
        anomaly_trace_log=anomaly_trace_log,
    )
