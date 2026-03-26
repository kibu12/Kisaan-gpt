import joblib
import numpy as np

model = joblib.load("models/crop_model.pkl")
scaler = joblib.load("models/scaler.pkl")
le = joblib.load("models/label_encoder.pkl")
features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

# Default values from UI
default_params = {"N": 150, "P": 60, "K": 80, "temperature": 25.0, "humidity": 65.0, "ph": 6.5, "rainfall": 103.0}

# Rice values
rice_params = {"N": 270, "P": 58, "K": 86, "temperature": 20.8, "humidity": 82.0, "ph": 6.5, "rainfall": 203.0}

for name, params in [("Default UI values", default_params), ("Rice typical values", rice_params)]:
    X = np.array([[params[f] for f in features]])
    X_scaled = scaler.transform(X)
    proba = model.predict_proba(X_scaled)[0]
    top3_idx = np.argsort(proba)[-3:][::-1]
    top3 = [(le.classes_[i], round(float(proba[i]) * 100, 1)) for i in top3_idx]
    print(f"--- {name} ---")
    print(f"Top 3 crops & confidence: {top3}\n")
