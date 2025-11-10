import streamlit as st
import pandas as pd
import os
import base64

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="💧 Monthly Consumption Tracker", layout="wide")

# ---------------------------------------------------------
# BACKGROUND IMAGE HANDLER
# ---------------------------------------------------------
def set_background(image_file=None):
    try:
        if image_file and os.path.exists(image_file):
            with open(image_file, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            css = f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-position: center;
            }}
            </style>
            """
        else:
            css = """
            <style>
            .stApp {
                background: linear-gradient(135deg, #0078D7, #00C9A7);
                background-size: cover;
            }
            </style>
            """
        st.markdown(css, unsafe_allow_html=True)
    except Exception:
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #0078D7, #00C9A7);
        }
        </style>
        """, unsafe_allow_html=True)

set_background("background/bg.jpg")

# ---------------------------------------------------------
# STYLING (Glass Card)
# ---------------------------------------------------------
st.markdown("""
<style>
.glass-card {
    background: rgba(255,255,255,0.88);
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.markdown("<h1 style='text-align:center; color:white;'>💧 Monthly Consumption Tracker (Excel Style)</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATA DIRECTORY
# ---------------------------------------------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------------------------------------
# SIDEBAR (COMPANY + MONTH)
# ---------------------------------------------------------
st.sidebar.header("🏢 Company & Month Setup")
company = st.sidebar.text_input("Company Name:", "Kitengela")
month = st.sidebar.text_input("Month & Year (e.g., August 2025):", "August 2025")

file_name = f"{company}_{month.replace(' ', '_')}.csv"
file_path = os.path.join(DATA_DIR, file_name)

columns = ["No.", "Name", "Current", "Old Meter", "New Meter", "1st Total", "Rate", "2nd Total", "Amount Paid", "Balance"]

# ---------------------------------------------------------
# LOAD OR CREATE FILE
# ---------------------------------------------------------
if "current_file" not in st.session_state:
    st.session_state.current_file = file_path

if os.path.exists(st.session_state.current_file):
    df = pd.read_csv(st.session_state.current_file)
else:
    df = pd.DataFrame(columns=columns)

# ---------------------------------------------------------
# EXCEL-LIKE EDITABLE TABLE
# ---------------------------------------------------------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.subheader(f"📋 {company} — {month} Data Table (Editable like Excel)")

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    key="editor"
)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# AUTO CALCULATION (LIKE FORMULAS)
# ---------------------------------------------------------
if not edited_df.empty:
    for col in ["Old Meter", "New Meter", "Rate", "Amount Paid", "1st Total", "2nd Total", "Current"]:
        edited_df[col] = pd.to_numeric(edited_df[col], errors="coerce").fillna(0)

    edited_df["1st Total"] = edited_df["New Meter"] - edited_df["Old Meter"]
    edited_df["2nd Total"] = edited_df["1st Total"] * edited_df["Rate"]
    edited_df["Balance"] = edited_df["2nd Total"] - edited_df["Amount Paid"]

# ---------------------------------------------------------
# AUTO-SAVE FEATURE
# ---------------------------------------------------------
edited_df.to_csv(st.session_state.current_file, index=False)
st.success(f"💾 Auto-saved: {company} - {month}")

# ---------------------------------------------------------
# TOTAL SALES SUMMARY
# ---------------------------------------------------------
if not edited_df.empty:
    total_sales = edited_df["2nd Total"].sum()
    st.metric("💰 Total Monthly Sales", f"{total_sales:,.2f}")

# ---------------------------------------------------------
# SIDEBAR: SAVED FILES MANAGER (LIKE EXCEL OPEN)
# ---------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("📂 Saved Files Manager")

saved_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]

if saved_files:
    selected_file = st.sidebar.selectbox("Select a saved file:", saved_files)
    open_btn = st.sidebar.button("📂 Open Selected File")

    if open_btn and selected_file:
        st.session_state.current_file = os.path.join(DATA_DIR, selected_file)
        st.success(f"✅ Opened {selected_file}")
        st.rerun()
else:
    st.sidebar.info("No saved files found yet.")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("<p style='text-align:center;color:white;'>Created by Eudes 💧 | Excel-Style Smart Tracker</p>", unsafe_allow_html=True)






