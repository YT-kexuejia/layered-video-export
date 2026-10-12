"""Generate disposable synthetic input locally; no personal footage is bundled."""
from pathlib import Path
import subprocess
from runtime import load_settings
C=load_settings();file=Path(C['sourceVideo']);file.parent.mkdir(parents=True,exist_ok=True)
if file.exists():raise SystemExit('Refusing to overwrite existing media: '+str(file))
subprocess.run([C['ffmpeg'],'-y','-hide_banner','-f','lavfi','-i','testsrc2=size=1920x1080:rate=24','-f','lavfi','-i','sine=frequency=440:sample_rate=48000','-t','12','-c:v','libx264','-preset','ultrafast','-crf','22','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(file)],check=True)
print('Generated local synthetic video and tone:',file)
