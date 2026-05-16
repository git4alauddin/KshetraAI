import unittest

import pandas as pd

from backend.engines.priority_classifier import (
    PriorityClassificationError,
    add_priority_classification,
    classify_priority_score,
    load_decision_threshold_config,
)


class Build03PriorityClassifierTest(unittest.TestCase):
    def test_classify_priority_score_uses_configured_thresholds(self):
        config = load_decision_threshold_config()

        self.assertEqual(classify_priority_score(95, config).priority_level, "Critical")
        self.assertEqual(classify_priority_score(80, config).priority_level, "Critical")
        self.assertEqual(classify_priority_score(79.9995, config).priority_level, "High")
        self.assertEqual(classify_priority_score(65, config).priority_level, "High")
        self.assertEqual(classify_priority_score(64.9995, config).priority_level, "Medium")
        self.assertEqual(classify_priority_score(50, config).priority_level, "Medium")
        self.assertEqual(classify_priority_score(49.9995, config).priority_level, "Low")
        self.assertEqual(classify_priority_score(0, config).priority_level, "Low")

    def test_classification_trace_preserves_level_metadata(self):
        classification = classify_priority_score(65)

        self.assertEqual(classification.priority_level, "High")
        self.assertEqual(classification.priority_level_key, "high")
        self.assertEqual(classification.priority_severity_rank, 3)
        self.assertEqual(
            classification.to_trace(),
            {
                "priority_level": "High",
                "priority_level_key": "high",
                "priority_severity_rank": 3,
                "score": 65.0,
                "matched_min_score": 65.0,
            },
        )

    def test_add_priority_classification_preserves_rows_and_adds_columns(self):
        priority_scores = pd.DataFrame(
            [
                {"entity_id": "RET001", "priority_score": 82.5},
                {"entity_id": "RET002", "priority_score": 63.475},
                {"entity_id": "RET003", "priority_score": 12},
            ]
        )

        output = add_priority_classification(priority_scores)

        self.assertEqual(output["entity_id"].tolist(), ["RET001", "RET002", "RET003"])
        self.assertEqual(output["priority_level"].tolist(), ["Critical", "Medium", "Low"])
        self.assertEqual(output["priority_level_key"].tolist(), ["critical", "medium", "low"])
        self.assertEqual(output["priority_severity_rank"].tolist(), [4, 2, 1])
        self.assertEqual(output.loc[0, "classification_trace"]["priority_level"], "Critical")

    def test_missing_priority_score_column_fails_explicitly(self):
        with self.assertRaisesRegex(PriorityClassificationError, "priority_score"):
            add_priority_classification(pd.DataFrame([{"entity_id": "RET001"}]))

    def test_non_numeric_priority_score_fails_explicitly(self):
        with self.assertRaisesRegex(PriorityClassificationError, "numeric"):
            classify_priority_score("high")

    def test_out_of_range_priority_score_fails_explicitly(self):
        with self.assertRaisesRegex(PriorityClassificationError, "0-100"):
            classify_priority_score(101)


if __name__ == "__main__":
    unittest.main()
