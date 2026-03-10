from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import markdown2

from main import run_trip_planner


# Ensure environment variables from .env are available in web context
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Trip Planner Web UI")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Serve static assets (CSS, images) if present
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Render the trip input form."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
        },
    )


@app.post("/plan", response_class=HTMLResponse)
async def plan(
    request: Request,
    origin: str = Form(...),
    cities: str = Form(...),
    date_range: str = Form(...),
    interests: str = Form(...),
) -> HTMLResponse:
    """
    Handle form submission, run the trip planner, and render the result page.
    """
    itinerary = run_trip_planner(
        origin=origin.strip(),
        cities=cities.strip(),
        date_range=date_range.strip(),
        interests=interests.strip(),
    )
    itinerary_text = str(itinerary)
    itinerary_html = markdown2.markdown(itinerary_text)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "origin": origin,
            "cities": cities,
            "date_range": date_range,
            "interests": interests,
            "itinerary": itinerary,
            "itinerary_html": itinerary_html,
        },
    )


@app.post("/api/plan")
async def api_plan(
    origin: str,
    cities: str,
    date_range: str,
    interests: str,
) -> dict:
    """
    Simple JSON API for programmatic access.
    """
    itinerary = run_trip_planner(
        origin=origin.strip(),
        cities=cities.strip(),
        date_range=date_range.strip(),
        interests=interests.strip(),
    )
    return {
        "origin": origin,
        "cities": cities,
        "date_range": date_range,
        "interests": interests,
        "itinerary": str(itinerary),
    }

