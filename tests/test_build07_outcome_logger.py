import unittest

import pandas as pd

from backend.learning.outcome_logger import (
    OutcomeLoggingError,
    build_outcome_log,
    load_outcome_metric_config,
    log_outcome,
)


KNOWN_RECOMMENDATION_IDS = (
    "AGRONOMIC_PEST_DISEASE_RISK_HIGH",
    "INVENTORY_REPLENISHMENT_NEED_HIGH",
)

VALID_OUTCOME_SUBMISSION = {
    "recommendation_id": "AGRONOMIC_PEST_DISEASE_RISK_HIGH",
    "alert_id": "ALERT_RET001_PEST_RISK",
    "entity_id": "RET001",
    "rep_id": "REP001",
    "visit_completed": True,
    "recommendation_followed": True,
    "sale_made": True,
    "order_placed": True,
    "order_value": 18500,
    "alert_validated": True,
    "feedback_category": "useful",
    "rep_feedback": "Retailer accepted advisory and placed order.",
    "submitted_at": "2026-05-17",
}


class Build07OutcomeLoggerTest(unittest.TestCase):
    def test_log_outcome_normalizes_canonical_record_and_trace(self):
        record = log_outcome(
            VALID_OUTCOME_SUBMISSION,
            known_recommendation_ids=KNOWN_RECOMMENDATION_IDS,
        )

        self.assertEqual(record.outcome_id, "OUTCOME_RET001_AGRONOMIC_PEST_DISEASE_RISK_HIGH")
        self.assertEqual(record.order_value, 18500.0)
        self.assertTrue(record.visit_completed)
        self.assertTrue(record.recommendation_followed)
        self.assertEqual(record.alert_validated, True)
        self.assertEqual(record.to_trace()["commercial_success"], True)
        self.assertNotIn("metric_value", record.to_row())
        self.assertNotIn("recalibration_signal", record.to_row())

    def test_build_outcome_log_uses_configured_schema_and_stable_order(self):
        config = load_outcome_metric_config()
        submissions = pd.DataFrame(
            [
                {**VALID_OUTCOME_SUBMISSION, "entity_id": "RET002", "recommendation_id": "INVENTORY_REPLENISHMENT_NEED_HIGH"},
                VALID_OUTCOME_SUBMISSION,
            ]
        )

        output = build_outcome_log(
            submissions,
            known_recommendation_ids=KNOWN_RECOMMENDATION_IDS,
            config=config,
        )

        self.assertEqual(output.columns.tolist(), config["outcome_log_schema"])
        self.assertEqual(output["entity_id"].tolist(), ["RET001", "RET002"])
        self.assertTrue(output["outcome_trace"].map(bool).all())
        self.assertEqual(
            output.loc[0, "submitted_at"],
            "2026-05-17",
        )

    def test_default_submitted_at_is_configured_and_deterministic(self):
        submission = dict(VALID_OUTCOME_SUBMISSION)
        submission.pop("submitted_at")

        record = log_outcome(
            submission,
            known_recommendation_ids=KNOWN_RECOMMENDATION_IDS,
        )

        self.assertEqual(record.submitted_at, "configured_static_outcome_submission")

    def test_unknown_recommendation_id_fails_explicitly(self):
        submission = {
            **VALID_OUTCOME_SUBMISSION,
            "recommendation_id": "UNKNOWN_REC",
        }

        with self.assertRaisesRegex(OutcomeLoggingError, "UNKNOWN_REC"):
            log_outcome(
                submission,
                known_recommendation_ids=KNOWN_RECOMMENDATION_IDS,
            )

    def test_invalid_feedback_category_fails_explicitly(self):
        submission = {
            **VALID_OUTCOME_SUBMISSION,
            "feedback_category": "maybe_useful",
        }

        with self.assertRaisesRegex(OutcomeLoggingError, "feedback_category"):
            log_outcome(
                submission,
                known_recommendation_ids=KNOWN_RECOMMENDATION_IDS,
            )

    def test_invalid_boolean_field_fails_explicitly(self):
        submission = {
            **VALID_OUTCOME_SUBMISSION,
            "visit_completed": "yes",
        }

        with self.assertRaisesRegex(OutcomeLoggingError, "visit_completed"):
            log_outcome(
                submission,
                known_recommendation_ids=KNOWN_RECOMMENDATION_IDS,
            )

    def test_negative_order_value_fails_explicitly(self):
        submission = {
            **VALID_OUTCOME_SUBMISSION,
            "order_value": -1,
        }

        with self.assertRaisesRegex(OutcomeLoggingError, "non-negative"):
            log_outcome(
                submission,
                known_recommendation_ids=KNOWN_RECOMMENDATION_IDS,
            )

    def test_empty_outcome_log_preserves_schema(self):
        output = build_outcome_log(
            pd.DataFrame(),
            known_recommendation_ids=KNOWN_RECOMMENDATION_IDS,
        )

        self.assertTrue(output.empty)
        self.assertEqual(output.columns.tolist(), load_outcome_metric_config()["outcome_log_schema"])


if __name__ == "__main__":
    unittest.main()
