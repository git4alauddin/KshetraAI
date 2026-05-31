"""
generate_data.py

Makes the whole project self contained. Generates eight synthetic CSV files
that match the schema the pipeline expects, so anyone can clone the repo and
run it without needing any proprietary dataset. The numbers are made up but
the shapes and relationships are realistic: retailers belong to territories,
visits happen at tehsil level, POS transactions link back to retailers, and
growers carry crop calendars.

Run it once before the pipeline:

    python generate_data.py
    python run_pipeline.py

Everything lands in raw_data/. Re run any time to get a fresh dataset.
"""

import os
import json
import random
import argparse
import numpy as np
import pandas as pd

from src import config

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Geography. Each district sits in a state. Tehsils are numbered within a district.
GEO = [
    ("Maharashtra", "Akola"), ("Maharashtra", "Amravati"),
    ("Haryana", "Hisar"), ("Haryana", "Sirsa"),
    ("Bihar", "Patna"), ("Bihar", "Muzaffarpur"),
    ("Punjab", "Ludhiana"), ("Punjab", "Bathinda"),
    ("Madhya Pradesh", "Sehore"), ("Madhya Pradesh", "Ujjain"),
    ("Uttar Pradesh", "Varanasi"), ("Uttar Pradesh", "Agra"),
    ("Rajasthan", "Bharatpur"), ("Rajasthan", "Jaipur"),
    ("Gujarat", "Ahmedabad"), ("Gujarat", "Rajkot"),
]

CROPS = ["wheat", "mustard", "chickpea", "potato", "barley", "lentil"]

# Products. The four campaign products plus a few others so POS has variety.
CAMPAIGN = config.CAMPAIGN_PRODUCTS
OTHER_PRODUCTS = ["Tilt 250 EC", "Vertimec 1.8 EC", "Amistar 250 SC", "Axial 5 EC"]
ALL_PRODUCTS = CAMPAIGN + OTHER_PRODUCTS

# Crop stage templates. Approx dates within the Rabi season for each crop.
STAGE_TEMPLATES = {
    "wheat":    [("tillering", "2025-12-20"), ("flowering", "2026-01-25"), ("grain_filling", "2026-02-20")],
    "mustard":  [("vegetative", "2025-12-10"), ("flowering", "2026-01-15"), ("pod_formation", "2026-02-10")],
    "chickpea": [("vegetative", "2025-12-15"), ("flowering", "2026-01-20"), ("pod_formation", "2026-02-15")],
    "potato":   [("vegetative", "2025-12-05"), ("tuber_initiation", "2026-01-10")],
    "barley":   [("tillering", "2025-12-22"), ("flowering", "2026-01-28")],
    "lentil":   [("vegetative", "2025-12-18"), ("pod_formation", "2026-02-05")],
}


def make_geography(n_territories, tehsils_per_territory):
    """Assign territories to districts and give each a set of tehsils."""
    rows = []
    for t in range(n_territories):
        state, district = GEO[t % len(GEO)]
        terr_id = f"TER_{t:04d}"
        tehsils = [f"{district}_T{t * tehsils_per_territory + j:03d}" for j in range(tehsils_per_territory)]
        rows.append({"territory_id": terr_id, "state": state, "district": district, "tehsils": tehsils})
    return rows


def gen_retailers(geo, retailers_per_territory):
    rid = 0
    rows = []
    for g in geo:
        for _ in range(retailers_per_territory):
            tehsil = random.choice(g["tehsils"])
            rows.append({
                "retailer_id": f"RTL_{rid:05d}",
                "territory_id": g["territory_id"],
                "state": g["state"],
                "district": g["district"],
                "tehsil": tehsil,
            })
            rid += 1
    return pd.DataFrame(rows)


def gen_reps(geo):
    rows = []
    for i, g in enumerate(geo):
        rows.append({
            "rep_id": f"REP_{i:03d}",
            "territory_id": g["territory_id"],
            "tehsil_list": json.dumps(g["tehsils"]),
        })
    return pd.DataFrame(rows)


def gen_visit_log(geo, n_weeks):
    """Visits at tehsil level. Each territory gets a few visits per week."""
    rows = []
    start = pd.Timestamp("2025-10-01")
    for g in geo:
        for w in range(n_weeks):
            visit_date = start + pd.Timedelta(weeks=w) + pd.Timedelta(days=random.randint(0, 5))
            n_visits = random.randint(1, 3)
            for _ in range(n_visits):
                rows.append({
                    "visit_date": visit_date,
                    "territory_id": g["territory_id"],
                    "visit_tehsil": random.choice(g["tehsils"]),
                    "product_recommended": random.choice(ALL_PRODUCTS),
                })
    return pd.DataFrame(rows)


def gen_inventory(retailers, n_weeks):
    """Weekly stock snapshot per retailer per SKU. Some go to zero (stockout)."""
    rows = []
    start = pd.Timestamp("2025-10-05")
    for _, r in retailers.iterrows():
        base_stock = {p: random.randint(5, 40) for p in ALL_PRODUCTS}
        for w in range(n_weeks):
            week_end = start + pd.Timedelta(weeks=w)
            for p in ALL_PRODUCTS:
                # stock drifts down over weeks, occasionally restocked
                drift = random.randint(-4, 2)
                base_stock[p] = max(0, base_stock[p] + drift)
                if random.random() < 0.1:
                    base_stock[p] = random.randint(20, 40)  # restock event
                rows.append({
                    "retailer_id": r["retailer_id"],
                    "week_end_date": week_end,
                    "sku_name": p,
                    "sku_qty": base_stock[p],
                })
    return pd.DataFrame(rows)


def gen_pos(retailers, n_weeks):
    """POS transactions. Price mostly stable, with a few outliers for anomaly demo."""
    rows = []
    start = pd.Timestamp("2025-10-03")
    base_price = {p: random.choice([480, 520, 610, 750, 900]) for p in ALL_PRODUCTS}
    for _, r in retailers.iterrows():
        for w in range(n_weeks):
            txn_date = start + pd.Timedelta(weeks=w) + pd.Timedelta(days=random.randint(0, 6))
            n_txn = np.random.poisson(2)
            for _ in range(n_txn):
                p = random.choice(ALL_PRODUCTS)
                price = base_price[p]
                # 3 percent of transactions are price outliers (parallel market / data error)
                if random.random() < 0.03:
                    price = int(price * random.choice([0.5, 3.5, 4.0]))
                rows.append({
                    "retailer_id": r["retailer_id"],
                    "transaction_date": txn_date,
                    "sku_name": p,
                    "sku_qty": random.randint(1, 8),
                    "sku_price": price,
                })
    return pd.DataFrame(rows)


def gen_growers(geo, growers_per_territory):
    rows = []
    gid = 0
    for g in geo:
        for _ in range(growers_per_territory):
            crop = random.choice(CROPS)
            tehsil = random.choice(g["tehsils"])
            # 7.5 percent of growers have a broken/empty calendar (realistic data quality)
            if random.random() < 0.075:
                calendar = {}
            else:
                calendar = {
                    "crop": crop,
                    "stages": [{"stage": s, "approx": d} for s, d in STAGE_TEMPLATES[crop]],
                }
            scanned = random.random() < 0.18
            rows.append({
                "grower_id": f"GRW_{gid:05d}",
                "territory_id": g["territory_id"],
                "tehsil": tehsil,
                "grower_crop_calendar": json.dumps(calendar),
                "grower_farm_size": round(random.uniform(0.5, 8.0), 2) if random.random() > 0.124 else np.nan,
                "product_scan": scanned,
                "product_name": random.choice(ALL_PRODUCTS) if scanned else np.nan,
                "product_scan_datetime": pd.Timestamp("2026-01-10") if scanned else pd.NaT,
                "campaign_attendance_date": pd.NaT,
            })
            gid += 1
    return pd.DataFrame(rows)


def gen_whatsapp(growers, n_weeks):
    """WhatsApp engagement for the ~75 percent of growers on smartphones."""
    rows = []
    start = pd.Timestamp("2025-10-07")
    smartphone = growers.sample(frac=0.75, random_state=SEED)
    for _, gr in smartphone.iterrows():
        for w in range(0, n_weeks, 2):  # message every other week
            sent = start + pd.Timedelta(weeks=w)
            delivered = random.random() < 0.95
            opened = delivered and random.random() < 0.6
            clicked = opened and random.random() < 0.35
            rows.append({
                "grower_id": gr["grower_id"],
                "message_sent_date": sent,
                "delivered_status": int(delivered),
                "opened_status": int(opened),
                "clicked_status": int(clicked),
            })
    return pd.DataFrame(rows)


def gen_funnel(n_weeks):
    rows = []
    start = pd.Timestamp("2025-10-01")
    for w in range(n_weeks):
        rows.append({
            "week_start_date": start + pd.Timedelta(weeks=w),
            "impressions": random.randint(5000, 20000),
            "clicks": random.randint(200, 1500),
            "leads": random.randint(20, 150),
        })
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(description="Generate synthetic field force data")
    ap.add_argument("--territories", type=int, default=40, help="number of territories")
    ap.add_argument("--retailers-per-territory", type=int, default=10)
    ap.add_argument("--growers-per-territory", type=int, default=15)
    ap.add_argument("--tehsils-per-territory", type=int, default=4)
    ap.add_argument("--weeks", type=int, default=26, help="weeks of history (Rabi season)")
    args = ap.parse_args()

    os.makedirs(config.RAW, exist_ok=True)
    print(f"generating data into {config.RAW}")

    geo = make_geography(args.territories, args.tehsils_per_territory)

    retailers = gen_retailers(geo, args.retailers_per_territory)
    reps = gen_reps(geo)
    visit_log = gen_visit_log(geo, args.weeks)
    inventory = gen_inventory(retailers, args.weeks)
    pos = gen_pos(retailers, args.weeks)
    growers = gen_growers(geo, args.growers_per_territory)
    whatsapp = gen_whatsapp(growers, args.weeks)
    funnel = gen_funnel(args.weeks)

    files = {
        "retailers.csv": retailers,
        "reps_territory.csv": reps,
        "retailer_visit_log.csv": visit_log,
        "retailer_inventory_weekly.csv": inventory,
        "retailer_pos.csv": pos,
        "growers.csv": growers,
        "whatsapp_campaign.csv": whatsapp,
        "digital_funnel_weekly.csv": funnel,
    }
    for name, df in files.items():
        path = os.path.join(config.RAW, name)
        df.to_csv(path, index=False)
        print(f"  {name:35} {len(df):>8,} rows")

    print("\ndone. now run: python run_pipeline.py")


if __name__ == "__main__":
    main()
