import os
from crewai import Crew
from textwrap import dedent
from trip_agents import TripAgents
from trip_tasks import TripTasks

from dotenv import load_dotenv
load_dotenv()
import os

class TripSuggestionCrew:
  def __init__(self, Destination, date_range, hobbies):
    self.Destination = Destination
    self.date_range = date_range
    self.hobbies = hobbies

  def run(self):
    agents = TripAgents()
    tasks = TripTasks()

    city_landscape_suggestion = agents.city_landscape_suggestion_agent()

    Suggestion = tasks.Suggestion_task(
      city_landscape_suggestion,
      self.Destination,
      self.date_range,
      self.hobbies,
    )

    crew = Crew(
      agents=[
        city_landscape_suggestion
      ],
      tasks=[Suggestion],
      verbose=True
    )

    result = crew.kickoff()
    return result

class TripPlannerCrew:
  def __init__(self, cities, landscapes, start_date, duration_days, transport_mode):
        self.cities = cities
        self.landscapes = landscapes
        self.start_date = start_date
        self.duration_days = duration_days
        self.transport_mode = transport_mode

  def run(self):
    agents = TripAgents()
    tasks = TripTasks()
    
    trip_input = {
    "cities": self.cities,
    "landscapes": self.landscapes,
    "start_date": self.start_date,
    "duration_days": self.duration_days,
    "transport_mode": self.transport_mode,
    }

    planner_agent = agents.landscape_planning_agent()

    planning_task = tasks.landscape_planning_task(planner_agent, trip_input)

    crew = Crew(
            agents=[planner_agent],
            tasks=[planning_task],
            verbose=True
        )

    result = crew.kickoff()
    return result
  
if __name__ == "__main__":
  # print("## Welcome to Trip Planner")
  # print('-------------------------------')
  # Destination = input(
  #   dedent("""
  #     What are the cities options you are interested in visiting?
  #   """))
  # date_range = input(
  #   dedent("""
  #     What is the date range you are interested in traveling?
  #   """))
  # hobbies = input(
  #   dedent("""
  #     What are some of your high level interests and hobbies?
  #   """))
  
  # trip_crew = TripSuggestionCrew(Destination, date_range, hobbies)
  # result = trip_crew.run()
  # print("\n\n########################")
  # print("## Here are Landscape Suggestions for your trip:")
  # print("########################\n")
  # print(result)
    print("## Welcome to Multi-City Landscape Trip Planner")
    print("----------------------------------------------")

    cities = input(dedent("""
        Enter city options (comma separated):
        Example: Toronto, Niagara Falls
    """))

    landscapes = input(dedent("""
        Enter landscape list (comma separated):
        Example: High Park, Niagara Falls, Toronto Islands
    """))

    start_date = input(dedent("""
        Enter trip start date (YYYY-MM-DD):
    """))

    duration_days = int(input(dedent("""
        Enter trip duration (number of days):
    """)))

    transport_mode = input(dedent("""
        Enter transport mode (driving/transit/walking):
    """))
    
    
    trip_crew = TripPlannerCrew(
        cities,
        landscapes,
        start_date,
        duration_days,
        transport_mode
    )

    result = trip_crew.run()

    print("\n\n########################")
    print("## Here is your optimized itinerary:")
    print("########################\n")
    print(result)