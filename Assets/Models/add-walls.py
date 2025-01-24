import os
import json
import random

# Directory containing the JSON files
directory = '.'

# Function to generate walls for each room
def generate_walls(rooms):
    for room in rooms:
        # Add vault value: 0 for 1x1 rooms, 1 otherwise
        room['vault'] = 0 if room['w'] == 1 and room['h'] == 1 else 1
        
        # Determine the ceiling height
        ceiling = determine_ceiling(room)
        room['ceiling'] = ceiling
        
        walls_by_level = {level: [] for level in range(ceiling + 1)}

        for level in range(ceiling + 1):
            # Top wall
            for i in range(room['w']):
                walls_by_level[level].append({"x": room['x'] + i, "y": room['y'], "dir": {"x": 1, "y": 0}, "level": level})

            # Bottom wall
            for i in range(room['w']):
                walls_by_level[level].append({"x": room['x'] + i, "y": room['y'] + room['h'], "dir": {"x": 1, "y": 0}, "level": level})

            # Left wall
            for i in range(room['h']):
                walls_by_level[level].append({"x": room['x'], "y": room['y'] + i, "dir": {"x": 0, "y": 1}, "level": level})

            # Right wall
            for i in range(room['h']):
                walls_by_level[level].append({"x": room['x'] + room['w'], "y": room['y'] + i, "dir": {"x": 0, "y": 1}, "level": level})

        room['walls'] = [wall for level_walls in walls_by_level.values() for wall in level_walls]

# Determine the ceiling height based on room size
def determine_ceiling(room):
    if room['w'] == 1 or room['h'] == 1:
        return 0  # No high ceilings for rooms with width or height of 1

    # Probability distribution for ceiling heights based on room size
    size = room['w'] * room['h']
    if size < 4:
        return random.choices([0, 1], [0.8, 0.2])[0]
    elif size < 9:
        return random.choices([0, 1, 2], [0.5, 0.3, 0.2])[0]
    else:
        return random.choices([0, 1, 2, 3], [0.4, 0.3, 0.2, 0.1])[0]

# Determine the direction of the wall
def determine_direction(wall):
    if wall['dir']['x'] == 1 and wall['dir']['y'] == 0:
        return 'east'
    elif wall['dir']['x'] == -1 and wall['dir']['y'] == 0:
        return 'west'
    elif wall['dir']['x'] == 0 and wall['dir']['y'] == 1:
        return 'south'
    elif wall['dir']['x'] == 0 and wall['dir']['y'] == -1:
        return 'north'

# Function to find exits for rotunda rooms
def find_exits_for_rotunda(room, wall_count):
    exits = set()
    for wall in room['walls']:
        wall_tuple = (wall['x'], wall['y'], wall['dir']['x'], wall['dir']['y'])
        if wall_count.get(wall_tuple, 0) > 1:
            direction = determine_direction(wall)
            exits.add(direction)
    room['exits'] = list(exits)

# Remove duplicate walls where rooms intersect
def remove_duplicate_walls(rooms):
    wall_count = {}
    for room in rooms:
        for wall in room['walls']:
            wall_tuple = (wall['x'], wall['y'], wall['dir']['x'], wall['dir']['y'], wall['level'])
            if wall_tuple in wall_count:
                wall_count[wall_tuple] += 1
            else:
                wall_count[wall_tuple] = 1

    for room in rooms:
        room['walls'] = [wall for wall in room['walls'] if wall_count[(wall['x'], wall['y'], wall['dir']['x'], wall['dir']['y'], wall['level'])] == 1]

# Process each JSON file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        
        with open(filepath) as f:
            data = json.load(f)
        
        # Generate walls for all rooms
        generate_walls(data['rects'])

        # Find exits for rotunda rooms
        wall_count = {}
        for room in data['rects']:
            for wall in room['walls']:
                wall_tuple = (wall['x'], wall['y'], wall['dir']['x'], wall['dir']['y'], wall['level'])
                if wall_tuple in wall_count:
                    wall_count[wall_tuple] += 1
                else:
                    wall_count[wall_tuple] = 1

        for room in data['rects']:
            if 'rotunda' in room and room['rotunda']:
                find_exits_for_rotunda(room, wall_count)
        
        # Remove duplicate walls
        remove_duplicate_walls(data['rects'])
        
        # Save the modified JSON data
        new_filepath = os.path.join(directory, f'{filename}')
        with open(new_filepath, 'w') as f:
            json.dump(data, f, indent=4)

print("All files processed and saved with wall arrays added, high ceilings handled, exits for rotunda rooms handled, and duplicate walls removed.")

