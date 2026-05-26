import streamlit as st
import pandas as pd
from lib.api_client import BulkPingAPI

if "access_token" not in st.session_state:
    st.switch_page("pages/1_Login.py")
    st.stop()

api = BulkPingAPI()
api.token = st.session_state["access_token"]

st.title("Campaigns")

tab_list, tab_new, tab_quick = st.tabs(["All campaigns", "New campaign", "Quick send"])

with tab_list:
    try:
        campaigns = api.get("/api/campaigns/")
        if campaigns:
            df = pd.DataFrame(campaigns)
            st.dataframe(df, use_container_width=True)
            selected = st.selectbox("View campaign details", options=[c["id"] for c in campaigns], format_func=lambda x: next(c["name"] for c in campaigns if c["id"] == x))
            if st.button("View details") and selected:
                st.session_state["campaign_detail_id"] = selected
                st.switch_page("pages/6_Campaign_Detail.py")
        else:
            st.info("No campaigns yet.")
    except Exception as exc:
        st.error(exc)
    if st.button("Refresh", key="refresh_campaigns"):
        st.rerun()

with tab_new:
    try:
        groups = api.get("/api/groups/")
        group_options = {g["name"]: g["id"] for g in groups}
    except Exception:
        group_options = {}
    name = st.text_input("Campaign name")
    message = st.text_area("Message")
    group_name = st.selectbox("Target group", list(group_options.keys()) or ["—"])
    media_url = st.text_input("Media URL (optional)")
    if st.button("Send broadcast"):
        if not group_options:
            st.error("Create a group with contacts first.")
        else:
            try:
                payload = {
                    "name": name,
                    "message_text": message,
                    "group_id": group_options[group_name],
                }
                if media_url:
                    payload["media_url"] = media_url
                result = api.post("/api/campaigns/", json=payload)
                if result.get("warning"):
                    st.warning(result["warning"])
                st.success(f"Campaign queued: {result.get('id')}")
            except Exception as exc:
                st.error(exc)

with tab_quick:
    st.subheader("Send a message to a single contact")
    try:
        contacts = api.get("/api/contacts/")
        if not contacts:
            st.info("No contacts yet. Add contacts first.")
        else:
            contact_map = {f"{c['name']} — {c['phone']}": c for c in contacts}
            selected_label = st.selectbox("Select contact", list(contact_map.keys()))
            contact = contact_map[selected_label]
            quick_msg = st.text_area("Message", key="quick_msg")
            quick_media = st.text_input("Media URL (optional)", key="quick_media")
            if st.button("Send", type="primary"):
                payload = {
                    "name": contact["name"],
                    "phone": contact["phone"],
                    "message_text": quick_msg,
                }
                if quick_media:
                    payload["media_url"] = quick_media
                result = api.post("/api/campaigns/quick-send/", json=payload)
                st.success(f"Message sent to {contact['name']}! Campaign: {result.get('id')}")
    except Exception as exc:
        st.error(exc)
