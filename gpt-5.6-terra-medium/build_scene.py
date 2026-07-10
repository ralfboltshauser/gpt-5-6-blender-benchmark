import bpy, math, random
from mathutils import Vector
random.seed(16)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def M(n,c,emit=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=.78
 if emit:b.inputs['Emission Color'].default_value=(*c,1);b.inputs['Emission Strength'].default_value=emit
 return m
wood=M('Cedar',(.30,.11,.025)); lightwood=M('Cut cedar',(.52,.23,.065)); dark=M('Dark timber',(.055,.022,.008)); roof=M('Slate charcoal',(.025,.03,.045)); stone=M('Stone',(.22,.24,.27)); grass=M('Meadow',(.10,.22,.055)); pine=M('Needles',(.035,.15,.04)); pine2=M('Needle highlights',(.10,.28,.065)); earth=M('Path earth',(.42,.23,.09)); glow=M('Golden window',(1,.14,.004),4); iron=M('Iron',(.01,.008,.006)); red=M('Mushroom red',(.65,.025,.005))
def cube(n,p,s,ma,bevel=0):
 bpy.ops.mesh.primitive_cube_add(location=p);o=bpy.context.object;o.name=n;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if ma:o.data.materials.append(ma)
 if bevel: q=o.modifiers.new('Rounded corners','BEVEL');q.width=bevel;q.segments=2
 return o
def cyl(n,p,r,d,ma,v=8,rot=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=v,radius=r,depth=d,location=p,rotation=rot or (0,0,0));o=bpy.context.object;o.name=n;o.data.materials.append(ma);return o
def cone(n,p,r,d,ma,v=7):
 bpy.ops.mesh.primitive_cone_add(vertices=v,radius1=r,radius2=0,depth=d,location=p);o=bpy.context.object;o.name=n;o.data.materials.append(ma);return o
def ico(n,p,r,ma):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=r,location=p);o=bpy.context.object;o.name=n;o.data.materials.append(ma);return o
def beam(n,a,b,w,ma):
 a,b=Vector(a),Vector(b);o=cube(n,(a+b)/2,(w,w,(b-a).length/2),ma,.02);o.rotation_mode='QUATERNION';o.rotation_quaternion=Vector((0,0,1)).rotation_difference((b-a).normalized());return o

# land and meandering low-poly path
cube('Meadow',(0,0,-.35),(16,14,.35),grass)
for i in range(20):
 t=i/19;x=-8+7.8*t;y=-4.4+1.9*t+1.1*math.sin(t*5);ico('Path stone',(x,y,-.02),.54+random.random()*.2,earth)

# stone base, timber cabin
for x in [-2.4,-1.6,-.8,0,.8,1.6,2.4]:
 for y in [-1.55,1.55]:cube('Foundation stone',(x,y,.12),(.35,.3,.24),stone,.04)
for z in [.45,.78,1.11,1.44,1.77,2.1]:
 cube('Front log',(0,-1.5,z),(2.65,.15,.14),wood,.035);cube('Back log',(0,1.5,z),(2.65,.15,.14),wood,.035);cube('Side log',(-2.5,0,z),(.15,1.55,.14),wood,.035);cube('Side log',(2.5,0,z),(.15,1.55,.14),wood,.035)
for z,w in [(2.4,2.2),(2.7,1.75),(3,1.3),(3.3,.85),(3.6,.4)]:cube('Gable planks',(0,-1.51,z),(w,.12,.13),wood,.02)
for x in [-2.5,2.5]:
 for y in [-1.5,1.5]:cube('Corner post',(x,y,1.3),(.16,.16,1.25),dark,.03)
cube('Door',(0,-1.68,1.04),(.53,.06,.85),lightwood,.02)
for x in [-.42,-.14,.14,.42]:cube('Door board',(x,-1.75,1.04),(.015,.02,.8),dark)
cube('Door lintel',(0,-1.75,1.98),(.75,.1,.1),dark,.02);cyl('Door handle',(.38,-1.82,1.1),.05,.07,iron,8,(math.pi/2,0,0))
def window(p,w,h,side=False):
 x,y,z=p
 if not side:
  cube('Glowing window',p,(w,.015,h),glow);cube('Frame',(x,y-.035,z+h),(w+.1,.035,.05),dark);cube('Frame',(x,y-.035,z-h),(w+.1,.035,.05),dark)
  for dx in [-w,0,w]:cube('Mullion',(x+dx,y-.04,z),(.04,.035,h),dark)
  cube('Mullion',(x,y-.04,z),(w,.035,.035),dark)
 else:
  cube('Glowing window',p,(.015,w,h),glow)
  for dy in [-w,0,w]:cube('Mullion',(x+.04,y+dy,z),(.035,.04,h),dark)
  for dz in [-h,h]:cube('Frame',(x+.04,y,z+dz),(.035,w+.1,.05),dark)
  cube('Mullion',(x+.04,y,z),(.035,w,.035),dark)
window((0,-1.67,2.88),.38,.38);window((2.67,-.65,1.35),.44,.42,True);window((2.67,.75,1.35),.44,.42,True)

# individually visible shingle courses
for side in [-1,1]:
 for row in range(7):
  for col in range(7):
   o=cube('Roof shingle',(-2.55+col*.84+(row%2)*.18,side*(1.65-row*.20),2.2+row*.23),(.46,.22,.055),roof,.015);o.rotation_euler[0]=side*math.radians(37)
beam('Roof fascia',(-2.9,-1.72,2.14),(0,-1.72,3.92),.11,lightwood);beam('Roof fascia',(0,-1.72,3.92),(2.9,-1.72,2.14),.11,lightwood);beam('Ridge',(0,-1.7,3.92),(0,1.7,3.92),.12,dark)
for level in range(8):
 for ix in range(2):
  for iy in range(2):cube('Chimney block',(.75+(ix-.5)*.32,.45+(iy-.5)*.32,3.15+level*.24),(.18,.18,.12),stone,.02)
cube('Chimney cap',(.75,.45,5.05),(.5,.5,.08),dark,.02)

# porch and lanterns
cube('Porch deck',(0,-2.3,.38),(1.8,.72,.12),lightwood,.03)
for i in range(3):cube('Front step',(0,-3.05-i*.23,.18-i*.1),(1.15-i*.11,.26,.1),lightwood,.02)
for x in [-1.62,1.62]:
 for y in [-2.85,-1.72]:cube('Porch post',(x,y,.9),(.1,.1,.65),dark,.02)
 beam('Porch rail',(x,-2.85,.9),(x,-1.72,.9),.05,lightwood)
def lantern(p,s):
 x,y,z=p;cube('Lantern housing',(x,y,z),(.12*s,.1*s,.19*s),iron,.015);cube('Lantern glow',(x,y-.11*s,z),(.075*s,.01*s,.12*s),glow);cyl('Lantern hood',(x,y,z+.25*s),.17*s,.05*s,iron,6)
lantern((-1.15,-1.92,1.4),.85);lantern((-5.1,-3.2,.55),.7)

# trees and environmental dressing
def tree(x,y,s):
 cyl('Pine trunk',(x,y,s*.55),s*.18,s*1.1,wood,7)
 for i,(r,z) in enumerate([(s*.8,s*.9),(s*.65,s*1.35),(s*.47,s*1.78),(s*.29,s*2.14)]):cone('Faceted pine',(x,y,z),r,s*.8,pine2 if i%2==0 else pine,7)
for v in [(-5,-2,2.1),(-6.6,2,2.9),(-4.2,4,2.1),(4.8,-2.4,3.2),(5.8,2.5,3.5),(3.8,5,2.5),(-1.8,5.2,2.8),(7,5,4),(-8,5,2.3),(7,-5,2.8)]:tree(*v)
mount=M('Distant mountains',(.25,.28,.22))
for x in [-10,-6,-2,2,6,10]:cone('Distant mountain',(x,9,2.3),2.5+random.random()*1.4,4+random.random()*2,mount,5)
for i in range(35):
 a=random.random()*math.tau;r=random.uniform(3.5,9);x,y=math.cos(a)*r,math.sin(a)*r
 if -3<x<3 and -3<y<3:continue
 if random.random()<.5:ico('Forest rock',(x,y,.17),random.uniform(.12,.4),stone)
 else:ico('Shrub',(x,y,.25),random.uniform(.22,.5),pine2)
for x,y in [(3,-4.8),(2.2,-4.2),(-3.5,-3.2),(4.3,-3.7)]:
 cyl('Mushroom stem',(x,y,.12),.06,.22,lightwood,7);cone('Mushroom cap',(x,y,.29),.18,.13,red,8)
for row in range(3):
 for j in range(4-row):cyl('Stacked log',(4+j*.55+row*.22,-3.5,.28+row*.28),.14,.65,lightwood,10,(0,math.pi/2,0))
cyl('Chopping stump',(2.8,-3.35,.45),.38,.8,lightwood,8);beam('Axe handle',(2.7,-3.38,.88),(2.1,-3.9,.35),.045,lightwood);ico('Axe head',(2.72,-3.36,.88),.14,stone)
for x in [-6,-5.1,-4.2]:cube('Fence post',(x,-3.2,.55),(.08,.08,.55),lightwood,.015)
beam('Fence rail',(-6,-3.2,.65),(-4.2,-3.2,.65),.05,lightwood)

# golden-hour composition
world=bpy.data.worlds.new('World');bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.04,.055,.08,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.25
bpy.ops.object.light_add(type='AREA',location=(-5,-6,9));key=bpy.context.object;key.data.energy=1250;key.data.color=(1,.32,.08);key.data.shape='DISK';key.data.size=8;key.rotation_euler=(math.radians(25),0,math.radians(-35))
bpy.ops.object.light_add(type='AREA',location=(2,-3,4));fill=bpy.context.object;fill.data.energy=350;fill.data.color=(1,.15,.03);fill.data.shape='DISK';fill.data.size=5;fill.rotation_euler=(math.radians(45),0,math.radians(155))
bpy.ops.object.camera_add(location=(10,-15,8.1));cam=bpy.context.object;bpy.context.scene.camera=cam;cam.rotation_euler=(Vector((0,-.1,1.6))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=52;cam.data.dof.use_dof=True;cam.data.dof.focus_object=bpy.data.objects['Door'];cam.data.dof.aperture_fstop=5
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE';s.render.resolution_x=900;s.render.resolution_y=700;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath='/home/ralf/prj/exploration/blender-benchmark/gpt-5.6-terra-medium/cabin_render.png';s.view_settings.look='AgX - Medium High Contrast'
bpy.ops.wm.save_as_mainfile(filepath='/home/ralf/prj/exploration/blender-benchmark/gpt-5.6-terra-medium/forest_cabin.blend');bpy.ops.render.render(write_still=True)
