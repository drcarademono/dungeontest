import os
import json
from collections import deque
import random

# Directory containing the JSON files
directory = '.'

def find_bridges(rooms, doors):
    print("Starting ramp detection...")

    # Initialize all rooms as unvisited and clear previous types and stories
    for room in rooms:
        room.pop('type', None)  # Remove any existing 'type'
        room.pop('story', None)  # Remove any existing 'story'
        room.pop('ramp_info', None)  # Remove any existing 'ramp_info'
        room['type'] = None  # Initialize 'type' as None
        room['story'] = None  # Initialize 'story' as None
        room['ramp_info'] = None  # Initialize 'ramp_info' as None
        print(f"Cleared 'type', 'story', and 'ramp_info' for room at ({room['x']}, {room['y']}).")

    # Find the connected components
    components = get_connected_components(rooms)

    # Identify bridge rooms
    for room_index, room in enumerate(rooms):
        if is_valid_ramp(room, rooms, doors):
            # Temporarily remove the room and test connectivity
            remaining_rooms = [r for i, r in enumerate(rooms) if i != room_index]
            new_components = get_connected_components(remaining_rooms)

            # If removing the room increases the number of components, it's a bridge
            if len(new_components) > len(components):
                room['type'] = 'ramp'
                print(f"Room at ({room['x']}, {room['y']}) marked as ramp.")

    # Resolve clusters of adjacent ramps
    resolve_adjacent_ramps(rooms)

    print("Ramp detection completed.")
    return rooms

def resolve_adjacent_ramps(rooms):
    print("Resolving adjacent ramps...")
    ramps = [room for room in rooms if room['type'] == 'ramp']
    processed = set()

    for ramp in ramps:
        ramp_key = (ramp['x'], ramp['y'])  # Use (x, y) as a unique identifier
        if ramp_key in processed:
            continue

        # Find all connected ramps (orthogonal adjacency only)
        cluster = find_adjacent_ramp_cluster(ramp, rooms)
        if len(cluster) <= 1:
            continue  # No need to resolve single ramps

        print(f"Found ramp cluster with {len(cluster)} rooms.")
        cluster.sort(key=lambda r: (r['x'], r['y']))  # Sort to ensure deterministic ordering

        # Determine the ramp to keep
        if all(r['w'] == cluster[0]['w'] and r['h'] == cluster[0]['h'] for r in cluster):  # Same dimensions
            if len(cluster) % 2 == 1:
                keep = cluster[len(cluster) // 2]  # Middle one
            else:
                keep = random.choice(cluster)  # Pick one at random
        else:  # Keep the longest or widest ramp
            keep = max(cluster, key=lambda r: max(r['w'], r['h']))

        # Mark all other ramps in the cluster as non-ramps
        for r in cluster:
            r_key = (r['x'], r['y'])
            if r != keep:
                r['type'] = None
                print(f"Removed ramp designation from room at ({r['x']}, {r['y']}).")
            processed.add(r_key)  # Mark the room as processed

def find_adjacent_ramp_cluster(start_ramp, rooms):
    """Find all ramps in the same cluster using orthogonal adjacency."""
    cluster = []
    queue = deque([start_ramp])
    visited = set()

    while queue:
        current = queue.popleft()
        current_key = (current['x'], current['y'])
        if current_key in visited:
            continue
        visited.add(current_key)
        cluster.append(current)

        # Add orthogonally adjacent ramps
        for neighbor in find_adjacent_rooms(current, rooms):
            neighbor_key = (neighbor['x'], neighbor['y'])
            if neighbor['type'] == 'ramp' and neighbor_key not in visited:
                queue.append(neighbor)

    return cluster

# Assign stories and update ramps
def assign_stories(rooms):
    print("Starting story assignment...")

    # Assign story 0 starting from the entrance
    entrance = next((room for room in rooms if room['x'] == 0 and room['y'] == 0), None)
    if not entrance:
        raise ValueError("No entrance room found at (0, 0).")
    
    entrance['story'] = 0
    flood_fill_story([entrance], rooms, story=0)

    # Update ramps adjacent to story 0
    update_adjacent_ramps(rooms, story=0)

    # Iterative process to assign progressively lower stories
    current_story = 0
    while True:
        # Find all ramps for the current story
        current_story_ramps = [room for room in rooms if room['type'] == 'ramp' and room['story'] == current_story]
        if not current_story_ramps:
            break  # Exit if there are no more ramps to process

        print(f"Processing story {current_story} ramps...")

        # Assign the next story to unvisited rooms adjacent to current story ramps
        next_story = current_story - 1
        for ramp in current_story_ramps:
            neighbors = find_adjacent_rooms(ramp, rooms)
            for neighbor in neighbors:
                if neighbor['story'] is None:  # Unvisited room
                    neighbor['story'] = next_story
                    flood_fill_story([neighbor], rooms, story=next_story)

        # Update ramps adjacent to the next story
        update_adjacent_ramps(rooms, story=next_story)

        # Move to the next story level
        current_story = next_story

    print("Story assignment completed.")
    return rooms

# Flood-fill for assigning stories with ramp detection
def flood_fill_story(start_rooms, rooms, story):
    """Flood-fill to assign a story and mark unvisited ramps blocking the fill."""
    queue = deque(start_rooms)
    while queue:
        current_room = queue.popleft()
        print(f"Processing room at ({current_room['x']}, {current_room['y']}) for story {story}.")
        neighbors = find_adjacent_rooms(current_room, rooms)

        for neighbor in neighbors:
            if neighbor['story'] is None and neighbor.get('type') != 'ramp':  # Unvisited, non-ramp rooms
                neighbor['story'] = story
                queue.append(neighbor)
                print(f"Flood-filled room at ({neighbor['x']}, {neighbor['y']}) with story {story}.")
            elif neighbor['story'] is None and neighbor.get('type') == 'ramp':  # Unvisited ramp
                neighbor['story'] = story
                print(f"Marked ramp at ({neighbor['x']}, {neighbor['y']}) as story {story} (blocked flood-fill).")

def update_adjacent_ramps(rooms, story):
    """Update ramps adjacent to rooms with the specified story."""
    for room in rooms:
        if room['story'] == story:
            neighbors = find_adjacent_rooms(room, rooms)
            for neighbor in neighbors:
                if neighbor.get('type') == 'ramp' and neighbor['story'] is None:
                    neighbor['story'] = story  # Assign the highest story
                    print(f"Updated ramp at ({neighbor['x']}, {neighbor['y']}) with story {neighbor['story']}.")


def get_direction(room, neighbor):
    """Determine the direction of the neighbor relative to the room."""
    if neighbor['x'] + neighbor['w'] == room['x']:
        return 'west'
    elif room['x'] + room['w'] == neighbor['x']:
        return 'east'
    elif neighbor['y'] + neighbor['h'] == room['y']:
        return 'south'
    elif room['y'] + room['h'] == neighbor['y']:
        return 'north'
    return 'unknown'

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
            neighbors = find_adjacent_rooms_by_index(room_index, rooms)
            stack.extend(neighbors)

    return component

# Find all adjacent rooms by index
def find_adjacent_rooms_by_index(room_index, rooms):
    adjacent = []
    for other_index, other_room in enumerate(rooms):
        if other_index != room_index and is_adjacent(rooms[room_index], other_room):
            adjacent.append(other_index)
    return adjacent

# Find all adjacent rooms
def find_adjacent_rooms(room, rooms):
    adjacent = []
    for other_room in rooms:
        if other_room != room and is_adjacent(room, other_room):
            adjacent.append(other_room)
    return adjacent

# Check if two rooms are adjacent
def is_adjacent(room1, room2):
    if (room1['x'] + room1['w'] == room2['x'] or room2['x'] + room2['w'] == room1['x']) and (room1['y'] < room2['y'] + room2['h'] and room1['y'] + room1['h'] > room2['y']):
        return True  # Horizontal adjacency
    if (room1['y'] + room1['h'] == room2['y'] or room2['y'] + room2['h'] == room1['y']) and (room1['x'] < room2['x'] + room2['w'] and room1['x'] + room1['w'] > room2['x']):
        return True  # Vertical adjacency
    return False

# Check if a room is a valid ramp (1xN or Nx1) with opposite adjacency
def is_valid_ramp(room, rooms, doors):
    # Check if the room is 1xN or Nx1
    if not (room['w'] == 1 or room['h'] == 1):
        return False

    # Check for disqualifying doors
    disqualifying_door_types = {1, 2, 4, 6, 7}
    room_has_disqualifying_door = any(
        door['type'] in disqualifying_door_types and
        door['x'] >= room['x'] and door['x'] < room['x'] + room['w'] and
        door['y'] >= room['y'] and door['y'] < room['y'] + room['h']
        for door in doors
    )
    if room_has_disqualifying_door:
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

def assign_ramp_directions(rects):
    """
    Assign directions to ramps based on the lowest-story adjacent room.
    """
    for rect in rects:
        if rect.get('type') == 'ramp':
            neighbors = find_adjacent_rooms_by_direction(rect, rects)

            # Filter neighbors to only those with a valid story
            valid_neighbors = {direction: room for direction, room in neighbors.items() if 'story' in room and room['story'] is not None}

            if valid_neighbors:
                # Find the neighbor with the lowest story
                lowest_story_direction = min(valid_neighbors, key=lambda d: valid_neighbors[d]['story'])
                rect['ramp_dir'] = lowest_story_direction
                print(f"Assigned direction {lowest_story_direction} to ramp at ({rect['x']}, {rect['y']}) with story {rect['story']}.")
            else:
                rect['ramp_dir'] = 'unknown'
                print(f"Could not determine direction for ramp at ({rect['x']}, {rect['y']}). No valid adjacent rooms.")

    return rects

def assign_door_stories(rects, doors):
    """
    Assigns the story of the corresponding room to each door in the doors array.

    Parameters:
    - rects: List of room rectangles with `x`, `y`, `w`, `h`, and `story`.
    - doors: List of door objects with `x`, `y`, and other properties.

    Returns:
    - Updated doors array with assigned `story` values.
    """
    for door in doors:
        door_x, door_y = door['x'], door['y']
        door_story = None

        # Find the room that contains this door
        for rect in rects:
            rect_x, rect_y, rect_w, rect_h = rect['x'], rect['y'], rect['w'], rect['h']
            if rect_x <= door_x < rect_x + rect_w and rect_y <= door_y < rect_y + rect_h:
                door_story = rect.get('story', 0)  # Default story is 0 if not assigned
                break

        if door_story is not None:
            door['story'] = door_story
            print(f"Assigned story {door_story} to door at ({door_x}, {door_y}).")
        else:
            print(f"Could not assign a story to door at ({door_x}, {door_y}). No matching room found.")

    return doors

def assign_column_stories(rects, columns):
    """
    Assign the correct story to each column based on the room it is in.

    Parameters:
    - rects: List of room rectangles with `x`, `y`, `w`, `h`, and `story`.
    - columns: List of column objects with `x` and `y`.

    Returns:
    - Updated columns array with assigned `story` values.
    """
    for column in columns:
        column_x, column_y = column['x'], column['y']
        column_story = None

        # Find the room that contains this column
        for rect in rects:
            rect_x, rect_y, rect_w, rect_h = rect['x'], rect['y'], rect['w'], rect['h']
            if rect_x <= column_x < rect_x + rect_w and rect_y <= column_y < rect_y + rect_h:
                column_story = rect.get('story', 0)  # Default story is 0 if not assigned
                break

        if column_story is not None:
            column['story'] = column_story
            print(f"Assigned story {column_story} to column at ({column_x}, {column_y}).")
        else:
            print(f"Could not assign a story to column at ({column_x}, {column_y}). No matching room found.")

    return columns

# Process each JSON file
directory = "./"  # Replace with your directory path

for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)

        with open(filepath) as f:
            data = json.load(f)

        print(f"Processing file: {filename}")
        data['rects'] = find_bridges(data['rects'], data.get('doors', []))  # Pass the doors array
        data['rects'] = assign_stories(data['rects'])  # Assign stories
        data['rects'] = assign_ramp_directions(data['rects'])  # Assign ramp directions
        data['doors'] = assign_door_stories(data['rects'], data.get('doors', []))  # Assign door stories
        data['columns'] = assign_column_stories(data['rects'], data.get('columns', []))  # Assign column stories

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

print("All files processed with ramps, stories, and door stories assigned.")
