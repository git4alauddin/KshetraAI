import unittest

import pandas as pd

from backend.learning.analytics_engine import (
    ALERT_VALIDATION_COLUMNS,
    RECOMMENDATION_EFFECTIVENESS_COLUMNS,
    REP_FEEDBACK_COLUMNS,
    AnalyticsCalculationError,
    build_alert_validation_summary,
    build_recommendation_effectiveness_summary,
    build_rep_feedback_summary,
)
from backend.learning.feedback_processor import build_feedback_signal_view
from backend.learning.metrics_engine import MetricsCalculationError, calculate_performance_metrics


OUTCOME_LOG_ROWS = [
    {
        "outcome_id": "OUTCOME_001",
        "recommendation_id": "RULE_A",
        "alert_id": "ALERT_001",
        "entity_id": "RET001",
        "rep_id": "REP001",
        "visit_completed": True,
        "recommendation_followed": True,
        "sale_made": True,
        "order_placed": True,
        "order_value": 1000.0,
        "alert_validated": True,
        "feedback_category": "useful",
        "rep_feedback": "Useful",
        "submitted_at": "2026-05-17",
        "outcome_trace": {},
    },
    {
        "outcome_id": "OUTCOME_002",
        "recommendation_id": "RULE_B",
        "alert_id": "ALERT_002",
        "entity_id": "RET002",
        "rep_id": "REP002",
        "visit_completed": True,
        "recommendation_followed": False,
        "sale_made": False,
        "order_placed": False,
        "order_value": 0.0,
        "alert_validated": False,
        "feedback_category": "wrong_timing",
        "rep_feedback": "Wrong timing",
        "submitted_at": "2026-05-17",
        "outcome_trace": {},
    },
    {
        "outcome_id": "OUTCOME_003",
        "recommendation_id": "RULE_C",
        "alert_id": "",
        "entity_id": "RET003",
        "rep_id": "REP003",
        "visit_completed": False,
        "recommendation_followed": False,
        "sale_made": False,
        "order_placed": False,
        "order_value": 0.0,
        "alert_validated": "unknown",
        "feedback_category": "no_feedback",
        "rep_feedback": "",
        "submitted_at": "2026-05-17",
        "outcome_trace": {},
    },
]

TRACKING_ROWS = [
    {
        "recommendation_id": "RULE_A",
        "entity_id": "RET001",
        "matched_rule_id": "RULE_A",
        "recommended_actions": ["action_a"],
        "recommended_product_category": "Crop Protection",
        "recommendation_confidence_level": "High",
        "outcome_id": "OUTCOME_001",
        "rep_id": "REP001",
        "visit_completed": True,
        "recommendation_followed": True,
        "sale_made": True,
        "order_placed": True,
        "order_value": 1000.0,
        "commercial_success": True,
        "alert_id": "ALERT_001",
        "alert_validated": True,
        "feedback_category": "useful",
        "submitted_at": "2026-05-17",
        "tracking_status": "outcome_logged",
        "tracking_trace": {},
    },
    {
        "recommendation_id": "RULE_A",
        "entity_id": "RET002",
        "matched_rule_id": "RULE_A",
        "recommended_actions": ["action_a"],
        "recommended_product_category": "Crop Protection",
        "recommendation_confidence_level": "High",
        "outcome_id": "OUTCOME_002",
        "rep_id": "REP002",
        "visit_completed": True,
        "recommendation_followed": False,
        "sale_made": False,
        "order_placed": False,
        "order_value": 0.0,
        "commercial_success": False,
        "alert_id": "ALERT_002",
        "alert_validated": False,
        "feedback_category": "wrong_timing",
        "submitted_at": "2026-05-17",
        "tracking_status": "outcome_logged",
        "tracking_trace": {},
    },
]


class Build07MetricsAnalyticsTest(unittest.TestCase):
    def test_calculate_performance_metrics_uses_configured_formulas(self):
        metrics = calculate_performance_metrics(pd.DataFrame(OUTCOME_LOG_ROWS))

        metric_values = dict(zip(metrics["metric_name"], metrics["metric_value"]))
        self.assertEqual(metric_values["visit_completion_rate"], 0.6667)
        self.assertEqual(metric_values["recommendation_acceptance_rate"], 0.3333)
        self.assertEqual(metric_values["order_conversion_rate"], 0.5)
        self.assertEqual(metric_values["alert_validation_rate"], 0.5)
        self.assertEqual(metric_values["average_order_value"], 1000.0)
        self.assertEqual(metric_values["feedback_positive_rate"], 0.5)
        self.assertTrue(metrics["metric_trace"].map(bool).all())
        self.assertNotIn("signal_id", metrics.columns)

    def test_calculate_performance_metrics_handles_zero_denominator(self):
        outcome_log = pd.DataFrame(
            [{**OUTCOME_LOG_ROWS[0], "order_placed": False, "order_value": 0.0}]
        )

        metrics = calculate_performance_metrics(outcome_log)
        average_order_value = metrics[
            metrics["metric_name"] == "average_order_value"
        ]["metric_value"].iloc[0]

        self.assertEqual(average_order_value, 0.0)

    def test_missing_metric_column_fails_explicitly(self):
        outcome_log = pd.DataFrame(OUTCOME_LOG_ROWS).drop(columns=["order_value"])

        with self.assertRaisesRegex(MetricsCalculationError, "order_value"):
            calculate_performance_metrics(outcome_log)

    def test_build_recommendation_effectiveness_summary(self):
        summary = build_recommendation_effectiveness_summary(pd.DataFrame(TRACKING_ROWS))

        self.assertEqual(summary.columns.tolist(), RECOMMENDATION_EFFECTIVENESS_COLUMNS)
        self.assertEqual(summary.loc[0, "matched_rule_id"], "RULE_A")
        self.assertEqual(summary.loc[0, "tracked_recommendations"], 2)
        self.assertEqual(summary.loc[0, "outcomes_logged"], 2)
        self.assertEqual(summary.loc[0, "recommendations_followed"], 1)
        self.assertEqual(summary.loc[0, "commercial_successes"], 1)
        self.assertEqual(summary.loc[0, "total_order_value"], 1000.0)

    def test_build_alert_validation_summary(self):
        summary = build_alert_validation_summary(pd.DataFrame(TRACKING_ROWS))

        self.assertEqual(summary.columns.tolist(), ALERT_VALIDATION_COLUMNS)
        self.assertEqual(set(summary["alert_validation_status"]), {"False", "True"})
        self.assertTrue(summary["alert_validation_trace"].map(bool).all())

    def test_build_rep_feedback_summary(self):
        feedback_view = build_feedback_signal_view(pd.DataFrame(TRACKING_ROWS))

        summary = build_rep_feedback_summary(feedback_view)

        self.assertEqual(summary.columns.tolist(), REP_FEEDBACK_COLUMNS)
        self.assertEqual(set(summary["feedback_category"]), {"useful", "wrong_timing"})
        self.assertEqual(summary["learning_ready_count"].sum(), 2)
        self.assertTrue(summary["feedback_summary_trace"].map(bool).all())

    def test_missing_analytics_column_fails_explicitly(self):
        tracking_view = pd.DataFrame(TRACKING_ROWS).drop(columns=["matched_rule_id"])

        with self.assertRaisesRegex(AnalyticsCalculationError, "matched_rule_id"):
            build_recommendation_effectiveness_summary(tracking_view)

    def test_empty_summary_views_preserve_schema(self):
        self.assertEqual(
            build_recommendation_effectiveness_summary(pd.DataFrame()).columns.tolist(),
            RECOMMENDATION_EFFECTIVENESS_COLUMNS,
        )
        self.assertEqual(
            build_alert_validation_summary(pd.DataFrame()).columns.tolist(),
            ALERT_VALIDATION_COLUMNS,
        )
        self.assertEqual(
            build_rep_feedback_summary(pd.DataFrame()).columns.tolist(),
            REP_FEEDBACK_COLUMNS,
        )


if __name__ == "__main__":
    unittest.main()
