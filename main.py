import streamlit as st
from auth.oauth_flow import fetch_token, get_auth_url, get_user_info
from config.sheet_adapter import get_approved_emails
from config.logger import log_event
from config.config import get

def main():
    approved_emails = get_approved_emails()

    if "user_info" not in st.session_state:
        code = st.query_params.get("code")
        if code:
            token_data = fetch_token(code)
            access_token = token_data.get("access_token")
            if access_token:
                user_info = get_user_info(access_token)
                email = user_info.get("email", "").lower()
                if email in approved_emails:
                    st.session_state.user_info = user_info
                    st.success(f"Welcome, {email}!")
                    log_event("logging_sheets", "LOGGER_SHEET", "LOGGER_WORKSHEET_MEMBERSHIP", "Login", email, "Access granted")
                else:
                    st.error("Access denied. Your email is not authorized.")
                    log_event("logging_sheets", "LOGGER_SHEET", "LOGGER_WORKSHEET_MEMBERSHIP", "Login", email, "Access denied")
                    st.stop()
            else:
                st.error("Token retrieval failed.")
                st.stop()
        else:
            st.markdown(f"[🔐 Login with Google]({get_auth_url()})")
            st.stop()
    else:
        email = st.session_state.user_info.get("email")
        st.success(f"Welcome back, {email}!")
        if st.button("Logout"):
            del st.session_state["user_info"]
            log_event("logging_sheets", "LOGGER_SHEET", "LOGGER_WORKSHEET_MEMBERSHIP", "Logout", email, "User logged out")
            st.rerun()

if __name__ == "__main__":
    main()