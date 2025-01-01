import streamlit as st

# Function to load custom CSS
def load_css(file_path):
    """Function to load a CSS file."""
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Set the page configuration
st.set_page_config(page_title="Travel Website - Login", page_icon="🌍")

# Load the CSS from the 'css' folder
load_css("css/style.css")

# Sidebar heading
st.sidebar.title("USMAAANNEEE")

# Main heading
st.title("Welcome to TravelGo 🌟")
st.subheader("Your gateway to amazing travel experiences")

# Login form
st.write("### Login to Your Account")
username = st.text_input("Username", placeholder="Enter your username")
password = st.text_input("Password", type="password", placeholder="Enter your password")

if st.button("Login"):
    if username == "admin" and password == "password123":
        st.success(f"Welcome back, {username}!")
        st.write("🎉 Enjoy exploring new travel destinations!")
    else:
        st.error("Invalid username or password. Please try again.")

# Additional options
st.write("Don't have an account? [Sign up here](#)")
st.write("Forgot your password? [Reset it here](#)")

# Footer
st.markdown("---")
st.write("💼 Crafted by **TravelGo Team**")
st.write("🌐 Visit us at [TravelGo](https://example.com)")
