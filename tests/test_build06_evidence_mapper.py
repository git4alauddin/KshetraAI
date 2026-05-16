import unittest

import pandas as pd

from backend.anomaly.anomaly_engine import build_anomaly_outputs
from backend.engines.priority_engine import build_ranked_priority_view
from backend.engines.recommendation_engine import build_recommendation_view
from backend.explainability.evidence_mapper import (
    EVIDENCE_OUTPUT_COLUMNS,
    EvidenceMappingError,
    build_evidence_view,
    map_anomaly_evidence,
    map_priority_evidence,
    map_recommendation_evidence,
)
from backend.explainability.explanation_registry import (
    default_template_for_type,
    list_explanation_type_specs,
    list_template_specs,
)


def priority_feature_row(entity_id="RET001"):
    return {
        "entity_id": entity_id,
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


class Build06EvidenceMapperTest(unittest.TestCase):
    def test_registry_loads_template_specs_for_supported_types(self):
        type_specs = list_explanation_type_specs()
        template_specs = list_template_specs()

        self.assertEqual(
            tuple(spec.explanation_type for spec in type_specs),
            ("anomaly", "confidence", "evidence_summary", "priority", "recommendation"),
        )
        self.assertEqual(len(template_specs), 5)
        self.assertEqual(
            default_template_for_type("anomaly").template_id,
            "ANOMALY_ALERT_SUMMARY",
        )

    def test_map_priority_evidence_uses_top_component_scores(self):
        ranked_view = build_ranked_priority_view(pd.DataFrame([priority_feature_row()]))

        bundle = map_priority_evidence(ranked_view.iloc[0].to_dict())

        self.assertEqual(bundle.explanation_type, "priority")
        self.assertEqual(bundle.source_output_id, "PRIORITY_RET001")
        self.assertEqual(bundle.template_id, "PRIORITY_SIGNAL_SUMMARY")
        self.assertEqual(bundle.source_trace_ids, ("priority_trace", "classification_trace"))
        self.assertEqual(bundle.evidence_items[0].evidence_type, "priority_component")
        self.assertEqual(bundle.evidence_items[-1].source_field, "priority_score")
        self.assertNotIn("summary_text", bundle.to_row())

    def test_map_recommendation_evidence_uses_rule_evidence_signals(self):
        recommendation_view = build_recommendation_view(pd.DataFrame([RECOMMENDATION_CONTEXT_ROW]))
        recommendation_row = recommendation_view.iloc[0].to_dict()

        bundle = map_recommendation_evidence(recommendation_row)

        self.assertEqual(bundle.explanation_type, "recommendation")
        self.assertEqual(bundle.source_output_id, recommendation_row["matched_rule_id"])
        self.assertEqual(bundle.template_id, "RECOMMENDATION_RULE_SUMMARY")
        self.assertEqual(bundle.confidence_level, "High")
        self.assertTrue(all(item.evidence_type == "recommendation_signal" for item in bundle.evidence_items))

    def test_map_anomaly_evidence_uses_supporting_evidence_items(self):
        anomaly_outputs = build_anomaly_outputs(
            pd.DataFrame([ANOMALY_FEATURE_ROW]),
            detected_at="2026-05-17",
        )
        alert_row = anomaly_outputs.anomaly_alerts.iloc[0].to_dict()

        bundle = map_anomaly_evidence(alert_row)

        self.assertEqual(bundle.explanation_type, "anomaly")
        self.assertEqual(bundle.source_output_id, alert_row["alert_id"])
        self.assertEqual(bundle.template_id, "ANOMALY_ALERT_SUMMARY")
        self.assertEqual(bundle.source_trace_ids, ("anomaly_trace",))
        self.assertTrue(all(item.evidence_type == "anomaly_signal" for item in bundle.evidence_items))

    def test_build_evidence_view_has_stable_schema_and_order(self):
        recommendation_view = build_recommendation_view(
            pd.DataFrame(
                [
                    RECOMMENDATION_CONTEXT_ROW,
                    {**RECOMMENDATION_CONTEXT_ROW, "entity_id": "RET002"},
                ]
            )
        )

        evidence_view = build_evidence_view(recommendation_view, "recommendation")

        self.assertEqual(evidence_view.columns.tolist(), EVIDENCE_OUTPUT_COLUMNS)
        self.assertEqual(evidence_view["entity_id"].tolist()[:3], ["RET001", "RET001", "RET001"])
        self.assertTrue(evidence_view["evidence_items"].map(bool).all())
        self.assertNotIn("priority_score", evidence_view.columns)
        self.assertNotIn("summary_text", evidence_view.columns)

    def test_recommendation_without_evidence_fails_explicitly(self):
        recommendation_view = build_recommendation_view(pd.DataFrame([RECOMMENDATION_CONTEXT_ROW]))
        recommendation_row = recommendation_view.iloc[0].to_dict()
        recommendation_row["evidence_signals"] = {}

        with self.assertRaisesRegex(EvidenceMappingError, "evidence_signals"):
            map_recommendation_evidence(recommendation_row)

    def test_unsupported_evidence_type_fails_explicitly(self):
        with self.assertRaisesRegex(EvidenceMappingError, "Unsupported"):
            build_evidence_view(pd.DataFrame([{"entity_id": "RET001"}]), "unknown")


if __name__ == "__main__":
    unittest.main()
