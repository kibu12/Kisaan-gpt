import sys
import os
sys.path.append(os.getcwd())

print("Testing VisionAgent imports...")
try:
    from agents.vision_agent import VisionAgent
    print("VisionAgent imported!")
    v = VisionAgent()
    print("VisionAgent initialized!")
    if hasattr(v, "client"):
        print("Success: Client initialized.")
except Exception as e:
    print(f"Error: {e}")
