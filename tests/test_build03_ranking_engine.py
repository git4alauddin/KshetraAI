import unittest

import pandas as pd

from backend.engines.ranking_engine import RankingEngineError, rank_priority_scores


class Build03RankingEngineTest(unittest.TestCase):
    def test_rank_priority_scores_orders_by_score_and_tie_breakers(self):
        priority_scores = pd.DataFrame(
            [
                {
                    "entity_id": "RET004",
                    "priority_score": 70,
                    "agronomic_urgency": 80,
                    "inventory_need": 60,
                    "sales_opportunity": 70,
                    "account_priority_score": 50,
                    "travel_cost": 10,
                },
                {
                    "entity_id": "RET003",
                    "priority_score": 70,
                    "agronomic_urgency": 80,
                    "inventory_need": 60,
                    "sales_opportunity": 70,
                    "account_priority_score": 50,
                    "travel_cost": 25,
                },
                {
                    "entity_id": "RET002",
                    "priority_score": 70,
                    "agronomic_urgency": 80,
                    "inventory_need": 80,
                    "sales_opportunity": 60,
                    "account_priority_score": 40,
                    "travel_cost": 20,
                },
                {
                    "entity_id": "RET001",
                    "priority_score": 75,
                    "agronomic_urgency": 50,
                    "inventory_need": 50,
                    "sales_opportunity": 50,
                    "account_priority_score": 50,
                    "travel_cost": 90,
                },
            ]
        )

        ranked = rank_priority_scores(priority_scores)

        self.assertEqual(ranked["rank"].tolist(), [1, 2, 3, 4])
        self.assertEqual(ranked["entity_id"].tolist(), ["RET001", "RET002", "RET004", "RET003"])

    def test_entity_id_is_final_stable_tie_breaker(self):
        priority_scores = pd.DataFrame(
            [
                {
                    "entity_id": "RET002",
                    "priority_score": 70,
                    "agronomic_urgency": 80,
                    "inventory_need": 60,
                    "sales_opportunity": 70,
                    "travel_cost": 10,
                },
                {
                    "entity_id": "RET001",
                    "priority_score": 70,
                    "agronomic_urgency": 80,
                    "inventory_need": 60,
                    "sales_opportunity": 70,
                    "travel_cost": 10,
                },
            ]
        )

        ranked = rank_priority_scores(priority_scores)

        self.assertEqual(ranked["entity_id"].tolist(), ["RET001", "RET002"])

    def test_missing_required_column_fails_explicitly(self):
        priority_scores = pd.DataFrame(
            [
                {
                    "entity_id": "RET001",
                    "priority_score": 70,
                    "agronomic_urgency": 80,
                    "sales_opportunity": 70,
                    "travel_cost": 10,
                }
            ]
        )

        with self.assertRaisesRegex(RankingEngineError, "inventory_need"):
            rank_priority_scores(priority_scores)

    def test_non_numeric_ranking_column_fails_explicitly(self):
        priority_scores = pd.DataFrame(
            [
                {
                    "entity_id": "RET001",
                    "priority_score": "high",
                    "agronomic_urgency": 80,
                    "inventory_need": 60,
                    "sales_opportunity": 70,
                    "travel_cost": 10,
                }
            ]
        )

        with self.assertRaisesRegex(RankingEngineError, "priority_score"):
            rank_priority_scores(priority_scores)


if __name__ == "__main__":
    unittest.main()
