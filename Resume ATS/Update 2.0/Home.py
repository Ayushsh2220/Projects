import streamlit as st
import pandas as pd
from utils.db import get_resume_count, get_avg_match_score, init_db

# ✅ Set page config first
st.set_page_config(page_title="Resume Tracker Dashboard", layout="wide")

# ✅ Initialize database
init_db()

# 🧠 Session state defaults
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'role' not in st.session_state:
    st.session_state['role'] = None

# 🚪 Logout function
def logout():
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
    st.rerun()

# 🔐 Login screen
def login_screen():
    st.title("🔐 Welcome to Resume ATS Portal")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login = st.button("Login")

    if login:
        if username == "admin" and password == "admin123":
            st.session_state['logged_in'] = True
            st.session_state['role'] = "admin"
            st.success("✅ Logged in as Admin")
            st.rerun()
        elif username == "recruiter" and password == "recruiter123":
            st.session_state['logged_in'] = True
            st.session_state['role'] = "recruiter"
            st.success("✅ Logged in as Recruiter")
            st.rerun()
        else:
            st.error("❌ Invalid credentials")

# 🎯 Dashboard page
def dashboard_page():
    st.title("📊 ATS Dashboard Overview")

    total_resumes = get_resume_count()
    st.metric("📄 Total Resumes Uploaded", total_resumes)

    if st.session_state['role'] == "admin":
        avg_score = get_avg_match_score()
        st.metric("📈 Avg. BERT Match Score", f"{avg_score:.2f}" if avg_score else "N/A")
        st.success("🔧 Full access granted.")
    else:
        st.warning("👤 Recruiter access is limited.")

# 🛠 Upload Resume page
def upload_resume_page():
    st.title("📤 Upload Resumes")
    st.info("🚧 This page will be for uploading resumes (you can build this feature later).")

# 🛠 Admin Tools page
def admin_tools_page():
    st.title("🛠️ Admin Tools")

    if st.session_state['role'] != 'admin':
        st.error("⛔ Access denied. Admins only.")
        st.stop()

    st.success("✅ Welcome Admin!")
    st.info("Manage users, settings, and view advanced reports here.")

# ➡️ Main app flow
if not st.session_state['logged_in']:
    # If not logged in, show login screen
    login_screen()
else:
    # If logged in, show sidebar and page content
    with st.sidebar:
        st.header(f"👋 {st.session_state['role'].capitalize()} Menu")

        if st.session_state['role'] == "admin":
            menu_options = ["Dashboard", "Upload Resume", "Admin Tools"]
        else:
            menu_options = ["Dashboard", "Upload Resume"]  # Recruiter can't see Admin Tools

        choice = st.selectbox("Go to", menu_options)
        st.button("🚪 Logout", on_click=logout)

    # Page Content based on selection
    if choice == "Dashboard":
        dashboard_page()
    elif choice == "Upload Resume":
        upload_resume_page()
    elif choice == "Admin Tools":
        admin_tools_page()