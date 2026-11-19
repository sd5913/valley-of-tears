import argparse
import json
import pathlib
import subprocess
import time

ROOT=pathlib.Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--wait',action='store_true')
args=parser.parse_args()
while True:
    status=json.loads((ROOT/'flyby-render-status.json').read_text())
    print(json.dumps(status),flush=True)
    if status['state']=='failed':
        raise RuntimeError(status.get('error','Render failed'))
    if status['state']=='complete':
        break
    if not args.wait:
        raise RuntimeError('Render still in progress; run with --wait')
    time.sleep(45)

missing=[f for f in range(1,289) if not (ROOT/'flyby-frames'/f'frame-{f:04d}.png').is_file()]
assert not missing, f'Missing frames: {missing}'
output=ROOT/'valley-of-tears-flyby.mp4'
assert not output.exists(), f'Video already exists: {output}'
temporary=ROOT/'valley-of-tears-flyby.part.mp4'
command=['ffmpeg','-hide_banner','-loglevel','warning','-n','-framerate','24','-start_number','1','-i',str(ROOT/'flyby-frames'/'frame-%04d.png'),'-frames:v','288','-c:v','libx264','-preset','medium','-crf','18','-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart','-metadata','title=Valley of Tears | The River Pilgrimage',str(temporary)]
print('Encoding H.264 MP4...',flush=True)
subprocess.run(command,check=True)
probe=subprocess.run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(temporary)],capture_output=True,text=True,check=True)
metadata=json.loads(probe.stdout)
video=next(s for s in metadata['streams'] if s['codec_type']=='video')
assert video['nb_read_frames']=='288', video
assert video['r_frame_rate']=='24/1', video
assert video['width']==1280 and video['height']==840, video
assert abs(float(metadata['format']['duration'])-12)<.05, metadata['format']
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(temporary),'-f','null','-'],check=True)
temporary.rename(output)
(ROOT/'flyby-video-metadata.json').write_text(json.dumps(metadata,indent=2))
print(json.dumps({'video':str(output),'frames':288,'fps':24,'duration':12,'dimensions':[1280,840],'decode_check':'passed','bytes':output.stat().st_size}),flush=True)
