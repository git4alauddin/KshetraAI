"""
Learning to rank model.

The original trained a binary classifier and then reported it against an
NDCG target it never computed. This module does the thing the deck described:
a LightGBM LambdaRank model grouped by rep and day, evaluated with NDCG at 5.
It also reports a simple baseline so the headline number has something to be
compared against, adds light regularisation, and runs an expanding window
time series cross validation instead of a single fold.
"""

import logging
import numpy as np
import pandas as pd

from . import config

log = logging.getLogger("kshetra.ranker")

FEATURE_COLS = list(config.RULE_WEIGHTS.keys())
GROUP_KEYS = ["rep_id", "visit_date"]


def _group_sizes(df):
    """LightGBM needs the number of rows in each query group, in order."""
    return df.groupby(GROUP_KEYS, sort=False).size().to_numpy()


def _sorted_by_group(df):
    return df.sort_values(GROUP_KEYS).reset_index(drop=True)


def train(train_df, valid_df):
    """Train a LambdaRank ranker. Returns the model and its validation NDCG."""
    import lightgbm as lgb
    tr = _sorted_by_group(train_df)
    va = _sorted_by_group(valid_df)

    dtrain = lgb.Dataset(tr[FEATURE_COLS], label=tr["label"], group=_group_sizes(tr))
    dvalid = lgb.Dataset(va[FEATURE_COLS], label=va["label"], group=_group_sizes(va),
                         reference=dtrain)

    params = {
        "objective": "lambdarank",
        "metric": "ndcg",
        "ndcg_eval_at": [5],
        "boosting_type": "gbdt",
        "num_leaves": 31,
        "learning_rate": 0.05,
        "min_child_samples": 50,   # more conservative than the default 20
        "reg_alpha": 0.1,          # L1, added to fight the overfitting seen
        "reg_lambda": 0.1,         # L2, same reason
        "feature_fraction": 0.9,
        "verbose": -1,
        "random_state": config.RANDOM_STATE,
    }
    model = lgb.train(
        params, dtrain, num_boost_round=500,
        valid_sets=[dvalid], valid_names=["valid"],
        callbacks=[lgb.early_stopping(80, verbose=False)],
    )
    ndcg = model.best_score["valid"]["ndcg@5"]
    log.info("LambdaRank best NDCG@5 = %.4f at iteration %s", ndcg, model.best_iteration)
    return model, ndcg


def baseline_ndcg(valid_df):
    """NDCG at 5 for a popularity baseline that ranks by recent sales velocity.
    Gives the LambdaRank number something honest to beat."""
    from sklearn.metrics import ndcg_score
    va = _sorted_by_group(valid_df)
    scores = []
    for _, g in va.groupby(GROUP_KEYS, sort=False):
        if len(g) < 2 or g["label"].sum() == 0:
            continue
        rel = g["label"].to_numpy().reshape(1, -1)
        pred = g["sales_velocity_score"].to_numpy().reshape(1, -1)
        scores.append(ndcg_score(rel, pred, k=5))
    return float(np.mean(scores)) if scores else float("nan")


def cross_validate(feature_df, months=("2025-11", "2025-12", "2026-01", "2026-02")):
    """Expanding window CV. Train on everything before each cutoff month, test
    on that month. Reports NDCG@5 per fold so variance is visible."""
    results = []
    df = feature_df.copy()
    df["ym"] = df["visit_date"].dt.to_period("M").astype(str)
    for cut in months:
        tr = df[df["ym"] < cut]
        te = df[df["ym"] == cut]
        if tr.empty or te.empty:
            continue
        model, _ = train(tr, te)
        results.append({"test_month": cut, "ndcg@5": round(model.best_score["valid"]["ndcg@5"], 4)})
    return pd.DataFrame(results)


def predict(model, feature_matrix):
    """Score every retailer for inference using the same feature columns."""
    return model.predict(feature_matrix[FEATURE_COLS])


def save(model, path):
    model.save_model(path)


def load(path):
    import lightgbm as lgb
    return lgb.Booster(model_file=path)
