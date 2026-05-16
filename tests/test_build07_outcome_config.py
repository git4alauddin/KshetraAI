import unittest
from pathlib import Path

import yaml


OUTCOME_METRICS_PATH = Path("backend/config/outcome_metrics.yaml")
RECALIBRATION_RULES_PATH = Path("backend/config/recalibration_rules.yaml")
EXPECTED_METRICS = {
    "visit_completion_rate",
    "recommendation_acceptance_rate",
    "order_conversion_rate",
    "alert_validation_rate",
    "average_order_value",
    "feedback_positive_rate",
}
FORBIDDEN_AUTONOMOUS_ACTIONS = (
    "automatic_weight_updates_allowed",
    "automatic_rule_updates_allowed",
    "automatic_threshold_updates_allowed",
)


def load_yaml(path):
    with path.open(encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)


class Build07OutcomeConfigTest(unittest.TestCase):
    def test_outcome_policy_is_deterministic_and_auditable(self):
        config = load_yaml(OUTCOME_METRICS_PATH)
        policy = config["outcome_policy"]

        self.assertTrue(policy["deterministic_processing"])
        self.assertTrue(policy["require_known_recommendation_id"])
        self.assertTrue(policy["require_entity_id"])
        self.assertTrue(policy["require_rep_id"])
        self.assertTrue(policy["require_non_negative_order_value"])
        self.assertEqual(policy["default_submitted_at"], "configured_static_outcome_submission")
        self.assertEqual(
            policy["deterministic_sort_keys"],
            ["entity_id", "recommendation_id", "outcome_id"],
        )

    def test_outcome_and_metric_schemas_are_stable(self):
        config = load_yaml(OUTCOME_METRICS_PATH)

        self.assertEqual(
            config["outcome_log_schema"],
            [
                "outcome_id",
                "recommendation_id",
                "alert_id",
                "entity_id",
                "rep_id",
                "visit_completed",
                "recommendation_followed",
                "sale_made",
                "order_placed",
                "order_value",
                "alert_validated",
                "feedback_category",
                "rep_feedback",
                "submitted_at",
                "outcome_trace",
            ],
        )
        self.assertEqual(
            config["performance_metric_schema"],
            [
                "metric_id",
                "metric_name",
                "numerator",
                "denominator",
                "metric_value",
                "metric_unit",
                "metric_trace",
            ],
        )

    def test_metric_definitions_cover_build_objectives(self):
        config = load_yaml(OUTCOME_METRICS_PATH)
        metric_definitions = config["metric_definitions"]

        self.assertEqual(set(metric_definitions), EXPECTED_METRICS)
        for metric_name, metric in metric_definitions.items():
            with self.subTest(metric=metric_name):
                self.assertEqual(metric["metric_name"], metric_name)
                self.assertTrue(metric["metric_id"].isupper())
                self.assertIn(metric["metric_unit"], ("ratio", "currency"))
                self.assertIn("denominator_scope", metric)
                self.assertTrue(metric["description"])

    def test_valid_status_and_feedback_values_are_controlled(self):
        config = load_yaml(OUTCOME_METRICS_PATH)

        self.assertIn("useful", config["valid_feedback_categories"])
        self.assertIn("no_feedback", config["valid_feedback_categories"])
        for field, field_config in config["valid_outcome_statuses"].items():
            with self.subTest(field=field):
                self.assertTrue(field_config["allowed_values"])
                self.assertIn(True, field_config["allowed_values"])
                self.assertIn(False, field_config["allowed_values"])

    def test_recalibration_policy_is_human_review_only(self):
        config = load_yaml(RECALIBRATION_RULES_PATH)
        policy = config["recalibration_policy"]

        self.assertEqual(policy["mode"], "human_review_only")
        self.assertTrue(policy["requires_human_review"])
        for action in FORBIDDEN_AUTONOMOUS_ACTIONS:
            self.assertFalse(policy[action])
        self.assertEqual(
            policy["deterministic_sort_keys"],
            ["signal_type", "source_metric", "affected_component"],
        )

    def test_recalibration_rules_are_reviewable_and_metric_backed(self):
        outcome_config = load_yaml(OUTCOME_METRICS_PATH)
        recalibration_config = load_yaml(RECALIBRATION_RULES_PATH)
        metric_names = set(outcome_config["metric_definitions"])
        signal_types = set(recalibration_config["signal_types"])

        for rule_key, rule in recalibration_config["recalibration_rules"].items():
            with self.subTest(rule=rule_key):
                self.assertEqual(rule["rule_id"], rule["rule_id"].upper())
                self.assertIn(rule["signal_type"], signal_types)
                self.assertIn(rule["source_metric"], metric_names)
                self.assertTrue(rule["affected_component"])
                self.assertTrue(rule["requires_human_review"])
                self.assertIn(rule["trigger"]["operator"], ("gte", "lte"))
                self.assertGreaterEqual(rule["trigger"]["minimum_denominator"], 1)
                self.assertIn("review", rule["suggestion_text"].lower())

    def test_recalibration_signal_schema_is_stable(self):
        config = load_yaml(RECALIBRATION_RULES_PATH)

        self.assertEqual(
            config["signal_schema"],
            [
                "signal_id",
                "signal_type",
                "source_metric",
                "affected_component",
                "trigger_condition",
                "suggestion_text",
                "requires_human_review",
                "signal_trace",
            ],
        )

    def test_safety_constraints_forbid_automatic_mutation(self):
        config = load_yaml(RECALIBRATION_RULES_PATH)
        forbidden_actions = set(config["safety_constraints"]["forbidden_actions"])

        self.assertIn("mutate_priority_weights", forbidden_actions)
        self.assertIn("rewrite_contextual_rules", forbidden_actions)
        self.assertIn("change_anomaly_thresholds", forbidden_actions)
        self.assertIn("retrain_model", forbidden_actions)
        self.assertIn("deploy_automatic_changes", forbidden_actions)


if __name__ == "__main__":
    unittest.main()
