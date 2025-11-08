import streamlit as st
import pandas as pd
import os
import base64

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="💧 Company Water Tracker", layout="wide")

# ---------------------------------------------------------
# BACKGROUND IMAGE OR GRADIENT
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
            .stApp {{
                background: linear-gradient(135deg, #0078D7, #00C9A7);
                background-size: cover;
            }}
            </style>
            """
        st.markdown(css, unsafe_allow_html=True)
    except Exception:
        st.markdown("""
        <style>
        .stApp {{
            background: linear-gradient(135deg, #0078D7, #00C9A7);
        }}
        </style>
        """, unsafe_allow_html=True)

set_background("background/bg.jpg")

# ---------------------------------------------------------
# STYLES
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

st.markdown("<h1 style='text-align:center; color:white;'>💧 Company Water Consumption Tracker</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# DIRECTORY SETUP
# ---------------------------------------------------------
BASE_DIR = "data"
os.makedirs(BASE_DIR, exist_ok=True)

# ---------------------------------------------------------
# SIDEBAR: COMPANY AND MONTH
# ---------------------------------------------------------
st.sidebar.header("🏢 Company Selection")

# Company name
company_name = st.sidebar.text_input("Enter or select company name (e.g., Kitengela, Ebenezer):", "Kitengela")
company_dir = os.path.join(BASE_DIR, company_name)
os.makedirs(company_dir, exist_ok=True)

st.sidebar.markdown("---")
month = st.sidebar.text_input("Enter Month and Year (e.g., August 2025):", "August 2025")
file_path = os.path.join(company_dir, f"{month.replace(' ', '_')}.csv")

# ---------------------------------------------------------
# TABLE COLUMNS
# ---------------------------------------------------------
columns = ["No.", "Name", "Old Meter", "New Meter", "Units Used", "Rate", "Total", "Amount Paid", "Balance"]

# ---------------------------------------------------------
# LOAD OR CREATE DATA
# ---------------------------------------------------------
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    st.success(f"✅ Loaded data for {company_name} - {month}")
else:
    df = pd.DataFrame(columns=columns)
    st.info(f"🆕 No data found for {company_name} in {month}. Start entering readings below.")

# ---------------------------------------------------------
# MAIN TABLE
# ---------------------------------------------------------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.subheader(f"📋 {company_name} - {month} Consumption Table")

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    key=f"editor_{company_name}_{month}"
)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# SAFE AUTO CALCULATIONS
# ---------------------------------------------------------
if not edited_df.empty:
    try:
        for col in ["Old Meter", "New Meter", "Rate", "Amount Paid"]:
            edited_df[col] = pd.to_numeric(edited_df[col], errors="coerce").fillna(0)

        edited_df["Units Used"] = edited_df["New Meter"] - edited_df["Old Meter"]
        edited_df["Total"] = edited_df["Units Used"] * edited_df["Rate"]
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
new_month_btn = st.sidebar.button("🆕 New Month")
compare_btn = st.sidebar.button("📈 Compare Months (Company)")

# ---------------------------------------------------------
# SAVE DATA
# ---------------------------------------------------------
if save_btn:
    edited_df.to_csv(file_path, index=False)
    st.success(f"✅ Saved successfully for {company_name} - {month}")

# ---------------------------------------------------------
# CREATE NEW MONTH
# ---------------------------------------------------------
if new_month_btn:
    st.session_state.pop(f"editor_{company_name}_{month}", None)
    new_month = st.sidebar.text_input("Enter new month (e.g., September 2025):", "")
    if new_month:
        new_file = os.path.join(company_dir, f"{new_month.replace(' ', '_')}.csv")
        pd.DataFrame(columns=columns).to_csv(new_file, index=False)
        st.success(f"🆕 Created new month file for {company_name} - {new_month}.")
        st.rerun()

# ---------------------------------------------------------
# COMPARE MONTHS FOR SAME COMPANY
# ---------------------------------------------------------
if compare_btn:
    months = []
    for f in os.listdir(company_dir):
        if f.endswith(".csv"):
            m = f.replace("_", " ").replace(".csv", "")
            t = pd.read_csv(os.path.join(company_dir, f))["Total"].sum()
            months.append({"Month": m, "Total": t})

    if months:
        st.subheader(f"📊 Monthly Comparison for {company_name}")
        compare_df = pd.DataFrame(months).sort_values("Month")
        st.dataframe(compare_df, use_container_width=True)
        st.bar_chart(compare_df.set_index("Month"))
    else:
        st.info("ℹ️ No saved months available for comparison.")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("<p style='text-align:center;color:white;'>Created by Eudes 💧 | Powered by Streamlit</p>", unsafe_allow_html=True)
