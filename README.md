# 🚗 Dynamic Pricing & Smart Rerouting Engine for Urban Parking Lots

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.63.0-FF4B4B.svg)](https://streamlit.io/)
[![Dockerized](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Capstone](https://img.shields.io/badge/Capstone-Summer%20Analytics%202025-green.svg)](#)

Capstone Project submission for **Summer Analytics 2025**
By **Ankit Kumar** (Consulting & Analytics Club × Pathway)

---

## 📌 Executive Summary

Urban parking scarcity is a major contributor to inner-city traffic congestion, increased carbon emissions, and driver inefficiency. Traditional static pricing models fail to adapt to live fluctuations in parking demand, local traffic congestion, special events, or nearby competitor pricing.

This repository implements a **production-ready, real-time dynamic pricing and smart rerouting system** for 14 urban parking lots. Built with a modular Python architecture and a Streamlit interactive web dashboard, the engine combines 3 pricing models and an automated spatial rerouting algorithm.

---

## 🏗️ System Architecture

```
                                  ┌──────────────────────────┐
                                  │   Real-Time Data Feed    │
                                  │ (Occupancy, Queue, etc.) │
                                  └─────────────┬────────────┘
                                                │
                                                ▼
                                  ┌──────────────────────────┐
                                  │    Data Preprocessor     │
                                  │  (Normalization & Map)   │
                                  └─────────────┬────────────┘
                                                │
                 ┌──────────────────────────────┼──────────────────────────────┐
                 │                              │                              │
                 ▼                              ▼                              ▼
    ┌─────────────────────────┐   ┌───────────────────────────┐  ┌──────────────────────────┐
    │  Model 1: Linear        │   │  Model 2: Demand-Based    │  │  Model 3: Competitive    │
    │  P_{t+1} = P_t + alpha  │   │  Multi-Factor Score (D)   │  │  Blended Geo-Distance    │
    └────────────┬────────────┘   └─────────────┬─────────────┘  └─────────────┬────────────┘
                 │                              │                              │
                 └──────────────────────────────┼──────────────────────────────┘
                                                │
                                                ▼
                                  ┌──────────────────────────┐
                                  │   Smart Rerouting Engine │
                                  │    (Haversine Metric)    │
                                  └─────────────┬────────────┘
                                                │
                                                ▼
                                  ┌──────────────────────────┐
                                  │ Streamlit Web Dashboard  │
                                  │   & Interactive Maps     │
                                  └──────────────────────────┘
```

---

## 📊 Models Implemented

### 1. Model 1 – Baseline Linear Pricing
Price increases based on capacity utilization ratio:
$$P_{t+1} = P_t + \alpha \cdot \left(\frac{\text{Occupancy}}{\text{Capacity}}\right)$$

### 2. Model 2 – Multi-Factor Demand-Based Dynamic Pricing
Calculates a multi-variate composite demand score $D$:
$$D = \alpha \cdot \left(\frac{\text{Occupancy}}{\text{Capacity}}\right) + \beta \cdot \text{QueueLength} - \gamma \cdot \text{TrafficLevel} + \delta \cdot \text{IsSpecialDay} + \epsilon \cdot \text{VehicleTypeWeight}$$

Price is updated by centering normalized demand and capping bounded multipliers:
$$P_t = P_{\text{base}} \cdot \left(1 + \lambda \cdot (\hat{D} - 0.5)\right) \quad \text{where } P_t \in [0.5 \cdot P_{\text{base}},\, 2.0 \cdot P_{\text{base}}]$$

### 3. Model 3 – Geo-Distance Competitive Pricing
Blends internal demand-based price with surrounding competitor parking rates:
$$P_{\text{comp}} = (1 - w_{\text{comp}}) \cdot P_{\text{demand}} + w_{\text{comp}} \cdot P_{\text{competitor}}$$

### 4. Smart Rerouting Engine
When a target lot reaches saturation capacity ($\ge 90\%$ occupancy), the system calculates Haversine spatial proximity and available spaces to recommend top alternative parking lots.

---

## 📂 Project Structure

```
.
├── app.py                                    # Streamlit Production Web Dashboard
├── dataset.csv                               # Generated Synthetic Urban Parking Dataset
├── Dockerfile                                # Multi-stage Docker Container Configuration
├── docker-compose.yml                        # Container Orchestration Spec
├── Dynamic_Pricing_Ankit_Kumar_SA2025.ipynb  # Comprehensive Jupyter Notebook Analysis
├── README.md                                 # Project Documentation & Guide
├── requirements.txt                          # Python Dependencies Spec
├── src/
│   ├── __init__.py
│   ├── data_generator.py                    # Dataset Generation Module
│   ├── pricing_engine.py                    # Core Models 1, 2, and 3 Implementations
│   └── rerouting.py                         # Spatial Haversine Rerouting Engine
└── tests/
    └── test_pricing.py                       # Unit & Integration Pytest Suite
```

---

## 🚀 Quick Start & Installation

### Option 1: Running Locally with Python

1. **Clone Repository & Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate / Refresh Dataset:**
   ```bash
   python3 src/data_generator.py
   ```

3. **Launch Web Application:**
   ```bash
   streamlit run app.py
   ```
   Open `http://localhost:8501` in your browser.

4. **Run Automated Test Suite:**
   ```bash
   python3 -m pytest
   ```

---

### Option 2: Running with Docker / Docker Compose

1. **Build & Run Container:**
   ```bash
   docker-compose up --build
   ```
2. Open `http://localhost:8501` in your browser.

---

## 💻 Web Dashboard Features

- **📊 Real-Time Network Overview:** Live KPIs, parking lot map, and lot-level inspector.
- **📈 Model Comparison & Analytics:** Interactive Plotly scatter and bar plots comparing Model 1, Model 2, and Model 3 behavior.
- **🧭 Smart Rerouting Engine:** Real-time alternative lot recommendation with customizable search radius and occupancy simulation.
- **⚡ Live Simulation Stream:** Step-by-step real-time time-series simulation of pricing adjustments.
- **📚 Mathematical Formulations:** Detailed LaTeX equations and derivations.

---

## ✅ Author

**Ankit Kumar**  
Capstone Project for:  
📊 Consulting & Analytics Club × 🧠 Pathway  
**Summer Analytics 2025**
