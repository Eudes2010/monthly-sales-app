import streamlit as st
import pandas as pd
import os
import random

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="Water Billing System", page_icon="💧", layout="wide")

# ---------------------------------------------------------
# THEMES
# ---------------------------------------------------------
themes = [
    "linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%)",
    "linear-gradient(135deg, #f6d365 0%, #fda085 100%)",
    "linear-gradient(120deg, #89f7fe 0%, #66a6ff 100%)",
    "linear-gradient(120deg, #d4fc79 0%, #96e6a1 100%)",
]
st.markdown(
    f"""
    <style>
        .stApp {{
            background: {random.choice(themes)};
            color: black;
            font-family: 'Segoe UI', sans-serif;
        }}
        div[data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.8);
        }}
        .stDataFrame {{
            background-color: rgba(255, 255, 255, 0.85);
            border-radius: 12px;
            padding: 10px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.title("💧 Water Consumption & Billing System")
st.markdown("Easily record, calculate, and track monthly water usage for multiple companies.")

# ---------------------------------------------------------
# STORAGE SETUP
# ---------------------------------------------------------
BASE_DIR = "company_data"
os.makedirs(BASE_DIR, exist_ok=True)

# ---------------------------------------------------------
# COMPANY SELECTION
# ---------------------------------------------------------
companies = ["Kitengela", "Ebenezer"]
company = st.sidebar.selectbox("🏢 Select Company", companies)
COMPANY_DIR = os.path.join(BASE_DIR, company)
os.makedirs(COMPANY_DIR, exist_ok=True)

# ---------------------------------------------------------
# MONTH ENTRY
# ---------------------------------------------------------
month = st.sidebar.text_input("🗓️ Enter Month (e.g. August 2025)")
file_path = os.path.join(COMPANY_DIR, f"{month.replace(' ', '_')}.csv") if month else None

# ---------------------------------------------------------
# TABLE STRUCTURE
# ---------------------------------------------------------
columns = [
    "Name",
    "Previous",
    "New Meter",
    "Rate",
    "Total",
    "Amount Paid",
    "Balance",
]

if month and os.path.exists(file_path):
    df = pd.read_csv(file_path)
else:
    df = pd.DataFrame(columns=columns)

# ---------------------------------------------------------
# EDITOR
# ---------------------------------------------------------
st.subheader(f"📘 Water Usage Data — {company}")
st.info("Enter customer details, meter readings, and payments. Totals and balances update automatically.")

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    key="editor",
    use_container_width=True,
)

# ---------------------------------------------------------
# AUTO-CALCULATIONS
# ---------------------------------------------------------
try:
    edited_df["Previous"] = pd.to_numeric(edited_df["Previous"], errors="coerce")
    edited_df["New Meter"] = pd.to_numeric(edited_df["New Meter"], errors="coerce")
    edited_df["Rate"] = pd.to_numeric(edited_df["Rate"], errors="coerce").fillna(135)
    edited_df["Amount Paid"] = pd.to_numeric(edited_df["Amount Paid"], errors="coerce").fillna(0)

    edited_df["Total"] = (edited_df["New Meter"] - edited_df["Previous"]) * edited_df["Rate"]
    edited_df["Balance"] = edited_df["Total"] - edited_df["Amount Paid"]
except Exception:
    st.warning("⚠️ Please ensure all meter and rate values are numbers.")

# ---------------------------------------------------------
# DISPLAY UPDATED TABLE
# ---------------------------------------------------------
st.dataframe(edited_df, use_container_width=True)

# ---------------------------------------------------------
# SIDEBAR BUTTONS
# ---------------------------------------------------------
st.sidebar.markdown("---")
save = st.sidebar.button("💾 Save Data")
new = st.sidebar.button("🆕 New Month")
view = st.sidebar.button("📁 View Saved Months")

# SAVE
if save:
    if not month:
        st.error("⚠️ Please enter a month before saving.")
    else:
        edited_df.to_csv(file_path, index=False)
        st.success(f"✅ Data saved for {month} ({company})")

# NEW MONTH
if new:
    st.session_state.clear()
    st.session_state["new_month_df"] = pd.DataFrame(columns=columns)
    st.rerun()

# VIEW SAVED MONTHS
if view:
    saved_files = [
        f.replace("_", " ").replace(".csv", "")
        for f in os.listdir(COMPANY_DIR)
        if f.endswith(".csv")
    ]
    if saved_files:
        st.subheader(f"📁 Saved Months — {company}")
        for m in sorted(saved_files):
            path = os.path.join(COMPANY_DIR, f"{m.replace(' ', '_')}.csv")
            df_month = pd.read_csv(path)
            total_sum = df_month["Total"].sum()
            balance_sum = df_month["Balance"].sum()
            st.write(f"🗓️ **{m}** — 💰 Total: **{total_sum:,.2f}**, Balance: **{balance_sum:,.2f}**")
    else:
        st.info("ℹ️ No saved months yet for this company.")


