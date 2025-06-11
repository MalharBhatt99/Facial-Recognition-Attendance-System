# launcher.py

import streamlit as st
import subprocess

st.set_page_config(page_title="Select Role", layout="centered")
st.title("📚 Welcome to the Attendance System")

role = st.selectbox("Choose your role:", ["Select", "Admin", "Student"])

if role == "Admin":
    st.success("Launching Admin Login...")
    subprocess.Popen(["streamlit", "run", "admin_login.py"])
    st.stop()

elif role == "Student":
    st.success("Launching Student Dashboard...")
    subprocess.Popen(["streamlit", "run", "student_dashboard.py"])
    st.stop()
