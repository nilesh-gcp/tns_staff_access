import streamlit as st
import pandas as pd
import uuid
from datetime import datetime, timedelta, timezone
from config.sheet_adapter import get_worksheet
from config.logger import log_event
import plotly.express as px
from auth.session_guard import require_auth

# Load reservation sheet
sheet = get_worksheet("reservation_sheets", "RESERVATION_SHEET", "RESERVATION_WORKSHEET")
# Enforce authentication
require_auth()

st.title("📅 Reservation Dashboard")

# Load and sanitize data
data = sheet.get_all_values()
df = pd.DataFrame(data[1:], columns=data[0])
df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

# Ensure reservation_date is datetime
if "reservation_date" not in df.columns:
    st.error("❌ 'Reservation Date' column not found. Please check your sheet headers.")
    st.stop()

df["reservation_date"] = pd.to_datetime(df["reservation_date"], format="%Y-%m-%d", errors="coerce")


# Time anchors
today = datetime.now().date()
start_of_week = today - timedelta(days=today.weekday())
start_of_next_week = start_of_week + timedelta(days=7)
start_of_month = today.replace(day=1)
start_of_next_month = (start_of_month + timedelta(days=32)).replace(day=1)

# Filter options
filter_option = st.radio("📆 Period", ["Today", "Current Week", "Next Week", "This Month", "Next Month"], horizontal=True)

def filter_reservations(option):
    if option == "Today":
        return df[df["reservation_date"] == pd.Timestamp(today)]
    elif option == "Current Week":
        end_of_week = start_of_week + timedelta(days=6)
        print(end_of_week, start_of_week)
        return df[(df["reservation_date"] >= pd.Timestamp(start_of_week)) & (df["reservation_date"] <= pd.Timestamp(end_of_week))]
    elif option == "Next Week":
        end_of_next_week = start_of_next_week + timedelta(days=6)
        return df[(df["reservation_date"] >= pd.Timestamp(start_of_next_week)) & (df["reservation_date"] <= pd.Timestamp(end_of_next_week))]
    elif option == "This Month":
        end_of_month = start_of_next_month - timedelta(days=1)
        return df[(df["reservation_date"] >= pd.Timestamp(start_of_month)) & (df["reservation_date"] <= pd.Timestamp(end_of_month))]
    elif option == "Next Month":
        end_of_next_month = (start_of_next_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        return df[(df["reservation_date"] >= pd.Timestamp(start_of_next_month)) & (df["reservation_date"] <= pd.Timestamp(end_of_next_month))]

filtered_df = filter_reservations(filter_option)

# Unified aggregation table
st.markdown(f"### 📊 Summary for: {filter_option}")

if filtered_df.empty:
    st.info("No reservations found for the selected period.")
else:
    summary_rows = []
    grouped = filtered_df.groupby(filtered_df["reservation_date"].dt.date)

    for date, group in grouped:
        total_pax = pd.to_numeric(group["pax"], errors="coerce").sum()
        total_reservations = len(group)
        slot_counts = group["time_slot"].value_counts().to_dict()
        status_counts = group["status"].value_counts().to_dict()

        summary_rows.append({
            "Date": date,
            "Total Reservations": total_reservations,
            "Total PAX": int(total_pax),
            "Morning": slot_counts.get("Morning", 0),
            "Afternoon": slot_counts.get("Afternoon", 0),
            "Evening": slot_counts.get("Evening", 0),
            "In-Progress": status_counts.get("In-Progress", 0),
            "Confirmed": status_counts.get("Confirmed", 0),
            "Cancelled": status_counts.get("Cancelled", 0),
            "Completed": status_counts.get("Completed", 0),
            "Lost": status_counts.get("Lost", 0)
        })

    summary_df = pd.DataFrame(summary_rows)
    st.dataframe(summary_df, use_container_width=True)

    # Pie chart with dynamic status adjustment
    adjusted_df = filtered_df.copy()
    adjusted_df["effective_status"] = adjusted_df.apply(
        lambda row: "Completed" if row["status"] == "Confirmed" and row["reservation_date"].date() < today else row["status"],
        axis=1
    )

    status_labels = ["In-Progress", "Confirmed", "Cancelled", "Completed", "Lost"]
    status_pax = {
        status: pd.to_numeric(
            adjusted_df[adjusted_df["effective_status"] == status]["pax"], errors="coerce"
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
            "Lost": "gray"
        }

    )
    # Show raw numbers instead of percentages
    fig.update_traces(textinfo="label+value")

    st.markdown("### 🥧 PAX Distribution by Status")
    st.plotly_chart(fig, use_container_width=True)