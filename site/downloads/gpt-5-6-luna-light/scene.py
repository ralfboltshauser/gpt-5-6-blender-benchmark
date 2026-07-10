import bpy, math, random, os
from mathutils import Vector

random.seed(12)
bpy.ops.wm.read_factory_settings(use_empty=True)
OUT='/home/ralf/prj/exploration/blender-benchmark/gpt-5.6-luna-light'

def mat(n,c,rough=.8,emit=None):
    m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*c,1); bs.inputs['Roughness'].default_value=rough
    if emit: bs.inputs['Emission Color'].default_value=(*emit,1); bs.inputs['Emission Strength'].default_value=4
    return m
wood=mat('warm pine',(0.28,.105,.035)); wood2=mat('trim',(0.48,.20,.06)); darkwood=mat('dark beams',(.12,.045,.018)); roof=mat('charcoal shingles',(.035,.045,.06)); stone=mat('rough stone',(.22,.23,.24)); grass=mat('forest floor',(.16,.25,.075)); pathmat=mat('path',(.52,.33,.18)); green=mat('pine green',(.12,.23,.07)); green2=mat('pine highlight',(.22,.34,.10)); trunk=mat('trunks',(.20,.09,.035)); glass=mat('golden windows',(.95,.36,.035),emit=(1,.3,.02)); metal=mat('iron',(.08,.06,.04)); snow=mat('mountain',(.55,.48,.39))

def cube(n,loc,scale,ma,bev=0):
    bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.name=n; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bev: mod=o.modifiers.new('soft edges','BEVEL'); mod.width=bev; mod.segments=1
    o.data.materials.append(ma); return o
def cyl(n,loc,r,d,ma,verts=8,rot=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=d,location=loc,rotation=rot or (0,0,0)); o=bpy.context.object;o.name=n;o.data.materials.append(ma);return o
def cone(n,loc,r1,r2,d,ma,verts=7):
    bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=r1,radius2=r2,depth=d,location=loc);o=bpy.context.object;o.name=n;o.data.materials.append(ma);return o
def tree(x,y,s=1):
    cyl('tree trunk',(x,y,1.45*s),.22*s,2.9*s,trunk,7)
    for z,r in [(2.35,1.0),(3.15,.78),(3.85,.5)]: cone('faceted pine',(x,y,z*s),r*s,.08*s,1.55*s,green if z<3 else green2)
def window(x,y,z,w=0.55):
    cube('glowing window',(x,y,z),(w,.035,w*1.15),glass,.03)
    for dx in [-w*.48,w*.48]: cube('window frame',(x+dx,y-.05,z),(.045,.06,w*1.25),wood2)
    cube('window frame',(x,y-.05,z),(w*.55,.06,.045),wood2)
    cube('window frame',(x,y-.05,z),(w*.045,.06,w*1.1),wood2)

# ground and distant mountains
cube('ground',(0,0,-.18),(14,12,.18),grass)
for x in [-10,-7,-4,-1,2,5,8,11]: cone('distant mountain',(x,5,3.5+random.random()),3.4,0,7,snow,7)
# path stepping stones
for i in range(13):
    y=-7+i*.7; x=-2.6+i*.16; cube('path stone',(x,y,.05),(random.uniform(.35,.7),.27,.06),pathmat,.08).rotation_euler[2]=random.uniform(-.4,.4)
# cabin body
cube('cabin body',(2,0,2.15),(2.8,2.0,2.15),wood,.08)
cube('stone foundation',(2,0,.28),(2.95,2.12,.32),stone,.05)
# horizontal logs
for z in [.65,1.25,1.85,2.45,3.05,3.65]: cube('log course',(2,-2.04,z),(2.9,.14,.17),wood2,.05)
# roof two slopes as beams + dark roof planes
for side in [-1,1]:
    y=side*1.45; o=cube('roof slope',(2,y,4.35),(3.3,1.15,.16),roof,.03); o.rotation_euler[0]=side*math.radians(43)
    # shingles as rows
    for j in range(4):
        yy=side*(.55+j*.43); z=3.72+j*.43; sh=cube('roof shingle',(2,yy,z),(3.0,.28,.06),roof,.015); sh.rotation_euler[0]=side*math.radians(43)
# front gable triangular suggestion with beams
cube('gable beam',(2,-2.1,4.0),(2.1,.16,.13),wood2); a=cube('gable beam',(2,-2.1,4.7),(1.55,.16,.13),wood2); a.rotation_euler[1]=math.radians(35)
# door and windows
cube('door',(2,-2.22,1.65),(.62,.08,1.2),wood2,.04); cube('door knob',(2.52,-2.35,1.65),(.06,.04,.06),metal)
window(2,-2.26,4.1,.42); window(.15,-2.25,2.15,.48); window(3.85,-2.25,2.15,.48)
# porch
cube('porch',(2,-2.65,.75),(2.35,.85,.12),wood2,.04)
for x in [-.2,4.2]:
    cube('porch post',(x,-3.3,1.45),(.12,.12,.85),wood2); cube('porch rail',(x+1 if x<0 else x-1,-3.3,1.4),(1,.1,.1),wood2)
for x in [1.1,1.6,2.1,2.6,3.1]: cube('porch step',(x,-3.25,.3),(1.5,.35,.12),wood2)
# chimney
for z in [3.7,4.0,4.3,4.6]:
    for x in [4.0,4.45]: cube('chimney brick',(x,-.2,z),(.22,.38,.18),stone,.03)
cube('chimney cap',(4.22,-.2,4.85),(.55,.55,.1),metal)
# foreground trees
for x,y,s in [(-7,-3,1.8),(-5,2,1.25),(-8,5,1.4),(7,3,1.8),(9,-1,1.5),(11,5,1.2),(-11,1,1.6)]: tree(x,y,s)
# bushes and rocks
for i in range(28):
    x=random.uniform(-10,10); y=random.uniform(-6,5)
    if 0<x<5 and -3<y<2: continue
    if i%2: ico=None; bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=random.uniform(.25,.55),location=(x,y,.25)); o=bpy.context.object;o.name='low poly rock';o.scale.z=.65;o.data.materials.append(stone)
    else: cone('bush',(x,y,.35),random.uniform(.35,.7),.05,.7,green,6)
# logs and stump
cyl('stump',(7,-4,.55),.65,1.1,wood2,9); cyl('stump top',(7,-4,1.12),.57,.05,wood,9)
for i in range(5):
    o=cyl('cut log',(7.7+i*.18,-4.0+i*.2,.5+i*.08),.25,2.2,wood2,8,rot=(0,math.radians(90),math.radians(12))); cyl('log end',(8.8+i*.18,-4.0+i*.2,.5+i*.08),.20,.02,wood,8,rot=(0,math.radians(90),math.radians(12)))
# fence
for x in [-9,-7,-5]: cube('fence post',(x,-4.2,.8),(.12,.12,.9),wood2); cube('fence rail',(-7,-4.2,1.05),(2.1,.1,.1),wood2); cube('fence rail',(-7,-4.2,.55),(2.1,.1,.1),wood2)
# lanterns
for x,y in [(-5,-4),(0,-2.7)]:
    cyl('lantern post',(x,y,1),.06,1.4,darkwood,6); cube('lantern',(x,y,1.65),(.22,.18,.3),glass,.03)
    bpy.ops.object.light_add(type='POINT',location=(x,y,1.65)); bpy.context.object.data.energy=55; bpy.context.object.data.color=(1,.35,.08)
# lighting/world
world=bpy.context.scene.world or bpy.data.worlds.new('World'); bpy.context.scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(.09,.07,.05,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.42
bpy.ops.object.light_add(type='AREA', location=(-7,-6,10)); sun=bpy.context.object; sun.data.energy=1300; sun.data.shape='DISK'; sun.data.size=8; sun.rotation_euler=(math.radians(28),0,math.radians(-35))
bpy.ops.object.light_add(type='AREA', location=(7,-10,6)); fill=bpy.context.object; fill.data.energy=650; fill.data.size=7; fill.data.color=(1,.42,.16); fill.rotation_euler=(math.radians(55),0,math.radians(135))
# camera
bpy.ops.object.camera_add(location=(12,-18,9),rotation=(math.radians(67),0,math.radians(34))); cam=bpy.context.object; bpy.context.scene.camera=cam
def track(o,pt): o.rotation_euler=(Vector(pt)-o.location).to_track_quat('-Z','Y').to_euler()
track(cam,(1,0,2.4)); cam.data.lens=48
sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=960; sc.render.resolution_y=640; sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'; sc.render.filepath=OUT+'/luna_light.png'; sc.render.film_transparent=False
sc.view_settings.look='AgX - Medium High Contrast'; sc.render.image_settings.color_mode='RGBA'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/luna_light.blend'); bpy.ops.render.render(write_still=True)
