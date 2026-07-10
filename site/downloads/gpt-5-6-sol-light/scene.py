import bpy, math, random, os
from mathutils import Vector

random.seed(56)
ROOT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color, rough=.75, emission=None, strength=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough
    if emission:
        bs.inputs['Emission Color'].default_value=(*emission,1); bs.inputs['Emission Strength'].default_value=strength
    return m
wood=mat('warm cedar',(0.27,.105,.035)); wood2=mat('cut wood',(.48,.22,.075)); darkwood=mat('dark trim',(.12,.045,.018)); roofmat=mat('charcoal shingles',(.075,.06,.058)); stone=mat('cool fieldstone',(.25,.25,.27)); mortar=mat('chimney stone',(.38,.34,.31)); green=mat('pine green',(.075,.19,.085)); green2=mat('sunlit pine',(.17,.29,.10)); grass=mat('forest floor',(.22,.31,.10)); dirt=mat('path earth',(.48,.31,.16)); glow=mat('window glow',(1,.38,.035),emission=(1,.20,.015),strength=8); black=mat('iron',(.025,.018,.012),.35); red=mat('mushroom red',(.65,.055,.018)); white=mat('mushroom stem',(.72,.61,.43)); leaf=mat('bushes',(.10,.28,.075)); mountain=mat('distant mountain',(.32,.30,.27)); water=mat('water',(.18,.42,.48),.25)

def cube(n,loc,scale,ma,rot=(0,0,0),bev=0):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot); o=bpy.context.object; o.name=n; o.scale=(scale[0]/2,scale[1]/2,scale[2]/2); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if ma:o.data.materials.append(ma)
    if bev:
        mod=o.modifiers.new('soft hewn edges','BEVEL'); mod.width=bev; mod.segments=1
    return o
def cyl(n,loc,r,depth,ma,verts=8,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc,rotation=rot); o=bpy.context.object;o.name=n
    if ma:o.data.materials.append(ma)
    return o
def cone(n,loc,r1,r2,depth,ma,verts=8):
    bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=r1,radius2=r2,depth=depth,location=loc);o=bpy.context.object;o.name=n;o.data.materials.append(ma);return o
def ico(n,loc,scale,ma,sub=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=loc);o=bpy.context.object;o.name=n;o.scale=scale;o.data.materials.append(ma);return o

# terrain and winding path
cube('ground',(0,0,-.3),(38,32,.6),grass,bev=.3)
for i in range(42):
    y=-15+i*.42; x=-4.5+1.4*math.sin(i*.16)
    ico('path stone',(x+random.uniform(-.7,.7),y,0.02),(random.uniform(.55,1.0),random.uniform(.35,.75),.10),dirt,1)
for i in range(45):
    x=random.uniform(-17,17); y=random.uniform(-14,13)
    if -7<x<7 and -7<y<5: continue
    ico('ground facet',(x,y,.01),(random.uniform(.7,1.8),random.uniform(.7,1.8),.05),random.choice([grass,green2]),1)

# foundation
for x in [-3.2,-1.6,0,1.6,3.2]: cube('foundation block',(x,0,.35),(1.45,6.5,.7),stone,bev=.07)
for y in [-2.75,-1.35,.05,1.45,2.75]:
    cube('foundation side',(-3.55,y,.35),(.7,1.25,.7),stone,bev=.07); cube('foundation side',(3.55,y,.35),(.7,1.25,.7),stone,bev=.07)

# log walls, alternating tones
for z in [1.0+i*.43 for i in range(9)]:
    m=random.choice([wood,wood,wood2]); cube('front hewn log',(0,-3,z),(7.2,.38,.40),m,bev=.055); cube('back hewn log',(0,3,z),(7.2,.38,.40),m,bev=.055)
    cube('side hewn log',(-3.5,0,z),(.38,6.2,.40),m,bev=.055); cube('side hewn log',(3.5,0,z),(.38,6.2,.40),m,bev=.055)
# corner log ends
for x in [-3.72,3.72]:
 for y in [-3.22,3.22]:
  for z in [1+i*.86 for i in range(5)]: cube('protruding log end',(x,y,z),(.65,.65,.36),darkwood,bev=.06)

# front gable planks and beams
for x in [-2.8,-2.1,-1.4,-.7,0,.7,1.4,2.1,2.8]:
    h=max(.2,2.4-abs(x)*.72); cube('gable plank',(x,-3.02,4.7+h/2),(.66,.30,h),wood,bev=.035)
cube('gable crossbeam',(0,-3.35,4.55),(7.3,.32,.35),wood2,bev=.07)
for s in [-1,1]: cube('gable fascia',(s*1.75,-3.38,6.15),(4.5,.34,.30),wood2,rot=(0,s*math.radians(39),0),bev=.06)

# door
cube('door',(0,-3.24,2.35),(1.7,.25,3.35),wood2,bev=.04)
for x in [-.68,.68]: cube('door frame',(x,-3.39,2.35),(.25,.25,3.7),darkwood,bev=.035)
cube('door lintel',(0,-3.4,4.15),(1.8,.28,.28),darkwood,bev=.04)
for x in [-.5,0,.5]: cube('door board',(x,-3.42,2.35),(.05,.05,3.0),darkwood)
cyl('door handle',(.55,-3.58,2.3),.08,.12,black,8,rot=(math.pi/2,0,0))

def window(n,loc,size=(1.35,.18,1.55),front=True):
    cube(n+' light',loc,size,glow,bev=.025)
    if front:
        x,y,z=loc; cube(n+' vertical',(x,y-.12,z),(.11,.18,size[2]+.35),darkwood); cube(n+' horizontal',(x,y-.13,z),(size[0]+.35,.18,.11),darkwood)
        for xx in [-size[0]/2-.12,size[0]/2+.12]: cube(n+' frame',(x+xx,y-.11,z),(.22,.21,size[2]+.4),wood2,bev=.025)
        for zz in [-size[2]/2-.12,size[2]/2+.12]: cube(n+' frame',(x,y-.11,z+zz),(size[0]+.4,.21,.22),wood2,bev=.025)
window('gable window',(0,-3.25,5.45),(1.1,.18,1.25))
# side windows on camera-facing right x wall: rotate window assemblies simply as glowing panels and frames
for yy in [-.8,1.55]:
    cube('side window light',(3.72,yy,2.75),(.16,1.25,1.5),glow)
    for dy in [-.74,.74]: cube('side window frame',(3.82,yy+dy,2.75),(.22,.20,1.85),wood2,bev=.03)
    for dz in [-.88,.88]: cube('side window frame',(3.82,yy,dz+2.75),(.22,1.65,.20),wood2,bev=.03)
    cube('side mullion',(3.84,yy,2.75),(.22,.1,1.5),darkwood); cube('side mullion',(3.84,yy,2.75),(.22,1.25,.1),darkwood)

# roof planes and shingles
roof_angle=math.radians(39)
for s in [-1,1]: cube('roof underlay',(s*1.75,0,5.9),(4.65,7.15,.28),roofmat,rot=(0,s*roof_angle,0),bev=.04)
for s in [-1,1]:
 for row in range(7):
  for col in range(5):
   u=-3.0+row*.95; xlocal=.35+col*.82
   x=s*xlocal*math.cos(roof_angle); z=7.38-xlocal*math.sin(roof_angle)
   y=u+(row%2)*.10
   cube('individual shingle',(x,y,z),(1.0,.92,.10),random.choice([roofmat,darkwood]),rot=(0,s*roof_angle,0),bev=.018)
cube('ridge cap',(0,0,7.5),(.38,7.25,.34),darkwood,bev=.07)

# chimney blocks
for zi in range(5):
 for yi in range(2):
  for xi in range(2):
   cube('chimney masonry',(1.85+xi*.48+(zi%2)*.08,1.05+yi*.48,6.45+zi*.38),(.45,.45,.34),mortar,bev=.035)
cube('chimney cap',(2.12,1.3,8.33),(1.35,1.2,.22),black,bev=.04)

# porch deck, stairs, railings
cube('porch deck',(0,-4.45,.72),(7.4,2.5,.30),wood2,bev=.04)
for i in range(5): cube('deck board',(-3+i*1.5,-4.5,.9),(1.4,2.2,.08),darkwood)
for i in range(3): cube('front step',(0,-5.8-i*.42,.55-i*.18),(2.6,.72,.22),wood2,bev=.035)
for x in [-3.3,3.3]:
 for y in [-3.75,-5.15]: cube('porch post',(x,y,1.55),(.28,.28,1.7),wood2,bev=.04)
 cube('porch rail',(x,-4.45,1.65),(.23,2.55,.22),wood2,bev=.035)
 for y in [-4.05,-4.55,-5.05]: cube('porch baluster',(x,y,1.35),(.18,.18,1.15),wood2)

# lanterns
def lantern(loc):
    x,y,z=loc; cube('lantern glow',(x,y,z),(.42,.32,.55),glow,bev=.03); cube('lantern top',(x,y,z+.38),(.62,.48,.12),black); cube('lantern bottom',(x,y,z-.38),(.58,.44,.12),black)
    for dx in [-.25,.25]: cube('lantern bar',(x+dx,y,z),(.055,.06,.75),black)
lantern((-1.45,-3.55,3.2)); lantern((-7.3,-9.8,1.2))

# pines
def pine(x,y,h,fg=False):
    cyl('pine trunk',(x,y,h*.19),h*.075,h*.38,darkwood,7)
    for j,(rr,zz) in enumerate([(h*.24,h*.38),(h*.20,h*.55),(h*.15,h*.70),(h*.10,h*.84)]): cone('pine crown',(x,y,zz),rr,0,h*.32,green if j%2 else green2,7)
for args in [(-12,4,8),(-9,8,7),(-6,7,10),(7,6,10),(11,2,13),(14,7,10),(-14,-4,7),(-10,-1,6),(8,-1,7),(15,-5,9),(-16,9,9),(3,9,8),(0,10,7)]: pine(*args)

# bushes, rocks, grass tufts
for i in range(34):
    x=random.uniform(-10,10); y=random.uniform(-8,7)
    if -4<x<4 and -5<y<4: continue
    ico('angular bush',(x,y,.45),(random.uniform(.45,1.0),random.uniform(.45,.9),random.uniform(.45,.85)),leaf,1)
for i in range(30):
    x=random.uniform(-12,12); y=random.uniform(-11,8)
    if -3<x<3 and -6<y<3: continue
    ico('rock',(x,y,.25),(random.uniform(.25,.75),random.uniform(.3,.8),random.uniform(.25,.6)),stone,1)
for i in range(35):
    x=random.uniform(-12,12); y=random.uniform(-11,8)
    for a in [-.18,0,.18]: cone('grass blade',(x+a,y,.28),.12,0,.65,green2,5)

# wood pile, stump, axe
for row in range(3):
 for j in range(4-row):
  z=.34+row*.42; y=-5.8+j*.53+row*.22
  cyl('stacked firewood',(6.8,y,z),.22,2.1,wood2,8,rot=(0,math.pi/2,0))
cyl('chopping stump',(4.7,-6.3,.45),.72,.9,wood2,9)
cube('axe handle',(4.8,-6.3,1.45),(.14,.14,2.2),wood2,rot=(0,.55,.12),bev=.03); cube('axe head',(4.22,-6.34,2.25),(.65,.18,.38),stone,rot=(0,.25,0),bev=.05)
# barrel
cyl('barrel',(-1.8,-4.05,1.35),.42,1.1,wood2,12); cyl('barrel hoop',(-1.8,-4.05,1.72),.45,.09,black,12); cyl('barrel hoop',(-1.8,-4.05,.98),.45,.09,black,12)
# mushrooms
for x,y in [(-5.5,-6.8),(6.2,-8.0),(8.8,-7.0)]: cyl('mushroom stem',(x,y,.22),.08,.35,white,7); cone('mushroom cap',(x,y,.43),.28,0,.18,red,8)

# background mountains
for x,y,h,r in [(-12,14,12,7),(-3,16,14,8),(7,17,15,9),(16,15,13,8)]: cone('mountain',(x,y,h/2-1),r,0,h,mountain,7)

# lighting/world
world=bpy.data.worlds.new('golden forest world'); bpy.context.scene.world=world; world.use_nodes=True; world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.055,.075,.09,1); world.node_tree.nodes['Background'].inputs['Strength'].default_value=.32
bpy.ops.object.light_add(type='AREA',location=(-7,-10,17)); sun=bpy.context.object; sun.name='large warm sun'; sun.data.energy=1650; sun.data.shape='DISK'; sun.data.size=8; sun.data.color=(1,.55,.27); sun.rotation_euler=(math.radians(25),0,math.radians(-28))
bpy.ops.object.light_add(type='AREA',location=(5,-5,8)); fill=bpy.context.object; fill.data.energy=550; fill.data.color=(1,.24,.05); fill.data.size=5

# camera
bpy.ops.object.camera_add(location=(18,-25,14.5)); cam=bpy.context.object; bpy.context.scene.camera=cam
def track(obj,pt): obj.rotation_euler=(Vector(pt)-obj.location).to_track_quat('-Z','Y').to_euler()
track(cam,(0,-.3,3.0)); cam.data.lens=52; cam.data.dof.use_dof=True; cam.data.dof.focus_object=bpy.data.objects['door']; cam.data.dof.aperture_fstop=2.8

sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=1000; sc.render.resolution_y=563; sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'; sc.render.filepath=os.path.join(ROOT,'render.png'); sc.render.film_transparent=False
sc.render.image_settings.color_mode='RGBA'; sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=1.15
sc.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'sol_light.blend'))
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'sol_light.blend'))
