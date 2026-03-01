"""TripPlanner - Multi-Destination Trip Planner

This application creates optimized multi-day trip itineraries with:
- Detailed daily schedules with attraction timings
- Multi-modal transportation options (driving, transit, walking)
- Weather forecasts for each stop
- Restaurant recommendations for lunch and dinner
- Cost estimates for attractions, meals, and transportation
"""

import os
from crewai import Crew
from textwrap import dedent
from trip_agents import TripAgents
from trip_tasks import TripTasks

from dotenv import load_dotenv
load_dotenv()


def parse_csv_list(input_str):
    """Parse comma-separated string into a list of trimmed items."""
    return [item.strip() for item in input_str.split(",") if item.strip()]


def safe_int_input(prompt, default=1):
    """Safely parse integer input with a default fallback."""
    try:
        return int(input(prompt))
    except ValueError:
        print(f"Invalid input. Using default: {default}")
        return default

class TripPlannerCrew:
    """Main trip planning crew that generates detailed multi-day itineraries."""
    
    def __init__(self, destinations, attractions, start_date, duration_days, day_start="09:00", day_end="20:00"):
        self.destinations = destinations
        self.attractions = attractions
        self.start_date = start_date
        self.duration_days = duration_days
        self.transport_modes = ["driving", "transit", "walking"]  # Always check all transport modes
        self.day_start = day_start
        self.day_end = day_end

    def run(self):
        agents = TripAgents()
        tasks = TripTasks()
        
        trip_input = {
            "destinations": self.destinations,
            "attractions": self.attractions,
            "start_date": self.start_date,
            "duration_days": self.duration_days,
            "transport_modes_available": self.transport_modes,
            "day_start_time": self.day_start,
            "day_end_time": self.day_end,
            "assignment_policy": "auto"  # Auto-assign attractions to nearest destinations
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
    print("=" * 60)
    print("## Welcome to Multi-Destination Trip Planner")
    print("=" * 60)
    print("\nThis planner will generate a detailed itinerary including:")
    print("  ✓ Daily attraction schedule with timing")
    print("  ✓ Multi-modal transportation options")
    print("  ✓ Restaurant recommendations")
    print("  ✓ Weather forecasts")
    print("  ✓ Cost estimates\n")
    print("-" * 60)

    destinations = parse_csv_list(input(dedent("""
        Enter destinations you want to visit (comma separated):
        > """)))

    attractions = parse_csv_list(input(dedent("""
        Enter any specific attractions you already know you want to visit (comma separated):
        (Leave blank to let AI suggest attractions based on your destinations)
        > """)))

    start_date = input(dedent("""
        Enter trip start date (YYYY-MM-DD):
        > """))

    duration_days = safe_int_input(dedent("""
        Enter trip duration (number of days):
        > """), default=3)

    day_start = input(dedent("""
        Daily start time (HH:MM, default 09:00):
        > """)) or "09:00"

    day_end = input(dedent("""
        Daily end time (HH:MM, default 20:00):
        > """)) or "20:00"

    print("\n" + "=" * 60)
    print("Generating your optimized itinerary...")
    print("=" * 60 + "\n")

    trip_crew = TripPlannerCrew(
        destinations=destinations,
        attractions=attractions,
        start_date=start_date,
        duration_days=duration_days,
        day_start=day_start,
        day_end=day_end
    )

    result = trip_crew.run()

    print("\n\n" + "=" * 60)
    print("## YOUR OPTIMIZED ITINERARY")
    print("=" * 60 + "\n")
    print(result)