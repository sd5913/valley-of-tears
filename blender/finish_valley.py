from pathlib import Path
import bpy,math,random
from mathutils import Vector,noise
random.seed(131)
scene=bpy.context.scene
groups={c.name[:2]:c for c in scene.collection.children}

def mesh(name,vs,fs,mat,group='07'):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
    ob=bpy.data.objects.new(name,me);groups[group].objects.link(ob);me.materials.append(mat)
    return ob

def mat(name,color,emission=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.86
    if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
    return m

# Layered silhouettes carry the eye beyond the built canyon into a larger world.
for layer,y in enumerate([195,245,310,390]):
    color=[(.085,.15,.15),(.12,.21,.23),(.17,.27,.30),(.23,.33,.36)][layer]
    mm=mat('Distance | mountain layer %d'%layer,color,.18)
    vs=[];fs=[]
    for row in range(4):
        for i in range(121):
            x=-250+i*500/120
            h=18+31*abs(math.sin(i*.27+layer))**3+14*noise.noise_vector(Vector((i*.25,layer*3,1)))[0]
            h*=.35+.65*min(1,abs(x+15)/70)
            z=h if row==1 else (h*.75 if row==2 else -15)
            vs.append((x,y+[0,5,26,45][row],z))
    for row in range(3):
        for i in range(120):
            a=row*121+i;fs.append((a,a+1,a+122,a+121))
    ob=mesh('Horizon | receding broken mountain range %d'%layer,vs,fs,mm)
    for p in ob.data.polygons:p.use_smooth=True

# A procedural storm sky, with a pale break above the distant mountains.
nt=scene.world.node_tree
bg=nt.nodes.get('Background');bg.inputs['Strength'].default_value=.6
tex=nt.nodes.new('ShaderNodeTexCoord')
mul=nt.nodes.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=(2,2,6)
nt.links.new(tex.outputs['Normal'],mul.inputs[0])
n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=2.6;n.inputs['Detail'].default_value=5;n.inputs['Roughness'].default_value=.7
nt.links.new(mul.outputs[0],n.inputs['Vector'])
r=nt.nodes.new('ShaderNodeValToRGB')
r.color_ramp.elements[0].position=.24;r.color_ramp.elements[0].color=(.026,.059,.09,1)
r.color_ramp.elements[1].position=.78;r.color_ramp.elements[1].color=(.40,.46,.43,1)
nt.links.new(n.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs['Color'],bg.inputs['Color'])

moon=mat('Sky | pale setting moon',(.7,.79,.70),1.6)
nt=moon.node_tree;p=nt.nodes.get('Principled BSDF')
t=nt.nodes.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=7;t.inputs['Detail'].default_value=4
r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.27,.34,.32,1);r.color_ramp.elements[1].color=(.73,.78,.65,1)
nt.links.new(t.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs['Color'],p.inputs['Base Color']);nt.links.new(r.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.95
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=1,location=(-29,350,105))
ob=bpy.context.object;ob.name='Sky | the witness moon';ob.scale=(12,2,12)
for c in list(ob.users_collection):c.objects.unlink(ob)
groups['07'].objects.link(ob);ob.data.materials.append(moon)
for p in ob.data.polygons:p.use_smooth=True

# Soft-edged local mist gathers at the falls instead of flattening the entire view.
mist=bpy.data.materials.new('Mist | soft billows of waterfall spray');mist.use_nodes=True
nt=mist.node_tree;nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputMaterial');vol=nt.nodes.new('ShaderNodeVolumePrincipled');vol.inputs['Color'].default_value=(.46,.66,.65,1);vol.inputs['Anisotropy'].default_value=.15
tc=nt.nodes.new('ShaderNodeTexCoord')
sub=nt.nodes.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(.5,.5,.5)
nt.links.new(tc.outputs['Generated'],sub.inputs[0])
length=nt.nodes.new('ShaderNodeVectorMath');length.operation='LENGTH';nt.links.new(sub.outputs[0],length.inputs[0])
ramp=nt.nodes.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=.14;ramp.inputs['From Max'].default_value=.5;ramp.inputs['To Min'].default_value=.09;ramp.inputs['To Max'].default_value=0
nt.links.new(length.outputs['Value'],ramp.inputs['Value'])
n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=5;n.inputs['Detail'].default_value=3
nt.links.new(tc.outputs['Generated'],n.inputs['Vector'])
mult=nt.nodes.new('ShaderNodeMath');mult.operation='MULTIPLY'
nt.links.new(ramp.outputs[0],mult.inputs[0]);nt.links.new(n.outputs['Fac'],mult.inputs[1]);nt.links.new(mult.outputs[0],vol.inputs['Density']);nt.links.new(vol.outputs[0],out.inputs['Volume'])
for k,(loc,sc) in enumerate([((-19,39,1.7),(7,4,2.5)),((25,78,1.8),(7,4,3)),((3,59,1),(14,5,1.6)),((-2,121,1.2),(10,4,1.7))]):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc)
    ob=bpy.context.object;ob.name='Mist | drifting spray bank %d'%k;ob.scale=sc
    for c in list(ob.users_collection):c.objects.unlink(ob)
    groups['07'].objects.link(ob);ob.data.materials.append(mist)

# Small, asymmetric bird silhouettes are a final cue to the landscape's size.
bird=mat('Wildlife | distant ravens',(.006,.013,.016))
vs=[];fs=[]
for k in range(13):
    x=random.uniform(-12,16);y=random.uniform(90,135);z=random.uniform(35,44);s=random.uniform(.22,.46)
    n=len(vs)
    vs.extend([(x,y,z),(x-s*.55,y+.06,z+s*.45),(x-s*1.4,y+.3,z+s*.28),(x-s*.55,y+.2,z+.04),(x+s*.65,y+.05,z+s*.32),(x+s*1.5,y+.25,z+s*.05),(x+s*.55,y+.2,z-.06)])
    fs.extend([(n,n+1,n+2,n+3),(n,n+4,n+5,n+6)])
mesh('Wildlife | ravens above the sanctuary',vs,fs,bird)

# Preserve both composed views in the delivered project.
detaildata=bpy.data.cameras.new('Detail | beneath the First Warden')
detail=bpy.data.objects.new('Detail | beneath the First Warden',detaildata);groups['08'].objects.link(detail)
detail.location=(3,-4,11);detail.rotation_euler=(Vector((-13,49,24))-detail.location).to_track_quat('-Z','Y').to_euler();detaildata.lens=34;detaildata.clip_end=1200
scene.render.resolution_x=1920;scene.render.resolution_y=1260;scene.render.resolution_percentage=100
scene.eevee.taa_render_samples=96
scene.eevee.volumetric_samples=96
scene.eevee.volumetric_tile_size='4'
scene.render.filepath=str(Path(__file__).resolve().parent / 'valley-of-tears.png')
scene['Final art']='Layered distant mountains, clouded sky, setting moon, local spray, ravens and two composed cameras.'
bpy.context.view_layer.objects.active=scene.camera
for ob in bpy.context.selected_objects:ob.select_set(False)
scene.camera.select_set(True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.region_3d.view_camera_zoom=5
            area.spaces.active.lock_camera=False
            area.spaces.active.overlay.show_overlays=False
            area.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(Path(__file__).resolve().parent / 'valley-of-tears.blend'))
result={'ready':True,'objects':len(scene.objects),'render':[1920,1260]}
