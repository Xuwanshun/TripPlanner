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
            Generate a formal, optimized multi-destination trip itinerary.

            INPUT:
            {trip_input}

            CORE RULES (ALWAYS APPLY):
            1) Validate every destination and attraction using Google Place Tool.
            - Store and reference places by place_id whenever possible.
            2) Respect the trip time window each day:
            - day_start_time to day_end_time
            3) Routing times should consider multiple transport options.
            - `trip_input` provides estimated travel durations per transport mode
              (for example: {{"driving": 30, "transit": 45, "walking": 20}}).
            - Use these provided durations as baseline estimates for planning.
            - When calling the Google Distance Matrix Tool:
              * Use place_id format when available: "place_id:ChIJxxxxxxxxx"
              * For each pair of locations, call the tool 3 times (once per mode: driving, transit, walking)
              * departure_time is OPTIONAL - only include it for transit or when you need traffic data
              * If you get "INVALID_REQUEST", try using formatted addresses instead of place_ids
              * Example valid origins/destinations: ["High Park, Toronto, ON"] or ["place_id:ChIJxxx"]
            4) Use Weather Forecast Tool for each attraction visit window:
            - compute suitability score per stop
            - if score < 50, try re-ordering within the same day/destination
            5) Use default_visit_minutes per stop unless limited by time window.

            MULTI-DESTINATION LOGIC:
            A) If attractions list is EMPTY or has fewer than 3 items:
            - Use Search the internet tool to find "top tourist attractions in [destination]"
            - Research and find 10-15 popular, highly-rated attractions per destination
            - Combine these with any user-provided attractions
            - Then INTELLIGENTLY SELECT which attractions to include based on:
              * Available hours per day = (day_end_time - day_start_time) - meal times (2-3 hours)
              * Estimated visit duration for each attraction type
              * Travel time between attractions (use Distance Matrix)
              * Fit as many as realistically possible without rushing (typically 3-5 per day)
              * Prioritize higher-rated and more popular attractions
            - DO NOT force all found attractions into the schedule - only include what fits comfortably
            B) If input includes destinations[i].attractions:
            - Plan attractions within their specified destination base.
            C) If input includes a global attractions list (assignment_policy='auto'):
            - Assign each attraction to the nearest/most relevant destination
                (based on distance to destination center from Google Place Tool coordinates).
            - Then plan within each destination.

            SCHEDULING LOGIC:
            - For each destination base, allocate days = nights (or derived from duration_days if provided).
            - Build a daily itinerary that starts/ends at the destination base.
            - ⚠️ CRITICAL - ADAPTIVE SCHEDULING WITH SPECIFIC TIMES:
              * Calculate total available hours per day: day_end_time - day_start_time (typically 11 hours: 09:00-20:00)
              * DINNER CAN EXTEND PAST day_end_time: If the last attraction ends near 20:00, dinner can be scheduled at 20:00-21:30
              * For EACH stop, you MUST specify:
                - arrival_time: "HH:MM" (when to arrive)
                - departure_time: "HH:MM" (when to leave)
                - visit_duration_minutes: exact minutes at this attraction
              * For EACH stop after the first, calculate travel_from_previous with all 3 modes
              * Example day timeline:
                Stop 1: arrival "09:00", departure "11:30" (150 min visit)
                Travel: 25 min by transit
                Stop 2: arrival "11:55", departure "13:00" (65 min visit)
                Lunch: 13:00-14:00 (60 min)
                Travel: 15 min walking
                Stop 3: arrival "14:15", departure "16:30" (135 min visit)
                Travel: 30 min driving
                Stop 4: arrival "17:00", departure "19:30" (150 min visit)
                Dinner: 19:45-21:00 (can extend past 20:00 end time)
              * Fit as many attractions as realistically possible within the time constraint:
                - If an attraction needs 6+ hours (theme parks, zoos, major museums) → Schedule 1 attraction that day
                - If attractions need 2-3 hours each → Schedule 2-3 attractions per day
                - If attractions need 30-90 min each → Schedule 4-5 attractions per day
              * DO NOT force multiple attractions if time doesn't allow
              * DO NOT schedule only 1 short attraction when time allows for more
              * Times must be sequential and logical (departure of stop N + travel = arrival of stop N+1)
            - ESTIMATE VISIT DURATION for each attraction based on its type:
              * Large museums/theme parks: 2-4 hours
              * Small museums/galleries: 1-2 hours
              * Landmarks/viewpoints: 30-60 minutes
              * Parks/gardens: 1-2 hours
              * Shopping districts: 1-3 hours
              * Historical sites: 1-2 hours
              Use your knowledge of the specific attraction to make realistic estimates.
            - Account for travel time between attractions using Distance Matrix results.
            - Account for meal times: 45-60 minutes for lunch, 60-90 minutes for dinner.
            - Optimize stop ordering per day to minimize travel time and reduce backtracking.
            - Balance workload across days (avoid packing all far stops into one day).
            - When beneficial, select different transport modes for different legs
              (e.g., walking for nearby attractions, driving/transit between destinations)
              using the provided transport durations and Distance Matrix guidance.

            RESTAURANT RECOMMENDATIONS:
            - For each day, use Nearby Hotel and Restaurant Finder tool to find restaurants
              near the lunch and dinner time locations.
            - When calling the tool, use the lat,lng coordinates from the Google Place Tool results
              (format: "latitude,longitude" e.g., "43.6532,-79.3832")
            - Recommend 1-2 restaurants per meal time (lunch/dinner) based on:
              * Proximity to attractions being visited around that time
              * Rating and reviews
              * Cuisine variety
              * Price range

            COST ESTIMATION:
            - Use Calculator Tool to compute costs:
              * Attraction entry fees (estimate based on typical costs)
              * Meals (breakfast ~$15, lunch ~$25, dinner ~$40 per person in CAD)
              * Transportation (driving: $0.20/km + parking ~$20/day, transit: ~$3.50/ride, walking: $0)
            - Provide per-day and total trip cost estimates.

            OUTPUT (JSON ONLY, no explanation):
            {{
            "trip_summary": {{
                "start_date": "...",
                "end_date": "...",
                "total_duration_days": ...,
                "transport_options_available": ["driving", "transit", "walking"],
                "day_start_time": "...",
                "day_end_time": "...",
                "estimated_total_cost": {{
                    "currency": "CAD",
                    "attractions": ...,
                    "meals": ...,
                    "transportation": ...,
                    "total": ...
                }}
            }},
            "destination_plans": [
                {{
                "destination": "...",
                "nights": 2,
                "days": [
                    {{
                    "date": "...",
                    "day_number": 1,
                    "total_travel_time_minutes": ...,
                    "stops": [
                        {{
                        "order": 1,
                        "name": "...",
                        "place_id": "...",
                        "arrival_time": "HH:MM",
                        "departure_time": "HH:MM",
                        "visit_duration_minutes": ...,
                        "estimated_cost": ...,
                        "travel_from_previous": {{
                            "driving": {{"minutes": ..., "distance_km": ...}},
                            "transit": {{"minutes": ..., "distance_km": ...}},
                            "walking": {{"minutes": ..., "distance_km": ...}},
                            "recommended_mode": "..."
                        }},
                        "weather": {{
                            "score": ...,
                            "temperature_c": ...,
                            "conditions": "...",
                            "notes": [...]
                        }}
                        }}
                    ],
                    "recommended_restaurants": [
                        {{
                        "meal_time": "lunch|dinner",
                        "name": "...",
                        "place_id": "...",
                        "cuisine_type": "...",
                        "rating": ...,
                        "price_level": ...,
                        "estimated_cost_per_person": ...,
                        "distance_from_last_stop_minutes": ...
                        }}
                    ],
                    "daily_cost_estimate": {{
                        "attractions": ...,
                        "meals": ...,
                        "transportation": ...,
                        "total": ...
                    }}
                    }}
                ]
                }}
            ]
            }}

            Optimization objective:
            - Minimize total travel time across chosen transport modes
            - Maximize weather suitability
            - Respect time window constraints
            - Keep plans practical and evenly distributed
            """),
            agent=agent,
            expected_output="Structured JSON itinerary for a multi-destination trip"
        )

    def Hotel_Restaurants_task(self, agent, location):
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