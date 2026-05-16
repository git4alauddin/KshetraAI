import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from backend.engines.contextual_decision_engine import (
    CONTEXTUAL_DECISION_OUTPUT_VIEW_ORDER,
    build_contextual_decision_output_views,
    write_contextual_decision_output_views,
)
from backend.pipelines.build_context_view import (
    build_contextual_decision_views,
    write_contextual_decision_views,
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


class Build04ContextualTraceOutputsTest(unittest.TestCase):
    def test_build_contextual_decision_output_views_returns_expected_views(self):
        contextual_view = pd.DataFrame([FULL_CONTEXT_ROW, low_context_row()])

        output_views = build_contextual_decision_output_views(contextual_view)

        self.assertEqual(tuple(output_views), CONTEXTUAL_DECISION_OUTPUT_VIEW_ORDER)
        self.assertEqual(output_views["rule_match_trace_log"]["entity_id"].tolist(), ["RET001", "RET002"])
        self.assertEqual(output_views["recommendation_outputs"]["entity_id"].tolist(), ["RET001", "RET001", "RET001", "RET002"])
        self.assertEqual(output_views["recommendation_trace_log"]["entity_id"].tolist(), ["RET001", "RET001", "RET001", "RET002"])
        self.assertEqual(output_views["advisory_outputs"]["entity_id"].tolist(), ["RET001", "RET002"])

    def test_trace_views_preserve_rule_evidence_confidence_and_no_explanation_text(self):
        output_views = build_contextual_decision_output_views(pd.DataFrame([FULL_CONTEXT_ROW]))

        rule_trace = output_views["rule_match_trace_log"].loc[0, "rule_match_trace"]
        recommendation_trace = output_views["recommendation_trace_log"].loc[0, "recommendation_trace"]
        advisory_trace = output_views["advisory_outputs"].loc[0, "advisory_trace"]

        self.assertEqual(rule_trace["matched_rule_ids"][0], "AGRONOMIC_PEST_DISEASE_RISK_HIGH")
        self.assertEqual(recommendation_trace["confidence_level"], "High")
        self.assertEqual(
            recommendation_trace["evidence_signals"],
            {
                "pest_disease_risk_score": 90,
                "crop_stage_risk_score": 80,
            },
        )
        self.assertIn("selected_actions", advisory_trace)
        self.assertNotIn("explanation", recommendation_trace)
        self.assertNotIn("reason_text", advisory_trace)

    def test_pipeline_wrapper_returns_same_output_keys(self):
        contextual_view = pd.DataFrame([FULL_CONTEXT_ROW])

        output_views = build_contextual_decision_views(contextual_view)

        self.assertEqual(tuple(output_views), CONTEXTUAL_DECISION_OUTPUT_VIEW_ORDER)

    def test_write_contextual_decision_output_views_serializes_trace_columns(self):
        output_views = build_contextual_decision_output_views(pd.DataFrame([FULL_CONTEXT_ROW]))

        with tempfile.TemporaryDirectory() as temp_dir:
            output_paths = write_contextual_decision_output_views(output_views, temp_dir)

            self.assertEqual(tuple(output_paths), CONTEXTUAL_DECISION_OUTPUT_VIEW_ORDER)
            recommendation_trace_path = output_paths["recommendation_trace_log"]
            self.assertTrue(recommendation_trace_path.exists())

            written = pd.read_csv(recommendation_trace_path)
            parsed_trace = json.loads(written.loc[0, "recommendation_trace"])
            self.assertEqual(parsed_trace["matched_rule_id"], "AGRONOMIC_PEST_DISEASE_RISK_HIGH")
            self.assertEqual(parsed_trace["confidence_level"], "High")

    def test_pipeline_writer_delegates_to_engine_writer(self):
        output_views = build_contextual_decision_views(pd.DataFrame([low_context_row()]))

        with tempfile.TemporaryDirectory() as temp_dir:
            output_paths = write_contextual_decision_views(output_views, Path(temp_dir))

            self.assertEqual(
                sorted(path.name for path in output_paths.values()),
                [
                    "advisory_outputs.csv",
                    "recommendation_outputs.csv",
                    "recommendation_trace_log.csv",
                    "rule_match_trace_log.csv",
                ],
            )


if __name__ == "__main__":
    unittest.main()
