import unittest

import pandas as pd

from backend.explainability.evidence_mapper import EvidenceBundle, EvidenceItem
from backend.explainability.explanation_engine import build_explanation_view
from backend.explainability.explanation_registry import default_template_for_type
from backend.explainability.reasoning_formatter import (
    REASONING_OUTPUT_COLUMNS,
    ReasoningFormattingError,
    build_reasoning_view,
    format_reasoning_record,
)


class Build06ReasoningFormatterTest(unittest.TestCase):
    def test_format_reasoning_record_builds_downstream_ready_payload(self):
        explanation_row = _explanation_view().iloc[0].to_dict()

        formatted = format_reasoning_record(explanation_row)

        self.assertEqual(formatted.entity_id, "RET001")
        self.assertEqual(formatted.safe_explanation_text, explanation_row["summary_text"])
        self.assertIn("priority signal 1", formatted.evidence_summary)
        payload = formatted.to_payload()
        self.assertEqual(payload["summary"], explanation_row["summary_text"])
        self.assertEqual(payload["confidence"]["level"], "High")
        self.assertEqual(payload["traceability"]["template_used"], "PRIORITY_SIGNAL_SUMMARY")
        self.assertEqual(payload["safety"]["validation_status"], "Safe")

    def test_build_reasoning_view_has_stable_schema_and_order(self):
        explanation_view = _explanation_view(entity_ids=("RET002", "RET001"))

        reasoning_view = build_reasoning_view(explanation_view)

        self.assertEqual(reasoning_view.columns.tolist(), REASONING_OUTPUT_COLUMNS)
        self.assertEqual(reasoning_view["entity_id"].tolist(), ["RET001", "RET002"])
        self.assertTrue(reasoning_view["safe_explanation_text"].map(bool).all())
        self.assertTrue(reasoning_view["reasoning_payload"].map(bool).all())
        self.assertNotIn("api_route", reasoning_view.columns)
        self.assertNotIn("frontend_component", reasoning_view.columns)

    def test_empty_reasoning_view_keeps_schema(self):
        reasoning_view = build_reasoning_view(pd.DataFrame())

        self.assertTrue(reasoning_view.empty)
        self.assertEqual(reasoning_view.columns.tolist(), REASONING_OUTPUT_COLUMNS)

    def test_non_safe_explanation_fails_explicitly(self):
        explanation_row = _explanation_view().iloc[0].to_dict()
        explanation_row["safety_validation_status"] = "Needs Review"

        with self.assertRaisesRegex(ReasoningFormattingError, "Safe"):
            format_reasoning_record(explanation_row)

    def test_missing_evidence_items_fails_explicitly(self):
        explanation_row = _explanation_view().iloc[0].to_dict()
        explanation_row["evidence_items"] = []

        with self.assertRaisesRegex(ReasoningFormattingError, "evidence_items"):
            format_reasoning_record(explanation_row)

    def test_missing_required_field_fails_explicitly(self):
        explanation_row = _explanation_view().iloc[0].to_dict()
        explanation_row.pop("summary_text")

        with self.assertRaisesRegex(ReasoningFormattingError, "summary_text"):
            format_reasoning_record(explanation_row)


def _explanation_view(entity_ids=("RET001",)):
    evidence_rows = [
        _evidence_bundle("priority", entity_id=entity_id).to_row()
        for entity_id in entity_ids
    ]
    return build_explanation_view(pd.DataFrame(evidence_rows))


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
