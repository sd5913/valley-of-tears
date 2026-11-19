from pathlib import Path
import bpy
import math
import random
from mathutils import Vector, noise

random.seed(731)
OUT = str(Path(__file__).resolve().parent)
scene = bpy.data.scenes.new('VALLEY OF TEARS | The Weeping Wardens')
bpy.context.window.scene = scene
groups = {}
for name in ['01 | Landforms', '02 | River and falling tears', '03 | The Weeping Wardens', '04 | Pilgrim bridge', '05 | Forgotten sanctuary', '06 | Trees and memorials', '07 | Atmosphere', '08 | Cameras and light']:
    col = bpy.data.collections.new(name)
    scene.collection.children.link(col)
    groups[name[:2]] = col

def mesh(name, verts, faces, mat, group='01', smooth=False):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    groups[group].objects.link(obj)
    if mat:
        data.materials.append(mat)
    if smooth:
        for p in data.polygons:
            p.use_smooth = True
    return obj

def move(obj, group, name, mat=None):
    obj.name = name
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    groups[group].objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    return obj

def material(name, color, roughness=.65, metallic=0, emission=None):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metallic
    if emission:
        p.inputs['Emission Color'].default_value = (*color, 1)
        p.inputs['Emission Strength'].default_value = emission
    return m

def rock_material(name, low, high, scale=1):
    m = material(name, low, .83)
    nt = m.node_tree
    p = nt.nodes.get('Principled BSDF')
    tex = nt.nodes.new('ShaderNodeTexCoord')
    n = nt.nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value = .23 * scale
    n.inputs['Detail'].default_value = 5
    n.inputs['Roughness'].default_value = .73
    nt.links.new(tex.outputs['Object'], n.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = .21
    ramp.color_ramp.elements[0].color = (*low, 1)
    ramp.color_ramp.elements[1].position = .78
    ramp.color_ramp.elements[1].color = (*high, 1)
    nt.links.new(n.outputs['Fac'], ramp.inputs[0])
    nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    fine = nt.nodes.new('ShaderNodeTexNoise')
    fine.inputs['Scale'].default_value = 4.2 * scale
    fine.inputs['Detail'].default_value = 3
    nt.links.new(tex.outputs['Object'], fine.inputs['Vector'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .58
    bump.inputs['Distance'].default_value = .21 / scale
    nt.links.new(fine.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], p.inputs['Normal'])
    return m

rock = rock_material('Basalt | rain-darkened striated stone', (.045,.075,.083), (.25,.32,.29))
stone = rock_material('Wardens | weathered pale limestone', (.15,.21,.21), (.52,.57,.48), 1.3)
oldstone = rock_material('Sanctuary | ancient chalk and lichen', (.16,.20,.16), (.43,.44,.32), 2)
moss = rock_material('Moss | deep velvet green', (.018,.047,.025), (.13,.21,.075), 2)
bark = rock_material('Trees | charcoal bark', (.018,.028,.028), (.095,.13,.12), 3)
leaves = [material('Foliage | silver sage',(.18,.26,.20)), material('Foliage | dusk olive',(.075,.14,.09)),material('Foliage | pale lichen',(.32,.39,.26))]
dark = material('Carved recesses', (.008,.017,.020), .94)
gold = material('Old brass', (.34,.19,.055), .33, .72)
glow = material('Lanterns | warm living flame', (1,.35,.065), .3, emission=8)
waterfallmat = material('Tears | aerated silver water',(.36,.72,.74),.23,.28,emission=.24)
foam = material('Tears | white foam',(.52,.79,.78),.4,emission=.18)
river = material('River | deep glacial jade',(.018,.105,.113),.17,.57)
nt=river.node_tree
p=nt.nodes.get('Principled BSDF')
p.inputs['IOR'].default_value=1.333
coord=nt.nodes.new('ShaderNodeTexCoord')
mapping=nt.nodes.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'
mapping.inputs[1].default_value=(1.1,6,2)
nt.links.new(coord.outputs['Object'],mapping.inputs[0])
n=nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=1.7; n.inputs['Detail'].default_value=3
nt.links.new(mapping.outputs[0],n.inputs['Vector'])
b=nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value=.23; b.inputs['Distance'].default_value=.12
nt.links.new(n.outputs['Fac'],b.inputs['Height']); nt.links.new(b.outputs['Normal'],p.inputs['Normal'])

def nv(x,y,z=0):
    return noise.noise_vector(Vector((x,y,z)))[0]

def riverx(y):
    return 5*math.sin(y*.037)+3*math.sin(y*.071+.7)

def landz(x,y):
    d=abs(x-riverx(y))
    widening=4*math.exp(-((y+32)/42)**2)
    bank=11+widening
    bank+=(21*math.exp(-((y-39)/13)**4) if x<riverx(y) else 12*math.exp(-((y-77)/14)**4))
    detail=nv(x*.19,y*.19,4)*.65+nv(x*.65,y*.65,5)*.18
    if d<bank:
        return -1.2+detail*.25
    if d<bank+9:
        return .3+(d-bank)*.24+detail
    h=29+10*math.sin(y*.045)+7*math.sin(y*.11+1)+9*nv(x*.032,y*.035,9)
    return 2.5+(1-math.exp(-(d-bank-9)/7))*h+detail*2+5*nv(x*.09,y*.065,7)

verts=[]; faces=[]
nx,ny=220,360
for j in range(ny+1):
    y=-95+j*340/ny
    for i in range(nx+1):
        x=-110+i*220/nx
        verts.append((x,y,landz(x,y)))
for j in range(ny):
    for i in range(nx):
        a=j*(nx+1)+i
        faces.append((a,a+1,a+nx+2,a+nx+1))
mesh('The eroded gorge | continuous sculpted terrain',verts,faces,rock,smooth=True)

def crag(name,x,y,z,rx,ry,height,mat=rock,group='01',seed=0):
    rng=random.Random(seed)
    segs,layers=18,22
    phase=[rng.uniform(-.14,.14) for _ in range(segs)]
    vs=[]; fs=[]
    for j in range(layers+1):
        t=j/layers
        taper=(1-.35*t)*(1+.065*math.sin(t*58)+.06*math.sin(t*113))
        for i in range(segs):
            a=2*math.pi*i/segs
            r=taper*(1+phase[i]+.07*math.sin(t*27+i*4))
            zz=z+t*height+(.7*math.sin(i*2.7)+1.2*math.sin(i*.9))*(t**3)
            vs.append((x+rx*r*math.cos(a)+math.sin(t*3)*1.5,y+ry*r*math.sin(a),zz))
    for j in range(layers):
        for i in range(segs):
            a=j*segs+i; b=j*segs+(i+1)%segs
            fs.append((a,b,b+segs,a+segs))
    fs.append(tuple(range(layers*segs,(layers+1)*segs)))
    return mesh(name,vs,fs,mat,group)

for side in [-1,1]:
    for k in range(18):
        y=-8+k*11+random.uniform(-5,5)
        x=riverx(y)+side*random.uniform(31,53)
        crag('Columnar canyon buttress %s.%02d'%(side,k),x,y,random.uniform(2,8),random.uniform(6,13),random.uniform(7,15),random.uniform(32,66),seed=k+100*(side+1))

# A broad connected water surface catches the cliff and sky reflections.
vs=[];fs=[]
for j in range(381):
    y=-105+j*.88
    width=55
    for i in range(19):
        x=riverx(y)+(i/18*2-1)*width
        z=.06+.022*math.sin(x*2+y*3)+.014*math.sin(y*6-x)
        vs.append((x,y,z))
for j in range(380):
    for i in range(18):
        a=j*19+i;fs.append((a,a+1,a+20,a+19))
mesh('River of remembrance | winding reflective water',vs,fs,river,'02',True)

def curve(name, points, radius, mat, group='02', radii=None):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=10
    cu.bevel_depth=radius;cu.bevel_resolution=2
    sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
    for k,co in enumerate(points):
        sp.points[k].co=(*co,1)
        if radii:sp.points[k].radius=radii[k]
    ob=bpy.data.objects.new(name,cu);groups[group].objects.link(ob);cu.materials.append(mat)
    return ob

def ico(name, loc, scale, mat, group='01',sub=2):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=loc)
    ob=move(bpy.context.object,group,name,mat);ob.scale=scale
    return ob

def cube(name,loc,scale,mat,group='04',bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    ob=move(bpy.context.object,group,name,mat)
    for v in ob.data.vertices:
        v.co.x*=scale[0];v.co.y*=scale[1];v.co.z*=scale[2]
    if bevel:
        mod=ob.modifiers.new('Eroded stone edges','BEVEL');mod.width=bevel;mod.segments=2
    return ob

def head_surface(x,z,rx,rz):
    q=max(.012,1-(x/rx)**2-(z/rz)**2)
    yy=-4.5*math.sqrt(q)
    yy-=2.25*math.exp(-(x/1.1)**2-((z-.1)/4.3)**2)
    yy-=.9*math.exp(-(x/1.7)**2-((z+1.8)/1)**2)
    for sx in [-1,1]:
        yy+=.8*math.exp(-((x-sx*2.8)/1.65)**2-((z-3.1)/1.1)**2)
        yy-=.65*math.exp(-((x-sx*3.5)/2)**2-((z+1.4)/2.6)**2)
        yy-=.7*math.exp(-((x-sx*2.8)/2)**2-((z-4.5)/.7)**2)
    yy+=.65*math.exp(-(x/2.7)**4-((z+4.4)/.28)**2)
    yy-=.7*math.exp(-(x/2.6)**2-((z+7.6)/2.2)**2)
    return yy

def waterfall(name,top,bottom,width):
    vs=[];fs=[]
    N,W=100,7
    for j in range(N+1):
        t=j/N
        z=top[2]*(1-t)+bottom[2]*t
        cy=top[1]*(1-t)+bottom[1]*t-.6*math.sin(math.pi*t)
        cx=top[0]*(1-t)+bottom[0]*t+.09*math.sin(t*32)
        w=width*(.65+.6*t+.13*math.sin(t*65))
        for i in range(W+1):
            u=i/W*2-1
            vs.append((cx+u*w,cy+.06*math.sin(t*150+i*2)+.1*u*u,z))
    for j in range(N):
        for i in range(W):
            a=j*(W+1)+i;fs.append((a,a+1,a+W+2,a+W+1))
    ob=mesh(name,vs,fs,waterfallmat,'02',True)
    for k in range(6):
        dx=random.uniform(-.8,.8)*width
        points=[]
        for j in range(65):
            t=j/64
            points.append((top[0]*(1-t)+bottom[0]*t+dx+.045*math.sin(t*83+k),top[1]*(1-t)+bottom[1]*t-.6*math.sin(math.pi*t)-.06,top[2]*(1-t)+bottom[2]*t))
        curve(name+' | falling silver filament',points,random.uniform(.013,.032),foam)
    for k in range(6):
        r=.6+k*.45
        pts=[(bottom[0]+r*math.cos(a*2*math.pi/80),bottom[1]+r*.65*math.sin(a*2*math.pi/80),.13+random.random()*.025) for a in range(81)]
        curve('Impact | spreading ripple',pts,.018*(1-k*.09),foam)
    return ob

for idx,(cx,cy,cz,sc) in enumerate([(-19,47,27,1),(25,86,33,1.12)]):
    rx,rz=7.4*sc,13.2*sc
    vs=[];fs=[]
    nlon,nlat=112,100
    for j in range(nlat+1):
        th=.004+(math.pi-.008)*j/nlat
        for i in range(nlon):
            ph=2*math.pi*i/nlon
            x=rx*math.sin(th)*math.cos(ph)
            z=rz*math.cos(th)
            if math.sin(ph)<0:
                y=head_surface(x/sc,z/sc,7.4,13.2)*sc
            else:
                y=5.0*sc*math.sin(th)*math.sin(ph)
            weather=.1*nv(x*1.8,z*1.8,idx+7)+.08*nv(x*5,z*5,5)
            vs.append((cx+x,cy+y+weather,cz+z))
    for j in range(nlat):
        for i in range(nlon):
            a=j*nlon+i;b=j*nlon+(i+1)%nlon
            fs.append((a,b,b+nlon,a+nlon))
    mesh('Warden %d | sculpted face of the mourner'%(idx+1),vs,fs,stone,'03',True)
    crag('Warden %d | rock-cut mantle'%(idx+1),cx,cy+4,0,10*sc,7*sc,cz+13*sc,rock,'03',idx+500)
    # Closed eyes and a downturned mouth are cut as deep, narrow dark seams.
    for s in [-1,1]:
        pts=[]
        for k in range(35):
            x=s*2.8+(k/34-.5)*2.7
            z=3.1-.23*math.sin(k/34*math.pi)
            pts.append((cx+x*sc,cy+head_surface(x,z,7.4,13.2)*sc-.085,cz+z*sc))
        curve('Warden | closed eye',pts,.11*sc,dark,'03')
        ex=s*2.7
        top=(cx+ex*sc,cy+head_surface(ex,2.8,7.4,13.2)*sc-.14,cz+2.8*sc)
        bottom=(cx+ex*sc+(.35 if s>0 else -.35),cy-7.2*sc,.15)
        waterfall('Warden %d | tear %s'%(idx+1,s),top,bottom,.28*sc)
    pts=[]
    for k in range(45):
        x=(k/44-.5)*4.9;z=-4.3-.48*(abs(x)/2.45)**1.3
        pts.append((cx+x*sc,cy+head_surface(x,z,7.4,13.2)*sc-.06,cz+z*sc))
    curve('Warden | sorrowful mouth',pts,.085*sc,dark,'03')
    # Fractures run through the brow and crown, following the stone surface.
    for side in [-1,1]:
        pts=[]
        for k in range(24):
            z=6+k*.26;x=side*(3.4+.32*math.sin(k*.8))
            if (x/7.4)**2+(z/13.2)**2<.98:
                pts.append((cx+x*sc,cy+head_surface(x,z,7.4,13.2)*sc-.04,cz+z*sc))
        if len(pts)>1:curve('Warden | centuries-old fracture',pts,.027,dark,'03')

# Arch bridge: radial voussoirs, individual deck stones and broken parapets.
by=12;bc=riverx(by);span=13.5
for i in range(39):
    a0=math.pi*i/39;a1=math.pi*(i+1)/39
    vs=[]
    for y in [by-1.7,by+1.7]:
        for r,a in [(span,a0),(span,a1),(span+1.25,a1),(span+1.25,a0)]:
            vs.append((bc+r*math.cos(a),y,-2.7+r*.64*math.sin(a)))
    ob=mesh('Bridge | radial arch stone %02d'%i,vs,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],oldstone,'04')
    mod=ob.modifiers.new('Worn joints','BEVEL');mod.width=.045;mod.segments=1
for i in range(45):
    x=bc-span-1+i*(span+1)*2/44
    z=-2.7+(span+1.25)*.64*math.sqrt(max(0,1-((x-bc)/(span+1.25))**2))+.12
    cube('Bridge | worn pilgrim footpath',(x,by,z),(.66,3.55,.32),oldstone,bevel=.065)
    if i%3==0:
        for s in [-1,1]:
            if random.random()>.24:
                cube('Bridge | fragment of parapet',(x,by+s*1.72,z+.65),(.95,.36,1.05+random.random()*.25),oldstone,bevel=.09)

def cylinder(name,loc,radius,depth,mat,group='05',vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
    return move(bpy.context.object,group,name,mat)

# A ruined circular sanctuary stands beyond the bridge, under the second warden.
sx,sy=-2,105
crag('Sanctuary | rocky island',sx,sy,-1,8,12,3.4,rock,'05',999)
for k in range(4):
    cylinder('Sanctuary | concentric ceremonial steps',(sx,sy,2.3+k*.23),6.4-k*.52,.3,oldstone,vertices=64)
for k in range(11):
    a=2*math.pi*k/12
    x=sx+4.7*math.cos(a);y=sy+4.7*math.sin(a)
    h=random.choice([3.0,4.4,6.8,7.5,8.0])
    cylinder('Sanctuary | broken fluted column',(x,y,3+h/2),.42,h,oldstone)
    cylinder('Sanctuary | column foot',(x,y,3.1),.7,.35,oldstone)
    cylinder('Sanctuary | surviving capital',(x,y,3+h),.65,.28,oldstone)
    if h>6:
        for flute in range(10):
            fa=flute*math.pi/5
            curve('Sanctuary | column flute',[(x+.425*math.cos(fa),y+.425*math.sin(fa),3.4),(x+.425*math.cos(fa),y+.425*math.sin(fa),3+h-.25)],.025,dark,'05')
for i in range(12):
    a0=i*2*math.pi/12;a1=(i+1)*2*math.pi/12
    if i in [1,2,3,6,7]:
        pts=[(sx+4.7*math.cos(a0+(a1-a0)*t/12),sy+4.7*math.sin(a0+(a1-a0)*t/12),10.8) for t in range(13)]
        curve('Sanctuary | broken entablature',pts,.42,oldstone,'05')
cylinder('Sanctuary | altar',(sx,sy,3.5),1.1,1.4,oldstone)
ico('Sanctuary | last votive flame',(sx,sy,4.6),(.22,.22,.65),glow,'05')

# Branching trees share a single mesh per tree, rather than hundreds of objects.
def tree(name,x,y,z,h,seed,foliage=False):
    rng=random.Random(seed);vs=[];fs=[]
    tips=[]
    def branch(start,direction,length,radius,depth):
        end=start+direction.normalized()*length
        side=direction.cross(Vector((0,0,1)))
        if side.length<.01:side=Vector((1,0,0))
        side.normalize();up=direction.normalized().cross(side).normalized()
        offset=len(vs);n=6
        for c,r in [(start,radius),(end,radius*.60)]:
            for k in range(n):
                q=c+r*(side*math.cos(k*2*math.pi/n)+up*math.sin(k*2*math.pi/n));vs.append(tuple(q))
        for k in range(n):fs.append((offset+k,offset+(k+1)%n,offset+(k+1)%n+n,offset+k+n))
        if depth:
            for k in range(2 if depth<3 else 3):
                d=direction.normalized()+Vector((rng.uniform(-.85,.85),rng.uniform(-.85,.85),rng.uniform(-.05,.55)))
                branch(end,d,length*rng.uniform(.54,.73),radius*.56,depth-1)
        else:tips.append(end)
    branch(Vector((x,y,z)),Vector((rng.uniform(-.18,.18),rng.uniform(-.18,.18),1)),h*.38,h*.075,3)
    mesh(name,vs,fs,bark,'06')
    if foliage:
        for tip in tips[::3]:
            ico(name+' | wind-worn canopy',tip,(h*.26,h*.23,h*.17),rng.choice(leaves),'06',1)

for k in range(54):
    y=random.uniform(-24,155);side=random.choice([-1,1]);x=riverx(y)+side*random.uniform(16,22)
    z=landz(x,y)
    if z<13:tree('Riverbank | ancient wind-bent tree',x,y,z,random.uniform(2.6,6.4),k+400, k%4==0)
tree('Foreground | the witness',-17,-17,landz(-17,-17),9.5,1491,True)
tree('Foreground | blackthorn',23,-24,landz(23,-24),7.2,1153)

# River stones, moss caps and memorial markers break up the banks.
for k in range(230):
    y=random.uniform(-48,180);x=riverx(y)+random.choice([-1,1])*random.uniform(11,25);z=landz(x,y)
    r=random.uniform(.25,1.6)
    ico('Scree | river-polished basalt',(x,y,z+r*.25),(r,r*.73,r*.6),rock,'01',1)
    if k%4==0 and z<9:
        ico('Scree | moss cushion',(x,y,z+r*.65),(r*.83,r*.65,r*.18),moss,'06',1)
for k in range(44):
    y=random.uniform(-5,122);x=riverx(y)+random.choice([-1,1])*random.uniform(15,19)
    z=landz(x,y);h=random.uniform(.6,1.6)
    ob=cube('Memorial | nameless stone',(x,y,z+h/2),(.45,.30,h),oldstone,'06',.08)
    ob.rotation_euler=(random.uniform(-.14,.14),random.uniform(-.18,.18),random.random())

def light(name,kind,loc,color,power,size=1):
    data=bpy.data.lights.new(name,kind);data.energy=power;data.color=color
    if kind=='AREA':data.shape='DISK';data.size=size
    if kind=='POINT':data.shadow_soft_size=size
    ob=bpy.data.objects.new(name,data);groups['08'].objects.link(ob);ob.location=loc
    return ob

def aim(obj,at):
    obj.rotation_euler=(Vector(at)-obj.location).to_track_quat('-Z','Y').to_euler()

def lantern(x,y,z,group='04'):
    cylinder('Lantern | brass foot',(x,y,z),.16,.10,gold,group,8)
    ico('Lantern | amber glass',(x,y,z+.23),(.11,.11,.21),glow,group,2)
    cylinder('Lantern | roof',(x,y,z+.46),.18,.10,gold,group,8)
    light('Lantern | pool of warmth','POINT',(x,y,z+.25),(1,.33,.07),55,.3)

# A hooded traveler, with a separate cloak, staff, and hand-held light.
px,py=bc-1.8,by-.3
pz=-2.7+(span+1.25)*.64*math.sqrt(1-((px-bc)/(span+1.25))**2)+.3
cloak=material('Pilgrim | faded ochre cloak',(.30,.095,.028),.92)
bpy.ops.mesh.primitive_cone_add(vertices=20,radius1=.39,radius2=.16,depth=1.25,location=(px,py,pz+.77))
move(bpy.context.object,'04','Pilgrim | cloak',cloak)
ico('Pilgrim | hood',(px,py,pz+1.55),(.23,.22,.28),cloak,'04',2)
curve('Pilgrim | walking staff',[(px-.48,py,pz),(px-.51,py,pz+1.9)],.035,bark,'04')
curve('Pilgrim | outstretched arm',[(px+.13,py,pz+1.18),(px+.57,py-.04,pz+1.08)],.09,cloak,'04')
lantern(px+.62,py-.04,pz+.72)
for s in [-1,1]:
    lantern(bc+s*11.7,by-1.48,2.55)
light('Sanctuary | memory of fire','POINT',(sx,sy,5),(1,.45,.11),350,1.4)

# Long cloud banks and a restrained, spatially varying atmospheric volume.
fog=bpy.data.materials.new('Atmosphere | blue valley haze');fog.use_nodes=True
nt=fog.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');v=nt.nodes.new('ShaderNodeVolumePrincipled')
v.inputs['Color'].default_value=(.42,.61,.65,1);v.inputs['Density'].default_value=.0065;v.inputs['Anisotropy'].default_value=.28
nt.links.new(v.outputs['Volume'],out.inputs['Volume'])
cube('Atmosphere | aerial perspective',(0,90,44),(220,330,125),fog,'07')

world=bpy.data.worlds.new('Dusk | the storm has passed');world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.18,.29,.34,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
scene.world=world
sun=light('Sun | last light through the storm','SUN',(60,110,100),(1,.72,.40),2.7)
sun.rotation_euler=(math.radians(28),math.radians(-24),math.radians(-150));sun.data.angle=math.radians(9)
key=light('Sky | vast cool softbox','AREA',(0,-10,74),(.54,.74,1),55000,80);aim(key,(0,58,0))
rim=light('Sky break | pale gold','AREA',(20,100,78),(1,.79,.49),75000,42);aim(rim,(-12,45,20))
fill=light('Wardens | soft reflected riverlight','AREA',(0,4,29),(.36,.66,.73),18000,32);aim(fill,(-18,47,28))

camdata=bpy.data.cameras.new('Hero | a pilgrim enters the valley');cam=bpy.data.objects.new('Hero | a pilgrim enters the valley',camdata);groups['08'].objects.link(cam)
cam.location=(12,-66,17);aim(cam,(-1,65,21));camdata.lens=33;camdata.clip_end=1200
scene.camera=cam
scene.render.engine='BLENDER_EEVEE'
scene.render.resolution_x=1600;scene.render.resolution_y=1050;scene.render.resolution_percentage=60
scene.render.image_settings.file_format='PNG';scene.render.filepath=OUT+'/valley-of-tears-preview.png'
scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=.45
scene.render.image_settings.color_mode='RGBA'
scene.use_nodes=True
nt=bpy.data.node_groups.new('Valley | final photographic glow','CompositorNodeTree')
scene.compositing_node_group=nt
nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
rl=nt.nodes.new('CompositorNodeRLayers')
gl=nt.nodes.new('CompositorNodeGlare')
gl.inputs['Type'].default_value='Fog Glow';gl.inputs['Quality'].default_value='High'
gl.inputs['Strength'].default_value=.35
co=nt.nodes.new('NodeGroupOutput')
nt.links.new(rl.outputs['Image'],gl.inputs['Image']);nt.links.new(gl.outputs['Image'],co.inputs['Image'])

scene['Title']='VALLEY OF TEARS'
scene['Lore']='The Wardens have wept since the names were lost. Each year, one pilgrim crosses the old bridge to keep the last sanctuary flame alive.'
scene['Build']='Procedural original world, built through Blender MCP. Seed 731.'
readme=bpy.data.texts.new('READ ME | Valley of Tears')
readme.write('VALLEY OF TEARS\nThe Weeping Wardens\n\n'+scene['Lore']+'\n\nAll geometry and shaders are original and procedural.\nCollections are organized by environment layer.\nHero camera is composed for 1600 x 1050.\nOriginal starter scene is retained separately.\n')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.lock_camera=False
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.region_3d.view_camera_zoom=5
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/valley-of-tears.blend')
result={'scene':scene.name,'objects':len(scene.objects),'vertices':sum(len(o.data.vertices) for o in scene.objects if o.type=='MESH'),'blend':bpy.data.filepath,'preview':scene.render.filepath}
