import bpy
import math
import os
import random
from mathutils import Vector

"""A hand-built, low-poly forest cabin tableau.

Everything is deliberately modeled from simple primitive geometry: faceted terrain,
stacked timber walls, individually laid roof shingles, and layered pine crowns.
The scene is self-contained so it can be regenerated with Blender in background mode.
"""

ROOT = os.path.dirname(os.path.abspath(__file__))
random.seed(5606)
bpy.ops.wm.read_factory_settings(use_empty=True)


def material(name, color, roughness=0.72, metallic=0.0, emission=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*emission, 1)
        bsdf.inputs['Emission Strength'].default_value = strength
    return m


# Palette: warm timber and light, cool roof/stone, deep evergreen surroundings.
wood_dark = material('Oak - deep grain', (0.105, 0.036, 0.012))
wood = material('Hewn cedar', (0.285, 0.105, 0.028))
wood_light = material('Fresh cut cedar', (0.48, 0.205, 0.052))
wood_end = material('End grain', (0.58, 0.29, 0.10))
roof_dark = material('Charcoal roof', (0.035, 0.040, 0.050))
roof_mid = material('Blue black shingle', (0.095, 0.110, 0.145))
roof_warm = material('Weathered shingle', (0.155, 0.085, 0.058))
stone = material('Foundation granite', (0.20, 0.205, 0.22))
stone_lit = material('Chimney stone', (0.37, 0.335, 0.30))
stone_dark = material('Stone shadow', (0.12, 0.13, 0.15))
grass = material('Mossy clearing', (0.105, 0.22, 0.040))
grass_lit = material('Sunny grass', (0.20, 0.34, 0.070))
dirt = material('Packed path', (0.42, 0.245, 0.105))
dirt_lit = material('Path sun facets', (0.58, 0.34, 0.16))
pine_dark = material('Pine shade', (0.026, 0.095, 0.048))
pine_mid = material('Pine green', (0.035, 0.155, 0.048))
pine_lit = material('Pine tips', (0.11, 0.255, 0.065))
bush_mat = material('Forest shrub', (0.065, 0.22, 0.045))
iron = material('Forged iron', (0.018, 0.014, 0.012), 0.33, 0.62)
glass_glow = material('Golden window light', (1.0, 0.34, 0.025), 0.35, emission=(1.0, 0.19, 0.007), strength=7.5)
lantern_glow = material('Lantern flame', (1.0, 0.22, 0.005), 0.24, emission=(1.0, 0.09, 0.002), strength=13)
red = material('Fly agaric cap', (0.75, 0.035, 0.012))
cream = material('Mushroom stem', (0.73, 0.61, 0.38))
mountain_mat = material('Hazy mountain', (0.24, 0.19, 0.14))
mountain_lit = material('Hazy mountain light', (0.42, 0.30, 0.20))
print('TERRA: materials ready', flush=True)


def smooth(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def cube(name, loc, size, mat=None, rotation=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Small softened edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 1
    return obj


def cylinder(name, loc, radius, depth, mat, vertices=8, rotation=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Edge bevel', 'BEVEL')
        mod.width = bevel
        mod.segments = 1
    return obj


def cone(name, loc, radius1, radius2, depth, mat, vertices=7, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def ico(name, loc, scale, mat, subdivisions=1, rotation=None):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    if rotation:
        obj.rotation_euler = rotation
    obj.data.materials.append(mat)
    return obj


def rotate_toward(obj, point):
    obj.rotation_euler = (Vector(point) - obj.location).to_track_quat('-Z', 'Y').to_euler()


# ---------------------------------------------------------------------------
# Faceted ground, including a deliberately irregular winding path.
# ---------------------------------------------------------------------------
cube('Forest clearing base', (0, 0, -0.38), (42, 37, 0.72), grass, bevel=0.22)

for ix in range(-11, 12):
    for iy in range(-9, 10):
        # Loose large triangles / facets break up an otherwise featureless ground plane.
        x = ix * 1.72 + random.uniform(-0.22, 0.22)
        y = iy * 1.66 + random.uniform(-0.23, 0.23)
        if abs(x) < 5.0 and -8.0 < y < 4.3:
            continue
        ico('Low-poly ground facet', (x, y, -0.005),
            (random.uniform(0.72, 1.25), random.uniform(0.68, 1.20), random.uniform(0.025, 0.065)),
            random.choice([grass, grass, grass_lit]), 1,
            (0, 0, random.uniform(0, math.tau)))

path_points = []
for n in range(34):
    t = n / 33
    y = -16.0 + t * 13.7
    x = -2.7 + 1.45 * math.sin(t * 5.0) + 0.48 * math.sin(t * 12.0)
    path_points.append((x, y))
    for k in range(3):
        px = x + random.uniform(-0.78, 0.78)
        py = y + random.uniform(-0.28, 0.28)
        ico('Path paving facet', (px, py, 0.035),
            (random.uniform(0.38, 0.92), random.uniform(0.35, 0.73), random.uniform(0.045, 0.095)),
            random.choice([dirt, dirt, dirt_lit]), 1, (0, 0, random.uniform(0, math.tau)))
print('TERRA: terrain ready', flush=True)


# ---------------------------------------------------------------------------
# Cabin: sturdy stone plinth, horizontal hewn logs, a framed gable and roof.
# ---------------------------------------------------------------------------
for x in [-3.15, -1.58, 0, 1.58, 3.15]:
    cube('Front foundation blocks', (x, -2.86, 0.36), (1.45, 0.72, 0.68), stone, bevel=0.075)
    cube('Rear foundation blocks', (x, 2.86, 0.36), (1.45, 0.72, 0.68), stone, bevel=0.075)
for y in [-2.05, -0.7, 0.7, 2.05]:
    cube('Foundation side block', (-3.52, y, 0.36), (0.72, 1.20, 0.68), stone, bevel=0.075)
    cube('Foundation side block', (3.52, y, 0.36), (0.72, 1.20, 0.68), stone, bevel=0.075)

log_z = [0.93 + n * 0.43 for n in range(9)]
for n, z in enumerate(log_z):
    logmat = [wood, wood, wood_light, wood][n % 4]
    cube('Front horizontal cabin log', (0, -3.10, z), (7.18, 0.39, 0.38), logmat, bevel=0.058)
    cube('Back horizontal cabin log', (0, 3.10, z), (7.18, 0.39, 0.38), logmat, bevel=0.058)
    cube('Left horizontal cabin log', (-3.49, 0, z), (0.39, 6.15, 0.38), logmat, bevel=0.058)
    cube('Right horizontal cabin log', (3.49, 0, z), (0.39, 6.15, 0.38), logmat, bevel=0.058)

for x in [-3.73, 3.73]:
    for y in [-3.22, 3.22]:
        for z in [1.0, 1.86, 2.72, 3.58]:
            cube('Protruding dovetail log ends', (x, y, z), (0.69, 0.69, 0.36), wood_dark, bevel=0.06)

# Gable is made of vertical planks filling the triangle, held by a timber frame.
for i in range(11):
    x = -2.85 + i * 0.57
    h = max(0.30, 2.58 - abs(x) * 0.82)
    cube('Gable vertical cedar plank', (x, -3.16, 4.55 + h / 2), (0.52, 0.29, h), wood, bevel=0.025)
cube('Gable tie beam', (0, -3.35, 4.58), (7.40, 0.32, 0.32), wood_light, bevel=0.05)
gable_angle = math.radians(39)
for side in [-1, 1]:
    cube('Thick gable fascia', (side * 1.88, -3.38, 5.92), (0.32, 0.35, 4.76), wood_light,
         rotation=(0, side * gable_angle, 0), bevel=0.055)
    cube('Gable inner support', (side * 1.18, -3.36, 5.28), (0.20, 0.30, 3.15), wood_dark,
         rotation=(0, side * gable_angle, 0), bevel=0.035)

# Door and trim.
cube('Front door', (-0.10, -3.34, 2.26), (1.64, 0.22, 3.22), wood_light, bevel=0.035)
for x in [-0.72, -0.10, 0.52]:
    cube('Door vertical board seam', (x, -3.465, 2.26), (0.055, 0.045, 2.90), wood_dark)
for x in [-1.00, 0.80]:
    cube('Door upright frame', (x, -3.46, 2.29), (0.24, 0.27, 3.67), wood_dark, bevel=0.035)
cube('Door lintel', (-0.10, -3.47, 4.11), (2.04, 0.28, 0.26), wood_dark, bevel=0.035)
cylinder('Door iron handle', (0.49, -3.53, 2.27), 0.075, 0.13, iron, 8, rotation=(math.pi / 2, 0, 0))


def front_window(name, x, z, width=1.25, height=1.40):
    y = -3.315
    cube(name + ' amber light', (x, y, z), (width, 0.10, height), glass_glow, bevel=0.018)
    for dx in [-width / 2 - 0.10, width / 2 + 0.10]:
        cube(name + ' outer vertical trim', (x + dx, y - 0.10, z), (0.20, 0.18, height + 0.32), wood_light, bevel=0.026)
    for dz in [-height / 2 - 0.10, height / 2 + 0.10]:
        cube(name + ' outer horizontal trim', (x, y - 0.10, z + dz), (width + 0.38, 0.18, 0.20), wood_light, bevel=0.026)
    cube(name + ' centre mullion', (x, y - 0.14, z), (0.10, 0.16, height), wood_dark)
    cube(name + ' cross mullion', (x, y - 0.14, z), (width, 0.16, 0.10), wood_dark)


front_window('Attic window', (0.0), 5.52, 1.02, 1.18)
front_window('Left cabin window', -2.30, 2.55, 1.16, 1.30)


def side_window(name, y, z, width=1.25, height=1.40):
    x = 3.57
    cube(name + ' amber light', (x, y, z), (0.10, width, height), glass_glow, bevel=0.018)
    for dy in [-width / 2 - 0.10, width / 2 + 0.10]:
        cube(name + ' outer vertical trim', (x + 0.10, y + dy, z), (0.18, 0.20, height + 0.32), wood_light, bevel=0.026)
    for dz in [-height / 2 - 0.10, height / 2 + 0.10]:
        cube(name + ' outer horizontal trim', (x + 0.10, y, z + dz), (0.18, width + 0.38, 0.20), wood_light, bevel=0.026)
    cube(name + ' centre mullion', (x + 0.14, y, z), (0.16, 0.10, height), wood_dark)
    cube(name + ' cross mullion', (x + 0.14, y, z), (0.16, width, 0.10), wood_dark)


side_window('Side window one', -1.42, 2.57, 1.28, 1.34)
side_window('Side window two', 1.37, 2.57, 1.28, 1.34)

# Roof underlays and individually staggered slab shingles.
for side in [-1, 1]:
    cube('Roof plane', (side * 1.83, 0, 5.97), (4.92, 7.32, 0.24), roof_dark,
         rotation=(0, side * gable_angle, 0), bevel=0.035)
    for row in range(8):
        y = -2.89 + row * 0.84
        for col in range(5):
            distance = 0.44 + col * 0.78
            # Nudge along the roof surface normal so every shingle is clearly
            # above the underlay instead of being swallowed by it.
            x = side * distance * math.cos(gable_angle) + side * 0.14
            z = 7.40 - distance * math.sin(gable_angle) + 0.18
            # Rows have a tiny overlap and alternating seams, like actual shingles.
            cube('Staggered roof shingle', (x, y + (col % 2) * 0.10, z + 0.06),
                 (0.98, 0.82, 0.095), random.choice([roof_mid, roof_mid, roof_dark, roof_warm]),
                 rotation=(0, side * gable_angle, 0), bevel=0.018)
cube('Roof ridge pole', (0, 0, 7.49), (0.38, 7.47, 0.30), wood_dark, bevel=0.055)

# Masonry chimney climbing from the rear roof slope.
for row in range(6):
    for yi in range(2):
        for xi in range(2):
            cube('Hand laid chimney block', (1.74 + xi * 0.51 + (row % 2) * 0.06, 1.05 + yi * 0.50, 6.45 + row * 0.39),
                 (0.47, 0.46, 0.35), stone_lit if row % 3 else stone, bevel=0.028)
cube('Chimney cap', (2.02, 1.30, 8.72), (1.50, 1.25, 0.20), iron, bevel=0.035)

# Covered front porch, loose plank seams, staircase and low timber rails.
cube('Porch deck', (-0.12, -4.52, 0.83), (7.55, 2.40, 0.28), wood_light, bevel=0.040)
for i in range(6):
    cube('Porch deck board seam', (-3.14 + i * 1.20, -4.52, 0.986), (0.045, 2.10, 0.024), wood_dark)
for step in range(3):
    cube('Front porch stair', (-0.12, -5.83 - step * 0.42, 0.62 - step * 0.18),
         (2.70 + step * 0.16, 0.72, 0.22), wood_light, bevel=0.03)
for x in [-3.40, 3.18]:
    for y in [-3.70, -5.20]:
        cube('Porch rail post', (x, y, 1.62), (0.27, 0.27, 1.72), wood_light, bevel=0.04)
    cube('Porch handrail', (x, -4.46, 1.72), (0.23, 2.64, 0.20), wood_light, bevel=0.03)
    for y in [-4.00, -4.48, -4.96]:
        cube('Porch baluster', (x, y, 1.37), (0.16, 0.16, 1.12), wood_dark, bevel=0.018)


def lantern(name, loc, scale=1.0):
    x, y, z = loc
    cube(name + ' golden pane', (x, y, z), (0.38 * scale, 0.29 * scale, 0.50 * scale), lantern_glow, bevel=0.022)
    cube(name + ' top', (x, y, z + 0.34 * scale), (0.59 * scale, 0.46 * scale, 0.10 * scale), iron, bevel=0.018)
    cube(name + ' base', (x, y, z - 0.34 * scale), (0.56 * scale, 0.43 * scale, 0.10 * scale), iron, bevel=0.018)
    cone(name + ' roof', (x, y, z + 0.44 * scale), 0.34 * scale, 0.08 * scale, 0.18 * scale, iron, 4)
    for dx in [-0.22, 0.22]:
        cube(name + ' iron upright', (x + dx * scale, y, z), (0.045 * scale, 0.05 * scale, 0.71 * scale), iron)


lantern('Door lantern', (-1.47, -3.62, 3.05), 0.92)
print('TERRA: cabin ready', flush=True)

# ---------------------------------------------------------------------------
# Surrounding low-poly plants / foreground storytelling props.
# ---------------------------------------------------------------------------
def pine(name, x, y, height, tier_count=4, tint=0):
    cylinder(name + ' trunk', (x, y, height * 0.19), height * 0.070, height * 0.40, wood_dark, 7)
    radii = [0.28, 0.235, 0.185, 0.135, 0.09]
    for j in range(tier_count):
        level = 0.34 + j * (0.53 / max(tier_count - 1, 1))
        r = height * radii[j]
        cmat = [pine_dark, pine_mid, pine_lit][(j + tint) % 3]
        cone(name + ' angular crown', (x, y, height * level), r, 0.015, height * 0.34, cmat, 7)


# Tall foreground and middle-ground pines establish the framing and depth hierarchy.
tree_specs = [
    ('Pine L close', -13.4, -3.3, 9.7, 5, 0), ('Pine L middle', -10.7, 3.2, 8.1, 4, 1),
    ('Pine L back', -13.1, 8.0, 9.4, 4, 2), ('Pine back one', -6.0, 7.9, 11.2, 5, 1),
    ('Pine back two', -1.7, 9.6, 9.4, 4, 0), ('Pine back three', 3.8, 10.4, 10.8, 4, 1),
    ('Pine R hero', 10.8, 1.6, 14.2, 5, 2), ('Pine R close', 15.0, -4.0, 11.4, 5, 0),
    ('Pine R behind', 13.0, 7.6, 12.7, 5, 1), ('Pine R rear', 8.1, 8.8, 9.0, 4, 2),
    ('Pine far left', -17.0, 4.5, 10.8, 4, 0), ('Pine far right', 17.3, 7.0, 12.0, 5, 1),
    ('Pine tiny left', -8.6, -0.5, 5.0, 3, 1), ('Pine tiny right', 7.0, -0.1, 6.2, 4, 0),
]
for args in tree_specs:
    pine(*args)
print('TERRA: trees ready', flush=True)

for i in range(52):
    x = random.uniform(-13.8, 13.8)
    y = random.uniform(-10.5, 7.7)
    if -4.7 < x < 4.8 and -6.0 < y < 4.0:
        continue
    ico('Angular undergrowth bush', (x, y, random.uniform(0.30, 0.56)),
        (random.uniform(0.34, 0.93), random.uniform(0.31, 0.80), random.uniform(0.30, 0.72)),
        random.choice([bush_mat, pine_mid, pine_lit]), 1, (0, 0, random.uniform(0, math.tau)))

for i in range(45):
    x = random.uniform(-14.5, 14.5)
    y = random.uniform(-11.5, 9.0)
    # Keep the porch / path readable and mostly unencumbered.
    if abs(x) < 4.0 and -7.0 < y < 4.2:
        continue
    ico('Faceted field rock', (x, y, random.uniform(0.15, 0.28)),
        (random.uniform(0.20, 0.68), random.uniform(0.22, 0.72), random.uniform(0.20, 0.54)),
        random.choice([stone, stone, stone_dark]), 1, (0, 0, random.uniform(0, math.tau)))

for i in range(68):
    x = random.uniform(-13.0, 13.0)
    y = random.uniform(-11.0, 8.5)
    if abs(x) < 3.3 and -7.0 < y < 3.9:
        continue
    for angle in [-0.22, 0, 0.22]:
        cone('Tufted grass blade', (x + angle, y, 0.24), 0.10, 0.0, random.uniform(0.38, 0.75),
             grass_lit if i % 3 else pine_mid, 5, rotation=(0, angle, 0))

# A split rail fence guides the eye along the entrance path.
for x, y in [(-6.6, -9.2), (-6.6, -6.3), (-3.9, -8.8)]:
    cube('Fence post', (x, y, 0.95), (0.28, 0.28, 1.85), wood_light, rotation=(0.04, 0.02, 0.02), bevel=0.035)
cube('Fence upper rail', (-5.25, -8.00, 1.37), (0.22, 3.28, 0.20), wood_light, rotation=(0.02, 0.10, 0.06), bevel=0.03)
cube('Fence lower rail', (-5.25, -8.00, 0.83), (0.18, 3.28, 0.18), wood_dark, rotation=(-0.02, 0.07, 0.06), bevel=0.025)
lantern('Path lantern', (-6.6, -9.2, 1.30), 0.86)

# Firewood stack, chopping stump and axe at lower right.
for row in range(3):
    for j in range(5 - row):
        z = 0.30 + row * 0.39
        y = -7.15 + j * 0.46 + row * 0.16
        log = cylinder('Stacked split firewood', (6.98, y, z), 0.20, 2.12, wood, 8, rotation=(0, math.pi / 2, 0))
        # A small end-grain disk exposes the cut face on the camera side.
        cylinder('Firewood end grain', (5.91, y, z), 0.168, 0.016, wood_end, 8, rotation=(0, math.pi / 2, 0))
cylinder('Chopping stump', (4.45, -6.78, 0.48), 0.72, 0.96, wood_light, 9)
cylinder('Stump top grain', (4.45, -6.78, 0.97), 0.57, 0.018, wood_end, 9)
cube('Axe wooden shaft', (4.58, -6.72, 1.76), (0.13, 0.13, 2.15), wood_light, rotation=(0.12, 0.52, -0.08), bevel=0.025)
cube('Axe iron head', (4.02, -6.74, 2.56), (0.66, 0.19, 0.34), stone_lit, rotation=(0.08, 0.28, -0.04), bevel=0.045)

# Barrel and a handful of cheerful small forest details.
cylinder('Rain barrel', (-2.05, -4.13, 1.35), 0.42, 1.10, wood, 12)
for z in [0.99, 1.35, 1.72]:
    cylinder('Barrel iron hoop', (-2.05, -4.13, z), 0.445, 0.06, iron, 12)
for x, y, s in [(-5.8, -6.8, 1.0), (6.45, -8.4, 1.2), (8.0, -7.0, 0.83), (3.7, -8.7, 0.72)]:
    cylinder('Mushroom pale stem', (x, y, 0.16 * s), 0.07 * s, 0.30 * s, cream, 7)
    cone('Mushroom red cap', (x, y, 0.37 * s), 0.26 * s, 0.025, 0.18 * s, red, 8)

# Layered distant mountains are very simple silhouette geometry, softened by depth-of-field.
for i, (x, y, h, r) in enumerate([(-18.0, 34.0, 15.0, 8.0), (-8.0, 36.0, 19.0, 9.0), (3.0, 37.0, 16.0, 9.0), (14.0, 35.0, 21.0, 10.0), (25.0, 34.0, 16.5, 8.5)]):
    cone('Distant mountain silhouette', (x, y, h / 2 - 0.5), r, 0.0, h, mountain_lit if i % 2 else mountain_mat, 7)
print('TERRA: props and background ready', flush=True)

# ---------------------------------------------------------------------------
# Cinematic golden-hour lighting, foggy glow and a low, cabin-focused camera.
# ---------------------------------------------------------------------------
world = bpy.data.worlds.new('Amber sky world')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.72, 0.56, 0.38, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.35

bpy.ops.object.light_add(type='SUN', location=(-10, -10, 15))
sun = bpy.context.object
sun.name = 'Low golden evening sun'
sun.data.energy = 3.00
sun.data.angle = math.radians(7.5)
sun.data.color = (1.0, 0.62, 0.38)
sun.rotation_euler = (math.radians(31), math.radians(-18), math.radians(-35))

bpy.ops.object.light_add(type='AREA', location=(-5.5, -7.5, 11.0))
key = bpy.context.object
key.name = 'Warm soft key light'
key.data.energy = 1450
key.data.shape = 'DISK'
key.data.size = 7.0
key.data.color = (1.0, 0.62, 0.36)
rotate_toward(key, (0, 0, 2.7))

bpy.ops.object.light_add(type='AREA', location=(7.5, 1.0, 8.0))
fill = bpy.context.object
fill.name = 'Cool forest fill light'
fill.data.energy = 720
fill.data.size = 6.0
fill.data.color = (0.18, 0.34, 0.55)
rotate_toward(fill, (1.0, -0.7, 3.0))

for name, location, energy in [('Door glow light', (-1.45, -3.8, 3.0), 120), ('Window glow light', (2.8, -0.4, 2.8), 100), ('Path glow light', (-6.6, -9.2, 1.8), 65)]:
    bpy.ops.object.light_add(type='POINT', location=location)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.color = (1.0, 0.22, 0.025)
    light.data.shadow_soft_size = 1.2

bpy.ops.object.camera_add(location=(20.0, -32.5, 12.5))
camera = bpy.context.object
camera.name = 'Hero cabin camera'
bpy.context.scene.camera = camera
rotate_toward(camera, (0.0, -0.55, 3.0))
camera.data.lens = 55
camera.data.sensor_width = 36
camera.data.dof.use_dof = True
camera.data.dof.focus_object = bpy.data.objects['Front door']
camera.data.dof.aperture_fstop = 3.0

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1680
scene.render.resolution_y = 945
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.filepath = os.path.join(ROOT, 'terra_cabin_render.png')
scene.render.film_transparent = False
scene.render.image_settings.color_mode = 'RGB'
scene.view_settings.look = 'AgX - Medium High Contrast'

print('TERRA: scene construction complete')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, 'terra_cabin.blend'))
if os.environ.get('TERRA_SKIP_RENDER') != '1':
    print('TERRA: rendering preview')
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, 'terra_cabin.blend'))
