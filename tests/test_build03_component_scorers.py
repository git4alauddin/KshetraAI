import unittest

import pandas as pd

from backend.engines.component_scorers import (
    ComponentScoringError,
    build_component_score_view,
    component_scores_as_dict,
    load_priority_weight_config,
    score_all_components,
    score_component,
)


FEATURE_ROW = {
    "entity_id": "RET002",
    "territory_id": "T01",
    "entity_type": "retailer",
    "primary_crop": "cotton",
    "weather_risk_score": 70,
    "pest_disease_risk_score": 90,
    "crop_stage_risk_score": 80,
    "ndvi_stress_score": 50,
    "historical_sales_score": 60,
    "seasonal_product_relevance": 80,
    "purchase_history_score": 40,
    "crop_acreage_score": 50,
    "sales_opportunity_score": 70,
    "stock_level_score": 80,
    "sales_velocity_score": 60,
    "stockout_risk_score": 90,
    "inventory_need_score": 70,
    "relationship_need_score": 55,
    "account_priority_score": 75,
    "campaign_engagement_score": 35,
    "competitive_pressure_score": 65,
    "travel_cost_score": 42,
}


class Build03ComponentScorersTest(unittest.TestCase):
    def test_score_component_applies_signal_weights_and_trace(self):
        config = load_priority_weight_config()

        score = score_component(FEATURE_ROW, "agronomic_urgency", config)

        self.assertEqual(score.component_name, "agronomic_urgency")
        self.assertEqual(score.score, 75.5)
        self.assertEqual(
            score.signal_breakdown,
            {
                "pest_disease_risk_score": 90.0,
                "crop_stage_risk_score": 80.0,
                "weather_risk_score": 70.0,
                "ndvi_stress_score": 50.0,
            },
        )
        self.assertEqual(
            score.applied_weights,
            {
                "pest_disease_risk_score": 0.35,
                "crop_stage_risk_score": 0.25,
                "weather_risk_score": 0.20,
                "ndvi_stress_score": 0.20,
            },
        )

    def test_score_all_components_returns_contract_components(self):
        scores = score_all_components(FEATURE_ROW)

        self.assertEqual(
            tuple(scores),
            (
                "agronomic_urgency",
                "sales_opportunity",
                "inventory_need",
                "relationship_need",
                "competitive_pressure",
                "travel_cost",
            ),
        )
        self.assertEqual(
            component_scores_as_dict(scores),
            {
                "agronomic_urgency": 75.5,
                "sales_opportunity": 62.5,
                "inventory_need": 75.5,
                "relationship_need": 57.0,
                "competitive_pressure": 65.0,
                "travel_cost": 42.0,
            },
        )

    def test_build_component_score_view_preserves_context_and_breakdown(self):
        feature_view = pd.DataFrame(
            [
                {**FEATURE_ROW, "entity_id": "RET002"},
                {**FEATURE_ROW, "entity_id": "RET001", "pest_disease_risk_score": 50},
            ]
        )

        output = build_component_score_view(feature_view)

        self.assertEqual(output["entity_id"].tolist(), ["RET001", "RET002"])
        self.assertEqual(
            output.columns.tolist(),
            [
                "entity_id",
                "territory_id",
                "entity_type",
                "primary_crop",
                "agronomic_urgency",
                "sales_opportunity",
                "inventory_need",
                "relationship_need",
                "competitive_pressure",
                "travel_cost",
                "component_breakdown",
            ],
        )
        self.assertIn("agronomic_urgency", output.loc[0, "component_breakdown"])
        self.assertEqual(
            output.loc[0, "component_breakdown"]["travel_cost"]["signal_breakdown"],
            {"travel_cost_score": 42.0},
        )

    def test_missing_required_signal_fails_explicitly(self):
        incomplete_row = dict(FEATURE_ROW)
        incomplete_row.pop("inventory_need_score")

        with self.assertRaisesRegex(ComponentScoringError, "inventory_need_score"):
            score_component(incomplete_row, "inventory_need")

    def test_out_of_range_signal_fails_explicitly(self):
        invalid_row = dict(FEATURE_ROW)
        invalid_row["travel_cost_score"] = 101

        with self.assertRaisesRegex(ComponentScoringError, "travel_cost_score"):
            score_component(invalid_row, "travel_cost")


if __name__ == "__main__":
    unittest.main()
