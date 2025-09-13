import streamlit as st
from config.sheet_adapter import get_worksheet
from config.logger import log_event

def membership_page():
    st.title("👥 Membership Directory")

    email = st.session_state.user_info.get("email")
    sheet = get_worksheet("membership_sheets", "MEMBERSHIP_SHEET", "MEMBERSHIP_WORKSHEET")

    st.subheader("Add Member")
    name = st.text_input("Member Name")
    role = st.selectbox("Role", ["Member", "Admin", "Guest"])
    contact = st.text_input("Contact Info")

    if st.button("Add Member"):
        row = [name, role, contact, email]
        sheet.append_row(row, value_input_option="USER_ENTERED")
        st.success("Member added.")
        log_event("logging_sheets", "LOGGER_SHEET", "LOGGER_WORKSHEET_MEMBERSHIP", "AddMember", email, f"Added {name} as {role}")

    st.subheader("📋 Member List")
    data = sheet.get_all_values()
    for row in data[1:]:
        st.write(f"👤 {row[0]} — {row[1]} ({row[2]})")

membership_page()