import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime

DATASET_DIR = "dataset"
CSV_FILE = os.path.join(DATASET_DIR, "students_fixed.csv")

st.set_page_config("🎓 Student Attendance Dashboard", layout="wide")
st.title("🎓 Student Login & Dashboard")

# ------------------------- Helper Functions -------------------------
def pie_chart(attended, missed):
    fig, ax = plt.subplots()
    ax.pie(
        [attended, missed],
        labels=["Present", "Absent"],
        autopct='%1.1f%%',
        startangle=90,
        colors=["green", "red"]
    )
    ax.axis("equal")
    return fig

def load_students():
    students_path = "dataset/students_fixed.csv"
    if os.path.exists(students_path):
        df = pd.read_csv(students_path, dtype={'roll_no': str})  # force roll_no as string
        df['roll_no'] = df['roll_no'].str.zfill(5)  # pad with zeros if needed
        return df
    return pd.DataFrame()


def validate_student(roll, password, df):
    if 'roll_no' in df.columns:
        df['roll_no'] = df['roll_no'].astype(str).str.zfill(5)
        roll = str(roll).strip().zfill(5)
        match = df[df['roll_no'] == roll]
        if not match.empty:
            expected_password = roll[-4:] if len(roll) >= 4 else ""
            return password == expected_password
    return False


def get_attendance_logs(roll_no):
    # Load student name from CSV
    students_df = load_students()
    students_df['roll_no'] = students_df['roll_no'].astype(str).str.zfill(5)
    roll_no = roll_no.zfill(5)

    student_row = students_df[students_df['roll_no'] == roll_no]
    if student_row.empty:
        return pd.DataFrame()

    student_name = student_row.iloc[0]['name']

    found_logs = []
    for root, _, files in os.walk("attendance_logs"):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)
                    if 'Name' in df.columns:
                        matches = df[df["Name"].str.contains(student_name, case=False, na=False)]
                        if not matches.empty:
                            # Extract date from filename and add as a new column
                            date_str = file.split("-")[-1].replace(".csv", "")
                            matches["date"] = date_str
                            found_logs.append(matches)
                except Exception as e:
                    print(f"[WARN] Skipped file {file_path}: {e}")
                    continue
    if found_logs:
        return pd.concat(found_logs, ignore_index=True)
    return pd.DataFrame()


# ------------------------- Login Form -------------------------
with st.form("student_login"):
    roll_no = st.text_input("🎓 Roll Number")
    password = st.text_input("🔐 Password", type="password")
    submitted = st.form_submit_button("Login")

if submitted:
    students_df = load_students()

    if validate_student(roll_no, password, students_df):
        st.success("✅ Login successful!")
        logs_df = get_attendance_logs(roll_no)

        if logs_df.empty:
            st.warning("No attendance records found.")
        else:
            # Convert and preprocess
            logs_df["date"] = pd.to_datetime(logs_df["date"], errors="coerce")
            logs_df["day"] = logs_df["date"].dt.strftime('%A')

            # Filters
            st.subheader("📌 Filter Your Attendance")
            col1, col2 = st.columns(2)
            with col1:
                selected_subject = st.selectbox("Subject", ["All"] + sorted(logs_df["Classroom"].unique()))
            with col2:
                date_range = st.date_input("Filter by Date Range", [])

            filtered = logs_df.copy()

            if selected_subject != "All":
                filtered = filtered[filtered["Classroom"] == selected_subject]
            if len(date_range) == 2:
                start, end = date_range
                filtered = filtered[(filtered["date"] >= pd.to_datetime(start)) & (filtered["date"] <= pd.to_datetime(end))]

            st.subheader("📋 Your Attendance Logs")
            st.dataframe(filtered, use_container_width=True)

            # Download
            csv_data = filtered.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", csv_data, file_name=f"{roll_no}_attendance.csv", mime="text/csv")

            # Charts in two columns
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📅 Weekly Attendance")
                day_summary = filtered["day"].value_counts().sort_index()
                st.bar_chart(day_summary)

            with col2:
                st.subheader("📊 Attendance %")
                total_classes = 30  # Adjust as needed
                attended = len(filtered)
                missed = max(total_classes - attended, 0)
                st.pyplot(pie_chart(attended, missed))


    else:
        st.error("❌ Invalid credentials. Hint: Password is last 4 digits of your roll number (for demo).")
