# Open the input file and read the data
input_file = "data.txt"
output_file = "dataClean.txt"

data_dict = {}

# Read and parse the input file
with open(input_file, "r") as file:
    for line in file:
        if "->" in line:
            key, values = line.split("->")
            key = key.strip()
            values = eval(values.strip())
            if key not in data_dict:
                data_dict[key] = []
            data_dict[key].extend(values)

# Write the cleaned data to the output file, ignoring entries with fewer than 20 values
with open(output_file, "w") as file:
    for key, values in data_dict.items():
        if len(values) >= 10:  # Only include entries with 20 or more values
            file.write(f"{key} -> {values}\n")
