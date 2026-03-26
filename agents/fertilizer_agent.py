"""agents/fertilizer_agent.py"""
import joblib
import os

CROP_N = {
    "rice":9, "wheat":9, "maize":9, "sugarcane":9,
    "cotton":9, "groundnut":9, "chickpea":9, "lentil":9,
    "banana":9, "mango":9, "grapes":9, "watermelon":9,
    "muskmelon":9, "apple":9, "orange":9, "papaya":9,
    "coconut":9, "coffee":9, "jute":9, "kidneybeans":9,
    "mothbeans":9, "mungbean":9, "blackgram":9, "pigeonpeas":9,
    "pomegranate":9,
}

BASELINE = {
    "rice":       (120, 60, 60),
    "wheat":      (120, 60, 40),
    "maize":      (150, 75, 60),
    "groundnut":  (25,  50, 75),
    "cotton":     (120, 60, 60),
    "sugarcane":  (275, 62, 112),
    "chickpea":   (20,  40, 20),
    "default":    (90,  45, 45),
}

class FertilizerAgent:
    def __init__(self):
        try:
            # Base directory (project root)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            self.model   = joblib.load(os.path.join(base_dir, "models", "fertilizer_model.pkl"))
            self.le_fert = joblib.load(os.path.join(base_dir, "models", "fertilizer_le.pkl"))
            self._has_model = True
        except Exception:
            self._has_model = False

    def recommend(self, soil_params: dict, crop: str) -> dict:
        crop_lower = crop.lower().replace(" ", "")
        base_n, base_p, base_k = BASELINE.get(crop_lower, BASELINE["default"])

        soil_n = soil_params.get("N", 90)
        soil_p = soil_params.get("P", 42)
        soil_k = soil_params.get("K", 43)

        dose_n = max(int(base_n * 0.2), base_n - int(soil_n * 0.25))
        dose_p = max(int(base_p * 0.2), base_p - int(soil_p * 0.5))
        dose_k = max(int(base_k * 0.2), base_k - int(soil_k * 0.2))

        # ── Adjust doses by soil type ──
        soil_type = soil_params.get("soil_type", "").lower()
        land_acres = soil_params.get("land_acres", 1.0)
        app_note = "Apply P & K as basal. Split N: 50% basal + 25% at 30 days + 25% at 60 days."

        if "sandy" in soil_type:
            dose_n = int(dose_n * 1.20)          # +20% N — sandy soils leach nitrogen
            app_note = ("Sandy soil: split N into 4 doses (25% each at 0, 20, 40, 60 days) "
                        "to reduce leaching. Apply P & K as basal.")
        elif "clay" in soil_type:
            dose_n = int(dose_n * 0.90)           # -10% N — clay retains better
            app_note = ("Clay soil retains nutrients well. Apply P & K as basal. "
                        "Split N: 50% basal + 50% at 30 days.")
        elif "laterite" in soil_type:
            dose_p = int(dose_p * 1.15)           # +15% P — laterite fixes phosphorus
            app_note = ("Laterite soil fixes phosphorus. Use rock phosphate or SSP. "
                        "Split N: 50% basal + 25% at 30 days + 25% at 60 days.")

        # Convert kg/ha to total kg for the given acreage (1 acre = 0.404686 hectares)
        hectares = land_acres * 0.404686
        total_n = int(dose_n * hectares)
        total_p = int(dose_p * hectares)
        total_k = int(dose_k * hectares)

        return {
            "primary_fertilizer": "DAP + Urea + MOP",
            "n_dose_kg_ha":  dose_n,
            "p_dose_kg_ha":  dose_p,
            "k_dose_kg_ha":  dose_k,
            "total_n_kg":    total_n,
            "total_p_kg":    total_p,
            "total_k_kg":    total_k,
            "application_note": app_note,
            "source":        "ICAR fertilizer recommendation table (adjusted for soil type & nutrient status)",
        }
