# generate_encodings.py

import cv2
import pandas as pd
import pickle
import os
from insightface.app import FaceAnalysis
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Set dataset path
dataset_dir = "dataset"
csv_path = os.path.join(dataset_dir, "students_fixed.csv")

# Load student data
students_df = pd.read_csv(csv_path)

# Initialize InsightFace
face_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
face_app.prepare(ctx_id=0)

known_encodings = []
known_metadata = []

for idx, row in students_df.iterrows():
    img_path = row['image_path']
    full_img_path = os.path.join(dataset_dir, os.path.basename(img_path))

    if not os.path.exists(full_img_path):
        print(f"[!] Image not found: {full_img_path}")
        continue

    image = cv2.imread(full_img_path)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    faces = face_app.get(rgb)
    if faces:
        # Align face properly before getting embedding
        face = faces[0]
        face_embedding = face.normed_embedding
    if not faces:
        print(f"[x] No face found in: {img_path}")
        continue

    embedding = faces[0].normed_embedding
    known_encodings.append(embedding)
    known_metadata.append({
        "name": row['name'],
        "roll_no": row['roll_no'],
        "semester": row['semester'],
        "branch": row['branch'],
        "section": row['section']
    })

    print(f"[✓] Encoded: {row['name']} ({row['roll_no']})")

# Save encodings
output_dir = "encodings"
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "face_encodings.pickle"), "wb") as f:
    pickle.dump({
        "encodings": known_encodings,
        "metadata": known_metadata
    }, f)

print("\n✅ Encodings saved to: encodings/face_encodings.pickle")
