# recognize_from_video.py

import cv2
import pickle
import os
import csv
import numpy as np
from datetime import datetime
from insightface.app import FaceAnalysis
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# ==== CONFIGURATION ====
encoding_file = "encodings/face_encodings.pickle"
attendance_file = "attendance_from_video.csv"
frame_skip = 12
resize_scale = 0.5
tolerance = 0.85  # Euclidean distance threshold

# ==== CLI Input for Video/Camera ====
print("📷 Choose input source:")
print("1. Webcam")
print("2. Video File")
choice = input("Enter 1 or 2: ").strip()

if choice == '1':
    video_source = 0  # Webcam
elif choice == '2':
    video_path = input("Enter video file path (default: test_clip.mp4): ").strip()
    video_path = video_path.strip('"').strip("'")  # Remove quotes
    video_source = video_path if video_path else "test_clip.mp4"
else:
    print("[ERROR] Invalid choice. Exiting.")
    exit()

# ==== LOAD ENCODINGS ====
with open(encoding_file, "rb") as f:
    data = pickle.load(f)

known_encodings = np.array(data["encodings"])
known_names = data["metadata"]

# ==== INIT INSIGHTFACE ====
face_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
face_app.prepare(ctx_id=0)

# ==== VIDEO CAPTURE ====
cap = cv2.VideoCapture(video_source)
if not cap.isOpened():
    print("[ERROR] Could not open video source.")
    exit()

seen_names = set()
frame_count = 0

# ==== ATTENDANCE SETUP ====
if not os.path.exists(attendance_file):
    with open(attendance_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Time"])

# ==== MAIN LOOP ====
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % frame_skip != 0:
        continue

    # Resize for speed
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

        # Attendance marking
        if name != "Unknown" and name not in seen_names:
            seen_names.add(name)
            print(f"[✓] Marked Present: {name}")
            with open(attendance_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

        # Draw bounding box and name (scaled back up to original frame size)
        x1, y1, x2, y2 = face.bbox.astype(int)
        x1 = int(x1 / resize_scale)
        y1 = int(y1 / resize_scale)
        x2 = int(x2 / resize_scale)
        y2 = int(y2 / resize_scale)

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0) if name != "Unknown" else (0, 0, 255), 2)

    # Show video
    cv2.imshow("Live Feed - Press Q to Quit", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ==== CLEANUP ====
cap.release()
cv2.destroyAllWindows()
print("✅ Attendance processing complete.")
