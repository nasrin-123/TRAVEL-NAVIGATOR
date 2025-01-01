import streamlit as st
import base64

def set_background(image_file):
    """Sets the background image for the Streamlit app."""
    with open(image_file, "rb") as img:
        data = base64.b64encode(img.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{data}");
            background-size: cover;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
# Set page configuration
st.set_page_config(page_title="Signup Page", page_icon="📋")

# Set the background image
set_background(r'C:\Users\samee\Documents\projects\TRAVEL-NAVIGATOR\TRAVEL-NAVIGATOR\images\signup.jpg')  # Replace with your image file path

# Signup form
st.title("Signup Page")
st.write("Please fill in the details below to sign up.")

# Input fields
name = st.text_input("Name", placeholder="Enter your full name")
username = st.text_input("Username", placeholder="Choose a unique username")
email = st.text_input("Email", placeholder="Enter your email address")
password = st.text_input("Password", placeholder="Create a password", type="password")

if st.button("Signup"):
    if name and username and email and password:
        # Placeholder for database or other actions
        st.success(f"Thank you for signing up, {name}!")
        st.write("Your details:")
        st.write(f"- **Username:** {username}")
        st.write(f"- **Email:** {email}")
    else:
        st.error("Please fill in all the fields.")
