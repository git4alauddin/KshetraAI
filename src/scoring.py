"""
Rule based scorer and the hybrid blend.

Two corrections from the original here. First, the rule based score is no
longer fed into the model as a feature and then added again at blend time;
that double counting is removed, so the rule score and the model score stay
independent. Second, both scores are scaled to 0..1 before blending, so the
stated split actually holds. The rule scorer remains fully transparent and can
run on its own when the model or connectivity is unavailable.
"""

import numpy as np
import pandas as pd

from . import config

SIGNAL_COLS = list(config.RULE_WEIGHTS.keys())


def rule_score(feature_matrix):
    """Weighted sum of the nine signals, returned on a 0..1 scale."""
    fm = feature_matrix
    score = np.zeros(len(fm))
    for col, w in config.RULE_WEIGHTS.items():
        score = score + fm[col].to_numpy() * w
    return pd.Series(score, index=fm.index, name="rule_score")


def _unit_scale(s):
    lo, hi = s.min(), s.max()
    if hi - lo < 1e-12:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - lo) / (hi - lo)


def hybrid_score(feature_matrix, ml_score):
    """Blend rule and model scores on a common 0..1 scale, then rank per
    territory. ml_score is the raw model output for each retailer."""
    fm = feature_matrix.copy()
    fm["rule_score"] = rule_score(fm)
    fm["ml_score"] = np.asarray(ml_score, dtype=float)

    rule_n = _unit_scale(fm["rule_score"])
    ml_n = _unit_scale(fm["ml_score"])
    fm["final_score"] = config.RULE_BLEND_WEIGHT * rule_n + config.ML_BLEND_WEIGHT * ml_n

    # Spread the final score across the full 0..100 range so the field tiers
    # (urgent, important, monitor) separate clearly instead of bunching up.
    fm["final_score_100"] = (_unit_scale(fm["final_score"]) * 100).round(2)
    fm["final_rank"] = fm.groupby("territory_id")["final_score"].rank(
        ascending=False, method="dense"
    )
    return fm


def tier(score_100):
    """Map a 0..100 score to a field facing label."""
    if score_100 >= 66:
        return "URGENT"
    if score_100 >= 40:
        return "IMPORTANT"
    return "MONITOR"
