import unittest
from pathlib import Path

import yaml


EXPLANATION_TEMPLATES_PATH = Path("backend/config/explanation_templates.yaml")
CONFIDENCE_RULES_PATH = Path("backend/config/confidence_rules.yaml")
EXPECTED_EXPLANATION_TYPES = {
    "priority",
    "recommendation",
    "anomaly",
    "confidence",
    "evidence_summary",
}
FORBIDDEN_CERTAINTY_PHRASES = (
    "definitely infected",
    "confirmed disease",
    "guaranteed",
    "will definitely",
    "must be purchased",
    "certain outcome",
)


def load_yaml(path):
    with path.open(encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)


class Build06ExplainabilityConfigTest(unittest.TestCase):
    def test_explanation_template_policy_is_deterministic_and_safe(self):
        config = load_yaml(EXPLANATION_TEMPLATES_PATH)
        policy = config["template_policy"]

        self.assertEqual(policy["generation_mode"], "deterministic_template")
        self.assertTrue(policy["require_evidence_items"])
        self.assertTrue(policy["require_source_trace_ids"])
        self.assertTrue(policy["forbid_uncontrolled_llm_generation"])
        self.assertEqual(policy["safety_validation_statuses"], ["Safe", "Needs Review"])
        self.assertEqual(
            policy["deterministic_sort_keys"],
            ["entity_id", "explanation_type", "source_output_id"],
        )

    def test_explanation_output_schemas_are_stable(self):
        config = load_yaml(EXPLANATION_TEMPLATES_PATH)

        self.assertEqual(
            config["output_schema"],
            [
                "entity_id",
                "explanation_type",
                "source_output_type",
                "source_output_id",
                "summary_text",
                "evidence_items",
                "confidence_level",
                "confidence_reasoning",
                "source_trace_ids",
                "template_used",
                "safety_validation_status",
            ],
        )
        self.assertEqual(
            config["trace_output_schema"],
            [
                "entity_id",
                "explanation_type",
                "source_output_type",
                "source_output_id",
                "evidence_used",
                "template_used",
                "confidence_rule_used",
                "safety_validation_status",
            ],
        )

    def test_all_explanation_types_have_default_templates(self):
        config = load_yaml(EXPLANATION_TEMPLATES_PATH)
        explanation_types = config["explanation_types"]
        templates = config["templates"]

        self.assertEqual(set(explanation_types), EXPECTED_EXPLANATION_TYPES)
        for explanation_type, type_config in explanation_types.items():
            with self.subTest(explanation_type=explanation_type):
                self.assertTrue(type_config["required_trace_fields"])
                default_template_id = type_config["default_template_id"]
                self.assertIn(default_template_id, templates)
                self.assertEqual(
                    templates[default_template_id]["explanation_type"],
                    explanation_type,
                )

    def test_templates_are_evidence_backed_and_link_confidence_rules(self):
        templates = load_yaml(EXPLANATION_TEMPLATES_PATH)["templates"]
        confidence_rules = load_yaml(CONFIDENCE_RULES_PATH)["confidence_rules"]

        for template_id, template in templates.items():
            with self.subTest(template_id=template_id):
                self.assertIn(template["explanation_type"], EXPECTED_EXPLANATION_TYPES)
                self.assertIn(template["confidence_rule_id"], confidence_rules)
                self.assertTrue(template["required_evidence_fields"])
                self.assertTrue(template["placeholders"])
                self.assertIn("{", template["text_template"])
                self.assertTrue(template["safety_notes"])

    def test_confidence_levels_are_ranked_and_interpretable(self):
        config = load_yaml(CONFIDENCE_RULES_PATH)
        levels = config["confidence_levels"]

        self.assertEqual(config["confidence_policy"]["supported_levels"], ["High", "Medium", "Low"])
        self.assertEqual(levels["High"]["confidence_rank"], 3)
        self.assertEqual(levels["Medium"]["confidence_rank"], 2)
        self.assertEqual(levels["Low"]["confidence_rank"], 1)
        self.assertGreater(
            levels["High"]["minimum_evidence_items"],
            levels["Medium"]["minimum_evidence_items"],
        )
        self.assertGreater(
            levels["Medium"]["minimum_evidence_items"],
            levels["Low"]["minimum_evidence_items"],
        )

    def test_confidence_rules_have_thresholds_for_all_levels(self):
        config = load_yaml(CONFIDENCE_RULES_PATH)
        confidence_rules = config["confidence_rules"]

        for rule_id, rule in confidence_rules.items():
            with self.subTest(rule_id=rule_id):
                self.assertEqual(rule["rule_id"], rule_id)
                self.assertTrue(rule["applies_to"])
                self.assertTrue(rule["evidence_sources"])
                for threshold_key in ("high_when", "medium_when", "low_when"):
                    self.assertIn("minimum_evidence_items", rule[threshold_key])
                    self.assertIn("minimum_trace_completeness", rule[threshold_key])

    def test_template_and_confidence_language_avoid_unsafe_certainty(self):
        template_config = load_yaml(EXPLANATION_TEMPLATES_PATH)
        confidence_config = load_yaml(CONFIDENCE_RULES_PATH)
        text_values = []

        for template in template_config["templates"].values():
            text_values.append(template["text_template"])
            text_values.extend(template["safety_notes"])
        text_values.extend(confidence_config["safety_language"]["confidence_wording_rules"])

        for text_value in text_values:
            lowered_text = text_value.lower()
            with self.subTest(text=text_value):
                for phrase in FORBIDDEN_CERTAINTY_PHRASES:
                    self.assertNotIn(phrase, lowered_text)

    def test_safety_phrase_lists_match_between_configs(self):
        template_config = load_yaml(EXPLANATION_TEMPLATES_PATH)
        confidence_config = load_yaml(CONFIDENCE_RULES_PATH)

        self.assertEqual(
            template_config["safety_terms"]["forbidden_phrases"],
            confidence_config["safety_language"]["forbidden_certainty_phrases"],
        )


if __name__ == "__main__":
    unittest.main()
