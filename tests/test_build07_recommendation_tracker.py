import unittest

import pandas as pd

from backend.learning.outcome_logger import build_outcome_log
from backend.learning.recommendation_tracker import (
    RECOMMENDATION_TRACKING_COLUMNS,
    RecommendationTrackingError,
    build_recommendation_tracking_view,
    track_recommendation,
)


RECOMMENDATION_ROW = {
    "entity_id": "RET001",
    "matched_rule_id": "AGRONOMIC_PEST_DISEASE_RISK_HIGH",
    "recommended_actions": [
        "inspect_crop_symptoms",
        "discuss_crop_protection_advisory_if_symptoms_are_observed",
    ],
    "recommended_product_category": "Crop Protection",
    "confidence_level": "High",
}

OUTCOME_SUBMISSION = {
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


class Build07RecommendationTrackerTest(unittest.TestCase):
    def test_track_recommendation_links_outcome_and_derives_signals(self):
        outcome_log = _outcome_log()

        record = track_recommendation(RECOMMENDATION_ROW, outcome_log.iloc[0].to_dict())

        self.assertEqual(record.recommendation_id, "AGRONOMIC_PEST_DISEASE_RISK_HIGH")
        self.assertEqual(record.outcome_id, "OUTCOME_RET001_AGRONOMIC_PEST_DISEASE_RISK_HIGH")
        self.assertEqual(record.tracking_status, "outcome_logged")
        self.assertTrue(record.visit_completed)
        self.assertTrue(record.recommendation_followed)
        self.assertTrue(record.commercial_success)
        self.assertEqual(record.to_trace()["accepted"], True)
        self.assertNotIn("metric_value", record.to_row())
        self.assertNotIn("recalibration_signal", record.to_row())

    def test_track_recommendation_without_outcome_is_explicit(self):
        record = track_recommendation(RECOMMENDATION_ROW)

        self.assertEqual(record.tracking_status, "no_outcome_logged")
        self.assertEqual(record.outcome_id, "")
        self.assertIsNone(record.visit_completed)
        self.assertIsNone(record.recommendation_followed)
        self.assertFalse(record.commercial_success)
        self.assertEqual(record.alert_validated, "unknown")

    def test_build_recommendation_tracking_view_has_stable_schema_and_order(self):
        recommendation_view = pd.DataFrame(
            [
                {**RECOMMENDATION_ROW, "entity_id": "RET002", "matched_rule_id": "INVENTORY_REPLENISHMENT_NEED_HIGH"},
                RECOMMENDATION_ROW,
            ]
        )
        outcome_log = _outcome_log()

        output = build_recommendation_tracking_view(recommendation_view, outcome_log)

        self.assertEqual(output.columns.tolist(), RECOMMENDATION_TRACKING_COLUMNS)
        self.assertEqual(output["entity_id"].tolist(), ["RET001", "RET002"])
        self.assertEqual(output.loc[0, "tracking_status"], "outcome_logged")
        self.assertEqual(output.loc[1, "tracking_status"], "no_outcome_logged")
        self.assertTrue(output["tracking_trace"].map(bool).all())

    def test_mismatched_outcome_recommendation_id_fails_explicitly(self):
        outcome_row = _outcome_log().iloc[0].to_dict()
        outcome_row["recommendation_id"] = "OTHER_RULE"

        with self.assertRaisesRegex(RecommendationTrackingError, "recommendation_id"):
            track_recommendation(RECOMMENDATION_ROW, outcome_row)

    def test_mismatched_outcome_entity_id_fails_explicitly(self):
        outcome_row = _outcome_log().iloc[0].to_dict()
        outcome_row["entity_id"] = "OTHER_ENTITY"

        with self.assertRaisesRegex(RecommendationTrackingError, "entity_id"):
            track_recommendation(RECOMMENDATION_ROW, outcome_row)

    def test_missing_recommendation_column_fails_explicitly(self):
        recommendation_view = pd.DataFrame([RECOMMENDATION_ROW]).drop(columns=["confidence_level"])

        with self.assertRaisesRegex(RecommendationTrackingError, "confidence_level"):
            build_recommendation_tracking_view(recommendation_view, _outcome_log())

    def test_empty_recommendation_view_preserves_schema(self):
        output = build_recommendation_tracking_view(pd.DataFrame(), _outcome_log())

        self.assertTrue(output.empty)
        self.assertEqual(output.columns.tolist(), RECOMMENDATION_TRACKING_COLUMNS)


def _outcome_log():
    return build_outcome_log(
        pd.DataFrame([OUTCOME_SUBMISSION]),
        known_recommendation_ids=("AGRONOMIC_PEST_DISEASE_RISK_HIGH",),
    )


if __name__ == "__main__":
    unittest.main()
