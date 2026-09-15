"""
Smart Rerouting Engine for Urban Parking Systems.
Finds nearest available alternative parking lots when a lot is full or high demand.
"""

import math
from typing import List, Dict, Any


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great circle distance between two points on the Earth in kilometers.
    """
    R = 6371.0  # Earth radius in km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def find_alternative_lots(
    target_lot_id: str,
    all_lots: List[Dict[str, Any]],
    max_distance_km: float = 5.0,
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    Finds nearest alternative parking lots with available space (Occupancy < Capacity).
    Returns sorted by composite score combining distance and occupancy percentage.
    """
    target_lot = next((lot for lot in all_lots if lot["LotID"] == target_lot_id), None)
    if not target_lot:
        return []

    t_lat, t_lon = target_lot["Latitude"], target_lot["Longitude"]
    alternatives = []

    for lot in all_lots:
        if lot["LotID"] == target_lot_id:
            continue

        occ = lot.get("Occupancy", 0)
        cap = lot.get("Capacity", 1)

        # Only suggest lots with available capacity (< 95% full)
        if occ >= cap * 0.95:
            continue

        dist = haversine_distance(t_lat, t_lon, lot["Latitude"], lot["Longitude"])
        if dist <= max_distance_km:
            avail_pct = (cap - occ) / cap
            # Score: lower distance + higher availability is better
            score = dist - (avail_pct * 2.0)

            alternatives.append({
                "LotID": lot["LotID"],
                "LotName": lot.get("LotName", lot["LotID"]),
                "DistanceKM": round(dist, 2),
                "AvailableSpaces": cap - occ,
                "OccupancyPct": round((occ / cap) * 100, 1),
                "CurrentPrice": lot.get("CurrentPrice", lot.get("BasePrice", 10.0)),
                "Score": score
            })

    alternatives.sort(key=lambda x: x["Score"])
    return alternatives[:top_k]
