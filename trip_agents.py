from crewai import Agent
from textwrap import dedent

from tools.browser_tools import ScrapeWebsiteTool
from tools.calculator_tools import CalculatorTool
from tools.search_tools import SearchInternetTool
from tools.Image_tools import LandscapeImageSearchTool
from tools.Distance_tools import GoogleDistanceMatrixTool
from tools.Place_tools import GooglePlaceTool
from tools.weather_tools import WeatherForecastTool
from tools.hotel_restaurant_tools import NearbyHotelRestaurantTool

class TripAgents():

    def city_landscape_suggestion_agent(self):
        return Agent(
            role="City Landscape Suggestion Agent",
            goal="Suggest best city landscapes with real images",
            backstory="Expert travel planner using real-time internet data",
            tools=[
                SearchInternetTool(),
                ScrapeWebsiteTool(),
                LandscapeImageSearchTool()
            ],
            verbose=True
        )

    def landscape_planning_agent(self):
        return Agent(
            role="Multi-Destination Trip Optimization Planner",
            goal=(
                "Create an optimized multi-destination, multi-day trip itinerary "
                "with detailed timing, multi-modal transportation options, nearby restaurant "
                "recommendations, weather forecasts, and cost estimates for each day."
            ),
            backstory=dedent("""
                You are a senior travel logistics optimizer and cost analyst.
                You validate places using Google Place Tool (place_id + lat/lng),
                compute travel times using Google Distance Matrix (traffic-aware for driving),
                evaluate outdoor suitability using the Weather Forecast Tool,
                find nearby restaurants using the Nearby Hotel and Restaurant Finder,
                and calculate trip costs using the Calculator Tool.

                You can plan long trips that span multiple destinations by:
                - Treating each destination as a base for a number of nights (days to explore).
                - Clustering and ordering attractions within each destination.
                - Ensuring a realistic day schedule within day_start_time/day_end_time.
                - Recommending restaurants near attractions for lunch and dinner.
                - Providing detailed cost breakdowns including attractions, meals, and transportation.
                - Comparing travel times across driving, transit, and walking for each leg.
            """),
            tools=[
                GooglePlaceTool(),
                GoogleDistanceMatrixTool(),
                WeatherForecastTool(),
                NearbyHotelRestaurantTool(),
                CalculatorTool()
            ],
            verbose=True
        )

    def Hotel_Restaurant_agent(self):
        return Agent(
            role="Hospitality & Dining Research Analyst",
            goal=(
                "Find the best hotels and restaurants near a given location, "
                "evaluate them using web research, and provide ranked recommendations "
                "with scores and pros/cons."
            ),
            backstory=dedent("""
                You are a professional travel research analyst.
                You use:
                - Google Places API to discover nearby hotels and restaurants.
                - Internet search to gather reviews and reputation.
                - Website scraping to extract deeper insights.
                
                You score each place based on:
                - Rating
                - Review sentiment
                - Amenities
                - Location convenience
                - Online reputation
                
                You provide:
                - Score (0–100)
                - Pros
                - Cons
                - Summary
            """),
            tools=[
                NearbyHotelRestaurantTool(),
                SearchInternetTool(),
                ScrapeWebsiteTool()
            ],
            verbose=True
        )