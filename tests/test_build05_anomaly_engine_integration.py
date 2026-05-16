import unittest

import pandas as pd

from backend.anomaly.alert_generator import ALERT_OUTPUT_COLUMNS, TRACE_OUTPUT_COLUMNS
from backend.anomaly.anomaly_engine import build_anomaly_outputs


QUIET_ANOMALY_FEATURE_ROWS = [
    {
        "entity_id": "RET999",
        "territory_id": "T09",
        "weather_risk_score": 20,
        "pest_disease_risk_score": 20,
        "crop_stage_risk_score": 20,
        "ndvi_stress_score": 25,
        "sales_opportunity_score": 30,
        "seasonal_product_relevance": 25,
        "inventory_need_score": 30,
        "stockout_risk_score": 30,
        "sales_velocity_score": 25,
        "competitive_pressure_score": 20,
        "historical_sales_score": 70,
        "relationship_need_score": 30,
        "account_priority_score": 30,
    },
]


HIGH_SIGNAL_ANOMALY_FEATURE_ROWS = [
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


class Build05AnomalyEngineIntegrationTest(unittest.TestCase):
    def test_quiet_input_produces_no_alerts_or_trace_rows(self):
        outputs = build_anomaly_outputs(
            pd.DataFrame(QUIET_ANOMALY_FEATURE_ROWS),
            detected_at="2026-05-17",
        )

        self.assertTrue(outputs.deviation_view.empty)
        self.assertTrue(outputs.severity_view.empty)
        self.assertTrue(outputs.anomaly_alerts.empty)
        self.assertTrue(outputs.anomaly_trace_log.empty)
        self.assertEqual(outputs.anomaly_alerts.columns.tolist(), ALERT_OUTPUT_COLUMNS)
        self.assertEqual(outputs.anomaly_trace_log.columns.tolist(), TRACE_OUTPUT_COLUMNS)

    def test_full_engine_covers_configured_alert_categories_and_preserves_traces(self):
        outputs = build_anomaly_outputs(
            pd.DataFrame(HIGH_SIGNAL_ANOMALY_FEATURE_ROWS),
            detected_at="2026-05-17",
        )

        self.assertEqual(len(outputs.anomaly_alerts), 7)
        self.assertEqual(
            set(outputs.anomaly_alerts["category"]),
            {
                "agronomic_anomaly",
                "sales_opportunity",
                "sales_risk",
                "inventory_risk",
                "competitive_event",
                "operational_gap",
            },
        )
        self.assertEqual(len(outputs.anomaly_trace_log), len(outputs.anomaly_alerts))
        self.assertTrue(outputs.anomaly_alerts["supporting_evidence"].map(bool).all())
        self.assertTrue(outputs.anomaly_alerts["anomaly_trace"].map(bool).all())
        self.assertEqual(
            outputs.anomaly_alerts["detected_at"].unique().tolist(),
            ["2026-05-17"],
        )
        self.assertNotIn("priority_score", outputs.anomaly_alerts.columns)
        self.assertNotIn("recommended_actions", outputs.anomaly_alerts.columns)

    def test_trace_log_matches_generated_alert_ids(self):
        outputs = build_anomaly_outputs(
            pd.DataFrame(HIGH_SIGNAL_ANOMALY_FEATURE_ROWS),
            detected_at="2026-05-17",
        )

        self.assertEqual(
            sorted(outputs.anomaly_alerts["alert_id"].tolist()),
            sorted(outputs.anomaly_trace_log["alert_id"].tolist()),
        )
        self.assertEqual(
            outputs.anomaly_trace_log[
                outputs.anomaly_trace_log["detector_id"] == "SALES_DECLINE_RISK"
            ]["current_signal"].iloc[0],
            "historical_sales_score",
        )


if __name__ == "__main__":
    unittest.main()
