import streamlit as st
import pandas as pd
import os
import random

# ---------------------------------------------------------
# APP CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="Water Consumption Tracker", page_icon="💧", layout="wide")

# ---------------------------------------------------------
# BEAUTIFY WITH RANDOM BACKGROUNDS
# ---------------------------------------------------------
backgrounds = [
    "linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%)",
    "linear-gradient(135deg, #f6d365 0%, #fda085 100%)",
    "linear-gradient(120deg, #89f7fe 0%, #66a6ff 100%)",
    "linear-gradient(120deg, #d4fc79 0%, #96e6a1 100%)",
]
st.markdown(
    f"""
    <style>
        .stApp {{
            background: {random.choice(backgrounds)};
            color: #000000;
            font-family: 'Segoe UI', sans-serif;
        }}
        div[data-testid="stSidebar"] {{
            background-color: rgba(255,255,255,0.7);
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💧 Smart Water Consumption Tracker")
st.markdown("Easily record, save, and compare monthly water usage for multiple companies.")

# ---------------------------------------------------------
# DATA STORAGE
# ---------------------------------------------------------
BASE_DIR = "company_data"
os.makedirs(BASE_DIR, exist_ok=True)

# ---------------------------------------------------------
# SELECT COMPANY
# ---------------------------------------------------------
companies = ["Kitengela", "Ebenezer"]
selected_company = st.sidebar.selectbox("🏢 Select Company", companies)
COMPANY_DIR = os.path.join(BASE_DIR, selected_company)
os.makedirs(COMPANY_DIR, exist_ok=True)

# ---------------------------------------------------------
# ENTER MONTH
# ---------------------------------------------------------
month = st.sidebar.text_input("🗓️ Enter Month (e.g. August 2025)")
file_path = os.path.join(COMPANY_DIR, f"{month.replace(' ', '_')}.csv") if month else None

# ---------------------------------------------------------
# TABLE STRUCTURE
# ---------------------------------------------------------
columns = ["Name", "Old Meter", "New Meter", "Rate", "Total"]

# Load data if exists
if month and os.path.exists(file_path):
    df = pd.read_csv(file_path)
else:
    df = pd.DataFrame(columns=columns)

# ---------------------------------------------------------
# DISPLAY EDITOR
# ---------------------------------------------------------
st.subheader(f"📘 Water Usage Data — {selected_company}")
st.info("Enter names, meter readings, and rates below. Totals will calculate automatically.")

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    key="editor",
    use_container_width=True,
)

# ---------------------------------------------------------
# CALCULATE TOTALS
# ---------------------------------------------------------
try:
    edited_df["Old Meter"] = pd.to_numeric(edited_df["Old Meter"], errors="coerce")
    edited_df["New Meter"] = pd.to_numeric(edited_df["New Meter"], errors="coerce")
    edited_df["Rate"] = pd.to_numeric(edited_df["Rate"], errors="coerce")
    edited_df["Total"] = (edited_df["New Meter"] - edited_df["Old Meter"]) * edited_df["Rate"]
except Exception:
    st.warning("⚠️ Please ensure Old Meter, New Meter, and Rate contain valid numbers.")

st.dataframe(edited_df, use_container_width=True)

# ---------------------------------------------------------
# SIDEBAR BUTTONS
# ---------------------------------------------------------
st.sidebar.markdown("---")
save_btn = st.sidebar.button("💾 Save Data")
new_btn = st.sidebar.button("🆕 New Month")
saved_btn = st.sidebar.button("📁 View Saved Months")

# Save
if save_btn:
    if not month:
        st.error("⚠️ Please enter a month name before saving.")
    else:
        edited_df.to_csv(file_path, index=False)
        st.success(f"✅ Data saved successfully for {month} ({selected_company})")

# ✅ FIXED NEW MONTH BUTTON
if new_btn:
    st.session_state.clear()
    st.session_state["new_month_df"] = pd.DataFrame(columns=columns)
    st.session_state["month"] = ""
    st.rerun()

# ✅ VIEW SAVED MONTHS
if saved_btn:
    saved_files = [
        f.replace("_", " ").replace(".csv", "")
        for f in os.listdir(COMPANY_DIR)
        if f.endswith(".csv")
    ]
    if saved_files:
        st.subheader(f"📁 Saved Months for {selected_company}")
        for m in sorted(saved_files):
            path = os.path.join(COMPANY_DIR, f"{m.replace(' ', '_')}.csv")
            total = pd.read_csv(path)["Total"].sum()
            st.write(f"🗓️ **{m}** — 💰 Total: **{total:,.2f}**")
    else:
        st.info("ℹ️ No saved months yet for this company.")


