"""Portable settings and subtitle helpers; no credentials or bundled media."""
from pathlib import Path
import os,json,shutil,re
BASE=Path(__file__).resolve().parent
SETTINGS_PATH=Path(os.environ.get('LVE_CONFIG',BASE/'config.json')).resolve()
def load_settings():
    file=SETTINGS_PATH if SETTINGS_PATH.exists() else BASE/'config.example.json'
    settings=json.loads(file.read_text('utf-8'))
    def local(value):return str((file.parent/value).resolve()) if not Path(value).is_absolute() else value
    for key in ['projectDir','outputDir','sourceVideo','fontDir']:settings[key]=local(settings[key])
    for key in ['node','ffmpeg','ffprobe']:
        value=settings.get(key,key);found=shutil.which(value) or (local(value) if Path(local(value)).is_file() else None)
        if not found:raise RuntimeError(f'{key} not found. Install it on PATH or configure its full path.')
        settings[key]=found
    chrome=settings.get('chrome') or os.environ.get('CHROME_PATH')
    if not chrome:
        candidates=[Path(os.environ.get('PROGRAMFILES','C:/Program Files'))/'Google/Chrome/Application/chrome.exe',Path(os.environ.get('LOCALAPPDATA',''))/'Google/Chrome/Application/chrome.exe']
        chrome=next((str(p) for p in candidates if p.is_file()),None)
    if not chrome or not Path(chrome).is_file():raise RuntimeError('Chrome not found. Set chrome in config.json or CHROME_PATH.')
    settings['chrome']=chrome
    output=Path(settings['outputDir']);output.mkdir(parents=True,exist_ok=True)
    resolved=output/'.resolved-config.json';resolved.write_text(json.dumps(settings,ensure_ascii=False),'utf-8')
    os.environ['LVE_RESOLVED_CONFIG']=str(resolved)
    return settings
def write_srt(captions,target,start,duration):
    def stamp(t):
        n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
    lines=[];i=0
    for c in json.loads(Path(captions).read_text('utf-8')):
        a=max(start,c['start']);b=min(start+duration,c['end'])
        if b<=a:continue
        i+=1;text=re.sub(r'[，。！？、；：,.!?;:]+',' ',c['text']).strip()
        lines.append(f'{i}\n{stamp(a-start)} --> {stamp(b-start)}\n{text}\n')
    Path(target).write_text('\n'.join(lines),'utf-8')
