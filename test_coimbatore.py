import joblib
import numpy as np
model = joblib.load("models/crop_model.pkl")
scaler = joblib.load("models/scaler.pkl")
le = joblib.load("models/label_encoder.pkl")
features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
# Coimbatore approx
params = {"N": 320, "P": 18, "K": 220, "temperature": 28.0, "humidity": 70.0, "ph": 6.8, "rainfall": 150.0}
X = np.array([[params[f] for f in features]])
X_scaled = scaler.transform(X)
proba = model.predict_proba(X_scaled)[0]
top3_idx = np.argsort(proba)[-3:][::-1]
top3 = [(le.classes_[i], round(float(proba[i]) * 100, 1)) for i in top3_idx]
print("Coimbatore:", top3)
