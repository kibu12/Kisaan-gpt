"""voice/transcriber.py"""
import whisper, os

_model = None

def get_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model

def transcribe_audio(audio_file_path: str, language: str = "ta") -> str:
    result = get_model().transcribe(audio_file_path, language=language)
    return result["text"]
