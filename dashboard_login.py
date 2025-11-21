import streamlit as st
from utils.auth import login, logout, is_logged_in, get_current_user, require_login

st.set_page_config(page_title="WCA Procurement & PFM Dashboard", layout="wide")

# Initialize auth session state
if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "user": None}

# ---------- LOGIN PAGE ----------
if not is_logged_in():
    st.title("WCA Procurement & PFM Dashboard - Login")
    st.markdown("Please sign in to access the dashboard.")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Sign in"):
        ok, msg = login(username, password)
        if ok:
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error(msg)
    st.info("Demo credentials: username `admin`, password `pwd123`")
    st.stop()

# ---------- AUTHENTICATED CONTENT ----------
user = get_current_user()
st.sidebar.markdown(f"**Signed in as:** {user}")
if st.sidebar.button("Sign out"):
    logout()
    st.rerun()

st.title("West & Central Africa - Procurement & PFM Dashboard")
st.markdown("""
This interactive dashboard helps analyze procurement cycles, PFM and QA for HTM commodities across selected Francophone WCA countries.
Use the left sidebar to navigate pages. You can:
- Generate country two-pagers (DOCX and PDF)
- Export comparison tables
""")
st.caption("Dummy data is used in this demo version.")
