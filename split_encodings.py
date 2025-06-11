import os
import pickle
from collections import defaultdict
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Load the combined encoding file
with open("encodings/face_encodings.pickle", "rb") as f:
    data = pickle.load(f)

# Group by branch and semester
grouped = defaultdict(lambda: {"encodings": [], "metadata": []})

for encoding, meta in zip(data["encodings"], data["metadata"]):
    key = f"{meta['branch']}_{meta['semester']}"
    grouped[key]["encodings"].append(encoding)
    grouped[key]["metadata"].append(meta)

# Create an output directory
os.makedirs("split_encodings", exist_ok=True)

# Save separate pickle files
for key, value in grouped.items():
    with open(f"split_encodings/{key}.pickle", "wb") as f:
        pickle.dump(value, f)

print("✅ Encoding files saved in 'split_encodings/' folder.")
