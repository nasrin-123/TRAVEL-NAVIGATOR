import streamlit as st
import os

st.set_page_config(page_title="Travel Around the World", layout="wide", page_icon="✈️")

def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

css_path = os.path.join("css", "homestyle.css")
load_css(css_path)

def show_home():
    st.markdown(
        """
        <header>
            <div class="logo">TRAVELNAVIGATOR®</div>
            <nav>
                <ul>
                    <li><a href="#">Home</a></li>
                    <li><a href="#">About us</a></li>
                    <li><a href="#">Routes</a></li>
                    <li><a href="#">Reviews</a></li>
                    <li><a href="#">Blogs</a></li>
                </ul>
            </nav>
            <div class="actions">
                <span>EN</span>
                <button>Sign In</button>
            </div>
        </header>
        """,
        unsafe_allow_html=True,
    )

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

    st.markdown("### Top destinations for your next holiday")
    st.markdown("Here's where your fellow travelers are headed")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
            st.image("images/goa.jpg", caption="Goa, India", use_container_width=True)
            if st.button("Explore Goa", use_container_width=True):
                st.session_state["page"] = "Goa"

    with col2:
        st.image("images/kashmir.jpg", caption="Kashmir, India", use_container_width=True)
        if st.button("Explore Kashmir", use_container_width=True):
            st.session_state["page"] = "Kashmir"

    with col3:
        st.image("images/mumbai.jpg", caption="Mumbai, India", use_container_width=True)
        if st.button("Explore Mumbai", use_container_width=True):
            st.session_state["page"] = "Mumbai"

    with col4:
        st.image("images/kuttanad.jpg", caption="Kuttanad, India", use_container_width=True)
        if st.button("Explore Kuttanad", use_container_width=True):
            st.session_state["page"] = "Kuttanad"
    
   
def show_details(place):
    st.title(f"Discover {place}")
    if place == "Goa":
        st.write("Goa is known for its vibrant street life and cultural landmarks...")
    elif place == "Kashmir":
        st.write("kashmir is a global hub of commerce, culture, and cuisine...")
    elif place == "Mumbai":
        st.write("Mumbai is India’s financial capital and home to Bollywood...")
    elif place == "Kuttanad":
        st.write("Kuttanad is famous for its forested volcanic mountains and iconic beaches...")
    st.button("Back to Home", on_click=lambda: st.session_state.update({"page": "Home"}))


# Main Logic
if "page" not in st.session_state:
    st.session_state["page"] = "Home"

if st.session_state["page"] == "Home":
    show_home()
else:
    show_details(st.session_state["page"])
