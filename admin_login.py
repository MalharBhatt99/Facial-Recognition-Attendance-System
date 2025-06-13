# admin_login.py

import streamlit as st
import subprocess
import os

# Admin credentials
VALID_ADMINS = {
    "admin": "admin123",
    "teacher": "teachme"
}

st.set_page_config(page_title="Admin Login", layout="centered")
st.title("🧑‍💼 Admin Login")

with st.form("admin_login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.form_submit_button("Login")

if login_button:
    if username in VALID_ADMINS and password == VALID_ADMINS[username]:
        st.success("✅ Login successful!")
        st.info("Launching Admin Dashboard...")

        try:
            subprocess.Popen(["streamlit", "run", "facial_gui_attendance.py"])
            st.stop()
        except Exception as e:
            st.error(f"Failed to launch admin GUI: {e}")
    else:
        st.error("❌ Invalid admin credentials.")
