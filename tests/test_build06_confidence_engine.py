import unittest

import pandas as pd

from backend.explainability.confidence_engine import (
    CONFIDENCE_OUTPUT_COLUMNS,
    ConfidenceReasoningError,
    add_confidence_reasoning,
    assess_confidence,
)
from backend.explainability.evidence_mapper import EvidenceBundle, EvidenceItem
from backend.explainability.explanation_registry import default_template_for_type


class Build06ConfidenceEngineTest(unittest.TestCase):
    def test_assess_confidence_returns_high_for_complete_priority_evidence(self):
        bundle = _evidence_bundle("priority", evidence_count=4, source_trace_ids=("priority_trace",))

        assessment = assess_confidence(bundle)

        self.assertEqual(assessment.confidence_level, "High")
        self.assertEqual(assessment.confidence_rank, 3)
        self.assertEqual(assessment.confidence_rule_id, "CONFIDENCE_FROM_PRIORITY_TRACE")
        self.assertEqual(assessment.evidence_count, 4)
        self.assertGreaterEqual(assessment.trace_completeness, 0.80)
        self.assertNotIn("summary_text", assessment.to_row())

    def test_assess_confidence_returns_medium_for_partial_recommendation_evidence(self):
        bundle = _evidence_bundle(
            "recommendation",
            evidence_count=2,
            source_trace_ids=("recommendation_trace",),
        )

        assessment = assess_confidence(bundle)

        self.assertEqual(assessment.confidence_level, "Medium")
        self.assertEqual(assessment.confidence_rank, 2)
        self.assertEqual(assessment.confidence_reasoning, "some supporting evidence is available")

    def test_assess_confidence_returns_low_for_limited_evidence(self):
        bundle = _evidence_bundle(
            "anomaly",
            evidence_count=1,
            source_trace_ids=("anomaly_trace",),
        )

        assessment = assess_confidence(bundle)

        self.assertEqual(assessment.confidence_level, "Low")
        self.assertEqual(assessment.confidence_rank, 1)
        self.assertEqual(
            assessment.confidence_reasoning,
            "available evidence is limited or incomplete",
        )

    def test_add_confidence_reasoning_uses_stable_schema_and_order(self):
        evidence_view = pd.DataFrame(
            [
                _evidence_bundle("recommendation", entity_id="RET002", evidence_count=2).to_row(),
                _evidence_bundle("recommendation", entity_id="RET001", evidence_count=2).to_row(),
            ]
        )

        output = add_confidence_reasoning(evidence_view)

        for column in CONFIDENCE_OUTPUT_COLUMNS:
            self.assertIn(column, output.columns)
        self.assertEqual(output["entity_id"].tolist(), ["RET001", "RET002"])
        self.assertEqual(output["confidence_level"].tolist(), ["Medium", "Medium"])
        self.assertTrue(output["confidence_trace"].map(bool).all())
        self.assertNotIn("safe_explanation_text", output.columns)

    def test_missing_evidence_trace_fails_explicitly(self):
        evidence_row = _evidence_bundle("priority").to_row()
        evidence_row.pop("evidence_trace")

        with self.assertRaisesRegex(ConfidenceReasoningError, "evidence_trace"):
            assess_confidence(evidence_row)

    def test_unknown_confidence_rule_fails_explicitly(self):
        evidence_row = _evidence_bundle("priority").to_row()
        evidence_row["evidence_trace"]["confidence_rule_id"] = "UNKNOWN_RULE"

        with self.assertRaisesRegex(ConfidenceReasoningError, "UNKNOWN_RULE"):
            assess_confidence(evidence_row)


def _evidence_bundle(
    explanation_type,
    *,
    entity_id="RET001",
    evidence_count=3,
    source_trace_ids=None,
):
    template = default_template_for_type(explanation_type)
    resolved_source_trace_ids = source_trace_ids or (f"{explanation_type}_trace",)
    return EvidenceBundle(
        entity_id=entity_id,
        explanation_type=explanation_type,
        source_output_type=template.source_output_type,
        source_output_id=f"{explanation_type.upper()}_{entity_id}",
        evidence_items=tuple(
            EvidenceItem(
                evidence_id=f"{explanation_type}:signal_{index}",
                source_field=f"signal_{index}",
                value=80 - index,
                evidence_type=f"{explanation_type}_signal",
            )
            for index in range(1, evidence_count + 1)
        ),
        confidence_level="Low",
        source_trace_ids=resolved_source_trace_ids,
        template_id=template.template_id,
        template=template,
    )


if __name__ == "__main__":
    unittest.main()
