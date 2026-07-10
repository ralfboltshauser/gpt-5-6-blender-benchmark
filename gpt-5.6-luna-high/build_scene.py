import bpy
import math
import random
from mathutils import Vector

random.seed(42)

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def mat(name, color, roughness=0.8, metallic=0.0, emission=None, emission_strength=0.0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    if emission is not None:
        # Blender 4/5 uses Emission Color and Emission Strength.
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = (*emission, 1.0)
        elif 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = (*emission, 1.0)
        if 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = emission_strength
    return m

def assign(obj, material):
    obj.data.materials.append(material)
    return obj

def cube(name, loc, scale, material, bevel=0.0, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rotation)
    o = bpy.context.object
    o.name = name
    o.scale = (scale[0] / 2, scale[1] / 2, scale[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        mod = o.modifiers.new('soft edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 1
    return assign(o, material)

def cyl(name, loc, radius, depth, material, vertices=8, rotation=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rotation)
    o = bpy.context.object
    o.name = name
    if bevel > 0:
        mod = o.modifiers.new('edge wear', 'BEVEL')
        mod.width = bevel
        mod.segments = 1
    return assign(o, material)

def ico(name, loc, scale, material, subdivisions=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return assign(o, material)

def cone(name, loc, radius1, radius2, depth, material, vertices=8, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=loc, rotation=rotation)
    o = bpy.context.object
    o.name = name
    return assign(o, material)

def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

def beam_between(name, a, b, thickness, material, bevel=0.03):
    a, b = Vector(a), Vector(b)
    mid = (a + b) * 0.5
    vec = b - a
    o = cube(name, mid, (thickness, thickness, vec.length), material, bevel=bevel)
    o.rotation_euler = vec.to_track_quat('Z', 'Y').to_euler()
    return o

def window(name, loc, width, height, front=True):
    # A softly glowing amber pane with chunky timber frame.
    x, y, z = loc
    if front:
        pane = cube(name + '_glow', (x, y, z), (width, 0.07, height), glow, bevel=0.03)
        cube(name + '_top', (x, y - 0.06, z + height/2 + 0.09), (width + .28, .18, .16), wood_light, bevel=.035)
        cube(name + '_bottom', (x, y - 0.06, z - height/2 - 0.09), (width + .28, .18, .16), wood_light, bevel=.035)
        cube(name + '_left', (x - width/2 - .09, y - 0.06, z), (.16, .18, height + .3), wood_light, bevel=.035)
        cube(name + '_right', (x + width/2 + .09, y - 0.06, z), (.16, .18, height + .3), wood_light, bevel=.035)
        cube(name + '_cross_v', (x, y - .11, z), (.07, .12, height), wood_dark, bevel=.01)
        cube(name + '_cross_h', (x, y - .11, z), (width, .12, .07), wood_dark, bevel=.01)
        light = bpy.data.lights.new(name + '_light', 'POINT')
        light.energy = 75
        light.color = (1.0, 0.42, 0.10)
        light.shadow_soft_size = 1.0
        lo = bpy.data.objects.new(name + '_light', light)
        bpy.context.collection.objects.link(lo)
        lo.location = (x, y + .18, z)
    else:
        pane = cube(name + '_glow', (x, y, z), (0.07, width, height), glow, bevel=0.03)
        cube(name + '_top', (x + .06, y, z + height/2 + 0.09), (.18, width + .28, .16), wood_light, bevel=.035)
        cube(name + '_bottom', (x + .06, y, z - height/2 - 0.09), (.18, width + .28, .16), wood_light, bevel=.035)
        cube(name + '_left', (x + .06, y - width/2 - .09, z), (.18, .16, height + .3), wood_light, bevel=.035)
        cube(name + '_right', (x + .06, y + width/2 + .09, z), (.18, .16, height + .3), wood_light, bevel=.035)
        cube(name + '_cross_v', (x + .11, y, z), (.12, .07, height), wood_dark, bevel=.01)
        cube(name + '_cross_h', (x + .11, y, z), (.12, width, .07), wood_dark, bevel=.01)
        light = bpy.data.lights.new(name + '_light', 'POINT')
        light.energy = 85
        light.color = (1.0, 0.42, 0.10)
        light.shadow_soft_size = 1.0
        lo = bpy.data.objects.new(name + '_light', light)
        bpy.context.collection.objects.link(lo)
        lo.location = (x - .18, y, z)
    return pane

def tree(x, y, z, s=1.0, lean=0.0, dark=False):
    trunk_mat = trunk_dark if dark else trunk
    foliage = pine_dark if dark else pine
    cyl('pine trunk', (x, y, z + 1.25*s), .22*s, 2.5*s, trunk_mat, vertices=7, rotation=(0, lean, 0))
    # Layered irregular cones: a key part of the stylized reference silhouette.
    layers = [(2.15, 1.35, .15), (3.0, 1.12, .35), (3.72, .82, .55), (4.32, .52, .73)]
    for i, (height, radius, offset) in enumerate(layers):
        cone('faceted pine crown', (x + lean*height*.10, y, z + height*s), radius*s, .06*s, 1.35*s*(1.0 - i*.06), foliage, vertices=7)

def stone(loc, scale, material=None):
    if material is None:
        material = stone_mat
    o = ico('angular field stone', loc, scale, material, subdivisions=1)
    o.rotation_euler = (random.random(), random.random(), random.random())
    return o

# ------------------------------------------------------------
# Materials
# ------------------------------------------------------------
ground_mat = mat('mossy ground', (0.17, 0.25, 0.10), .95)
grass_mat = mat('pathside grass', (0.25, 0.38, 0.12), .92)
grass_light = mat('sunlit grass', (0.42, 0.52, 0.15), .9)
path_mat = mat('warm earth path', (0.48, 0.30, 0.16), .98)
path_light = mat('path stones', (0.66, 0.45, 0.28), .95)
wood = mat('aged pine wood', (0.29, 0.12, 0.045), .82)
wood_light = mat('fresh cut wood', (0.52, 0.25, 0.08), .75)
wood_dark = mat('deep wood seams', (0.10, 0.035, 0.015), .9)
roof_mat = mat('charcoal roof shingles', (0.055, 0.06, 0.07), .85)
roof_alt = mat('shingle variation', (0.085, 0.09, 0.11), .85)
stone_mat = mat('blue grey stone', (0.22, 0.24, 0.26), .9)
stone_light = mat('pale chimney stone', (0.48, 0.46, 0.41), .86)
pine = mat('pine needles', (0.18, 0.28, 0.07), .9)
pine_dark = mat('shadowed pine needles', (0.10, 0.18, 0.055), .93)
trunk = mat('tree bark', (0.20, 0.09, 0.035), .95)
trunk_dark = mat('dark bark', (0.12, 0.055, 0.025), .95)
rock_mat = mat('granite', (0.25, 0.27, 0.29), .94)
metal = mat('iron hardware', (0.045, 0.04, 0.03), .62, metallic=.45)
glow = mat('candlelit window', (1.0, .16, .01), .3, emission=(1.0, .045, .002), emission_strength=2.8)
lantern_glow = mat('lantern flame', (1.0, .32, .045), .25, emission=(1.0, .18, .02), emission_strength=8.0)
water = mat('distant blue water', (.16, .30, .31), .25)
snow = mat('mountain haze', (.56, .52, .43), .95)

# ------------------------------------------------------------
# Reset and render settings
# ------------------------------------------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    pass

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 600
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = '/home/ralf/prj/exploration/blender-benchmark/gpt-5.6-luna-high/cabin_render.png'
scene.render.film_transparent = False
scene.render.image_settings.color_mode = 'RGBA'
scene.render.resolution_percentage = 100
scene.render.engine = 'BLENDER_EEVEE'
scene.world.color = (0.035, 0.025, 0.02)
world = scene.world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (0.20, 0.12, 0.065, 1.0)
bg.inputs['Strength'].default_value = 0.42

# Color management.
try:
    scene.view_settings.look = 'AgX - Medium High Contrast'
except Exception:
    pass

# ------------------------------------------------------------
# Ground and distant environment
# ------------------------------------------------------------
cube('large forest floor', (0, 2, -0.35), (42, 44, .5), ground_mat)

# Low-poly distant mountain masses behind the trees.
for i, x in enumerate([-16, -11, -6, -1, 4, 9, 14, 19]):
    h = random.uniform(6.5, 11.0)
    w = random.uniform(5.0, 8.0)
    cone('distant mountain', (x, 15 + random.uniform(-1, 2), h/2 - .1), w, .15, h, snow, vertices=7)
    # small dark foothill in front of each mountain
    ico('hazy foothill', (x + random.uniform(-1,1), 12, 2.2), (w*1.1, 1.6, 2.3), mat('foothill %d'%i, (0.28, .30, .20), .98), subdivisions=1)

# A sliver of river/pond in the left background.
cube('distant water', (-7.0, 8.5, .02), (6.0, 1.8, .06), water)

# Background pines, intentionally softened by distance and camera DOF.
for i in range(26):
    x = random.uniform(-14, 15)
    y = random.uniform(5.0, 12.5)
    s = random.uniform(.55, 1.35)
    tree(x, y, 0, s, random.uniform(-.08,.08), dark=(i % 3 == 0))

# ------------------------------------------------------------
# Cabin body, foundation, roof
# ------------------------------------------------------------
cx, cy = 2.2, 1.0
wall_bottom = 1.05
wall_top = 4.15
cube('cabin main body', (cx, cy, (wall_bottom+wall_top)/2), (5.7, 4.1, wall_top-wall_bottom), wood, bevel=.06)

# Horizontal plank faces on front and visible right wall.
for i, z in enumerate([1.35, 1.77, 2.19, 2.61, 3.03, 3.45, 3.87]):
    cube('front wall plank', (cx, cy-2.07, z), (5.55, .09, .34), wood_light if i%3==0 else wood, bevel=.025)
for i, y in enumerate([-0.2, .38, .96, 1.54, 2.12]):
    cube('side wall plank', (cx+2.87, y, 2.55), (.09, .52, 2.85), wood_light if i%2==0 else wood, bevel=.025)

# Stone foundation blocks.
for x in [cx-2.35, cx-1.55, cx-.75, cx+.05, cx+.85, cx+1.65, cx+2.45]:
    cube('foundation stone front', (x, cy-2.16, .78), (.72, .42, .62), stone_mat, bevel=.05, rotation=(0,0,random.uniform(-.03,.03)))
for y in [-.45, .35, 1.15, 1.95, 2.55]:
    cube('foundation stone side', (cx+2.95, y, .78), (.42, .72, .62), stone_mat, bevel=.05, rotation=(0,0,random.uniform(-.03,.03)))

# Roof slabs.
ridge_z = 6.45
eave_z = 4.02
eave_x = 3.25
half_ridge = .34
dx = eave_x - half_ridge
dz = ridge_z - eave_z
roof_angle = math.atan2(dz, dx)
roof_len = math.sqrt(dx*dx + dz*dz) + .22
roof_y_len = 4.65
cube('right roof plane', (cx + (eave_x+half_ridge)/2, cy, (eave_z+ridge_z)/2), (roof_len, roof_y_len, .24), roof_mat, bevel=.03, rotation=(0, roof_angle, 0))
cube('left roof plane', (cx - (eave_x+half_ridge)/2, cy, (eave_z+ridge_z)/2), (roof_len, roof_y_len, .24), roof_mat, bevel=.03, rotation=(0, -roof_angle, 0))

# Shingle rows as dark overlapping tiles on the visible right slope.
for row in range(5):
    t = (row + .55) / 5.3
    x = cx + half_ridge + t*dx
    z = ridge_z - t*dz + .03
    for col in range(-3, 4):
        y = cy + col*.65 + (0.30 if row%2 else 0)
        # small tiles follow the roof slope. Slightly separated for graphic read.
        tile = cube('individual roof shingle', (x, y, z), (.72, .73, .12), roof_alt if (row+col)%3==0 else roof_mat, bevel=.02, rotation=(0, roof_angle, 0))

# Front gable triangle.
verts = [(cx-eave_x+.15, cy-2.24, eave_z+.05), (cx+eave_x-.15, cy-2.24, eave_z+.05), (cx, cy-2.24, ridge_z-.1)]
mesh = bpy.data.meshes.new('gable mesh')
mesh.from_pydata(verts, [], [(0,1,2)])
mesh.update()
gable = bpy.data.objects.new('front triangular gable', mesh)
bpy.context.collection.objects.link(gable)
assign(gable, wood)

# Structural beams around gable and corners.
beam_between('left roof fascia', (cx-eave_x, cy-2.40, eave_z), (cx, cy-2.40, ridge_z), .18, wood_light)
beam_between('right roof fascia', (cx, cy-2.40, ridge_z), (cx+eave_x, cy-2.40, eave_z), .18, wood_light)
for x in [cx-2.75, cx+2.75]:
    cube('front corner timber', (x, cy-2.22, 2.55), (.22, .20, 3.1), wood_light, bevel=.03)
cube('gable crossbeam', (cx, cy-2.38, 3.72), (4.85, .18, .18), wood_light, bevel=.03)

# Gable window and triangular trim.
window('attic window', (cx, cy-2.36, 4.95), 1.0, 1.05, front=True)
beam_between('attic left trim', (cx-.55,cy-2.48,4.40),(cx,cy-2.48,5.65),.10,wood_light,bevel=.02)
beam_between('attic right trim', (cx,cy-2.48,5.65),(cx+.55,cy-2.48,4.40),.10,wood_light,bevel=.02)

# Main front door, frame, planks, knob.
cube('front door', (cx+.25, cy-2.31, 2.35), (1.22, .14, 2.25), wood_dark, bevel=.035)
for i in range(5):
    cube('door board', (cx+.25, cy-2.40, 1.52+i*.40), (1.02, .06, .32), wood_light if i%2 else wood, bevel=.015)
cube('door lintel', (cx+.25, cy-2.44, 3.53), (1.55, .18, .18), wood_light, bevel=.03)
cube('door jamb L', (cx-.48, cy-2.43, 2.35), (.18,.18,2.55), wood_light, bevel=.03)
cube('door jamb R', (cx+.98, cy-2.43, 2.35), (.18,.18,2.55), wood_light, bevel=.03)
cyl('iron door handle', (cx+.72, cy-2.53, 2.35), .075, .12, metal, vertices=8, rotation=(math.pi/2,0,0))

# Front window to left of door and side window toward camera.
window('front window', (cx-1.55, cy-2.30, 2.65), 1.15, 1.35, front=True)
window('side window', (cx+2.93, cy+.55, 2.65), 1.25, 1.35, front=False)

# Chimney built from individual pale blocks.
chimney_x, chimney_y = cx+1.25, cy+.55
for row in range(5):
    for col in range(2):
        cube('chimney block', (chimney_x + (col-.5)*.45, chimney_y, 5.35 + row*.38), (.42, .75, .32), stone_light, bevel=.035)
cube('chimney cap', (chimney_x, chimney_y, 7.28), (1.05, 1.0, .18), roof_mat, bevel=.03)

# ------------------------------------------------------------
# Porch, steps, railings and lantern
# ------------------------------------------------------------
cube('front porch floor', (cx, cy-2.95, 1.22), (3.65, 1.55, .22), wood_light, bevel=.04)
for x in [cx-1.55, cx+1.55]:
    cube('porch post', (x, cy-3.40, 2.05), (.18, .18, 1.65), wood_light, bevel=.03)
cube('porch rail left', (cx-1.55, cy-3.40, 2.48), (.18,.18,2.8), wood_light, bevel=.03, rotation=(0,math.pi/2,0))
cube('porch rail right', (cx+1.55, cy-3.40, 2.48), (.18,.18,2.8), wood_light, bevel=.03, rotation=(0,math.pi/2,0))
cube('porch rail front', (cx, cy-3.40, 2.48), (3.2,.18,.18), wood_light, bevel=.03)
for x in [cx-1.05, cx-.35, cx+.35, cx+1.05]:
    cube('porch baluster', (x, cy-3.40, 2.08), (.12,.12,.9), wood_light, bevel=.02)
for i in range(4):
    y = cy-3.72 - i*.38
    z = 1.00 - i*.18
    cube('porch stair', (cx, y, z), (1.85-i*.18, .55, .20), wood_light, bevel=.035)

# Hanging lantern left of door.
cube('lantern bracket', (cx-2.25, cy-2.40, 2.75), (.12,.12,.8), metal, bevel=.02)
cube('lantern roof', (cx-2.25, cy-2.46, 2.98), (.52,.40,.10), metal, bevel=.02)
cube('lantern glass', (cx-2.25, cy-2.46, 2.68), (.30,.25,.42), lantern_glow, bevel=.025)
for xx in [cx-2.42,cx-2.08]: cube('lantern frame', (xx,cy-2.61,2.68),(.04,.05,.5),metal,bevel=.01)
ll = bpy.data.lights.new('porch lantern light','POINT'); ll.energy=130; ll.color=(1.0,.25,.05); ll.shadow_soft_size=.7
lo=bpy.data.objects.new('porch lantern light',ll); bpy.context.collection.objects.link(lo); lo.location=(cx-2.25,cy-2.65,2.68)

# Barrel beside the front wall.
cyl('oak barrel', (cx-2.5, cy-2.20, 1.48), .38, .85, wood_light, vertices=10)
for z in [1.22,1.72]: cyl('barrel iron hoop', (cx-2.5, cy-2.20, z), .39, .055, metal, vertices=10)

# ------------------------------------------------------------
# Ground storytelling: path, rocks, stump, logs, axe, plants
# ------------------------------------------------------------
path_points = [(-5.2,-13,.03),(-4.4,-11.2,.04),(-3.7,-9.6,.05),(-2.8,-8.0,.06),(-1.8,-6.45,.07),(-.8,-5.15,.08),(.4,-4.0,.09), (cx,-3.55,.10)]
for j, (x,y,z) in enumerate(path_points):
    for k in range(4 if j < 4 else 3):
        xx=x+random.uniform(-.75,.75); yy=y+random.uniform(-.55,.55)
        stone((xx,yy,z+.05), (random.uniform(.32,.65), random.uniform(.22,.46), .09), path_light)

# Scattered rocks, clustered around foreground and cabin.
for i in range(28):
    x=random.uniform(-8,10); y=random.uniform(-11,6)
    if -4 < x < 6 and -4 < y < 0: continue
    stone((x,y,.18), (random.uniform(.22,.6),random.uniform(.2,.52),random.uniform(.18,.48)), rock_mat)

# Low bushes made from overlapping faceted blobs.
for i in range(38):
    x=random.uniform(-8.5,10); y=random.uniform(-8,6.5)
    if -2 < x < 6 and -2 < y < 4: continue
    base = (0.13,0.25,0.05) if i%3 else (0.22,0.34,0.06)
    bushmat = mat('leaf cluster %02d'%i, base, .95)
    for k in range(random.randint(2,4)):
        ico('angular shrub', (x+random.uniform(-.55,.55),y+random.uniform(-.4,.4),.35+random.uniform(0,.4)), (random.uniform(.35,.75),random.uniform(.3,.62),random.uniform(.28,.55)), bushmat, subdivisions=1)

# Grass blades as little triangular cones.
for i in range(48):
    x=random.uniform(-8,9); y=random.uniform(-11,5)
    if -3.5 < x < 5 and -3 < y < 3: continue
    cone('tuft of grass',(x,y,.28),.13,.01,random.uniform(.35,.65),grass_light if i%4==0 else grass_mat,vertices=4,rotation=(random.uniform(-.3,.3),random.uniform(-.3,.3),random.uniform(0,6.2)))

# Stump and stacked firewood on right foreground.
stump_x, stump_y = 7.0, -7.0
cyl('chopped stump', (stump_x, stump_y, .65), .72, 1.25, wood_light, vertices=9)
cyl('stump top', (stump_x, stump_y, 1.31), .68, .06, wood, vertices=9)
for i in range(6):
    x=8.0+random.uniform(-.2,.2); y=-7.2+i*.42; z=.45+i*.04
    log=cyl('cut firewood', (x,y,z), .25, 2.1, wood_light if i%2 else wood, vertices=9, rotation=(0,math.pi/2,random.uniform(-.08,.08)))
    cyl('log end', (x-1.06,y,z), .20, .035, path_light, vertices=9, rotation=(0,math.pi/2,0))

# Axe leaning against stump: handle and metal head.
axe_handle = beam_between('axe wooden handle', (stump_x-.1,stump_y-.15,1.18),(stump_x+1.0,stump_y-.15,2.65),.10,wood_light,bevel=.02)
cube('axe head', (stump_x+1.0, stump_y-.15, 2.65), (.50,.16,.34), metal, bevel=.04, rotation=(0,.25,-.52))

# A few iconic red mushrooms.
mushroom_cap = mat('mushroom red', (.72,.12,.035), .8)
for x,y,s in [(5.4,-6.2,.8),(8.8,-9.1,.65),(-6.2,-7.5,.55)]:
    cyl('mushroom stem',(x,y,.42),.10,.46,stone_light,vertices=7)
    ico('mushroom cap',(x,y,.70*s+.32),( .34*s,.34*s,.18*s),mushroom_cap,subdivisions=1)

# Foreground framing pines.
tree(-10,-8,0,2.25,-.08,True)
tree(11,-7,0,2.0,.06,False)
tree(-11,1,0,1.55,.04,False)
tree(12,3,0,1.65,-.05,True)

# ------------------------------------------------------------
# Lighting and camera
# ------------------------------------------------------------
sun_data = bpy.data.lights.new('late afternoon sun', 'SUN')
sun_data.energy = 2.0
sun_data.angle = math.radians(8)
sun_data.color = (1.0, .60, .29)
sun = bpy.data.objects.new('late afternoon sun', sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(28), math.radians(-25), math.radians(-38))

fill_data = bpy.data.lights.new('soft sky fill', 'AREA')
fill_data.energy = 1400
fill_data.shape = 'DISK'
fill_data.size = 9
fill_data.color = (.48,.56,.68)
fill = bpy.data.objects.new('soft sky fill', fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (-7,-7,11)
look_at(fill, (1,0,2))

rim_data = bpy.data.lights.new('warm rim', 'AREA')
rim_data.energy = 800
rim_data.size = 7
rim_data.color = (1.0,.24,.07)
rim = bpy.data.objects.new('warm rim', rim_data)
bpy.context.collection.objects.link(rim)
rim.location = (8,7,9)
look_at(rim, (2,1,3))

cam_data = bpy.data.cameras.new('hero camera')
cam = bpy.data.objects.new('hero camera', cam_data)
bpy.context.collection.objects.link(cam)
scene.camera = cam
cam.location = (13.3, -21.2, 9.5)
cam_data.lens = 52
cam_data.sensor_width = 36
cam_data.dof.use_dof = True
cam_data.dof.focus_object = bpy.data.objects.get('front door')
cam_data.dof.aperture_fstop = 5.6
look_at(cam, (1.2, -0.2, 3.1))

# Blender 5.0's compositor API is intentionally left untouched here; the
# warm windows and lantern use real emissive materials and point lights.

# Organize objects into a few visible collections for sane inspection.
scene.render.filepath = '/home/ralf/prj/exploration/blender-benchmark/gpt-5.6-luna-high/cabin_render.png'
bpy.ops.wm.save_as_mainfile(filepath='/home/ralf/prj/exploration/blender-benchmark/gpt-5.6-luna-high/cabin_scene.blend')
bpy.ops.render.render(write_still=True)
