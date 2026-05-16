import unittest
from pathlib import Path

import yaml


ANOMALY_THRESHOLDS_PATH = Path("backend/config/anomaly_thresholds.yaml")
BASELINES_PATH = Path("backend/config/baselines.yaml")
FORBIDDEN_CERTAINTY_PHRASES = (
    "will definitely",
    "guaranteed",
    "confirmed disease",
    "must be purchased",
)


def load_yaml(path):
    with path.open(encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)


class Build05AnomalyConfigTest(unittest.TestCase):
    def test_severity_thresholds_use_architecture_bands(self):
        config = load_yaml(ANOMALY_THRESHOLDS_PATH)
        levels = config["severity_levels"]

        self.assertEqual(config["score_range"], {"min": 0, "max": 100})
        self.assertEqual(levels["critical"]["min_score"], 80)
        self.assertEqual(levels["high"]["min_score"], 65)
        self.assertEqual(levels["moderate"]["min_score"], 50)
        self.assertEqual(levels["low"]["min_score"], 0)
        self.assertEqual(
            [levels[name]["label"] for name in ("critical", "high", "moderate", "low")],
            ["Critical", "High", "Moderate", "Low"],
        )
        self.assertEqual(
            [levels[name]["severity_rank"] for name in ("critical", "high", "moderate", "low")],
            [4, 3, 2, 1],
        )

    def test_detector_config_is_complete_and_deterministic(self):
        config = load_yaml(ANOMALY_THRESHOLDS_PATH)
        detectors = config["detectors"]
        alert_categories = set(config["alert_categories"])
        confidence_levels = set(config["confidence_levels"])
        detector_ids = [detector["detector_id"] for detector in detectors.values()]

        self.assertEqual(len(detector_ids), len(set(detector_ids)))
        for detector_key, detector in detectors.items():
            with self.subTest(detector=detector_key):
                self.assertEqual(detector["detector_id"], detector["detector_id"].upper())
                self.assertIn(detector["category"], alert_categories)
                self.assertIn(detector["confidence_level"], confidence_levels)
                self.assertIn(detector["deviation_direction"], ("increase", "decrease"))
                self.assertLess(detector["minimum_deviation_score"], detector["high_deviation_score"])
                self.assertLess(detector["high_deviation_score"], detector["critical_deviation_score"])
                self.assertAlmostEqual(
                    sum(detector["severity_signal_weights"].values()),
                    1.0,
                )
                self.assertIn(detector["current_signal"], detector["evidence_fields"])
                self.assertIn(detector["baseline_signal"], detector["evidence_fields"])

    def test_detector_baseline_signals_are_defined_in_baseline_config(self):
        thresholds = load_yaml(ANOMALY_THRESHOLDS_PATH)
        baselines = load_yaml(BASELINES_PATH)
        baseline_signals = {
            signal_name
            for group in baselines["baseline_groups"].values()
            for signal_name in group["signals"]
        }

        for detector in thresholds["detectors"].values():
            with self.subTest(detector=detector["detector_id"]):
                self.assertIn(detector["baseline_signal"], baseline_signals)

    def test_baseline_config_uses_stable_policy_and_valid_defaults(self):
        config = load_yaml(BASELINES_PATH)
        policy = config["baseline_policy"]

        self.assertEqual(policy["baseline_score_range"], {"min": 0, "max": 100})
        self.assertEqual(policy["default_source"], "configured_static_baseline")
        self.assertEqual(policy["missing_baseline_behavior"], "explicit_warning_skip_detector")
        self.assertEqual(policy["deterministic_join_keys"], ["entity_id", "territory_id"])

        for group_name, group in config["baseline_groups"].items():
            with self.subTest(group=group_name):
                self.assertGreater(group["baseline_window_days"], 0)
                self.assertEqual(group["source_view"], "anomaly_feature_view")
                self.assertTrue(group["signals"])
                for signal_name, signal_config in group["signals"].items():
                    self.assertTrue(signal_name.endswith("_baseline_score"))
                    self.assertTrue(signal_config["source_signal"].endswith("_score"))
                    self.assertGreaterEqual(signal_config["default_value"], 0)
                    self.assertLessEqual(signal_config["default_value"], 100)

    def test_alert_language_is_operational_not_certain(self):
        config = load_yaml(ANOMALY_THRESHOLDS_PATH)

        for detector in config["detectors"].values():
            alert_text = detector["alert_type"].lower()
            with self.subTest(detector=detector["detector_id"]):
                for phrase in FORBIDDEN_CERTAINTY_PHRASES:
                    self.assertNotIn(phrase, alert_text)


if __name__ == "__main__":
    unittest.main()
