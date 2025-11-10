import streamlit as st
import pandas as pd
import os
import base64

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="💧 Monthly Consumption Tracker", layout="wide")

# ---------------------------------------------------------
# BACKGROUND IMAGE
# ---------------------------------------------------------
def set_background(image_file=None):
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

set_background("background/bg.jpg")

# ---------------------------------------------------------
# PAGE STYLE
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
# HEADER
# ---------------------------------------------------------
st.markdown("<h1 style='text-align:center; color:white;'>💧 Monthly Consumption Tracker (Excel Style)</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATA DIRECTORY
# ---------------------------------------------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------------------------------------
# SIDEBAR CONTROLS
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
# MAIN BUTTONS
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("💾 Save File"):
        df.to_csv(st.session_state.current_file, index=False)
        st.success(f"✅ File saved: {os.path.basename(st.session_state.current_file)}")

with col2:
    if st.button("🆕 New Month"):
        new_file = f"{company}_{month.replace(' ', '_')}_new.csv"
        st.session_state.current_file = os.path.join(DATA_DIR, new_file)
        st.session_state.new_df = pd.DataFrame(columns=columns)
        st.success("📄 New blank month created.")
        st.rerun()

with col3:
    if st.button("📂 Compare Months"):
        st.session_state.view = "compare"
        st.rerun()

with col4:
    if st.button("↩ Return"):
        st.session_state.view = "main"
        st.rerun()

# ---------------------------------------------------------
# VIEW LOGIC
# ---------------------------------------------------------
if "view" not in st.session_state:
    st.session_state.view = "main"

# ---------------------------------------------------------
# MAIN VIEW (EXCEL-LIKE EDITOR)
# ---------------------------------------------------------
if st.session_state.view == "main":
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader(f"📋 {company} — {month} Data Table")

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key="editor"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Automatic Calculations
    if not edited_df.empty:
        for col in ["Old Meter", "New Meter", "Rate", "Amount Paid", "1st Total", "2nd Total", "Current"]:
            edited_df[col] = pd.to_numeric(edited_df[col], errors="coerce").fillna(0)

        edited_df["1st Total"] = edited_df["New Meter"] - edited_df["Old Meter"]
        edited_df["2nd Total"] = edited_df["1st Total"] * edited_df["Rate"]
        edited_df["Balance"] = edited_df["2nd Total"] - edited_df["Amount Paid"]

        edited_df.to_csv(st.session_state.current_file, index=False)
        st.success(f"💾 Auto-saved: {os.path.basename(st.session_state.current_file)}")

        total_sales = edited_df["2nd Total"].sum()
        st.metric("💰 Total Monthly Sales", f"{total_sales:,.2f}")

# ---------------------------------------------------------
# COMPARE MONTHS VIEW
# ---------------------------------------------------------
elif st.session_state.view == "compare":
    st.subheader("📊 Compare Two Saved Months")

    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    if len(files) < 2:
        st.warning("You need at least 2 saved months to compare.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            f1 = st.selectbox("Select First Month", files, key="f1")
        with c2:
            f2 = st.selectbox("Select Second Month", files, key="f2")

        if st.button("🔍 Compare Now"):
            df1 = pd.read_csv(os.path.join(DATA_DIR, f1))
            df2 = pd.read_csv(os.path.join(DATA_DIR, f2))

            t1 = df1["2nd Total"].sum()
            t2 = df2["2nd Total"].sum()

            diff = t2 - t1

            st.write(f"💧 **{f1}:** {t1:,.2f}")
            st.write(f"💧 **{f2}:** {t2:,.2f}")
            st.write(f"📈 **Change:** {diff:,.2f}")

            st.bar_chart(pd.DataFrame({
                "Month": [f1, f2],
                "Total Sales": [t1, t2]
            }).set_index("Month"))

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("<p style='text-align:center;color:white;'>Created by Eudes 💧 | Excel-Style Tracker</p>", unsafe_allow_html=True)








