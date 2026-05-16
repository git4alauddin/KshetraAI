import unittest
from pathlib import Path

import yaml


PRIORITY_WEIGHTS_PATH = Path("backend/config/priority_weights.yaml")
DECISION_THRESHOLDS_PATH = Path("backend/config/decision_thresholds.yaml")


def load_yaml(path):
    with path.open(encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)


class Build03PriorityConfigTest(unittest.TestCase):
    def test_component_weights_follow_priority_engine_contract(self):
        config = load_yaml(PRIORITY_WEIGHTS_PATH)

        self.assertEqual(config["score_range"], {"min": 0, "max": 100})
        self.assertEqual(
            config["component_weights"],
            {
                "agronomic_urgency": 0.30,
                "sales_opportunity": 0.25,
                "inventory_need": 0.20,
                "relationship_need": 0.10,
                "competitive_pressure": 0.10,
                "travel_cost": -0.05,
            },
        )
        self.assertEqual(config["component_weights"]["travel_cost"], -0.05)
        self.assertEqual(
            config["component_policy"]["penalty_components"],
            ["travel_cost"],
        )

    def test_signal_weights_are_bounded_and_sum_to_one_per_component(self):
        config = load_yaml(PRIORITY_WEIGHTS_PATH)

        for component_name, signal_weights in config["signal_weights"].items():
            with self.subTest(component=component_name):
                self.assertTrue(signal_weights)
                self.assertAlmostEqual(sum(signal_weights.values()), 1.0)
                for signal_name, weight in signal_weights.items():
                    self.assertTrue(signal_name.endswith("_score") or signal_name == "seasonal_product_relevance")
                    self.assertGreaterEqual(weight, 0)
                    self.assertLessEqual(weight, 1)

    def test_priority_thresholds_use_architecture_bands(self):
        config = load_yaml(DECISION_THRESHOLDS_PATH)
        levels = config["priority_levels"]

        self.assertEqual(config["score_range"], {"min": 0, "max": 100})
        self.assertEqual(levels["critical"]["min_score"], 80)
        self.assertEqual(levels["high"]["min_score"], 65)
        self.assertEqual(levels["medium"]["min_score"], 50)
        self.assertEqual(levels["low"]["min_score"], 0)
        self.assertEqual(
            [levels[name]["label"] for name in ("critical", "high", "medium", "low")],
            ["Critical", "High", "Medium", "Low"],
        )
        self.assertEqual(
            [levels[name]["severity_rank"] for name in ("critical", "high", "medium", "low")],
            [4, 3, 2, 1],
        )

    def test_threshold_ranges_cover_score_range_without_overlap(self):
        config = load_yaml(DECISION_THRESHOLDS_PATH)
        levels = config["priority_levels"]
        ordered_levels = ("low", "medium", "high", "critical")

        self.assertEqual(levels["low"]["min_score"], config["score_range"]["min"])
        self.assertEqual(levels["critical"]["max_score"], config["score_range"]["max"])

        for lower_level, upper_level in zip(ordered_levels, ordered_levels[1:]):
            with self.subTest(lower=lower_level, upper=upper_level):
                self.assertLess(
                    levels[lower_level]["max_score"],
                    levels[upper_level]["min_score"],
                )


if __name__ == "__main__":
    unittest.main()
