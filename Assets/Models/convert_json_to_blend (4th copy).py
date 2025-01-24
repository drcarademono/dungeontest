import bpy
import json
import os
import math

def clear_default_scene():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def create_materials():
    floor_material = bpy.data.materials.new(name="FloorMaterial")
    wall_material = bpy.data.materials.new(name="WallMaterial")
    return floor_material, wall_material

def create_floor(x, y, w, h, floor_material):
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(x + w/2, y + h/2, 0))
    plane = bpy.context.active_object
    plane.scale[0] = w
    plane.scale[1] = h
    bpy.ops.object.transform_apply(location=False, scale=True, rotation=False)
    add_uvs(plane, 1, 1)
    plane.data.materials.append(floor_material)
    return plane

def create_circle_quadrant(x, y, radius, collection, quadrant=1, floor_material=None, wall_material=None):
    segment_length = 1.0
    arc_length = (math.pi / 2) * radius
    segments = max(1, int(arc_length / segment_length))

    angle_offset = math.pi / 2
    angle_start = (quadrant - 1) * angle_offset
    angle_end = quadrant * angle_offset

    mesh = bpy.data.meshes.new("CircleQuadrant")
    obj = bpy.data.objects.new("CircleQuadrant", mesh)
    collection.objects.link(obj)

    verts = [(x, y, 0)]
    verts += [(x + math.cos(angle_start + angle_offset * i / segments) * radius, 
               y + math.sin(angle_start + angle_offset * i / segments) * radius, 0) 
              for i in range(segments + 1)]
    edges = []
    faces = [tuple(range(len(verts)))]

    mesh.from_pydata(verts, edges, faces)
    mesh.update()
    add_uvs(obj, 1, 1)

    if floor_material:
        obj.data.materials.append(floor_material)

    walls = []
    for i in range(1, len(verts) - 1):
        start_vert = verts[i]
        end_vert = verts[i + 1]
        wall = create_vertical_face(start_vert, end_vert, collection, wall_material)
        walls.append(wall)

    return obj, walls

def create_vertical_face(start_vert, end_vert, collection, wall_material=None):
    width = math.sqrt((end_vert[0] - start_vert[0]) ** 2 + (end_vert[1] - start_vert[1]) ** 2)
    height = 0.5

    mesh = bpy.data.meshes.new("Wall")
    obj = bpy.data.objects.new("Wall", mesh)
    collection.objects.link(obj)

    verts = [start_vert, end_vert, (end_vert[0], end_vert[1], 1), (start_vert[0], start_vert[1], 1)]
    edges = []
    faces = [(0, 1, 2, 3)]

    mesh.from_pydata(verts, edges, faces)
    mesh.update()

    add_rotunda_uvs(obj, width, height)
    if wall_material:
        obj.data.materials.append(wall_material)

    return obj

def create_rotunda_quadrants(rect, collection, floor_material=None, wall_material=None):
    x, y, w, h = rect['x'], rect['y'], rect['w'], rect['h']
    radius = (min(w, h) - 1) / 2
    offset = h / 2 - 0.5

    objs = []
    walls = []
    obj, quadrant_walls = create_circle_quadrant(x + w - offset, y + h - offset, radius, collection, quadrant=1, floor_material=floor_material, wall_material=wall_material)
    objs.append(obj)
    walls.extend(quadrant_walls)
    obj, quadrant_walls = create_circle_quadrant(x + offset, y + h - offset, radius, collection, quadrant=2, floor_material=floor_material, wall_material=wall_material)
    objs.append(obj)
    walls.extend(quadrant_walls)
    obj, quadrant_walls = create_circle_quadrant(x + offset, y + offset, radius, collection, quadrant=3, floor_material=floor_material, wall_material=wall_material)
    objs.append(obj)
    walls.extend(quadrant_walls)
    obj, quadrant_walls = create_circle_quadrant(x + w - offset, y + offset, radius, collection, quadrant=4, floor_material=floor_material, wall_material=wall_material)
    objs.append(obj)
    walls.extend(quadrant_walls)

    for wall in walls:
        flip_wall_normals(wall)

    return objs, walls

def add_rotunda_uvs(obj, width, height):
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UVMap")

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='OBJECT')

    uv_layer = obj.data.uv_layers.active.data

    for poly in obj.data.polygons:
        for loop_index in poly.loop_indices:
            uv = uv_layer[loop_index].uv
            vertex = obj.data.vertices[obj.data.loops[loop_index].vertex_index].co

            uv[0] = uv[0] * width
            uv[1] = uv[1] / height

def create_rotunda_plus(x, y, w, h, floor_material):
    objs = []
    center_x = x + w / 2
    center_y = y + h / 2

    for i in range(w):
        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(x + i + 0.5, center_y, 0))
        plane = bpy.context.active_object
        objs.append(plane)
        add_uvs(plane, 1, 1)
        plane.data.materials.append(floor_material)
    
    for j in range(h):
        bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(center_x, y + j + 0.5, 0))
        plane = bpy.context.active_object
        objs.append(plane)
        add_uvs(plane, 1, 1)
        plane.data.materials.append(floor_material)

    return objs

def create_wall(x, y, dir_x, dir_y, rect_x, rect_y, rect_w, rect_h, wall_material):
    wall = None
    if dir_x == 1 and dir_y == 0:
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x + 0.5, y, 0.5))
        wall = bpy.context.active_object
        wall.rotation_euler[0] = math.radians(90)
        if y == rect_y:
            flip_wall_normals(wall)
    elif dir_x == 0 and dir_y == 1:
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y + 0.5, 0.5))
        wall = bpy.context.active_object
        wall.rotation_euler[0] = math.radians(90)
        wall.rotation_euler[2] = math.radians(90)
        if x != rect_x:
            flip_wall_normals(wall)
    elif dir_x == -1 and dir_y == 0:
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x - 0.5, y, 0.5))
        wall = bpy.context.active_object
        wall.rotation_euler[0] = math.radians(90)
    elif dir_x == 0 and dir_y == -1:
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y - 0.5, 0.5))
        wall = bpy.context.active_object
        wall.rotation_euler[0] = math.radians(90)
        wall.rotation_euler[2] = math.radians(90)
    add_uvs(wall, 1, 0.5)
    wall.data.materials.append(wall_material)
    return wall

def create_doorway(x, y, dir_x, dir_y, collection, wall_material):
    # Create a doorway wall with a rectangular hole
    thickness = 0.2
    door_width = 0.5
    door_height = 0.9

    if dir_x != 0:
        # Vertical wall
        bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(x + 0.5, y + 0.5, 0.5))
        doorway = bpy.context.active_object
        doorway.scale = (thickness, 1, 1)
    elif dir_y != 0:
        # Horizontal wall
        bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(x + 0.5, y + 0.5, 0.5))
        doorway = bpy.context.active_object
        doorway.scale = (1, thickness, 1)

    # Create the hole
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(x + 0.5, y + 0.5, 0.45))
    hole = bpy.context.active_object
    hole.scale = (door_width, door_width, door_height)
    collection.objects.link(hole)

    # Apply the boolean modifier
    bpy.context.view_layer.objects.active = doorway
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].operation = 'DIFFERENCE'
    bpy.context.object.modifiers["Boolean"].object = hole
    bpy.ops.object.modifier_apply(modifier="Boolean")
    bpy.data.objects.remove(hole)

    # Manually set UVs for the doorway
    bpy.context.view_layer.objects.active = doorway
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.reset()
    bpy.ops.object.mode_set(mode='OBJECT')

    uv_layer = doorway.data.uv_layers.active.data

    for poly in doorway.data.polygons:
        normal = poly.normal
        # Reset UVs for each polygon before setting new UVs
        for loop_index in poly.loop_indices:
            uv = uv_layer[loop_index].uv

        # Now set the UVs based on orientation and adjust for thickness
        for loop_index in poly.loop_indices:
            uv = uv_layer[loop_index].uv
            vertex = doorway.data.vertices[doorway.data.loops[loop_index].vertex_index].co

            if dir_x != 0:  # Vertical wall
                if abs(normal.z) > 0.99:  # Faces on the thickness axis
                    uv[1] = (vertex.y - 0.5) * 2
                    uv[0] = vertex.x / 4
                elif abs(normal.y) > 0.99:  # Faces on the thickness axis
                    uv[1] = (vertex.z - 0.5) * 2
                    uv[0] = vertex.x / 4
                else:  # Other faces
                    uv[0] = vertex.y  # Width along the Y-axis
                    uv[1] = vertex.z / 0.5  # Height along the Z-axis (64x32 texture)
            if dir_y != 0:  # Horizontal wall
                if abs(normal.z) > 0.99:  # Faces on the thickness axis
                    uv[1] = (vertex.x - 0.5) * 2
                    uv[0] = vertex.y / 4
                elif abs(normal.x) > 0.99:  # Faces on the thickness axis
                    uv[1] = (vertex.z - 0.5) * 2
                    uv[0] = vertex.y / 4
                else:  # Other faces
                    uv[0] = vertex.x  # Width along the X-axis
                    uv[1] = vertex.z / 0.5  # Height along the Z-axis (64x32 texture)

    doorway.data.materials.append(wall_material)
    collection.objects.link(doorway)
    return doorway


def flip_wall_normals(wall):
    bpy.context.view_layer.objects.active = wall
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode='OBJECT')

def keep_cardinal_walls(rect):
    cardinal_walls = []
    x, y, w, h = rect['x'], rect['y'], rect['w'], rect['h']
    cardinal_positions = [
        (x + w // 2, y),
        (x + w // 2, y + h),
        (x, y + h // 2),
        (x + w, y + h // 2)
    ]

    for wall in rect['walls']:
        wall_pos = (wall['x'], wall['y'])
        if wall_pos in cardinal_positions:
            cardinal_walls.append(wall)

    return cardinal_walls

def add_uvs(obj, width, height):
    if not obj.data.uv_layers:
        obj.data.uv_layers.new()
    
    uv_layer = obj.data.uv_layers.active.data
    for poly in obj.data.polygons:
        for loop_index in poly.loop_indices:
            uv = uv_layer[loop_index].uv
            vertex = obj.data.vertices[obj.data.loops[loop_index].vertex_index].co
            uv[0] = (vertex.x - obj.location.x) / width
            uv[1] = (vertex.y - obj.location.y) / height

def merge_objects(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    objs[0].name = name
    return objs[0]

def process_json_file(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    clear_default_scene()
    
    collection_name = os.path.splitext(os.path.basename(json_file))[0]
    collection = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(collection)

    floor_material, wall_material = create_materials()

    room_objects = {}

    for rect in data['rects']:
        objects_to_merge = []

        if 'rotunda' in rect and rect['rotunda']:
            quadrant_objs, quadrant_walls = create_rotunda_quadrants(rect, collection, floor_material=floor_material, wall_material=wall_material)
            objects_to_merge.extend(quadrant_objs)
            objects_to_merge.extend(quadrant_walls)
            objects_to_merge.extend(create_rotunda_plus(rect['x'], rect['y'], rect['w'], rect['h'], floor_material=floor_material))

            rect['walls'] = keep_cardinal_walls(rect)
            if 'walls' in rect:
                for wall in rect['walls']:
                    objects_to_merge.append(create_wall(wall['x'], wall['y'], wall['dir']['x'], wall['dir']['y'], rect['x'], rect['y'], rect['w'], rect['h'], wall_material=wall_material))
        else:
            objects_to_merge.append(create_floor(rect['x'], rect['y'], rect['w'], rect['h'], floor_material=floor_material))
            if 'walls' in rect:
                for wall in rect['walls']:
                    objects_to_merge.append(create_wall(wall['x'], wall['y'], wall['dir']['x'], wall['dir']['y'], rect['x'], rect['y'], rect['w'], rect['h'], wall_material=wall_material))

        if objects_to_merge:
            room_name = f"Room_{rect['x']}_{rect['y']}"
            merged_object = merge_objects(objects_to_merge, room_name)
            room_objects[room_name] = merged_object.name

    for door in data.get('doors', []):
        doorway = create_doorway(door['x'], door['y'], door['dir']['x'], door['dir']['y'], collection, wall_material)
        room_name = None
        for rect in data['rects']:
            if rect['x'] <= door['x'] < rect['x'] + rect['w'] and rect['y'] <= door['y'] < rect['y'] + rect['h']:
                room_name = f"Room_{rect['x']}_{rect['y']}"
                break

        if room_name and room_name in room_objects:
            room_obj = bpy.data.objects.get(room_objects[room_name])
            if room_obj:
                bpy.context.view_layer.objects.active = room_obj
                doorway.select_set(True)
                room_obj.select_set(True)
                bpy.ops.object.join()
                room_objects[room_name] = bpy.context.view_layer.objects.active.name

    output_file_blend = json_file.replace('.json', '.blend')
    output_file_fbx = json_file.replace('.json', '.fbx')
    #bpy.ops.wm.save_as_mainfile(filepath=output_file_blend)
    bpy.ops.export_scene.fbx(filepath=output_file_fbx, use_selection=False)

def main():
    for json_file in os.listdir('.'):
        if json_file.endswith('.json'):
            process_json_file(json_file)

if __name__ == "__main__":
    main()

