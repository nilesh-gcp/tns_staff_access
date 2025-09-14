import streamlit as st
from config.sheet_adapter import get_worksheet
from config.logger import log_event
from auth.session_guard import require_auth


#🔐 Enforce authentication for this page
require_auth()

def membership_page():
    # Set the page title
    st.title("👥 Membership Directory")

    # Get the current user's email from session state
    email = st.session_state.user_info.get("email")
    # Access the membership worksheet
    sheet = get_worksheet("membership_sheets", "MEMBERSHIP_SHEET", "MEMBERSHIP_WORKSHEET")

    # Section to add a new member
    st.subheader("Add Member")
    name = st.text_input("Member Name")  # Input for member's name
    role = st.selectbox("Role", ["Member", "Admin", "Guest"])  # Select member's role
    contact = st.text_input("Contact Info")  # Input for contact info

    # Handle the Add Member button click
    if st.button("Add Member"):
        row = [name, role, contact, email]  # Prepare row data
        sheet.append_row(row, value_input_option="USER_ENTERED")  # Add row to sheet
        st.success("Member added.")  # Show success message
        # Log the event of adding a member
        log_event("logging_sheets", "LOGGER_SHEET", "LOGGER_WORKSHEET_MEMBERSHIP", "AddMember", email, f"Added {name} as {role}")

    # Section to display the member list
    st.subheader("📋 Member List")
    data = sheet.get_all_values()  # Get all member data
    # Display each member (skip header row)
    for row in data[1:]:
        st.write(f"👤 {row[0]} — {row[1]} ({row[2]})")

# Run the membership page
membership_page()