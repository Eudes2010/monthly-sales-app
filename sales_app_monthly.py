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

# ✅ Try loading background, if missing ➝ fallback to gradient
set_background("background/bg.jpg")

# ---------------------------------------------------------
# GLASS CARD STYLING
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
st.markdown("""
<h1 style='text-align:center; color:white;'>💧 Monthly Consumption Tracker</h1>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATA DIRECTORY
# ---------------------------------------------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.header("📅 Month Selection")
month = st.sidebar.text_input("Enter Month and Year (e.g., August 2025):", "August 2025")
file_path = os.path.join(DATA_DIR, f"{month.replace(' ', '_')}.csv")

columns = ["No.", "Name", "Old Meter", "New Meter", "Units Used", "Rate", "Total", "Amount Paid", "Balance"]

# Load or create dataframe
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    st.success(f"✅ Loaded data for {month}")
else:
    df = pd.DataFrame(columns=columns)
    st.info(f"🆕 No data for {month}. Start entering readings below.")

# ---------------------------------------------------------
# EDITABLE TABLE (inside glass card)
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
# AUTO CALCULATION
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
st.metric("💰 Total Monthly Sales", f"{edited_df['Total'].sum():,.2f}")

# ---------------------------------------------------------
# SIDEBAR BUTTONS
# ---------------------------------------------------------
st.sidebar.markdown("---")
save_btn = st.sidebar.button("💾 Save Data")
new_btn = st.sidebar.button("🆕 New Month")
compare_btn = st.sidebar.button("📈 Compare Months")

# Save data
if save_btn:
    edited_df.to_csv(file_path, index=False)
    st.success(f"✅ Saved successfully for {month}")

# New month
if new_btn:
    st.session_state.editor = pd.DataFrame(columns=columns)
    st.experimental_rerun()

# Compare months
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
        st.info("ℹ️ No saved months available for comparison.")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("<p style='text-align:center;color:white;'>Created by Eudes 💧 | Powered by Streamlit</p>", unsafe_allow_html=True)



