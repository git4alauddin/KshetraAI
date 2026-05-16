import unittest

import pandas as pd

from backend.engines.action_selector import ActionSelectionError, select_actions
from backend.engines.advisory_engine import (
    AdvisorySelectionError,
    build_advisory_bundle,
    build_advisory_view,
)
from backend.engines.recommendation_engine import (
    NO_MATCH_ACTION,
    NO_MATCH_RULE_ID,
    build_recommendation_view,
)


FULL_CONTEXT_ROW = {
    "entity_id": "RET001",
    "territory_id": "T01",
    "entity_type": "retailer",
    "primary_crop": "cotton",
    "priority_score": 82.5,
    "priority_level": "Critical",
    "weather_risk_score": 80,
    "pest_disease_risk_score": 90,
    "crop_stage_risk_score": 80,
    "ndvi_stress_score": 70,
    "inventory_need_score": 85,
    "stockout_risk_score": 80,
    "sales_velocity_score": 75,
    "stock_level_score": 70,
    "sales_opportunity_score": 85,
    "seasonal_product_relevance": 80,
    "historical_sales_score": 70,
    "purchase_history_score": 70,
    "relationship_need_score": 80,
    "account_priority_score": 70,
    "campaign_engagement_score": 75,
    "competitive_pressure_score": 80,
}


def low_context_row(entity_id="RET002"):
    return {
        **FULL_CONTEXT_ROW,
        "entity_id": entity_id,
        "weather_risk_score": 10,
        "pest_disease_risk_score": 10,
        "crop_stage_risk_score": 10,
        "ndvi_stress_score": 10,
        "inventory_need_score": 10,
        "stockout_risk_score": 10,
        "sales_velocity_score": 10,
        "stock_level_score": 10,
        "sales_opportunity_score": 10,
        "seasonal_product_relevance": 10,
        "historical_sales_score": 10,
        "purchase_history_score": 10,
        "relationship_need_score": 10,
        "account_priority_score": 10,
        "campaign_engagement_score": 10,
        "competitive_pressure_score": 10,
    }


class Build04AdvisoryActionSelectionTest(unittest.TestCase):
    def test_select_actions_normalizes_and_deduplicates_actions(self):
        recommendations = [
            {
                "entity_id": "RET001",
                "matched_rule_id": "RULE_ONE",
                "rule_type": "inventory",
                "recommended_actions": ["review_current_stock_position", "plan_inventory_follow_up"],
                "recommended_product_category": "Relevant Seasonal SKU",
                "confidence_level": "High",
            },
            {
                "entity_id": "RET001",
                "matched_rule_id": "RULE_TWO",
                "rule_type": "inventory",
                "recommended_actions": ["review_current_stock_position", "check_reorder_timing"],
                "recommended_product_category": "Relevant Seasonal SKU",
                "confidence_level": "Medium",
            },
        ]

        actions = select_actions(recommendations)

        self.assertEqual(
            tuple(action.action_id for action in actions),
            (
                "review_current_stock_position",
                "plan_inventory_follow_up",
                "check_reorder_timing",
            ),
        )
        self.assertEqual(actions[0].action_category, "inventory_follow_up")

    def test_select_actions_rejects_unsupported_action_shape(self):
        recommendation = {
            "entity_id": "RET001",
            "matched_rule_id": "RULE_ONE",
            "rule_type": "inventory",
            "recommended_actions": ["Review Stock"],
            "recommended_product_category": "Relevant Seasonal SKU",
            "confidence_level": "High",
        }

        with self.assertRaisesRegex(ActionSelectionError, "lower snake-case"):
            select_actions([recommendation])

    def test_build_advisory_bundle_aggregates_structured_recommendations(self):
        recommendation_view = build_recommendation_view(pd.DataFrame([FULL_CONTEXT_ROW]))

        bundle = build_advisory_bundle(recommendation_view.to_dict(orient="records"))

        self.assertEqual(bundle.entity_id, "RET001")
        self.assertEqual(bundle.confidence_level, "High")
        self.assertEqual(
            bundle.matched_rule_ids,
            (
                "AGRONOMIC_PEST_DISEASE_RISK_HIGH",
                "COMPETITOR_PRESSURE_RESPONSE_HIGH",
                "INVENTORY_REPLENISHMENT_NEED_HIGH",
            ),
        )
        self.assertIn("inspect_crop_symptoms", bundle.advisory_actions)
        self.assertIn("agronomic_advisory", bundle.action_categories)
        self.assertIn("Crop Protection", bundle.recommended_product_categories)
        self.assertIn("advisory_trace", bundle.to_row())
        self.assertNotIn("explanation", bundle.to_trace())

    def test_no_match_recommendation_builds_low_confidence_bundle(self):
        recommendation_view = build_recommendation_view(pd.DataFrame([low_context_row()]))

        bundle = build_advisory_bundle(recommendation_view.to_dict(orient="records"))

        self.assertEqual(bundle.entity_id, "RET002")
        self.assertEqual(bundle.confidence_level, "Low")
        self.assertEqual(bundle.matched_rule_ids, ())
        self.assertEqual(bundle.advisory_actions, (NO_MATCH_ACTION,))
        self.assertEqual(bundle.action_categories, ("no_recommendation",))
        self.assertEqual(recommendation_view.loc[0, "matched_rule_id"], NO_MATCH_RULE_ID)

    def test_build_advisory_view_preserves_context_and_one_row_per_entity(self):
        recommendation_view = build_recommendation_view(
            pd.DataFrame([FULL_CONTEXT_ROW, low_context_row()])
        )

        advisory_view = build_advisory_view(recommendation_view)

        self.assertEqual(advisory_view["entity_id"].tolist(), ["RET001", "RET002"])
        self.assertEqual(advisory_view.loc[0, "priority_level"], "Critical")
        self.assertEqual(advisory_view.loc[0, "confidence_level"], "High")
        self.assertEqual(advisory_view.loc[1, "confidence_level"], "Low")
        self.assertIn("advisory_actions", advisory_view.columns)
        self.assertIn("advisory_trace", advisory_view.columns)

    def test_mixed_entity_bundle_fails_explicitly(self):
        recommendations = [
            {
                "entity_id": "RET001",
                "matched_rule_id": "RULE_ONE",
                "risk_or_opportunity": "High inventory replenishment need",
                "rule_type": "inventory",
                "recommended_actions": ["review_current_stock_position"],
                "recommended_product_category": "Relevant Seasonal SKU",
                "confidence_level": "High",
            },
            {
                "entity_id": "RET002",
                "matched_rule_id": "RULE_TWO",
                "risk_or_opportunity": "Relationship follow-up need",
                "rule_type": "relationship",
                "recommended_actions": ["schedule_relationship_follow_up"],
                "recommended_product_category": "None",
                "confidence_level": "Medium",
            },
        ]

        with self.assertRaisesRegex(AdvisorySelectionError, "one entity_id"):
            build_advisory_bundle(recommendations)


if __name__ == "__main__":
    unittest.main()
