"""agents/weather_agent.py"""
import os, requests

class WeatherAgent:
    def get_forecast(self, location: str) -> dict:
        api_key = os.environ.get("OPENWEATHER_API_KEY", "")
        if not api_key:
            return self._fallback()
        try:
            url  = f"http://api.openweathermap.org/data/2.5/weather?q={location},IN&appid={api_key}&units=metric"
            data = requests.get(url, timeout=5).json()
            return {
                "temperature": data["main"]["temp"],
                "humidity":    data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "rainfall_mm": data.get("rain", {}).get("1h", 0),
                "source":      "OpenWeatherMap",
            }
        except Exception:
            return self._fallback()

    def _fallback(self):
        return {
            "temperature": 28.0,
            "humidity":    65.0,
            "description": "Regional average (live data unavailable)",
            "rainfall_mm": 0,
            "source":      "fallback",
        }
