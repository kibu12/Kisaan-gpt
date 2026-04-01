"""
backend/main.py — FastAPI backend for KisaanGPT
Serves the API endpoints and the static React frontend build.
"""
import os
import sys
import traceback
import os
import sys
import subprocess
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Add parent directory to path so we can import agents, memory, etc.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


# ── Auto-Training Lifecycle ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Check if models exist, if not, train them
    model_path = os.path.join(os.path.dirname(__file__), "..", "models", "crop_model.pkl")
    train_script = os.path.join(os.path.dirname(__file__), "..", "models", "train_crop_model.py")
    
    if not os.path.exists(model_path) and os.path.exists(train_script):
        print("🏗️ First-time setup: Training ML models...")
        try:
            result = subprocess.run([sys.executable, train_script], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Models trained successfully!")
            else:
                print(f"❌ Training failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Error triggering training: {e}")
    yield
    # Shutdown logic (if any) goes here

app = FastAPI(title="KisaanGPT API", version="1.0.0", lifespan=lifespan)


# CORS for local dev (React dev server on port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Lazy-loaded singletons ────────────────────────────────────────────────────
_orchestrator = None
_farm_fns = None
_auth_fns = None


def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        from agents.orchestrator import OrchestratorAgent
        _orchestrator = OrchestratorAgent()
    return _orchestrator


def get_farm_fns():
    global _farm_fns
    if _farm_fns is None:
        try:
            from memory.farm_twin import ensure_farm, save_reading, get_farm_history, get_trajectory
            _farm_fns = {"ensure_farm": ensure_farm, "save_reading": save_reading,
                         "get_farm_history": get_farm_history, "get_trajectory": get_trajectory}
        except Exception:
            _farm_fns = {}
    return _farm_fns


def get_auth_fns():
    global _auth_fns
    if _auth_fns is None:
        try:
            from memory.farm_twin import register_farmer, authenticate_farmer, get_farm_profile
            _auth_fns = {"register": register_farmer, "authenticate": authenticate_farmer,
                         "get_profile": get_farm_profile}
        except Exception:
            _auth_fns = {}
    return _auth_fns


# ── Pydantic Models ───────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    farm_id: str
    password: str


class SignupRequest(BaseModel):
    farm_id: str
    farmer_name: str
    password: str
    location: str = ""
    district: str = ""


class SoilAnalysisRequest(BaseModel):
    soil_params: dict
    location: str = "Coimbatore"
    farmer_query: str = "Which crop should I plant this season and how much fertilizer do I need?"
    language: str = "en"
    season: str = "Kharif 2025"
    farm_id: str = ""
    farmer_name: str = ""


class ChatRequest(BaseModel):
    query: str
    location: str = "Coimbatore"
    language: str = "en"


# ── Health Check ──────────────────────────────────────────────────────────────

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "KisaanGPT API"}


# ── Authentication Endpoints ─────────────────────────────────────────────────

@app.post("/api/auth/login")
def login(req: LoginRequest):
    auth = get_auth_fns()
    if "authenticate" not in auth:
        raise HTTPException(status_code=503, detail="Database connection missing.")
    
    if auth["authenticate"](req.farm_id, req.password):
        profile = auth["get_profile"](req.farm_id)
        return {
            "success": True,
            "farm_id": req.farm_id,
            "farmer_name": profile.get("farmer_name", ""),
            "district": profile.get("district", ""),
            "location": profile.get("location", ""),
        }
    raise HTTPException(status_code=401, detail="Invalid Farm ID or Password.")


@app.post("/api/auth/signup")
def signup(req: SignupRequest):
    auth = get_auth_fns()
    if "register" not in auth:
        raise HTTPException(status_code=503, detail="Database connection missing.")
    
    success = auth["register"](
        req.farm_id, req.farmer_name, req.password,
        req.location, req.district, ""
    )
    if success:
        return {"success": True, "message": "Profile created!"}
    raise HTTPException(status_code=409, detail="Farm ID already exists.")


# ── Soil Analysis Endpoint ───────────────────────────────────────────────────

@app.post("/api/analyze")
def analyze_soil(req: SoilAnalysisRequest):
    try:
        orch = get_orchestrator()
        result = orch._run_crop(
            soil_params=req.soil_params,
            location=req.location,
            query=req.farmer_query,
            language=req.language,
            season=req.season,
        )

        # Save to farm twin if possible
        farm_fns = get_farm_fns()
        farm_saved = False
        if req.farm_id and "save_reading" in farm_fns:
            try:
                if req.farmer_name:
                    farm_fns["ensure_farm"](req.farm_id, req.farmer_name, req.location, req.location)
                farm_fns["save_reading"](req.farm_id, req.soil_params, result["crop_predictions"], req.season)
                farm_saved = True
            except Exception:
                pass

        # Serialize DataFrame if present
        serialized = serialize_result(result)
        serialized["farm_saved"] = farm_saved
        return serialized

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Chat Endpoint ────────────────────────────────────────────────────────────

@app.post("/api/chat")
def chat(req: ChatRequest):
    try:
        orch = get_orchestrator()
        result = orch.run(
            soil_params={},
            location=req.location,
            farmer_query=req.query,
            language=req.language,
        )
        return serialize_result(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Image Analysis Endpoint ──────────────────────────────────────────────────

@app.post("/api/analyze-image")
async def analyze_image(
    image: UploadFile = File(...),
    query: str = Form("What disease does this plant have?"),
    language: str = Form("en"),
):
    try:
        orch = get_orchestrator()
        image_bytes = await image.read()
        result = orch.analyze_image(image_bytes, query, language)
        return serialize_result(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Farm History Endpoint ────────────────────────────────────────────────────

@app.get("/api/farm/{farm_id}/history")
def farm_history(farm_id: str):
    farm_fns = get_farm_fns()
    if "get_farm_history" not in farm_fns:
        raise HTTPException(status_code=503, detail="Database not configured.")
    
    history = farm_fns["get_farm_history"](farm_id)
    trajectory = farm_fns["get_trajectory"](farm_id)
    return {"history": history, "trajectory": trajectory}


# ── Utility ──────────────────────────────────────────────────────────────────

def serialize_result(result: dict) -> dict:
    """Convert any non-JSON-serializable objects (like DataFrames) to dicts."""
    import pandas as pd
    serialized = {}
    for key, value in result.items():
        if isinstance(value, pd.DataFrame):
            serialized[key] = value.to_dict(orient="records") if not value.empty else []
        else:
            serialized[key] = value
    return serialized


# ── Serve React static build (production) ────────────────────────────────────
# In production, the React app is built and placed in frontend/dist/
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the React SPA for any non-API route."""
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
