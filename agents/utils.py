import os
from dotenv import load_dotenv

# Load .env for local development
load_dotenv()

def get_api_key(name: str) -> str:
    """
    Retrieves an API key from environment variables or Streamlit Secrets.
    Priority: os.getenv -> st.secrets -> empty string
    """
    # 1. Check environment variables (standard for local .env)
    val = os.getenv(name)
    if val:
        return val
    
    # 2. Check Streamlit Secrets (standard for Streamlit Cloud)
    try:
        # Lazy import to avoid hanging in non-streamlit environments
        import streamlit as st
        # Streamlit secrets can be accessed via st.secrets dict
        if hasattr(st, "secrets") and name in st.secrets:
            return st.secrets[name]
    except Exception:
        # st.secrets might not be initialized if not running in Streamlit
        pass
        
    return ""
