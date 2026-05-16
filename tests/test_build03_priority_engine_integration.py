import unittest

import pandas as pd

from backend.engines.priority_engine import build_ranked_priority_view


def feature_row(entity_id, *, pest_risk, inventory_need, sales_opportunity, travel_cost):
    return {
        "entity_id": entity_id,
        "territory_id": "T01",
        "entity_type": "retailer",
        "primary_crop": "cotton",
        "weather_risk_score": pest_risk,
        "pest_disease_risk_score": pest_risk,
        "crop_stage_risk_score": pest_risk,
        "ndvi_stress_score": pest_risk,
        "historical_sales_score": sales_opportunity,
        "seasonal_product_relevance": sales_opportunity,
        "purchase_history_score": sales_opportunity,
        "crop_acreage_score": sales_opportunity,
        "sales_opportunity_score": sales_opportunity,
        "stock_level_score": inventory_need,
        "sales_velocity_score": inventory_need,
        "stockout_risk_score": inventory_need,
        "inventory_need_score": inventory_need,
        "relationship_need_score": 50,
        "account_priority_score": 50,
        "campaign_engagement_score": 50,
        "competitive_pressure_score": 50,
        "travel_cost_score": travel_cost,
    }


class Build03PriorityEngineIntegrationTest(unittest.TestCase):
    def test_ranked_priority_view_runs_full_build03_flow(self):
        feature_view = pd.DataFrame(
            [
                feature_row(
                    "RET002",
                    pest_risk=95,
                    inventory_need=95,
                    sales_opportunity=95,
                    travel_cost=10,
                ),
                feature_row(
                    "RET001",
                    pest_risk=60,
                    inventory_need=60,
                    sales_opportunity=60,
                    travel_cost=10,
                ),
                feature_row(
                    "RET003",
                    pest_risk=30,
                    inventory_need=30,
                    sales_opportunity=30,
                    travel_cost=5,
                ),
            ]
        )

        ranked = build_ranked_priority_view(feature_view)

        self.assertEqual(ranked["rank"].tolist(), [1, 2, 3])
        self.assertEqual(ranked["entity_id"].tolist(), ["RET002", "RET001", "RET003"])
        self.assertEqual(ranked["priority_level"].tolist(), ["Critical", "Medium", "Low"])
        self.assertEqual(ranked.loc[0, "priority_score"], 80.75)
        self.assertEqual(ranked.loc[1, "priority_score"], 54.5)
        self.assertEqual(ranked.loc[2, "priority_score"], 32.25)
        self.assertIn("priority_trace", ranked.columns)
        self.assertIn("classification_trace", ranked.columns)
        self.assertIn("component_breakdown", ranked.columns)

    def test_full_flow_uses_deterministic_tie_breakers(self):
        feature_view = pd.DataFrame(
            [
                feature_row(
                    "RET002",
                    pest_risk=70,
                    inventory_need=60,
                    sales_opportunity=60,
                    travel_cost=20,
                ),
                feature_row(
                    "RET001",
                    pest_risk=70,
                    inventory_need=60,
                    sales_opportunity=60,
                    travel_cost=20,
                ),
            ]
        )

        ranked = build_ranked_priority_view(feature_view)

        self.assertEqual(ranked["entity_id"].tolist(), ["RET001", "RET002"])
        self.assertEqual(ranked["rank"].tolist(), [1, 2])


if __name__ == "__main__":
    unittest.main()
