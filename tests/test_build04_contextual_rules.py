import unittest
from pathlib import Path

import yaml


RULE_FILES = (
    Path("backend/rules/agronomic_rules.yaml"),
    Path("backend/rules/inventory_rules.yaml"),
    Path("backend/rules/sales_rules.yaml"),
    Path("backend/rules/relationship_rules.yaml"),
    Path("backend/rules/competitor_rules.yaml"),
)
DECISION_THRESHOLDS_PATH = Path("backend/config/decision_thresholds.yaml")
REQUIRED_RULE_FIELDS = {
    "rule_id",
    "rule_type",
    "priority_order",
    "conditions",
    "risk_or_opportunity",
    "recommended_actions",
    "recommended_product_category",
    "confidence_level",
    "evidence_fields",
}
FORBIDDEN_CERTAINTY_PHRASES = (
    "crop is infected",
    "will definitely",
    "must be purchased",
    "confirmed disease",
)


def load_yaml(path):
    with path.open(encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)


def load_all_rules():
    rules = []
    for path in RULE_FILES:
        config = load_yaml(path)
        for rule in config["rules"]:
            rules.append((path.name, rule))
    return rules


class Build04ContextualRulesTest(unittest.TestCase):
    def test_rule_files_define_inspectable_rules_for_each_context(self):
        rules_by_file = {
            path.name: load_yaml(path)["rules"]
            for path in RULE_FILES
        }

        self.assertEqual(
            set(rules_by_file),
            {
                "agronomic_rules.yaml",
                "inventory_rules.yaml",
                "sales_rules.yaml",
                "relationship_rules.yaml",
                "competitor_rules.yaml",
            },
        )
        for file_name, rules in rules_by_file.items():
            with self.subTest(file=file_name):
                self.assertGreaterEqual(len(rules), 1)
                for rule in rules:
                    self.assertTrue(REQUIRED_RULE_FIELDS.issubset(rule))

    def test_rule_ids_are_stable_and_globally_unique(self):
        rules = load_all_rules()
        rule_ids = [rule["rule_id"] for _file_name, rule in rules]

        self.assertEqual(len(rule_ids), len(set(rule_ids)))
        for rule_id in rule_ids:
            self.assertEqual(rule_id, rule_id.upper())
            self.assertNotIn(" ", rule_id)

    def test_rules_follow_configured_confidence_types_and_product_categories(self):
        thresholds = load_yaml(DECISION_THRESHOLDS_PATH)
        contextual_config = thresholds["contextual_decision"]
        allowed_rule_types = set(contextual_config["allowed_rule_types"])
        allowed_confidence_levels = set(contextual_config["confidence_levels"])
        allowed_product_categories = set(contextual_config["allowed_product_categories"])
        supported_operators = set(contextual_config["supported_operators"])

        for file_name, rule in load_all_rules():
            with self.subTest(file=file_name, rule=rule["rule_id"]):
                self.assertIn(rule["rule_type"], allowed_rule_types)
                self.assertIn(rule["confidence_level"], allowed_confidence_levels)
                self.assertIn(rule["recommended_product_category"], allowed_product_categories)
                self.assertIsInstance(rule["priority_order"], int)
                self.assertGreater(rule["priority_order"], 0)

                conditions = rule["conditions"]["all"]
                self.assertGreaterEqual(len(conditions), 1)
                for condition in conditions:
                    self.assertIn(condition["operator"], supported_operators)
                    self.assertIn(condition["field"], rule["evidence_fields"])
                    self.assertIsInstance(condition["value"], (int, float, str))

    def test_rule_actions_and_risk_language_are_structured_and_safe(self):
        for file_name, rule in load_all_rules():
            with self.subTest(file=file_name, rule=rule["rule_id"]):
                self.assertGreaterEqual(len(rule["recommended_actions"]), 1)
                for action in rule["recommended_actions"]:
                    self.assertEqual(action, action.lower())
                    self.assertNotIn(" ", action)

                combined_text = " ".join(
                    [
                        rule["risk_or_opportunity"],
                        rule["recommended_product_category"],
                        *rule["recommended_actions"],
                    ]
                ).lower()
                for phrase in FORBIDDEN_CERTAINTY_PHRASES:
                    self.assertNotIn(phrase, combined_text)

    def test_contextual_config_does_not_replace_priority_thresholds(self):
        thresholds = load_yaml(DECISION_THRESHOLDS_PATH)

        self.assertEqual(thresholds["priority_levels"]["critical"]["min_score"], 80)
        self.assertEqual(thresholds["priority_levels"]["high"]["min_score"], 65)
        self.assertEqual(thresholds["priority_levels"]["medium"]["min_score"], 50)
        self.assertIn("contextual_decision", thresholds)


if __name__ == "__main__":
    unittest.main()
