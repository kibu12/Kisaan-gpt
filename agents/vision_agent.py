"""agents/vision_agent.py — Uses Groq LLaMA 3.2 Vision for Pathology"""
import os
import base64
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class VisionAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def analyze_disease(self, image_bytes: bytes, user_prompt: str, language: str) -> str:
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        lang_instr = (
            "Respond entirely in Tamil (தமிழ்). Use simple agricultural Tamil." 
            if language == "ta" else "Respond in clear English."
        )
        
        system_prompt = f"""You are KISAAN-GPT's expert plant pathologist and agronomist.
{lang_instr}
Analyze the uploaded image of a plant/leaf.
1. Identify the crop if possible.
2. Identify any visible diseases, pests, or nutrient deficiencies.
3. Provide a brief explanation of the symptoms.
4. Recommend actionable, concrete organic and chemical treatment methods.
If the image is not a plant, politely inform the user.
Keep your answer clear, encouraging, and highly practical."""

        prompt = user_prompt if user_prompt and len(user_prompt) > 2 else "What disease does this plant have, and how do I treat it?"

        try:
            response = self.client.chat.completions.create(
                model="llama-3.2-11b-vision-instruct", # Updated to post-beta production model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=600,
                temperature=0.4
            )
            return response.choices[0].message.content
        except Exception as e:
            err_str = str(e)
            if "does not exist or you do not have access" in err_str or "403" in err_str or "404" in err_str:
                return "⚠️ **Groq API Tier Restriction:** Your current Groq API key does not have access to Vision models. Groq recently restricted image analysis specifically to funded/higher API tiers. To use the Plant Disease Detector, please ensure your Groq account has Vision access enabled, or just describe your plant's symptoms in text instead!"
            return f"Error analyzing image: {err_str}"
