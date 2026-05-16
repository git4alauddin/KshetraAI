import unittest

import pandas as pd

from backend.anomaly.baseline_engine import build_baseline_feature_view
from backend.anomaly.deviation_detector import (
    build_deviation_view,
    detect_deviations_for_row,
)
from backend.anomaly.severity_classifier import (
    SeverityClassificationError,
    add_severity_classification,
    classify_deviation_severity,
)


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


class Build05SeverityClassifierTest(unittest.TestCase):
    def test_classify_deviation_severity_applies_detector_weights(self):
        baseline_view = build_baseline_feature_view(pd.DataFrame(ANOMALY_FEATURE_ROWS))
        high_row = baseline_view[baseline_view["entity_id"] == "RET002"].iloc[0].to_dict()
        inventory_deviation = [
            record
            for record in detect_deviations_for_row(high_row)
            if record.detector_id == "INVENTORY_STOCKOUT_RISK"
        ][0]

        classification = classify_deviation_severity(inventory_deviation)

        self.assertEqual(classification.severity_score, 74.5)
        self.assertEqual(classification.severity_level, "High")
        self.assertEqual(classification.severity_level_key, "high")
        self.assertEqual(classification.severity_rank, 3)
        self.assertEqual(
            classification.applied_weights,
            {
                "current_signal_weight": 0.70,
                "deviation_weight": 0.30,
            },
        )

    def test_classify_deviation_severity_supports_critical_level(self):
        baseline_view = build_baseline_feature_view(pd.DataFrame(ANOMALY_FEATURE_ROWS))
        critical_row = baseline_view[baseline_view["entity_id"] == "RET003"].iloc[0].to_dict()
        ndvi_deviation = [
            record
            for record in detect_deviations_for_row(critical_row)
            if record.detector_id == "AGRONOMIC_CROP_STRESS_ESCALATION"
        ][0]

        classification = classify_deviation_severity(ndvi_deviation)

        self.assertEqual(classification.severity_score, 81.0)
        self.assertEqual(classification.severity_level, "Critical")
        self.assertEqual(classification.severity_rank, 4)

    def test_add_severity_classification_adds_trace_columns_and_sorts(self):
        baseline_view = build_baseline_feature_view(pd.DataFrame(ANOMALY_FEATURE_ROWS))
        deviation_view = build_deviation_view(baseline_view)

        output = add_severity_classification(deviation_view)

        self.assertIn("severity_score", output.columns)
        self.assertIn("severity_level", output.columns)
        self.assertIn("severity_trace", output.columns)
        self.assertEqual(output.loc[0, "entity_id"], "RET002")
        self.assertGreaterEqual(output.loc[0, "severity_rank"], output.loc[1, "severity_rank"])
        self.assertEqual(
            output.loc[0, "severity_trace"]["detector_id"],
            output.loc[0, "detector_id"],
        )
        self.assertNotIn("alert_id", output.columns)

    def test_missing_deviation_field_fails_explicitly(self):
        with self.assertRaisesRegex(SeverityClassificationError, "current_value"):
            classify_deviation_severity(
                {
                    "entity_id": "RET001",
                    "detector_id": "INVENTORY_STOCKOUT_RISK",
                    "deviation_value": 30,
                }
            )

    def test_unknown_detector_fails_explicitly(self):
        with self.assertRaisesRegex(SeverityClassificationError, "UNKNOWN_DETECTOR"):
            classify_deviation_severity(
                {
                    "entity_id": "RET001",
                    "detector_id": "UNKNOWN_DETECTOR",
                    "current_value": 80,
                    "deviation_value": 30,
                }
            )

    def test_non_numeric_severity_field_fails_explicitly(self):
        with self.assertRaisesRegex(SeverityClassificationError, "current_value"):
            classify_deviation_severity(
                {
                    "entity_id": "RET001",
                    "detector_id": "INVENTORY_STOCKOUT_RISK",
                    "current_value": "high",
                    "deviation_value": 30,
                }
            )


if __name__ == "__main__":
    unittest.main()
