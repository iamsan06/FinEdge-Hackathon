import requests
import time
from datetime import datetime
import random

API_URL = "http://127.0.0.1:8000/predict"


def generate_features(atm_id):

    now = datetime.now()

    # -------------------------
    # Controlled Operational Profiles
    # -------------------------

    if atm_id == "ATM-001":  
        # Always HEALTHY
        severity = 0

    elif atm_id == "ATM-002":  
        # Always WARNING (moderate degradation)
        severity = 2

    elif atm_id == "ATM-003":  
        # Always CRITICAL (strong degradation)
        severity = 4

    elif atm_id == "ATM-004":  
        # Slight fluctuation between healthy and warning
        severity = random.choice([0, 1, 2])

    # -------------------------
    # Feature Engineering (Important)
    # Stronger multipliers = higher model probability
    # -------------------------

    return {
        "atm_id": atm_id,
        "atm_age_years": 5.0,
        "hour_of_day": int(now.hour),
        "day_of_week": int(now.weekday()),
        "is_weekend": int(now.weekday() >= 5),

        "cash_level_pct": float(90 - severity * 12),
        "network_latency_ms": float(40 + severity * 180),
        "avg_response_time_ms": float(120 + severity * 350),
        "temp_celsius": float(32 + severity * 8),
        "voltage_fluctuations_24h": float(1 + severity * 8),
        "ups_battery_level_pct": float(95 - severity * 15),
        "tx_volume_1h": float(20 + severity * 6),
        "error_count_1h": float(severity * 5),

        # rolling features
        "network_latency_ms_roll6h_mean": float(45 + severity * 170),
        "network_latency_ms_roll6h_std": float(5 + severity * 20),
        "avg_response_time_ms_roll6h_mean": float(150 + severity * 320),
        "avg_response_time_ms_roll6h_std": float(10 + severity * 40),
        "temp_celsius_roll6h_mean": float(33 + severity * 7),
        "temp_celsius_roll6h_std": float(1 + severity * 4),
        "voltage_fluctuations_24h_roll6h_mean": float(2 + severity * 7),
        "voltage_fluctuations_24h_roll6h_std": float(1 + severity * 4),
        "error_count_1h_roll6h_mean": float(0.5 + severity * 3),
        "error_count_1h_roll6h_std": float(0.1 + severity * 2),
    }


# -------------------------
# Main Loop
# -------------------------

while True:

    payload = []

    for atm in ["ATM-001", "ATM-002", "ATM-003", "ATM-004"]:
        payload.append(generate_features(atm))

    try:
        response = requests.post(API_URL, json=payload)
        print("\nResponse:", response.json())
    except Exception as e:
        print("ERROR:", e)

    time.sleep(5)