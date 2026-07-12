"""
test_evaluation.py

Checks the eval suite computes sensible numbers on tiny hand made inputs, and
that SALAH always returns a usable recommendation even with no API key (the
fallback path). These are the pieces that make the project a portfolio piece
rather than a notebook, so they are worth a test.
"""

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import evaluation, salah_agent


def test_precision_at_k_counts_converters():
    scores = pd.DataFrame({
        "retailer_id": ["A", "B", "C", "D"],
        "territory_id": ["T1", "T1", "T1", "T1"],
        "final_score_100": [90, 80, 70, 10],
    })
    outcomes = pd.DataFrame({"retailer_id": ["A", "B"], "sale_made": [1, 1]})
    res = evaluation.precision_at_k(scores, outcomes, k=2)
    # top 2 are A and B, both converted, precision should be 1.0
    assert res["precision_at_k"] == 1.0


def test_precision_at_k_handles_empty():
    res = evaluation.precision_at_k(pd.DataFrame(), pd.DataFrame(), k=5)
    assert res["precision_at_k"] is None


def test_rep_acceptance_split():
    outcomes = pd.DataFrame({
        "retailer_id": ["A", "B", "C", "D"],
        "recommended_rank": [1, 2, None, None],
        "sale_made": [1, 1, 0, 0],
    })
    res = evaluation.rep_acceptance_vs_outcome(outcomes)
    assert res["followed_recommendation"]["sale_rate"] == 1.0
    assert res["went_off_plan"]["sale_rate"] == 0.0


def test_golden_dataset_loads():
    res = evaluation.golden_dataset_eval()
    # should find the json and report case count, even without a scorer
    assert "cases" in res
    assert res["cases"] >= 1


def test_salah_fallback_always_returns_recommendation():
    # with no API key set, recommend must still return a complete dict
    saved = {k: os.environ.pop(k, None) for k in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]}
    try:
        rec = salah_agent.recommend({
            "retailer_id": "RTL_00001", "dominant_crop": "mustard",
            "final_score_100": 88, "district": "Akola",
        }, language="hinglish")
        assert rec["product"]
        assert rec["pitch_line"]
        assert rec["source"] == "fallback_rule_based"
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v


def test_salah_languages():
    for lang in ["english", "hindi", "hinglish"]:
        rec = salah_agent.recommend({"dominant_crop": "wheat", "retailer_id": "X"}, language=lang)
        assert rec["pitch_line"]
