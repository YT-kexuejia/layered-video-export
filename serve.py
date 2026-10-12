"""Local-only export dashboard. Bind to loopback; never expose this endpoint publicly."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
import json,subprocess,threading,sys,os,re
from runtime import load_settings
C=load_settings();BASE=Path(__file__).resolve().parent;OUT=Path(C['outputDir']);PORT=int(os.environ.get('LVE_PORT','4920'));LOCK=threading.Lock();PROCESS=None
POINTER=OUT/'latest.txt'
def active_job():return POINTER.read_text().strip() if POINTER.exists() else None
def status():
    job=active_job();file=OUT/(job+'.json') if job else None
    if file and file.exists():
        try:
            data=json.loads(file.read_text('utf-8'))
            if data['stage'] not in ('complete','error','paused') and (PROCESS is None or PROCESS.poll() is not None):data.update(stage='paused',resumable=True,error='Worker stopped. Existing local assets are retained.')
            return data
        except (OSError,ValueError):pass
    return {'stage':'idle'}
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(BASE),**kw)
    def json(self,value,code=200):
        data=json.dumps(value,ensure_ascii=False).encode();self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if self.path=='/api/export':return self.json(status())
        if self.path=='/':self.path='/dashboard.html'
        # Serve only explicitly allowed code/example files, never config or arbitrary paths.
        if self.path.split('?')[0] not in ('/dashboard.html','/example.html','/story.json','/captions.json','/source.mp4') and not self.path.startswith('/exports/'):return self.send_error(404)
        return super().do_GET()
    def translate_path(self,path):
        route=path.split('?')[0]
        if route=='/source.mp4':return C['sourceVideo']
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
                if job and PROCESS and PROCESS.poll() is None:(OUT/(job+'.cancel')).touch()
                return self.json(status())
            if self.path!='/api/export':return self.json({'error':'Unknown endpoint'},404)
            if PROCESS and PROCESS.poll() is None:return self.json(status(),202)
            previous=status()
            if not job or not previous.get('resumable'):
                import datetime
                job='export-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
                POINTER.write_text(job)
            marker=OUT/(job+'.cancel')
            if marker.exists():marker.unlink()
            with (OUT/(job+'.log')).open('ab') as log:
                PROCESS=subprocess.Popen([sys.executable,str(BASE/'export_video.py'),'--job='+job],cwd=BASE,stdin=subprocess.DEVNULL,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
            return self.json({'job':job,'stage':'preparing'},202)
    def end_headers(self):self.send_header('Cache-Control','no-store');super().end_headers()
if __name__=='__main__':
    print(f'Dashboard: http://127.0.0.1:{PORT}/')
    ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
