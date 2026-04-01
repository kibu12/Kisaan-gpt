import sys
import os
# Add the current directory to sys.path to allow imports
sys.path.append(os.getcwd())

from agents.utils import get_api_key

print("Checking GROQ_API_KEY...")
key = get_api_key("GROQ_API_KEY")
if key:
    print(f"Success! Found key: {key[:10]}...")
else:
    print("Failure: Key not found.")
