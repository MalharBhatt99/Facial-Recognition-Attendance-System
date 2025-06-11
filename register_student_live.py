import cv2
import os
import csv
import pickle
import numpy as np
import streamlit as st
from insightface.app import FaceAnalysis
import subprocess
import sys

DATASET_DIR = "dataset"
CSV_FILE = os.path.join(DATASET_DIR, "students_fixed.csv")
ENCODING_FILE = "encodings/face_encodings.pickle"

os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs("encodings", exist_ok=True)

def capture_student_image_gui(filename, video_source=0):
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        st.error("[ERROR] Cannot access camera.")
        return None

    st.info("📷 Showing camera. Press 's' to capture. Press 'q' to cancel.")
    image_path = os.path.join(DATASET_DIR, filename)

    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("[ERROR] Failed to grab frame.")
            break

        cv2.imshow("Capture Student Face", frame)
        key = cv2.waitKey(1)

        if key & 0xFF == ord('s'):
            cv2.imwrite(image_path, frame)
            st.success(f"[✓] Image saved: {image_path}")
            cap.release()
            cv2.destroyAllWindows()
            return image_path

        elif key & 0xFF == ord('q'):
            st.warning("[INFO] Registration cancelled.")
            cap.release()
            cv2.destroyAllWindows()
            return None

def extract_embedding(image_path):
    face_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    face_app.prepare(ctx_id=0)

    image = cv2.imread(image_path)
    if image is None:
        st.error(f"[ERROR] Failed to load image at {image_path}")
        return None

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    faces = face_app.get(rgb)

    if not faces:
        st.error("[ERROR] No face found in captured image.")
        return None

    return faces[0].normed_embedding

def trigger_split_encodings():
    script_path = os.path.join(os.path.dirname(__file__), "split_encodings.py")
    if not os.path.exists(script_path):
        st.warning("❌ split_encodings.py not found.")
        return
    try:
        st.info("⚙️ Running split_encodings.py...")
        subprocess.run([sys.executable, script_path], check=True)
        st.success("✅ split_encodings.py executed successfully.")
        return True

    except subprocess.CalledProcessError as e:
        st.error(f"❌ Failed to run split_encodings.py: {e}")
        return

def register_student_details(roll_no,name,semester,branch,section,image_path):
    csv_path = os.path.join(DATASET_DIR, "students_fixed.csv")
    write_header = not os.path.exists(csv_path)
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["roll_no", "name", "semester", "branch", "section", "image_path"])
        writer.writerow([roll_no, name, semester, branch, section, image_path])
    st.success("[✓] Student info saved to CSV.")

def register_student_gui(roll_no,name,semester,branch,section):
    st.subheader("📝 Register a New Student")

    filename = f"{roll_no}_{name.replace(' ', '_')}.jpg"

    ##image_capturing starts here
    image_path = capture_student_image_gui(filename)
    if image_path is None:
        st.warning("❌ Registration aborted. Image is required.")
        return

    embedding = extract_embedding(image_path)
    if embedding is None:
        st.warning("❌ Registration aborted. Face not detected.")
        os.remove(image_path)
        return

    if os.path.exists(ENCODING_FILE):
        with open(ENCODING_FILE, "rb") as f:
            data = pickle.load(f)
        data["encodings"].append(embedding)
        data["metadata"].append({
            "name": name,
            "roll_no": roll_no,
            "semester": semester,
            "branch": branch,
            "section": section
        })
    else:
        data = {
            "encodings": [embedding],
            "metadata": [{
                "name": name,
                "roll_no": roll_no,
                "semester": semester,
                "branch": branch,
                "section": section
            }]
        }

    with open(ENCODING_FILE, "wb") as f:
        pickle.dump(data, f)

    st.success("✅ Embedding added.")
    result = trigger_split_encodings()
    if result is True:
        register_student_details(roll_no,name,semester,branch,section,image_path)
        return True
    else :
        return False

