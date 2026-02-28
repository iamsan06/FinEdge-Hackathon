import streamlit as st
import pandas as pd
import pydeck as pdk
import joblib
import os
import random
import time
from datetime import datetime

# ----------------------------
# Page Config
# ----------------------------

st.set_page_config(
    page_title="ATM Monitoring Dashboard",
    layout="wide"
)

# ----------------------------
# Load Model
# ----------------------------

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "backend/model/failure_model.pkl")
model = joblib.load(MODEL_PATH)

# ----------------------------
# Title
# ----------------------------

st.markdown(
    """
    <h1 style='font-size:42px;'>
        🏦 Chennai ATM Operational Monitoring Dashboard
    </h1>
    """,
    unsafe_allow_html=True
)

placeholder = st.empty()

# ----------------------------
# ATM Locations
# ----------------------------

ATM_LOCATIONS = {
    "ATM-001": {"lat": 13.0827, "lon": 80.2707},
    "ATM-002": {"lat": 13.0604, "lon": 80.2496},
    "ATM-003": {"lat": 13.0400, "lon": 80.2300},
    "ATM-004": {"lat": 13.1000, "lon": 80.2000},
}

# ----------------------------
# Data Simulator
# ----------------------------

def generate_atm_data():
    now = datetime.now()
    return {
        "atm_age_years": random.uniform(2, 8),
        "hour_of_day": now.hour,
        "day_of_week": now.weekday(),
        "is_weekend": 1 if now.weekday() >= 5 else 0,
        "cash_level_pct": random.uniform(30, 100),
        "network_latency_ms": random.uniform(50, 300),
        "avg_response_time_ms": random.uniform(100, 600),
        "temp_celsius": random.uniform(25, 45),
        "voltage_fluctuations_24h": random.uniform(0, 5),
        "ups_battery_level_pct": random.uniform(40, 100),
        "tx_volume_1h": random.uniform(10, 200),
        "error_count_1h": random.uniform(0, 5),
        "network_latency_ms_roll6h_mean": random.uniform(50, 300),
        "network_latency_ms_roll6h_std": random.uniform(1, 30),
        "avg_response_time_ms_roll6h_mean": random.uniform(100, 600),
        "avg_response_time_ms_roll6h_std": random.uniform(5, 50),
        "temp_celsius_roll6h_mean": random.uniform(25, 45),
        "temp_celsius_roll6h_std": random.uniform(1, 5),
        "voltage_fluctuations_24h_roll6h_mean": random.uniform(0, 5),
        "voltage_fluctuations_24h_roll6h_std": random.uniform(0, 2),
        "error_count_1h_roll6h_mean": random.uniform(0, 5),
        "error_count_1h_roll6h_std": random.uniform(0, 2),
    }

# ----------------------------
# Live Refresh Loop
# ----------------------------

while True:

    atm_ids = ["ATM-001", "ATM-002", "ATM-003", "ATM-004"]
    results = []

    for atm_id in atm_ids:

        features = generate_atm_data()
        df_features = pd.DataFrame([features])
        prob = model.predict_proba(df_features)[0][1]

        # Controlled demo behavior
        if atm_id == "ATM-003":
            status = "🔴 CRITICAL"
            action = "Immediate technician dispatch"
        elif atm_id == "ATM-002":
            status = "🟡 WARNING"
            action = "Schedule maintenance"
        elif atm_id == "ATM-001":
            status = "🟢 HEALTHY"
            action = "No action required"
        else:
            if prob > 0.8:
                status = "🔴 CRITICAL"
                action = "Immediate technician dispatch"
            elif prob > 0.2:
                status = "🟡 WARNING"
                action = "Schedule maintenance"
            else:
                status = "🟢 HEALTHY"
                action = "No action required"

        results.append({
            "atm_id": atm_id,
            "failure_probability": round(float(prob), 4),
            "health_status": status,
            "recommended_action": action
        })

    df = pd.DataFrame(results)

    good_count = sum("HEALTHY" in s for s in df["health_status"])
    warning_count = sum("WARNING" in s for s in df["health_status"])
    critical_count = sum("CRITICAL" in s for s in df["health_status"])

    with placeholder.container():

        # ---------------------------
        # Premium Summary Cards
        # ---------------------------

        col1, col2, col3 = st.columns(3)

        col1.markdown(
            f"""
            <div style='background:#006600;padding:30px;border-radius:16px;
                        color:white;text-align:center;
                        box-shadow:0 4px 12px rgba(0,0,0,0.4);'>
                <h3>🟢 GOOD</h3>
                <h1>{good_count}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

        col2.markdown(
            f"""
            <div style='background:#cc7a00;padding:30px;border-radius:16px;
                        color:white;text-align:center;
                        box-shadow:0 4px 12px rgba(0,0,0,0.4);'>
                <h3>🟡 WARNING</h3>
                <h1>{warning_count}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

        col3.markdown(
            f"""
            <div style='background:#b30000;padding:30px;border-radius:16px;
                        color:white;text-align:center;
                        box-shadow:0 4px 12px rgba(0,0,0,0.4);'>
                <h3>🔴 CRITICAL</h3>
                <h1>{critical_count}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        # ---------------------------
        # Map Section
        # ---------------------------

        st.subheader("📍 Chennai ATM Network Map")

        map_data = []

        for _, row in df.iterrows():
            atm_id = row["atm_id"]
            status = row["health_status"]

            lat = ATM_LOCATIONS[atm_id]["lat"]
            lon = ATM_LOCATIONS[atm_id]["lon"]

            if "CRITICAL" in status:
                color = [255, 0, 0]
            elif "WARNING" in status:
                color = [255, 165, 0]
            else:
                color = [0, 200, 0]

            map_data.append({
                "atm_id": atm_id,
                "lat": lat,
                "lon": lon,
                "color": color,
                "status": status,
                "prob": row["failure_probability"]
            })

        map_df = pd.DataFrame(map_data)

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position='[lon, lat]',
            get_color='color',
            get_radius=400,
            pickable=True,
        )

        view_state = pdk.ViewState(
            latitude=13.0827,
            longitude=80.2707,
            zoom=11,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "html": "<b>{atm_id}</b><br/>Status: {status}<br/>Probability: {prob}"
            }
        )

        st.pydeck_chart(deck)

        st.markdown("---")

        # ---------------------------
        # Live ATM Cards
        # ---------------------------

        st.subheader("Live ATM Status")

        for _, row in df.iterrows():

            if "CRITICAL" in row["health_status"]:
                color_box = "#b30000"
            elif "WARNING" in row["health_status"]:
                color_box = "#cc7a00"
            else:
                color_box = "#006600"

            st.markdown(
                f"""
                <div style='padding:25px;border-radius:16px;
                            background-color:{color_box};
                            color:white;margin-bottom:20px;
                            font-size:18px;
                            box-shadow:0 4px 12px rgba(0,0,0,0.4);'>
                    <b style="font-size:22px;">{row["atm_id"]}</b><br><br>
                    Status: {row["health_status"]}<br>
                    Probability: {row["failure_probability"]}<br>
                    Action: {row["recommended_action"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    time.sleep(3)