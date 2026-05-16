import unittest

import pandas as pd

from backend.engines.component_scorers import (
    load_priority_weight_config,
    score_all_components,
)
from backend.engines.priority_engine import (
    build_priority_score_view,
    score_priority_row,
)
from backend.engines.scoring_engine import (
    PriorityScoringError,
    calculate_priority_score,
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


class Build03PriorityScoringTest(unittest.TestCase):
    def test_calculate_priority_score_applies_component_weights_and_penalty(self):
        config = load_priority_weight_config()
        component_scores = score_all_components(FEATURE_ROW, config)

        priority_score = calculate_priority_score(component_scores, config)

        self.assertEqual(priority_score.core_urgency_score, 65.575)
        self.assertEqual(priority_score.travel_penalty, 2.1)
        self.assertEqual(priority_score.priority_score, 63.475)
        self.assertEqual(priority_score.applied_weights["travel_cost"], -0.05)
        self.assertEqual(
            priority_score.component_scores,
            {
                "agronomic_urgency": 75.5,
                "sales_opportunity": 62.5,
                "inventory_need": 75.5,
                "relationship_need": 57.0,
                "competitive_pressure": 65.0,
                "travel_cost": 42.0,
            },
        )

    def test_priority_trace_preserves_component_breakdown(self):
        priority_score = score_priority_row(FEATURE_ROW)
        trace = priority_score.to_trace()

        self.assertEqual(trace["priority_score"], 63.475)
        self.assertEqual(trace["core_urgency_score"], 65.575)
        self.assertEqual(trace["travel_penalty"], 2.1)
        self.assertIn("agronomic_urgency", trace["component_breakdown"])
        self.assertEqual(
            trace["component_breakdown"]["travel_cost"]["signal_breakdown"],
            {"travel_cost_score": 42.0},
        )

    def test_build_priority_score_view_preserves_context_and_scores(self):
        feature_view = pd.DataFrame(
            [
                {**FEATURE_ROW, "entity_id": "RET002"},
                {**FEATURE_ROW, "entity_id": "RET001", "travel_cost_score": 10},
            ]
        )

        output = build_priority_score_view(feature_view)

        self.assertEqual(output["entity_id"].tolist(), ["RET001", "RET002"])
        self.assertEqual(output.loc[0, "travel_penalty"], 0.5)
        self.assertEqual(output.loc[0, "priority_score"], 65.075)
        self.assertEqual(output.loc[1, "priority_score"], 63.475)
        self.assertIn("priority_trace", output.columns)
        self.assertIn("component_breakdown", output.columns)

    def test_missing_component_score_fails_explicitly(self):
        component_scores = score_all_components(FEATURE_ROW)
        component_scores.pop("travel_cost")

        with self.assertRaisesRegex(PriorityScoringError, "travel_cost"):
            calculate_priority_score(component_scores)

    def test_final_score_is_clamped_to_contract_range(self):
        config = load_priority_weight_config()
        component_scores = score_all_components(FEATURE_ROW, config)
        overridden_config = {
            **config,
            "component_weights": {
                **config["component_weights"],
                "travel_cost": -2.0,
            },
        }

        priority_score = calculate_priority_score(component_scores, overridden_config)

        self.assertEqual(priority_score.priority_score, 0)


if __name__ == "__main__":
    unittest.main()
