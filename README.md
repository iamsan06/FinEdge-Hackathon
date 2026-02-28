🏦 AI-Based ATM Health Monitoring & Failure Prediction System
🚀 Overview

This project is an AI-powered ATM Operational Monitoring System that predicts potential ATM failures in real time and visualizes ATM health across Chennai using an interactive dashboard.

The system uses a Random Forest machine learning model to estimate failure probability and classify ATM health into:

🟢 Healthy

🟡 Warning

🔴 Critical

This is Version 1.0.0 (Prototype Release).

🎯 Problem Statement

ATM failures lead to:

Customer dissatisfaction

Revenue loss due to downtime

Reactive maintenance instead of predictive

Lack of centralized operational visibility

This project demonstrates a predictive, AI-driven solution.

🧠 Solution Architecture (Prototype v1)
ATM Data Simulation
        ↓
Random Forest Model (Failure Probability)
        ↓
Streamlit Dashboard
        ↓
Live Monitoring + Chennai Map Visualization

This version runs as a standalone Streamlit application (monolithic architecture for deployment simplicity).

🛠 Tech Stack

Python

Scikit-learn (Random Forest)

Streamlit

PyDeck (Map Visualization)

Pandas / NumPy

Joblib (Model Loading)

📊 Features (v1.0.0)

✅ Real-time ATM health simulation
✅ Failure probability prediction
✅ Status classification (Healthy / Warning / Critical)
✅ Live dashboard refresh
✅ Chennai ATM geo-visualization
✅ Color-coded health indicators
✅ Action recommendations per ATM

📍 Dashboard Capabilities

Premium summary metric cards

Interactive Chennai map

Tooltip with probability and status

Live auto-refresh every few seconds

Structured ATM status cards
