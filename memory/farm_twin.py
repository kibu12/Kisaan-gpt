"""memory/farm_twin.py — Supabase-backed farm digital twin"""
from rag.supabase_client import get_supabase
import hashlib

def hash_password(password: str) -> str:
    """Returns a SHA-256 hash of the password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def register_farmer(farm_id: str, farmer_name: str, password: str, 
                    location: str, district: str, season: str, area_acres: float = 0.0) -> bool:
    """Registers a new farm profile with a password hash and default season."""
    supabase = get_supabase()
    # Check if exists
    res = supabase.table("farms").select("farm_id").eq("farm_id", farm_id).execute()
    if res.data:
        return False  # Farm ID already taken

    supabase.table("farms").insert({
        "farm_id":      farm_id,
        "farmer_name":  farmer_name,
        "password_hash": hash_password(password),
        "location":     location,
        "district":     district,
        "area_acres":   area_acres,
        # We can store the initial season conceptually, but for now it's in soil_readings.
        # However, to let the UI remember the current season setting, we can return True.
    }).execute()
    return True

def authenticate_farmer(farm_id: str, password: str) -> bool:
    """Verifies the farm_id and password match."""
    supabase = get_supabase()
    res = supabase.table("farms").select("password_hash").eq("farm_id", farm_id).execute()
    if not res.data:
        return False
    
    stored_hash = res.data[0].get("password_hash")
    if not stored_hash:
        return False  # Existing users without a password cannot log in via this method
        
    return stored_hash == hash_password(password)

def get_farm_profile(farm_id: str) -> dict:
    """Fetches the static farm profile details."""
    supabase = get_supabase()
    res = supabase.table("farms").select("farmer_name, location, district").eq("farm_id", farm_id).execute()
    if res.data:
        return res.data[0]
    return {}

def ensure_farm(farm_id: str, farmer_name: str, location: str,
                district: str, area_acres: float = 0.0):
    supabase = get_supabase()
    supabase.table("farms").upsert({
        "farm_id":      farm_id,
        "farmer_name":  farmer_name,
        "location":     location,
        "district":     district,
        "area_acres":   area_acres,
    }).execute()

def save_reading(farm_id: str, params: dict, recommendation: dict, season: str):
    supabase = get_supabase()
    supabase.table("soil_readings").insert({
        "farm_id":          farm_id,
        "season":           season,
        "n_val":            params.get("N"),
        "p_val":            params.get("P"),
        "k_val":            params.get("K"),
        "ph":               params.get("ph"),
        "humidity":         params.get("humidity"),
        "temperature":      params.get("temperature"),
        "rainfall":         params.get("rainfall"),
        "ec":               params.get("ec", 0),
        "oc":               params.get("oc", 0),
        "recommended_crop": recommendation.get("top_crop"),
        "confidence":       recommendation.get("top_crop_confidence"),
    }).execute()


def get_farm_history(farm_id: str) -> list[dict]:
    supabase = get_supabase()
    resp = (
        supabase.table("soil_readings")
        .select("reading_date,season,n_val,p_val,k_val,ph,oc,ec,recommended_crop,confidence")
        .eq("farm_id", farm_id)
        .order("reading_date", desc=True)
        .limit(10)
        .execute()
    )
    return resp.data or []


def get_trajectory(farm_id: str) -> dict:
    history = get_farm_history(farm_id)
    if len(history) < 2:
        return {"status": "insufficient_data", "seasons": len(history)}

    ph_values = [r["ph"] for r in history if r.get("ph") is not None]
    if len(ph_values) < 2:
        return {"status": "insufficient_data"}

    ph_values = list(reversed(ph_values))   # oldest → newest
    ph_trend  = ph_values[-1] - ph_values[0]
    rate      = ph_trend / (len(ph_values) - 1)

    seasons_to_critical = None
    if rate < 0 and ph_values[-1] > 5.5:
        seasons_to_critical = int((ph_values[-1] - 5.5) / abs(rate))

    return {
        "ph_trend":               "degrading" if ph_trend < -0.1 else ("improving" if ph_trend > 0.1 else "stable"),
        "ph_current":             ph_values[-1],
        "ph_change_total":        round(ph_trend, 2),
        "seasons_to_critical_ph": seasons_to_critical,
        "alert":                  seasons_to_critical is not None and seasons_to_critical <= 3,
    }
