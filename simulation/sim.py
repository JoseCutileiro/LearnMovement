import numpy as np
import random
from PIL import Image, ImageDraw
from moviepy.editor import ImageSequenceClip

# Parameters
num_objects = 10000  # Number of objects
inner_radius = 3  # Inner radius of the roundabout
outer_radius = 6  # Outer radius of the roundabout
entry_points = [(10, 0), (0, 10), (-10, 0), (0, -10)]  # Four entry points
exit_angles_relative = [np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi]  # Relative exit angles
roundabout_center = (0, 0)
theta_step = np.pi / 60  # Angle step for smooth movement
exit_length = 30  # Linear movement distance after exiting
min_speed = 0.5  # Minimum speed (steps per frame)
max_speed = 1.5  # Maximum speed (steps per frame)

# Storage for trajectories and speeds
trajectories = []
speeds = []

def normalize_angle(angle):
    """Normalize an angle to the range [0, 2π]."""
    while angle < 0:
        angle += 2 * np.pi
    while angle >= 2 * np.pi:
        angle -= 2 * np.pi
    return angle

def generate_trajectory(entry, speed):
    """Generates a trajectory for an object entering, moving, and exiting the roundabout."""
    trajectory = []
    
    # Random radius between inner and outer bounds
    random_radius = np.random.uniform(inner_radius, outer_radius)
    
    # Compute entry angle and final position on the roundabout
    entry_vector = np.array(entry) - np.array(roundabout_center)
    entry_angle = normalize_angle(np.arctan2(entry_vector[1], entry_vector[0]))
    final_position = (
        roundabout_center[0] + random_radius * np.cos(entry_angle),
        roundabout_center[1] + random_radius * np.sin(entry_angle),
    )
    
    # Add initial linear movement to the final position on the roundabout
    entry_steps = int(30 / speed)  # Adjust steps based on speed
    for i in range(entry_steps):
        alpha = i / entry_steps
        point = (
            entry[0] * (1 - alpha) + final_position[0] * alpha,
            entry[1] * (1 - alpha) + final_position[1] * alpha,
        )
        trajectory.append(point)
    
    # Move around the roundabout
    chosen_exit = random.choice([1, 2, 3])  # Random exit choice
    relative_exit_angle = exit_angles_relative[chosen_exit - 1]  # Determine relative exit angle
    target_angle = normalize_angle(entry_angle + relative_exit_angle)  # Calculate absolute exit angle
    
    # Ensure counterclockwise movement
    if target_angle < entry_angle:
        target_angle += 2 * np.pi
    
    # Move along the roundabout to the exit angle
    circular_steps = int(abs(target_angle - entry_angle) / (speed * theta_step))
    angles = np.linspace(entry_angle, target_angle, circular_steps)
    for angle in angles:
        x = roundabout_center[0] + random_radius * np.cos(angle)
        y = roundabout_center[1] + random_radius * np.sin(angle)
        trajectory.append((x, y))
    
    # Move tangentially out of the roundabout
    last_position = np.array(trajectory[-1])
    tangent_angle = target_angle
    exit_steps = int(exit_length / speed)
    for i in range(exit_steps):
        dx = np.cos(tangent_angle) * (i / 5)
        dy = np.sin(tangent_angle) * (i / 5)
        point = last_position + [dx, dy]
        trajectory.append(tuple(point))
    
    return trajectory

# Generate trajectories for all objects
for obj_id in range(num_objects):
    entry = random.choice(entry_points)
    speed = np.random.uniform(min_speed, max_speed)  # Assign a random speed
    speeds.append(speed)
    trajectory = generate_trajectory(entry, speed)
    trajectories.append(trajectory)

# Save trajectories and speeds to data.txt
with open('data.txt', 'w') as file:
    for obj_id, trajectory in enumerate(trajectories):
        file.write(f"object {obj_id + 1} -> {trajectory} (speed: {speeds[obj_id]})\n")

# Visualization with PIL
frames = []
width, height = 500, 500
scale = 20  # Scaling for coordinates to fit the canvas

def to_canvas_coords(point):
    """Converts simulation coordinates to canvas coordinates."""
    return int(width / 2 + point[0] * scale), int(height / 2 - point[1] * scale)

for frame_idx in range(300):  # Number of frames
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

# Save the animation as data.mp4 using moviepy
clip = ImageSequenceClip(frames, fps=30)
clip.write_videofile("data.mp4", codec="libx264")
