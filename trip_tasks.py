from crewai import Task
from textwrap import dedent
from datetime import date

class TripTasks:

    def Suggestion_task(self, agent, destination, date, hobbies):
        return Task(
            description=dedent(f"""
                You are required to use the provided tools to complete this task.

                USER INPUT:
                - Destination: {destination}
                - Travel Date: {date}
                - Hobbies: {", ".join(hobbies)}

                MANDATORY WORKFLOW (DO NOT SKIP STEPS):

                STEP 1 — Seasonal Research
                - Use the Search the internet tool.
                - Search: "{destination} weather in {date}"
                - Extract seasonal and climate conditions.

                STEP 2 — Scenic Location Research
                - Use the Search the internet tool again.
                - Search: "Top scenic landscape locations in {destination}"
                - Identify at least 10 real landscape places.

                STEP 3 — Hobby Matching
                - For each location:
                    - Evaluate how it matches the hobbies.
                    - Consider seasonal suitability.

                STEP 4 — Image Retrieval (MANDATORY)
                - For EACH selected location:
                    - Call Landscape Image Search Tool.
                    - Use exact location name.
                    - Retrieve 1 real high-quality landscape image.
                    - ONLY use image URLs returned by the tool.
                    - DO NOT fabricate image URLs.

                STEP 5 — Ranking
                Rank the 5 locations based on:
                1. Hobby match score
                2. Seasonal suitability
                3. Scenic popularity

                OUTPUT RULES:
                - You MUST use tool outputs.
                - You MUST NOT rely only on prior knowledge.
                - You MUST NOT invent image URLs.
                - Return STRICTLY valid JSON.
                - No explanations outside JSON.

                RETURN FORMAT:

                [
                {{
                    "rank": 1,
                    "location_name": "",
                    "season_summary": "",
                    "description": "",
                    "hobby_match_reason": "",
                    "image": {{
                        "image_url": "",
                        "source": ""
                    }}
                }}
                ]
                """),
            agent=agent,
            expected_output="Strict JSON ranked list with real image URLs."
        )

    def landscape_planning_task(self, agent, trip_input):
        return Task(
            description=dedent(f"""
            Generate a formal, optimized multi-city landscape trip itinerary.

            INPUT:
            {trip_input}

            CORE RULES (ALWAYS APPLY):
            1) Validate every city and landscape using Google Place Tool.
            - Store and reference places by place_id whenever possible.
            2) Respect the trip time window each day:
            - day_start_time to day_end_time
            3) Use Google Distance Matrix Tool for routing times:
            - mode = transport_mode
            - include departure_time to reflect traffic/transit schedules
            4) Use Weather Forecast Tool for each landscape visit window:
            - compute suitability score per stop
            - if score < 50, try re-ordering within the same day/city
            5) Use default_visit_minutes per stop unless limited by time window.

            MULTI-CITY LOGIC:
            A) If input includes cities[i].landscapes:
            - Plan landscapes within their specified city base.
            B) If input includes a global landscapes list (assignment_policy='auto'):
            - Assign each landscape to the nearest/most relevant city
                (based on distance to city center from Google Place Tool coordinates).
            - Then plan within each city.

            SCHEDULING LOGIC:
            - For each city base, allocate days = nights (or derived from duration_days if provided).
            - Build a daily itinerary that starts/ends at the city base.
            - Optimize stop ordering per day to minimize travel time and reduce backtracking.
            - Balance workload across days (avoid packing all far stops into one day).

            OUTPUT (JSON ONLY, no explanation):
            {{
            "trip_summary": {{
                "start_date": "...",
                "transport_mode": "...",
                "day_start_time": "...",
                "day_end_time": "..."
            }},
            "city_plans": [
                {{
                "city": "...",
                "nights": 2,
                "days": [
                    {{
                    "date": "...",
                    "total_travel_time_minutes": ...,
                    "stops": [
                        {{
                        "order": 1,
                        "name": "...",
                        "place_id": "...",
                        "arrival_time": "...",
                        "departure_time": "...",
                        "travel_minutes_from_previous": ...,
                        "weather_score": ...,
                        "weather_notes": [...]
                        }}
                    ]
                    }}
                ]
                }}
            ]
            }}

            Optimization objective:
            - Minimize total travel time
            - Maximize weather suitability
            - Respect time window constraints
            - Keep plans practical and evenly distributed
            """),
            agent=agent,
            expected_output="Structured JSON itinerary for a multi-city trip"
        )

    def Hotel_Restarants_task(self, agent, location):
        return Task(
            description=dedent(f"""
                Generate hotel and restaurant recommendations.

                INPUT LOCATION:
                {location}

                STEPS:

                1. Use Nearby Hotel and Restaurant Finder tool
                   to retrieve nearby hotels and restaurants.

                2. Select top 5 hotels and top 5 restaurants.

                3. For each selected place:
                   - Use Search tool to gather review summaries.
                   - Scrape at least one major review website or official site.
                   - Extract strengths and weaknesses.

                4. Assign a score (0–100) using:
                   - Google rating
                   - Review sentiment
                   - Amenities
                   - Reputation consistency

                5. Provide structured output:

                OUTPUT FORMAT:

                {{
                  "location": "...",
                  "recommended_hotels": [
                    {{
                      "name": "...",
                      "score": 85,
                      "pros": [...],
                      "cons": [...],
                      "summary": "..."
                    }}
                  ],
                  "recommended_restaurants": [
                    {{
                      "name": "...",
                      "score": 90,
                      "pros": [...],
                      "cons": [...],
                      "summary": "..."
                    }}
                  ]
                }}

                Return JSON only.
                Do not include explanation.
            """),
            agent=agent,
            expected_output="Ranked hotel and restaurant recommendation JSON"
        )