"""
Data generator for Dynamic Parking Pricing system.
Generates synthetic data for 14 urban parking lots with spatial coordinates,
traffic levels, vehicle types, demand drivers, and competitor rates.
"""

import random
import numpy as np
import pandas as pd

# 14 Urban Parking Lots metadata with geographic coordinates (e.g. Metro Area)
PARKING_LOTS = [
    {"LotID": "LOT_01", "Name": "Downtown Central Hub", "Capacity": 200, "Latitude": 28.6139, "Longitude": 77.2090, "BasePrice": 12.0},
    {"LotID": "LOT_02", "Name": "Financial District North", "Capacity": 150, "Latitude": 28.6180, "Longitude": 77.2140, "BasePrice": 15.0},
    {"LotID": "LOT_03", "Name": "Tech Park Plaza", "Capacity": 300, "Latitude": 28.6250, "Longitude": 77.2100, "BasePrice": 10.0},
    {"LotID": "LOT_04", "Name": "Metro Station East", "Capacity": 250, "Latitude": 28.6100, "Longitude": 77.2250, "BasePrice": 8.0},
    {"LotID": "LOT_05", "Name": "Shopping Mall Complex", "Capacity": 400, "Latitude": 28.6300, "Longitude": 77.2200, "BasePrice": 14.0},
    {"LotID": "LOT_06", "Name": "City Hospital Garage", "Capacity": 180, "Latitude": 28.6050, "Longitude": 77.2000, "BasePrice": 9.0},
    {"LotID": "LOT_07", "Name": "University Campus South", "Capacity": 220, "Latitude": 28.5950, "Longitude": 77.1950, "BasePrice": 7.0},
    {"LotID": "LOT_08", "Name": "Cultural Center Lot", "Capacity": 120, "Latitude": 28.6200, "Longitude": 77.1900, "BasePrice": 11.0},
    {"LotID": "LOT_09", "Name": "Stadium Arena Parking", "Capacity": 500, "Latitude": 28.6350, "Longitude": 77.2400, "BasePrice": 16.0},
    {"LotID": "LOT_10", "Name": "Harbor Bay Terminal", "Capacity": 160, "Latitude": 28.5900, "Longitude": 77.2300, "BasePrice": 10.0},
    {"LotID": "LOT_11", "Name": "Airport Express Hub", "Capacity": 350, "Latitude": 28.5800, "Longitude": 77.1800, "BasePrice": 18.0},
    {"LotID": "LOT_12", "Name": "Old Town Market Sq", "Capacity": 100, "Latitude": 28.6400, "Longitude": 77.2050, "BasePrice": 13.0},
    {"LotID": "LOT_13", "Name": "Convention Center Park", "Capacity": 280, "Latitude": 28.6150, "Longitude": 77.2350, "BasePrice": 14.0},
    {"LotID": "LOT_14", "Name": "Suburban Commuter Lot", "Capacity": 210, "Latitude": 28.5700, "Longitude": 77.2100, "BasePrice": 6.0},
]

VEHICLE_TYPES = ["car", "bike", "truck"]
TRAFFIC_LEVELS = ["low", "medium", "high"]


def generate_parking_dataset(num_records: int = 500, seed: int = 42) -> pd.DataFrame:
    """Generates synthetic parking data records."""
    random.seed(seed)
    np.random.seed(seed)

    records = []
    for i in range(num_records):
        lot = random.choice(PARKING_LOTS)
        capacity = lot["Capacity"]

        # Occupancy simulated with realistic distribution
        occ_pct = np.clip(np.random.beta(a=2, b=1.5), 0.05, 1.0)
        occupancy = int(round(occ_pct * capacity))

        # Queue length depends on occupancy
        queue_len = int(np.random.poisson(lam=max(0, (occ_pct - 0.7) * 15))) if occ_pct > 0.6 else random.randint(0, 2)

        traffic = random.choice(TRAFFIC_LEVELS)
        is_special = random.choice([0, 0, 0, 1])  # 25% chance of special event
        v_type = random.choice(["car", "car", "car", "bike", "truck"])  # cars most common

        # Nearby competitor price fluctuation
        competitor_price = round(max(5.0, lot["BasePrice"] + np.random.normal(0, 2.5)), 2)

        records.append({
            "Timestamp": pd.Timestamp("2025-07-01") + pd.Timedelta(minutes=15 * i),
            "LotID": lot["LotID"],
            "LotName": lot["Name"],
            "Capacity": capacity,
            "Occupancy": occupancy,
            "QueueLength": queue_len,
            "TrafficConditionNearby": traffic,
            "IsSpecialDay": is_special,
            "VehicleType": v_type,
            "BasePrice": lot["BasePrice"],
            "CompetitorPrice": competitor_price,
            "Latitude": lot["Latitude"],
            "Longitude": lot["Longitude"],
        })

    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    df = generate_parking_dataset()
    df.to_csv("dataset.csv", index=False)
    print(f"Generated {len(df)} records in dataset.csv successfully.")
