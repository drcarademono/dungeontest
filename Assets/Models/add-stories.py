import os
import json

# Directory containing the JSON files
directory = '.'

def find_bridges(rooms):
    # Initialize all rooms as unvisited and clear previous types
    for room in rooms:
        room['type'] = None

    # Find the connected components
    components = get_connected_components(rooms)

    # Identify bridge rooms
    for room_index, room in enumerate(rooms):
        if is_valid_ramp(room, rooms):
            # Temporarily remove the room and test connectivity
            remaining_rooms = [r for i, r in enumerate(rooms) if i != room_index]
            new_components = get_connected_components(remaining_rooms)

            # If removing the room increases the number of components, it's a bridge
            if len(new_components) > len(components):
                room['type'] = 'ramp'

    return rooms

# Get connected components using flood-fill
def get_connected_components(rooms):
    visited = set()
    components = []

    for room_index in range(len(rooms)):
        if room_index not in visited:
            # Perform a flood-fill to find all connected rooms
            component = flood_fill(room_index, rooms, visited)
            components.append(component)

    return components

# Flood-fill to find all connected rooms from a starting room
def flood_fill(start_index, rooms, visited):
    stack = [start_index]
    component = []

    while stack:
        room_index = stack.pop()
        if room_index not in visited:
            visited.add(room_index)
            component.append(room_index)
            neighbors = find_adjacent_rooms(room_index, rooms)
            stack.extend(neighbors)

    return component

# Find all adjacent rooms to a given room index
def find_adjacent_rooms(room_index, rooms):
    adjacent = []
    for other_index, other_room in enumerate(rooms):
        if other_index != room_index and is_adjacent(rooms[room_index], other_room):
            adjacent.append(other_index)
    return adjacent

# Check if two rooms are adjacent
def is_adjacent(room1, room2):
    if (room1['x'] + room1['w'] == room2['x'] or room2['x'] + room2['w'] == room1['x']) and (room1['y'] < room2['y'] + room2['h'] and room1['y'] + room1['h'] > room2['y']):
        return True  # Horizontal adjacency
    if (room1['y'] + room1['h'] == room2['y'] or room2['y'] + room2['h'] == room1['y']) and (room1['x'] < room2['x'] + room2['w'] and room1['x'] + room1['w'] > room2['x']):
        return True  # Vertical adjacency
    return False

# Check if a room is a valid ramp (1xN or Nx1) with opposite adjacency
def is_valid_ramp(room, rooms):
    # Check if the room is 1xN or Nx1
    if not (room['w'] == 1 or room['h'] == 1):
        return False

    # Get adjacent rooms
    neighbors = find_adjacent_rooms_by_direction(room, rooms)

    # Ensure exactly two neighbors exist and they are on opposite sides
    if len(neighbors) == 2:
        directions = list(neighbors.keys())
        return (('north' in directions and 'south' in directions) or
                ('east' in directions and 'west' in directions))

    return False

# Find adjacent rooms by direction (north, south, east, west)
def find_adjacent_rooms_by_direction(room, rooms):
    neighbors = {}

    for other_room in rooms:
        if is_adjacent(room, other_room):
            if other_room['x'] + other_room['w'] == room['x']:  # West
                neighbors['west'] = other_room
            elif room['x'] + room['w'] == other_room['x']:  # East
                neighbors['east'] = other_room
            elif other_room['y'] + other_room['h'] == room['y']:  # South
                neighbors['south'] = other_room
            elif room['y'] + room['h'] == other_room['y']:  # North
                neighbors['north'] = other_room

    return neighbors

# Process each JSON file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)

        with open(filepath) as f:
            data = json.load(f)

        # Find and mark bridges
        data['rects'] = find_bridges(data['rects'])

        # Save the modified JSON data (overwrite the original file)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

print("All files processed with bridges marked as ramps.")

