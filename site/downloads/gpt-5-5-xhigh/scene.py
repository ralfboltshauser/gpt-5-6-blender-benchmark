#!/usr/bin/env python3
"""Build a stylized low-poly forest cabin scene in Blender.

The script is deliberately procedural so the resulting .blend stays editable:
objects are named by role, organized into collections, and built from simple
mesh primitives rather than a flat image projection.
"""

from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
BLEND_PATH = ROOT / "low_poly_forest_cabin.blend"
RENDER_PATH = ROOT / "preview.png"
SEED = 55891
rng = random.Random(SEED)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for datablock in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for item in list(datablock):
            if item.users == 0:
                datablock.remove(item)


def make_mat(name: str, color, roughness: float = 0.75, metallic: float = 0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
    return mat


def make_emission_mat(name: str, color, strength: float):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = color
    emission.inputs["Strength"].default_value = strength
    output = nodes.new("ShaderNodeOutputMaterial")
    mat.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return mat


def make_transparent_mat(name: str, color, alpha: float):
    mat = make_mat(name, (color[0], color[1], color[2], alpha), 0.9)
    mat.blend_method = "BLEND"
    mat.use_screen_refraction = False
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf and "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = alpha
    return mat


MATS = {}


def init_materials() -> None:
    MATS.update(
        {
            "grass_a": make_mat("grass patch warm green", (0.33, 0.48, 0.20, 1)),
            "grass_b": make_mat("grass patch yellow green", (0.43, 0.56, 0.23, 1)),
            "grass_c": make_mat("grass patch deep green", (0.22, 0.36, 0.17, 1)),
            "path_a": make_mat("faceted dirt path honey", (0.77, 0.56, 0.34, 1)),
            "path_b": make_mat("faceted path ocher", (0.64, 0.45, 0.28, 1)),
            "path_c": make_mat("faceted path pale stone", (0.86, 0.68, 0.45, 1)),
            "wood_a": make_mat("cabin log warm pine", (0.60, 0.32, 0.13, 1)),
            "wood_b": make_mat("cabin log amber", (0.76, 0.42, 0.17, 1)),
            "wood_dark": make_mat("dark wood gaps and trim", (0.25, 0.13, 0.07, 1)),
            "wood_end": make_mat("fresh log cut faces", (0.78, 0.49, 0.24, 1)),
            "roof_a": make_mat("roof shingle charcoal brown", (0.17, 0.16, 0.16, 1)),
            "roof_b": make_mat("roof shingle warm grey", (0.24, 0.22, 0.20, 1)),
            "roof_c": make_mat("roof shingle blue grey", (0.13, 0.17, 0.19, 1)),
            "stone_a": make_mat("foundation stone cool grey", (0.46, 0.45, 0.43, 1)),
            "stone_b": make_mat("foundation stone pale grey", (0.62, 0.60, 0.56, 1)),
            "stone_c": make_mat("foundation stone dark grey", (0.34, 0.35, 0.36, 1)),
            "pine_a": make_mat("pine needles sunlit", (0.33, 0.48, 0.22, 1)),
            "pine_b": make_mat("pine needles mid", (0.22, 0.38, 0.20, 1)),
            "pine_c": make_mat("pine needles deep", (0.12, 0.29, 0.18, 1)),
            "trunk": make_mat("pine trunk brown", (0.32, 0.18, 0.09, 1)),
            "window_glow": make_emission_mat("warm window glass emission", (1.0, 0.44, 0.05, 1), 2.35),
            "lantern_glow": make_emission_mat("lantern core emission", (1.0, 0.58, 0.15, 1), 4.5),
            "metal_dark": make_mat("blackened iron", (0.04, 0.035, 0.03, 1), 0.55),
            "mushroom_red": make_mat("mushroom cap red orange", (0.95, 0.20, 0.08, 1)),
            "mushroom_stem": make_mat("mushroom stem cream", (0.86, 0.75, 0.56, 1)),
            "mountain_near": make_emission_mat("near low poly mountain", (0.62, 0.55, 0.44, 1), 0.55),
            "mountain_far": make_emission_mat("far hazy mountain", (0.82, 0.70, 0.56, 1), 0.48),
            "sky_sunset": make_emission_mat("peach sunset sky backdrop", (1.0, 0.66, 0.38, 1), 0.85),
            "sky_haze": make_transparent_mat("warm valley haze planes", (0.95, 0.70, 0.45, 1), 0.22),
        }
    )


def collection(name: str):
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)
    return coll


COLLS = {}


def init_collections() -> None:
    for name in [
        "terrain",
        "cabin",
        "porch",
        "roof",
        "chimney",
        "windows_and_lamps",
        "forest",
        "foreground_props",
        "mountains",
        "lighting_camera",
    ]:
        COLLS[name] = collection(name)


def link_to(obj, coll_name: str):
    coll = COLLS.get(coll_name)
    if not coll:
        return obj
    if obj.name not in coll.objects:
        coll.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)
    return obj


def assign_mat(obj, mat) -> None:
    if mat:
        obj.data.materials.append(mat)


def apply_scale(obj) -> None:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)


def soften(obj, width: float = 0.025) -> None:
    if width <= 0:
        return
    bevel = obj.modifiers.new("small bevels for toy-like edge highlights", "BEVEL")
    bevel.width = width
    bevel.segments = 1
    bevel.affect = "EDGES"
    obj.modifiers.new("weighted normals", "WEIGHTED_NORMAL")


def cube(name: str, loc, dims, mat=None, rot=(0, 0, 0), coll="cabin", bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    assign_mat(obj, mat)
    apply_scale(obj)
    soften(obj, bevel)
    link_to(obj, coll)
    return obj


def cylinder(
    name: str,
    loc,
    radius: float,
    depth: float,
    mat=None,
    vertices: int = 8,
    rot=(0, 0, 0),
    coll="cabin",
    bevel=0.0,
    scale=(1, 1, 1),
):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    assign_mat(obj, mat)
    apply_scale(obj)
    soften(obj, bevel)
    link_to(obj, coll)
    return obj


def cone(
    name: str,
    loc,
    radius1: float,
    radius2: float,
    depth: float,
    mat=None,
    vertices: int = 6,
    rot=(0, 0, 0),
    coll="forest",
    scale=(1, 1, 1),
):
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices,
        radius1=radius1,
        radius2=radius2,
        depth=depth,
        location=loc,
        rotation=rot,
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    assign_mat(obj, mat)
    apply_scale(obj)
    link_to(obj, coll)
    return obj


def ico(name: str, loc, scale, mat=None, coll="terrain"):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    assign_mat(obj, mat)
    apply_scale(obj)
    link_to(obj, coll)
    return obj


def beam_between(
    name: str,
    start,
    end,
    radius: float,
    mat=None,
    vertices: int = 4,
    coll="cabin",
    bevel=0.0,
):
    start_v = Vector(start)
    end_v = Vector(end)
    vec = end_v - start_v
    mid = (start_v + end_v) * 0.5
    if vec.length == 0:
        return None
    rot = vec.to_track_quat("Z", "Y").to_euler()
    return cylinder(
        name,
        mid,
        radius,
        vec.length,
        mat=mat,
        vertices=vertices,
        rot=rot,
        coll=coll,
        bevel=bevel,
    )


def look_at(obj, target) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def point_segment_distance_xy(p, a, b) -> float:
    px, py = p
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    denom = vx * vx + vy * vy
    if denom == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, (wx * vx + wy * vy) / denom))
    cx, cy = ax + t * vx, ay + t * vy
    return math.hypot(px - cx, py - cy)


PATH_POINTS = [
    (-5.4, -9.2),
    (-4.2, -7.5),
    (-3.0, -6.0),
    (-1.55, -4.85),
    (-0.25, -3.42),
]


def distance_to_path(x: float, y: float) -> float:
    return min(
        point_segment_distance_xy((x, y), PATH_POINTS[i], PATH_POINTS[i + 1])
        for i in range(len(PATH_POINTS) - 1)
    )


def path_width_at_y(y: float) -> float:
    return 1.05 + max(0.0, -y - 4.0) * 0.05


def terrain_height(x: float, y: float) -> float:
    d = distance_to_path(x, y)
    path_sink = -0.05 if d < path_width_at_y(y) else 0.0
    undulate = 0.08 * math.sin(x * 0.75 + y * 0.28) + 0.04 * math.cos(y * 0.9)
    return undulate + path_sink


def create_terrain() -> None:
    x_min, x_max = -12.0, 12.0
    y_min, y_max = -10.0, 11.0
    step = 1.0
    xs = [x_min + i * step for i in range(int((x_max - x_min) / step) + 1)]
    ys = [y_min + i * step for i in range(int((y_max - y_min) / step) + 1)]

    verts = []
    for y in ys:
        for x in xs:
            verts.append((x, y, terrain_height(x, y)))

    faces = []
    material_indices = []
    terrain_mats = [
        MATS["grass_a"],
        MATS["grass_b"],
        MATS["grass_c"],
        MATS["path_a"],
        MATS["path_b"],
        MATS["path_c"],
    ]
    cols = len(xs)
    for yi in range(len(ys) - 1):
        for xi in range(len(xs) - 1):
            v0 = yi * cols + xi
            v1 = v0 + 1
            v2 = v0 + cols
            v3 = v2 + 1
            center_x = (xs[xi] + xs[xi + 1]) * 0.5
            center_y = (ys[yi] + ys[yi + 1]) * 0.5
            d = distance_to_path(center_x, center_y)
            if d < path_width_at_y(center_y):
                mat_i = 3 + int(rng.random() * 3)
            else:
                mat_i = int(rng.random() * 3)
            if rng.random() < 0.5:
                tris = [(v0, v1, v3), (v0, v3, v2)]
            else:
                tris = [(v0, v1, v2), (v1, v3, v2)]
            for tri in tris:
                faces.append(tri)
                material_indices.append(mat_i)

    mesh = bpy.data.meshes.new("triangulated rolling forest floor mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("low poly rolling ground with tan path", mesh)
    for mat in terrain_mats:
        mesh.materials.append(mat)
    for poly, mat_i in zip(mesh.polygons, material_indices):
        poly.material_index = mat_i
    bpy.context.scene.collection.objects.link(obj)
    link_to(obj, "terrain")

    # Individual path pavers give the reference-like faceted cobble surface.
    tile_mats = [MATS["path_a"], MATS["path_b"], MATS["path_c"]]
    count = 0
    for i in range(len(PATH_POINTS) - 1):
        a = Vector((PATH_POINTS[i][0], PATH_POINTS[i][1], 0))
        b = Vector((PATH_POINTS[i + 1][0], PATH_POINTS[i + 1][1], 0))
        seg = b - a
        steps = max(3, int(seg.length / 0.38))
        tangent = Vector((seg.x, seg.y, 0)).normalized()
        normal = Vector((-tangent.y, tangent.x, 0))
        for j in range(steps):
            t = (j + 0.4 + 0.25 * rng.random()) / steps
            center = a.lerp(b, t)
            width = path_width_at_y(center.y) * (0.35 + rng.random() * 0.75)
            center += normal * rng.uniform(-width * 0.55, width * 0.55)
            z = terrain_height(center.x, center.y) + 0.045
            rx = rng.uniform(0.18, 0.42)
            ry = rng.uniform(0.16, 0.38)
            cylinder(
                f"individual angular path stone {count:03d}",
                (center.x, center.y, z),
                1,
                0.045,
                mat=rng.choice(tile_mats),
                vertices=rng.choice([5, 6, 7]),
                rot=(0, 0, rng.random() * math.tau),
                coll="terrain",
                scale=(rx, ry, 1),
            )
            count += 1


def create_mountains() -> None:
    sky_mesh = bpy.data.meshes.new("single warm sky backdrop mesh")
    sky_mesh.from_pydata(
        [(-80, 12.2, -5.0), (80, 12.2, -5.0), (80, 12.2, 25.0), (-80, 12.2, 25.0)],
        [],
        [(0, 1, 2, 3)],
    )
    sky_mesh.update()
    sky = bpy.data.objects.new("flat warm peach sunset backdrop behind mountains", sky_mesh)
    sky.data.materials.append(MATS["sky_sunset"])
    bpy.context.scene.collection.objects.link(sky)
    link_to(sky, "mountains")

    def mountain(name, y, x, width, peak_z, mat, zbase=0.35):
        verts = [
            (x - width * 0.55, y, zbase),
            (x - width * 0.15, y, peak_z * 0.78),
            (x, y, peak_z),
            (x + width * 0.22, y, peak_z * 0.72),
            (x + width * 0.58, y, zbase),
            (x, y - 0.18, zbase - 0.12),
        ]
        faces = [(0, 1, 5), (1, 2, 5), (2, 3, 5), (3, 4, 5), (0, 5, 4)]
        mesh = bpy.data.meshes.new(f"{name} mesh")
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        obj.data.materials.append(mat)
        bpy.context.scene.collection.objects.link(obj)
        link_to(obj, "mountains")
        return obj

    for i, (x, w, h) in enumerate(
        [(-10.0, 7.5, 4.5), (-4.0, 8.0, 5.2), (2.5, 9.0, 5.8), (8.6, 8.2, 5.0)]
    ):
        mountain(f"far hazy polygon mountain {i}", 10.3, x, w, h, MATS["mountain_far"])
    for i, (x, w, h) in enumerate([(-7.2, 5.5, 3.7), (-1.1, 6.4, 4.3), (5.8, 6.0, 4.1)]):
        mountain(f"near angular mountain face {i}", 7.7, x, w, h, MATS["mountain_near"])

    for i, y in enumerate([6.8, 8.4]):
        cube(
            f"soft warm haze sheet {i}",
            (0, y, 2.1 + i * 0.7),
            (23, 0.03, 3.0),
            MATS["sky_haze"],
            coll="mountains",
        )


def create_window_front(name: str, x: float, y: float, z: float, w: float, h: float) -> None:
    cube(f"{name} glowing panes", (x, y - 0.035, z), (w, 0.04, h), MATS["window_glow"], coll="windows_and_lamps")
    frame = MATS["wood_dark"]
    cube(f"{name} frame top", (x, y - 0.075, z + h / 2 + 0.055), (w + 0.25, 0.10, 0.10), frame, coll="windows_and_lamps", bevel=0.01)
    cube(f"{name} frame bottom", (x, y - 0.075, z - h / 2 - 0.055), (w + 0.25, 0.10, 0.10), frame, coll="windows_and_lamps", bevel=0.01)
    cube(f"{name} frame left", (x - w / 2 - 0.055, y - 0.075, z), (0.10, 0.10, h + 0.20), frame, coll="windows_and_lamps", bevel=0.01)
    cube(f"{name} frame right", (x + w / 2 + 0.055, y - 0.075, z), (0.10, 0.10, h + 0.20), frame, coll="windows_and_lamps", bevel=0.01)
    cube(f"{name} mullion vertical", (x, y - 0.095, z), (0.055, 0.11, h), frame, coll="windows_and_lamps")
    cube(f"{name} mullion horizontal", (x, y - 0.095, z), (w, 0.11, 0.055), frame, coll="windows_and_lamps")
    bpy.ops.object.light_add(type="POINT", location=(x, y - 0.35, z))
    light = bpy.context.object
    light.name = f"{name} warm point light"
    light.data.color = (1.0, 0.55, 0.16)
    light.data.energy = 90
    light.data.shadow_soft_size = 1.15
    link_to(light, "windows_and_lamps")


def create_window_side(name: str, x: float, y: float, z: float, w: float, h: float) -> None:
    cube(f"{name} glowing panes", (x + 0.035, y, z), (0.04, w, h), MATS["window_glow"], coll="windows_and_lamps")
    frame = MATS["wood_dark"]
    cube(f"{name} frame top", (x + 0.075, y, z + h / 2 + 0.055), (0.10, w + 0.25, 0.10), frame, coll="windows_and_lamps", bevel=0.01)
    cube(f"{name} frame bottom", (x + 0.075, y, z - h / 2 - 0.055), (0.10, w + 0.25, 0.10), frame, coll="windows_and_lamps", bevel=0.01)
    cube(f"{name} frame left", (x + 0.075, y - w / 2 - 0.055, z), (0.10, 0.10, h + 0.20), frame, coll="windows_and_lamps", bevel=0.01)
    cube(f"{name} frame right", (x + 0.075, y + w / 2 + 0.055, z), (0.10, 0.10, h + 0.20), frame, coll="windows_and_lamps", bevel=0.01)
    cube(f"{name} mullion vertical", (x + 0.095, y, z), (0.11, 0.055, h), frame, coll="windows_and_lamps")
    cube(f"{name} mullion horizontal", (x + 0.095, y, z), (0.11, w, 0.055), frame, coll="windows_and_lamps")
    bpy.ops.object.light_add(type="POINT", location=(x + 0.35, y, z))
    light = bpy.context.object
    light.name = f"{name} warm point light"
    light.data.color = (1.0, 0.55, 0.16)
    light.data.energy = 85
    light.data.shadow_soft_size = 1.1
    link_to(light, "windows_and_lamps")


def create_lantern(name: str, loc, scale: float = 1.0, coll="windows_and_lamps") -> None:
    x, y, z = loc
    cube(f"{name} glowing glass", (x, y, z), (0.20 * scale, 0.20 * scale, 0.32 * scale), MATS["lantern_glow"], coll=coll)
    iron = MATS["metal_dark"]
    for dx in [-0.13, 0.13]:
        for dy in [-0.13, 0.13]:
            cube(f"{name} corner iron {dx:.1f} {dy:.1f}", (x + dx * scale, y + dy * scale, z), (0.035 * scale, 0.035 * scale, 0.42 * scale), iron, coll=coll)
    cube(f"{name} top cap", (x, y, z + 0.24 * scale), (0.34 * scale, 0.34 * scale, 0.05 * scale), iron, coll=coll)
    cube(f"{name} base cap", (x, y, z - 0.24 * scale), (0.30 * scale, 0.30 * scale, 0.05 * scale), iron, coll=coll)
    bpy.ops.object.light_add(type="POINT", location=(x, y, z))
    light = bpy.context.object
    light.name = f"{name} actual warm light"
    light.data.color = (1.0, 0.58, 0.17)
    light.data.energy = 60 * scale
    light.data.shadow_soft_size = 0.65 * scale
    link_to(light, coll)


def create_cabin() -> None:
    # Stone foundation.
    x = -2.6
    block_i = 0
    while x < 2.65:
        w = rng.uniform(0.45, 0.72)
        mat = rng.choice([MATS["stone_a"], MATS["stone_b"], MATS["stone_c"]])
        cube(
            f"front foundation individual stone {block_i:02d}",
            (x + w * 0.5, -2.43, 0.28),
            (w, 0.34, rng.uniform(0.34, 0.48)),
            mat,
            coll="cabin",
            bevel=0.025,
        )
        x += w * 0.95
        block_i += 1

    for side_x in [-2.95, 2.95]:
        y = -1.95
        row = 0
        while y < 2.25:
            d = rng.uniform(0.45, 0.75)
            cube(
                f"side foundation stone {'left' if side_x < 0 else 'right'} {row:02d}",
                (side_x, y + d * 0.5, 0.27),
                (0.34, d, rng.uniform(0.34, 0.47)),
                rng.choice([MATS["stone_a"], MATS["stone_b"], MATS["stone_c"]]),
                coll="cabin",
                bevel=0.025,
            )
            y += d * 0.93
            row += 1

    # Horizontal log siding on all visible sides.
    z0 = 0.62
    plank_h = 0.255
    for i in range(11):
        z = z0 + i * plank_h
        mat = MATS["wood_a"] if i % 2 else MATS["wood_b"]
        cube(f"front horizontal log plank {i:02d}", (0, -2.31, z), (5.74, 0.18, 0.19), mat, coll="cabin", bevel=0.018)
        cube(f"right wall horizontal log plank {i:02d}", (2.91, 0, z), (0.18, 4.42, 0.19), mat, coll="cabin", bevel=0.018)
        cube(f"left wall horizontal log plank {i:02d}", (-2.91, 0, z), (0.18, 4.42, 0.19), mat, coll="cabin", bevel=0.018)
        cube(f"dark shadow gap under plank {i:02d}", (0, -2.415, z - 0.12), (5.78, 0.035, 0.035), MATS["wood_dark"], coll="cabin")

    for x in [-2.87, 2.87]:
        cube(f"front corner upright log {x:+.1f}", (x, -2.26, 1.72), (0.32, 0.34, 2.58), MATS["wood_dark"], coll="cabin", bevel=0.025)
    cube("right rear upright log", (2.86, 2.20, 1.72), (0.32, 0.32, 2.58), MATS["wood_dark"], coll="cabin", bevel=0.025)
    cube("left rear upright log", (-2.86, 2.20, 1.72), (0.32, 0.32, 2.58), MATS["wood_dark"], coll="cabin", bevel=0.025)

    # Wood grain and knots on the front wall.
    for i in range(75):
        z = rng.uniform(0.75, 2.95)
        gx = rng.uniform(-2.45, 2.4)
        if -1.05 < gx < 0.25 and 0.55 < z < 2.35:
            continue
        cube(
            f"thin dark wood grain front {i:02d}",
            (gx, -2.425, z),
            (rng.uniform(0.18, 0.48), 0.025, 0.018),
            MATS["wood_dark"],
            rot=(0, 0, rng.uniform(-0.04, 0.04)),
            coll="cabin",
        )

    # Door and frame.
    cube("front heavy plank door base", (-0.42, -2.50, 1.38), (1.02, 0.13, 1.76), MATS["wood_b"], coll="cabin", bevel=0.02)
    for dx in [-0.25, 0.0, 0.25]:
        cube(f"front door vertical board {dx:+.2f}", (-0.42 + dx, -2.585, 1.38), (0.065, 0.055, 1.62), MATS["wood_dark"], coll="cabin")
    cube("front door top cross brace", (-0.42, -2.595, 2.12), (1.05, 0.07, 0.08), MATS["wood_dark"], coll="cabin")
    cube("front door lower cross brace", (-0.42, -2.595, 0.72), (1.05, 0.07, 0.08), MATS["wood_dark"], coll="cabin")
    cube("front door left jamb", (-1.02, -2.56, 1.38), (0.16, 0.18, 1.96), MATS["wood_dark"], coll="cabin", bevel=0.012)
    cube("front door right jamb", (0.18, -2.56, 1.38), (0.16, 0.18, 1.96), MATS["wood_dark"], coll="cabin", bevel=0.012)
    cube("front door lintel", (-0.42, -2.56, 2.35), (1.38, 0.19, 0.17), MATS["wood_dark"], coll="cabin", bevel=0.012)
    cylinder("small iron door knob", (0.03, -2.66, 1.31), 0.055, 0.035, MATS["metal_dark"], vertices=8, rot=(math.pi / 2, 0, 0), coll="cabin")

    # Gable wall under the roof.
    verts = [
        (-2.78, -2.42, 3.00),
        (2.78, -2.42, 3.00),
        (0.0, -2.42, 4.86),
        (-2.78, -2.26, 3.00),
        (2.78, -2.26, 3.00),
        (0.0, -2.26, 4.86),
    ]
    faces = [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
    mesh = bpy.data.meshes.new("front triangular gable wall mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    gable = bpy.data.objects.new("front triangular timber gable wall", mesh)
    gable.data.materials.append(MATS["wood_a"])
    bpy.context.scene.collection.objects.link(gable)
    link_to(gable, "cabin")

    for i, z in enumerate([3.15, 3.40, 3.65, 3.90, 4.15, 4.40]):
        half_w = max(0.35, 2.78 * (1 - (z - 3.0) / (4.86 - 3.0)))
        cube(
            f"front gable horizontal visible plank {i:02d}",
            (0, -2.54, z),
            (half_w * 2.0, 0.10, 0.13),
            MATS["wood_b"] if i % 2 else MATS["wood_a"],
            coll="cabin",
            bevel=0.008,
        )

    beam_between("left sloped front gable beam", (-2.95, -2.62, 2.94), (0, -2.62, 4.98), 0.11, MATS["wood_dark"], vertices=4, coll="cabin", bevel=0.012)
    beam_between("right sloped front gable beam", (2.95, -2.62, 2.94), (0, -2.62, 4.98), 0.11, MATS["wood_dark"], vertices=4, coll="cabin", bevel=0.012)
    cube("front gable cross beam", (0, -2.62, 3.08), (5.8, 0.20, 0.16), MATS["wood_dark"], coll="cabin", bevel=0.012)
    beam_between("gable diagonal brace left", (-0.75, -2.66, 3.08), (0, -2.66, 4.30), 0.055, MATS["wood_dark"], vertices=4, coll="cabin")
    beam_between("gable diagonal brace right", (0.75, -2.66, 3.08), (0, -2.66, 4.30), 0.055, MATS["wood_dark"], vertices=4, coll="cabin")

    create_window_front("front gable square window", 0.0, -2.64, 3.78, 0.72, 0.72)
    create_window_front("front right warm window", 1.48, -2.52, 1.66, 0.76, 0.84)
    create_window_side("right wall front warm window", 2.99, -1.22, 1.62, 0.78, 0.90)
    create_window_side("right wall rear warm window", 2.99, 0.55, 1.60, 0.78, 0.86)

    create_lantern("front porch wall lantern", (-1.32, -2.67, 1.48), 0.85)
    beam_between("small lantern bracket", (-1.18, -2.58, 1.83), (-1.32, -2.72, 1.70), 0.018, MATS["metal_dark"], vertices=4, coll="windows_and_lamps")


def create_roof_and_chimney() -> None:
    roof_run = 3.15
    roof_rise = 2.08
    eave_z = 3.05
    ridge_z = eave_z + roof_rise
    roof_len = math.sqrt(roof_run**2 + roof_rise**2)
    angle = math.atan2(roof_rise, roof_run)
    y_len = 5.72

    cube(
        "left broad sloped roof plane",
        (-roof_run / 2, -0.08, (eave_z + ridge_z) / 2),
        (roof_len, y_len, 0.22),
        MATS["roof_a"],
        rot=(0, -angle, 0),
        coll="roof",
        bevel=0.015,
    )
    cube(
        "right broad sloped roof plane",
        (roof_run / 2, -0.08, (eave_z + ridge_z) / 2),
        (roof_len, y_len, 0.22),
        MATS["roof_b"],
        rot=(0, angle, 0),
        coll="roof",
        bevel=0.015,
    )

    roof_mats = [MATS["roof_a"], MATS["roof_b"], MATS["roof_c"]]
    idx = 0
    for side, sign, rot_y in [("right", 1, angle), ("left", -1, -angle)]:
        for row in range(7):
            t = 0.12 + row * 0.115
            sx = sign * roof_run * (1 - t)
            sz = eave_z + roof_rise * t + 0.13
            y = -2.42
            while y < 2.55:
                tile_len = rng.uniform(0.45, 0.82)
                y_mid = y + tile_len * 0.5
                cube(
                    f"{side} roof individual uneven shingle {idx:03d}",
                    (sx + rng.uniform(-0.035, 0.035), y_mid, sz + rng.uniform(-0.015, 0.015)),
                    (0.52, tile_len * 0.92, 0.045),
                    rng.choice(roof_mats),
                    rot=(0, rot_y, 0),
                    coll="roof",
                    bevel=0.006,
                )
                y += tile_len * rng.uniform(0.84, 1.05)
                idx += 1

    beam_between("roof ridge cap round timber", (0, -2.94, ridge_z + 0.06), (0, 2.78, ridge_z + 0.06), 0.12, MATS["wood_dark"], vertices=6, coll="roof", bevel=0.01)
    beam_between("front left roof fascia timber", (-roof_run, -2.92, eave_z - 0.03), (0, -2.92, ridge_z + 0.03), 0.13, MATS["wood_b"], vertices=4, coll="roof", bevel=0.015)
    beam_between("front right roof fascia timber", (roof_run, -2.92, eave_z - 0.03), (0, -2.92, ridge_z + 0.03), 0.13, MATS["wood_b"], vertices=4, coll="roof", bevel=0.015)
    beam_between("left eave timber", (-roof_run, -2.90, eave_z - 0.04), (-roof_run, 2.80, eave_z - 0.04), 0.105, MATS["wood_dark"], vertices=4, coll="roof")
    beam_between("right eave timber", (roof_run, -2.90, eave_z - 0.04), (roof_run, 2.80, eave_z - 0.04), 0.105, MATS["wood_dark"], vertices=4, coll="roof")

    # Chimney made from individually offset blocks.
    cx, cy = 1.74, 1.20
    cube("chimney dark inner core", (cx, cy, 4.86), (0.74, 0.70, 1.50), MATS["stone_c"], coll="chimney", bevel=0.02)
    block = 0
    for layer in range(6):
        z = 4.22 + layer * 0.25
        offset = 0.14 if layer % 2 else -0.05
        for bx in [-0.23, 0.23]:
            cube(
                f"chimney front ashlar block {block:02d}",
                (cx + bx + offset * 0.25, cy - 0.38, z),
                (0.42, 0.16, 0.22),
                rng.choice([MATS["stone_a"], MATS["stone_b"], MATS["stone_c"]]),
                coll="chimney",
                bevel=0.012,
            )
            block += 1
        for by in [-0.15, 0.15]:
            cube(
                f"chimney right side block {block:02d}",
                (cx + 0.40, cy + by + offset * 0.12, z),
                (0.16, 0.34, 0.22),
                rng.choice([MATS["stone_a"], MATS["stone_b"], MATS["stone_c"]]),
                coll="chimney",
                bevel=0.012,
            )
            block += 1
    cube("chimney black top cap", (cx, cy, 5.67), (1.00, 0.94, 0.13), MATS["metal_dark"], coll="chimney", bevel=0.012)
    cube("chimney soot opening", (cx, cy, 5.79), (0.50, 0.46, 0.08), MATS["metal_dark"], coll="chimney")


def create_porch() -> None:
    cube("porch stone base slab", (-0.70, -3.16, 0.45), (4.45, 1.34, 0.32), MATS["stone_c"], coll="porch", bevel=0.025)
    for i, x in enumerate([-2.45, -1.75, -1.05, -0.35, 0.35, 1.05]):
        cube(f"porch deck plank {i:02d}", (x, -3.16, 0.72), (0.56, 1.48, 0.12), MATS["wood_b"] if i % 2 else MATS["wood_a"], coll="porch", bevel=0.012)
    cube("porch front nosing beam", (-0.70, -3.92, 0.79), (4.65, 0.20, 0.20), MATS["wood_dark"], coll="porch", bevel=0.014)

    for i, (y, w, z) in enumerate([(-4.08, 1.68, 0.42), (-4.32, 2.08, 0.25), (-4.56, 2.46, 0.10)]):
        cube(f"front porch stair tread {i}", (-0.42, y, z), (w, 0.36, 0.20), MATS["wood_b"], coll="porch", bevel=0.012)

    post_positions = [(-2.70, -3.86), (1.47, -3.86), (-2.70, -2.52), (1.47, -2.52)]
    for i, (x, y) in enumerate(post_positions):
        cube(f"porch chunky square post {i}", (x, y, 1.16), (0.20, 0.20, 0.98), MATS["wood_dark"], coll="porch", bevel=0.012)
    cube("porch front rail left", (-2.08, -3.86, 1.34), (1.12, 0.13, 0.14), MATS["wood_b"], coll="porch", bevel=0.01)
    cube("porch front rail right", (0.86, -3.86, 1.34), (1.22, 0.13, 0.14), MATS["wood_b"], coll="porch", bevel=0.01)
    cube("porch left side rail", (-2.70, -3.18, 1.34), (0.13, 1.22, 0.14), MATS["wood_b"], coll="porch", bevel=0.01)
    cube("porch right side rail", (1.47, -3.18, 1.34), (0.13, 1.22, 0.14), MATS["wood_b"], coll="porch", bevel=0.01)
    cube("porch left lower rail", (-2.70, -3.18, 1.02), (0.11, 1.10, 0.11), MATS["wood_dark"], coll="porch")
    cube("porch right lower rail", (1.47, -3.18, 1.02), (0.11, 1.10, 0.11), MATS["wood_dark"], coll="porch")

    cylinder("small barrel on porch", (-1.62, -2.70, 0.98), 0.23, 0.54, MATS["wood_a"], vertices=12, coll="porch", bevel=0.01)
    cylinder("barrel upper iron band", (-1.62, -2.70, 1.16), 0.245, 0.035, MATS["metal_dark"], vertices=12, coll="porch")
    cylinder("barrel lower iron band", (-1.62, -2.70, 0.82), 0.245, 0.035, MATS["metal_dark"], vertices=12, coll="porch")


def pine_tree(name: str, x: float, y: float, scale: float, mat_bias: int = 1) -> None:
    ground_z = terrain_height(x, y)
    trunk_h = 0.92 * scale
    cylinder(
        f"{name} faceted trunk",
        (x, y, ground_z + trunk_h * 0.5),
        0.16 * scale,
        trunk_h,
        MATS["trunk"],
        vertices=5,
        rot=(0, 0, rng.random() * math.tau),
        coll="forest",
        bevel=0.005,
    )
    foliage_mats = [MATS["pine_a"], MATS["pine_b"], MATS["pine_c"]]
    levels = 3 if scale < 1.35 else 4
    for level in range(levels):
        radius = scale * (0.95 - level * 0.14)
        depth = scale * (1.10 - level * 0.04)
        z = ground_z + trunk_h * 0.62 + level * scale * 0.55 + depth * 0.5
        mat = foliage_mats[min(2, max(0, mat_bias + rng.choice([-1, 0, 0, 1])))]
        cone(
            f"{name} angular pine tier {level}",
            (x, y, z),
            radius,
            0.03 * scale,
            depth,
            mat,
            vertices=6,
            rot=(0, 0, rng.random() * math.tau),
            coll="forest",
        )


def create_forest() -> None:
    hero_trees = [
        ("large right foreground pine", 7.8, -2.85, 1.90, 1),
        ("right shoulder pine behind cabin", 5.5, 0.7, 1.65, 1),
        ("large left foreground pine", -8.6, -3.4, 1.72, 1),
        ("left midground path pine", -5.2, -1.5, 1.25, 0),
        ("rear center tall pine", 0.7, 3.8, 1.55, 1),
        ("rear left tall pine", -3.4, 3.4, 1.42, 1),
        ("rear right tall pine", 3.9, 3.6, 1.55, 2),
    ]
    for args in hero_trees:
        pine_tree(*args)

    placed = 0
    attempts = 0
    while placed < 32 and attempts < 260:
        attempts += 1
        x = rng.uniform(-10.0, 10.0)
        y = rng.uniform(-0.4, 8.5)
        if -4.2 < x < 4.0 and -3.3 < y < 2.8:
            continue
        if distance_to_path(x, y) < 1.05 and y < -1.0:
            continue
        scale = rng.uniform(0.62, 1.25) * (1.0 + y * 0.035)
        pine_tree(f"background staggered pine {placed:02d}", x, y, scale, rng.choice([0, 1, 1, 2]))
        placed += 1


def create_rocks_bushes_grass() -> None:
    rock_mats = [MATS["stone_a"], MATS["stone_b"], MATS["stone_c"]]
    rock_positions = [
        (-4.8, -5.25, 0.55),
        (-2.75, -3.95, 0.38),
        (3.7, -3.55, 0.50),
        (5.2, -4.35, 0.38),
        (-6.7, -7.7, 0.42),
        (6.4, -1.35, 0.65),
        (-1.9, -6.8, 0.28),
        (1.2, -7.2, 0.34),
        (4.5, 1.6, 0.48),
        (-5.7, 0.6, 0.54),
    ]
    for i, (x, y, s) in enumerate(rock_positions):
        z = terrain_height(x, y) + s * 0.42
        obj = ico(f"faceted foreground rock {i:02d}", (x, y, z), (s * 0.9, s * rng.uniform(0.55, 0.85), s * 0.62), rng.choice(rock_mats), coll="terrain")
        obj.rotation_euler = (rng.random() * 0.6, rng.random() * 0.4, rng.random() * math.tau)

    bush_mats = [MATS["grass_a"], MATS["grass_b"], MATS["pine_b"]]
    for i in range(34):
        x = rng.uniform(-8.5, 8.5)
        y = rng.uniform(-6.4, 4.8)
        if -3.2 < x < 3.4 and -3.6 < y < 2.6:
            continue
        if distance_to_path(x, y) < 0.8 and y < -2.5:
            continue
        base_z = terrain_height(x, y)
        for k in range(rng.randint(2, 4)):
            sx = rng.uniform(0.28, 0.55)
            loc = (x + rng.uniform(-0.28, 0.28), y + rng.uniform(-0.24, 0.24), base_z + sx * 0.52)
            ico(f"low rounded bush {i:02d} lobe {k}", loc, (sx, sx * rng.uniform(0.65, 1.05), sx * 0.62), rng.choice(bush_mats), coll="forest")

    for i in range(70):
        x = rng.uniform(-9.0, 8.5)
        y = rng.uniform(-8.7, 4.5)
        if distance_to_path(x, y) < 0.45 and y < -2.5:
            continue
        z = terrain_height(x, y) + 0.05
        blades = rng.randint(3, 5)
        for b in range(blades):
            angle = rng.random() * math.tau
            blade = cone(
                f"small grass blade cluster {i:02d}-{b}",
                (x + rng.uniform(-0.12, 0.12), y + rng.uniform(-0.12, 0.12), z + 0.16),
                0.035,
                0.0,
                rng.uniform(0.24, 0.42),
                rng.choice([MATS["grass_a"], MATS["grass_b"], MATS["grass_c"]]),
                vertices=3,
                rot=(rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25), angle),
                coll="terrain",
            )
            blade.name = f"triangular grass blade {i:02d}-{b}"

    for i, (x, y, sc) in enumerate([(5.4, -7.6, 0.42), (5.9, -7.1, 0.30), (-2.0, -3.8, 0.24), (-5.4, -5.7, 0.28)]):
        z = terrain_height(x, y)
        cylinder(f"mushroom stem {i}", (x, y, z + 0.11 * sc / 0.3), 0.055 * sc / 0.3, 0.22 * sc / 0.3, MATS["mushroom_stem"], vertices=6, coll="foreground_props")
        cone(f"mushroom red cap {i}", (x, y, z + 0.25 * sc / 0.3), 0.18 * sc / 0.3, 0.04 * sc / 0.3, 0.12 * sc / 0.3, MATS["mushroom_red"], vertices=8, coll="foreground_props")


def create_fence_and_props() -> None:
    # Left foreground fence with hanging lantern.
    post_pts = [(-7.7, -6.3), (-5.95, -5.65), (-4.20, -5.05)]
    for i, (x, y) in enumerate(post_pts):
        z = terrain_height(x, y)
        cube(f"left path fence post {i}", (x, y, z + 0.63), (0.20, 0.20, 1.20), MATS["wood_dark"], coll="foreground_props", bevel=0.01)
    for i in range(len(post_pts) - 1):
        a = post_pts[i]
        b = post_pts[i + 1]
        za = terrain_height(*a)
        zb = terrain_height(*b)
        beam_between(f"left fence upper rail {i}", (a[0], a[1], za + 0.92), (b[0], b[1], zb + 0.98), 0.065, MATS["wood_b"], vertices=4, coll="foreground_props", bevel=0.008)
        beam_between(f"left fence lower rail {i}", (a[0], a[1], za + 0.55), (b[0], b[1], zb + 0.61), 0.055, MATS["wood_a"], vertices=4, coll="foreground_props")
    create_lantern("fence hanging lantern", (-5.75, -5.86, terrain_height(-5.75, -5.86) + 0.58), 0.75, coll="foreground_props")
    beam_between("curved-looking lantern hanger", (-5.95, -5.65, terrain_height(-5.95, -5.65) + 1.08), (-5.75, -5.86, terrain_height(-5.75, -5.86) + 0.83), 0.025, MATS["metal_dark"], vertices=4, coll="foreground_props")

    # Log pile and axe on the right foreground.
    base_x, base_y = 4.85, -6.25
    log_i = 0
    for layer, zoff in enumerate([0.18, 0.47, 0.76]):
        count = 5 - layer
        for j in range(count):
            x = base_x + (j - count * 0.5) * 0.46 + 0.20 * layer
            y = base_y + 0.02 * j
            z = terrain_height(base_x, base_y) + zoff
            cylinder(
                f"stacked firewood log {log_i:02d}",
                (x, y, z),
                0.18,
                1.65,
                MATS["wood_a"],
                vertices=10,
                rot=(0, math.pi / 2, rng.uniform(-0.04, 0.04)),
                coll="foreground_props",
                bevel=0.01,
            )
            cylinder(
                f"visible cut ring on firewood {log_i:02d}",
                (x + 0.84, y, z),
                0.155,
                0.025,
                MATS["wood_end"],
                vertices=10,
                rot=(0, math.pi / 2, 0),
                coll="foreground_props",
            )
            log_i += 1
    for i, yoff in enumerate([-0.36, 0.36]):
        beam_between(
            f"dark skid under log pile {i}",
            (3.28, base_y + yoff, terrain_height(3.28, base_y + yoff) + 0.09),
            (6.20, base_y + yoff, terrain_height(6.20, base_y + yoff) + 0.09),
            0.055,
            MATS["wood_dark"],
            vertices=4,
            coll="foreground_props",
        )

    stump_x, stump_y = 3.30, -6.88
    stump_z = terrain_height(stump_x, stump_y)
    cylinder("faceted chopping stump", (stump_x, stump_y, stump_z + 0.43), 0.42, 0.82, MATS["wood_a"], vertices=9, coll="foreground_props", bevel=0.015)
    cylinder("stump pale top cut", (stump_x, stump_y, stump_z + 0.86), 0.39, 0.035, MATS["wood_end"], vertices=9, coll="foreground_props")
    beam_between("axe wooden handle leaning", (2.62, -7.28, stump_z + 0.16), (3.42, -6.76, stump_z + 1.05), 0.045, MATS["wood_b"], vertices=8, coll="foreground_props", bevel=0.004)
    verts = [
        (-0.02, -0.035, -0.30),
        (0.42, -0.035, -0.13),
        (0.42, -0.035, 0.18),
        (-0.02, 0.035, -0.30),
        (0.42, 0.035, -0.13),
        (0.42, 0.035, 0.18),
    ]
    faces = [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
    mesh = bpy.data.meshes.new("axe head wedge mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    axe = bpy.data.objects.new("wedge shaped axe head on stump", mesh)
    axe.location = (3.45, -6.72, stump_z + 1.08)
    axe.rotation_euler = (0.25, 0.3, -0.63)
    axe.data.materials.append(MATS["stone_b"])
    bpy.context.scene.collection.objects.link(axe)
    link_to(axe, "foreground_props")


def setup_lighting_camera() -> None:
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.color = (1.0, 0.76, 0.48)

    bpy.ops.object.light_add(type="SUN", location=(-6.0, -7.0, 8.0))
    sun = bpy.context.object
    sun.name = "low warm sunset sun from left"
    sun.data.energy = 2.25
    sun.data.angle = math.radians(7.0)
    sun.data.color = (1.0, 0.68, 0.36)
    look_at(sun, (0.5, -0.5, 1.4))
    link_to(sun, "lighting_camera")

    bpy.ops.object.light_add(type="AREA", location=(-4.5, -5.2, 5.3))
    area = bpy.context.object
    area.name = "large warm cabin fill area"
    area.data.energy = 240
    area.data.size = 5.5
    area.data.color = (1.0, 0.62, 0.30)
    look_at(area, (0, -1.5, 1.7))
    link_to(area, "lighting_camera")

    bpy.ops.object.camera_add(location=(8.9, -12.2, 4.95))
    cam = bpy.context.object
    cam.name = "camera low hero view"
    look_at(cam, (0.25, -2.20, 2.15))
    cam.data.lens = 25
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = (cam.location - Vector((0.25, -2.0, 2.0))).length
    cam.data.dof.aperture_fstop = 5.2
    bpy.context.scene.camera = cam
    link_to(cam, "lighting_camera")

    # A small empty marks the visual focus point for anyone opening the scene.
    empty = bpy.data.objects.new("focus point: front cabin wall", None)
    empty.empty_display_type = "SPHERE"
    empty.empty_display_size = 0.25
    empty.location = (0, -1.55, 2.0)
    bpy.context.scene.collection.objects.link(empty)
    link_to(empty, "lighting_camera")


def configure_render() -> None:
    scene = bpy.context.scene
    engines = {item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items}
    if "BLENDER_EEVEE_NEXT" in engines:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    elif "BLENDER_EEVEE" in engines:
        scene.render.engine = "BLENDER_EEVEE"
    elif "CYCLES" in engines:
        scene.render.engine = "CYCLES"

    if scene.render.engine == "CYCLES" and hasattr(scene, "cycles"):
        scene.cycles.samples = 96
        scene.cycles.use_denoising = True
        scene.cycles.max_bounces = 5
    if hasattr(scene, "eevee"):
        for attr, value in [
            ("taa_render_samples", 96),
            ("use_gtao", True),
            ("gtao_distance", 3),
            ("gtao_factor", 1.2),
            ("use_bloom", True),
        ]:
            if hasattr(scene.eevee, attr):
                setattr(scene.eevee, attr, value)

    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.film_transparent = False
    scene.render.filepath = str(RENDER_PATH)
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    for transform in ["AgX", "Filmic", "Standard"]:
        try:
            scene.view_settings.view_transform = transform
            break
        except TypeError:
            continue
    for look in ["Medium High Contrast", "Medium High Contrast", "None"]:
        try:
            scene.view_settings.look = look
            break
        except TypeError:
            continue


def build_scene(render: bool) -> None:
    clear_scene()
    init_materials()
    init_collections()
    create_terrain()
    create_mountains()
    create_cabin()
    create_roof_and_chimney()
    create_porch()
    create_forest()
    create_rocks_bushes_grass()
    create_fence_and_props()
    setup_lighting_camera()
    configure_render()

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    if render:
        bpy.ops.render.render(write_still=True)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--render", action="store_true", help="Render preview.png after saving the .blend")
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1 :]
    else:
        argv = []
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    build_scene(render=args.render)
