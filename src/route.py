"""
Route optimiser using Google OR-Tools.

The solver and the haversine distance are correct. The honest caveat, stated
here and in the documentation, is that retailer coordinates are approximated
from the district centre plus a small systematic offset per tehsil. They are
not GPS readings, so the distances are indicative. In a pilot these would be
replaced by real retailer locations from the CRM, after which the same solver
runs unchanged.
"""

import math
import re
import logging
import pandas as pd

from . import config

log = logging.getLogger("kshetra.route")


def approx_coords(district, tehsil):
    """Approximate a tehsil coordinate from its district centre. Indicative
    only, not GPS. Replace with real retailer coordinates for a pilot."""
    if district not in config.DISTRICT_COORDS:
        return (0.0, 0.0)
    base_lat, base_lon = config.DISTRICT_COORDS[district]
    nums = re.findall(r"\d+", str(tehsil))
    if not nums:
        return (base_lat, base_lon)
    n = int(nums[-1])
    lat = base_lat + (n % 10) * 0.05 - 0.25
    lon = base_lon + (n // 10) * 0.05 - 0.10
    return (round(lat, 4), round(lon, 4))


def haversine(lat1, lon1, lat2, lon2):
    """Great circle distance in kilometres."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def optimize_territory(scored, territory_id, top_n=None):
    """Return the top retailers in a territory in an optimised visit order."""
    from ortools.constraint_solver import routing_enums_pb2, pywrapcp
    top_n = top_n or config.VISITS_PER_TERRITORY
    terr = scored[scored["territory_id"] == territory_id].nlargest(top_n, "final_score_100").copy()
    if len(terr) < 2:
        return None

    coords = [approx_coords(d, t) for d, t in zip(terr["district"], terr["tehsil"])]
    n = len(coords)
    dist = [[0 if i == j else int(haversine(*coords[i], *coords[j]) * 1000)
             for j in range(n)] for i in range(n)]

    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    routing = pywrapcp.RoutingModel(manager)

    def cb(i, j):
        return dist[manager.IndexToNode(i)][manager.IndexToNode(j)]

    idx = routing.RegisterTransitCallback(cb)
    routing.SetArcCostEvaluatorOfAllVehicles(idx)
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.time_limit.seconds = config.ORTOOLS_TIME_LIMIT_SEC

    sol = routing.SolveWithParameters(params)
    if not sol:
        return None

    order, node = [], routing.Start(0)
    while not routing.IsEnd(node):
        order.append(manager.IndexToNode(node))
        node = sol.Value(routing.NextVar(node))

    out = terr.iloc[order].copy()
    out["visit_order"] = range(1, len(out) + 1)
    out["route_km_indicative"] = round(sol.ObjectiveValue() / 1000.0, 1)
    return out
