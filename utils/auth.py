import streamlit as st
import hashlib

# WARNING: This is a simple demo auth. For production use OAuth or a secure auth provider.

CREDENTIALS = {
    # username: password  (change here)
    "admin": "pwd123",
    "analyst": "analystpass"
}

# -----------------------
# Hash function (optional)
# -----------------------
def _hash(s: str):
    return hashlib.sha256(s.encode()).hexdigest()

# -----------------------
# LOGIN / LOGOUT
# -----------------------
def login(username: str, password: str):
    if username in CREDENTIALS and CREDENTIALS[username] == password:
        st.session_state.auth = {"logged_in": True, "user": username}
        return True, "ok"
    return False, "Invalid username or password."

def logout():
    st.session_state.auth = {"logged_in": False, "user": None}

# -----------------------
# SESSION CHECKS
# -----------------------
def is_logged_in():
    return st.session_state.get("auth", {}).get("logged_in", False)

def get_current_user():
    return st.session_state.get("auth", {}).get("user", "unknown")

# -----------------------
# PAGE PROTECTION
# -----------------------
def require_login():
    """
    Call this at the top of any page to block unauthorized access.
    Stops execution if the user is not logged in.
    """
    if not is_logged_in():
        st.warning("⚠️ You must log in to access this page.")
        st.stop()
