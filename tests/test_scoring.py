"""
test_scoring.py

Quick checks on the scoring logic. Not exhaustive, just the things that would
actually break the product if they regressed: scores stay in range, the blend
respects its weights, tiers fall on the right side of the thresholds.

Run:  pytest tests/  (or python -m pytest)
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import config, scoring


def _fake_features(n=50):
    rng = np.random.default_rng(0)
    fm = pd.DataFrame({"retailer_id": [f"RTL_{i:05d}" for i in range(n)]})
    fm["territory_id"] = [f"TER_{i % 5:04d}" for i in range(n)]
    for s in config.RULE_WEIGHTS:
        fm[s] = rng.random(n)
    fm["dominant_crop"] = "wheat"
    return fm


def test_rule_score_in_unit_range():
    fm = _fake_features()
    rule = scoring.rule_score(fm)
    assert rule.min() >= 0.0
    assert rule.max() <= 1.0


def test_hybrid_score_uses_full_range():
    fm = _fake_features()
    ml = np.random.default_rng(1).random(len(fm))
    out = scoring.hybrid_score(fm, ml)
    # after min max scaling the final score should span close to 0 and 100
    assert out["final_score_100"].min() >= 0.0
    assert out["final_score_100"].max() <= 100.0
    assert out["final_score_100"].max() - out["final_score_100"].min() > 50  # not compressed


def test_rule_weights_sum_to_one():
    assert abs(sum(config.RULE_WEIGHTS.values()) - 1.0) < 1e-9


def test_blend_weights_sum_to_one():
    assert abs(config.RULE_BLEND_WEIGHT + config.ML_BLEND_WEIGHT - 1.0) < 1e-9


def test_tiers_fall_on_right_side():
    assert scoring.tier(90) == "URGENT"
    assert scoring.tier(50) == "IMPORTANT"
    assert scoring.tier(20) == "MONITOR"
