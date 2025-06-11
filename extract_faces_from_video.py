import cv2
import os
import time

# --------- CONFIGURABLE SETTINGS ----------
person_id = "4_Umang"
save_dir = f"dataset/{person_id}"
video_source = "http://192.168.1.8:4747/video"
  # Default webcam; for DroidCam use: "http://192.168.0.101:4747/video"
face_count_target = 3
# ------------------------------------------

os.makedirs(save_dir, exist_ok=True)

cap = cv2.VideoCapture(video_source)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

face_saved = 0
frame_skip = 0

print(f"[INFO] Starting face capture for: {person_id}")
print("[INFO] Press 'q' to quit early.\n")

while face_saved < face_count_target:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Camera not accessible.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)

    for (x, y, w, h) in faces:
        if frame_skip % 5 == 0:  # Save every 5th detected face (avoid duplicates)
            face_img = frame[y:y + h, x:x + w]
            filename = os.path.join(save_dir, f"{face_saved + 1}.jpg")
            cv2.imwrite(filename, face_img)
            face_saved += 1
            print(f"[✓] Saved: {filename}")
            time.sleep(1)  # Pause to give user time to change pose

        # Draw rectangle for user feedback
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    frame_skip += 1
    cv2.imshow("Live Capture (Press 'q' to exit)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(f"\n✅ Face capture complete. Total saved: {face_saved}")
