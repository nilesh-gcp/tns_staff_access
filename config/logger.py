from config.sheet_adapter import get_worksheet
from datetime import datetime, timezone

def log_event(section, sheet_key, worksheet_key, event_type, email=None, details=None):
    sheet = get_worksheet(section, sheet_key, worksheet_key)
    timestamp = datetime.now(timezone.utc).isoformat()
    row = [timestamp, event_type, email or "N/A", details or "N/A"]
    sheet.append_row(row, value_input_option="USER_ENTERED")