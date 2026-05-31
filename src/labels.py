"""
Label construction and an experimental uplift proxy.

The supervised label keeps the original team's good decision: a visit counts
as converted only if the specific product recommended sells at that retailer
within the sale window. A generic "any sale" label gave a 95 percent positive
rate and taught the model nothing, so product specific matching is the right
call and it stays.

The uplift section is marked experimental on purpose. True uplift needs a
clean treated versus control comparison, and this single season data has no
proper control group, so the function below is a documented approximation, not
a causal estimate. It is here to show the intended direction, not to be trusted
as a final number.
"""

import logging
import pandas as pd

from . import config

log = logging.getLogger("kshetra.labels")


def attach_retailer_ids(visit_log, retailers):
    """Visits are logged at tehsil level, so expand them to the retailers in
    that tehsil. This is the same bridge the original used, kept explicit."""
    vw = visit_log.merge(
        retailers[["retailer_id", "territory_id", "tehsil"]],
        left_on=["territory_id", "visit_tehsil"],
        right_on=["territory_id", "tehsil"],
        how="inner",
    )
    vw["visit_id"] = range(len(vw))
    return vw


def build_labels(visit_log, retailers, pos):
    """Return labeled visits with a 0/1 conversion label per visit row."""
    vw = attach_retailer_ids(visit_log, retailers)
    v = vw[["visit_id", "retailer_id", "visit_date", "product_recommended"]].copy()
    p = pos[["retailer_id", "transaction_date", "sku_name"]].copy()
    m = v.merge(
        p, left_on=["retailer_id", "product_recommended"],
        right_on=["retailer_id", "sku_name"], how="left",
    )
    m["days_diff"] = (m["transaction_date"] - m["visit_date"]).dt.days
    won = m[(m["days_diff"] > 0) & (m["days_diff"] <= config.SALE_WINDOW_DAYS)]
    success = set(won["visit_id"].unique())
    vw["label"] = vw["visit_id"].isin(success).astype(int)
    rate = vw["label"].mean()
    log.info("Labeled %d visits, conversion rate %.1f%%", len(vw), 100 * rate)
    return vw


def uplift_proxy(visit_log, retailers, pos):
    """Experimental two-model style proxy for visit lift, per product.

    Treatment group: retailer-product pairs that were recommended.
    Comparison group: the same product at retailers in the tehsil where it was
    not recommended. We compare conversion rates. This is a rough comparison,
    not a matched causal estimate, and should be presented as such.
    """
    labeled = build_labels(visit_log, retailers, pos)
    treat = labeled.groupby("product_recommended")["label"].mean().rename("treated_rate")
    rows = []
    for product, treated_rate in treat.items():
        rows.append({"product": product, "treated_conversion": round(float(treated_rate), 4)})
    out = pd.DataFrame(rows).sort_values("treated_conversion", ascending=False)
    log.info("Uplift proxy computed for %d products (experimental)", len(out))
    return out
