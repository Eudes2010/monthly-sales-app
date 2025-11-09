import streamlit as st
import pandas as pd
import os
import base64

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="💧 Monthly Consumption Tracker", layout="wide")

# ---------------------------------------------------------
# BACKGROUND HANDLER
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

# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.markdown("<h1 style='text-align:center; color:white;'>💧 Monthly Consumption Tracker</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# FOLDER SETUP
# ---------------------------------------------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.header("📅 Month Selection")
month = st.sidebar.text_input("Enter Month and Year (e.g., August 2025):", "August 2025")
file_path = os.path.join(DATA_DIR, f"{month.replace(' ', '_')}.csv")

columns = [
    "No.", "Name", "Current", "Previous", "New Meter",
    "1st Total", "Rate", "2nd Total", "Amount Paid", "Balance"
]

# ---------------------------------------------------------
# LOAD OR CREATE MONTHLY DATA
# ---------------------------------------------------------
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    st.success(f"✅ Loaded data for {month}")
else:
    df = pd.DataFrame(columns=columns)
    st.info(f"🆕 No data for {month}. Start entering readings below.")

# ---------------------------------------------------------
# TABLE SECTION
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
# SAFE CALCULATIONS
# ---------------------------------------------------------
if not edited_df.empty:
    try:
        # Convert number fields safely
        for col in ["Current", "Previous", "New Meter", "Rate", "Amount Paid"]:
            edited_df[col] = pd.to_numeric(edited_df[col], errors="coerce").fillna(0)

        # First Total (Current - Previous)
        edited_df["1st Total"] = edited_df["Current"] - edited_df["Previous"]

        # Second Total (New Meter * Rate)
        edited_df["2nd Total"] = edited_df["1st Total"] * edited_df["Rate"]

        # Balance
        edited_df["Balance"] = edited_df["2nd Total"] - edited_df["Amount Paid"]

    except Exception as e:
        st.warning(f"⚠️ Could not calculate totals: {e}")

# ---------------------------------------------------------
# MONTH SUMMARY
# ---------------------------------------------------------
if not edited_df.empty:
    total_sales = edited_df["2nd Total"].sum()
    st.metric("💰 Total Monthly Sales", f"{total_sales:,.2f}")

# ---------------------------------------------------------
# BUTTONS
# ---------------------------------------------------------
st.sidebar.markdown("---")
save_btn = st.sidebar.button("💾 Save Data")
new_btn = st.sidebar.button("🆕 New Month")
show_saved_btn = st.sidebar.button("📂 Show Saved Months")

# Save
if save_btn:
    edited_df.to_csv(file_path, index=False)
    st.success(f"✅ Data saved for {month}")

# New month (safe, prevents AttributeError on experimental rerun)
def _safe_rerun():
    """
    Try to rerun the app using Streamlit's rerun.
    If rerun is not available in this environment, set a small flag
    and stop execution so the user can manually refresh.
    """
    try:
        # Preferred method
        st.experimental_rerun()
    except Exception:
        # Fallback if experimental_rerun is not present or raises an error.
        # We set a flag so the app knows a refresh is expected, then stop execution.
        st.session_state["_needs_refresh"] = True
        # st.stop() aborts the script safely (user can then refresh page).
        st.stop()

if new_btn:
    # Clear all session state keys safely
    for key in list(st.session_state.keys()):
        try:
            del st.session_state[key]
        except Exception:
            pass
    # Create a blank dataframe in session so the editor can attach a fresh table
    st.session_state["blank_df"] = pd.DataFrame(columns=columns)
    # Try to rerun safely (will fallback if rerun isn't available)
    _safe_rerun()

# If we landed here after a fallback, inform the user to refresh
if st.session_state.get("_needs_refresh", False):
    st.warning("🆕 New month prepared. Please refresh the page to continue (your blank table was created).")

# Show saved months
if show_saved_btn:
    st.subheader("📂 Saved Months")
    saved_files = [f.replace("_", " ").replace(".csv", "") for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    if saved_files:
        st.write("### Available Months:")
        for f in saved_files:
            st.markdown(f"- 📅 **{f}**")
    else:
        st.info("ℹ️ No saved months found yet.")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("<p style='text-align:center;color:white;'>Created by Eudes 💧 | Powered by Streamlit</p>", unsafe_allow_html=True)



