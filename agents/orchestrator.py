"""
agents/orchestrator.py
Updated orchestrator with full intent routing:
User Query -> Intent Understanding -> Tool Selection -> Execution -> Final Response
"""
import os
from dotenv import load_dotenv
import groq

from agents.soil_analyst_agent    import SoilAnalystAgent
from agents.crop_predictor_agent  import CropPredictorAgent
from agents.rag_retriever_agent   import RAGRetrieverAgent
from agents.weather_agent         import WeatherAgent
from agents.fertilizer_agent      import FertilizerAgent
from agents.synthesis_agent       import SynthesisAgent
from agents.text_to_sql_agent     import TextToSQLAgent
from agents.vision_agent          import VisionAgent

load_dotenv()

def detect_intent(query: str) -> str:
    """
    Classify user intent into one of three tool categories:
    - 'sql'  : data/statistics questions about the dataset
    - 'rag'  : knowledge/guideline questions
    - 'crop' : user provides soil parameters and wants crop recommendation
    """
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""Classify this agriculture query into exactly one category.

Categories:
- sql   : asks for statistics, comparisons, averages, totals from crop data
           Examples: "which crop needs most water", "compare nitrogen levels",
                     "show highest yield crops", "fertilizer usage by crop"
- rag   : asks for knowledge, guidelines, best practices, general advice
           Examples: "how to improve soil health", "what season for tomato",
                     "sandy soil crops", "irrigation advice"
- crop  : user provides soil parameters and wants crop recommendation
           Examples: "I have pH 6.5 N 90 P 42", "recommend crop for my soil",
                     "what to plant with these values"

Query: "{query}"

Reply with ONLY one word: sql, rag, or crop"""

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=10,
        messages=[{"role": "user", "content": prompt}],
    )
    intent = resp.choices[0].message.content.strip().lower()
    
    # Clean up intent string in case model outputs extra characters
    if "sql" in intent:
        return "sql"
    elif "crop" in intent:
        return "crop"
    return "rag"


class OrchestratorAgent:
    def __init__(self):
        self.client           = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.soil_agent       = SoilAnalystAgent()
        self.crop_agent       = CropPredictorAgent()
        self.rag_agent        = RAGRetrieverAgent()
        self.weather_agent    = WeatherAgent()
        self.fertilizer_agent = FertilizerAgent()
        self.synthesis_agent  = SynthesisAgent()
        self.sql_agent        = TextToSQLAgent()
        self.vision_agent     = VisionAgent()

    def analyze_image(self, image_bytes: bytes, query: str, language: str = "en") -> dict:
        """Vision pipeline."""
        diagnosis = self.vision_agent.analyze_disease(image_bytes, query, language)
        return {
            "intent":           "vision",
            "soil_analysis":    {"issues": [], "warnings": [], "overall_health": "N/A"},
            "crop_predictions": {"top_crop": "N/A", "top_crop_confidence": 0, "top_3": []},
            "fertilizer":       {"n_dose_kg_ha": 0, "p_dose_kg_ha": 0, "k_dose_kg_ha": 0,
                                  "primary_fertilizer": "N/A", "application_note": "",
                                  "source": ""},
            "weather":          {"temperature": 0, "humidity": 0,
                                  "description": "", "source": ""},
            "final_advice":     diagnosis,
            "rag_sources":      "",
            "sql_query":        "",
            "sql_result":       None,
            "sql_error":        None,
        }

    def run(self, soil_params: dict, location: str,
            farmer_query: str, language: str = "en") -> dict:
        """
        Full pipeline:
        Query -> Intent -> Tool Selection -> Execution -> Response
        """
        # Step 1 — Detect intent
        intent = detect_intent(farmer_query)

        # Step 2 — Route to correct tool
        if intent == "sql":
            return self._run_sql(farmer_query, language)
        elif intent == "rag":
            return self._run_rag(farmer_query, language)
        else:
            return self._run_crop(soil_params, location, farmer_query, language)

    def _run_sql(self, query: str, language: str) -> dict:
        """Text-to-SQL pipeline."""
        result = self.sql_agent.query(query)
        return {
            "intent":           "sql",
            "soil_analysis":    {"issues": [], "warnings": [], "overall_health": "N/A"},
            "crop_predictions": {"top_crop": "N/A", "top_crop_confidence": 0, "top_3": []},
            "fertilizer":       {"n_dose_kg_ha": 0, "p_dose_kg_ha": 0, "k_dose_kg_ha": 0,
                                  "primary_fertilizer": "N/A", "application_note": "",
                                  "source": ""},
            "weather":          {"temperature": 0, "humidity": 0,
                                  "description": "", "source": ""},
            "final_advice":     result["explanation"],
            "rag_sources":      "",
            "sql_query":        result["sql"],
            "sql_result":       result["result"],
            "sql_error":        result["error"],
        }

    def _run_rag(self, query: str, language: str) -> dict:
        """RAG-only pipeline for knowledge questions."""
        rag_context = self.rag_agent.retrieve_by_query(query)
        advice      = self._synthesize_rag_only(query, rag_context, language)
        return {
            "intent":           "rag",
            "soil_analysis":    {"issues": [], "warnings": [], "overall_health": "N/A"},
            "crop_predictions": {"top_crop": "N/A", "top_crop_confidence": 0, "top_3": []},
            "fertilizer":       {"n_dose_kg_ha": 0, "p_dose_kg_ha": 0, "k_dose_kg_ha": 0,
                                  "primary_fertilizer": "N/A", "application_note": "",
                                  "source": ""},
            "weather":          {"temperature": 0, "humidity": 0,
                                  "description": "", "source": ""},
            "final_advice":     advice,
            "rag_sources":      rag_context,
            "sql_query":        "",
            "sql_result":       None,
            "sql_error":        None,
        }

    def _run_crop(self, soil_params: dict, location: str,
                  query: str, language: str, season: str = "") -> dict:
        """Full soil analysis + crop prediction pipeline."""
        soil_analysis    = self.soil_agent.analyze(soil_params)
        crop_predictions = self.crop_agent.predict(soil_params, location, season)
        rag_context      = self.rag_agent.retrieve(soil_params, crop_predictions["top_crop"])
        weather          = self.weather_agent.get_forecast(location)
        fertilizer       = self.fertilizer_agent.recommend(soil_params, crop_predictions["top_crop"])
        final_advice     = self.synthesis_agent.synthesize(
            soil_analysis, crop_predictions, rag_context,
            weather, fertilizer, query, language,
        )
        return {
            "intent":           "crop",
            "soil_analysis":    soil_analysis,
            "crop_predictions": crop_predictions,
            "fertilizer":       fertilizer,
            "weather":          weather,
            "final_advice":     final_advice,
            "rag_sources":      rag_context,
            "sql_query":        "",
            "sql_result":       None,
            "sql_error":        None,
        }

    def _synthesize_rag_only(self, query: str, context: str, language: str) -> str:
        lang = ("Respond in Tamil." if language == "ta" else "Respond in clear English.")
        prompt = f"""You are KISAAN-GPT, an expert agricultural advisor.
{lang}
Answer the user's question using the provided Context if it is relevant. 
If the Context does NOT contain the answer, use your advanced agricultural knowledge to answer the question directly. Do not say "there is no information" if you know the answer!
Be helpful, accurate, and keep the answer under 150 words.

Question: {query}

Context:
{context}"""
        resp = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()
