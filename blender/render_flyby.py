from pathlib import Path
import bpy
import json
import os
import time
import traceback

ROOT=str(Path(__file__).resolve().parent)
START=time.time()
STATE=ROOT+'/flyby-render-status.json'
scene=bpy.context.scene

def status(state, **extra):
    record={'state':state,'pid':os.getpid(),'elapsed_seconds':round(time.time()-START,1),'total_frames':scene.frame_end-scene.frame_start+1}
    record.update(extra)
    with open(STATE+'.tmp','w') as handle:
        json.dump(record,handle,indent=2)
    os.replace(STATE+'.tmp',STATE)

def rendered(scene,*args):
    count=sum(os.path.isfile(ROOT+'/flyby-frames/frame-%04d.png'%f) for f in range(1,289))
    status('rendering',last_frame=scene.frame_current,completed_frames=count)

try:
    preferences=bpy.context.preferences.addons['cycles'].preferences
    preferences.compute_device_type='OPTIX'
    preferences.refresh_devices()
    for device in preferences.devices:
        device.use=device.type=='OPTIX'
    assert any(d.type=='OPTIX' and d.use for d in preferences.devices), 'NVIDIA OptiX GPU not detected'
    scene.render.engine='CYCLES'
    scene.cycles.device='GPU'
    scene.render.use_overwrite=False
    scene.render.use_persistent_data=True
    scene.render.filepath=ROOT+'/flyby-frames/frame-'
    bpy.app.handlers.render_write.append(rendered)
    status('starting',completed_frames=sum(os.path.isfile(ROOT+'/flyby-frames/frame-%04d.png'%f) for f in range(1,289)))
    bpy.ops.render.render(animation=True)
    missing=[f for f in range(1,289) if not os.path.isfile(ROOT+'/flyby-frames/frame-%04d.png'%f)]
    assert not missing, 'Missing frames: %s'%missing
    status('complete',completed_frames=288)
except Exception:
    status('failed',error=traceback.format_exc())
    raise
