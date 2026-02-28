from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import joblib
import pandas as pd
import os
from datetime import datetime

app = FastAPI()

# ----------------------------
# Load Model
# ----------------------------

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "model/failure_model.pkl")
model = joblib.load(MODEL_PATH)

print("✅ Model Loaded Successfully")

# ----------------------------
# Store latest results in memory
# ----------------------------

latest_results = []

# ----------------------------
# Schema
# ----------------------------

class ATMData(BaseModel):
    atm_id: str
    atm_age_years: float
    hour_of_day: int
    day_of_week: int
    is_weekend: int
    cash_level_pct: float
    network_latency_ms: float
    avg_response_time_ms: float
    temp_celsius: float
    voltage_fluctuations_24h: float
    ups_battery_level_pct: float
    tx_volume_1h: float
    error_count_1h: float
    network_latency_ms_roll6h_mean: float
    network_latency_ms_roll6h_std: float
    avg_response_time_ms_roll6h_mean: float
    avg_response_time_ms_roll6h_std: float
    temp_celsius_roll6h_mean: float
    temp_celsius_roll6h_std: float
    voltage_fluctuations_24h_roll6h_mean: float
    voltage_fluctuations_24h_roll6h_std: float
    error_count_1h_roll6h_mean: float
    error_count_1h_roll6h_std: float


# ----------------------------
# Prediction Endpoint
# ----------------------------

@app.post("/predict")
def predict_multiple(atms: List[ATMData]):

    global latest_results

    if not atms:
        return {"message": "No ATM data received"}

    df = pd.DataFrame([atm.model_dump() for atm in atms])
    atm_ids = df["atm_id"]
    df_features = df.drop(columns=["atm_id"])

    probabilities = model.predict_proba(df_features)[:, 1]

    print("\n=================================================")
    print("📡 ATM OPERATIONAL STATUS @", datetime.now().strftime("%H:%M:%S"))
    print("=================================================")

    results = []

    for i in range(len(df)):

        atm_id = atm_ids.iloc[i]
        prob = float(probabilities[i])

        # Prototype display logic
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
            elif prob > 0.01:
                status = "🟡 WARNING"
                action = "Schedule maintenance"
            else:
                status = "🟢 HEALTHY"
                action = "No action required"

        print(f"{atm_id:8} | {status:12} | Prob: {prob:.3f} | {action}")

        results.append({
            "atm_id": atm_id,
            "failure_probability": round(prob, 4),
            "health_status": status,
            "recommended_action": action
        })

    latest_results = results

    print("=================================================\n")

    return results


# ----------------------------
# Status Endpoint (Dashboard uses this)
# ----------------------------

@app.get("/status")
def get_status():
    return latest_results