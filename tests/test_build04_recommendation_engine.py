import unittest

import pandas as pd

from backend.engines.contextual_decision_engine import (
    RuleMatchResult,
    load_contextual_rules,
    match_contextual_rules,
)
from backend.engines.recommendation_engine import (
    NO_MATCH_ACTION,
    NO_MATCH_RULE_ID,
    RecommendationGenerationError,
    build_recommendation_view,
    generate_recommendations,
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


class Build04RecommendationEngineTest(unittest.TestCase):
    def test_generate_recommendations_from_matched_rules(self):
        match_result = match_contextual_rules(FULL_CONTEXT_ROW)

        recommendations = generate_recommendations(FULL_CONTEXT_ROW, match_result)

        self.assertEqual(len(recommendations), 3)
        self.assertEqual(recommendations[0].rule_id, "AGRONOMIC_PEST_DISEASE_RISK_HIGH")
        self.assertEqual(recommendations[0].risk_or_opportunity, "Possible pest or disease pressure")
        self.assertEqual(recommendations[0].recommended_product_category, "Crop Protection")
        self.assertEqual(recommendations[0].confidence_level, "High")
        self.assertEqual(
            recommendations[0].recommended_actions,
            (
                "inspect_crop_symptoms",
                "discuss_crop_protection_advisory_if_symptoms_are_observed",
                "capture_field_observation_notes",
            ),
        )
        self.assertEqual(
            recommendations[0].evidence_signals,
            {
                "pest_disease_risk_score": 90,
                "crop_stage_risk_score": 80,
            },
        )

    def test_no_match_generates_explicit_structured_record(self):
        row = low_context_row()
        match_result = match_contextual_rules(row)

        recommendations = generate_recommendations(row, match_result)

        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].rule_id, NO_MATCH_RULE_ID)
        self.assertEqual(recommendations[0].recommended_actions, (NO_MATCH_ACTION,))
        self.assertEqual(recommendations[0].recommended_product_category, "None")
        self.assertEqual(recommendations[0].confidence_level, "Low")
        self.assertEqual(recommendations[0].evidence_signals, {})

    def test_recommendation_trace_is_structured_and_not_human_explanation(self):
        recommendation = generate_recommendations(FULL_CONTEXT_ROW)[0]
        trace = recommendation.to_trace()

        self.assertEqual(trace["matched_rule_id"], "AGRONOMIC_PEST_DISEASE_RISK_HIGH")
        self.assertIn("evidence_signals", trace)
        self.assertNotIn("explanation", trace)
        self.assertNotIn("reason_text", trace)

    def test_build_recommendation_view_preserves_context_and_stable_order(self):
        contextual_view = pd.DataFrame(
            [
                FULL_CONTEXT_ROW,
                low_context_row("RET002"),
            ]
        )

        output = build_recommendation_view(contextual_view)

        self.assertEqual(output["entity_id"].tolist(), ["RET001", "RET001", "RET001", "RET002"])
        self.assertEqual(
            output["matched_rule_id"].tolist(),
            [
                "AGRONOMIC_PEST_DISEASE_RISK_HIGH",
                "COMPETITOR_PRESSURE_RESPONSE_HIGH",
                "INVENTORY_REPLENISHMENT_NEED_HIGH",
                NO_MATCH_RULE_ID,
            ],
        )
        self.assertEqual(output.loc[0, "priority_level"], "Critical")
        self.assertIn("recommendation_trace", output.columns)
        self.assertIn("recommended_actions", output.columns)

    def test_entity_mismatch_between_row_and_match_result_fails_explicitly(self):
        rules = load_contextual_rules()
        mismatched_result = RuleMatchResult(
            entity_id="OTHER",
            matched_rules=(rules[0],),
        )

        with self.assertRaisesRegex(RecommendationGenerationError, "entity_id"):
            generate_recommendations(FULL_CONTEXT_ROW, mismatched_result)


if __name__ == "__main__":
    unittest.main()
