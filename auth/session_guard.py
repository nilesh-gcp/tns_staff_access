import streamlit as st
from datetime import datetime, timedelta
from config.logger import log_event
from auth.oauth_flow import get_auth_url

SESSION_TIMEOUT_MINUTES = 60  # Customize as needed

def require_auth():
    """Ensure user is authenticated and session is fresh."""
    user_info = st.session_state.get("user_info", {})
    email = user_info.get("email")

    # Check if email is missing or session expired
    if not email:
        log_event("logging_sheets", "LOGGER_SHEET", "LOGGER_WORKSHEET_MEMBERSHIP", "Access", "unknown", "Unauthenticated access attempt")
        st.markdown(f"[🔐 Login with Google]({get_auth_url()})")
        st.stop()

    if "auth_time" in st.session_state:
        elapsed = datetime.now() - st.session_state.auth_time
        if elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            log_event("logging_sheets", "LOGGER_SHEET", "LOGGER_WORKSHEET_MEMBERSHIP", "Session", email, "Session expired")
            del st.session_state["user_info"]
            del st.session_state["auth_time"]
            st.markdown(f"⏳ Session expired. [🔐 Login again]({get_auth_url()})")
            st.stop()

def set_auth_session(user_info):
    """Initialize session state after successful login."""
    st.session_state.user_info = user_info
    st.session_state.auth_time = datetime.now()