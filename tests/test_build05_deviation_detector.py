import unittest

import pandas as pd

from backend.anomaly.baseline_engine import build_baseline_feature_view
from backend.anomaly.deviation_detector import (
    DeviationDetectionError,
    build_deviation_view,
    detect_deviations_for_row,
    list_detector_specs,
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
        "entity_id": "RET001",
        "territory_id": "T01",
        "weather_risk_score": 20,
        "pest_disease_risk_score": 25,
        "crop_stage_risk_score": 20,
        "ndvi_stress_score": 30,
        "sales_opportunity_score": 35,
        "seasonal_product_relevance": 30,
        "inventory_need_score": 40,
        "stockout_risk_score": 30,
        "sales_velocity_score": 30,
        "competitive_pressure_score": 20,
        "historical_sales_score": 70,
        "relationship_need_score": 50,
        "account_priority_score": 50,
    },
]


class Build05DeviationDetectorTest(unittest.TestCase):
    def test_list_detector_specs_is_stable(self):
        detectors = list_detector_specs()

        self.assertEqual(len(detectors), 7)
        self.assertEqual(
            tuple(detector.detector_id for detector in detectors[:3]),
            (
                "AGRONOMIC_CROP_STRESS_ESCALATION",
                "AGRONOMIC_PEST_WEATHER_RISK_ESCALATION",
                "COMPETITIVE_PRESSURE_ESCALATION",
            ),
        )
        self.assertEqual(detectors[0].current_signal, "ndvi_stress_score")
        self.assertEqual(detectors[0].baseline_signal, "ndvi_stress_baseline_score")

    def test_detect_deviations_for_row_returns_triggered_directional_deviations(self):
        baseline_view = build_baseline_feature_view(pd.DataFrame(ANOMALY_FEATURE_ROWS))
        high_row = baseline_view[baseline_view["entity_id"] == "RET002"].iloc[0].to_dict()

        records = detect_deviations_for_row(high_row)

        self.assertEqual(
            tuple(record.detector_id for record in records),
            (
                "AGRONOMIC_CROP_STRESS_ESCALATION",
                "AGRONOMIC_PEST_WEATHER_RISK_ESCALATION",
                "COMPETITIVE_PRESSURE_ESCALATION",
                "INVENTORY_STOCKOUT_RISK",
                "OPERATIONAL_COVERAGE_GAP",
                "SALES_DEMAND_SPIKE_OPPORTUNITY",
            ),
        )
        inventory_risk = [record for record in records if record.detector_id == "INVENTORY_STOCKOUT_RISK"][0]
        self.assertEqual(inventory_risk.current_value, 88)
        self.assertEqual(inventory_risk.baseline_value, 45)
        self.assertEqual(inventory_risk.deviation_value, 43)
        self.assertEqual(inventory_risk.deviation_direction, "increase")
        self.assertEqual(
            inventory_risk.evidence_signals,
            {
                "inventory_need_score": 88,
                "inventory_need_baseline_score": 45.0,
                "stockout_risk_score": 84,
                "sales_velocity_score": 82,
            },
        )

    def test_deviation_under_threshold_does_not_trigger(self):
        baseline_view = build_baseline_feature_view(pd.DataFrame(ANOMALY_FEATURE_ROWS))
        low_row = baseline_view[baseline_view["entity_id"] == "RET001"].iloc[0].to_dict()

        records = detect_deviations_for_row(low_row)

        self.assertEqual(records, ())

    def test_build_deviation_view_is_stable_and_traceable(self):
        baseline_view = build_baseline_feature_view(pd.DataFrame(ANOMALY_FEATURE_ROWS))

        output = build_deviation_view(baseline_view)

        self.assertEqual(output["entity_id"].unique().tolist(), ["RET002"])
        self.assertIn("deviation_trace", output.columns)
        self.assertEqual(output.loc[0, "detector_id"], "COMPETITIVE_PRESSURE_ESCALATION")
        self.assertEqual(output.loc[0, "deviation_trace"]["threshold_used"], 15.0)
        self.assertNotIn("severity_level", output.columns)
        self.assertNotIn("alert_id", output.columns)

    def test_missing_detector_field_fails_explicitly(self):
        baseline_view = build_baseline_feature_view(pd.DataFrame(ANOMALY_FEATURE_ROWS))
        row = baseline_view.iloc[0].to_dict()
        row.pop("sales_opportunity_baseline_score")

        with self.assertRaisesRegex(DeviationDetectionError, "sales_opportunity_baseline_score"):
            detect_deviations_for_row(row)

    def test_non_numeric_detector_field_fails_explicitly(self):
        baseline_view = build_baseline_feature_view(pd.DataFrame(ANOMALY_FEATURE_ROWS))
        row = baseline_view.iloc[0].to_dict()
        row["inventory_need_score"] = "high"

        with self.assertRaisesRegex(DeviationDetectionError, "inventory_need_score"):
            detect_deviations_for_row(row)


if __name__ == "__main__":
    unittest.main()
