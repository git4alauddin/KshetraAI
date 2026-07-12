"""
Anomaly detection, the CHETAVANI module.

The important fix is in the demand spike. The original compared a monthly sum
of recent sales against a per-transaction historical average, which is a units
mismatch (a month against a day), so almost ninety percent of retailers were
flagged. Raising the threshold from 2x to 3x does not fix that, because the
ratio itself is malformed. Here both sides are weekly rates, so a 3x spike
means the recent weekly rate is three times the trailing weekly rate. Alerts
are also returned in priority order rather than as one flat list.
"""

import logging
import numpy as np
import pandas as pd

from . import config

log = logging.getLogger("kshetra.anomaly")


def price_anomalies(pos):
    """Flag retailer and SKU pairs whose price varies a lot around its mean."""
    g = pos.groupby(["retailer_id", "sku_name"])["sku_price"].agg(
        ["mean", "std", "min", "max"]
    ).reset_index()
    g["cv"] = (g["std"] / g["mean"]).fillna(0)
    flagged = g[g["cv"] > config.PRICE_ANOMALY_CV_THRESHOLD].copy()
    flagged = flagged.sort_values("cv", ascending=False)
    flagged["alert_type"] = "PRICE_ANOMALY"
    log.info("Price anomalies flagged: %d retailer-SKU pairs", len(flagged))
    return flagged


def demand_spikes(pos, as_of=None):
    """Compare recent weekly sales rate against the trailing weekly rate.

    recent rate  = units in the last DEMAND_SPIKE_RECENT_DAYS, per week
    baseline rate = units in the window before that, per week

    A retailer is flagged when recent rate is at least DEMAND_SPIKE_RATIO times
    the baseline rate. Same units on both sides, so the ratio is meaningful.
    """
    as_of = pd.Timestamp(as_of or config.DATA_LAST_DATE)
    recent_start = as_of - pd.Timedelta(days=config.DEMAND_SPIKE_RECENT_DAYS)
    base_start = recent_start - pd.Timedelta(days=config.DEMAND_SPIKE_BASELINE_DAYS)

    recent = pos[(pos["transaction_date"] <= as_of) & (pos["transaction_date"] > recent_start)]
    base = pos[(pos["transaction_date"] <= recent_start) & (pos["transaction_date"] > base_start)]

    recent_rate = recent.groupby("retailer_id")["sku_qty"].sum() / (config.DEMAND_SPIKE_RECENT_DAYS / 7)
    base_rate = base.groupby("retailer_id")["sku_qty"].sum() / (config.DEMAND_SPIKE_BASELINE_DAYS / 7)

    df = pd.DataFrame({"recent_weekly": recent_rate, "baseline_weekly": base_rate}).fillna(0)
    # Guard against divide by zero: require a real baseline before calling it a spike.
    df = df[df["baseline_weekly"] >= 1.0]
    df["spike_ratio"] = df["recent_weekly"] / df["baseline_weekly"]

    flagged = df[df["spike_ratio"] >= config.DEMAND_SPIKE_RATIO].copy()
    flagged = flagged.sort_values("spike_ratio", ascending=False).reset_index()
    flagged["alert_type"] = "DEMAND_SPIKE"
    log.info(
        "Demand spikes flagged: %d of %d retailers (%.1f%%)",
        len(flagged), pos["retailer_id"].nunique(),
        100 * len(flagged) / max(pos["retailer_id"].nunique(), 1),
    )
    return flagged


def build_alert_feed(pos, as_of=None, top_n=20):
    """Combine both anomaly types into one priority ordered feed for a rep.

    Priority is by normalised severity so the rep sees the sharpest signals
    first instead of scrolling a flat list of hundreds of alerts.
    """
    spikes = demand_spikes(pos, as_of)
    prices = price_anomalies(pos)

    feed = []
    for _, r in spikes.iterrows():
        feed.append({
            "retailer_id": r["retailer_id"], "alert_type": "DEMAND_SPIKE",
            "severity": float(min(r["spike_ratio"] / 10.0, 1.0)),
            "detail": f"recent weekly rate {r['recent_weekly']:.1f} vs baseline {r['baseline_weekly']:.1f}",
        })
    for _, r in prices.iterrows():
        feed.append({
            "retailer_id": r["retailer_id"], "alert_type": "PRICE_ANOMALY",
            "severity": float(min(r["cv"], 1.0)),
            "detail": f"{r['sku_name']} price {r['min']:.0f} to {r['max']:.0f}, cv {r['cv']:.2f}",
        })

    feed = pd.DataFrame(feed).sort_values("severity", ascending=False).head(top_n)
    return feed.reset_index(drop=True)
