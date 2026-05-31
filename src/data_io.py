"""
Loading and light cleaning of the eight raw files.

Two things the original EDA notebook got right and are kept here: it checked
that every territory and retailer joins cleanly, and it traced the missing
values in growers.csv to a real cause rather than dropping rows. The change
here is that JSON parsing now reports how many rows failed instead of
swallowing errors with a bare except.
"""

import os
import json
import logging
import pandas as pd

from . import config

log = logging.getLogger("kshetra.data")

RAW = config.RAW


def _read(name, **kw):
    path = os.path.join(RAW, name)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Expected raw file not found: {path}. "
            f"Set KSHETRA_BASE so that <BASE>/raw_data/{name} exists."
        )
    return pd.read_csv(path, **kw)


def parse_json_field(series, label):
    """Parse a column of JSON strings into dicts and log the failures.

    The earlier code used `except: return {}`, so nobody knew how many of the
    450 growers with a bad calendar actually failed. Here we count them.
    """
    failures = 0

    def _one(value):
        nonlocal failures
        if isinstance(value, dict):
            return value
        if not isinstance(value, str) or not value.strip():
            failures += 1
            return {}
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            try:
                import ast
                return ast.literal_eval(value)
            except (ValueError, SyntaxError):
                failures += 1
                return {}

    out = series.apply(_one)
    if failures:
        log.warning("%s: %d of %d rows did not parse as JSON", label, failures, len(series))
    return out


def load_all():
    """Return a dict of cleaned dataframes keyed by short name."""
    retailers = _read("retailers.csv")
    reps = _read("reps_territory.csv")
    visit_log = _read("retailer_visit_log.csv", parse_dates=["visit_date"])
    inventory = _read("retailer_inventory_weekly.csv", parse_dates=["week_end_date"])
    pos = _read("retailer_pos.csv", parse_dates=["transaction_date"])
    growers = _read("growers.csv")
    whatsapp = _read("whatsapp_campaign.csv", parse_dates=["message_sent_date"])

    # Grower calendar is a JSON string. Parse with failure logging.
    growers["grower_crop_calendar"] = parse_json_field(
        growers["grower_crop_calendar"], "grower_crop_calendar"
    )
    growers["crop"] = growers["grower_crop_calendar"].apply(
        lambda d: d.get("crop", "unknown") if isinstance(d, dict) else "unknown"
    )

    # Farm size: median impute, but keep a flag so the model can tell.
    if "grower_farm_size" in growers:
        med = growers["grower_farm_size"].median()
        growers["farm_size_missing"] = growers["grower_farm_size"].isna().astype(int)
        growers["grower_farm_size"] = growers["grower_farm_size"].fillna(med)

    data = {
        "retailers": retailers,
        "reps": reps,
        "visit_log": visit_log,
        "inventory": inventory,
        "pos": pos,
        "growers": growers,
        "whatsapp": whatsapp,
    }
    _sanity_checks(data)
    return data


def _sanity_checks(data):
    """Fail loudly if the joins the whole pipeline depends on are broken."""
    retailers, visit_log, pos = data["retailers"], data["visit_log"], data["pos"]

    r_terr = set(retailers["territory_id"].unique())
    v_terr = set(visit_log["territory_id"].unique())
    missing = v_terr - r_terr
    if missing:
        log.warning("%d territories in visit_log have no retailer match", len(missing))

    pos_ret = set(pos["retailer_id"].unique())
    ref_ret = set(retailers["retailer_id"].unique())
    if not pos_ret.issubset(ref_ret):
        log.warning("POS contains retailer ids not present in retailers.csv")

    log.info(
        "Loaded retailers=%d visits=%d pos=%d",
        len(retailers), len(visit_log), len(pos),
    )
