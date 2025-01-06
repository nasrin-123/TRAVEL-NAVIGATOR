import streamlit as st
from streamlit_folium import st_folium
import folium

# Title and description
st.title("Travel Navigator")
st.write("Plan your trip, generate a detailed itinerary, and see all the places on an interactive map.")

# Initialize session state
if "itinerary" not in st.session_state:
    st.session_state.itinerary = None
if "destination" not in st.session_state:
    st.session_state.destination = ""
if "preferences" not in st.session_state:
    st.session_state.preferences = []

# Mock function to simulate fetching itinerary places
@st.cache_data
def fetch_places(destination, preferences):
    # Simulated data (replace this with actual API calls like Google Places or OpenStreetMap)
    return [
        {"name": "Central Park", "lat": 40.785091, "lon": -73.968285, "type": "Park"},
        {"name": "Times Square", "lat": 40.758896, "lon": -73.985130, "type": "Attraction"},
        {"name": "Joe's Pizza", "lat": 40.730610, "lon": -73.935242, "type": "Restaurant"},
        {"name": "Broadway Theatre", "lat": 40.759011, "lon": -73.984472, "type": "Theatre"},
    ]

# User input form
with st.form("trip_form"):
    destination = st.text_input("Enter your destination:", st.session_state.destination)
    preferences = st.multiselect(
        "Select your preferences:",
        ["Restaurants", "Shops", "Museums", "Parks"],
        st.session_state.preferences
    )
    submitted = st.form_submit_button("Create Itinerary")

# Process form submission
if submitted:
    st.session_state.destination = destination
    st.session_state.preferences = preferences
    st.session_state.itinerary = fetch_places(destination, preferences)

# Display itinerary and map only if data is available
if st.session_state.itinerary:
    st.write(f"**Destination:** {st.session_state.destination}")
    st.write(f"**Preferences:** {', '.join(st.session_state.preferences)}")

    st.write("**Itinerary:**")
    for place in st.session_state.itinerary:
        st.write(f"- {place['name']} ({place['type']})")

    # Create and display the map
    map_center = [st.session_state.itinerary[0]['lat'], st.session_state.itinerary[0]['lon']]
    m = folium.Map(location=map_center, zoom_start=12)

    # Add itinerary locations as markers
    for place in st.session_state.itinerary:
        folium.Marker(
            location=[place['lat'], place['lon']],
            popup=f"{place['name']} ({place['type']})",
            icon=folium.Icon(color="blue" if place["type"] == "Park" else "green")
        ).add_to(m)

    st.write("**Map of Itinerary Locations:**")
    st_folium(m, width=700, height=500)
