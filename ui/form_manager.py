# ui/form_manager.py

import streamlit as st
from datetime import datetime

# def reset_reservation_form():
#     """Reset all reservation form fields on next rerun."""
#     # defaults = {
#     #     "name_input": "",
#     #     "company_input": "",
#     #     "contact_input": "",
#     #     "ts_lead_input": "",
#     #     "advance_input": "",
#     #     "notes_input": "",
#     #     "res_type_input": "Meeting",
#     #     "slot_input": "Morning",
#     #     "status_input": "In-Progress",
#     #     "date_input": datetime.today(),
#     #     "pax_input": 1
#     # }
#     # for key, value in defaults.items():
#     #     st.session_state[key] = value
#     # st.session_state.reset_form = False

def reset_form_fields():
    st.session_state["name_input"] = ""
    st.session_state["company_input"] = ""
    st.session_state["contact_input"] = ""
    st.session_state["ts_lead_input"] = ""
    st.session_state["advance_input"] = ""
    st.session_state["notes_input"] = ""
    st.session_state["res_type_input"] = "Meeting"
    st.session_state["slot_input"] = "Morning"
    st.session_state["status_input"] = "In-Progress"
    st.session_state["date_input"] = datetime.today()
    st.session_state["pax_input"] = 1
    st.session_state.reset_form = False

def trigger_form_reset():
    """Set flag to reset form on next rerun."""
    st.session_state.reset_form = True
    st.rerun()

def init_reset_flag():
    """Ensure reset flag is initialized."""
    if "reset_form" not in st.session_state:
        st.session_state.reset_form = False