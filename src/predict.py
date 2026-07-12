"""
Serving. Score one retailer or produce a full beat plan for a territory.

This is the piece the original was missing. The model and feature columns were
saved but there was no function to turn them into a live recommendation. With
this, a demo can ask for any territory and get back an ordered, explained,
routed visit list.
"""

import logging
import pandas as pd

from . import config, features, scoring, ranker, explain, route

log = logging.getLogger("kshetra.predict")


def score_all(retailers, data, weather, model, as_of=None):
    """Build features, run the ranker, blend, and return scored retailers."""
    fm = features.build_inference_features(retailers, data, weather, as_of)
    ml = ranker.predict(model, fm)
    return scoring.hybrid_score(fm, ml)


def beat_plan(territory_id, scored, model, explainer=None, shap_df=None):
    """Return an ordered, explained visit plan for one territory."""
    routed = route.optimize_territory(scored, territory_id)
    if routed is None:
        return None
    plan = []
    for _, r in routed.iterrows():
        item = {
            "visit_order": int(r["visit_order"]),
            "retailer_id": r["retailer_id"],
            "tehsil": r["tehsil"],
            "crop": r.get("dominant_crop", r.get("crop", "")),
            "final_score": r["final_score_100"],
            "tier": scoring.tier(r["final_score_100"]),
            "route_km_indicative": r["route_km_indicative"],
        }
        if shap_df is not None:
            item["why"] = explain.explain_recommendation(r["retailer_id"], scored, shap_df)
        plan.append(item)
    return {"territory_id": territory_id, "stops": plan}


def score_one_retailer(retailer_id, scored):
    """Convenience lookup for a single retailer's score and rank."""
    row = scored[scored["retailer_id"] == retailer_id]
    if row.empty:
        return None
    row = row.iloc[0]
    return {
        "retailer_id": retailer_id,
        "final_score": float(row["final_score_100"]),
        "tier": scoring.tier(row["final_score_100"]),
        "territory_rank": int(row["final_rank"]),
    }
