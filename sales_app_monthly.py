import streamlit as st
import pandas as pd
import os
import base64

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="💧 Monthly Consumption Tracker", layout="wide")

# ---------------------------------------------------------
# BACKGROUND IMAGE FUNCTION
# ---------------------------------------------------------
def add_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}

        .glass-card {{
            background: rgba(255, 255, 255, 0.82);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ✅ CALL BACKGROUND IMAGE HERE — CHANGE FILE NAME IF DIFFERENT
add_bg_from_local("background/bg.jpg")

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.markdown(
    "<h1 style='text-align:center;color:#0078D7;'>💧 Monthly Consumption Tracker</h1>",
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# DATA DIRECTORY SETUP
# ---------------------------------------------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.header("📅 Month Selection")
month = st.sidebar.text_input("Enter Month and Year (e.g., August 2025):", "August 2025")
file_name = month.replace(" ", "_") + ".csv"
file_path = os.path.join(DATA_DIR, file_name)

# ---------------------------------------------------------
# TABLE COLUMNS
# ---------------------------------------------------------
columns = ["No.", "Name", "Old Meter", "New Meter", "Units Used", "Rate", "Total", "Amount Paid", "Balance"]

# ---------------------------------------------------------
# LOAD OR CREATE DATAFRAME
# ---------------------------------------------------------
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    st.success(f"✅ Loaded data for {month}")
else:
    df = pd.DataFrame(columns=columns)
    st.info(f"🆕 No data for {month}. Start entering readings below.")

# ---------------------------------------------------------
# EDITABLE TABLE WITH GLASS CARD EFFECT
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
# AUTO CALCULATIONS (NO ERRORS NOW)
# ---------------------------------------------------------
if not edited_df.empty:
    for col in ["Old Meter", "New Meter", "Rate", "Amount Paid"]:
        edited_df[col] = pd.to_numeric(edited_df[col], errors="coerce").fillna(0)

    edited_df["Units Used"] = edited_df["New Meter"] - edited_df["Old Meter"]
    edited_df["Total"] = edited_df["Units Used"] * edited_df["Rate"]
    edited_df["Balance"] = edited_df["Total"] - edited_df["Amount Paid"]

# ---------------------------------------------------------
# MONTH TOTAL SALES
# ---------------------------------------------------------
st.metric(label="💰 Total Monthly Sales", value=f"{edited_df['Total'].sum():,.2f}")

# ---------------------------------------------------------
# SIDEBAR BUTTONS
# ---------------------------------------------------------
st.sidebar.markdown("---")
save_btn = st.sidebar.button("💾 Save Data")
new_btn = st.sidebar.button("🆕 New Month")
compare_btn = st.sidebar.button("📈 Compare Months")

# ---------------------------------------------------------
# SAVE DATA BUTTON
# ---------------------------------------------------------
if save_btn:
    edited_df.to_csv(file_path, index=False)
    st.success(f"✅ Data saved for {month}!")

# ---------------------------------------------------------
# NEW MONTH BUTTON
# ---------------------------------------------------------
if new_btn:
    st.session_state.editor = pd.DataFrame(columns=columns)
    st.experimental_rerun()

# ---------------------------------------------------------
# MONTH COMPARISON BUTTON
# ---------------------------------------------------------
if compare_btn:
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    summary = []

    for f in files:
        mo = f.replace("_", " ").replace(".csv", "")
        data = pd.read_csv(os.path.join(DATA_DIR, f))
        total = data["Total"].sum()
        summary.append({"Month": mo, "Total": total})

    if summary:
        summary_df = pd.DataFrame(summary)
        st.subheader("📊 Monthly Comparison Summary")
        summary_df = summary_df.sort_values("Month", key=lambda x: pd.to_datetime(x, errors="coerce"))
        st.dataframe(summary_df, use_container_width=True)
        st.bar_chart(summary_df.set_index("Month"))
    else:
        st.info("ℹ️ No saved months to compare.")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("<p style='text-align:center;color:gray;'>Created by Eudes 💧 | Powered by Streamlit</p>", unsafe_allow_html=True)




