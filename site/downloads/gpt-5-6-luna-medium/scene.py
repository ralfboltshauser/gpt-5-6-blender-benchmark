import bpy, math, random, os
from mathutils import Vector

random.seed(12)
ROOT = os.path.dirname(os.path.abspath(__file__))

def mat(name, color, rough=0.8, metallic=0.0, emission=None, strength=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1)
    m.use_nodes=True; bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metallic
    if emission:
        bs.inputs['Emission Color'].default_value=(*emission,1); bs.inputs['Emission Strength'].default_value=strength
    return m

def cube(name, loc, scale, material, bevel=0.0, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o=bpy.context.object; o.name=name; o.scale=(scale[0]/2,scale[1]/2,scale[2]/2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material:o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('soft edges','BEVEL'); mod.width=bevel; mod.segments=2
    return o

def cyl(name, loc, radius, depth, material, verts=8, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc, rotation=rot)
    o=bpy.context.object; o.name=name
    if material:o.data.materials.append(material)
    return o

def cone(name, loc, r1, r2, depth, material, verts=8):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth, location=loc)
    o=bpy.context.object; o.name=name
    if material:o.data.materials.append(material)
    return o

def look_at(o, target):
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()

# materials
ground=mat('mossy ground',(0.16,0.26,0.10)); grass=mat('grass',(0.28,0.40,0.12))
pathlight=mat('path stones',(0.68,0.48,0.30)); wood=mat('cabin timber',(0.34,0.14,0.045))
wood2=mat('sunlit wood',(0.53,0.25,0.08)); darkwood=mat('dark beams',(0.18,0.07,0.025))
roofmat=mat('charcoal shingles',(0.055,0.06,0.065)); stone=mat('foundation stone',(0.25,0.27,0.25))
chimney=mat('chimney bricks',(0.38,0.36,0.31)); glass=mat('golden window glow',(0.18,0.06,0.008),emission=(1.0,0.28,0.015),strength=8)
metal=mat('iron',(0.035,0.04,0.035),rough=.35,metallic=.5); leaf=mat('pine green',(0.12,0.25,0.07))
leaf2=mat('pine light',(0.23,0.37,0.10)); trunk=mat('tree trunks',(0.20,0.09,0.035))
rockmat=mat('faceted rocks',(0.28,0.30,0.30)); red=mat('berries',(0.55,0.06,0.02)); orange=mat('mushroom caps',(0.80,0.18,0.035)); cream=mat('mushroom stems',(0.65,0.51,0.30))

# ground and path
bpy.ops.mesh.primitive_plane_add(size=70, location=(0,3,-0.2)); bpy.context.object.data.materials.append(ground)
for i in range(18):
    t=i/17; x=-5.0+4.3*t+0.5*math.sin(t*7); y=-8+7.2*t; s=1.0-0.35*t
    o=cyl('path stone',(x,y,0.02),0.48*s,0.10,pathlight,verts=6); o.rotation_euler[2]=random.random()*math.pi; o.scale.y=random.uniform(.65,1.25)

# cabin body, foundation, logs
for x in [-2.4,-1.2,0,1.2,2.4]:
    for y in [-.9,1.0]: cube('foundation block',(x,y,.35),(1.18,1.05,.65),stone,.06)
cube('cabin body',(0,0.1,3.35),(5.5,4.0,5.8),wood,.12)
for z in [1.1,2.0,2.9,3.8,4.7,5.6]: cube('log course',(0,-1.96,z),(5.65,.18,.22),wood2,.04)
for x in [-2.55,2.55]: cube('corner timber',(x,-2.03,3.5),(.28,.28,5.7),darkwood,.04)
for x in [-2.25,2.25]: cube('gable brace',(x,-2.05,6.15),(.20,.22,2.5),wood2,.03,rot=(0,math.radians(-38 if x<0 else 38),0))
cube('gable cross beam',(0,-2.08,5.45),(4.55,.22,.24),wood2,.04)

# roof and shingles
ang=math.radians(35); slab_len=4.2/math.cos(ang)
cube('left roof',(-2.0,0.15,7.0),(slab_len,4.55,.32),roofmat,.05,rot=(0,-ang,0))
cube('right roof',(2.0,0.15,7.0),(slab_len,4.55,.32),roofmat,.05,rot=(0,ang,0))
for side in [-1,1]:
    for row in range(4):
        z=5.55+row*.55; x=side*(1.0+row*.72)
        for j in range(5): cube('roof shingle',(x,-1.98+j*.92,z),(1.05,.82,.10),roofmat,.025,rot=(0,side*ang,0))

# door and windows
cube('front door',(0,-2.18,2.35),(1.28,.16,2.55),darkwood,.04); cube('door inset',(0,-2.29,2.35),(1.02,.05,2.18),wood2,.02)
for x in [-.47,.47]: cube('door trim',(x,-2.34,2.35),(.16,.13,2.75),wood2,.025)
cube('door lintel',(0,-2.34,3.72),(1.55,.14,.18),wood2,.025); cyl('door handle',(.40,-2.42,2.35),.07,.06,metal,verts=8,rot=(math.pi/2,0,0))
def window(x,y,z,w=1.05,h=1.35):
    cube('lit window',(x,y,z),(w,.10,h),glass,.02)
    for dx in [-w/2-.08,w/2+.08]: cube('window side',(x+dx,y-.03,z),(.14,.16,h+.22),wood2,.02)
    for dz in [-h/2-.08,h/2+.08]: cube('window top',(x,y-.03,z+dz),(w+.30,.16,.14),wood2,.02)
    cube('window mullion',(x,y-.10,z),(0.10,.08,h),wood2,.01); cube('window mullion',(x,y-.10,z),(w,.08,.10),wood2,.01)
window(-1.72,-2.25,2.75); window(1.72,-2.25,2.75); window(1.85,.0,3.1,1.0,1.35); window(0,-2.25,6.0,.85,1.05)

# porch
cube('porch deck',(0,-3.0,1.05),(4.4,1.75,.22),wood2,.04)
for i in range(3): cube('porch step',(0,-3.85+i*.28,.45+i*.22),(1.8,.38,.22),wood2,.03)
for x in [-1.9,1.9]:
    cube('railing post',(x,-3.45,1.8),(.18,.18,1.55),darkwood,.03); cube('railing post',(x,-2.55,1.8),(.18,.18,1.55),darkwood,.03)
    cube('railing top',(0,-3.45,2.35),(3.95,.16,.18),wood2,.03); cube('railing side',(x,-2.55,2.35),(.18,1.0,.18),wood2,.03)

# chimney
for z in [6.1,6.45,6.8,7.15]:
    for x in [-.45,-.15,.15,.45]: cube('chimney brick',(x,.75,z),(.28,.75,.30),chimney,.025)
cube('chimney cap',(0,.75,7.38),(1.25,.95,.16),darkwood,.04)

def lantern(loc):
    x,y,z=loc; cube('lantern frame',(x,y,z),(.42,.34,.68),metal,.03); cube('lantern light',(x,y,z),(.22,.10,.36),glass,.01); cube('lantern roof',(x,y,z+.40),(.52,.42,.12),metal,.03)
lantern((-3.15,-2.25,2.2)); lantern((-5.0,-5.7,1.5))
cyl('barrel',(-2.0,-2.35,1.35),.42,.9,wood2,verts=12)
for z in [1.05,1.55]: cyl('barrel band',(-2.0,-2.35,z),.45,.08,metal,verts=12)
cyl('stump',(5.0,-2.2,.7),.72,1.35,wood2,verts=9); cyl('stump top',(5.0,-2.2,1.4),.70,.08,wood,verts=9)
for i in range(6):
    x=5.6+random.uniform(-.15,.2); y=-1.8+i*.38; z=.48+0.28*(i%2)
    cyl('cut log',(x,y,z),.28,2.2,wood2,verts=10,rot=(0,math.pi/2,random.uniform(-.12,.12)))

# pines and environment
def pine(x,y,s=1.0):
    cyl('pine trunk',(x,y,1.15*s),.22*s,2.3*s,trunk,verts=7)
    for i,(zz,rr) in enumerate([(2.1,.95),(2.95,.76),(3.65,.56)]): cone('pine crown',(x,y,zz*s),rr*s,.05,1.55*s,leaf if i%2 else leaf2,verts=7)
for args in [(-8,1,1.35),(-6,6,1.6),(-4,8,1.2),(5,7,1.55),(9,3,1.9),(8,-1,1.2),(-9,-5,1.5),(10,-6,1.7),(-5,-10,1.1),(7,-10,1.35),(12,8,1.2)]: pine(*args)
for i in range(26):
    x=random.uniform(-10,10); y=random.uniform(-9,9)
    if -3.5<x<4 and -3<y<3: continue
    s=random.uniform(.25,.65); cone('shrub',(x,y,s*.65),.65*s,.05,1.2*s,leaf,verts=6)
for i in range(25):
    x=random.uniform(-9,9); y=random.uniform(-7,7)
    if -3<x<3 and -2<y<3: continue
    s=random.uniform(.25,.65)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=s,location=(x,y,s*.65)); o=bpy.context.object; o.name='faceted rock'; o.scale=(1.2,.85,.8); o.data.materials.append(rockmat)
for i in range(18):
    x=random.uniform(-7,7); y=random.uniform(-7,2)
    for k in range(3): cube('grass blade',(x+random.uniform(-.12,.12),y,.25+.25),(.06,.06,.55),grass,.01,rot=(0,random.uniform(-.35,.35),random.uniform(-.25,.25)))
for x,y in [(-4.8,-1.5),(4.5,-4.8),(6.0,-5.2)]:
    cyl('mushroom stem',(x,y,.38),.12,.45,cream,verts=8); cone('mushroom cap',(x,y,.68),.32,.04,.25,orange,verts=8)

# lighting, camera, render
bpy.ops.object.light_add(type='AREA',location=(-8,-10,14)); key=bpy.context.object; key.data.energy=1300; key.data.shape='DISK'; key.data.size=8; key.data.color=(1.0,.55,.25); look_at(key,(0,0,2))
bpy.ops.object.light_add(type='AREA',location=(5,2,10)); fill=bpy.context.object; fill.data.energy=600; fill.data.size=6; fill.data.color=(.35,.5,1.0); look_at(fill,(0,0,3))
bpy.ops.object.light_add(type='POINT',location=(0,-2.8,3.0)); bpy.context.object.data.energy=180; bpy.context.object.data.color=(1.0,.18,.03)
bpy.ops.object.camera_add(location=(16,-22,12)); cam=bpy.context.object; look_at(cam,(0,-.4,3.3)); cam.data.lens=48; cam.data.dof.use_dof=True; cam.data.dof.focus_object=bpy.data.objects.get('front door'); cam.data.dof.aperture_fstop=5.0; bpy.context.scene.camera=cam
scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE'; scene.render.resolution_x=960; scene.render.resolution_y=720; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(ROOT,'cabin_preview.png')
scene.world.use_nodes=True; bg=scene.world.node_tree.nodes['Background']; bg.inputs['Color'].default_value=(0.09,0.12,0.18,1); bg.inputs['Strength'].default_value=.35
scene.view_settings.look='AgX - Medium High Contrast'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'forest_cabin.blend')); bpy.ops.render.render(write_still=True)
