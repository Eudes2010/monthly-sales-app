import streamlit as st
import pandas as pd
import os
import base64

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="💧 Monthly Consumption Tracker", layout="wide")

# ---------------- BACKGROUND (unchanged) ----------------
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

# ---------------- STYLES (unchanged) ----------------
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

st.markdown("<h1 style='text-align:center; color:white;'>💧 Monthly Consumption Tracker</h1>", unsafe_allow_html=True)

# ---------------- DATA DIRECTORY ----------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- SIDEBAR: month input (use session key so we can set it) ----------------
if "month" not in st.session_state:
    st.session_state["month"] = "August 2025"
month = st.sidebar.text_input("Enter Month and Year (e.g., August 2025):", value=st.session_state["month"], key="month")

file_path = os.path.join(DATA_DIR, f"{month.replace(' ', '_')}.csv")

# ---------------- COLUMNS (with Current and both totals) ----------------
columns = [
    "No.", "Name", "Current", "Previous", "New Meter",
    "1st Total", "Rate", "2nd Total", "Amount Paid", "Balance"
]

# ---------------- Helper: safe rerun ----------------
def _safe_rerun():
    try:
        st.experimental_rerun()
    except Exception:
        try:
            st.session_state["_needs_refresh"] = True
            st.stop()
        except Exception:
            # last resort: do nothing
            pass

# ---------------- Load dataframe: if a file was loaded via "Load saved month" use it ----------------
# If a loaded_df exists in session state (from pressing Load), use that instead of reading file_path.
if "loaded_df" in st.session_state and st.session_state.get("loaded_from") == f"{file_path}":
    df = st.session_state["loaded_df"]
else:
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
        except Exception:
            df = pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(columns=columns)

# ---------------- Main editable table ----------------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.subheader(f"📋 {month} Consumption Table")

# Use a stable key per month so editor state doesn't clash
editor_key = f"editor_{month.replace(' ', '_')}"
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key=editor_key)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Safe calculations ----------------
if not edited_df.empty:
    try:
        for col in ["Current", "Previous", "New Meter", "Rate", "Amount Paid"]:
            edited_df[col] = pd.to_numeric(edited_df[col], errors="coerce").fillna(0)

        edited_df["1st Total"] = edited_df["Current"] - edited_df["Previous"]
        edited_df["2nd Total"] = edited_df["1st Total"] * edited_df["Rate"]
        edited_df["Balance"] = edited_df["2nd Total"] - edited_df["Amount Paid"]
    except Exception as e:
        st.warning(f"⚠️ Could not calculate totals: {e}")

# ---------------- Month summary ----------------
if not edited_df.empty and "2nd Total" in edited_df.columns:
    total_sales = edited_df["2nd Total"].sum()
    st.metric("💰 Total Monthly Sales", f"{total_sales:,.2f}")

# ---------------- Sidebar buttons ----------------
st.sidebar.markdown("---")
save_btn = st.sidebar.button("💾 Save Data")
new_btn = st.sidebar.button("🆕 New Month")
show_saved_btn = st.sidebar.button("📂 Show Saved Months")

# --------------- Save logic (unchanged) ---------------
if save_btn:
    # ensure directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
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


# --------------- Show Saved Months and allow Loading ---------------
if show_saved_btn:
    saved_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".csv")])
    if not saved_files:
        st.info("ℹ️ No saved months found yet.")
    else:
        st.subheader("📂 Saved Months")
        # show a selectbox of saved files (display friendly names)
        display_names = [f.replace("_", " ").replace(".csv", "") for f in saved_files]
        selected_index = st.selectbox("Select a month to load:", options=list(range(len(display_names))),
                                      format_func=lambda i, names=display_names: names[i])
        col1, col2 = st.columns([3,1])
        with col2:
            if st.button("Load Selected"):
                chosen_file = saved_files[selected_index]
                chosen_path = os.path.join(DATA_DIR, chosen_file)
                try:
                    df_loaded = pd.read_csv(chosen_path)
                except Exception:
                    df_loaded = pd.DataFrame(columns=columns)
                # store loaded df and where it was loaded from, then set sidebar month to the loaded name
                st.session_state["loaded_df"] = df_loaded
                st.session_state["loaded_from"] = chosen_path
                # set the sidebar month text to the chosen name (without .csv)
                st.session_state["month"] = display_names[selected_index]
                _safe_rerun()

# If we loaded a file previously but the sidebar month doesn't match, keep the editor content consistent
if "loaded_df" in st.session_state and st.session_state.get("loaded_from"):
    # ensure editor shows loaded_df for that file
    # when the user edits and hits Save, code above will save to file_path computed from sidebar month
    pass

# If we prepared a blank_df after New Month, and the editor key is present, ensure editor shows blank
if "blank_df" in st.session_state and st.session_state["month"] == "":
    # replace editor content by showing blank_df — create a temporary editor key
    temp_key = "editor_blank"
    if temp_key not in st.session_state:
        st.session_state[temp_key] = True
    # display blank editor (this won't overwrite the main editor above but ensures a blank is ready after rerun)
    st.write("🆕 New month ready — please type the month name in the sidebar and begin entering data.")

# ---------------- Footer ----------------
st.markdown("<p style='text-align:center;color:white;'>Created by Eudes 💧 | Powered by Streamlit</p>", unsafe_allow_html=True)




