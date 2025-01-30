import os
import json
import random


def exit_yrotation(door_dir):
    """
    Map the door's direction to a specific YRotation value.
    """
    if door_dir == {"x": 1, "y": 0}:  # Forgotten Lair
        return 0
    elif door_dir == {"x": 0, "y": 1}:  # Silverstar House
        return 512
    elif door_dir == {"x": -1, "y": 0}:  # Temple of Riellis
        return 1024
    elif door_dir == {"x": 0, "y": -1}:  # Tomb of the Demon Priest
        return 1536
    else:
        return 0  # Default rotation


def calculate_player_position(door_dir):
    """
    Calculate the player's position adjustment based on the door's direction.
    Ensure only one of XPos or ZPos is non-zero.
    """
    if door_dir == {"x": 0, "y": -1}:  # South
        return {"XPos": 0, "ZPos": 128}
    elif door_dir == {"x": 0, "y": 1}:  # North
        return {"XPos": 0, "ZPos": -128}
    elif door_dir == {"x": 1, "y": 0}:  # East
        return {"XPos": -128, "ZPos": 0}
    elif door_dir == {"x": -1, "y": 0}:  # West
        return {"XPos": 128, "ZPos": 0}
    else:
        return {"XPos": 0, "ZPos": 0}  # Default (no adjustment)


def calculate_object_position(x, y, direction="north", base_x=0, base_z=0):
    """
    Calculates the world position for any object, adjusting for rotation and offsets.

    Parameters:
        x (int): Grid x-coordinate of the object.
        y (int): Grid y-coordinate of the object.
        direction (str): Object's facing direction ("north", "east", "south", "west").
        base_x (int): Base offset for a north-facing object (adjust as needed).
        base_z (int): Base offset for a north-facing object (adjust as needed).

    Returns:
        dict: {"XPos", "ZPos"} with calculated world positions.
    """
    # Convert tile coordinates to world space
    x_pos = x * -128
    z_pos = y * -128

    # Adjust offsets based on direction
    if direction == "north":
        x_offset = base_x
        z_offset = base_z
    elif direction == "east":
        x_offset = -base_z
        z_offset = base_x
    elif direction == "south":
        x_offset = -base_x
        z_offset = -base_z
    elif direction == "west":
        x_offset = base_z
        z_offset = -base_x
    else:  # Default to no offset if direction is invalid
        x_offset = 0
        z_offset = 0

    # Apply adjusted offsets
    x_pos += x_offset
    z_pos += z_offset

    return {"XPos": x_pos, "ZPos": z_pos}


def add_door_model_reference(output_data):
    """Add the door model reference to the ModelReferenceList if not already present."""
    door_model_id = "55005"
    model_reference_list = output_data["RdbBlock"].setdefault("ModelReferenceList", [])
    if not any(ref["ModelId"] == door_model_id for ref in model_reference_list):
        model_reference_list.append(
            {
                "ModelId": door_model_id,
                "ModelIdNum": int(door_model_id),
                "Description": "DOR"
            }
        )

def calculate_door_position(door):
    """
    Calculate the door's world position based on its coordinates and direction,
    then adjust its placement within the doorframe based on its facing direction.
    """
    # Convert door grid coordinates to world coordinates
    x_pos = door["x"] * -128
    z_pos = door["y"] * -128

    # Adjust within doorframe based on direction
    direction = door.get("dir", {})
    if direction == {"x": 0, "y": -1}:
        x_pos += 24
    elif direction == {"x": 0, "y": 1}:
        x_pos -= 24
    elif direction == {"x": 1, "y": 0}:
        z_pos -= 24
    elif direction == {"x": -1, "y": 0}:
        z_pos += 24

    return {"XPos": x_pos, "ZPos": z_pos}

def door_yrotation(door_dir):
    """
    Map the door's direction to a specific YRotation value.
    """
    if door_dir == {"x": 0, "y": 1}:
        return 0
    elif door_dir == {"x": 1, "y": 0}:
        return 512
    elif door_dir == {"x": 0, "y": -1}:
        return 1024
    elif door_dir == {"x": -1, "y": 0}:
        return 1536
    else:
        return 0  # Default rotation

def add_doors(output_data, doors):
    """Add doors to the ObjectRootList > RdbObjects."""
    door_model = {"ModelId": "55005", "ModelIdNum": 55005, "Description": "DOR"}
    if door_model not in output_data["RdbBlock"]["ModelReferenceList"]:
        output_data["RdbBlock"]["ModelReferenceList"].append(door_model)

    door_model_index = len(output_data["RdbBlock"]["ModelReferenceList"]) - 1
    object_root_list = output_data["RdbBlock"].setdefault("ObjectRootList", [])
    if not object_root_list:
        object_root_list.append({"RdbObjects": []})

    rdb_objects = object_root_list[0].setdefault("RdbObjects", [])

    for door in doors:
        if door["type"] in {1, 2, 4, 6, 7}:  
            dir_map = {
                (0, 1): "north",
                (1, 0): "east",
                (0, -1): "south",
                (-1, 0): "west"
            }

            # Convert the 'dir' dictionary into a tuple before looking it up
            direction_tuple = tuple(door.get("dir", {}).values())  # Converts {'x': 0, 'y': 1} → (0, 1)
            direction = dir_map.get(direction_tuple, "north")  # Default to "north" if not found

            # Calculate the door position
            door_position = calculate_object_position(door["x"], door["y"], direction, base_x=-24, base_z=64)

            y_rotation = door_yrotation(door["dir"])
            story = door.get("story", 0)
            y_pos = (story * -128)

            door_object = {
                "Position": random.randint(10000, 30000),
                "Index": len(rdb_objects),
                "XPos": door_position["XPos"],
                "YPos": y_pos,
                "ZPos": door_position["ZPos"],
                "Type": "Model",
                "Resources": {
                    "ModelResource": {
                        "XRotation": 0,
                        "YRotation": y_rotation,
                        "ZRotation": 0,
                        "ModelIndex": door_model_index,
                        "TriggerFlag_StartingLock": 0,
                        "SoundIndex": 70,
                        "ActionResource": {
                            "Position": 0,
                            "Axis": 0,
                            "Duration": 0,
                            "Magnitude": 0,
                            "NextObjectOffset": 0,
                            "PreviousObjectOffset": -1,
                            "NextObjectIndex": 0,
                            "Flags": 16
                        }
                    }
                }
            }

            rdb_objects.append(door_object)


def calculate_monster_count(room_size):
    """
    Determine the number of monsters in a room based on the shortest side length.
    """
    if room_size <= 1:  # Ignore 1x1 rooms
        return 0

    # Set the base probabilities
    prob_two = min(0.1, room_size * 0.025)  # Max 20%, increases with room size
    prob_one = 0.4  # 50% chance of one monster
    prob_zero = 1 - prob_two - prob_one  # Remainder goes to zero monsters

    # Generate a random value and assign the monster count
    rand_value = random.random()
    if rand_value < prob_zero:
        return 0
    elif rand_value < prob_zero + prob_one:
        return 1
    else:
        return 2

def place_monsters_in_room(room, monster_count, faction_ids, rdb_objects):
    """
    Place monsters randomly within a room's tiles.
    """
    room_tiles = [
        (x, y)
        for x in range(room["x"], room["x"] + room["w"])
        for y in range(room["y"], room["y"] + room["h"])
    ]
    monster_positions = random.sample(room_tiles, min(len(room_tiles), monster_count))

    for i, (tile_x, tile_y) in enumerate(monster_positions):
        x_pos = tile_x * -128
        z_pos = tile_y * -128
        position_value = random.randint(10000, 30000)

        monster_object = {
            "Position": position_value,
            "Index": len(rdb_objects),
            "XPos": x_pos,
            "YPos": 0,
            "ZPos": z_pos,
            "Type": "Flat",
            "Resources": {
                "FlatResource": {
                    "Position": position_value,
                    "TextureArchive": 199,
                    "TextureRecord": 16,
                    "Flags": 0,
                    "Magnitude": 0,
                    "SoundIndex": 0,
                    "FactionOrMobileId": faction_ids[i],
                    "NextObjectOffset": 0,
                    "Action": 0,
                    "IsCustomData": False,
                }
            },
        }
        rdb_objects.append(monster_object)


def add_monsters_by_rooms(output_data, rects, entrance_coords, door_coords):
    """
    Add monsters to rooms based on their size and randomized rules.
    """
    for rect in rects:
        room_width = rect["w"]
        room_height = rect["h"]
        room_size = min(room_width, room_height)  # Shortest side

        # Skip 1x1 rooms
        if room_size <= 1:
            continue

        # Determine monster count
        monster_count = calculate_monster_count(room_size - 1)
        print(f"Room {rect['x']}, {rect['y']} - Monster count: {monster_count}")

        # Get the story value for the room
        story = rect.get("story", 0)

        # Place monsters randomly in the room
        placed_positions = set()  # Track occupied tiles
        for _ in range(monster_count):
            while True:
                x = random.randint(rect["x"], rect["x"] + rect["w"] - 1)
                y = random.randint(rect["y"], rect["y"] + rect["h"] - 1)

                if (x, y) not in placed_positions and (x, y) not in entrance_coords and (x, y) not in door_coords:
                    placed_positions.add((x, y))
                    add_monster(output_data, x, y, faction_id=512, story=story)  # Pass story
                    break

def add_monster(output_data, x, y, faction_id, story=0):
    """
    Add a monster to the RdbObjects list in output_data.
    """
    rdb_objects = output_data["RdbBlock"]["ObjectRootList"][0]["RdbObjects"]

    if rdb_objects is None:
        rdb_objects = []
        output_data["RdbBlock"]["ObjectRootList"][0]["RdbObjects"] = rdb_objects

    # Generate a unique Position and Index for the monster
    position = random.randint(10000, 30000)
    index = len(rdb_objects)  # Sequential index for the object

    # Convert coordinates to world positions
    x_pos = x * -128
    z_pos = y * -128
    y_pos = story * -128  # Adjust YPos based on the story

    # Define the monster object
    monster = {
        "Position": position,
        "Index": index,
        "XPos": x_pos,
        "YPos": y_pos,  # Adjusted for story
        "ZPos": z_pos,
        "Type": "Flat",
        "Resources": {
            "FlatResource": {
                "Position": position,
                "TextureArchive": 199,
                "TextureRecord": 15,
                "Flags": 0,
                "Magnitude": 0,
                "SoundIndex": 0,
                "FactionOrMobileId": faction_id,
                "NextObjectOffset": 0,
                "Action": 0,
                "IsCustomData": False,
            }
        },
    }

    # Add the monster to the RdbObjects list
    rdb_objects.append(monster)

def add_quest_marker(output_data, rooms):
    """
    Selects a random quest marker file from the QuestMarkers subdirectory
    and places it inside a room that is at least as big as required.

    Parameters:
    - output_data: The dungeon JSON data being modified.
    - rooms: The list of room rectangles in the dungeon.
    """
    quest_marker_dir = "QuestMarkers"
    quest_marker_files = [
        f for f in os.listdir(quest_marker_dir) if f.endswith(".json")
    ]
    
    if not quest_marker_files:
        print("No quest marker files found.")
        return
    
    # Pick a random quest marker file
    quest_marker_file = random.choice(quest_marker_files)
    quest_marker_path = os.path.join(quest_marker_dir, quest_marker_file)

    # Extract required dimensions from filename (e.g., "2x2_QuestMarker_00.json")
    parts = quest_marker_file.split("_")
    required_width, required_height = map(int, parts[0].split("x"))

    # Find a suitable room (at least required_width x required_height)
    eligible_rooms = [
        room for room in rooms if room["w"] >= required_width and room["h"] >= required_height
    ]

    if not eligible_rooms:
        print(f"No suitable room found for quest marker requiring size ({required_width}, {required_height}).")
        return
    
    # Pick a random eligible room
    selected_room = random.choice(eligible_rooms)
    room_x, room_y = selected_room["x"], selected_room["y"]
    room_story = selected_room.get("story", 0)

    print(f"Adding quest marker from {quest_marker_file} to room at ({room_x}, {room_y}).")

    # Load the quest marker JSON
    with open(quest_marker_path, "r") as file:
        quest_marker_data = json.load(file)

    # Ensure the ModelReferenceList exists
    model_reference_list = output_data["RdbBlock"].setdefault("ModelReferenceList", [])

    # Add new model references from quest marker data if not already present
    for model in quest_marker_data["RdbBlock"].get("ModelReferenceList", []):
        if model not in model_reference_list:
            model_reference_list.append(model)

    # Get the updated index for newly added models
    model_index_map = {
        model["ModelId"]: i for i, model in enumerate(model_reference_list)
    }

    # Ensure at least one ObjectRoot exists in the ObjectRootList
    object_root_list = output_data["RdbBlock"].setdefault("ObjectRootList", [])
    if not object_root_list:
        object_root_list.append({"RdbObjects": []})

    rdb_objects = object_root_list[0].setdefault("RdbObjects", [])

    # Adjust positions and add quest marker objects
    for obj in quest_marker_data["RdbBlock"]["ObjectRootList"][0]["RdbObjects"]:
        adjusted_obj = obj.copy()

        # Compute the center offset for the room
        room_center_x = room_x + (selected_room["w"] / 2)
        room_center_y = room_y + (selected_room["h"] / 2)

        # Compute the offset for the quest marker dimensions
        marker_offset_x = required_width / 2
        marker_offset_y = required_height / 2

        # Adjust X, Y, Z positions based on the room's center and the marker's size
        adjusted_obj["XPos"] += ((room_center_x - marker_offset_x + .5) * -128)
        adjusted_obj["ZPos"] += ((room_center_y - marker_offset_y + .5) * -128)
        adjusted_obj["YPos"] += room_story * -128

        # Adjust ModelIndex to match new model reference index
        if adjusted_obj["Type"] == "Model":
            model_id = quest_marker_data["RdbBlock"]["ModelReferenceList"][obj["Resources"]["ModelResource"]["ModelIndex"]]["ModelId"]
            adjusted_obj["Resources"]["ModelResource"]["ModelIndex"] = model_index_map[model_id]

        # Append adjusted object to the RdbObjects list
        adjusted_obj["Index"] = len(rdb_objects)  # Set correct index
        rdb_objects.append(adjusted_obj)

def process_json(input_file):
    # Read the input JSON
    with open(input_file, "r") as file:
        data = json.load(file)

    # Prepare the RDB.json structure
    output_data = {
        "Position": 0,
        "Index": 0,
        "Name": os.path.splitext(os.path.basename(input_file))[0] + ".RDB",
        "Type": "Rdb",
        "RmbBlock": {
            "FldHeader": {
                "NumBlockDataRecords": 0,
                "NumMisc3dObjectRecords": 0,
                "NumMiscFlatObjectRecords": 0,
                "BlockPositions": None,
                "BuildingDataList": None,
                "BlockDataSizes": None,
                "GroundData": {},
                "AutoMapData": None,
                "Name": None,
                "OtherNames": None,
            },
            "SubRecords": None,
            "Misc3dObjectRecords": None,
            "MiscFlatObjectRecords": None,
        },
        "RdbBlock": {
            "ModelReferenceList": [
                {"ModelId": "850004", "ModelIdNum": 850004, "Description": "XXX"},
                {"ModelId": "70300", "ModelIdNum": 70300, "Description": "EXT"},
            ],
            "ObjectRootList": [
                {
                    "RdbObjects": [
                        {
                            "Position": 66580,
                            "Index": 0,
                            "XPos": 64,
                            "YPos": 0,
                            "ZPos": 64,
                            "Type": "Model",
                            "Resources": {
                                "ModelResource": {
                                    "XRotation": 0,
                                    "YRotation": 0,
                                    "ZRotation": 0,
                                    "ModelIndex": 0,
                                    "TriggerFlag_StartingLock": 0,
                                    "SoundIndex": 0,
                                    "ActionResource": {
                                        "Position": 0,
                                        "Axis": 0,
                                        "Duration": 0,
                                        "Magnitude": 0,
                                        "NextObjectOffset": 0,
                                        "PreviousObjectOffset": 0,
                                        "NextObjectIndex": 0,
                                        "Flags": 0,
                                    },
                                }
                            },
                        },
                        {
                            "Position": 94516,
                            "Index": 1,
                            "XPos": 0,
                            "YPos": 0,
                            "ZPos": 64,
                            "Type": "Model",
                            "Resources": {
                                "ModelResource": {
                                    "XRotation": 0,
                                    "YRotation": 1024,  # Placeholder; will adjust
                                    "ZRotation": 0,
                                    "ModelIndex": 1,
                                    "TriggerFlag_StartingLock": 0,
                                    "SoundIndex": 0,
                                    "ActionResource": {
                                        "Position": 0,
                                        "Axis": 0,
                                        "Duration": 0,
                                        "Magnitude": 0,
                                        "NextObjectOffset": 0,
                                        "PreviousObjectOffset": 0,
                                        "NextObjectIndex": 0,
                                        "Flags": 0,
                                    },
                                }
                            },
                        },
                        {
                            "Position": 38028,
                            "Index": 2,
                            "XPos": 128,
                            "YPos": 0,
                            "ZPos": 0,
                            "Type": "Flat",
                            "Resources": {
                                "FlatResource": {
                                    "Position": 0,
                                    "TextureArchive": 199,
                                    "TextureRecord": 10,
                                    "Flags": 0,
                                    "Magnitude": 0,
                                    "SoundIndex": 0,
                                    "FactionOrMobileId": 0,
                                    "NextObjectOffset": 0,
                                    "Action": 0,
                                    "IsCustomData": False,
                                }
                            },
                        },
                    ]
                }
            ]
            + [{"RdbObjects": None} for _ in range(9)],  # Remaining empty ObjectRootList entries
        },
        "RdiBlock": {"Data": None},
    }

    # Add the door model reference
    add_door_model_reference(output_data)

    # Process doors
    doors = data.get("doors", [])
    add_doors(output_data, doors)

    # Adjust the YRotation for ModelIndex 1 and position for Index 2
    doors = data.get("doors", [])
    door_match = next((door for door in doors if door["x"] == 0 and door["y"] == 0), None)

    if door_match:
        door_dir = door_match.get("dir", {})
        adjusted_yrotation = exit_yrotation(door_dir)
        position_adjustment = calculate_player_position(door_dir)

        # Update the YRotation for ModelIndex 1
        for obj_root in output_data["RdbBlock"]["ObjectRootList"]:
            if obj_root["RdbObjects"] is not None:
                for rdb_object in obj_root["RdbObjects"]:
                    if (
                        rdb_object.get("Type") == "Model"
                        and rdb_object.get("Resources", {})
                        .get("ModelResource", {})
                        .get("ModelIndex")
                        == 1
                    ):
                        rdb_object["Resources"]["ModelResource"][
                            "YRotation"
                        ] = adjusted_yrotation

        # Update the player's starting position (Index 2, Type Flat)
        for obj_root in output_data["RdbBlock"]["ObjectRootList"]:
            if obj_root["RdbObjects"] is not None:
                for rdb_object in obj_root["RdbObjects"]:
                    if rdb_object.get("Index") == 2 and rdb_object.get("Type") == "Flat":
                        rdb_object["XPos"] = position_adjustment["XPos"]
                        rdb_object["ZPos"] = position_adjustment["ZPos"]


    # Get entrance coordinates (assuming a single entrance at (0, 0) for now)
    entrance_coords = (0, 0)  # Replace with actual entrance logic if dynamic

    # Get all door coordinates from the 'doors' list
    door_coords = {(door["x"], door["y"]) for door in data.get("doors", [])}

    # Add monsters by rooms
    add_monsters_by_rooms(output_data, data.get("rects", []), entrance_coords, door_coords)

    # Add quest marker
    add_quest_marker(output_data, data.get("rects", []))

    # Write the modified data to the output file
    output_file = os.path.splitext(input_file)[0] + ".RDB.json"
    with open(output_file, "w") as file:
        json.dump(output_data, file, indent=4)


def main():
    # Process all JSON files in the current directory
    for filename in os.listdir("."):
        if filename.endswith(".json") and not filename.endswith(".RDB.json"):
            print(f"Processing {filename}...")
            process_json(filename)
    print("Processing complete.")


if __name__ == "__main__":
    main()

