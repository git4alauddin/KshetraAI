"""
SHAP based explanations, the reasoning behind SALAH and the why on each card.

The original generated explanations with ad hoc string formatting inside the
dashboard. Here it is a single reusable function that takes a retailer and
returns the top reasons in plain language, so the same logic serves the
dashboard, the mobile card, and any audit.
"""

import logging
import numpy as np
import pandas as pd

from . import config

log = logging.getLogger("kshetra.explain")

FEATURE_COLS = list(config.RULE_WEIGHTS.keys())

# Human readable names for each signal, used in the rep facing explanation.
SIGNAL_LABELS = {
    "days_since_visit_score": "long gap since last visit",
    "stock_urgency_score": "low stock or stockout risk",
    "sales_velocity_score": "recent sales momentum",
    "stock_decline_score": "stock drawing down fast",
    "weather_risk_score": "weather driven disease risk",
    "product_gap_score": "campaign product not yet pitched here",
    "crop_stage_score": "crop near a sensitive stage",
    "grower_engagement_score": "growers engaging with campaigns",
    "ndvi_proxy_score": "crop health proxy",
}


def build_explainer(model):
    import shap
    return shap.TreeExplainer(model)


def shap_table(explainer, feature_matrix):
    """Return a dataframe of SHAP values, one row per retailer."""
    values = explainer.shap_values(feature_matrix[FEATURE_COLS])
    df = pd.DataFrame(values, columns=[f"shap_{c}" for c in FEATURE_COLS])
    df["retailer_id"] = feature_matrix["retailer_id"].to_numpy()
    return df


def explain_recommendation(retailer_id, feature_matrix, shap_df, top_k=3):
    """Plain language reasons for why a retailer is ranked where it is."""
    row = shap_df[shap_df["retailer_id"] == retailer_id]
    if row.empty:
        return {"retailer_id": retailer_id, "reasons": [], "watch": []}
    row = row.iloc[0]

    contrib = []
    for c in FEATURE_COLS:
        contrib.append((c, float(row[f"shap_{c}"])))
    contrib.sort(key=lambda x: abs(x[1]), reverse=True)

    reasons, watch = [], []
    for col, val in contrib[:top_k]:
        if val > 0:
            reasons.append(SIGNAL_LABELS.get(col, col))
    for col, val in contrib:
        if val < 0:
            watch.append(SIGNAL_LABELS.get(col, col))
            break

    return {"retailer_id": retailer_id, "reasons": reasons, "watch": watch}
