import bpy
import math
import random
from mathutils import Vector


random.seed(560)

ROOT = "/home/ralf/prj/exploration/blender-benchmark/gpt-5.6-sol-extra-high"
BLEND_PATH = f"{ROOT}/low_poly_forest_cabin.blend"
RENDER_PATH = f"{ROOT}/low_poly_forest_cabin.png"


# -----------------------------------------------------------------------------
# Scene setup and helpers
# -----------------------------------------------------------------------------

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def collection(name):
    col = bpy.data.collections.new(name)
    scene.collection.children.link(col)
    return col


COL = {
    "environment": collection("ENVIRONMENT"),
    "cabin": collection("CABIN"),
    "props": collection("PROPS"),
    "vegetation": collection("VEGETATION"),
    "lights": collection("LIGHTS_AND_CAMERA"),
}


def move_to(obj, col_name):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    COL[col_name].objects.link(obj)
    return obj


def make_mat(name, color, roughness=0.72, emission=None, emission_strength=0.0, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color[:3], color[3] if len(color) > 3 else 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = mat.diffuse_color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*emission[:3], 1.0)
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = (*emission[:3], 1.0)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


M = {}
M["ground"] = [
    make_mat("Meadow olive", (0.24, 0.31, 0.105, 1)),
    make_mat("Meadow moss", (0.29, 0.37, 0.13, 1)),
    make_mat("Meadow sun", (0.36, 0.43, 0.17, 1)),
    make_mat("Meadow deep", (0.18, 0.27, 0.10, 1)),
    make_mat("Meadow dry", (0.40, 0.42, 0.17, 1)),
]
M["path"] = [
    make_mat("Path sand", (0.58, 0.38, 0.21, 1)),
    make_mat("Path warm", (0.69, 0.47, 0.28, 1)),
    make_mat("Path light", (0.78, 0.57, 0.35, 1)),
    make_mat("Path shade", (0.49, 0.32, 0.19, 1)),
]
M["wood"] = [
    make_mat("Pine honey", (0.36, 0.16, 0.055, 1)),
    make_mat("Pine warm", (0.47, 0.22, 0.075, 1)),
    make_mat("Pine sunlit", (0.58, 0.29, 0.09, 1)),
    make_mat("Pine dark", (0.23, 0.095, 0.038, 1)),
    make_mat("Pine muted", (0.39, 0.19, 0.075, 1)),
]
M["roof"] = [
    make_mat("Shingle umber", (0.115, 0.075, 0.062, 1)),
    make_mat("Shingle brown", (0.17, 0.105, 0.08, 1)),
    make_mat("Shingle charcoal", (0.075, 0.071, 0.071, 1)),
    make_mat("Shingle warm", (0.22, 0.125, 0.085, 1)),
]
M["stone"] = [
    make_mat("Stone gray", (0.31, 0.30, 0.30, 1)),
    make_mat("Stone warm", (0.40, 0.36, 0.33, 1)),
    make_mat("Stone light", (0.49, 0.46, 0.43, 1)),
    make_mat("Stone shade", (0.22, 0.23, 0.24, 1)),
]
M["pine"] = [
    make_mat("Pine needle dark", (0.085, 0.20, 0.105, 1)),
    make_mat("Pine needle", (0.13, 0.27, 0.12, 1)),
    make_mat("Pine needle olive", (0.24, 0.34, 0.12, 1)),
    make_mat("Pine needle light", (0.32, 0.41, 0.15, 1)),
]
M["mountain"] = [
    make_mat("Mountain haze", (0.49, 0.43, 0.36, 1)),
    make_mat("Mountain light", (0.63, 0.53, 0.43, 1)),
    make_mat("Mountain shadow", (0.38, 0.36, 0.33, 1)),
]
M["trunk"] = make_mat("Tree trunk", (0.26, 0.115, 0.045, 1))
M["trunk_dark"] = make_mat("Tree trunk dark", (0.15, 0.065, 0.03, 1))
M["frame"] = make_mat("Window and door frame", (0.19, 0.072, 0.025, 1))
M["door"] = make_mat("Door", (0.49, 0.20, 0.05, 1))
M["metal"] = make_mat("Blackened iron", (0.035, 0.033, 0.03, 1), roughness=0.38, metallic=0.55)
M["iron"] = make_mat("Axe iron", (0.30, 0.33, 0.34, 1), roughness=0.32, metallic=0.65)
M["window"] = make_mat(
    "Warm glowing glass", (1.0, 0.36, 0.035, 1), roughness=0.28,
    emission=(1.0, 0.18, 0.015), emission_strength=8.0,
)
M["lantern_glass"] = make_mat(
    "Lantern glow", (1.0, 0.45, 0.06, 1), roughness=0.2,
    emission=(1.0, 0.20, 0.015), emission_strength=14.0,
)
M["mushroom"] = make_mat("Mushroom red", (0.78, 0.12, 0.035, 1))
M["mushroom_stem"] = make_mat("Mushroom cream", (0.72, 0.57, 0.38, 1))
M["grass"] = make_mat("Grass blades", (0.17, 0.29, 0.06, 1))
M["log_end"] = make_mat("Fresh log ends", (0.61, 0.30, 0.09, 1))


def set_material(obj, material):
    obj.data.materials.append(material)
    return obj


def add_box(name, loc, dims, material, rot=(0, 0, 0), bevel=0.0, col="props"):
    # Establish local dimensions before rotating. Setting world-space dimensions on
    # an already tilted cube can create extremely long, needle-like roof pieces.
    bpy.ops.mesh.primitive_cube_add(location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.rotation_euler = rot
    set_material(obj, material)
    if bevel > 0:
        mod = obj.modifiers.new("Tiny hand-hewn edges", "BEVEL")
        mod.width = bevel
        mod.segments = 1
    return move_to(obj, col)


def add_cylinder(name, loc, radius, depth, material, vertices=8, rot=(0, 0, 0), col="props", end_mat=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    if end_mat:
        obj.data.materials.append(end_mat)
        for poly in obj.data.polygons:
            if abs(poly.normal.z) > 0.75:
                poly.material_index = 1
    return move_to(obj, col)


def add_ico(name, loc, scale, material, subdivisions=1, col="props"):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.rotation_euler = (
        random.uniform(-0.25, 0.25),
        random.uniform(-0.25, 0.25),
        random.uniform(0, math.tau),
    )
    set_material(obj, material)
    return move_to(obj, col)


def add_cone(name, loc, radius1, radius2, depth, material, vertices=8, rot=(0, 0, 0), col="vegetation"):
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices, radius1=radius1, radius2=radius2,
        depth=depth, location=loc, rotation=rot,
    )
    obj = bpy.context.object
    obj.name = name
    set_material(obj, material)
    return move_to(obj, col)


def beam_between(name, a, b, thickness, material, col="props", bevel=0.0):
    a, b = Vector(a), Vector(b)
    vec = b - a
    obj = add_box(name, (a + b) * 0.5, (vec.length, thickness, thickness), material, bevel=bevel, col=col)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = vec.to_track_quat("X", "Z")
    return obj


def add_point_light(name, loc, color, energy, radius=0.35):
    data = bpy.data.lights.new(name, "POINT")
    data.color = color
    data.energy = energy
    data.shadow_soft_size = radius
    obj = bpy.data.objects.new(name, data)
    obj.location = loc
    COL["lights"].objects.link(obj)
    return obj


# -----------------------------------------------------------------------------
# Terrain, path, stones and distant mountains
# -----------------------------------------------------------------------------

def ground_height(x, y):
    # Keep the cabin clearing calm but let the outer scene feel faceted.
    ripple = 0.12 * math.sin(x * 0.42) + 0.08 * math.cos(y * 0.36) + 0.04 * math.sin((x + y) * 0.7)
    clearing = max(0.0, min(1.0, (abs(x - 2.0) + abs(y - 1.0) - 5.0) / 8.0))
    return 0.12 + ripple * clearing


step = 2.0
xvals = [(-20 + i * step) for i in range(23)]
yvals = [(-18 + j * step) for j in range(25)]
verts = [(x, y, ground_height(x, y)) for y in yvals for x in xvals]
faces = []
nx = len(xvals)
for j in range(len(yvals) - 1):
    for i in range(len(xvals) - 1):
        a = j * nx + i
        b = a + 1
        c = a + nx
        d = c + 1
        if (i + j) % 2:
            faces.extend([(a, b, c), (b, d, c)])
        else:
            faces.extend([(a, b, d), (a, d, c)])
mesh = bpy.data.meshes.new("Faceted meadow mesh")
mesh.from_pydata(verts, [], faces)
mesh.materials.clear()
for mat in M["ground"]:
    mesh.materials.append(mat)
ground = bpy.data.objects.new("Faceted meadow", mesh)
COL["environment"].objects.link(ground)
for p in ground.data.polygons:
    p.material_index = random.choices(range(len(M["ground"])), weights=[4, 5, 2, 3, 2])[0]


path_pts = [
    (-0.5, -17.0), (-1.4, -14.2), (-3.0, -11.4), (-4.45, -8.7),
    (-5.8, -6.2), (-6.7, -3.8), (-6.1, -1.0), (-7.5, 1.8),
    (-8.0, 4.6), (-7.2, 7.2), (-8.5, 10.0),
]
path_verts = []
widths = [2.6, 2.55, 2.45, 2.25, 2.15, 2.0, 1.8, 1.65, 1.4, 1.2, 0.95]
for i, (x, y) in enumerate(path_pts):
    p_prev = Vector(path_pts[max(0, i - 1)])
    p_next = Vector(path_pts[min(len(path_pts) - 1, i + 1)])
    tangent = (p_next - p_prev).normalized()
    normal = Vector((-tangent.y, tangent.x))
    w = widths[i]
    for side in (-1, 1):
        q = Vector((x, y)) + normal * w * 0.5 * side
        path_verts.append((q.x, q.y, ground_height(q.x, q.y) + 0.10))
path_faces = []
for i in range(len(path_pts) - 1):
    a, b, c, d = i * 2, i * 2 + 1, i * 2 + 2, i * 2 + 3
    path_faces.extend([(a, b, c), (b, d, c)])
mesh = bpy.data.meshes.new("Winding trail mesh")
mesh.from_pydata(path_verts, [], path_faces)
for mat in M["path"]:
    mesh.materials.append(mat)
path = bpy.data.objects.new("Winding trail", mesh)
COL["environment"].objects.link(path)
for p in path.data.polygons:
    p.material_index = random.randrange(len(M["path"]))


def add_rock(x, y, scale=0.5, mat=None, name="Rock"):
    z = ground_height(x, y) + scale * 0.35
    return add_ico(name, (x, y, z), (scale, scale * random.uniform(0.7, 1.1), scale * random.uniform(0.65, 1.1)), mat or random.choice(M["stone"]), col="environment")


# Trail pebbles and substantial clearing rocks.
for i in range(32):
    x, y = random.choice(path_pts)
    x += random.uniform(-1.0, 1.0)
    y += random.uniform(-1.0, 1.0)
    add_rock(x, y, random.uniform(0.09, 0.22), random.choice(M["stone"]), "Trail pebble")
for x, y, s in [
    (-8.3, -7.5, 0.8), (-6.8, -10.2, 0.55), (-2.4, -5.3, 0.62),
    (6.9, -7.3, 0.72), (8.3, -4.7, 0.48), (7.9, 4.5, 1.05),
    (-4.0, 2.8, 0.95), (10.8, 1.2, 0.70), (4.8, -8.4, 0.48),
    (1.2, -8.9, 0.55), (-10.4, -3.4, 0.75),
]:
    add_rock(x, y, s)


def add_mountain(name, x, y, width, depth, height, materials):
    n = 7
    ring = []
    for i in range(n):
        ang = math.tau * i / n
        ring.append((
            x + math.cos(ang) * width * random.uniform(0.78, 1.08),
            y + math.sin(ang) * depth * random.uniform(0.75, 1.10),
            0.0,
        ))
    peak = (x + random.uniform(-0.14, 0.14) * width, y + random.uniform(-0.1, 0.1) * depth, height)
    verts = ring + [peak]
    faces = []
    for i in range(n):
        faces.append((i, (i + 1) % n, n))
    faces.append(tuple(reversed(range(n))))
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(verts, [], faces)
    for mat in materials:
        mesh.materials.append(mat)
    obj = bpy.data.objects.new(name, mesh)
    COL["environment"].objects.link(obj)
    for poly in obj.data.polygons:
        poly.material_index = random.randrange(len(materials))
    return obj


# Back layer first, then a warmer nearer ridge.
for i, (x, h, w) in enumerate([(-22, 11, 8), (-12, 13, 9), (-2, 15, 9), (9, 16, 10), (21, 14, 10)]):
    add_mountain(f"Hazy mountain {i}", x, 35 + random.uniform(-1, 1), w, 5.5, h, M["mountain"][:2])
for i, (x, h, w) in enumerate([(-18, 8, 7), (-7, 10, 8), (4, 11, 8), (15, 10, 8), (26, 9, 8)]):
    add_mountain(f"Near mountain {i}", x, 29 + random.uniform(-1, 1), w, 4.2, h, M["mountain"])


# -----------------------------------------------------------------------------
# Cabin architecture
# -----------------------------------------------------------------------------

cx, cy = 2.0, 1.0
wall_half = 3.5
front_y, back_y = -2.0, 4.0
wall_base, eave_z, ridge_z = 0.82, 4.65, 8.05

# Stone foundation: individual uneven blocks around the visible faces.
for x in [cx - 3.2 + i * 0.82 for i in range(9)]:
    add_box("Foundation front stone", (x, front_y - 0.10, 0.55), (0.76, 0.58, 0.56), random.choice(M["stone"]),
            rot=(0, random.uniform(-0.04, 0.04), random.uniform(-0.035, 0.035)), bevel=0.07, col="cabin")
for y in [front_y + 0.35 + i * 0.78 for i in range(8)]:
    add_box("Foundation side stone", (cx + wall_half + 0.08, y, 0.55), (0.58, 0.72, 0.56), random.choice(M["stone"]),
            rot=(random.uniform(-0.04, 0.04), 0, random.uniform(-0.035, 0.035)), bevel=0.07, col="cabin")

# Solid dark wall backing.
add_box("Front wall backing", (cx, front_y, (wall_base + eave_z) / 2), (7.0, 0.42, eave_z - wall_base), M["wood"][3], col="cabin")
add_box("Right wall backing", (cx + wall_half, cy, (wall_base + eave_z) / 2), (0.42, 6.0, eave_z - wall_base), M["wood"][3], col="cabin")
add_box("Left wall backing", (cx - wall_half, cy, (wall_base + eave_z) / 2), (0.38, 6.0, eave_z - wall_base), M["wood"][3], col="cabin")

# Horizontal hand-hewn logs with slight alternating overlap.
for row, z in enumerate([1.02 + i * 0.43 for i in range(9)]):
    add_box(
        "Front hewn log", (cx + random.uniform(-0.035, 0.035), front_y - 0.24, z),
        (7.18 + (0.16 if row % 2 else 0), 0.34, 0.37), random.choice(M["wood"][:3] + [M["wood"][4]]),
        rot=(random.uniform(-0.012, 0.012), 0, random.uniform(-0.006, 0.006)), bevel=0.055, col="cabin",
    )
    add_box(
        "Side hewn log", (cx + wall_half + 0.23, cy + random.uniform(-0.035, 0.035), z),
        (0.34, 6.15 + (0.14 if not row % 2 else 0), 0.37), random.choice(M["wood"][:3] + [M["wood"][4]]),
        rot=(0, random.uniform(-0.012, 0.012), random.uniform(-0.006, 0.006)), bevel=0.055, col="cabin",
    )

# Corner posts and structural beams.
for x in (cx - wall_half, cx + wall_half):
    for y in (front_y - 0.24, back_y):
        if y == back_y and x == cx - wall_half:
            continue
        add_box("Cabin corner post", (x, y, 2.7), (0.43, 0.43, 4.15), M["wood"][3], bevel=0.05, col="cabin")
add_box("Front top beam", (cx, front_y - 0.34, 4.52), (7.55, 0.45, 0.42), M["wood"][1], bevel=0.055, col="cabin")


def add_tri_prism(name, center_x, y_center, y_depth, z0, half_w, z_peak, material):
    y0, y1 = y_center - y_depth / 2, y_center + y_depth / 2
    verts = [
        (center_x - half_w, y0, z0), (center_x + half_w, y0, z0), (center_x, y0, z_peak),
        (center_x - half_w, y1, z0), (center_x + half_w, y1, z0), (center_x, y1, z_peak),
    ]
    faces = [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh)
    COL["cabin"].objects.link(obj)
    return obj


add_tri_prism("Front timber gable", cx, front_y - 0.03, 0.34, eave_z - 0.05, wall_half, ridge_z - 0.12, M["wood"][3])
# Gable board rhythm, with the roof hiding their rectangular overhangs.
for i, x in enumerate([cx - 2.8 + i * 0.70 for i in range(9)]):
    local_height = max(0.35, (ridge_z - eave_z) * (1 - abs(x - cx) / wall_half))
    add_box("Gable vertical board", (x, front_y - 0.25, eave_z + local_height / 2 - 0.05),
            (0.62, 0.18, local_height), M["wood"][i % 3], bevel=0.025, col="cabin")

# Roof underlay and patchwork shingles.
roof_run = 4.18
roof_rise = ridge_z - eave_z
roof_slope = math.sqrt(roof_run ** 2 + roof_rise ** 2)
roof_angle = math.atan2(roof_rise, roof_run)
for side in (-1, 1):
    # Local +X must climb toward the ridge on the left slope and descend away
    # from it on the right slope.
    rot_y = side * roof_angle
    add_box(
        "Roof plane", (cx + side * roof_run * 0.5, cy, (eave_z + ridge_z) * 0.5),
        (roof_slope, 7.12, 0.24), M["roof"][0], rot=(0, rot_y, 0), bevel=0.03, col="cabin",
    )
    rows, cols = 5, 7
    for r in range(rows):
        t = (r + 0.52) / rows
        for c in range(cols):
            y = front_y - 0.42 + (c + 0.5) * (6.85 / cols)
            y += (0.12 if r % 2 else -0.06)
            x = cx + side * roof_run * (1.0 - t)
            z = eave_z + roof_rise * t + 0.16
            tile = add_box(
                "Individual roof shingle", (x, y, z),
                (roof_slope / rows * 1.12, 6.85 / cols * 0.92, 0.095), random.choice(M["roof"]),
                rot=(0, rot_y, random.uniform(-0.015, 0.015)), bevel=0.025, col="cabin",
            )
            tile.scale.y *= random.uniform(0.92, 1.07)

# Ridge timber and fascia boards.
add_cylinder("Roof ridge timber", (cx, cy, ridge_z + 0.15), 0.16, 7.25, M["wood"][1], vertices=6, rot=(math.pi / 2, 0, 0), col="cabin")
for side in (-1, 1):
    beam_between(
        "Front roof fascia",
        (cx, front_y - 0.58, ridge_z + 0.10),
        (cx + side * roof_run, front_y - 0.58, eave_z + 0.02),
        0.25, M["wood"][1], col="cabin", bevel=0.035,
    )

# Door, surround, raised panels and ironwork.
door_x = 1.25
add_box("Door slab", (door_x, front_y - 0.48, 2.48), (1.47, 0.22, 2.85), M["door"], bevel=0.045, col="cabin")
for x in (door_x - 0.82, door_x + 0.82):
    add_box("Door jamb", (x, front_y - 0.59, 2.48), (0.22, 0.24, 3.12), M["frame"], bevel=0.025, col="cabin")
add_box("Door lintel", (door_x, front_y - 0.59, 4.02), (1.88, 0.24, 0.24), M["frame"], bevel=0.025, col="cabin")
for x in (door_x - 0.42, door_x, door_x + 0.42):
    add_box("Door vertical panel", (x, front_y - 0.61, 2.48), (0.075, 0.08, 2.54), M["wood"][3], bevel=0.012, col="cabin")
for z in (1.55, 2.45, 3.35):
    add_box("Door cross brace", (door_x, front_y - 0.63, z), (1.24, 0.085, 0.10), M["wood"][3], bevel=0.012, col="cabin")
bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=4, radius=0.09, location=(door_x + 0.48, front_y - 0.74, 2.42))
knob = bpy.context.object
knob.name = "Iron door knob"
set_material(knob, M["metal"])
move_to(knob, "cabin")


def add_front_window(name, x, z, width, height):
    add_box(name + " dark recess", (x, front_y - 0.50, z), (width + 0.24, 0.16, height + 0.24), M["frame"], bevel=0.03, col="cabin")
    add_box(name + " glowing glass", (x, front_y - 0.60, z), (width, 0.08, height), M["window"], col="cabin")
    add_box(name + " sill", (x, front_y - 0.69, z - height / 2 - 0.12), (width + 0.45, 0.30, 0.20), M["wood"][1], bevel=0.025, col="cabin")
    add_box(name + " top", (x, front_y - 0.68, z + height / 2 + 0.12), (width + 0.42, 0.28, 0.18), M["wood"][1], bevel=0.025, col="cabin")
    for dx in (-width / 2 - 0.11, width / 2 + 0.11):
        add_box(name + " side trim", (x + dx, front_y - 0.68, z), (0.18, 0.26, height + 0.48), M["wood"][1], bevel=0.02, col="cabin")
    add_box(name + " vertical mullion", (x, front_y - 0.67, z), (0.075, 0.10, height), M["frame"], col="cabin")
    add_box(name + " horizontal mullion", (x, front_y - 0.67, z), (width, 0.10, 0.075), M["frame"], col="cabin")
    add_point_light(name + " light", (x, front_y - 0.80, z), (1.0, 0.25, 0.045), 55, 0.25)


def add_side_window(name, y, z, width, height):
    x = cx + wall_half + 0.50
    add_box(name + " dark recess", (x, y, z), (0.16, width + 0.24, height + 0.24), M["frame"], bevel=0.03, col="cabin")
    add_box(name + " glowing glass", (x + 0.10, y, z), (0.08, width, height), M["window"], col="cabin")
    add_box(name + " sill", (x + 0.18, y, z - height / 2 - 0.12), (0.30, width + 0.45, 0.20), M["wood"][1], bevel=0.025, col="cabin")
    add_box(name + " top", (x + 0.17, y, z + height / 2 + 0.12), (0.28, width + 0.42, 0.18), M["wood"][1], bevel=0.025, col="cabin")
    for dy in (-width / 2 - 0.11, width / 2 + 0.11):
        add_box(name + " side trim", (x + 0.17, y + dy, z), (0.26, 0.18, height + 0.48), M["wood"][1], bevel=0.02, col="cabin")
    add_box(name + " vertical mullion", (x + 0.16, y, z), (0.10, 0.075, height), M["frame"], col="cabin")
    add_box(name + " horizontal mullion", (x + 0.16, y, z), (0.10, width, 0.075), M["frame"], col="cabin")
    add_point_light(name + " light", (x + 0.42, y, z), (1.0, 0.25, 0.045), 42, 0.25)


add_front_window("Gable window", cx, 5.92, 1.05, 1.20)
add_side_window("Side front window", -0.55, 2.65, 1.18, 1.55)
add_side_window("Side rear window", 2.25, 2.65, 1.05, 1.45)

# Decorative gable braces.
beam_between("Gable left brace", (cx, front_y - 0.72, 7.35), (cx - 1.30, front_y - 0.72, 4.72), 0.15, M["wood"][1], col="cabin")
beam_between("Gable right brace", (cx, front_y - 0.72, 7.35), (cx + 1.30, front_y - 0.72, 4.72), 0.15, M["wood"][1], col="cabin")

# Chimney bricks.
chimney_x, chimney_y = 4.05, 1.45
for row in range(6):
    z = 6.30 + row * 0.39
    offset = 0.10 if row % 2 else -0.08
    for col_i in (-1, 1):
        add_box("Chimney stone", (chimney_x + col_i * 0.31 + offset, chimney_y, z),
                (0.58, 0.70, 0.34), random.choice(M["stone"]), rot=(0, 0, random.uniform(-0.025, 0.025)), bevel=0.045, col="cabin")
add_box("Chimney cap", (chimney_x, chimney_y, 8.68), (1.15, 0.95, 0.20), M["stone"][2], bevel=0.045, col="cabin")
add_cylinder("Chimney soot cap", (chimney_x, chimney_y, 8.86), 0.39, 0.13, M["metal"], vertices=8, col="cabin")


# -----------------------------------------------------------------------------
# Porch, railings, steps, lanterns and small props
# -----------------------------------------------------------------------------

porch_z = 0.98
for i in range(11):
    x = cx - 3.45 + i * 0.69
    add_box("Porch plank", (x, -3.55, porch_z), (0.61, 2.78, 0.20), random.choice(M["wood"][:3]), bevel=0.025, col="cabin")
for x in (cx - 3.45, cx + 3.45):
    add_box("Porch support post", (x, -4.63, 1.55), (0.30, 0.30, 1.55), M["wood"][1], bevel=0.03, col="cabin")
for x in (cx - 3.45, cx + 3.45):
    add_box("Porch back railing post", (x, -2.65, 1.55), (0.28, 0.28, 1.42), M["wood"][1], bevel=0.03, col="cabin")
for x in (cx - 3.45, cx + 3.45):
    beam_between("Porch side rail", (x, -4.63, 1.72), (x, -2.65, 1.72), 0.20, M["wood"][1], col="cabin", bevel=0.025)
    for y in (-4.15, -3.62, -3.08):
        add_box("Porch baluster", (x, y, 1.42), (0.16, 0.16, 0.83), M["wood"][1], bevel=0.02, col="cabin")
# Front rails leave a gap at the steps.
for xa, xb in ((cx - 3.45, cx - 0.92), (cx + 0.92, cx + 3.45)):
    beam_between("Porch front rail", (xa, -4.63, 1.72), (xb, -4.63, 1.72), 0.20, M["wood"][1], col="cabin", bevel=0.025)
    for x in [xa + (xb - xa) * t for t in (0.25, 0.5, 0.75)]:
        add_box("Porch front baluster", (x, -4.63, 1.42), (0.16, 0.16, 0.83), M["wood"][1], bevel=0.02, col="cabin")
for i in range(3):
    add_box("Porch step", (cx, -5.05 - i * 0.43, 0.78 - i * 0.22),
            (2.05 + i * 0.15, 0.58, 0.22), random.choice(M["wood"][:3]), bevel=0.025, col="cabin")


def add_lantern(name, loc, scale=1.0, hanging=False):
    x, y, z = loc
    add_box(name + " base", (x, y, z - 0.32 * scale), (0.48 * scale, 0.35 * scale, 0.09 * scale), M["metal"], bevel=0.025 * scale)
    add_box(name + " top", (x, y, z + 0.34 * scale), (0.50 * scale, 0.37 * scale, 0.09 * scale), M["metal"], bevel=0.025 * scale)
    add_cone(name + " cap", (x, y, z + 0.46 * scale), 0.34 * scale, 0.12 * scale, 0.24 * scale, M["metal"], vertices=4, col="props")
    add_box(name + " glass", (x, y, z), (0.34 * scale, 0.22 * scale, 0.55 * scale), M["lantern_glass"], col="props")
    for dx in (-0.20, 0.20):
        for dy in (-0.14, 0.14):
            add_box(name + " frame", (x + dx * scale, y + dy * scale, z), (0.045 * scale, 0.045 * scale, 0.67 * scale), M["metal"], col="props")
    if hanging:
        beam_between(name + " hanging arm", (x, y + 0.06, z + 0.53 * scale), (x, y + 0.06, z + 0.86 * scale), 0.055 * scale, M["metal"])
    add_point_light(name + " point light", (x, y, z), (1.0, 0.28, 0.035), 32 * scale, 0.18 * scale)


add_lantern("Porch lantern", (door_x - 1.35, front_y - 0.82, 3.12), 0.72, hanging=True)
beam_between("Porch lantern bracket", (door_x - 1.35, front_y - 0.30, 3.65), (door_x - 1.35, front_y - 0.83, 3.65), 0.075, M["metal"], col="cabin")

# Barrel beside the door.
barrel_x, barrel_y = -0.45, -3.70
add_cylinder("Porch barrel", (barrel_x, barrel_y, 1.48), 0.42, 0.92, M["wood"][1], vertices=10, col="props")
for z in (1.12, 1.48, 1.84):
    add_cylinder("Barrel iron band", (barrel_x, barrel_y, z), 0.445, 0.065, M["metal"], vertices=10, col="props")
for a in range(0, 360, 60):
    ang = math.radians(a)
    add_box("Barrel stave line", (barrel_x + math.cos(ang) * 0.415, barrel_y + math.sin(ang) * 0.415, 1.48),
            (0.025, 0.025, 0.76), M["wood"][3], rot=(0, 0, ang), col="props")


# Split-rail fence along the left trail.
fence_posts = [(-10.0, -8.5), (-9.6, -5.7), (-9.4, -2.9), (-8.9, 0.0)]
for x, y in fence_posts:
    add_box("Fence post", (x, y, 1.12), (0.34, 0.34, 2.05), M["wood"][1], rot=(0, random.uniform(-0.07, 0.07), random.uniform(-0.05, 0.05)), bevel=0.035)
for (x1, y1), (x2, y2) in zip(fence_posts[:-1], fence_posts[1:]):
    beam_between("Fence rail upper", (x1, y1, 1.45), (x2, y2, 1.62), 0.22, M["wood"][1], bevel=0.03)
    beam_between("Fence rail lower", (x1, y1, 0.75), (x2, y2, 0.92), 0.20, M["wood"][0], bevel=0.03)
add_lantern("Trail lantern", (-9.45, -5.70, 1.28), 0.78, hanging=True)


# -----------------------------------------------------------------------------
# Forest vegetation
# -----------------------------------------------------------------------------

def add_pine(name, x, y, height, radius, tone=1, lean=0.0):
    base = ground_height(x, y)
    trunk_h = height * 0.43
    add_cylinder(name + " trunk", (x, y, base + trunk_h / 2), radius * 0.18, trunk_h, M["trunk"], vertices=7, col="vegetation")
    tiers = [
        (0.28, 0.47, 1.00),
        (0.48, 0.39, 0.78),
        (0.66, 0.31, 0.58),
    ]
    for i, (z_frac, h_frac, r_frac) in enumerate(tiers):
        h = height * h_frac
        z_bottom = base + height * z_frac
        obj = add_cone(
            name + f" foliage tier {i + 1}",
            (x, y, z_bottom + h * 0.5), radius * r_frac, radius * 0.06, h,
            M["pine"][max(0, min(3, tone + (1 if i == 2 and tone < 3 else 0)))],
            vertices=7, col="vegetation",
        )
        obj.rotation_euler.y = lean
    return


pine_data = [
    # Foreground framing trees.
    (-12.5, -7.5, 8.0, 2.65, 1), (-10.3, -2.0, 6.2, 2.0, 2),
    (11.3, -0.5, 10.5, 3.25, 1), (15.0, -6.5, 10.0, 3.2, 2),
    (19.0, -1.0, 8.5, 2.8, 1),
    # Cabin surround.
    (-4.6, 1.0, 7.7, 2.45, 2), (-2.8, 6.0, 8.8, 2.7, 1),
    (8.8, 6.2, 8.7, 2.7, 0), (12.8, 6.5, 9.6, 3.0, 1),
    (7.3, 11.0, 7.8, 2.35, 2), (-8.8, 5.7, 6.8, 2.1, 1),
    # Mid/background layers.
    (-15.0, 7.0, 7.5, 2.1, 2), (-11.8, 11.8, 7.0, 2.0, 1),
    (-7.5, 13.5, 8.0, 2.3, 2), (-2.5, 12.5, 6.7, 1.9, 0),
    (2.0, 14.5, 8.2, 2.4, 1), (5.5, 16.0, 7.0, 2.0, 2),
    (10.3, 14.5, 8.4, 2.5, 1), (15.5, 13.0, 7.5, 2.2, 0),
    (20.0, 10.0, 8.7, 2.6, 1), (-18.0, 15.0, 7.0, 2.1, 1),
    (-13.0, 18.0, 6.8, 2.0, 2), (-5.5, 19.0, 7.6, 2.2, 1),
    (2.0, 20.0, 6.5, 1.9, 2), (9.0, 20.5, 7.3, 2.1, 1),
    (16.0, 19.0, 8.0, 2.3, 2), (22.0, 17.0, 7.5, 2.2, 1),
]
for i, data in enumerate(pine_data):
    add_pine(f"Pine {i + 1}", *data)


def add_bush(name, x, y, scale, tone=1):
    z = ground_height(x, y)
    for i, (dx, dy, ds) in enumerate([(-0.42, 0, 0.72), (0.10, 0.12, 1.0), (0.52, -0.05, 0.68), (0.08, -0.34, 0.66)]):
        add_ico(name + f" lobe {i}", (x + dx * scale, y + dy * scale, z + 0.48 * scale * ds),
                (0.62 * scale * ds, 0.52 * scale * ds, 0.58 * scale * ds), M["pine"][tone], col="vegetation")


for i, (x, y, s, t) in enumerate([
    (-3.1, -4.2, 1.15, 2), (-2.4, -2.0, 0.9, 1), (6.8, -3.6, 1.1, 0),
    (8.6, -3.5, 1.25, 1), (8.3, 1.8, 1.2, 0), (6.3, 4.9, 0.9, 1),
    (-3.5, 3.8, 1.2, 2), (-7.6, -5.5, 0.85, 1), (4.8, -6.7, 0.9, 1),
    (9.4, -7.0, 1.0, 0), (-0.3, -8.0, 0.85, 2), (-8.5, 2.5, 1.0, 1),
]):
    add_bush(f"Forest bush {i + 1}", x, y, s, t)


def add_grass_tuft(name, x, y, scale=1.0):
    z = ground_height(x, y) + 0.05
    verts, faces = [], []
    for i, angle in enumerate((0.0, math.pi / 3, 2 * math.pi / 3, math.pi / 2)):
        dx, dy = math.cos(angle), math.sin(angle)
        base = len(verts)
        verts.extend([
            (x - dy * 0.11 * scale, y + dx * 0.11 * scale, z),
            (x + dy * 0.11 * scale, y - dx * 0.11 * scale, z),
            (x + dx * random.uniform(0.08, 0.25) * scale, y + dy * random.uniform(0.08, 0.25) * scale, z + random.uniform(0.55, 0.90) * scale),
        ])
        faces.append((base, base + 1, base + 2))
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(M["grass"])
    obj = bpy.data.objects.new(name, mesh)
    COL["vegetation"].objects.link(obj)


for i, (x, y, s) in enumerate([
    (-7.0, -8.2, 0.7), (-3.4, -6.8, 0.75), (0.2, -7.7, 0.8),
    (3.2, -7.3, 0.7), (7.9, -8.1, 0.8), (9.6, -4.7, 0.7),
    (-8.8, -1.2, 0.65), (-4.0, 1.4, 0.7), (6.9, 2.7, 0.65),
    (5.6, -4.8, 0.6), (10.8, -6.8, 0.75), (-11.0, -5.1, 0.8),
]):
    add_grass_tuft(f"Grass tuft {i + 1}", x, y, s)


def add_mushroom(name, x, y, scale=1.0):
    z = ground_height(x, y)
    add_cylinder(name + " stem", (x, y, z + 0.18 * scale), 0.07 * scale, 0.34 * scale, M["mushroom_stem"], vertices=7, col="vegetation")
    add_cone(name + " cap", (x, y, z + 0.40 * scale), 0.24 * scale, 0.10 * scale, 0.18 * scale, M["mushroom"], vertices=8, col="vegetation")


for i, (x, y, s) in enumerate([(-4.0, -5.1, 0.8), (8.8, -7.8, 1.0), (10.0, -6.2, 0.65), (-2.2, -3.1, 0.55)]):
    add_mushroom(f"Mushroom {i + 1}", x, y, s)


# -----------------------------------------------------------------------------
# Wood pile, stump and axe
# -----------------------------------------------------------------------------

log_positions = [
    (7.5, -5.95, 0.60), (8.3, -5.95, 0.60), (9.1, -5.95, 0.60),
    (7.9, -5.76, 1.08), (8.7, -5.76, 1.08),
    (8.3, -5.58, 1.56),
]
for i, (x, y, z) in enumerate(log_positions):
    add_cylinder(f"Firewood log {i + 1}", (x, y, z), 0.34, 2.7, random.choice(M["wood"][:3]), vertices=9,
                 rot=(0, math.pi / 2, random.uniform(-0.08, 0.08)), col="props", end_mat=M["log_end"])
for i in range(3):
    beam_between("Woodpile ground rail", (6.4, -6.60 + i * 0.56, 0.32), (9.8, -6.60 + i * 0.56, 0.32), 0.20, M["wood"][3], bevel=0.02)

stump_x, stump_y = 5.25, -5.95
add_cylinder("Chopping stump", (stump_x, stump_y, 0.82), 0.75, 1.35, M["wood"][1], vertices=9, col="props", end_mat=M["log_end"])
for i in range(5):
    ang = math.tau * i / 5 + 0.2
    beam_between("Stump root", (stump_x, stump_y, 0.35),
                 (stump_x + math.cos(ang) * 1.0, stump_y + math.sin(ang) * 0.9, 0.18),
                 0.28, M["wood"][1], bevel=0.035)
# Axe blade is embedded in the stump; its handle leans up toward the trail.
handle_a = (5.20, -5.94, 1.62)
handle_b = (4.28, -4.78, 2.86)
beam_between("Axe handle", handle_a, handle_b, 0.13, M["wood"][2], bevel=0.025)
add_box("Axe head", (5.18, -5.94, 1.58), (0.22, 0.72, 0.48), M["iron"], rot=(0.10, -0.55, 0.12), bevel=0.035)


# -----------------------------------------------------------------------------
# Lighting, camera, rendering
# -----------------------------------------------------------------------------

world = bpy.data.worlds.new("Golden mountain air")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = (0.43, 0.245, 0.125, 1)
bg.inputs["Strength"].default_value = 0.68

sun_data = bpy.data.lights.new("Low golden sun", "SUN")
sun_data.energy = 2.4
sun_data.color = (1.0, 0.58, 0.28)
sun_data.angle = math.radians(13)
sun = bpy.data.objects.new("Low golden sun", sun_data)
sun.rotation_euler = (math.radians(35), math.radians(-28), math.radians(-35))
COL["lights"].objects.link(sun)

area_data = bpy.data.lights.new("Warm key light", "AREA")
area_data.energy = 1050
area_data.color = (1.0, 0.58, 0.30)
area_data.shape = "DISK"
area_data.size = 8.0
area = bpy.data.objects.new("Warm key light", area_data)
area.location = (-9.0, -10.0, 17.0)
area.rotation_euler = (Vector((cx, cy, 3.4)) - area.location).to_track_quat("-Z", "Y").to_euler()
COL["lights"].objects.link(area)

# Soft fill keeps the dark pines readable while preserving the evening mood.
fill_data = bpy.data.lights.new("Forest fill", "AREA")
fill_data.energy = 500
fill_data.color = (0.32, 0.48, 0.58)
fill_data.size = 10.0
fill = bpy.data.objects.new("Forest fill", fill_data)
fill.location = (16.0, -6.0, 12.0)
fill.rotation_euler = (Vector((2.0, 1.0, 3.0)) - fill.location).to_track_quat("-Z", "Y").to_euler()
COL["lights"].objects.link(fill)

camera_data = bpy.data.cameras.new("Storybook camera")
camera = bpy.data.objects.new("Storybook camera", camera_data)
camera.location = (22.0, -37.0, 16.0)
target = Vector((0.1, 0.1, 3.35))
camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
camera_data.lens = 60
camera_data.sensor_width = 36
camera_data.dof.use_dof = True
camera_data.dof.focus_distance = (camera.location - Vector((2.0, -0.2, 3.4))).length
camera_data.dof.aperture_fstop = 1.8
camera_data.dof.aperture_blades = 6
COL["lights"].objects.link(camera)
scene.camera = camera

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.filepath = RENDER_PATH
scene.render.film_transparent = False
scene.render.use_file_extension = True
scene.render.image_settings.color_depth = "8"
scene.render.resolution_percentage = 100

try:
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.look = "AgX - Medium High Contrast"
except Exception:
    pass

# Mild ambient shadowing and enough temporal samples for the many beveled props.
scene.render.engine = "BLENDER_EEVEE"
scene.render.image_settings.file_format = "PNG"
try:
    scene.render.image_settings.color_depth = "8"
except Exception:
    pass

# World floor behind the mountains should never show transparency.
scene.camera.data.lens = 60

bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)

print(f"Saved Blender scene to {BLEND_PATH}")
print(f"Saved render to {RENDER_PATH}")
