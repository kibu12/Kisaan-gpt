import os
from supabase import create_client, Client
from agents.utils import get_api_key

# load_dotenv() is now handled in agents.utils

_client: Client | None = None

def get_supabase() -> Client:
    global _client
    if _client is None:
        url = get_api_key("SUPABASE_URL")
        key = get_api_key("SUPABASE_KEY")
        _client = create_client(url, key)
    return _client
