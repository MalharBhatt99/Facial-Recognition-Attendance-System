# controller.py
import cv2
import pandas as pd
import pickle
import os
from datetime import datetime
import csv
import numpy as np
from insightface.app import FaceAnalysis
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# CONFIG
ENCODING_DIR = "split_encodings"
ATTENDANCE_DIR = "attendance_logs"
TIMETABLE_CSV = "timetable.csv"
CAMERA_MAP_CSV = "camera_mapping.csv"
TOLERANCE = 0.85
FRAME_SKIP = 8
RESIZE_SCALE = 0.5

os.makedirs(ATTENDANCE_DIR, exist_ok=True)

# CURRENT TIME
now = datetime.now()
current_day = now.strftime("%A")
current_time = now.strftime("%H:%M")
print(f"[INFO] Day: {current_day}, Time: {current_time}")

# LOAD TIMETABLE
df = pd.read_csv(TIMETABLE_CSV)
df['start_time'] = pd.to_datetime(df['start_time'], format='%H:%M').dt.strftime('%H:%M')
df['end_time'] = pd.to_datetime(df['end_time'], format='%H:%M').dt.strftime('%H:%M')

current_class = df[
    (df['day'] == current_day) &
    (df['start_time'] <= current_time) &
    (df['end_time'] > current_time)
]

if current_class.empty:
    print("[INFO] No class is scheduled right now.")
    exit()

# CAMERA MAP
camera_df = pd.read_csv(CAMERA_MAP_CSV)

# INIT INSIGHTFACE
face_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
face_app.prepare(ctx_id=0)

# PROCESS EACH ACTIVE CLASSROOM
for _, row in current_class.iterrows():
    classroom = row['classroom']
    branch = row['branch']
    semester = row['semester']
    section = row['section']
    subject = row['subject']
    start_time = row['start_time']
    end_time = row['end_time']

    encoding_file = os.path.join(ENCODING_DIR, f"{branch}_{semester}.pickle")
    if not os.path.exists(encoding_file):
        print(f"[WARNING] Encoding file not found for {branch}_{semester}")
        continue

    camera_url = camera_df.loc[camera_df['class_id'] == classroom, 'camera_url'].values
    if len(camera_url) == 0:
        print(f"[WARNING] Camera not mapped for {classroom}")
        continue
    camera_url = camera_url[0]

    print(f"\n[INFO] 🔍 Starting attendance for {branch}-{semester}-{section} in {classroom}")
    print(f"[INFO] 🎥 Using camera: {camera_url}")

    # Load Encodings
    with open(encoding_file, 'rb') as f:
        data = pickle.load(f)
    known_encodings = np.array(data['encodings'])
    print(f"[DEBUG] Loaded {len(known_encodings)} encodings of shape {known_encodings[0].shape if len(known_encodings) else 'N/A'}")

    known_names = data['metadata']

    seen_names = set()
    cap = cv2.VideoCapture(camera_url)
    frame_count = 0

    if not cap.isOpened():
        print(f"[ERROR] Could not open camera: {camera_url}")
        continue

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % FRAME_SKIP != 0:
            continue

        small_frame = cv2.resize(frame, (0, 0), fx=RESIZE_SCALE, fy=RESIZE_SCALE)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        faces = face_app.get(rgb_frame)
        #####for checking the detection of faces
        # print(f"[DEBUG] Detected {len(faces)} faces")

        for face in faces:
            embedding = face.normed_embedding
            dists = np.linalg.norm(known_encodings - embedding, axis=1)
            min_dist = np.min(dists)
            # print(f"[DEBUG] Min distance: {min_dist}")
            min_idx = np.argmin(dists)

            name = "Unknown"
            if min_dist < TOLERANCE:
                name = known_names[min_idx]['name']

            if name != "Unknown" and name not in seen_names:
                seen_names.add(name)
                print(f"[✓] Marked Present: {name}")

                # Create path and filename
                date_str = now.strftime("%Y-%m-%d")
                start_time_safe = start_time.replace(":", "_")
                end_time_safe = end_time.replace(":", "_")
                filename = f"{branch}-{semester}-{section}-{subject}-{start_time_safe}-{end_time_safe}-{date_str}.csv"

                # Create folder structure
                branch_path = os.path.join(ATTENDANCE_DIR, branch)
                semester_path = os.path.join(branch_path, str(semester))
                os.makedirs(semester_path, exist_ok=True)

                attendance_path = os.path.join(semester_path, filename)
                print(f"[DEBUG] Writing to: {attendance_path}")

                write_header = not os.path.exists(attendance_path)
                with open(attendance_path, 'a', newline='') as f:
                    writer = csv.writer(f)
                    if write_header:
                        writer.writerow(["Name", "Time", "Branch", "Semester", "Section", "Classroom"])
                    writer.writerow([name, now.strftime("%H:%M:%S"), branch, semester, section, classroom])

        if len(seen_names) >= 5:
            break  # demo stop

    cap.release()
    print(f"✅ Attendance saved for {branch}-{semester}-{section}.")

print("✅ All active classrooms processed.")
