import streamlit as st
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

from main import TripCrew

st.set_page_config(page_title="TripPlanner AI", page_icon="🗺️", layout="centered")

st.title("🗺️ TripPlanner AI")
st.markdown(
    "Plan your perfect trip with the help of three AI agents: a **City Selection Expert**, "
    "a **Local Expert**, and a **Travel Concierge** — all working together to build your ideal itinerary."
)

st.divider()

with st.form("trip_form"):
    origin = st.text_input("Where are you traveling from?", placeholder="e.g. San Francisco")

    cities = st.text_input(
        "Which cities are you considering?",
        placeholder="e.g. Tokyo, Paris, New York",
    )

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", value=date.today() + timedelta(days=30))
    with col2:
        end_date = st.date_input("End date", value=date.today() + timedelta(days=37))

    interests = st.text_area(
        "What are your interests and hobbies?",
        placeholder="e.g. food, culture, history, hiking, museums",
        height=100,
    )

    submitted = st.form_submit_button("Plan My Trip ✈️", use_container_width=True, type="primary")

if submitted:
    errors = []
    if not origin.strip():
        errors.append("Please enter your origin city.")
    if not cities.strip():
        errors.append("Please enter at least one destination city.")
    if start_date >= end_date:
        errors.append("End date must be after start date.")
    if not interests.strip():
        errors.append("Please enter your interests.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        date_range = f"{start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"

        with st.spinner("Your AI agents are planning your trip... this may take a few minutes."):
            try:
                crew = TripCrew(origin.strip(), cities.strip(), date_range, interests.strip())
                result = crew.run()
                st.session_state["itinerary"] = str(result)
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.session_state.pop("itinerary", None)

if "itinerary" in st.session_state:
    st.divider()
    st.subheader("Your Travel Itinerary")
    st.markdown(st.session_state["itinerary"])
