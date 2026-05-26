import streamlit as st
import pandas as pd
from lib.api_client import BulkPingAPI

if "access_token" not in st.session_state:
    st.switch_page("pages/1_Login.py")
    st.stop()

api = BulkPingAPI()
api.token = st.session_state["access_token"]

st.title("Analytics")

try:
    analytics = api.get("/api/campaigns/analytics/")
    campaigns = analytics.get("campaigns", [])
except Exception as exc:
    st.error(f"Failed to load analytics: {exc}")
    st.stop()

if not campaigns:
    st.info("No campaigns yet. Create a campaign and send messages to see analytics.")
    st.stop()

st.subheader("Aggregate totals")
t1, t2, t3, t4, t5 = st.columns(5)
t1.metric("Total campaigns", analytics.get("total_campaigns", 0))
t2.metric("Total recipients", analytics.get("total_recipients", 0))
t3.metric("Total sent", analytics.get("total_sent", 0))
t4.metric("Total delivered", analytics.get("total_delivered", 0))
t5.metric("Total read", analytics.get("total_read", 0))

t6, t7, t8, t9 = st.columns(4)
t6.metric("Total failed", analytics.get("total_failed", 0))
t7.metric("Pending / processing", analytics.get("total_pending", 0))
t8.metric("Total replied", analytics.get("total_replied", 0))
t9.metric("Stopped", analytics.get("total_stopped", 0))

open_rate_total = round(
    (analytics.get("total_read", 0) / analytics.get("total_delivered", 1) * 100), 1
) if analytics.get("total_delivered", 0) else 0.0
st.metric("Overall open rate", f"{open_rate_total}%")

st.divider()

st.subheader("Per-campaign analytics")
df = pd.DataFrame(campaigns)
display_cols = [
    "name", "status", "total_count", "queued_processing", "sent_count",
    "delivered_count", "read_count", "ignored_count", "failed_count",
    "reply_count", "open_rate", "stopped",
]
existing_cols = [c for c in display_cols if c in df.columns]
st.dataframe(df[existing_cols], use_container_width=True)

st.divider()

st.subheader("Delivery funnel chart")
selected_name = st.selectbox("Select campaign", options=[c["name"] for c in campaigns])
camp = next(c for c in campaigns if c["name"] == selected_name)
funnel_data = pd.DataFrame(
    {
        "Stage": ["Sent", "Delivered", "Read", "Failed"],
        "Count": [
            camp.get("sent_count", 0),
            camp.get("delivered_count", 0),
            camp.get("read_count", 0),
            camp.get("failed_count", 0),
        ],
    }
).set_index("Stage")
st.bar_chart(funnel_data)

st.divider()

st.subheader("Campaign detail")
selected_id = st.selectbox(
    "View detailed stats for campaign",
    options=[c["id"] for c in campaigns],
    format_func=lambda x: next(c["name"] for c in campaigns if c["id"] == x),
)
if selected_id:
    try:
        detail = api.get(f"/api/campaigns/{selected_id}/stats/")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total", detail.get("total_count", 0))
        col_b.metric("Sent", detail.get("sent_count", 0))
        col_c.metric("Delivered", detail.get("delivered_count", 0))

        col_d, col_e, col_f = st.columns(3)
        col_d.metric("Read", detail.get("read_count", 0))
        col_e.metric("Failed", detail.get("failed_count", 0))
        col_f.metric("Open rate", f"{detail.get('open_rate', 0)}%")

        logs = detail.get("logs", [])
        if logs:
            st.subheader("Per-contact delivery log")
            st.dataframe(pd.DataFrame(logs), use_container_width=True)

        if st.button("Stop campaign", type="secondary"):
            try:
                api.post(f"/api/campaigns/{selected_id}/stop/")
                st.success("Campaign stopped")
                st.rerun()
            except Exception as exc:
                st.error(exc)
    except Exception as exc:
        st.error(exc)
