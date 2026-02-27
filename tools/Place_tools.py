import os
import json
import requests
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class GooglePlaceInput(BaseModel):
    query: str = Field(..., description="Place name, e.g. 'High Park, Toronto'")
    language: str = Field("en", description="Language code")
    region: str = Field("ca", description="Region bias, e.g. 'ca'")

class GooglePlaceTool(BaseTool):
    name: str = "Google Place Tool"
    description: str = "Find place using Google Places API and return place_id and coordinates."
    args_schema: Type[BaseModel] = GooglePlaceInput

    def _run(self, query: str, language: str = "en", region: str = "ca") -> str:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            return "Missing GOOGLE_MAPS_API_KEY"

        url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"

        params = {
            "input": query,
            "inputtype": "textquery",
            "fields": "place_id,name,formatted_address,geometry",
            "language": language,
            "region": region,
            "key": api_key,
        }

        response = requests.get(url, params=params, timeout=30)
        if response.status_code != 200:
            return f"HTTP Error: {response.status_code}"

        data = response.json()
        if data.get("status") != "OK":
            return f"API Error: {data.get('status')}"

        result = data["candidates"][0]

        output = {
            "name": result.get("name"),
            "formatted_address": result.get("formatted_address"),
            "place_id": result.get("place_id"),
            "lat": result["geometry"]["location"]["lat"],
            "lng": result["geometry"]["location"]["lng"],
        }

        return json.dumps(output, indent=2)