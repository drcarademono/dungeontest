import os

# Set the starting number
start_number = 60000

# Get the current directory
directory = os.getcwd()

# Get all .json files in the directory, excluding .json.meta files
json_files = sorted([f for f in os.listdir(directory) if f.endswith('.json') and not f.endswith('.json.meta')])

# Rename each file
for index, file_name in enumerate(json_files, start=start_number):
    # Construct new name with .json extension
    new_name = f"{index}.json"
    # Get the full path of the old and new files
    old_path = os.path.join(directory, file_name)
    new_path = os.path.join(directory, new_name)
    # Rename the file
    os.rename(old_path, new_path)
    print(f"Renamed: {file_name} -> {new_name}")

print("Renaming complete!")

