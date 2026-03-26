import os
from dotenv import load_dotenv
load_dotenv()

from agents.orchestrator import detect_intent, OrchestratorAgent

query = "Which crop needs the highest rainfall?"
print("TESTING DETECT_INTENT...")
intent = detect_intent(query)
print(f"Intent detected: {intent}")

print("\\nTESTING FULL ORCHESTRATOR RUN...")
orch = OrchestratorAgent()
try:
    result = orch.run(soil_params={}, location="Coimbatore", farmer_query=query, language="en")
    print("Orchestrator Run Result Keys:", result.keys())
    print("Final Advice:", result.get("final_advice", ""))
    print("SQL Query:", result.get("sql_query", ""))
    print("SUCCESS.")
except Exception as e:
    import traceback
    traceback.print_exc()
