import json
import os
import requests
from typing import Type, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class LandscapeImageSearchInput(BaseModel):
    location_name: str = Field(
        ..., description="Exact name of the landscape location"
    )
    num_images: int = Field(
        default=3, description="Number of images to return"
    )


class LandscapeImageSearchTool(BaseTool):
    name: str = "Landscape Image Search Tool"
    description: str = (
        "Searches Google Images via Serper API and returns real, "
        "high-quality landscape image URLs for a given location."
    )
    args_schema: Type[BaseModel] = LandscapeImageSearchInput

    def _run(self, location_name: str, num_images: int = 3) -> str:
        try:
            url = "https://google.serper.dev/images"

            payload = json.dumps({
                "q": f"{location_name} landscape scenic view high quality",
                "gl": "us",
                "hl": "en"
            })

            headers = {
                "X-API-KEY": os.environ.get("SERPER_API_KEY"),
                "content-type": "application/json",
            }

            response = requests.post(url, headers=headers, data=payload)

            if response.status_code != 200:
                return json.dumps({
                    "error": "Image search request failed",
                    "status_code": response.status_code
                })

            data = response.json()

            if "images" not in data:
                return json.dumps({
                    "error": "No images found in response"
                })

            images = data["images"][:num_images]

            results = []

            for img in images:
                # Avoid thumbnails
                image_url = img.get("imageUrl")
                source = img.get("source")
                title = img.get("title")

                if not image_url:
                    continue

                results.append({
                    "title": title,
                    "image_url": image_url,
                    "source": source
                })

            return json.dumps(results, indent=2)

        except Exception as e:
            return json.dumps({
                "error": str(e)
            })