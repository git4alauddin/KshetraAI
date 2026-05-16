import unittest

import pandas as pd

from backend.anomaly.anomaly_engine import build_anomaly_outputs
from backend.engines.priority_engine import build_ranked_priority_view
from backend.engines.recommendation_engine import build_recommendation_view
from backend.explainability.evidence_mapper import build_evidence_view
from backend.explainability.explanation_engine import (
    build_explanation_trace_view,
    build_explanation_view,
)
from backend.explainability.reasoning_formatter import build_reasoning_view


PRIORITY_FEATURE_ROW = {
    "entity_id": "RET001",
    "territory_id": "T01",
    "entity_type": "retailer",
    "primary_crop": "cotton",
    "weather_risk_score": 95,
    "pest_disease_risk_score": 95,
    "crop_stage_risk_score": 95,
    "ndvi_stress_score": 95,
    "historical_sales_score": 90,
    "seasonal_product_relevance": 90,
    "purchase_history_score": 90,
    "crop_acreage_score": 90,
    "sales_opportunity_score": 90,
    "stock_level_score": 90,
    "sales_velocity_score": 90,
    "stockout_risk_score": 90,
    "inventory_need_score": 90,
    "relationship_need_score": 65,
    "account_priority_score": 70,
    "campaign_engagement_score": 60,
    "competitive_pressure_score": 70,
    "travel_cost_score": 10,
}

RECOMMENDATION_CONTEXT_ROW = {
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

ANOMALY_FEATURE_ROW = {
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
}


class Build06ExplainabilityIntegrationTest(unittest.TestCase):
    def test_priority_explainability_flow_is_deterministic(self):
        ranked_view = build_ranked_priority_view(pd.DataFrame([PRIORITY_FEATURE_ROW]))

        first_reasoning = _reasoning_from_source(ranked_view, "priority")
        second_reasoning = _reasoning_from_source(ranked_view, "priority")

        pd.testing.assert_frame_equal(first_reasoning, second_reasoning)
        self.assertEqual(first_reasoning.loc[0, "explanation_type"], "priority")
        self.assertEqual(first_reasoning.loc[0, "safety_validation_status"], "Safe")
        self.assertIn("because", first_reasoning.loc[0, "safe_explanation_text"])
        self.assertTrue(first_reasoning.loc[0, "reasoning_payload"]["evidence"])

    def test_recommendation_explainability_flow_preserves_rule_traceability(self):
        recommendation_view = build_recommendation_view(pd.DataFrame([RECOMMENDATION_CONTEXT_ROW]))

        reasoning_view = _reasoning_from_source(recommendation_view, "recommendation")

        self.assertEqual(set(reasoning_view["explanation_type"]), {"recommendation"})
        self.assertTrue(reasoning_view["source_output_id"].str.contains("_HIGH").all())
        self.assertTrue(reasoning_view["source_trace_ids"].map(bool).all())
        self.assertTrue(reasoning_view["safe_explanation_text"].str.contains("rule").all())
        self.assertNotIn("recommended_actions", reasoning_view.columns)

    def test_anomaly_explainability_flow_preserves_alert_traceability(self):
        anomaly_outputs = build_anomaly_outputs(
            pd.DataFrame([ANOMALY_FEATURE_ROW]),
            detected_at="2026-05-17",
        )

        reasoning_view = _reasoning_from_source(anomaly_outputs.anomaly_alerts, "anomaly")

        self.assertEqual(set(reasoning_view["explanation_type"]), {"anomaly"})
        self.assertTrue(reasoning_view["source_output_id"].str.startswith("ALERT_").all())
        self.assertTrue(reasoning_view["safe_explanation_text"].str.contains("flagged").all())
        self.assertNotIn("alert_id", reasoning_view.columns)
        self.assertNotIn("priority_score", reasoning_view.columns)

    def test_explanation_trace_rows_match_reasoning_outputs(self):
        evidence_view = build_evidence_view(
            build_recommendation_view(pd.DataFrame([RECOMMENDATION_CONTEXT_ROW])),
            "recommendation",
        )
        explanation_view = build_explanation_view(evidence_view)
        trace_view = build_explanation_trace_view(evidence_view)
        reasoning_view = build_reasoning_view(explanation_view)

        self.assertEqual(
            sorted(reasoning_view["source_output_id"].tolist()),
            sorted(trace_view["source_output_id"].tolist()),
        )
        self.assertTrue(trace_view["evidence_used"].map(bool).all())
        self.assertEqual(trace_view["safety_validation_status"].unique().tolist(), ["Safe"])

    def test_empty_explainability_flow_keeps_stable_outputs(self):
        evidence_view = build_evidence_view(pd.DataFrame(), "priority")
        explanation_view = build_explanation_view(evidence_view)
        reasoning_view = build_reasoning_view(explanation_view)

        self.assertTrue(evidence_view.empty)
        self.assertTrue(explanation_view.empty)
        self.assertTrue(reasoning_view.empty)
        self.assertIn("safe_explanation_text", reasoning_view.columns)


def _reasoning_from_source(source_view, explanation_type):
    evidence_view = build_evidence_view(source_view, explanation_type)
    explanation_view = build_explanation_view(evidence_view)
    return build_reasoning_view(explanation_view)


if __name__ == "__main__":
    unittest.main()
