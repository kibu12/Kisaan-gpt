import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from agents.orchestrator import OrchestratorAgent
    print("Attempting to initialize OrchestratorAgent...")
    oa = OrchestratorAgent()
    print("OrchestratorAgent initialized successfully!")
except Exception as e:
    print(f"FAILED to initialize OrchestratorAgent: {e}")
    import traceback
    traceback.print_exc()
