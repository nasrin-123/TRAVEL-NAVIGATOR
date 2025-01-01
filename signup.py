import streamlit as st

st.set_page_config(page_title="Signup Page", page_icon="📋")

with open("css/signup.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("Travel Navigator✈️")
st.write("Please fill in the details below to sign up.")

name = st.text_input("Name", placeholder="Enter your full name")
username = st.text_input("Username", placeholder="Choose a unique username")
email = st.text_input("Email", placeholder="Enter your email address")
password = st.text_input("Password", placeholder="Create a password", type="password")

if st.button("Signup"):
    if name and username and email and password:
        st.success(f"Thank you for signing up, {name}!")
        st.write("Your details:")
        st.write(f"- **Username:** {username}")
        st.write(f"- **Email:** {email}")
    else:
        st.error("Please fill in all the fields.")
