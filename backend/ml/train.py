import pandas as pd
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

# -----------------------------
# Load dataset
# -----------------------------

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "../data/atmcsv.csv")

df = pd.read_csv(DATA_PATH)

# Fill missing values if any
df = df.fillna(0)

# -----------------------------
# Define Features & Target
# -----------------------------

TARGET = "failure_within_24h"

X = df.drop([
    "timestamp",
    "atm_id",
    "failure_within_24h",
    "failure_within_48h",  # 🔥 add this
    "failure_cause"
], axis=1)
y = df[TARGET]

# -----------------------------
# Train/Test Split
# -----------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# -----------------------------
# Train RandomForest
# -----------------------------

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    n_jobs=-1, 
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

# -----------------------------
# Evaluate
# -----------------------------

pred = model.predict(X_test)
proba = model.predict_proba(X_test)[:, 1]

print("Classification Report:\n")
print(classification_report(y_test, pred))

print("AUC Score:", roc_auc_score(y_test, proba))

# -----------------------------
# Save Model
# -----------------------------

MODEL_PATH = os.path.join(BASE_DIR, "failure_model.pkl")
joblib.dump(model, MODEL_PATH)

print("\nModel saved as failure_model.pkl")