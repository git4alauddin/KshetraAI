import unittest

import pandas as pd

from backend.learning.recalibration_engine import (
    RecalibrationSignalError,
    generate_recalibration_signals,
    load_recalibration_config,
)


PERFORMANCE_METRICS = pd.DataFrame(
    [
        {
            "metric_id": "RECOMMENDATION_ACCEPTANCE_RATE",
            "metric_name": "recommendation_acceptance_rate",
            "numerator": 2.0,
            "denominator": 10.0,
            "metric_value": 0.2,
            "metric_unit": "ratio",
            "metric_trace": {},
        },
        {
            "metric_id": "ORDER_CONVERSION_RATE",
            "metric_name": "order_conversion_rate",
            "numerator": 8.0,
            "denominator": 10.0,
            "metric_value": 0.8,
            "metric_unit": "ratio",
            "metric_trace": {},
        },
        {
            "metric_id": "ALERT_VALIDATION_RATE",
            "metric_name": "alert_validation_rate",
            "numerator": 2.0,
            "denominator": 10.0,
            "metric_value": 0.2,
            "metric_unit": "ratio",
            "metric_trace": {},
        },
        {
            "metric_id": "FEEDBACK_POSITIVE_RATE",
            "metric_name": "feedback_positive_rate",
            "numerator": 3.0,
            "denominator": 10.0,
            "metric_value": 0.3,
            "metric_unit": "ratio",
            "metric_trace": {},
        },
    ]
)


class Build07RecalibrationEngineTest(unittest.TestCase):
    def test_generate_recalibration_signals_from_configured_rules(self):
        signals = generate_recalibration_signals(PERFORMANCE_METRICS)

        self.assertEqual(signals.columns.tolist(), load_recalibration_config()["signal_schema"])
        self.assertEqual(
            set(signals["signal_id"]),
            {
                "SIGNAL_INVENTORY_WEIGHT_POSITIVE_REVIEW",
                "SIGNAL_RECOMMENDATION_RULE_LOW_ACCEPTANCE_REVIEW",
                "SIGNAL_ANOMALY_ALERT_VALIDATION_REVIEW",
                "SIGNAL_CONFIDENCE_CALIBRATION_REVIEW",
            },
        )
        self.assertTrue(signals["requires_human_review"].all())
        self.assertTrue(signals["signal_trace"].map(bool).all())
        self.assertNotIn("updated_weight", signals.columns)
        self.assertNotIn("new_threshold", signals.columns)

    def test_generate_recalibration_signals_is_deterministic(self):
        first_output = generate_recalibration_signals(PERFORMANCE_METRICS)
        second_output = generate_recalibration_signals(PERFORMANCE_METRICS.sample(frac=1))

        self.assertEqual(first_output["signal_id"].tolist(), second_output["signal_id"].tolist())
        self.assertEqual(
            first_output["trigger_condition"].tolist(),
            second_output["trigger_condition"].tolist(),
        )

    def test_rules_do_not_fire_when_thresholds_or_denominators_do_not_qualify(self):
        metrics = PERFORMANCE_METRICS.copy()
        metrics["metric_value"] = [0.8, 0.4, 0.9, 0.8]
        metrics["denominator"] = [4.0, 4.0, 4.0, 4.0]

        signals = generate_recalibration_signals(metrics)

        self.assertTrue(signals.empty)
        self.assertEqual(signals.columns.tolist(), load_recalibration_config()["signal_schema"])

    def test_missing_metric_column_fails_explicitly(self):
        metrics = PERFORMANCE_METRICS.drop(columns=["denominator"])

        with self.assertRaisesRegex(RecalibrationSignalError, "denominator"):
            generate_recalibration_signals(metrics)

    def test_missing_source_metric_fails_explicitly(self):
        metrics = PERFORMANCE_METRICS[
            PERFORMANCE_METRICS["metric_name"] != "feedback_positive_rate"
        ]

        with self.assertRaisesRegex(RecalibrationSignalError, "feedback_positive_rate"):
            generate_recalibration_signals(metrics)

    def test_config_blocks_automatic_recalibration_policy(self):
        config = load_recalibration_config()
        config["recalibration_policy"]["automatic_weight_updates_allowed"] = True

        with self.assertRaisesRegex(RecalibrationSignalError, "automatic_weight"):
            generate_recalibration_signals(PERFORMANCE_METRICS, config=config)

    def test_empty_performance_metrics_preserves_signal_schema(self):
        signals = generate_recalibration_signals(pd.DataFrame())

        self.assertTrue(signals.empty)
        self.assertEqual(signals.columns.tolist(), load_recalibration_config()["signal_schema"])


if __name__ == "__main__":
    unittest.main()
