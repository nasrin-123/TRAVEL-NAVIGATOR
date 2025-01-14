import streamlit as st

def show_login():
    # Load custom CSS for styling
    with open("css/loginstyle.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Login Container HTML
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
        <div class="social-buttons">
            <p>Don't have an account?</p>
            <a href="#" onclick="st.session_state['page']='Signup'">Sign Up</a>
        </div>
    </div>
    """
    st.markdown(login_container, unsafe_allow_html=True)

    
