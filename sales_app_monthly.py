import streamlit as st
import pandas as pd
import os
import base64
import random

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="💧 Monthly Consumption Tracker", layout="wide")

# ---------------------------------------------------------
# RANDOM BACKGROUND COLOR OR IMAGE
# ---------------------------------------------------------
def set_random_background():
    colors = [
        "linear-gradient(135deg, #0078D7, #00C9A7)",
        "linear-gradient(135deg, #6A11CB, #2575FC)",
        "linear-gradient(135deg, #FF6A00, #EE0979)",
        "linear-gradient(135deg, #11998e, #38ef7d)",
        "linear-gradient(135deg, #F7971E, #FFD200)"
    ]
    chosen = random.choice(colors)
    css = f"""
    <style>
    .stApp {{
        background: {chosen};
        background-size: cover;
        color: white;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

set_random_background()

# ---------------------------------------------------------
# GLASS CARD STYLE
# ---------------------------------------------------------
st.markdown("""
<style>
.glass-card {
    background: rgba(255,255,255,0.85);
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
}
.stButton>button {
    background-color: #0078D7;
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    border: none;
}
.stButton>button:hover {
    background-color: #00C9A7;
    color: black;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.markdown("<h1 style='text-align:center; color:white;'>💧 Monthly Water Consumption Tracker</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATA DIRECTORY
# ---------------------------------------------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.header("📅 Month Settings")
month = st.sidebar.text_input("Enter Month and Year (e.g., August 2025):", "August 2025")

file_path = os.path.join(DATA_DIR, f"{month.replace(' ', '_')}.csv")

columns = ["No.", "Name", "Old Meter", "New Meter", "Units Used", "Rate", "Total", "Amount Paid", "Balance"]

# ---------------------------------------------------------
# LOAD OR CREATE DATA
# ---------------------------------------------------------
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    st.success(f"✅ Loaded data for {month}")
else:
    df = pd.DataFrame(columns=columns)
    st.info(f"🆕 No data for {month}. Start entering readings below.")

# ---------------------------------------------------------
# MAIN TABLE
# ---------------------------------------------------------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.subheader(f"📋 {month} Consumption Table")

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    key="editor"
)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SAFE CALCULATIONS
# ---------------------------------------------------------
if not edited_df.empty:
    for col in ["Old Meter", "New Meter", "Rate", "Amount Paid"]:
        edited_df[col] = pd.to_numeric(edited_df[col], errors="coerce").fillna(0)

    edited_df["Units Used"] = edited_df["New Meter"] - edited_df["Old Meter"]
    edited_df["Total"] = edited_df["Units Used"] * edited_df["Rate"]
    edited_df["Balance"] = edited_df["Total"] - edited_df["Amount Paid"]

# ---------------------------------------------------------
# MONTH SUMMARY
# ---------------------------------------------------------
if not edited_df.empty:
    st.metric("💰 Total Monthly Sales", f"{edited_df['Total'].sum():,.2f}")

# ---------------------------------------------------------
# SIDEBAR BUTTONS
# ---------------------------------------------------------
st.sidebar.markdown("---")
save_btn = st.sidebar.button("💾 Save Data")
new_btn = st.sidebar.button("🆕 New Month")
saved_btn = st.sidebar.button("📁 View Saved Months")

# Save
if save_btn:
    edited_df.to_csv(file_path, index=False)
    st.success(f"✅ Data saved successfully for {month}")

# New Month
if new_btn:
    st.session_state.clear()
    st.session_state.editor = pd.DataFrame(columns=columns)
    st.rerun()

# View Saved Months
if saved_btn:
    saved_files = [f.replace("_", " ").replace(".csv", "") for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    if saved_files:
        st.subheader("📁 Saved Months")
        for m in sorted(saved_files):
            path = os.path.join(DATA_DIR, f"{m.replace(' ', '_')}.csv")
            total = pd.read_csv(path)["Total"].sum()
            st.write(f"🗓️ **{m}** — 💰 Total: **{total:,.2f}**")
    else:
        st.info("ℹ️ No saved months yet.")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("<p style='text-align:center;color:white;'>Created by Eudes 💧 | Powered by Streamlit</p>", unsafe_allow_html=True)

