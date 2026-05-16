import unittest

import pandas as pd

from backend.engines.contextual_decision_engine import (
    ContextualRuleMatchingError,
    build_rule_match_view,
    load_contextual_rules,
    match_contextual_rules,
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


class Build04ContextualRuleMatchingTest(unittest.TestCase):
    def test_load_contextual_rules_is_deterministic(self):
        rules = load_contextual_rules()

        self.assertEqual(len(rules), 10)
        self.assertEqual(
            tuple(rule.rule_id for rule in rules[:5]),
            (
                "AGRONOMIC_PEST_DISEASE_RISK_HIGH",
                "COMPETITOR_PRESSURE_RESPONSE_HIGH",
                "INVENTORY_REPLENISHMENT_NEED_HIGH",
                "RELATIONSHIP_FOLLOW_UP_NEED_HIGH",
                "SALES_SEASONAL_OPPORTUNITY_HIGH",
            ),
        )

    def test_match_contextual_rules_returns_top_matches_with_evidence(self):
        result = match_contextual_rules(FULL_CONTEXT_ROW)
        trace = result.to_trace(FULL_CONTEXT_ROW)

        self.assertTrue(result.has_match)
        self.assertEqual(
            result.matched_rule_ids,
            (
                "AGRONOMIC_PEST_DISEASE_RISK_HIGH",
                "COMPETITOR_PRESSURE_RESPONSE_HIGH",
                "INVENTORY_REPLENISHMENT_NEED_HIGH",
            ),
        )
        self.assertEqual(trace["entity_id"], "RET001")
        self.assertEqual(trace["matched_rules"][0]["confidence_level"], "High")
        self.assertEqual(
            trace["matched_rules"][0]["evidence_signals"],
            {
                "pest_disease_risk_score": 90,
                "crop_stage_risk_score": 80,
            },
        )

    def test_no_match_returns_explicit_empty_match_result(self):
        low_context_row = {
            **FULL_CONTEXT_ROW,
            "entity_id": "RET002",
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

        result = match_contextual_rules(low_context_row)

        self.assertFalse(result.has_match)
        self.assertEqual(result.matched_rule_ids, ())
        self.assertEqual(result.to_trace(low_context_row)["matched_rules"], [])

    def test_missing_required_rule_field_fails_explicitly(self):
        incomplete_row = dict(FULL_CONTEXT_ROW)
        incomplete_row.pop("stockout_risk_score")

        with self.assertRaisesRegex(ContextualRuleMatchingError, "stockout_risk_score"):
            match_contextual_rules(incomplete_row)

    def test_build_rule_match_view_preserves_context_and_trace(self):
        contextual_view = pd.DataFrame(
            [
                FULL_CONTEXT_ROW,
                {**FULL_CONTEXT_ROW, "entity_id": "RET002", "pest_disease_risk_score": 10},
            ]
        )

        output = build_rule_match_view(contextual_view)

        self.assertEqual(output["entity_id"].tolist(), ["RET001", "RET002"])
        self.assertEqual(output.loc[0, "matched_rule_count"], 3)
        self.assertEqual(output.loc[0, "matched_rule_ids"][0], "AGRONOMIC_PEST_DISEASE_RISK_HIGH")
        self.assertIn("rule_match_trace", output.columns)
        self.assertEqual(output.loc[0, "priority_level"], "Critical")


if __name__ == "__main__":
    unittest.main()
