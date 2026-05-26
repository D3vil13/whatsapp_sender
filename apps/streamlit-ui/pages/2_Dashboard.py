import streamlit as st
import pandas as pd
from lib.api_client import BulkPingAPI

if "access_token" not in st.session_state:
    st.switch_page("pages/1_Login.py")
    st.stop()

api = st.session_state.get("api") or BulkPingAPI()
api.token = st.session_state["access_token"]

st.title("Dashboard")

col1, col2, col3 = st.columns(3)
with col1:
    try:
        instance = api.get("/api/instance/status/")
        st.metric("Instance status", instance.get("status", "unknown"))
        if instance.get("phone_number"):
            st.caption(f"📞 {instance['phone_number']}")
    except Exception:
        st.metric("Instance status", "—")

with col2:
    try:
        instance = api.get("/api/instance/status/")
        sent = instance.get("daily_sent_count", 0)
        cap = instance.get("daily_cap", 50)
        st.metric("Daily sends", f"{sent} / {cap}")
        st.progress(min(sent / max(cap, 1), 1.0))
    except Exception:
        st.metric("Daily sends", "—")

with col3:
    try:
        campaigns = api.get("/api/campaigns/")
        st.metric("Total campaigns", len(campaigns))
    except Exception:
        st.metric("Total campaigns", "—")

st.divider()

try:
    analytics = api.get("/api/campaigns/analytics/")
    st.subheader("Aggregate analytics")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total recipients", analytics.get("total_recipients", 0))
    m2.metric("Sent", analytics.get("total_sent", 0))
    m3.metric("Delivered", analytics.get("total_delivered", 0))
    m4.metric("Read", analytics.get("total_read", 0))
    m5.metric("Failed", analytics.get("total_failed", 0))

    campaigns_data = analytics.get("campaigns", [])
    if campaigns_data:
        st.subheader("Recent campaigns")
        df = pd.DataFrame(campaigns_data)
        cols = ["name", "status", "total_count", "sent_count", "delivered_count", "read_count", "failed_count", "open_rate"]
        display_cols = [c for c in cols if c in df.columns]
        st.dataframe(df[display_cols], use_container_width=True)
except Exception as exc:
    st.caption(f"Analytics unavailable: {exc}")
