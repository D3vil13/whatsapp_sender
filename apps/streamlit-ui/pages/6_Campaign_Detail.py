import streamlit as st
import pandas as pd
from lib.api_client import BulkPingAPI

if "access_token" not in st.session_state:
    st.switch_page("pages/1_Login.py")
    st.stop()

api = BulkPingAPI()
api.token = st.session_state["access_token"]

st.title("Campaign detail")

campaign_id = st.session_state.get("campaign_detail_id")
if not campaign_id:
    campaign_id = st.text_input("Campaign ID")
    if not campaign_id:
        st.info("Select a campaign from the Campaigns page or enter an ID above.")
        st.stop()

with st.spinner("Loading stats..."):
    try:
        stats = api.get(f"/api/campaigns/{campaign_id}/stats/")
    except Exception as exc:
        st.error(f"Failed to load campaign: {exc}")
        st.stop()

st.subheader(stats.get("name", "—"))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Status", stats.get("status", "—"))
c2.metric("Total recipients", stats.get("total_count", 0))
c3.metric("Sent", stats.get("sent_count", 0))
c4.metric("Delivered", stats.get("delivered_count", 0))

c5, c6, c7, c8 = st.columns(4)
c5.metric("Read", stats.get("read_count", 0))
c6.metric("Failed", stats.get("failed_count", 0))
c7.metric("Open rate", f"{stats.get('open_rate', 0)}%")
c8.metric("Ignored", stats.get("ignored_count", 0))

st.divider()

funnel = pd.DataFrame(
    {
        "Stage": ["Sent", "Delivered", "Read", "Failed"],
        "Count": [
            stats.get("sent_count", 0),
            stats.get("delivered_count", 0),
            stats.get("read_count", 0),
            stats.get("failed_count", 0),
        ],
    }
).set_index("Stage")
st.bar_chart(funnel)

st.divider()

by_status = stats.get("by_status", {})
st.subheader("Per-contact breakdown by status")
for status_name in ("failed", "pending", "sent", "delivered", "read"):
    contacts = by_status.get(status_name, [])
    label = f"{status_name.title()} ({len(contacts)})"
    if status_name == "failed":
        expand = True
    else:
        expand = False
    if contacts:
        with st.expander(label, expanded=expand):
            for c in contacts:
                ts = c.get("status_updated_at") or ""
                st.text(f"{c['contact_name']} — {c['contact_phone']}  ({ts})")
    else:
        st.markdown(f"**{label}**: —")

st.divider()

logs = stats.get("logs", [])
if logs:
    st.subheader("Full delivery log")
    st.dataframe(pd.DataFrame(logs), use_container_width=True)
else:
    st.info("No message logs yet.")

if st.button("Back to campaigns"):
    st.switch_page("pages/5_Campaigns.py")
