import json
import os
import requests
from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class NearbyPlacesInput(BaseModel):
    address: str = Field(..., description="Full address or city name")
    radius: int = Field(2000, description="Search radius in meters (default 2000m)")
    max_results: int = Field(5, description="Maximum results per category")

class NearbyHotelRestaurantTool(BaseTool):
    name: str = "Nearby Hotel and Restaurant Finder"
    description: str = (
        "Find nearby hotels and restaurants using Google Places API "
        "based on a given address."
    )
    args_schema: Type[BaseModel] = NearbyPlacesInput

    def _run(self, address: str, radius: int = 2000, max_results: int = 5) -> str:
        api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

        if not api_key:
            return "Error: GOOGLE_MAPS_API_KEY not set."

        # ----------------------------
        # Step 1: Geocode Address
        # ----------------------------
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        geocode_params = {
            "address": address,
            "key": api_key
        }

        geo_response = requests.get(geocode_url, params=geocode_params)

        if geo_response.status_code != 200:
            return "Error: Failed to geocode address."

        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return "Error: Address not found."

        location = geo_data["results"][0]["geometry"]["location"]
        lat = location["lat"]
        lng = location["lng"]

        # ----------------------------
        # Step 2: Nearby Search
        # ----------------------------
        def search_places(place_type):
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": radius,
                "type": place_type,
                "key": api_key
            }

            response = requests.get(url, params=params)

            if response.status_code != 200:
                return []

            data = response.json()

            if data.get("status") != "OK":
                return []

            results = []
            for place in data.get("results", [])[:max_results]:
                results.append({
                    "name": place.get("name"),
                    "place_id": place.get("place_id"),
                    "rating": place.get("rating"),
                    "user_ratings_total": place.get("user_ratings_total"),
                    "price_level": place.get("price_level"),
                    "address": place.get("vicinity"),
                    "lat": place["geometry"]["location"]["lat"],
                    "lng": place["geometry"]["location"]["lng"],
                    "types": place.get("types")
                })
            return results

        hotels = search_places("lodging")
        restaurants = search_places("restaurant")

        output = {
            "input_address": address,
            "search_radius_meters": radius,
            "hotels": hotels,
            "restaurants": restaurants
        }

        return json.dumps(output, indent=2)