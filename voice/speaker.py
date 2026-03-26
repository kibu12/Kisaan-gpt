"""voice/speaker.py"""
import tempfile, os
from gtts import gTTS

def speak(text: str, language: str = "ta") -> str:
    tts = gTTS(text=text, lang=language, slow=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        return f.name
