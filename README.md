# 🌍 AI Trip Planner - Multi-Agent Travel Orchestration

## 🎯 Overview
An intelligent trip planning system powered by **CrewAI** that generates comprehensive, multi-day itineraries with precise timing, estimated transportation time, restaurant recommendations, weather forecasts, and cost estimates. This project demonstrates advanced AI agent collaboration to solve complex scheduling and optimization problems.

### ✨ Key Capabilities
- 🗺️ **Multi-Destination Planning** - Seamlessly plan trips across multiple cities with optimized routing
- 🚗🚇🚶 **Trasnportation Time Estimate** - Compare driving, transit, and walking options with real-time duration estimates
- ⏰ **Precise Timeline Generation** - Specific arrival/departure times for every attraction and activity
- 🍽️ **Contextual Restaurant Recommendations** - Curated dining options near each attraction
- ☀️ **Weather-Aware Scheduling** - Dynamic suitability scoring and rescheduling for outdoor activities
- 💰 **Comprehensive Cost Estimation** - Detailed breakdown of attractions, meals, and transportation costs
- 🧠 **Adaptive Scheduling Algorithm** - Intelligently fits 1-5 attractions per day based on visit duration and constraints

## 🏗️ Architecture

### Multi-Agent System Design
```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INPUT                               │
│  Destinations | Attractions | Dates | Duration | Time Preferences│
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CREWAI ORCHESTRATOR                          │
│              (Coordinates Agent Collaboration)                   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
┌──────────────────┐       ┌──────────────────┐
│  PLANNING AGENT  │       │ RESTAURANT AGENT │
│                  │       │                  │
│ • Route Planning │       │ • Dining Options │
│ • Time Scheduling│       │ • Cuisine Match  │
│ • Weather Check  │       │ • Proximity Sort │
│ • Cost Calc      │       │ • Rating Filter  │
└────────┬─────────┘       └────────┬─────────┘
         │                          │
         │    ┌─────────────────────┴───────────────┐
         │    │         SHARED TOOL LAYER           │
         └────┤                                     │
              │  🗺️  Google Places API              │
              │  📍  Distance Matrix API            │
              │  🌤️  Weather Forecast API          │
              │  🔍  Web Search & Scraping          │
              │  🧮  Cost Calculator                │
              └─────────────────┬───────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   INTELLIGENT CORE    │
                    │                       │
                    │ • LLM Decision Engine │
                    │ • Context Management  │
                    │ • Task Coordination   │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  STRUCTURED OUTPUT    │
                    │                       │
                    │  JSON Itinerary with: │
                    │  • Daily schedules    │
                    │  • Transport options  │
                    │  • Cost breakdowns    │
                    │  • Weather forecasts  │
                    └───────────────────────┘
```

### Agent Roles & Responsibilities

#### 🎯 Landscape Planning Agent
**Role:** Master Trip Planner  
**Capabilities:**
- Validates destinations using Google Places API
- Discovers top attractions when user input is minimal
- Calculates optimal visit sequences to minimize backtracking
- Estimates realistic visit durations by attraction type
- Generates minute-by-minute timelines with arrival/departure times
- Compares all transport modes (driving, transit, walking) for each leg
- Integrates weather forecasts and reschedules outdoor activities if needed
- Computes total trip costs including attractions, meals, and transport

**Tools:**
- `GooglePlaceTool` - Attraction validation & coordinate lookup
- `GoogleDistanceMatrixTool` - Multi-modal travel time calculations
- `WeatherForecastTool` - 7-day forecasts with suitability scoring
- `SearchInternetTool` - Discovery of top-rated attractions
- `CalculatorTool` - Cost computations and budget estimates

#### 🍽️ Restaurant Agent
**Role:** Dining Curator  
**Capabilities:**
- Finds restaurants near attraction coordinates
- Filters by cuisine variety, ratings, and price levels
- Recommends meal options aligned with activity schedules
- Provides cost estimates per meal type

**Tools:**
- `NearbyHotelRestaurantTool` - Google Places integration for dining
- Accepts lat/lng coordinates for precise proximity searches

### 🔄 Workflow Pipeline

```
1. INPUT PARSING
   ├─ Parse CSV destinations and attractions
   ├─ Validate date formats and duration
   └─ Set daily time boundaries (default: 09:00-20:00)

2. DESTINATION VALIDATION
   ├─ Google Places lookup for each destination
   ├─ Extract coordinates and place_id
   └─ Validate user-provided attractions

3. ATTRACTION DISCOVERY (if needed)
   ├─ Search for "top attractions in [destination]"
   ├─ Research 10-15 highly-rated options per city
   └─ Combine with user must-visit attractions

4. INTELLIGENT SCHEDULING
   ├─ Estimate visit duration by type:
   │  • Theme parks/major museums: 2-4 hours
   │  • Small museums/galleries: 1-2 hours  
   │  • Landmarks/viewpoints: 30-60 minutes
   │  • Parks/gardens: 1-2 hours
   │
   ├─ Calculate travel time between all pairs:
   │  • Call Distance Matrix API 3x per leg (driving/transit/walking)
   │  • Select recommended mode based on duration/practicality
   │
   ├─ Generate timeline:
   │  • Assign arrival_time and departure_time for each stop
   │  • Account for meal breaks (lunch: 60 min, dinner: 60-90 min)
   │  • Ensure sequential logic (stop N departure + travel = stop N+1 arrival)
   │
   └─ Adaptive fitting:
      • 6+ hour attractions → 1 per day (e.g., theme parks)
      • 2-3 hour attractions → 2-3 per day
      • 30-90 min attractions → 4-5 per day

5. WEATHER INTEGRATION
   ├─ Fetch 7-day forecast for each destination
   ├─ Score suitability (0-100) for outdoor activities
   └─ Reschedule if score < 50 (swap days or times)

6. RESTAURANT RECOMMENDATIONS
   ├─ Find dining options near lunch/dinner locations
   ├─ Use lat/lng from attraction coordinates
   └─ Filter by rating, cuisine, and proximity

7. COST ESTIMATION
   ├─ Attraction entry fees (researched or estimated)
   ├─ Meal costs (breakfast: $15, lunch: $25, dinner: $40 CAD)
   └─ Transport costs (driving: $0.20/km + parking, transit: $3.50/ride)

8. OUTPUT GENERATION
   └─ Structured JSON with complete itinerary details
```

## 📋 Table of Contents
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [API Requirements](#api-requirements)
- [Configuration & Customization](#configuration--customization)
- [Example Output](#example-output)
- [License](#license)

## 🚀 Installation & Setup
## 🚀 Installation & Setup

### Prerequisites
- **Python 3.11+**
- **Poetry** (Python dependency management)
- **API Keys:**
  - Google Maps Platform (Places, Distance Matrix, Geocoding APIs)
  - OpenWeather API
  - OpenAI API (GPT-4 recommended)

### Step-by-Step Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd TripPlanner
   ```

2. **Configure Environment Variables**
   
   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
   
   Add your API keys:
   ```env
   GOOGLE_MAPS_API_KEY=your_google_maps_key_here
   OPENWEATHER_API_KEY=your_openweather_key_here
   OPENAI_API_KEY=your_openai_key_here
   ```

3. **Install Dependencies**
   ```bash
   poetry install --no-root
   ```

4. **Run the Application**
   ```bash
   poetry run python main.py
   ```

## 📖 Usage Guide

### Interactive CLI Flow

When you run the application, you'll be prompted for:

```
1. Destinations (comma-separated)
   Example: Toronto, Montreal, Quebec City
   
2. Specific Attractions (optional - leave blank for AI suggestions)
   Example: CN Tower, Old Montreal, Montmorency Falls
   Or: [Press Enter to let AI discover top attractions]
   
3. Trip Start Date (YYYY-MM-DD)
   Example: 2026-06-15
   
4. Total Trip Duration (days)
   Example: 5
   
5. Daily Start Time (HH:MM, default: 09:00)
   Example: 08:30
   
6. Daily End Time (HH:MM, default: 20:00)
   Example: 21:00
   Note: Dinner can extend past this time
```

### What Happens Next

The AI agents will:
1. ✅ Validate all destinations using Google Maps
2. 🔍 Discover top attractions (if you didn't provide any)
3. 🧮 Calculate travel times for all transport modes
4. ⏰ Generate minute-by-minute schedules
5. 🌤️ Check weather forecasts and optimize outdoor activities
6. 🍽️ Find restaurants near your attraction locations
7. 💰 Calculate total trip costs
8. 📄 Output a complete JSON itinerary

## 📁 Project Structure

```
TripPlanner/
│
├── 🎯 Core Application
│   ├── main.py                      # CLI entry point & crew orchestration
│   ├── trip_agents.py               # Agent definitions (roles, goals, backstories)
│   └── trip_tasks.py                # Task descriptions & expected outputs
│
├── 🛠️ Tool Suite (tools/)
│   ├── Place_tools.py               # Google Places API - attraction validation
│   ├── Distance_tools.py            # Distance Matrix API - multi-modal travel times
│   ├── weather_tools.py             # OpenWeather API - forecasts & suitability
│   ├── hotel_restaurant_tools.py    # Google Places API - dining discovery
│   ├── search_tools.py              # Web search - attraction research
│   ├── calculator_tools.py          # Cost computations & budget estimates
│   ├── browser_tools.py             # Web scraping utilities
│   ├── Image_tools.py               # Attraction image search
│   └── __init__.py
│
├── 📦 Configuration
│   ├── pyproject.toml               # Poetry dependencies & project metadata
│   ├── .env                         # API keys (not in version control)
│   ├── .env.example                 # Template for environment variables
│   └── README.md                    # This file
│
└── 🧪 Testing
    └── test/
        └── debug.py                 # Development & debugging utilities
```

### Key Files Explained

| File | Purpose | Key Components |
|------|---------|----------------|
| `main.py` | Application entry point | `TripPlannerCrew` class, CLI prompts, input parsing |
| `trip_agents.py` | Agent configuration | `landscape_planning_agent`, tool assignments |
| `trip_tasks.py` | Task instructions | Scheduling logic, output schema, optimization rules |
| `Distance_tools.py` | Travel time API | Multi-modal duration calculations, error handling |
| `weather_tools.py` | Weather integration | 7-day forecasts, suitability scoring |
| `hotel_restaurant_tools.py` | Dining finder | Geocoding, proximity search, lat/lng support |

## 📊 Example Output

### Complete Itinerary Structure
## 📊 Example Output

### Complete Itinerary Structure

```json
{
  "trip_summary": {
    "start_date": "2026-06-01",
    "end_date": "2026-06-03",
    "total_duration_days": 3,
    "transport_options_available": ["driving", "transit", "walking"],
    "day_start_time": "09:00",
    "day_end_time": "20:00",
    "estimated_total_cost": {
      "currency": "CAD",
      "attractions": 180,
      "meals": 240,
      "transportation": 95,
      "total": 515
    }
  },
  "destination_plans": [
    {
      "destination": "Toronto",
      "nights": 2,
      "days": [
        {
          "date": "2026-06-01",
          "day_number": 1,
          "total_travel_time_minutes": 85,
          "stops": [
            {
              "order": 1,
              "name": "CN Tower",
              "place_id": "ChIJpTvG15DL1IkRd8S0KlBVNTI",
              "arrival_time": "09:00",
              "departure_time": "11:30",
              "visit_duration_minutes": 150,
              "estimated_cost": 45,
              "travel_from_previous": {
                "driving": {"minutes": 0, "distance_km": 0},
                "transit": {"minutes": 0, "distance_km": 0},
                "walking": {"minutes": 0, "distance_km": 0},
                "recommended_mode": "start"
              },
              "weather": {
                "score": 85,
                "temperature_c": 22,
                "conditions": "Sunny",
                "notes": ["Excellent conditions for tower visit"]
              }
            },
            {
              "order": 2,
              "name": "Ripley's Aquarium",
              "place_id": "ChIJ...",
              "arrival_time": "12:00",
              "departure_time": "14:30",
              "visit_duration_minutes": 150,
              "estimated_cost": 40,
              "travel_from_previous": {
                "driving": {"minutes": 8, "distance_km": 1.2},
                "transit": {"minutes": 15, "distance_km": 1.0},
                "walking": {"minutes": 12, "distance_km": 0.9},
                "recommended_mode": "walking"
              },
              "weather": {
                "score": 100,
                "temperature_c": 23,
                "conditions": "Indoor",
                "notes": ["Weather independent"]
              }
            },
            {
              "order": 3,
              "name": "St. Lawrence Market",
              "place_id": "ChIJ...",
              "arrival_time": "15:00",
              "departure_time": "17:00",
              "visit_duration_minutes": 120,
              "estimated_cost": 25,
              "travel_from_previous": {
                "driving": {"minutes": 12, "distance_km": 3.5},
                "transit": {"minutes": 22, "distance_km": 3.2},
                "walking": {"minutes": 35, "distance_km": 2.8},
                "recommended_mode": "transit"
              },
              "weather": {
                "score": 90,
                "temperature_c": 24,
                "conditions": "Partly Cloudy",
                "notes": ["Good shopping weather"]
              }
            }
          ],
          "recommended_restaurants": [
            {
              "meal_time": "lunch",
              "name": "Canoe Restaurant",
              "place_id": "ChIJ...",
              "cuisine_type": "Canadian",
              "rating": 4.5,
              "price_level": 3,
              "estimated_cost_per_person": 35,
              "distance_from_last_stop_minutes": 5
            },
            {
              "meal_time": "dinner",
              "name": "Pai Northern Thai Kitchen",
              "place_id": "ChIJ...",
              "cuisine_type": "Thai",
              "rating": 4.7,
              "price_level": 2,
              "estimated_cost_per_person": 28,
              "distance_from_last_stop_minutes": 8
            }
          ],
          "daily_cost_estimate": {
            "attractions": 110,
            "meals": 78,
            "transportation": 25,
            "total": 213
          }
        }
      ]
    }
  ]
}
```

## 🔌 API Requirements

### Google Maps Platform

**Required APIs** (enable in [Google Cloud Console](https://console.cloud.google.com/)):

| API | Purpose | Free Tier | Pricing |
|-----|---------|-----------|---------|
| **Places API** | Attraction validation & search|
| **Distance Matrix API** | Multi-modal travel times |
| **Geocoding API** | Address → coordinates |

**Setup Instructions:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable: Places API, Distance Matrix API, Geocoding API
4. Create credentials → API Key
5. (Recommended) Restrict key to these 3 APIs only

### OpenWeather API

**Plan:** Free tier (1000 calls/day)  
**Purpose:** 7-day weather forecasts with temperature, conditions, precipitation

**Setup:**
1. Sign up at [OpenWeather](https://openweathermap.org/api)
2. Get your API key from dashboard
3. Add to `.env` file

### OpenAI API

**Model:** GPT-4 (recommended) or GPT-3.5-turbo  
**Purpose:** AI agent reasoning and decision-making

**Cost Estimate:**
- GPT-4: ~$0.50-2.00 per trip plan
- GPT-3.5-turbo: ~$0.10-0.30 per trip plan

**Setup:**
1. Create account at [OpenAI Platform](https://platform.openai.com/)
2. Add payment method (pay-as-you-go)
3. Generate API key
4. Add to `.env` file

## ⚙️ Configuration & Customization

### Using Different LLM Models

Edit `trip_agents.py` to switch models:
### Using Different LLM Models

Edit `trip_agents.py` to switch models:

```python
from langchain.chat_models import ChatOpenAI

# Option 1: GPT-3.5 (cheaper, faster, less sophisticated)
llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.7)

# Option 2: GPT-4 (default - best quality)
llm = ChatOpenAI(model='gpt-4', temperature=0.7)

# Apply to agents
def landscape_planning_agent(self):
    return Agent(
        role='Expert Trip Planner',
        goal='Create detailed, optimized multi-day itineraries',
        backstory='...',
        tools=[...],
        llm=llm,  # Use custom LLM
        verbose=True
    )
```

### Customizing Default Times

Edit `main.py` to change default schedule:

```python
def __init__(self, destinations, attractions, start_date, duration_days, 
             day_start="08:00",  # Start earlier
             day_end="22:00"):   # End later
    # ... rest of init
```

### Adjusting Restaurant Search Radius

Edit `tools/hotel_restaurant_tools.py`:

```python
class NearbyPlacesInput(BaseModel):
    address: str = Field(...)
    radius: int = Field(3000, ...)  # Change from 2000 to 3000 meters
    max_results: int = Field(10, ...)  # Show more options
```

### Modifying Visit Duration Estimates

Edit `trip_tasks.py` scheduling logic:

```python
- ESTIMATE VISIT DURATION for each attraction based on its type:
  * Large museums/theme parks: 3-5 hours  # Increased from 2-4
  * Small museums/galleries: 1-2 hours
  * Landmarks/viewpoints: 45-90 minutes   # Increased from 30-60
  ...
```

### Changing Cost Assumptions

Edit `trip_tasks.py` cost estimation:

```python
COST ESTIMATION:
- Meals (breakfast ~$20, lunch ~$30, dinner ~$50 per person in CAD)  # Adjusted prices
- Transportation (driving: $0.25/km + parking ~$25/day)  # Increased rates
```

## 🎓 Technical Highlights

### Advanced Features

1. **Adaptive Time Allocation**
   - Dynamically adjusts number of attractions based on estimated visit duration
   - Prevents over-scheduling while maximizing daily experiences
   - Ensures realistic timelines with buffer for delays

2. **Multi-Modal Transport Optimization**
   - Compares driving, transit, and walking for every leg
   - Recommends optimal mode based on distance, time, and practicality
   - Accounts for traffic patterns when using transit

3. **Weather-Aware Rescheduling**
   - Scores outdoor activity suitability (0-100)
   - Automatically reorders stops if weather score < 50
   - Prioritizes indoor activities on poor weather days

4. **Constraint-Based Planning**
   - Respects daily time boundaries (day_start to day_end)
   - Allows dinner to extend past end time
   - Balances workload across days to avoid burnout

5. **Coordinate-Based Restaurant Discovery**
   - Accepts lat/lng format to avoid geocoding failures
   - Searches within configurable radius of attractions
   - Filters by cuisine variety, ratings, and price levels

## 🚀 Future Enhancements

Potential improvements for this project:

- [ ] **Web UI** - Replace CLI with interactive web interface
- [ ] **Hotel Booking Integration** - Find and book accommodations
- [ ] **Real-Time Updates** - Adjust plans based on live traffic/weather
- [ ] **Budget Constraints** - Optimize for specific price ranges
- [ ] **Group Travel** - Handle multiple travelers with different preferences
- [ ] **Export Formats** - Generate PDF/calendar files
- [ ] **Historical Data** - Learn from past trip feedback to improve recommendations
- [ ] **Accessibility Options** - Filter for wheelchair-accessible routes
- [ ] **Local Events** - Integrate festivals, concerts, and seasonal activities

## 📜 License

This project is released under the **MIT License**.

---

**Built with:** CrewAI | Google Maps API | OpenWeather API | OpenAI GPT-4  
**Architecture:** Multi-agent collaboration with specialized roles and shared tools
