import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="💧 Water Consumption Tracker", layout="wide")

st.title("💧 Water Consumption Tracker")

# ---------------------------------------------------------
# DATA DIRECTORY
# ---------------------------------------------------------
SAVE_DIR = "saved_months"
os.makedirs(SAVE_DIR, exist_ok=True)

# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=100)
menu = st.sidebar.radio(
    "📂 Navigation",
    ["🏠 Home", "🆕 New Month", "💾 Saved Files", "📊 Compare", "ℹ️ About"]
)

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
def create_empty_table():
    columns = ["No.", "Name", "Current", "Previous", "New Meter", "Total", "Rate", "Total Sales", "Amount Paid", "Balance"]
    return pd.DataFrame(columns=columns)

def calculate_totals(df):
    df = df.copy()
    try:
        # Keep "No." and "Name" as-is (text columns)
        numeric_cols = ["Current", "Previous", "New Meter", "Rate", "Amount Paid"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Auto calculations
        df["Total"] = df["New Meter"] - df["Previous"]
        df["Total Sales"] = df["Total"] * df["Rate"]
        df["Balance"] = df["Total Sales"] - df["Amount Paid"]

        # Recalculate row numbers
        df["No."] = range(1, len(df) + 1)

    except Exception as e:
        st.error(f"Error calculating totals: {e}")
    return df

def save_month_data(df, filename):
    filepath = os.path.join(SAVE_DIR, filename)
    df.to_csv(filepath, index=False)

def load_saved_files():
    return [f for f in os.listdir(SAVE_DIR) if f.endswith(".csv")]

def load_month_data(filename):
    filepath = os.path.join(SAVE_DIR, filename)
    return pd.read_csv(filepath)

# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------
if menu == "🏠 Home":
    st.markdown("""
        ### Welcome to the Water Consumption Tracker 💧  
        Track, compare, and analyze monthly water usage and costs.
        Use the sidebar to navigate between features.
    """)
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=400)

# ---------------------------------------------------------
# NEW MONTH PAGE
# ---------------------------------------------------------
elif menu == "🆕 New Month":
    st.subheader("🆕 Create a New Month Record")
    month_name = st.text_input("Enter Month Name (e.g. August 2025):")

    if "data" not in st.session_state:
        st.session_state["data"] = create_empty_table()

    st.write("### Enter Water Consumption Data Below")
    edited_df = st.data_editor(
        st.session_state["data"],
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="editable_table",
    )

    updated_df = calculate_totals(edited_df)
    st.dataframe(updated_df, use_container_width=True)

    if st.button("💾 Save Month Data"):
        if month_name.strip() == "":
            st.warning("⚠️ Please enter a valid month name before saving.")
        else:
            filename = f"{month_name.replace(' ', '_')}.csv"
            save_month_data(updated_df, filename)
            st.success(f"✅ Data saved successfully as {filename}")

# ---------------------------------------------------------
# SAVED FILES PAGE
# ---------------------------------------------------------
elif menu == "💾 Saved Files":
    st.subheader("📁 View and Edit Saved Files")

    files = load_saved_files()
    if not files:
        st.info("ℹ️ No saved files yet. Create a new month to get started.")
    else:
        selected_file = st.selectbox("Select a file to open:", files)
        df = load_month_data(selected_file)
        st.write(f"### Editing {selected_file}")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        edited_df = calculate_totals(edited_df)

        if st.button("💾 Save Changes"):
            save_month_data(edited_df, selected_file)
            st.success("✅ Changes saved successfully.")

        st.dataframe(edited_df, use_container_width=True)

# ---------------------------------------------------------
# COMPARE PAGE
# ---------------------------------------------------------
elif menu == "📊 Compare":
    st.subheader("📊 Compare Monthly Data")

    files = load_saved_files()
    if len(files) < 2:
        st.warning("⚠️ Please save at least two months to compare.")
    else:
        month1 = st.selectbox("Select first month:", files, key="month1")
        month2 = st.selectbox("Select second month:", files, key="month2")

        if st.button("Compare"):
            df1 = load_month_data(month1)
            df2 = load_month_data(month2)

            total1 = df1["Total Sales"].sum()
            total2 = df2["Total Sales"].sum()
            diff = total2 - total1

            st.write(f"💧 **{month1} Total Sales:** {total1:,.2f}")
            st.write(f"💧 **{month2} Total Sales:** {total2:,.2f}")
            st.write(f"📈 **Difference:** {diff:,.2f}")

# ---------------------------------------------------------
# ABOUT PAGE (with Contact Info)
# ---------------------------------------------------------
elif menu == "ℹ️ About":
    st.markdown("""
        ### ℹ️ About This App
        This water consumption tracker helps you manage and compare monthly usage.  
        You can save data for each month, open it again later, and see how totals change.  

        **Developed by:** Eudes Roy  
        **Version:** 4.1 — Added Contact Info & Column Fixes  
        **Purpose:** Simplify water usage tracking for Kitengela, Ebenezer, and more projects.  

        ---

        ### 📞 Contact Information
        - 📧 **Email:** eudesroy@example.com  
        - 📱 **Phone:** +254 700 123 456  
        - 🌐 **Website:** [www.eudesroyprojects.com](http://www.eudesroyprojects.com)  
        - 🏢 **Address:** Kitengela, Kajiado County, Kenya  

        ---

        💬 *Thank you for using the Water Consumption Tracker!*
    """)





