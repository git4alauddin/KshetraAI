"""
evaluation.py

This is the part that actually matters. Anyone can rank retailers. The harder
question is: are the recommendations any good, and how do you know?

Four things get measured here:

  1. precision_at_k       did the retailers we put at the top actually convert
  2. explanation_faithfulness  do the SHAP reasons line up with real outcomes
  3. rep_acceptance_vs_outcome when reps follow the model, do they do better
  4. golden_dataset_eval  score the model against hand labelled "correct" cases

The first three read from the pipeline outputs and the SEEKHO outcome log. The
fourth reads data/golden_dataset.json, which is a small set of field situations
with a known right answer. Together they give an honest picture of quality
instead of a single accuracy number that hides everything.

Run it after the pipeline:

    python -m src.evaluation
"""

import os
import json
import logging
import numpy as np
import pandas as pd

from src import config

log = logging.getLogger("kshetra.eval")


def _read(path):
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()


# ---------------------------------------------------------------------------
# 1. Precision at k
# ---------------------------------------------------------------------------
def precision_at_k(scores, outcomes, k=6, horizon_days=14):
    """
    Of the top k retailers we recommended per territory, what fraction actually
    converted (made a sale) within the horizon. This is the headline number a
    sales manager cares about: if I follow the top six, how many were worth it.

    scores   : final_scores.csv (retailer_id, territory_id, final_score_100)
    outcomes : visit_outcomes.csv (retailer_id, sale_made, ...)
    """
    if scores.empty or outcomes.empty:
        return {"k": k, "precision_at_k": None, "note": "missing scores or outcomes"}

    converted = set(outcomes.loc[outcomes["sale_made"] == 1, "retailer_id"])
    hits, total = 0, 0
    for _, grp in scores.groupby("territory_id"):
        topk = grp.nlargest(k, "final_score_100")["retailer_id"]
        for rid in topk:
            total += 1
            if rid in converted:
                hits += 1
    return {
        "k": k,
        "precision_at_k": round(hits / total, 4) if total else None,
        "top_k_evaluated": total,
        "converters_in_set": hits,
    }


# ---------------------------------------------------------------------------
# 2. Explanation faithfulness
# ---------------------------------------------------------------------------
def explanation_faithfulness(scores, shap_df, outcomes):
    """
    SHAP tells us which signal pushed a retailer up the list. If the system is
    being honest, the signal it leans on should actually relate to the outcome.

    Simple version: for retailers where the top SHAP signal was stock urgency,
    check whether they converted more often than the base rate. If the model
    says "I recommended this because stock was low" then low stock recommendations
    should convert better than random. If they do not, the explanation is decorative.

    Returns a per signal lift table. Lift above 1.0 means the signal is faithful.
    """
    if scores.empty or shap_df.empty or outcomes.empty:
        return pd.DataFrame()

    converted = set(outcomes.loc[outcomes["sale_made"] == 1, "retailer_id"])
    base_rate = len(converted) / scores["retailer_id"].nunique() if scores["retailer_id"].nunique() else 0

    shap_cols = [c for c in shap_df.columns if c.startswith("shap_")]
    if not shap_cols:
        return pd.DataFrame()

    # top signal per retailer
    top_signal = {}
    for _, row in shap_df.iterrows():
        vals = {c.replace("shap_", ""): row[c] for c in shap_cols}
        top = max(vals, key=lambda s: vals[s])
        top_signal[row["retailer_id"]] = top

    rows = []
    sig_groups = {}
    for rid, sig in top_signal.items():
        sig_groups.setdefault(sig, []).append(rid)

    for sig, rids in sig_groups.items():
        conv = sum(1 for r in rids if r in converted)
        rate = conv / len(rids) if rids else 0
        lift = round(rate / base_rate, 2) if base_rate else None
        rows.append({"signal": sig, "retailers": len(rids), "conversion_rate": round(rate, 3),
                     "lift_vs_base": lift, "faithful": (lift is not None and lift >= 1.0)})

    out = pd.DataFrame(rows).sort_values("lift_vs_base", ascending=False)
    return out


# ---------------------------------------------------------------------------
# 3. Rep acceptance vs outcome
# ---------------------------------------------------------------------------
def rep_acceptance_vs_outcome(outcomes):
    """
    The number that proves the whole thing is worth running. Split outcomes into
    visits where the rep followed the recommendation (recommended_rank is small)
    versus visits where they went off plan, and compare the sale rate.

    If following the model does not beat going off plan, the model is not adding
    value and you should say so plainly.
    """
    if outcomes.empty or "recommended_rank" not in outcomes:
        return {"note": "no outcome data with rank"}

    followed = outcomes[outcomes["recommended_rank"].notna() & (outcomes["recommended_rank"] <= 6)]
    skipped = outcomes[outcomes["recommended_rank"].isna() | (outcomes["recommended_rank"] > 6)]

    def rate(df):
        return round(df["sale_made"].mean(), 3) if len(df) else None

    return {
        "followed_recommendation": {"visits": len(followed), "sale_rate": rate(followed)},
        "went_off_plan": {"visits": len(skipped), "sale_rate": rate(skipped)},
        "lift": (round(rate(followed) / rate(skipped), 2)
                 if rate(followed) and rate(skipped) else None),
    }


# ---------------------------------------------------------------------------
# 4. Golden dataset eval
# ---------------------------------------------------------------------------
def golden_dataset_eval(scorer_fn=None, golden_path=None):
    """
    The golden dataset is a handful of real field situations, each with a known
    right call (visit A or B, pitch this product, escalate this alert). It comes
    from talking to people who actually do the job, not from the data.

    Pass a scorer_fn(situation_dict) that returns the model's decision. If you do
    not pass one, this just reports how many cases are in the set and what they
    test, which is still useful as documentation of what "good" means here.
    """
    golden_path = golden_path or os.path.join(config.BASE, "data", "golden_dataset.json")
    if not os.path.exists(golden_path):
        return {"note": f"no golden dataset at {golden_path}"}

    cases = json.load(open(golden_path))["cases"]
    if scorer_fn is None:
        return {
            "cases": len(cases),
            "dimensions_tested": sorted({c["tests"] for c in cases}),
            "note": "pass a scorer_fn to actually score the model against these",
        }

    correct = 0
    details = []
    for c in cases:
        decision = scorer_fn(c["situation"])
        ok = decision == c["expected"]
        correct += int(ok)
        details.append({"id": c["id"], "tests": c["tests"], "expected": c["expected"],
                        "got": decision, "correct": ok})
    return {"cases": len(cases), "correct": correct,
            "accuracy": round(correct / len(cases), 3), "details": details}


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def run_full_eval():
    """Read pipeline outputs and run every check. Returns a dict you can dump to JSON."""
    scores = _read(os.path.join(config.OUTPUT, "final_scores.csv"))
    shap_df = _read(os.path.join(config.OUTPUT, "shap_values.csv"))
    outcomes = _read(os.path.join(config.OUTPUT, "visit_outcomes.csv"))

    report = {
        "precision_at_k": precision_at_k(scores, outcomes, k=config.VISITS_PER_TERRITORY),
        "rep_acceptance_vs_outcome": rep_acceptance_vs_outcome(outcomes),
        "golden_dataset": golden_dataset_eval(),
    }
    faith = explanation_faithfulness(scores, shap_df, outcomes)
    report["explanation_faithfulness"] = faith.to_dict(orient="records") if not faith.empty else []
    return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    rep = run_full_eval()
    print(json.dumps(rep, indent=2, default=str))
    out_path = os.path.join(config.OUTPUT, "evaluation_report.json")
    os.makedirs(config.OUTPUT, exist_ok=True)
    json.dump(rep, open(out_path, "w"), indent=2, default=str)
    log.info("wrote %s", out_path)
