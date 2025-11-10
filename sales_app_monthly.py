import streamlit as st
import pandas as pd
import os
import base64

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="💧 Monthly Consumption Tracker", layout="wide")

# ---------------- BACKGROUND (safe) ----------------
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
    background: rgba(255,255,255,0.9);
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
}
.sidebar-title { font-size:1.1rem; font-weight:bold; color:#00C9A7; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>💧 Monthly Consumption Tracker</h1>", unsafe_allow_html=True)

# ---------------- DATA DIR ----------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------- SIDEBAR MENU ----------------
st.sidebar.markdown("<p class='sidebar-title'>🏠 Main Menu</p>", unsafe_allow_html=True)
menu = st.sidebar.radio("Navigate:", ["🏡 Home", "📋 Manage Data", "💾 Saved Files", "📊 Compare Months", "ℹ️ About App"], index=1)

# ---------------- COMMONS ----------------
COLUMNS = ["No.", "Name", "Current", "Old Meter", "New Meter", "1st Total", "Rate", "2nd Total", "Amount Paid", "Balance"]

# ---------------- HOME ----------------
if menu == "🏡 Home":
    # try safe image load, fallback to text if missing
    image_path = "background/businessman.jpg"
    if os.path.exists(image_path):
        try:
            st.image(image_path, use_column_width=True)
        except Exception:
            st.write("Welcome — image could not be displayed but the app is working.")
    else:
        # show a simple welcoming glass card if no image
        st.markdown("""
        <div class="glass-card">
            <h2>Welcome 👋</h2>
            <p>This is the Monthly Water Consumption Tracker.</p>
            <p>Use the left menu to manage data, open saved files, compare months or learn about the app.</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------- MANAGE DATA ----------------
elif menu == "📋 Manage Data":
    st.sidebar.markdown("---")
    company = st.sidebar.text_input("Company Name:", value="Kitengela")
    month = st.sidebar.text_input("Month & Year (e.g., August 2025):", value="August 2025")

    file_name = f"{company}_{month.replace(' ', '_')}.csv"
    file_path = os.path.join(DATA_DIR, file_name)

    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            st.success(f"✅ Loaded existing data for {company} - {month}")
        except Exception:
            df = pd.DataFrame(columns=COLUMNS)
            st.warning("File exists but couldn't be read cleanly; starting a fresh table.")
    else:
        df = pd.DataFrame(columns=COLUMNS)
        st.info(f"🆕 No existing data for {company} - {month}. Start entering new data.")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader(f"📋 {company} — {month} Data Table")
    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, key=f"manage_{company}_{month}")
    st.markdown("</div>", unsafe_allow_html=True)

    # calculations
    if not edited.empty:
        for c in ["Current", "Old Meter", "New Meter", "Rate", "Amount Paid"]:
            edited[c] = pd.to_numeric(edited[c], errors="coerce").fillna(0)
        edited["1st Total"] = edited["Current"] - edited["Old Meter"]
        edited["2nd Total"] = edited["1st Total"] * edited["Rate"]
        edited["Balance"] = edited["2nd Total"] - edited["Amount Paid"]

        st.metric("💰 Total Monthly Sales", f"{edited['2nd Total'].sum():,.2f}")

    # Save + New Month buttons in sidebar (always visible here)
    st.sidebar.markdown("---")
    if st.sidebar.button("💾 Save File"):
        try:
            # ensure columns present and ordered
            for c in COLUMNS:
                if c not in edited.columns:
                    edited[c] = ""
            save_df = edited[COLUMNS]
            save_df.to_csv(file_path, index=False)
            st.success(f"✅ File saved: {file_name}")
        except Exception as e:
            st.error(f"Save failed: {e}")

    if st.sidebar.button("🆕 New Month"):
        # create blank dataframe and set sidebar fields to empty so user enters new month
        st.session_state[f"blank_{company}"] = pd.DataFrame(columns=COLUMNS)
        st.success("🆕 New blank month created — enter month name and start filling.")
        st.experimental_rerun()

# ---------------- SAVED FILES ----------------
elif menu == "💾 Saved Files":
    st.subheader("📂 Saved Files")
    files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".csv")])
    if not files:
        st.info("No saved files found yet.")
    else:
        selected = st.selectbox("Select a saved file to open:", files)
        if st.button("📂 Open File"):
            path = os.path.join(DATA_DIR, selected)
            try:
                loaded = pd.read_csv(path)
            except Exception:
                loaded = pd.DataFrame(columns=COLUMNS)
            # show editable view and Save button below it
            st.success(f"✅ Opened file: {selected}")
            edited_saved = st.data_editor(loaded, num_rows="dynamic", use_container_width=True, key=f"saved_{selected}")

            # recalc on saved editor
            if not edited_saved.empty:
                for c in ["Current", "Old Meter", "New Meter", "Rate", "Amount Paid"]:
                    edited_saved[c] = pd.to_numeric(edited_saved[c], errors="coerce").fillna(0)
                edited_saved["1st Total"] = edited_saved["Current"] - edited_saved["Old Meter"]
                edited_saved["2nd Total"] = edited_saved["1st Total"] * edited_saved["Rate"]
                edited_saved["Balance"] = edited_saved["2nd Total"] - edited_saved["Amount Paid"]

                st.metric("💰 Total Monthly Sales", f"{edited_saved['2nd Total'].sum():,.2f}")

            # Save button for the opened saved file
            if st.button("💾 Save Changes to Opened File"):
                try:
                    for c in COLUMNS:
                        if c not in edited_saved.columns:
                            edited_saved[c] = ""
                    edited_saved[COLUMNS].to_csv(path, index=False)
                    st.success(f"✅ Saved changes to {selected}")
                except Exception as e:
                    st.error(f"Save failed: {e}")

# ---------------- COMPARE MONTHS ----------------
elif menu == "📊 Compare Months":
    st.subheader("📊 Compare Saved Months")
    files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".csv")])
    if len(files) < 2:
        st.warning("You need at least 2 saved months to compare.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            f1 = st.selectbox("Select First Month", files, key="cmp1")
        with c2:
            f2 = st.selectbox("Select Second Month", files, key="cmp2")
        if st.button("🔍 Compare Now"):
            df1 = pd.read_csv(os.path.join(DATA_DIR, f1))
            df2 = pd.read_csv(os.path.join(DATA_DIR, f2))
            t1 = df1.get("2nd Total", pd.Series(dtype=float)).sum()
            t2 = df2.get("2nd Total", pd.Series(dtype=float)).sum()
            diff = t2 - t1
            st.write(f"💧 **{f1}:** {t1:,.2f}")
            st.write(f"💧 **{f2}:** {t2:,.2f}")
            st.write(f"📈 **Change:** {diff:,.2f}")
            st.bar_chart(pd.DataFrame({"Month":[f1,f2],"Total Sales":[t1,t2]}).set_index("Month"))

# ---------------- ABOUT ----------------
elif menu == "ℹ️ About App":
    st.markdown("""
    <div class='glass-card'>
        <h2>About This App</h2>
        <p>Monthly Water Consumption Tracker — created by Eudes. Use Manage Data to create/edit files, Saved Files to open older files, and Compare to analyze.</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("<p style='text-align:center;color:white;'>Created by Eudes 💧 | Business Dashboard Edition</p>", unsafe_allow_html=True)









