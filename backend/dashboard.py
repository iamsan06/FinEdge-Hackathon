import streamlit as st
import requests
import pandas as pd
import time
import pydeck as pdk

API_STATUS_URL = "http://127.0.0.1:8000/status"

st.set_page_config(page_title="ATM Monitoring Dashboard", layout="wide")

st.title("🏦 Chennai ATM Operational Monitoring Dashboard")

placeholder = st.empty()

# Chennai ATM Locations (Realistic Sample Coordinates)
ATM_LOCATIONS = {
    "ATM-001": {"lat": 13.0827, "lon": 80.2707},  # Central Chennai
    "ATM-002": {"lat": 13.0604, "lon": 80.2496},  # T Nagar
    "ATM-003": {"lat": 13.0400, "lon": 80.2300},  # Guindy
    "ATM-004": {"lat": 13.1000, "lon": 80.2000},  # Anna Nagar
}

while True:

    try:
        response = requests.get(API_STATUS_URL)

        if response.status_code == 200:
            data = response.json()

            if data:
                df = pd.DataFrame(data)

                # ---------------------------
                # Summary Counts
                # ---------------------------
                good_count = 0
                warning_count = 0
                critical_count = 0

                for _, row in df.iterrows():
                    if "CRITICAL" in row["health_status"]:
                        critical_count += 1
                    elif "WARNING" in row["health_status"]:
                        warning_count += 1
                    else:
                        good_count += 1

                with placeholder.container():

                    # ---------------------------
                    # Summary Boxes
                    # ---------------------------
                    col1, col2, col3 = st.columns(3)

                    col1.markdown(
                        f"<div style='background:#006600;padding:20px;border-radius:12px;color:white;text-align:center;'>"
                        f"<h3>🟢 GOOD</h3><h2>{good_count}</h2></div>",
                        unsafe_allow_html=True,
                    )

                    col2.markdown(
                        f"<div style='background:#cc7a00;padding:20px;border-radius:12px;color:white;text-align:center;'>"
                        f"<h3>🟡 WARNING</h3><h2>{warning_count}</h2></div>",
                        unsafe_allow_html=True,
                    )

                    col3.markdown(
                        f"<div style='background:#b30000;padding:20px;border-radius:12px;color:white;text-align:center;'>"
                        f"<h3>🔴 CRITICAL</h3><h2>{critical_count}</h2></div>",
                        unsafe_allow_html=True,
                    )

                    st.markdown("---")

                    # ---------------------------
                    # Map Data Preparation
                    # ---------------------------

                    map_data = []

                    for _, row in df.iterrows():

                        atm_id = row["atm_id"]
                        status = row["health_status"]

                        lat = ATM_LOCATIONS[atm_id]["lat"]
                        lon = ATM_LOCATIONS[atm_id]["lon"]

                        if "CRITICAL" in status:
                            color = [255, 0, 0]       # Red
                        elif "WARNING" in status:
                            color = [255, 165, 0]     # Orange
                        else:
                            color = [0, 200, 0]       # Green

                        map_data.append({
                            "atm_id": atm_id,
                            "lat": lat,
                            "lon": lon,
                            "color": color,
                            "status": status,
                            "prob": row["failure_probability"]
                        })

                    map_df = pd.DataFrame(map_data)

                    # ---------------------------
                    # PyDeck Map
                    # ---------------------------

                    st.subheader("📍 Chennai ATM Network Map")

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
                        pitch=0,
                    )

                    tooltip = {
                        "html": "<b>{atm_id}</b><br/>Status: {status}<br/>Probability: {prob}",
                        "style": {"backgroundColor": "black", "color": "white"}
                    }

                    deck = pdk.Deck(
                        layers=[layer],
                        initial_view_state=view_state,
                        tooltip=tooltip
                    )

                    st.pydeck_chart(deck)

                    st.markdown("---")

                    # ---------------------------
                    # Detailed Cards
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
                            <div style='padding:20px;
                                        border-radius:12px;
                                        background-color:{color_box};
                                        color:white;
                                        margin-bottom:15px;
                                        font-size:18px;'>
                                <b>{row["atm_id"]}</b><br>
                                Status: {row["health_status"]}<br>
                                Probability: {row["failure_probability"]}<br>
                                Action: {row["recommended_action"]}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            else:
                st.warning("Waiting for simulator data...")

        else:
            st.error("Backend not reachable")

    except Exception as e:
        st.error(f"Error connecting to API: {e}")

    time.sleep(3)