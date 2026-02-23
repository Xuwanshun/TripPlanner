from crewai import Agent

from tools.browser_tools import ScrapeWebsiteTool
from tools.calculator_tools import CalculatorTool
from tools.search_tools import SearchInternetTool


class TripAgents():

    def city_selection_agent(self):
        search_tool = SearchInternetTool()
        scrape_tool = ScrapeWebsiteTool()

        return Agent(
            role='City Selection Expert',
            goal='Select the best city based on weather, season, and prices',
            backstory='An expert in analyzing travel data to pick ideal destinations',
            tools=[
                search_tool,
                scrape_tool
            ],
            verbose=True
        )

    def local_expert(self):
        search_tool = SearchInternetTool()
        scrape_tool = ScrapeWebsiteTool()

        return Agent(
            role='Local Expert at this city',
            goal='Provide the BEST insights about the selected city',
            backstory="""A knowledgeable local guide with extensive information
            about the city, its attractions and customs""",
            tools=[
                search_tool,
                scrape_tool
            ],
            verbose=True
        )

    def travel_concierge(self):
        search_tool = SearchInternetTool()
        scrape_tool = ScrapeWebsiteTool()
        calculator_tool = CalculatorTool()

        return Agent(
            role='Amazing Travel Concierge',
            goal="""Create the most amazing travel itineraries with budget and 
            packing suggestions for the city""",
            backstory="""Specialist in travel planning and logistics with 
            decades of experience""",
            tools=[
                search_tool,
                scrape_tool,
                calculator_tool
            ],
            verbose=True
        )