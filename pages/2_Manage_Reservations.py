import streamlit as st
import pandas as pd
import uuid
import numpy as np
from datetime import datetime, timedelta, timezone, date as dt_date
from config.sheet_adapter import get_worksheet, sanitize_for_json
from config.logger import log_event
from auth.session_guard import require_auth
from ui.form_manager import init_reset_flag, reset_form_fields

# 🔐 Enforce authentication
require_auth()
email = st.session_state.user_info.get("email")

# 🧠 Initialize form reset flag
init_reset_flag()
if st.session_state.reset_form:
    reset_form_fields()

# Always ensure keys exist before rendering widgets
st.session_state.setdefault("name_input", "")
st.session_state.setdefault("company_input", "")
st.session_state.setdefault("contact_input", "")
st.session_state.setdefault("ts_lead_input", "")
st.session_state.setdefault("advance_input", "")
st.session_state.setdefault("notes_input", "")
st.session_state.setdefault("res_type_input", "Meeting")
st.session_state.setdefault("slot_input", "Morning")
st.session_state.setdefault("status_input", "In-Progress")
st.session_state.setdefault("date_input", datetime.today())
st.session_state.setdefault("pax_input", 1)


# 📝 Session state for edit tracking
if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

st.title("✏️ Manage Reservations")

mode = st.radio("Choose Action", ["Add New", "Edit Existing"], horizontal=True)

# 🎯 Show filters only in Edit mode
if mode == "Edit Existing":
    filter_option = st.radio("📆 Filter by Date", ["Today", "Current Week", "Next Week", "This Month", "Next Month", "Select Date"], horizontal=True)
    selected_date = st.date_input("Choose a Date") if filter_option == "Select Date" else None
    mobile_filter = st.text_input("📞 Filter by Contact Number")
else:
    filter_option = None
    selected_date = None
    mobile_filter = None

# 📊 Load and sanitize data
sheet = get_worksheet("reservation_sheets", "RESERVATION_SHEET", "RESERVATION_WORKSHEET")
data = sheet.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
df["reservation_date"] = pd.to_datetime(df["reservation_date"], errors="coerce")

# 📅 Time anchors
today = datetime.now().date()
start_of_week = today - timedelta(days=today.weekday())
start_of_next_week = start_of_week + timedelta(days=7)
start_of_month = today.replace(day=1)
start_of_next_month = (start_of_month + timedelta(days=32)).replace(day=1)



def filter_by_date(option):
    if option == "Today":
        return df[df["reservation_date"].dt.date == today]
    elif option == "Current Week":
        end_of_week = start_of_week + timedelta(days=6)
        return df[(df["reservation_date"].dt.date >= start_of_week) & (df["reservation_date"].dt.date <= end_of_week)]
    elif option == "Next Week":
        end_of_next_week = start_of_next_week + timedelta(days=6)
        return df[(df["reservation_date"].dt.date >= start_of_next_week) & (df["reservation_date"].dt.date <= end_of_next_week)]
    elif option == "This Month":
        end_of_month = start_of_next_month - timedelta(days=1)
        return df[(df["reservation_date"].dt.date >= start_of_month) & (df["reservation_date"].dt.date <= end_of_month)]
    elif option == "Next Month":
        end_of_next_month = (start_of_next_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        return df[(df["reservation_date"].dt.date >= start_of_next_month) & (df["reservation_date"].dt.date <= end_of_next_month)]
    elif option == "Select Date" and selected_date:
        return df[df["reservation_date"].dt.date == selected_date]
    return df

filtered_df = filter_by_date(filter_option) if mode == "Edit Existing" else df
if mobile_filter:
    filtered_df = filtered_df[filtered_df["contact_number"].str.contains(mobile_filter, na=False)]

# ➕ ADD NEW MODE
if mode == "Add New":
    st.subheader("➕ Add New Reservation")

    with st.form("add_form", clear_on_submit=False):
        name = st.text_input("Name", key="name_input")
        company = st.text_input("Company", key="company_input")
        contact = st.text_input("Contact Number", key="contact_input")
        ts_lead = st.text_input("T&S LEAD", key="ts_lead_input")
        pax = st.number_input("PAX", min_value=1, step=1, key="pax_input")
        advance = st.text_input("Advance Payment", key="advance_input")
        res_type = st.selectbox("Reservation Type", ["Meeting", "Event", "Workshop", "Famili Getogether", "Office Group"], key="res_type_input")
        date = st.date_input("Reservation Date", key="date_input")
        slot = st.selectbox("Time Slot", ["Morning", "Afternoon", "Evening"], key="slot_input")
        notes = st.text_area("Notes", key="notes_input")
        status = st.selectbox("Status", ["In-Progress", "Confirmed", "Cancelled", "Completed", "Lost"], key="status_input")

        submitted = st.form_submit_button("Submit Reservation")



    if submitted:
        submitted_at = datetime.now(timezone.utc).isoformat()
        audit_id = str(uuid.uuid4())

        row = [
            name, company, contact, ts_lead, pax, advance, res_type,
            str(date), slot, notes, email, submitted_at, audit_id, status
        ]
        sheet.append_row(sanitize_for_json(row), value_input_option="USER_ENTERED")
        log_event("logging_sheets", "LOGGER_SHEET", "LOGGER_WORKSHEET_RESERVATION", "Reservation", email, f"{res_type} for {date} | Audit ID: {audit_id}")
        st.success("✅ Reservation added successfully!")

        st.session_state.reset_form = True
        st.rerun()

# ✏️ EDIT MODE
elif mode == "Edit Existing":
    st.subheader("✏️ Edit Existing Reservation")
    edit_id = st.session_state.edit_id

    if edit_id:
        row_data = df[df["audit_trail_id"] == edit_id].iloc[0]
        row_index = df[df["audit_trail_id"] == edit_id].index[0] + 2

        # Assign audit ID if missing
        if not row_data["audit_trail_id"]:
            new_audit_id = str(uuid.uuid4())
            sheet.update(f"M{row_index}", [[new_audit_id]])  # Adjust column if needed
            df.at[row_index - 2, "audit_trail_id"] = new_audit_id
            row_data["audit_trail_id"] = new_audit_id

        with st.form("edit_form"):
            name = st.text_input("Name", value=row_data["name"])
            company = st.text_input("Company", value=row_data["company"])
            contact = st.text_input("Contact Number", value=row_data["contact_number"])
            ts_lead = st.text_input("T&S LEAD", value=row_data["t&s_lead"])
            pax = st.number_input("PAX", min_value=1, step=1, value=int(row_data["pax"]))
            advance = st.text_input("Advance Payment", value=row_data["advance_payment"])
            res_type = st.selectbox("Reservation Type", ["Meeting", "Event", "Workshop", "Famili Getogether", "Office Group"], index=["Meeting", "Event", "Workshop", "Famili Getogether", "Office Group"].index(row_data["reservation_type"]))
            date = st.date_input("Reservation Date", value=row_data["reservation_date"].date())
            slot = st.selectbox("Time Slot", ["Morning", "Afternoon", "Evening"], index=["Morning", "Afternoon", "Evening"].index(row_data["time_slot"]))
            notes = st.text_area("Notes", value=row_data["notes"])
            status = st.selectbox("Status", ["In-Progress", "Confirmed", "Cancelled", "Completed", "Lost"], index=["In-Progress", "Confirmed", "Cancelled", "Completed", "Lost"].index(row_data["status"]))
            submitted_at = row_data["submitted_at"]
            audit_id = row_data["audit_trail_id"] or str(uuid.uuid4())

            updated = st.form_submit_button("Update Reservation")
            if updated:
                updated_row = [
                    name, company, contact, ts_lead, pax, advance, res_type,
                    str(date), slot, notes, email, submitted_at, audit_id, status
                ]
                sheet.update(f"A{row_index}", [sanitize_for_json(updated_row)])
                log_event("logging_sheets", "LOGGER_SHEET", "LOGGER_WORKSHEET_RESERVATION", "Reservation Edited", email, f"{res_type} for {date} | Audit ID: {audit_id}")
                st.success("Reservation updated.")
                st.session_state.edit_id = None
                st.rerun()

    elif not filtered_df.empty:
        st.markdown("### 🔍 Select a Reservation to Edit")

        # Table header
        header_cols = st.columns([2, 2, 2, 1, 1])
        header_cols[0].markdown("**Name**")
        header_cols[1].markdown("**Mobile**")
        header_cols[2].markdown("**Date**")
        header_cols[3].markdown("**PAX**")
        header_cols[4].markdown("**Action**")

        # Table rows
        for _, row in filtered_df.iterrows():
            cols = st.columns([2, 2, 2, 1, 1])
            cols[0].write(row["name"])
            cols[1].write(row["contact_number"])
            cols[2].write(row["reservation_date"].date())
            cols[3].write(row["pax"])
            if cols[4].button("✏️ Edit", key=row["audit_trail_id"]):
                st.session_state.edit_id = row["audit_trail_id"]
                st.rerun()
    else:
        st.info("No reservations found for the selected filters.")