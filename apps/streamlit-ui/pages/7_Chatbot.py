import streamlit as st
import pandas as pd
from lib.api_client import BulkPingAPI

if "access_token" not in st.session_state:
    st.switch_page("pages/1_Login.py")
    st.stop()

api = BulkPingAPI()
api.token = st.session_state["access_token"]

st.title("Chatbot rules")

try:
    rules = api.get("/api/chatbot/rules/")
    for rule in rules:
        active = st.checkbox(
            f"{'[FALLBACK] ' if rule.get('is_fallback') else ''}{rule.get('keyword', '')}",
            value=rule.get("is_active", True),
            key=str(rule["id"]),
        )
        if active != rule.get("is_active"):
            api.patch(f"/api/chatbot/rules/{rule['id']}/", {"is_active": active})
    st.dataframe(pd.DataFrame(rules), use_container_width=True)
except Exception as exc:
    st.info(f"No rules: {exc}")

with st.form("new_rule"):
    keyword = st.text_input("Keyword (leave empty for fallback)")
    reply = st.text_area("Reply text")
    is_fallback = st.checkbox("Fallback rule")
    if st.form_submit_button("Add rule"):
        try:
            payload = {"reply_text": reply, "is_fallback": is_fallback}
            if keyword:
                payload["keyword"] = keyword
            api.post("/api/chatbot/rules/", json=payload)
            st.success("Rule added")
            st.rerun()
        except Exception as exc:
            st.error(exc)
