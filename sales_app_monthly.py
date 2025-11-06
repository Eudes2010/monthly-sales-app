# sales_app_monthly.py
import streamlit as st
import pandas as pd
import os
from io import BytesIO

st.set_page_config(page_title="Monthly Consumption / Sales Tracker", layout="wide")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

st.title("📋 Monthly Consumption / Sales Tracker")

# Helper: month key format
def month_key(year: int, month: int):
    return f"{month:02d}-{year}"

# Default table structure
def default_dataframe():
    cols = [
        "Name",
        "Current",       # numeric
        "Previous",      # numeric
        "NewMeter",      # numeric (if any)
        "Consumption",   # auto: Current - Previous + NewMeter (if NewMeter > 0)
        "UnitRate",      # unit price
        "Amount",        # auto: Consumption * UnitRate
        "AmountPaid",    # numeric
        "Balance"        # auto: Amount - AmountPaid
    ]
    # create an empty DataFrame with one blank row
    df = pd.DataFrame([["", 0.0, 0.0, 0.0, 0.0, 135.0, 0.0, 0.0, 0.0]], columns=cols)
    return df

def compute_columns(df: pd.DataFrame) -> pd.DataFrame:
    # ensure numeric columns exist
    for c in ["Current", "Previous", "NewMeter", "UnitRate", "AmountPaid"]:
        if c not in df.columns:
            df[c] = 0.0
    # calculate Consumption
    df["Consumption"] = (pd.to_numeric(df["Current"], errors="coerce").fillna(0)
                         - pd.to_numeric(df["Previous"], errors="coerce").fillna(0)
                         + pd.to_numeric(df["NewMeter"], errors="coerce").fillna(0))
    # ensure non-negative consumption
    df["Consumption"] = df["Consumption"].astype(float).round(3)
    # Amount
    df["UnitRate"] = pd.to_numeric(df["UnitRate"], errors="coerce").fillna(0.0)
    df["Amount"] = (df["Consumption"] * df["UnitRate"]).round(2)
    # AmountPaid numeric
    df["AmountPaid"] = pd.to_numeric(df["AmountPaid"], errors="coerce").fillna(0.0)
    # Balance
    df["Balance"] = (df["Amount"] - df["AmountPaid"]).round(2)
    # keep order
    cols = ["Name", "Current", "Previous", "NewMeter", "Consumption", "UnitRate", "Amount", "AmountPaid", "Balance"]
    return df[cols]

def month_filepath(key: str) -> str:
    safe = key.replace("/", "-")
    return os.path.join(DATA_DIR, f"{safe}.csv")

def save_month(key: str, df: pd.DataFrame):
    path = month_filepath(key)
    df.to_csv(path, index=False)

def load_month(key: str) -> pd.DataFrame:
    path = month_filepath(key)
    if os.path.exists(path):
        df = pd.read_csv(path)
        return compute_columns(df)
    return default_dataframe()

def list_saved_months():
    files = []
    if os.path.exists(DATA_DIR):
        for f in os.listdir(DATA_DIR):
            if f.endswith(".csv"):
                nm = f[:-4]
                files.append(nm)
    return sorted(files)

# Sidebar for controls
st.sidebar.header("Month Controls")
col1, col2 = st.sidebar.columns(2)
with col1:
    sel_year = st.sidebar.number_input("Year", min_value=2000, max_value=2100, value=2025, step=1)
with col2:
    sel_month = st.sidebar.number_input("Month (1-12)", min_value=1, max_value=12, value=8, step=1)

month_key_str = month_key(sel_year, sel_month)
st.sidebar.write("Selected month:", f"**{month_key_str}**")

# Buttons for actions
 btn_col1, btn_col2, btn_col3 = st.sidebar.columns([1,1,1])
if btn_col1.button("Load month"):
    st.session_state["df"] = load_month(month_key_str)
    st.success(f"Loaded {month_key_str}")

if btn_col2.button("New month (blank)"):
    st.session_state["df"] = default_dataframe()
    st.success("Created new blank table (not yet saved).")

if btn_col3.button("Save month"):
    df_to_save = compute_columns(st.session_state.get("df", default_dataframe()))
    save_month(month_key_str, df_to_save)
    st.success(f"Saved month {month_key_str} to {month_filepath(month_key_str)}")

# Initialize session state df if missing
if "df" not in st.session_state:
    st.session_state["df"] = load_month(month_key_str) if month_key_str in list_saved_months() else default_dataframe()

# Main area: editable table
st.subheader(f"Editable table — {month_key_str}")
st.write("Edit names and numeric values directly. Consumption, Amount and Balance are calculated automatically.")

# Use Streamlit data editor (editable)
edited = st.data_editor(st.session_state["df"], num_rows="dynamic", use_container_width=True)

# Compute columns from edited
computed = compute_columns(edited)
st.session_state["df"] = computed  # store back

# Show totals
totals_col1, totals_col2, totals_col3 = st.columns(3)
total_consumption = computed["Consumption"].sum()
total_amount = computed["Amount"].sum()
total_balance = computed["Balance"].sum()
totals_col1.metric("Total Consumption", f"{total_consumption:.2f}")
totals_col2.metric("Total Amount", f"Ksh {total_amount:.2f}")
totals_col3.metric("Total Balance", f"Ksh {total_balance:.2f}")

# Buttons row under table
b1, b2, b3 = st.columns([1,1,1])
with b1:
    if st.button("Save current table (overwrite)"):
        save_month(month_key_str, computed)
        st.success(f"Saved {month_key_str}")

with b2:
    if st.button("Download CSV"):
        to_download = computed.to_csv(index=False).encode("utf-8")
        st.download_button("Download this month's CSV", data=to_download, file_name=f"{month_key_str}.csv", mime="text/csv")

with b3:
    if st.button("Add blank row"):
        new_row = pd.DataFrame([["", 0.0, 0.0, 0.0, 0.0, 135.0, 0.0, 0.0, 0.0]], columns=computed.columns)
        st.session_state["df"] = pd.concat([computed, new_row], ignore_index=True)
        st.experimental_rerun()

st.markdown("---")
# Comparison
st.subheader("Compare months")
saved = list_saved_months()
if not saved:
    st.info("No saved months yet. Save a month to enable comparison.")
else:
    c1, c2 = st.columns(2)
    with c1:
        m1 = st.selectbox("Month A", options=saved, index=0)
    with c2:
        m2 = st.selectbox("Month B", options=saved, index=min(1, len(saved)-1))
    if st.button("Compare Totals"):
        df1 = compute_columns(pd.read_csv(month_filepath(m1)))
        df2 = compute_columns(pd.read_csv(month_filepath(m2)))
        s1 = df1["Amount"].sum()
        s2 = df2["Amount"].sum()
        st.write(f"**{m1} Total Amount:** Ksh {s1:.2f}")
        st.write(f"**{m2} Total Amount:** Ksh {s2:.2f}")
        comp = pd.DataFrame({
            "Month": [m1, m2],
            "TotalConsumption": [df1["Consumption"].sum(), df2["Consumption"].sum()],
            "TotalAmount": [s1, s2],
            "TotalBalance": [df1["Balance"].sum(), df2["Balance"].sum()]
        })
        st.dataframe(comp.style.format({"TotalConsumption":"{:.2f}", "TotalAmount":"Ksh {:.2f}", "TotalBalance":"Ksh {:.2f}"}), height=220)
