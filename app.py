"""
app.py — KISAAN-GPT Streamlit Application
Apple-esque minimalist UI: clean white/light-gray, sage-green accents, Inter font.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import tempfile, os, json, subprocess
from dotenv import load_dotenv

# Load env variables (GROQ_API_KEY, SUPABASE_URL, etc.)
load_dotenv()

# ── Page config (must be first) ──────────────────────────────────────────────
st.set_page_config(
    page_title="KisaanGPT - Your AI Agriculture Assistant",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

import os
import base64

logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    st.logo(
        f"data:image/png;base64,{img_b64}",
        size="large"
    )
    
    # Update page config icon to use same base64 if it fails otherwise
    # st.set_page_config is above this, so relying on filepath there is usually fine.




# ── Auto-Training Logic ──────────────────────────────────────────────────────
def ensure_models_trained():
    """Checks if the model file exists; if not, runs the training script."""
    # Adjust 'crop_model.pkl' to the actual name your training script outputs
    model_path = os.path.join("models", "crop_model.pkl") 
    train_script = os.path.join("models", "train_crop_model.py")

    if not os.path.exists(model_path):
        if os.path.exists(train_script):
            with st.status("🏗️ First-time setup: Training AI models...", expanded=True) as status:
                st.write("Initializing RandomForest Regressor...")
                try:
                    # Run the training script
                    result = subprocess.run(["python", train_script], capture_output=True, text=True)
                    if result.returncode == 0:
                        status.update(label="✅ Models trained successfully!", state="complete", expanded=False)
                    else:
                        st.error(f"Training script failed: {result.stderr}")
                except Exception as e:
                    st.error(f"Error triggering training: {e}")
        else:
            st.error("Model files and training script are both missing!")

# Trigger the check immediately
ensure_models_trained() 

# Inject Google Search Console verification meta tag using Streamlit components
import streamlit.components.v1 as components
components.html(
    """
    <meta name="google-site-verification" content="YOUR_VERIFICATION_CODE_HERE" />
    """,
    height=0,
    width=0,
)


# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS — Apple-esque minimalist design system
# Palette:  Background #F8F9FA · Surface #FFFFFF · Primary #2E7D32
#           Secondary #607D8B · Text #212121 · Border #E0E0E0
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: #212121;
}
.main { background: #F8F9FA !important; }
.main .block-container {
    padding: 2.5rem 3rem 3rem;
    max-width: 1320px;
}

/* ── Sidebar — frosted glass ── */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.72) !important;
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border-right: 1px solid rgba(0, 0, 0, 0.06);
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    font-family: 'Inter', sans-serif;
}

/* ── Typography ── */
h1 {
    font-family: 'Inter', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #212121;
    letter-spacing: -0.03em;
}
h2 {
    font-family: 'Inter', sans-serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: #212121;
    letter-spacing: -0.01em;
}
h3 {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    font-weight: 600;
    color: #607D8B;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Metric cards ── */
.metric-card {
    background: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease;
}
.metric-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.07); }
.metric-label {
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: #607D8B; margin-bottom: 6px;
}
.metric-value {
    font-size: 1.75rem; font-weight: 700;
    color: #212121; font-family: 'Inter', sans-serif;
}
.metric-unit { font-size: 12px; color: #9E9E9E; margin-left: 4px; font-weight: 400; }

/* ── Status badges (pill style) ── */
.badge-good {
    background: #E8F5E9; color: #2E7D32;
    border: none; border-radius: 20px;
    padding: 4px 14px; font-size: 12px; font-weight: 600;
    display: inline-block;
}
.badge-warning {
    background: #FFF8E1; color: #F57F17;
    border: none; border-radius: 20px;
    padding: 4px 14px; font-size: 12px; font-weight: 600;
    display: inline-block;
}
.badge-critical {
    background: #FFEBEE; color: #C62828;
    border: none; border-radius: 20px;
    padding: 4px 14px; font-size: 12px; font-weight: 600;
    display: inline-block;
}

/* ── Alert boxes ── */
.alert-critical {
    background: #FFFFFF; border-left: 4px solid #EF5350;
    border-radius: 0 12px 12px 0; padding: 1rem 1.25rem;
    margin: 0.5rem 0; font-size: 13px; color: #424242;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.alert-warning {
    background: #FFFFFF; border-left: 4px solid #FFA726;
    border-radius: 0 12px 12px 0; padding: 1rem 1.25rem;
    margin: 0.5rem 0; font-size: 13px; color: #424242;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.alert-info {
    background: #FFFFFF; border-left: 4px solid #66BB6A;
    border-radius: 0 12px 12px 0; padding: 1rem 1.25rem;
    margin: 0.5rem 0; font-size: 13px; color: #424242;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* ── Advisory card ── */
.advisory-card {
    background: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 14px;
    padding: 1.75rem;
    line-height: 1.8;
    font-size: 14px;
    color: #424242;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* ── Fertilizer plan card ── */
.fert-card {
    background: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.fert-row { display: flex; gap: 2.5rem; margin-top: 0.75rem; }
.fert-item { text-align: center; }
.fert-item .val {
    font-size: 1.5rem; font-weight: 700;
    font-family: 'Inter', sans-serif; color: #212121;
}
.fert-item .lbl {
    font-size: 11px; font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.06em; color: #607D8B;
}

/* ── Crop confidence card ── */
.crop-card {
    background: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 12px;
    padding: 0.85rem 1.25rem;
    margin-bottom: 0.5rem;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease, transform 0.15s ease;
}
.crop-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.07); transform: translateY(-1px); }
.crop-name { font-size: 14px; font-weight: 600; color: #212121; }
.crop-conf { font-size: 13px; color: #607D8B; font-weight: 500; }
.crop-bar-outer { background: #E8F5E9; border-radius: 4px; height: 6px; width: 120px; }
.crop-bar-inner { background: #2E7D32; border-radius: 4px; height: 6px; }

/* ── Section divider ── */
.section-divider { border: none; border-top: 1px solid #E0E0E0; margin: 1.75rem 0; }

/* ── Tab styling ── */
[data-testid="stHorizontalBlock"] { gap: 1.5rem; }
.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif;
    font-size: 13px; font-weight: 500;
    color: #9E9E9E;
}
.stTabs [aria-selected="true"] { color: #2E7D32; font-weight: 600; }

/* ── Buttons ── */
.stButton > button {
    background: #2E7D32 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 2px 8px rgba(46, 125, 50, 0.25) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #1B5E20 !important;
    box-shadow: 0 4px 14px rgba(46, 125, 50, 0.35) !important;
    transform: translateY(-1px);
}

/* ── Sliders ── */
[data-testid="stSlider"] > div > div > div { background: #C8E6C9 !important; }
[data-testid="stSlider"] [data-testid="stThumbValue"] { color: #2E7D32; font-weight: 600; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #2E7D32 !important; }

/* ── Header strip ── */
.page-header {
    display: flex; align-items: center; gap: 1rem;
    padding-bottom: 1.25rem; border-bottom: 1px solid #E0E0E0;
    margin-bottom: 2rem;
}
.page-header h1 { margin: 0; }
.header-tag {
    background: #E8F5E9; color: #2E7D32;
    border-radius: 20px; padding: 5px 14px;
    font-size: 11px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.06em;
}

/* ── Inputs (text, select) ── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] > div > div {
    border-radius: 10px !important;
    border-color: #E0E0E0 !important;
    font-family: 'Inter', sans-serif !important;
}
textarea {
    border-radius: 10px !important;
    border-color: #E0E0E0 !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #E0E0E0;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ── Lazy imports ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_orchestrator():
    try:
        from agents.orchestrator import OrchestratorAgent
        return OrchestratorAgent()
    except Exception as e:
        import traceback
        st.error(f"Failed to load AI Orchestrator: {e}")
        st.code(traceback.format_exc())
        return None

@st.cache_resource(show_spinner=False)
def load_farm_fns():
    try:
        from memory.farm_twin import ensure_farm, save_reading, get_farm_history, get_trajectory
        return ensure_farm, save_reading, get_farm_history, get_trajectory
    except Exception:
        return None, None, None, None

@st.cache_resource(show_spinner=False)
def load_auth_fns():
    try:
        from memory.farm_twin import register_farmer, authenticate_farmer, get_farm_profile
        return register_farmer, authenticate_farmer, get_farm_profile
    except Exception:
        return None, None, None

orchestrator = load_orchestrator()
ensure_farm, save_reading, get_farm_history, get_trajectory = load_farm_fns()
register_farmer, authenticate_farmer, get_farm_profile = load_auth_fns()

# ── Authentication UI ─────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown('<div class="page-header" style="justify-content:center; border:none; margin-top:40px;"><h1>🌾 KisaanGPT</h1></div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#607D8B; margin-bottom:40px;">KisaanGPT is your AI Agriculture Assistant providing intelligent soil analysis and recommendations — Please Log In</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["🔒 Login", "📝 Sign Up"])
        
        with tab_login:
            with st.container(border=True):
                l_id = st.text_input("Farm Profile ID")
                l_pwd = st.text_input("Password", type="password")
                if st.button("Log In", use_container_width=True, type="primary"):
                    if authenticate_farmer is None:
                        st.error("Database connection missing.")
                    elif authenticate_farmer(l_id, l_pwd):
                        st.session_state["logged_in"] = True
                        st.session_state["farm_id"] = l_id
                        profile = get_farm_profile(l_id)
                        st.session_state["farmer_name"] = profile.get("farmer_name", "")
                        st.session_state["district"] = profile.get("district", "")
                        st.rerun()
                    else:
                        st.error("Invalid Farm ID or Password.")
        
        with tab_signup:
            with st.container(border=True):
                s_id = st.text_input("New Farm ID *")
                s_name = st.text_input("Farmer Name *")
                c_loc, c_dist = st.columns(2)
                with c_loc:
                    s_loc = st.text_input("Location/Village")
                with c_dist:
                    s_dist = st.text_input("District")
                s_pwd = st.text_input("Create Password *", type="password")
                s_pwd2 = st.text_input("Confirm Password *", type="password")
                
                if st.button("Create Profile", use_container_width=True, type="primary"):
                    if not s_id or not s_name or not s_pwd:
                        st.error("Please fill in all required (*) fields.")
                    elif s_pwd != s_pwd2:
                        st.error("Passwords do not match.")
                    elif register_farmer is None:
                        st.error("Database connection missing.")
                    else:
                        success = register_farmer(s_id, s_name, s_pwd, s_loc, s_dist, "")
                        if success:
                            st.success("Profile created! Please switch to the Login tab.")
                        else:
                            st.error("Farm ID already exists or database error.")
                            
    st.stop()

# ── Plotly theme — clean, minimal, white ─────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=40, b=0, l=0, r=0),
    xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#F0F0F0")
)

BENCHMARK = {
    "Coimbatore": {"pH": 6.8, "N": 320, "P": 18, "K": 220, "OC": 0.68},
    "Erode":      {"pH": 6.5, "N": 290, "P": 15, "K": 195, "OC": 0.62},
    "Salem":      {"pH": 7.1, "N": 340, "P": 22, "K": 240, "OC": 0.71},
    "Tiruppur":   {"pH": 6.6, "N": 310, "P": 17, "K": 205, "OC": 0.65},
    "Nilgiris":   {"pH": 5.9, "N": 380, "P": 26, "K": 280, "OC": 0.91},
}

PRIMARY   = "#2E7D32"
SECONDARY = "#607D8B"
ACCENT    = "#FFA726"
MIST      = "#C8E6C9"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<p style="font-family:Inter,sans-serif;font-size:1.4rem;font-weight:700;'
        'color:#212121;margin-bottom:0;letter-spacing:-0.02em">🌾 KisaanGPT</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-size:11px;color:#9E9E9E;text-transform:uppercase;'
        'letter-spacing:0.08em;margin-top:2px;font-weight:500">Soil Intelligence Platform</p>',
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown("**Farm Profile**")
    st.info(f"👤 **{st.session_state.get('farmer_name', 'Unknown')}**\n\nID: {st.session_state.get('farm_id', '')}")
    
    farm_id      = st.session_state.get("farm_id", "")
    farmer_name  = st.session_state.get("farmer_name", "")
    location     = st.session_state.get("district", "Coimbatore")
    
    season       = st.selectbox("Season", ["Kharif 2025", "Rabi 2025-26", "Summer 2026"])
    soil_type    = st.selectbox("Soil Type", [
        "Alluvial", "Black (Regur)", "Red", "Laterite",
        "Sandy", "Clay", "Loamy", "Saline/Alkaline",
    ])
    language     = st.selectbox("Language / மொழி", ["English", "Tamil"])
    lang_code    = "ta" if language == "Tamil" else "en"
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.divider()
    st.markdown(
        '<p style="font-size:11px;color:#9E9E9E;font-weight:500">'
        'Model: RandomForest · ≈99% accuracy<br>'
        'RAG: Supabase pgvector · ICAR/TNAU docs</p>',
        unsafe_allow_html=True,
    )

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>KisaanGPT - Your AI Agriculture Assistant</h1>
  <span class="header-tag">Tamil Nadu</span>
  <span class="header-tag">AI-Powered</span>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "  Soil Analysis & Recommendation  ",
    "  Farm History & Trajectory  ",
    "  Voice Advisory  ",
    "  Regional Benchmark  ",
    "  AI Chat Assistant  ",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SOIL ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("### Soil parameters")
        
        c1, c2 = st.columns(2)
        with c1:
            N  = st.slider("Nitrogen N (kg/ha)",     0,   450,  320)
            P  = st.slider("Phosphorus P (kg/ha)",   0,   250,  18)
            K  = st.slider("Potassium K (kg/ha)",    0,   450,  220)
            ph = st.slider("Soil pH",              3.5,   9.5, 6.8, step=0.1)
        with c2:
            humidity    = st.slider("Humidity (%)",      14.0, 100.0, 70.0)
            temperature = st.slider("Temperature (°C)",   8.0,  44.0, 28.0)
            rainfall    = st.slider("Rainfall (mm)",     20.0, 300.0, 150.0)

        c3, c4, c5 = st.columns(3)
        with c3:
            ec = st.number_input("EC (dS/m)", 0.0, 10.0, 0.5, step=0.1)
        with c4:
            oc = st.number_input("Organic Carbon (%)", 0.0, 3.0, 0.75, step=0.05)
        with c5:
            land_acres = st.number_input("Land (Acres)", 0.1, 100.0, 1.0, step=0.1)

        farmer_query = "Which crop should I plant this season and how much fertilizer do I need?"
        run_btn = st.button("Get Recommendation →", type="primary", use_container_width=True)

    # ── Logic execution ──
    if run_btn:
        soil_params = {"N": N, "P": P, "K": K, "ph": ph, "humidity": humidity, "temperature": temperature, 
                       "rainfall": rainfall, "ec": ec, "oc": oc, "soil_type": soil_type, "land_acres": land_acres}
        if orchestrator is not None:
            with st.spinner("Consulting soil agents…"):
                result = orchestrator._run_crop(soil_params=soil_params, location=location, query=farmer_query, language=lang_code, season=season)
            st.session_state["last_result"] = result
            st.session_state["last_language"] = language
            st.session_state["last_lang_code"] = lang_code
            if save_reading:
                try:
                    if farmer_name: ensure_farm(farm_id, farmer_name, location, location)
                    save_reading(farm_id, soil_params, result["crop_predictions"], season)
                    st.session_state["farm_saved"] = True
                except: st.session_state["farm_saved"] = False

    # ── Display ──
    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        disp_language = st.session_state.get("last_language", language)
        disp_lang_code = st.session_state.get("last_lang_code", lang_code)
        
        with left:
            st.markdown("<br>", unsafe_allow_html=True)
            
            # ── Radar confidence chart ──
            ph_score = max(0, 100 - abs(ph - 6.5) * 30)
            nutrient_score = min(100, (N/140 + P/145 + K/205) * 33)
            climate_score = min(100, max(0, 100 - abs(temperature - 25) * 4))
            model_conf = result["crop_predictions"]["top_crop_confidence"]
            
            fig_radar = go.Figure(go.Scatterpolar(
                r=[model_conf, climate_score, nutrient_score, ph_score, model_conf],
                theta=["Soil fit", "Climate match", "Nutrient level", "pH score", "Soil fit"],
                fill="toself", fillcolor="rgba(46,125,50,0.08)",
                line=dict(color=PRIMARY, width=2), marker=dict(size=5, color=PRIMARY)
            ))
            fig_radar.update_layout(**PLOT_LAYOUT, polar=dict(radialaxis=dict(range=[0, 100], showticklabels=False), bgcolor="#FFFFFF"), height=280,
                                    title=dict(text=f"Confidence — {result['crop_predictions']['top_crop'].title()}", font=dict(size=13), x=0.5))
            st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False}, key="sidebar_radar")

            # ── Voice Advisory Button ──
            if st.button("▶  Play advisory in " + disp_language, key="play_advis_left_v2", use_container_width=True):
                try:
                    from voice.speaker import speak
                    audio_path = speak(result["final_advice"], disp_lang_code)
                    st.audio(audio_path)
                except: st.info("Voice output requires gTTS.")

        with right:
            # Soil health
            result = st.session_state["last_result"]
            disp_language = st.session_state.get("last_language", language)
            disp_lang_code = st.session_state.get("last_lang_code", lang_code)

            # ── Soil health status ──
            health = result["soil_analysis"]["overall_health"]
            badge_map = {"GOOD": "badge-good", "WARNING": "badge-warning", "CRITICAL": "badge-critical"}
            st.markdown(f'**Soil health:** <span class="{badge_map.get(health, "badge-good")}">{health}</span>', unsafe_allow_html=True)

            for issue in result["soil_analysis"]["issues"]:
                st.markdown(f'<div class="alert-critical"><strong>{issue["parameter"]}</strong> — {issue["message"]}<br><em>Action: {issue["action"]}</em></div>', unsafe_allow_html=True)
            for w in result["soil_analysis"]["warnings"]:
                st.markdown(f'<div class="alert-warning"><strong>{w["parameter"]}</strong> — {w["message"]}</div>', unsafe_allow_html=True)

            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

            # ── Crop prediction bars ──
            st.markdown("### Recommended crops")
            top3 = result["crop_predictions"]["top_3"]
            for i, (crop, conf) in enumerate(top3):
                bar_w = int(conf * 1.2)
                prefix = "→ " if i == 0 else ""
                st.markdown(f"""
                <div class="crop-card">
                  <span class="crop-name">{prefix}{crop.title()}</span>
                  <div style="display:flex;align-items:center;gap:10px">
                    <div class="crop-bar-outer"><div class="crop-bar-inner" style="width:{bar_w}px"></div></div>
                    <span class="crop-conf">{conf}%</span>
                  </div>
                </div>""", unsafe_allow_html=True)

            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

            # ── Advisory & Fertilizer Plan side-by-side ──
            col_adv, col_fert = st.columns([1.2, 1], gap="large")

            with col_adv:
                # ── Advisory ──
                st.markdown("### Advisory")
                st.markdown(f'<div class="advisory-card">{result["final_advice"].replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

            with col_fert:
                # ── Fertilizer plan ──
                fert = result["fertilizer"]
                st.markdown("### Fertilizer plan")
                st.markdown(f"""
                <div class="fert-card">
                  <div style="font-size:13px;color:#2E7D32;margin-bottom:8px;font-weight:600">{fert['primary_fertilizer']}</div>
                  <div class="fert-row">
                    <div class="fert-item"><div class="val">{fert['n_dose_kg_ha']}</div><div class="lbl">N kg/ha</div></div>
                    <div class="fert-item"><div class="val">{fert['p_dose_kg_ha']}</div><div class="lbl">P kg/ha</div></div>
                    <div class="fert-item"><div class="val">{fert['k_dose_kg_ha']}</div><div class="lbl">K kg/ha</div></div>
                  </div>
                  <div class="fert-row" style="margin-top: 1.2rem; border-top: 1px solid #F0F0F0; padding-top: 1.2rem;">
                    <div class="fert-item"><div class="val">{fert.get('total_n_kg', 0)}</div><div class="lbl">Total N (kg)</div></div>
                    <div class="fert-item"><div class="val">{fert.get('total_p_kg', 0)}</div><div class="lbl">Total P (kg)</div></div>
                    <div class="fert-item"><div class="val">{fert.get('total_k_kg', 0)}</div><div class="lbl">Total K (kg)</div></div>
                  </div>
                  <div style="font-size:12px;color:#607D8B;margin-top:15px">{fert['application_note']}</div>
                  <div style="font-size:11px;color:#9E9E9E;margin-top:4px">Source: {fert['source']}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

            # ── Farm twin save confirmation ──
            if st.session_state.get("farm_saved"):
                st.markdown('<div class="alert-info">Reading saved to Farm Digital Twin.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — FARM HISTORY
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Soil health timeline")

    if get_farm_history is None:
        st.info("Supabase not configured. Add SUPABASE_URL and SUPABASE_KEY to your .env file.")
    else:
        try:
            history    = get_farm_history(farm_id)
            trajectory = get_trajectory(farm_id)
        except Exception:
            history    = []
            trajectory = {"status": "insufficient_data"}

        if len(history) < 2:
            st.markdown('<div class="alert-info">Add at least 2 seasonal soil readings to unlock trajectory analysis.</div>', unsafe_allow_html=True)
        else:
            df_hist = pd.DataFrame(history).rename(columns={
                "n_val": "N", "p_val": "P", "k_val": "K",
                "recommended_crop": "crop", "reading_date": "date"
            })

            # Trajectory summary
            traj = trajectory.get("ph_trend", "stable")
            badge = "badge-critical" if traj == "degrading" else ("badge-good" if traj == "improving" else "badge-warning")
            st.markdown(f'**pH Trajectory:** <span class="{badge}">{traj.upper()}</span> &nbsp; Current pH: <strong>{trajectory.get("ph_current", "–")}</strong>', unsafe_allow_html=True)

            if trajectory.get("alert"):
                st.markdown(f'<div class="alert-critical">pH ALERT — At current rate, pH will reach the critical threshold (5.5) in approximately <strong>{trajectory["seasons_to_critical_ph"]} seasons</strong>. Apply lime immediately.</div>', unsafe_allow_html=True)

            c1, c2 = st.columns(2)

            with c1:
                # Use date instead of season for X axis, to prevent vertical stacking
                fig_ph = px.line(df_hist, x="date", y="ph", markers=True, hover_data=["season"],
                                 title=f"Soil pH over time (vs {location})")
                dist_ph = BENCHMARK.get(location, BENCHMARK["Coimbatore"])["pH"]
                fig_ph.add_hline(y=dist_ph, line_dash="solid", line_color="#81C784", line_width=2,
                                 annotation_text=f"{location} Avg ({dist_ph})", annotation_font_size=11)
                fig_ph.add_hline(y=5.5, line_dash="dash",  line_color="#EF5350", line_width=1,
                                 annotation_text="Critical (5.5)", annotation_font_size=11)
                fig_ph.add_hline(y=6.0, line_dash="dot",   line_color="#FFA726", line_width=1,
                                 annotation_text="Warning (6.0)", annotation_font_size=11)
                fig_ph.update_traces(line_color=PRIMARY, marker_color=PRIMARY)
                fig_ph.update_layout(**PLOT_LAYOUT, height=280)
                st.plotly_chart(fig_ph, use_container_width=True, config={"displayModeBar": False})

            with c2:
                fig_npk = px.line(df_hist, x="date", y=["N", "P", "K"], markers=True, hover_data=["season"],
                                  title=f"NPK trend over time (vs {location})")
                dist_ref = BENCHMARK.get(location, BENCHMARK["Coimbatore"])
                
                # Add district averages as reference lines
                fig_npk.add_hline(y=dist_ref["N"], line_dash="dot", line_color=PRIMARY, line_width=1, annotation_text=f"{location} N", annotation_font_size=10)
                fig_npk.add_hline(y=dist_ref["P"], line_dash="dot", line_color=SECONDARY, line_width=1, annotation_text=f"{location} P", annotation_font_size=10)
                fig_npk.add_hline(y=dist_ref["K"], line_dash="dot", line_color=ACCENT, line_width=1, annotation_text=f"{location} K", annotation_font_size=10)
                
                fig_npk.update_traces(selector=dict(name="N"), line_color=PRIMARY)
                fig_npk.update_traces(selector=dict(name="P"), line_color=SECONDARY)
                fig_npk.update_traces(selector=dict(name="K"), line_color=ACCENT)
                fig_npk.update_layout(**PLOT_LAYOUT, height=280)
                st.plotly_chart(fig_npk, use_container_width=True, config={"displayModeBar": False})

            # History table
            st.markdown("### Reading history")
            display_cols = ["date", "season", "ph", "N", "P", "K", "oc", "crop", "confidence"]
            cols_available = [c for c in display_cols if c in df_hist.columns]
            st.dataframe(
                df_hist[cols_available].rename(columns={"confidence": "model conf (%)"}),
                use_container_width=True,
                hide_index=True,
            )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — VOICE ADVISORY
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Voice advisory")
    st.markdown('<div class="alert-info">Upload a voice recording of your question (WAV or MP3). The system will transcribe, process with current soil parameters, and speak the response back in your chosen language.</div>', unsafe_allow_html=True)

    col_v1, col_v2 = st.columns([1, 1], gap="large")

    with col_v1:
        st.markdown("**Upload voice note**")
        audio_file = st.file_uploader("Voice note (.wav or .mp3)", type=["wav", "mp3"], label_visibility="collapsed")

        if audio_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio_file.read())
                tmp_path = f.name
            try:
                from voice.transcriber import transcribe_audio
                with st.spinner("Transcribing…"):
                    transcribed = transcribe_audio(tmp_path, language=lang_code)
                st.markdown(f'<div class="advisory-card"><strong>Transcribed:</strong><br>{transcribed}</div>', unsafe_allow_html=True)
                os.unlink(tmp_path)

                if st.button("Process this query →"):
                    st.info("Use the transcribed text in the Soil Analysis tab as your query.")
            except Exception as e:
                st.error(f"Transcription error: {e}. Ensure openai-whisper is installed.")

    with col_v2:
        st.markdown("**Supported languages**")
        st.markdown("""
        <div class="fert-card">
          <div style="margin-bottom:8px;font-size:13px;color:#212121;font-weight:600">Speech-to-text</div>
          <div style="font-size:13px;color:#607D8B">OpenAI Whisper — Tamil (ta), English (en)</div>
          <div style="margin-top:14px;margin-bottom:8px;font-size:13px;color:#212121;font-weight:600">Text-to-speech</div>
          <div style="font-size:13px;color:#607D8B">Google TTS — Tamil (ta), English (en)</div>
          <div style="margin-top:14px;font-size:11px;color:#9E9E9E">Select language in the sidebar before recording.</div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — REGIONAL BENCHMARK
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### Tamil Nadu regional soil benchmark")
    st.markdown('<p style="font-size:12px;color:#9E9E9E;font-weight:500">Source: India Soil Health Card Mission — Tamil Nadu district aggregates (soilhealth.dac.gov.in)</p>', unsafe_allow_html=True)

    dist_ref = BENCHMARK.get(location, BENCHMARK["Coimbatore"])
    
    df_compare = pd.DataFrame([
        {"Entity": "My Farm", "pH": ph, "N": N, "P": P, "K": K, "OC": oc},
        {"Entity": f"{location} Avg", "pH": dist_ref["pH"], "N": dist_ref["N"], "P": dist_ref["P"], "K": dist_ref["K"], "OC": dist_ref["OC"]}
    ])

    b1, b2 = st.columns(2, gap="large")

    with b1:
        fig_ph_b = px.bar(df_compare, x="Entity", y="pH",
                          title=f"Soil pH: My Farm vs {location}", color="Entity",
                          color_discrete_map={"My Farm": PRIMARY, f"{location} Avg": "#B0BEC5"})
        fig_ph_b.add_hline(y=5.5, line_dash="dash", line_color="#EF5350", line_width=1, annotation_text="Critical (5.5)")
        fig_ph_b.update_layout(**PLOT_LAYOUT, height=300, showlegend=False)
        st.plotly_chart(fig_ph_b, use_container_width=True, config={"displayModeBar": False})

    with b2:
        df_npk_melt = df_compare.melt(id_vars="Entity", value_vars=["N", "P", "K"], var_name="Nutrient", value_name="Value")
        
        fig_npk_b = px.bar(df_npk_melt, x="Nutrient", y="Value", color="Entity",
                           title=f"NPK levels: My Farm vs {location}", barmode="group",
                           color_discrete_map={"My Farm": PRIMARY, f"{location} Avg": "#B0BEC5"})
        fig_npk_b.update_layout(**PLOT_LAYOUT, height=300)
        st.plotly_chart(fig_npk_b, use_container_width=True, config={"displayModeBar": False})

    st.markdown("### Your farm vs district average")
    dist_ref = BENCHMARK.get(location, BENCHMARK["Coimbatore"])

    comp_metrics = [
        ("Nitrogen (N)",     N,    dist_ref["N"],  "kg/ha"),
        ("Phosphorus (P)",   P,    dist_ref["P"],  "kg/ha"),
        ("Potassium (K)",    K,    dist_ref["K"],  "kg/ha"),
        ("pH",               ph,   dist_ref["pH"], ""),
        ("Organic Carbon",   oc,   dist_ref["OC"], "%"),
    ]

    cols = st.columns(len(comp_metrics))
    for col, (name, user_val, dist_val, unit) in zip(cols, comp_metrics):
        diff    = user_val - dist_val
        diff_pct= round((diff / dist_val) * 100) if dist_val else 0
        arrow   = "↑" if diff > 0 else ("↓" if diff < 0 else "—")
        color   = "#2E7D32" if diff >= 0 else "#C62828"
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">{name}</div>
              <div class="metric-value">{user_val}<span class="metric-unit">{unit}</span></div>
              <div style="font-size:11px;margin-top:6px;color:{color};font-weight:500">{arrow} {abs(diff_pct)}% vs district avg ({dist_val}{unit})</div>
            </div>""", unsafe_allow_html=True)

    # Full benchmark table
    st.markdown("### Full district data")
    df_bench = pd.DataFrame(BENCHMARK).T.reset_index()
    df_bench.columns = ["District", "pH", "N", "P", "K", "OC"]
    st.dataframe(df_bench, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — AI CHAT ASSISTANT
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("### 🤖 Agriculture AI Chatbot")
    st.caption("Ask anything about crops, farming data, or guidelines (e.g., 'Which crop needs the highest rainfall?')")

    if "chat_msgs" not in st.session_state:
        st.session_state["chat_msgs"] = []

    # Display chat history
    for msg in st.session_state["chat_msgs"]:
        with st.chat_message(msg["role"]):
            if "dataframe" in msg:
                st.markdown(msg["content"], unsafe_allow_html=True)
                st.dataframe(msg["dataframe"], use_container_width=True, hide_index=True)
            else:
                st.markdown(msg["content"], unsafe_allow_html=True)

    if prompt := st.chat_input("Ask your agriculture question here..."):
        # Display user prompt
        st.session_state["chat_msgs"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if orchestrator is None:
                err_msg = "Models not loaded. Please train models first."
                st.warning(err_msg)
                st.session_state["chat_msgs"].append({"role": "assistant", "content": err_msg})
            else:
                with st.spinner("AI is thinking..."):
                    # Use empty soil params since it's a general question or data query
                    result = orchestrator.run(
                        soil_params={}, 
                        location=location,
                        farmer_query=prompt, 
                        language=lang_code
                    )

                advice = result.get("final_advice", "")
                
                # Format response nicely
                if result["intent"] == "sql":
                    st.markdown(advice)
                    df_res = result.get("sql_result")
                    if df_res is not None and not df_res.empty:
                        st.dataframe(df_res, use_container_width=True, hide_index=True)
                        st.session_state["chat_msgs"].append({
                            "role": "assistant", 
                            "content": advice,
                            "dataframe": df_res
                        })
                    else:
                        st.session_state["chat_msgs"].append({"role": "assistant", "content": advice})
                        
                elif result["intent"] == "rag":
                    st.markdown(advice)
                    sources = result.get("rag_sources", "")
                    if sources:
                        with st.expander("View Reference Sources"):
                            st.text(sources)
                    st.session_state["chat_msgs"].append({"role": "assistant", "content": advice})
                    
                else:
                    # If it somehow routed to crop prediction without soil params
                    st.markdown(advice)
                    st.session_state["chat_msgs"].append({"role": "assistant", "content": advice})
