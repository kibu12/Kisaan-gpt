"""agents/soil_analyst_agent.py"""
import json
import os

class SoilAnalystAgent:
    def __init__(self):
        try:
            # Base directory (project root)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            with open(os.path.join(base_dir, "models", "model_metadata.json")) as f:
                self.thresholds = json.load(f)["soil_thresholds"]
        except (FileNotFoundError, KeyError):
            self.thresholds = {
                "ph_critical_low": 5.5, "ph_warning_low": 6.0, "ph_optimal_max": 7.5,
                "ec_salinity_danger": 4.0, "oc_critical_low": 0.5,
                "n_low": 280, "p_low": 10, "k_low": 108
            }

    def analyze(self, params: dict) -> dict:
        issues, warnings = [], []
        ph = params.get("ph", 7.0)

        if ph < self.thresholds["ph_critical_low"]:
            issues.append({
                "parameter": "pH", "value": ph, "status": "CRITICAL",
                "message": f"pH {ph:.1f} is below 5.5 — aluminium toxicity risk.",
                "action": "Apply agricultural lime @ 2–3 tonnes/ha immediately."
            })
        elif ph < self.thresholds["ph_warning_low"]:
            warnings.append({
                "parameter": "pH", "value": ph, "status": "WARNING",
                "message": f"pH {ph:.1f} is approaching critical acidic zone.",
                "action": "Apply lime @ 1 tonne/ha this season."
            })
        elif ph > self.thresholds["ph_optimal_max"]:
            warnings.append({
                "parameter": "pH", "value": ph, "status": "WARNING",
                "message": f"pH {ph:.1f} is alkaline — some micronutrients unavailable.",
                "action": "Apply gypsum @ 2 tonnes/ha."
            })

        ec = params.get("ec", 0)
        if ec > self.thresholds["ec_salinity_danger"]:
            issues.append({
                "parameter": "EC", "value": ec, "status": "CRITICAL",
                "message": f"EC {ec} dS/m — salt toxicity risk for most crops.",
                "action": "Leach salts with excess irrigation. Apply gypsum."
            })

        oc = params.get("oc", 0.75)
        if oc < self.thresholds["oc_critical_low"]:
            warnings.append({
                "parameter": "Organic Carbon", "value": oc, "status": "LOW",
                "message": f"OC {oc}% is critically low — soil biological activity reduced.",
                "action": "Apply FYM 10 tonnes/ha. Incorporate crop residues."
            })

        for nutrient, key, thr in [
            ("Nitrogen", "N", "n_low"),
            ("Phosphorus", "P", "p_low"),
            ("Potassium", "K", "k_low"),
        ]:
            if params.get(key, 999) < self.thresholds[thr]:
                warnings.append({
                    "parameter": nutrient, "value": params.get(key), "status": "LOW",
                    "message": f"{nutrient} below optimal range ({params.get(key)} kg/ha).",
                    "action": f"Supplement {nutrient} before next sowing."
                })

        # ── Soil-type-specific warnings ──
        soil_type = params.get("soil_type", "").lower()
        rainfall  = params.get("rainfall", 100)

        if "sandy" in soil_type:
            if oc < 0.75:
                warnings.append({
                    "parameter": "Soil Type (Sandy)", "value": soil_type, "status": "WARNING",
                    "message": "Sandy soil with low organic carbon — high nutrient leaching risk.",
                    "action": "Apply FYM/compost 12–15 tonnes/ha. Use split fertilizer doses."
                })
        elif "clay" in soil_type:
            if rainfall > 150:
                warnings.append({
                    "parameter": "Soil Type (Clay)", "value": soil_type, "status": "WARNING",
                    "message": "Heavy clay soil with high rainfall — waterlogging risk.",
                    "action": "Ensure adequate drainage. Consider raised-bed planting."
                })
        elif "laterite" in soil_type:
            warnings.append({
                "parameter": "Soil Type (Laterite)", "value": soil_type, "status": "WARNING",
                "message": "Laterite soils are typically acidic and phosphorus-fixing.",
                "action": "Apply rock phosphate or single super phosphate. Lime if pH < 6.0."
            })
        elif "saline" in soil_type or "alkaline" in soil_type:
            warnings.append({
                "parameter": "Soil Type (Saline/Alkaline)", "value": soil_type, "status": "WARNING",
                "message": "Saline/alkaline soils restrict crop choices and nutrient uptake.",
                "action": "Apply gypsum @ 2–5 tonnes/ha. Grow salt-tolerant varieties."
            })

        return {
            "issues":         issues,
            "warnings":       warnings,
            "overall_health": "CRITICAL" if issues else ("WARNING" if warnings else "GOOD"),
        }
