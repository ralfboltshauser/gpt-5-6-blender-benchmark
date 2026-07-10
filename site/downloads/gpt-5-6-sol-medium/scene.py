import bpy
import math
import random
from mathutils import Vector

random.seed(56)

# ---------- scene helpers ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 720
scene.render.resolution_y = 450
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.render.image_settings.color_mode = 'RGBA'
scene.render.filepath = '/home/ralf/prj/exploration/blender-benchmark/gpt-5.6-sol-medium/render.png'
scene.render.resolution_percentage = 100
scene.render.image_settings.color_depth = '8'
scene.world = bpy.data.worlds.new('Forest World')
scene.world.color = (0.035, 0.045, 0.035)
scene.view_settings.look = 'AgX - Medium High Contrast'

def mat(name, color, rough=0.7, metallic=0.0, emission=None, strength=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metallic
    if emission:
        bs.inputs['Emission Color'].default_value = (*emission, 1)
        bs.inputs['Emission Strength'].default_value = strength
    return m

WOOD = mat('warm hewn pine', (0.28, 0.095, 0.025))
WOOD2 = mat('cut timber', (0.46, 0.19, 0.045))
DARKWOOD = mat('dark endgrain', (0.12, 0.035, 0.012))
ROOF = mat('charcoal shingles', (0.075, 0.065, 0.064))
ROOF2 = mat('warm shingles', (0.12, 0.08, 0.065))
STONE = mat('foundation stone', (0.24, 0.25, 0.25))
STONE2 = mat('warm rock', (0.34, 0.31, 0.29))
GREEN = mat('forest green', (0.10, 0.24, 0.10))
GREEN2 = mat('pine highlight', (0.19, 0.33, 0.12))
GRASS = mat('mossy ground', (0.22, 0.34, 0.12))
PATH = mat('sunlit path', (0.49, 0.32, 0.16))
GLASS = mat('golden glow', (0.95, 0.35, 0.035), emission=(1.0, 0.28, 0.015), strength=8)
METAL = mat('black iron', (0.025, 0.022, 0.018), rough=0.32, metallic=0.75)
MOUNTAIN = mat('misty mountains', (0.40, 0.39, 0.32))
RED = mat('mushroom caps', (0.65, 0.08, 0.025))
CREAM = mat('mushroom stems', (0.65, 0.48, 0.29))

def assign(obj, material):
    obj.data.materials.append(material)
    return obj

def cube(name, loc, scale, material, bevel=0.05, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(o,material)
    if bevel:
        mod=o.modifiers.new('soft hewn edges','BEVEL'); mod.width=bevel; mod.segments=2
    return o

def cyl(name, loc, radius, depth, material, vertices=8, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    o=bpy.context.object; o.name=name; assign(o,material); return o

def cone(name, loc, r1, r2, depth, material, vertices=8):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=r1, radius2=r2, depth=depth, location=loc)
    o=bpy.context.object; o.name=name; assign(o,material); return o

def ico(name, loc, scale, material, sub=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=1, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); assign(o,material); return o

def look_at(obj, target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

# ---------- ground and path ----------
cyl('raised forest clearing',(0,0,-0.35),15.5,0.7,GRASS,vertices=64)
for i in range(52):
    a=random.uniform(-6.5,6.5); y=random.uniform(-15,-2.8)
    center=0.20*y+1.1
    width=1.3 + 0.06*(-y)
    x=center+random.uniform(-width,width)
    s=random.uniform(.32,.75)
    ico('path stone',(x,y,0.03),(s,random.uniform(.32,.7),random.uniform(.06,.13)), PATH,1)
for i in range(28):
    x=random.uniform(-13,13); y=random.uniform(-13,10)
    if abs(x-(0.20*y+1.1)) < 2.2 and y < -2: continue
    ico('ground facet',(x,y,0.02),(random.uniform(.5,1.4),random.uniform(.5,1.5),.035),random.choice([GRASS,GREEN2]),1)

# ---------- cabin foundation ----------
for y in [-3.2,3.2]:
    for x in [-3.6,-2.4,-1.2,0,1.2,2.4,3.6]: cube('foundation block',(x,y,0.38),(.57,.42,.36),STONE,.07)
for x in [-4.1,4.1]:
    for y in [-2.4,-1.2,0,1.2,2.4]: cube('foundation block',(x,y,0.38),(.42,.57,.36),STONE,.07)

# Main wall masses
cube('cabin body',(0,0,2.65),(3.85,2.9,2.25),WOOD,0.10)

# Horizontal log courses, emphasized on front and right side
for z in [0.85,1.42,1.99,2.56,3.13,3.70,4.27]:
    for x in [-2.75,0,2.75]:
        cube('front log',(x,-3.05,z),(1.45,.18,.24),WOOD2,.09)
    for y in [-2,-.7,.7,2.0]:
        cube('side log',(4.00,y,z),(.18,.78,.24),WOOD2,.09)

# Corner log ends
for x in [-4.15,4.15]:
    for z in [1.1,1.7,2.3,2.9,3.5,4.1]:
        cube('corner log end',(x,-3.22,z),(.34,.36,.18),WOOD2,.06,rot=(0,0,(z%1)*.08))

# Porch platform, supports and railing
cube('porch deck',(0,-4.45,.85),(4.55,1.35,.20),WOOD2,.06)
for x in [-3.8,-2.0,2.0,3.8]:
    cube('porch post',(x,-5.35,1.65),(.15,.15,.82),WOOD2,.04)
for x in [-3.8,3.8]:
    cube('porch top rail',(x,-4.7,2.08),(.13,.95,.13),WOOD2,.04)
    cube('porch mid rail',(x,-4.7,1.45),(.11,.95,.11),WOOD2,.04)
for y in [-5.45,-4.82,-4.2]:
    cube('porch rail post',(-3.8,y,1.64),(.12,.12,.65),WOOD2,.03)
    cube('porch rail post',(3.8,y,1.64),(.12,.12,.65),WOOD2,.03)
# stairs
for i in range(3):
    cube('front step',(0,-5.95-i*.42,.65-i*.23),(1.45,.36,.13),WOOD2,.04)

# Door and trim
cube('front door',(0,-3.25,2.22),(0.88,.13,1.48),DARKWOOD,.05)
for x in [-.95,.95]: cube('door trim',(x,-3.42,2.25),(.13,.13,1.62),WOOD2,.04)
cube('door header',(0,-3.42,3.86),(1.08,.13,.14),WOOD2,.04)
for x in [-.55,0,.55]: cube('door plank',(x,-3.40,2.25),(.04,.04,1.35),WOOD2,.01)
cyl('door handle',(.60,-3.56,2.28),.07,.18,METAL,12,rot=(math.pi/2,0,0))

def window(name, loc, w=1.0,h=1.15, front=True):
    x,y,z=loc
    sc=(w,.12,h) if front else (.12,w,h)
    cube(name+' glow',loc,sc,GLASS,.025)
    if front:
        cube(name+' top',(x,y-.13,z+h+.16),(w+.2,.14,.12),WOOD2,.03)
        cube(name+' bottom',(x,y-.13,z-h-.16),(w+.2,.14,.12),WOOD2,.03)
        for dx in [-w-.16,w+.16]: cube(name+' side',(x+dx,y-.13,z),(.12,.14,h+.18),WOOD2,.03)
        cube(name+' mullion v',(x,y-.16,z),(.055,.08,h),DARKWOOD,.01)
        cube(name+' mullion h',(x,y-.16,z),(w,.08,.055),DARKWOOD,.01)
    else:
        cube(name+' top',(x+.13,y,z+h+.16),(.14,w+.2,.12),WOOD2,.03)
        cube(name+' bottom',(x+.13,y,z-h-.16),(.14,w+.2,.12),WOOD2,.03)
        for dy in [-w-.16,w+.16]: cube(name+' side',(x+.13,y+dy,z),(.14,.12,h+.18),WOOD2,.03)
        cube(name+' mullion v',(x+.16,y,z),(.08,.055,h),DARKWOOD,.01)
        cube(name+' mullion h',(x+.16,y,z),(.08,w,.055),DARKWOOD,.01)

window('front left window',(-2.45,-3.22,2.45),.62,.85,True)
window('right window',(4.02,-.85,2.55),.7,.92,False)
window('right rear window',(4.02,1.45,2.55),.62,.82,False)

# Gable triangle face and loft window
verts=[(-3.75,-3.00,4.55),(3.75,-3.00,4.55),(0,-3.00,8.0)]
mesh=bpy.data.meshes.new('gable_mesh'); mesh.from_pydata(verts,[],[(0,1,2)]); mesh.materials.append(DARKWOOD)
gable=bpy.data.objects.new('front timber gable',mesh); bpy.context.collection.objects.link(gable)
window('loft window',(0,-3.14,5.72),.57,.72,True)
for x,ang in [(-1.93,-.82),(1.93,.82)]:
    cube('gable beam',(x,-3.28,6.25),(.13,.13,2.55),WOOD2,.04,rot=(0,ang,0))
cube('gable cross beam',(0,-3.30,4.73),(3.85,.15,.16),WOOD2,.05)

# Roof planes
angle=math.radians(43)
cube('left roof',(-2.1,0,6.18),(3.02,3.62,.19),ROOF,.05,rot=(0,-angle,0))
cube('right roof',(2.1,0,6.18),(3.02,3.62,.19),ROOF,.05,rot=(0,angle,0))
# Roof shingle rows / alternating panels
for side in [-1,1]:
    for row in range(5):
        z=4.65+row*.69
        x=side*(3.55-row*.57)
        for y in [-2.75,-1.45,-.15,1.15,2.45]:
            cube('individual shingle',(x,y,z),(.54,.64,.07),random.choice([ROOF,ROOF2]),.025,rot=(0,side*angle,0))
# Ridge beam
cyl('roof ridge',(0,0,8.15),.18,7.5,WOOD2,6,rot=(math.pi/2,0,0))

# chimney stone stack
for z in [6.35,6.82,7.29,7.76,8.23]:
    for x in [1.45,1.92]:
        for y in [.6,1.05]:
            cube('chimney stone',(x+random.uniform(-.03,.03),y,z),(.22,.21,.22),STONE,.035)
cube('chimney cap',(1.68,.83,8.56),(.62,.58,.13),DARKWOOD,.03)

# ---------- props ----------
def lantern(loc):
    x,y,z=loc
    cube('lantern glow',(x,y,z),(.18,.13,.28),GLASS,.03)
    for dx in [-.23,.23]: cube('lantern frame',(x+dx,y,z),(.025,.03,.34),METAL,.01)
    cube('lantern top',(x,y,z+.36),(.30,.20,.05),METAL,.01)
    cube('lantern base',(x,y,z-.36),(.30,.20,.05),METAL,.01)
    cyl('lantern roof',(x,y,z+.45),.36,.16,METAL,4)
    light_data=bpy.data.lights.new('lantern point','POINT'); light_data.energy=60; light_data.color=(1,.18,.025); light_data.shadow_soft_size=1.0
    light=bpy.data.objects.new('lantern light',light_data); bpy.context.collection.objects.link(light); light.location=(x,y,z)
lantern((-1.55,-3.52,3.26))
lantern((-5.8,-8.8,1.15))

# fence on left
for x,y in [(-7.7,-8),(-6.2,-7.7),(-8.1,-5.9)]: cube('fence post',(x,y,.85),(.18,.18,.9),WOOD2,.04)
cube('fence rail',(-7.0,-7.85,1.05),(1.0,.11,.11),WOOD2,.04,rot=(0,0,.15))
cube('fence rail',(-7.1,-6.8,.85),(1.15,.11,.11),WOOD2,.04,rot=(0,0,-.8))

# woodpile and stump, front-right
cyl('stump',(5.4,-6.8,.65),1.05,1.25,WOOD2,10)
cyl('stump top',(5.4,-6.8,1.29),.87,.04,CREAM,10)
for row in range(3):
    for j in range(4-row):
        y=-6.45+j*.48+row*.23
        z=.45+row*.55
        cyl('firewood',(7.15,y,z),.25,2.2,WOOD2,8,rot=(0,math.pi/2,0))
        cyl('cut end',(6.03,y,z),.21,.04,CREAM,8,rot=(0,math.pi/2,0))
# axe in stump
cube('axe handle',(4.75,-6.8,2.05),(.09,.09,1.45),WOOD2,.04,rot=(0,-.63,0))
cube('axe head',(5.65,-6.8,2.85),(.48,.14,.27),METAL,.04,rot=(0,-.15,0))

# barrel
cyl('barrel',(-2.65,-4.2,1.45),.48,.95,WOOD2,12)
for z in [1.05,1.42,1.82]: cyl('barrel hoop',(-2.65,-4.2,z),.51,.06,METAL,12)

# ---------- trees, shrubs, rocks ----------
def pine(x,y,s=1.0, foreground=False):
    z=0
    cyl('pine trunk',(x,y,1.65*s),.38*s,3.3*s,DARKWOOD,7)
    for k,(rz,rad,h) in enumerate([(2.2,2.25,2.7),(3.7,1.8,2.5),(5.1,1.35,2.4)]):
        cone('pine tier',(x,y,rz*s),rad*s,.05,h*s, GREEN2 if k==2 and foreground else GREEN, vertices=7)

tree_specs=[(-11,-4,1.15),(-10,5,1.35),(-7,7,1.12),(-5,9,1.3),(-2,10,1.0),(2,10,1.2),(6,8,1.25),(9,6,1.35),(11,2,1.55),(12,-4,1.2),(-12,-10,1.45),(-13,1,1.25),(-8,2,1.0),(7,3.5,.85),(-5,3.5,.9)]
for x,y,s in tree_specs: pine(x,y,s, abs(x)>10)

for i in range(34):
    a=random.uniform(0,math.tau); r=random.uniform(5,13)
    x,y=math.cos(a)*r,math.sin(a)*r
    if -5<x<6 and -7<y<4: continue
    ico('bush',(x,y,.65),(random.uniform(.45,1.0),random.uniform(.5,1.1),random.uniform(.45,.8)),random.choice([GREEN,GREEN2]),1)
for i in range(24):
    a=random.uniform(0,math.tau); r=random.uniform(4.5,13)
    x,y=math.cos(a)*r,math.sin(a)*r
    if -4<x<5 and -6<y<3: continue
    ico('low poly rock',(x,y,.45),(random.uniform(.35,.85),random.uniform(.35,.8),random.uniform(.35,.75)),random.choice([STONE,STONE2]),1)

# grass tufts
for i in range(55):
    x=random.uniform(-12,12); y=random.uniform(-12,8)
    if -4.5<x<4.5 and -5.5<y<3.5: continue
    for a in [-.35,0,.35]:
        cone('grass blade',(x+a*.25,y,.35),.13,.0,.7,GREEN2,vertices=3)

# mushrooms near foreground
for x,y,s in [(6.3,-9.2,.7),(8.2,-7.7,.45),(-2.7,-7.4,.42),(-3.0,-7.2,.28)]:
    cyl('mushroom stem',(x,y,.28*s),.12*s,.55*s,CREAM,8)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, location=(x,y,.60*s)); cap=bpy.context.object; cap.name='red mushroom'; cap.scale=(.38*s,.38*s,.18*s); assign(cap,RED)

# background mountain silhouettes
for i,x in enumerate(range(-15,16,4)):
    y=13+random.uniform(-1,2); h=random.uniform(7,12)
    cone('distant mountain',(x,y,h*.42),random.uniform(4,6),0.3,h,MOUNTAIN,vertices=6)

# ---------- lighting and camera ----------
sun_data=bpy.data.lights.new('warm sunset','SUN'); sun_data.energy=2.8; sun_data.color=(1.0,.52,.26); sun_data.angle=math.radians(12)
sun=bpy.data.objects.new('warm sunset',sun_data); bpy.context.collection.objects.link(sun); sun.rotation_euler=(math.radians(33),0,math.radians(-42))
area_data=bpy.data.lights.new('sky fill','AREA'); area_data.energy=1500; area_data.color=(.34,.48,.72); area_data.shape='DISK'; area_data.size=18
area=bpy.data.objects.new('sky fill',area_data); bpy.context.collection.objects.link(area); area.location=(-5,-6,15); look_at(area,(0,0,2))

cam_data=bpy.data.cameras.new('Camera'); cam=bpy.data.objects.new('Camera',cam_data); bpy.context.collection.objects.link(cam)
cam.location=(19,-29,15.0); look_at(cam,(0,-1.0,2.65)); cam.data.lens=54
cam.data.dof.use_dof=True; cam.data.dof.focus_object=bpy.data.objects['front door']; cam.data.dof.aperture_fstop=5.0
scene.camera=cam

# warm world via nodes
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.16,0.11,0.07,1); bg.inputs['Strength'].default_value=.55

bpy.ops.wm.save_as_mainfile(filepath='/home/ralf/prj/exploration/blender-benchmark/gpt-5.6-sol-medium/cabin_scene.blend')
bpy.ops.render.render(write_still=True)
