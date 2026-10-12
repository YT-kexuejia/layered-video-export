"""Web export controller: 5-minute segments, durable resume, validated cleanup."""
from pathlib import Path
import os,sys,json,time,subprocess,hashlib,shutil,argparse
from runtime import load_settings, SETTINGS_PATH
C=load_settings();WORK=Path(__file__).resolve().parent;ROOT=Path(C['projectDir']);EXPORTS=Path(C['outputDir'])
NODE=Path(C['node']);PY=Path(sys.executable);FF=Path(C['ffmpeg']);FP=Path(C['ffprobe']);SOURCE=Path(C['sourceVideo'])
p=argparse.ArgumentParser();p.add_argument('--job',required=True);p.add_argument('--config',help='Reserved job metadata; settings come from LVE_CONFIG');p.add_argument('--start',type=float,default=0);p.add_argument('--duration',type=float);p.add_argument('--segment-frames',type=int,default=7200);args=p.parse_args()
if not args.job.replace('-','').replace('_','').isalnum():raise ValueError('Invalid job')
story=json.loads((ROOT/'story.json').read_text('utf-8'));duration=min(args.duration or story['duration'],story['duration']-args.start);total=int(__import__('math').ceil(duration*24))
if duration<=0 or args.start<0 or not 1<=args.segment_frames<=7200:raise ValueError('Invalid duration')
job=args.job;cache=EXPORTS/(job+'.frames');segments=cache/'segments';segments.mkdir(parents=True,exist_ok=True)
status=EXPORTS/(job+'.json');cancel=EXPORTS/(job+'.cancel');manifest=cache/'manifest.json';began=time.perf_counter();completed=0;fresh=0;current=None
def atomic(file,data):
    temp=file.with_name(file.name+f'.{os.getpid()}.tmp')
    for i in range(8):
        try:temp.write_text(json.dumps(data,ensure_ascii=False),'utf-8');temp.replace(file);return
        except PermissionError:time.sleep(.025*(i+1))
    raise RuntimeError('Cannot save checkpoint '+str(file))
signature=hashlib.sha256()
for file in [ROOT/n for n in C['fingerprintFiles']]+list(WORK.glob('*.py'))+list(WORK.glob('*.mjs')):
    signature.update(file.read_bytes())
signature.update(json.dumps(C,sort_keys=True).encode());signature.update(json.dumps(dict(start=args.start,duration=duration,fps=24,size=SOURCE.stat().st_size,mtime=SOURCE.stat().st_mtime_ns,segmentSize=args.segment_frames)).encode())
fingerprint=signature.hexdigest()
info=json.loads(manifest.read_text('utf-8')) if manifest.exists() else dict(fingerprint=fingerprint,start=args.start,duration=duration,total=total,fps=24,segments=[],packs=[],backend='hybrid-v1')
def state(stage,**extra):
    elapsed=time.perf_counter()-began;preview=completed;phase=None;phase_done=0;phase_total=0
    if current and (current/'layer-progress.json').exists():
        try:
            layer=json.loads((current/'layer-progress.json').read_text('utf-8'));phase=layer['phase'];phase_done=layer['done'];phase_total=layer['total'];q=min(1,phase_done/max(1,phase_total))
            weight={'gpu':.15*q,'ui':.15+.45*q,'ready':.60,'ui-encoding':.60,'wave':.65+.05*q,'compose':.70,'done':1}.get(phase,0)
            if phase=='compose' and (current/'compose-progress.txt').exists():
                for line in (current/'compose-progress.txt').read_text(errors='replace').splitlines():
                    if line.startswith('frame='):weight=.70+.30*min(1,int(line.split('=')[1])/count)
            preview+=int(count*weight)
        except (ValueError,OSError,KeyError):pass
    has_assets=completed>0 or bool(current and (any((current/'ui').glob('*.png')) or (current/'gpu.ready').exists()))
    data=dict(job=job,pid=os.getpid(),stage=stage,width=1920,height=1080,fps=24,total=total,frames=min(total,preview),cachedFrames=min(total,preview),encodedFrames=completed,completedSegments=len(info['segments']),percent=min(100,preview/total*100),elapsed=elapsed,renderFps=fresh/elapsed if fresh else None,eta=(total-preview)/(fresh/elapsed) if fresh else None,workers=1,encoder='h264_nvenc',workflow='hybrid-segments',backend='hybrid-v1',phase=phase,phaseDone=phase_done,phaseTotal=phase_total,resumable=has_assets and stage!='complete',segmentStart=completed,segmentFrames=count if current else 0,removeCompletedFrames=True,**extra)
    atomic(status,data)
def check():
    if cancel.exists():raise InterruptedError('已暂停 尚未合成的图片及图层已保留')
    if shutil.disk_usage(cache).free<1024**3:raise RuntimeError('磁盘剩余空间不足 1GB 已生成素材保留 请释放空间后继续')
def run(cmd,stage):
    check();state(stage)
    with (cache/'worker.log').open('a',encoding='utf-8') as log:
        child=subprocess.Popen([str(x) for x in cmd],cwd=WORK,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        stopping=None
        while child.poll() is None:
            if cancel.exists():
                if stopping is None:stopping=time.perf_counter()
                # Chromium renderer polls its marker and closes itself. Other workers are a dedicated tree.
                if child.args[0]!=str(NODE) or time.perf_counter()-stopping>15:
                    subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW)
            state(stage);time.sleep(.5)
        if cancel.exists():raise InterruptedError('已暂停 尚未合成的图片及图层已保留')
        if child.returncode:raise RuntimeError('快速导出步骤失败 '+(cache/'worker.log').read_text('utf-8',errors='replace')[-1600:])
def validate(file,n):
    result=subprocess.run([str(FP),'-v','error','-count_packets','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_packets','-of','json',str(file)],capture_output=True,encoding='utf-8',timeout=120,creationflags=subprocess.CREATE_NO_WINDOW,check=True)
    s=json.loads(result.stdout)['streams'][0]
    if s['width']!=1920 or s['height']!=1080 or s['r_frame_rate']!='24/1' or int(s['nb_read_packets'])!=n:raise RuntimeError('视频段验证失败 原图已保留')
def clean(folder):
    # Delete only this job's segment work directory after verified MP4 + manifest commit.
    resolved=folder.resolve();base=cache.resolve()
    if resolved.parent!=base or not resolved.name.startswith('work-'):raise RuntimeError('Unsafe cleanup path')
    if folder.exists():shutil.rmtree(folder)
try:
    if info['fingerprint']!=fingerprint:raise RuntimeError('画面或导出代码版本已改变 请另建新任务 旧素材保留')
    atomic(manifest,info);state('preparing')
    probe=subprocess.run([str(FF),'-v','error','-f','lavfi','-i','color=size=1920x1080:rate=24','-frames:v','1','-c:v','h264_nvenc','-f','null','-'],capture_output=True,timeout=20,creationflags=subprocess.CREATE_NO_WINDOW)
    if probe.returncode:raise RuntimeError('NVIDIA 编码器不可用 请关闭占用 GPU 的其他导出程序后重试')
    for first in range(0,total,args.segment_frames):
        check();count=min(args.segment_frames,total-first);current=cache/f'work-{first:08}';target=segments/f'{first:08}.mp4';entry=next((s for s in info['segments'] if s['start']==first),None)
        if entry or target.exists():
            validate(target,count)
            if not entry:info['segments'].append(dict(start=first,count=count,file=target.name));atomic(manifest,info)
            clean(current);completed+=count;current=None;continue
        current.mkdir(exist_ok=True);(current/'ui').mkdir(exist_ok=True)
        if (current/'segment.mp4').exists():validate(current/'segment.mp4',count)
        else:
            fonts=current/'fonts';fonts.mkdir(exist_ok=True)
            for f in Path(C['fontDir']).glob('*.otf'):
                if not (fonts/f.name).exists():shutil.copyfile(f,fonts/f.name)
            run([NODE,WORK/'render_layers.mjs',f'--dir={current}',f'--start={args.start+first/24}',f'--frames={count}',f'--cancel={cancel}'],'rendering')
            run([PY,WORK/'segment_assets.py',current,args.start+first/24,count],'segment-encoding')
            validate(current/'segment.mp4',count)
        (current/'segment.mp4').replace(target)
        info['segments'].append(dict(start=first,count=count,file=target.name,encoder='h264_nvenc'));atomic(manifest,info)
        completed+=count;fresh+=count;clean(current);current=None;state('segment-ready')
    state('merging');(segments/'concat.txt').write_text('\n'.join(f"file '{s['file']}'" for s in sorted(info['segments'],key=lambda s:s['start'])),'ascii')
    temp=EXPORTS/(job+'.partial.mp4');output=EXPORTS/(job+'.mp4')
    run([FF,'-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',segments/'concat.txt','-ss',args.start,'-i',SOURCE,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',duration,'-movflags','+faststart',temp],'merging')
    validate(temp,total);temp.replace(output)
    from runtime import write_srt
    write_srt(ROOT/'captions.json',EXPORTS/(job+'.srt'),args.start,duration)
    state('complete',url='/exports/'+job+'.mp4',subtitleUrl='/exports/'+job+'.srt',bytes=output.stat().st_size)
except InterruptedError as e:state('paused',error=str(e))
except Exception as e:state('error',error=str(e));raise
