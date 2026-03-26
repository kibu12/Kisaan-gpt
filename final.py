import os, json, urllib.request
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
req = urllib.request.Request("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {api_key}"})
try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        vmodels = [m['id'] for m in data.get('data', []) if 'vision' in m['id'].lower()]
        with open("vision_out.txt", "w") as f:
            if not vmodels:
                f.write("No vision models available.")
            else:
                f.write("\n".join(vmodels))
        with open("all_out.txt", "w") as f:
            f.write("\n".join([m['id'] for m in data.get('data', [])]))
except Exception as e:
    with open("vision_out.txt", "w") as f:
        f.write(str(e))
