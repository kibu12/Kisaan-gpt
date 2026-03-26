"""agents/synthesis_agent.py — uses Groq (free tier, Llama 3.3 70B)"""
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class SynthesisAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def synthesize(self, soil_analysis, crop_predictions, rag_context,
                   weather, fertilizer, farmer_query, language="en",
                   soil_type="", land_acres=1.0) -> str:

        lang_instr = (
            "Respond entirely in Tamil (தமிழ்). Use simple, everyday Tamil "
            "that a farmer with basic literacy would understand."
            if language == "ta"
            else "Respond in clear, simple English."
        )

        system_prompt = f"""You are KISAAN-GPT, a trusted and warm agricultural advisor for Tamil Nadu farmers.
{lang_instr}

STRICT RULES:
1. Never invent numbers. Only use figures from the data and RAG context provided.
2. Always cite ICAR or TNAU when recommending doses or thresholds.
3. If there are CRITICAL soil issues, mention them FIRST before any crop recommendation.
4. Mention the top recommended crop and its confidence score.
5. End every response with exactly ONE concrete action the farmer should take THIS WEEK.
6. Keep the total response under 280 words.
7. Tone: warm, practical, like a knowledgeable neighbour — not a formal report.
8. When soil type is provided, mention soil-type-specific best practices (drainage, nutrient management, etc.)."""

        soil_type_line = f"\nSOIL TYPE: {soil_type}" if soil_type else ""
        land_line = f"\nLAND SIZE: {land_acres} Acres" if land_acres else ""

        user_prompt = f"""FARMER QUERY: {farmer_query}
{soil_type_line}{land_line}
SOIL HEALTH ANALYSIS:
Overall: {soil_analysis['overall_health']}
Critical Issues: {soil_analysis['issues']}
Warnings: {soil_analysis['warnings']}

ML CROP PREDICTION — Top 3:
{crop_predictions['top_3']}
Confidence in {crop_predictions['top_crop']}: {crop_predictions['top_crop_confidence']}%

CURRENT WEATHER ({weather.get('source')}):
Temperature: {weather.get('temperature')}°C, Humidity: {weather.get('humidity')}%
Conditions: {weather.get('description')}

FERTILIZER PLAN (ICAR-adjusted for this soil):
{fertilizer['primary_fertilizer']}
N: {fertilizer['n_dose_kg_ha']} kg/ha | P: {fertilizer['p_dose_kg_ha']} kg/ha | K: {fertilizer['k_dose_kg_ha']} kg/ha
Note: {fertilizer['application_note']}

RETRIEVED GUIDELINES (ICAR/TNAU knowledge base):
{rag_context}

Provide a complete, grounded recommendation structured as:
1. Soil health summary (CRITICAL issues first if any)
2. Recommended crop with reason (soil match + confidence)
3. Fertilizer action plan (cite ICAR dose)
4. This week's single most important action"""

        resp = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        return resp.choices[0].message.content
