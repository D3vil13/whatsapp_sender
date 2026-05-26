import streamlit as st
from lib.api_client import BulkPingAPI

st.title("Login / Signup")

api = BulkPingAPI()
tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

with tab_login:
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        try:
            data = api.login(email, password)
            st.session_state["access_token"] = data["access"]
            st.session_state["refresh_token"] = data["refresh"]
            st.session_state["api"] = api
            st.success("Logged in!")
            st.switch_page("pages/2_Dashboard.py")
        except Exception as exc:
            st.error(f"Login failed: {exc}")

with tab_signup:
    email_s = st.text_input("Email", key="signup_email")
    password_s = st.text_input("Password", type="password", key="signup_password")
    disclaimer = st.checkbox(
        "I understand BulkPing uses an unofficial WhatsApp bridge (Baileys). "
        "This may violate Meta ToS. I accept full responsibility for my account."
    )
    if st.button("Create account"):
        if not disclaimer:
            st.error("You must accept the disclaimer.")
        else:
            try:
                data = api.signup(email_s, password_s, disclaimer)
                st.session_state["access_token"] = data["access"]
                st.session_state["refresh_token"] = data["refresh"]
                st.session_state["api"] = api
                st.success("Account created!")
                st.switch_page("pages/2_Dashboard.py")
            except Exception as exc:
                st.error(f"Signup failed: {exc}")
