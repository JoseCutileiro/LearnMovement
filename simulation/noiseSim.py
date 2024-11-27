import ast
import random

# Parameters
noise_size = 0.1  # Maximum noise to add to each coordinate

# Load trajectories from data.txt
trajectories_with_noise = []
with open("data.txt", "r") as file:
    for line in file:
        # Parse the trajectory from the file
        object_id, trajectory_data = line.split("->")
        trajectory_str, speed_data = trajectory_data.split("(speed:")  # Extract speed separately
        trajectory = ast.literal_eval(trajectory_str.strip())
        speed = float(speed_data.strip().rstrip(")"))
        
        # Add random noise to each point in the trajectory
        noisy_trajectory = [
            (x + random.uniform(-noise_size, noise_size), y + random.uniform(-noise_size, noise_size))
            for x, y in trajectory
        ]
        trajectories_with_noise.append((object_id.strip(), noisy_trajectory, speed))

# Save trajectories with noise to data_with_noise.txt
with open("data_with_noise.txt", "w") as file:
    for object_id, noisy_trajectory, speed in trajectories_with_noise:
        file.write(f"{object_id} -> {noisy_trajectory} (speed: {speed})\n")
