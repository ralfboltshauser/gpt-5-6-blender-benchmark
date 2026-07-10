import bpy
import math
import os
import random
from mathutils import Vector


OUT = "/home/ralf/prj/exploration/blender-benchmark/gpt-5.6-luna-extra-high"
random.seed(5606)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1120
scene.render.resolution_y = 760
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.color_depth = "8"
scene.render.film_transparent = False
scene.render.filepath = os.path.join(OUT, "luna_extra_high.png")
scene.render.image_settings.color_mode = "RGB"
try:
    scene.view_settings.look = "AgX - Medium High Contrast"
except Exception:
    pass


# ---------- materials ----------
def material(name, color, roughness=0.75, metallic=0.0, emission=None, emission_strength=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*color, 1.0)
    bs.inputs["Roughness"].default_value = roughness
    bs.inputs["Metallic"].default_value = metallic
    if emission is not None:
        bs.inputs["Emission Color"].default_value = (*emission, 1.0)
        bs.inputs["Emission Strength"].default_value = emission_strength
    return m


WOOD = material("pine logs", (0.30, 0.115, 0.035), 0.9)
WOOD_LIGHT = material("fresh cut timber", (0.55, 0.235, 0.065), 0.86)
WOOD_DARK = material("deep wood shadow", (0.12, 0.036, 0.012), 0.92)
WOOD_MID = material("warm timber variation", (0.39, 0.145, 0.040), 0.88)
ROOF = material("charcoal roof", (0.050, 0.055, 0.070), 0.92)
ROOF_ALT = material("aged roof tile", (0.135, 0.125, 0.135), 0.88)
STONE = material("cool foundation stone", (0.24, 0.25, 0.25), 0.96)
STONE_DARK = material("stone shadow", (0.15, 0.17, 0.17), 0.99)
GRASS = material("forest floor", (0.17, 0.275, 0.085), 0.96)
GRASS_LIGHT = material("sunlit grass", (0.29, 0.38, 0.105), 0.96)
PINE_DARK = material("pine green", (0.075, 0.19, 0.060), 0.98)
PINE_MID = material("pine mid green", (0.13, 0.29, 0.085), 0.98)
PINE_LIGHT = material("pine lit green", (0.26, 0.39, 0.12), 0.98)
TRUNK = material("fir trunks", (0.20, 0.075, 0.025), 0.98)
PATH = material("ochre path", (0.55, 0.34, 0.17), 0.96)
PATH_LIGHT = material("path highlights", (0.70, 0.45, 0.24), 0.96)
MOUNTAIN_A = material("distant mountain warm", (0.48, 0.39, 0.29), 1.0)
MOUNTAIN_B = material("distant mountain haze", (0.61, 0.52, 0.40), 1.0)
MOUNTAIN_C = material("distant mountain light", (0.70, 0.60, 0.46), 1.0)
SKY = material("warm evening sky", (0.40, 0.235, 0.125), 1.0, emission=(0.25, 0.08, 0.018), emission_strength=0.55)
GLASS = material("golden window glow", (0.84, 0.34, 0.018), 0.28, emission=(1.0, 0.30, 0.010), emission_strength=1.35)
LANTERN_GLASS = material("lantern amber", (0.94, 0.38, 0.025), 0.25, emission=(1.0, 0.28, 0.010), emission_strength=1.85)
IRON = material("black iron", (0.028, 0.023, 0.018), 0.31, 0.72)
MUSHROOM_RED = material("mushroom red", (0.73, 0.10, 0.025), 0.84)
MUSHROOM_ORANGE = material("mushroom orange", (0.88, 0.26, 0.045), 0.84)
MUSHROOM_STEM = material("mushroom stems", (0.71, 0.52, 0.30), 0.92)
AXE_STEEL = material("axe steel", (0.20, 0.21, 0.19), 0.35, 0.8)


def assign(obj, mat):
    obj.data.materials.append(mat)
    return obj


def cube(name, loc, scale, mat, bevel=0.0, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, mat)
    if bevel:
        mod = obj.modifiers.new("soft hewn edges", "BEVEL")
        mod.width = bevel
        mod.segments = 1
    return obj


def cyl(name, loc, radius, depth, mat, vertices=8, rot=(0.0, 0.0, 0.0), bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    assign(obj, mat)
    if bevel:
        mod = obj.modifiers.new("worn edge", "BEVEL")
        mod.width = bevel
        mod.segments = 1
    return obj


def cone(name, loc, r1, r2, depth, mat, vertices=7, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    assign(obj, mat)
    return obj


def ico(name, loc, scale, mat, subdivisions=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, mat)
    return obj


def beam_between(name, a, b, width, depth, mat):
    a, b = Vector(a), Vector(b)
    vec = b - a
    obj = cube(name, (a + b) * 0.5, (vec.length * 0.5, width, depth), mat, bevel=0.025)
    obj.rotation_euler = vec.to_track_quat("X", "Z").to_euler()
    return obj


def point_light(name, loc, energy, color=(1.0, 0.28, 0.04), radius=0.35):
    bpy.ops.object.light_add(type="POINT", location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = energy
    light.data.color = color
    light.data.shadow_soft_size = radius
    return light


# ---------- ground and distant setting ----------
ground = cyl("faceted forest clearing", (0.0, 0.0, -0.38), 16.0, 0.75, GRASS, vertices=64)
ground.rotation_euler[2] = math.radians(3.0)

# warm, layered low-poly mountain silhouettes
mountains = [(-11, 12, 4.0, 9.0, MOUNTAIN_C), (-6, 13, 5.0, 11.0, MOUNTAIN_B), (-1, 14, 4.2, 9.0, MOUNTAIN_C), (5, 13, 5.0, 10.0, MOUNTAIN_A), (11, 14, 5.0, 12.0, MOUNTAIN_B)]
for i, (x, y, radius, height, mat) in enumerate(mountains):
    cone("distant mountain", (x, y, height * 0.5 - 0.2), radius, 0.15, height, mat, vertices=7)
    if i % 2 == 0:
        cone("mountain snow facet", (x - 0.6, y - 0.15, height * 0.73), radius * 0.32, 0.02, height * 0.46, MOUNTAIN_C, vertices=5)

# path stones: a loose, gently bending approach from the foreground
path_points = [(-2.9, -10.0), (-2.45, -8.9), (-2.0, -7.8), (-1.9, -6.8), (-1.45, -5.9), (-1.15, -5.1), (-0.75, -4.4), (-0.2, -3.7), (0.0, -3.0)]
for i, (x, y) in enumerate(path_points):
    for j in range(3 if i < 3 else 2):
        px = x + (j - 1) * random.uniform(0.42, 0.62) + random.uniform(-0.14, 0.14)
        py = y + random.uniform(-0.30, 0.30)
        s = random.uniform(0.38, 0.72) * (1.0 if i < 7 else 0.82)
        stone = ico("path stepping stone", (px, py, 0.06), (s, random.uniform(0.25, 0.48), random.uniform(0.055, 0.10)), random.choice([PATH, PATH, PATH_LIGHT]), 1)
        stone.rotation_euler[2] = random.uniform(-0.55, 0.55)

# scattered polygonal ground plates add the illustrated faceted look
for i in range(42):
    x, y = random.uniform(-13, 13), random.uniform(-9, 7)
    if -4.6 < x < 5.0 and -3.0 < y < 2.8:
        continue
    plate = ico("ground facet", (x, y, 0.018), (random.uniform(0.55, 1.35), random.uniform(0.42, 1.15), 0.035), random.choice([GRASS, GRASS, GRASS_LIGHT, PINE_MID]), 1)
    plate.rotation_euler[2] = random.random() * math.tau


# ---------- cabin shell ----------
CX, FRONT, BACK = 1.25, -2.20, 2.20
BODY_W, BODY_D, EAVE_Z = 3.55, 2.20, 4.05

# foundation courses, individually spaced like rough stone blocks
for z, rowscale in [(0.34, 1.0), (0.72, 0.96)]:
    for y in [FRONT + 0.05, BACK - 0.05]:
        for x in [CX - 3.0, CX - 1.8, CX - 0.6, CX + 0.6, CX + 1.8, CX + 3.0]:
            cube("foundation block", (x + random.uniform(-0.04, 0.04), y, z), (0.54 * rowscale, 0.38, 0.18), random.choice([STONE, STONE, STONE_DARK]), 0.06)
    for x in [CX - BODY_W + 0.08, CX + BODY_W - 0.08]:
        for y in [-1.45, -0.25, 0.95, 2.0]:
            cube("foundation corner block", (x, y, z), (0.38, 0.50, 0.18), random.choice([STONE, STONE_DARK]), 0.06)

# solid log wall mass behind the trim
cube("cabin timber core", (CX, 0.0, 2.35), (BODY_W, BODY_D, 1.65), WOOD, 0.08)

# horizontal log courses and corner joinery
for z in [1.05, 1.62, 2.19, 2.76, 3.33, 3.90]:
    cube("front log course", (CX, FRONT - 0.10, z), (BODY_W + 0.15, 0.17, 0.18), random.choice([WOOD, WOOD, WOOD_MID, WOOD_LIGHT]), 0.045)
    cube("back log course", (CX, BACK + 0.10, z), (BODY_W + 0.15, 0.17, 0.18), WOOD_DARK, 0.045)
    cube("left log course", (CX - BODY_W - 0.02, 0.0, z), (0.17, BODY_D + 0.10, 0.18), WOOD_MID, 0.045)
    cube("right log course", (CX + BODY_W + 0.02, 0.0, z), (0.17, BODY_D + 0.10, 0.18), WOOD_LIGHT, 0.045)

# chunky corner posts
for x in [CX - BODY_W - 0.06, CX + BODY_W + 0.06]:
    for y in [FRONT - 0.10, BACK + 0.10]:
        cube("corner timber", (x, y, 2.45), (0.22, 0.22, 1.80), WOOD_DARK, 0.04)

# roof base planes with a steep alpine pitch
roof_angle = math.radians(42.0)
ridge_z = 7.10
roof_slope = math.tan(roof_angle)
for side in [-1, 1]:
    y = side * 1.28
    z = ridge_z - abs(y) * roof_slope
    base = cube("roof plane", (CX, y, z), (BODY_W + 0.58, 1.65, 0.15), ROOF, 0.035, rot=(-side * roof_angle, 0.0, 0.0))
    # staggered tile rows, with a little color variation in each course
    for row in range(5):
        yy = side * (0.28 + row * 0.52)
        zz = ridge_z - abs(yy) * roof_slope + 0.16
        for col in range(7):
            xx = CX - 3.10 + col * 1.03 + (0.50 if row % 2 else 0.0)
            if xx > CX + 3.25:
                continue
            tile = cube("individual roof shingle", (xx, yy, zz), (0.54, 0.32, 0.065), ROOF_ALT if (row + col) % 4 == 0 else ROOF, 0.018, rot=(-side * roof_angle, 0.0, 0.0))

# front triangular gable face
verts = [(CX - BODY_W, FRONT - 0.05, EAVE_Z), (CX + BODY_W, FRONT - 0.05, EAVE_Z), (CX, FRONT - 0.05, ridge_z - 0.08)]
mesh = bpy.data.meshes.new("gable triangle mesh")
mesh.from_pydata(verts, [], [(0, 1, 2)])
mesh.update()
gable = bpy.data.objects.new("front gable", mesh)
bpy.context.collection.objects.link(gable)
assign(gable, WOOD_MID)

# heavy gable framing and ridge cap
beam_between("left gable rafter", (CX - BODY_W - 0.12, FRONT - 0.20, EAVE_Z - 0.05), (CX, FRONT - 0.20, ridge_z + 0.08), 0.15, 0.16, WOOD_LIGHT)
beam_between("right gable rafter", (CX + BODY_W + 0.12, FRONT - 0.20, EAVE_Z - 0.05), (CX, FRONT - 0.20, ridge_z + 0.08), 0.15, 0.16, WOOD_LIGHT)
beam_between("gable cross beam", (CX - 2.05, FRONT - 0.23, 4.42), (CX + 2.05, FRONT - 0.23, 4.42), 0.14, 0.14, WOOD_LIGHT)


# ---------- doors, windows and porch ----------
def front_window(x, z, w=0.78, h=1.18):
    cube("front glowing window", (x, FRONT - 0.29, z), (w, 0.055, h), GLASS, 0.025)
    cube("window top frame", (x, FRONT - 0.36, z + h + 0.11), (w + 0.16, 0.10, 0.10), WOOD_LIGHT, 0.035)
    cube("window sill", (x, FRONT - 0.36, z - h - 0.11), (w + 0.18, 0.11, 0.10), WOOD_LIGHT, 0.035)
    cube("window left frame", (x - w - 0.08, FRONT - 0.36, z), (0.10, 0.10, h + 0.15), WOOD_LIGHT, 0.035)
    cube("window right frame", (x + w + 0.08, FRONT - 0.36, z), (0.10, 0.10, h + 0.15), WOOD_LIGHT, 0.035)
    cube("window mullion vertical", (x, FRONT - 0.39, z), (0.045, 0.065, h), WOOD_DARK, 0.02)
    cube("window mullion horizontal", (x, FRONT - 0.39, z), (w, 0.065, 0.045), WOOD_DARK, 0.02)
    point_light("warm window light", (x, FRONT + 0.05, z), 52, (1.0, 0.20, 0.025), 0.45)


def side_window(y, z, w=0.72, h=1.08):
    x = CX + BODY_W + 0.29
    cube("right side glowing window", (x, y, z), (0.055, w, h), GLASS, 0.025)
    cube("side top frame", (x + 0.06, y, z + h + 0.10), (0.10, w + 0.14, 0.10), WOOD_LIGHT, 0.03)
    cube("side sill", (x + 0.06, y, z - h - 0.10), (0.10, w + 0.14, 0.10), WOOD_LIGHT, 0.03)
    cube("side left frame", (x + 0.06, y - w - 0.08, z), (0.10, 0.10, h + 0.14), WOOD_LIGHT, 0.03)
    cube("side right frame", (x + 0.06, y + w + 0.08, z), (0.10, 0.10, h + 0.14), WOOD_LIGHT, 0.03)
    cube("side mullion", (x + 0.07, y, z), (0.065, 0.045, h), WOOD_DARK, 0.02, rot=(0.0, 0.0, math.radians(90)))
    point_light("side window light", (x - 0.05, y, z), 48, (1.0, 0.22, 0.03), 0.45)


front_window(CX - 2.25, 2.32, 0.55, 0.86)
front_window(CX + 2.25, 2.32, 0.55, 0.86)
side_window(-0.10, 2.32, 0.58, 0.86)

# door and deep trim
cube("front door", (CX, FRONT - 0.32, 1.95), (0.72, 0.10, 1.42), WOOD_MID, 0.045)
cube("door left jamb", (CX - 0.84, FRONT - 0.39, 1.95), (0.12, 0.14, 1.58), WOOD_LIGHT, 0.04)
cube("door right jamb", (CX + 0.84, FRONT - 0.39, 1.95), (0.12, 0.14, 1.58), WOOD_LIGHT, 0.04)
cube("door lintel", (CX, FRONT - 0.39, 3.57), (0.96, 0.14, 0.13), WOOD_LIGHT, 0.04)
for z in [1.16, 1.72, 2.28]:
    cube("door plank", (CX, FRONT - 0.44, z), (0.62, 0.025, 0.025), WOOD_DARK, 0.01)
cube("door handle", (CX + 0.49, FRONT - 0.52, 1.96), (0.07, 0.05, 0.07), IRON, 0.025)

# little triangular loft window
cube("loft glowing window", (CX, FRONT - 0.31, 5.18), (0.28, 0.05, 0.34), GLASS, 0.025)
beam_between("loft window diagonal A", (CX - 0.45, FRONT - 0.40, 4.67), (CX, FRONT - 0.40, 5.55), 0.06, 0.05, WOOD_DARK)
beam_between("loft window diagonal B", (CX + 0.45, FRONT - 0.40, 4.67), (CX, FRONT - 0.40, 5.55), 0.06, 0.05, WOOD_DARK)
point_light("loft light", (CX, FRONT + 0.02, 5.18), 70, (1.0, 0.22, 0.025), 0.5)

# porch deck, stairs, rails
cube("front porch deck", (CX, FRONT - 0.88, 0.98), (2.58, 0.92, 0.14), WOOD_LIGHT, 0.045)
for x in [CX - 2.35, CX + 2.35]:
    cube("porch post", (x, FRONT - 1.60, 1.95), (0.13, 0.13, 1.04), WOOD_DARK, 0.035)
    cube("porch post cap", (x, FRONT - 1.60, 3.04), (0.22, 0.20, 0.08), WOOD_LIGHT, 0.03)
cube("porch front rail", (CX, FRONT - 1.60, 1.64), (2.35, 0.10, 0.10), WOOD_LIGHT, 0.03)
cube("porch left rail", (CX - 2.35, FRONT - 1.10, 1.64), (0.10, 0.50, 0.10), WOOD_LIGHT, 0.03)
cube("porch right rail", (CX + 2.35, FRONT - 1.10, 1.64), (0.10, 0.50, 0.10), WOOD_LIGHT, 0.03)
for x in [CX - 1.8, CX - 0.9, CX, CX + 0.9, CX + 1.8]:
    cube("porch baluster", (x, FRONT - 1.60, 1.14), (0.07, 0.07, 0.48), WOOD_LIGHT, 0.02)
for i in range(3):
    cube("front step", (CX, FRONT - 2.35 - i * 0.38, 0.74 - i * 0.24), (1.10 + i * 0.18, 0.38, 0.12), WOOD_LIGHT, 0.04)

# door lantern
cube("door lantern frame", (CX - 1.30, FRONT - 0.62, 2.05), (0.27, 0.10, 0.37), IRON, 0.03)
cube("door lantern glass", (CX - 1.30, FRONT - 0.73, 2.05), (0.18, 0.025, 0.27), LANTERN_GLASS, 0.015)
point_light("door lantern glow", (CX - 1.30, FRONT - 0.78, 2.05), 110, (1.0, 0.18, 0.02), 0.5)


# ---------- chimney ----------
chim_x, chim_y = CX + 2.05, 0.62
chimney_blocks = [
    (chim_x - 0.26, chim_y - 0.28), (chim_x + 0.26, chim_y - 0.28),
    (chim_x - 0.26, chim_y + 0.28), (chim_x + 0.26, chim_y + 0.28),
]
for row in range(5):
    for bi, (x, y) in enumerate(chimney_blocks):
        shift = 0.12 if row % 2 and bi in [1, 2] else 0.0
        cube("chimney brick", (x + shift, y, 5.86 + row * 0.36), (0.25, 0.26, 0.16), random.choice([STONE, STONE, STONE_DARK]), 0.035)
cube("chimney cap", (chim_x, chim_y, 7.78), (0.68, 0.66, 0.13), IRON, 0.04)
cube("chimney neck", (chim_x, chim_y, 7.58), (0.34, 0.34, 0.18), STONE_DARK, 0.03)


# ---------- trees, bushes and small forest details ----------
def pine_tree(x, y, s=1.0, palette=(PINE_DARK, PINE_MID, PINE_LIGHT)):
    cyl("faceted fir trunk", (x, y, 1.18 * s), 0.22 * s, 2.35 * s, TRUNK, vertices=7)
    levels = [(2.12, 1.10, 1.55), (2.95, 0.88, 1.45), (3.70, 0.63, 1.35)]
    for i, (z, r, h) in enumerate(levels):
        tier = cone("layered pine crown", (x, y, z * s), r * s, 0.06 * s, h * s, palette[min(i, 2)], vertices=7)
        tier.rotation_euler[2] = (i % 2) * math.radians(13)


tree_list = [
    (-8.7, -2.7, 1.75), (-7.8, 3.7, 1.20), (-6.6, 8.0, 1.45), (-4.8, 5.0, 1.10),
    (-3.6, 8.8, 1.35), (6.8, 5.6, 1.65), (8.9, 1.7, 1.45), (10.7, 6.6, 1.22),
    (11.3, -3.0, 1.65), (-11.0, 4.6, 1.50), (10.0, -8.0, 0.90), (-8.8, -7.5, 1.12),
]
for x, y, s in tree_list:
    pine_tree(x, y, s)

# smaller understory trees around the cabin, kept low to preserve sightlines
for x, y, s in [(-5.4, -1.2, 0.72), (-4.7, 1.0, 0.62), (5.8, -0.3, 0.68), (6.7, -2.0, 0.82), (4.9, 2.2, 0.58)]:
    pine_tree(x, y, s, (PINE_DARK, PINE_MID, PINE_MID))

for i in range(34):
    x, y = random.uniform(-10.5, 10.5), random.uniform(-6.8, 4.7)
    if 0.0 < x < 5.8 and -3.2 < y < 2.8:
        continue
    ico("low polygon bush", (x, y, random.uniform(0.22, 0.43)), (random.uniform(0.32, 0.75), random.uniform(0.26, 0.65), random.uniform(0.28, 0.62)), random.choice([PINE_DARK, PINE_MID, PINE_LIGHT]), 1)

def grass_clump(x, y, s=1.0):
    for ang in [-0.38, 0.0, 0.34]:
        blade = cone("tuft of grass", (x + ang * 0.16 * s, y, 0.34 * s), 0.10 * s, 0.018 * s, 0.72 * s, GRASS_LIGHT, vertices=4)
        blade.rotation_euler[1] = ang
        blade.rotation_euler[2] = random.uniform(-0.25, 0.25)


for i in range(30):
    grass_clump(random.uniform(-10, 10), random.uniform(-7, 1), random.uniform(0.65, 1.2))

for i in range(18):
    x, y = random.uniform(-10, 10), random.uniform(-6.5, 4.5)
    if 0.0 < x < 5.8 and -3.4 < y < 2.5:
        continue
    rock = ico("angular forest rock", (x, y, random.uniform(0.17, 0.34)), (random.uniform(0.28, 0.62), random.uniform(0.25, 0.56), random.uniform(0.25, 0.48)), random.choice([STONE, STONE_DARK]), 1)
    rock.rotation_euler[2] = random.random() * math.tau


def mushroom(x, y, s=1.0, cap_mat=MUSHROOM_RED):
    cyl("mushroom stem", (x, y, 0.28 * s), 0.12 * s, 0.48 * s, MUSHROOM_STEM, vertices=7)
    cone("mushroom cap", (x, y, 0.56 * s), 0.35 * s, 0.04 * s, 0.24 * s, cap_mat, vertices=8)


for x, y, s, m in [(7.8, -5.9, 1.15, MUSHROOM_RED), (9.1, -5.4, 0.85, MUSHROOM_ORANGE), (-4.0, -5.0, 0.72, MUSHROOM_ORANGE), (-6.1, -3.8, 0.60, MUSHROOM_RED)]:
    mushroom(x, y, s, m)


# ---------- fence, woodpile, stump and axe ----------
for x in [-10.0, -8.0, -6.0, -4.0]:
    cube("fence post", (x, -4.65, 0.78), (0.14, 0.14, 0.95), WOOD_DARK, 0.035)
for z in [0.63, 1.18]:
    cube("fence rail", (-7.0, -4.65, z), (3.05, 0.11, 0.11), WOOD_LIGHT, 0.025)
cube("fence rail diagonal", (-7.0, -4.66, 0.90), (3.05, 0.10, 0.08), WOOD_MID, 0.025, rot=(0.0, math.radians(-8.0), 0.0))

# stump
cyl("cut stump", (7.25, -4.50, 0.53), 0.62, 1.06, WOOD_MID, vertices=9, bevel=0.05)
cyl("pale stump top", (7.25, -4.50, 1.075), 0.52, 0.045, WOOD_LIGHT, vertices=9)
for r in [0.16, 0.31, 0.45]:
    # rings made from thin dark cylinders give a readable cut surface
    cyl("stump growth ring", (7.25, -4.50, 1.10 + r * 0.001), r, 0.012, WOOD_DARK, vertices=9)

# woodpile: alternating logs with visible cut ends
for row in range(3):
    for j in range(4 - (row % 2)):
        x = 8.1 + j * 0.77 + (0.32 if row % 2 else 0.0)
        y = -4.55 + row * 0.18
        z = 0.43 + row * 0.43
        angle = math.radians(random.uniform(-2.5, 2.5))
        cyl("stacked firewood", (x, y, z), 0.27, 2.05, WOOD_MID if row % 2 else WOOD_LIGHT, vertices=8, rot=(0.0, math.radians(90.0), angle))
        cyl("cut log end", (x + 1.04, y - math.sin(angle) * 0.05, z), 0.205, 0.025, WOOD_DARK, vertices=8, rot=(0.0, math.radians(90.0), angle))

# axe embedded in stump
beam_between("axe handle", (7.55, -4.43, 1.08), (8.20, -4.35, 2.15), 0.07, 0.07, WOOD_LIGHT)
axe_head = cube("axe head", (8.23, -4.35, 2.18), (0.26, 0.08, 0.19), AXE_STEEL, 0.035)
axe_head.rotation_euler[1] = math.radians(-18.0)


# lantern along the path
def path_lantern(x, y, scale=1.0):
    cyl("lantern pole", (x, y, 0.82 * scale), 0.055 * scale, 1.45 * scale, IRON, vertices=6)
    cube("lantern body", (x, y, 1.56 * scale), (0.23 * scale, 0.18 * scale, 0.29 * scale), LANTERN_GLASS, 0.025)
    cube("lantern top", (x, y, 1.90 * scale), (0.29 * scale, 0.23 * scale, 0.06 * scale), IRON, 0.02)
    cube("lantern base", (x, y, 1.20 * scale), (0.29 * scale, 0.23 * scale, 0.06 * scale), IRON, 0.02)
    point_light("path lantern glow", (x, y, 1.56 * scale), 120 * scale, (1.0, 0.18, 0.02), 0.40 * scale)


path_lantern(-5.25, -4.25, 0.90)
path_lantern(-1.15, -3.05, 0.72)


# ---------- lighting, camera, atmosphere ----------
world = bpy.data.worlds.new("amber mountain world")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.055, 0.082, 0.12, 1.0)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.48

# large warm key from upper left/front, plus a cool fill for the shaded forest
bpy.ops.object.light_add(type="AREA", location=(-7.5, -9.0, 13.0))
key = bpy.context.object
key.name = "late afternoon sun"
key.data.energy = 1100
key.data.shape = "DISK"
key.data.size = 7.5
key.data.color = (1.0, 0.62, 0.36)
key.rotation_euler = (math.radians(24), 0.0, math.radians(-28))

bpy.ops.object.light_add(type="AREA", location=(10.0, 2.0, 8.0))
fill = bpy.context.object
fill.name = "cool forest fill"
fill.data.energy = 850
fill.data.size = 10.0
fill.data.color = (0.40, 0.53, 0.62)
fill.rotation_euler = (math.radians(55), 0.0, math.radians(160))

# camera framing prioritizes the cabin, with foreground path and woodpile creating depth
bpy.ops.object.camera_add(location=(15.8, -22.8, 10.2))
camera = bpy.context.object
camera.name = "storybook camera"
camera.data.lens = 53
camera.data.sensor_width = 36
camera.data.dof.use_dof = True
camera.data.dof.focus_object = gable
camera.data.dof.aperture_fstop = 5.2
camera.rotation_euler = (Vector((0.55, -0.10, 2.85)) - camera.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = camera

# subtle depth haze in the far setting
scene.view_settings.exposure = 0.20

# The scene is deliberately self-contained and Eevee-compatible on the installed
# Blender 5.0 runtime; the bright emissive windows provide the warm focal glow.

# Save and render
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "luna_extra_high.blend"))
bpy.ops.render.render(write_still=True)
