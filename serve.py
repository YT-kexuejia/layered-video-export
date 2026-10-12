"""Local-only export dashboard. Bind to loopback; never expose this endpoint publicly."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import json,subprocess,threading,sys,os,re
from runtime import load_settings
C=load_settings();BASE=Path(__file__).resolve().parent;OUT=Path(C['outputDir']);PORT=int(os.environ.get('LVE_PORT','4920'));LOCK=threading.Lock();PROCESS=None
POINTER=OUT/'latest.txt'
def active_job():return POINTER.read_text().strip() if POINTER.exists() else None
def alive(pid):
    if not pid:return False
    if os.name=='nt':
        import ctypes
        kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.OpenProcess.restype=ctypes.c_void_p
        handle=kernel.OpenProcess(0x1000,False,int(pid))
        if not handle:return False
        try:
            code=ctypes.c_ulong();kernel.GetExitCodeProcess(ctypes.c_void_p(handle),ctypes.byref(code));return code.value==259
        finally:kernel.CloseHandle(ctypes.c_void_p(handle))
    try:os.kill(int(pid),0);return True
    except OSError:return False
def status():
    job=active_job();file=OUT/(job+'.json') if job else None
    if file and file.exists():
        try:
            data=json.loads(file.read_text('utf-8'))
            if data['stage'] not in ('complete','error','paused') and not alive(data.get('pid')):data.update(stage='paused',resumable=True,error='Worker stopped. Existing local assets are retained.')
            return data
        except (OSError,ValueError):pass
    return {'stage':'idle'}
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(BASE),**kw)
    def json(self,value,code=200):
        data=json.dumps(value,ensure_ascii=False).encode();self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if self.path=='/favicon.ico':self.send_response(204);self.end_headers();return
        if self.path=='/api/export':return self.json(status())
        if self.path=='/':self.path='/dashboard.html'
        route=self.path.split('?')[0]
        if route=='/source.mp4':return self.source()
        if route not in ('/dashboard.html','/example.html','/film.html','/bundle.js','/bundle.css','/story.json','/captions.json','/captions.srt') and not route.startswith(('/exports/','/assets/','/fonts/')):return self.send_error(404)
        return super().do_GET()
    def source(self):
        file=Path(C['sourceVideo']);size=file.stat().st_size;start=0;end=size-1
        match=re.fullmatch(r'bytes=(\d+)-(\d*)',self.headers.get('Range',''))
        if match:
            start=int(match[1]);end=min(size-1,int(match[2])) if match[2] else size-1
            if start>=size or start>end:return self.send_error(416)
        self.send_response(206 if match else 200);self.send_header('Content-Type','video/mp4');self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(end-start+1))
        if match:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.end_headers()
        try:
            with file.open('rb') as f:
                f.seek(start);left=end-start+1
                while left:
                    b=f.read(min(left,1024*1024))
                    if not b:break
                    self.wfile.write(b);left-=len(b)
        except (BrokenPipeError,ConnectionResetError):pass
    def translate_path(self,path):
        route=path.split('?')[0]
        if route=='/source.mp4':return C['sourceVideo']
        if route in ('/film.html','/bundle.js','/bundle.css','/story.json','/captions.json','/captions.srt') or route.startswith(('/assets/','/fonts/')):
            from urllib.parse import unquote
            root=Path(C['projectDir']).resolve();target=(root/unquote(route).lstrip('/')).resolve()
            if target.is_relative_to(root) and target.suffix.lower() in {'.html','.js','.css','.json','.srt','.png','.jpg','.jpeg','.svg','.webp','.otf','.ttf','.woff2'}:return str(target)
            return str(BASE/'.not-found')
        if route.startswith('/exports/'):
            name=route.removeprefix('/exports/')
            if re.fullmatch(r'[A-Za-z0-9_-]+\.(mp4|srt)',name):return str(OUT/name)
            return str(BASE/'.not-found')
        return super().translate_path(path)
    def do_POST(self):
        global PROCESS
        if self.headers.get('Origin') not in (f'http://127.0.0.1:{PORT}',f'http://localhost:{PORT}') or self.headers.get('Content-Type')!='application/json':return self.json({'error':'Local dashboard requests only'},403)
        if int(self.headers.get('Content-Length','0'))>1024:return self.json({'error':'Body too large'},413)
        self.rfile.read(int(self.headers.get('Content-Length','0')))
        with LOCK:
            job=active_job()
            if self.path=='/api/export/cancel':
                if job and alive(status().get('pid')):(OUT/(job+'.cancel')).touch()
                return self.json(status())
            if self.path!='/api/export':return self.json({'error':'Unknown endpoint'},404)
            if alive(status().get('pid')):return self.json(status(),202)
            previous=status()
            if not job or not previous.get('resumable'):
                import datetime
                job='export-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
                POINTER.write_text(job)
            marker=OUT/(job+'.cancel')
            if marker.exists():marker.unlink()
            with (OUT/(job+'.log')).open('ab') as log:
                PROCESS=subprocess.Popen([sys.executable,str(BASE/'export_video.py'),'--job='+job],cwd=BASE,stdin=subprocess.DEVNULL,stdout=log,stderr=log,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
            return self.json({'job':job,'stage':'preparing'},202)
    def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
if __name__=='__main__':
    print(f'Dashboard: http://127.0.0.1:{PORT}/')
    ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
