import unittest

import pandas as pd

from backend.anomaly.alert_generator import (
    ALERT_OUTPUT_COLUMNS,
    TRACE_OUTPUT_COLUMNS,
    AlertGenerationError,
    build_alert_view,
    build_trace_log_view,
    generate_alert,
)
from backend.anomaly.anomaly_engine import build_anomaly_outputs
from backend.anomaly.baseline_engine import build_baseline_feature_view
from backend.anomaly.deviation_detector import build_deviation_view
from backend.anomaly.severity_classifier import add_severity_classification


ANOMALY_FEATURE_ROWS = [
    {
        "entity_id": "RET002",
        "territory_id": "T01",
        "weather_risk_score": 70,
        "pest_disease_risk_score": 80,
        "crop_stage_risk_score": 70,
        "ndvi_stress_score": 75,
        "sales_opportunity_score": 82,
        "seasonal_product_relevance": 78,
        "inventory_need_score": 88,
        "stockout_risk_score": 84,
        "sales_velocity_score": 82,
        "competitive_pressure_score": 66,
        "historical_sales_score": 40,
        "relationship_need_score": 76,
        "account_priority_score": 72,
    },
    {
        "entity_id": "RET003",
        "territory_id": "T02",
        "weather_risk_score": 90,
        "pest_disease_risk_score": 95,
        "crop_stage_risk_score": 90,
        "ndvi_stress_score": 95,
        "sales_opportunity_score": 95,
        "seasonal_product_relevance": 90,
        "inventory_need_score": 96,
        "stockout_risk_score": 95,
        "sales_velocity_score": 90,
        "competitive_pressure_score": 92,
        "historical_sales_score": 20,
        "relationship_need_score": 95,
        "account_priority_score": 90,
    },
]


class Build05AlertGenerationTest(unittest.TestCase):
    def test_generate_alert_creates_stable_id_and_trace(self):
        severity_view = _build_severity_view()
        inventory_row = severity_view[
            severity_view["detector_id"] == "INVENTORY_STOCKOUT_RISK"
        ].iloc[0].to_dict()

        alert = generate_alert(inventory_row, detected_at="2026-05-17")

        self.assertEqual(alert.alert_id, "ALERT_RET002_INVENTORY_STOCKOUT_RISK")
        self.assertEqual(alert.severity_level, "High")
        self.assertEqual(alert.confidence_level, "High")
        self.assertEqual(alert.detected_at, "2026-05-17")
        self.assertEqual(alert.anomaly_trace["triggered_rule"], "INVENTORY_STOCKOUT_RISK")
        self.assertEqual(alert.anomaly_trace["trend"]["trend_direction"], "above_baseline")
        self.assertIn(
            {"signal": "sales_velocity_score", "value": 82},
            alert.to_row()["supporting_evidence"],
        )

    def test_build_alert_view_uses_stable_schema_and_order(self):
        severity_view = _build_severity_view()

        alert_view = build_alert_view(severity_view)

        self.assertEqual(alert_view.columns.tolist(), ALERT_OUTPUT_COLUMNS)
        self.assertEqual(alert_view.loc[0, "entity_id"], "RET002")
        self.assertGreaterEqual(
            alert_view.loc[0, "severity_rank"],
            alert_view.loc[1, "severity_rank"],
        )
        self.assertTrue(alert_view["supporting_evidence"].map(bool).all())
        self.assertNotIn("priority_score", alert_view.columns)
        self.assertNotIn("recommended_actions", alert_view.columns)

    def test_build_trace_log_view_preserves_threshold_and_severity_metadata(self):
        severity_view = _build_severity_view()
        alert_view = build_alert_view(severity_view)

        trace_log = build_trace_log_view(alert_view)

        self.assertEqual(trace_log.columns.tolist(), TRACE_OUTPUT_COLUMNS)
        inventory_trace = trace_log[
            trace_log["detector_id"] == "INVENTORY_STOCKOUT_RISK"
        ].iloc[0]
        self.assertEqual(inventory_trace["threshold_used"], 15.0)
        self.assertEqual(inventory_trace["severity_score"], 74.5)
        self.assertEqual(inventory_trace["triggered_rule"], "INVENTORY_STOCKOUT_RISK")

    def test_build_anomaly_outputs_runs_end_to_end_deterministically(self):
        source_view = pd.DataFrame(ANOMALY_FEATURE_ROWS)

        first_output = build_anomaly_outputs(source_view, detected_at="2026-05-17")
        second_output = build_anomaly_outputs(source_view, detected_at="2026-05-17")

        pd.testing.assert_frame_equal(
            first_output.anomaly_alerts,
            second_output.anomaly_alerts,
        )
        pd.testing.assert_frame_equal(
            first_output.anomaly_trace_log,
            second_output.anomaly_trace_log,
        )
        self.assertEqual(
            set(first_output.to_mapping()),
            {
                "baseline_feature_view",
                "deviation_view",
                "severity_view",
                "anomaly_alerts",
                "anomaly_trace_log",
            },
        )

    def test_alert_generation_requires_supporting_evidence(self):
        severity_row = _build_severity_view().iloc[0].to_dict()
        severity_row["evidence_signals"] = {}

        with self.assertRaisesRegex(AlertGenerationError, "supporting evidence"):
            generate_alert(severity_row)

    def test_missing_alert_field_fails_explicitly(self):
        severity_row = _build_severity_view().iloc[0].to_dict()
        severity_row.pop("severity_level")

        with self.assertRaisesRegex(AlertGenerationError, "severity_level"):
            generate_alert(severity_row)


def _build_severity_view() -> pd.DataFrame:
    baseline_view = build_baseline_feature_view(pd.DataFrame(ANOMALY_FEATURE_ROWS))
    deviation_view = build_deviation_view(baseline_view)
    return add_severity_classification(deviation_view)


if __name__ == "__main__":
    unittest.main()
