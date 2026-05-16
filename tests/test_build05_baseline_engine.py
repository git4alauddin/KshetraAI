import unittest

import pandas as pd

from backend.anomaly.baseline_engine import (
    BASELINE_GENERATED_AT,
    BaselineEngineError,
    build_baseline_feature_view,
    build_baseline_long_view,
    list_baseline_specs,
    load_baseline_config,
)


ANOMALY_FEATURE_ROWS = [
    {
        "entity_id": "RET002",
        "territory_id": "T01",
        "weather_risk_score": 70,
        "pest_disease_risk_score": 80,
        "ndvi_stress_score": 75,
        "sales_opportunity_score": 82,
        "inventory_need_score": 88,
        "stockout_risk_score": 84,
        "competitive_pressure_score": 66,
        "historical_sales_score": 40,
        "relationship_need_score": 76,
    },
    {
        "entity_id": "RET001",
        "territory_id": "T01",
        "weather_risk_score": 20,
        "pest_disease_risk_score": 25,
        "ndvi_stress_score": 30,
        "sales_opportunity_score": 35,
        "inventory_need_score": 40,
        "stockout_risk_score": 30,
        "competitive_pressure_score": 20,
        "historical_sales_score": 70,
        "relationship_need_score": 50,
    },
]


class Build05BaselineEngineTest(unittest.TestCase):
    def test_list_baseline_specs_returns_stable_configured_specs(self):
        specs = list_baseline_specs()

        self.assertEqual(len(specs), 9)
        self.assertEqual(
            tuple(spec.baseline_signal for spec in specs[:3]),
            (
                "ndvi_stress_baseline_score",
                "pest_disease_risk_baseline_score",
                "weather_risk_baseline_score",
            ),
        )
        self.assertEqual(specs[0].source_signal, "ndvi_stress_score")
        self.assertEqual(specs[0].default_value, 35)
        self.assertEqual(specs[0].baseline_source, "configured_static_baseline")

    def test_build_baseline_feature_view_adds_baselines_and_trace(self):
        anomaly_feature_view = pd.DataFrame(ANOMALY_FEATURE_ROWS)

        output = build_baseline_feature_view(anomaly_feature_view)

        self.assertEqual(output["entity_id"].tolist(), ["RET001", "RET002"])
        self.assertEqual(output.loc[0, "ndvi_stress_baseline_score"], 35)
        self.assertEqual(output.loc[0, "inventory_need_baseline_score"], 45)
        self.assertIn("baseline_trace", output.columns)
        self.assertEqual(
            output.loc[0, "baseline_trace"]["ndvi_stress_baseline_score"]["source_signal"],
            "ndvi_stress_score",
        )

    def test_build_baseline_long_view_uses_contract_schema(self):
        anomaly_feature_view = pd.DataFrame(ANOMALY_FEATURE_ROWS)
        config = load_baseline_config()

        output = build_baseline_long_view(anomaly_feature_view, config)

        self.assertEqual(output.columns.tolist(), config["baseline_output_schema"])
        self.assertEqual(len(output), 18)
        self.assertEqual(output.loc[0, "entity_id"], "RET001")
        self.assertEqual(output.loc[0, "baseline_generated_at"], BASELINE_GENERATED_AT)
        self.assertEqual(
            output[output["baseline_signal"] == "inventory_need_baseline_score"]
            ["baseline_value"]
            .unique()
            .tolist(),
            [45.0],
        )

    def test_missing_source_signal_fails_explicitly(self):
        anomaly_feature_view = pd.DataFrame(ANOMALY_FEATURE_ROWS).drop(columns=["ndvi_stress_score"])

        with self.assertRaisesRegex(BaselineEngineError, "ndvi_stress_score"):
            build_baseline_feature_view(anomaly_feature_view)

    def test_invalid_source_signal_range_fails_explicitly(self):
        anomaly_feature_view = pd.DataFrame(ANOMALY_FEATURE_ROWS)
        anomaly_feature_view.loc[0, "inventory_need_score"] = 101

        with self.assertRaisesRegex(BaselineEngineError, "inventory_need_score"):
            build_baseline_feature_view(anomaly_feature_view)

    def test_missing_join_key_fails_for_long_view(self):
        anomaly_feature_view = pd.DataFrame(ANOMALY_FEATURE_ROWS).drop(columns=["territory_id"])

        with self.assertRaisesRegex(BaselineEngineError, "territory_id"):
            build_baseline_long_view(anomaly_feature_view)


if __name__ == "__main__":
    unittest.main()
