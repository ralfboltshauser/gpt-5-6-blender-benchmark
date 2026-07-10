import bpy
import math
import os
import random
from mathutils import Vector


# A deliberately self-contained, deterministic scene builder.  The individual
# pieces are simple low-poly meshes; the richness comes from their construction
# and layering rather than from texture maps.
ROOT = os.path.dirname(os.path.abspath(__file__))
RNG = random.Random(560816)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1120
scene.render.resolution_y = 630
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.image_settings.color_depth = '8'
scene.render.filepath = os.path.join(ROOT, 'render.png')
scene.render.film_transparent = False
scene.render.use_file_extension = True
scene.render.image_settings.color_management = 'FOLLOW_SCENE'
scene.view_settings.look = 'AgX - Medium High Contrast'
bpy.context.preferences.filepaths.save_version = 0


def make_material(name, color, roughness=0.74, metallic=0.0,
                  emission=None, emission_strength=0.0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = (*color, 1.0)
    bsdf = material.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if emission is not None:
        bsdf.inputs['Emission Color'].default_value = (*emission, 1.0)
        bsdf.inputs['Emission Strength'].default_value = emission_strength
    return material


# Palette: keep most surfaces matte, warm lights and pale sky doing the work.
WOOD_DARK = make_material('walnut timber shadow', (0.105, 0.038, 0.012))
WOOD = make_material('weathered honey pine', (0.285, 0.112, 0.029))
WOOD_LIGHT = make_material('sunlit cut pine', (0.485, 0.225, 0.070))
WOOD_GOLD = make_material('fresh warm timber', (0.365, 0.145, 0.035))
ROOF = make_material('charcoal slate roof', (0.052, 0.047, 0.053))
ROOF_BLUE = make_material('blue black roof variation', (0.037, 0.055, 0.076))
ROOF_BROWN = make_material('weathered roof edge', (0.105, 0.063, 0.045))
STONE = make_material('cool foundation stone', (0.225, 0.245, 0.255))
STONE_DARK = make_material('shadowed fieldstone', (0.145, 0.155, 0.160))
STONE_WARM = make_material('chimney warm gray', (0.355, 0.325, 0.300))
STONE_LIGHT = make_material('highlighted mortar stone', (0.430, 0.398, 0.365))
IRON = make_material('black forged iron', (0.018, 0.013, 0.010), 0.34, 0.75)
GLASS_GLOW = make_material('amber window light', (1.0, 0.280, 0.015), 0.34,
                           emission=(0.75, 0.120, 0.004), emission_strength=2.4)
LANTERN_GLOW = make_material('lantern flame', (1.0, 0.220, 0.010), 0.25,
                             emission=(0.90, 0.115, 0.003), emission_strength=4.8)
GRASS = make_material('moss green earth', (0.185, 0.285, 0.075))
GRASS_LIGHT = make_material('sunlit grass facet', (0.300, 0.405, 0.110))
GRASS_OLIVE = make_material('olive grass facet', (0.140, 0.205, 0.055))
GRASS_DEEP = make_material('deep ground green', (0.066, 0.145, 0.052))
PATH = make_material('ochre path stone', (0.480, 0.285, 0.125))
PATH_LIGHT = make_material('warm path highlight', (0.660, 0.405, 0.190))
PINE_DARK = make_material('deep pine', (0.035, 0.125, 0.050))
PINE = make_material('forest pine', (0.070, 0.215, 0.075))
PINE_LIT = make_material('sunlit olive pine', (0.195, 0.315, 0.100))
BUSH = make_material('low forest bush', (0.085, 0.245, 0.075))
BUSH_LIT = make_material('sunny bush facets', (0.205, 0.360, 0.085))
ROCK = make_material('blue gray rock', (0.330, 0.345, 0.360))
ROCK_DARK = make_material('dark slate rock', (0.215, 0.230, 0.240))
MOUNTAIN_FAR = make_material('misty distant mountain', (0.590, 0.470, 0.340),
                             emission=(0.17, 0.115, 0.065), emission_strength=.22)
MOUNTAIN_NEAR = make_material('soft ridge slate', (0.420, 0.410, 0.355),
                              emission=(0.10, 0.100, 0.075), emission_strength=.16)
WATER = make_material('far stream glint', (0.250, 0.445, 0.480), 0.30)
CUT_WOOD = make_material('split log endgrain', (0.620, 0.330, 0.115))
MUSHROOM_RED = make_material('fly agaric red', (0.73, 0.050, 0.016))
MUSHROOM_CREAM = make_material('mushroom stem', (0.780, 0.630, 0.390))


def assign(obj, material):
    obj.data.materials.append(material)
    return obj


def bevel(obj, amount=0.04, segments=1):
    modifier = obj.modifiers.new('small hand-cut bevel', 'BEVEL')
    modifier.width = amount
    modifier.segments = segments
    return obj


def cube(name, location, dimensions, material, rotation=(0, 0, 0), edge=0.0):
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = tuple(component * 0.5 for component in dimensions)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, material)
    if edge:
        bevel(obj, edge)
    return obj


def cylinder(name, location, radius, depth, material, vertices=8, rotation=(0, 0, 0), edge=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                       location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    assign(obj, material)
    if edge:
        bevel(obj, edge)
    return obj


def cone(name, location, radius_bottom, radius_top, depth, material,
         vertices=7, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius_bottom,
                                   radius2=radius_top, depth=depth,
                                   location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    assign(obj, material)
    return obj


def ico(name, location, scale, material, subdivisions=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1,
                                          location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    assign(obj, material)
    return obj


def track_to(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def point_light(name, location, color, energy, radius=0.5):
    data = bpy.data.lights.new(name, 'POINT')
    data.color = color
    data.energy = energy
    data.shadow_soft_size = radius
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    return obj


# ---------------------------------------------------------------------------
# Faceted terrain and a deliberately uneven path toward the porch.
# ---------------------------------------------------------------------------
def make_terrain():
    step = 2.0
    x_count, y_count = 21, 19
    x0, y0 = -20.0, -17.0
    vertices = []
    for iy in range(y_count):
        for ix in range(x_count):
            x = x0 + ix * step
            y = y0 + iy * step
            # A very shallow height field preserves the hand-cut triangular read.
            z = -0.19 + 0.10 * math.sin(x * 0.23) * math.cos(y * 0.17)
            z += RNG.uniform(-0.055, 0.055)
            vertices.append((x, y, z))
    faces = []
    for iy in range(y_count - 1):
        for ix in range(x_count - 1):
            a = iy * x_count + ix
            b, c, d = a + 1, a + x_count, a + x_count + 1
            if (ix + iy) % 2:
                faces.extend([(a, b, c), (b, d, c)])
            else:
                faces.extend([(a, b, d), (a, d, c)])
    mesh = bpy.data.meshes.new('triangulated forest floor mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.clear()
    for material in (GRASS, GRASS_LIGHT, GRASS_OLIVE, GRASS_DEEP):
        mesh.materials.append(material)
    terrain = bpy.data.objects.new('rolling low-poly forest clearing', mesh)
    bpy.context.collection.objects.link(terrain)
    for polygon in mesh.polygons:
        # Favours a coherent moss base while retaining clearly different facets.
        roll = RNG.random()
        polygon.material_index = 0 if roll < .50 else (1 if roll < .70 else (2 if roll < .91 else 3))
    return terrain


make_terrain()

# Warm broken path, narrow at the porch and spreading toward the foreground.
for i in range(58):
    t = i / 57.0
    y = -15.7 + 10.9 * t
    center_x = -2.45 * (1 - t) + 0.25 * math.sin(t * math.pi * 2.1)
    x = center_x + RNG.uniform(-0.48 - 0.44 * (1 - t), 0.48 + 0.44 * (1 - t))
    radius = RNG.uniform(.36, .72) * (1.08 - 0.24 * t)
    rock = ico('irregular path paver', (x, y, -0.015 + RNG.uniform(-.015, .025)),
               (radius, radius * RNG.uniform(.56, .88), RNG.uniform(.055, .105)),
               PATH_LIGHT if RNG.random() < .27 else PATH, 1)
    rock.rotation_euler[2] = RNG.uniform(0, math.tau)

# A small quiet water glimpse behind the clearing, a useful cool counterpoint.
cube('distant stream', (-10.0, 8.2, -0.10), (6.5, 2.1, .035), WATER, edge=.03)


# ---------------------------------------------------------------------------
# Cabin: stone plinth, stacked timber, framed gable, shingles, chimney.
# ---------------------------------------------------------------------------
front_y, back_y = -2.55, 2.55
wall_half_width = 3.35

# Uneven masonry foundation.
for x in [-2.85, -1.72, -.57, .57, 1.72, 2.85]:
    cube('front foundation block', (x, front_y - .07, .38),
         (1.05 + RNG.uniform(-.10, .11), .53, .63),
         RNG.choice([STONE, STONE, STONE_DARK]), edge=.055)
for y in [-1.82, -.70, .45, 1.60]:
    for x in (-wall_half_width - .02, wall_half_width + .02):
        cube('side foundation block', (x, y, .38),
             (.55, 1.03 + RNG.uniform(-.10, .10), .63),
             RNG.choice([STONE, STONE_DARK, STONE_WARM]), edge=.055)
for x in [-2.86, -1.72, -.57, .57, 1.72, 2.85]:
    cube('rear foundation block', (x, back_y + .07, .38), (1.05, .52, .63), STONE_DARK, edge=.05)

# Dark recessed wall mass makes the timber courses read as discrete pieces.
cube('cabin shadow interior', (0, 0, 2.66), (6.55, 5.00, 4.12), WOOD_DARK, edge=.05)

# Long hand-hewn courses on the front and sides.
log_levels = [0.84 + .49 * i for i in range(8)]
for level, z in enumerate(log_levels):
    material = (WOOD_LIGHT if level in (0, 3, 6) else (WOOD if level % 2 else WOOD_GOLD))
    cube('front horizontal hewn log', (0, front_y - .105, z),
         (6.84, .31, .39), material, edge=.055)
    cube('rear horizontal hewn log', (0, back_y + .105, z),
         (6.84, .31, .39), material, edge=.055)
    for x in (-wall_half_width - .105, wall_half_width + .105):
        cube('side horizontal hewn log', (x, 0, z),
             (.31, 5.02, .39), material, edge=.055)

# Alternating projecting log ends at visible front corners.
for level, z in enumerate(log_levels):
    for x in (-3.53, 3.53):
        dimensions = (.68, .53, .36) if level % 2 else (.49, .67, .36)
        cube('interlocking log corner', (x, front_y - .12, z), dimensions,
             WOOD_DARK if level % 3 == 0 else WOOD_LIGHT, edge=.055)

# Door, plank seams, hardware, and assertive timber trim.
cube('recessed front door', (-.05, front_y - .285, 2.31), (1.56, .17, 2.88), WOOD_GOLD, edge=.035)
for dx in [-.58, -.19, .20, .59]:
    cube('door plank seam', (dx - .05, front_y - .388, 2.30), (.045, .035, 2.60), WOOD_DARK)
for x in (-.94, .84):
    cube('door side jamb', (x, front_y - .38, 2.30), (.20, .20, 3.25), WOOD_LIGHT, edge=.035)
cube('door lintel', (-.05, front_y - .40, 3.92), (2.05, .22, .26), WOOD_LIGHT, edge=.04)
cube('door threshold', (-.05, front_y - .40, .88), (1.78, .22, .16), WOOD_DARK, edge=.02)
cylinder('round door handle', (.55, front_y - .48, 2.30), .075, .14, IRON, 10,
         rotation=(math.pi / 2, 0, 0))
for z in (1.43, 3.10):
    cube('door strap hinge', (-.67, front_y - .48, z), (.23, .045, .105), IRON, edge=.01)


def front_window(name, x, z, width=1.13, height=1.28):
    y = front_y - .275
    cube(name + ' warm glass', (x, y, z), (width, .12, height), GLASS_GLOW, edge=.018)
    # A nested heavier outer frame and slender mullions, set ahead of the glow.
    for dx in (-width / 2 - .11, width / 2 + .11):
        cube(name + ' vertical frame', (x + dx, y - .095, z), (.19, .15, height + .26), WOOD_LIGHT, edge=.025)
    for dz in (-height / 2 - .11, height / 2 + .11):
        cube(name + ' horizontal frame', (x, y - .10, z + dz), (width + .34, .15, .19), WOOD_LIGHT, edge=.025)
    cube(name + ' vertical mullion', (x, y - .19, z), (.07, .06, height), WOOD_DARK)
    cube(name + ' horizontal mullion', (x, y - .20, z), (width, .06, .07), WOOD_DARK)
    point_light(name + ' indoor glow', (x, front_y + .42, z), (1.0, .19, .025), 38, .85)


def side_window(name, y, z, width=1.20, height=1.30):
    x = wall_half_width + .275
    cube(name + ' warm glass', (x, y, z), (.12, width, height), GLASS_GLOW, edge=.018)
    for dy in (-width / 2 - .11, width / 2 + .11):
        cube(name + ' vertical frame', (x + .09, y + dy, z), (.15, .19, height + .26), WOOD_LIGHT, edge=.025)
    for dz in (-height / 2 - .11, height / 2 + .11):
        cube(name + ' horizontal frame', (x + .10, y, z + dz), (.15, width + .34, .19), WOOD_LIGHT, edge=.025)
    cube(name + ' vertical mullion', (x + .19, y, z), (.06, .07, height), WOOD_DARK)
    cube(name + ' horizontal mullion', (x + .20, y, z), (.06, width, .07), WOOD_DARK)
    point_light(name + ' indoor glow', (wall_half_width - .38, y, z), (1.0, .18, .025), 32, .70)


# The visual focus comes from the right side lights and one upper gable light.
side_window('right front mullioned window', -.88, 2.52, 1.05, 1.32)
side_window('right rear mullioned window', 1.34, 2.52, 1.02, 1.28)

# Front gable: a dark triangular field, individual planks, and timber truss.
gable_vertices = [(-3.32, front_y - .14, 4.47), (3.32, front_y - .14, 4.47),
                  (0, front_y - .14, 7.52)]
gable_mesh = bpy.data.meshes.new('front gable triangle mesh')
gable_mesh.from_pydata(gable_vertices, [], [(0, 1, 2)])
gable_mesh.materials.append(WOOD_DARK)
gable = bpy.data.objects.new('deep timber gable', gable_mesh)
bpy.context.collection.objects.link(gable)
for x in [-2.82, -2.18, -1.54, -.90, -.27, .36, 1.00, 1.64, 2.28, 2.84]:
    height = max(.22, 2.86 - abs(x) * .90)
    cube('vertical gable plank', (x, front_y - .225, 4.48 + height * .50),
         (.48, .15, height), WOOD if RNG.random() < .58 else WOOD_GOLD, edge=.025)

front_window('small glowing loft window', (0), 5.70, .86, 1.00)
roof_angle = math.radians(40.0)
cube('gable lower tie beam', (0, front_y - .35, 4.57), (6.95, .23, .24), WOOD_LIGHT, edge=.045)
for side in (-1, 1):
    cube('heavy gable rafter', (side * 1.78, front_y - .37, 6.05),
         (4.66, .26, .28), WOOD_LIGHT, rotation=(0, side * roof_angle, 0), edge=.045)
for side in (-1, 1):
    cube('gable diagonal brace', (side * 1.22, front_y - .39, 5.31),
         (2.20, .18, .17), WOOD_GOLD, rotation=(0, side * roof_angle, 0), edge=.025)

# Steep roof shell.  Individual shingle rows sit on top, with an overlap that
# is apparent at the eaves and a slight blue-black variation across the field.
for side in (-1, 1):
    cube('broad roof underlay', (side * 1.88, .10, 5.90), (4.86, 6.35, .19),
         ROOF, rotation=(0, side * roof_angle, 0), edge=.035)
    for row in range(7):
        x = side * (3.56 - row * .52)
        z = 4.34 + (3.70 - abs(x)) * math.tan(roof_angle) + .13
        for column in range(8):
            y = -2.75 + column * .78 + (.34 if row % 2 else 0)
            if y > 2.93:
                continue
            material = ROOF_BLUE if RNG.random() < .19 else (ROOF_BROWN if RNG.random() < .10 else ROOF)
            shingle = cube('staggered roof shingle', (x, y, z), (.78, .83, .095), material,
                           rotation=(0, side * roof_angle, RNG.uniform(-.016, .016)), edge=.018)
            # Minimal displacement makes rows catch highlights without looking noisy.
            shingle.location.z += RNG.uniform(-.018, .018)

# Crisp fascia pieces and a dark ridge cap complete the silhouette.
for side in (-1, 1):
    cube('front roof fascia', (side * 1.92, front_y - .47, 5.92), (4.98, .20, .24),
         WOOD_DARK, rotation=(0, side * roof_angle, 0), edge=.035)
    cube('rear roof fascia', (side * 1.92, back_y + .47, 5.92), (4.98, .20, .24),
         WOOD_DARK, rotation=(0, side * roof_angle, 0), edge=.035)
cube('roof ridge cap', (0, .10, 7.52), (.31, 6.60, .30), WOOD_DARK, edge=.05)

# Chunky individual chimney stones rise from the visible right slope.
for course in range(5):
    z = 6.38 + course * .42
    for xi in range(2):
        for yi in range(2):
            x = 1.44 + xi * .47 + (.05 if course % 2 else 0)
            y = .48 + yi * .47
            material = RNG.choice([STONE_WARM, STONE_WARM, STONE, STONE_LIGHT])
            cube('separate chimney fieldstone',
                 (x + RNG.uniform(-.028, .028), y + RNG.uniform(-.025, .025), z),
                 (.45 + RNG.uniform(-.035, .035), .44 + RNG.uniform(-.035, .035), .36),
                 material, edge=.035)
cube('wide chimney cap', (1.70, .72, 8.35), (1.40, 1.23, .17), IRON, edge=.035)
cylinder('chimney dark flue', (1.70, .72, 8.49), .34, .18, IRON, 8)


# ---------------------------------------------------------------------------
# Porch, rail, lantern, and a few deliberately readable cabin-life props.
# ---------------------------------------------------------------------------
cube('raised porch deck', (0, -3.98, .83), (7.05, 2.34, .24), WOOD_GOLD, edge=.045)
for x in [-2.90, -1.72, -.54, .64, 1.82, 3.00]:
    cube('separate porch board', (x, -4.01, .98), (1.02, 2.16, .085),
         WOOD_LIGHT if int((x + 3) * 10) % 3 else WOOD, edge=.018)
for step in range(3):
    cube('front porch stair', (0, -5.33 - step * .43, .66 - step * .19),
         (2.48 + step * .16, .74, .20), WOOD_LIGHT, edge=.035)

# Side rails leave a central entrance open.
for x in (-3.05, 3.05):
    for y in (-4.89, -3.45):
        cube('squared porch rail post', (x, y, 1.64), (.24, .24, 1.58), WOOD_LIGHT, edge=.035)
    cube('porch side top rail', (x, -4.15, 2.07), (.20, 1.72, .17), WOOD_LIGHT, edge=.025)
    cube('porch side lower rail', (x, -4.15, 1.38), (.15, 1.72, .12), WOOD_GOLD, edge=.02)
    for y in (-4.55, -4.13, -3.71):
        cube('porch side baluster', (x, y, 1.67), (.13, .13, .83), WOOD_GOLD, edge=.018)
for x in (-2.25, -1.50, 1.50, 2.25):
    cube('front rail baluster', (x, -5.03, 1.52), (.14, .14, .94), WOOD_GOLD, edge=.02)
for x_center in (-2.25, 2.25):
    cube('front short rail', (x_center, -5.03, 1.97), (1.32, .17, .15), WOOD_LIGHT, edge=.025)


def lantern(name, location, scale=1.0, point_energy=58):
    x, y, z = location
    cube(name + ' amber core', (x, y, z), (.30 * scale, .22 * scale, .48 * scale), LANTERN_GLOW, edge=.025)
    cube(name + ' top', (x, y, z + .33 * scale), (.47 * scale, .34 * scale, .09 * scale), IRON, edge=.018)
    cube(name + ' base', (x, y, z - .33 * scale), (.43 * scale, .31 * scale, .08 * scale), IRON, edge=.018)
    for dx in (-.18 * scale, .18 * scale):
        cube(name + ' iron side', (x + dx, y, z), (.035 * scale, .045 * scale, .69 * scale), IRON)
    cylinder(name + ' little roof', (x, y, z + .43 * scale), .29 * scale, .12 * scale, IRON, 4)
    point_light(name + ' flame light', (x, y, z), (1.0, .17, .015), point_energy, 0.75 * scale)


# Wall bracket plus lantern, held under a small beam.
cube('lantern bracket arm', (-1.65, front_y - .45, 3.30), (.62, .09, .09), IRON, edge=.015)
cube('lantern bracket drop', (-1.96, front_y - .45, 3.10), (.08, .09, .46), IRON, edge=.015)
lantern('porch hanging lantern', (-1.96, front_y - .49, 2.72), .80, 45)

# A small barrel sits to one side of the door.
cylinder('porch barrel body', (-2.35, -4.22, 1.38), .41, .93, WOOD_GOLD, 12)
for z in (1.04, 1.37, 1.72):
    cylinder('barrel iron hoop', (-2.35, -4.22, z), .44, .055, IRON, 12)

# Split rail fence and freestanding lantern at the left of the path.
fence_points = [(-8.30, -8.25), (-6.70, -7.65), (-7.82, -5.72)]
for x, y in fence_points:
    cube('rough fence upright', (x, y, .82), (.22, .22, 1.40), WOOD_LIGHT, edge=.035,
         rotation=(RNG.uniform(-.03, .03), RNG.uniform(-.03, .03), RNG.uniform(-.08, .08)))
cube('upper split rail', (-7.50, -7.95, 1.12), (1.73, .14, .15), WOOD_GOLD, rotation=(0, 0, .20), edge=.035)
cube('lower split rail', (-7.24, -6.73, .77), (1.88, .14, .14), WOOD_GOLD, rotation=(0, 0, -.72), edge=.035)
lantern('fence path lantern', (-6.70, -7.65, 1.22), .78, 33)

# Firewood, stump, and axe provide the foreground counterpart to the cabin.
for row in range(3):
    for log_index in range(5 - row):
        y = -7.00 + log_index * .48 + row * .22
        z = .27 + row * .43
        log = cylinder('stacked chopped firewood', (7.20, y, z), .205, 2.25,
                       WOOD_DARK if (row + log_index) % 2 else WOOD, 8,
                       rotation=(0, math.pi / 2, 0))
        # A cut face on the camera side prevents the pile from reading as rods.
        cylinder('visible cut log end', (6.05, y, z), .166, .020, CUT_WOOD, 8,
                 rotation=(0, math.pi / 2, 0))
        log.rotation_euler[0] += RNG.uniform(-.04, .04)
cylinder('chopping stump', (4.72, -6.63, .54), .71, 1.03, WOOD_GOLD, 9)
cylinder('stump cut top', (4.72, -6.63, 1.07), .59, .025, CUT_WOOD, 9)
for a in range(6):
    angle = a * math.tau / 6 + .18
    cube('stump root flare', (4.72 + math.cos(angle) * .53, -6.63 + math.sin(angle) * .53, .18),
         (.42, .30, .22), WOOD_GOLD, rotation=(0, 0, angle), edge=.025)
cube('axe hickory handle', (4.15, -6.75, 1.57), (.12, .12, 2.15), WOOD_LIGHT,
     rotation=(0, .63, -.05), edge=.025)
cube('axe forged head', (3.56, -6.75, 2.45), (.53, .19, .35), IRON,
     rotation=(0, .18, 0), edge=.035)


# ---------------------------------------------------------------------------
# Forest: layered conifers, bush clusters, rocks, grass and mushrooms.
# ---------------------------------------------------------------------------
def pine_tree(name, x, y, scale, foreground=False):
    trunk_height = 2.15 * scale
    cylinder(name + ' faceted trunk', (x, y, trunk_height * .50), .24 * scale,
             trunk_height, WOOD_DARK, 7)
    # Distinct tiers, not a smooth cone, give the trees their graphic silhouette.
    tiers = [(1.42, 1.12, 1.60), (2.40, .92, 1.45), (3.25, .70, 1.30), (4.00, .44, 1.14)]
    for tier_index, (z, radius, height) in enumerate(tiers):
        material = (PINE_LIT if tier_index == 3 and foreground else
                    (PINE_DARK if tier_index == 0 else (PINE if tier_index % 2 else PINE_LIT)))
        foliage = cone(name + ' separated pine tier', (x, y, z * scale), radius * scale,
                       .035 * scale, height * scale, material, 7,
                       rotation=(0, 0, RNG.uniform(-.23, .23)))
        foliage.rotation_euler[0] = RNG.uniform(-.025, .025)
        foliage.rotation_euler[1] = RNG.uniform(-.025, .025)


# Far trees are smaller and cooler, while edge trees frame the house.
background_trees = [
    (-15.3, 8.8, 1.10), (-12.1, 8.0, 1.28), (-9.1, 10.1, 1.02),
    (-6.6, 8.5, 1.22), (-4.2, 11.2, 1.06), (-1.8, 9.5, .93),
    (1.2, 11.1, 1.17), (4.2, 9.3, 1.09), (7.1, 11.0, 1.27),
    (10.0, 8.4, 1.45), (13.1, 9.4, 1.15), (16.0, 7.6, 1.35),
    (-13.4, 3.5, 1.40), (-9.8, 4.4, 1.05), (-6.6, 4.8, .92),
    (8.5, 4.0, 1.18), (12.5, 2.2, 1.55),
]
for index, (x, y, scale) in enumerate(background_trees):
    pine_tree('background fir %02d' % index, x, y, scale, False)

# Foreground trees stay deliberately out of focus but make the composition feel enclosed.
for index, (x, y, scale) in enumerate([(-13.5, -5.5, 2.08), (-10.3, -2.1, 1.60),
                                         (10.1, -.60, 2.35), (14.0, -5.8, 2.55),
                                         (-16.8, -10.2, 2.65), (22.0, -10.5, 2.55)]):
    pine_tree('foreground framing fir %02d' % index, x, y, scale, True)

# Bushes and stones are carefully excluded from the cabin floor and central path.
for index in range(56):
    for attempt in range(30):
        x = RNG.uniform(-14.5, 14.5)
        y = RNG.uniform(-12.5, 8.3)
        path_x = -2.45 * (1 - max(0, min(1, (y + 15.7) / 10.9)))
        if not (-4.7 < x < 4.7 and -6.2 < y < 3.8) and abs(x - path_x) > 1.25:
            break
    size = RNG.uniform(.34, .90)
    bush = ico('angular forest shrub', (x, y, .28 + size * .39),
               (size, size * RNG.uniform(.72, 1.14), size * RNG.uniform(.52, .90)),
               BUSH_LIT if RNG.random() < .25 else BUSH, 1)
    bush.rotation_euler = (RNG.uniform(-.2, .2), RNG.uniform(-.2, .2), RNG.uniform(0, math.tau))

for index in range(42):
    for attempt in range(30):
        x = RNG.uniform(-14.0, 14.0)
        y = RNG.uniform(-13.0, 8.0)
        if not (-4.8 < x < 5.0 and -6.3 < y < 3.5):
            break
    scale = RNG.uniform(.22, .70)
    rock = ico('low poly clearing rock', (x, y, scale * .34 - .05),
               (scale * RNG.uniform(.72, 1.20), scale * RNG.uniform(.65, 1.12), scale),
               ROCK if RNG.random() < .62 else ROCK_DARK, 1)
    rock.rotation_euler = (RNG.uniform(-.28, .28), RNG.uniform(-.28, .28), RNG.uniform(0, math.tau))


def grass_tuft(x, y, scale=1.0):
    for offset, angle in [(-.13, -.25), (0, 0), (.13, .24)]:
        blade = cone('triangular grass blade', (x + offset * scale, y, .26 * scale),
                     .085 * scale, 0, .58 * scale, PINE_LIT, 3)
        blade.rotation_euler[1] = angle


for index in range(94):
    x = RNG.uniform(-13.5, 13.5)
    y = RNG.uniform(-12.5, 7.7)
    if not (-4.6 < x < 4.8 and -6.0 < y < 3.6) and abs(x + 1.8) > .7:
        grass_tuft(x, y, RNG.uniform(.55, 1.2))

for x, y, size in [(6.45, -9.05, .83), (8.30, -7.72, .56), (7.60, -8.45, .38),
                    (-4.45, -7.18, .46), (3.50, -8.72, .40)]:
    cylinder('mushroom pale stem', (x, y, .20 * size), .10 * size, .42 * size, MUSHROOM_CREAM, 7)
    cone('mushroom red cap', (x, y, .48 * size), .34 * size, 0.03 * size, .22 * size,
         MUSHROOM_RED, 9)


# Layered, deliberately pale mountain facets beyond the trees.
for index, (x, y, radius, height, material) in enumerate([
        (-15.0, 27.3, 7.1, 5.8, MOUNTAIN_FAR), (-7.2, 29.8, 8.2, 6.9, MOUNTAIN_FAR),
        (1.4, 30.2, 8.7, 7.9, MOUNTAIN_NEAR), (10.4, 29.5, 8.3, 6.9, MOUNTAIN_FAR),
        (18.0, 27.0, 7.5, 6.0, MOUNTAIN_NEAR)]):
    cone('faceted distant mountain %02d' % index, (x, y, height * .42 - .25), radius,
         .12, height, material, 6, rotation=(0, 0, RNG.uniform(-.15, .15)))


# ---------------------------------------------------------------------------
# Golden late-day lighting, a warm sky and a cinematic three-quarter view.
# ---------------------------------------------------------------------------
world = bpy.data.worlds.new('peach evening sky')
world.use_nodes = True
background = world.node_tree.nodes.get('Background')
background.inputs['Color'].default_value = (0.250, 0.130, 0.055, 1.0)
background.inputs['Strength'].default_value = .50
scene.world = world

# A broad front-left key gives the wood its golden separation; the sun keeps long
# graphic shadows while a very gentle cool fill preserves roof/forest detail.
bpy.ops.object.light_add(type='AREA', location=(-10.5, -13.5, 15.5))
key = bpy.context.object
key.name = 'large soft late afternoon key'
key.data.energy = 880
key.data.shape = 'DISK'
key.data.size = 7.5
key.data.color = (1.0, .62, .30)
track_to(key, (0, -1.2, 2.6))

bpy.ops.object.light_add(type='SUN', location=(-10, -12, 14))
sun = bpy.context.object
sun.name = 'low golden sun direction'
sun.data.energy = 1.30
sun.data.angle = math.radians(5.0)
sun.data.color = (1.0, .65, .34)
track_to(sun, (0, 0, 0))

bpy.ops.object.light_add(type='AREA', location=(8.0, 5.0, 10.5))
fill = bpy.context.object
fill.name = 'soft cool forest fill'
fill.data.energy = 570
fill.data.shape = 'DISK'
fill.data.size = 9.0
fill.data.color = (.23, .42, .52)
track_to(fill, (0, 0, 3.0))

# Camera: slightly above the doorway, three-quarter to the visible right wall.
bpy.ops.object.camera_add(location=(17.2, -29.0, 12.6))
camera = bpy.context.object
camera.name = 'cinematic cabin camera'
scene.camera = camera
track_to(camera, (.20, -.60, 3.05))
camera.data.lens = 55
camera.data.sensor_width = 36
camera.data.dof.use_dof = True
camera.data.dof.focus_object = bpy.data.objects['recessed front door']
camera.data.dof.aperture_fstop = 3.7
camera.data.dof.aperture_blades = 7

# Eevee options retained only where the current Blender build exposes them.
if hasattr(scene, 'eevee'):
    try:
        scene.eevee.taa_samples = 48
    except Exception:
        pass

scene.camera.data.lens = 55
scene.render.filepath = os.path.join(ROOT, 'render.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, 'terra_ultra.blend'))
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, 'terra_ultra.blend'))
