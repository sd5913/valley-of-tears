from pathlib import Path
import bpy, math, random
from mathutils import Vector, noise
random.seed(812)
scene=bpy.context.scene
groups={c.name[:2]:c for c in scene.collection.children}
src=open(str(Path(__file__).resolve().parent / 'build_valley.py')).read()
ns={'bpy':bpy,'math':math,'Vector':Vector,'noise':noise}
exec(src[src.index('def nv('):src.index('verts=[]; faces=[]')],ns)
landz,riverx=ns['landz'],ns['riverx']

def mesh(name,vs,fs,mats,group='06',indices=None):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
    ob=bpy.data.objects.new(name,me);groups[group].objects.link(ob)
    for m in mats:me.materials.append(m)
    if indices:
        for p,i in zip(me.polygons,indices):p.material_index=i
    return ob

def mat(name,col,rough=.75):
    m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough
    return m

rock=bpy.data.materials['Basalt | rain-darkened striated stone']
ram=next(n for n in rock.node_tree.nodes if n.type=='VALTORGB')
ram.color_ramp.elements[0].color=(.014,.027,.026,1)
ram.color_ramp.elements[1].color=(.15,.205,.165,1)
nt=rock.node_tree;p=nt.nodes.get('Principled BSDF')
# Broad lichen patches avoid a uniform noise texture across the whole gorge.
tex=nt.nodes.new('ShaderNodeTexCoord')
n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=.45;n.inputs['Detail'].default_value=3
nt.links.new(tex.outputs['Object'],n.inputs['Vector'])
r=nt.nodes.new('ShaderNodeValToRGB')
r.color_ramp.elements[0].position=.48;r.color_ramp.elements[0].color=(0,0,0,1)
r.color_ramp.elements[1].position=.76;r.color_ramp.elements[1].color=(.7,.7,.7,1)
nt.links.new(n.outputs['Fac'],r.inputs[0])
mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[2].default_value=(.075,.14,.037,1)
nt.links.new(r.outputs['Color'],mix.inputs[0]);nt.links.new(ram.outputs['Color'],mix.inputs[1]);nt.links.new(mix.outputs[0],p.inputs['Base Color'])

for ob in scene.objects:
    if ob.type=='MESH' and (ob.name.startswith('Columnar canyon') or 'rock-cut mantle' in ob.name):
        # Reduce regular terracing while retaining the long vertical fissures.
        for j in range(23):
            t=j/22
            old=(1-.35*t)*(1+.065*math.sin(t*58)+.06*math.sin(t*113))
            new=(1-.35*t)*(1+.018*math.sin(t*58)+.022*math.sin(t*113))
            layer=ob.data.vertices[j*18:(j+1)*18]
            center=sum((v.co.copy() for v in layer),Vector())/18
            for i,v in enumerate(layer):
                q=v.co-center
                a=i*math.pi/9
                f=new/old*(1+.035*math.sin(a*7+t*5))
                v.co.x=center.x+q.x*f;v.co.y=center.y+q.y*f
        for poly in ob.data.polygons:poly.use_smooth=True
        sub=ob.modifiers.new('Eroded cliff silhouette','SUBSURF');sub.levels=1;sub.render_levels=1

face_ns={'math':math}
exec(src[src.index('def head_surface('):src.index('def waterfall(')],face_ns)
hs=face_ns['head_surface']
for idx,(cx,cy,cz,sc) in enumerate([(-19,47,27,1),(25,86,33,1.12)]):
    for sign in [-1,1]:
        name='Warden %d | tear %s'%(idx+1,sign)
        for ob in [o for o in scene.objects if o.name==name or o.name.startswith(name+' | falling')]:
            if ob.type=='MESH':
                for v in ob.data.vertices:
                    z=(v.co.z-cz)/sc
                    if -12.3<z<3.1:
                        v.co.y=min(v.co.y,cy+hs(sign*2.7,z,7.4,13.2)*sc-.24)
            elif ob.type=='CURVE':
                for sp in ob.data.splines:
                    for p in sp.points:
                        z=(p.co.z-cz)/sc
                        if -12.3<z<3.1:p.co.y=min(p.co.y,cy+hs(sign*2.7,z,7.4,13.2)*sc-.29)

grassm=[mat('Wetland | sedge green',(.055,.12,.037)),mat('Wetland | straw gold',(.21,.24,.078)),mat('Wetland | silver reed',(.23,.31,.18)),mat('Wetland | shadow fern',(.027,.085,.037))]
vs=[];fs=[];mi=[]
for k in range(10500):
    y=random.uniform(-48,165);x=riverx(y)+random.choice([-1,1])*random.uniform(12,25)
    z=landz(x,y)
    if not .2<z<7.5:continue
    h=random.uniform(.12,.72);w=random.uniform(.025,.07);a=random.uniform(0,math.tau)
    dx,dy=math.cos(a),math.sin(a);bend=random.uniform(.1,.4)
    n=len(vs)
    vs.extend([(x-w*dy,y+w*dx,z),(x+w*dy,y-w*dx,z),(x+dx*bend+w*.4*dy,y+dy*bend-w*.4*dx,z+h*.65),(x+dx*bend-w*.4*dy,y+dy*bend+w*.4*dx,z+h*.65),(x+dx*bend*1.8,y+dy*bend*1.8,z+h)])
    fs.extend([(n,n+1,n+2,n+3),(n+3,n+2,n+4)]);c=random.choices(range(4),[5,1,1,3])[0];mi.extend([c,c])
mesh('Wetland | thousands of individual sedge blades',vs,fs,grassm,indices=mi)

vs=[];fs=[];mi=[]
for k in range(350):
    y=random.uniform(-35,130);x=riverx(y)+random.choice([-1,1])*random.uniform(14,23);z=landz(x,y)
    if not .3<z<9:continue
    size=random.uniform(.3,1.0)
    for frond in range(7):
        a=frond*math.tau/7+random.random()*.5
        outward=Vector((math.cos(a),math.sin(a),0));side=Vector((-math.sin(a),math.cos(a),0))
        for leaf in range(2,10):
            t=leaf/10;base=Vector((x,y,z))+outward*(t*size)+Vector((0,0,math.sin(t*2.3)*size*.6))
            length=math.sin(t*math.pi)*size*.24
            for s in [-1,1]:
                n=len(vs);tip=base+side*s*length+outward*size*.12
                vs.extend([tuple(base-outward*.04),tuple(tip),tuple(base+outward*.06+Vector((0,0,.035)))])
                fs.append((n,n+1,n+2));mi.append(3 if k%2 else 0)
mesh('Wetland | feathered fern rosettes',vs,fs,grassm,indices=mi)

# Replace coarse canopy shells with individually modeled pointed leaves.
leafm=[mat('Willow | deep sage',(.065,.145,.066)),mat('Willow | olive highlights',(.17,.25,.088)),mat('Willow | silver underside',(.25,.34,.18))]
vs=[];fs=[];mi=[]
for ob in list(scene.objects):
    if 'wind-worn canopy' not in ob.name:continue
    center=ob.location.copy();sc=ob.scale.copy()
    ob.hide_render=True;ob.hide_set(True)
    for k in range(330):
        a=random.random()*math.tau;z=random.uniform(-1,1);rr=math.sqrt(max(0,1-z*z))
        r=random.random()**.3
        base=center+Vector((sc.x*rr*math.cos(a)*r,sc.y*rr*math.sin(a)*r,sc.z*z*r))
        length=random.uniform(.12,.33);direction=Vector((math.cos(a),math.sin(a),random.uniform(-.8,.3))).normalized()
        side=Vector((-math.sin(a),math.cos(a),0))*length*.20
        n=len(vs);tip=base+direction*length;mid=base+direction*length*.48+Vector((0,0,.035))
        vs.extend([tuple(base),tuple(mid+side),tuple(tip),tuple(mid-side),tuple(mid+Vector((0,0,.025)))])
        fs.extend([(n,n+1,n+4),(n+1,n+2,n+4),(n+2,n+3,n+4),(n+3,n,n+4)]);mi.extend([random.randrange(3)]*4)
mesh('Willows | individually modeled wind-scattered leaves',vs,fs,leafm,indices=mi)

# Ivy descends from the wardens and ruined columns in broken curtains.
vs=[];fs=[];mi=[]
for idx,(cx,cy,cz,sc) in enumerate([(-19,47,27,1),(25,86,33,1.12)]):
    for stem in range(38):
        x=cx+random.choice([-1,1])*random.uniform(5.4,8.5)*sc
        y=cy+random.uniform(-2,3)*sc
        top=cz+random.uniform(4,12)*sc
        length=random.uniform(2,10)*sc
        for k in range(int(length*7)):
            z=top-k*.14;xx=x+.13*math.sin(k*.55+stem)
            for s in [-1,1]:
                n=len(vs);l=random.uniform(.10,.22)*sc
                vs.extend([(xx,y,z),(xx+s*l,y-.04,z-.05),(xx+s*l*.8,y,z-.28),(xx,y+.03,z-.16)])
                fs.append((n,n+1,n+2,n+3));mi.append(random.randrange(3))
mesh('Wardens | curtains of hanging ivy',vs,fs,leafm,indices=mi)

fog=bpy.data.materials['Atmosphere | blue valley haze'].node_tree
v=next(n for n in fog.nodes if n.type=='PRINCIPLED_VOLUME');v.inputs['Density'].default_value=.0027
v.inputs['Color'].default_value=(.28,.43,.49,1)
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.11,.20,.29,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.32
bpy.data.lights['Sun | last light through the storm'].energy=1.75
bpy.data.lights['Sun | last light through the storm'].color=(1,.67,.34)
bpy.data.lights['Sky | vast cool softbox'].energy=30000
bpy.data.lights['Wardens | soft reflected riverlight'].energy=11000
scene.view_settings.exposure=.15
scene.eevee.use_raytracing=True
scene.eevee.taa_render_samples=48
scene.render.filepath=str(Path(__file__).resolve().parent / 'valley-of-tears-preview-03.png')
scene['Polish']='Moss and lichen, hand-shaped tear paths, botanical leaf geometry, sedge and ferns, hanging ivy, atmospheric dusk.'
bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).resolve().parent / 'valley-of-tears.blend'))
result={'polished':True,'objects':len(scene.objects)}
