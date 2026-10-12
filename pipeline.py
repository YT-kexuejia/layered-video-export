"""Prepare a talking-head video for an existing agent; no model API key is required."""
from pathlib import Path
import argparse,json,os,re,shutil,subprocess,sys,unicodedata
BASE=Path(__file__).resolve().parent
PYTHON_SRC=BASE/'src'/'python'
if str(PYTHON_SRC) not in sys.path:sys.path.insert(0,str(PYTHON_SRC))
def save(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf-8')
def run(cmd):subprocess.run([str(x) for x in cmd],check=True)
def clean(s):return re.sub(r'\s+',' ',''.join(' ' if unicodedata.category(c).startswith('P') else c for c in s)).strip()
def captions_from_words(segments,maxlen=32):
    cues=[];words=[];text=''
    def flush():
        nonlocal words,text
        if words and text.strip():cues.append(dict(start=words[0]['start'],end=words[-1]['end'],text=text.strip()))
        words=[];text=''
    for seg in segments:
        for w in seg.get('words',[]):
            token=clean(w['word'])
            if not token:continue
            gap=w['start']-words[-1]['end'] if words else 0
            if words and (len(text)+len(token)>maxlen or gap>.65):flush()
            # Whisper carries spacing for Latin words; Chinese is concatenated.
            sep=' ' if text and (w['word'].startswith(' ') or gap>.25) else ''
            words.append(w);text+=sep+token
        flush()
    return cues
def settings(file):
    os.environ['LVE_CONFIG']=str(file.resolve())
    from runtime import load_settings
    # runtime.SETTINGS_PATH was captured at import; this helper is called only once.
    return load_settings()
def init(a):
    video=Path(a.video).resolve();root=Path(a.project).resolve();root.mkdir(parents=True,exist_ok=True)
    if (root/'config.json').exists():raise RuntimeError('Project exists; use its config to continue rather than overwriting it')
    if not video.is_file():raise FileNotFoundError(video)
    c=json.loads((BASE/'examples'/'basic'/'config.example.json').read_text('utf-8'))
    c.update(projectDir=str(root),sourceVideo=str(video),outputDir=str(root/'exports'),fontDir=str(root/'fonts'),filmFile='film.html',uiFile='film.html',uiEntry='main.jsx',subtitleFont='Source Han Sans SC',fingerprintFiles=['bundle.js','bundle.css','story.json','captions.json'])
    for k in ['node','ffmpeg','ffprobe','chrome']:
        if getattr(a,k,None):c[k]=getattr(a,k)
    save(root/'config.json',c);c=settings(root/'config.json')
    probe=json.loads(subprocess.check_output([c['ffprobe'],'-v','error','-show_streams','-show_format','-of','json',str(video)]))
    vs=next(s for s in probe['streams'] if s['codec_type']=='video')
    if not any(s['codec_type']=='audio' for s in probe['streams']):raise RuntimeError('Video has no narration audio')
    if vs['width']!=1920 or vs['height']!=1080:
        target=root/'source.mp4';run([c['ffmpeg'],'-y','-i',video,'-vf','scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2','-c:v','libx264','-preset','fast','-crf','18','-c:a','aac',target]);c['sourceVideo']=str(target)
    save(root/'config.json',c)
    duration=float(probe['format']['duration']);save(root/'media.json',dict(duration=duration,originalWidth=vs['width'],originalHeight=vs['height']))
    run([c['ffmpeg'],'-y','-hide_banner','-loglevel','error','-i',c['sourceVideo'],'-vn','-ac','1','-ar','16000',root/'voice.wav'])
    print('Prepared:',root,'\nNext: transcribe then author plan.json from timed narration')
def transcribe(a):
    root=Path(a.project).resolve();settings(root/'config.json')
    from faster_whisper import WhisperModel
    model=WhisperModel(a.model,device=a.device,compute_type='int8_float16' if a.device=='cuda' else 'int8')
    partial=root/'transcript.partial.json';done=json.loads(partial.read_text('utf-8')) if partial.exists() else []
    # Resume by skipping completed segments; VAD and word times remain global.
    cutoff=done[-1]['end'] if done else 0
    # init creates known mono PCM WAV; avoid FFmpeg/PyAV ABI differences for decoding.
    import wave,numpy as np
    with wave.open(str(root/'voice.wav'),'rb') as wav:
        if wav.getframerate()!=16000 or wav.getnchannels()!=1 or wav.getsampwidth()!=2:raise ValueError('Expected 16kHz mono PCM WAV')
        audio=np.frombuffer(wav.readframes(wav.getnframes()),dtype=np.int16).astype(np.float32)/32768
    segments,info=model.transcribe(audio,language=None if a.language=='auto' else a.language,word_timestamps=True,vad_filter=True,beam_size=5,clip_timestamps=str(cutoff))
    for s in segments:
        done.append(dict(start=s.start,end=s.end,text=s.text,words=[dict(start=w.start,end=w.end,word=w.word,probability=w.probability) for w in s.words or []]));save(partial,done);print(f'{s.end:.1f}s {s.text}',flush=True)
    save(root/'transcript.json',done);save(root/'captions.json',captions_from_words(done))
    (root/'transcript.txt').write_text('\n'.join(f"[{s['start']:.2f}–{s['end']:.2f}] {s['text']}" for s in done),'utf-8')
    print('Transcript and punctuation-free timed captions ready. Agent must author plan.json; no automatic topic guesses are applied.')
KINDS={'sphere','chip','camera','chapter','ui','cards','checklist','metric','bars','score','prompt','storyboard','character','timeline','balance','workflow','loop','flow','server','assembly','cache','gpu-board','film-reel','camera-rig','scales','deployment','turntable','dolly','path-editor','editorial','split-compare','iteration','decision','asset-tray','input-spectrum','grid-scale','contact-sheet','prompt-compare','request-card','prompt-morph','dialogue','control-desk','handoff','optimize','filmcut','edit-bay','continuity'}
def validate(plan,duration):
    if abs(plan['duration']-duration)>.1:raise ValueError('Plan duration must match media')
    if not plan['scenes'] or not plan['chapters']:raise ValueError('Empty scene plan')
    end=0;ids=set()
    for s in plan['scenes']:
        if s['id'] in ids:raise ValueError('Duplicate scene id')
        ids.add(s['id'])
        if abs(s['start']-end)>.05 or s['end']<=s['start']:raise ValueError('Scenes must cover narration without gaps/overlap')
        if s['kind'] not in KINDS:raise ValueError('Unknown visual kind')
        if not 0<=s['chapter']<len(plan['chapters']):raise ValueError('Chapter index')
        for k in ['a','b','desc']:
            if not isinstance(s.get(k),str):raise ValueError('Missing '+k)
        for t in s.get('reveal',[])+[s.get('titleAt',s['start']),s.get('visualAt',s['start'])]:
            if not s['start']<=t<s['end']:raise ValueError('Reveal outside scene')
        if s['kind'] in {'cards','checklist','flow'} and not s.get('items'):raise ValueError('Items required')
        if s['kind']=='ui' and (not s.get('image') or Path(s['image']).name!=s['image']):raise ValueError('UI requires an asset filename')
        end=s['end']
    if abs(end-duration)>.1:raise ValueError('Plan does not cover full duration')
    themes={'blue','cyan','violet','amber','ice'}
    for ch in plan['chapters']:
        if ch.get('theme') not in themes or not ch.get('short') or len(ch.get('beam',[]))!=2:raise ValueError('Invalid chapter theme/short/beam')
def build(a):
    root=Path(a.project).resolve();c=settings(root/'config.json');plan=json.loads((root/'plan.json').read_text('utf-8'));validate(plan,json.loads((root/'media.json').read_text('utf-8'))['duration'])
    for s in plan['scenes']:
        if s['kind']=='ui' and not (root/'assets'/s['image']).is_file():raise FileNotFoundError(s['image'])
    save(root/'story.json',plan)
    template=Path(a.template).resolve() if a.template else BASE/'templates'/'studio-blue'
    manifest=json.loads((template/'template.json').read_text('utf-8'))
    if manifest.get('protocol')!='layered-film-v1' or manifest.get('sourceGeometry')!='presenter-v1':raise ValueError('Incompatible template protocol or source geometry')
    def inside(folder,name):
        result=(folder/name).resolve()
        if not result.is_relative_to(folder):raise ValueError('Template path escapes directory')
        return result
    for src,dst in manifest['files'].items():
        target=inside(root,dst);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(inside(template,src),target)
    for asset in manifest.get('assets',[]):
        if not asset.get('license') or not asset.get('source'):raise ValueError('Template asset requires license and source')
        target=inside(root,asset['target']);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(inside(template,asset['file']),target)
    c['uiEntry']=manifest['previewEntrypoint'];c['gpuModules']=manifest['gpuModules'];c['templateId']=manifest['id'];c['templateVersion']=manifest['version'];save(root/'config.json',c)
    save(root/'template-used.json',manifest)
    css=root/'base.css'
    if a.font:
        font=Path(a.font).resolve();(root/'fonts').mkdir(exist_ok=True);shutil.copyfile(font,root/'fonts'/font.name)
        text=css.read_text('utf-8');text=re.sub(r"url\('[^']+\.otf'\)","url('./fonts/"+font.name+"')",text);css.write_text(text,'utf-8')
    else:css.write_text(re.sub(r'@font-face\{[^}]+\}','',css.read_text('utf-8')),'utf-8')
    (root/'film.html').write_text('<!doctype html><html lang="zh"><meta charset="utf-8"><title>Video composition</title><link rel="stylesheet" href="bundle.css"><div id="root"></div><script src="bundle.js"></script></html>','utf-8')
    save(root/'exports/.resolved-config.json',c)
    run([c['node'],BASE/'src'/'js'/'build_project.mjs',root/'exports/.resolved-config.json'])
    from runtime import write_srt
    write_srt(root/'captions.json',root/'captions.srt',0,plan['duration']);print('Built preview and SRT. Start serve.py with LVE_CONFIG='+str(root/'config.json'))
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('init');q.add_argument('video');q.add_argument('--project',required=True)
    for k in ['node','ffmpeg','ffprobe','chrome']:q.add_argument('--'+k)
    q=sub.add_parser('transcribe');q.add_argument('--project',required=True);q.add_argument('--model',default='small');q.add_argument('--device',choices=['cpu','cuda'],default='cpu');q.add_argument('--language',default='auto')
    q=sub.add_parser('build');q.add_argument('--project',required=True);q.add_argument('--font');q.add_argument('--template',help='Downloaded template directory containing template.json')
    a=p.parse_args();{'init':init,'transcribe':transcribe,'build':build}[a.command](a)
if __name__=='__main__':main()
