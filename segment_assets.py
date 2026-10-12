"""Build lossless UI / masks / native wave and compose one bounded segment."""
from pathlib import Path
import sys,json,time,hashlib,subprocess,re,math
from PIL import Image,ImageDraw
from runtime import load_settings
C=load_settings();WORK=Path(__file__).resolve().parent
ROOT=Path(sys.argv[1]).resolve();START=float(sys.argv[2]);N=int(sys.argv[3]);D=N/24
SRC=Path(C['projectDir']);FF=Path(C['ffmpeg']);SOURCE=C['sourceVideo']
STORY=json.loads((SRC/'story.json').read_text('utf-8'))
def progress(phase,done=0,total=N):
    (ROOT/'layer-progress.json').write_text(json.dumps(dict(phase=phase,done=done,total=total)),'utf-8')
def run(args,name):
    with (ROOT/(name+'.log')).open('w',encoding='utf-8') as log:
        p=subprocess.run([str(FF),'-y','-hide_banner',*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    if p.returncode:raise RuntimeError(name+' 失败 '+(ROOT/(name+'.log')).read_text('utf-8',errors='replace')[-2500:])
def stamp(t):
    n=round(max(0,t)*100);return f'{n//360000}:{n//6000%60:02}:{n//100%60:02}.{n%100:02}'
def subtitles():
    header=(WORK/'subtitle-style.ass').read_text('utf-8')
    header=header.replace('Source Han Sans SC',C['subtitleFont'])
    lines=[]
    for c in json.loads((SRC/'captions.json').read_text('utf-8')):
        if c['end']<=START or c['start']>=START+D:continue
        text=re.sub(r'[，。！？、；：,.!?;:]+',' ',c['text']).strip()
        # Preserve original timings while limiting cue length, preferring spaces.
        parts=[]
        while len(text)>36:
            cut=text.rfind(' ',12,37);cut=cut if cut>=12 else 36
            parts.append(text[:cut].strip());text=text[cut:].strip()
        if text:parts.append(text)
        size=sum(map(len,parts));at=c['start']
        for part in parts:
            end=at+(c['end']-c['start'])*len(part)/max(1,size)
            a=max(0,at-START);b=min(D,end-START)
            if b>a:lines.append(f'Dialogue: 0,{stamp(a)},{stamp(b)},Default,,0,0,0,,{part.replace(chr(123),chr(65371)).replace(chr(125),chr(65373))}')
            at=end
    (ROOT/'segment.ass').write_text(header+'\n'.join(lines)+'\n','utf-8')
def ui():
    if (ROOT/'ui-alpha.mov').exists():return
    progress('ui-encoding');indices=json.loads((ROOT/'ui-index.json').read_text('utf-8'));kept=[];last=None
    for i in indices:
        digest=hashlib.sha256((ROOT/'ui'/f'{i:05}.png').read_bytes()).digest()
        if digest!=last:kept.append(i);last=digest
    lines=['ffconcat version 1.0']
    for j,i in enumerate(kept):
        end=kept[j+1] if j+1<len(kept) else N
        lines.extend([f"file 'ui/{i:05}.png'",'option framerate 24',f'duration {(end-i)/24:.9f}'])
    lines.extend([f"file 'ui/{kept[-1]:05}.png'",'option framerate 24'])
    (ROOT/'ui-concat.txt').write_text('\n'.join(lines),'ascii')
    run(['-f','concat','-safe','0','-i','ui-concat.txt','-vf','fps=24,format=argb','-frames:v',str(N),'-c:v','qtrle','ui-alpha.partial.mov'],'ui-encoding')
    (ROOT/'ui-alpha.partial.mov').replace(ROOT/'ui-alpha.mov')
def wave():
    if (ROOT/'wave-alpha.mov').exists():return
    progress('wave');import manimgx as m
    m.config.pixel_width=342;m.config.pixel_height=34;m.config.frame_height=34/120;m.config.frame_rate=24;m.config.background_opacity=0
    class Wave(m.Scene):
        def construct(self):
            bars=m.VGroup(*[m.Rectangle(width=2/120,height=20/120,stroke_width=0,fill_color='#b7dbff',fill_opacity=.7) for _ in range(23)])
            def update(mob,dt):
                t=self.time+START;chapter=next((c for c in reversed(STORY['chapters']) if c['start']<=t),STORY['chapters'][0])
                for j,b in enumerate(mob):
                    b.stretch_to_fit_height((7+(math.sin(j*1.8+t*7)+1)*13)/120);b.move_to([(j*5+1-171)/120,0,0]);b.set_color(chapter['accent']);b.set_opacity(max(0,min(1,(t-7.3)/.7))*.7)
            bars.add_updater(update);self.add(bars);self.wait(D)
    with (ROOT/'wave.log').open('w') as log:
        p=subprocess.Popen([str(FF),'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pixel_format','rgba','-video_size','342x34','-framerate','24','-i','pipe:0','-an','-c:v','qtrle',str(ROOT/'wave-alpha.partial.mov')],stdin=subprocess.PIPE,stderr=log)
        count=0
        def sink(f):
            nonlocal count
            data=f.pixels()
            for _ in range(min(f.repeat,N-count)):
                p.stdin.write(data);count+=1
            if count%120==0:progress('wave',count)
        try:Wave().render(frames=sink)
        finally:p.stdin.close()
        if p.wait():raise RuntimeError('ManimGX wave failed')
    (ROOT/'wave-alpha.partial.mov').replace(ROOT/'wave-alpha.mov')
def masks():
    mask=Image.new('L',(342,500));ImageDraw.Draw(mask).rounded_rectangle((0,0,341,499),24,fill=255);mask.save(ROOT/'portrait-mask.png')
    shade=Image.new('RGBA',(342,500));d=ImageDraw.Draw(shade)
    for y in range(500):
        f=y/500;a=max(0,.93*(f-.63)/.37)
        if f<.25:a=max(a,.53*(1-f/.25))
        d.line((0,y,341,y),fill=(2,6,11,round(a*255)))
    shade.putalpha(Image.composite(shade.getchannel('A'),Image.new('L',(342,500)),mask));shade.save(ROOT/'shade.png')
    if START<7.62:
        folder=ROOT/'intro-mask';folder.mkdir(exist_ok=True)
        for r in json.loads((ROOT/'presenter-positions.json').read_text('utf-8')):
            im=Image.new('L',(1920,1080));ImageDraw.Draw(im).rounded_rectangle((r['x'],r['y'],r['x']+r['w']-1,r['y']+r['h']-1),r['radius'],fill=255);im.save(folder/f"{r['frame']:04}.png",compress_level=1)
    changes={0:None}
    chapters=[s for s in STORY['scenes'] if s['kind']=='chapter' and s['start']<START+D and s['start']+.95>START]
    for s in chapters:
        for i in range(max(0,math.floor((s['start']-START)*24)),min(N,math.ceil((s['start']+.95-START)*24)+1)):changes[i]=s
        end=math.ceil((s['start']+.95-START)*24)
        if 0<=end<N:changes[end]=None
    if chapters:
        folder=ROOT/'wipe-mask';folder.mkdir(exist_ok=True);lines=['ffconcat version 1.0'];keys=sorted(changes)
        for j,i in enumerate(keys):
            s=changes[i];im=Image.new('L',(1920,1080));draw=ImageDraw.Draw(im)
            if s:
                u=max(0,min(1,(START+i/24-s['start'])/.95));p=4*u**3 if u<.5 else 1-(-2*u+2)**3/2;x=-1920+3840*p
                if x<1919 and x+1919>0:draw.rectangle((max(0,x),0,min(1919,x+1919),1079),fill=255)
                draw.rectangle((103,927,1838,1001),fill=0)
            name=f'{i:05}.png';im.save(folder/name,compress_level=1)
            end=keys[j+1] if j+1<len(keys) else N
            lines.extend([f"file '{name}'",'option framerate 24',f'duration {(end-i)/24:.9f}'])
        lines.extend([f"file '{keys[-1]:05}.png'",'option framerate 24']);(folder/'concat.txt').write_text('\n'.join(lines),'ascii')
    return chapters
def compose(chapters):
    progress('compose');cmd=['-r','24','-i','gpu.h264','-i','ui-alpha.mov','-ss',str(START),'-i',SOURCE,'-loop','1','-i','portrait-mask.png','-loop','1','-i','shade.png']
    graph=f"[0:v]fps=24[base];[2:v]fps=24,format=rgba[src];[src]crop=738:1080:615:0,scale=342:500[p];[3:v]format=gray[pm];[p][pm]alphamerge[person];[base][person]overlay=1496:292:enable='gte(t,{7.62-START})'[b1];[b1][4:v]overlay=1496:292:enable='gte(t,{7.62-START})'[b2];"
    idx=5
    if START<7.62:
        graph=graph.replace('[src]crop','[src]split=2[isrc][psrc];[psrc]crop')
        v=f'(t+{START})';q=f'if(lt({v},6.42),0,if(gte({v},7.62),1,if(lt(({v}-6.42)/1.2,0.5),8*pow(({v}-6.42)/1.2,4),1-pow(-2*({v}-6.42)/1.2+2,4)/2)))'
        w=f'(1716-1374*({q}))';h=f'(766-266*({q}))';x=f'(102+1394*({q}))';y=f'(164+128*({q}))';intro=min(D,7.62-START)
        cmd+=['-framerate','24','-i','intro-mask/%04d.png']
        graph+=f"[isrc]trim=duration={intro},scale=w='max({w},{h}*16/9)':h=-2:eval=frame,format=rgba[iv];color=black@0:s=1920x1080:r=24:d={intro},format=rgba[blank];[blank][iv]overlay=x='{x}-(overlay_w-{w})*.52':y='{y}-(overlay_h-{h})*.5':shortest=1[ifull];[{idx}:v]format=gray[imask];[ifull][imask]alphamerge=shortest=1[masked];[b2][masked]overlay=eof_action=pass[b3];"
        idx+=1
    else:graph+='[b2]null[b3];'
    cmd+=['-i','wave-alpha.mov'];graph+=f'[b3][1:v]overlay=eof_action=pass[b4];[b4][{idx}:v]overlay=1496:811:eof_action=pass[bw];';idx+=1
    if chapters:
        enable='+'.join(f'between(t,{max(0,s["start"]-START)},{min(D,s["start"]+.95-START)})' for s in chapters)
        cmd+=['-f','concat','-safe','0','-i','wipe-mask/concat.txt'];graph+=f"[bw]split=2[clean][forblur];[forblur]gblur=sigma=12:enable='{enable}'[blurred];[{idx}:v]fps=24,format=gray[wm];[clean][blurred][wm]maskedmerge=enable='{enable}'[finished];"
    else:graph+='[bw]null[finished];'
    # Absolute font path lives in a font directory copied by the controller; no shell escaping.
    graph+='[finished]subtitles=segment.ass:fontsdir=fonts,format=yuv420p[v]'
    cmd+=['-filter_complex_threads','2','-filter_complex',graph,'-map','[v]','-an','-frames:v',str(N),'-r','24','-c:v','h264_nvenc','-preset','p5','-cq','18','-b:v','0','-movflags','+faststart','-progress','compose-progress.txt','segment.partial.mp4']
    run(cmd,'compose')
    (ROOT/'segment.partial.mp4').replace(ROOT/'segment.mp4')
started=time.perf_counter()
ui();wave();subtitles();chapters=masks();compose(chapters)
(ROOT/'segment-timing.json').write_text(json.dumps(dict(seconds=time.perf_counter()-started,frames=N)),'utf-8')
progress('done',N)
