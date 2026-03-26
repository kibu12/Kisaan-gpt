import os
import shutil

# First securely copy the python script from root into agents inside the merge logic so the root is untouched initially.
def move_files():
    files = ["orchestrator.py", "rag_retriever_agent.py", "text_to_sql_agent.py"]
    for f in files:
        if os.path.exists(f):
            # os.replace handles cross-device sometimes, better use shutil.copy then os.remove
            shutil.copy(f, os.path.join("agents", f))
            os.remove(f)

def build_app():
    if not os.path.exists("app.py") or not os.path.exists("app_new.py"):
        return
        
    with open("app.py", "r", encoding="utf-8") as f:
        app_old = f.read()

    with open("app_new.py", "r", encoding="utf-8") as f:
        app_new = f.read()

    auth_fns_start = app_old.find("@st.cache_resource(show_spinner=False)\ndef load_auth_fns():")
    auth_fns_end = app_old.find("orchestrator = load_orchestrator()")
    auth_fns_code = app_old[auth_fns_start:auth_fns_end].strip()

    loader_code = "register_farmer, authenticate_farmer, get_farm_profile = load_auth_fns()"

    auth_ui_start = app_old.find("# ── Authentication UI ─────────────────────────────────────────────────────────")
    auth_ui_end = app_old.find("# ── Plotly theme — clean, minimal, white ─────────────────────────────────────")
    auth_ui_code = app_old[auth_ui_start:auth_ui_end].strip()
    auth_ui_code = auth_ui_code.replace("KisaanGPT is your AI Agriculture Assistant providing intelligent soil analysis and recommendations", "Soil Intelligence Platform")
    auth_ui_code = auth_ui_code.replace("<h1>🌾 KisaanGPT</h1>", "<h1>🌾 KISAAN-GPT</h1>")

    lazy_imports_start = app_new.find("# ── Lazy imports ──────────────────────────────────────────────────────────────")
    lazy_imports_end = app_new.find("PLOT_LAYOUT = dict(")

    sidebar_start = app_new.find("# ── Sidebar ───────────────────────────────────────────────────────────────────")
    sidebar_end = app_new.find("# ── Page header ───────────────────────────────────────────────────────────────")

    sidebar_new_code = """
# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p style="font-family:\\'DM Serif Display\\',serif;font-size:1.3rem;color:#1e2a1a;margin-bottom:0">KISAAN-GPT</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:11px;color:#9a9690;text-transform:uppercase;letter-spacing:0.07em;margin-top:0">Soil Intelligence Platform</p>', unsafe_allow_html=True)
    st.divider()
    st.markdown("**Farm Profile**")
    st.info(f"👤 **{st.session_state.get('farmer_name', 'Unknown')}**\\n\\nID: {st.session_state.get('farm_id', '')}")
    
    farm_id      = st.session_state.get("farm_id", "")
    farmer_name  = st.session_state.get("farmer_name", "")
    location     = st.session_state.get("district", "Coimbatore")
    
    season       = st.selectbox("Season", ["Kharif 2025","Rabi 2025-26","Summer 2026"])
    language     = st.selectbox("Language / மொழி", ["English","Tamil"])
    lang_code    = "ta" if language == "Tamil" else "en"
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.divider()
    st.markdown('<p style="font-size:11px;color:#9a9690">Crop model: Naive Bayes (99.55%)<br>RAG: Supabase keyword search<br>LLM: Claude Sonnet</p>', unsafe_allow_html=True)
"""

    part1 = app_new[:lazy_imports_end] 
    part1 += f"\\n\\n{auth_fns_code}\\n"
    part1 += f"\\n{loader_code}\\n\\n"
    part2 = app_new[lazy_imports_end:sidebar_start] 
    part3 = f"\\n{auth_ui_code}\\n\\n" 
    part4 = sidebar_new_code 
    part5 = app_new[sidebar_end:] 
    
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(part1 + part2 + part3 + part4 + part5)

if __name__ == "__main__":
    move_files()
    build_app()
    if os.path.exists("app_new.py"):
        os.remove("app_new.py")
