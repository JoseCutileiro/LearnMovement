import cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import logging, sys
from tqdm import tqdm

# AVOID PRINTING YOLO OUTPUT
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)
logging.getLogger("ultralytics").setLevel(logging.WARNING)

# Initialize YOLO and DeepSort
model = YOLO("models/yolo11s.pt")  # Use the correct YOLO model path
tracker = DeepSort(max_age=100, n_init=2, nn_budget=200)

# Open the video file
video_path = "vid.mkv"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error: Unable to open video file {video_path}")
    sys.exit()

# Prepare the output file
output_file = "data.txt"
with open(output_file, "w") as f:
    f.write("")  # Clear the file content if it exists

frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
progress_bar = tqdm(total=frame_count, desc="Processing Frames")

# Store active trajectories in memory
active_trajectories = {}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    progress_bar.update(1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Perform object detection
    results = model(frame_rgb)
    
    # Extract bounding boxes and class names
    detections = []
    for result in results:
        for box, confidence, class_id in zip(result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
            x1, y1, x2, y2 = map(int, box.tolist())
            detections.append(((x1, y1, x2, y2), confidence.item(), int(class_id)))

    # Update tracker with YOLO detections
    tracks = tracker.update_tracks(detections, frame=frame_rgb)
    
    # Process tracking results
    lost_ids = set(active_trajectories.keys())  # Start by assuming all are lost
    for track in tracks:
        if not track.is_confirmed() or track.time_since_update > 0:
            continue

        track_id = track.track_id
        x1, y1, x2, y2 = map(int, track.to_tlbr())  # Convert to top-left and bottom-right coordinates
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # Center point

        # Label objects based on class IDs from YOLO detections
        class_id = track.get_det_class() if hasattr(track, 'get_det_class') else None
        label = f"car{track_id}" if class_id == 2 else f"person{track_id}"

        # Update trajectory
        if label not in active_trajectories:
            active_trajectories[label] = []

        active_trajectories[label].append((cx, cy))
        lost_ids.discard(label)  # This track is still active

    # Write trajectories for lost objects
    with open(output_file, "a") as f:
        for lost_id in lost_ids:
            trajectory = active_trajectories.pop(lost_id)
            trajectory_str = ", ".join([str(pos) if pos is not None else "None" for pos in trajectory])
            f.write(f"{lost_id} -> [{trajectory_str}]\n")

cap.release()
progress_bar.close()

# Write remaining trajectories
with open(output_file, "a") as f:
    for obj_id, trajectory in active_trajectories.items():
        trajectory_str = ", ".join([str(pos) if pos is not None else "None" for pos in trajectory])
        f.write(f"{obj_id} -> [{trajectory_str}]\n")

print("Trajectories saved to data.txt")
