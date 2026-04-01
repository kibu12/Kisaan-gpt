import os
from dotenv import load_dotenv

# Load .env for local development
load_dotenv()

def get_api_key(name: str) -> str:
    """
    Retrieves an API key from environment variables or Streamlit Secrets.
    Priority: os.getenv -> .env file -> st.secrets -> empty string
    """
    # Ensure .env is loaded from the project root (one level up from this file)
    import pathlib
    env_path = pathlib.Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=env_path, override=True)

    # 1. Check environment variables (including those loaded from .env)
    val = os.getenv(name)
    if val:
        return val

    # 2. Attempt to read from Streamlit Secrets if available
    try:
        import streamlit as st
        if hasattr(st, "secrets") and name in st.secrets:
            return st.secrets[name]
    except Exception:
        # Not running in Streamlit or streamlit not installed
        pass

    return ""
