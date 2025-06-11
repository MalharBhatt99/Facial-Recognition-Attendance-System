import cv2
import os
import sys
import csv
import pickle
import numpy as np
from insightface.app import FaceAnalysis
import subprocess  # For triggering external script

DATASET_DIR = "dataset"
CSV_FILE = os.path.join(DATASET_DIR, "students_fixed.csv")
ENCODING_FILE = "encodings/face_encodings.pickle"

os.makedirs(DATASET_DIR, exist_ok=True)
os.makedirs("encodings", exist_ok=True)

def capture_student_image(filename, video_source=0):
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print("[ERROR] Cannot access camera.")
        return None

    print(f"\n[INFO] Showing camera. Press 's' to capture photo. Press 'q' to cancel registration.")
    image_path = os.path.join(DATASET_DIR, filename)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to grab frame.")
            break

        cv2.imshow("Capture Student Face", frame)
        key = cv2.waitKey(1)

        if key & 0xFF == ord('s'):
            cv2.imwrite(image_path, frame)
            print(f"[✓] Image saved: {image_path}")
            cap.release()
            cv2.destroyAllWindows()
            return image_path

        elif key & 0xFF == ord('q'):
            print("[INFO] Registration cancelled.")
            cap.release()
            cv2.destroyAllWindows()
            return None

def extract_embedding(image_path):
    face_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    face_app.prepare(ctx_id=0)

    image = cv2.imread(image_path)
    if image is None:
        print(f"[ERROR] Failed to load image at {image_path}")
        return None

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    faces = face_app.get(rgb)

    if not faces:
        print("[ERROR] No face found in captured image.")
        return None

    return faces[0].normed_embedding


def register_student():
    print("\n=== Student Registration ===")
    name = input("Name: ").strip().capitalize()
    roll_no = input("Roll Number: ").strip()
    semester = input("Semester: ").strip()
    branch = input("Branch: ").strip().upper()
    section = input("Section: ").strip().upper()

    # Define image filename
    filename = f"{roll_no}_{name.replace(' ', '_')}.jpg"

    # Capture image (required)
    image_path = capture_student_image(filename)
    if image_path is None:
        print("❌ Registration aborted. Image is required.")
        return

    # Extract embedding
    embedding = extract_embedding(image_path)
    if embedding is None:
        print("❌ Registration aborted. Face not detected.")
        os.remove(image_path)  # Clean up image
        return

    # Save student record to CSV
    write_header = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([ "roll_no","name", "semester", "branch", "section", "image_path"])
        writer.writerow([roll_no,name,  semester, branch, section, image_path])

    print(f"[✓] Student info saved to CSV.")

    # Append embedding to encoding file
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

    print("✅ Embedding added. Student successfully registered!\n")

    def trigger_split_encodings():
        script_path = os.path.join(os.path.dirname(__file__), "split_encodings.py")
        if not os.path.exists(script_path):
            print("❌ split_encodings.py not found.")
            return
        try:
            print("[⚙️] Running split_encodings.py...")
            subprocess.run([sys.executable, script_path], check=True)
            print("✅ split_encodings.py executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to run split_encodings.py: {e}")


    # Trigger split encoding script
    trigger_split_encodings()


# Run it directly from terminal
if __name__ == "__main__":
    register_student()

