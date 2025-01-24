import os
import json


def calculate_yrotation(door_dir):
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
        return 1536
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
        return {"XPos": 0, "ZPos": 100}
    else:
        return {"XPos": 0, "ZPos": 0}  # Default (no adjustment)

def add_doors(output_data, doors):
    """Add doors to the ObjectRootList > RdbObjects."""
    door_model_index = len(output_data["RdbBlock"]["ModelReferenceList"]) - 1
    object_root_list = output_data["RdbBlock"].setdefault("ObjectRootList", [])
    if not object_root_list:
        object_root_list.append({"RdbObjects": []})  # Ensure at least one ObjectRoot exists

    rdb_objects = object_root_list[0].setdefault("RdbObjects", [])

    for door in doors:
        if door["type"] in {1, 4, 7}:  # Filter door types
            x = door["x"]
            y = door["y"]
            dir = door["dir"]
            y_rotation = calculate_yrotation(dir)

            door_object = {
                "Position": random.randint(10000, 30000),  # Unique random number
                "Index": len(rdb_objects),  # Index in RdbObjects
                "XPos": x * 100,
                "YPos": 0,  # Default Y position for doors
                "ZPos": y * 100,
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
                        },
                        {
                            "Position": 94516,
                            "Index": 1,
                            "XPos": 0,
                            "YPos": 0,
                            "ZPos": 0,
                            "Type": "Model",
                            "Resources": {
                                "ModelResource": {
                                    "XRotation": 0,
                                    "YRotation": -1024,  # Placeholder; will adjust
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
                            "XPos": 100,
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

    # Adjust the YRotation for ModelIndex 1 and position for Index 2
    doors = data.get("doors", [])
    door_match = next((door for door in doors if door["x"] == 0 and door["y"] == 0), None)

    if door_match:
        door_dir = door_match.get("dir", {})
        adjusted_yrotation = calculate_yrotation(door_dir)
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

