import bpy
import math
import random
from mathutils import Vector

random.seed(560)

# -----------------------------------------------------------------------------
# Scene helpers
# -----------------------------------------------------------------------------

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    pass

def mat(name, color, rough=0.65, metallic=0.0, emission=None, strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metallic
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*emission, 1)
        bsdf.inputs['Emission Strength'].default_value = strength
    return m

M = {
    'ground': mat('Moss green', (0.22, 0.34, 0.10)),
    'ground2': mat('Fern green', (0.29, 0.42, 0.13)),
    'ground3': mat('Olive sun', (0.38, 0.46, 0.17)),
    'path': mat('Warm path', (0.57, 0.39, 0.22)),
    'path2': mat('Path light', (0.70, 0.49, 0.28)),
    'path3': mat('Path shadow', (0.43, 0.30, 0.19)),
    'wood': mat('Cabin honey wood', (0.38, 0.18, 0.065)),
    'woodlight': mat('Fresh cut wood', (0.56, 0.27, 0.08)),
    'wooddark': mat('Dark timber', (0.19, 0.085, 0.035)),
    'bark': mat('Bark', (0.22, 0.095, 0.035)),
    'roof1': mat('Roof charcoal', (0.145, 0.13, 0.12)),
    'roof2': mat('Roof brown', (0.22, 0.16, 0.125)),
    'roof3': mat('Roof slate', (0.12, 0.14, 0.15)),
    'stone': mat('Foundation stone', (0.28, 0.28, 0.29)),
    'stone2': mat('Stone light', (0.42, 0.40, 0.39)),
    'stone3': mat('Stone warm', (0.33, 0.30, 0.28)),
    'pine1': mat('Pine deep', (0.055, 0.16, 0.075)),
    'pine2': mat('Pine green', (0.10, 0.25, 0.10)),
    'pine3': mat('Pine sun', (0.25, 0.34, 0.105)),
    'glass': mat('Golden window', (1.0, 0.34, 0.035), rough=0.25, emission=(1.0, 0.18, 0.015), strength=7.0),
    'metal': mat('Black iron', (0.035, 0.028, 0.022), rough=0.4, metallic=0.65),
    'red': mat('Mushroom red', (0.72, 0.08, 0.025)),
    'cream': mat('Mushroom cream', (0.84, 0.68, 0.43)),
    'leaf': mat('Shrub green', (0.12, 0.31, 0.085)),
    'leaf2': mat('Shrub light', (0.24, 0.42, 0.09)),
    'mountain': mat('Distant warm rock', (0.48, 0.43, 0.36)),
    'mountain2': mat('Distant pale rock', (0.61, 0.54, 0.45)),
}

def set_mat(obj, material):
    obj.data.materials.append(material)
    return obj

def cube(name, loc, scale, material, rot=(0,0,0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (scale[0]/2, scale[1]/2, scale[2]/2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    set_mat(o, material)
    if bevel:
        mod = o.modifiers.new('Soft hewn edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    return o

def cyl(name, loc, radius, depth, material, vertices=10, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object; o.name=name; set_mat(o, material); return o

def ico(name, loc, scale, material, subdivisions=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    set_mat(o,material); return o

def cone(name, loc, r1, r2, depth, material, vertices=7):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=r1, radius2=r2, depth=depth, location=loc)
    o=bpy.context.object; o.name=name; set_mat(o, material); return o

def beam_between(name, a, b, width, material, bevel=0.03):
    a,b=Vector(a),Vector(b); d=b-a
    o=cube(name,(a+b)/2,(width,width,d.length),material,bevel=bevel)
    o.rotation_mode='QUATERNION'; o.rotation_quaternion=d.to_track_quat('Z','Y')
    return o

def point_light(name, loc, color=(1,.25,.05), energy=100, radius=.3):
    d=bpy.data.lights.new(name,'POINT'); d.energy=energy; d.color=color; d.shadow_soft_size=radius
    o=bpy.data.objects.new(name,d); bpy.context.collection.objects.link(o); o.location=loc; return o

# -----------------------------------------------------------------------------
# Faceted terrain and path
# -----------------------------------------------------------------------------

N=18; step=2.1; half=N*step/2
verts=[]
for j in range(N+1):
    y=-half+j*step
    for i in range(N+1):
        x=-half+i*step
        z=-0.25 + 0.035*abs(x) + 0.018*(y+8) + random.uniform(-.18,.18)
        verts.append((x,y,z))
faces=[]; mids=[]
for j in range(N):
    for i in range(N):
        a=j*(N+1)+i; b=a+1; c=a+(N+1); d=c+1
        if (i+j)%2: faces.extend([(a,b,c),(b,d,c)])
        else: faces.extend([(a,b,d),(a,d,c)])
mesh=bpy.data.meshes.new('Triangulated meadow mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.clear()
for mm in (M['ground'],M['ground2'],M['ground3']): mesh.materials.append(mm)
ground=bpy.data.objects.new('Low polygon meadow',mesh); bpy.context.collection.objects.link(ground)
for p in ground.data.polygons:
    p.material_index=random.choices([0,1,2],[5,3,1])[0]

# broad triangulated path ribbon, then irregular overlapping flat low-poly stones
path_pts=[(-5.2,-14.5),(-4.3,-12.3),(-3.3,-10.2),(-3.1,-8.1),(-2.0,-6.3),(-1.2,-4.7),(-.6,-3.4)]
path_verts=[]
for idx,(x,y) in enumerate(path_pts):
    if idx==0: tangent=Vector(path_pts[1])-Vector(path_pts[0])
    elif idx==len(path_pts)-1: tangent=Vector(path_pts[-1])-Vector(path_pts[-2])
    else: tangent=Vector(path_pts[idx+1])-Vector(path_pts[idx-1])
    tangent.normalize(); perp=Vector((-tangent.y,tangent.x))
    width=2.25-idx*.12
    path_verts.extend([(x+perp.x*width/2,y+perp.y*width/2,.07),(x-perp.x*width/2,y-perp.y*width/2,.07)])
path_faces=[]
for i in range(len(path_pts)-1):
    a=i*2; path_faces.extend([(a,a+1,a+2),(a+1,a+3,a+2)])
pm=bpy.data.meshes.new('Triangulated winding path mesh'); pm.from_pydata(path_verts,[],path_faces)
for mm in (M['path'],M['path2'],M['path3']): pm.materials.append(mm)
po=bpy.data.objects.new('Winding forest path',pm); bpy.context.collection.objects.link(po)
for poly in po.data.polygons: poly.material_index=random.choices([0,1,2],[4,2,2])[0]

for idx,(x,y) in enumerate(path_pts):
    for k in range(3):
        xx=x+(k-2)*.42+random.uniform(-.18,.18)
        yy=y+random.uniform(-.7,.7)
        bpy.ops.mesh.primitive_cylinder_add(vertices=random.choice([5,6,7]), radius=random.uniform(.58,.85), depth=.06,
            location=(xx,yy,.05), rotation=(0,0,random.random()*math.pi))
        o=bpy.context.object; o.name='Path stone'; o.scale=(1.25,.75,1); set_mat(o, random.choice([M['path'],M['path2'],M['path3']]))

# -----------------------------------------------------------------------------
# Cabin foundation, walls, porch
# -----------------------------------------------------------------------------

CX,CY=1.2,0.5
wall_bottom=.7; wall_top=5.0

# stone foundation blocks around visible front and right side
for y in [-2.55,3.55]:
    for x in [CX-3.4+i*.85 for i in range(9)]:
        cube('Foundation block',(x,y,.55),(.78,.55,.62),random.choice([M['stone'],M['stone2'],M['stone3']]),bevel=.07)
for x in [CX-3.45,CX+3.45]:
    for y in [CY-2.5+i*.78 for i in range(8)]:
        cube('Foundation block',(x,y,.55),(.55,.71,.62),random.choice([M['stone'],M['stone2'],M['stone3']]),bevel=.07)

# dark backing walls
cube('Cabin front wall',(CX,CY-2.55,2.9),(6.7,.35,4.4),M['wooddark'])
cube('Cabin right wall',(CX+3.35,CY+.45,2.9),(.35,5.9,4.4),M['wooddark'])
cube('Cabin left wall',(CX-3.35,CY+.45,2.9),(.35,5.9,4.4),M['wooddark'])
cube('Cabin rear wall',(CX,CY+3.45,2.9),(6.7,.35,4.4),M['wooddark'])

# horizontal log courses
for zi,z in enumerate([1.05+i*.48 for i in range(9)]):
    jitter=random.uniform(-.025,.025)
    cube('Front hewn log',(CX,CY-2.79,z),(6.85,.42,.40),random.choice([M['wood'],M['woodlight']]),bevel=.07)
    cube('Right hewn log',(CX+3.58,CY+.45,z),(.42,6.05,.40),random.choice([M['wood'],M['woodlight']]),bevel=.07)
    cube('Left hewn log',(CX-3.58,CY+.45,z),(.42,6.05,.40),M['wood'],bevel=.07)

# corner dovetail ends
for z in [1.0+i*.48 for i in range(9)]:
    for x in [CX-3.62,CX+3.62]:
        cube('Corner log end',(x,CY-2.84,z),(.62,.72,.34),M['woodlight'],bevel=.06)

# gable triangle mesh
gv=[(CX-3.36,CY-2.77,4.82),(CX+3.36,CY-2.77,4.82),(CX,CY-2.77,7.2)]
gm=bpy.data.meshes.new('Front gable mesh'); gm.from_pydata(gv,[],[(0,1,2)]); gm.materials.append(M['wooddark'])
go=bpy.data.objects.new('Front timber gable',gm); bpy.context.collection.objects.link(go)

# gable horizontal boards
for i,z in enumerate([5.05,5.42,5.79,6.16,6.53]):
    halfw=max(.5,3.1-(z-4.9)*1.35)
    cube('Gable board',(CX,CY-2.87,z),(halfw*2,.24,.30),M['wood'],bevel=.04)

# structural gable beams
beam_between('Left gable fascia',(CX-3.7,CY-3.04,4.72),(CX,CY-3.04,7.43),.28,M['woodlight'],.045)
beam_between('Right gable fascia',(CX+3.7,CY-3.04,4.72),(CX,CY-3.04,7.43),.28,M['woodlight'],.045)
cube('Gable tie beam',(CX,CY-3.03,4.86),(7.25,.34,.34),M['woodlight'],bevel=.055)

# door
cube('Door slab',(CX-.75,CY-3.05,2.38),(1.55,.22,2.95),M['woodlight'],bevel=.05)
for x in [CX-1.38,CX-.88,CX-.38]: cube('Door vertical board',(x,CY-3.18,2.38),(.07,.05,2.8),M['wooddark'])
cube('Door top trim',(CX-.75,CY-3.18,3.92),(1.95,.28,.24),M['woodlight'],bevel=.04)
cube('Door left trim',(CX-1.62,CY-3.18,2.42),(.25,.28,3.25),M['woodlight'],bevel=.04)
cube('Door right trim',(CX+.12,CY-3.18,2.42),(.25,.28,3.25),M['woodlight'],bevel=.04)
cyl('Door knob',(CX-.18,CY-3.32,2.35),.07,.12,M['metal'],vertices=12,rot=(math.pi/2,0,0))

def window_front(name,x,z,w=1.35,h=1.45,y=CY-3.13):
    cube(name+' glow',(x,y,z),(w,.08,h),M['glass'])
    cube(name+' sill',(x,y-.08,z-h/2-.10),(w+0.45,.28,.22),M['woodlight'],bevel=.035)
    cube(name+' top',(x,y-.08,z+h/2+.10),(w+0.45,.28,.22),M['woodlight'],bevel=.035)
    for xx in [x-w/2-.12,x+w/2+.12,x]: cube(name+' frame',(xx,y-.09,z),(.18,.25,h+0.35),M['wooddark'],bevel=.025)
    cube(name+' cross',(x,y-.1,z),(w+.25,.25,.14),M['wooddark'])
    point_light(name+' warm spill',(x,y-.55,z),energy=45,radius=.45)

window_front('Gable window',CX,5.86,.95,1.15)

def window_side(name,y,z,w=1.30,h=1.45,x=CX+3.77):
    cube(name+' glow',(x,y,z),(.08,w,h),M['glass'])
    cube(name+' sill',(x+.08,y,z-h/2-.1),(.28,w+.42,.22),M['woodlight'],bevel=.035)
    cube(name+' top',(x+.08,y,z+h/2+.1),(.28,w+.42,.22),M['woodlight'],bevel=.035)
    for yy in [y-w/2-.12,y+w/2+.12,y]: cube(name+' frame',(x+.09,yy,z),(.25,.18,h+.35),M['wooddark'],bevel=.025)
    cube(name+' cross',(x+.10,y,z),(.25,w+.25,.14),M['wooddark'])
    point_light(name+' warm spill',(x+.65,y,z),energy=55,radius=.5)

window_side('Side window A',-.2,2.65)
window_side('Side window B',2.05,2.65,1.1,1.35)

# roof under-panels and individually varied shingles
slope=math.atan2(2.65,4.05)
for side in [-1,1]:
    rotY=side*slope
    xmid=CX-side*2.0
    cube('Roof underlay',(xmid,CY+.25,6.0),(4.95,7.2,.23),M['roof1'],rot=(0,rotY,0))
    for row in range(8):
        y=CY-2.55+row*.83
        for col in range(4):
            # center distance out from ridge in world x
            dist=.55+col*1.03 + (row%2)*.11
            x=CX-side*dist
            z=7.28-dist*math.tan(slope)+random.uniform(-.025,.025)
            yy=y+random.uniform(-.018,.018)
            tile=cube('Hand-laid roof shingle',(x,yy,z),(1.18,.91,.10),random.choice([M['roof1'],M['roof2'],M['roof3']]),rot=(0,rotY,0),bevel=.018)

# ridge cap
beam_between('Roof ridge',(CX,CY-3.25,7.45),(CX,CY+3.8,7.45),.24,M['roof2'],.035)

# chimney with block pattern
for row,z in enumerate([6.45,6.87,7.29,7.71,8.13]):
    for ix in range(2):
        for iy in range(2):
            x=CX+1.75+(ix-.5)*.43 + (row%2)*.06
            y=CY+1.4+(iy-.5)*.43
            cube('Chimney stone',(x,y,z),(.48,.48,.38),random.choice([M['stone'],M['stone2'],M['stone3']]),bevel=.035)
cube('Chimney cap',(CX+1.78,CY+1.4,8.38),(1.25,1.0,.18),M['stone'],bevel=.04)

# porch deck and stairs
cube('Porch base',(CX-1.0,CY-3.75,.85),(6.6,2.0,.34),M['stone'])
for i in range(9): cube('Porch floor plank',(CX-3.75+i*.68,CY-3.78,1.08),(.58,1.75,.16),M['woodlight'],bevel=.035)
for s in range(3):
    cube('Front step',(CX-1.0,CY-5.0-s*.34,.86-s*.24),(2.35,.55,.24),M['woodlight'],bevel=.035)

# porch posts/rails; leave center stair opening
for x in [CX-4.05,CX-2.35,CX+.45,CX+2.3]:
    cube('Porch post',(x,CY-4.6,1.75),(.26,.26,1.55),M['woodlight'],bevel=.035)
for xa,xb in [(CX-4.05,CX-2.35),(CX+.45,CX+2.3)]:
    beam_between('Porch rail',(xa,CY-4.6,1.75),(xb,CY-4.6,1.75),.18,M['woodlight'])
    for x in [xa+.42,xa+.84,xa+1.26]: beam_between('Porch baluster',(x,CY-4.6,1.12),(x,CY-4.6,1.75),.11,M['woodlight'])
for side_x in [CX-4.05,CX+2.3]:
    beam_between('Side porch rail',(side_x,CY-4.55,1.75),(side_x,CY-3.05,1.75),.18,M['woodlight'])

# -----------------------------------------------------------------------------
# Lantern, barrel, fence
# -----------------------------------------------------------------------------

def lantern(name,loc,scale=1.0, hanging=False):
    x,y,z=loc
    cube(name+' base',(x,y,z),(.52*scale,.52*scale,.14*scale),M['metal'],bevel=.03)
    cube(name+' glow',(x,y,z+.42*scale),(.38*scale,.38*scale,.62*scale),M['glass'],bevel=.03)
    cube(name+' top',(x,y,z+.78*scale),(.55*scale,.55*scale,.16*scale),M['metal'],bevel=.03)
    for dx in [-.23,.23]:
        for dy in [-.23,.23]: beam_between(name+' bar',(x+dx*scale,y+dy*scale,z+.08*scale),(x+dx*scale,y+dy*scale,z+.78*scale),.05*scale,M['metal'])
    point_light(name+' light',(x,y,z+.42*scale),energy=70*scale,radius=.25*scale)

lantern('Door lantern',(CX-2.0,CY-3.33,3.15),.62)
cyl('Barrel',(-1.7,-3.52,1.62),.45,1.05,M['bark'],vertices=12)
for z in [1.2,1.72,2.05]:
    bpy.ops.mesh.primitive_torus_add(major_radius=.43,minor_radius=.035,major_segments=12,minor_segments=5,location=(-1.7,-3.52,z)); set_mat(bpy.context.object,M['metal'])

# rustic fence on left
for x,y in [(-9,-6.7),(-6.8,-7.0),(-4.8,-7.15),(-9.4,-9.5),(-7.2,-9.7)]:
    cube('Fence post',(x,y,1.05),(.35,.35,2.1),M['woodlight'],rot=(0,random.uniform(-.08,.08),random.uniform(-.07,.07)),bevel=.05)
beam_between('Fence rail',(-9,-6.7,1.35),(-4.8,-7.15,1.45),.22,M['woodlight'])
beam_between('Fence lower rail',(-9,-6.7,.72),(-4.8,-7.15,.78),.18,M['wood'])
beam_between('Fence back rail',(-9.4,-9.5,1.3),(-7.2,-9.7,1.35),.22,M['woodlight'])
lantern('Fence lantern',(-6.75,-7.13,1.05),.7)

# -----------------------------------------------------------------------------
# Trees, mountains, shrubs, stones
# -----------------------------------------------------------------------------

def pine(name,x,y,h,green=None,stages=3):
    green=green or random.choice([M['pine1'],M['pine2'],M['pine3']])
    base=-.05
    cyl(name+' trunk',(x,y,base+h*.22),h*.09,h*.48,M['bark'],vertices=8)
    for i in range(stages):
        frac=i/(stages-1) if stages>1 else 0
        z=base+h*(.30+frac*.24)
        rad=h*(.25-frac*.052)
        dep=h*.34
        cone(name+' crown',(x,y,z),rad,0,dep,green,vertices=7)
    cone(name+' top',(x,y,base+h*.78),h*.15,0,h*.45,green,vertices=7)

# background mountains
for i,(x,y,z,s) in enumerate([
    (-15,19,10,9),(-8,21,11,11),(-1,23,12,12),(7,22,13,13),(15,21,11,11),(23,23,13,14)
]):
    ico('Faceted mountain',(x,y,z),(s,4.3,s*.75),random.choice([M['mountain'],M['mountain2']]),1)

# mid/background pines, avoid cabin silhouette center foreground
tree_data=[
(-12,8,10),(-9,12,8),(-6,8,12),(-3,12,10),(1,13,12),(5,11,10),(9,12,13),(13,9,11),(16,11,13),
(-15,3,8),(-11,2,11),(-7,4,9),(-5,1,12),(7,5,9),(10,4,12),(13,2,10),(17,4,13),
(-15,-3,8),(-11,-2,9),(-8,-3,7),(10,-2,12),(14,-3,15),(18,-2,11),
(-17,-9,11),(17,-9,13),(20,-7,12)
]
for i,(x,y,h) in enumerate(tree_data): pine('Pine %02d'%i,x,y,h)

# foreground framing trees
pine('Hero left pine',-11.5,-7.0,9.5,M['pine2'])
pine('Hero right pine',14.8,-1.0,15.5,M['pine1'])
pine('Near right crop',21,-10,17,M['pine3'])
pine('Near left crop',-20,-12,15,M['pine1'])

# rocks
for i in range(30):
    x=random.uniform(-12,13); y=random.uniform(-11,7)
    if (-3.2 < x < 5.3 and -5.5 < y < 4): continue
    s=random.uniform(.25,.72)
    ico('Angular rock',(x,y,s*.35),(s,s*.82,s*.65),random.choice([M['stone'],M['stone2'],M['stone3']]),1)

# shrub clusters
for base_x,base_y in [(-3.8,-2.4),(5.3,-3.0),(6.5,-1.9),(7.2,1.4),(-4.6,-.7),(8,-5),(-1,-6.0)]:
    for k in range(random.randint(3,6)):
        x=base_x+random.uniform(-.8,.8); y=base_y+random.uniform(-.7,.7)
        s=random.uniform(.45,.85)
        ico('Faceted shrub',(x,y,.35+s*.25),(s,s*.8,s*.65),random.choice([M['leaf'],M['leaf2']]),1)

# grass tufts (simple triangular blade beams)
for i in range(45):
    x=random.uniform(-11,12); y=random.uniform(-11,6)
    if (-3<x<5 and -5<y<3): continue
    for k in range(3):
        beam_between('Grass blade',(x,y,.05),(x+random.uniform(-.22,.22),y+random.uniform(-.12,.12),random.uniform(.38,.7)),.045,random.choice([M['pine2'],M['ground3']]),0)

# mushrooms
for x,y,s in [(-4.7,-4.9,.42),(7.9,-7.9,.48),(9.0,-8.6,.32),(-1.8,-7.3,.32),(5.6,-4.8,.24)]:
    cyl('Mushroom stem',(x,y,.18*s/.42),.10*s/.42,.36*s/.42,M['cream'],vertices=8)
    cone('Mushroom cap',(x,y,.43*s/.42),.31*s/.42,.08*s/.42,.20*s/.42,M['red'],vertices=10)

# stump, axe and log pile at right foreground
stx,sty=6.4,-7.2
cyl('Chopping stump',(stx,sty,1.0),.8,1.8,M['bark'],vertices=11)
cyl('Stump cut face',(stx,sty,1.93),.68,.07,M['woodlight'],vertices=11)
beam_between('Axe handle',(stx-.2,sty-.05,1.9),(stx-2.0,sty-1.2,.45),.13,M['woodlight'])
axe=cube('Axe head',(stx-.18,sty-.05,2.0),(.65,.18,.42),M['metal'],rot=(0,.3,.2),bevel=.05)

for row in range(3):
    for col in range(4-row):
        x=8.0+col*.72+row*.3; y=-7.1; z=.38+row*.52
        cyl('Firewood log',(x,y,z),.28,2.1,M['bark'],vertices=9,rot=(math.pi/2,0,0))
        cyl('Firewood cut',(x,y-1.07,z),.24,.05,M['woodlight'],vertices=9,rot=(math.pi/2,0,0))
beam_between('Woodpile side rail',(7.65,-8.2,.15),(10.75,-6.8,1.55),.16,M['wood'])
beam_between('Woodpile side rail',(7.65,-6.0,.15),(10.75,-7.4,1.55),.16,M['wood'])

# -----------------------------------------------------------------------------
# Lighting, camera, render
# -----------------------------------------------------------------------------

world=bpy.context.scene.world or bpy.data.worlds.new('World')
bpy.context.scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.14,0.18,0.13,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.72

sun_data=bpy.data.lights.new('Warm low sun','SUN'); sun_data.energy=2.15; sun_data.color=(1.0,.64,.34); sun_data.angle=math.radians(12)
sun=bpy.data.objects.new('Warm low sun',sun_data); bpy.context.collection.objects.link(sun); sun.rotation_euler=(math.radians(28),math.radians(-18),math.radians(-38))
area_data=bpy.data.lights.new('Sky fill','AREA'); area_data.energy=1100; area_data.color=(.38,.52,.72); area_data.shape='DISK'; area_data.size=12
area=bpy.data.objects.new('Sky fill',area_data); bpy.context.collection.objects.link(area); area.location=(-7,-4,16); area.rotation_euler=(0,0,0)

# warm bounce by cabin facade
area2_data=bpy.data.lights.new('Cabin warm bounce','AREA'); area2_data.energy=180; area2_data.color=(1.0,.34,.09); area2_data.shape='RECTANGLE'; area2_data.size=5
area2=bpy.data.objects.new('Cabin warm bounce',area2_data); bpy.context.collection.objects.link(area2); area2.location=(-4,-9,6)
target=Vector((1,-1,3)); area2.rotation_euler=(target-Vector(area2.location)).to_track_quat('-Z','Y').to_euler()

cam_data=bpy.data.cameras.new('Camera'); cam=bpy.data.objects.new('Camera',cam_data); bpy.context.collection.objects.link(cam)
cam.location=(19.5,-30.5,13.5); target=Vector((.4,-1.6,2.55)); cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
cam.data.lens=53; cam.data.sensor_width=36; cam.data.dof.use_dof=True; cam.data.dof.focus_object=go; cam.data.dof.aperture_fstop=3.6
bpy.context.scene.camera=cam

scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1280; scene.render.resolution_y=720; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGBA'
scene.render.film_transparent=False
scene.render.image_settings.color_depth='8'
scene.render.filepath='/home/ralf/prj/exploration/blender-benchmark/gpt-5.6-sol-high/final_render.png'
scene.render.resolution_percentage=100
scene.render.use_file_extension=True
scene.render.image_settings.color_mode='RGB'
scene.view_settings.look='AgX - Medium High Contrast'

# mist-like warm backdrop plane
cube('Distant backdrop',(0,27,7),(50,.5,28),mat('Sunset haze',(0.68,.48,.31),rough=1.0))

# Organize by object naming and save
bpy.ops.wm.save_as_mainfile(filepath='/home/ralf/prj/exploration/blender-benchmark/gpt-5.6-sol-high/cabin_forest.blend')
bpy.ops.render.render(write_still=True)
print('DONE: cabin_forest.blend and final_render.png')
