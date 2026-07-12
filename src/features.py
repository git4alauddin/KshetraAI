"""
Feature assembly. Both entry points below build the same nine signals from the
functions in signals.py. The only difference is the as_of date: inference uses
a single reference date for every retailer, training uses each visit's own date
(bucketed by week for speed) so the features are what the rep would have seen
at the time. Same definitions, no train versus inference drift.
"""

import logging
import numpy as np
import pandas as pd

from . import config, signals

log = logging.getLogger("kshetra.features")

SIGNAL_COLS = list(config.RULE_WEIGHTS.keys())


def _assemble(retailers, data, weather, as_of):
    """Compute all nine signal columns for every retailer as of one date."""
    r = retailers
    s1 = signals.days_since_visit(r, data["visit_log"], as_of)
    s2 = signals.stock_urgency(r, data["inventory"], as_of)
    s3 = signals.sales_velocity(r, data["pos"], as_of)
    s4 = signals.stock_decline(r, data["inventory"], as_of)
    s5 = signals.product_gap(r, data["visit_log"], as_of, config.CAMPAIGN_PRODUCTS)
    s6 = signals.grower_engagement(r, data["whatsapp"], data["growers"], as_of)
    s7 = signals.crop_stage(r, data["growers"], as_of)
    s8 = signals.weather_risk(r, weather, as_of)

    fm = r[["retailer_id", "territory_id", "state", "district", "tehsil"]].copy()
    for part in (s1, s2, s3, s4, s5, s6, s7, s8):
        fm = fm.merge(part, on="retailer_id", how="left")

    fm["ndvi_proxy_score"] = signals.ndvi_proxy(fm["crop_stage_score"], fm["avg_humidity"])

    # Fill absent signals with 0 and record which were missing.
    for col in SIGNAL_COLS:
        if col not in fm:
            fm[col] = config.MISSING_FILL
        fm[col + "_missing"] = fm[col].isna().astype(int)
        fm[col] = fm[col].fillna(config.MISSING_FILL)
    return fm


def build_inference_features(retailers, data, weather, as_of=None):
    """Feature matrix for scoring all retailers on a single date."""
    as_of = pd.Timestamp(as_of or config.REFERENCE_DATE)
    log.info("Building inference features as of %s", as_of.date())
    return _assemble(retailers, data, weather, as_of)


def build_training_features(labeled_visits, retailers, data, weather):
    """Per-visit features, computed at the week boundary on or before each visit.

    Visits are grouped by ISO week so the signal functions run once per week
    rather than once per visit. Each visit then receives the signals as they
    stood that week, which is point in time and matches how inference works.
    """
    lv = labeled_visits.copy()
    lv["week"] = lv["visit_date"].dt.to_period("W").apply(lambda p: p.end_time.normalize())

    frames = []
    for week, chunk in lv.groupby("week"):
        fm = _assemble(retailers, data, weather, week)
        keep = ["retailer_id"] + SIGNAL_COLS
        merged = chunk.merge(fm[keep], on="retailer_id", how="left")
        frames.append(merged)

    out = pd.concat(frames, ignore_index=True)
    for col in SIGNAL_COLS:
        out[col] = out[col].fillna(config.MISSING_FILL)
    log.info("Training features built for %d visit rows", len(out))
    return out
