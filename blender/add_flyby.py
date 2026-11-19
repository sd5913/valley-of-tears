from pathlib import Path
import bpy
import math
import json
import os
from mathutils import Vector, noise

ROOT = str(Path(__file__).resolve().parent)
scene = bpy.context.scene
assert scene.name == 'VALLEY OF TEARS | The Weeping Wardens'
assert not bpy.data.objects.get('Flyby | river pilgrimage'), 'Flyby already exists'
collection = bpy.data.collections.new('09 | Animated river pilgrimage')
scene.collection.children.link(collection)
data = bpy.data.cameras.new('Flyby | 33 mm river pilgrimage')
camera = bpy.data.objects.new('Flyby | river pilgrimage', data)
collection.objects.link(camera)
data.lens = 33
data.clip_start = .12
data.clip_end = 1200
data.passepartout_alpha = 1

# Hermite interpolation gives a continuous tangent at every waypoint.
positions = [Vector(p) for p in [(12,-66,17),(8,-32,15),(3,4,12.5),(0,36,14),(4,73,20)]]
targets = [Vector(p) for p in [(-1,65,21),(-8,59,24),(-12,51,24),(6,87,26),(-2,108,8)]]

def interpolate(points, u):
    f = u * (len(points)-1)
    i = min(int(f), len(points)-2)
    t = f-i
    p0,p1 = points[i],points[i+1]
    m0 = (points[i+1]-points[max(0,i-1)])*.5
    m1 = (points[min(len(points)-1,i+2)]-points[i])*.5
    return (2*t**3-3*t*t+1)*p0+(t**3-2*t*t+t)*m0+(-2*t**3+3*t*t)*p1+(t**3-t*t)*m1

camera.rotation_mode = 'QUATERNION'
previous = None
samples = []
for frame in range(1,289):
    t = (frame-1)/287
    # Gentle acceleration and deceleration retain motion through the middle.
    u = .55*t+.45*(t*t*(3-2*t))
    pos = interpolate(positions,u)
    target = interpolate(targets,u)
    quat = (target-pos).to_track_quat('-Z','Y')
    if previous and quat.dot(previous)<0:
        quat.negate()
    camera.location = pos
    camera.rotation_quaternion = quat
    camera.keyframe_insert(data_path='location', frame=frame, group='River flight')
    camera.keyframe_insert(data_path='rotation_quaternion', frame=frame, group='Gaze through the valley')
    previous = quat.copy()
    samples.append({'frame':frame,'position':list(pos),'target':list(target)})
camera.animation_data.action.name = 'River pilgrimage | twelve-second continuous camera flight'

# The editable route is visible in the viewport and excluded from renders.
curve = bpy.data.curves.new('Flyby route | editable reference','CURVE')
curve.dimensions = '3D'
spline = curve.splines.new('POLY')
spline.points.add(len(samples)-1)
for point,sample in zip(spline.points,samples):
    point.co = (*sample['position'],1)
route = bpy.data.objects.new('Flyby | camera route reference',curve)
collection.objects.link(route)
route.hide_render = True
route.color = (.95,.53,.14,1)

scene.frame_start=1
scene.frame_end=288
scene.render.fps=24
scene.render.fps_base=1
scene.camera=camera
scene.frame_set(1)
for name,frame in [('Enter the valley',1),('Approach the pilgrim bridge',82),('Cross above the pilgrim',145),('Between the Wardens',214),('The last sanctuary flame',288)]:
    scene.timeline_markers.new(name,frame=frame)

preferences = bpy.context.preferences.addons['cycles'].preferences
preferences.compute_device_type='OPTIX'
preferences.refresh_devices()
for device in preferences.devices:
    device.use=device.type=='OPTIX'
assert any(d.type=='OPTIX' and d.use for d in preferences.devices), 'No OptiX device'
scene.render.engine='CYCLES'
scene.cycles.device='GPU'
scene.cycles.samples=24
scene.cycles.preview_samples=16
scene.cycles.use_denoising=True
scene.cycles.denoiser='OPTIX'
scene.cycles.use_adaptive_sampling=True
scene.cycles.adaptive_threshold=.06
scene.cycles.max_bounces=6
scene.cycles.diffuse_bounces=3
scene.cycles.glossy_bounces=3
scene.cycles.transmission_bounces=4
scene.cycles.volume_bounces=1
scene.cycles.sample_clamp_indirect=5
scene.render.use_persistent_data=True
scene.render.use_motion_blur=True
scene.render.motion_blur_shutter=.25
scene.render.resolution_x=1280
scene.render.resolution_y=840
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.image_settings.color_mode='RGB'
scene.render.image_settings.compression=25
scene.render.use_file_extension=True
scene.render.use_overwrite=False
scene.render.use_placeholder=False
os.makedirs(ROOT+'/flyby-frames',exist_ok=True)
scene.render.filepath=ROOT+'/flyby-frames/frame-'
scene['Flyby']='Frames 1-288, 24 fps, 12 seconds. River approach, bridge crossing, Wardens, sanctuary. Cycles / NVIDIA OptiX, 1280 x 840.'
scene['GPU verified']='NVIDIA GeForce RTX 3060 Laptop GPU / OptiX; Blender already uses NVIDIA Vulkan. No restart needed.'

# Reuse the terrain function to check every point against the sculpted river bed.
source=open(ROOT+'/build_valley.py').read()
ns={'math':math,'Vector':Vector,'noise':noise}
exec(source[source.index('def nv('):source.index('verts=[]; faces=[]')],ns)
clearance=min(p['position'][2]-ns['landz'](p['position'][0],p['position'][1]) for p in samples)
assert clearance>8, 'Camera is too close to the terrain: %.3f'%clearance
with open(ROOT+'/flyby-camera-path.json','w') as handle:
    json.dump({'fps':24,'frames':288,'minimum_terrain_clearance':clearance,'samples':samples},handle,indent=2)
text=bpy.data.texts.new('SOURCE | add_flyby.py')
text.write(open(ROOT+'/add_flyby.py').read())
for ob in bpy.context.selected_objects:
    ob.select_set(False)
camera.select_set(True)
bpy.context.view_layer.objects.active=camera
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/valley-of-tears-flyby.blend')
result={'blend':bpy.data.filepath,'camera':camera.name,'frames':288,'seconds':12,'resolution':[1280,840],'minimum_terrain_clearance':round(clearance,3),'optix_devices':[d.name for d in preferences.devices if d.type=='OPTIX' and d.use]}
