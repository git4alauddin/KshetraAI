import unittest

import pandas as pd

from backend.engines.contextual_decision_engine import (
    CONTEXTUAL_DECISION_OUTPUT_VIEW_ORDER,
    build_contextual_decision_output_views,
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
        "priority_score": 30,
        "priority_level": "Low",
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


class Build04ContextualDecisionIntegrationTest(unittest.TestCase):
    def test_full_contextual_decision_flow_is_structured_and_deterministic(self):
        contextual_view = pd.DataFrame([FULL_CONTEXT_ROW, low_context_row()])

        output_views = build_contextual_decision_output_views(contextual_view)

        self.assertEqual(tuple(output_views), CONTEXTUAL_DECISION_OUTPUT_VIEW_ORDER)
        self.assertEqual(
            output_views["rule_match_trace_log"]["matched_rule_count"].tolist(),
            [3, 0],
        )
        self.assertEqual(
            output_views["recommendation_outputs"]["matched_rule_id"].tolist(),
            [
                "AGRONOMIC_PEST_DISEASE_RISK_HIGH",
                "COMPETITOR_PRESSURE_RESPONSE_HIGH",
                "INVENTORY_REPLENISHMENT_NEED_HIGH",
                "NO_CONTEXTUAL_RULE_MATCH",
            ],
        )
        self.assertEqual(
            output_views["advisory_outputs"]["advisory_actions"].tolist()[1],
            ["record_no_contextual_recommendation"],
        )

    def test_full_flow_preserves_priority_context_without_recomputing_scores(self):
        contextual_view = pd.DataFrame([FULL_CONTEXT_ROW])

        output_views = build_contextual_decision_output_views(contextual_view)
        recommendation_output = output_views["recommendation_outputs"]
        advisory_output = output_views["advisory_outputs"]

        self.assertEqual(recommendation_output["priority_score"].unique().tolist(), [82.5])
        self.assertEqual(recommendation_output["priority_level"].unique().tolist(), ["Critical"])
        self.assertEqual(advisory_output.loc[0, "priority_score"], 82.5)
        self.assertEqual(advisory_output.loc[0, "priority_level"], "Critical")

    def test_full_flow_preserves_trace_metadata_without_explanation_text(self):
        contextual_view = pd.DataFrame([FULL_CONTEXT_ROW])

        output_views = build_contextual_decision_output_views(contextual_view)
        trace_payloads = [
            output_views["rule_match_trace_log"].loc[0, "rule_match_trace"],
            output_views["recommendation_trace_log"].loc[0, "recommendation_trace"],
            output_views["advisory_outputs"].loc[0, "advisory_trace"],
        ]

        for trace_payload in trace_payloads:
            with self.subTest(trace=trace_payload):
                self.assertNotIn("explanation", trace_payload)
                self.assertNotIn("reason_text", trace_payload)
                self.assertNotIn("anomaly", trace_payload)
                self.assertNotIn("priority_score_formula", trace_payload)

        self.assertIn(
            "evidence_signals",
            output_views["recommendation_trace_log"].loc[0, "recommendation_trace"],
        )
        self.assertIn(
            "selected_actions",
            output_views["advisory_outputs"].loc[0, "advisory_trace"],
        )


if __name__ == "__main__":
    unittest.main()
