"""agents/crop_predictor_agent.py"""
import joblib
import numpy as np
import json
import os

class CropPredictorAgent:
    def __init__(self):
        # Base directory (project root)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.model  = joblib.load(os.path.join(base_dir, "models", "crop_model.pkl"))
        self.scaler = joblib.load(os.path.join(base_dir, "models", "scaler.pkl"))
        self.le     = joblib.load(os.path.join(base_dir, "models", "label_encoder.pkl"))
        self.features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
        
        # Load regional metadata for filtering
        meta_path = os.path.join(base_dir, "models", "model_metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
        self.regional_mapping = self.metadata.get("regional_mapping", {})

    def predict(self, params: dict, location: str = "", season: str = "") -> dict:
        X        = np.array([[params.get(f, 0) for f in self.features]])
        X_scaled = self.scaler.transform(X)
        proba    = self.model.predict_proba(X_scaled)[0]
        
        # 1. Apply strict regional filter
        if location and location in self.regional_mapping:
            allowed_by_region = set(self.regional_mapping[location].get("crop_classes", []))
        else:
            allowed_by_region = set(self.le.classes_)

        # 2. Apply strict seasonal filter
        base_season = season.split()[0] if season else ""
        if location == "Nilgiris":
            base_season = "Nilgiris_Annual"
            
        self.seasonal_mapping = self.metadata.get("seasonal_mapping", {})
        if base_season and base_season in self.seasonal_mapping:
            allowed_by_season = set(self.seasonal_mapping[base_season])
        else:
            allowed_by_season = set(self.le.classes_)

        # 3. Intersect both filters
        final_allowed = allowed_by_region.intersection(allowed_by_season)

        for i, crop_name in enumerate(self.le.classes_):
            if crop_name not in final_allowed:
                proba[i] = 0.0  # Force probability to 0 for impossible crops

        # Re-normalize probabilities so they act as relative confidence
        total_prob = np.sum(proba)
        if total_prob > 0:
            proba = proba / total_prob

        top3_idx = np.argsort(proba)[-3:][::-1]
        top3     = [(self.le.classes_[i], round(float(proba[i]) * 100, 1)) for i in top3_idx if proba[i] > 0]
        
        if not top3:
            top3 = [("Unknown (No suitable crop found)", 0.0)]

        return {
            "top_crop":            top3[0][0],
            "top_crop_confidence": top3[0][1],
            "top_3":               top3,
        }
