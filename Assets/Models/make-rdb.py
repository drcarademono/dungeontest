import os
import json
import random


def exit_yrotation(door_dir):
    """
    Map the door's direction to a specific YRotation value.
    """
    if door_dir == {"x": 0, "y": 1}:  # Silverstar House
        return 512
    elif door_dir == {"x": 1, "y": 0}:  # Forgotten Lair
        return 0
    elif door_dir == {"x": 0, "y": -1}:  # Tomb of the Demon Priest
        return 1536
    elif door_dir == {"x": -1, "y": 0}:  # Temple of Riellis
        return 1024
    else:
        return 0  # Default rotation


def calculate_player_position(door_dir):
    """
    Calculate the player's position adjustment based on the door's direction.
    Ensure only one of XPos or ZPos is non-zero.
    """
    if door_dir == {"x": 0, "y": -1}:  # South
        return {"XPos": 0, "ZPos": 100}
    elif door_dir == {"x": 0, "y": 1}:  # North
        return {"XPos": 0, "ZPos": -100}
    elif door_dir == {"x": 1, "y": 0}:  # East
        return {"XPos": -100, "ZPos": 0}
    elif door_dir == {"x": -1, "y": 0}:  # West
        return {"XPos": 100, "ZPos": 0}
    else:
        return {"XPos": 0, "ZPos": 0}  # Default (no adjustment)

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
    x_pos = door["x"] * -100
    z_pos = door["y"] * -100
    story = door.get("story", 0)
    y_pos = story * 100

    direction = door.get("dir", {})
    if direction == {"x": 0, "y": -1}:
        x_pos -= 24
    elif direction == {"x": 0, "y": 1}:
        x_pos += 24
    elif direction == {"x": 1, "y": 0}:
        z_pos += 24
    elif direction == {"x": -1, "y": 0}:
        z_pos -= 24

    return {"XPos": x_pos, "YPos": y_pos, "ZPos": z_pos}


def add_doors(output_data, doors):
    door_model = {"ModelId": "55005", "ModelIdNum": 55005, "Description": "DOR"}
    if door_model not in output_data["RdbBlock"]["ModelReferenceList"]:
        output_data["RdbBlock"]["ModelReferenceList"].append(door_model)

    door_model_index = len(output_data["RdbBlock"]["ModelReferenceList"]) - 1
    object_root_list = output_data["RdbBlock"].setdefault("ObjectRootList", [])
    if not object_root_list:
        object_root_list.append({"RdbObjects": []})

    rdb_objects = object_root_list[0].setdefault("RdbObjects", [])

    for door in doors:
        if door["type"] in {1, 4, 5, 6, 7}:
            door_position = calculate_door_position(door)
            y_rotation = door_yrotation(door["dir"])

            door_object = {
                "Position": random.randint(10000, 30000),
                "Index": len(rdb_objects),
                "XPos": door_position["XPos"],
                "YPos": door_position["YPos"],
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

    max_monsters = min(room_size, 3)  # Clamp to 4 maximum monsters
    for count in range(max_monsters, -1, -1):  # Start with the max possible
        if random.random() < 0.25:  # Fixed probability for each step
            return count
    return 0  # Default to no monsters if no threshold is met


def place_monsters_in_room(room, monster_count, faction_ids, rdb_objects):
    room_tiles = [
        (x, y)
        for x in range(room["x"], room["x"] + room["w"])
        for y in range(room["y"], room["y"] + room["h"])
    ]
    monster_positions = random.sample(room_tiles, min(len(room_tiles), monster_count))

    story = room.get("story", 0)
    y_pos = story * 100

    for i, (tile_x, tile_y) in enumerate(monster_positions):
        x_pos = tile_x * -100
        z_pos = tile_y * -100
        position_value = random.randint(10000, 30000)

        monster_object = {
            "Position": position_value,
            "Index": len(rdb_objects),
            "XPos": x_pos,
            "YPos": y_pos,
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

        # Get a random FactionId for the room (50% 0, others split evenly)
        faction_id = 512

        # Place monsters randomly in the room
        placed_positions = set()  # Track occupied tiles
        for _ in range(monster_count):
            while True:
                x = random.randint(rect["x"], rect["x"] + rect["w"] - 1)
                y = random.randint(rect["y"], rect["y"] + rect["h"] - 1)

                if (x, y) not in placed_positions and (x, y) not in entrance_coords and (x, y) not in door_coords:
                    placed_positions.add((x, y))
                    add_monster(output_data, x, y, faction_id)
                    break

import random

def add_monster(output_data, x, y, faction_id, story=0):
    """
    Add a monster to the RdbObjects list in output_data, adjusting for story.
    
    Parameters:
    - output_data: The output data structure to which the monster will be added.
    - x, y: Tile coordinates for the monster.
    - faction_id: The faction ID of the monster.
    - story: The story (floor level) of the room, used to adjust the YPos.
    """
    rdb_objects = output_data["RdbBlock"]["ObjectRootList"][0]["RdbObjects"]

    if rdb_objects is None:
        rdb_objects = []
        output_data["RdbBlock"]["ObjectRootList"][0]["RdbObjects"] = rdb_objects

    # Generate a unique Position and Index for the monster
    position = random.randint(10000, 30000)
    index = len(rdb_objects)  # Sequential index for the object

    # Convert coordinates to world positions
    x_pos = x * -100
    z_pos = y * -100
    y_pos = story * 100  # Adjust vertical position based on the story

    # Define the monster object
    monster = {
        "Position": position,
        "Index": index,
        "XPos": x_pos,
        "YPos": y_pos,  # Adjusted for the story
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
                            "XPos": 50,
                            "YPos": 0,
                            "ZPos": 50,
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
                        }
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

    # Add monsters by rooms, adjusting YPos for the story
    rects = data.get("rects", [])
    for rect in rects:
        room_story = rect.get("story", 0)  # Get the story for the room
        add_monsters_by_rooms(output_data, [rect], entrance_coords, door_coords, story=room_story)

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

