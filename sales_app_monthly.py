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
        }
        </style>
        """
    st.markdown(css, unsafe_allow_html=True)

set_background("background/bg.jpg")

# ---------------------------------------------------------
# STYLE
# ---------------------------------------------------------
st.markdown("""
<style>
.glass-card {
    background: rgba(255,255,255,0.85);
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.sidebar-button {
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.markdown("<h1 style='text-align:center; color:white;'>💧 Monthly Consumption Tracker</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATA DIRECTORY
# ---------------------------------------------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.header("📅 Manage Data")

# Option to choose existing or new file
file_option = st.sidebar.radio("Select Option:", ["🆕 New Month", "📂 Open Saved File"])

# File name handling
if file_option == "🆕 New Month":
    month = st.sidebar.text_input("Enter Month and Year (e.g., August 2025):", "August 2025")
    file_path = os.path.join(DATA_DIR, f"{month.replace(' ', '_')}.csv")
else:
    saved_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    if saved_files:
        selected_file = st.sidebar.selectbox("Select a Saved File:", saved_files)
        file_path = os.path.join(DATA_DIR, selected_file)
    else:
        st.sidebar.info("No saved files found. Create a new month first.")
        file_path = None

columns = [
    "No.", "Name", "Current", "Old Meter", "New Meter",
    "1st Total", "Rate", "2nd Total", "Amount Paid", "Balance"
]

# ---------------------------------------------------------
# LOAD OR CREATE DATAFRAME
# ---------------------------------------------------------
if file_path and os.path.exists(file_path):
    df = pd.read_csv(file_path)
    st.success(f"✅ Loaded data from: {os.path.basename(file_path)}")
else:
    df = pd.DataFrame(columns=columns)
    if file_option == "🆕 New Month":
        st.info("🆕 Start entering new data for this month below.")

# ---------------------------------------------------------
# TABLE DISPLAY
# ---------------------------------------------------------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.subheader("📋 Water Consumption Table")

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    key="editor"
)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# AUTO CALCULATION
# ---------------------------------------------------------
if not edited_df.empty:
    try:
        for col in ["Old Meter", "New Meter", "Rate", "Amount Paid", "1st Total", "2nd Total", "Current"]:
            edited_df[col] = pd.to_numeric(edited_df[col], errors="coerce").fillna(0)

        edited_df["1st Total"] = edited_df["New Meter"] - edited_df["Old Meter"]
        edited_df["2nd Total"] = edited_df["1st Total"] * edited_df["Rate"]
        edited_df["Balance"] = edited_df["2nd Total"] - edited_df["Amount Paid"]

        total_sales = edited_df["2nd Total"].sum()
        st.metric("💰 Total Monthly Sales", f"{total_sales:,.2f}")

    except Exception as e:
        st.warning(f"⚠️ Could not calculate totals: {e}")

# ---------------------------------------------------------
# SIDEBAR BUTTONS
# ---------------------------------------------------------
st.sidebar.markdown("---")
save_btn = st.sidebar.button("💾 Save File", key="save_btn")
compare_btn = st.sidebar.button("📊 Compare Months", key="compare_btn")

# Save
if save_btn:
    if file_path:
        edited_df.to_csv(file_path, index=False)
        st.success(f"✅ Data saved successfully to {os.path.basename(file_path)}")
    else:
        st.error("⚠️ Please enter a valid month or select a file before saving.")

# Compare Months
if compare_btn:
    months = []
    for f in os.listdir(DATA_DIR):
        if f.endswith(".csv"):
            try:
                data = pd.read_csv(os.path.join(DATA_DIR, f))
                total = data["2nd Total"].sum()
                months.append({"Month": f.replace(".csv", ""), "Total": total})
            except Exception:
                continue

    if months:
        st.subheader("📊 Monthly Comparison Summary")
        compare_df = pd.DataFrame(months).sort_values("Month")
        st.dataframe(compare_df, use_container_width=True)
        st.bar_chart(compare_df.set_index("Month"))
    else:
        st.info("ℹ️ No saved data found for comparison.")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("<p style='text-align:center;color:white;'>Created by Eudes 💧 | Powered by Streamlit</p>", unsafe_allow_html=True)









