import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

# Define required scopes for Sheets + Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_client():
    """
    Authorizes gspread using service account credentials from streamlit.secrets.
    """
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

def get_worksheet(section: str, sheet_key: str, worksheet_key: str):
    """
    Retrieves a worksheet using keys from a nested secrets section.
    Example: get_worksheet("reservation_sheets", "RESERVATION_SHEET", "RESERVATION_WORKSHEET")
    """
    client = get_client()
    sheet_id = st.secrets[section][sheet_key]
    worksheet_name = st.secrets[section][worksheet_key]
    return client.open_by_key(sheet_id).worksheet(worksheet_name)

def get_approved_emails():
    """
    Loads authorized email addresses from the access control sheet.
    Assumes emails are in the first column, starting from row 2.
    """
    sheet = get_worksheet("access_control_sheets", "ACCESS_CONTROL_SHEET", "ACCESS_CONTROL_WORKSHEET")
    return [email.strip().lower() for email in sheet.col_values(1)[1:] if email]