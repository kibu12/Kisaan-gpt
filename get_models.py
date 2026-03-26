import os
import requests
from dotenv import load_dotenv

load_dotenv("E:\\projects\\kisaan_gpt_project\\kisaan_gpt\\.env")
api_key = os.environ.get("GROQ_API_KEY")
headers = {"Authorization": f"Bearer {api_key}"}

try:
    response = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
    data = response.json()
    vision_models = [m['id'] for m in data.get('data', []) if 'vision' in m['id'].lower()]
    print("--- AVAILABLE VISION MODELS ---")
    for vm in vision_models:
        print(vm)
    print("-------------------------------")
    
    # Also print some standard text models just to ensure it worked
    print("\nSome other models:")
    for m in data.get('data', [])[:5]:
        print(m['id'])
except Exception as e:
    print(f"Error fetching models: {e}")
