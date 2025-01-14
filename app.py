import streamlit as st
import os
from login import show_login
from signup import show_signup

# Set the page configuration at the very top
st.set_page_config(page_title="Travel Around the World", layout="wide", page_icon="✈️")

def load_css(file_path):
    """Function to load CSS styles."""
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the CSS for the home page
css_path = os.path.join("css", "homestyle.css")
load_css(css_path)

def show_home():
    """Function to display the home page."""
    # Header with Streamlit buttons for Login and Sign Up
    col1, col2, col3 = st.columns([3, 1, 1])  # Adjust column widths as needed
    with col1:
        st.markdown("<div class='logo'>TRAVELNAVIGATOR®</div>", unsafe_allow_html=True)
    with col2:
        if st.button("Login"):
            st.session_state["page"] = "Login"
    with col3:
        if st.button("Sign Up"):
            st.session_state["page"] = "Signup"

    # Hero section
    st.markdown(
        """
        <div class="hero">
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <h1>Travel Around the World</h1>
                <p>As an independent entity, we provide supportive and neutral governance to our coalition.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Destinations section
    st.markdown("### Top destinations for your next holiday")
    st.markdown("Here's where your fellow travelers are headed")

    col4, col5, col6, col7 = st.columns(4)

    with col4:
        st.image("images/lake.jpg", caption="Goa, India", use_container_width=True)
        if st.button("Explore Goa"):
            st.session_state["page"] = "Goa"

    with col5:
        st.image("images/kashmir.jpg", caption="Kashmir, India", use_container_width=True)
        if st.button("Explore Kashmir"):
            st.session_state["page"] = "Kashmir"

    with col6:
        st.image("images/mumbai.jpg", caption="Mumbai, India", use_container_width=True)
        if st.button("Explore Mumbai"):
            st.session_state["page"] = "Mumbai"

    with col7:
        st.image("images/kuttanad.jpg", caption="Kuttanad, India", use_container_width=True)
        if st.button("Explore Kuttanad"):
            st.session_state["page"] = "Kuttanad"

def show_details(place):
    """Function to display details for a destination."""
    st.title(f"Discover {place}")
    if place == "Goa":
        st.write("Goa is known for its vibrant street life and cultural landmarks...")
    elif place == "Kashmir":
        st.write("Kashmir is a global hub of commerce, culture, and cuisine...")
    elif place == "Mumbai":
        st.write("Mumbai is India’s financial capital and home to Bollywood...")
    elif place == "Kuttanad":
        st.write("Kuttanad is famous for its forested volcanic mountains and iconic beaches...")
    if st.button("Back to Home"):
        st.session_state["page"] = "Home"

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state["page"] = "Home"

# Routing logic
if st.session_state["page"] == "Home":
    show_home()
elif st.session_state["page"] == "Login":
    show_login()
elif st.session_state["page"] == "Signup":
    show_signup()
else:
    show_details(st.session_state["page"])
