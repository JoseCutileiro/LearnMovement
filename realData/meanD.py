# Function to calculate the mean length of values associated with each key
def calculate_mean_length(data_file):
    lengths = []
    with open(data_file, "r") as file:
        for line in file:
            if "->" in line:
                key, values = line.split("->")
                values = eval(values.strip())
                lengths.append(len(values))
    mean_length = sum(lengths) / len(lengths) if lengths else 0
    return mean_length

# Example usage
input_file = "dataClean.txt"
mean_length = calculate_mean_length(input_file)
print(f"The mean length of all the lists is: {mean_length}")
