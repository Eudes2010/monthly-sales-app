import streamlit as st
import pandas as pd
import os
import base64

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="💧 Monthly Consumption Tracker", layout="wide")

# ---------------------------------------------------------
# BACKGROUND IMAGE HANDLER WITH FALLBACK
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
# GLASS CARD STYLE
# ---------------------------------------------------------
st.markdown("""
<style>
.glass-card {
    background: rgba(255,255,255,0.82);
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
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
# SIDEBAR
# ---------------------------------------------------------
st.sidebar.header("📅 Month Selection")
month = st.sidebar.text_input("Enter Month and Year (e.g., August 2025):", "August 2025")
file_path = os.path.join(DATA_DIR, f"{month.replace(' ', '_')}.csv")

# Updated columns with "Current" and two "Total" columns
columns = [
    "No.", "Name", "Current", "Previous", "New Meter",
    "Total 1", "Rate", "Total", "Amount Paid", "Balance"
]

# Load or create data
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    st.success(f"✅ Loaded data for {month}")
else:
    df = pd.DataFrame(columns=columns)
    st.info(f"🆕 No data for {month}. Start entering readings below.")

# ---------------------------------------------------------
# EDITABLE TABLE
# ---------------------------------------------------------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.subheader(f"📋 {month} Consumption Table")

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    key=f"editor_{month}"
)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SAFE AUTO CALCULATION
# ---------------------------------------------------------
if not edited_df.empty:
    try:
        for col in ["Current", "Previous", "New Meter", "Rate", "Amount Paid"]:
            edited_df[col] = pd.to_numeric(edited_df[col], errors="coerce").fillna(0)

        # Calculate the two totals
        edited_df["Total 1"] = edited_df["Current"] - edited_df["Previous"]
        edited_df["Total"] = edited_df["Total 1"] * edited_df["Rate"]
        edited_df["Balance"] = edited_df["Total"] - edited_df["Amount Paid"]

    except Exception as e:
        st.warning(f"⚠️ Could not calculate totals: {e}")

# ---------------------------------------------------------
# MONTH SUMMARY
# ---------------------------------------------------------
if not edited_df.empty:
    total_sales = edited_df["Total"].sum()
    st.metric("💰 Total Monthly Sales", f"{total_sales:,.2f}")

# ---------------------------------------------------------
# SIDEBAR BUTTONS
# ---------------------------------------------------------
st.sidebar.markdown("---")
save_btn = st.sidebar.button("💾 Save Data")
new_btn = st.sidebar.button("🆕 New Month")
compare_btn = st.sidebar.button("📈 Compare Months")
saved_btn = st.sidebar.button("📂 Show Saved Months")

# Save
if save_btn:
    edited_df.to_csv(file_path, index=False)
    st.success(f"✅ Data saved for {month}")

# New month
if new_btn:
    st.session_state[f"editor_{month}"] = pd.DataFrame(columns=columns)
    st.rerun()

# Compare
if compare_btn:
    months = []
    for f in os.listdir(DATA_DIR):
        if f.endswith(".csv"):
            m = f.replace("_", " ").replace(".csv", "")
            t = pd.read_csv(os.path.join(DATA_DIR, f))["Total"].sum()
            months.append({"Month": m, "Total": t})

    if months:
        st.subheader("📊 Monthly Comparison Summary")
        compare_df = pd.DataFrame(months).sort_values("Month")
        st.dataframe(compare_df, use_container_width=True)
        st.bar_chart(compare_df.set_index("Month"))
    else:
        st.info("ℹ️ No saved months yet to compare.")

# Show saved months
if saved_btn:
    saved_files = [f.replace("_", " ").replace(".csv", "") for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    if saved_files:
        st.subheader("📂 Saved Months")
        st.write(saved_files)
    else:
        st.info("No saved months found yet.")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("<p style='text-align:center;color:white;'>Created by Eudes 💧 | Powered by Streamlit</p>", unsafe_allow_html=True)



