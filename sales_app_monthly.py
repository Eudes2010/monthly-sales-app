import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="💧 Monthly Consumption Tracker", layout="wide")

# Create folder for data
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

st.title("💧 Monthly Water/Sales Consumption Tracker")

# Sidebar controls
st.sidebar.header("📅 Month Selector")
month = st.sidebar.text_input("Enter month and year (e.g., August 2025):", "August 2025")
file_path = os.path.join(DATA_DIR, f"{month.replace(' ', '_')}.csv")

# Table structure
columns = [
    "No.",
    "Name",
    "Current Reading",
    "Previous Reading",
    "New Meter",
    "Total",
    "Amount Paid",
    "Balance"
]

# Load or create table
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    st.success(f"Loaded existing data for {month}")
else:
    df = pd.DataFrame(columns=columns)
    st.warning(f"No data found for {month}. Starting a new table.")

# Display editable table
st.subheader(f"📋 {month} Consumption Table")
edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    key="data_editor"
)

# Calculate total
if not edited_df.empty:
    try:
        total_sales = edited_df["Total"].astype(float).sum()
    except:
        total_sales = 0
else:
    total_sales = 0

st.metric("💰 Total Sales / Consumption", f"{total_sales:,.2f}")

# Action buttons
btn_col1, btn_col2, btn_col3 = st.sidebar.columns([1, 1, 1])

save_clicked = btn_col1.button("💾 Save Table")
new_clicked = btn_col2.button("🆕 New Month")
show_all_clicked = btn_col3.button("📈 Compare Months")

# Save data
if save_clicked:
    edited_df.to_csv(file_path, index=False)
    st.success(f"✅ Data saved for {month}!")

# Start new month
if new_clicked:
    st.session_state["data_editor"] = pd.DataFrame(columns=columns)
    st.experimental_rerun()

# Compare all months
if show_all_clicked:
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    summary = []
    for f in files:
        m = f.replace("_", " ").replace(".csv", "")
        data = pd.read_csv(os.path.join(DATA_DIR, f))
        total = data["Total"].astype(float).sum() if "Total" in data.columns else 0
        summary.append({"Month": m, "Total": total})
    summary_df = pd.DataFrame(summary).sort_values("Month")
    st.subheader("📊 Monthly Comparison Summary")
    st.dataframe(summary_df, use_container_width=True)
