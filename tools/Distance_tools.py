import os
import json
import requests
from typing import Type, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class GoogleDistanceMatrixInput(BaseModel):
    origins: List[str] = Field(..., description="List of origins (address or place_id:XXXX)")
    destinations: List[str] = Field(..., description="List of destinations")
    mode: str = Field("driving", description="driving | transit | walking | bicycling")
    departure_time: int = Field(None, description="Optional unix timestamp for departure (required for transit with traffic)")


class GoogleDistanceMatrixTool(BaseTool):
    name: str = "Google Distance Matrix Tool"
    description: str = "Compute travel time matrix using Google Distance Matrix API."
    args_schema: Type[BaseModel] = GoogleDistanceMatrixInput

    def _run(self, origins: list, destinations: list, mode: str = "driving", departure_time: int = None) -> str:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not api_key:
            return "Missing GOOGLE_MAPS_API_KEY"

        url = "https://maps.googleapis.com/maps/api/distancematrix/json"

        params = {
            "origins": "|".join(origins),
            "destinations": "|".join(destinations),
            "mode": mode,
            "key": api_key,
        }

        # Only add departure_time if provided (required for transit, optional for driving with traffic)
        if departure_time:
            params["departure_time"] = departure_time

        response = requests.get(url, params=params, timeout=30)
        if response.status_code != 200:
            return f"HTTP Error: {response.status_code}"

        data = response.json()
        if data.get("status") != "OK":
            error_msg = data.get("error_message", "Unknown error")
            return json.dumps({
                "error": f"API Error: {data.get('status')}",
                "message": error_msg,
                "origins": origins,
                "destinations": destinations,
                "mode": mode
            }, indent=2)

        matrix = []

        for row in data["rows"]:
            row_data = []
            for element in row["elements"]:
                row_data.append({
                    "status": element.get("status"),
                    "duration_sec": element.get("duration", {}).get("value"),
                    "duration_in_traffic_sec": element.get("duration_in_traffic", {}).get("value"),
                    "distance_m": element.get("distance", {}).get("value"),
                })
            matrix.append(row_data)

        return json.dumps({
            "mode": mode,
            "matrix": matrix
        }, indent=2)