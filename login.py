import streamlit as st

st.set_page_config(page_title="Travel Website - Login", page_icon="🌍")

with open("css/loginstyle.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


login_container = """

<div class="login-container">
    <h3 style="font-family: 'Playfair Display', serif;">Travel Navigator</h3>
    <p>Your gateway to amazing travel experiences</p>
    <form>
        <input type="text" placeholder="Username" required>
        <input type="password" placeholder="Password" required>
        <a href="#" style="float: right; font-size: 0.8rem; color: #007BFF; text-decoration: none;">Forgot password?</a>
        <button type="submit">Log In</button>
    </form>
    <p style=""></p> 
    <div class="social-buttons">
        Don't have an account?
        <a>Sign Up<a/>
    </div>
</div>

"""

st.markdown(login_container, unsafe_allow_html=True)
