import bpy
import math
import random
from mathutils import Vector

# A warm low-poly woodland cabin scene, composed only from procedural Blender primitives.
random.seed(56)

# -----------------------------------------------------------------------------
# scene / utilities
# -----------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1152
scene.render.resolution_y = 648
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = '//cabin_woodland.png'
scene.render.film_transparent = False
scene.render.image_settings.color_mode = 'RGBA'
scene.view_settings.look = 'AgX - Medium High Contrast'
if scene.world is None:
    scene.world = bpy.data.worlds.new('Woodland World')
scene.world.color = (0.055, 0.075, 0.045)

def mat(name, color, metallic=0.0, rough=0.72, emission=None):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metallic
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*emission[0], 1)
        bsdf.inputs['Emission Strength'].default_value = emission[1]
    return m

M = {
    'grass': mat('Mossy forest floor', (0.18, .31, .085)),
    'grass2': mat('Olive clearing', (.28, .40, .10)),
    'path': mat('Warm earthen path', (.52, .30, .15)),
    'path2': mat('Sunlit path facets', (.67, .42, .22)),
    'wood': mat('Honey pine logs', (.35, .16, .06)),
    'wood2': mat('Fresh-cut orange wood', (.52, .25, .08)),
    'wooddark': mat('Dark timber', (.16, .065, .025)),
    'roof': mat('Charcoal roof slate', (.075, .078, .095)),
    'roof2': mat('Blue black slate', (.055, .08, .115)),
    'stone': mat('Foundation stone', (.23, .23, .25)),
    'stone2': mat('Chimney stone', (.36, .33, .31)),
    'glass': mat('Amber window glow', (1.0, .27, .025), rough=.35, emission=((1.0, .19, .012), 3.8)),
    'lamp': mat('Lantern glow', (1.0, .35, .03), rough=.2, emission=((1.0, .16, .005), 9)),
    'green1': mat('Pine sun green', (.17, .30, .08)),
    'green2': mat('Pine dark green', (.065, .17, .07)),
    'green3': mat('Pine olive green', (.29, .39, .09)),
    'bush': mat('Shrub green', (.16, .36, .08)),
    'bark': mat('Pine bark', (.20, .085, .027)),
    'mushroom': mat('Mushroom cap', (.70, .055, .016)),
    'cream': mat('Mushroom stem', (.72, .53, .30)),
    'iron': mat('Black iron', (.035, .025, .02), metallic=.65, rough=.31),
    'mountain': mat('Distant warm granite', (.36, .27, .20)),
    'mountainlight': mat('Sunlit distant granite', (.53, .40, .29)),
}

def assign(obj, material):
    obj.data.materials.append(material)
    return obj

def cube(name, loc, scale, material, bevel=0, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (scale[0]/2, scale[1]/2, scale[2]/2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if material: assign(o, material)
    if bevel:
        mod = o.modifiers.new('Small softened edges', 'BEVEL')
        mod.width, mod.segments = bevel, 1
    return o

def cone(name, loc, radius1, radius2, depth, material, vertices=6, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius1, radius2=radius2, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    assign(o, material)
    return o

def cyl(name, loc, radius, depth, material, vertices=8, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name
    assign(o, material)
    return o

def ico(name, loc, radius, material, scale=(1,1,1)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(o, material); return o

def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z','Y').to_euler()

# -----------------------------------------------------------------------------
# irregular faceted ground
# -----------------------------------------------------------------------------
size, n = 32, 12
verts=[]
for j in range(n+1):
    for i in range(n+1):
        x=-size/2 + size*i/n; y=-size/2 + size*j/n
        z=random.uniform(-.11,.11) if 0 < i < n and 0 < j < n else 0
        verts.append((x,y,z))
faces=[]
for j in range(n):
    for i in range(n):
        a=j*(n+1)+i; b=a+1; c=a+n+1; d=c+1
        faces.extend([(a,b,d),(a,d,c)] if (i+j)%2 else [(a,b,c),(b,d,c)])
mesh=bpy.data.meshes.new('Faceted forest floor mesh'); mesh.from_pydata(verts,[],faces)
ground=bpy.data.objects.new('Faceted forest floor',mesh); bpy.context.collection.objects.link(ground)
for x in (M['grass'],M['grass2'], mat('Deep moss',(.10,.22,.055))): ground.data.materials.append(x)
for p in ground.data.polygons: p.material_index=random.choices([0,1,2],[.55,.32,.13])[0]

# meandering paved dirt path
pts=[(-4.2,-15),(-2.9,-10.5),(-2.0,-7),(-2.8,-4.2),(-1.3,-2.2),(0.0,-.6)]
pv=[]
for i,p in enumerate(pts):
    q=Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)])
    q.normalize(); side=Vector((-q.y,q.x))
    w=1.22 if i<4 else 1.0
    pv.extend([(p[0]+side.x*w,p[1]+side.y*w,.09),(p[0]-side.x*w,p[1]-side.y*w,.09)])
pf=[]
for i in range(len(pts)-1):
    pf.extend([(i*2,i*2+1,i*2+2),(i*2+1,i*2+3,i*2+2)])
pm=bpy.data.meshes.new('Path mesh');pm.from_pydata(pv,[],pf)
path=bpy.data.objects.new('Winding front path',pm); bpy.context.collection.objects.link(path)
path.data.materials.append(M['path']);path.data.materials.append(M['path2'])
for p in path.data.polygons:p.material_index=random.randrange(2)

# -----------------------------------------------------------------------------
# cabin base, logs and gable
# -----------------------------------------------------------------------------
# Foundation stones around base
for x in [-3.55,-2.35,-1.15,0.05,1.25,2.45,3.55]:
    cube('Front foundation stone',(x,-2.35,.48),(1.05,.62,.72),M['stone'],.06)
    cube('Back foundation stone',(x,3.52,.48),(1.05,.62,.72),M['stone'],.06)
for y in [-1.63,-.42,.8,2.02,3.1]:
    cube('Side foundation stone',(-3.62,y,.48),(.65,1.05,.72),M['stone'],.06)
    cube('Side foundation stone',(3.62,y,.48),(.65,1.05,.72),M['stone'],.06)

# dark inner wall mass, retained behind individual logs
cube('Cabin wall core',(0,.55,2.72),(7.0,5.65,4.45),M['wooddark'],.05)
# front horizontal log courses, interrupted by door
for k in range(7):
    z=1.12+k*.48
    for x,length in [(-2.45,2.1),(2.45,2.1)]:
        cube('Front hand-hewn log',(x,-2.31,z),(length,.36,.39),M['wood'],.045)
# corner log ends
for k in range(7):
    z=1.12+k*.48
    for x in (-3.52,3.52): cube('Protruding corner log',(x,-2.40,z),(.72,.5,.39),M['wood2'],.04)
# right side log courses
for k in range(7):
    z=1.12+k*.48
    cube('Right wall log',(3.49,.55,z),(.36,5.5,.39),M['wood'],.045)
# left edge showing down side
for k in range(7): cube('Left wall log',(-3.49,.55,1.12+k*.48),(.36,5.5,.39),M['wood'],.045)

# front gable triangle filled with horizontal boards
for row in range(6):
    z=4.42+row*.42
    width=6.7-row*1.02
    cube('Gable timber',(0,-2.35,z),(width,.30,.34),M['wood'],.025)
# strong framing on face and gable
cube('Front top beam',(0,-2.56,4.20),(7.65,.42,.42),M['wood2'],.04)
for sx in (-1,1):
    angle=sx * math.atan2(2.45,3.75)
    cube('Gable diagonal timber',(sx*1.91,-2.59,5.52),(4.65,.38,.38),M['wood2'],.035,rot=(0,angle,0))
cube('Gable vertical timber',(0,-2.58,5.52),(.34,.38,2.65),M['wood2'],.025)

# door (slats, surround, iron handle)
cube('Door',(0,-2.53,2.25),(1.48,.18,2.72),M['wooddark'],.025)
for x in [-.54,-.18,.18,.54]: cube('Door vertical plank',(x,-2.65,2.25),(.29,.075,2.55),M['wood2'],.015)
cube('Door lintel',(0,-2.72,3.68),(1.95,.33,.38),M['wood2'],.03)
for x in (-.88,.88): cube('Door side timber',(x,-2.72,2.35),(.32,.33,2.85),M['wood2'],.02)
cyl('Door handle',(.52,-2.77,2.32),.075,.23,M['iron'],8,rot=(math.pi/2,0,0))

def window(name, loc, width=1.26, height=1.45, orient='front'):
    # positioned just ahead of wall; all parts use local x span for front, y span for side
    if orient=='front':
        cube(name+' glow',loc,(width,.08,height),M['glass'])
        cube(name+' top',(loc[0],loc[1]-.065,loc[2]+height/2),(width+.28,.18,.22),M['wood2'])
        cube(name+' bottom',(loc[0],loc[1]-.065,loc[2]-height/2),(width+.28,.18,.22),M['wood2'])
        for xx in (-width/2-.02,0,width/2+.02): cube(name+' mullion',(loc[0]+xx,loc[1]-.07,loc[2]),(.16,.19,height+.26),M['wood2'])
        cube(name+' cross',(loc[0],loc[1]-.08,loc[2]),(width+.12,.19,.13),M['wood2'])
    else:
        cube(name+' glow',loc,(.08,width,height),M['glass'])
        cube(name+' top',(loc[0]+.065,loc[1],loc[2]+height/2),(.18,width+.28,.22),M['wood2'])
        cube(name+' bottom',(loc[0]+.065,loc[1],loc[2]-height/2),(.18,width+.28,.22),M['wood2'])
        for yy in (-width/2-.02,0,width/2+.02): cube(name+' mullion',(loc[0]+.07,loc[1]+yy,loc[2]),(.19,.16,height+.26),M['wood2'])
        cube(name+' cross',(loc[0]+.08,loc[1],loc[2]),(.19,width+.12,.13),M['wood2'])

window('Gable window',(0,-2.58,5.47),1.02,1.25,'front')
window('Front left window',(-2.20,-2.55,2.55),1.32,1.42,'front')
window('Side window',(3.60,1.55,2.55),1.38,1.48,'side')

# Porch, timber railing, steps
cube('Porch deck',(0,-3.55,.98),(5.2,2.2,.28),M['wood2'],.035)
for x in [-2.3,-1.1,0,1.1,2.3]: cube('Deck boards',(x,-3.55,1.16),(.78,2.0,.09),M['wooddark'],.01)
for x in (-2.32,2.32):
    cube('Porch post',(x,-4.37,1.84),(.26,.26,1.72),M['wood2'],.03)
    cube('Porch rail',(x,-3.75,1.66),(.20,1.4,.18),M['wood2'],.02)
cube('Left porch rail',(-1.35,-4.36,1.65),(1.85,.19,.18),M['wood2'],.02)
for x in (-2.32,2.32,-1.35): cube('Rail upright',(x,-4.36,1.32),(.17,.17,.88),M['wood2'],.02)
for z,y,w in [(.72,-4.88,2.15),(.45,-5.18,1.75),(.20,-5.44,1.30)]: cube('Porch steps',(0,y,z),(w,.54,.25),M['wood2'],.025)

# roof main planes and shingles
pitch=math.atan2(2.65,4.65)
for side in (-1,1):
    # main roof slab: the long dimension follows slope, rotated around Y
    cube('Roof underlay',(side*2.32,.55,5.74),(5.36,6.65,.20),M['roof'],.02,rot=(0,side*pitch,0))
    # staggered individual slate bands; y moves along ridge direction
    for r in range(6):
        yy=-2.23+r*1.02
        for c in range(4):
            # x runs from near ridge to outer eave along the pitched roof
            along=.68+c*1.18
            x=side*(along*math.cos(pitch))
            z=6.0-along*math.sin(pitch)+.14
            tile=cube('Overlapping roof slate',(x,yy,z),(1.24,1.18,.12),M['roof2'] if (r+c)%4==0 else M['roof'],.018,rot=(0,side*pitch,0))
# ridge cap
cube('Roof ridge cap',(0,.55,6.13),(.42,6.86,.26),M['wooddark'],.03)

# chimney individual blockwork
for zrow in range(6):
    z=5.52+zrow*.42
    for yy in (1.45,1.83):
        x=1.64 + (.14 if (zrow+int(yy*10))%2 else -.08)
        cube('Chimney stone',(x,yy,z),(.64,.42,.38),M['stone2'],.035)
cube('Chimney crown',(1.65,1.65,8.08),(1.02,.88,.18),M['iron'],.025)

# warm porch lanterns
def lantern(name, loc):
    cube(name+' top',loc+Vector((0,0,.36)),(.34,.34,.10),M['iron'],.02)
    cube(name+' base',loc+Vector((0,0,-.36)),(.28,.28,.10),M['iron'],.02)
    cube(name+' glow',loc,(.23,.23,.55),M['lamp'],.015)
    for x in (-.14,.14): cube(name+' bars',loc+Vector((x,0,0)),(.035,.31,.68),M['iron'])
    for y in (-.14,.14): cube(name+' bars',loc+Vector((0,y,0)),(.31,.035,.68),M['iron'])
lantern('Porch lantern',Vector((-2.52,-3.02,2.48)))

# -----------------------------------------------------------------------------
# forest, rocks, shrubs and woodshed details
# -----------------------------------------------------------------------------
def pine(name,x,y,s=1):
    # keeping all trees angular and built from a brown trunk plus three cone crowns
    h=4.1*s
    cyl(name+' trunk',(x,y,h*.23),.29*s,h*.62,M['bark'],7)
    levels=[(.47,1.15,2.0),(.72,1.7,1.85),(1.03,2.3,1.7)]
    for idx,(zfac,r,dep) in enumerate(levels):
        cone(name+' crown '+str(idx),(x,y,h*zfac),r*s,.04*s,dep*s,[M['green2'],M['green1'],M['green3']][idx],6)

# background and framing pines (explicit locations retain a visible cabin clearing)
for i,(x,y,s) in enumerate([
    (-12,5,1.8),(-9,6,1.35),(-7,9,1.75),(-3,10,1.6),(2,10,1.6),(6,9,1.9),(10,8,1.75),(13,6,2.0),
    (-13,0,1.7),(-10,1.7,1.15),(-8,3.2,1.5),(9,3.5,2.1),(12,1,1.65),(14,-3,1.7),
    (-11,-3,1.5),(-10,-9,1.35),(10,-7,1.45),(13,-7,1.35),(-7,-11,1.15),(5,12,2.0)
]): pine('Low poly pine %02d'%i,x,y,s)

for i in range(44):
    x=random.uniform(-12.5,12.5); y=random.uniform(-9.5,8)
    # leave the central cabin / front path visually uncluttered
    if -5 < x < 6 and -6 < y < 5: continue
    ico('Angular shrub',(x,y,.42),random.uniform(.3,.72),M['bush'],(random.uniform(.75,1.3),random.uniform(.75,1.3),random.uniform(.75,1.1)))

# rock scatter including a few framing stones
for i in range(34):
    x=random.uniform(-11.5,11.5); y=random.uniform(-10,7)
    if -4.2 < x < 5.2 and -5.2 < y < 4.2: continue
    ico('Faceted granite stone',(x,y,.18),random.uniform(.18,.55),M['stone'],(random.uniform(.75,1.5),random.uniform(.75,1.35),random.uniform(.65,1.2)))
for x,y,s in [(-4.4,-3.1,.75),(-3.6,1.2,.95),(4.6,-4.8,.7),(5.2,-2.6,.5),(3.8,4.3,.8),(-5.5,-6.4,.58)]: ico('Clearing boulder',(x,y,.28),s,M['stone'],(1.2,.8,.8))

# grass tufts, each a tiny set of triangular blades
def grass_tuft(x,y,scale=1):
    for a in range(4):
        ang=a*1.55+random.uniform(-.15,.15)
        cone('Grass blade',(x+math.cos(ang)*.13*scale,y+math.sin(ang)*.13*scale,.16*scale),.06*scale,0,.43*scale,M['green3'],3,rot=(.20*math.sin(ang),.25*math.cos(ang),ang))
for x,y in [(-5,-4),(-4,-6),(-1.5,-6.5),(2.6,-5.8),(4,-4.1),(5.1,-5.2),(-4.7,2.2),(4.8,3.3),(1.6,-6.7),(6,-1.8),(-7,-3.5),(7.2,-6)]: grass_tuft(x,y,random.uniform(.7,1.25))

# wood pile and stump in right foreground
for row in range(3):
    for j in range(4-row%2):
        x=4.1+j*.68+row*.18; y=-5.35+row*.22; z=.35+row*.36
        cyl('Stacked firewood',(x,y,z),.17,.72,M['wooddark'],8,rot=(0,math.pi/2,0))
        # exposed cut end (simple orange cap)
        cyl('Cut log end',(x-.37,y,z),.175,.025,M['wood2'],8,rot=(0,math.pi/2,0))
cyl('Tree stump',(2.95,-6.0,.58),.52,1.1,M['wood2'],7)
cone('Stump cut face',(2.95,-6.0,1.14),.54,.54,.05,M['wood2'],7)
# axe leaning into stump
cube('Axe handle',(2.40,-5.65,1.18),(.12,.12,2.25),M['wood2'],.025,rot=(0,.45,-.38))
cube('Axe head',(2.05,-5.52,2.12),(.52,.18,.32),M['iron'],.025,rot=(0,.45,-.38))

# a few red-capped mushrooms
for i,(x,y) in enumerate([(5.9,-7.1),(6.35,-7.25),(-5.8,-5.4),(1.8,-7.7)]):
    cyl('Mushroom stem',(x,y,.18),.07,.32,M['cream'],7)
    cone('Red mushroom cap',(x,y,.40),.20,.05,.17,M['mushroom'],8)

# fence and path lantern to left
for x,y,ang in [(-6.7,-5.5,.12),(-7.9,-5.25,.12),(-9.1,-5.05,.12)]:
    cube('Rustic fence post',(x,y,.82),(.20,.20,1.55),M['wood2'],.025)
for y,z in [(-5.15,.86),(-5.55,.48)]: cube('Rustic fence rail',(-7.9,y,z),(2.8,.13,.14),M['wood2'],.02,rot=(0,0,.10))
cube('Path lantern post',(-6.6,-5.5,1.2),(.13,.13,2.1),M['wooddark'],.02)
lantern('Path lantern',Vector((-6.6,-5.5,1.82)))

# -----------------------------------------------------------------------------
# lighting, atmosphere, camera
# -----------------------------------------------------------------------------
# Large warm low-angle sun at upper left/front
bpy.ops.object.light_add(type='SUN', location=(-8,-10,14))
sun=bpy.context.object; sun.name='Golden hour sun'; sun.data.energy=2.2; sun.data.angle=math.radians(8); sun.data.color=(1.0,.70,.42)
sun.rotation_euler=(math.radians(28),math.radians(-18),math.radians(-28))
bpy.ops.object.light_add(type='AREA', location=(-4.5,-5,7))
fill=bpy.context.object; fill.name='Soft warm sky fill'; fill.data.energy=420; fill.data.shape='DISK'; fill.data.size=7; fill.data.color=(1.0,.68,.40); look_at(fill,(0,0,2.5))
bpy.ops.object.light_add(type='AREA', location=(3,1,5.6))
housefill=bpy.context.object; housefill.name='Window bounce'; housefill.data.energy=160; housefill.data.size=3; housefill.data.color=(1.0,.25,.035); look_at(housefill,(0,-2,2))

# hazy peach sky backdrop (world) and mist card far behind
scene.world.use_nodes=True
bg=scene.world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.28,.18,.095,1); bg.inputs['Strength'].default_value=.48

# camera composition: cabin fills frame with path leading in from lower left
bpy.ops.object.camera_add(location=(13.8,-24.8,10.8))
cam=bpy.context.object; cam.name='Hero cabin camera'; cam.data.lens=54; cam.data.sensor_width=36
look_at(cam,(0,-.15,3.05)); scene.camera=cam

# rendering-quality settings
scene.render.image_settings.color_mode='RGB'
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_percentage=100
scene.render.use_file_extension=True

bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath('//low_poly_woodland_cabin.blend'))
bpy.ops.render.render(write_still=True)
