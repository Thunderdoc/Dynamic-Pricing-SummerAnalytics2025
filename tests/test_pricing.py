"""
Unit and Integration Test Suite for Dynamic Pricing System
"""

import pytest
import pandas as pd
from src.data_generator import generate_parking_dataset, PARKING_LOTS
from src.pricing_engine import (
    linear_pricing,
    calculate_demand_score,
    demand_based_pricing,
    competitive_pricing,
    calculate_price_for_row
)
from src.rerouting import haversine_distance, find_alternative_lots


def test_data_generation():
    df = generate_parking_dataset(num_records=50, seed=123)
    assert len(df) == 50
    assert "LotID" in df.columns
    assert "Capacity" in df.columns
    assert "Occupancy" in df.columns
    assert "CompetitorPrice" in df.columns
    assert (df["Occupancy"] <= df["Capacity"]).all()


def test_linear_pricing():
    # Full occupancy -> max alpha increase
    p1 = linear_pricing(10.0, occupancy=100, capacity=100, alpha=1.5)
    assert p1 == 11.5

    # Zero occupancy -> no increase
    p0 = linear_pricing(10.0, occupancy=0, capacity=100, alpha=1.5)
    assert p0 == 10.0


def test_demand_score_and_pricing():
    # High demand scenario
    score_high = calculate_demand_score(
        occupancy=90,
        capacity=100,
        queue_length=5,
        traffic_condition="high",
        is_special_day=1,
        vehicle_type="truck"
    )
    p_high = demand_based_pricing(10.0, score_high)

    # Low demand scenario
    score_low = calculate_demand_score(
        occupancy=10,
        capacity=100,
        queue_length=0,
        traffic_condition="low",
        is_special_day=0,
        vehicle_type="bike"
    )
    p_low = demand_based_pricing(10.0, score_low)

    assert score_high > score_low
    assert p_high >= p_low
    # Test bounds [0.5x, 2.0x]
    assert 5.0 <= p_high <= 20.0
    assert 5.0 <= p_low <= 20.0


def test_competitive_pricing():
    d_price = 10.0
    comp_price = 15.0
    blended = competitive_pricing(d_price, comp_price, comp_weight=0.4)
    assert blended == 12.0


def test_haversine_distance():
    # Distance between same points should be 0
    d = haversine_distance(28.6139, 77.2090, 28.6139, 77.2090)
    assert d == 0.0

    # Non-zero distance
    d_far = haversine_distance(28.6139, 77.2090, 28.6180, 77.2140)
    assert d_far > 0.0


def test_rerouting():
    lots = [
        {"LotID": "L1", "LotName": "Main Lot", "Latitude": 28.61, "Longitude": 77.20, "Occupancy": 100, "Capacity": 100, "BasePrice": 10.0},
        {"LotID": "L2", "LotName": "Near Lot", "Latitude": 28.615, "Longitude": 77.205, "Occupancy": 30, "Capacity": 100, "BasePrice": 10.0},
        {"LotID": "L3", "LotName": "Full Lot", "Latitude": 28.612, "Longitude": 77.202, "Occupancy": 100, "Capacity": 100, "BasePrice": 10.0},
    ]

    alts = find_alternative_lots("L1", lots, max_distance_km=5.0)
    assert len(alts) == 1
    assert alts[0]["LotID"] == "L2"
