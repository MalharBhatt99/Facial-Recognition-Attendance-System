# recognize_from_video.py

import cv2
import pickle
import os
import csv
import numpy as np
from datetime import datetime
from insightface.app import FaceAnalysis
import subprocess
import streamlit as st
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

def live_recognition_and_attendance():
    # Live Camera mode: rewritten recognize_and_mark_attendance.py for GUI
    # Inside the else block for Live Camera mode
    ...  # previous unchanged code

    # Live Camera mode: rewritten recognize_and_mark_attendance.py for GUI
    st.subheader("📡 Running Live Camera Attendance")

    encoding_file = "encodings/face_encodings.pickle"
    attendance_file = "attendance_from_video.csv"
    frame_skip = 12
    resize_scale = 0.5
    tolerance = 0.85

    if not os.path.exists(encoding_file):
        st.error("Encoding file not found.")
    else:
        with open(encoding_file, "rb") as f:
            data = pickle.load(f)

        known_encodings = np.array(data["encodings"])
        known_names = data["metadata"]

        face_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        face_app.prepare(ctx_id=0)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Could not open webcam.")
        else:
            seen_names = set()
            frame_count = 0

            if not os.path.exists(attendance_file):
                with open(attendance_file, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Name", "Time"])

            status_box = st.empty()
            stframe = st.container()

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1
                if frame_count % frame_skip != 0:
                    continue

                small_frame = cv2.resize(frame, (0, 0), fx=resize_scale, fy=resize_scale)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                faces = face_app.get(rgb_small_frame)

                for face in faces:
                    embedding = face.normed_embedding
                    dists = np.linalg.norm(known_encodings - embedding, axis=1)
                    min_dist = np.min(dists)
                    min_idx = np.argmin(dists)

                    name = "Unknown"
                    if min_dist < tolerance:
                        name = known_names[min_idx]["name"]

                    if name != "Unknown" and name not in seen_names:
                        seen_names.add(name)
                        with open(attendance_file, "a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow([name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                        status_box.success(f"✓ Marked Present: {name}")

                    x1, y1, x2, y2 = face.bbox.astype(int)
                    x1 = int(x1 / resize_scale)
                    y1 = int(y1 / resize_scale)
                    x2 = int(x2 / resize_scale)
                    y2 = int(y2 / resize_scale)

                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                with stframe:
                    st.image(frame, channels="BGR", caption="📷 Live Camera Feed", width=400)

                if len(seen_names) >= 5:
                    break

            cap.release()
            st.success("✅ Attendance via Live Camera completed.")


# ==== CLEANUP ====
cv2.destroyAllWindows()
print("✅ Attendance processing complete.")
