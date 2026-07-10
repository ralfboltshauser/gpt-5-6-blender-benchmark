import bpy, math, random
from mathutils import Vector
random.seed(12)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def M(n,c,emit=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=.72
 if emit:b.inputs['Emission Color'].default_value=(*c,1);b.inputs['Emission Strength'].default_value=emit
 return m
wood=M('warm timber',(.28,.10,.028)); lightwood=M('cut timber',(.48,.20,.055)); roof=M('charcoal shingles',(.035,.027,.025)); stone=M('slate stone',(.16,.18,.20)); grass=M('moss grass',(.12,.25,.055)); pine=M('pine',(.035,.16,.055)); pinehi=M('sunlit pine',(.16,.31,.075)); dirt=M('path earth',(.45,.22,.09)); glow=M('window fire',(1,.16,.005),3); iron=M('iron',(.015,.012,.01)); red=M('mushroom',(.7,.025,.005)); cream=M('stem',(.7,.55,.28))
def cube(n,l,s,ma,bev=0):
 bpy.ops.mesh.primitive_cube_add(location=l);o=bpy.context.object;o.name=n;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma)
 if bev: q=o.modifiers.new('edge bevel','BEVEL');q.width=bev;q.segments=1
 return o
def cyl(n,l,r,d,ma,rot=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=d,location=l,rotation=rot or (0,0,0));o=bpy.context.object;o.name=n;o.data.materials.append(ma);return o
def cone(n,l,r,d,ma):
 bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=r,radius2=.025,depth=d,location=l);o=bpy.context.object;o.name=n;o.data.materials.append(ma);return o
def lamp(l,e=90):
 bpy.ops.object.light_add(type='POINT',location=l);o=bpy.context.object;o.data.energy=e;o.data.color=(1,.22,.025);o.data.shadow_soft_size=1.2
# terrain and trail
cube('ground',(0,0,-.25),(18,18,.25),grass)
for y in range(-13,1):
 for x in [-.42,0,.42]:
  if random.random()>.12: cone('faceted path',(x+.16*math.sin(y),y,.012),.42,.04,dirt)
# stone foundation
for x in [-2,-1.35,-.7,0,.7,1.35,2]:
 for y in [-.05,2.45]:cube('foundation',(x,y,.24),(.3,.27,.25),stone,.04)
for y in [.55,1.15,1.75]:
 for x in [-2,2]:cube('foundation',(x,y,.24),(.27,.3,.25),stone,.04)
# timber cabin walls
for z in [.65,1.05,1.45,1.85,2.25]:
 for x in [-1.7,-1.15,-.58,0,.58,1.15,1.7]:cube('front log',(x,-.04,z),(.30,.15,.17),wood,.025)
 for y in [.4,.9,1.4,1.9,2.25]:
  cube('side log',(-1.95,y,z),(.15,.23,.17),wood,.02);cube('side log',(1.95,y,z),(.15,.23,.17),wood,.02)
# door and front windows
cube('door',(0,-.21,1.28),(.39,.04,.90),lightwood,.02)
for x in [-.45,.45]:cube('door frame',(x,-.26,1.28),(.06,.06,1.04),wood,.02)
cube('door top',(0,-.26,2.3),(.55,.06,.06),wood,.02);cyl('door handle',(.29,-.28,1.27),.04,.05,iron,(math.pi/2,0,0))
def win(x,y,z,side=False):
 if side: cube('window glow',(x,y,z),(.02,.30,.36),glow);cube('mullion',(x+.04,y,z),(.03,.035,.43),wood);cube('cross',(x+.04,y,z),(.03,.36,.025),wood)
 else: cube('window glow',(x,y,z),(.30,.02,.36),glow);cube('mullion',(x,y-.04,z),(.025,.03,.43),wood);cube('cross',(x,y-.04,z),(.37,.03,.025),wood)
win(-1.28,-.2,1.48);win(1.28,-.2,1.48);win(2.0,1.40,1.48,True)
# gable
for i in range(4):cube('gable wood',(0,-.03,2.52+i*.32),(1.72-i*.35,.14,.13),wood,.02)
for s in [-1,1]:
 b=cube('gable brace',(s*.9,-.16,3.12),(.08,.10,1.0),lightwood,.02);b.rotation_euler[1]=-s*.48
win(0,-.19,2.83)
# roof tile courses
for side in [-1,1]:
 for row in range(7):
  for x in [-1.75,-1.17,-.59,0,.59,1.17,1.75]:
   t=cube('individual roof shingle',(x+(row%2)*.12,1.07+side*(.17+row*.20),2.5+row*.27),(.36,.32,.045),roof,.015);t.rotation_euler[0]=side*.59
cube('ridge',(0,1.07,4.34),(2.2,.12,.1),lightwood,.025)
# chimney
for z in [3.2,3.5,3.8,4.1]:
 for x in [1.02,1.32]:
  for y in [1.45,1.72]:cube('chimney brick',(x,y,z),(.145,.145,.14),stone,.02)
cube('chimney cap',(1.17,1.58,4.3),(.44,.42,.07),iron,.02)
# porch, rails, lantern
cube('porch',(0,-1.02,.43),(1.65,.7,.09),lightwood,.02)
for x in [-1.48,1.48]:cube('rail post',(x,-1.55,.82),(.07,.07,.48),lightwood,.02)
cube('left rail',(-.75,-1.55,.82),(.7,.05,.05),lightwood);cube('right rail',(.75,-1.55,.82),(.7,.05,.05),lightwood)
for y,w,z in [(-1.72,.75,.25),(-1.92,.58,.08)]:cube('stairs',(0,y,z),(w,.2,.12),lightwood,.02)
cube('lantern',(-1.72,-.38,1.35),(.13,.09,.20),iron,.02);cube('lantern glass',(-1.72,-.49,1.35),(.08,.015,.13),glow);lamp((-1.72,-.72,1.36))
# trees
def tree(x,y,s):
 cyl('trunk',(x,y,s*.48),s*.13,s*.96,wood)
 for r,z,ma in [(s*.72,s*.75,pine),(s*.55,s*1.15,pine),(s*.39,s*1.53,pinehi)]:cone('low poly pine',(x,y,z),r,s*.78,ma)
for a in [(-6,1,2.7),(-5,-2.5,2),(-3.7,4.2,3),(5.7,.4,3.4),(5,-3.1,2.5),(7,4.5,3.4),(-8,-3,3.1),(2.1,5.6,2.7),(-7,4.8,3.4),(7,-5,3.2)]:tree(*a)
# clutter / foreground logs
for i in range(40):
 x=random.uniform(-8,8);y=random.uniform(-6,6)
 if -2.7<x<2.7 and -2<y<3:continue
 cone('rock',(x,y,.16),random.uniform(.15,.42),random.uniform(.25,.5),stone)
for i in range(35):
 x=random.uniform(-7,7);y=random.uniform(-6,5)
 if -2.4<x<2.4 and -1<y<3:continue
 cone('shrub',(x,y,.2),random.uniform(.16,.36),random.uniform(.25,.52),pinehi)
for x,y in [(3.1,-4.2),(3.55,-4.35),(3.7,-3.9)]:cyl('firewood',(x,y,.25),.15,.95,lightwood,(0,math.pi/2,.2))
cyl('stump',(1.5,-3.9,.34),.34,.68,lightwood);h=cyl('axe handle',(1.84,-3.55,.78),.035,1.2,lightwood,(.85,0,-.3));cube('axe head',(2.1,-3.3,1.17),(.14,.08,.1),stone,.02)
for x,y in [(1.9,-5.0),(2.35,-4.85)]:cyl('mushroom stem',(x,y,.1),.05,.2,cream);cone('red cap',(x,y,.25),.18,.11,red)
# lighting and camera
bpy.context.scene.world.use_nodes=True;bg=bpy.context.scene.world.node_tree.nodes['Background'];bg.inputs['Color'].default_value=(.12,.045,.012,1);bg.inputs['Strength'].default_value=.32
bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.data.energy=1.7;sun.data.color=(1,.42,.14);sun.rotation_euler=(.45,-.4,-.6)
bpy.ops.object.light_add(type='AREA',location=(-5,-5,8));ar=bpy.context.object;ar.data.energy=900;ar.data.shape='DISK';ar.data.size=6;ar.data.color=(1,.32,.08);ar.rotation_euler=(.4,0,-.5)
bpy.ops.object.camera_add(location=(8.7,-13.8,6.6));cam=bpy.context.object;bpy.context.scene.camera=cam;cam.rotation_euler=(Vector((0,.25,1.75))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=52
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1100;s.render.resolution_y=780;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath='/home/ralf/prj/exploration/blender-benchmark/gpt-5.6-terra-light/terra_light.png';s.view_settings.look='AgX - Medium High Contrast'
bpy.ops.wm.save_as_mainfile(filepath='/home/ralf/prj/exploration/blender-benchmark/gpt-5.6-terra-light/terra_light.blend');bpy.ops.render.render(write_still=True)
