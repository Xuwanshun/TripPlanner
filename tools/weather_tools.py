import os
import json
import requests
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class WeatherForecastInput(BaseModel):
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    start_time: int = Field(..., description="Visit start time (unix)")
    end_time: int = Field(..., description="Visit end time (unix)")
    units: str = Field("metric", description="metric | imperial")

class WeatherForecastTool(BaseTool):
    name: str = "Weather Forecast Tool"
    description: str = "Fetch hourly weather and compute suitability score."
    args_schema: Type[BaseModel] = WeatherForecastInput

    def _run(self, latitude: float, longitude: float, start_time: int, end_time: int, units: str = "metric") -> str:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            return "Missing OPENWEATHER_API_KEY"

        url = "https://api.openweathermap.org/data/3.0/onecall"

        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": api_key,
            "units": units,
            "exclude": "minutely,daily,alerts"
        }

        response = requests.get(url, params=params, timeout=30)
        if response.status_code != 200:
            return f"HTTP Error: {response.status_code}"

        data = response.json()
        hourly = data.get("hourly", [])

        selected_hours = [
            h for h in hourly if start_time <= h["dt"] <= end_time
        ]

        if not selected_hours:
            return "No hourly data available in time range."

        score = 100
        notes = []

        for h in selected_hours:
            rain = h.get("rain", {}).get("1h", 0)
            wind = h.get("wind_speed", 0)
            temp = h.get("temp")

            if rain > 5:
                score -= 25
                notes.append("Heavy rain")
            elif rain > 0:
                score -= 10
                notes.append("Light rain")

            if wind > 12:
                score -= 15
                notes.append("High wind")

            if units == "metric" and (temp > 35 or temp < -5):
                score -= 15
                notes.append("Extreme temperature")

        score = max(0, min(100, score))

        return json.dumps({
            "suitability_score": score,
            "notes": list(set(notes)),
            "hours_analyzed": len(selected_hours)
        }, indent=2)