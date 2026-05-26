import streamlit as st
import pandas as pd
from lib.api_client import BulkPingAPI

if "access_token" not in st.session_state:
    st.switch_page("pages/1_Login.py")
    st.stop()

api = BulkPingAPI()
api.token = st.session_state["access_token"]

st.title("Contacts & Groups")

tab_contacts, tab_groups = st.tabs(["Contacts", "Groups"])

with tab_contacts:
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Add contact")
        with st.form("add_contact"):
            name = st.text_input("Name", key="add_name")
            phone = st.text_input("Phone (+91...)", key="add_phone")
            if st.form_submit_button("Add contact"):
                try:
                    api.post("/api/contacts/", json={"name": name, "phone": phone})
                    st.success("Contact added")
                    st.rerun()
                except Exception as exc:
                    st.error(exc)
    with col_right:
        st.subheader("Import CSV")
        uploaded = st.file_uploader("Columns: name, phone", type=["csv"])
        if uploaded and st.button("Import"):
            try:
                result = api.post(
                    "/api/contacts/import/",
                    files={"file": (uploaded.name, uploaded.getvalue(), "text/csv")},
                )
                st.success(f"Imported {result.get('imported')} / {result.get('total')} contacts")
                st.caption(result.get("disclaimer", ""))
                st.rerun()
            except Exception as exc:
                st.error(exc)

    st.subheader("All contacts")
    try:
        contacts = api.get("/api/contacts/")
        if contacts:
            df = pd.DataFrame(contacts)
            df["delete"] = False
            for i, row in df.iterrows():
                c1, c2 = st.columns([6, 1])
                c1.text(f"{row['name']} — {row['phone']}")
                if c2.button("Delete", key=f"del_{row['id']}"):
                    api.delete(f"/api/contacts/{row['id']}/")
                    st.rerun()
        else:
            st.info("No contacts yet. Add one above or import a CSV.")
    except Exception as exc:
        st.info(f"Could not load contacts: {exc}")

with tab_groups:
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Create group")
        with st.form("new_group"):
            group_name = st.text_input("Group name")
            if st.form_submit_button("Create group"):
                try:
                    api.post("/api/groups/", json={"name": group_name})
                    st.success("Group created")
                    st.rerun()
                except Exception as exc:
                    st.error(exc)

    st.subheader("All groups")
    try:
        groups = api.get("/api/groups/")
        if not groups:
            st.info("No groups yet.")
        for g in groups:
            with st.expander(f"{g['name']} ({g.get('member_count', 0)} members)"):
                try:
                    members = api.get(f"/api/groups/{g['id']}/members/")
                    member_ids = {m["id"] for m in members}
                except Exception:
                    members = []
                    member_ids = set()

                if members:
                    for m in members:
                        c1, c2 = st.columns([5, 1])
                        c1.text(f"{m['name']} — {m['phone']}")
                        if c2.button("Remove", key=f"rm_{g['id']}_{m['id']}"):
                            api.delete(
                                f"/api/groups/{g['id']}/members/",
                                json={"contact_ids": [m["id"]]},
                            )
                            st.rerun()

                st.divider()
                st.caption("Add contacts to this group")
                try:
                    all_contacts = api.get("/api/contacts/")
                    available = [c for c in all_contacts if c["id"] not in member_ids]
                    if available:
                        selected_names = st.multiselect(
                            "Select contacts",
                            options=[f"{c['name']} — {c['phone']}" for c in available],
                            key=f"add_{g['id']}",
                        )
                        if st.button("Add selected", key=f"add_btn_{g['id']}"):
                            selected_ids = [
                                c["id"]
                                for c in available
                                if f"{c['name']} — {c['phone']}" in selected_names
                            ]
                            if selected_ids:
                                api.post(
                                    f"/api/groups/{g['id']}/members/",
                                    json={"contact_ids": selected_ids},
                                )
                                st.rerun()
                    else:
                        st.info("All contacts are already in this group.")
                except Exception as exc:
                    st.caption(f"Could not load contacts: {exc}")
    except Exception as exc:
        st.info(f"Could not load groups: {exc}")
