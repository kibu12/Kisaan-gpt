import os, json
import urllib.request
from dotenv import load_dotenv

load_dotenv("E:\\projects\\kisaan_gpt_project\\kisaan_gpt\\.env")
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    with open("E:\\projects\\kisaan_gpt_project\\kisaan_gpt\\vision_models.txt", "w") as f:
        f.write("No API key found in .env!")
    exit(1)

req = urllib.request.Request("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {api_key}"})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        vmodels = [m['id'] for m in data.get('data', []) if 'vision' in m['id'].lower()]
        with open("E:\\projects\\kisaan_gpt_project\\kisaan_gpt\\vision_models.txt", "w") as f:
            f.write("Models: " + ", ".join(vmodels))
            f.write("\nAll Models: " + ", ".join([m['id'] for m in data.get('data', [])]))
except Exception as e:
    with open("E:\\projects\\kisaan_gpt_project\\kisaan_gpt\\vision_models.txt", "w") as f:
        f.write(f"Error: {str(e)}")
