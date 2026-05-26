import base64
import time

import streamlit as st
from lib.api_client import BulkPingAPI

if "access_token" not in st.session_state:
    st.switch_page("pages/1_Login.py")
    st.stop()

auto_polling = st.session_state.get("polling", False) and st.session_state.get("last_qr")
if auto_polling:
    count = st.session_state.get("poll_count", 0)
    if count < 60:
        st.session_state["poll_count"] = count + 1
        time.sleep(3)
        st.rerun()

api = BulkPingAPI()
api.token = st.session_state["access_token"]

st.title("Connect WhatsApp")
st.caption(
    "This QR links your WhatsApp number to BulkPing (not your BulkPing login). "
    "Use WhatsApp → Linked devices → Link a device."
)


def decode_qr(qr: str) -> bytes:
    if qr.startswith("data:"):
        qr = qr.split(",", 1)[-1]
    return base64.b64decode(qr)


col1, col2 = st.columns(2)
with col1:
    if st.button("Show QR code", type="primary", use_container_width=True):
        try:
            result = api.post("/api/instance/create/")
            qr = result.get("qr_base64") or ""
            st.session_state["last_qr"] = qr
            st.session_state["polling"] = True
            st.session_state["poll_count"] = 0
            if not qr:
                st.warning("No QR returned. Try again or check Evolution API logs.")
            else:
                st.success("QR ready — scan with WhatsApp")
        except Exception as exc:
            st.error(f"Failed: {exc}")

with col2:
    if st.button("Refresh status", use_container_width=True):
        st.rerun()

qr_data = st.session_state.get("last_qr")
polling = st.session_state.get("polling", False)

if not qr_data:
    try:
        status = api.get("/api/instance/status/")
        qr_data = status.get("qr_base64")
        if status.get("status") == "connected":
            st.success(f"Connected: {status.get('phone_number', '—')}")
            st.balloons()
            st.stop()
    except Exception as exc:
        st.info(f"Click **Show QR code** to connect. ({exc})")

if qr_data:
    try:
        st.image(decode_qr(qr_data), caption="Scan with WhatsApp → Linked devices", width=320)
    except Exception as exc:
        st.error(f"Could not display QR image: {exc}")

try:
    status = api.get("/api/instance/status/")
    st.subheader("Instance status")
    if status.get("status") == "connected":
        st.success(f"Connected: {status.get('phone_number', '—')}")
        st.session_state["polling"] = False
        st.balloons()
    else:
        st.info(f"Status: {status.get('status', 'unknown')} — scan the QR with your phone")
    st.json(status)
except Exception as exc:
    st.caption(f"Status unavailable: {exc}")
