import numpy as np
from PIL import Image, ImageDraw
from moviepy.editor import ImageSequenceClip
import ast

# Parameters
width, height = 500, 500
scale = 20  # Scaling for coordinates to fit the canvas
roundabout_center = (0, 0)
inner_radius = 3  # Inner radius of the roundabout
outer_radius = 6  # Outer radius of the roundabout
num_frames = 200  # Total number of frames
prediction_horizon = 50  # Number of points to predict
initial_distance_threshold = 2.0  # Threshold for initial position filtering
dynamic_distance_threshold = 3.0  # Threshold for real-time filtering

def to_canvas_coords(point):
    """Converts simulation coordinates to canvas coordinates."""
    return int(width / 2 + point[0] * scale), int(height / 2 - point[1] * scale)

def euclidean_distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Read trajectories and speeds from data.txt
trajectories = []
with open('data_with_noise.txt', 'r') as file:
    for line in file:
        # Parse trajectory
        obj_data = line.strip().split(" -> ")
        trajectory = ast.literal_eval(obj_data[1].split(" (speed:")[0])
        trajectories.append(trajectory)

# Set the first trajectory as the test trajectory
test_trajectory = trajectories[0]
observed_trajectory = []

# Filter trajectories by initial position
initial_position = test_trajectory[0]
filtered_trajectories = [
    traj for traj in trajectories[1:]  # Exclude the test trajectory
    if euclidean_distance(traj[0], initial_position) <= initial_distance_threshold
]

# Create frames for the video
frames = []

for frame_idx in range(num_frames):
    # Add the current point to the observed trajectory
    if frame_idx < len(test_trajectory):
        observed_trajectory.append(test_trajectory[frame_idx])  # Simulate observations for the test trajectory
    
    # Further filter trajectories dynamically based on the current position
    current_position = observed_trajectory[-1]
    filtered_trajectories = [
        traj for traj in filtered_trajectories
        if frame_idx < len(traj) and euclidean_distance(traj[frame_idx], current_position) <= dynamic_distance_threshold
    ]
    
    # Match observed trajectory with the most similar trajectory from the filtered set
    most_similar_trajectory = None
    min_distance = float('inf')
    for traj in filtered_trajectories:
        if frame_idx < len(traj):
            distance = euclidean_distance(current_position, traj[frame_idx])
            if distance < min_distance:
                min_distance = distance
                most_similar_trajectory = traj
    
    # Predict future positions based on the matched trajectory
    predicted_points = []
    if most_similar_trajectory:
        start_idx = frame_idx + 1
        end_idx = min(start_idx + prediction_horizon, len(most_similar_trajectory))
        predicted_points = most_similar_trajectory[start_idx:end_idx]

    # Visualization with PIL
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    
    # Draw the roundabout (inner and outer circles)
    center = to_canvas_coords(roundabout_center)
    inner_radius_scaled = inner_radius * scale
    outer_radius_scaled = outer_radius * scale
    draw.ellipse(
        [center[0] - outer_radius_scaled, center[1] - outer_radius_scaled,
         center[0] + outer_radius_scaled, center[1] + outer_radius_scaled],
        outline="black", width=2
    )
    draw.ellipse(
        [center[0] - inner_radius_scaled, center[1] - inner_radius_scaled,
         center[0] + inner_radius_scaled, center[1] + inner_radius_scaled],
        outline="black", width=2
    )
    
    # Draw the observed trajectory in blue
    for point in observed_trajectory:
        pos = to_canvas_coords(point)
        draw.ellipse([pos[0] - 3, pos[1] - 3, pos[0] + 3, pos[1] + 3], fill="blue")
    
    # Draw the predicted points in red
    for point in predicted_points:
        pos = to_canvas_coords(point)
        draw.ellipse([pos[0] - 3, pos[1] - 3, pos[0] + 3, pos[1] + 3], fill="red")
    
    # Append the frame to the list
    frames.append(np.array(img))

# Save the animation as a video
clip = ImageSequenceClip(frames, fps=30)
clip.write_videofile("prediction_video_position_filtered.mp4", codec="libx264")
