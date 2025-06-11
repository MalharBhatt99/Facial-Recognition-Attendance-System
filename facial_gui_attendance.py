import os
import cv2
import csv
import time
import pickle
import subprocess
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime
import  controller as run_attendance
from insightface.app import FaceAnalysis

import recognize_and_mark_attendance as live_attendance
import register_student_live as new_student_registration_live
import register_student_image as new_student_registration_image

start = time.time()

st.set_page_config("Face Recognition Attendance System", layout="wide")
st.title("📸 Face Recognition Attendance Dashboard")

# Globals
face_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
face_app.prepare(ctx_id=0)

dataset_dir = "dataset"
os.makedirs(dataset_dir, exist_ok=True)
#
# # Camera-based Registration (from register_student_live.py)
# def capture_student_image(filename, video_source=0):
#     cap = cv2.VideoCapture(video_source)
#     if not cap.isOpened():
#         st.error("[ERROR] Cannot access camera.")
#         return None
#
#     st.info("Showing camera. Press 's' to capture, 'q' to cancel.")
#     image_path = os.path.join(dataset_dir, filename)
#
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             st.error("[ERROR] Failed to grab frame.")
#             break
#
#         cv2.imshow("Capture Student Face", frame)
#         key = cv2.waitKey(1)
#
#         if key & 0xFF == ord('s'):
#             cv2.imwrite(image_path, frame)
#             cap.release()
#             cv2.destroyAllWindows()
#             return image_path
#
#         elif key & 0xFF == ord('q'):
#             cap.release()
#             cv2.destroyAllWindows()
#             return None
#
# def extract_embedding(image_path):
#     face_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
#     face_app.prepare(ctx_id=0)
#
#     image = cv2.imread(image_path)
#     if image is None:
#         print(f"[ERROR] Failed to load image at {image_path}")
#         return None
#
#     rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     faces = face_app.get(rgb)
#
#     if not faces:
#         print("[ERROR] No face found in captured image.")
#         return None
#
#     return faces[0].normed_embedding
#
#
# def trigger_split_encodings():
#     script_path = os.path.join(os.path.dirname(__file__), "split_encodings.py")
#     if not os.path.exists(script_path):
#         st.warning("split_encodings.py not found.")
#         return
#     try:
#         subprocess.run(["python", script_path], check=True)
#         st.success("Encodings split successfully.")
#     except subprocess.CalledProcessError as e:
#         st.error(f"Failed to run split_encodings.py: {e}")
#
# def register_student_camera(name, roll_no, semester, branch, section):
#     filename = f"{roll_no}_{name.replace(' ', '_')}.jpg"
#     image_path = capture_student_image(filename)
#     if image_path is None:
#         st.warning("Registration cancelled.")
#         return False
#
#     embedding = extract_embedding(image_path)
#     if embedding is None:
#         st.error("No face detected. Try again.")
#         os.remove(image_path)
#         return False


#     os.makedirs("encodings", exist_ok=True)
#     enc_path = "encodings/face_encodings.pickle"
#     if os.path.exists(enc_path):
#         with open(enc_path, "rb") as f:
#             data = pickle.load(f)
#     else:
#         data = {"encodings": [], "metadata": []}
#
#     data["encodings"].append(embedding)
#     data["metadata"].append({
#         "name": name,
#         "roll_no": roll_no,
#         "semester": semester,
#         "branch": branch,
#         "section": section
#     })
#
#     with open(enc_path, "wb") as f:
#         pickle.dump(data, f)
#
#     trigger_split_encodings()
#     return True

# UI Tabs
tabs = st.tabs(["Register Student", "Run Attendance", "View Logs"])

with tabs[0]:
    st.header("Register New Student")
    with st.form("register_form"):
        name = st.text_input("Name").strip().capitalize()
        roll = st.text_input("Roll No").strip()
        sem = st.selectbox("Semester", list(range(1, 9)))
        branch = st.selectbox("Branch", ["CE", "CSE", "IT", "ECE"])
        section = st.selectbox("Section", ["A", "B"])
        st.form_submit_button("Submit")


    mode = st.radio("Registration Mode", ["Upload Image", "Use Camera"])
    ###reegister_student_image.py starts from here
    if mode == "Upload Image":
        image = st.file_uploader("Upload Face Image", type=["jpg", "png"])
        if image:
           result = new_student_registration_image.register_student_image_gui(roll, name, sem, branch, section, image)


    ###register_student_live.py starts from here
    elif mode == "Use Camera":
        result = new_student_registration_live.register_student_gui(roll,name, sem, branch, section)
    if st.button("Register Now"):
        if all([roll,name, sem, branch, section ,result]):
            st.success("Student successfully registered!")
        else:
            st.warning("Please fill all required fields.")

# with tabs[1]:
#     st.header("Generate Face Encodings")
#     if st.button("Generate Encodings"):
#         if generate_encodings():
#             st.success("Encodings generated successfully")
#         else:
#             st.error("Student CSV not found")
#
# with tabs[2]:
#     st.header("Split Encodings")
#     if st.button("Split Now"):
#         if split_encodings():
#             st.success("Encodings split by branch and semester")

with tabs[1]:
    st.header("Run Real-time Attendance")
    mode = st.radio("Select Attendance Mode", ["Video File", "Live Camera"])
    if mode == "Video File":
        #Video File mode: controller.py
        result =  run_attendance.mark_attendance()
    elif mode == "Live Camera":
        # Live Camera mode: run recognize_and_mark_attendance.py
        result = live_attendance.live_recognition_and_attendance()
        if result.returncode == 0:
            st.success("Attendance via Live Camera completed.")
        else:
            st.error(f"Error: {result.stderr}")


with tabs[2]:
    st.header("Attendance Logs")
    ATTENDANCE_DIR = "attendance_logs"
    if os.path.exists(ATTENDANCE_DIR):
        for branch in sorted(os.listdir(ATTENDANCE_DIR)):
            branch_path = os.path.join(ATTENDANCE_DIR, branch)
            if not os.path.isdir(branch_path):
                continue
            for sem in sorted(os.listdir(branch_path)):
                sem_path = os.path.join(branch_path, sem)
                if not os.path.isdir(sem_path):
                    continue
                st.subheader(f"{branch} - Semester {sem}")
                for file in sorted(os.listdir(sem_path)):
                    if not file.endswith(".csv"):
                        continue
                    file_path = os.path.join(sem_path, file)
                    st.markdown(f"**📄 {file}**")
                    try:
                        df = pd.read_csv(file_path)
                        st.dataframe(df)
                    except Exception as e:
                        st.error(f"Failed to load {file}: {e}")
    else:
        st.info("No logs found.")

# ... your code ...

end = time.time()
print("⏱ Duration:", end - start, "seconds")
