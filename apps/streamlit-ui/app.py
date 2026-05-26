import streamlit as st

st.set_page_config(page_title="BulkPing", page_icon="📣", layout="wide")

st.title("BulkPing")
st.caption("WhatsApp BSP — Testing UI (Streamlit)")

if "access_token" not in st.session_state:
    st.warning("Please log in from the **Login** page in the sidebar.")
    st.page_link("pages/1_Login.py", label="Go to Login →")
else:
    st.success("You are logged in.")
    st.page_link("pages/2_Dashboard.py", label="Go to Dashboard →")
