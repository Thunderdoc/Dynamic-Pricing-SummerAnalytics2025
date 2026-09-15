"""
Core Dynamic Pricing Engine for Urban Parking Systems.
Implements:
- Model 1: Baseline Linear Pricing
- Model 2: Multi-Factor Demand-Based Dynamic Pricing
- Model 3: Geo-Distance Competitive Pricing
"""

from typing import Dict, Any, Union
import numpy as np
import pandas as pd


# Default Weights for Demand Score Calculation
DEFAULT_DEMAND_WEIGHTS = {
    'alpha': 1.0,   # Occupancy weight
    'beta': 0.6,    # Queue length weight
    'gamma': 0.4,   # Traffic condition penalty
    'delta': 0.7,   # Special day boost
    'epsilon': 0.8  # Vehicle type modifier
}

VEHICLE_WEIGHTS = {
    'car': 1.0,
    'bike': 0.5,
    'truck': 1.5
}

TRAFFIC_MAP = {
    'low': 1,
    'medium': 2,
    'high': 3
}


def linear_pricing(prev_price: float, occupancy: int, capacity: int, alpha: float = 1.5) -> float:
    """
    Model 1: Baseline Linear Pricing
    Price_t+1 = Price_t + alpha * (Occupancy / Capacity)
    """
    if capacity <= 0:
        return float(prev_price)
    utilization = min(max(occupancy / capacity, 0.0), 1.0)
    new_price = prev_price + alpha * utilization
    return round(float(new_price), 2)


def calculate_demand_score(
    occupancy: int,
    capacity: int,
    queue_length: int,
    traffic_condition: str,
    is_special_day: int,
    vehicle_type: str,
    weights: Dict[str, float] = None
) -> float:
    """
    Calculates composite demand score based on 5 core urban factors.
    Demand = alpha*(Occ/Cap) + beta*Queue - gamma*Traffic + delta*Special + epsilon*VehicleWeight
    """
    if weights is None:
        weights = DEFAULT_DEMAND_WEIGHTS

    occ_ratio = occupancy / capacity if capacity > 0 else 0.0
    traffic_val = TRAFFIC_MAP.get(str(traffic_condition).lower(), 2)
    v_weight = VEHICLE_WEIGHTS.get(str(vehicle_type).lower(), 1.0)
    special_val = 1.0 if is_special_day else 0.0

    demand = (
        weights.get('alpha', 1.0) * occ_ratio +
        weights.get('beta', 0.6) * queue_length -
        weights.get('gamma', 0.4) * traffic_val +
        weights.get('delta', 0.7) * special_val +
        weights.get('epsilon', 0.8) * v_weight
    )
    return float(demand)


def demand_based_pricing(
    base_price: float,
    demand_score: float,
    lam: float = 0.5,
    min_mult: float = 0.5,
    max_mult: float = 2.0
) -> float:
    """
    Model 2: Multi-Factor Demand-Based Pricing
    Price = BasePrice * (1 + lambda * (NormalizedDemand - 0.5))
    Bounded between [min_mult * BasePrice, max_mult * BasePrice]
    """
    # Normalize demand score assuming typical range [0, 10]
    norm_demand = min(max(demand_score / 10.0, 0.0), 1.0)
    price = base_price * (1.0 + lam * (norm_demand - 0.5))

    min_price = base_price * min_mult
    max_price = base_price * max_mult

    final_price = min(max(price, min_price), max_price)
    return round(float(final_price), 2)


def competitive_pricing(
    demand_price: float,
    competitor_price: float,
    comp_weight: float = 0.3
) -> float:
    """
    Model 3: Competitive Geo-Distance Adjusted Pricing
    Blends internal demand-based price with competitor pricing nearby.
    Price = (1 - comp_weight) * DemandPrice + comp_weight * CompetitorPrice
    """
    comp_price = (1.0 - comp_weight) * demand_price + comp_weight * competitor_price
    return round(float(comp_price), 2)


def calculate_price_for_row(row: Union[pd.Series, dict], model_type: str = "demand", weights: Dict[str, float] = None) -> float:
    """Convenience evaluator for a dataset row or dictionary."""
    base_p = float(row.get('BasePrice', 10.0))
    occ = int(row.get('Occupancy', 0))
    cap = int(row.get('Capacity', 100))

    if model_type == "linear":
        return linear_pricing(base_p, occ, cap)

    d_score = calculate_demand_score(
        occupancy=occ,
        capacity=cap,
        queue_length=int(row.get('QueueLength', 0)),
        traffic_condition=str(row.get('TrafficConditionNearby', 'medium')),
        is_special_day=int(row.get('IsSpecialDay', 0)),
        vehicle_type=str(row.get('VehicleType', 'car')),
        weights=weights
    )

    d_price = demand_based_pricing(base_p, d_score)

    if model_type == "competitive":
        comp_p = float(row.get('CompetitorPrice', base_p))
        return competitive_pricing(d_price, comp_p)

    return d_price
