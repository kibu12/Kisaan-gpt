import os
from dotenv import load_dotenv

# Load .env for local development
load_dotenv()

def get_api_key(name: str) -> str:
    """
    Retrieves an API key from environment variables.
    Loads .env from the project root for local development.
    """
    import pathlib
    env_path = pathlib.Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=env_path, override=True)

    val = os.getenv(name)
    return val if val else ""

