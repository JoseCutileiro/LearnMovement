import ast
from PIL import Image, ImageDraw
from moviepy.editor import ImageSequenceClip
import numpy as np

# Parameters
width, height = 500, 500  # Canvas dimensions
scale = 20  # Scaling factor for coordinates
roundabout_center = (0, 0)  # Center of the roundabout
inner_radius = 3  # Inner radius of the roundabout
outer_radius = 6  # Outer radius of the roundabout

# Load trajectories from data.txt
trajectories = []
with open("data_with_noise.txt", "r") as file:
    for line in file:
        # Parse the trajectory from the file
        _, trajectory_data = line.split("->")
        trajectory_str, _ = trajectory_data.split("(speed:")  # Ignore speed
        trajectory = ast.literal_eval(trajectory_str.strip())
        trajectories.append(trajectory)

# Visualization with PIL
frames = []

def to_canvas_coords(point):
    """Converts simulation coordinates to canvas coordinates."""
    return int(width / 2 + point[0] * scale), int(height / 2 - point[1] * scale)

# Find the maximum number of frames across all trajectories
max_frames = max(len(trajectory) for trajectory in trajectories)

for frame_idx in range(max_frames):
    # Create a blank image
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
    
    # Draw all objects up to the current frame
    for trajectory in trajectories:
        if frame_idx < len(trajectory):
            pos = to_canvas_coords(trajectory[frame_idx])
            draw.ellipse([pos[0] - 3, pos[1] - 3, pos[0] + 3, pos[1] + 3], fill="blue")
    
    # Append the frame
    frames.append(np.array(img))

# Save the animation as replicated.mp4 using moviepy
clip = ImageSequenceClip(frames, fps=30)
clip.write_videofile("replicated.mp4", codec="libx264")
