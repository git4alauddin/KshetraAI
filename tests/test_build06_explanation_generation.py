import unittest

import pandas as pd

from backend.explainability.evidence_mapper import EvidenceBundle, EvidenceItem
from backend.explainability.explanation_engine import (
    EXPLANATION_OUTPUT_COLUMNS,
    EXPLANATION_TRACE_COLUMNS,
    ExplanationGenerationError,
    build_explanation_trace_view,
    build_explanation_view,
    generate_explanation,
)
from backend.explainability.explanation_registry import (
    default_template_for_type,
    load_explanation_template_config,
)
from backend.explainability.template_generator import (
    TemplateGenerationError,
    render_explanation_text,
)


class Build06ExplanationGenerationTest(unittest.TestCase):
    def test_generate_priority_explanation_uses_configured_template(self):
        evidence_row = _evidence_bundle("priority", evidence_count=4).to_row()

        explanation = generate_explanation(evidence_row)

        self.assertEqual(explanation.explanation_type, "priority")
        self.assertEqual(explanation.template_used, "PRIORITY_SIGNAL_SUMMARY")
        self.assertEqual(explanation.safety_validation_status, "Safe")
        self.assertIn("RET001 is marked", explanation.summary_text)
        self.assertIn("because", explanation.summary_text)
        self.assertEqual(explanation.confidence_level, "High")
        self.assertNotIn("recommended_actions", explanation.to_row())

    def test_generate_recommendation_explanation_uses_rule_source_id(self):
        evidence_row = _evidence_bundle("recommendation", evidence_count=2).to_row()

        explanation = generate_explanation(evidence_row)

        self.assertEqual(explanation.explanation_type, "recommendation")
        self.assertEqual(explanation.confidence_level, "Medium")
        self.assertIn("rule RECOMMENDATION_RET001", explanation.summary_text)
        self.assertIn("matched supported evidence", explanation.summary_text)

    def test_generate_anomaly_explanation_preserves_safe_language(self):
        evidence_row = _evidence_bundle("anomaly", evidence_count=3).to_row()
        evidence_row["source_output_id"] = "ALERT_RET001_INVENTORY_STOCKOUT_RISK"

        explanation = generate_explanation(evidence_row)

        self.assertEqual(explanation.explanation_type, "anomaly")
        self.assertEqual(explanation.confidence_level, "High")
        self.assertIn("This anomaly alert was flagged", explanation.summary_text)
        self.assertNotIn("definitely", explanation.summary_text.lower())
        self.assertNotIn("guaranteed", explanation.summary_text.lower())

    def test_build_explanation_view_has_stable_output_schema_and_order(self):
        evidence_view = pd.DataFrame(
            [
                _evidence_bundle("priority", entity_id="RET002").to_row(),
                _evidence_bundle("priority", entity_id="RET001").to_row(),
            ]
        )

        explanation_view = build_explanation_view(evidence_view)

        self.assertEqual(explanation_view.columns.tolist(), EXPLANATION_OUTPUT_COLUMNS)
        self.assertEqual(explanation_view["entity_id"].tolist(), ["RET001", "RET002"])
        self.assertTrue(explanation_view["summary_text"].map(bool).all())
        self.assertEqual(explanation_view["safety_validation_status"].unique().tolist(), ["Safe"])
        self.assertNotIn("priority_score", explanation_view.columns)
        self.assertNotIn("api_response", explanation_view.columns)

    def test_build_explanation_trace_view_preserves_template_and_confidence_rule(self):
        evidence_view = pd.DataFrame([_evidence_bundle("anomaly", evidence_count=3).to_row()])

        trace_view = build_explanation_trace_view(evidence_view)

        self.assertEqual(trace_view.columns.tolist(), EXPLANATION_TRACE_COLUMNS)
        self.assertEqual(trace_view.loc[0, "template_used"], "ANOMALY_ALERT_SUMMARY")
        self.assertEqual(trace_view.loc[0, "confidence_rule_used"], "CONFIDENCE_FROM_ALERT_EVIDENCE")
        self.assertEqual(trace_view.loc[0, "safety_validation_status"], "Safe")
        self.assertTrue(trace_view.loc[0, "evidence_used"])

    def test_missing_evidence_items_fails_explicitly(self):
        evidence_row = _evidence_bundle("priority").to_row()
        evidence_row["evidence_items"] = []

        with self.assertRaisesRegex(ExplanationGenerationError, "evidence_items"):
            generate_explanation(evidence_row)

    def test_template_rendering_blocks_configured_unsafe_phrase(self):
        config = load_explanation_template_config()
        config["safety_terms"]["forbidden_phrases"] = ["because"]
        evidence_row = _evidence_bundle("priority").to_row()

        with self.assertRaisesRegex(TemplateGenerationError, "unsafe"):
            render_explanation_text(evidence_row, config)


def _evidence_bundle(
    explanation_type,
    *,
    entity_id="RET001",
    evidence_count=3,
):
    template = default_template_for_type(explanation_type)
    return EvidenceBundle(
        entity_id=entity_id,
        explanation_type=explanation_type,
        source_output_type=template.source_output_type,
        source_output_id=f"{explanation_type.upper()}_{entity_id}",
        evidence_items=tuple(
            EvidenceItem(
                evidence_id=f"{explanation_type}:signal_{index}",
                source_field=f"{explanation_type}_signal_{index}",
                value=80 - index,
                evidence_type=f"{explanation_type}_signal",
            )
            for index in range(1, evidence_count + 1)
        ),
        confidence_level="Low",
        source_trace_ids=(f"{explanation_type}_trace",),
        template_id=template.template_id,
        template=template,
    )


if __name__ == "__main__":
    unittest.main()
