# Complete robust version: replace your current app file with this
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

# ---------------- STYLES ----------------
st.markdown("""
<style>
.glass-card {
    background: rgba(255,255,255,0.92);
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>💧 Monthly Consumption Tracker</h1>", unsafe_allow_html=True)

# ---------------- DATA DIR ----------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- COLUMNS ----------------
COLUMNS = [
    "No.", "Name", "Current", "Previous", "New Meter",
    "1st Total", "Rate", "2nd Total", "Amount Paid", "Balance"
]

# ---------------- SESSION DEFAULTS ----------------
if "current_file" not in st.session_state:
    st.session_state["current_file"] = None
if "df_loaded" not in st.session_state:
    st.session_state["df_loaded"] = None

# ---------------- SAFE RERUN HELPER ----------------
def safe_rerun():
    try:
        st.experimental_rerun()
    except Exception:
        # fallback: set flag and stop
        st.session_state["_needs_refresh"] = True
        st.stop()

# ---------------- SIDEBAR: month input ----------------
# We control the sidebar month text via session so Load can set it
if "sidebar_month" not in st.session_state:
    st.session_state["sidebar_month"] = "August 2025"

month_input = st.sidebar.text_input(
    "Enter Month and Year (e.g., August 2025):",
    value=st.session_state["sidebar_month"],
    key="month_input"
)

# When user types a month and it's different, update current_file and clear loaded df
if month_input != st.session_state.get("sidebar_month"):
    st.session_state["sidebar_month"] = month_input
    # update current file path but don't overwrite loaded_df unless file exists
    if month_input.strip() == "":
        st.session_state["current_file"] = None
    else:
        st.session_state["current_file"] = os.path.join(DATA_DIR, f"{month_input.replace(' ', '_')}.csv")
    # clear df_loaded only if the file does not match
    if not (st.session_state["current_file"] and os.path.exists(st.session_state["current_file"])):
        st.session_state["df_loaded"] = None

# ---------------- SELECT WHICH dataframe to show in editor ----------------
def load_df_for_editor():
    # Priority:
    # 1) if df_loaded in session and current_file matches loaded_from => use it
    # 2) else if file exists for current_file => read file
    # 3) else empty df with columns
    cur = st.session_state.get("current_file")
    if st.session_state.get("df_loaded") is not None:
        return st.session_state["df_loaded"]
    if cur and os.path.exists(cur):
        try:
            df = pd.read_csv(cur)
            # ensure columns consistent
            for c in COLUMNS:
                if c not in df.columns:
                    df[c] = ""
            return df[COLUMNS]
        except Exception:
            # corrupted file fallback
            return pd.DataFrame(columns=COLUMNS)
    # default blank
    return pd.DataFrame(columns=COLUMNS)

df = load_df_for_editor()

# ---------------- MAIN EDITOR ----------------
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.subheader(f"📋 {month_input or 'New Month'} Consumption Table")
editor_key = f"editor_{(st.session_state.get('current_file') or 'blank').replace('/', '_')}"
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key=editor_key)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------- CALCULATIONS ----------------
def recalc(df_in):
    if df_in is None or df_in.empty:
        return df_in
    try:
        for col in ["Current", "Previous", "New Meter", "Rate", "Amount Paid"]:
            if col in df_in.columns:
                df_in[col] = pd.to_numeric(df_in[col], errors="coerce").fillna(0)
            else:
                df_in[col] = 0
        # Compute totals
        df_in["1st Total"] = df_in["Current"] - df_in["Previous"]
        df_in["2nd Total"] = df_in["1st Total"] * df_in["Rate"]
        df_in["Balance"] = df_in["2nd Total"] - df_in["Amount Paid"]
        # Keep only desired column order (and convert to numeric where appropriate)
        for c in ["1st Total", "2nd Total", "Balance"]:
            df_in[c] = pd.to_numeric(df_in[c], errors="coerce").fillna(0)
    except Exception:
        st.warning("⚠️ Could not calculate totals (check numeric fields).")
    return df_in

edited_df = recalc(edited_df)

# ---------------- SHOW METRIC ----------------
if "2nd Total" in edited_df.columns and not edited_df.empty:
    st.metric("💰 Total Monthly Sales", f"{edited_df['2nd Total'].sum():,.2f}")

# ---------------- SIDEBAR BUTTONS ----------------
st.sidebar.markdown("---")
save_btn = st.sidebar.button("💾 Save Data")
new_btn = st.sidebar.button("🆕 New Month")
show_saved_btn = st.sidebar.button("📂 Show Saved Months")

# ---------------- SAVE LOGIC ----------------
if save_btn:
    # ensure we have a month name
    if not st.session_state.get("sidebar_month"):
        st.error("⚠️ Please enter a month name in the sidebar before saving.")
    else:
        cur = st.session_state["current_file"]
        # if no current_file path (empty month), set from sidebar_month
        if not cur:
            cur = os.path.join(DATA_DIR, f"{st.session_state['sidebar_month'].replace(' ', '_')}.csv")
            st.session_state["current_file"] = cur
        # write file: convert dataframe to CSV (force all columns present)
        try:
            save_df = edited_df.copy()
            for c in COLUMNS:
                if c not in save_df.columns:
                    save_df[c] = ""
            save_df = save_df[COLUMNS]
            os.makedirs(DATA_DIR, exist_ok=True)
            save_df.to_csv(cur, index=False)
            # mark loaded_df so that after save editor shows same
            st.session_state["df_loaded"] = save_df
            st.session_state["loaded_from"] = cur
            st.success(f"✅ Data saved to {os.path.basename(cur)}")
        except Exception as e:
            st.error(f"Failed to save file: {e}")

# ---------------- NEW MONTH ----------------
if new_btn:
    # clear session keys that control editor or loaded data
    for k in list(st.session_state.keys()):
        if k.startswith("editor_") or k in ("df_loaded", "loaded_from", "current_file"):
            del st.session_state[k]
    # prepare an empty dataframe in session and clear month input
    st.session_state["df_loaded"] = pd.DataFrame(columns=COLUMNS)
    st.session_state["current_file"] = None
    st.session_state["sidebar_month"] = ""
    # rerun safely
    safe_rerun()

# ---------------- SHOW AND LOAD SAVED MONTHS ----------------
if show_saved_btn:
    saved_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".csv")])
    if not saved_files:
        st.info("ℹ️ No saved months found yet.")
    else:
        st.subheader("📂 Saved Months")
        display_names = [f.replace("_", " ").replace(".csv", "") for f in saved_files]
        selected_display = st.selectbox("Select a month to load:", options=display_names)
        if st.button("Load Selected"):
            # map display to filename
            idx = display_names.index(selected_display)
            chosen_file = saved_files[idx]
            chosen_path = os.path.join(DATA_DIR, chosen_file)
            try:
                df_loaded = pd.read_csv(chosen_path)
            except Exception:
                df_loaded = pd.DataFrame(columns=COLUMNS)
            # set session state so editor will show this df
            st.session_state["df_loaded"] = df_loaded
            st.session_state["loaded_from"] = chosen_path
            # set sidebar month text to loaded name
            st.session_state["sidebar_month"] = selected_display
            st.session_state["current_file"] = chosen_path
            safe_rerun()

# ---------------- If we have loaded_df set from earlier, show a small note ---------------
if st.session_state.get("df_loaded") is not None and st.session_state.get("loaded_from"):
    st.info(f"Loaded file: {os.path.basename(st.session_state['loaded_from'])} — you can edit and Save.")

# ---------------- FOOTER ----------------
st.markdown("<p style='text-align:center;color:white;'>Created by Eudes 💧 | Powered by Streamlit</p>", unsafe_allow_html=True)





