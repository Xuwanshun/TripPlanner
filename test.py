import json
import os
from typing import Type, Literal, Optional, Dict, Any, List

import requests
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from dotenv import load_dotenv

load_dotenv()


class RoutePlannerInput(BaseModel):
    origin: str
    destination: str
    travel_mode: Literal["driving", "walking", "bicycling", "transit"] = "driving"
    departure_time: Optional[str] = None  # use "now" if needed
    language: str = "en"
    region: Optional[str] = None
    alternatives: bool = False


class RoutePlannerTool(BaseTool):
    name: str = "Route planner (Google Maps)"
    description: str = "Get distance, duration and step-by-step directions."
    args_schema: Type[BaseModel] = RoutePlannerInput

    def _run(
        self,
        origin: str,
        destination: str,
        travel_mode: str = "driving",
        departure_time: Optional[str] = None,
        language: str = "en",
        region: Optional[str] = None,
        alternatives: bool = False,
    ) -> str:

        api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        if not api_key:
            return json.dumps({"error": "Missing GOOGLE_MAPS_API_KEY"})

        timeout_s = 15

        # -------------------------
        # Distance Matrix
        # -------------------------
        dm_params = {
            "origins": origin,
            "destinations": destination,
            "mode": travel_mode,
            "language": language,
            "key": api_key,
        }

        if region:
            dm_params["region"] = region

        if departure_time == "now" and travel_mode in ("driving", "transit"):
            dm_params["departure_time"] = "now"

        dm_resp = requests.get(
            "https://maps.googleapis.com/maps/api/distancematrix/json",
            params=dm_params,
            timeout=timeout_s,
        )
        dm_data = dm_resp.json()

        if dm_data.get("status") != "OK":
            return json.dumps({"error": "Distance Matrix error", "details": dm_data})

        element = dm_data["rows"][0]["elements"][0]
        if element.get("status") != "OK":
            return json.dumps(
                {"error": "No route found", "status": element.get("status")}
            )

        distance = element["distance"]["text"]
        duration = element["duration"]["text"]
        duration_traffic = element.get("duration_in_traffic", {}).get("text")

        # -------------------------
        # Directions
        # -------------------------
        dir_params = {
            "origin": origin,
            "destination": destination,
            "mode": travel_mode,
            "language": language,
            "alternatives": alternatives,
            "key": api_key,
        }

        if region:
            dir_params["region"] = region

        if departure_time == "now" and travel_mode in ("driving", "transit"):
            dir_params["departure_time"] = "now"

        dir_resp = requests.get(
            "https://maps.googleapis.com/maps/api/directions/json",
            params=dir_params,
            timeout=timeout_s,
        )
        dir_data = dir_resp.json()

        if dir_data.get("status") != "OK":
            return json.dumps({"error": "Directions API error", "details": dir_data})

        route = dir_data["routes"][0]
        leg = route["legs"][0]

        steps = []
        for s in leg.get("steps", []):
            steps.append({
                "instruction": s.get("html_instructions"),
                "distance": s["distance"]["text"],
                "duration": s["duration"]["text"],
                "mode": s.get("travel_mode"),
            })

        result = {
            "origin": leg["start_address"],
            "destination": leg["end_address"],
            "mode": travel_mode,
            "distance": distance,
            "duration": duration,
            "duration_in_traffic": duration_traffic,
            "route_summary": route.get("summary"),
            "steps": steps,
        }

        return json.dumps(result, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    tool = RoutePlannerTool()

    print(
        tool.run(
            origin="Shibuya Station, Tokyo",
            destination="Senso-ji, Tokyo",
            travel_mode="driving",
        )
    )