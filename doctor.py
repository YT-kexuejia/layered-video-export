"""Check configured tools and source metadata without starting an export."""
from pathlib import Path
import json,subprocess,sys
BASE=Path(__file__).resolve().parent
PYTHON_SRC=BASE/'src'/'python'
if str(PYTHON_SRC) not in sys.path:sys.path.insert(0,str(PYTHON_SRC))
from runtime import load_settings
C=load_settings()
print('Python:',sys.version.split()[0]);print('Chrome:',C['chrome'])
if sys.version_info<(3,13):raise SystemExit('ManimGX requires Python 3.13 or later')
for key in ['node','ffmpeg','ffprobe']:print(key+':',C[key])
import PIL,manimgx
subprocess.run([C['node'],'--check',str(BASE/'src'/'js'/'render_layers.mjs')],check=True)
probe=subprocess.run([C['ffmpeg'],'-v','error','-f','lavfi','-i','color=size=1920x1080:rate=24','-frames:v','1','-c:v','h264_nvenc','-f','null','-'],capture_output=True)
if probe.returncode:raise SystemExit('NVIDIA NVENC is required for this reference release. Check the driver and FFmpeg build.')
source=Path(C['sourceVideo'])
if source.exists():
    data=json.loads(subprocess.check_output([C['ffprobe'],'-v','error','-show_streams','-of','json',str(source)]))
    video=next(s for s in data['streams'] if s['codec_type']=='video')
    if (video['width'],video['height'])!=(1920,1080):raise SystemExit('The reference portrait crop requires a 1920x1080 source.')
    if not any(s['codec_type']=='audio' for s in data['streams']):raise SystemExit('Source must contain an audio track.')
else:print('Source not generated yet: run generate_example.py or configure your own media.')
print('Checks passed. No export was started.')
