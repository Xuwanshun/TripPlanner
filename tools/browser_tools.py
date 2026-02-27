from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import json
import os
import requests
from unstructured.partition.html import partition_html
from crewai import Agent, Task


class ScrapeWebsiteInput(BaseModel):
    website: str = Field(..., description="Website URL to scrape")


class ScrapeWebsiteTool(BaseTool):
    name: str = "Scrape website content"
    description: str = "Scrape and summarize website content"
    args_schema: Type[BaseModel] = ScrapeWebsiteInput

    def _run(self, website: str) -> str:
        url = f"https://chrome.browserless.io/content?token={os.environ['BROWSERLESS_API_KEY']}"
        payload = json.dumps({"url": website})
        headers = {
            'cache-control': 'no-cache',
            'content-type': 'application/json'
        }

        response = requests.post(url, headers=headers, data=payload)
        # extract clean text from the HTML response
        elements = partition_html(text=response.text)
        # conbine all text into one big block
        content = "\n\n".join([str(el) for el in elements])
        # split the content into smaller chunks for processing due to token limits
        chunks = [content[i:i + 8000] for i in range(0, len(content), 8000)]

        summaries = []

        for chunk in chunks:
            agent = Agent(
                role='Principal Researcher',
                goal='Do amazing research and summaries',
                backstory="Expert researcher",
                allow_delegation=False
            )

            task = Task(
                agent=agent,
                description=f"""
                Analyze and summarize the content below.
                Return only the summary.

                CONTENT:
                {chunk}
                """
            )

            summaries.append(task.execute())

        return "\n\n".join(summaries)