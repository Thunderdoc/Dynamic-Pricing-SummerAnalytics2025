"""
Dynamic Pricing Engine for Urban Parking Lots
Streamlit Web Application Dashboard with Advanced UI/UX & CSS Animations
"""

import time
import random
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.data_generator import generate_parking_dataset
from src.pricing_engine import (
    linear_pricing,
    calculate_demand_score,
    demand_based_pricing,
    competitive_pricing,
    DEFAULT_DEMAND_WEIGHTS
)
from src.rerouting import find_alternative_lots

# Page Config
st.set_page_config(
    page_title="Urban Parking Dynamic Pricing Engine",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling & CSS Animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Gradient Background Banner */
    .hero-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #312E81 100%);
        padding: 2.2rem 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);
        position: relative;
        overflow: hidden;
        animation: fadeIn 0.8s ease-in-out;
    }

    .hero-container::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.3) 0%, rgba(0,0,0,0) 70%);
        border-radius: 50%;
    }

    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin-bottom: 0.4rem;
        background: linear-gradient(90deg, #FFFFFF 0%, #E2E8F0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #94A3B8;
        font-weight: 400;
        max-width: 800px;
    }

    /* Glassmorphism Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-radius: 14px;
        padding: 1.25rem 1rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.1);
        border-color: #6366F1;
    }

    .metric-label {
        font-size: 0.825rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 0.3rem;
    }

    .metric-value {
        font-size: 1.75rem;
        font-weight: 800;
        color: #0F172A;
    }

    /* Keyframe Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    .badge-live {
        display: inline-flex;
        align-items: center;
        padding: 0.35rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        background-color: #DEF7EC;
        color: #03543F;
        animation: pulseGlow 2s infinite;
        margin-bottom: 0.5rem;
    }

    .dot-live {
        width: 8px;
        height: 8px;
        background-color: #10B981;
        border-radius: 50%;
        margin-right: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    try:
        return pd.read_csv("dataset.csv")
    except Exception:
        df = generate_parking_dataset()
        df.to_csv("dataset.csv", index=False)
        return df


df_raw = load_data()

# Hero Header with Glassmorphism
st.markdown("""
<div class="hero-container">
    <div class="badge-live"><div class="dot-live"></div> REAL-TIME SYSTEM ONLINE</div>
    <div class="hero-title">🚗 Urban Parking Dynamic Pricing & Rerouting Engine</div>
    <div class="hero-subtitle">Production-grade smart city mobility framework with multi-factor demand modeling, spatial Haversine competitor pricing, and automated load re-balancing.</div>
</div>
""", unsafe_allow_html=True)

# Sidebar Controls
st.sidebar.title("🎛️ Control Center")

app_mode = st.sidebar.radio(
    "Select System Module",
    ["📊 Real-Time Dashboard", "📈 Model Comparison & Analytics", "🧭 Smart Rerouting Engine", "⚡ Live Simulation Stream", "📚 Mathematical Formulations"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Dynamic Model Weights")

w_alpha = st.sidebar.slider("α (Occupancy Ratio)", 0.0, 2.0, DEFAULT_DEMAND_WEIGHTS['alpha'], 0.1)
w_beta = st.sidebar.slider("β (Queue Length)", 0.0, 2.0, DEFAULT_DEMAND_WEIGHTS['beta'], 0.1)
w_gamma = st.sidebar.slider("γ (Traffic Condition)", 0.0, 2.0, DEFAULT_DEMAND_WEIGHTS['gamma'], 0.1)
w_delta = st.sidebar.slider("δ (Special Event Boost)", 0.0, 2.0, DEFAULT_DEMAND_WEIGHTS['delta'], 0.1)
w_epsilon = st.sidebar.slider("ε (Vehicle Type Modifier)", 0.0, 2.0, DEFAULT_DEMAND_WEIGHTS['epsilon'], 0.1)

weights = {
    'alpha': w_alpha,
    'beta': w_beta,
    'gamma': w_gamma,
    'delta': w_delta,
    'epsilon': w_epsilon
}

# Process Dataset with dynamic weights
processed_df = df_raw.copy()
processed_df['DemandScore'] = processed_df.apply(
    lambda r: calculate_demand_score(
        occupancy=r['Occupancy'],
        capacity=r['Capacity'],
        queue_length=r['QueueLength'],
        traffic_condition=r['TrafficConditionNearby'],
        is_special_day=r['IsSpecialDay'],
        vehicle_type=r['VehicleType'],
        weights=weights
    ), axis=1
)

processed_df['Model1_Linear'] = processed_df.apply(
    lambda r: linear_pricing(r['BasePrice'], r['Occupancy'], r['Capacity']), axis=1
)

processed_df['Model2_Demand'] = processed_df.apply(
    lambda r: demand_based_pricing(r['BasePrice'], r['DemandScore']), axis=1
)

processed_df['Model3_Competitive'] = processed_df.apply(
    lambda r: competitive_pricing(r['Model2_Demand'], r['CompetitorPrice']), axis=1
)

# ==========================================
# MODULE 1: REAL-TIME DASHBOARD
# ==========================================
if app_mode == "📊 Real-Time Dashboard":
    st.subheader("📊 Network-Wide System Overview")

    # Key Performance Indicators Cards
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    avg_occ = (processed_df['Occupancy'].sum() / processed_df['Capacity'].sum()) * 100
    avg_demand_price = processed_df['Model2_Demand'].mean()
    avg_linear_price = processed_df['Model1_Linear'].mean()
    total_lots = processed_df['LotID'].nunique()
    total_capacity = processed_df.groupby('LotID')['Capacity'].first().sum()

    kpi1.markdown(f'<div class="metric-card"><div class="metric-label">Total Parking Hubs</div><div class="metric-value">{total_lots}</div></div>', unsafe_allow_html=True)
    kpi2.markdown(f'<div class="metric-card"><div class="metric-label">Total Capacity</div><div class="metric-value">{total_capacity:,}</div></div>', unsafe_allow_html=True)
    kpi3.markdown(f'<div class="metric-card"><div class="metric-label">Avg Occupancy</div><div class="metric-value" style="color:#6366F1;">{avg_occ:.1f}%</div></div>', unsafe_allow_html=True)
    kpi4.markdown(f'<div class="metric-card"><div class="metric-label">Avg Demand Price</div><div class="metric-value" style="color:#10B981;">${avg_demand_price:.2f}</div></div>', unsafe_allow_html=True)
    kpi5.markdown(f'<div class="metric-card"><div class="metric-label">Price Delta (M2 vs M1)</div><div class="metric-value">${(avg_demand_price - avg_linear_price):+.2f}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Filter Lot
    col_filter, col_map = st.columns([1, 2])

    with col_filter:
        st.subheader("🔍 Lot Quick Inspection")
        selected_lot = st.selectbox("Select Parking Lot", options=sorted(processed_df['LotName'].unique()))

        lot_data = processed_df[processed_df['LotName'] == selected_lot].iloc[0]

        st.markdown(f"**Lot ID:** `{lot_data['LotID']}`")
        st.markdown(f"**Capacity:** {lot_data['Capacity']} vehicles")
        st.markdown(f"**Current Occupancy:** {lot_data['Occupancy']} ({round(lot_data['Occupancy']/lot_data['Capacity']*100, 1)}%)")
        st.markdown(f"**Queue Length:** {lot_data['QueueLength']} vehicles")
        st.markdown(f"**Nearby Traffic:** {lot_data['TrafficConditionNearby'].upper()}")
        st.markdown(f"**Special Day / Event:** {'Yes 🎆' if lot_data['IsSpecialDay'] else 'No 📅'}")

        st.markdown("### 🏷️ Pricing Calculations")
        st.write(f"- Base Price: **${lot_data['BasePrice']:.2f}**")
        st.write(f"- Model 1 (Linear): **${lot_data['Model1_Linear']:.2f}**")
        st.write(f"- Model 2 (Demand-Based): **${lot_data['Model2_Demand']:.2f}**")
        st.write(f"- Model 3 (Competitive): **${lot_data['Model3_Competitive']:.2f}**")

    with col_map:
        st.subheader("🗺️ Live Geographic Distribution & Occupancy Map")

        map_df = processed_df.groupby(['LotID', 'LotName', 'Latitude', 'Longitude', 'Capacity']).agg({
            'Occupancy': 'mean',
            'Model2_Demand': 'mean',
            'CompetitorPrice': 'mean'
        }).reset_index()
        map_df['Occupancy %'] = (map_df['Occupancy'] / map_df['Capacity']) * 100

        fig_map = px.scatter_map(
            map_df,
            lat="Latitude",
            lon="Longitude",
            color="Occupancy %",
            size="Capacity",
            hover_name="LotName",
            hover_data={"Model2_Demand": ":$.2f", "Occupancy %": ":.1f%"},
            color_continuous_scale=px.colors.cyclical.IceFire,
            size_max=25,
            zoom=11,
            map_style="open-street-map",
            title="Real-Time Parking Lot Map (Color = Occupancy %, Size = Capacity)"
        )
        fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_map, width="stretch")

# ==========================================
# MODULE 2: MODEL COMPARISON & ANALYTICS
# ==========================================
elif app_mode == "📈 Model Comparison & Analytics":
    st.subheader("📈 Comparative Analysis: Model 1 vs Model 2 vs Model 3")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("##### Price Comparison Across Parking Lots")
        lot_prices = processed_df.groupby('LotName')[['Model1_Linear', 'Model2_Demand', 'Model3_Competitive']].mean().reset_index()

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=lot_prices['LotName'], y=lot_prices['Model1_Linear'], name='Model 1 (Linear)', marker_color='#94A3B8'))
        fig_bar.add_trace(go.Bar(x=lot_prices['LotName'], y=lot_prices['Model2_Demand'], name='Model 2 (Demand)', marker_color='#6366F1'))
        fig_bar.add_trace(go.Bar(x=lot_prices['LotName'], y=lot_prices['Model3_Competitive'], name='Model 3 (Competitive)', marker_color='#10B981'))

        fig_bar.update_layout(barmode='group', xaxis_tickangle=-45, height=450, margin=dict(l=20, r=20, t=30, b=100))
        st.plotly_chart(fig_bar, width="stretch")

    with col_chart2:
        st.markdown("##### Price vs Occupancy Ratio Scatter Plot")
        processed_df['OccupancyRatio'] = processed_df['Occupancy'] / processed_df['Capacity']

        fig_scatter = px.scatter(
            processed_df,
            x='OccupancyRatio',
            y='Model2_Demand',
            color='TrafficConditionNearby',
            size='QueueLength',
            hover_name='LotName',
            labels={'OccupancyRatio': 'Occupancy Ratio (Occupancy/Capacity)', 'Model2_Demand': 'Demand Price ($)'},
            title="Model 2 Price Behavior by Traffic & Queue"
        )
        fig_scatter.update_layout(height=450)
        st.plotly_chart(fig_scatter, width="stretch")

    st.markdown("---")
    st.markdown("##### Vehicle Type Dynamic Adjustment Distribution")

    fig_box = px.box(
        processed_df,
        x='VehicleType',
        y='Model2_Demand',
        color='VehicleType',
        points="all",
        title="Price Variance by Vehicle Type (Car vs Bike vs Truck)"
    )
    st.plotly_chart(fig_box, width="stretch")

# ==========================================
# MODULE 3: SMART REROUTING ENGINE
# ==========================================
elif app_mode == "🧭 Smart Rerouting Engine":
    st.subheader("🧭 Intelligent Parking Lot Rerouting Recommendation System")
    st.info("When a driver arrives at a lot that is full or excessively priced, the system calculates distance and availability to recommend the optimal nearby alternative.")

    target_lot_name = st.selectbox("Select Target Parking Lot", options=sorted(processed_df['LotName'].unique()))

    all_lots_latest = []
    for lot_name, group in processed_df.groupby('LotName'):
        row = group.iloc[0]
        all_lots_latest.append({
            "LotID": row['LotID'],
            "LotName": row['LotName'],
            "Latitude": row['Latitude'],
            "Longitude": row['Longitude'],
            "Capacity": row['Capacity'],
            "Occupancy": row['Occupancy'],
            "CurrentPrice": row['Model2_Demand'],
            "BasePrice": row['BasePrice']
        })

    target_lot = next(l for l in all_lots_latest if l['LotName'] == target_lot_name)

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Selected Lot", target_lot['LotName'])

    sim_occ = c2.slider("Simulate Occupancy for Selected Lot", 0, target_lot['Capacity'], target_lot['Capacity'])
    max_dist = c3.slider("Max Search Radius (km)", 1.0, 10.0, 5.0)

    target_lot['Occupancy'] = sim_occ

    if sim_occ >= target_lot['Capacity'] * 0.90:
        st.warning(f"⚠️ **{target_lot['LotName']}** is nearly full ({sim_occ}/{target_lot['Capacity']} spaces taken, {round(sim_occ/target_lot['Capacity']*100,1)}%). Rerouting active!")

        alternatives = find_alternative_lots(target_lot['LotID'], all_lots_latest, max_distance_km=max_dist)

        if alternatives:
            st.markdown("### 🏆 Top Recommended Alternative Lots")
            alt_df = pd.DataFrame(alternatives)

            st.dataframe(
                alt_df[['LotName', 'DistanceKM', 'AvailableSpaces', 'OccupancyPct', 'CurrentPrice']],
                column_config={
                    "LotName": "Alternative Parking Lot",
                    "DistanceKM": st.column_config.NumberColumn("Distance (km)", format="%.2f km"),
                    "AvailableSpaces": "Available Spaces",
                    "OccupancyPct": st.column_config.NumberColumn("Occupancy Rate", format="%.1f%%"),
                    "CurrentPrice": st.column_config.NumberColumn("Dynamic Price", format="$%.2f")
                },
                hide_index=True,
                width="stretch"
            )
        else:
            st.error("No available alternative lots within the specified search radius.")
    else:
        st.success(f"✅ **{target_lot['LotName']}** has ample space ({target_lot['Capacity'] - sim_occ} spaces available). No rerouting required.")

# ==========================================
# MODULE 4: LIVE SIMULATION STREAM
# ==========================================
elif app_mode == "⚡ Live Simulation Stream":
    st.subheader("⚡ Real-Time Streaming Simulation")
    st.write("Simulates continuous incoming streaming events and live price updates over consecutive time steps.")

    sim_lot_name = st.selectbox("Select Lot to Simulate Stream", options=sorted(processed_df['LotName'].unique()))
    sim_steps = st.slider("Simulation Steps (Time Steps)", 5, 30, 10)

    if st.button("🚀 Run Live Streaming Simulation"):
        chart_placeholder = st.empty()
        status_placeholder = st.empty()

        sim_data = []
        base_p = processed_df[processed_df['LotName'] == sim_lot_name]['BasePrice'].iloc[0]
        cap = processed_df[processed_df['LotName'] == sim_lot_name]['Capacity'].iloc[0]

        curr_occ = random.randint(20, cap // 2)

        for step in range(1, sim_steps + 1):
            time_label = f"T+{step*15}m"

            delta_occ = random.randint(-15, 25)
            curr_occ = int(np.clip(curr_occ + delta_occ, 5, cap))
            queue = max(0, curr_occ - cap) + random.randint(0, 5) if curr_occ > cap * 0.8 else random.randint(0, 2)
            traffic = random.choice(['low', 'medium', 'high'])
            is_special = random.choice([0, 1])
            v_type = random.choice(['car', 'bike', 'truck'])

            d_score = calculate_demand_score(curr_occ, cap, queue, traffic, is_special, v_type, weights)
            p1 = linear_pricing(base_p, curr_occ, cap)
            p2 = demand_based_pricing(base_p, d_score)
            p3 = competitive_pricing(p2, base_p + random.uniform(-2, 3))

            sim_data.append({
                "TimeStep": time_label,
                "Occupancy": curr_occ,
                "OccupancyPct": (curr_occ / cap) * 100,
                "Model1_Linear": p1,
                "Model2_Demand": p2,
                "Model3_Competitive": p3
            })

            df_sim = pd.DataFrame(sim_data)

            fig_sim = go.Figure()
            fig_sim.add_trace(go.Scatter(x=df_sim['TimeStep'], y=df_sim['Model1_Linear'], mode='lines+markers', name='Model 1 (Linear)', line=dict(color='#94A3B8', dash='dash')))
            fig_sim.add_trace(go.Scatter(x=df_sim['TimeStep'], y=df_sim['Model2_Demand'], mode='lines+markers', name='Model 2 (Demand)', line=dict(color='#6366F1', width=3)))
            fig_sim.add_trace(go.Scatter(x=df_sim['TimeStep'], y=df_sim['Model3_Competitive'], mode='lines+markers', name='Model 3 (Competitive)', line=dict(color='#10B981')))

            fig_sim.update_layout(
                title=f"Live Dynamic Price Stream for {sim_lot_name}",
                xaxis_title="Time Step",
                yaxis_title="Calculated Price ($)",
                height=450,
                legend=dict(x=0, y=1)
            )

            chart_placeholder.plotly_chart(fig_sim, width="stretch")
            status_placeholder.markdown(f"**Step {step}/{sim_steps}:** Current Occupancy = `{curr_occ}/{cap}` ({round(curr_occ/cap*100, 1)}%) | Calculated Demand Price = **${p2:.2f}**")
            time.sleep(0.3)

        st.success("Simulation Complete!")

# ==========================================
# MODULE 5: MATHEMATICAL FORMULATIONS
# ==========================================
elif app_mode == "📚 Mathematical Formulations":
    st.subheader("📚 Mathematical Formulations & Systems Architecture")

    st.markdown("""
    ### 1. Model 1: Baseline Linear Pricing Model
    Linear pricing adjusts price strictly as a function of capacity utilization ratio:
    """)
    st.latex(r"P_{t+1} = P_t + \alpha \cdot \left(\frac{\text{Occupancy}}{\text{Capacity}}\right)")

    st.markdown("""
    ---
    ### 2. Model 2: Multi-Factor Demand-Based Dynamic Pricing
    Calculates a multi-variate demand composite score $D$, integrating occupancy, queue length, surrounding traffic density, special events, and vehicle classification:
    """)
    st.latex(r"D = \alpha \cdot \left(\frac{\text{Occupancy}}{\text{Capacity}}\right) + \beta \cdot \text{QueueLength} - \gamma \cdot \text{TrafficLevel} + \delta \cdot \text{IsSpecialDay} + \epsilon \cdot \text{VehicleTypeWeight}")

    st.markdown("Price is updated by centering normalized demand and applying bounded caps:")
    st.latex(r"P_t = P_{\text{base}} \cdot \left(1 + \lambda \cdot \left(\hat{D} - 0.5\right)\right)")
    st.latex(r"P_t \in \left[0.5 \cdot P_{\text{base}},\, 2.0 \cdot P_{\text{base}}\right]")

    st.markdown("""
    ---
    ### 3. Model 3: Geo-Distance Competitive Pricing
    Blends local demand-driven price with surrounding competitor parking rates:
    """)
    st.latex(r"P_{\text{comp}} = (1 - w_{\text{comp}}) \cdot P_{\text{demand}} + w_{\text{comp}} \cdot P_{\text{competitor}}")

    st.markdown("""
    ---
    ### 4. Smart Rerouting Haversine Metric
    Calculates spatial proximity to re-route incoming drivers to optimal neighboring lots:
    """)
    st.latex(r"d = 2R \cdot \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)")
