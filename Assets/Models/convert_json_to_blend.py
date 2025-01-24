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

def create_circle_quadrant(x, y, radius, collection, quadrant=1, floor_material=None, wall_material=None, levels=1):
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
        walls.extend(create_vertical_face(start_vert, end_vert, collection, wall_material, levels))

    return obj, walls



def create_vertical_face(start_vert, end_vert, collection, wall_material=None, levels=1):
    walls = []
    width = math.sqrt((end_vert[0] - start_vert[0]) ** 2 + (end_vert[1] - start_vert[1]) ** 2)
    height = 0.5

    for level in range(levels + 1):
        z_offset = level
        
        mesh = bpy.data.meshes.new(f"Wall_Level_{level}")
        obj = bpy.data.objects.new(f"Wall_Level_{level}", mesh)
        collection.objects.link(obj)

        verts = [
            (start_vert[0], start_vert[1], z_offset),
            (end_vert[0], end_vert[1], z_offset),
            (end_vert[0], end_vert[1], z_offset + 1),
            (start_vert[0], start_vert[1], z_offset + 1)
        ]
        edges = []
        faces = [(0, 1, 2, 3)]

        mesh.from_pydata(verts, edges, faces)
        mesh.update()

        add_rotunda_uvs(obj, width, height)
        if wall_material:
            obj.data.materials.append(wall_material)
        
        walls.append(obj)

    return walls


def create_rotunda_quadrants(rect, collection, floor_material=None, wall_material=None):
    x, y, w, h = rect['x'], rect['y'], rect['w'], rect['h']
    radius = (min(w, h) - 1) / 2
    offset = h / 2 - 0.5

    objs = []
    walls = []
    levels = rect.get('ceiling', 1)  # default to 1 if ceiling is not specified
    obj, quadrant_walls = create_circle_quadrant(x + w - offset, y + h - offset, radius, collection, quadrant=1, floor_material=floor_material, wall_material=wall_material, levels=levels)
    objs.append(obj)
    walls.extend(quadrant_walls)
    obj, quadrant_walls = create_circle_quadrant(x + offset, y + h - offset, radius, collection, quadrant=2, floor_material=floor_material, wall_material=wall_material, levels=levels)
    objs.append(obj)
    walls.extend(quadrant_walls)
    obj, quadrant_walls = create_circle_quadrant(x + offset, y + offset, radius, collection, quadrant=3, floor_material=floor_material, wall_material=wall_material, levels=levels)
    objs.append(obj)
    walls.extend(quadrant_walls)
    obj, quadrant_walls = create_circle_quadrant(x + w - offset, y + offset, radius, collection, quadrant=4, floor_material=floor_material, wall_material=wall_material, levels=levels)
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
            uv[1] = uv[1] / height * 0.5

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

def create_wall(x, y, dir_x, dir_y, rect_x, rect_y, rect_w, rect_h, wall_material, level=0):
    wall = None
    height_offset = level  # Each level is 1 unit above the previous
    if dir_x == 1 and dir_y == 0:  # West-facing wall
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x + 0.5, y, 0.5 + height_offset))
        wall = bpy.context.active_object
        wall.rotation_euler[0] = math.radians(90)
        if y == rect_y:  # West side
            flip_wall_normals(wall)
    elif dir_x == 0 and dir_y == 1:  # North-facing wall
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y + 0.5, 0.5 + height_offset))
        wall = bpy.context.active_object
        wall.rotation_euler[0] = math.radians(90)
        wall.rotation_euler[2] = math.radians(90)
        if x != rect_x:  # North side
            flip_wall_normals(wall)
    elif dir_x == -1 and dir_y == 0:  # East-facing wall
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x - 0.5, y, 0.5 + height_offset))
        wall = bpy.context.active_object
        wall.rotation_euler[0] = math.radians(90)
    elif dir_x == 0 and dir_y == -1:  # South-facing wall
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y - 0.5, 0.5 + height_offset))
        wall = bpy.context.active_object
        wall.rotation_euler[0] = math.radians(90)
        wall.rotation_euler[2] = math.radians(90)
    add_uvs(wall, 1, 1)  # Accounts for Daggerfall dungeon wall textures being 64x32
    wall.data.materials.append(wall_material)
    return wall

def create_doorway(x, y, dir_x, dir_y, collection, wall_material):
    # Create a doorway wall with a rectangular hole
    thickness = 0.2
    door_width = 0.48
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
                if abs(normal.z) > 0.99:
                    uv[1] = (vertex.y - 0.5)
                    uv[0] = vertex.x / 4
                elif abs(normal.y) > 0.99:  # Faces on the thickness axis
                    uv[1] = (vertex.z - 0.5)
                    uv[0] = vertex.x / 4
                else:  # Other faces
                    uv[0] = vertex.y  # Width along the Y-axis
                    uv[1] = vertex.z # Height along the Z-axis (/ 0.5 for 64x32 texture)
            if dir_y != 0:  # Horizontal wall
                if abs(normal.z) > 0.99:
                    uv[1] = (vertex.x - 0.5)
                    uv[0] = vertex.y / 4
                elif abs(normal.x) > 0.99:  # Faces on the thickness axis
                    uv[1] = (vertex.z - 0.5)
                    uv[0] = vertex.y / 4
                else:  # Other faces
                    uv[0] = vertex.x  # Width along the X-axis
                    uv[1] = vertex.z  # Height along the Z-axis (/ 0.5 for 64x32 texture)

    doorway.data.materials.append(wall_material)
    collection.objects.link(doorway)
    return doorway


def flip_wall_normals(wall):
    if isinstance(wall, list):
        for w in wall:
            bpy.context.view_layer.objects.active = w
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.flip_normals()
            bpy.ops.object.mode_set(mode='OBJECT')
    else:
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

def add_uvs_pyramid(obj, base_width, base_height, vaulted_height, texture_unit_size=1):
    """
    Adds UV mapping to a truncated pyramid with a fixed height for consistent scaling.
    
    Parameters:
    - obj: The truncated pyramid object.
    - base_width: Width of the base of the pyramid.
    - base_height: Height of the base of the pyramid.
    - vaulted_height: Fixed height of the pyramid.
    - texture_unit_size: The size of a single unit of texture in world coordinates (default = 1).
    """
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UVMap")
    
    uv_layer = obj.data.uv_layers.active.data
    
    for poly in obj.data.polygons:
        for loop_index in poly.loop_indices:
            uv = uv_layer[loop_index].uv
            vertex = obj.data.vertices[obj.data.loops[loop_index].vertex_index].co
            
            if poly.normal.z == 0:  # Side faces (vertical)
                # Map X to U and Z to V, scaled by texture_unit_size
                uv[0] = vertex.x / texture_unit_size
                uv[1] = vertex.z / texture_unit_size
            else:  # Top face (horizontal)
                # Map X to U and Y to V, scaled by texture_unit_size
                uv[0] = vertex.x / texture_unit_size
                uv[1] = vertex.y / texture_unit_size

def create_truncated_pyramid_ceiling(x, y, w, h, room_ceiling_height, ceiling_material, top_scale=0.5, vaulted_ceiling_height=0.5):
    """
    Creates a truncated pyramid ceiling with a fixed height to minimize texture stretching.
    
    Parameters:
    - x, y: Position of the room's bottom-left corner.
    - w, h: Dimensions of the room.
    - room_ceiling_height: Height of the room's ceiling (base of the pyramid).
    - ceiling_material: Material to apply to the pyramid.
    - top_scale: Ratio of the top's width/height to the base's width/height (default = 0.5).
    - vaulted_ceiling_height: Fixed height for all vaulted ceilings (default = 0.5).
    """
    # Adjust vaulted_ceiling_height if either x or y is 1
    if w == 1 or h == 1:
        vaulted_ceiling_height = 0.25

    # Create a new mesh and object for the ceiling
    mesh = bpy.data.meshes.new("TruncatedPyramidCeiling")
    ceiling_obj = bpy.data.objects.new("TruncatedPyramidCeiling", mesh)
    bpy.context.scene.collection.objects.link(ceiling_obj)
    
    # Base vertices (matching room's dimensions)
    base_verts = [
        (x, y, room_ceiling_height),               # Bottom-left
        (x + w, y, room_ceiling_height),           # Bottom-right
        (x + w, y + h, room_ceiling_height),       # Top-right
        (x, y + h, room_ceiling_height)            # Top-left
    ]
    
    # Top vertices (scaled down from base, fixed height for the top)
    top_verts = [
        (x + w * (1 - top_scale) / 2, y + h * (1 - top_scale) / 2, room_ceiling_height + vaulted_ceiling_height),  # Bottom-left
        (x + w * (1 + top_scale) / 2, y + h * (1 - top_scale) / 2, room_ceiling_height + vaulted_ceiling_height),  # Bottom-right
        (x + w * (1 + top_scale) / 2, y + h * (1 + top_scale) / 2, room_ceiling_height + vaulted_ceiling_height),  # Top-right
        (x + w * (1 - top_scale) / 2, y + h * (1 + top_scale) / 2, room_ceiling_height + vaulted_ceiling_height)   # Top-left
    ]
    
    # Combine vertices
    verts = base_verts + top_verts
    
    # Faces (connect base and top vertices, clockwise for inward normals)
    faces = [
        (0, 4, 5, 1),  # Bottom-right face
        (1, 5, 6, 2),  # Top-right face
        (2, 6, 7, 3),  # Top-left face
        (3, 7, 4, 0),  # Bottom-left face
        (7, 6, 5, 4)   # Top face (counter-clockwise for inward normals)
    ]
    
    # Create the mesh
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    # Add UV mapping with consistent scaling
    add_uvs_pyramid(ceiling_obj, w, h, vaulted_ceiling_height)
    
    # Assign material
    if ceiling_material:
        ceiling_obj.data.materials.append(ceiling_material)
    
    return ceiling_obj

def flip_normals(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode='OBJECT')

def create_ceiling(x, y, w, h, ceiling_height, ceiling_material):
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=False, align='WORLD', location=(x + w/2, y + h/2, ceiling_height))
    plane = bpy.context.active_object
    plane.scale[0] = w
    plane.scale[1] = h
    bpy.ops.object.transform_apply(location=False, scale=True, rotation=False)
    add_uvs(plane, 1, 1)
    plane.data.materials.append(ceiling_material)
    flip_normals(plane)
    return plane

def add_ceiling_to_room(rect, collection, ceiling_material):
    x, y, w, h, ceiling = rect['x'], rect['y'], rect['w'], rect['h'], rect.get('ceiling', 1)
    ceiling_height = ceiling + 1
    pyramid_ceiling = create_truncated_pyramid_ceiling(x, y, w, h, ceiling_height, ceiling_material)
    collection.objects.link(pyramid_ceiling)
    return pyramid_ceiling

def create_circle_quadrant_ceiling(x, y, radius, collection, quadrant=1, ceiling_material=None, ceiling_height=1):
    segment_length = 1.0
    arc_length = (math.pi / 2) * radius
    segments = max(1, int(arc_length / segment_length))

    angle_offset = math.pi / 2
    angle_start = (quadrant - 1) * angle_offset
    angle_end = quadrant * angle_offset

    mesh = bpy.data.meshes.new("CircleQuadrantCeiling")
    obj = bpy.data.objects.new("CircleQuadrantCeiling", mesh)
    collection.objects.link(obj)

    verts = [(x, y, ceiling_height)]
    verts += [(x + math.cos(angle_start + angle_offset * i / segments) * radius, 
               y + math.sin(angle_start + angle_offset * i / segments) * radius, ceiling_height) 
              for i in range(segments + 1)]
    edges = []
    faces = [tuple(range(len(verts)))]

    mesh.from_pydata(verts, edges, faces)
    mesh.update()
    add_uvs(obj, 1, 1)

    if ceiling_material:
        obj.data.materials.append(ceiling_material)

    return obj

def create_truncated_circle_quadrant_ceiling(x, y, radius, collection, quadrant=1, ceiling_material=None, room_ceiling_height=2.5, fixed_height=1.0):
    """
    Creates a truncated pyramid ceiling for a circle quadrant with inward-facing normals and specialized handling for 3x3, 4x4, and 5x5 rooms.
    
    Parameters:
    - x, y: The origin of the quadrant.
    - radius: The radius of the quadrant base.
    - collection: The Blender collection to link the object to.
    - quadrant: Specifies which quadrant of the circle (1 to 4).
    - ceiling_material: The material to apply.
    - room_ceiling_height: Height of the room's ceiling (base of the pyramid).
    - fixed_height: Fixed height for the top of the pyramid (default = 1.0).
    """
    segment_length = 1.0
    arc_length = (math.pi / 2) * radius
    segments = max(1, int(arc_length / segment_length))

    angle_offset = math.pi / 2
    angle_start = (quadrant - 1) * angle_offset
    angle_end = quadrant * angle_offset

    mesh = bpy.data.meshes.new("TruncatedCircleQuadrantCeiling")
    obj = bpy.data.objects.new("TruncatedCircleQuadrantCeiling", mesh)
    collection.objects.link(obj)

    # Determine room size handling
    is_small_room = radius == 1.0  # 3x3 rooms
    #is_medium_room = radius == 2.0  # 4x4 rooms
    is_large_room = radius >= 3.0  # 5x5 rooms

    # Create base vertices (curve of the quadrant)
    base_verts = [(x, y, room_ceiling_height)]  # Center point at the base
    base_verts += [
        (x + math.cos(angle_start + angle_offset * i / segments) * radius,
         y + math.sin(angle_start + angle_offset * i / segments) * radius,
         room_ceiling_height)
        for i in range(segments + 1)
    ]

    # Create top vertices
    if is_small_room:
        # For 3x3 rooms, create a flat 1x1 square in the center
        top_verts = [
            (x + 0.5, y + 0.5, room_ceiling_height + fixed_height),  # Center of the flat square
            (x + 0.5 + math.cos(angle_start) * 0.5, y + 0.5 + math.sin(angle_start) * 0.5, room_ceiling_height + fixed_height),
            (x + 0.5 + math.cos(angle_end) * 0.5, y + 0.5 + math.sin(angle_end) * 0.5, room_ceiling_height + fixed_height)
        ]
    elif is_large_room:
        # For 5x5 rooms, create a flat 4x4 square in the center
        truncation_factor = 4 / (2 * radius)  # Scale down to fit a 4x4 square
        top_verts = [(x, y, room_ceiling_height + fixed_height)]  # Center point at the top
        top_verts += [
            (x + math.cos(angle_start + angle_offset * i / segments) * radius * truncation_factor,
             y + math.sin(angle_start + angle_offset * i / segments) * radius * truncation_factor,
             room_ceiling_height + fixed_height)
            for i in range(segments + 1)
        ]
    else:
        # For 4x4 rooms (and others not explicitly handled), use the default technique
        top_verts = [(x, y, room_ceiling_height + fixed_height)]  # Center point at the top
        top_verts += [
            (x + math.cos(angle_start + angle_offset * i / segments) * radius * 0.5,
             y + math.sin(angle_start + angle_offset * i / segments) * radius * 0.5,
             room_ceiling_height + fixed_height)
            for i in range(segments + 1)
        ]

    # Combine vertices
    verts = base_verts + top_verts

    # Create faces
    faces = []
    base_offset = 0
    top_offset = len(base_verts)

    if is_small_room:
        # Raise the center vertex
        verts[base_offset] = (verts[base_offset][0],  # x-coordinate (unchanged)
                              verts[base_offset][1],  # y-coordinate (unchanged)
                              verts[base_offset][2] + fixed_height)  # z-coordinate (raised)

        # For 3x3 rooms, connect the base to the small center square
        for i in range(1, len(base_verts) - 1):
            faces.append((i + 1, i, base_offset))  # Reverse winding order
    else:
        # For larger rooms, connect the base to the full top
        for i in range(1, len(base_verts) - 1):
            faces.append((top_offset + i + 1, top_offset + i, top_offset))  # Top triangle
            faces.append((top_offset + i + 1, i + 1, i, top_offset + i))   # Side quadrilateral

    # Create the mesh
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    # Add UVs
    add_uvs_pyramid(obj, radius, radius, fixed_height)

    # Apply material
    if ceiling_material:
        obj.data.materials.append(ceiling_material)

    return obj

def create_rotunda_plus_ceiling(x, y, w, h, ceiling_material, ceiling_height):
    """
    Creates a plus-shaped ceiling with sloping arms that connect to the truncated circle quadrants.
    
    Parameters:
    - x, y: Bottom-left corner of the room.
    - w, h: Dimensions of the room.
    - ceiling_material: Material to apply to the ceiling.
    - ceiling_height: The final height at the center of the plus.
    """
    objs = []
    center_x = x + w / 2
    center_y = y + h / 2
    base_height = ceiling_height - 0.5  # Height of the edges
    slope_height = ceiling_height      # Height at the center

    # Create horizontal arms of the plus
    for i in range(w):
        start_x = x + i
        end_x = start_x + 1
        if i == 0:  # Westmost square
            verts = [
                (start_x, center_y - 0.5, base_height + 0.5),
                (end_x, center_y - 0.5, slope_height + 0.5),
                (end_x, center_y + 0.5, slope_height + 0.5),
                (start_x, center_y + 0.5, base_height + 0.5),
            ]
        elif i == w - 1:  # Eastmost square
            verts = [
                (start_x, center_y - 0.5, slope_height + 0.5),
                (end_x, center_y - 0.5, base_height + 0.5),
                (end_x, center_y + 0.5, base_height + 0.5),
                (start_x, center_y + 0.5, slope_height + 0.5),
            ]
        else:  # Flat squares in the middle
            verts = [
                (start_x, center_y - 0.5, base_height + 1),
                (end_x, center_y - 0.5, base_height + 1),
                (end_x, center_y + 0.5, base_height + 1),
                (start_x, center_y + 0.5, base_height + 1),
            ]
        mesh = bpy.data.meshes.new(f"HorizontalArm_{i}")
        obj = bpy.data.objects.new(f"HorizontalArm_{i}", mesh)
        mesh.from_pydata(verts, [], [(3, 2, 1, 0)])
        mesh.update()

        # Add UV mapping
        add_uvs(obj, 1, 1)

        # Apply material
        if ceiling_material:
            obj.data.materials.append(ceiling_material)

        objs.append(obj)

    # Create vertical arms of the plus
    for j in range(h):
        start_y = y + j
        end_y = start_y + 1
        if j == 0:  # Southmost square
            verts = [
                (center_x - 0.5, start_y, base_height + 0.5),
                (center_x + 0.5, start_y, base_height + 0.5),
                (center_x + 0.5, end_y, slope_height + 0.5),
                (center_x - 0.5, end_y, slope_height + 0.5),
            ]
        elif j == h - 1:  # Northmost square
            verts = [
                (center_x - 0.5, start_y, slope_height + 0.5),
                (center_x + 0.5, start_y, slope_height + 0.5),
                (center_x + 0.5, end_y, base_height + 0.5),
                (center_x - 0.5, end_y, base_height + 0.5),
            ]
        else:  # Flat squares in the middle
            verts = [
                (center_x - 0.5, start_y, base_height + 1),
                (center_x + 0.5, start_y, base_height + 1),
                (center_x + 0.5, end_y, base_height + 1),
                (center_x - 0.5, end_y, base_height + 1),
            ]
        mesh = bpy.data.meshes.new(f"VerticalArm_{j}")
        obj = bpy.data.objects.new(f"VerticalArm_{j}", mesh)
        mesh.from_pydata(verts, [], [(3, 2, 1, 0)])
        mesh.update()

        # Add UV mapping
        add_uvs(obj, 1, 1)

        # Apply material
        if ceiling_material:
            obj.data.materials.append(ceiling_material)

        objs.append(obj)

    return objs

def add_rotunda_ceiling(rect, collection, ceiling_material):
    """
    Adds a rotunda ceiling consisting of truncated circle quadrant ceilings and a central plus ceiling.

    Parameters:
    - rect: The dictionary containing room parameters (x, y, w, h, ceiling).
    - collection: The Blender collection to which the ceiling objects will be linked.
    - ceiling_material: The material to be applied to the ceiling.
    """
    x, y, w, h, ceiling = rect['x'], rect['y'], rect['w'], rect['h'], rect.get('ceiling', 1)
    room_ceiling_height = ceiling + 1  # Adjust height to start at the top of the walls
    fixed_height = 0.5

    objs = []
    # Create truncated pyramid ceilings for circle quadrants
    radius = (min(w, h) - 1) / 2
    obj = create_truncated_circle_quadrant_ceiling(
        x + w - (h / 2 - 0.5), 
        y + h - (h / 2 - 0.5), 
        radius, 
        collection, 
        quadrant=1, 
        ceiling_material=ceiling_material, 
        room_ceiling_height=room_ceiling_height, 
        fixed_height=fixed_height
    )
    objs.append(obj)

    obj = create_truncated_circle_quadrant_ceiling(
        x + (h / 2 - 0.5), 
        y + h - (h / 2 - 0.5), 
        radius, 
        collection, 
        quadrant=2, 
        ceiling_material=ceiling_material, 
        room_ceiling_height=room_ceiling_height, 
        fixed_height=fixed_height
    )
    objs.append(obj)

    obj = create_truncated_circle_quadrant_ceiling(
        x + (h / 2 - 0.5), 
        y + (h / 2 - 0.5), 
        radius, 
        collection, 
        quadrant=3, 
        ceiling_material=ceiling_material, 
        room_ceiling_height=room_ceiling_height, 
        fixed_height=fixed_height
    )
    objs.append(obj)

    obj = create_truncated_circle_quadrant_ceiling(
        x + w - (h / 2 - 0.5), 
        y + (h / 2 - 0.5), 
        radius, 
        collection, 
        quadrant=4, 
        ceiling_material=ceiling_material, 
        room_ceiling_height=room_ceiling_height, 
        fixed_height=fixed_height
    )
    objs.append(obj)

    # Cover the remaining part with a plus-shaped ceiling
    plus_objs = create_rotunda_plus_ceiling(x, y, w, h, ceiling_material, room_ceiling_height)
    objs.extend(plus_objs)

    # Ensure all parts are linked to the collection
    for obj in objs:
        if obj.name not in collection.objects:
            collection.objects.link(obj)

    return objs

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
    ceiling_material = bpy.data.materials.new(name="CeilingMaterial")

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
                    objects_to_merge.append(create_wall(wall['x'], wall['y'], wall['dir']['x'], wall['dir']['y'], rect['x'], rect['y'], rect['w'], rect['h'], wall_material=wall_material, level=wall['level']))
        else:
            objects_to_merge.append(create_floor(rect['x'], rect['y'], rect['w'], rect['h'], floor_material=floor_material))
            if 'walls' in rect:
                for wall in rect['walls']:
                    objects_to_merge.append(create_wall(wall['x'], wall['y'], wall['dir']['x'], wall['dir']['y'], rect['x'], rect['y'], rect['w'], rect['h'], wall_material=wall_material, level=wall['level']))

        if objects_to_merge:
            room_name = f"Room_{rect['x']}_{rect['y']}"
            merged_object = merge_objects(objects_to_merge, room_name)
            room_objects[room_name] = merged_object.name

        # Add ceiling to room
        ceiling_objs = []
        if 'rotunda' in rect and rect['rotunda']:
            ceiling_objs = add_rotunda_ceiling(rect, collection, ceiling_material)
        else:
            # Check the "vault" key to determine the type of ceiling
            if rect.get('vault', 0) == 1:  # Vaulted ceiling
                ceiling_objs.append(create_truncated_pyramid_ceiling(
                    rect['x'], rect['y'], rect['w'], rect['h'], rect.get('ceiling', 1) + 1, ceiling_material
                ))
            else:  # Standard flat ceiling
                ceiling_objs.append(create_ceiling(
                    rect['x'], rect['y'], rect['w'], rect['h'], rect.get('ceiling', 1) + 1, ceiling_material
                ))

        if room_name and room_name in room_objects:
            room_obj = bpy.data.objects.get(room_objects[room_name])
            if room_obj:
                bpy.context.view_layer.objects.active = room_obj
                for ceiling in ceiling_objs:
                    ceiling.select_set(True)
                room_obj.select_set(True)
                bpy.ops.object.join()
                room_objects[room_name] = bpy.context.view_layer.objects.active.name

    for door in data.get('doors', []):
        # Skip doors that don't meet the criteria
        if not (door.get('type') in [1, 2, 4, 6, 7] or (door['x'] == 0 and door['y'] == 0)):
            continue

        # Create the doorway if conditions are met
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

