import streamlit as st
import pandas as pd
import os

# --- App settings ---
st.set_page_config(page_title="💧 Monthly Consumption Tracker", layout="wide")

# --- Folder to store monthly data ---
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# --- Title ---
st.markdown("<h1 style='text-align:center;color:#0078D7;'>💧 Monthly Consumption Tracker</h1>", unsafe_allow_html=True)

# --- Sidebar controls ---
st.sidebar.header("📅 Month Selection")
month = st.sidebar.text_input("Enter Month and Year (e.g., August 2025):", "August 2025")
file_path = os.path.join(DATA_DIR, f"{month.replace(' ', '_')}.csv")

# --- Table columns ---
columns = [
    "No.",
    "Name",
    "Old Meter",
    "New Meter",
    "Units Used",
    "Rate",
    "Total",
    "Amount Paid",
    "Balance"
]

# --- Load or create data ---
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    st.success(f"✅ Loaded data for {month}")
else:
    df = pd.DataFrame(columns=columns)
    st.info(f"🆕 No data found for {month}. Start entering new readings below.")

# --- Editable Table ---
st.subheader(f"📋 {month} Table")
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="data_editor")

# --- Auto-calculate Units Used & Total ---
try:
    if not edited_df.empty:
        edited_df["Units Used"] = (
            edited_df["New Meter"].astype(float) - edited_df["Old Meter"].astype(float)
        )
        edited_df["Total"] = (
            edited_df["Units Used"].astype(float) * edited_df["Rate"].astype(float)
        )
except Exception:
    st.warning("⚠️ Make sure 'Old Meter', 'New Meter', and 'Rate' contain valid numbers.")

# --- Total Sales ---
total_sales = edited_df["Total"].sum() if "Total" in edited_df.columns else 0
st.metric(label="💰 Total Monthly Sales", value=f"{total_sales:,.2f}")

# --- Sidebar buttons ---
st.sidebar.markdown("---")
save_btn = st.sidebar.button("💾 Save Data")
new_btn = st.sidebar.button("🆕 New Month")
compare_btn = st.sidebar.button("📈 Compare Months")

# --- Fix for session_state error ---
if "data_editor" not in st.session_state:
    st.session_state["data_editor"] = pd.DataFrame(columns=columns)

# --- Save Data ---
if save_btn:
    edited_df.to_csv(file_path, index=False)
    st.success(f"✅ Data saved for {month}!")

# --- Create New Month ---
if new_btn:
    st.session_state["data_editor"] = pd.DataFrame(columns=columns)
    st.experimental_rerun()

# --- Compare all months ---
if compare_btn:
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    summary = []
    for f in files:
        m = f.replace("_", " ").replace(".csv", "")
        data = pd.read_csv(os.path.join(DATA_DIR, f))
        total = data["Total"].astype(float).sum() if "Total" in data.columns else 0
        summary.append({"Month": m, "Total": total})

    if summary:
        summary_df = pd.DataFrame(summary).sort_values("Month")
        st.subheader("📊 Monthly Comparison Summary")
        st.dataframe(summary_df, use_container_width=True)
        st.bar_chart(summary_df.set_index("Month"))
    else:
        st.info("ℹ️ No saved months available for comparison.")

# --- Footer ---
st.markdown("<p style='text-align:center;color:gray;'>Created by Eudes 💧 | Powered by Streamlit</p>", unsafe_allow_html=True)


