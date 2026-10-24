# Dynamic Pricing & Smart Rerouting for Urban Parking Lots

> Capstone project for **Summer Analytics 2025** (Consulting & Analytics Club × Pathway).
> A learning project that explores how parking prices could respond to demand — built on
> **synthetic data**, not live parking feeds, and **not a production system**.
> There is no public live deployment; run it locally with the steps below.

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Capstone](https://img.shields.io/badge/Capstone-Summer%20Analytics%202025-green.svg)](#)

## What it is

Urban parking demand shifts through the day — with occupancy, queues, nearby traffic,
special events, and what neighbouring lots charge. Static prices cannot react to any of
that. This project implements three pricing models side by side, plus a spatial
rerouting engine that suggests nearby alternatives when a lot fills up, all wrapped in
an interactive Streamlit dashboard.

Everything runs on a generated dataset for **14 fictional urban parking lots**
(Downtown Central Hub, Financial District North, Tech Park Plaza, and eleven more),
so the focus stays on the pricing logic itself rather than on real-world data
collection.

## How it works

### Data — synthetic, by design

`src/data_generator.py` generates the dataset (`generate_parking_dataset()`,
500 records by default, seed 42). Each record carries a timestamp (15-minute steps
from 2025-07-01), lot, capacity, occupancy, queue length, nearby traffic level
(`low` / `medium` / `high`), a special-day flag, vehicle type (`car` / `bike` /
`truck`), base price, a nearby competitor price, and the lot's latitude/longitude.

The dashboard (`app.py`) first tries to read `dataset.csv`; if it is missing, it
generates the dataset and writes `dataset.csv`. You can also regenerate it directly:

```bash
python3 src/data_generator.py
```

### Model 1 — Baseline linear pricing

The simplest possible response to crowding: price rises with the occupancy ratio.

```
P(t+1) = P(t) + alpha * (Occupancy / Capacity)
```

Default `alpha = 1.5` in `src/pricing_engine.py` (`linear_pricing`), with utilisation
clamped to [0, 1].

### Model 2 — Multi-factor demand-based pricing

A composite demand score combines five factors:

```
D = alpha * (Occupancy / Capacity) + beta * QueueLength
    - gamma * TrafficLevel + delta * IsSpecialDay + epsilon * VehicleTypeWeight
```

Default weights: `alpha = 1.0`, `beta = 0.6`, `gamma = 0.4`, `delta = 0.7`,
`epsilon = 0.8`. Traffic maps to `low = 1`, `medium = 2`, `high = 3`; vehicle
weights are `car = 1.0`, `bike = 0.5`, `truck = 1.5`.

The score is normalised (divided by 10, clipped to [0, 1]) and turned into a price
bounded to [0.5×, 2.0×] the base price:

```
P = P(base) * (1 + lambda * (D_normalised - 0.5)),   lambda = 0.5 by default
```

### Model 3 — Competitive pricing

The demand-based price is blended with the price charged by nearby competitors:

```
P(comp) = (1 - w) * P(demand) + w * P(competitor),   w = 0.3 by default
```

### Smart rerouting — Haversine distance

When a lot is nearly full (the dashboard flags lots at **≥ 90% occupancy**),
`src/rerouting.py` (`find_alternative_lots`) ranks nearby lots by Haversine
great-circle distance combined with available space. Only lots under 95% full are
suggested, within a 5 km default radius, with the top 3 returned.

## The dashboard

`streamlit run app.py` opens five modules (sidebar):

- **Real-Time Dashboard** — lot KPIs, a parking-lot map, and a lot-level inspector.
  ("Real-time" here means the simulated data stream in the app, not live city data.)
- **Model Comparison & Analytics** — Plotly charts comparing Models 1, 2, and 3.
- **Smart Rerouting Engine** — pick a lot, set a search radius, and see the top
  alternative lots when it fills up.
- **Live Simulation Stream** — step-by-step simulated price updates over time.
- **Mathematical Formulations** — the equations above, as written in the code.

Model weights (α, β, γ, δ, ε) are adjustable from the dashboard sidebar.

## Project structure

```
.
├── app.py                                    # Streamlit dashboard
├── dataset.csv                               # Generated synthetic dataset
├── Dockerfile                                # Python 3.12-slim image, serves on port 8501
├── docker-compose.yml                        # Single-service compose setup
├── Dynamic_Pricing_Ankit_Kumar_SA2025.ipynb  # Jupyter notebook analysis
├── README.md                                 # This file
├── requirements.txt                          # Python dependencies
├── src/
│   ├── __init__.py
│   ├── data_generator.py                    # Synthetic dataset generator (14 lots)
│   ├── pricing_engine.py                    # Models 1, 2, and 3
│   └── rerouting.py                         # Haversine rerouting engine
└── tests/
    └── test_pricing.py                       # Pytest suite
```

## Tech stack

From `requirements.txt` and the `Dockerfile`:

- **Python 3.12** (`python:3.12-slim` in the Dockerfile)
- **Streamlit** — dashboard (no version pinned; `streamlit>=1.30.0` in requirements)
- **pandas, NumPy** — data handling
- **Plotly, Matplotlib, Seaborn, Bokeh** — charts and analysis
- **pytest** — tests
- **Docker / Docker Compose** — containerised run

## Run it locally

```bash
git clone https://github.com/Thunderdoc/Dynamic-Pricing-SummerAnalytics2025.git
cd Dynamic-Pricing-SummerAnalytics2025
pip install -r requirements.txt
```

Generate the dataset (optional — the app generates it on first run if it is missing):

```bash
python3 src/data_generator.py
```

Launch the dashboard:

```bash
streamlit run app.py
```

Then open <http://localhost:8501> in your browser.

### With Docker

```bash
docker-compose up --build
```

Then open <http://localhost:8501>. The compose service maps host port 8501 to
container port 8501.

### Run the tests

```bash
python3 -m pytest
```

The suite in `tests/test_pricing.py` covers dataset generation, linear pricing,
demand-score and demand-based pricing (including the [0.5×, 2.0×] bounds),
competitive pricing, and Haversine distance.

## Honest status and limits

- **Capstone / learning project, Summer Analytics 2025.** It is not deployed
  anywhere, has no real users, and is not connected to any real parking system.
- **All data is synthetic.** Lot names, coordinates, occupancies, queues, and
  competitor prices are generated, not observed. Results demonstrate the models,
  not real parking behaviour.
- **"Live" / "real-time" in the app means simulated.** Prices update as the
  simulation steps forward; nothing here reads a live feed.
- **No screenshots or performance claims are made here**, because none were
  measured against real data.

## Author

**Ankit Kumar** — Capstone Project for Consulting & Analytics Club × Pathway,
Summer Analytics 2025.

Built by Thunderdoc.
