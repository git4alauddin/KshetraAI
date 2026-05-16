import unittest

import pandas as pd

from backend.learning.feedback_processor import (
    FEEDBACK_SIGNAL_COLUMNS,
    FeedbackProcessingError,
    build_feedback_signal_view,
    process_feedback,
)


TRACKING_ROW = {
    "recommendation_id": "AGRONOMIC_PEST_DISEASE_RISK_HIGH",
    "entity_id": "RET001",
    "outcome_id": "OUTCOME_RET001_AGRONOMIC_PEST_DISEASE_RISK_HIGH",
    "tracking_status": "outcome_logged",
    "feedback_category": "useful",
    "recommendation_followed": True,
    "commercial_success": True,
    "alert_validated": True,
}


class Build07FeedbackProcessorTest(unittest.TestCase):
    def test_process_feedback_creates_positive_learning_signal(self):
        signal = process_feedback(TRACKING_ROW)

        self.assertEqual(signal.feedback_signal_id, "FEEDBACK_RET001_AGRONOMIC_PEST_DISEASE_RISK_HIGH")
        self.assertEqual(signal.explicit_feedback_signal, "positive")
        self.assertEqual(signal.implicit_acceptance_signal, "accepted")
        self.assertEqual(signal.commercial_signal, "positive")
        self.assertEqual(signal.alert_validation_signal, "validated")
        self.assertEqual(signal.overall_feedback_signal, "positive")
        self.assertTrue(signal.learning_ready)
        self.assertNotIn("metric_value", signal.to_row())
        self.assertNotIn("recalibration_signal", signal.to_row())

    def test_process_feedback_creates_negative_signal_when_outcomes_are_negative(self):
        signal = process_feedback(
            {
                **TRACKING_ROW,
                "feedback_category": "wrong_timing",
                "recommendation_followed": False,
                "commercial_success": False,
                "alert_validated": False,
            }
        )

        self.assertEqual(signal.explicit_feedback_signal, "negative")
        self.assertEqual(signal.implicit_acceptance_signal, "rejected")
        self.assertEqual(signal.commercial_signal, "negative")
        self.assertEqual(signal.alert_validation_signal, "not_validated")
        self.assertEqual(signal.overall_feedback_signal, "negative")

    def test_process_feedback_handles_no_feedback_as_neutral(self):
        signal = process_feedback(
            {
                **TRACKING_ROW,
                "feedback_category": "no_feedback",
                "recommendation_followed": True,
                "commercial_success": False,
                "alert_validated": "unknown",
            }
        )

        self.assertEqual(signal.explicit_feedback_signal, "neutral")
        self.assertEqual(signal.alert_validation_signal, "unknown")
        self.assertEqual(signal.overall_feedback_signal, "neutral")
        self.assertTrue(signal.learning_ready)

    def test_process_feedback_without_logged_outcome_is_pending(self):
        signal = process_feedback(
            {
                **TRACKING_ROW,
                "outcome_id": "",
                "tracking_status": "no_outcome_logged",
                "feedback_category": "no_feedback",
                "recommendation_followed": None,
                "commercial_success": False,
                "alert_validated": "unknown",
            }
        )

        self.assertEqual(signal.overall_feedback_signal, "pending")
        self.assertEqual(signal.explicit_feedback_signal, "pending")
        self.assertFalse(signal.learning_ready)

    def test_build_feedback_signal_view_has_stable_schema_and_order(self):
        tracking_view = pd.DataFrame(
            [
                {**TRACKING_ROW, "entity_id": "RET002"},
                TRACKING_ROW,
            ]
        )

        output = build_feedback_signal_view(tracking_view)

        self.assertEqual(output.columns.tolist(), FEEDBACK_SIGNAL_COLUMNS)
        self.assertEqual(output["entity_id"].tolist(), ["RET001", "RET002"])
        self.assertTrue(output["feedback_trace"].map(bool).all())

    def test_missing_tracking_field_fails_explicitly(self):
        row = dict(TRACKING_ROW)
        row.pop("feedback_category")

        with self.assertRaisesRegex(FeedbackProcessingError, "feedback_category"):
            process_feedback(row)

    def test_unsupported_feedback_category_fails_explicitly(self):
        with self.assertRaisesRegex(FeedbackProcessingError, "maybe"):
            process_feedback({**TRACKING_ROW, "feedback_category": "maybe"})

    def test_empty_feedback_signal_view_preserves_schema(self):
        output = build_feedback_signal_view(pd.DataFrame())

        self.assertTrue(output.empty)
        self.assertEqual(output.columns.tolist(), FEEDBACK_SIGNAL_COLUMNS)


if __name__ == "__main__":
    unittest.main()
