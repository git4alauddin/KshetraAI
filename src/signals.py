"""
Signal definitions. There is exactly one implementation of each signal here,
and both the training feature builder and the inference feature builder call
these same functions. That is the fix for the train versus inference mismatch
in the original code, where the model trained on per-visit time-varying
features but scored production retailers on differently computed static ones.

Every signal takes an as_of date and only looks at data on or before it. That
keeps the features point in time and avoids leakage from the future.

Note on granularity, stated plainly: the visit log records activity at the
territory and tehsil level, not per retailer. So the days-since-visit and
product-gap signals are tehsil level and are shared by all retailers in a
tehsil. The stock, sales and engagement signals are genuinely per retailer.
"""

import numpy as np
import pandas as pd

from . import config


def _safe_minmax(s):
    """Scale a series to 0..1. Returns zeros if the range is degenerate."""
    lo, hi = s.min(), s.max()
    if not np.isfinite(lo) or not np.isfinite(hi) or hi - lo < 1e-12:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - lo) / (hi - lo)


def days_since_visit(retailers, visit_log, as_of):
    """Tehsil level recency. Older last-visit means higher score."""
    as_of = pd.Timestamp(as_of)
    vl = visit_log[visit_log["visit_date"] <= as_of]
    last = (
        vl.groupby(["territory_id", "visit_tehsil"])["visit_date"]
        .max()
        .reset_index()
        .rename(columns={"visit_tehsil": "tehsil", "visit_date": "last_visit"})
    )
    out = retailers[["retailer_id", "territory_id", "tehsil"]].merge(
        last, on=["territory_id", "tehsil"], how="left"
    )
    earliest = vl["visit_date"].min() if len(vl) else as_of
    out["last_visit"] = out["last_visit"].fillna(earliest)
    out["days"] = (as_of - out["last_visit"]).dt.days.clip(lower=0)
    out["days_since_visit_score"] = _safe_minmax(out["days"])
    return out[["retailer_id", "days_since_visit_score"]]


def stock_urgency(retailers, inventory, as_of):
    """Low stock plus stockouts at the latest snapshot on or before as_of."""
    as_of = pd.Timestamp(as_of)
    inv = inventory[inventory["week_end_date"] <= as_of]
    if inv.empty:
        return _zero_signal(retailers, "stock_urgency_score")
    latest_week = inv["week_end_date"].max()
    snap = inv[inv["week_end_date"] == latest_week]
    g = snap.groupby("retailer_id").agg(
        total_stock=("sku_qty", "sum"),
        stockout_count=("sku_qty", lambda x: int((x == 0).sum())),
        sku_count=("sku_qty", "count"),
    ).reset_index()
    g["stockout_rate"] = g["stockout_count"] / g["sku_count"].clip(lower=1)
    g["low_stock"] = 1 - _safe_minmax(g["total_stock"])
    g["stock_urgency_score"] = 0.5 * g["low_stock"] + 0.5 * g["stockout_rate"]
    out = retailers[["retailer_id"]].merge(
        g[["retailer_id", "total_stock", "stock_urgency_score"]],
        on="retailer_id", how="left",
    )
    return out


def sales_velocity(retailers, pos, as_of):
    """Recent 4 week sales scaled to 0..1. Higher means more active."""
    as_of = pd.Timestamp(as_of)
    recent_cut = as_of - pd.Timedelta(days=28)
    recent = (
        pos[(pos["transaction_date"] <= as_of) & (pos["transaction_date"] > recent_cut)]
        .groupby("retailer_id")["sku_qty"].sum().reset_index()
        .rename(columns={"sku_qty": "recent_4w_sales"})
    )
    out = retailers[["retailer_id"]].merge(recent, on="retailer_id", how="left")
    out["recent_4w_sales"] = out["recent_4w_sales"].fillna(0)
    out["sales_velocity_score"] = _safe_minmax(out["recent_4w_sales"])
    return out[["retailer_id", "recent_4w_sales", "sales_velocity_score"]]


def stock_decline(retailers, inventory, as_of):
    """Drop in total stock over the four weeks before as_of."""
    as_of = pd.Timestamp(as_of)
    window = inventory[
        (inventory["week_end_date"] <= as_of)
        & (inventory["week_end_date"] > as_of - pd.Timedelta(days=28))
    ]
    if window.empty:
        return _zero_signal(retailers, "stock_decline_score")
    weekly = window.groupby(["retailer_id", "week_end_date"])["sku_qty"].sum().reset_index()
    first = weekly.sort_values("week_end_date").groupby("retailer_id").first()["sku_qty"]
    last = weekly.sort_values("week_end_date").groupby("retailer_id").last()["sku_qty"]
    decline = (first - last).rename("decline").reset_index()
    decline["decline_pos"] = decline["decline"].clip(lower=0)
    decline["stock_decline_score"] = _safe_minmax(decline["decline_pos"])
    return retailers[["retailer_id"]].merge(
        decline[["retailer_id", "stock_decline_score"]], on="retailer_id", how="left"
    )


def product_gap(retailers, visit_log, as_of, campaign_products):
    """Tehsil level. Fraction of campaign products never pitched there."""
    as_of = pd.Timestamp(as_of)
    vl = visit_log[visit_log["visit_date"] <= as_of]
    pitched = vl.groupby("territory_id")["product_recommended"].apply(set).reset_index()
    n = len(campaign_products)
    pitched["product_gap_score"] = pitched["product_recommended"].apply(
        lambda s: sum(1 for p in campaign_products if p not in s) / n
    )
    return retailers[["retailer_id", "territory_id"]].merge(
        pitched[["territory_id", "product_gap_score"]], on="territory_id", how="left"
    )[["retailer_id", "product_gap_score"]]


def grower_engagement(retailers, whatsapp, growers, as_of):
    """Tehsil level WhatsApp engagement, smartphone growers only by nature."""
    as_of = pd.Timestamp(as_of)
    wa = whatsapp[whatsapp["message_sent_date"] <= as_of].copy()
    if wa.empty:
        return _zero_signal(retailers, "grower_engagement_score")
    wa["eng"] = (
        wa.get("delivered_status", 0).astype(float) * 0.2
        + wa.get("opened_status", 0).astype(float) * 0.4
        + wa.get("clicked_status", 0).astype(float) * 0.4
    )
    wa = wa.merge(growers[["grower_id", "tehsil"]], on="grower_id", how="left")
    teh = wa.groupby("tehsil")["eng"].mean().reset_index()
    teh = teh.rename(columns={"eng": "grower_engagement_score"})
    out = retailers[["retailer_id", "tehsil"]].merge(teh, on="tehsil", how="left")
    return out[["retailer_id", "grower_engagement_score"]]


def crop_stage(retailers, growers, as_of):
    """How close the dominant crop in a tehsil is to a sensitive stage."""
    as_of = pd.Timestamp(as_of)
    importance = {
        "wheat": {"tillering": 0.7, "flowering": 1.0},
        "mustard": {"flowering": 1.0},
        "chickpea": {"pod_formation": 1.0},
        "potato": {"tuber_initiation": 0.8},
        "barley": {"tillering": 0.7, "flowering": 0.9},
        "lentil": {"pod_formation": 0.9},
    }

    def score(cal):
        if not isinstance(cal, dict) or not cal:
            return 0.2
        crop = cal.get("crop", "")
        stages = cal.get("stages", [])
        if crop not in importance or not stages:
            return 0.2
        best = 0.0
        for st in stages:
            name = st.get("stage", "")
            try:
                d = pd.Timestamp(st.get("approx", "2000-01-01"))
            except (ValueError, TypeError):
                continue
            diff = abs((as_of - d).days)
            if diff <= 60:
                imp = importance.get(crop, {}).get(name, 0.3)
                best = max(best, imp * max(0.0, 1 - diff / 60))
        return best if best > 0 else 0.2

    growers = growers.copy()
    growers["stage_score"] = growers["grower_crop_calendar"].apply(score)
    teh = growers.groupby("tehsil")["stage_score"].mean().reset_index()
    teh = teh.rename(columns={"stage_score": "crop_stage_score"})
    return retailers[["retailer_id", "tehsil"]].merge(
        teh, on="tehsil", how="left"
    )[["retailer_id", "crop_stage_score"]]


def weather_risk(retailers, weather, as_of):
    """District level fungal and rainfall risk from the last seven days."""
    as_of = pd.Timestamp(as_of)
    w = weather[
        (weather["date"] <= as_of) & (weather["date"] > as_of - pd.Timedelta(days=7))
    ]
    if w.empty:
        out = _zero_signal(retailers, "weather_risk_score")
        out["avg_humidity"] = np.nan
        return out
    ref = w.groupby("district").agg(
        avg_humidity=("humidity_max", "mean"),
        avg_temp=("temp_max", "mean"),
        total_rain=("precipitation", "sum"),
    ).reset_index()
    ref["fungal"] = (ref["avg_humidity"] / 100).clip(0, 1)
    ref["rain"] = _safe_minmax(ref["total_rain"])
    ref["heat"] = ((ref["avg_temp"] - 25) / 20).clip(0, 1)
    ref["weather_risk_score"] = 0.5 * ref["fungal"] + 0.3 * ref["rain"] + 0.2 * ref["heat"]
    return retailers[["retailer_id", "district"]].merge(
        ref[["district", "weather_risk_score", "avg_humidity"]], on="district", how="left"
    )[["retailer_id", "weather_risk_score", "avg_humidity"]]


def ndvi_proxy(crop_stage_score, avg_humidity):
    """A proxy, not a satellite reading.

    Real NDVI from MODIS or Sentinel was attempted but the imagery service was
    not reliably available, so this estimates a crop-health-like value from
    crop stage and humidity. It is labelled a proxy everywhere it appears, and
    it carries the smallest weight in the rule scorer for that reason.
    """
    hum = pd.Series(avg_humidity).fillna(60) / 100.0
    val = 0.25 + crop_stage_score.fillna(0.2) * 0.45 + hum * 0.30
    return val.clip(0.1, 0.9)


def _zero_signal(retailers, col):
    out = retailers[["retailer_id"]].copy()
    out[col] = 0.0
    return out
