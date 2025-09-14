import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from config.sheet_adapter import get_worksheet
from config.logger import log_event
import plotly.express as px
from auth.session_guard import require_auth

# --- Column header variables ---
RESERVATION_DATE = "Reservation Date"
PAX = "PAX"
TIME_SLOT = "Time Slot"
STATUS = "Status"

# --- Streamlit app configuration & auth ---
st.set_page_config(
    page_title="Reservation Dashboard",
    page_icon="📅",
    layout="centered",  # Centered layout better on mobile
    initial_sidebar_state="collapsed"
)
require_auth()

# --- Title and caption ---
st.title("📅 Reservation Dashboard")
st.caption("Monitor upcoming reservations and track guest volumes & booking status.")

# --- Inline top filter to save mobile space ---
filter_option = st.selectbox(
    "Select period",
    options=["Today", "Current Week", "Next Week", "This Month", "Next Month"],
    index=0,
    help="Filter reservations by time period",
)

# --- Load data ---
sheet = get_worksheet("reservation_sheets", "RESERVATION_SHEET", "RESERVATION_WORKSHEET")
data = sheet.get_all_values()

df = pd.DataFrame(data[1:], columns=data[0])
# df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]

if RESERVATION_DATE not in df.columns:
    st.error(f"❌ '{RESERVATION_DATE}' column not found. Please verify your sheet headers.")
    st.stop()

# Convert to datetime
df[RESERVATION_DATE] = pd.to_datetime(df[RESERVATION_DATE], format="%Y-%m-%d", errors="coerce")

# --- Date anchors ---
today = datetime.now().date()
start_of_week = today - timedelta(days=today.weekday())
start_of_next_week = start_of_week + timedelta(days=7)
start_of_month = today.replace(day=1)
start_of_next_month = (start_of_month + timedelta(days=32)).replace(day=1)

def filter_reservations(option):
    if option == "Today":
        return df[df[RESERVATION_DATE] == pd.Timestamp(today)]
    elif option == "Current Week":
        end_of_week = start_of_week + timedelta(days=6)
        return df[(df[RESERVATION_DATE] >= pd.Timestamp(start_of_week)) & (df[RESERVATION_DATE] <= pd.Timestamp(end_of_week))]
    elif option == "Next Week":
        end_of_next_week = start_of_next_week + timedelta(days=6)
        return df[(df[RESERVATION_DATE] >= pd.Timestamp(start_of_next_week)) & (df[RESERVATION_DATE] <= pd.Timestamp(end_of_next_week))]
    elif option == "This Month":
        end_of_month = start_of_next_month - timedelta(days=1)
        return df[(df[RESERVATION_DATE] >= pd.Timestamp(start_of_month)) & (df[RESERVATION_DATE] <= pd.Timestamp(end_of_month))]
    elif option == "Next Month":
        end_of_next_month = (start_of_next_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        return df[(df[RESERVATION_DATE] >= pd.Timestamp(start_of_next_month)) & (df[RESERVATION_DATE] <= pd.Timestamp(end_of_next_month))]

filtered_df = filter_reservations(filter_option)

# --- Summary table ---
st.markdown(f"### 📊 Summary for: _{filter_option}_")

if filtered_df.empty:
    st.info("No reservations found for the selected period.")
else:
    summary_rows = []
    grouped = filtered_df.groupby(filtered_df[RESERVATION_DATE].dt.date)

    for date, group in grouped:
        total_pax = pd.to_numeric(group[PAX], errors="coerce").sum()
        total_reservations = len(group)
        slot_counts = group[TIME_SLOT].value_counts().to_dict()
        status_counts = group[STATUS].value_counts().to_dict()

        summary_rows.append({
            "Date": date,
            "Total Reservations": total_reservations,
            "Total PAX": int(total_pax),
            # On mobile smaller screens only show total reservations and pax to reduce horizontal scroll
            # Show all columns on wider screens via CSS media query or responsive design (can be added if needed)
            "Morning": slot_counts.get("Morning", 0),
            "Afternoon": slot_counts.get("Afternoon", 0),
            "Evening": slot_counts.get("Evening", 0),
            "In-Progress": status_counts.get("In-Progress", 0),
            "Confirmed": status_counts.get("Confirmed", 0),
            "Cancelled": status_counts.get("Cancelled", 0),
            "Completed": status_counts.get("Completed", 0),
            "Lost": status_counts.get("Lost", 0),
        })

    summary_df = pd.DataFrame(summary_rows)

    # Display a simplified table showing only Date, Total Reservations, and Total PAX first
    columns_small = ["Date", "Total Reservations", "Total PAX"]
    st.dataframe(summary_df[columns_small], use_container_width=True)
    st.caption("Note: On smaller screens, summary shows condensed columns for better readability.")

    # --- Pie chart ---
    adjusted_df = filtered_df.copy()
    adjusted_df["effective_status"] = adjusted_df.apply(
        lambda row: "Completed" if row[STATUS] == "Confirmed" and row[RESERVATION_DATE].date() < today else row[STATUS],
        axis=1
    )

    status_labels = ["In-Progress", "Confirmed", "Cancelled", "Completed", "Lost"]
    status_pax = {
        status: pd.to_numeric(
            adjusted_df[adjusted_df["effective_status"] == status][PAX], errors="coerce"
        ).sum()
        for status in status_labels
    }

    pie_data = pd.DataFrame({
        "Status": status_labels,
        "PAX": [status_pax.get(s, 0) for s in status_labels]
    })

    fig = px.pie(
        pie_data,
        names="Status",
        values="PAX",
        title=f"PAX Distribution by Status ({filter_option})",
        color_discrete_map={
            "In-Progress": "orange",
            "Confirmed": "green",
            "Cancelled": "red",
            "Completed": "blue",
            "Lost": "gray",
        }
    )
    fig.update_traces(textinfo="label+value")
    fig.update_layout(
        margin=dict(t=40, b=0, l=0, r=0),
        font=dict(size=14),
        title_x=0.5,
        legend=dict(orientation="h", y=-0.1)  # Horizontal legend below chart for narrow screens
    )

    st.markdown("### 🥧 PAX Distribution by Status")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Pie chart: Guest volume distribution by reservation status.")

# Optional minimal CSS for spacing & fonts (can extend for responsive tweaks)
st.markdown("""
<style>
    /* Reduce font size slightly on small screens */
    @media (max-width: 600px) {
        .block-container {
            padding: 1rem 0.5rem !important;
            font-size: 90%;
        }
    }
</style>
""", unsafe_allow_html=True)
