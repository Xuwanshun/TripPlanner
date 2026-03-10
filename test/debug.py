import os
import requests
from dotenv import load_dotenv

load_dotenv()
import os
print(f"[{os.getenv('SERPER_API_KEY')}]")

url = "https://google.serper.dev/search"
headers = {
    "X-API-KEY": os.getenv("SERPER_API_KEY"),
    "Content-Type": "application/json"
}
payload = {"q": "Toronto weather"}

response = requests.post(url, headers=headers, json=payload)

print(response.status_code)
print(response.text)



# from crewai import Agent
# from crewai_tools import SerperDevTool, WebsiteSearchTool


# class TripAgents():

#     def city_selection_agent(self):
#         search_tool = SerperDevTool()
#         scrape_tool = WebsiteSearchTool()

#         return Agent(
#             role='City Selection Expert',
#             goal='Select the best city based on weather, season, and prices',
#             backstory='An expert in analyzing travel data to pick ideal destinations',
#             tools=[
#                 search_tool,
#                 scrape_tool
#             ],
#             verbose=True
#         )

#     def local_expert(self):
#         search_tool = SerperDevTool()
#         scrape_tool = WebsiteSearchTool()

#         return Agent(
#             role='Local Expert at this city',
#             goal='Provide the BEST insights about the selected city',
#             backstory="""A knowledgeable local guide with extensive information
#             about the city, its attractions and customs""",
#             tools=[
#                 search_tool,
#                 scrape_tool
#             ],
#             verbose=True
#         )

#     def travel_concierge(self):
#         search_tool = SerperDevTool()
#         scrape_tool = WebsiteSearchTool()

#         return Agent(
#             role='Amazing Travel Concierge',
#             goal="""Create the most amazing travel itineraries with budget and 
#             packing suggestions for the city""",
#             backstory="""Specialist in travel planning and logistics with 
#             decades of experience""",
#             tools=[
#                 search_tool,
#                 scrape_tool
#             ],
#             verbose=True
#         )