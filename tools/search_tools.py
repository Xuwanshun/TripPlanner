import json
import os
import requests
from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class SearchInternetInput(BaseModel):
    query: str = Field(..., description="Search query to look up on the internet")


class SearchInternetTool(BaseTool):
    name: str = "Search the internet"
    description: str = (
        "Useful to search the internet about a given topic "
        "and return relevant results."
    )
    args_schema: Type[BaseModel] = SearchInternetInput

    def _run(self, query: str) -> str:
        top_result_to_return = 4
        url = "https://google.serper.dev/search"

        payload = json.dumps({"q": query})
        headers = {
            "X-API-KEY": os.environ.get("SERPER_API_KEY"),
            "content-type": "application/json",
        }

        response = requests.post(url, headers=headers, data=payload)

        if response.status_code != 200:
            return "Error: Failed to retrieve search results."

        data = response.json()

        if "organic" not in data:
            return "Sorry, I couldn't find anything. Check your SERPER_API_KEY."

        results = data["organic"]
        output = []

        for result in results[:top_result_to_return]:
            try:
                output.append(
                    "\n".join(
                        [
                            f"Title: {result['title']}",
                            f"Link: {result['link']}",
                            f"Snippet: {result['snippet']}",
                            "-----------------",
                        ]
                    )
                )
            except KeyError:
                continue

        return "\n\n".join(output)